import os
MODEL=os.environ.get("M","gemini-3.5-flash")
import gem, base64, json, sys, subprocess, difflib, re
paras=json.load(open("vo/paras.json")); chunks=[[0,1,2,3,4]]+json.load(open("vo/chunks.json"))
files=["vo/c0.wav"]+[f"vo/k{i:02d}.wav" for i in range(10)]
def norm(s): return re.sub(r"[^a-z0-9 ]"," ",s.lower()).split()
out=[]
for ci in map(int,sys.argv[1:]):
    f=files[ci]; mp3=f"/tmp/claude-0/qc{ci}.mp3"
    args=["ffmpeg","-loglevel","error","-y","-i",f]+(["-t","53.1"] if ci==0 else [])+["-b:a","48k",mp3]
    subprocess.run(args,check=True)
    data=base64.b64encode(open(mp3,"rb").read()).decode()
    body={"contents":[{"parts":[{"inlineData":{"mimeType":"audio/mp3","data":data}},{"text":"Transcribe this narration verbatim, words only, no timestamps or commentary."}]}]}
    try:
        r=gem.call(MODEL,body,retries=2,timeout=180); txt=r["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(ci,"transcribe failed",str(e)[:80]); continue
    ref=norm(" ".join(paras[i] for i in chunks[ci])); hyp=norm(txt)
    sm=difflib.SequenceMatcher(a=ref,b=hyp)
    diffs=[(op," ".join(ref[a1:a2])," ".join(hyp[b1:b2])) for op,a1,a2,b1,b2 in sm.get_opcodes() if op!="equal"]
    print(ci,"ratio %.3f"%sm.ratio(),diffs[:12],flush=True)
