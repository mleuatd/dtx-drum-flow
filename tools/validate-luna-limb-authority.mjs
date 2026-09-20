import fs from "node:fs";
import {execFileSync} from "node:child_process";

const chartPath="site/charts/luna_say_maybe/Luna_say_maybe_FINAL_notes.json";
const overridePath="site/charts/luna_say_maybe/Luna_say_maybe_limb_observed_overrides.json";
const EXPECTED_CHART_BLOB="c842c44264d7f32c4bf4b05d97b8df243827a81d";

const blob=execFileSync("git",["hash-object",chartPath],{encoding:"utf8"}).trim();
if(blob!==EXPECTED_CHART_BLOB){
  throw new Error("Luna FINAL chart drift is forbidden: expected "+EXPECTED_CHART_BLOB+" got "+blob);
}

const chart=JSON.parse(fs.readFileSync(chartPath,"utf8"));
const overrides=JSON.parse(fs.readFileSync(overridePath,"utf8"));
const noteKeys=new Set((chart.notes||[]).map(n=>Number(n.time).toFixed(6)+"|"+n.part));
const validLimbs=new Set(["L","R","LF","RF"]);
const seen=new Set();

for(const o of overrides.overrides||[]){
  const k=Number(o.time).toFixed(6)+"|"+o.part;
  if(!noteKeys.has(k)) throw new Error("Observed limb override does not match exact fixed chart note: "+k);
  if(!validLimbs.has(o.limb)) throw new Error("Invalid observed limb "+o.limb+" at "+k);
  if(seen.has(k)) throw new Error("Duplicate observed limb override: "+k);
  seen.add(k);
  if(!o.referenceId) throw new Error("Observed limb override requires referenceId: "+k);
}

console.log(JSON.stringify({
  ok:true,
  chartBlob:blob,
  fixedNotes:(chart.notes||[]).length,
  observedOverrides:(overrides.overrides||[]).length
},null,2));
