# Edit decision list, cut to an 80 BPM track (beat 0.75 s, bar 3.0 s)
BPM = 80.0
BEAT = 60.0 / BPM          # 0.75
BAR = 4 * BEAT             # 3.0
S16 = BEAT / 4             # 0.1875
DUR = 19.6
FPS = 30

# id, out_start, out_end, src_in (s), speed keyframes [(local_u 0..1, speed)], crop focus x (landscape), base zoom (z0,z1), base rot deg (r0,r1), decode fps
SHOTS = [
    dict(id="10760720", t0=0.0,   t1=3.0,   src=0.2,  speed=[(0, 1.5), (0.8, 1.5), (1, 3.0)], fx=0.50, zoom=(1.00, 1.10), rot=(0, 0),   dfps=24),
    dict(id="10760711", t0=3.0,   t1=4.5,   src=0.3,  speed=[(0, 5.0), (0.35, 1.0), (0.7, 1.0), (1, 5.0)], fx=0.42, zoom=(1.06, 1.0), rot=(0, 0), dfps=24),
    dict(id="35890304", t0=4.5,   t1=6.0,   src=2.0,  speed=[(0, 9.0), (0.4, 2.5), (0.7, 2.5), (1, 9.0)], fx=0.5,  zoom=(1.25, 1.12), rot=(-14, 10), dfps=30),
    dict(id="30172966", t0=6.0,   t1=7.5,   src=0.2,  speed=[(0, 4.5), (0.4, 1.0), (0.72, 1.0), (1, 4.5)], fx=0.5,  zoom=(1.0, 1.06), rot=(0, 0),  dfps=30),
    dict(id="35556857", t0=7.5,   t1=9.0,   src=0.3,  speed=[(0, 6.0), (0.45, 2.0), (0.7, 2.0), (1, 7.0)], fx=0.5,  zoom=(1.04, 1.12), rot=(0, 0), dfps=30),
    dict(id="30949117", t0=9.0,   t1=10.5,  src=2.0,  speed=[(0, 2.5), (0.14, 0.5), (1, 0.5)], fx=0.5,  zoom=(1.10, 1.02), rot=(0, 0),  dfps=59),
    dict(id="30159129", t0=10.5,  t1=11.25, src=3.2,  speed=[(0, 0.5), (1, 0.5)], fx=0.5,  zoom=(1.05, 1.10), rot=(0, 0),  dfps=60),
    dict(id="36855438", t0=11.25, t1=12.0,  src=1.0,  speed=[(0, 1.5), (1, 1.5)], fx=0.5,  zoom=(1.04, 1.14), rot=(0, 0),  dfps=30),
    dict(id="37975936", t0=12.0,  t1=13.5,  src=9.0,  speed=[(0, 9.0), (0.4, 1.0), (0.72, 1.0), (1, 8.0)], fx=0.5,  zoom=(1.0, 1.06), rot=(0, 0),  dfps=30),
    dict(id="37219534", t0=13.5,  t1=15.0,  src=20.0, speed=[(0, 9.0), (0.45, 3.0), (0.7, 3.0), (1, 10.0)], fx=0.52, zoom=(1.0, 1.08), rot=(0, 0), dfps=30),
    dict(id="14461063", t0=15.0,  t1=17.25, src=1.0,  speed=[(0, 3.0), (0.2, 1.2), (1, 1.0)], fx=0.40, zoom=(1.08, 1.0), rot=(0, 0),  dfps=30),
    dict(id="37973016", t0=17.25, t1=19.6,  src=0.5,  speed=[(0, 1.0), (1, 0.5)], fx=0.5,  zoom=(1.0, 1.07), rot=(0, 0),  dfps=60),
]

# transition INTO shot i (at SHOTS[i].t0): kind, half-duration seconds
TRANS = {
    1: ("zoom", 0.20),        # the drop
    2: ("whip_down", 0.17),
    3: ("spin", 0.20),
    4: ("whip_left", 0.17),
    5: ("zoom", 0.18),
    6: ("cut", 0.0),
    7: ("cut", 0.0),
    8: ("whip_right", 0.15),
    9: ("spin", 0.18),
    10: ("zoom_out", 0.22),
    11: ("dissolve", 0.45),
}
FLASH = {3.0: 1.0, 9.0: 0.6, 10.5: 0.25, 11.25: 0.25, 15.0: 0.8}   # exposure flashes on hits

# tiny location tags (start, end, text)
TAGS = [(6.25, 7.3, "GULMARG"), (7.75, 8.8, "SONAMARG"), (12.3, 13.3, "SRINAGAR")]
