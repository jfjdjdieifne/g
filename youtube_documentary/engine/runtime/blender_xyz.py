"""Optional Cycles backend for shared World geometry; no film assets/timeline here.
Requires bpy (tested 4.2.23). CPU/headless, no browser or EGL dependency.
"""
import math
from collections import defaultdict
import numpy as np


class CyclesWorldRenderer:
    def __init__(self,width=1280,height=720,samples=12):
        import bpy
        from mathutils import Vector
        self.bpy=bpy;self.Vector=Vector
        bpy.ops.wm.read_factory_settings(use_empty=True)
        s=bpy.context.scene;self.scene=s
        s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=samples
        s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True
        s.cycles.max_bounces=3;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=1;s.cycles.transmission_bounces=0
        s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100
        s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96
        s.render.threads_mode='FIXED';s.render.threads=2
        s.world=bpy.data.worlds.new('Environment');s.world.use_nodes=True
        s.world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.12,.16,1)
        s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
        s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.55
        self.materials={};self.objects=[]
        bpy.ops.mesh.primitive_plane_add(size=160,location=(0,0,-.62));ground=bpy.context.object
        ground.name='Ground';ground.data.materials.append(self.material((22,32,39),False,False))
        for name,loc,energy,size,col in [
            ('Key',(-7,-10,16),3500,10,(.86,.92,1)),
            ('Fill',(12,-3,10),1800,10,(.66,.80,1)),
            ('Rim',(-2,10,13),2500,8,(1,.78,.46))]:
            data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=col
            obj=bpy.data.objects.new(name,data);s.collection.objects.link(obj);obj.location=loc
            obj.rotation_euler=(Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
        data=bpy.data.cameras.new('Camera');self.camera=bpy.data.objects.new('Camera',data)
        s.collection.objects.link(self.camera);s.camera=self.camera
        data.sensor_fit='HORIZONTAL';data.sensor_width=36
    def material(self,color,emissive=False,textured=True):
        bpy=self.bpy;k=(tuple(color),emissive,textured)
        if k in self.materials:return self.materials[k]
        mat=bpy.data.materials.new(str(k));mat.use_nodes=True
        nodes=mat.node_tree.nodes;links=mat.node_tree.links
        shader=nodes.get('Principled BSDF')
        linear=tuple((c/255)**2.2 for c in color)
        shader.inputs['Base Color'].default_value=(*linear,1)
        shader.inputs['Roughness'].default_value=.72
        if emissive:
            shader.inputs['Emission Color'].default_value=(*linear,1)
            shader.inputs['Emission Strength'].default_value=.3
        if textured:
            noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=35;noise.inputs['Detail'].default_value=2
            bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.018
            links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],shader.inputs['Normal'])
        self.materials[k]=mat;return mat
    def set_world(self,world):
        import bmesh
        bpy=self.bpy
        for obj in self.objects:
            data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
            if isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
            elif isinstance(data,bpy.types.Curve):bpy.data.curves.remove(data)
        self.objects=[];groups=defaultdict(list)
        for pts,col,emissive,outline in world.faces:groups[(tuple(col),emissive)].append(pts)
        for (col,emissive),parts in groups.items():
            verts=[];faces=[]
            for pts in parts:
                start=len(verts);verts.extend(pts.tolist());faces.append(tuple(range(start,start+len(pts))))
            mesh=bpy.data.meshes.new('Geometry');mesh.from_pydata(verts,[],faces);mesh.update()
            bm=bmesh.new();bm.from_mesh(mesh)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
            obj=bpy.data.objects.new('World geometry',mesh);self.scene.collection.objects.link(obj)
            obj.data.materials.append(self.material(col,emissive))
            mod=obj.modifiers.new('Soft physical edges','BEVEL');mod.width=.014;mod.segments=2
            mod.limit_method='ANGLE';mod.angle_limit=.52
            self.objects.append(obj)
        # World-space strokes become actual tubes and participate in shadows/depth.
        bycolor=defaultdict(list)
        for points,col,width in world.lines:bycolor[(tuple(col),width)].append(points)
        for (col,width),lines in bycolor.items():
            curve=bpy.data.curves.new('Fine architecture','CURVE');curve.dimensions='3D'
            curve.bevel_depth=.0065*width;curve.bevel_resolution=1;curve.resolution_u=1
            for pts in lines:
                sp=curve.splines.new('POLY');sp.points.add(len(pts)-1)
                for dest,src in zip(sp.points,pts):dest.co=(*src,1)
            obj=bpy.data.objects.new('World lines',curve);self.scene.collection.objects.link(obj)
            obj.data.materials.append(self.material(col,False,False));self.objects.append(obj)
    def render(self,camera,path):
        bpy=self.bpy
        self.camera.location=tuple(camera.eye)
        # Forward vector is row two of the shared camera's rotation matrix.
        f=self.Vector(tuple(camera.R[2]));self.camera.rotation_euler=f.to_track_quat('-Z','Y').to_euler()
        self.camera.data.lens=36*camera.f/camera.width
        self.scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
