#!/usr/bin/env python3
import os,sys,unittest
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from solve_arm_reach import solve as solve_arm
from solve_leg_reach import solve as solve_leg
from validate_pose import validate_contact,validate_registration,validate_transition
class RuntimePoseTest(unittest.TestCase):
    def test_arm_contact(self):
        q=solve_arm([692,344],[420,535],140,100,120,0,1)
        self.assertTrue(q["reachable"]); self.assertLessEqual(q["tipErrorPx"],8)
    def test_leg_solver(self):
        q=solve_leg([800,620],[735,650],160,190,35,-1)
        self.assertTrue(q["reachable"]); self.assertLessEqual(q["pedalErrorPx"],8)
    def test_validators(self):
        n={"stoolAnchor":[790,724],"hipAnchor":[762,638],"joints":{"wrist_l":[505,490]}}
        h={"stoolAnchor":[790,724],"hipAnchor":[762,638],"joints":{"wrist_l":[520,500]},"contactPoint":[420,535],"stickTip":[420,535]}
        self.assertTrue(validate_contact(h)["pass"]); self.assertTrue(validate_registration(h,n)["pass"]); self.assertTrue(validate_transition(n,h)["pass"])
if __name__=="__main__": unittest.main()
