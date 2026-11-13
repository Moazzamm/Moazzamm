BPM = 90.0
BEAT = 60.0 / BPM            # 0.6667
BAR = 4 * BEAT               # 2.6667
GROOVE = 2 * BAR             # 5.333  darbuka groove starts
OUTRO = 8 * BAR              # 21.333 groove ends
DUR = 26.0
FPS = 30
B = BEAT
def S(id, t0, t1, src, sp=1.0, fx=0.5, zoom=(1.0, 1.06), dfps=30):
    return dict(id=id, t0=round(t0, 4), t1=round(t1, 4), src=src, speed=[(0, sp), (1, sp)], fx=fx, zoom=zoom, rot=(0, 0), dfps=dfps)
SHOTS = [
    S("4361415",  0,       4 * B,  0.5,  1.0, fx=0.60, zoom=(1.0, 1.06), dfps=25),   # sunrise, Wadi Rum
    S("26390583", 4 * B,   8 * B,  2.0,  1.0, zoom=(1.0, 1.04)),                     # Siq walk -> Treasury reveal
    S("35225085", 8 * B,   11 * B, 5.0,  1.2, zoom=(1.0, 1.05)),                     # out of the Siq
    S("38261225", 11 * B,  13 * B, 11.0, 0.6, zoom=(1.04, 1.0), dfps=60),            # Treasury, slow motion
    S("39728346", 13 * B,  16 * B, 0.5,  1.0, zoom=(1.0, 1.05)),                     # tomb road, Petra
    S("10981165", 16 * B,  18 * B, 0.3,  1.0, fx=0.40, zoom=(1.0, 1.04)),            # dune walker
    S("12511425", 18 * B,  20 * B, 3.5,  1.0, fx=0.45, zoom=(1.03, 1.0)),            # camels
    S("14918987", 20 * B,  22 * B, 3.3,  1.0, fx=0.55, zoom=(1.0, 1.04)),            # Bedouin + pickup
    S("4361421",  22 * B,  24 * B, 2.0,  1.0, fx=0.55, zoom=(1.0, 1.05), dfps=25),   # rock arch
    S("33919870", 24 * B,  26 * B, 1.0,  1.0, zoom=(1.0, 1.04)),                     # jeep in dust
    S("14874855", 26 * B,  28 * B, 20.0, 1.5, fx=0.5, zoom=(1.0, 1.05)),             # aerial canyon
    S("37251244", 28 * B,  30 * B, 5.0,  1.0, fx=0.50, zoom=(1.0, 1.04), dfps=60),   # Amman, Jordan Gate towers
    S("37251466", 30 * B,  32 * B, 8.0,  1.0, fx=0.47, zoom=(1.04, 1.0), dfps=60),   # Amman skyline
    S("19767276", 32 * B,  DUR,    0.15, 1.0, fx=0.30, zoom=(1.0, 1.06)),            # desert sunset
]
TRANS = {1: ("dissolve", 0.22), 13: ("dissolve", 0.3)}
# location tags: (start, end, arabic, english)
TAGS = [(8 * B + 0.25, 11 * B - 0.15, "البتراء", "PETRA"),
        (16 * B + 0.25, 19 * B - 0.15, "وادي رم", "WADI RUM"),
        (28 * B + 0.25, 31 * B - 0.15, "عمّان", "AMMAN")]
TITLE_T = (0.55, 4 * B - 0.25)
END_T = (32 * B + 0.6, DUR - 0.35)
