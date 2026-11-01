import json, base64, sys, subprocess, urllib.request, os, time
MODELS = (sys.argv[1] if len(sys.argv)>1 else "gemini-2.5-pro-preview-tts").split(",")
VOICE = sys.argv[2] if len(sys.argv)>2 else "Charon"
only = sys.argv[3:] 
d = json.load(open("scripts/narration.json"))
style = ""
for key, text in d:
    if only and key not in only: continue
    out = f"audio/{key}.wav"
    if os.path.exists(out) and not only: continue
    body = {"contents":[{"parts":[{"text": style + text}]}],
            "generationConfig":{"responseModalities":["AUDIO"],
              "speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":VOICE}}}}}
    for attempt in range(12):
        MODEL = MODELS[min(attempt // 3, len(MODELS) - 1)]
        try:
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                data=json.dumps(body).encode(), headers={"Content-Type":"application/json","x-goog-api-key":"dummy"})
            r = json.load(urllib.request.urlopen(req, timeout=300))
            b = base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            open(f"audio/{key}.pcm","wb").write(b)
            subprocess.run(["ffmpeg","-y","-loglevel","error","-f","s16le","-ar","24000","-ac","1","-i",f"audio/{key}.pcm",out],check=True)
            os.remove(f"audio/{key}.pcm")
            print(key, MODEL, len(b)/48000, "s", flush=True); break
        except Exception as e:
            print(key, "err", e, flush=True); time.sleep(15)
