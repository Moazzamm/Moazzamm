from lib2 import *
C_,V,Y,PK,GR='#4de1ff','#b79bff','#ffd24d','#ff6b9d','#5dffa0'
MUSIC='tech'; GRAIN=0; CAPSIZE=60; MUSICVOL=0.32
def S(h,at=None,sfx=None): return {'h':h,'at':at,'sfx':sfx}
c=lambda p:f'@@{p}@@'
def Pt(a,img,t='',k='',s='',pos='50% 50%',fx='',at=None,sfx=None): return S(page('tech',a,bgl(f'{img}.png',a,pos,fx,key=str(t)+k),txt(t,k,s),'lt'),at,sfx)
def Ct(a,t,k='',s='',fx='',at=None,sfx=None): return S(page('tech',a,techbg(a,fx,key=str(t)),txt(t,k,s)),at,sfx)
def R(a,inner,at=None,sfx=None,fx=''): return S(page('tech',a,techbg(a,fx,key=inner[:40]),inner),at,sfx)
def head(h,d=.1): return f"<div class='k rise' style='--d:{d}s;margin-bottom:40px'>{h}</div>" if h else ''
def foot(f,d): return f"<div class='s rise' style='--d:{d}s;margin-top:46px'>{f}</div>" if f else ''
def chips(a,items,hd='',ft='',fd=.6,at=None,sfx='pop',arcs=(),fx=''):
    h=(head(hd) if not arcs else '')+("<div class=sm>" if arcs else "<div style='max-width:1650px'>")
    for i,it in enumerate(items):
        it=list(it)+[None]*4; lab,d,on,off,num=it[:5]
        st=f"--d:{d}s"+(f";--on:{on}s" if on is not None else '')+(f";--off:{off}s" if off is not None else '')
        h+=f"<span class=chip id=c{i} style='{st}'>{lab}"+(f"<span class=num style='--nd:{num[1]}s'>{num[0]}</span>" if num else '')+"</span>"
    h+="</div>"+(foot(hd,.3) if arcs and hd and not ft else '')+foot(ft,fd)+''.join(f"<svg class=arc data-arc='c{f},c{t}' style='--d:{d}s'></svg>" for f,t,d in arcs)
    return R(a,h,at,sfx,fx)
def bars(a,sent,items,hd='',pick=0,d0=.5,at=None,sfx='pop'):
    ww,_=W(sent+' *____*',.2,.09); h=head(hd)+f"<div class=t style='--tsz:92px'>{ww}</div><div style='width:1250px;margin-top:40px'>"
    for i,(w,p) in enumerate(items):
        d=f"calc({d0}s + {i*.16:.2f}s)" if isinstance(d0,str) else f"{d0+i*.16:.2f}s"
        h+=f"<div class='row{'' if i==pick else ' lo'}' style='--d:{d}'><b>{w}</b><div class=bar style='width:{max(p,7)*10}px;--d:{d}'>{p}%</div></div>"
    return R(a,h+"</div>",at,sfx)
def mp(a,pts,rings,hd,at=None):
    h=head(hd)+"<div class=map>"+''.join(f"<div class=pt style='left:{x}%;top:{y}%;color:{col};--d:{d}s'>{l}</div>" for x,y,l,col,d in pts)
    h+=''.join(f"<div class=ring style='left:{x}%;top:{y}%;width:{w}px;height:{hh}px;--d:{d}s;--a:{col}'></div>" for x,y,w,hh,col,d in rings)
    return R(a,h+"</div>",at,'pop')
def dials(a,ft,seed=1,at=None,settle=False):
    import random; random.seed(seed); h="<div style='display:grid;grid-template-columns:repeat(10,118px);gap:24px'>"
    for i in range(30):
        r=[random.randint(-140,140) for _ in range(5)]
        if settle: r[3]=r[4]=int(-60+120*(i%10)/9)
        h+=f"<div class=dial style='--d:{i*.02:.2f}s'><i style='--r0:{r[0]}deg;--r1:{r[1]}deg;--r2:{r[2]}deg;--r3:{r[3]}deg;--r4:{r[4]}deg'></i></div>"
    return R(a,h+"</div>"+foot(ft,.6),at,'ticks')
def N(a,to,label,pre='',suf='',at=None,sfx='boom'): return R(a,f"<div class=big>{cnt(to,pre,suf,.15)}</div><div class='s rise' style='--d:.9s;font-size:52px'>{label}</div>",at,sfx)
def steps(a,cues,at=None):
    T=['Words become <b>&nbsp;tokens</b>','Tokens become <b>&nbsp;numbers&nbsp;</b> on a map of meaning','<b>Attention&nbsp;</b> works out what matters','Predict <b>&nbsp;one word</b>. Then the next.']
    return R(a,head('Put it together')+"<div style='text-align:left'>"+''.join(f"<div class=st style='--d:{d}s'><u style='--d:{d}s'>{i+1}</u>{s}</div>" for i,(s,d) in enumerate(zip(T,cues)))+"</div>",at,'pop',fx='open')
