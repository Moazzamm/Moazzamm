const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const dir=process.argv[2];const files=fs.readdirSync(dir).filter(f=>f.endsWith('.html')).sort();
const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:2});
let i=0;async function w(){const p=await ctx.newPage();while(i<files.length){const f=files[i++];await p.goto('file://'+path.join(dir,f));await p.waitForLoadState('load');await p.screenshot({path:path.join(dir,f.replace('.html','.png'))});}await p.close();}
await Promise.all([w(),w(),w(),w()]);await b.close();console.log('shot',files.length);})();
