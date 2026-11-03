#!/usr/bin/env python3
"""Synthesised SFX + ducked mix. All sounds generated here: no licences to track."""
import numpy as np,soundfile as sf,scipy.signal as ss,librosa,sys
S='/tmp/claude-0/-home-claude/8f2adbcd-e066-5e85-bcec-09819e7c12c8/scratchpad';sr=48000;D=23;N=D*sr
rng=np.random.default_rng(7)
def bp(x,a,b):return ss.sosfilt(ss.butter(2,[a,b],'band',fs=sr,output='sos'),x)
def lp(x,a):return ss.sosfilt(ss.butter(2,a,'low',fs=sr,output='sos'),x)
def env(t,pts):return np.interp(t,[p[0] for p in pts],[p[1] for p in pts])
fx=np.zeros((N,2));T=np.arange(N)/sr
def put(sig,t0,g=1,pan=0):
    i=int(t0*sr);n=min(len(sig),N-i);l,r=np.cos((pan+1)*np.pi/4),np.sin((pan+1)*np.pi/4)
    fx[i:i+n,0]+=sig[:n]*g*l*1.41;fx[i:i+n,1]+=sig[:n]*g*r*1.41
w=rng.standard_normal(N)
# wind, hero
wind=bp(w,180,900)*(.55+.45*np.sin(T*1.1+.4*np.sin(T*.5)));put(wind*env(T,[(0,0),(.5,1),(3.3,1),(3.8,0)]),0,.22,-.2)
# hall: room tone + banner flaps
room=lp(rng.standard_normal(N),220);put(room*env(T,[(3.5,0),(3.8,1),(6.8,1),(7.1,0)]),0,.35)
flap=bp(rng.standard_normal(N),160,800)*(.5+.5*np.sign(np.sin(T*2*np.pi*2.4)+.2*np.sin(T*17)))*(.5+.5*np.sin(T*2*np.pi*.7))
put(flap*env(T,[(3.6,0),(3.9,1),(6.7,1),(7,0)]),0,.16,.25)
# wood: lantern creaks, owl, low wind
wn=bp(rng.standard_normal(N),120,420)*env(T,[(7,0),(7.4,1),(11,1),(11.4,0)]);put(wn,0,.16,.1)
for t0 in (7.25,9.2):
    n=int(.34*sr);tt=np.arange(n)/sr;c=np.sin(2*np.pi*(780*tt+160*tt*tt/.34))*np.exp(-tt*7)*(1+.6*np.sign(np.sin(2*np.pi*38*tt)));put(bp(c,500,2400),t0,.05,.25)
for t0,g in ((8.5,.05),(8.86,.04)):
    n=int(.42*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(318-22*tt)*tt+.8*np.sin(2*np.pi*5*tt))*np.sin(np.pi*tt/.42)**2,t0,g,-.6)
# eyes: swell + heartbeat
n=int(2.2*sr);tt=np.arange(n)/sr;put((np.sin(2*np.pi*48*tt)+.5*np.sin(2*np.pi*73*tt))*np.sin(np.pi*tt/2.2)**2,10.15,.28)
for t0 in (11.3,11.72):
    n=int(.25*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(62-20*tt)*tt)*np.exp(-tt*16),t0,.5)
# cauldron: bubbles + crackle
for _ in range(70):
    t0=rng.uniform(12.4,15.5);n=int(rng.uniform(.04,.13)*sr);tt=np.arange(n)/sr;f=rng.uniform(170,520)
    put(np.sin(2*np.pi*(f*tt+f*2.2*tt*tt/ (n/sr)))*np.sin(np.pi*tt/(n/sr)),t0,rng.uniform(.02,.06),rng.uniform(-.5,.5))
