import fs from "node:fs/promises";

const base="character-assets/prototypes/luna_say_maybe_16m";
const actionKey=(process.argv[2]||"").trim();
const phase=(process.argv[3]||"hit").trim().toLowerCase();
const failure=(process.argv[4]||"UNKNOWN").trim();
const repeat=Math.max(1,Number(process.argv[5]||1));
const outPath=process.argv[6]||base+"/RETRY_DECISION.json";
if(!actionKey||!["hit","rebound"].includes(phase)) throw new Error("usage: node tools/character-retry-controller.mjs <ACTION_KEY> <hit|rebound> <FAILURE_ID> [repeatCount] [out.json]");

const rules={
  "FAIL-EDIT-NULL":{
    first:"VERIFY_VISUAL_CONTINUITY",
    second:"SWITCH_TO_LOCAL_MASK_EDIT",
    guidance:[
      "Do not reject solely because edit_op is null.",
      "First compare identity/camera/stool/body-scale and changed-region locality against approved neutral.",
      "If visual continuity passes and only the intended limb region changes, allow candidate to continue to contact QA.",
      "If continuity fails, do not repeat the same image-generation strategy; switch to local masked edit."
    ]
  },
  "FAIL-FRONT-CHAR":{
    first:"SWITCH_TO_LOCAL_MASK_EDIT",
    second:"SWITCH_TO_APPROVED_LIMB_PATCH",
    guidance:["Never retry the same full-frame generation prompt.","Preserve baseline outside a tight limb/shoulder mask."]
  },
  "FAIL-CAMERA-JUMP":{
    first:"SWITCH_TO_LOCAL_MASK_EDIT",
    second:"SWITCH_TO_APPROVED_LIMB_PATCH",
    guidance:["Lock all pixels outside the target limb region.","Do not regenerate face/hair/torso/stool."]
  },
  "FAIL-STOOL-SHIFT":{
    first:"LOCK_CORE_AND_RETRY_LOCAL",
    second:"SWITCH_TO_APPROVED_LIMB_PATCH",
    guidance:["Treat pelvis/stool/core as immutable pixels.","Only edit the target limb and minimum shoulder connection."]
  },
  "FAIL-RC-WRONG-SIDE":{first:"CONTACT_GUIDED_LOCAL_RETRY",second:"CONTACT_GUIDED_APPROVED_PATCH",guidance:["Use INSTRUMENT_CONTACT_POINTS and fixed-drum overlay before retry.","Change target direction, not character identity."]},
  "FAIL-RD-WRONG-SIDE":{first:"CONTACT_GUIDED_LOCAL_RETRY",second:"CONTACT_GUIDED_APPROVED_PATCH",guidance:["Use INSTRUMENT_CONTACT_POINTS and fixed-drum overlay before retry.","Change target direction, not character identity."]},
  "FAIL-DRUM-LEAK":{first:"MASK_TO_CHARACTER_ONLY",second:"ALPHA_CLEANUP_ONLY",guidance:["Do not regenerate pose if pose is otherwise valid.","Remove only leaked hardware/background pixels."]},
  "LOCAL_EDIT_ARTIFACT":{first:"REDUCE_EDIT_REGION",second:"USE_APPROVED_LIMB_PATCH",guidance:["Do not repeat the same raster transform.","Use smaller feathered mask or a registered approved limb source."]}
};
const rule=rules[failure]||{first:"TARGETED_RETRY",second:"CHANGE_STRATEGY",guidance:["Retry only the failed property.","Never repeat an identical failed strategy more than once."]};
const strategy=repeat<=1?rule.first:rule.second;
const hardStopSameStrategy=repeat>=2;
const result={
  schemaVersion:1,
  generatedAt:new Date().toISOString(),
  actionKey,phase,failureId:failure,repeatCount:repeat,
  decision:strategy,
  hardStopSameStrategy,
  rules:[
    "A candidate can fail one strategy once; the same failure on the next attempt forces a strategy change.",
    "edit_op=null is evidence, not an automatic rejection by itself; visual continuity + locality decide whether it is a redraw.",
    "Binary validity failures remain hard failures.",
    "Rejected/NEVER_USE bytes remain forbidden.",
    "Never advance hit -> rebound until hit passes."
  ],
  guidance:rule.guidance,
  nextPromptMode:strategy
};
await fs.writeFile(outPath,JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));
