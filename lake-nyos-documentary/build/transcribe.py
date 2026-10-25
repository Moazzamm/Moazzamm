import gem,base64,sys,json
data=base64.b64encode(open(sys.argv[1],"rb").read()).decode()
body={"contents":[{"parts":[{"inlineData":{"mimeType":"audio/wav","data":data}},{"text":"Transcribe this audio verbatim. Also report approximately at what second the speech starts and ends, and describe the speaking pace and tone in one line."}]}]}
r=gem.call("gemini-3.5-flash",body)
print(r["candidates"][0]["content"]["parts"][0]["text"])
