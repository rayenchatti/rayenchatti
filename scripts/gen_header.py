"""Generates assets/header.svg: a real 3D `</>` symbol rotating over a hologram pad,
next to an extruded 3D name. All 3D is computed here and baked into SMIL keyframes.

Run: python scripts/gen_header.py
"""
import math
import random
from pathlib import Path

W, H = 1200, 420
HORIZON = 330
random.seed(3)

# ---------- 3D helpers ----------
def rot(p, a, b):
    x, y, z = p
    x1 = x * math.cos(a) + z * math.sin(a)
    z1 = -x * math.sin(a) + z * math.cos(a)
    y1 = y * math.cos(b) - z1 * math.sin(b)
    z2 = y * math.sin(b) + z1 * math.cos(b)
    return x1, y1, z2


def proj(p, cx, cy, f=700):
    x, y, z = p
    s = f / (f + z)
    return cx + x * s, cy + y * s


def path(pts):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


# ---------- the </> glyph, extruded ----------
S = 1.45
GLYPHS = [
    [(40, -42), (0, 0), (40, 42), (54, 30), (24, 0), (54, -30)],      # <
    [(64, 46), (78, 46), (100, -46), (86, -46)],                        # /
    [(120, -42), (160, 0), (120, 42), (106, 30), (136, 0), (106, -30)],  # >
]
DEPTH = 16
GX, GY = 300, 195
FRAMES = 60
DUR = 8

front_frames = [[] for _ in GLYPHS]
back_frames = [[] for _ in GLYPHS]
side_frames = [[[] for _ in g] for g in GLYPHS]
for k in range(FRAMES + 1):
    t = k / FRAMES
    a = math.radians(38) * math.sin(2 * math.pi * t)
    b = math.radians(14) * math.cos(2 * math.pi * t)
    for gi, g in enumerate(GLYPHS):
        f3 = [((x - 80) * S, y * S, -DEPTH) for x, y in g]
        b3 = [((x - 80) * S, y * S, DEPTH) for x, y in g]
        f2 = [proj(rot(p, a, b), GX, GY) for p in f3]
        b2 = [proj(rot(p, a, b), GX, GY) for p in b3]
        front_frames[gi].append(path(f2))
        back_frames[gi].append(path(b2))
        n = len(g)
        for e in range(n):
            quad = [f2[e], f2[(e + 1) % n], b2[(e + 1) % n], b2[e]]
            side_frames[gi][e].append(path(quad))


def animated_path(frames, cls):
    return (f'<path class="{cls}" d="{frames[0]}"><animate attributeName="d" dur="{DUR}s" '
            f'repeatCount="indefinite" values="{";".join(frames)}"/></path>')


glyph_svg = []
for gi in range(len(GLYPHS)):
    glyph_svg.append(animated_path(back_frames[gi], "back"))
for gi in range(len(GLYPHS)):
    for e in range(len(GLYPHS[gi])):
        glyph_svg.append(animated_path(side_frames[gi][e], "side"))
for gi in range(len(GLYPHS)):
    glyph_svg.append(animated_path(front_frames[gi], "front"))

# ---------- perspective grid floor ----------
VPX = 600
grid = []
for i in range(-14, 15):
    x_bottom = VPX + i * 95
    grid.append(f'<line x1="{VPX + i * 8}" y1="{HORIZON}" x2="{x_bottom}" y2="{H}" class="gl"/>')
# horizontal lines scrolling toward the viewer
N_H, STEPS = 7, 24
for j in range(N_H):
    ys = []
    for s in range(STEPS + 1):
        z = 1 - ((j + s / STEPS) / N_H)  # 1 far -> 0 near
        z = max(z, 0.0001)
        ys.append(f"{HORIZON + (H - HORIZON) * (0.06 / (z + 0.06) - 0.06 / 1.06) / (1 - 0.06 / 1.06):.1f}")
    grid.append(f'<line x1="0" x2="{W}" y1="{ys[0]}" y2="{ys[0]}" class="gl">'
                f'<animate attributeName="y1" values="{";".join(ys)}" dur="3s" repeatCount="indefinite"/>'
                f'<animate attributeName="y2" values="{";".join(ys)}" dur="3s" repeatCount="indefinite"/></line>')

# ---------- stars ----------
stars = "".join(
    f'<circle cx="{random.uniform(10, W-10):.0f}" cy="{random.uniform(10, HORIZON-20):.0f}" r="{random.choice([.6, .9, 1.2])}" '
    f'class="star" style="animation-delay:{random.uniform(0, 5):.1f}s;animation-duration:{random.uniform(2.5, 6):.1f}s"/>'
    for _ in range(60)
)

