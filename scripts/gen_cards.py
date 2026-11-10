"""Generates assets/whoami.svg (animated terminal) and assets/project-*.svg (3D project cards).

Run: python scripts/gen_cards.py
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
INK, PANEL, STEEL, LIGHT, BONE, ACCENT, MUTED = "#0A1222", "#0d1830", "#6F8BB8", "#B9C7DD", "#ECE8DF", "#D4FF3A", "#8193b3"
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))

BASE_STYLE = f"""
    text {{ font-family: 'Fira Code', 'JetBrains Mono', Consolas, 'Courier New', monospace; }}
    .big {{ font-family: 'Segoe UI', Inter, Ubuntu, Arial, sans-serif; font-weight: 900; }}
    @keyframes in {{ to {{ opacity: 1 }} }}
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def shade(hex_color, k):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * k))) for c in (r, g, b))


def poly(pts, fill, extra=""):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" {extra}/>'


def iso_box(ox, oy, u, gx, gy, w, d, h, color, z=0):
    def iso(a, b, hh):
        return ox + (a - b) * C30 * u, oy + (a + b) * S30 * u - hh
    A, B, C, D = iso(gx, gy, z + h), iso(gx + w, gy, z + h), iso(gx + w, gy + d, z + h), iso(gx, gy + d, z + h)
    bl, bc, br = iso(gx, gy + d, z), iso(gx + w, gy + d, z), iso(gx + w, gy, z)
    return (poly([D, C, bc, bl], shade(color, 0.55)) + poly([C, B, br, bc], shade(color, 0.8)) +
            poly([A, B, C, D], shade(color, 1.1), 'stroke="#ffffff" stroke-opacity=".2"'))


def frame_card(w, h, depth=12):
    """Card with an extruded 3D edge, like the stats cards."""
    return (f'<polygon points="0,{depth} {depth},0 {w},0 {w},{h - depth} {w - depth},{h} 0,{h}" fill="#1d2f52"/>'
            f'<rect x="0" y="{depth}" width="{w - depth}" height="{h - depth}" fill="{INK}" stroke="{STEEL}" stroke-opacity=".6"/>')


