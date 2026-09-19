#!/usr/bin/env python3
import argparse,json
from common import load_json,write_json
def main():
    p=argparse.ArgumentParser(); p.add_argument("--pose",required=True); p.add_argument("--appearance",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    pose=load_json(a.pose); app=load_json(a.appearance)
    effectors=pose.get("effectors") or []
    out={"schemaVersion":2,"mode":"CONSTRAINED_RENDER_ONLY","actionKey":pose["actionKey"],"phase":pose["phase"],
      "targetHeadCount":pose["targetHeadCount"],"exactJointPositions":pose["joints"],
      "actionComponents":pose.get("actionComponents"),"effectors":effectors,
      "exactContactPoints":[{"part":e.get("part"),"limb":e.get("limb"),"target":e.get("target")} for e in effectors],
      "stoolAnchor":pose["stoolAnchor"],"hipAnchor":pose["hipAnchor"],"camera":pose["camera"],
      "characterScaleLocked":True,"fixedDrumSha256":pose["fixedDrumSha256"],"appearanceModel":app,
      "minimalMotionRule":pose.get("minimalMotionRule"),
      "forbiddenChanges":["camera","stool","hip anchor","inactive limbs","limb side","instrument","head count","hair shortening","outfit redesign","fixed drum registration","drum pixels in character layer"],
      "retryPolicy":"Only numeric correction instructions from validators; no vague free-form correction.","formalOverwriteAllowed":False}
    if not effectors:
        out["exactContactPoint"]=pose.get("contactPoint")
        out["stickTipTarget"]=pose.get("contactPoint") if pose.get("limb") in ("L","R") and pose["phase"]=="hit" else pose.get("stickTip")
        out["pedalTarget"]=pose.get("pedalTarget")
    write_json(a.output,out); print(json.dumps(out,ensure_ascii=False))
if __name__=="__main__": main()
