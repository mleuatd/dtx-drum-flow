from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from pathlib import Path
O=Path('work_output');src=np.array(Image.open(O/'variants/sn/hit_l_candidate_v3.png').convert('RGBA'));gen=np.array(Image.open(O/'sources/right_arm_donor.png').convert('RGBA'))
mask=Image.new('L',(1448,1086));d=ImageDraw.Draw(mask);d.polygon([(292,410),(480,390),(550,395),(608,380),(662,359),(668,402),(650,457),(566,477),(477,481),(292,441)],fill=255);d.polygon([(975,412),(995,409),(1045,306),(1068,307),(1070,342),(1036,407),(1044,458),(1012,486),(998,492),(985,453),(975,435)],fill=255);m=np.array(mask)>0;out=src.copy();out[m]=gen[m]
# Extract only the new rigid stick and shorten it to the original stick scale.
stickmask=Image.new('L',(1448,1086));ImageDraw.Draw(stickmask).polygon([(298,410),(478,426),(481,449),(298,432)],fill=255);sm=np.array(stickmask)>0;stick=np.zeros_like(out);stick[sm]=out[sm];out[sm]=0
crop=Image.fromarray(stick).crop((295,407,483,452));crop=crop.resize((132,45),Image.Resampling.BICUBIC);st=Image.new('RGBA',(1448,1086));st.alpha_composite(crop,(351,407));hit=Image.alpha_composite(Image.fromarray(out),st)
# Distal limb rotates as a rigid unit; elbow sleeve remains attached.
dm=Image.new('L',(1448,1086));ImageDraw.Draw(dm).polygon([(340,397),(468,398),(515,408),(567,400),(597,409),(604,453),(567,470),(479,481),(341,452)],fill=255);ma=np.array(dm)>0;h=np.array(hit);moving=np.zeros_like(h);moving[ma]=h[ma];fixed=h.copy();fixed[ma]=0;re=Image.fromarray(moving).rotate(-17,Image.Resampling.BICUBIC,center=(597,435),expand=False);rebound=Image.alpha_composite(Image.fromarray(fixed),re)
for phase,im in [('hit',hit),('rebound',rebound)]:
 fn=O/'variants/hh'/f'{phase}_r_local_edit_v3.png';im.save(fn);dr=Image.open(O/'sources/drum_fixed.png').convert('RGBA');bg=Image.new('RGBA',dr.size,'white');bg.alpha_composite(dr);bg.alpha_composite(im);bg.convert('RGB').save(O/'previews'/f'hh_r_{phase}_local_edit_v3.png')
mask.save(O/'qa/hh_r_local_edit_mask.png')
qa={'status':'VISUAL_QA_PENDING','source':'SN:L candidate v3; local AI right-arm donor only','protected_regions':'All non-ROI pixels copied verbatim from source. Rebound distal-arm rotation union is additional ROI.','global_generation_rejected':True,'original_drum_sha256':hashlib.sha256((O/'sources/drum_fixed.png').read_bytes()).hexdigest()};(O/'qa/hh_r_local_edit_v3.json').write_text(json.dumps(qa,indent=2))
