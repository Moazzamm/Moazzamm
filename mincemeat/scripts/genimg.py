import json,base64,sys,urllib.request,time
model=sys.argv[1]; out=sys.argv[2]; prompt=sys.argv[3]
body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"16:9"}}}
for a in range(3):
  try:
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":"d"})
    r=json.load(urllib.request.urlopen(req,timeout=300))
    for p in r["candidates"][0]["content"]["parts"]:
      if "inlineData" in p: open(out,"wb").write(base64.b64decode(p["inlineData"]["data"])); print("ok",out); sys.exit(0)
    print("noimg", str(r)[:300])
  except urllib.error.HTTPError as e: print(out, e.code, e.read().decode()[:200]); time.sleep(10)
  except Exception as e: print(out,"err",e); time.sleep(5)
