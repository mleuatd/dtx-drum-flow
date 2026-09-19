from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
defs={
 "hit":{"src":"character-assets/review-candidates/m136/bd_ft_rf_r_hit_attempt01.png","dst":"character-assets/layers/character/combo/bd_ft_rf_r_hit_refresh.png","sha":"297f815ffdf287e4f8a2f50836eae4d15d276c569a5889fb790ec103a8958bb3"},
 "rebound":{"src":"character-assets/review-candidates/m136/bd_ft_rf_r_rebound_attempt01.png","dst":"character-assets/layers/character/combo/bd_ft_rf_r_rebound_refresh.png","sha":"2d4f9e6eb11a4e821fd19e06ee1b44701ff4ba70a344a40878407aba517e3e7e"}
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mp=ROOT/"character-assets/config/assets_manifest.json";m=json.load(open(mp,encoding="utf-8"));assets=m.setdefault("assets",[]);by={a.get("path"):a for a in assets}
for phase,d in defs.items():
 src=ROOT/d["src"];dst=ROOT/d["dst"]
 if sha(src)!=d["sha"]:raise SystemExit(f"{phase} source sha mismatch")
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 if sha(dst)!=d["sha"]:raise SystemExit(f"{phase} formal sha mismatch")
 rel=str(dst.relative_to(ROOT));entry={"path":rel,"width":1448,"height":1086,"x":0,"y":0,"sha256":d["sha"],"status":"FORMAL_QA_PASSED_RUNTIME_PENDING","purpose":f"Luna M136 BD+FT:RF/R formal {phase}; exact FT:R parent plus approved local BD cue.","part":"BD+FT","phase":phase,"hand":"RF/R","notes":["Deterministic BD cue composition; fixed-drum visual QA PASS.",f"Dropbox exact bytes saved /ChatGPT/dtx-drum-flow/bd_ft_rf_r_{phase}_attempt01.png","Build run 35427546381 artifact 10579317531."]}
 if rel in by:by[rel].update(entry)
 else:assets.append(entry);by[rel]=entry
m["updatedAt"]=now;mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
txp=ROOT/"character-assets/prototypes/luna_say_maybe_136/transactions/bd_ft_rf_r.json";tx=json.load(open(txp,encoding="utf-8"));tx["status"]="FORMAL_QA_PASSED_RUNTIME_PENDING"
for phase,d in defs.items():
 ph=tx["phases"][phase];ph.update({"stage":"FORMAL","sha256":d["sha"],"qaStatus":"VISUAL_QA_PASS","formalPath":d["dst"]})
tx["qa"].update({"static":"PASS","compositeVisual":"PASS","locality":"PASS_BD_CUE_ONLY","transition":"PASS_VISUAL"});tx["build"]={"workflowRun":35427546381,"artifactId":10579317531};tx["updatedAt"]=now;tx.setdefault("notes",[]).append("Attempt01 exact bytes saved to Dropbox and promoted after deterministic locality/fixed-drum QA.");txp.write_text(json.dumps(tx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
pp=ROOT/"character-assets/prototypes/luna_say_maybe_136/PROGRESS.json";p=json.load(open(pp,encoding="utf-8"));p["status"]="FORMAL_QA_PASSED_RUNTIME_PENDING";p["analysis"].update({"formalPairReady":True,"allMapped":False,"dropboxSaved":True,"hitSha256":defs["hit"]["sha"],"reboundSha256":defs["rebound"]["sha"]});p["requiredNext"]="Register M136 formal frames/mapping, expand runtimeScope through M136, then run public PC/Xperia runtime QA.";p["updatedAt"]=now;pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("promoted M136")
