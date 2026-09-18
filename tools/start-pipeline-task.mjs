import fs from "node:fs/promises";
import { spawnSync } from "node:child_process";
const base="character-assets/prototypes/luna_say_maybe_16m";
const task=(process.argv[2]||"").trim();if(!task)throw new Error("usage: node tools/start-pipeline-task.mjs <task-category> [out.json]");
const run=(cmd,args)=>{const x=spawnSync(cmd,args,{encoding:"utf8",stdio:["ignore","pipe","pipe"]});if(x.status!==0)throw new Error(cmd+" "+args.join(" ")+" failed: "+x.stderr);return x.stdout};
run("node",["tools/build-pipeline-context-cache.mjs",base+"/PIPELINE_CONTEXT_CACHE.json"]);
run("node",["tools/audit-pipeline-efficiency.mjs",base+"/AUTO_OPTIMIZATION_REPORT.json"]);
const read=async p=>JSON.parse(await fs.readFile(p,"utf8"));
const state=await read(base+"/CURRENT_PROJECT_STATE.json");
const policy=await read(base+"/PIPELINE_USAGE_POLICY.json");
const cache=await read(base+"/PIPELINE_CONTEXT_CACHE.json");
const audit=await read(base+"/AUTO_OPTIMIZATION_REPORT.json");
const route=policy.taskRouting[task]||null;
const out={schemaVersion:2,startedAt:new Date().toISOString(),taskCategory:task,status:route?"PIPELINE_REQUIRED":"ROUTE_REVIEW_REQUIRED",
 requiredTools:route||[],repository:state.repository,branch:state.branch,liveRuntimeScope:state.liveRuntimeScope,
 currentNextWork:state.nextRecommendedWork,nextAsset:cache.nextAsset||null,contextCache:base+"/PIPELINE_CONTEXT_CACHE.json",
 autoOptimizationReport:base+"/AUTO_OPTIMIZATION_REPORT.json",autoOptimizationSuggestions:audit.suggestions||[],
 manualOverrideAllowed:!route,manualOverrideRequiredIfSkipped:!!route,completionEvidence:[],
 notes:route?["Use each required tool/workflow where applicable before manual equivalent.","Prefer PIPELINE_CONTEXT_CACHE.json for repeated read-heavy planning."]:["Search PRODUCTION_PIPELINE.md and repository tools before manual work."]};
const dest=process.argv[3]||base+"/ACTIVE_PIPELINE_SESSION.json";await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");
console.log(JSON.stringify({dest,status:out.status,requiredTools:out.requiredTools,nextAsset:out.nextAsset?.id||null,autoOptimizationSuggestions:out.autoOptimizationSuggestions.length},null,2));