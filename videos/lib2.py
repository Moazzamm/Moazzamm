import os,hashlib
ROOT=os.path.dirname(os.path.abspath(__file__))
TH={'dark':"--fg:#efe7d6;--ff:'DejaVu Serif',serif;--kf:'Inter Display','Inter',sans-serif;--tw:700;--ts:-.01em;--sub:#c9c0ae;--base:radial-gradient(ellipse at 50% 40%,#1b1815 0%,#0a0908 70%,#030303 100%)",
    'tech':"--fg:#f3f6ff;--ff:'Inter Display','Inter',sans-serif;--kf:'Inter Display','Inter',sans-serif;--tw:800;--ts:-.035em;--sub:#aeb9de;--base:radial-gradient(ellipse at 50% 30%,#1a2552 0%,#0b1026 60%,#050814 100%)"}
CSS="""*{box-sizing:border-box;margin:0;padding:0;animation-fill-mode:both!important}
html,body{width:1920px;height:1080px;overflow:hidden;background:#000}
body{position:relative;color:var(--fg);font-family:var(--ff)}
.base{position:absolute;inset:0;background:var(--base)}
.grid{position:absolute;inset:-100px;background-image:linear-gradient(#ffffff0d 1px,transparent 1px),linear-gradient(90deg,#ffffff0d 1px,transparent 1px);background-size:80px 80px;animation:gdrift var(--dur) linear}
@keyframes gdrift{to{transform:translate(60px,40px)}}
.orb{position:absolute;border-radius:50%;filter:blur(90px);opacity:.33;animation:orb var(--dur) ease-in-out}
@keyframes orb{from{transform:translate(0,0) scale(1)}to{transform:translate(var(--ox),var(--oy)) scale(1.25)}}
.bg{position:absolute;inset:-5%;background-size:cover;background-position:var(--pos,50% 50%);animation:kb var(--dur) linear;filter:var(--grade,none)}
@keyframes kb{from{transform:scale(var(--z0)) translate(var(--x0),var(--y0))}to{transform:scale(var(--z1)) translate(var(--x1),var(--y1))}}
.tint{position:absolute;inset:0;background:var(--a);mix-blend-mode:soft-light;opacity:.28}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 42%,transparent 38%,rgba(0,0,0,.72) 100%),linear-gradient(to top,rgba(0,0,0,.92) 0%,rgba(0,0,0,.35) 36%,transparent 62%)}
.fog{position:absolute;inset:-25%;background:radial-gradient(ellipse at 20% 62%,rgba(255,255,255,.13),transparent 42%),radial-gradient(ellipse at 72% 38%,rgba(255,255,255,.10),transparent 40%),radial-gradient(ellipse at 50% 85%,rgba(255,255,255,.09),transparent 35%);animation:drift var(--dur) linear;filter:blur(40px)}
@keyframes drift{from{transform:translateX(-7%)}to{transform:translateX(7%)}}
.mote{position:absolute;width:7px;height:7px;border-radius:50%;background:var(--a);box-shadow:0 0 16px 4px var(--a);opacity:.0;animation:mote var(--md) linear var(--mdl) infinite}
@keyframes mote{0%{opacity:0;transform:translate(0,0)}15%{opacity:.8}85%{opacity:.6}100%{opacity:0;transform:translate(var(--mx),-260px)}}
.open{position:absolute;inset:0;background:#000;animation:fo .5s ease-out}@keyframes fo{from{opacity:1}to{opacity:0}}
.flash{position:absolute;inset:0;background:#fff;mix-blend-mode:overlay;animation:fl .45s ease-out}@keyframes fl{from{opacity:.55}to{opacity:0}}
.c{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:70px 150px 250px;animation:exit .26s ease-in calc(var(--dur) - .26s)}
.c.lt{justify-content:flex-end;align-items:flex-start;text-align:left;padding:0 140px 255px}
@keyframes exit{to{opacity:0;transform:scale(1.035);filter:blur(10px)}}
.w{display:inline-block;white-space:pre;animation:wi .6s cubic-bezier(.16,.84,.24,1) var(--d,0s)}
@keyframes wi{from{opacity:0;transform:translateY(48px);filter:blur(16px)}}
.rise{animation:ri .65s cubic-bezier(.16,.84,.24,1) var(--d,0s)}@keyframes ri{from{opacity:0;transform:translateY(34px)}}
.grow{transform-origin:var(--o,left);animation:gr .7s cubic-bezier(.16,.84,.24,1) var(--d,0s)}@keyframes gr{from{transform:scaleX(0)}}
.pop{animation:po .55s cubic-bezier(.2,1.5,.4,1) var(--d,0s)}@keyframes po{from{opacity:0;transform:scale(.4)}}
.slam{animation:sl .38s cubic-bezier(.2,.9,.3,1) var(--d,0s)}@keyframes sl{from{opacity:0;transform:scale(2.8) rotate(-4deg)}}
.hl{color:var(--a);text-shadow:0 0 44px var(--a)}
.k{font-family:var(--kf);font-weight:700;letter-spacing:.38em;font-size:30px;color:var(--a);text-transform:uppercase;margin-bottom:18px}
.rule{width:130px;height:5px;background:var(--a);box-shadow:0 0 28px var(--a);margin-bottom:30px;border-radius:3px}
.t{font-weight:var(--tw);font-size:var(--tsz,112px);line-height:1.06;letter-spacing:var(--ts);text-shadow:0 6px 40px rgba(0,0,0,.8)}
.lt .t{--tsz:92px;max-width:1500px}
.s{font-family:var(--kf);font-size:42px;color:var(--sub);line-height:1.35;margin-top:22px;max-width:1350px;font-weight:500}
.big{font-size:320px;font-weight:800;line-height:1;color:var(--a);text-shadow:0 0 100px var(--a);letter-spacing:-.03em;font-variant-numeric:tabular-nums;animation:po .6s cubic-bezier(.2,1.2,.4,1)}
.q{font-style:italic;font-size:96px;line-height:1.14;max-width:1550px;font-weight:var(--tw)}
.qm{font-size:260px;line-height:.6;color:var(--a);height:120px;font-family:Georgia,'DejaVu Serif',serif}
.doc{background:linear-gradient(170deg,#e4dac2,#cfc4a8);color:#1c1812;font-family:'JetBrains Mono','DejaVu Sans Mono',monospace;width:1180px;padding:60px 76px;text-align:left;box-shadow:0 50px 140px #000;animation:docin .7s cubic-bezier(.16,.84,.24,1)}
@keyframes docin{from{opacity:0;transform:translateY(120px) rotate(6deg)}to{transform:rotate(-1.6deg)}}
.doc .h{font-weight:800;font-size:40px;border-bottom:4px solid #1c1812;padding-bottom:16px;margin-bottom:26px;letter-spacing:.12em}
.doc .l{font-size:42px;line-height:1.75;font-weight:500;position:relative;width:max-content;padding:0 14px;margin-left:-14px;animation:ty .5s steps(18) var(--d)}
@keyframes ty{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
.doc .l i{position:absolute;inset:6px 0;background:#b3261e;z-index:-1;transform-origin:left;animation:gr .32s ease-out var(--h,9999s)}
.doc .l.x{animation:ty .5s steps(18) var(--d),inv .01s linear var(--h)}@keyframes inv{to{color:#fff}}
.stamp{position:absolute;right:60px;bottom:50px;border:8px solid #b3261e;color:#b3261e;font-family:var(--kf);font-weight:900;font-size:64px;padding:6px 26px;letter-spacing:.1em;transform:rotate(-12deg);animation:sl .35s cubic-bezier(.2,.9,.3,1) var(--d)}
.bw{font-size:180px;font-weight:700;margin:0 34px;display:inline-block;opacity:.12;animation:bw .28s ease-out var(--d)}
@keyframes bw{from{opacity:.12;transform:scale(1)}60%{transform:scale(1.25)}to{opacity:1;color:var(--a);text-shadow:0 0 80px var(--a);transform:scale(1)}}
.chip{display:inline-block;padding:22px 36px;margin:11px;border-radius:20px;font-size:56px;font-weight:700;background:#ffffff12;border:2px solid #ffffff2a;backdrop-filter:blur(6px);animation:po .5s cubic-bezier(.2,1.5,.4,1) var(--d,0s),lit .3s ease var(--on,99999s),dimm .4s ease var(--off,99999s)}
@keyframes lit{to{background:var(--a);color:#06102a;border-color:var(--a);box-shadow:0 0 60px var(--a)}}
@keyframes dimm{to{opacity:.22}}
.sm{white-space:nowrap;margin-top:150px}.sm .chip{font-size:41px;padding:16px 22px;margin:7px;border-radius:14px}
.num{font-family:'JetBrains Mono',monospace;font-size:32px;color:var(--a);display:block;margin-top:10px;font-weight:500;animation:ri .5s ease var(--nd,99999s)}
.row{display:flex;align-items:center;gap:28px;font-size:44px;font-weight:700;margin:16px 0;animation:ri .5s ease var(--d)}
.row b{width:260px;text-align:right}.row.lo{color:#8b96bd}
.bar{height:60px;border-radius:14px;background:linear-gradient(90deg,var(--a),#9b7bff);display:flex;align-items:center;padding-left:22px;font-size:34px;font-weight:800;color:#06102a;white-space:nowrap;transform-origin:left;animation:gr .9s cubic-bezier(.16,.84,.24,1) var(--d);box-shadow:0 0 40px -6px var(--a)}
.row.lo .bar{background:#ffffff26;color:#dfe5ff;box-shadow:none}
.map{position:relative;width:1560px;height:610px;border:2px solid #ffffff22;border-radius:30px;background:#ffffff09;overflow:hidden}
.pt{position:absolute;font-size:46px;font-weight:800;white-space:nowrap;animation:po .5s cubic-bezier(.2,1.5,.4,1) var(--d)}
.pt:before{content:'';display:inline-block;width:28px;height:28px;border-radius:50%;background:currentColor;box-shadow:0 0 34px currentColor;margin-right:16px}
.ring{position:absolute;border:3px dashed var(--a);border-radius:50%;animation:po .6s ease var(--d)}
.dial{width:118px;height:118px;border-radius:50%;border:6px solid #ffffff33;position:relative;background:#ffffff0d;animation:po .4s ease var(--d)}
.dial i{position:absolute;left:53px;top:11px;width:8px;height:50px;border-radius:4px;background:var(--a);box-shadow:0 0 18px var(--a);transform-origin:50% 100%;animation:nd var(--dur) cubic-bezier(.4,0,.2,1)}
@keyframes nd{0%{transform:rotate(var(--r0))}30%{transform:rotate(var(--r1))}55%{transform:rotate(var(--r2))}80%{transform:rotate(var(--r3))}100%{transform:rotate(var(--r4))}}
.st{font-size:58px;font-weight:600;margin:24px 0;display:flex;align-items:center;opacity:.18;animation:stl .4s ease var(--d)}
@keyframes stl{to{opacity:1}}
.st u{text-decoration:none;display:inline-block;width:88px;height:88px;line-height:88px;text-align:center;border-radius:50%;background:#ffffff30;color:#06102a;font-weight:900;margin-right:32px;flex:none;animation:stn .4s ease var(--d)}
@keyframes stn{to{background:var(--a);box-shadow:0 0 40px var(--a)}}
.st b{color:var(--a)}
svg.arc{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none}svg.arc path{fill:none;stroke:var(--a);stroke-width:7;stroke-linecap:round;filter:drop-shadow(0 0 14px var(--a));stroke-dasharray:1;stroke-dashoffset:1;animation:dr .8s ease-out var(--d)}
@keyframes dr{to{stroke-dashoffset:0}}
.paper{background:#f2efe6;color:#111;font-family:'DejaVu Serif',serif;width:1000px;padding:70px;text-align:center;box-shadow:0 50px 140px #000;animation:docin .7s cubic-bezier(.16,.84,.24,1)}
"""
JS="""window.__seek=t=>{document.getAnimations().forEach(a=>{a.pause();a.currentTime=t});
document.querySelectorAll('.cnt').forEach(e=>{const d=(+e.dataset.d||0)*1000,L=(+e.dataset.len||1.3)*1000;let p=Math.min(1,Math.max(0,(t-d)/L));p=1-Math.pow(1-p,4);const v=Math.round(+e.dataset.to*p);e.textContent=(e.dataset.pre||'')+(e.dataset.nc?String(v):v.toLocaleString('en-US'))+(e.dataset.suf||'');});};
window.__init=()=>{const R=e=>{let x=0,y=0,n=e;while(n){x+=n.offsetLeft;y+=n.offsetTop;n=n.offsetParent}return {l:x,t:y,w:e.offsetWidth}};
document.querySelectorAll('[data-arc]').forEach(s=>{const [f,t]=s.dataset.arc.split(',').map(i=>R(document.getElementById(i)));const x1=f.l+f.w/2,x2=t.l+t.w/2,y=Math.min(f.t,t.t)-8,hh=Math.min(170,50+Math.abs(x2-x1)*0.22);s.innerHTML=`<path pathLength="1" d="M${x1} ${y} C${x1} ${y-hh},${x2} ${y-hh},${x2} ${y}"/>`;});};"""
def _h(s): return int(hashlib.md5(s.encode()).hexdigest(),16)
def page(theme,a,layers,inner,cls=''):
    return f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body style=\"{TH[theme]};--a:{a};--dur:__DUR__s\">{layers}<div class='c {cls}'>{inner}</div><script>{JS}</script></body></html>"
