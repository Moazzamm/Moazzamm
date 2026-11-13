BPM = 60.0
BEAT = 1.0
DUR = 15.5
FPS = 30
HIT = 12.0
def S(id, t0, t1, src, sp=1.0, fx=0.5, zoom=(1.0, 1.06), dfps=30):
    return dict(id=id, t0=t0, t1=t1, src=src, speed=[(0, sp), (1, sp)], fx=fx, zoom=zoom, rot=(0, 0), dfps=dfps)
SHOTS = [
    S("18765949", 0.0,  2.0,  5.0,  0.6, fx=0.60, zoom=(1.0, 1.05), dfps=60),     # Indus-Zanskar confluence
    S("38246027", 2.0,  4.0,  6.0,  1.5, zoom=(1.04, 1.0)),                       # clouds over Himalayan peaks
    S("11710132", 4.0,  6.0,  1.8,  1.0, fx=0.85, zoom=(1.0, 1.05), dfps=25),     # Diskit Maitreya Buddha
    S("17982149", 6.0,  8.0,  2.6,  1.0, fx=0.50, zoom=(1.0, 1.05)),              # Pangong Tso
    S("27975367", 8.0,  9.0,  9.5,  1.0, zoom=(1.0, 1.04), dfps=60),              # rock-pillar road
    S("18227144", 9.0,  10.0, 1.0,  0.6, zoom=(1.0, 1.04), dfps=60),              # prayer flags
    S("18766038", 10.0, 10.5, 8.0,  1.0, fx=0.65, zoom=(1.0, 1.03), dfps=60),     # Zangla
    S("17912055", 10.5, 11.0, 10.0, 1.0, fx=0.45, zoom=(1.0, 1.03), dfps=60),     # Lamayuru
    S("19024880", 11.0, 11.5, 6.0,  1.0, fx=0.50, zoom=(1.0, 1.03), dfps=60),     # over Pangong
    S("27975373", 11.5, 12.0, 6.0,  1.0, zoom=(1.0, 1.03), dfps=60),              # river valley
    S("39410696", 12.0, DUR,  0.4,  0.6, fx=0.47, zoom=(1.0, 1.12), dfps=60),     # monastery on golden ridge
]
TRANS = {}
TAGS = []
PETRA_TAG = (100.0, 101.0, "x", "x")
TITLE_T = (100.0, 101.0)
END_T = (100.0, 101.0)
