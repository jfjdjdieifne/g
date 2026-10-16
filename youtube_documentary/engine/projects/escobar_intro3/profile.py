"""Broad, spoiler-free intro profile. No prison/escape/fate narrative in this cut."""
from pathlib import Path
BUILD=Path('/home/user/build/escobar_intro3')
FPS=24
W,H=1920,1080
VOICE='voice-02'
NARRATION={
 'wealth':"In nineteen eighty-seven, Forbes put Pablo Escobar on its billionaire list. Think about that. A cocaine trafficker, listed alongside the world's richest people.",
 'social':"But in parts of Medellín, there was another picture of him. He paid for homes and football fields. People had reasons to be grateful. That support mattered. Now listen to the other side of the story.",
 'questions':"How does someone selling cocaine become powerful enough to challenge a government? And how does he convince some of the people living with that violence to see him as a hero?",
 'close':"We're going back to Medellín, before the name took over the story."
}
ARCHIVE={
 'ship':{'source_in':66.38,'source_out':71.53,'quote':"To the United States. I mean, not just a little kilo here, a kilo there, but planeloads, shiploads.",'speaker':'Andrew Cockburn'},
 'wanted':{'source_in':12.66,'source_out':15.30,'quote':"the most wanted man in the Western Hemisphere",'speaker':'Charlie Rose','audio_only':True},
 'fear':{'source_in':76.74,'source_out':82.25,'quote':"He didn't really invent anything, but he had the gift for organization and instilling fear.",'speaker':'Andrew Cockburn'}
}
# Intentional intervals, not a preset30-second limit. Length includes intact new takes.
STARTS={'ship':0.0,'wealth':5.35,'wanted':21.0,'social':23.84,'fear':40.70,'questions':46.45,'close':57.80}
DURATION=63.25

# Film data for the shared runtime, not a separate per-film engine.
import json
DEPTH=json.loads((Path(__file__).parent/"depth_masks.json").read_text())
