#!/usr/bin/env python3
"""plates.py CROPS.json LIBRARY_DIR OUT_DIR  -> 2048x1152 plate + depth map per entry.
CROPS: {"name":{"file":"repo/path.png","y":90,"x":0,"w":896}}  y null = auto-strip letterbox.
Model: https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx saved as DA_MODEL (default ./da.onnx).
pip: onnxruntime opencv-python-headless pillow."""
import sys,os,json,numpy as np,cv2,onnxruntime as ort
from PIL import Image
crops=json.load(open(sys.argv[1]));lib=sys.argv[2];out=sys.argv[3];os.makedirs(out,exist_ok=True)
sess=ort.InferenceSession(os.environ.get('DA_MODEL','da.onnx'),providers=['CPUExecutionProvider']);inn=sess.get_inputs()[0].name
for k,c in crops.items():
    im=Image.open(os.path.join(lib,c['file'])).convert('RGB');W,H=im.size;x=c.get('x',0);y=c.get('y',0);w=c.get('w',W)
    if y is None:
        a=np.asarray(im);r=np.where(a.mean((1,2))>12)[0];t,b=r[0]+4,r[-1]-4;h=int(w*9/16)
        if b-t<h: h=b-t;w=int(h*16/9);x=(W-w)//2
        y=t+((b-t)-h)//2
    h=int(w*9/16);y=min(y,H-h)
    p=im.crop((x,y,x+w,y+h)).resize((2048,1152),Image.LANCZOS);p.save(f'{out}/{k}.jpg',quality=93,subsampling=0)
    s=518;i=np.asarray(p.resize((s*16//9//14*14,s),Image.BICUBIC)).astype('f4')/255
    i=((i-[.485,.456,.406])/[.229,.224,.225]).transpose(2,0,1)[None].astype('f4')
    d=sess.run(None,{inn:i})[0].squeeze();lo,hi=np.percentile(d,[1,99]);d=np.clip((d-lo)/(hi-lo),0,1)
    d=cv2.resize(d,(1024,576),interpolation=cv2.INTER_CUBIC);d=cv2.GaussianBlur(cv2.bilateralFilter(d.astype('f4'),9,.15,7),(0,0),2.2)
    cv2.imwrite(f'{out}/{k}_d.png',(np.clip(d,0,1)*255).astype('u1'));print(k,(W,H),'upscale %.2f'%(1920/w),flush=True)
