import os, json, urllib.request

user, token = os.environ["GH_USER"], os.environ.get("GH_TOKEN") or ""
q = """query($u:String!){user(login:$u){
 followers{totalCount}
 repositories(ownerAffiliation:OWNER,isFork:false,first:100){totalCount nodes{stargazerCount}}
 pullRequests{totalCount} issues{totalCount}
 contributionsCollection{totalCommitContributions restrictedContributionsCount}}}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    json.dumps({"query": q, "variables": {"u": user}}).encode(),
    {"Authorization": f"bearer {token}"})
u = json.load(urllib.request.urlopen(req))["data"]["user"]
c = u["contributionsCollection"]
rows = [
    ("Stars", sum(r["stargazerCount"] for r in u["repositories"]["nodes"])),
    ("Commits (this year)", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
    ("Pull Requests", u["pullRequests"]["totalCount"]),
    ("Issues", u["issues"]["totalCount"]),
    ("Repositories", u["repositories"]["totalCount"]),
    ("Followers", u["followers"]["totalCount"]),
]
body = "".join(
    f'<text x="25" y="{70+i*28}" fill="#C9D1D9" font-size="15">{k}</text>'
    f'<text x="300" y="{70+i*28}" fill="#00FF00" font-size="15" font-weight="700" text-anchor="end">{v}</text>'
    for i, (k, v) in enumerate(rows))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="330" height="{90+len(rows)*28}" font-family="Segoe UI,Arial,sans-serif">
<rect width="100%" height="100%" rx="8" fill="#0D1117" stroke="#00FF00" stroke-opacity=".4"/>
<text x="25" y="38" fill="#00FF00" font-size="19" font-weight="700">Arman's GitHub Stats</text>{body}</svg>'''
os.makedirs("assets", exist_ok=True)
open("assets/stats.svg", "w").write(svg)
