#!/usr/bin/env python3
import os,sys,unittest
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from common import parse_action_key
from solve_arm_reach import solve as solve_arm
from solve_leg_reach import solve as solve_leg
from validate_pose import validate_contact,validate_contacts,validate_registration,validate_transition,active_joint_names
from build_runtime_pose_constraints import solve_arm_nearest_source,solve_arm_prefer_neutral

class RuntimePoseTest(unittest.TestCase):
    def test_action_key_parser_single(self):
        self.assertEqual(parse_action_key("SN:L"),[{"part":"SN","limb":"L"}])

    def test_action_key_parser_combo(self):
        self.assertEqual(parse_action_key("BD+RC:RF/R"),[
            {"part":"BD","limb":"RF"},{"part":"RC","limb":"R"}])
        self.assertEqual(parse_action_key("RD+SN:R/L"),[
            {"part":"RD","limb":"R"},{"part":"SN","limb":"L"}])

    def test_action_key_parser_rejects_cardinality_mismatch(self):
        with self.assertRaises(ValueError):
            parse_action_key("BD+RC:R")

    def test_arm_contact(self):
        q=solve_arm([692,344],[420,535],140,100,120,0,1)
        self.assertTrue(q["reachable"]); self.assertLessEqual(q["tipErrorPx"],8)

    def test_arm_branch_preserves_source_elbow(self):
        q=solve_arm_nearest_source([692,344],[420,535],137.266,86.354,156.16,[651,475],[575,516])
        self.assertTrue(q["reachable"]); self.assertEqual(q["selectedBend"],-1)
        self.assertLess(abs(q["elbow"][0]-651),30)
        self.assertLess(abs(q["elbow"][1]-475),30)

    def test_sn_l_prefers_neutral_shoulder_when_reachable(self):
        neutral={"joints":{"shoulder_l":[635,342],"elbow_l":[585,470],"wrist_l":[505,490]},
                 "props":{"stick_tip_l":[432,384]}}
        state={"joints":{"shoulder_l":[692,344],"elbow_l":[651,475],"wrist_l":[575,516]},
               "props":{"stick_tip_l":[445,467]}}
        q=solve_arm_prefer_neutral(neutral,state,"l",[420,535])
        self.assertTrue(q["reachable"])
        self.assertEqual(q["anchorPolicy"],"neutral_shoulder_and_lengths")
        self.assertEqual(q["shoulder"],[635,342])
        self.assertLessEqual(q["tipErrorPx"],8)
        self.assertLess(abs(q["elbow"][0]-594.573),1)
        self.assertLess(abs(q["wrist"][0]-515.776),1)

    def test_leg_solver(self):
        q=solve_leg([800,620],[735,650],160,190,35,-1)
        self.assertTrue(q["reachable"]); self.assertLessEqual(q["pedalErrorPx"],8)

    def test_phase_aware_contact(self):
        self.assertTrue(validate_contact({"phase":"neutral","contactPoint":[420,535],"stickTip":[432,384]})["pass"])
        self.assertTrue(validate_contact({"phase":"hit","contactPoint":[420,535],"stickTip":[420,535]})["pass"])
        self.assertTrue(validate_contact({"phase":"rebound","contactPoint":[420,535],"stickTip":[438,418]})["pass"])

    def test_multi_effector_contact(self):
        pkg={"phase":"hit","effectors":[
            {"part":"BD","limb":"RF","kind":"pedal","target":[735,650],"point":[735,650]},
            {"part":"RC","limb":"R","kind":"stick","target":[1215,145],"point":[1215,145]}
        ]}
        q=validate_contacts(pkg)
        self.assertTrue(q["pass"]); self.assertEqual(len(q["checks"]),2)

    def test_missing_combo_contact_blocks_hit(self):
        pkg={"phase":"hit","effectors":[
            {"part":"LC","limb":"R","kind":"stick","target":None,"point":[100,100]}
        ]}
        q=validate_contacts(pkg)
        self.assertFalse(q["pass"])
        self.assertEqual(q["checks"][0]["mode"],"missing_authoritative_contact")

    def test_active_joint_names_combo(self):
        q=active_joint_names({"actionKey":"BD+RC:RF/R"})
        self.assertIn("ankle_r",q); self.assertIn("wrist_r",q)

    def test_validators(self):
        n={"stoolAnchor":[790,724],"hipAnchor":[762,638],"joints":{"wrist_l":[505,490]},"limb":"L"}
        h={"stoolAnchor":[790,724],"hipAnchor":[762,638],"joints":{"wrist_l":[520,500]},"contactPoint":[420,535],"stickTip":[420,535],"phase":"hit","limb":"L"}
        self.assertTrue(validate_contact(h)["pass"]); self.assertTrue(validate_registration(h,n)["pass"]); self.assertTrue(validate_transition(n,h)["pass"])

if __name__=="__main__": unittest.main()
