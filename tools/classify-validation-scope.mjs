import fs from "node:fs/promises";
const input=process.argv[2];if(!input)throw new Error("usage: node tools/classify-validation-scope.mjs <changed-files.txt> [out.json]");
const files=(await fs.readFile(input,"utf8")).split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
const hit=p=>files.some(f=>p.some(x=>f===x||f.startsWith(x)));
const evidenceOnly=files.length>0&&files.every(f=>
  f.startsWith("character-assets/edit-workspaces/")||
  f==="character-assets/prototypes/luna_say_maybe_16m/MOTION_DEFECT_BACKLOG.json"||
  f==="character-assets/prototypes/luna_say_maybe_16m/HOLD_REPAIR_PLAYBOOK.json"||
  f==="WORK_SYNC.md"||
  /^\.github\/.*(?:trigger|promote).*\.txt$/.test(f)
);
const flags={audio:hit(["tools/audio_pipeline/","site/audio-analysis.js","site/original-audio.js"]),chart:hit(["site/charts/","tools/chart_validation.py","tools/songsterr_gp_to_chart.py"]),runtime:hit(["site/character-prototype.js","character-assets/config/","character-assets/layers/"]),ui:hit(["site/app.js","site/styles.css","site/index.html","site/oshi-sketch/","tools/ui_contract_test.py","tools/oshi_sketch_smoke.js"]),pipeline:hit(["character-assets/prototypes/luna_say_maybe_16m/","tools/build-","tools/luna-","tools/production-","tools/start-pipeline-task.mjs","tools/check-pipeline-compliance.mjs",".github/workflows/luna-","tools/validate_production_pipeline.py"]),workflow:hit([".github/workflows/validate.yml"])};
const docsOnly=files.length>0&&files.every(f=>/\.(md|txt)$/.test(f)||f==="CHANGELOG.md");
const scope=evidenceOnly?"EVIDENCE_FAST":flags.audio?"AUDIO_FULL":(flags.chart||flags.runtime||flags.ui?"PRODUCT_FULL":(flags.pipeline||flags.workflow?"PIPELINE_FAST":docsOnly?"DOCS_FAST":"PRODUCT_FULL"));
const heavy=!["EVIDENCE_FAST","DOCS_FAST"].includes(scope);
const out={schemaVersion:2,files,scope,flags,evidenceOnly,run:{setupToolchains:heavy,installAudioDeps:scope==="AUDIO_FULL"||scope==="PRODUCT_FULL",audioTests:scope==="AUDIO_FULL"||scope==="PRODUCT_FULL",syntax:heavy,oshiSmoke:scope==="PRODUCT_FULL",chartValidation:heavy,planningValidation:heavy,pipelineValidation:heavy,pipelineSmoke:heavy,uiContract:scope==="PRODUCT_FULL"}};
const dest=process.argv[3]||"/tmp/validation-scope.json";await fs.writeFile(dest,JSON.stringify(out,null,2)+"\n");console.log(JSON.stringify(out,null,2));