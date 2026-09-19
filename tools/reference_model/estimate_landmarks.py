#!/usr/bin/env python3
import argparse,json
from pathlib import Path

POSE_KEYS=['head_top','chin','neck','shoulder_l','shoulder_r','elbow_l','elbow_r','wrist_l','wrist_r','hip_l','hip_r','knee_l','knee_r','ankle_l','ankle_r']
HAIR_KEYS=['crown','hair_left_extent','hair_right_extent','hair_back_extent','hair_tip_left','hair_tip_center','hair_tip_right','side_lock_l','side_lock_r']
GARMENT_KEYS=['jacket_shoulder_l','jacket_shoulder_r','lapel_l','lapel_r','jacket_hem_l','jacket_hem_r','skirt_hem_l','skirt_hem_r']
FOOT_KEYS=['boot_ankle_l','boot_ankle_r','boot_toe_l','boot_toe_r','heel_l','heel_r']

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--view-manifest',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--provider',default='manual-template',choices=['manual-template'])
    a=ap.parse_args()
    m=json.loads(Path(a.view_manifest).read_text())
    views=[]
    for v in m['views']:
        views.append({'index':v['index'],'frameIndex':v['frameIndex'],'yawDeg':v['yawDeg'],'sourceFrameSha256':v.get('sha256'),
          'provider':a.provider,'status':'NEEDS_OBSERVATION',
          'coordinateSystem':{'raw':'pixels','normalized':'0..1 by source width/height','headUnit':'relative to head_top->chin after observation'},
          'pose':{k:None for k in POSE_KEYS},'hair':{k:None for k in HAIR_KEYS},'garment':{k:None for k in GARMENT_KEYS},
          'footwear':{k:None for k in FOOT_KEYS},'silhouette':{'bbox':None},'confidence':{}})
    out={'schemaVersion':1,'type':'multiview_landmarks','sourceManifest':a.view_manifest,'views':views}
    Path(a.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'views':len(views),'output':a.output}))
if __name__=='__main__':main()
