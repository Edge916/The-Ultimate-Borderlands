import unittest, tempfile
from pathlib import Path
from ultimate_vh.preflight import load_sheets,inspect
from ultimate_vh.progression import (GAMES, VAULT_HUNTERS, EXPANDED_SKILLS,HunterState,
                                     accessible_campaigns,can_fast_travel,loot_level,session_compatible)
from ultimate_vh.save import save_state,load_state

class DesignTests(unittest.TestCase):
    def test_preflight(self):self.assertEqual(inspect(load_sheets()),[])
    def test_count(self):self.assertEqual((len(GAMES),len(VAULT_HUNTERS),len(EXPANDED_SKILLS)),(5,26,78))
    def test_dlc_hunters(self):
        self.assertIn('bl4_loveless',[h.id for h in VAULT_HUNTERS])
        self.assertIn('bl4_c4sh',[h.id for h in VAULT_HUNTERS])
    def test_unique_names(self):self.assertEqual(len({h.id for h in VAULT_HUNTERS}),26)
    def test_stage_gates(self):
        self.assertEqual(accessible_campaigns(set()),['bl1'])
        self.assertEqual(accessible_campaigns({'bl1'}),['bl1','tps'])
        self.assertEqual(accessible_campaigns({'bl1','tps','bl2','bl3'}),[g.id for g in GAMES])
    def test_gear_cap(self):self.assertEqual(loot_level(299,2),300)
    def test_scale(self):self.assertEqual(loot_level(120,2),122)
    def test_bad_scale(self):
        with self.assertRaises(ValueError):loot_level(200,3)
    def test_hunter(self):HunterState('bl4_loveless').validate()
    def test_hunter_reject(self):
        with self.assertRaises(ValueError):HunterState('unknown').validate()
    def test_skill_unlock(self):
        with self.assertRaises(ValueError):HunterState('bl1_roland',level=59,skills={'bl1_roland_tier1':1}).validate()
    def test_skill_prerequisite(self):
        with self.assertRaises(ValueError):HunterState('bl1_roland',level=120,skills={'bl1_roland_tier2':1}).validate()
    def test_skill_effect(self):
        s=HunterState('bl1_roland',level=120,skills={'bl1_roland_tier1':3,'bl1_roland_tier2':1})
        self.assertEqual(s.effective_bonus('action_cooldown'),0.09)
    def test_fast_travel(self):
        s=HunterState('bl1_lilith',completed_campaigns={'bl1'},unlocked_locations={'bl1:fyrestone','tps:concordia'})
        self.assertTrue(can_fast_travel(s,'bl1:fyrestone'))
        self.assertTrue(can_fast_travel(s,'tps:concordia'))
        self.assertFalse(can_fast_travel(s,'bl2:sanctuary'))
    def test_save_round_trip(self):
        s=HunterState('bl1_lilith',level=65,experience=23,money=500,eridium=3,completed_campaigns={'bl1'},unlocked_locations={'bl1:fyrestone'},equipment_refs=[{'game':'bl1','object_key':'opaque_owned_game_ref','level':60}])
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.json';save_state(p,s)
            self.assertEqual(load_state(p),s)
    def test_save_detects_tamper(self):
        s=HunterState('bl1_lilith')
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.json';save_state(p,s)
            p.write_text(p.read_text().replace('"level": 1','"level": 2'))
            with self.assertRaises(ValueError):load_state(p)
    def test_match_same_manifest(self):
        self.assertTrue(session_compatible([HunterState('bl1_lilith'),HunterState('bl2_maya')],['sha','sha']))
    def test_match_diff_manifest(self):
        self.assertFalse(session_compatible([HunterState('bl1_lilith'),HunterState('bl2_maya')],['sha','other']))
    def test_incorrect_skill(self):
        with self.assertRaises(ValueError):HunterState('bl1_lilith',level=300,skills={'bl1_roland_tier1':1}).validate()
    def test_level_cap(self):
        with self.assertRaises(ValueError):HunterState('bl1_lilith',level=301).validate()

if __name__=='__main__':unittest.main()