TR=['The','trophy',"didn't",'fit','in','the','suitcase','because','it','was','too','big']
SHOTS=[
[[Pt(C_,'ai/21',t="It has *no idea*|what it's about to say",k='Every time you ask ChatGPT',fx='open'),
  chips(C_,[('The',.1),('answer',.3),('is',.5),('?',.8,1.0)],ft='Not even the next sentence',fd=c('Not even'),at='Not the full'),
  Ct(C_,[('*Guessing.*',.15),('One word at a time',c('One word'))],at='It is guessing',sfx='hit')],
 [chips(V,[('Poems',c('poems'),c('poems')),('Code',c('fix code'),c('fix code')),('Law exams',c('pass a'),c('pass a'))],hd='And yet it can',sfx='cut'),Ct(Y,'So&hellip; *how?*',at='So how',sfx='boom'),Ct(Y,[('*6 minutes.*',.15),('No math. No jargon.',c('No math'))],at='Give me'),Pt(C_,'ai/32',t='Understand A.I.|*better than most*',k='By the end',at='By the end')]],
[[Pt(C_,'ai/22',t='Start with your phone',k='Part 1',fx='open',sfx='whoosh'),bars(C_,"I'm on my",[('way',71),('phone',12),('bike',6)],hd='Your keyboard',d0=c('your keyboard'),at='When you type'),Ct(C_,'*Autocomplete*',s='It has seen millions of messages',at="That's autocomplete",sfx='chime')],
 [Ct(V,'Large Language Model',k='L &middot; L &middot; M',s='The same idea &mdash; scaled up to an absurd level'),bars(V,'The cat sat on the',[('mat',62),('floor',14),('sofa',9),('moon',1)],d0=c('It predicts'),at='You give it'),
  chips(V,[('The',.05),('cat',.1),('sat',.15),('on',.2),('the',.25),('mat',.5,.6),('and',c('and predicts'),c('and predicts')),('purred',c('And again#1'),c('And again#1')),('softly',c('And again#2'),c('And again#2'))],ft='Add the word. Predict again.',at='Then it adds')],
 [Ct(C_,"That's the *whole trick.*"),chips(C_,[('ChatGPT',.1,.2),('Claude',c('Claude,'),c('Claude,')),('Gemini',c('Gemini'),c('Gemini'))],ft='One game: guess what comes next',fd=c('one game'),at='ChatGPT,'),Ct(Y,'How *good*|are the guesses?',at='The magic')]],
[[Ct(PK,'The A.I. never|actually *sees words*',k='First surprise',fx='open',sfx='whoosh'),Ct(PK,'Only *numbers.*',at='Computers only',sfx='hit')],
 [Ct(PK,'Unbelievable!',k='Your sentence'),chips(PK,[('Un',.1,.5,None,('1844',c('Then every'))),('believ',.2,.6,None,('31021',c('Then every'))),('able',.3,.7,None,('481',c('Then every'))),('!',.4,.8,None,('0',c('Then every')))],hd='Chopped into tokens',ft='A token = a word, or a chunk of a word',fd=c('A token'),at='chopped')],
 [Pt(C_,'ai/26',t='A map of *meaning*',k='Think of coordinates'),mp(C_,[(12,20,'cat',C_,c('cat sits')),(21,40,'dog',C_,c('dog.')),(58,14,'Paris',V,c('Paris')),(69,34,'France',V,c('France.')),(40,76,'banana',Y,c('banana'))],[(8,10,470,330,C_,c('dog.')),(54,4,520,340,V,c('France.'))],'A map of meaning',at='On this map')],
 [Ct(Y,'Math with *ideas*'),chips(Y,[('king',.1),('&minus;',c('subtract')),('man',c('subtract')),('+',c('add woman')),('woman',c('add woman')),('=',c('and you land')),('queen',c('queen'),c('queen'))],at='Take king'),Ct(Y,[('Nobody taught it that.',.15),('*It figured it out.*',c('It figured'))],at='Nobody taught'),Ct(Y,'*How?*',s='This is the wildest part',at='And how',sfx='boom')]],
[[Ct(GR,'*Training*',k='Part 2',fx='open',sfx='whoosh'),Pt(GR,'ai/23',k='A huge slice of the internet',at='Engineers'),chips(GR,[('Books',.1,.1),('Articles',c('articles'),c('articles')),('Websites',c('websites'),c('websites')),('Code',c('code.'),c('code.'))],at='Books,',sfx='cut'),N(GR,1000,'of lifetimes of reading',suf='s',at='More text')],
 [Ct(GR,'A guessing *game*'),bars(GR,'The sky is',[('green',41),('blue',33),('loud',6)],hd='Hide the next word. Make it guess.',d0=c('Make it'),at='Hide the'),bars(GR,'The sky is',[('blue',79),('green',9),('loud',1)],hd='Wrong? Nudge it toward the right answer.',d0=.4,at="If it's wrong"),Ct(GR,'*Trillions*',s='of practice rounds',at='trillions',sfx='hit')],
 [Pt(GR,'ai/25',t='*Billions* of little dials',k='Inside the model'),dials(GR,'<b>Parameters</b> &mdash; every wrong guess turns them slightly',1,at='called parameters'),Ct(GR,[('Nobody programs grammar.',.15),('Nobody types in facts.',c('Nobody types'))],at='Nobody programs'),dials(GR,'They settle into the shape of human language',2,at='The dials just',settle=True)],
 [Pt(Y,'ai/24',t=[('Months.',.2),('Warehouses of chips.',c('warehouses')),('*Millions of dollars.*',c('many millions'))],k='The cost'),Ct(Y,'One more *ingredient*',s='The reason A.I. suddenly got good',at='But guessing',sfx='boom')]],
[[Pt(V,'ai/27',k='Read this sentence',fx='open',sfx='whoosh'),
  chips(V,[(w,f'{.05+i*.06:.2f}',(c('What does') if i==8 else c('The trophy, obviously') if i==1 else None)) for i,w in enumerate(TR)],ft='What does &ldquo;it&rdquo; mean?',fd=c('What does'),arcs=[(8,1,c('The trophy, obviously'))],at="The trophy didn't"),
  Ct(PK,'But a computer|has *no idea.*',at='But a computer',sfx='boom')],
 [Pt(V,'ai/28',k='2017',t='8 researchers at Google'),R(V,"<div class=paper><div style='font-size:74px;font-weight:700;line-height:1.2'>Attention Is All<br>You Need</div><div style='font-size:32px;color:#555;margin-top:30px;font-family:Inter'>Vaswani et al. &middot; 2017</div></div>",at='Attention Is',sfx='boom'),Ct(V,'The *Transformer*',at='Their idea',sfx='chime'),
  chips(V,[(w,f'{.05+i*.04:.2f}') for i,w in enumerate(TR)],ft='Every word looks at every other word &mdash; and decides which ones matter',fd=c('and decide'),arcs=[(8,1,.6),(8,6,.9),(8,11,1.2),(1,3,1.5),(1,6,1.8),(6,11,2.1),(3,6,2.4)],at='lets every')],
 [chips(V,[(w,f'{.05+i*.04:.2f}',(.5 if i==8 else c('lights up') if i==1 else None),(c('dims') if i==6 else None)) for i,w in enumerate(TR)],hd='Attention',arcs=[(8,1,c('lights up'))]),Pt(V,'ai/21',pos='50% 60%',t='It follows your meaning',s='across a whole conversation',at='That is how'),chips(V,[('G',.1),('P',.2),('T',.3,c("It's the T"))],ft='Generative &middot; Pre-trained &middot; <b>Transformer</b>',fd=c("It's the T"),at='And that',sfx='chime')]],
[[Ct(PK,"A.I.'s biggest *flaw*",k='Now you can understand',fx='open',sfx='whoosh'),Ct(PK,[('Sounds right',.15),('&ne; *is right*',c('Not what'))],at='It is trained',sfx='boom')],
 [Ct(PK,'No database.',s='It predicts plausible words'),Ct(PK,'It confidently|*invents things*',at='So sometimes'),Ct(PK,'*Hallucination*',at='This is called',sfx='hit')],
 [Pt(Y,'ai/29',k='New York &middot; 2023',t='A lawyer used ChatGPT'),N(Y,6,'legal cases cited',at='It cited'),Ct(PK,'*None* of them existed.',at='None of them',sfx='hit'),N(Y,5000,'fine',pre='$',at='five thousand')],
 [Pt(C_,'ai/30',t='A little *randomness*'),bars(C_,'Once upon a',[('time',88),('dream',7),('hill',3)],pick=1,d0=.4,at='The model'),Ct(C_,[('Same question.',.15),('*Different answer.*',c('different answer'))],at="That's why")]],
[[steps(C_,[c('Your words'),c('Tokens become'),c('Attention works'),c('And the model')])],
 [Pt(V,'ai/32',pos='50% 40%',t='Is that really *thinking?*'),Ct(V,'Even experts|still argue.',at='Honestly'),Ct(V,'Now *you know*',s="what's actually happening behind the screen",at='But now',sfx='chime')],
 [Ct(Y,'If guessing words|can do *this&hellip;*'),Pt(Y,'ai/31',t='What happens when it can|*use tools?*',at='wait until',sfx='hit'),Ct(C_,'Watch next &#9654;',s="I'll see you there",at="That's the next")]]]
