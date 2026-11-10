"""Generates assets/stats.svg from live GitHub data: an isometric 3D skyline where each
language is a tower, plus 3D stat cards.

Runs daily in .github/workflows/stats.yml. Locally: python scripts/gen_stats.py
Uses GITHUB_TOKEN if set (higher rate limits); works without it too.
"""
import json
import math
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER = os.environ.get("GH_USER", "rayenchatti")
TOKEN = os.environ.get("GITHUB_TOKEN")
ALIAS = {"Blade": "PHP", "Cython": "Python", "Jupyter Notebook": "Python"}
IGNORE = {"Dockerfile", "Shell", "Batchfile", "PowerShell", "Procfile", "Makefile", "C"}
ACCENT = "#D4FF3A"
COLORS = [ACCENT, "#6F8BB8", "#8FA6C9", "#56739F", "#B9C7DD", "#40598a"]  # #1 language gets the accent


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search_count(kind, q):
    return get(f"https://api.github.com/search/{kind}?per_page=1&q={urllib.parse.quote(q)}")["total_count"]


# ---------- data ----------
repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
# Each repo counts equally, so one repo with vendored code can't dominate.
langs = {}
for r in repos:
    sizes = {}
    for lang, size in get(r["languages_url"]).items():
        lang = ALIAS.get(lang, lang)
        if lang not in IGNORE:
            sizes[lang] = sizes.get(lang, 0) + size
    repo_total = sum(sizes.values())
    for lang, size in sizes.items():
        if repo_total:
            langs[lang] = langs.get(lang, 0) + size / repo_total
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
total = sum(v for _, v in top) or 1
top = [(name, v / total) for name, v in top]

since = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
cards = [
    ("repositories", len(repos)),
    ("commits / 12 months", search_count("commits", f"author:{USER} author-date:>={since}")),
    ("pull requests", search_count("issues", f"author:{USER} type:pr")),
    ("stars earned", sum(r["stargazers_count"] for r in repos)),
]
updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ---------- isometric helpers ----------
W, H = 1200, 560
U = 38
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
OX, OY = 120, 440


def iso(gx, gy, h=0):
    return OX + (gx - gy) * C30 * U, OY + (gx + gy) * S30 * U - h


def poly(pts, fill, extra=""):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" {extra}/>'


def shade(hex_color, k):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * k))) for c in (r, g, b))


def box(gx, gy, w, d, h, color, z=0):
    """Isometric box: footprint w x d grid cells, height h px, sitting at height z."""
    a, b_, c, d_ = iso(gx, gy, z + h), iso(gx + w, gy, z + h), iso(gx + w, gy + d, z + h), iso(gx, gy + d, z + h)
    bl, bc, br = iso(gx, gy + d, z), iso(gx + w, gy + d, z), iso(gx + w, gy, z)
    return (
        poly([d_, c, bc, bl], shade(color, 0.55)) +   # left face
        poly([c, b_, br, bc], shade(color, 0.8)) +    # right face
        poly([a, b_, c, d_], shade(color, 1.15), 'stroke="#ffffff" stroke-opacity=".25"')  # top
    )


# ---------- plinths: one per tower, in a straight row across the screen ----------
n = len(top)
STEP = 1.6
parts = []
for i in range(n):
    g = i * STEP
    parts.append(box(g - 0.3, -g - 0.3, 1.6, 1.6, 12, "#1d2f52", z=-12))

# ---------- towers ----------
MAX_H = 230
peak = max((s for _, s in top), default=1)
towers, labels, packets = [], [], []
for i, (name, share) in enumerate(top):
    gx, gy = i * STEP, -i * STEP
    h = max(14, MAX_H * (share / peak))
    bx, by = iso(gx + 0.5, gy + 0.5)  # base center
    delay = 0.3 + i * 0.18
    towers.append(
        f'<g class="tower" style="transform-origin:{bx:.1f}px {by:.1f}px;animation-delay:{delay:.2f}s">'
        f'{box(gx, gy, 1, 1, h, COLORS[i])}</g>'
    )
    tx, ty = iso(gx + 0.5, gy + 0.5, h)
    labels.append(
        f'<g class="lbl" style="animation-delay:{delay + 0.9:.2f}s">'
        f'<line x1="{tx:.1f}" y1="{ty - 8:.1f}" x2="{tx:.1f}" y2="{ty - 30:.1f}" stroke="{COLORS[i]}" stroke-opacity=".6"/>'
        f'<text x="{tx:.1f}" y="{ty - 54:.1f}" class="ln" text-anchor="middle">{name}</text>'
        f'<text x="{tx:.1f}" y="{ty - 36:.1f}" class="lp" text-anchor="middle" fill="{COLORS[i]}">{share * 100:.0f}%</text></g>'
    )
    for p in range(2):
        packets.append(
            f'<rect x="{tx - 3:.1f}" y="{ty - 3:.1f}" width="6" height="6" fill="{COLORS[i]}" class="pk" '
            f'style="animation-delay:{delay + 1.4 + p * 1.6 + i * 0.3:.2f}s"/>'
        )

