import cv2,numpy as np
from PIL import Image
P={'hero':{'cloth':[([(.60,.66),(.98,.76),(.92,.86),(.64,.90)],1),([(.27,.11),(.41,.10),(.39,.23),(.30,.24)],.6)]},
'hall':{'cloth':[([(a,y0),(b,y0),(b,y1),(a,y1)],'pin') for a,b,y0,y1 in [(.34,.40,.05,.47),(.595,.655,.05,.47),(.22,.31,0,.385),(.69,.77,0,.385)]]},
'wood':{'rigid':[([(.485,.525),(.60,.525),(.60,.70),(.485,.70)],1)]},
'witch':{'flow':[([(.33,.18),(.74,.18),(.76,.72),(.24,.72)],1),([(.14,.72),(.92,.72),(.96,1),(.2,1)],.55)]},
'mage':{'flow':[([(0,.08),(.24,.08),(.24,.5),(0,.5)],1)]},'sword':{},'hood':{}}
for k,d in P.items():
    w,h=Image.open(f'plates/{k}.jpg').size;w2,h2=w//2,h//2
    out=np.zeros((h2,w2,3),'f4')
    for ch,n in (('cloth',2),('flow',1),('rigid',0)): # BGR: R cloth, G flow, B rigid
        for poly,v in d.get(n and ch or ch,[]):
            m=np.zeros((h2,w2),'f4');pts=np.array([(x*w2,y*h2) for x,y in poly],'i4');cv2.fillPoly(m,[pts],1)
            if v=='pin':
                y0=min(p[1] for p in poly)*h2;y1=max(p[1] for p in poly)*h2;g=np.clip((np.arange(h2)-y0)/(y1-y0),0,1)[:,None];m*=g
            else:m*=v
            out[...,n]=np.maximum(out[...,n],m)
    out=cv2.GaussianBlur(out,(0,0),h2/90)
    cv2.imwrite(f'plates/{k}_m.png',(np.clip(out,0,1)*255).astype('u1'));print(k)