def W(text,d0=.15,step=.075):
    out=[];k=0;hl=False
    for li,line in enumerate(text.split('|')):
        if li: out.append('<br>')
        for tok in line.split(' '):
            if not tok: continue
            st=tok.startswith('*'); en=tok.endswith('*') and len(tok)>1; tok=tok.strip('*')
            if st: hl=True
            dd=f"calc({d0}s + {k*step:.2f}s)" if isinstance(d0,str) else f"{d0+k*step:.2f}s"
            out.append(f"<span class='w{' hl' if hl else ''}' style='--d:{dd}'>{tok} </span>"); k+=1
            if en: hl=False
    return ''.join(out),(d0 if isinstance(d0,str) else d0+k*step)
def txt(t='',k='',s='',d0=.15,rule=True,step=.075):
    h='';d=d0
    if k: h+=f"<div class='k rise' style='--d:{d0:.2f}s'>{k}</div>"; d0+=.12
    if rule and t: h+=f"<div class='rule grow' style='--d:{d0:.2f}s'></div>"
    if t:
        lines=t if isinstance(t,list) else [(t,d0+.1)]; parts=[]
        for tx,dl in lines: ww,d=W(tx,dl,step); parts.append(ww)
        h+=f"<div class=t>{'<br>'.join(parts)}</div>"
    if s:
        sd=f"calc({d}s + .5s)" if isinstance(d,str) else f"{d+.15:.2f}s"
        h+=f"<div class='s rise' style='--d:{sd}'>{s}</div>"
    return h
