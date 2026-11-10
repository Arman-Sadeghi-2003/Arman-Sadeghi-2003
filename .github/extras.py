import os, sys, json, urllib.request, urllib.error

user = os.environ["GH_USER"]
token = os.environ.get("GH_TOKEN", "").strip()
if not token:
    sys.exit("GH_TOKEN is missing or empty.")

q = """query($u:String!){user(login:$u){
 followers{totalCount}
 repositories(ownerAffiliations:[OWNER],isFork:false,first:100){totalCount nodes{stargazerCount}}
 pullRequests{totalCount}
 issues{totalCount}
 contributionsCollection{
  totalCommitContributions restrictedContributionsCount
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    json.dumps({"query": q, "variables": {"u": user}}).encode(),
    {"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "extras"})
try:
    res = json.load(urllib.request.urlopen(req))
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code}: {e.read().decode()}")
if "errors" in res or not res.get("data"):
    sys.exit("GraphQL error: " + json.dumps(res, indent=2))

u = res["data"]["user"]
c = u["contributionsCollection"]
os.makedirs("assets", exist_ok=True)

# ---------- Trophies ----------
stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
commits = c["totalCommitContributions"] + c["restrictedContributionsCount"]
items = [
    ("Stars", "⭐", stars, [1, 10, 50, 200]),
    ("Commits", "💾", commits, [10, 100, 500, 1500]),
    ("Followers", "👥", u["followers"]["totalCount"], [1, 10, 50, 200]),
    ("Pull Requests", "🔀", u["pullRequests"]["totalCount"], [1, 10, 50, 200]),
    ("Issues", "🐞", u["issues"]["totalCount"], [1, 10, 50, 200]),
    ("Repositories", "📦", u["repositories"]["totalCount"], [1, 10, 30, 80]),
]
ranks = ["-", "C", "B", "A", "S"]
colors = ["#30363D", "#1B7F3B", "#00C853", "#69F0AE", "#00FF00"]

def rank(v, th):
    return sum(v >= t for t in th)

cw, gap = 120, 10
W = len(items) * cw + (len(items) - 1) * gap
cards = ""
for i, (name, icon, v, th) in enumerate(items):
    r = rank(v, th)
    x = i * (cw + gap)
    cards += (
        f'<g transform="translate({x},0)">'
        f'<rect width="{cw}" height="140" rx="8" fill="#0D1117" stroke="{colors[r]}" stroke-opacity=".7"/>'
        f'<text x="{cw/2}" y="42" text-anchor="middle" font-size="26">{icon}</text>'
        f'<text x="{cw/2}" y="76" text-anchor="middle" fill="{colors[r]}" font-size="26" font-weight="700">{ranks[r]}</text>'
        f'<text x="{cw/2}" y="102" text-anchor="middle" fill="#C9D1D9" font-size="13">{name}</text>'
        f'<text x="{cw/2}" y="124" text-anchor="middle" fill="#8B949E" font-size="13">{v}</text>'
        f'</g>')
open("assets/trophies.svg", "w", encoding="utf-8").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="140" font-family="Segoe UI,Arial,sans-serif">{cards}</svg>')

# ---------- Activity graph (last 90 days) ----------
days = [d for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"]][-90:]
vals = [d["contributionCount"] for d in days]
GW, GH, px, py = 800, 220, 40, 30
mx = max(max(vals), 1)
n = max(len(vals) - 1, 1)
pts = [(px + i * (GW - 2 * px) / n, GH - py - v * (GH - 2 * py) / mx) for i, v in enumerate(vals)]
line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
area = f"{px},{GH-py} " + line + f" {pts[-1][0]:.1f},{GH-py}"
dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#FFFFFF"/>' for x, y in pts)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{GW}" height="{GH}" font-family="Segoe UI,Arial,sans-serif">
<rect width="100%" height="100%" rx="8" fill="#0D1117" stroke="#00FF00" stroke-opacity=".4"/>
<text x="{px}" y="22" fill="#00FF00" font-size="15" font-weight="700">Contributions, last 90 days</text>
<text x="{GW-px}" y="22" fill="#8B949E" font-size="12" text-anchor="end">peak: {mx}/day</text>
<line x1="{px}" y1="{GH-py}" x2="{GW-px}" y2="{GH-py}" stroke="#30363D"/>
<polygon points="{area}" fill="#00FF00" fill-opacity=".15"/>
<polyline points="{line}" fill="none" stroke="#00FF00" stroke-width="2"/>{dots}
<text x="{px}" y="{GH-10}" fill="#8B949E" font-size="11">{days[0]["date"]}</text>
<text x="{GW-px}" y="{GH-10}" fill="#8B949E" font-size="11" text-anchor="end">{days[-1]["date"]}</text>
</svg>'''
open("assets/activity.svg", "w", encoding="utf-8").write(svg)
