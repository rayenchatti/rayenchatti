"""Generates assets/globe.svg: a rotating 3D wireframe globe with Tunisia pinned and
arcs launching to cities around the world, plus hackathon results.

Run: python scripts/gen_globe.py
"""
import math
import random
from pathlib import Path

W, H = 1200, 440
CX, CY, R = 600, 220, 150
FRAMES, DUR = 72, 30
INK, STEEL, LIGHT, BONE, ACCENT = "#0A1222", "#6F8BB8", "#B9C7DD", "#ECE8DF", "#D4FF3A"
random.seed(11)

HOME = (34, 9)  # Tunisia
CITIES = [(49, 2), (52, 13), (45, -73), (36, 140), (37, -122), (25, 55), (-34, 151)]


def vec(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo))


def spin(v, th):
    x, y, z = v
    return (x * math.cos(th) + z * math.sin(th), y, -x * math.sin(th) + z * math.cos(th))


def screen(v):
    x, y, z = v
    return CX + R * x, CY - R * y, z


def slerp(a, b, t):
    dot = max(-1, min(1, sum(p * q for p, q in zip(a, b))))
    om = math.acos(dot)
    if om < 1e-6:
        return a
    s1, s2 = math.sin((1 - t) * om) / math.sin(om), math.sin(t * om) / math.sin(om)
    return tuple(s1 * p + s2 * q for p, q in zip(a, b))


thetas = [-2 * math.pi * k / FRAMES for k in range(FRAMES + 1)]

# meridians: ellipses whose width follows the rotation
meridians = []
for lon in range(0, 180, 20):
    rxs = ";".join(f"{R * abs(math.sin(math.radians(lon) + th)):.1f}" for th in thetas)
    meridians.append(f'<ellipse cx="{CX}" cy="{CY}" rx="0" ry="{R}" class="mer">'
                     f'<animate attributeName="rx" values="{rxs}" dur="{DUR}s" repeatCount="indefinite"/></ellipse>')
parallels = []
for lat in range(-60, 61, 30):
    y = CY - R * math.sin(math.radians(lat))
    hw = R * math.cos(math.radians(lat))
    parallels.append(f'<line x1="{CX - hw:.1f}" x2="{CX + hw:.1f}" y1="{y:.1f}" y2="{y:.1f}" class="par"/>')


def moving_point(v0, r=4, cls="city"):
    xs, ops = [], []
    for th in thetas:
        x, y, z = screen(spin(v0, th))
        xs.append(f"{x:.1f}")
        ops.append(f"{max(0, min(1, z * 3 + 0.4)):.2f}")
    _, y, _ = screen(v0)
    return (f'<circle cy="{y:.1f}" cx="{xs[0]}" r="{r}" class="{cls}">'
            f'<animate attributeName="cx" values="{";".join(xs)}" dur="{DUR}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{";".join(ops)}" dur="{DUR}s" repeatCount="indefinite"/></circle>'), xs, ops, y


home_v = vec(*HOME)
home_dot, hxs, hops, hy = moving_point(home_v, 6, "home")
home_ring = (f'<circle cy="{hy:.1f}" cx="{hxs[0]}" r="6" class="ring">'
             f'<animate attributeName="cx" values="{";".join(hxs)}" dur="{DUR}s" repeatCount="indefinite"/>'
             f'<animate attributeName="r" values="6;22" dur="1.8s" repeatCount="indefinite"/>'
             f'<animate attributeName="stroke-opacity" values="1;0" dur="1.8s" repeatCount="indefinite"/></circle>')

cities, arcs = [], []
for ci, (lat, lon) in enumerate(CITIES):
    dot, *_ = moving_point(vec(lat, lon), 3.5)
    cities.append(dot)
    target = vec(lat, lon)
    ds, ops = [], []
    for th in thetas:
        pts, zs = [], []
        for s in range(21):
            t = s / 20
            p = slerp(home_v, target, t)
            lift = 1 + 0.28 * math.sin(math.pi * t)
            x, y, z = screen(spin(tuple(c * lift for c in p), th))
            pts.append(f"{x:.1f},{y:.1f}")
            zs.append(z)
        ds.append("M" + "L".join(pts))
        ops.append(f"{max(0, min(1, (sum(zs) / len(zs)) * 2.5 + 0.3)):.2f}")
    arcs.append(f'<path class="arc" d="{ds[0]}" style="animation-delay:{ci * 0.4:.1f}s">'
                f'<animate attributeName="d" values="{";".join(ds)}" dur="{DUR}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{";".join(ops)}" dur="{DUR}s" repeatCount="indefinite"/></path>')

stars = "".join(
    f'<circle cx="{random.uniform(10, W-10):.0f}" cy="{random.uniform(10, H-10):.0f}" r="{random.choice([.6, .9, 1.2])}" '
    f'class="star" style="animation-delay:{random.uniform(0, 5):.1f}s"/>' for _ in range(70)
)

# extruded 3D words on the left
def extruded(text, x, y, size, face):
    layers = "".join(
        f'<text x="{x + i * 0.9:.1f}" y="{y + i * 0.9:.1f}" font-size="{size}" class="big" '
        f'fill="rgb({20 + i * 3},{34 + i * 5},{60 + i * 9})">{text}</text>' for i in range(10, 0, -1)
    )
    return layers + f'<text x="{x}" y="{y}" font-size="{size}" class="big" fill="{face}">{text}</text>'


