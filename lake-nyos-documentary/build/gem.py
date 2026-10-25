import json, base64, sys, time, urllib.request, os, wave
API="https://generativelanguage.googleapis.com/v1beta/models/"
def call(model, body, timeout=300, retries=3):
    req=json.dumps(body).encode()
    for i in range(retries):
        try:
            r=urllib.request.Request(API+model+":generateContent", data=req, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(r, timeout=timeout) as f:
                return json.load(f)
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:500]; print("HTTP",e.code,msg,file=sys.stderr)
            if e.code in (400,403,404,429): raise
        except Exception as e:
            print("ERR",e,file=sys.stderr)
        time.sleep(4*(i+1))
    raise RuntimeError("failed")
def inline_parts(resp):
    out=[]
    for c in resp.get("candidates",[]):
        for p in c.get("content",{}).get("parts",[]):
            if "inlineData" in p: out.append(p["inlineData"])
    return out
def tts(text, path, voice="Charon", model="gemini-2.5-pro-preview-tts", style=""):
    body={"contents":[{"parts":[{"text": style+text}]}],
          "generationConfig":{"responseModalities":["AUDIO"],
            "speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":voice}}}}}
    resp=call(model, body)
    d=inline_parts(resp)[0]
    pcm=base64.b64decode(d["data"])
    rate=24000
    mt=d.get("mimeType","")
    if "rate=" in mt: rate=int(mt.split("rate=")[1].split(";")[0])
    with wave.open(path,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
    return path
def image(prompt, path, model="gemini-3-pro-image", aspect="16:9", size="2K"):
    body={"contents":[{"parts":[{"text":prompt}]}],
          "generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":aspect,"imageSize":size}}}
    resp=call(model, body, timeout=400)
    parts=inline_parts(resp)
    if not parts: raise RuntimeError("no image: "+json.dumps(resp)[:400])
    open(path,"wb").write(base64.b64decode(parts[-1]["data"]))
    return path, parts[-1].get("mimeType")