# =====================================================================
# whoami terminal
# =====================================================================
def whoami():
    W, H = 1200, 400
    lines = [
        # (kind, text, extra)  kind: cmd | out | kv | win
        ("cmd", "whoami", None),
        ("out", "rayen chatti  /  software engineering student @ ISIMa, Tunisia", None),
        ("cmd", "cat focus.txt", None),
        ("kv", "web & mobile", "idea -> deployed product, end to end"),
        ("kv", "ai", "RAG pipelines, local LLMs, assistants"),
        ("kv", "security", "learning to break things to secure them"),
        ("cmd", 'grep -c "1st place" hackathons.log', None),
        ("win", "2", "and a top 5 / 30 at HACK4UCAR"),
    ]
    x0, y0, lh = 48, 104, 34
    t = 0.4
    body = []
    for i, (kind, text, extra) in enumerate(lines):
        y = y0 + i * lh
        if kind == "cmd":
            dur = 0.05 * len(text) + 0.3
            body.append(
                f'<clipPath id="c{i}"><rect x="{x0 + 150}" y="{y - 24}" height="34" width="0">'
                f'<animate attributeName="width" to="900" begin="{t + 0.3:.2f}s" dur="{dur * 2.4:.2f}s" fill="freeze"/></rect></clipPath>'
                f'<g class="ln" style="animation-delay:{t:.2f}s">'
                f'<text x="{x0}" y="{y}" class="prompt">rayen@isima</text><text x="{x0 + 122}" y="{y}" class="sym">$</text>'
                f'<text x="{x0 + 150}" y="{y}" class="cmd" clip-path="url(#c{i})">{esc(text)}</text></g>'
            )
            t += dur + 0.5
        elif kind == "out":
            body.append(f'<text x="{x0}" y="{y}" class="out ln" style="animation-delay:{t:.2f}s">{esc(text)}</text>')
            t += 0.5
        elif kind == "kv":
            body.append(
                f'<g class="ln" style="animation-delay:{t:.2f}s"><text x="{x0 + 24}" y="{y}" class="key">{esc(text)}</text>'
                f'<text x="{x0 + 210}" y="{y}" class="dots">::</text>'
                f'<text x="{x0 + 250}" y="{y}" class="out">{esc(extra)}</text></g>'
            )
            t += 0.35
        elif kind == "win":
            body.append(
                f'<g class="ln" style="animation-delay:{t:.2f}s"><text x="{x0}" y="{y + 4}" class="win">{text}</text>'
                f'<text x="{x0 + 40}" y="{y}" class="dim">// {esc(extra)}</text></g>'
            )
            t += 0.4
    last_y = y0 + len(lines) * lh
    body.append(
        f'<g class="ln" style="animation-delay:{t:.2f}s"><text x="{x0}" y="{last_y}" class="prompt">rayen@isima</text>'
        f'<text x="{x0 + 122}" y="{last_y}" class="sym">$</text><rect x="{x0 + 150}" y="{last_y - 18}" width="11" height="22" class="cur"/></g>'
    )

    # a slowly rotating wireframe cube in the corner, for depth
    verts = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8) if sum(p != q for p, q in zip(verts[a], verts[b])) == 1]
    F = 60
    cx, cy, s = 1040, 220, 62
    frames = []
    for k in range(F + 1):
        a = 2 * math.pi * k / F
        b = math.radians(25)
        pts = []
        for x, y, z in verts:
            x1 = x * math.cos(a) + z * math.sin(a)
            z1 = -x * math.sin(a) + z * math.cos(a)
            y1 = y * math.cos(b) - z1 * math.sin(b)
            pts.append((cx + x1 * s, cy + y1 * s))
        frames.append(pts)
    cube = []
    for a_, b_ in edges:
        vals = {k: ";".join(f"{fr[i][j]:.1f}" for fr in frames) for k, (i, j) in
                {"x1": (a_, 0), "y1": (a_, 1), "x2": (b_, 0), "y2": (b_, 1)}.items()}
        anims = "".join(f'<animate attributeName="{k}" values="{v}" dur="14s" repeatCount="indefinite"/>' for k, v in vals.items())
        cube.append(f'<line class="edge">{anims}</line>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="whoami: Rayen Chatti, software engineering student at ISIMa, Tunisia. Web and mobile, AI, security. Two first places at hackathons.">
  <style>{BASE_STYLE}
    .bar {{ fill: {PANEL}; }}
    .title {{ fill: {MUTED}; font-size: 14px; }}
    .prompt {{ fill: {STEEL}; font-size: 19px; }}
    .sym {{ fill: {MUTED}; font-size: 19px; }}
    .cmd {{ fill: {BONE}; font-size: 19px; }}
    .out {{ fill: {LIGHT}; font-size: 18px; }}
    .key {{ fill: {BONE}; font-size: 18px; font-weight: 700; }}
    .dots {{ fill: {MUTED}; font-size: 18px; }}
    .dim {{ fill: {MUTED}; font-size: 17px; }}
    .win {{ fill: {ACCENT}; font-size: 30px; font-weight: 800; }}
    .ln {{ opacity: 0; animation: in .2s forwards; }}
    .cur {{ fill: {ACCENT}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    .edge {{ stroke: {STEEL}; stroke-opacity: .55; stroke-width: 1.5; }}
  </style>
  {frame_card(W, H, 14)}
  <rect x="0" y="14" width="{W - 14}" height="42" class="bar"/>
  <circle cx="28" cy="35" r="6" fill="{STEEL}" fill-opacity=".5"/>
  <circle cx="48" cy="35" r="6" fill="{STEEL}" fill-opacity=".5"/>
  <circle cx="68" cy="35" r="6" fill="{ACCENT}"/>
  <text x="{(W - 14) / 2}" y="40" text-anchor="middle" class="title">rayen@isima: ~ / zsh</text>
  {''.join(cube)}
  {''.join(body)}
</svg>
"""
    (OUT / "whoami.svg").write_text(svg, encoding="utf-8")


# =====================================================================
# project scenes (drawn around a center point, inside the right part of a card)
# =====================================================================
def scene_flashcards(cx, cy):
    """VeritasLearn: a floating stack of study cards."""
    out = []
    for i in range(3):
        z = i * 34
        top = i == 2
        color = "#24385c" if not top else "#2f4a78"
        card = iso_box(cx - 10, cy + 40, 30, -1.6, -1.1, 3.2, 2.2, 6, color, z=z)
        lines = ""
        if top:
            for j, ln in enumerate((2.2, 1.6, 2.4)):
                gx, gy = -1.2, -0.6 + j * 0.55
                x1, y1 = cx - 10 + (gx - gy) * C30 * 30, cy + 40 + (gx + gy) * S30 * 30 - z - 6
                x2, y2 = cx - 10 + (gx + ln - gy) * C30 * 30, cy + 40 + (gx + ln + gy) * S30 * 30 - z - 6
                lines += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ACCENT if j == 0 else LIGHT}" stroke-width="3" stroke-linecap="round" stroke-opacity=".9"/>'
        out.append(f'<g class="bob" style="animation-delay:{-i * 0.6:.1f}s">{card}{lines}</g>')
    return "".join(out)


def scene_qr(cx, cy):
    """LifePass: a QR code tilted into 3D with a scan beam."""
    random.seed(5)
    N, m = 17, 7
    cells = []
    finder = lambda r, c: any(r0 <= r < r0 + 7 and c0 <= c < c0 + 7 for r0, c0 in ((0, 0), (0, N - 7), (N - 7, 0)))
    for r in range(N):
        for c in range(N):
            if finder(r, c):
                rr = min(r % (N - 7) if r >= N - 7 else r, 6)
                cc = min(c % (N - 7) if c >= N - 7 else c, 6)
                rr, cc = (r - (N - 7) if r >= N - 7 else r), (c - (N - 7) if c >= N - 7 else c)
                on = rr in (0, 6) or cc in (0, 6) or (2 <= rr <= 4 and 2 <= cc <= 4)
            else:
                on = random.random() < 0.45
            if on:
                cells.append(f'<rect x="{c * m}" y="{r * m}" width="{m - 1}" height="{m - 1}"/>')
    size = N * m
    ox, oy = cx, cy - 58
    return f"""
    <g transform="matrix({C30:.3f},{S30:.3f},{-C30:.3f},{S30:.3f},{ox},{oy})">
      <rect x="-14" y="-14" width="{size + 28}" height="{size + 28}" fill="#1d2f52" transform="translate(10,10)"/>
      <rect x="-14" y="-14" width="{size + 28}" height="{size + 28}" fill="{PANEL}" stroke="{STEEL}" stroke-opacity=".7"/>
      <g fill="{LIGHT}">{''.join(cells)}</g>
      <rect x="-14" y="0" width="{size + 28}" height="4" fill="{ACCENT}" opacity=".9">
        <animate attributeName="y" values="-14;{size + 10};-14" dur="3.2s" repeatCount="indefinite"/>
      </rect>
    </g>"""


def scene_pulse(cx, cy):
    """UCAR Pulse: 30 institutions as pillars, with a pulse wave rippling out from the hub."""
    u, cols, rows = 22, 6, 5
    ox, oy = cx - 10, cy - 10
    hub = (2, 2)
    out = []
    order = sorted(((c, r) for c in range(cols) for r in range(rows)), key=lambda p: p[0] + p[1])
    for c, r in order:
        gx, gy = c - cols / 2, r - rows / 2
        dist = math.hypot(c - hub[0], r - hub[1])
        color = ACCENT if (c, r) == hub else STEEL
        h = 18
        bx = ox + (gx + 0.35 - gy - 0.35) * C30 * u
        by = oy + (gx + 0.35 + gy + 0.35) * S30 * u
        out.append(f'<g class="pillar" style="transform-origin:{bx:.1f}px {by:.1f}px;animation-delay:{dist * 0.18:.2f}s">'
                   f'{iso_box(ox, oy, u, gx, gy, 0.7, 0.7, h, color)}</g>')
    return "".join(out)


def scene_network(cx, cy):
    """ITGate: a small neural network rotating in 3D, layers lighting up in turn."""
    layers = [3, 4, 4, 2]
    nodes = []
    for li, n in enumerate(layers):
        for k in range(n):
            nodes.append((li, ((li - 1.5) * 1.0, (k - (n - 1) / 2) * 0.75, ((k * 37 + li * 11) % 5 - 2) * 0.18)))
    edges = [(a, b) for a in range(len(nodes)) for b in range(len(nodes)) if nodes[b][0] == nodes[a][0] + 1]
    F, s = 48, 78
    frames = []
    for k in range(F + 1):
        a = math.radians(40) * math.sin(2 * math.pi * k / F)
        b = math.radians(12)
        pts = []
        for _, (x, y, z) in nodes:
            x1 = x * math.cos(a) + z * math.sin(a)
            z1 = -x * math.sin(a) + z * math.cos(a)
            y1 = y * math.cos(b) - z1 * math.sin(b)
            pts.append((cx + x1 * s, cy + y1 * s))
        frames.append(pts)

    def anim(attr, i, j):
        return f'<animate attributeName="{attr}" values="{";".join(f"{fr[i][j]:.1f}" for fr in frames)}" dur="10s" repeatCount="indefinite"/>'

    out = []
    for a_, b_ in edges:
        out.append(f'<line class="syn">{anim("x1", a_, 0)}{anim("y1", a_, 1)}{anim("x2", b_, 0)}{anim("y2", b_, 1)}</line>')
    for i, (li, _) in enumerate(nodes):
        fill = ACCENT if li == len(layers) - 1 else LIGHT
        out.append(f'<circle r="6" fill="{fill}" class="node" style="animation-delay:{li * 0.35:.2f}s">{anim("cx", i, 0)}{anim("cy", i, 1)}</circle>')
    return "".join(out)


def scene_explorer(cx, cy):
    """ScoutSmart: an isometric map tile where discovery pins drop in one by one."""
    u = 34
    ox, oy = cx - 6, cy + 4
    out = [iso_box(ox, oy, u, -2, -2, 4, 4, 10, "#1d2f52")]
    def iso(a, b, h):
        return ox + (a - b) * C30 * u, oy + (a + b) * S30 * u - h
    # faint grid on the tile
    for i in range(5):
        x1, y1 = iso(-2 + i, -2, 10); x2, y2 = iso(-2 + i, 2, 10)
        x3, y3 = iso(-2, -2 + i, 10); x4, y4 = iso(2, -2 + i, 10)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{STEEL}" stroke-opacity=".35"/>'
                   f'<line x1="{x3:.1f}" y1="{y3:.1f}" x2="{x4:.1f}" y2="{y4:.1f}" stroke="{STEEL}" stroke-opacity=".35"/>')
    pins = [(-1.2, -0.8), (0.6, -1.3), (-0.4, 0.9), (1.2, 0.5), (0.2, -0.1)]
    for i, (a, b) in enumerate(pins):
        x, y = iso(a, b, 10)
        hi = i == len(pins) - 1
        col = ACCENT if hi else LIGHT
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="8" ry="4" fill="#000" fill-opacity=".35"/>'
                   f'<g class="pin" style="animation-delay:{i * 0.5:.1f}s">'
                   f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y - 34:.1f}" stroke="{col}" stroke-width="2"/>'
                   f'<circle cx="{x:.1f}" cy="{y - 40:.1f}" r="{9 if hi else 7}" fill="{col}"/></g>')
    return "".join(out)


def scene_layers(cx, cy):
    """Portfolio: stacked 3D pages sliding past each other, like scroll-driven scenes."""
    out = []
    for i in range(3):
        x = cx - 70 + i * 34
        y = cy - 70 - i * 6
        top = i == 2
        body = (f'<rect width="120" height="150" fill="{PANEL if not top else "#132344"}" stroke="{STEEL}" stroke-opacity=".8"/>'
                f'<rect width="120" height="16" fill="#1d2f52"/>'
                f'<rect x="12" y="30" width="{70 - i * 10}" height="6" fill="{LIGHT}" fill-opacity=".6"/>'
                f'<rect x="12" y="44" width="{90 - i * 14}" height="6" fill="{LIGHT}" fill-opacity=".35"/>')
        if top:
            body += (f'<circle cx="60" cy="96" r="22" fill="none" stroke="{ACCENT}" stroke-width="3"/>'
                     f'<circle cx="60" cy="96" r="6" fill="{ACCENT}"><animate attributeName="cx" values="52;68;52" dur="3s" repeatCount="indefinite"/></circle>')
        out.append(f'<g class="slide" style="animation-delay:{-i * 0.7:.1f}s">'
                   f'<g transform="matrix(0.866,0.5,0,1,{x},{y})">{body}</g></g>')
    return "".join(out)


PROJECTS = [
    ("veritaslearn", "VeritasLearn", ["AI study assistant that turns", "material into lessons, quizzes", "and flashcards."],
     "1ST PRIZE", "OPSYNC Hackathon", ["React Native", "Supabase", "Groq"], scene_flashcards),
    ("lifepass", "LifePass", ["Medical records shared through", "a personal QR code."],
     "1ST PRIZE", "DevHeist", ["React", "Tailwind", "Framer Motion"], scene_qr),
    ("ucar-pulse", "UCAR Pulse", ["AI platform connecting 30+", "University of Carthage", "institutions."],
     "TOP 5 / 30", "HACK4UCAR 2025", ["Next.js", "FastAPI", "Qdrant"], scene_pulse),
    ("scoutsmart", "ScoutSmart", ["AI nature explorer for kids:", "scan plants and animals, earn", "XP, pin discoveries on a map."],
     "HACKATHON BUILD", "Vecna's Algorithm 2.0", ["React Native", "Expo", "Gemini"], scene_explorer),
    ("itgate", "ITGate AI", ["Company-grounded RAG assistant", "running on a local LLM."],
     "INTERNSHIP", "ITGate Group", ["Spring Boot", "FastAPI", "Ollama"], scene_network),
    ("portfolio", "Portfolio", ["3D portfolio with scroll-driven", "WebGL scenes and a cursor-", "tracking portrait."],
     "LIVE", "rayenchatti.vercel.app", ["Next.js", "Three.js", "WebGL"], scene_layers),
]


def project_card(slug, name, desc, rank, event, stack, scene):
    W, H = 600, 340
    desc_svg = "".join(f'<text x="34" y="{128 + i * 24}" class="desc">{esc(d)}</text>' for i, d in enumerate(desc))
    chips, x = [], 34
    for t in stack:
        w = 16 + len(t) * 8.6
        chips.append(f'<rect x="{x}" y="270" width="{w:.0f}" height="30" fill="{PANEL}" stroke="{STEEL}" stroke-opacity=".5"/>'
                     f'<text x="{x + w / 2:.0f}" y="290" text-anchor="middle" class="chip">{esc(t)}</text>')
        x += w + 8
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(name)}: {esc(' '.join(desc))} {esc(rank)}, {esc(event)}.">
  <style>{BASE_STYLE}
    .name {{ fill: {BONE}; font-size: 34px; }}
    .desc {{ fill: {LIGHT}; font-size: 15px; }}
    .rank {{ fill: {ACCENT}; font-size: 16px; font-weight: 800; letter-spacing: 1px; }}
    .event {{ fill: {MUTED}; font-size: 15px; }}
    .chip {{ fill: {LIGHT}; font-size: 13px; }}
    .open {{ fill: {MUTED}; font-size: 13px; }}
    .bob {{ animation: bob 3.6s ease-in-out infinite; }}
    @keyframes bob {{ 50% {{ transform: translateY(-12px) }} }}
    .pillar {{ animation: pulse 2.8s ease-in-out infinite; }}
    @keyframes pulse {{ 0%, 100% {{ transform: scaleY(1) }} 25% {{ transform: scaleY(2.1) }} 50% {{ transform: scaleY(1) }} }}
    .syn {{ stroke: {STEEL}; stroke-opacity: .45; stroke-width: 1.2; }}
    .node {{ animation: fire 1.6s ease-in-out infinite; }}
    @keyframes fire {{ 0%, 100% {{ opacity: .55 }} 30% {{ opacity: 1 }} }}
    .pin {{ opacity: 0; animation: drop 3s cubic-bezier(.3,1.6,.5,1) infinite; }}
    @keyframes drop {{ 0% {{ opacity: 0; transform: translateY(-30px) }} 15%, 85% {{ opacity: 1; transform: none }} 100% {{ opacity: 0 }} }}
    .slide {{ animation: slide 4s ease-in-out infinite; }}
    @keyframes slide {{ 50% {{ transform: translate(-10px, -8px) }} }}
    .reveal {{ opacity: 0; animation: in .6s forwards; }}
  </style>
  {frame_card(W, H)}
  <g class="reveal" style="animation-delay:.1s">
    <text x="34" y="82" class="big name">{esc(name)}</text>
    {desc_svg}
  </g>
  <g class="reveal" style="animation-delay:.4s">
    <rect x="34" y="214" width="4" height="34" fill="{ACCENT}"/>
    <text x="50" y="228" class="rank">{esc(rank)}</text>
    <text x="50" y="246" class="event">{esc(event)}</text>
  </g>
  <g class="reveal" style="animation-delay:.6s">{''.join(chips)}</g>
  <text x="{W - 40}" y="56" text-anchor="end" class="open">open repo -&gt;</text>
  {scene(460, 170)}
</svg>
"""
    (OUT / f"project-{slug}.svg").write_text(svg, encoding="utf-8")


whoami()
for p in PROJECTS:
    project_card(*p)
print("wrote whoami.svg and", len(PROJECTS), "project cards")
