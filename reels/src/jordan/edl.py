BPM = 90.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
GROOVE = 2 * BAR
OUTRO = 8 * BAR
DUR = 26.0
FPS = 30
B = BEAT
def S(id, t0, t1, src, sp=1.0, fx=0.5, zoom=(1.0, 1.06), dfps=30):
    return dict(id=id, t0=round(t0, 4), t1=round(t1, 4), src=src, speed=[(0, sp), (1, sp)], fx=fx, zoom=zoom, rot=(0, 0), dfps=dfps)
SHOTS = [
    # HOOK: moving through the Siq, the Treasury opens up at the end of the shot
    S("26390583", 0,       4 * B,  1.55, 1.0, zoom=(1.0, 1.05)),
    # TITLE: Treasury in slow motion
    S("38261225", 4 * B,   8 * B,  10.0, 0.55, zoom=(1.0, 1.06), dfps=60),
    # DROP: scale change, vast Wadi Rum
    S("14874855", 8 * B,   10 * B, 20.0, 1.6, fx=0.5, zoom=(1.0, 1.05)),
    S("10981165", 10 * B,  11 * B, 0.3,  1.0, fx=0.40, zoom=(1.0, 1.03)),
    S("12511425", 11 * B,  12 * B, 3.5,  1.0, fx=0.45, zoom=(1.03, 1.0)),
    S("14918987", 12 * B,  14 * B, 0.6,  1.0, fx=1.0,  zoom=(1.0, 1.04)),    # Bedouin
    S("4361421",  14 * B,  16 * B, 2.0,  1.0, fx=0.55, zoom=(1.0, 1.06), dfps=25),
    S("10981174", 16 * B,  17 * B, 0.2,  1.0, fx=0.59, zoom=(1.0, 1.03)),
    S("33919870", 17 * B,  19 * B, 1.0,  1.0, zoom=(1.0, 1.05)),
    S("4361617",  19 * B,  20 * B, 3.0,  1.0, fx=0.5,  zoom=(1.04, 1.0), dfps=25),
    # CITY
    S("37251244", 20 * B,  22 * B, 5.0,  1.0, fx=0.50, zoom=(1.0, 1.05), dfps=60),
    S("37251466", 22 * B,  24 * B, 8.0,  1.0, fx=0.47, zoom=(1.05, 1.0), dfps=60),
    # BUILD: one-beat recap
    S("35225085", 24 * B,  25 * B, 6.0,  1.2, zoom=(1.0, 1.04)),
    S("12511425", 25 * B,  26 * B, 20.5, 1.0, fx=0.55, zoom=(1.0, 1.03)),
    S("32201660", 26 * B,  27 * B, 1.0,  1.0, zoom=(1.0, 1.04)),
    S("39728346", 27 * B,  28 * B, 1.5,  1.0, zoom=(1.0, 1.04)),
    S("12511425", 28 * B,  29 * B, 12.0, 1.0, fx=0.5, zoom=(1.0, 1.03)),
    S("10981165", 29 * B,  30 * B, 6.0,  1.0, fx=0.5, zoom=(1.0, 1.03)),
    S("4361415",  30 * B,  32 * B, 3.0,  1.0, fx=0.60, zoom=(1.0, 1.05), dfps=25),
    # OUTRO: hold on the sunset
    S("19767276", 32 * B,  DUR,    0.15, 1.0, fx=0.30, zoom=(1.0, 1.06)),
]
TRANS = {19: ("dissolve", 0.3)}
TAGS = [(4 * B + 0.0, 0, "", ""),] and []
TAGS = [(8 * B + 0.2, 11 * B - 0.1, "وادي رم", "WADI RUM"),
        (20 * B + 0.2, 23 * B - 0.1, "عمّان", "AMMAN")]
PETRA_TAG = (0.35, 4 * B - 0.15, "البتراء", "PETRA")
TITLE_T = (4 * B + 0.15, 8 * B - 0.2)
END_T = (32 * B + 0.6, DUR - 0.35)
