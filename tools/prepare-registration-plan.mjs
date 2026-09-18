import fs from "node:fs/promises";
const stagingPath=process.argv[2];if(!stagingPath)throw new Error("usage: node tools/prepare-registration-plan.mjs <staging.json> [out.json]");
const s=JSON.parse(await fs.readFile(stagingPath,"utf8"));const missing=[];for(const p of ["actionKey","runtimeKey","hit","rebound"])if(!s[p])missing.push(p);
if(missing.length)throw new Error("staging missing "+missing.join(","));
const out={schemaVersion:1,source:stagingPath,actionKey:s.actionKey,preconditions:["hit/rebound binary QA reviewed","static visual QA PASS","not rejected","formal GitHub paths decided","Dropbox metadata recorded"],steps:[
 {order:1,action:"verify source SHA/dimensions against staging"},
 {order:2,action:"save/copy approved hit+rebound to formal GitHub paths"},
 {order:3,action:"update assets_manifest.json"},
 {order:4,action:"update ACTION_KEY_ASSET_MAP.json"},
 {order:5,action:"update asset_inventory requiredFrames; runtime mapping only if RUNTIME_READY"},
 {order:6,action:"update M5_PLUS_PROGRESS_LEDGER.json and CURRENT_PROJECT_STATE.json"},
 {order:7,action:"run validate + Character asset validation"},
 {order:8,action:"commit/push using COMMIT_BOUNDARY_RULES.md"}
],safety:"This tool only prepares a registration plan; it never promotes binary bytes or changes live runtimeScope."};
const dest=process.argv[3]||stagingPath.replace(/\.json$/,".registration-plan.json");await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");console.log(JSON.stringify({dest,actionKey:s.actionKey},null,2));