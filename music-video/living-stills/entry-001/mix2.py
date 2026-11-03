import numpy as np,soundfile as sf,scipy.signal as ss,librosa
S='/tmp/claude-0/-home-claude/8f2adbcd-e066-5e85-bcec-09819e7c12c8/scratchpad';sr=48000;D=54.6;N=int(D*sr);rng=np.random.default_rng(11);T=np.arange(N)/sr
def bp(x,a,b):return ss.sosfilt(ss.butter(2,[a,b],'band',fs=sr,output='sos'),x)
def lp(x,a):return ss.sosfilt(ss.butter(2,a,'low',fs=sr,output='sos'),x)
def env(t,p):return np.interp(t,[a for a,b in p],[b for a,b in p])
fx=np.zeros((N,2))
def put(sig,t0,g=1,pan=0):
    i=int(t0*sr);n=min(len(sig),N-i);l,r=np.cos((pan+1)*np.pi/4),np.sin((pan+1)*np.pi/4);fx[i:i+n,0]+=sig[:n]*g*l*1.41;fx[i:i+n,1]+=sig[:n]*g*r*1.41
def nz():return rng.standard_normal(N)
put(lp(nz(),240)*env(T,[(0,0),(1,1),(46,1),(47,0)]),0,.2)
c=(rng.random(N)>.9997)*rng.standard_normal(N);put(bp(c,1200,6000)*env(T,[(0,1),(10,1),(10.6,0)]),0,.22)
def page(t0,g=.13,p=.2):
    n=int(.5*sr);tt=np.arange(n)/sr;put(bp(rng.standard_normal(n),700,6500)*np.exp(-((tt-.16)/.11)**2),t0,g,p)
for t in (3.4,10.3,21.7,32.7,46.3):page(t)
n=int(.3*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(90-40*tt)*tt)*np.exp(-tt*16),6.0,.3)
for t0 in (13.2,13.95,14.55,15.15):
    n=int(.09*sr);tt=np.arange(n)/sr;put(bp(rng.standard_normal(n),1800,6200)*np.exp(-tt*60)+.5*np.sin(2*np.pi*2600*tt)*np.exp(-tt*80),t0,.2,rng.uniform(-.3,.3))
wh=bp(nz(),2500,8000)*env(T,[(15.4,0),(15.9,1),(16.8,0)]);put(wh,0,.05,-.3)
n=int(2.5*sr);tt=np.arange(n)/sr;put((np.sin(2*np.pi*55*tt)+.5*np.sin(2*np.pi*82*tt))*np.sin(np.pi*tt/2.5)**2,17.8,.2)
wd=bp(nz(),150,700)*(.55+.45*np.sin(T*.9+.5*np.sin(T*.37)))*env(T,[(21.7,0),(22.3,1),(32,1),(32.8,0)]);put(wd,0,.2,-.2)
for t in (29.3,):
    n=int(2.6*sr);tt=np.arange(n)/sr;put(sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*d) for f,a,d in ((196,1,1.6),(233,.6,2.2),(392,.5,3),(471,.3,4),(622,.2,5))),t,.1,.1)
for t in (22.05,):
    n=int(1.5*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(120+25*np.sin(tt*3))*tt)*np.sin(np.pi*tt/1.5)**2,t,.05,.4)
c=(rng.random(N)>.9994)*rng.standard_normal(N);put(bp(c,1200,7000)*env(T,[(32.8,.3),(40,.7),(46,1),(46.5,0)]),0,.7)
put(lp(nz(),380)*env(T,[(32.7,0),(33.5,.5),(41,.6),(45.8,1),(46.5,0)]),0,.38)
n=int(1.4*sr);put(bp(rng.standard_normal(n),300,3000)*np.sin(np.linspace(0,np.pi,n))**2,40.6,.2,.2)
n=int(4.2*sr);tt=np.arange(n)/sr;put((np.sin(2*np.pi*46*tt)+.4*np.sin(2*np.pi*69*tt))*(tt/4.2)**2,46.4,.26)
for t0 in (48.6,49.3,49.9,50.25):
    n=int(.25*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(62-20*tt)*tt)*np.exp(-tt*16),t0,.34)
n=int(2.8*sr);tt=np.arange(n)/sr;put(np.sin(2*np.pi*(54-15*tt)*tt)*np.exp(-tt*2),50.55,.4)
ir=rng.standard_normal(int(1.2*sr))*np.exp(-np.arange(int(1.2*sr))/sr*5);ir=lp(ir,4200);ir/=np.sqrt((ir**2).sum())
fx=fx+.24*np.stack([ss.fftconvolve(fx[:,i],ir)[:N] for i in (0,1)],1)
L=[.5,3.6,6.85,10.6,13,17.05,22,24.35,29.35,33,36.95,41.15,46.6,50.6]
v=np.zeros(N)
for i,t0 in enumerate(L,1):
    y,_=librosa.load(f'{S}/e1/voice/l{i}.wav',sr=sr,mono=True);y=y/np.sqrt((y[np.abs(y)>.01]**2).mean())*.19;a=int(t0*sr);n=min(len(y),N-a);v[a:a+n]+=y[:n]
v=ss.sosfilt(ss.butter(2,90,'high',fs=sr,output='sos'),v);vw=.1*ss.fftconvolve(v,ir)[:N];vst=np.stack([v+vw,v+vw],1)
off=5.855;m,_=librosa.load('/mnt/user-data/uploads/Call_and_Response.wav',sr=sr,mono=False,duration=D-off);m=m.T;mm=np.zeros((N,2));a=int(off*sr);mm[a:a+len(m)]=m[:N-a]
act=np.clip(ss.fftconvolve((np.abs(v)>.01).astype('f4'),np.ones(int(.25*sr))/(.25*sr),'same')*2.5,0,1)
gain=env(T,[(off,0),(off+2.5,.95),(50.5,1.1),(50.55,.62),(52.6,.62),(54.6,0)]);duck=1-env(T,[(0,.45),(50.5,.45),(50.55,.65),(55,.65)])*act
mus=mm*(gain*duck)[:,None];mx=vst*.95+mus+fx*.8*(1-.3*act)[:,None]
print('peak',np.abs(mx).max())
for a,b,n in ((13,16.8,'book1'),(36.95,40.9,'book3'),(50.6,52.4,'drop')):
    i,j=int(a*sr),int(b*sr);r=lambda x:20*np.log10(np.sqrt((x[i:j]**2).mean())+1e-9);print(n,'voice %.1f music %.1f fx %.1f'%(r(vst),r(mus),r(fx*.8)))
pk=np.abs(mx);lim=np.minimum(1,.9/np.maximum(ss.fftconvolve(pk.max(1),np.ones(480)/480,'same'),1e-3));sf.write(f'{S}/e1/mix_raw.wav',mx*np.minimum(1,.97/np.maximum(pk.max(),1e-3)),sr)
