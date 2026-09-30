#!/usr/bin/env python3
"""Refresh star/fork/contributor counts inside assets/oss-*.svg cards."""
import json, os, re, sys, urllib.request

REPO = "ai-for-developers/awesome-ai-coding-tools"
SVG = "assets/oss-awesome-ai-coding-tools.svg"
TOKEN = os.environ.get("GITHUB_TOKEN")


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "oss-card"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), r.headers


def contributors(repo):
    data, headers = api(f"https://api.github.com/repos/{repo}/contributors?per_page=1&anonymous=true")
    m = re.search(r'page=(\d+)>; rel="last"', headers.get("Link", ""))
    return int(m.group(1)) if m else len(data)


def fmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n/1_000:.1f}k".replace(".0k", "k")
    return str(n)


info, _ = api(f"https://api.github.com/repos/{REPO}")
stats = {"stars": info["stargazers_count"], "forks": info["forks_count"], "contributors": contributors(REPO)}
svg = open(SVG, encoding="utf-8").read()
for key, val in stats.items():
    svg, n = re.subn(rf'(id="stat-{key}">)[^<]*(</text>)', rf"\g<1>{fmt(val)}\g<2>", svg)
    if n != 1:
        sys.exit(f"placeholder stat-{key} not found in {SVG}")
open(SVG, "w", encoding="utf-8").write(svg)
print("updated", stats)