c=(rng.random(N)>.99965)*rng.standard_normal(N);put(bp(c,1400,7000)*env(T,[(12.4,0),(12.6,1),(15.3,1),(15.6,0)]),0,.7)
put(lp(rng.standard_normal(N),300)*env(T,[(12.3,0),(12.7,1),(15.2,1),(15.6,0)]),0,.3)
# sword
n=int(.2*sr);tt=np.arange(n)/sr;sw=bp(rng.standard_normal(n),1500,9000)*(tt/.2)**2;put(sw,15.42,.16,.3)
n=int(1.5*sr);tt=np.arange(n)/sr
s=sum(a*np.sin(2*np.pi*f*tt+rng.uniform(0,6))*np.exp(-tt*d) for f,a,d in ((2310,1,3.6),(3705,.8,4.5),(5120,.55,6),(7240,.35,8),(2975,.4,5)));put(s,15.6,.1,.2)
n=int(.7*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(70-40*tt)*tt)*np.exp(-tt*6.5),15.6,.5)
# ice flame
sn=bp(rng.standard_normal(int(1.5*sr)),900,6500);put(sn*np.sin(np.linspace(0,np.pi,len(sn)))**2,17.4,.12,-.4)
for _ in range(70):
    t0=rng.uniform(17.6,19.9);n=int(.32*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*rng.uniform(3500,9000)*tt)*np.exp(-tt*14),t0,rng.uniform(.006,.018),rng.uniform(-.7,.2))
# end boom
n=int(2.4*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(52-14*tt)*tt)*np.exp(-tt*2.1),20.3,.38)
# reverb on fx
ir=rng.standard_normal(int(1.1*sr))*np.exp(-np.arange(int(1.1*sr))/sr*5.5);ir=lp(ir,4200);ir/=np.sqrt((ir**2).sum())
wet=np.stack([ss.fftconvolve(fx[:,i],ir)[:N] for i in (0,1)],1);fx=fx+.22*wet
# voice
LINES=[(.5,1),(3.9,2),(7.15,3),(10.25,4),(12.7,5),(15.75,6),(17.9,7)]
v=np.zeros(N)
for t0,i in LINES:
    y,_=librosa.load(f'{S}/r2/voice2/l{i}.wav',sr=sr,mono=True);y=y/np.sqrt((y[np.abs(y)>.01]**2).mean())*.19;a=int(t0*sr);v[a:a+len(y)]+=y[:N-a]
v=ss.sosfilt(ss.butter(2,90,'high',fs=sr,output='sos'),v)
vw=.1*ss.fftconvolve(v,ir)[:N];vst=np.stack([v+vw,v+vw],1)
# music + duck
m,_=librosa.load('/mnt/user-data/uploads/Call_and_Response.wav',sr=sr,mono=False,offset=29.095,duration=D);m=m.T[:N]
gain=env(T,[(0,0),(.4,.8),(15.55,.8),(15.6,.62),(21.3,.62),(23,0)])
act=ss.sosfilt(ss.butter(1,3,'low',fs=sr,output='sos'),(np.abs(v)>.01).astype('f4'));act=np.clip(ss.fftconvolve((np.abs(v)>.01).astype('f4'),np.ones(int(.25*sr))/(.25*sr),'same')*2.5,0,1)
duck=1-env(T,[(0,.5),(15.5,.5),(15.6,.72),(23,.72)])*act
mus=m*(gain*duck)[:,None]
sf.write(f'{S}/r2/stem_v.wav',vst,sr);mx=vst*.95+mus+fx*.8*(1-.35*act)[:,None]
print('peak',np.abs(mx).max())
for a,b,n in ((.5,3,'l1'),(12.7,15.1,'l5'),(15.6,17.5,'hit'),(20.3,21.5,'end')):
    i,j=int(a*sr),int(b*sr);r=lambda x:20*np.log10(np.sqrt((x[i:j]**2).mean())+1e-9);print(n,'voice %.1f music %.1f fx %.1f'%(r(vst),r(mus),r(fx*.8)))
sf.write(f'{S}/r2/mix_raw.wav',mx/max(1,np.abs(mx).max()*1.05),sr)