WINS = [("1st", "OPSYNC Hackathon", "IEEE ISIMa CS SBC"),
        ("1st", "DevHeist", "ISIMa DevOps Club"),
        ("TOP 5", "HACK4UCAR 2025", "out of 30 teams")]
wins = []
for i, (rank, name, org) in enumerate(WINS):
    y = 120 + i * 92
    wins.append(f"""
    <g class="win" style="animation-delay:{0.5 + i * 0.35:.2f}s">
      <rect x="868" y="{y}" width="290" height="72" fill="{INK}" stroke="{STEEL}" stroke-opacity=".6"/>
      <rect x="868" y="{y}" width="6" height="72" fill="{ACCENT}"/>
      <text x="892" y="{y + 31}" class="rank">{rank}</text>
      <text x="972" y="{y + 31}" class="wn">{name}</text>
      <text x="972" y="{y + 54}" class="wo">{org}</text>
    </g>""")

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Rotating globe: from Tunisia to the world, with hackathon results">
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#060b16"/><stop offset="1" stop-color="#0f1b33"/>
    </linearGradient>
    <radialGradient id="sphere" cx="0.38" cy="0.32" r="0.75">
      <stop offset="0" stop-color="#2a4370"/><stop offset="0.6" stop-color="#121f3a"/><stop offset="1" stop-color="#070d1a"/>
    </radialGradient>
    <radialGradient id="atmo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0.82" stop-color="{STEEL}" stop-opacity="0"/><stop offset="0.9" stop-color="{STEEL}" stop-opacity=".35"/><stop offset="1" stop-color="{STEEL}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <style>
    text {{ font-family: 'Fira Code', 'JetBrains Mono', Consolas, 'Courier New', monospace; }}
    .big {{ font-family: 'Segoe UI', Inter, Ubuntu, Arial, sans-serif; font-weight: 900; letter-spacing: 2px; }}
    .star {{ fill: {BONE}; animation: tw 4s ease-in-out infinite; }}
    @keyframes tw {{ 50% {{ opacity: .1 }} }}
    .mer, .par {{ fill: none; stroke: {STEEL}; stroke-opacity: .45; stroke-width: 1; }}
    .city {{ fill: {LIGHT}; }}
    .home {{ fill: {ACCENT}; }}
    .ring {{ fill: none; stroke: {ACCENT}; stroke-width: 2; }}
    .arc {{ fill: none; stroke: {LIGHT}; stroke-width: 1.6; stroke-dasharray: 5 7; animation: flow 1.2s linear infinite; }}
    @keyframes flow {{ to {{ stroke-dashoffset: -24 }} }}
    .orbit {{ fill: none; stroke: {STEEL}; stroke-opacity: .5; stroke-dasharray: 2 6; }}
    .sat {{ fill: {BONE}; }}
    .win {{ opacity: 0; animation: win .7s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes win {{ from {{ opacity: 0; transform: translateX(24px) }} to {{ opacity: 1; transform: none }} }}
    .rank {{ fill: {ACCENT}; font-size: 22px; font-weight: 800; }}
    .wn {{ fill: {BONE}; font-size: 17px; font-weight: 600; }}
    .wo {{ fill: #8193b3; font-size: 13px; }}
    .lbl {{ fill: #8193b3; font-size: 14px; }}
    .cta {{ fill: {LIGHT}; font-size: 16px; }}
    .cur {{ fill: {ACCENT}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
  </style>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    {stars}

    <circle cx="{CX}" cy="{CY}" r="{R + 22}" fill="url(#atmo)"/>
    <circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#sphere)"/>
    {"".join(parallels)}
    {"".join(meridians)}
    <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{LIGHT}" stroke-opacity=".6"/>
    {"".join(arcs)}
    {"".join(cities)}
    {home_ring}{home_dot}

    <ellipse id="orb" cx="{CX}" cy="{CY}" rx="220" ry="46" class="orbit" transform="rotate(-14 {CX} {CY})"/>
    <circle r="4" class="sat"><animateMotion dur="9s" repeatCount="indefinite" rotate="auto"
      path="M{CX - 220},{CY} a220,46 0 1,0 440,0 a220,46 0 1,0 -440,0"/></circle>

    <text x="44" y="84" class="lbl">// based in</text>
    {extruded("FROM", 44, 150, 64, BONE)}
    {extruded("TUNISIA", 44, 222, 64, ACCENT)}
    {extruded("TO THE", 44, 294, 64, BONE)}
    {extruded("WORLD", 44, 366, 64, BONE)}

    <text x="868" y="96" class="lbl">// hackathon results</text>
    {"".join(wins)}
    <text x="868" y="410" class="cta">$ let's build something <tspan class="cur">▌</tspan></text>
  </g>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="none" stroke="{STEEL}" stroke-opacity=".5" stroke-width="2"/>
</svg>
"""

out = Path(__file__).resolve().parent.parent / "assets" / "globe.svg"
out.write_text(svg, encoding="utf-8")
print(f"wrote {out} ({len(svg)//1024} KB)")
