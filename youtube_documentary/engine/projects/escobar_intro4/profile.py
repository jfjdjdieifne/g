"""Rhythm revision of the praised broader opening. Never modifies revision3."""
from pathlib import Path
PROJECT=Path(__file__).parent
BUILD=Path('/home/user/build/escobar_intro4')
FPS=24
WIDTH,HEIGHT=1920,1080
VOICE='voice-02'
# Both original name voices are from ONE truthful source, not fake separate news.
ARCHIVE={
 'name_host':{'in':11.36,'out':12.63,'quote':'Pablo Escobar','speaker':'Charlie Rose','audio_only':True},
 'name_guest':{'in':38.72,'out':39.78,'quote':'Pablo Escobar','speaker':'Andrew Cockburn'},
 'ship':{'in':67.26,'out':71.53,'quote':'I mean, not just a little kilo here, a kilo there, but planeloads, shiploads.','speaker':'Andrew Cockburn'},
 'wanted':{'in':12.66,'out':15.30,'quote':'the most wanted man in the Western Hemisphere','speaker':'Charlie Rose','audio_only':True},
 'fear':{'in':76.74,'out':82.25,'quote':"He didn't really invent anything, but he had the gift for organization and instilling fear.",'speaker':'Andrew Cockburn'}
}
NARRATOR_ORDER=['wealth','social','questions','close']
VOICE_PHRASE_REMOVALS={'wealth':[(6.56,9.02)],'social':[(11.94,16.6719375)]} # Delete “Think about that” and “Now listen to the other side of the story”; retain factual sentences.
PRESS_HOLD=2.0
NARRATOR_GAP=.12
ENDING_HOLD=1.35

import json
REFERENCE=PROJECT.parent/"escobar_intro3"
DEPTH=json.loads((REFERENCE/"depth_masks.json").read_text())
ARCHIVE_FILE=Path("/home/user/build/escobar_archive_official/original_opening.mp4")
