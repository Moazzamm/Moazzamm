import gem,base64,wave,time,json,os
paras=json.load(open("vo/paras.json"))
chunks=[(0,9),(9,16),(16,24),(24,30),(30,36)]
M="gemini-3.1-flash-tts-preview"
for ci,(a,b) in enumerate(chunks):
    path=f"vo/c{ci}.wav"
    if os.path.exists(path): continue
    text="\n\n".join(paras[a:b])
    body={"contents":[{"parts":[{"text":text}]}],
      "generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Gacrux"}}}}}
    for t in range(3):
        try:
            r=gem.call(M,body,retries=1,timeout=600); d=gem.inline_parts(r)[0]; pcm=base64.b64decode(d["data"])
            with wave.open(path,"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            print(ci,"ok",round(len(pcm)/48000,1),"s for",sum(len(p.split()) for p in paras[a:b]),"words",flush=True); break
        except Exception as e:
            print(ci,"retry",str(e)[:80],flush=True); time.sleep(30)
print("DONE")
