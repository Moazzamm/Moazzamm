import gem,base64,wave,time,json,os
paras=json.load(open("vo/paras.json"))
chunks=[];cur=[];n=0
for i in range(5,len(paras)):
    w=len(paras[i].split())
    if cur and n+w>115: chunks.append(cur);cur=[];n=0
    cur.append(i);n+=w
chunks.append(cur)
json.dump(chunks,open("vo/chunks.json","w"))
print(len(chunks),"chunks",chunks,flush=True)
models=["gemini-3.1-flash-tts-preview","gemini-3.8-flash-lite-tts","gemini-2.5-flash-preview-tts"]
mi=0
for ci,idx in enumerate(chunks):
    path=f"vo/k{ci:02d}.wav"
    if os.path.exists(path): continue
    text="\n\n".join(paras[i] for i in idx); words=len(text.split())
    body={"contents":[{"parts":[{"text":text}]}],
      "generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Gacrux"}}}}}
    done=False
    for t in range(6):
        try:
            r=gem.call(models[mi],body,retries=1,timeout=300); d=gem.inline_parts(r)[0]; pcm=base64.b64decode(d["data"])
            dur=len(pcm)/48000
            with wave.open(path,"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            print(ci,"ok",models[mi],round(dur,1),"s",words,"w",round(words/dur*60),"wpm",flush=True); done=True; break
        except Exception as e:
            s=str(e); print(ci,"err",models[mi],s[:60],flush=True)
            if "429" in s or "Too Many" in s:
                mi=min(mi+1,len(models)-1)
            time.sleep(8)
    if not done: print(ci,"FAILED",flush=True)
print("DONE",flush=True)
