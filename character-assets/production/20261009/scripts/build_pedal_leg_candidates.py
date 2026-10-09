"""Source-pixel local pedal/rear-boot repair. Candidate only until visible review."""
from pathlib import Path
import json, runpy, hashlib, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates

R=next(p for p in Path(__file__).resolve().parents if (p/'character-assets').is_dir())
P=R/'character-assets/production/20261009'; Q=P/'qa'; C=P/'candidates'
W,H=1448,1086
for p in [Q,C]:p.mkdir(parents=True,exist_ok=True)
B=P/'baseline'
work=R.parent/'work_output'
for sub in ['sources','previews','qa','variants/bd']:(work/sub).mkdir(parents=True,exist_ok=True)
shutil.copy(R/'character-assets/layers/character/base/neutral.png',work/'sources/neutral.png')
shutil.copy(B/'drum_base_before.png',work/'sources/drum_fixed.png')
d=runpy.run_path(str(R/'character-assets/production/20261008/scripts/make_bd_source_pair.py'))
kit=Image.open(B/'drum_base_before.png').convert('RGBA'); ka=np.array(kit)
def mask(points,size=(W,H)):
    im=Image.new('L',size);ImageDraw.Draw(im).polygon(points,fill=255);return im
def rough_line(draw,points,width=2):
    for a,b in zip(points,points[1:]):
        distance=np.hypot(b[0]-a[0],b[1]-a[1]); count=max(1,int(distance/5))
        for i in range(count):
            f=i/count;g=(i+1)/count
            draw.line((a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,a[0]+(b[0]-a[0])*g,a[1]+(b[1]-a[1])*g),fill=(20,20,20,255),width=width)

# Isolate the existing footboard/frame, not the bass shell or other stands.
oldmask=mask([(685,822),(751,822),(766,846),(780,939),(752,978),(714,1028),(707,1045),(613,1043),(611,1015),(631,980),(650,937),(666,895),(670,865),(678,845)])
old=np.array(oldmask)>0
part=ka.copy();part[~old]=0
angle=np.deg2rad(-18);co,si=np.cos(angle),np.sin(angle)
cx,cy=704,932;tx,ty=-25,0
yy,xx=np.mgrid[:H,:W]
sx=cx+co*(xx-cx-tx)+si*(yy-cy-ty);sy=cy-si*(xx-cx-tx)+co*(yy-cy-ty)
pedal=np.stack([map_coordinates(part[:,:,k],[sy,sx],order=1,mode='constant',cval=0) for k in range(4)],axis=2).astype('uint8')

# Repair only previously occluded background inside the old pedal silhouette.
background=Image.new('RGBA',(W,H)); bgdraw=ImageDraw.Draw(background)
bgdraw.ellipse((555,552,938,963),fill='white')
face_alpha=np.array(background)[:,:,3].copy()
texture=kit.crop((795,710,845,760))
for by in range(810,970,50):
    for bx in range(610,790,50):background.alpha_composite(texture,(bx,by))
bgarray=np.array(background);bgarray[face_alpha==0]=0;background=Image.fromarray(bgarray)
bgdraw=ImageDraw.Draw(background)
for offset,width in [(0,4),(7,3),(13,2)]:
    bgdraw.ellipse((555+offset,552+offset,938-offset,963-offset),outline=(25,25,25,255),width=width)
# Source bass-head pencil texture; no heavy invented hatch lines.
ba=np.array(background); repaired=ka.copy();repaired[old]=ba[old]
newkit=Image.alpha_composite(Image.fromarray(repaired),Image.fromarray(pedal))
# The fixed beater remains. A small local drive connector joins the moved pedal.
connector=Image.new('RGBA',(W,H)); cd=ImageDraw.Draw(connector)
rough_line(cd,[(730,819),(714,825),(696,832),(675,842)],3)
rough_line(cd,[(732,825),(715,831),(697,838),(677,848)],2)
for x,y in [(730,822),(675,845)]:cd.ellipse((x-4,y-4,x+4,y+4),fill='white',outline='black',width=2)
newkit=Image.alpha_composite(newkit,connector)
allowed=old|(pedal[:,:,3]>0)|(np.array(connector)[:,:,3]>0)
assert np.array_equal(np.array(newkit)[~allowed],ka[~allowed])
newkit.save(C/'drum_base_candidate.png');Image.fromarray(allowed.astype('uint8')*255).save(Q/'drum_change_mask.png')

