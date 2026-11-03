#!/usr/bin/env python3
"""analyze.py TRACK START DUR OUT.js  -> per-frame sub/mid/hi envelopes for assets/bands.js, prints onsets.
Sections: run `npx hyperframes audio TRACK --only sections,onsets,moments --json` first. pip: librosa scipy."""
import sys,json,numpy as np,librosa,scipy.signal as ss
tr,A,D,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
y,sr=librosa.load(tr,sr=22050,offset=max(A-1,0),duration=D+2,mono=True)
pre=min(A,1);hop=sr//120
St=np.abs(librosa.stft(y,n_fft=2048,hop_length=hop));f=librosa.fft_frequencies(sr=sr);t=np.arange(St.shape[1])*hop/sr-pre
res={}
for k,(a,b) in {'sub':(20,130),'mid':(300,2500),'hi':(4000,11000)}.items():
    e=np.log1p(St[(f>=a)&(f<b)].mean(0)*20)
    fl=np.maximum(0,np.diff(e,prepend=e[0]))
    v=np.clip((e-np.percentile(e,5))/(np.percentile(e,99.5)-np.percentile(e,5)),0,1)
    env=np.zeros_like(v);c=0;d=.93 if k=='sub' else .90
    for i,x in enumerate(v): c=max(x,c*d);env[i]=c
    res[k]=[round(float(np.interp(i/30,t,env)),3) for i in range(int(D*30)+1)]
    p,_=ss.find_peaks((fl/np.percentile(fl,99.5)).clip(0,1),height=.45,distance=30)
    tt=t[p];print(k,np.round(tt[(tt>=0)&(tt<D)],2).tolist())
open(out,'w').write('window.BANDS='+json.dumps(res,separators=(',',':'))+';')
