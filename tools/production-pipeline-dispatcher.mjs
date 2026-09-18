import fs from "node:fs/promises";
const base="character-assets/prototypes/luna_say_maybe_16m";
const task=(process.argv[2]||"").trim(); if(!task)throw new Error("usage: node tools/production-pipeline-dispatcher.mjs <task-category> [out.json]");
const policy=JSON.parse(await fs.readFile(base+"/PIPELINE_USAGE_POLICY.json","utf8"));
const route=policy.taskRouting[task];
const known=Object.keys(policy.taskRouting);
const result=route?{status:"USE_PIPELINE",task,required:route,manualAllowed:false,rule:"Use listed repository tool/workflow before manual equivalent."}:{status:"NO_EXACT_ROUTE",task,required:["Read PRODUCTION_PIPELINE.md and search existing tools before manual work"],manualAllowed:true,manualOverrideRequired:true,knownCategories:known};
const out=process.argv[3];if(out)await fs.writeFile(out,JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));