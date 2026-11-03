#!/usr/bin/env python3
"""lowrender.py IMAGE TRACK OUT.mp4 [--title "Text"] [--cycle 40] [--glitch 13]
Full-song YouTube video: one image, slow zoom in and out, a short RGB glitch every --glitch s.
Renders ONE seamless cycle, then repeats it with -c copy, so a 4-minute song costs one cycle."""
import sys,subprocess,argparse,os,math,tempfile
from PIL import Image,ImageOps
a=argparse.ArgumentParser();a.add_argument('image');a.add_argument('track');a.add_argument('out')
a.add_argument('--cycle',type=int,default=40);a.add_argument('--glitch',type=float,default=13);a.add_argument('--zoom',type=float,default=.08)
o=a.parse_args();F=30;W,H=1920,1080;n=o.cycle*F
tmp=tempfile.mkdtemp();src=tmp+'/s.png'
ImageOps.fit(Image.open(o.image).convert('RGB'),(2880,1620),Image.LANCZOS,centering=(.5,.4)).save(src)
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',o.track]))
z=f"1+{o.zoom}*(0.5-0.5*cos(2*PI*on/{n}))"
g=[(i*o.glitch) for i in range(1,int(o.cycle/o.glitch)+1) if i*o.glitch<o.cycle-1]
en='+'.join(f"between(n,{int(t*F)},{int(t*F)+5})" for t in g) or '0'
vf=(f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={F},"
    f"rgbashift=rh=-14:rv=4:bh=14:bv=-4:enable='{en}',noise=alls=24:allf=t:enable='{en}',format=yuv420p")
c=tmp+'/c.mp4'
subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-framerate',str(F),'-loop','1','-t',str(o.cycle),'-i',src,'-frames:v',str(n),'-vf',vf,'-c:v','libx264','-preset','medium','-crf','20',c],check=True)
open(tmp+'/l.txt','w').write(''.join(f"file '{c}'\n" for _ in range(math.ceil(dur/o.cycle)+1)))
subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-f','concat','-safe','0','-i',tmp+'/l.txt','-i',o.track,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-t',f'{dur:.3f}','-movflags','+faststart',o.out],check=True)
print(o.out,os.path.getsize(o.out)//1048576,'MB')
