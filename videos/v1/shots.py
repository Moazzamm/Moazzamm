from lib import *
A,G,B,RD='#e0a030','#6dff8f','#8fc4e8','#d8452e'
t='dark'; H=lambda s:f"<span class=hl>{s}</span>"
def T_(a,*x,**k): return T(t,a,*x,**k)
def P_(a,*x,**k): return P(t,a,*x,**k)
def N_(a,*x,**k): return N(t,a,*x,**k)
F=['Add: METHYL ALCOHOL','Add: KEROSENE','Add: BENZENE','Purpose: make it undrinkable']
LDP=['Lip.','Dip.','Paint.']
SHOTS=[
[[P_(B,'gg',k='San Francisco · 1950'),P_(B,'ship',k='A ship in the fog',dark=.4),N_(B,'800,000','people breathed it in'),T_(B,'Nobody told them.',s='Nobody asked them.')],
 [T_(RD,"That's story three."),P_(A,'whiskey',k='Story one',dark=.7),P_(G,'watch',k='Story two'),T_(RD,'3 true stories',s='your history teacher skipped')]],
[[T_(A,'The Poisoned Bottles',k='Story one'),P_(A,'nyc',t='New York City',k='Christmas Eve · 1926'),P_(A,'hall',k='Bellevue Hospital')],
 [P_(A,'hall',k="He's not alone",pos='30% 50%'),N_(A,'Dozens','dead within days'),T_(A,'Not moonshine.',s='Poison.'),T_(RD,'Put there '+H('on purpose'),s='by their own government')],
 [P_(A,'whiskey',k='Prohibition',dark=.7),P_(A,'jars',k='Stolen industrial alcohol'),D(t,A,'FEDERAL DENATURING ORDER',F),D(t,A,'FEDERAL DENATURING ORDER',F,(0,)),D(t,A,'FEDERAL DENATURING ORDER',F,(0,1)),D(t,A,'FEDERAL DENATURING ORDER',F,(0,1,2)),T_(RD,'They knew people<br>would drink it.',s='That was the point.')],
 [T_(A,'Charles Norris',k='Chief Medical Examiner · New York'),(Q(t,A,'Our national experiment in extermination','Charles Norris'),1.6)],
 [N_(RD,'10,000+','Americans killed (estimated)'),P_(A,'whiskey',k='One supporter shrugged',dark=.75,pos='70% 50%'),Q(t,A,'Deliberate suicide','A supporter of the program')],
 [P_(A,'jars',k='The government poisoned the drinks',pos='60% 40%'),T_(A,'They knew the risk.'),T_(G,'The next victims were told<br>it was '+H('good for them'))]],
[[T_(G,'The Girls Who Glowed',k='Story two'),P_(G,'watch',k='New Jersey · 1917',t='Glow-in-the-dark dials'),T_(G,H('Radium'),k='The secret ingredient')],
 [(P_(G,'watch',k='To keep the brush sharp',pos='40% 60%'),3),Wd(t,G,LDP,1),Wd(t,G,LDP,2),(Wd(t,G,LDP,3),1.3),(N_(G,'100s','of times a day — radium in their mouths'),3.2)],
 [T_(G,'&ldquo;Harmless.&rdquo;',k='Their bosses said'),T_(G,'Nails.<br>Teeth.',s='They painted themselves with it'),P_(G,'nyc',t='Glowing like ghosts',gray=1)],
 [P_(G,'jars',k='Down the hall',pos='40% 50%'),T_(G,'Lead screens.<br>Tongs.',s='Protection — for the scientists only')],
 [T_(RD,'Then the teeth fell out.'),T_(G,'Mollie Maggia',k='1922',s='Dial painter'),P_(G,'hall',k='A sore jaw',gray=1),T_(RD,'The bone came away<br>'+H('in his hand.'))],
 [N_(G,'24','years old'),D(t,G,'CERTIFICATE OF DEATH',['Name: MAGGIA, MOLLIE','Age: 24','Cause: SYPHILIS'],(2,)),T_(RD,'A lie.',s='It protected the company — and destroyed her name')],
 [P_(G,'gavel',t='Five dying women sued',k='1927'),T_(G,'The company stalled.',s='Hoping they would die before the verdict'),N_(G,'1928','They won'),T_(G,'Worker safety laws',s='that protect you today')],
 [N_(G,'1,600','year half-life'),(P_(G,'cemetery',t='Still radioactive',s='Right now.',gray=1),1.4)],
 [T_(G,'A company poisoned<br>its workers.'),T_(B,'What if the target is<br>'+H('an entire city?'))]],
[[T_(B,'The Fog',k='Story three'),P_(B,'gg2',k='September 1950'),P_(B,'ship',k='US Navy · offshore',dark=.4),P_(B,'gg3',k='Into the famous fog')],
 [T_(B,'Billions of bacteria',k='Inside the mist'),P_(B,'sf',t='A germ-attack test'),T_(RD,'So they attacked one.',s='Their own.')],
 [T_(B,'&ldquo;Success&rdquo;',k='The result'),N_(B,'800,000','residents inhaled the bacteria'),T_(B,'&ldquo;Harmless&rdquo;',k='The Navy believed')],
 [P_(B,'hall',k='Stanford hospital · days later',pos='70% 50%'),N_(B,'11','patients · one rare infection'),T_(RD,'Edward Nevin',k='One of them',s='He died.')],
 [N_(B,'25+','years of silence'),T_(B,'The Army admitted it',k='1977'),P_(B,'sf',t='Not the only city',pos='30% 60%')],
 [N_(RD,'239','secret tests'),N_(B,'20','years'),(P_(B,'subway',t='At rush hour',k='New York City subway'),1.5)],
 [P_(B,'gavel',k='The Nevin family sued'),T_(RD,'They lost.'),T_(B,'No one was held responsible')]],
[[P_(A,'whiskey',t='A poisoned bottle',dark=.7),P_(G,'watch',t='A glowing paintbrush'),P_(B,'gg',t='A fog that wasn&rsquo;t just fog'),(T_(RD,'&ldquo;An acceptable cost&rdquo;',s='decided by someone in power'),1.6),(T_(A,'Until someone refused<br>to stay quiet'),1.6)],
 [T_(A,'These three were admitted.'),T_(RD,'Buried '+H('much longer'),k='The next story'),T_(A,'&#9654;',k='Watch next',s='Click the video on screen')]]]
GRAIN=5
