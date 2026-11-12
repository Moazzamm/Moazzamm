from lib import *
import random
C,V,Y,PK,GR='#4de1ff','#b79bff','#ffd24d','#ff6b9d','#5dffa0'
BED='light'; GRAIN=3; t='tech'; H=lambda s:f"<span class=hl>{s}</span>"
def T_(a,*x,**k): return T(t,a,*x,**k)
def N_(a,*x,**k): return N(t,a,*x,**k)
def chips(a,ws,on=(),dim=(),nums=None,head='',foot=''):
    h=(f"<div class=k style='margin-bottom:40px'>{head}</div>" if head else '')+"<div>"
    for i,w in enumerate(ws):
        h+=f"<span class='chip {'on' if i in on else ''} {'dim' if i in dim else ''}'>{w}"+(f"<span class=num>{nums[i]}</span>" if nums else '')+"</span>"
    return R(t,a,h+"</div>"+(f"<div class=s style='margin-top:44px'>{foot}</div>" if foot else ''))
def bars(a,sent,items,pick=0,head=''):
    h=(f"<div class=k style='margin-bottom:30px'>{head}</div>" if head else '')+f"<div class=t style='font-size:84px'>{sent} <span class=hl>____</span></div><div style='width:1100px;margin-top:30px'>"
    for i,(w,p) in enumerate(items):
        h+=f"<div class=row style='opacity:{1 if i==pick else .45}'><b>{w}</b><div class=bar style='width:{max(p,6)*9}px'>{p}%</div></div>"
    return R(t,a,h+"</div>")
def mp(a,pts,head='A map of meaning'):
    h=f"<div class=k style='margin-bottom:24px'>{head}</div><div style='position:relative;width:1500px;height:600px;border:2px solid #ffffff22;border-radius:28px;background:#ffffff08'>"
    for x,y,l,c in pts: h+=f"<div style='position:absolute;left:{x}%;top:{y}%;font-size:44px;font-weight:700;color:{c};white-space:nowrap'><span style='display:inline-block;width:26px;height:26px;border-radius:50%;background:{c};box-shadow:0 0 30px {c};margin-right:14px'></span>{l}</div>"
    return R(t,a,h+"</div>")
def dials(a,seed,foot):
    random.seed(seed); h="<div style='display:grid;grid-template-columns:repeat(9,120px);gap:26px'>"
    for i in range(27):
        r=random.randint(-130,130); h+=f"<div style='width:120px;height:120px;border-radius:50%;border:6px solid #ffffff30;position:relative;background:#ffffff0c'><div style='position:absolute;left:54px;top:12px;width:8px;height:50px;border-radius:4px;background:var(--a);box-shadow:0 0 18px var(--a);transform-origin:50% 100%;transform:rotate({r}deg)'></div></div>"
    return R(t,a,h+f"</div><div class=s style='margin-top:50px'>{foot}</div>")
def steps(a,n):
    S=['Words become <b>tokens</b>','Tokens become <b>numbers</b> on a map of meaning','<b>Attention</b> works out what matters','Predict <b>one word</b>. Then the next.']
    h="<div class=k style='margin-bottom:36px'>Put it together</div><div style='text-align:left'>"
    for i,s in enumerate(S): h+=f"<div style='font-size:58px;font-weight:600;margin:26px 0;opacity:{1 if i<n else .16}'><span style='display:inline-block;width:86px;height:86px;line-height:86px;text-align:center;border-radius:50%;background:{'var(--a)' if i<n else '#ffffff30'};color:#06102a;font-weight:800;margin-right:30px'>{i+1}</span>{s}</div>"
    return R(t,a,h+"</div>")
