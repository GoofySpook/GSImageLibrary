import re,glob,os,sys,urllib.parse,numpy as np,cv2,onnxruntime as ort
from PIL import Image,ImageDraw
L,S=sys.argv[1:3];R='/home/claude/goofyspook/gsimagelibrary/'
txt=''.join(open(f).read() for f in glob.glob(L+'/references/*.md'))
pick={'study':'wizard-study-round-moon-window','dark':'wizard-study-green-orbs-skulls','locks':'book-fifty-locks','grave':'book-grave-manners','fires':'book-feeding-of-fires'}
sess=ort.InferenceSession(S+'/models/da.onnx',providers=['CPUExecutionProvider']);inn=sess.get_inputs()[0].name
for k,w in pick.items():
    m=re.search(r'### '+w+r'\n(.*?)(?=\n### |\Z)',txt,re.S);p=urllib.parse.unquote(re.search(r'main/(\S+)',m.group(1)).group(1));im=Image.open(R+p).convert('RGB');W,H=im.size
    s=2048/H;q=im.resize((round(W*s),2048),Image.LANCZOS);q.save(f'{S}/e1/plates/{k}.jpg',quality=93,subsampling=0);a=W/H;h=518;wd=round(h*a/14)*14
    i=np.asarray(q.resize((wd,h),Image.BICUBIC)).astype('f4')/255;i=((i-[.485,.456,.406])/[.229,.224,.225]).transpose(2,0,1)[None].astype('f4')
    d=sess.run(None,{inn:i})[0].squeeze();lo,hi=np.percentile(d,[1,99]);d=np.clip((d-lo)/(hi-lo),0,1);d=cv2.resize(d,(q.width//2,q.height//2),interpolation=cv2.INTER_CUBIC);d=cv2.GaussianBlur(cv2.bilateralFilter(d.astype('f4'),9,.15,7),(0,0),2.2)
    cv2.imwrite(f'{S}/e1/plates/{k}_d.png',(np.clip(d,0,1)*255).astype('u1'));cv2.imwrite(f'{S}/e1/plates/{k}_m.png',np.zeros((q.height//2,q.width//2,3),'u1'))
    g=q.resize((round(760*a),760));dr=ImageDraw.Draw(g)
    for n in range(1,10):
        x=n/10*g.width;y=n*76;dr.line([(x,0),(x,760)],fill=(255,255,0));dr.line([(0,y),(g.width,y)],fill=(255,255,0));dr.text((x+2,2),f'.{n}',fill='yellow');dr.text((2,y+2),f'.{n}',fill='yellow')
    g.save(f'{S}/sheets/e_{k}.jpg',quality=80);print(k,W,H,flush=True)
