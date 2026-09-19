#!/usr/bin/env python3
import argparse,json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference-model',required=True); ap.add_argument('--retargeted-pose',required=True)
    ap.add_argument('--output',required=True); ap.add_argument('--action-key'); ap.add_argument('--phase')
    a=ap.parse_args(); m=json.loads(Path(a.reference_model).read_text()); p=json.loads(Path(a.retargeted_pose).read_text())
    out={'schemaVersion':1,'mode':'AI_ASSISTED_CONSTRAINED_RENDER','actionKey':a.action_key,'phase':a.phase,
      'hardConstraints':{'targetHeadCount':p['targetHeadCount'],'joints':p['joints'],'appearance':m['appearanceConstraints'],
      'camera':m['cameraPolicy'],'forbidden':m['forbiddenChanges']},
      'postProcess':['tools/cowlick/apply_cowlick.py when crown patch required','tools/line_style/normalize_line_style.py','fixed-drum composite QA'],
      'rule':'AI may render only inside this numeric/semantic constraint package. It may not freely reinterpret pose, outfit, hair family, camera, proportions, or instrument target.'}
    Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__': main()
