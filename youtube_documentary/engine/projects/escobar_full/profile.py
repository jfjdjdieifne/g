"""Escobar full-film BODY profile: source-led editorial decisions, shared renderer.
Approved 795-frame opening is joined by packet copy, never rerendered or retimed.
Shot marks below reference the preserved raw VO clock, mapped by its pacing audit.
"""
from pathlib import Path
import json,math
from film_runtime import decode,wav
PROJECT=Path(__file__).parent;ROOT=PROJECT.parents[2]
BUILD=Path('/home/user/build/escobar_film');FPS=24;SIZE=(1920,1080);BPM=120
ENCODE={'crf':24,'maxrate':'1400k','bufsize':'2800k'}
OUTPUT='Escobar_Body_Review.mp4';FONT_DIR=ROOT/'assets_global/fonts'
ASSET_DIRS=[PROJECT.parent/'escobar_intro3/assets',PROJECT.parent/'escobar_intro4/assets']
DEPTH_SPECS=json.loads((PROJECT.parent/'escobar_intro3/depth_masks.json').read_text())
INTRO=Path('/home/user/build/escobar_intro5/Escobar_Intro_Revision5_New_Cut.mp4')
FULL_OUTPUT='Escobar_Full_Film_Review.mp4'
INTRO_SHA256='1a05ed7c029b7f910cd1d62be1bd911745fefc23b96652292b1bea9ceec0894d'
PBS='https://www.pbs.org/video/the-godfather-of-cocaine-ongrgz/'
# Each mark: raw VO seconds, source original seconds (or a disclosed diagram/photo), meaning.
CHAPTERS={
'01_business':[
(0,787,'Wealth followed the operation; estate footage, not a reconstructed crime'),
(3,802,'Different estate/home-movie scene; private possessions, no claim of a photographed deal'),
(7,1183,'US demand: contextual Miami street imagery'),
(13,884,'The actual subject; a different portion of the home-movie moment'),
(19,'andes','Coca inputs from Peru/Bolivia to Colombia; conceptual network, not one shipment'),
(25,2590.2,'Actual Tranquilandia lab interior and equipment; historical contextual example, not every Colombian lab'),
(28,959,'Actual pilot/cockpit imagery; transport north'),
(32,1057,'The cartel network was not one man; actual group footage'),
(36,1249,'Ochoa family context from the original report, not three falsely identified faces'),
(40,'north','Bahamas connection and onward movement; schematic paths, true geography'),
(47,1137,'Flights and onward movement; native smuggling/interdiction imagery'),
(52,1193,'Demand at the end of the chain: original street and consumer-cocaine imagery, not an asserted filmed Escobar transaction'),
(57,'network','Return to the whole geographical supply chain, with a wider camera'),
(61,1084,'A moving aircraft completes the supply-chain explanation')],
'02_support':[
(0,1127,'Transport succeeds only with protection; native source flight imagery'),
(4,1984,'Real hidden-camera payoff footage from the report; NOT a fabricated payment by Escobar'),
(10,2676,'Threats against officials: institutional security, not an invented assault'),
(15,1100,'The next shipment: different source aircraft moment'),
(19,383,'Transition to Medellin through its actual filmed streets'),
(23,'housing','Actual 1983 construction photograph, intentionally returning to opening evidence in a longer explanation'),
(28,1866.2,'Football facilities in the source report, not an unrelated stadium'),
(32,1797,'Actual neighborhood houses, contemporary to the original report'),
(36,1843,'The Flores household, identified as rehoused beneficiaries in the original programme'),
(40,1889,'Genuine painted Escobar myth in the community; not a generated portrait or a muted expert interview'),
(45,1820,'People living in the community; no claim all residents endorsed crime'),
(50,'bbc:106','Modern neighborhood context, explicitly dated 2013; not evidence of a particular 1983 recipient'),
(55,1871,'The same man: actual Escobar with people at a public football appearance, no expert interview under the narrator'),
(60,'aj:25','Same city, later time: 2018 Medellin context, explicitly dated')],
'03_politics':[
(0,1940,'Actual 1982 election mural from source; no fabricated newspaper'),
(5,'congress','Actual congressional photograph, deliberately reused for the alternate-representative qualification'),
(12,1954,'Legitimate institutions; chamber imagery rather than pretending he ran the country'),
(17,'public_depth','Actual public appearance, original-pixel 2.5D rather than invented action'),
(24,2120,'Actual Escobar family photograph from the report; not another person passed off as him'),
(28,1805,'Public benefactor image in the actual community'),
(31,2482,'Contrast with cocaine processing: real industrial laboratory imagery'),
(36,2068,'Actual Justice Minister Rodrigo Lara Bonilla speaking publicly'),
(41,2077,'Archival political meeting in the report; no further identity claim'),
(46,2732,'Aftermath of the minister assassination: damaged car, no graphic body'),
(50,2680,'Security outside public institutions; danger to people challenging the trade'),
(55,3603,'The press was also targeted: actual newspaper newsroom staff and computers'),
(61,2670,'Actual Escobar political address photograph; public image versus intimidation'),
(66,2749.3,'State response to cartel violence: genuine armed helicopter/operation imagery, not a muted interview or an asserted fatal shooter')],
'04_extradition':[
(0,3260,'US prison exterior in the report, extradition as the central threat'),
(4,3067,'Definition: face justice in another country; actual US exterior'),
(8,3050.6,'United States government context, not a fake news anchor'),
(12,1990,'Actual hidden-camera political payoff, later non-overlapping source seconds'),
(18,3265,'A prison cell abroad; genuine prison security footage, not a CGI cell'),
(24,2913,'Communications in trafficking logistics, contextual source imagery, not Escobar lip-sync'),
(29,610,'Actual historical Escobar portrait in the source biography; not an unrelated informant face'),
(34,3934,'Actual terror aftermath; contextual historical violence, no body close-up'),
(40,3600,'Journalists: original newspaper production footage'),
(44,3949.5,'Civilian cost: damaged buildings, not stock explosions'),
(49,3621,'Actual Galan campaign rally before the assassination'),
(53,3647,'The same documented campaign event, no synthetic gunfire'),
(58,3691,'Confusion and response at the event, source speed unchanged'),
(63,1790,'Ordinary people living with the consequences; historical Medellin housing'),
(69,'aj:35','Later Medellin view explicitly dated 2018; the city is not reduced to one man')],
'05_prison':[
(0,4027,'Actual constituent assembly; reform was larger than Escobar'),
(5,4039.4,'Different assembly angle: prohibition on extradition, not a forged constitution'),
(13,4032,'Constitutional process continued: avoid claiming he wrote the document'),
(20,4097,'Actual surrender transport helicopter, June 1991 in source context'),
(24,4107,'Actual La Catedral hillside location'),
(28,4131,'Prison grounds: comfort is not the whole issue'),
(31.72,4249,'The office inside La Catedral; retained operational connections'),
(37,4146,'Prison guards and perimeter; power inside an ostensibly controlled place'),
(42,4116,'Actual facility exterior, not a fabricated prison plan'),
(46,4203,'Actual prison interior; no claim a shown family photo depicts murdered associates'),
(50,4121,'Return to the actual prison location on the breakdown of the arrangement'),
(54,4283,'Nighttime exterior from the original escape report; not claimed to show him walking out'),
(57,4293,'Actual wanted poster after escape; do not misread peso reward as dollars'),
(62,4308,'Police mobilization after the failed agreement')],
'06_collapse':[
(0,4315,'Manhunt street patrol, actual original report'),
(5,4337,'Road searches, native source footage'),
(10,4410,'Actual police computer imagery modeling Escobar disguises during the search; not a modern generated face or a muted interview'),
(15,4369.3,'Property targeted by rivals during the manhunt, as identified by source context'),
(21,4378,'Aftermath and attacks on the network, not a lawful solution'),
(25,4487,'Pressure from different directions: police night operation'),
(31,'forbes','Actual 1987 wealth entry; deliberate callback to why a fortune was not protection'),
(36,4415,'Institutions and searches, not a fabricated betrayal scene'),
(43,4460,'Actual tracking equipment on the dated final search'),
(48,4550,'Mobile direction-finding imagery from the report'),
(52,4609,'Actual house/roofline in the final operation report; omit corpse images'),
(57,4580,'Actual location exterior; disputed fatal shot is not assigned to a person'),
(62,4643.5,'Actual death-site house and roof imagery from the report, not footage identifying the fatal shooter; no corpse close-up')],
'07_legacy':[
(0,'aj:65','Later merchandise and memory, explicitly 2018'),
(5,1848,'Actual beneficiary household from source; the aid was not imaginary'),
(9,'aj:48','Medellin Memory House Museum, not a generic memorial passed off as a particular victim'),
(14,'bbc:102.8','Modern families in the neighborhood, contextual not verified original recipients'),
(20,1814,'Genuine housing neighborhood in the older report, not a claim all residents agreed'),
(26,'aj:144','Memory House archive display; competing memories and documented history'),
(32,2596,'Historical Tranquilandia lab-complex/cargo imagery: the larger operation, not falsely presented as a filmed post-1993 transaction'),
(38,'aj:38','Contemporary city life continued, explicitly dated 2018'),
(45,4894,'Later trafficking incentives; waterfront/city imagery from the 1995 report'),
(55,4904,'Empire ended, incentives survived; native city movement, not a victorious payoff'),
(62,'aj:36.5','Return to Medellin rather than ending on the criminal as a hero')]
}


