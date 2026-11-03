"""Regenerate the AI-readable parts of the portfolio from llms-full.txt.

The project table in llms-full.txt is the source. This rewrites, in index.html, the
JSON-LD block and the no-JS project list, plus sitemap.xml.

Run from the repo root:  python tools/build_ai.py
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://vedant-builds.vercel.app/"
TODAY = datetime.date.today().isoformat()
ROLE = {"PE": "Product engineering", "PM": "Product management", "DATA": "Data & analytics", "FS": "Full-stack", "FO": "Founder's Office"}

full = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
rows = []
for line in full.split("## Projects")[1].split("## Skills")[0].splitlines():
    if line.startswith("| ") and not line.startswith("| Project"):
        c = [x.strip() for x in line.strip("|").split("|")]
        rows.append({"name": c[0], "desc": c[1], "roles": c[2], "stack": c[3], "urls": re.findall(r"https?://[^\s·]+", c[4])})


def role_names(r):
    return [ROLE[x.strip()] for x in r["roles"].split(",") if x.strip() in ROLE]


ld = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "ProfilePage", "@id": SITE + "#page", "url": SITE, "name": "Vedant Pawar — Portfolio", "dateModified": TODAY, "mainEntity": {"@id": SITE + "#person"}},
        {
            "@type": "Person", "@id": SITE + "#person", "name": "Vedant Pawar",
            "jobTitle": "Product-minded Software Engineer",
            "description": "Product-minded software engineer who scopes, designs, builds, ships and measures products end to end. Open to product engineering, product management, data & analytics, full-stack and Founder's Office roles.",
            "url": SITE, "image": SITE + "assets/me.jpg", "email": "mailto:hello.vedantp@gmail.com",
            "address": {"@type": "PostalAddress", "addressLocality": "Mumbai", "addressCountry": "IN"},
            "worksFor": {"@type": "Organization", "name": "Tekkers AI"},
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "V.E.S. Institute of Technology, Mumbai"},
            "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "B.E. Computer Engineering (CGPA 9.56)"},
            "seeks": [{"@type": "Demand", "name": r} for r in ROLE.values()],
            "award": ["DevIgnite Hackathon — 1st place (2024)", "Datazen Datathon — 1st place (2024)", "J.P. Morgan Code for Good — top 6 from VESIT (2024)"],
            "knowsAbout": ["Product management", "Product engineering", "Full-stack development", "Product analytics", "PostHog", "Python", "TypeScript", "React", "Next.js", "Node.js", "Flutter", "FastAPI", "Firebase", "SQL", "Snowflake", "Power BI", "Tableau", "LLM applications", "Voice AI", "Figma"],
            "sameAs": ["https://github.com/codderv006", "https://www.linkedin.com/in/vedant-pawar/", "https://x.com/Vedant52455825", "https://www.instagram.com/vedant.time/", "https://www.kaggle.com/vedantxtime", "https://codepen.io/codderv006", "https://vedantxdesign.my.canva.site/"],
        },
        {
            "@type": "ItemList", "@id": SITE + "#projects", "name": "Projects by Vedant Pawar",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": {
                    "@type": "CreativeWork", "name": r["name"], "description": r["desc"],
                    "keywords": ", ".join(role_names(r) + [r["stack"]]),
                    "creator": {"@id": SITE + "#person"}, **({"url": r["urls"][0]} if r["urls"] else {})}}
                for i, r in enumerate(rows)],
        },
    ],
}


def li(r):
    roles = ", ".join(role_names(r))
    links = " ".join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in r["urls"])
    return f'<li><b>{html.escape(r["name"])}</b>: {html.escape(r["desc"])}. Stack: {html.escape(r["stack"])}.' + (f" Shows: {html.escape(roles)}." if roles else "") + (" " + links if links else "") + "</li>"


noscript = ('<noscript>\n  <section id="projects-static" style="padding:40px var(--gut,20px);max-width:1120px;margin:0 auto">\n    <h2>Projects</h2>\n    <ul>'
            + "".join(li(r) for r in rows)
            + '</ul>\n    <p>Full profile in plain text: <a href="/llms-full.txt">/llms-full.txt</a></p>\n  </section>\n</noscript>')

p = ROOT / "index.html"
s = p.read_text(encoding="utf-8")
s = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
s = re.sub(r'\s*<noscript>\s*<section id="projects-static".*?</noscript>', "", s, flags=re.S)
s = s.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
marker = '<div class="showmore" id="showmore">'
i = s.index(marker)
j = s.index("</div>", i) + 6
s = s[:j] + "\n    " + noscript + s[j:]
p.write_text(s, encoding="utf-8", newline="\n")

(ROOT / "sitemap.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE}</loc><lastmod>{TODAY}</lastmod></url>
  <url><loc>{SITE}llms.txt</loc><lastmod>{TODAY}</lastmod></url>
  <url><loc>{SITE}llms-full.txt</loc><lastmod>{TODAY}</lastmod></url>
</urlset>
""", encoding="utf-8")
print("projects:", len(rows), "| no-JS blocks:", s.count("projects-static"), "| json-ld ok:", bool(json.loads(json.dumps(ld))))
