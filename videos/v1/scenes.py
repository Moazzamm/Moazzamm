from lib2 import *
A,G,B,RD='#e8a838','#6dff8f','#9fd0f0','#ff5a3c'
MUSIC='dark'; GRAIN=5; CAPHL='&H0038A8E8'; CAPSIZE=58
TAG="<div style='position:absolute;top:44px;right:60px;font-family:var(--kf);font-size:19px;letter-spacing:.32em;opacity:.42;font-weight:600'>AI RECONSTRUCTION</div>"
def S(h,at=None,sfx=None): return {'h':h,'at':at,'sfx':sfx}
def P(a,img,t='',k='',s='',pos='50% 50%',fx='',at=None,sfx=None):
    return S(page('dark',a,bgl(f'{img}.png' if img.startswith('ai/') else f'{img}.jpg',a,pos,fx,key=str(t)+k+pos)+(TAG if img.startswith('ai/') else ''),txt(t,k,s),'lt'),at,sfx)
def bk(img,a,fx=''): return bgl(f'{img}.png' if img.startswith('ai/') else f'{img}.jpg',a,fx=fx,blur=26,dim=.42,key='b')
def C(a,t,k='',s='',img='ai/08',fx='',at=None,sfx=None): return S(page('dark',a,bk(img,a,fx),txt(t,k,s)),at,sfx)
def N(a,to,label,pre='',suf='',img='ai/08',at=None,sfx='boom',nc=False,k=''):
    return S(page('dark',a,bk(img,a),(f"<div class='k rise'>{k}</div>" if k else '')+f"<div class=big>{cnt(to,pre,suf,.15,nc)}</div><div class='s rise' style='--d:.9s;font-size:50px'>{label}</div>"),at,sfx)
def Q(a,q,who,img,at=None,sfx='boom'):
    ww,d=W(q,.35,.11); return S(page('dark',a,bk(img,a),f"<div class='qm pop'>&ldquo;</div><div class=q>{ww}</div><div class='k rise' style='--d:{d+.3:.2f}s;margin-top:50px'>{who}</div>"),at,sfx)
def D(a,head,lines,img,at=None,stamp=None):
    h=f"<div class=doc><div class=h>{head}</div>"+''.join(f"<div class='l{' x' if hi else ''}' style='--d:{d}s;--h:{hi or 99999}s'>{'<i></i>' if hi else ''}{tx}</div>" for tx,d,hi in lines)
    if stamp: h+=f"<div class=stamp style='--d:{stamp[1]}s'>{stamp[0]}</div>"
    return S(page('dark',a,bk(img,a),h+"</div>"),at,'ticks')
