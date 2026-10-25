import gem,base64,wave,time,json,os,sys,urllib.error
paras=[p.strip().replace("\n"," ") for p in open("../script.txt").read().split("\n\n") if p.strip()]
json.dump(paras,open("vo/paras.json","w"),indent=1)
def one(i,t):
    path=f"vo/p{i:02d}.wav"
    if os.path.exists(path): return
    body={"contents":[{"parts":[{"text":t}]}],
      "generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Gacrux"}}}}}
    for a in range(8):
        try:
            r=gem.call("gemini-3.8-flash-tts",body,retries=1)
            d=gem.inline_parts(r)[0]; pcm=base64.b64decode(d["data"])
            with wave.open(path,"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            print(i,"ok",round(len(pcm)/48000,2),flush=True); return
        except Exception as e:
            print(i,"retry",a,str(e)[:80],flush=True); time.sleep(15+10*a)
    print(i,"FAILED",flush=True)
for i,t in enumerate(paras): one(i,t)
print("DONE")
