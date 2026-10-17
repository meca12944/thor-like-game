# Procedural impact SFX (numpy/scipy) -> assets/sfx/*.ogg. Original sounds, no samples, free to use.
# python3 tools/sfx/gen_sfx.py
import numpy as np, scipy.signal as sg, subprocess, os, wave
SR=44100; OUT='/workspace/town-demo/assets/sfx/'; rng=np.random.default_rng(7)
def t(d): return np.arange(int(SR*d))/SR
def env(n,a,d): x=np.arange(n)/SR; return np.minimum(1,x/max(a,1e-4))*np.exp(-x/d)
def bp(x,lo,hi,o=2): b,a=sg.butter(o,[lo/(SR/2),hi/(SR/2)],'band'); return sg.lfilter(b,a,x)
def lp(x,f,o=2): b,a=sg.butter(o,f/(SR/2)); return sg.lfilter(b,a,x)
def hp(x,f,o=2): b,a=sg.butter(o,f/(SR/2),'high'); return sg.lfilter(b,a,x)
def sweep_noise(d,f0,f1,q=.6):
    n=int(SR*d);x=rng.standard_normal(n);out=np.zeros(n);B=512
    for i in range(0,n,B):
        f=f0+(f1-f0)*(i/n);lo=max(60,f*(1-q/2));hi=min(SR/2-100,f*(1+q/2))
        out[i:i+B]=bp(x[max(0,i-2048):i+B],lo,hi)[-len(x[i:i+B]):]
    return out
def thump(d,f0,f1,dec):
    x=t(d);f=f1+(f0-f1)*np.exp(-x/ (dec*.35));ph=2*np.pi*np.cumsum(f)/SR;return np.sin(ph)*env(len(x),.002,dec)
def norm(x,pk=.9): x=x-np.mean(x); return x/ (np.max(np.abs(x))+1e-9)*pk
def sat(x,k): return np.tanh(x*k)/np.tanh(k)
def save(name,x):
    x=norm(x);fade=int(SR*.01);x[-fade:]*=np.linspace(1,0,fade)
    w=OUT+name+'.wav'
    with wave.open(w,'wb') as f: f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((x*32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-c:a','libvorbis','-q:a','3',OUT+name+'.ogg']);os.remove(w)
def whoosh(d,f0,f1,a=.03):
    x=sweep_noise(d,f0,f1); e=np.sin(np.pi*np.clip(t(d)/d,0,1))**1.5; return x*e
def impact(heavy=False,crit=False):
    d=.42 if heavy else .22
    body=thump(d,170 if not heavy else 130,48 if heavy else 62,.16 if heavy else .08)
    n=len(body); nz=rng.standard_normal(n)
    crunch=bp(nz,700,4200)*env(n,.0008,.05 if heavy else .03)
    click=hp(nz,3000)*env(n,.0002,.004)
    sub=np.sin(2*np.pi*45*t(d))*env(n,.004,.12 if heavy else .05)*(1 if heavy else .4)
    x=body*1.0+crunch*.7+click*.5+sub*.8
    if crit:
        ring=sum(np.sin(2*np.pi*f*t(d))*env(n,.001,.12)*a for f,a in [(2150,.25),(3420,.18),(5230,.1)])
        x=x+ring
    return sat(x,2.6 if heavy else 2.0)
save('swing_light',whoosh(.17,900,2600))
save('swing_heavy',whoosh(.30,350,1400)+thump(.30,90,50,.12)*.15)
save('hit_light',impact())
save('hit_heavy',impact(True))
save('hit_crit',impact(True,True))
d=.35;n=int(SR*d);x=lp(rng.standard_normal(n),2500)*env(n,.001,.08)+thump(d,300,60,.08)*.7;save('kill',sat(x,2))
save('spin_dark',whoosh(.55,250,1800)*1.0+thump(.55,70,40,.3)*.25)
save('wave',whoosh(.22,1400,3400))
d=.9;x=t(d);sw=sweep_noise(d,300,5000,.8)*(x/d)**2;tone=np.sin(2*np.pi*np.cumsum(200+600*(x/d)**2)/SR)*(x/d)**2*.4;save('ult_cutin',sw+tone)
d=1.6;n=int(SR*d);nz=rng.standard_normal(n);boom=lp(nz,1800)*env(n,.002,.35)+lp(nz,400)*env(n,.003,.6)+thump(d,90,30,.5)*1.2;save('ult_boom',sat(boom,2.2))
print(sorted(os.listdir(OUT)))
