#!/usr/bin/env python3
import argparse,copy,json
from common import load_json,write_json,dist,parse_action_key,limb_joint_names,HAND_LIMBS,FOOT_LIMBS
from solve_arm_reach import solve as solve_arm
from solve_leg_reach import solve as solve_leg

def midpoint(a,b):
    return [round((a[0]+b[0])/2,3),round((a[1]+b[1])/2,3)]

def solve_arm_nearest_source(shoulder,target,upper,fore,stick,source_elbow,source_wrist):
    candidates=[]
    for bend in (1,-1):
        q=solve_arm(shoulder,target,upper,fore,stick,0,bend)
        score=dist(q["elbow"],source_elbow)+0.25*dist(q["wrist"],source_wrist)
        candidates.append((score,bend,q))
    score,bend,q=min(candidates,key=lambda x:x[0])
    q["selectedBend"]=bend
    q["sourcePreservationScore"]=round(score,3)
    return q

def contact_target(contacts,part):
    cp=(contacts["parts"].get(part) or {}).get("approximate")
    return [cp["x"],cp["y"]] if cp else None

def copy_active_chains(neutral,state,components,phase):
    if phase=="neutral":
        return copy.deepcopy(neutral["joints"])
    joints=copy.deepcopy(neutral["joints"])
    for c in components:
        for name in limb_joint_names(c["limb"]):
            joints[name]=copy.deepcopy(state["joints"][name])
    return joints

def build_effectors(components,state,contacts):
    out=[]
    for c in components:
        part,limb=c["part"],c["limb"]
        target=contact_target(contacts,part)
        if limb in HAND_LIMBS:
            point=state["props"].get("stick_tip_"+limb.lower())
            kind="stick"
        else:
            side="l" if limb=="LF" else "r"
            point=state["joints"].get("ankle_"+side)
            kind="pedal"
        out.append({"part":part,"limb":limb,"kind":kind,"target":target,"point":copy.deepcopy(point)})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--action-key",required=True)
    p.add_argument("--phase",choices=["neutral","hit","rebound"],required=True)
    p.add_argument("--contacts",required=True)
    p.add_argument("--anchors",required=True)
    p.add_argument("--retarget",required=True)
    p.add_argument("--appearance",required=True)
    p.add_argument("--drum-sha",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    contacts=load_json(a.contacts); anchors=load_json(a.anchors)
    ret=load_json(a.retarget); appearance=load_json(a.appearance)
    components=parse_action_key(a.action_key)
    state=copy.deepcopy(anchors["states"][a.phase])
    neutral=anchors["states"]["neutral"]
    joints=copy_active_chains(neutral,state,components,a.phase)
    stool=neutral["props"]["stool_center"]
    hip=midpoint(neutral["joints"]["hip_l"],neutral["joints"]["hip_r"])
    effectors=build_effectors(components,state,contacts)

    out={"schemaVersion":2,"authority":"tool","actionKey":a.action_key,"phase":a.phase,
         "actionComponents":components,"instruments":[c["part"] for c in components],
         "limbs":[c["limb"] for c in components],"targetHeadCount":ret["targetHeadCount"],
         "camera":"three-quarter-back / over-shoulder; face slightly screen-left; gaze right; drum rightward",
         "stoolAnchor":stool,"hipAnchor":hip,"characterScaleLocked":True,
         "canvas":contacts["canvas"],"effectors":effectors,
         "fixedDrumSha256":a.drum_sha,
         "sourceFrameSha256":anchors["sourceFrames"][a.phase]["sha256"],
         "joints":joints,"appearanceProfileId":appearance["profileId"],
         "retargetProfileId":ret["profileId"],
         "minimalMotionRule":"neutral whole-body baseline; only actionKey limbs may differ by phase",
         "forbiddenMovementZones":["camera","stool","pelvis beyond tolerance","inactive limbs","wrong limb","wrong instrument","fixed drum pixels in character layer"],
         "tolerancesPx":{"effector":8,"stool":12,"hip":18,"transitionJoint":120,"reboundSeparation":16},
         "confidence":state.get("confidence",0)}

    for e in out["effectors"]:
        limb=e["limb"]; target=e["target"]
        if limb in HAND_LIMBS:
            side=limb.lower()
            if a.phase=="hit" and target:
                shoulder=joints["shoulder_"+side]; wrist=joints["wrist_"+side]; elbow=joints["elbow_"+side]
                upper=dist(shoulder,elbow); fore=dist(elbow,wrist)
                existing_tip=state["props"].get("stick_tip_"+side)
                stick=dist(wrist,existing_tip) if existing_tip else 150
                solved=solve_arm_nearest_source(shoulder,target,upper,fore,stick,elbow,wrist)
                joints["elbow_"+side]=solved["elbow"]; joints["wrist_"+side]=solved["wrist"]
                e["point"]=solved["stickTip"]; e["solve"]=solved
            elif a.phase=="rebound":
                e["rule"]="preserve source rebound tip away from contact; validate continuity, do not force contact"
        elif limb in FOOT_LIMBS and a.phase=="hit" and target:
            side="l" if limb=="LF" else "r"
            hipj=joints["hip_"+side]; knee=joints["knee_"+side]; ankle=joints["ankle_"+side]
            solved=solve_leg(hipj,target,dist(hipj,knee),dist(knee,ankle),35,1 if side=="l" else -1)
            joints["knee_"+side]=solved["knee"]; joints["ankle_"+side]=solved["ankle"]
            e["point"]=solved["footTarget"]; e["solve"]=solved

    if len(out["effectors"])==1:
        e=out["effectors"][0]
        out["instrument"]=e["part"]; out["limb"]=e["limb"]; out["contactPoint"]=e["target"]
        if e["kind"]=="stick":
            out["stickTip"]=e["point"]
            if e.get("solve"): out["reach"]=e["solve"]
            if a.phase=="rebound": out["reboundRule"]=e.get("rule")
        else:
            out["pedalTarget"]=e["target"]
            if e.get("solve"): out["legReach"]=e["solve"]

    write_json(a.output,out)
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__":
    main()
