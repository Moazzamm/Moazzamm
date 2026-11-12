const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{let [dir,out,sel]=process.argv.slice(2);dir=path.resolve(dir);out=path.resolve(out);const man=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json')));fs.mkdirSync(out,{recursive:true});
const only=sel?sel.split(',').map(Number):null;const q=man.map((m,i)=>({...m,i})).filter(m=>!only||only.includes(m.i));let qi=0,done=0;
const b=await chromium.launch({args:['--font-render-hinting=none','--disable-lcd-text']});
async function worker(){const ctx=await b.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});const p=await ctx.newPage();const cdp=await ctx.newCDPSession(p);
 while(qi<q.length){const m=q[qi++];if(!only&&fs.existsSync(path.join(out,String(m.start+m.frames-1).padStart(6,'0')+'.jpg'))){done++;continue;}await p.goto('file://'+path.join(dir,m.file));
  await p.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.querySelectorAll('.bg')].map(e=>{const u=getComputedStyle(e).backgroundImage.slice(5,-2);return new Promise(r=>{const im=new Image();im.onload=im.onerror=r;im.src=u;});}));window.__init();});
  const fr=only&&process.argv[5]?process.argv[5].split(',').map(Number):[...Array(m.frames).keys()];
  for(const f of fr){await p.evaluate(t=>window.__seek(t),f*1000/30);const r=await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:92,optimizeForSpeed:true});fs.writeFileSync(path.join(out,String(m.start+f).padStart(6,'0')+'.jpg'),Buffer.from(r.data,'base64'));}
  done++;if(done%10==0)console.log('shots',done,'/',q.length);}
 await ctx.close();}
await Promise.all([worker(),worker(),worker(),worker()]);await b.close();console.log('rendered',q.length);})();
