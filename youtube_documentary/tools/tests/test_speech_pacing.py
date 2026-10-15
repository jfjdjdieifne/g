"""Processing contract: preserve raw identity/file, word coverage and emphasis.
These tests cannot establish that speech sounds natural to a listener.
"""
import json,sys,tempfile,hashlib,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'engine/runtime'))
from film_runtime import wav,decode
from speech_pacing import shape

class PacingTests(unittest.TestCase):
    def test_word_partition_and_raw_preservation(self):
        with tempfile.TemporaryDirectory()as d:
            source=Path(d)/'source.wav';out=Path(d)/'processed.wav'
            t=np.arange(6*48000)/48000;wav(source,.04*np.sin(2*np.pi*190*t));before=hashlib.sha256(source.read_bytes()).hexdigest()
            words=[{'word':str(i),'start':.15+i*.45,'end':.43+i*.45}for i in range(12)]
            a=shape(source,words,out,target_wpm=188.2,emphasis=[(4,7)])
            self.assertEqual(before,hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual([i for r in a['regions']for i in range(r['word_first'],r['word_last_exclusive'])],list(range(12)))
            self.assertTrue(all(r['tempo_factor']==1 for r in a['regions']if r['emphasis']))
            self.assertTrue(all(1.02<=r['tempo_factor']<=1.45 for r in a['regions']if not r['emphasis']))
            self.assertAlmostEqual(len(decode(out))/48000,a['output_seconds'],places=5)
            self.assertFalse(a['manual_listening_claimed'])
            self.assertTrue(out.with_suffix('.audit.json').exists())
    def test_invalid_word_bounds_rejected(self):
        with tempfile.TemporaryDirectory()as d:
            source=Path(d)/'source.wav';wav(source,np.zeros(48000))
            with self.assertRaises(ValueError):shape(source,[{'word':'bad','start':.1,'end':4}],Path(d)/'out.wav')

if __name__=='__main__':unittest.main()
