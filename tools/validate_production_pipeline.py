from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
state=load("character-assets/prototypes/luna_say_maybe_16m/CURRENT_PROJECT_STATE.json")
ledger=load("character-assets/prototypes/luna_say_maybe_16m/M5_PLUS_PROGRESS_LEDGER.json")
mapping=load("character-assets/prototypes/luna_say_maybe_16m/ACTION_KEY_ASSET_MAP.json")
queue=load("character-assets/prototypes/luna_say_maybe_16m/NEXT_ASSET_QUEUE.json")
staging=load("character-assets/prototypes/luna_say_maybe_16m/STAGING_SCHEMA.json")
lifecycle=load("character-assets/prototypes/luna_say_maybe_16m/ASSET_LIFECYCLE.json")
rejected=load("character-assets/prototypes/luna_say_maybe_16m/REJECTED_ASSET_REGISTRY.json")
failures=load("character-assets/prototypes/luna_say_maybe_16m/FAILURE_PATTERN_REGISTRY.json")
contacts=load("character-assets/prototypes/luna_say_maybe_16m/INSTRUMENT_CONTACT_POINTS.json")
assert state["liveRuntimeScope"]["measureStart"]==1 and state["liveRuntimeScope"]["measureEnd"]==8
pp=ledger.get("productionPipelineSpeedup")
assert pp and pp["id"]=="PRODUCTION_PIPELINE_SPEEDUP"
ids=[x["id"] for x in pp["queue"]]
assert ids[:25]==[f"SPEED-{i:03d}" for i in range(1,26)]
for x in pp["queue"]:
    for k in ("id","task","status","startedAt","completedAt","commitSha","evidence","outputFiles","blocker","nextAction"): assert k in x,(x["id"],k)
assert len(mapping["entries"])==30
assert queue["items"] and queue["items"][0]["actionKey"]=="RC+SN:R/L" and queue["items"][0]["phase"]=="hit"
assert queue["items"][1]["actionKey"]=="RC+SN:R/L" and queue["items"][1]["phase"]=="rebound"
assert set(staging["required"]) >= {"actionKey","runtimeKey","block","measureRange","hit","rebound"}
life={x["id"] for x in lifecycle["states"]}
for s in ("GENERATED_CANDIDATE","BINARY_QA_PASSED","STATIC_VISUAL_QA_PASSED","FORMAL_SAVED","RUNTIME_PENDING","RUNTIME_READY","LIVE_QA_PASSED","DONE","REJECTED","NEVER_USE"): assert s in life
assert len(failures["patterns"])>=10
assert set(contacts["parts"])=={"LC","HH","SN","HT","LT","FT","RC","RD","LP","LB","BD"}
deny={x.get("githubPath") for x in rejected["entries"] if x.get("githubPath")}
inventory=load("character-assets/prototypes/luna_say_maybe_16m/asset_inventory.json")
active=set(inventory["runtimeFrameMap"].values())
for p in inventory["runtimePhaseFrameMap"].values(): active.update(p.values())
active_paths={"character-assets/"+inventory["requiredFrames"][x]["path"] for x in active if x in inventory["requiredFrames"]}
assert not deny & active_paths
required=[
"tools/build-next-asset-queue.mjs","tools/build-character-generation-prompt.mjs","tools/derive-rebound-instruction.mjs",
"tools/character_candidate_qa.py","tools/build-character-qa-preview.py","tools/character_image_diff_metrics.py",
"tools/build-staging-json.mjs","tools/build-block-start-checklist.mjs","tools/find-reuse-candidates.mjs",
"tools/build-qa-sampling-and-risk.mjs","tools/build-qa-summary.mjs","tools/build-next-chat-handoff.mjs","tools/luna-production-path.mjs",
".github/workflows/luna-fast-path.yml",".github/workflows/luna-full-path.yml"
]
for p in required: assert (ROOT/p).is_file(),p
# Fast/full path static criteria: current M1-8 all approved+mapped; M9-16 contains blocked/pending assets.
by={x["actionKey"]:x for x in mapping["entries"]}
assert all(by[k]["classification"]=="REUSE_APPROVED" and by[k]["runtimeMapped"] for k in ["SN:L","SN:R","BD:RF","HH:R","BD+RC:RF/R","RD:R"])
assert by["RC+SN:R/L"]["classification"]=="BLOCKED"
assert by["BD+SN:RF/L"]["classification"]=="REUSE_NEEDS_RUNTIME_QA"
print("PASS production pipeline validation: queue schema, 30-key map, staging/lifecycle, rejected safety, tools/workflows, fast/full criteria, live scope 1-8")
