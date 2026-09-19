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
usage_policy=load("character-assets/prototypes/luna_say_maybe_16m/PIPELINE_USAGE_POLICY.json")
auto_policy=load("character-assets/prototypes/luna_say_maybe_16m/AUTO_OPTIMIZATION_POLICY.json")
contacts=load("character-assets/prototypes/luna_say_maybe_16m/INSTRUMENT_CONTACT_POINTS.json")
assert state["liveRuntimeScope"]["measureStart"]==1 and isinstance(state["liveRuntimeScope"]["measureEnd"], int) and 8 <= state["liveRuntimeScope"]["measureEnd"] <= 148
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
".github/workflows/luna-fast-path.yml",".github/workflows/luna-full-path.yml",".github/workflows/luna-candidate-qa.yml",
"tools/production-pipeline-dispatcher.mjs","tools/start-pipeline-task.mjs","tools/check-pipeline-compliance.mjs","tools/build-pipeline-context-cache.mjs","tools/classify-validation-scope.mjs","tools/audit-pipeline-efficiency.mjs",
"character-assets/prototypes/luna_say_maybe_16m/PIPELINE_USAGE_POLICY.json","character-assets/prototypes/luna_say_maybe_16m/PIPELINE_USAGE_POLICY.md","character-assets/prototypes/luna_say_maybe_16m/AUTO_OPTIMIZATION_POLICY.json",
"character-assets/prototypes/luna_say_maybe_16m/PRODUCTION_PIPELINE.md","character-assets/prototypes/luna_say_maybe_16m/COMMIT_BOUNDARY_RULES.md","character-assets/prototypes/luna_say_maybe_16m/AUTONOMY_BOUNDARIES.md"
]
for p in required: assert (ROOT/p).is_file(),p
# Fast/full path static criteria: current M1-8 all approved+mapped; M9-16 may contain blocked or formal-pair runtime-QA-pending assets.
by={x["actionKey"]:x for x in mapping["entries"]}
assert all(by[k]["classification"]=="REUSE_APPROVED" and by[k]["runtimeMapped"] for k in ["SN:L","SN:R","BD:RF","HH:R","BD+RC:RF/R","RD:R"])
assert by["RC+SN:R/L"]["classification"] in {"BLOCKED","REUSE_NEEDS_RUNTIME_QA","REUSE_APPROVED"}
assert by["BD+SN:RF/L"]["classification"] in {"REUSE_NEEDS_RUNTIME_QA","REUSE_APPROVED"}
print(f"PASS production pipeline validation: queue schema, 30-key map, staging/lifecycle, rejected safety, tools/workflows, fast/full criteria, live scope 1-{state['liveRuntimeScope']['measureEnd']}")

# Sampling, screenshot naming, fast/full and handoff generator implementation contracts.
sampling_src=(ROOT/"tools/build-qa-sampling-and-risk.mjs").read_text(encoding="utf-8")
assert "first" in sampling_src and "middle" in sampling_src and "shortest-gap" in sampling_src and "longest-gap" in sampling_src and "high-risk" in sampling_src
runner_src=(ROOT/"tools/luna-block-qa.mjs").read_text(encoding="utf-8")
assert "QA_SAMPLING_FILE" in runner_src and "__p_" in runner_src and "__c_" in runner_src and "__n_" in runner_src
path_src=(ROOT/"tools/luna-production-path.mjs").read_text(encoding="utf-8")
assert "FAST_PATH" in path_src and "FULL_PATH" in path_src
next_chat_src=(ROOT/"tools/build-next-chat-handoff.mjs").read_text(encoding="utf-8")
assert "NEXT_IMPLEMENTATION_HANDOFF.md" in next_chat_src and "NEXT_CHAT_COMMAND.md" in next_chat_src
assert Path(BASE/"STAGING_SCHEMA.json").is_file()
assert Path(BASE/"ASSET_LIFECYCLE.json").is_file()
assert Path(BASE/"ACTION_KEY_COMPLETION_TEMPLATE.json").is_file()
assert Path(BASE/"FAILURE_PATTERN_REGISTRY.json").is_file()

# Mandatory pipeline-first usage contracts.
assert usage_policy["status"]=="CURRENT_MANDATORY"
assert usage_policy["principle"]=="PIPELINE_FIRST_NO_MANUAL_DUPLICATION"
assert usage_policy["compliance"]["dispatcherRequired"] is True
assert "build-generation-prompt" in usage_policy["taskRouting"]
assert state.get("pipelineUsagePolicy",{}).get("status")=="MANDATORY"
assert state["pipelineUsagePolicy"]["dispatcher"]=="tools/production-pipeline-dispatcher.mjs"
assert any("production-pipeline-dispatcher.mjs" in x for x in state["instructionsForNextChat"])
assert any("MANUAL_OVERRIDE" in x for x in state["instructionsForNextChat"])
pipeline_doc=(BASE/"PRODUCTION_PIPELINE.md").read_text(encoding="utf-8")
assert "Mandatory execution entry" in pipeline_doc and "production-pipeline-dispatcher.mjs" in pipeline_doc
handoff=(BASE/"NEXT_IMPLEMENTATION_HANDOFF.md").read_text(encoding="utf-8")
assert "Mandatory pipeline-first execution" in handoff

# Autonomous optimization contracts.
assert auto_policy["status"]=="CURRENT_MANDATORY"
assert auto_policy["thresholds"]["highPriorityAutoImplement"] is True
assert "session-bootstrap" in usage_policy["taskRouting"]
assert "optimize-pipeline" in usage_policy["taskRouting"]
assert state.get("autonomousOptimization",{}).get("status")=="MANDATORY"
assert "audit-pipeline-efficiency.mjs" in state["autonomousOptimization"]["efficiencyAudit"]
validate_yml=(ROOT/".github/workflows/validate.yml").read_text(encoding="utf-8")
assert "Classify validation scope" in validate_yml and "classify-validation-scope.mjs" in validate_yml
start_src=(ROOT/"tools/start-pipeline-task.mjs").read_text(encoding="utf-8")
assert "build-pipeline-context-cache.mjs" in start_src and "audit-pipeline-efficiency.mjs" in start_src
