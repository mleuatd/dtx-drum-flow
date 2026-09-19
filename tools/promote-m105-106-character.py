from __future__ import annotations
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
pairs={
 "BD+FT+SN:RF/R/L":{
  "slug":"bd_ft_sn_rf_r_l",
  "hitSha":"0134ec012829295404c1e2ac570c035bb2dcbb9105ced1eb83d801ac03c491db",
  "reboundSha":"ff1d69ae31b13b027ab18164ce27f7f88a0c367148d49dfa79f3c0761e50ca4b",
  "part":"BD+FT+SN","hand":"RF/R/L",
  "tx":"character-assets/prototypes/luna_say_maybe_105_106/transactions/bd_ft_sn_rf_r_l.json"
 },
 "BD+FT:RF/L":{
  "slug":"bd_ft_rf_l",
  "hitSha":"226149a35897dc36ab82d5aeb29a972d4964274e542d4ebefb6ff3bd6a328814",
  "reboundSha":"c7c94290d3d9cd9fa6a65821f103641b0be05fdbffc544a95d5c248bfd3383c7",
  "part":"BD+FT","hand":"RF/L",
  "tx":"character-assets/prototypes/luna_say_maybe_105_106/transactions/bd_ft_rf_l.json"
 }
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path=ROOT/"character-assets/config/assets_manifest.json"
manifest=json.load(open(manifest_path,encoding="utf-8"))
assets=manifest.setdefault("assets",[])
by_path={a.get("path"):a for a in assets}
for action,s in pairs.items():
 for phase in ("hit","rebound"):
  expected=s[phase+"Sha"]
  src=ROOT/f"character-assets/review-candidates/m105_106/{s['slug']}_{phase}_attempt01.png"
  dst=ROOT/f"character-assets/layers/character/combo/{s['slug']}_{phase}_refresh.png"
  actual=sha(src)
  if actual!=expected: raise SystemExit(f"{action} {phase} candidate SHA mismatch {actual}")
  dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
  if sha(dst)!=expected: raise SystemExit(f"{action} {phase} formal SHA mismatch")
  rel=str(dst.relative_to(ROOT))
  entry={
   "path":rel,"width":1448,"height":1086,"x":0,"y":0,"sha256":expected,
   "status":"FORMAL_QA_PASSED_RUNTIME_PENDING",
   "purpose":f"Luna M105-106 {action} formal {phase}; exact formal parent plus approved local BD cue.",
   "part":s["part"],"phase":phase,"hand":s["hand"],
   "notes":["Deterministic BD cue composition; fixed-drum visual QA PASS.",
            f"Dropbox exact bytes saved /ChatGPT/dtx-drum-flow/{s['slug']}_{phase}_attempt01.png",
            "Build run 35427052800 artifact 10578359682."]
  }
  if rel in by_path: by_path[rel].update(entry)
  else: assets.append(entry); by_path[rel]=entry
 txp=ROOT/s["tx"]; tx=json.load(open(txp,encoding="utf-8"))
 tx["status"]="FORMAL_QA_PASSED_RUNTIME_PENDING"
 for phase in ("hit","rebound"):
  ph=tx["phases"][phase]; ph["stage"]="FORMAL"; ph["sha256"]=s[phase+"Sha"]; ph["qaStatus"]="VISUAL_QA_PASS"
  ph["formalPath"]=f"character-assets/layers/character/combo/{s['slug']}_{phase}_refresh.png"
 tx["qa"].update({"static":"PASS","compositeVisual":"PASS","locality":"PASS_BD_CUE_ONLY","transition":"PASS_VISUAL"})
 tx["build"]={"workflowRun":35427052800,"artifactId":10578359682}
 tx["updatedAt"]=now
 tx.setdefault("notes",[]).append("Attempt01 exact bytes saved to Dropbox and promoted to formal paths after deterministic locality/fixed-drum visual QA.")
 txp.write_text(json.dumps(tx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
manifest["updatedAt"]=now
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
pp=ROOT/"character-assets/prototypes/luna_say_maybe_105_106/PROGRESS.json"
p=json.load(open(pp,encoding="utf-8")); p["status"]="FORMAL_QA_PASSED_RUNTIME_PENDING"; p["analysis"]["formalPairsReady"]=True
p["analysis"]["allMapped"]=False; p["analysis"]["dropboxSaved"]=True
p["analysis"]["shas"]={
 "BD+FT+SN:RF/R/L":{"hit":pairs["BD+FT+SN:RF/R/L"]["hitSha"],"rebound":pairs["BD+FT+SN:RF/R/L"]["reboundSha"]},
 "BD+FT:RF/L":{"hit":pairs["BD+FT:RF/L"]["hitSha"],"rebound":pairs["BD+FT:RF/L"]["reboundSha"]}
}
p["requiredNext"]="Register formal M105-106 frames/mappings, expand contiguous runtimeScope through M106, then run PC/Xperia public runtime QA."
p["updatedAt"]=now; pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("promoted M105-106 formal pairs")
