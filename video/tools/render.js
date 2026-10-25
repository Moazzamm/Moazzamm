// Render frames [from,to) of comp/index.html to an H.264 segment via Chromium screenshots piped into ffmpeg.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const [from, to, out, mode] = [+process.argv[2], +process.argv[3], process.argv[4], process.argv[5] || 'video'];
  const b = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto('file://' + path.resolve(__dirname, '../comp/index.html'));
  await p.evaluate(() => window.READY);
  const cdp = await p.context().newCDPSession(p);
  const fps = 24;
  if (mode === 'stills') {
    for (const t of process.argv.slice(6).map(Number)) {
      await p.evaluate(t => renderAt(t), t);
      await p.screenshot({ path: `${out}_${t}.jpg`, type: 'jpeg', quality: 85 });
    }
    await b.close(); return;
  }
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = from; f < to; f++) {
    await p.evaluate(t => renderAt(t), f / fps);
    const { data } = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 93, optimizeForSpeed: true });
    if (!ff.stdin.write(Buffer.from(data, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - from) % 240 === 0) console.log(out, f, ((f - from + 1) / ((Date.now() - t0) / 1000)).toFixed(1), 'fps');
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
