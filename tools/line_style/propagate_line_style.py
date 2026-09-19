#!/usr/bin/env python3
import argparse,json,subprocess,sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',required=True); ap.add_argument('--profile',required=True); ap.add_argument('--continue-on-fail',action='store_true')
    args=ap.parse_args(); doc=json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    root=Path(__file__).resolve().parent; results=[]
    for item in doc.get('items',[]):
        inp=item['input']; out=item['output']; q=item['qaReport']; v=item['verifyReport']; sha=item.get('expectedSha256')
        cmd=[sys.executable,str(root/'normalize_line_style.py'),'--input',inp,'--profile',args.profile,'--output',out,'--qa-report',q]
        if sha: cmd += ['--expected-source-sha256',sha]
        rc1=subprocess.run(cmd).returncode; rc2=99
        if rc1==0:
            cmd2=[sys.executable,str(root/'verify_line_style_normalization.py'),'--before',inp,'--after',out,'--profile',args.profile,'--report',v]
            if sha: cmd2 += ['--expected-source-sha256',sha]
            rc2=subprocess.run(cmd2).returncode
        ok=rc1==0 and rc2==0; results.append({'input':inp,'output':out,'pass':ok,'normalizeRc':rc1,'verifyRc':rc2})
        if not ok and not args.continue_on_fail: break
    print(json.dumps({'results':results},ensure_ascii=False))
    if results and not all(x['pass'] for x in results): raise SystemExit(2)
if __name__=='__main__': main()
