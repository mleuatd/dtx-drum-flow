import fs from "node:fs/promises";
const base="character-assets/prototypes/luna_say_maybe_16m";
const task=(process.argv[2]||"").trim();if(!task)throw new Error("usage: node tools/start-pipeline-task.mjs <task-category> [out.json]");
const read=async p=>JSON.parse(await fs.readFile(p,"utf8"));
const state=await read(base+"/CURRENT_PROJECT_STATE.json");
const policy=await read(base+"/PIPELINE_USAGE_POLICY.json");
const route=policy.taskRouting[task]||null;
const out={schemaVersion:1,startedAt:new Date().toISOString(),taskCategory:task,status:route?"PIPELINE_REQUIRED":"ROUTE_REVIEW_REQUIRED",
 requiredTools:route||[],repository:state.repository,branch:state.branch,liveRuntimeScope:state.liveRuntimeScope,
 currentNextWork:state.nextRecommendedWork,manualOverrideAllowed:!route,manualOverrideRequiredIfSkipped:!!route,
 completionEvidence:[],notes:route?["Use each required tool/workflow where applicable before manual equivalent."]:["Search PRODUCTION_PIPELINE.md and repository tools before manual work."]};
const dest=process.argv[3]||base+"/ACTIVE_PIPELINE_SESSION.json";await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");
console.log(JSON.stringify({dest,status:out.status,requiredTools:out.requiredTools},null,2));