# ---------- 3D stat cards ----------
card_svg = []
CW, CH = 190, 112
for i, (label, value) in enumerate(cards):
    x = 770 + (i % 2) * (CW + 26)
    y = 150 + (i // 2) * (CH + 30)
    d = 0.6 + i * 0.2
    depth = 10
    card_svg.append(f"""
    <g class="card" style="animation-delay:{d:.1f}s">
      <polygon points="{x},{y} {x + depth},{y - depth} {x + CW + depth},{y - depth} {x + CW + depth},{y + CH - depth} {x + CW},{y + CH} {x + CW},{y}" fill="#24385c"/>
      <rect x="{x}" y="{y}" width="{CW}" height="{CH}" fill="#0a1222" stroke="#6F8BB8" stroke-opacity=".7"/>
      <text x="{x + 18}" y="{y + 32}" class="cl">{label}</text>
      <text x="{x + 18}" y="{y + 88}" class="cv" fill="{ACCENT}">{value}</text>
    </g>""")

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Language skyline and GitHub activity for {USER}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#060b16"/>
      <stop offset="1" stop-color="#0f1b33"/>
    </linearGradient>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="1" fill="#6F8BB8" fill-opacity=".18"/>
    </pattern>
  </defs>
  <style>
    text {{ font-family: 'Fira Code', 'JetBrains Mono', Consolas, 'Courier New', monospace; }}
    .h {{ fill: #ECE8DF; font-size: 22px; font-weight: 700; letter-spacing: 3px; }}
    .hs {{ fill: #7d8fae; font-size: 14px; }}
    .pg {{ stroke: #6F8BB8; stroke-opacity: .25; }}
    .tower {{ transform: scaleY(0); animation: grow 1.1s cubic-bezier(.2,.9,.2,1.15) forwards; }}
    @keyframes grow {{ to {{ transform: scaleY(1) }} }}
    .lbl {{ opacity: 0; animation: in .5s forwards, bob 3s ease-in-out infinite; }}
    .ln {{ fill: #ECE8DF; font-size: 14px; }}
    .lp {{ font-size: 16px; font-weight: 700; }}
    .pk {{ opacity: 0; animation: pk 3.2s ease-out infinite; }}
    @keyframes pk {{ 0% {{ opacity: 0; transform: translateY(0) }} 15% {{ opacity: .9 }} 100% {{ opacity: 0; transform: translateY(-120px) }} }}
    .card {{ opacity: 0; animation: cin .7s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes cin {{ from {{ opacity: 0; transform: translateY(16px) }} to {{ opacity: 1; transform: none }} }}
    .cl {{ fill: #9aabc7; font-size: 14px; }}
    .cv {{ font-size: 46px; font-weight: 800; }}
    @keyframes in {{ to {{ opacity: 1 }} }}
    @keyframes bob {{ 50% {{ transform: translateY(-5px) }} }}
  </style>

  <rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="none" stroke="#6F8BB8" stroke-opacity=".45" stroke-width="2"/>

  <text x="40" y="58" class="h">LANGUAGE SKYLINE</text>
  <text x="40" y="82" class="hs">// each repo weighted equally · updated {updated}</text>
  <text x="770" y="58" class="h">ACTIVITY</text>
  <text x="770" y="82" class="hs">// live from the GitHub API</text>

  {''.join(parts)}
  {''.join(towers)}
  {''.join(packets)}
  {''.join(labels)}
  {''.join(card_svg)}
</svg>
"""

out = Path(__file__).resolve().parent.parent / "assets" / "stats.svg"
out.write_text(svg, encoding="utf-8")
print(f"wrote {out}")
