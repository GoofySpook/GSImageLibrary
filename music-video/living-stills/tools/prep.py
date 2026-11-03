import json,numpy as np,cv2,onnxruntime as ort,sys
from PIL import Image,ImageDraw
S='/tmp/claude-0/-home-claude/8f2adbcd-e066-5e85-bcec-09819e7c12c8/scratchpad'
R='/home/claude/goofyspook/gsimagelibrary/'
A=json.load(open(S+'/r2/art.json'))
pick={'hero':'joan-warrior-sunrise','hall':'throne-room-dark-blue-orange-stairs','wood':'forest-path-lantern-dusk','witch':'cloaked-figure-green-cauldron','sword':'dark-haired-warrior-orange-gem-sword','mage':'mage-combat-arcane-blast','hood':'hooded-face-amber-eyes-cobweb'}
sess=ort.InferenceSession(S+'/models/da.onnx',providers=['CPUExecutionProvider']);inn=sess.get_inputs()[0].name
for k,w in pick.items():
    im=Image.open(R+A[w]).convert('RGB');W,H=im.size;s=2048/H;p=im.resize((round(W*s),2048),Image.LANCZOS);p.save(f'plates/{k}.jpg',quality=93,subsampling=0)
    a=W/H;h=518;wd=round(h*a/14)*14;i=np.asarray(p.resize((wd,h),Image.BICUBIC)).astype('f4')/255
    i=((i-[.485,.456,.406])/[.229,.224,.225]).transpose(2,0,1)[None].astype('f4')
    d=sess.run(None,{inn:i})[0].squeeze();lo,hi=np.percentile(d,[1,99]);d=np.clip((d-lo)/(hi-lo),0,1)
    d=cv2.resize(d,(p.width//2,p.height//2),interpolation=cv2.INTER_CUBIC);d=cv2.GaussianBlur(cv2.bilateralFilter(d.astype('f4'),9,.15,7),(0,0),2.2)
    cv2.imwrite(f'plates/{k}_d.png',(np.clip(d,0,1)*255).astype('u1'))
    g=p.resize((round(1000*a),1000));dr=ImageDraw.Draw(g)
    for n in range(1,10):
        x=n/10*g.width;y=n*100;dr.line([(x,0),(x,1000)],fill=(255,255,0),width=1);dr.line([(0,y),(g.width,y)],fill=(255,255,0),width=1);dr.text((x+2,2),f'.{n}',fill='yellow');dr.text((2,y+2),f'.{n}',fill='yellow')
    g.save(f'{S}/sheets/g_{k}.jpg',quality=80);print(k,W,H,flush=True)
