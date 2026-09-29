import numpy as np, wave, sys
PRE=float(sys.argv[1]) if len(sys.argv)>1 else 1.0
sr=44100;BPM=128;beat=60/BPM;bar=beat*4;NB=48;TOT=NB*bar;N=int((TOT+4)*sr)
rng=np.random.default_rng(11)
m2f=lambda m:440*2**((m-69)/12)
def Z():return np.zeros((2,N))
def add(buf,t0,x,gain=1.0,pan=0.0):
    i0=int(round(t0*sr))
    if i0>=N or i0<0:return
    e=min(N,i0+len(x));s=x[:e-i0]*gain
    buf[0,i0:e]+=s*np.cos((pan+1)*np.pi/4);buf[1,i0:e]+=s*np.sin((pan+1)*np.pi/4)
def nhp(n,k=16):
    x=rng.standard_normal(n);return x-np.convolve(x,np.ones(k)/k,'same')
def kick(v=1):
    n=int(.45*sr);t=np.arange(n)/sr;f=42+110*np.exp(-t/.028);ph=2*np.pi*np.cumsum(f)/sr
    x=np.sin(ph)*(1-np.exp(-t/.0015))*np.exp(-t/.16)+rng.standard_normal(n)*np.exp(-t/.004)*.12
    return np.tanh(x*1.6)*v
def clap(v=1):
    n=int(.35*sr);t=np.arange(n)/sr;env=np.exp(-t/.11)*.6
    for d in(0,.011,.022):env+=np.where(t>=d,np.exp(-np.maximum(t-d,0)/.006),0)*.9
    return nhp(n,10)*env*.45*v
def hat(o=False,v=1):
    n=int((.16 if o else .05)*sr);t=np.arange(n)/sr
    return nhp(n,6)*np.exp(-t/(.06 if o else .012))*.22*v
def bassn(m,d,v=1):
    n=int((d+.05)*sr);t=np.arange(n)/sr;f=m2f(m)
    env=np.minimum(t/.006,1)*np.where(t<d,1,np.exp(-(t-d)/.02))
    x=np.sin(2*np.pi*f*t)+.35*np.sin(4*np.pi*f*t+.4)+.15*np.sin(6*np.pi*f*t)
    return np.tanh(x*1.4)*env*.5*v
def padn(m,d,v=1):
    n=int(d*sr);t=np.arange(n)/sr;f=m2f(m);x=np.zeros(n)
    for det in(-.004,.004):
        ff=f*(1+det)
        for h in range(1,11):
            if ff*h>5000:break
            x+=np.sin(2*np.pi*ff*h*t+h*1.3)/h/(1+(h*ff/2200)**2)
    a=int(.5*sr);r=int(.6*sr);env=np.ones(n);env[:a]=np.linspace(0,1,a)**2;env[-r:]=np.linspace(1,0,r)**2
    return x*env*.11*v
def pluck(m,v=1,dec=.32):
    n=int(1.4*sr);t=np.arange(n)/sr;f=m2f(m)
    x=np.sin(2*np.pi*f*t)+.4*np.sin(4*np.pi*f*t)*np.exp(-t/.1)+.15*np.sin(6*np.pi*f*t)*np.exp(-t/.05)
    return x*np.minimum(t/.004,1)*np.exp(-t/dec)*.3*v
def leadn(m,d,v=1):
    n=int((d+.3)*sr);t=np.arange(n)/sr;f=m2f(m);x=np.zeros(n)
    for h in range(1,9):x+=np.sin(2*np.pi*f*h*t)/h/(1+(h*f/3000)**2)
    env=np.minimum(t/.008,1)*np.where(t<d,1,np.exp(-(t-d)/.08))*np.exp(-t/.7)
    return x*env*.22*v
def riser(d,v=1):
    n=int(d*sr);t=np.arange(n)/sr;x=nhp(n,5)*(t/d)**2.2*.5
    f=200*np.exp(np.log(3000/200)*t/d);x+=np.sin(2*np.pi*np.cumsum(f)/sr)*(t/d)**2*.16
    return x*v
def impact(v=1,d=2.8):
    n=int(d*sr);t=np.arange(n)/sr;f=28+50*np.exp(-t/.25)
    sub=np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t/1.1)*.9
    return np.tanh((sub+np.sin(2*np.pi*55*t)*np.exp(-t/.7)*.25+nhp(n,3)*np.exp(-t/.6)*.35)*1.3)*v
def swell(d,v=1):
    n=int(d*sr);t=np.arange(n)/sr;return nhp(n,4)*(t/d)**3*.33*v