TR=['The','trophy',"didn't",'fit','in','the','suitcase','because','it','was','too','big']
MP=[(12,18,'cat',C),(20,32,'dog',C),(62,14,'Paris',V),(72,28,'France',V),(40,76,'banana',Y)]
EQ=['king','&minus;','man','+','woman','=']
SHOTS=[
[[T_(C,'It has no idea<br>what it&rsquo;s about to say',k='Every time you ask ChatGPT'),chips(C,['The','answer','is','?'],on=(3,)),T_(C,H('Guessing.'),s='One word at a time')],
 [chips(V,['Poems','Code','Law exams'],on=(0,1,2),head='And yet it can do'),T_(Y,'So&hellip; how?'),T_(Y,'6 minutes.',s='No math. No jargon.'),T_(C,'Understand A.I.',k='By the end',s='better than most people who use it every day')]],
[[T_(C,'Start with your phone',k='Part 1'),bars(C,"I'm on my",[('way',71),('phone',12),('bike',6)],head='Your keyboard'),T_(C,'Autocomplete',s='It has seen millions of messages')],
 [T_(V,'Large Language Model',k='L &middot; L &middot; M',s='The same idea &mdash; scaled up to an absurd level'),bars(V,'The cat sat on the',[('mat',62),('floor',14),('sofa',9),('moon',1)]),chips(V,['The','cat','sat','on','the','mat'],on=(5,),foot='Add the word. Predict again.'),chips(V,['The','cat','sat','on','the','mat','and'],on=(6,),foot='And again.'),chips(V,['The','cat','sat','on','the','mat','and','purred'],on=(7,),foot='And again.')],
 [chips(C,['ChatGPT','Claude','Gemini'],on=(0,1,2)),T_(C,'One game:',s='Guess what comes next'),T_(Y,'How '+H('good')+' are the guesses?')]],
[[T_(PK,'The A.I. never sees words',k='First surprise'),T_(PK,H('Only numbers.'))],
 [chips(PK,['Unbelievable!'],head='Your sentence'),chips(PK,['Un','believ','able','!'],on=(0,1,2,3),head='Chopped into tokens'),chips(PK,['Un','believ','able','!'],nums=['1844','31021','481','0'],head='Each token becomes numbers')],
 [T_(C,'A map of meaning',k='Think of coordinates'),mp(C,MP[:2]),mp(C,MP[:4]),mp(C,MP)],
 [chips(Y,EQ+['?'],on=(6,),head='Math with ideas'),chips(Y,EQ+['queen'],on=(6,),head='Math with ideas'),T_(Y,'Nobody taught it that.',s='It figured it out.'),T_(Y,'How?',s='This is the wildest part')]],
[[T_(GR,'Training',k='Part 2'),chips(GR,['Books','Articles','Websites','Code'],on=(0,1,2,3),head='A huge slice of the internet'),N_(GR,'1000s','of lifetimes of reading')],
 [bars(GR,'The sky is',[('green',40),('blue',35),('loud',5)],pick=0,head='Hide the next word. Guess.'),bars(GR,'The sky is',[('blue',78),('green',9),('loud',1)],pick=0,head='Wrong? Nudge it. Try again.'),N_(GR,'Trillions','of practice rounds')],
 [dials(GR,1,'Billions of little dials'),dials(GR,2,'&hellip;called <b>parameters</b>'),dials(GR,3,'Every wrong guess turns them slightly'),T_(GR,'Nobody programs grammar.',s='Nobody types in facts.'),dials(GR,4,'The dials settle into the shape of human language')],
 [chips(Y,['Months','Warehouses of chips','$ Millions'],on=(0,1,2),head='The cost'),T_(Y,'One more ingredient',s='The reason A.I. suddenly got good')]],
[[chips(V,TR,on=(8,),head='Read this sentence',foot='What does &ldquo;it&rdquo; mean?'),chips(V,TR,on=(1,8),dim=(2,3,4,5,6,7,9,10,11),head='The trophy. Obviously.'),T_(PK,'But a computer<br>has no idea.')],
 [N_(V,'2017','8 researchers at Google'),R(t,V,"<div class=doc style='font-family:DejaVu Serif;text-align:center;transform:rotate(-2deg)'><p style='font-size:64px;font-weight:700;line-height:1.2'>Attention Is All<br>You Need</p><br><p style='font-size:30px;color:#555'>Vaswani et al. &middot; 2017</p></div>"),T_(V,'The Transformer',s='Every word looks at every other word &mdash; and decides which ones matter')],
 [chips(V,TR,on=(1,8),dim=(6,),head='Attention',foot='&ldquo;it&rdquo; lights up <b>trophy</b> &mdash; and dims suitcase'),T_(V,'It follows your meaning',s='across a whole conversation'),chips(V,['G','P','T'],on=(2,),foot='Generative &middot; Pre-trained &middot; <b>Transformer</b>')]],
[[T_(PK,'A.I.&rsquo;s biggest flaw',k='Now you can understand'),T_(PK,'Sounds right',s='is not the same as <b>is right</b>')],
 [T_(PK,'No database.',s='It predicts plausible words'),T_(PK,H('Hallucination'),s='Confidently inventing things')],
 [N_(Y,'2023','A New York lawyer used ChatGPT for a court filing'),N_(PK,'6','legal cases cited &mdash; none of them existed'),N_(Y,'$5,000','fine')],
 [bars(C,'Once upon a',[('time',88),('dream',7),('hill',3)],pick=1,head='A little randomness'),T_(C,'Same question.',s='Different answer every time.')]],
[[steps(C,1),steps(C,2),steps(C,3),steps(C,4)],
 [T_(V,'Is that really<br>thinking?'),T_(V,'Even experts still argue.',s='But now you know what happens behind the screen')],
 [T_(Y,'If guessing words<br>can do this&hellip;'),T_(Y,'What happens when it can<br>'+H('use tools')+'?'),T_(C,'&#9654;',k='Next video',s='I&rsquo;ll see you there')]]]