# Keep the donor's rear shaft and heel. Move its three-quarter forefoot behind
# the shaft, rather than twisting the ankle toward the old slanted footboard.
b=d['b'].copy();bb=np.array(b)
toe_mask=mask([(173,153),(259,153),(259,276),(160,276),(164,243),(171,220),(172,207),(166,192),(174,179)],b.size)
tm=np.array(toe_mask)>0; shaft=bb.copy();shaft[tm]=0
toe=bb.copy();toe[~tm]=0
rear=Image.fromarray(shaft)
rd=ImageDraw.Draw(rear)
rough_line(rd,[(173,153),(174,179),(166,192),(172,207),(171,220),(164,243),(160,276)],1)
rear.save(Q/'rear_boot_projection.png')
src=np.array([[128,110,1],[184,191,1],[122,310,1]],float)
dst=np.array([[678,835],[723,896],[667,979]],float)
A=np.linalg.solve(src,dst).T;M=np.vstack([A,[0,0,1]]);inv=np.linalg.inv(M)
boot=rear.transform((W,H),Image.Transform.AFFINE,tuple(inv[:2].ravel()),Image.Resampling.BICUBIC)
bo=np.array(boot);bo[:817]=0;boot=Image.fromarray(bo)
skin=d['skin'].copy(); skin_img=Image.new('RGBA',(W,H));skin_img.alpha_composite(Image.fromarray(skin),(4,5))
skin_new=np.array(skin_img);skin_new[:730]=0
# Preserve the exact knee boundary at the upper edge, then blend the small shift.
original_skin=d['skin'];blend=np.clip((yy-730)/75,0,1)[:,:,None]
skin_new=(original_skin*(1-blend)+skin_new*blend).astype('uint8')
leg=np.array(Image.alpha_composite(Image.fromarray(skin_new),boot))
toex,toey=681,913
toe_lock=np.exp(-((xx-toex)**2+(yy-toey)**2)/(2*16**2))
lift=6*np.clip((yy-730)/80,0,1)*(1-toe_lock)
raised=np.stack([map_coordinates(leg[:,:,k],[yy+lift,xx],order=1,mode='constant',cval=0) for k in range(4)],axis=2).astype('uint8')
base=d['base']; original=np.array(Image.open(B/'neutral_performance_ready_before.png').convert('RGBA'))
roi=np.zeros((H,W),bool);roi[730:1005,560:800]=True
states={}
for label,part in [('hit',leg),('rebound',raised),('ready',raised)]:
    template=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(part)))
    out=original.copy();out[roi]=template[roi]
    assert np.array_equal(out[~roi],original[~roi]);states[label]=Image.fromarray(out)
    states[label].save(C/f'{label}_candidate.png')
    preview=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(W,H),'white'),newkit),states[label])
    preview.save(Q/f'{label}_composite.png')
    preview.crop((560,700,825,1055)).resize((530,710)).save(Q/f'{label}_detail.png')
strip=Image.new('RGB',(1590,710),'white')
for i,label in enumerate(['ready','hit','rebound']):
    strip.paste(Image.open(Q/f'{label}_detail.png').convert('RGB'),(i*530,0))
    ImageDraw.Draw(strip).text((i*530+8,8),label,fill='black')
strip.save(Q/'triplet_detail.png')
beige=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(W,H),(248,246,237,255)),newkit),states['ready'])
beige.crop((550,700,830,1060)).resize((560,720)).save(Q/'beige_background_detail.png')
frames=[Image.open(Q/f'{s}_composite.png').convert('RGB').resize((724,543)) for s in ['ready','hit','rebound','ready']]
frames[0].save(Q/'candidate_motion.gif',save_all=True,append_images=frames[1:],duration=[500,250,350,500],loop=0)
before=Image.alpha_composite(Image.alpha_composite(Image.new('RGBA',(W,H),'white'),kit),Image.fromarray(original))
comparison=Image.new('RGB',(1448,543),'white');comparison.paste(before.resize((724,543)).convert('RGB'),(0,0));comparison.paste(frames[0],(724,0));comparison.save(Q/'before_after.png')
report={'status':'CANDIDATE_STATIC_INVARIANTS_PASS_VISIBLE_REVIEW_PENDING','baselineCommit':'33e17e37fd235ad474b61219e664670d9818c344','drumChangedPixels':int(np.any(np.array(newkit)!=ka,axis=2).sum()),'drumOutsideMaskExact':True,'characterOutsideFootRoiExact':True,'characterRoi':[560,730,800,1005],'pedalTransform':{'rotationDegrees':-18,'translation':[-25,0]},'toeProjection':'Existing rear-boot shaft preserved; forefoot fully occluded behind shaft','toePivot':[toex,toey],'heelLiftPixels':6,'generatedWholeImage':False,'finalDrumLayers':1}
(Q/'candidate_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
