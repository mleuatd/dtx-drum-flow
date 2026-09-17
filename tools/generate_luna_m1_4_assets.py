from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import random

R=Path(__file__).resolve().parents[1]
W,H=1448,1086
neutral_path=R/'character-assets/layers/character/base/neutral.png'
drum_path=R/'character-assets/layers/drum/drum_base.png'
neutral=Image.open(neutral_path).convert('RGBA')
drum=Image.open(drum_path).convert('RGBA')
if neutral.size!=(W,H):
    raise ValueError(f'neutral size {neutral.size} != {(W,H)}')
if drum.size!=(W,H):
    raise ValueError(f'drum size {drum.size} != {(W,H)}')

def poly_mask(points):
    m=Image.new('L',(W,H),0)
    ImageDraw.Draw(m).polygon(points,fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.2))

LEFT=poly_mask([(370,350),(430,345),(485,395),(515,440),(565,465),(585,505),(558,548),(510,560),(462,525),(420,470),(380,410)])
RIGHT=poly_mask([(480,300),(535,300),(565,345),(590,400),(600,455),(580,485),(545,490),(515,450),(500,400)])
FOOT=poly_mask([(525,760),(665,760),(710,840),(700,985),(620,1025),(525,995),(500,900)])

def transform_region(base,mask,angle,center,translate=(0,0)):
    layer=Image.new('RGBA',(W,H),(0,0,0,0))
    layer.paste(base,(0,0),mask)
    cleared=base.copy()
    alpha=cleared.getchannel('A')
    cleared.putalpha(ImageChops.multiply(alpha,ImageChops.invert(mask)))
    if angle:
        layer=layer.rotate(angle,resample=Image.Resampling.BICUBIC,center=center,expand=False)
    if translate!=(0,0):
        moved=Image.new('RGBA',(W,H),(0,0,0,0))
        moved.alpha_composite(layer,translate)
        layer=moved
    return Image.alpha_composite(cleared,layer)

def make_variant(left=None,right=None,foot=None):
    im=neutral.copy()
    if left: im=transform_region(im,LEFT,*left)
    if right: im=transform_region(im,RIGHT,*right)
    if foot: im=transform_region(im,FOOT,*foot)
    return im

variants={
'character-assets/layers/character/sn/hit_l.png':make_variant(left=(30,(555,500),(0,8))),
'character-assets/layers/character/sn/rebound_l.png':make_variant(left=(14,(555,500),(0,3))),
'character-assets/layers/character/sn/hit_r.png':make_variant(right=(-28,(575,455),(-3,6))),
'character-assets/layers/character/sn/rebound_r.png':make_variant(right=(-12,(575,455),(-1,3))),
'character-assets/layers/character/hh/hit_r.png':make_variant(right=(34,(575,455),(-12,0))),
'character-assets/layers/character/hh/rebound_r.png':make_variant(right=(16,(575,455),(-6,0))),
'character-assets/layers/character/bd/hit_rf.png':make_variant(foot=(9,(605,815),(10,10))),
'character-assets/layers/character/bd/rebound_rf.png':make_variant(foot=(4,(605,815),(5,5))),
'character-assets/layers/character/combo/bd_rc_hit.png':make_variant(right=(-48,(575,455),(6,-8)),foot=(9,(605,815),(10,10))),
'character-assets/layers/character/combo/bd_rc_rebound.png':make_variant(right=(-22,(575,455),(2,-3)),foot=(4,(605,815),(5,5))),
}
for rel,im in variants.items():
    p=R/rel;p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)

# Rebuild/augment the fixed drum layer against the 11-lane kit contract.
d=ImageDraw.Draw(drum)
random.seed(20260917)
def jl(points,w=3,n=3,j=2):
    for _ in range(n):
        pts=[(x+random.randint(-j,j),y+random.randint(-j,j)) for x,y in points]
        d.line(pts,fill=(15,15,15,245),width=w,joint='curve')
def re(box,w=3,n=4,j=3,fill=None):
    if fill is not None:d.ellipse(box,fill=fill)
    x0,y0,x1,y1=box
    for _ in range(n):
        b=(x0+random.randint(-j,j),y0+random.randint(-j,j),x1+random.randint(-j,j),y1+random.randint(-j,j))
        d.ellipse(b,outline=(15,15,15,245),width=w)

# LT: convert the former stool-like foreground element into a drum shell.
d.rectangle((660,700,900,800),fill=(255,255,255,235))
re((645,655,920,755),3,5,3,(255,255,255,235))
re((660,748,905,825),3,4,3,(255,255,255,235))
jl([(660,705),(665,785),(680,815)],3,4,3);jl([(900,705),(900,790),(888,820)],3,4,3)
for x in (690,755,820,875):
    jl([(x,710),(x,800)],2,3,2);d.rectangle((x-5,735,x+5,755),outline=(20,20,20,230),width=2)
# RD: dedicated ride cymbal and stand in the middle-right zone.
re((730,330,1015,435),3,5,4,(255,255,255,220));re((842,365,885,405),2,3,2,None)
jl([(872,398),(850,680)],3,5,3);jl([(850,680),(805,815)],3,4,3);jl([(850,680),(895,815)],3,4,3)
# LP: visible hi-hat pedal under the HH stand.
d.polygon([(210,890),(270,890),(294,932),(228,940)],fill=(255,255,255,220))
jl([(210,890),(270,890),(294,932),(228,940),(210,890)],3,5,3)
for y in (900,910,920):jl([(230,y),(278,y+10)],1,2,1)
jl([(255,890),(285,590)],2,4,2)
# LB: left-foot bass pedal/linkage beside the existing BD pedal.
d.polygon([(370,875),(430,862),(455,930),(390,948)],fill=(255,255,255,220))
jl([(370,875),(430,862),(455,930),(390,948),(370,875)],3,5,3)
for i in range(4):jl([(390+i*10,885),(420+i*8,930)],1,2,1)
jl([(430,875),(505,870)],2,4,2);jl([(505,870),(545,770)],2,4,2);re((530,748,550,770),2,3,2,(255,255,255,220))
for _ in range(12):
    x=random.randint(680,890);y=random.randint(730,810);jl([(x,y),(x+random.randint(-30,30),y+random.randint(20,45))],1,1,1)
drum.save(drum_path,optimize=True)

print('generated variants',len(variants))
print('drum rebuilt',drum_path)
print('neutral preserved',neutral_path)