def BW(a,ws,cues,img,at=None): return S(page('dark',a,bk(img,a,'motes'),"<div>"+''.join(f"<span class=bw style='--d:{c}s'>{w}</span>" for w,c in zip(ws,cues))+"</div>"),at,'boom')
c=lambda p:f'@@{p}@@'
SHOTS=[
[[P(B,'ai/01',k='San Francisco &middot; 1950',fx='fog open'),P(B,'ai/18',fx='fog',at='sprayed'),N(B,800000,'people breathed it in',img='ai/17',at='Eight hundred',sfx='hit'),C(B,[('Nobody told them.',.15),('*Nobody asked them.*',c('Nobody asked'))],img='ai/17',at='Nobody told')],
 [C(RD,"That's *story three.*",img='ai/01'),P(A,'ai/08',at='And honestly'),P(G,'ai/10',at='not even',fx='motes'),P(B,'ai/16',at='darkest',fx='fog'),C(RD,'*3* true stories',s='your history teacher skipped',img='ai/04',at='These are',sfx='hit')]],
[[P(A,'ai/02',t='Christmas Eve, 1926',k='Story one &middot; The Poisoned Bottles',fx='open',sfx='whoosh'),P(A,'ai/03',k='Bellevue Hospital &middot; New York',at='A man stumbles'),P(A,'ai/03',pos='50% 20%',at='screaming')],
 [P(A,'ai/04',k="He's not alone"),C(A,'*Dozens* dead',s='within days',img='ai/04',at='dozens',sfx='boom'),P(A,'ai/06',t='Not bad moonshine.',at='Not from'),C(RD,'*Poison.*',img='ai/08',at='From poison',sfx='hit'),C(RD,[('Put there *on purpose*',.15),('by their own government',c('by their'))],img='ai/05',at='And the poison')],
 [P(A,'ai/06',pos='70% 50%',k='During Prohibition',t="Here's what happened"),P(A,'photos/jars',k='Bootleggers stole industrial alcohol',at='bootleggers'),P(A,'ai/05',t='&ldquo;Add more poison.&rdquo;',k='Federal order',at='So federal'),
  D(A,'FEDERAL DENATURING FORMULA',[('+ METHYL ALCOHOL',.1,.55),('+ KEROSENE',c('Kerosene'),c('Benzene')),('+ BENZENE',c('Benzene'),c('They knew'))],'ai/05',at='Methyl'),
  C(RD,[('They knew people|would drink it.',.15),('*That was the point.*',c('That was'))],img='ai/08',at='They knew',sfx='hit')],
 [P(A,'ai/07',t='Charles Norris',k='Chief Medical Examiner &middot; New York'),Q(A,'Our national experiment in *extermination*','Charles Norris &middot; 1926','ai/07',at='our national')],
 [P(A,'ai/08',pos='30% 50%',k='By the end of Prohibition'),N(RD,10000,'Americans killed (estimated)',suf='+',img='ai/04',at='at least',sfx='hit'),P(A,'ai/02',pos='75% 50%',k='One supporter shrugged it off',at='One supporter'),Q(A,'Deliberate *suicide*','A supporter of the program','ai/02',at='is committing')],
 [P(A,'ai/05',pos='60% 40%',t='The government poisoned the drinks'),P(A,'ai/06',pos='30% 50%',t='They knew the risk.',at='But at least'),P(G,'ai/09',t='The next victims were told|it was *good for them*',fx='motes',at='The women')]],
[[P(G,'ai/09',pos='50% 30%',k='Story two &middot; New Jersey, 1917',t='The Girls Who Glowed',fx='motes open',sfx='whoosh'),P(G,'photos/watch',k='Glow-in-the-dark watch dials',fx='motes',at='painting watch'),C(G,'*Radium*',k='The secret ingredient',img='ai/12',fx='motes',at='The secret',sfx='hit')],
 [P(G,'ai/10',k='They were taught one technique',fx='motes'),BW(G,['Lip.','Dip.','Paint.'],[.1,c('Dip.'),c('Paint.')],'ai/10',at='Lip.'),N(G,100,'of times a day &mdash; radium in their mouths',suf='s',img='ai/09',at='Hundreds')],
 [C(G,'&ldquo;Harmless.&rdquo;',k='Their bosses said',img='ai/09'),P(G,'ai/10',pos='60% 80%',t='Nails. Teeth.',fx='motes',at='So they'),P(G,'ai/11',t='Glowing like *ghosts*',fx='motes',at='They walked')],
 [P(G,'ai/12',k='Down the hall'),P(G,'ai/12',pos='20% 50%',t='Lead screens. Tongs.',s='Protection &mdash; for the scientists only',at='with lead')],
 [C(RD,'Then the teeth|started *falling out.*',img='ai/14',sfx='boom'),P(G,'ai/13',k='1922',t='Mollie Maggia',s='Dial painter',at='In 1922'),P(G,'ai/14',k='He touched it gently&hellip;',at='He touched'),C(RD,'The bone came away|*in his hand.*',img='ai/14',at='and the bone',sfx='hit')],
 [N(G,24,'years old',img='ai/13'),D(G,'CERTIFICATE OF DEATH',[('Name:  MAGGIA, MOLLIE',.3,None),('Age:   24',.8,None),('Cause: SYPHILIS',1.3,c('syphilis'))],'ai/13',at='Her death',stamp=('FALSE',c('A lie'))),C(RD,'*A lie.*',s='It protected the company &mdash; and destroyed her name',img='ai/09',at='that protected')],
 [P(G,'ai/15',t='Five dying women sued'),C(G,'The company *stalled.*',s='Hoping they would die before the verdict',img='ai/15',at='The company'),C(G,'*1928*',k='They won',img='ai/15',at='They won',sfx='chime'),P(G,'ai/09',pos='50% 20%',t='Worker safety laws',s='that protect you today',at='and their fight')],
 [N(G,1600,'year half-life',img='ai/16'),P(G,'ai/16',t='Still radioactive',s='in their graves',fx='motes fog',at='Those women'),C(G,'*Right now.*',img='ai/16',fx='motes',at='Right now',sfx='boom')],
 [P(G,'ai/11',pos='50% 30%',t='A company poisoned its workers',fx='motes'),P(B,'ai/17',t='What if the target is|*an entire city?*',fx='fog',at='But what',sfx='hit')]],
[[P(B,'photos/gg2',k='Story three &middot; September 1950',t='The Fog',fx='fog open',sfx='whoosh'),P(B,'ai/01',k='US Navy &middot; offshore',fx='fog',at='a US Navy'),P(B,'ai/18',t='Pumping a mist into the fog',fx='fog',at='pumping')],
 [C(B,'*Billions* of bacteria',k='Inside that mist',img='ai/18',fx='fog',sfx='boom'),P(B,'photos/sf',k='A germ-attack test',fx='fog',at='The military'),C(RD,[('So they attacked one.',.15),('*Their own.*',c('Their own'))],img='ai/17',at='So they',sfx='hit')],
 [C(B,'&ldquo;Success&rdquo;',k='The result',img='ai/01'),P(B,'ai/17',pos='20% 60%',fx='fog',at='Nearly all'),N(B,800000,'residents inhaled the bacteria',img='ai/17',at='eight hundred'),C(B,'&ldquo;Harmless&rdquo;',k='The Navy believed',img='ai/18',at='The Navy')],
 [P(B,'ai/19',k='Days later &middot; a Stanford hospital'),N(B,11,'patients &mdash; the same rare infection',img='ai/19',at='eleven'),P(B,'ai/19',pos='25% 60%',k='One of them',t='Edward Nevin',at='One of them'),C(RD,'*He died.*',img='ai/19',at='died',sfx='boom')],
 [N(B,25,'years of silence',suf='+',img='photos/gg3'),C(B,'The Army *admitted it*',k='1977',img='ai/01',at='In 1977'),P(B,'photos/sf',pos='30% 60%',t='Not the only city',fx='fog',at='And San')],
 [N(RD,239,'secret tests',img='ai/18',sfx='hit'),N(B,20,'years',img='ai/18',at='Over twenty'),P(B,'ai/20',k='New York City subway',fx='fog',at='Including'),P(B,'ai/20',pos='75% 40%',t='At rush hour',fx='fog',at='at rush')],
 [P(B,'photos/gavel',k='The Nevin family sued'),C(RD,'*They lost.*',img='photos/gavel',at='They lost',sfx='boom'),C(B,'No one was|held responsible',img='photos/gavel',at='The court')]],
[[P(A,'ai/08',pos='60% 50%',t='A poisoned bottle',fx='open'),P(G,'ai/10',t='A glowing paintbrush',fx='motes',at='A glowing'),P(B,'ai/17',pos='60% 40%',t='A fog that wasn&rsquo;t just fog',fx='fog',at='A fog'),C(RD,'&ldquo;An *acceptable cost*&rdquo;',s='decided by someone in power',img='ai/04',at='someone in power'),P(G,'ai/15',pos='50% 70%',t='Until someone refused|*to stay quiet*',at='And each')],
 [C(A,'These three were *admitted.*',img='ai/01'),C(RD,'Buried *much longer*',k='The next story',img='ai/16',at='The story',sfx='hit'),C(A,'Watch next &#9654;',s='Click the video on screen',img='ai/16',at='Click')]]]