def bgl(img,a,pos='50% 50%',fx='',blur=0,dim=1.0,key=''):
    h=_h(img+key); z0,z1=(1.02,1.15) if h%2 else (1.15,1.03); x1=[-1.6,1.6,0,-1.2][h%4]; y1=[0,-.8,.9,.6][(h//4)%4]
    gr=f"contrast(1.08) saturate(.82) brightness({.86*dim})"+(f" blur({blur}px)" if blur else '')
    L=f"<div class=bg style=\"background-image:url('file://{ROOT}/{img}');--pos:{pos};--z0:{z0};--z1:{z1};--x0:0%;--y0:0%;--x1:{x1}%;--y1:{y1}%;--grade:{gr}\"></div><div class=tint></div><div class=vig></div>"
    if 'fog' in fx: L+="<div class=fog></div>"
    if 'motes' in fx:
        for i in range(26):
            r=_h(f'{img}{i}'); L+=f"<div class=mote style='left:{r%100}%;top:{20+(r//100)%75}%;--md:{4+(r//7)%5}s;--mdl:-{(r//11)%8}.{r%9}s;--mx:{(r//13)%120-60}px'></div>"
    if 'open' in fx: L+="<div class=open></div>"
    if 'flash' in fx: L+="<div class=flash></div>"
    return L
def techbg(a,fx='',key=''):
    h=_h(key+a); L=f"<div class=base></div><div class=grid></div><div class=orb style='width:700px;height:700px;left:{h%60}%;top:{(h//7)%40}%;background:{a};--ox:{(h//3)%300-150}px;--oy:{(h//5)%200-100}px'></div><div class=orb style='width:560px;height:560px;right:{(h//11)%40}%;bottom:-10%;background:#9b7bff;--ox:{(h//13)%240-120}px;--oy:-90px'></div>"
    if 'open' in fx: L+="<div class=open></div>"
    return L
def cnt(to,pre='',suf='',d=.2,nc=False,ln=1.3): return f"<span class=cnt data-to='{to}' data-pre='{pre}' data-suf='{suf}' data-d='{d}' data-len='{ln}' {'data-nc=1' if nc else ''}>{pre}0{suf}</span>"
