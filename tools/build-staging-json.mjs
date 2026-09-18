import fs from "node:fs/promises";import crypto from "node:crypto";
const base="character-assets/prototypes/luna_say_maybe_16m";
const actionKey=process.argv[2],hit=process.argv[3],rebound=process.argv[4];
if(!actionKey||!hit||!rebound)throw new Error("usage: node tools/build-staging-json.mjs <ACTION_KEY> <hit-source> <rebound-source> [out.json]");
const read=async p=>JSON.parse(await fs.readFile(p,"utf8"));
const map=await read(base+"/ACTION_KEY_ASSET_MAP.json");const blocks=await read(base+"/FULL_SONG_IMPLEMENTATION_BLOCK_PLAN.json");
const entry=map.entries.find(x=>x.actionKey===actionKey);if(!entry)throw new Error("unknown actionKey "+actionKey);
const digest=async p=>{try{const b=await fs.readFile(p);return crypto.createHash("sha256").update(b).digest("hex")}catch{return null}};
const block=blocks.blocks.find(b=>entry.firstMeasure>=b.measureStart&&entry.firstMeasure<=b.measureEnd);
const safe=s=>s.toLowerCase().replace(/\+/g,"_").replace(/[:/]/g,"_").replace(/[^a-z0-9_]+/g,"_");
const root=safe(actionKey);
const out={schemaVersion:1,createdAt:new Date().toISOString(),actionKey,runtimeKey:entry.limbAwareRuntimeKey||entry.runtimeKey,block:block?.blockId||null,measureRange:block?[block.measureStart,block.measureEnd]:null,
 hit:{source:hit,sha256:await digest(hit),dimensions:[1448,1086],dropboxPath:null,githubPath:entry.hitAsset||null,binaryQa:null,visualQa:null},
 rebound:{source:rebound,sha256:await digest(rebound),dimensions:[1448,1086],dropboxPath:null,githubPath:entry.reboundAsset||null,binaryQa:null,visualQa:null},
 manifestStatus:entry.manifestStatus||"ABSENT",qaStatus:"DRAFT",registrationStatus:"NOT_REGISTERED",lifecycleStatus:"GENERATED_CANDIDATE",ledgerStatus:"IN_PROGRESS"};
const dest=process.argv[5]||base+"/staging/"+root+".json";await fs.mkdir(dest.split("/").slice(0,-1).join("/"),{recursive:true});await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");console.log(JSON.stringify({dest,actionKey},null,2));