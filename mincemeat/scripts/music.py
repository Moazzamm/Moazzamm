import json,base64,sys,urllib.request
model, prompt, out = sys.argv[1], sys.argv[2], sys.argv[3]
body={"contents":[{"parts":[{"text":prompt}]}]}
req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":"dummy"})
try:
    r=json.load(urllib.request.urlopen(req,timeout=600))
except urllib.error.HTTPError as e:
    print(e.read().decode()[:800]); sys.exit(1)
for p in r["candidates"][0]["content"]["parts"]:
    if "inlineData" in p:
        print(p["inlineData"]["mimeType"]); open(out,"wb").write(base64.b64decode(p["inlineData"]["data"]))
    elif "text" in p: print("TEXT:",p["text"][:300])