def source_at(t):
    if t<360:return Path('/home/user/build/escobar_intro5/primary_media/pbs_research.mp4'),0
    if t<1200:return Path('/home/user/build/escobar_intro5/industry_media/pbs_industry_research.mp4'),360
    offset=1200 if t<2160 else 2160 if t<3120 else 3120 if t<4080 else 4080
    return BUILD/'research'/str(offset)/f'pbs_later_{offset}_research.mp4',offset


def mapped(t,audit):
    regs=audit['regions']
    for r in regs:
        if r['source_in']<=t<=r['source_out']:
            return r['output_in']+(t-r['source_in'])/(r['source_out']-r['source_in'])*(r['output_out']-r['output_in'])
        if t<r['source_in']:return r['output_in']
    return audit['output_seconds']


def prepare():
    BUILD.mkdir(parents=True,exist_ok=True);clips=BUILD/'clips';clips.mkdir(exist_ok=True)
    pacing=json.loads((PROJECT/'narration_pacing.json').read_text());shots=[];audio=[];chapters=[];at=0
    quote_specs={'05_prison':(31.72,4191.35,4195.69,'murphy','STEPHEN MURPHY / DEA agent','Prison comfort: original English testimony, source picture/audio clock matched'),
                 '07_legacy':(54.8,4877.43,4882.08,'blum','JACK BLUM / Senate investigator','Death did not change the trade: original English witness, 1995 perspective')}
    nodes={'andes':[{'label':'Peru','lon':-75,'lat':-10},{'label':'Bolivia','lon':-65,'lat':-17},{'label':'Colombia','lon':-75.58,'lat':6.24}],
           'north':[{'label':'Colombia','lon':-75.58,'lat':6.24},{'label':'Bahamas','lon':-76.82,'lat':24.6,'label_offset':[15,12]},{'label':'Miami','lon':-80.19,'lat':25.76,'label_offset':[-100,-30]}]}
    nodes['network']=[{**nodes['andes'][0],'label_offset':[12,-80]},nodes['andes'][2],nodes['north'][1],nodes['north'][2]]
    for ci,(key,specs) in enumerate(CHAPTERS.items()):
        a=pacing[key];voice=PROJECT/'narration'/(key+'.flac');duration=a['output_seconds'];q=quote_specs.get(key);insert=mapped(q[0],a) if q else None;qlen=(q[2]-q[1]+.16) if q else 0
        start=math.ceil(at*FPS)/FPS
        def clock(raw):
            t=mapped(raw,a)
            return start+t+(qlen if q and t>=insert else 0)
        end=start+duration+qlen
        if q:
            x=decode(voice);b=round(insert*48000);wav(clips/(key+'_a.wav'),x[:b]);wav(clips/(key+'_b.wav'),x[b:])
            afile=clips/(key+'_a.wav');bfile=clips/(key+'_b.wav')
            source,offset=source_at(q[1]);actual=q[2]-q[1];wav(clips/(q[3]+'.wav'),decode(source,q[1]-offset,actual))
            for id,kind,file,s,d in [(key+'_a','narration',afile,start,insert),(q[3],'archive',clips/(q[3]+'.wav'),start+insert+.08,actual),(key+'_b','narration',bfile,start+insert+qlen,duration-insert)]:audio.append({'id':id,'kind':kind,'file':str(file),'start':s,'end':s+d,'duration':d})
        else:audio.append({'id':key,'kind':'narration','file':str(voice),'start':start,'end':start+duration,'duration':duration})
        marks=[(clock(raw),ref,meaning) for raw,ref,meaning in specs]
        if q:
            qs=start+insert
            # Insertion begins after the preceding VO phrase; include its own genuine source reveal.
            marks=[(t,ref,meaning) for t,ref,meaning in marks if not qs-.04<t<qs+qlen]
            prev=max(i for i,(raw,_,_) in enumerate(specs) if raw<=q[0]);resume=specs[prev][1]
            if isinstance(resume,(int,float)):resume+=insert-mapped(specs[prev][0],a)
            # Leave Murphy's picture before the source cuts to a party photograph.
            # His unchanged final words continue over the genuine prison office (L-cut).
            picture_end=qs+qlen-(.375 if q[3]=='murphy' else 0)
            marks.append((qs,'quote:'+q[3],q[5]));marks.append((picture_end,resume,'Return to the genuine prison interior under the witness tail; source audio remains untouched' if q[3]=='murphy' else 'Continue the interrupted source moment after the original witness, without replaying it'))
        marks.sort(key=lambda x:x[0]);chapter_last=math.ceil((end+.22)*FPS)/FPS
        if ci==len(CHAPTERS)-1:chapter_last=math.ceil((end+1.4)*FPS)/FPS
        for j,(s,ref,meaning) in enumerate(marks):
            # Coalesce the same source cue, retaining stable IDs and no replay/flash.
            if j+1<len(marks) and ref==marks[j+1][1]:
                marks[j+1]=(s,ref,meaning);continue
            first=round(s*FPS);last=round((marks[j+1][0] if j+1<len(marks) else chapter_last)*FPS)
            if last<=first:continue
            row={'id':f'{key}_{j:02d}','kind':'video','first':first,'last':last,'start':first/FPS,'end':last/FPS,'meaning':meaning,'credit':['FRONTLINE / 1995']}
            if isinstance(ref,(int,float)):
                src,offset=source_at(ref);row.update(path=str(src),source_in=ref-offset,original_source_in=ref,source_url=PBS)
            elif ref.startswith('quote:'):
                src,offset=source_at(q[1]);row.update(path=str(src),source_in=q[1]-offset-.08,original_source_in=q[1]-.08,source_url=PBS,credit=[q[4],'FRONTLINE / 1995'],speaker=True)
            elif ref.startswith('aj:') or ref.startswith('bbc:'):
                broadcaster,value=ref.split(':');row.update(path=f'/home/user/build/escobar_intro5/primary_media/{broadcaster}_research.mp4',source_in=float(value),original_source_in=float(value),watermark=True,source_url='https://www.bbc.com/news/av/world-25158010' if broadcaster=='bbc' else 'https://www.aljazeera.com/news/2018/12/2/pablo-escobars-legacy-25-years-on-tributes-and-disgust',credit=['BBC News / 2013' if broadcaster=='bbc' else 'Al Jazeera English / 2018','Later Medellin context'])
            elif ref in ['andes','north','network']:
                row.update(kind='route',stage=ref,nodes=nodes[ref],edges=[(0,2),(1,2)] if ref=='andes' else [(i,i+1) for i in range(len(nodes[ref])-1)],credit=['Explanatory map / Natural Earth','Schematic links, not recorded flights'])
            elif ref=='housing':row.update(kind='image',asset='housing1983.jpg',center=[600,410],span=1200,push=.04,yaw=.018,travel=[5,-2],credit=['Housing under construction, 1983','Edgar El Chino Jimenez / El Pais'])
            elif ref=='congress':row.update(kind='image',asset='congress.jpg',center=[300,220],span=610,push=.025,yaw=.014,travel=[0,-3],credit=['Congress, 1983 / El Tiempo archive'])
            elif ref=='public_depth':row.update(kind='depth',asset='football.jpg',center=[300,262],span=575,credit=['Public appearance, 1983 / El Tiempo archive','Animated photograph / Original pixels'])
            elif ref=='forbes':row.update(kind='image',asset='forbes_entry.png',center=[315,641],span=650,push=.025,yaw=.012,travel=[0,0],credit=['Forbes / 1987 billionaires issue'])
            else:raise ValueError(ref)
            shots.append(row)
        chapters.append({'id':key,'start':start,'end':chapter_last,'voice_seconds':duration,'quote_seconds':qlen});at=chapter_last
    for l,r in zip(shots,shots[1:]):
        if l['last']!=r['first']:raise ValueError('Gap/overlap '+l['id']+' '+r['id'])
    sections=[]
    for c,bpm,mode,density,root in zip(chapters,[122,112,116,132,86,138,94],['pulse','pulse','pulse','pressure','sparse','pressure','sparse'],[1,.80,.84,1.05,.70,1,.65],[73.416,65.406,73.416,69.296,65.406,73.416,65.406]):sections.append({'start':c['start'],'end':c['end'],'bpm':bpm,'mode':mode,'density':density,'root':root})
    shots[-1]['fade_out']=1.0
    plan={'schema':'sequence-film/1','render_mode':'segmented','fps':FPS,'frames':shots[-1]['last'],'audio':audio,'shots':shots,'chapters':chapters,'score_sections':sections,'effects':[c['start'] for c in chapters[1:]],'music_holes':[],'source_rights_cleared':False,'manual_listening_claimed':False,'native_footage_retimed':False,'archive_witnesses_retimed':False,'narration_clause_processed':True,'intro_prefix_external_locked':True}
    (PROJECT/'timeline.json').write_text(json.dumps(plan,indent=2));return plan
