const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path');
const b64=f=>fs.readFileSync(path.join(__dirname,'node_modules/@fontsource',f)).toString('base64');
const css=`
@font-face{font-family:CG;font-weight:500;src:url(data:font/woff2;base64,${b64('cormorant-garamond/files/cormorant-garamond-latin-500-normal.woff2')})}
@font-face{font-family:CG;font-weight:600;src:url(data:font/woff2;base64,${b64('cormorant-garamond/files/cormorant-garamond-latin-600-normal.woff2')})}
@font-face{font-family:CG;font-weight:500;font-style:italic;src:url(data:font/woff2;base64,${b64('cormorant-garamond/files/cormorant-garamond-latin-500-italic.woff2')})}
@font-face{font-family:IN;font-weight:600;src:url(data:font/woff2;base64,${b64('inter/files/inter-latin-600-normal.woff2')})}
html,body{margin:0;width:1080px;height:1920px;background:transparent}
.wrap{position:absolute;left:0;right:0;top:1010px;height:460px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
 background:radial-gradient(ellipse 62% 50% at 50% 50%,rgba(0,0,0,.42),rgba(0,0,0,0) 72%)}
.k{font:600 28px IN;letter-spacing:.42em;color:#F5C84B;text-transform:uppercase;margin-right:-.42em;text-shadow:0 2px 14px rgba(0,0,0,.6)}
.r{width:64px;height:3px;background:#F5C84B;margin:22px 0 20px}
.t{font:500 94px/1.06 CG;color:#fff;text-shadow:0 3px 26px rgba(0,0,0,.65),0 1px 3px rgba(0,0,0,.5);padding:0 90px 0 70px}
.t i{font-style:italic}
.big{font:600 120px/1.0 CG;letter-spacing:.06em}
.wrap.title{top:900px;height:560px}
`;
const cards={
 t01:`<div class="wrap title"><div class="k">India · Bay of Bengal</div><div class="r"></div><div class="t big">ANDAMAN<br>&amp; NICOBAR</div></div>`,
 t02:`<div class="wrap"><div class="k">The Archipelago</div><div class="r"></div><div class="t">836 islands.<br><i>Only 31 inhabited.</i></div></div>`,
 t03:`<div class="wrap"><div class="k">The Rainforest</div><div class="r"></div><div class="t">86% still<br><i>wrapped in forest.</i></div></div>`,
 t06:`<div class="wrap"><div class="k">The Reef</div><div class="r"></div><div class="t">And beneath<br><i>the surface…</i></div></div>`,
 t09:`<div class="wrap"><div class="k">The Nesting Grounds</div><div class="r"></div><div class="t">Four species of<br>sea turtle <i>nest here.</i></div></div>`,
 t11:`<div class="wrap"><div class="k">Barren Island</div><div class="r"></div><div class="t">Home to South Asia’s<br><i>only active volcano.</i></div></div>`,
 t13:`<div class="wrap title"><div class="t big">ANDAMAN<br>&amp; NICOBAR</div><div class="r"></div><div class="t" style="font-size:80px"><i>Still wild.</i></div></div>`};
(async()=>{const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1920}});
for(const [k,h] of Object.entries(cards)){await p.setContent(`<style>${css}</style>${h}`);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(150);
 await p.screenshot({path:path.join(__dirname,'../ov',k+'.png'),omitBackground:true});}
await br.close();})();
