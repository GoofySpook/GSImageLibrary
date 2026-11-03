import cv2,numpy as np
from PIL import Image
for k in ('grave','locks'): # knock out the white item background so the book sits in the dark
    a=np.asarray(Image.open(f'plates/{k}.jpg').convert('RGB')).astype('f4')/255
    l=a.mean(2);sat=a.max(2)-a.min(2);m=cv2.GaussianBlur(np.clip((l-.5)/.3,0,1)*np.clip(1-sat/.45,0,1),(0,0),6)[...,None]
    n=a*(1-m)+m*a*np.array([.09,.1,.17]);Image.fromarray((np.clip(n,0,1)*255).astype('u1')).save(f'plates/{k}.jpg',quality=93,subsampling=0)
P={'grave':{'cloth':[([(.1,.56),(.95,.56),(.95,.92),(.1,.92)],'pin')]},'fires':{'flow':[([(.04,.5),(.3,.2),(.6,.1),(.8,.16),(.7,.24),(.4,.3),(.15,.56)],1),([(.05,.55),(.7,.5),(.75,.72),(.55,.92),(.2,.76)],.8)]}}
for k,d in P.items():
    w,h=Image.open(f'plates/{k}.jpg').size;w2,h2=w//2,h//2;out=np.zeros((h2,w2,3),'f4')
    for ch,n in (('cloth',2),('flow',1)):
        for poly,v in d.get(ch,[]):
            m=np.zeros((h2,w2),'f4');cv2.fillPoly(m,[np.array([(x*w2,y*h2) for x,y in poly],'i4')],1)
            if v=='pin':
                y0=min(p[1] for p in poly)*h2;y1=max(p[1] for p in poly)*h2;m*=np.clip((np.arange(h2)-y0)/(y1-y0),0,1)[:,None]
            else:m*=v
            out[...,n]=np.maximum(out[...,n],m)
    cv2.imwrite(f'plates/{k}_m.png',(np.clip(cv2.GaussianBlur(out,(0,0),h2/110),0,1)*255).astype('u1'))
