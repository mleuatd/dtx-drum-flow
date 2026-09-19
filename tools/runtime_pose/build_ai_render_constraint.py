#!/usr/bin/env python3
import argparse,json
from common import load_json,write_json
def main():
    p=argparse.ArgumentParser(); p.add_argument("--pose",required=True); p.add_argument("--appearance",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    pose=load_json(a.pose); app=load_json(a.appearance)
    out={"schemaVersion":1,"mode":"CONSTRAINED_RENDER_ONLY","actionKey":pose["actionKey"],"phase":pose["phase"],
      "targetHeadCount":pose["targetHeadCount"],"exactJointPositions":pose["joints"],"exactContactPoint":pose.get("contactPoint"),
      "stickTipTarget":pose.get("contactPoint") if pose.get("limb") in ("L","R") and pose["phase"]=="hit" else pose.get("stickTip"),
      "pedalTarget":pose.get("pedalTarget"),"stoolAnchor":pose["stoolAnchor"],"hipAnchor":pose["hipAnchor"],"camera":pose["camera"],
      "characterScaleLocked":True,"fixedDrumSha256":pose["fixedDrumSha256"],"appearanceModel":app,
      "forbiddenChanges":["camera","stool","hip anchor","limb side","instrument","head count","hair shortening","outfit redesign","fixed drum registration","drum pixels in character layer"],
      "retryPolicy":"Only numeric correction instructions from validators; no vague free-form correction.","formalOverwriteAllowed":False}
    write_json(a.output,out); print(json.dumps(out,ensure_ascii=False))
if __name__=="__main__": main()