prog=[(33,[57,60,64],[57,60,64,69,72,76]),(29,[53,57,60],[53,57,60,65,69,72]),(36,[60,64,67],[60,64,67,72,76,79]),(31,[59,62,67],[59,62,67,71,74,79])]
DR,BS,PD,AR,LD,FX=Z(),Z(),Z(),Z(),Z(),Z()
kicks=[]
SCALE=[57,60,62,64,67,69,72,74,76,79,81,84,86,88,91,93]
B=lambda b,pos:b*bar+pos*beat
for b in range(NB):
    root,tri,arp=prog[b%4]
    t0=b*bar
    # pad (always)
    padv=.9 if b<3 else 1.0 if b<30 else 1.25 if b<36 else 1.1 if b<42 else 1.2
    for m in tri:add(PD,t0-.05,padn(m,bar+.9),padv,pan=rng.uniform(-.3,.3))
    if b>=30:
        for m in tri:add(PD,t0-.05,padn(m+12,bar+.9),padv*.55,pan=rng.uniform(-.5,.5))
    # counting motif (open + finale)
    if b<3:
        for j in range(4):
            n=b*4+j;add(AR,B(b,j),pluck(SCALE[n],.5+.03*n,.45),1,pan=-.3+.1*(n%7))
    if 44<=b<48:
        for j in range(4):
            n=(b-44)*4+j;add(AR,B(b,j),pluck(SCALE[n],max(.15,.62-.04*n),.6),1,pan=.35-.06*(n%9))
    # drums
    kpos=[]
    if b==2:kpos=[2,3]
    elif 3<=b<30 or 36<=b<42:kpos=[0,1,2,3]
    elif b==3:kpos=[0,1,2,3]
    elif 30<=b<33:kpos=[0,2.5]
    elif 33<=b<36:kpos=[0,1,2,3]
    elif b in(42,43):kpos=[0]
    for p in kpos:
        kv=.5 if b==2 else .85 if b<11 else 1.0
        add(DR,B(b,p),kick(kv),1);kicks.append((B(b,p),1 if b>2 else .5))
    clp=[]
    if (11<=b<30) or (36<=b<42):clp=[1,3]
    elif 30<=b<36:clp=[2]
    if b in(29,41):clp=[0,1,2,3,3.5,3.25,3.75]  # roll
    for p in clp:add(DR,B(b,p),clap(.9 if b not in(29,41) else .5+.1*p),1,pan=.1)
    hp=[]
    if 3<=b<11:hp=[.5,1.5,2.5,3.5]
    elif 11<=b<24 or 30<=b<33:hp=[j*.5 for j in range(8)]
    elif 24<=b<30 or 33<=b<42:hp=[j*.25 for j in range(16)]
    for p in hp:
        acc=1.0 if (p%1==.5) else .55
        add(DR,B(b,p),hat(False,acc*(.7 if b<24 else .9)),1,pan=.25*np.sin(p*3))
    if 11<=b<30 or 36<=b<42:
        for p in (.5,2.5):add(DR,B(b,p),hat(True,.5),1,pan=-.2)
    # bass
    if 3<=b<30:
        for j in range(8):
            if b<11 and j%2:continue
            add(BS,B(b,j*.5),bassn(root+(12 if j%4==3 and b>=11 else 0),.4*beat*1.05),.9)
    elif 30<=b<36:add(BS,t0,bassn(root,bar*.98),1.0)
    elif 36<=b<42:
        for p in (.5,1.5,2.5,3.5):add(BS,B(b,p),bassn(root+12*(p==3.5),.42*beat),.85)
        add(BS,t0,bassn(root,.4*beat),.9);add(BS,B(b,2),bassn(root,.4*beat),.9)
    elif 42<=b<46:add(BS,t0,bassn(root,bar*.98),.8 if b<44 else .5)
    # arps
    if 3<=b<24:
        step=.5 if b<13 else .25
        for j in range(int(4/step)):
            add(AR,B(b,j*step),pluck(arp[(j*(1 if step==.5 else 1))%6]+(12 if (j//6)%2 else 0),.55 if b<13 else .5,.28),1,pan=.5*np.sin(j*1.7))
    elif 24<=b<30:
        for j in range(16):add(AR,B(b,j*.25),pluck(arp[j%6]+12,.55,.25),1,pan=.5*np.sin(j*1.7))
    elif 30<=b<36:
        for j in range(8):add(AR,B(b,j*.5),pluck(arp[j%6]+ (12 if j>3 else 0),.5,.5),1,pan=.5*np.sin(j*1.3))
    elif 36<=b<42:
        for j in range(16):
            add(LD,B(b,j*.25),leadn(arp[(j*2)%6]+12,.22),.7 if j%4 else .95,pan=.4*np.sin(j*.9))
    if b in(43,44):  # lead motif
        mot=[81,79,76,79,81,84,81,79] if b==43 else [76,79,81,79,76,72]
        for j,m in enumerate(mot[:8]):add(LD,B(b,j*.5),leadn(m,.45,.6),1,pan=.2)
    # transitions
    if b in(3,11,24,30,36,42):add(FX,t0-.02,swell(.5),.8);add(FX,t0,impact(1.3 if b in(30,36,42) else .55,2.8 if b in(30,36,42) else 1.6),1)
    elif b>=1 and b not in(2,):add(FX,t0,impact(.28,1.0),1)   # cut punch
add(FX,B(2,0),riser(bar),.9)
add(FX,B(27,0),riser(3*bar),1.0)
add(FX,B(40,0),riser(2*bar),1.0)
# sidechain
duck=np.ones(N)
for tk,kv in kicks:
    i0=int(tk*sr);L=int(.32*sr);e=min(N,i0+L);tt=np.arange(e-i0)/sr
    duck[i0:e]=np.minimum(duck[i0:e],1-.55*kv*np.exp(-tt/.11))
dry=DR*1.0+BS*duck*.9+PD*duck**.6*.95+AR*duck**.5*.8+LD*duck**.5*.9+FX
# delay (dotted 8th ping-pong) on arp+lead
send=(AR+LD)
dl=np.zeros((2,N));dt=int(.75*beat*sr)
for k in range(1,5):
    o=dt*k
    if o<N:
        g=.4**k*.9
        dl[0,o:]+=send[k%2,:N-o]*g;dl[1,o:]+=send[(k+1)%2,:N-o]*g
# reverb
irn=int(2.4*sr);tt=np.arange(irn)/sr
def mkir():
    x=rng.standard_normal(irn)*np.exp(-tt/.6);x=np.convolve(x,np.ones(6)/6,'same');return x/np.sqrt((x**2).sum())
nfft=1<<int(np.ceil(np.log2(N+irn)))
wet_in=PD*.5+AR*.5+LD*.5+FX*.35+DR*0.06
rev=np.zeros((2,N))
for ch in range(2):
    ir=mkir();R=np.fft.irfft(np.fft.rfft(wet_in[ch],nfft)*np.fft.rfft(ir,nfft),nfft)[:N];rev[ch]=R
mix=dry+dl*.9+rev*1.6
# gates before big hits
for b in(30,36,42):
    tg=b*bar;i0=int((tg-.2)*sr);i1=int(tg*sr)
    g=np.ones(N);g[i0:i1]=np.linspace(1,0,i1-i0)**.5*.15 if False else 0.0
    ramp=int(.02*sr);g[i0-ramp:i0]=np.linspace(1,0,ramp)
    mix*=g
print('pre peak',np.abs(mix).max(),'pre rms',np.sqrt((mix**2).mean()))
secg=np.ones(N)
lv=[(0,3,.9),(3,11,.72),(11,24,.86),(24,30,.98),(30,36,1.08),(36,42,1.22),(42,48,1.0)]
for a,b_,g in lv:secg[int(a*bar*sr):int(b_*bar*sr)]=g
k=int(.35*sr);secg=np.convolve(secg,np.ones(k)/k,'same')
mix*=secg*PRE
mix=np.tanh(mix*1.3)/1.3
# master fade & trim
Tn=int(TOT*sr)
fo=int(3.2*sr);mix[:,Tn-fo:Tn]*=np.linspace(1,0,fo)**1.5
mix=mix[:,:Tn]
mix*=.92/np.abs(mix).max()
pcm=(mix.T*32767).astype(np.int16)
w=wave.open('score2.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes());w.close()
# report
print('peak',np.abs(mix).max(),'dur',Tn/sr)
for b in range(0,NB,1):
    seg=mix[:,int(b*bar*sr):int((b+1)*bar*sr)]
    print(b,round(float(np.sqrt((seg**2).mean())),3),end=' | ')
print()
x=mix.mean(0);F=np.abs(np.fft.rfft(x[int(40*bar*sr/40*40):int(40*bar*sr/40*40)+sr*8]))**2
fr=np.fft.rfftfreq(sr*8,1/sr);pass
#print('low<150',F[fr<150].sum()/F.sum(),'mid',F[(fr>=150)&(fr<2000)].sum()/F.sum(),'high',F[fr>=2000].sum()/F.sum())
