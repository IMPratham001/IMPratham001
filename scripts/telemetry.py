"""Builds assets/telemetry.svg from the GitHub API (public repos of the profile owner).

Usage: python scripts/telemetry.py <username> [token]
"""
import json, sys, urllib.request

user = sys.argv[1]
token = sys.argv[2] if len(sys.argv) > 2 else None
SANS = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'Fira Code','Cascadia Code',Consolas,monospace"
COLORS = ["#00E5FF", "#0A84FF", "#3DDC97", "#7F5AF0", "#FFB020", "#FF5C8A", "#7fa6c4"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "telemetry"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


profile = get(f"https://api.github.com/users/{user}")
repos = [r for r in get(f"https://api.github.com/users/{user}/repos?per_page=100") if not r["fork"]]
langs = {}
for r in repos:
    for k, v in get(r["languages_url"]).items():
        langs[k] = langs.get(k, 0) + v
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
stars = sum(r["stargazers_count"] for r in repos)
kloc = round(total / 40000, 1)  # ~40 bytes per line -> thousands of lines
metrics = [("REPOSITORIES", str(len(repos))), ("STARS", str(stars)), ("FOLLOWERS", str(profile["followers"])), ("CODE (~KLOC)", f"{kloc}")]

W, H = 1200, 300
b = []
for i, (k, v) in enumerate(metrics):
    x = 40 + i * 285
    b.append(f'<rect x="{x}" y="36" width="255" height="86" rx="10" fill="#0A84FF" fill-opacity=".10" stroke="#0A84FF" stroke-opacity=".4"/>'
             f'<text x="{x+20}" y="64" font-family="{MONO}" font-size="12" fill="#7fa6c4" letter-spacing="2">{k}</text>'
             f'<text x="{x+20}" y="106" font-family="{SANS}" font-size="38" font-weight="800" fill="#E6FBFF">{v}</text>')
b.append(f'<text x="40" y="162" font-family="{MONO}" font-size="12" fill="#00E5FF" letter-spacing="3">LANGUAGE DISTRIBUTION</text>')
x = 40
bar_w = 1120
for i, (name, size) in enumerate(top):
    w = max(size / total * bar_w, 4)
    c = COLORS[i % len(COLORS)]
    b.append(f'<rect x="{x:.1f}" y="176" width="{w:.1f}" height="14" fill="{c}"><animate attributeName="opacity" values=".7;1;.7" dur="{3+i}s" repeatCount="indefinite"/></rect>')
    x += w
for i, (name, size) in enumerate(top):
    c = COLORS[i % len(COLORS)]
    lx = 40 + (i % 3) * 380
    ly = 224 + (i // 3) * 32
    b.append(f'<circle cx="{lx+6}" cy="{ly-4}" r="6" fill="{c}"/>'
             f'<text x="{lx+22}" y="{ly}" font-family="{MONO}" font-size="14" fill="#E6FBFF">{name}</text>'
             f'<text x="{lx+22+len(name)*9+10}" y="{ly}" font-family="{MONO}" font-size="14" fill="#7fa6c4">{size/total*100:.1f}%</text>')
body = "".join(b)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub telemetry">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05090f"/><stop offset=".6" stop-color="#071a2b"/><stop offset="1" stop-color="#0a2a47"/></linearGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#0A84FF" stroke-opacity=".13"/></pattern>
<clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>{body}</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="#0A84FF" stroke-opacity=".45"/></svg>'''
open("assets/telemetry.svg", "w", encoding="utf-8").write(svg)
print("telemetry.svg", len(repos), "repos,", len(top), "languages")
