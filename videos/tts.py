import json,base64,subprocess,sys,time,os
d=sys.argv[1]; spec=json.load(open(f'{d}/text.json'))
for i,sec in enumerate(spec['sections']):
    out=f'{d}/sec_{i}.wav'
    if os.path.exists(out): continue
    body={"contents":[{"parts":[{"text":spec['style']+"\n\n"+"\n\n".join(sec)}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":spec['voice']}}}}}
    open(f'{d}/req.json','w').write(json.dumps(body))
    for attempt in range(8):
        r=subprocess.run(["curl","-sS","-m","300","-H","x-goog-api-key: dummy","-H","Content-Type: application/json","https://generativelanguage.googleapis.com/v1beta/models/"+spec.get("model","gemini-3.8-flash-tts")+":generateContent","-d",f"@{d}/req.json"],capture_output=True,text=True).stdout
        try:
            p=json.loads(r)['candidates'][0]['content']['parts'][0]['inlineData']
            raw=base64.b64decode(p['data'])
            open(f'{d}/sec_{i}.raw','wb').write(raw)
            src=["-i",f'{d}/sec_{i}.raw'] if raw[:4]==b'RIFF' else ["-f","s16le","-ar","24000","-ac","1","-i",f'{d}/sec_{i}.raw']
            subprocess.run(["ffmpeg","-v","error","-y",*src,out],check=True); print('ok',i,flush=True); break
        except Exception as e:
            print('retry',i,attempt,r[:200],flush=True); time.sleep(20)