# ---------- 3D extruded name ----------
LAYERS = 12
NSTEPS = 24
name_layers = []
for i in range(LAYERS, 0, -1):
    vals = []
    for s in range(NSTEPS + 1):
        ang = math.radians(45 + 28 * math.sin(2 * math.pi * s / NSTEPS))
        vals.append(f"{i * 0.9 * math.cos(ang):.2f} {i * 0.9 * math.sin(ang):.2f}")
    shade = 30 + int(60 * (1 - i / LAYERS))
    color = f"rgb({shade // 2 + 10},{shade // 2 + 30},{shade + 50})"
    name_layers.append(
        f'<g fill="{color}"><use href="#name"/><animateTransform attributeName="transform" type="translate" '
        f'values="{";".join(vals)}" dur="7s" repeatCount="indefinite"/></g>'
    )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Rayen Chatti, Software Engineering student">
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#060b16"/>
      <stop offset="0.75" stop-color="#0d1830"/>
      <stop offset="1" stop-color="#1d2f52"/>
    </linearGradient>
    <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1d2f52"/>
      <stop offset="1" stop-color="#060b16"/>
    </linearGradient>
    <linearGradient id="neon" gradientUnits="userSpaceOnUse" x1="560" y1="0" x2="1160" y2="0" spreadMethod="reflect">
      <stop offset="0" stop-color="#6F8BB8"/>
      <stop offset="0.5" stop-color="#6F8BB8"/>
      <stop offset="1" stop-color="#B9C7DD"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0 0;600 0;0 0" dur="8s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="face" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#D4FF3A"/>
      <stop offset="1" stop-color="#9fc21f"/>
    </linearGradient>
    <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#6F8BB8" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#6F8BB8" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="padlime" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#D4FF3A" stop-opacity="0.6"/><stop offset="1" stop-color="#D4FF3A" stop-opacity="0"/></radialGradient>
    <radialGradient id="pad" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#6F8BB8" stop-opacity="0.7"/>
      <stop offset="1" stop-color="#6F8BB8" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <text id="name" x="590" y="150" font-size="96" font-weight="900" letter-spacing="4">RAYEN<tspan x="590" dy="98">CHATTI</tspan></text>
    <clipPath id="t1"><rect x="585" y="262" height="32" width="0"><animate attributeName="width" to="560" begin="0.8s" dur="1.8s" fill="freeze"/></rect></clipPath>
    <clipPath id="t2"><rect x="585" y="296" height="32" width="0"><animate attributeName="width" to="560" begin="2.6s" dur="1.6s" fill="freeze"/></rect></clipPath>
    <style>
      text {{ font-family: 'Segoe UI', 'Inter', Ubuntu, 'Helvetica Neue', Arial, sans-serif; }}
      text.mono, .mono text {{ font-family: 'Fira Code', 'JetBrains Mono', Consolas, 'Courier New', monospace; }}
      .star {{ fill: #ECE8DF; animation: tw ease-in-out infinite; }}
      @keyframes tw {{ 50% {{ opacity: .1 }} }}
      .gl {{ stroke: #6F8BB8; stroke-opacity: .35; stroke-width: 1; }}
      .front {{ fill: url(#face); stroke: #f3ffc4; stroke-width: 1.5; stroke-linejoin: round; }}
      .side {{ fill: #24385c; fill-opacity: .75; stroke: #6F8BB8; stroke-opacity: .6; stroke-width: .8; }}
      .back {{ fill: #101a30; stroke: #3c5580; stroke-width: 1; }}
      .float {{ animation: float 4s ease-in-out infinite; }}
      @keyframes float {{ 50% {{ transform: translateY(-10px) }} }}
      .padring {{ transform-origin: 300px 352px; animation: ring 2.4s ease-out infinite; }}
      @keyframes ring {{ from {{ transform: scale(.4); opacity: 1 }} to {{ transform: scale(1.5); opacity: 0 }} }}
      .intro {{ opacity: 0; animation: intro 1.2s cubic-bezier(.2,.8,.2,1) .2s forwards; }}
      @keyframes intro {{ from {{ opacity: 0; transform: translateY(20px) }} to {{ opacity: 1; transform: none }} }}
      .sub {{ font-size: 22px; fill: #B9C7DD; }}
      .sub2 {{ font-size: 22px; fill: #ECE8DF; }}
      .cur {{ fill: #ECE8DF; animation: blink 1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0 }} }}
    </style>
  </defs>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{HORIZON}" fill="url(#sky)"/>
    {stars}
    <rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#floor)"/>
    {"".join(grid)}
    <line x1="0" x2="{W}" y1="{HORIZON}" y2="{HORIZON}" stroke="#B9C7DD" stroke-opacity=".6" filter="url(#glow)"/>

    <!-- hologram pad + beam -->
    <ellipse cx="300" cy="352" rx="150" ry="26" fill="url(#pad)"/>
    <ellipse class="padring" cx="300" cy="352" rx="120" ry="20" fill="none" stroke="#D4FF3A" stroke-width="2"/>
    <polygon points="170,352 430,352 380,60 220,60" fill="url(#beam)"/>

    <!-- rotating 3D </> -->
    <ellipse cx="300" cy="195" rx="150" ry="90" fill="url(#padlime)" opacity=".3"/>
    <g class="float">
      {"".join(glyph_svg)}
    </g>

    <!-- 3D extruded name -->
    <g class="intro">
      {"".join(name_layers)}
      <use href="#name" fill="#D4FF3A"/>
    </g>

    <g class="mono">
      <text class="sub" x="590" y="286" clip-path="url(#t1)">&gt; software_engineering.student()</text>
      <text class="sub2" x="590" y="320" clip-path="url(#t2)">web · mobile · ai · cybersecurity <tspan class="cur">▌</tspan></text>
    </g>
  </g>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="none" stroke="#6F8BB8" stroke-opacity=".5" stroke-width="2"/>
</svg>
"""

out = Path(__file__).resolve().parent.parent / "assets" / "header.svg"
out.write_text(svg, encoding="utf-8")
print(f"wrote {out} ({len(svg)//1024} KB)")
