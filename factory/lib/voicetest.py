import sys, json, base64, concurrent.futures as cf
sys.path.insert(0, "lib"); import gem
D = "assets/test/"
line = "In 1901, sponge divers pulled a lump of corroded bronze from a shipwreck. It sat in a museum drawer for decades. Then an X-ray revealed what was inside. And it was two thousand years ahead of its time."
style = "Read this as a top YouTube documentary narrator: deep, warm, confident and intrigued. Keep a brisk, engaging pace with crisp diction. Short pauses only at full stops. Build tension toward the last sentence"
voices = ["Charon", "Algenib", "Orus", "Fenrir", "Iapetus"]
with cf.ThreadPoolExecutor(5) as ex:
    list(ex.map(lambda v: gem.tts(line, D+f"f_{v}.wav", voice=v, style=style), voices))
words = len(line.split())
parts = []
for v in voices:
    d = gem.wav_dur(D+f"f_{v}.wav"); print(v, f"{d:.1f}s", f"{words/d*60:.0f} wpm")
    parts.append({"text": f"Clip {v}:"}); parts.append({"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(open(D+f"f_{v}.wav","rb").read()).decode()}})
parts.append({"text": "You are a YouTube audio director. Rank these 5 narration clips for a premium 'amazing facts' documentary channel. Judge naturalness, absence of robotic artifacts, gravitas, energy and how hooked a viewer would feel. Reply as compact JSON: {ranking:[names], notes:{name:'<=12 words'}}"})
r = gem._post(f"{gem.BASE}/models/gemini-flash-latest:generateContent", {"contents":[{"parts":parts}], "generationConfig":{"responseMimeType":"application/json"}})
print("".join(p.get("text","") for p in gem._parts(r)))
