import os
ROOT=os.path.dirname(os.path.abspath(__file__))
CSS={
'dark':"""body{background:radial-gradient(ellipse at 50% 40%,#1a1714 0%,#0a0908 70%,#040404 100%);color:#ece4d4;font-family:'DejaVu Serif',serif}
.k{font-family:'Inter';font-weight:700;letter-spacing:.42em;font-size:26px;color:var(--a);text-transform:uppercase}
.t{font-weight:700;font-size:118px;line-height:1.04;letter-spacing:-.01em;margin:26px 0}
.s{font-family:'Inter';font-size:40px;color:#b9b0a0;line-height:1.35;max-width:1300px}
.rule{width:140px;height:5px;background:var(--a);margin:0 auto 34px;box-shadow:0 0 30px var(--a)}""",
'tech':"""body{background:radial-gradient(ellipse at 50% 30%,#18224a 0%,#0b1024 60%,#060914 100%);color:#f2f5ff;font-family:'Inter Display','Inter',sans-serif}
body:before{content:'';position:absolute;inset:0;background-image:linear-gradient(#ffffff0a 1px,transparent 1px),linear-gradient(90deg,#ffffff0a 1px,transparent 1px);background-size:80px 80px}
.k{font-weight:700;letter-spacing:.34em;font-size:26px;color:var(--a);text-transform:uppercase}
.t{font-weight:800;font-size:112px;line-height:1.05;letter-spacing:-.03em;margin:26px 0}
.s{font-size:42px;color:#aab4d6;line-height:1.35;max-width:1300px}
.rule{width:120px;height:6px;border-radius:3px;background:var(--a);margin:0 auto 34px;box-shadow:0 0 30px var(--a)}
.chip{display:inline-block;padding:22px 34px;margin:10px;border-radius:18px;font-size:54px;font-weight:700;background:#ffffff10;border:2px solid #ffffff25}
.chip.on{background:var(--a);color:#06102a;border-color:var(--a);box-shadow:0 0 50px var(--a)}
.chip.dim{opacity:.28}
.num{font-family:'DejaVu Sans Mono',monospace;font-size:30px;color:var(--a);display:block;margin-top:10px;font-weight:400}
.bar{height:54px;border-radius:12px;background:linear-gradient(90deg,var(--a),#9b7bff);margin:14px 0;display:flex;align-items:center;padding-left:22px;font-size:34px;font-weight:700;color:#06102a;white-space:nowrap}
.row{display:flex;align-items:center;gap:26px;font-size:40px;font-weight:600}.row b{width:230px;text-align:right}"""}
BASE="""*{box-sizing:border-box;margin:0;padding:0}html,body{width:1920px;height:1080px;overflow:hidden;position:relative}
.c{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:90px 150px 230px}
.hl{color:var(--a);text-shadow:0 0 40px var(--a)} .ph{position:absolute;inset:0;background-size:cover}
.ov{position:absolute;inset:0}.big{font-size:330px;font-weight:800;line-height:1;color:var(--a);text-shadow:0 0 90px var(--a);letter-spacing:-.03em}
.q{font-style:italic;font-size:92px;line-height:1.15;max-width:1500px}
.doc{background:#d9cfb8;color:#1c1812;font-family:'DejaVu Sans Mono',monospace;width:1100px;padding:60px 70px;text-align:left;transform:rotate(-1.5deg);box-shadow:0 40px 120px #000}
.doc h{display:block;font-weight:700;font-size:40px;border-bottom:4px solid #1c1812;padding-bottom:16px;margin-bottom:24px;letter-spacing:.1em}
.doc p{font-size:40px;line-height:1.7}.doc p.x{background:#b3261e;color:#fff;padding:0 14px;display:inline-block}
.w{font-size:170px;font-weight:700;margin:0 30px;opacity:.13}.w.on{opacity:1;color:var(--a);text-shadow:0 0 70px var(--a)}"""
def page(theme,inner,a):
    return f"<!doctype html><html><head><meta charset=utf-8><style>{BASE}{CSS[theme]}</style></head><body style='--a:{a}'>{inner}</body></html>"
def _txt(k,t,s,rule=True):
    return (f"<div class=rule></div>" if rule else "")+(f"<div class=k>{k}</div>" if k else "")+(f"<div class=t>{t}</div>" if t else "")+(f"<div class=s>{s}</div>" if s else "")
def T(theme,a,t='',k='',s=''): return page(theme,f"<div class=c>{_txt(k,t,s)}</div>",a)
def P(theme,a,photo,t='',k='',s='',pos='50% 50%',dark=.5,gray=.75):
    return page(theme,f"<div class=ph style=\"background-image:url('file://{ROOT}/photos/{photo}.jpg');background-position:{pos};filter:grayscale({gray}) contrast(1.15) brightness(.8)\"></div><div class=ov style='background:{a};mix-blend-mode:soft-light;opacity:.5'></div><div class=ov style='background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,{dark*.6}) 0%,rgba(0,0,0,{min(1,dark+.42)}) 100%)'></div><div class=c>{_txt(k,t,s,rule=bool(t))}</div>",a)
def N(theme,a,num,label='',k=''): return page(theme,f"<div class=c>"+(f"<div class=k>{k}</div>" if k else "")+f"<div class=big>{num}</div><div class=s style='margin-top:20px'>{label}</div></div>",a)
def Q(theme,a,q,who=''): return page(theme,f"<div class=c><div class=q>&ldquo;{q}&rdquo;</div><div class=k style='margin-top:50px'>{who}</div></div>",a)
def D(theme,a,head,lines,hi=()): return page(theme,"<div class=c><div class=doc><h>"+head+"</h>"+"".join(f"<p class='{'x' if i in hi else ''}'>{l}</p><br>" if i in hi else f"<p>{l}</p>" for i,l in enumerate(lines))+"</div></div>",a)
def Wd(theme,a,words,n): return page(theme,"<div class=c><div style='display:flex'>"+"".join(f"<div class='w {'on' if i<n else ''}'>{w}</div>" for i,w in enumerate(words))+"</div></div>",a)
def R(theme,a,html): return page(theme,f"<div class=c>{html}</div>",a)
