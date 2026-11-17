#!/usr/bin/env python3
"""Bouwt de statische krant uit editions/*.json naar public/.

Alleen standaardbibliotheek. Gebruik: python3 build.py
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
EDITIONS = ROOT / "editions"
PUBLIC = ROOT / "public"
TITLE = "Het Advertentie Dagblad"

MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december"]
DAYS = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]


def e(s):
    return html.escape(str(s), quote=True)


def nl_date(iso):
    d = date.fromisoformat(iso)
    return f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]} {d.year}"


def sources(srcs):
    links = " · ".join(
        f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>' for s in srcs
    )
    return f'<p class="src">Bron: {links}</p>' if links else ""


def render_edition(ed, number, prev_date, next_date, prefix):
    lead = ed["lead"]
    lead_html = f"""
    <article class="lead">
      <p class="kicker">{e(lead["kicker"])}</p>
      <h2>{e(lead["title"])}</h2>
      <div class="lead-body">
        {''.join(f'<p>{e(p)}</p>' for p in lead["summary"])}
        <aside class="why"><strong>Wat betekent dit voor ons?</strong> {e(lead["why"])}</aside>
        {sources(lead.get("sources", []))}
      </div>
    </article>"""

    sections_html = ""
    for sec in ed.get("sections", []):
        items = "".join(
            f"""
        <article class="item">
          <span class="impact impact-{e(it.get('impact', 'laag'))}">{e(it.get('impact', 'laag'))} impact</span>
          <h4>{e(it["title"])}</h4>
          <p>{e(it["summary"])}</p>
          {sources(it.get("sources", []))}
        </article>"""
            for it in sec["items"]
        )
        sections_html += f"""
      <section class="section">
        <h3>{e(sec["name"])}</h3>{items}
      </section>"""

    briefs = "".join(
        f'<li><a href="{e(b["url"])}" target="_blank" rel="noopener">{e(b["title"])}</a> <span>{e(b["source"])}</span></li>'
        for b in ed.get("briefs", [])
    )
    actions = "".join(f"<li>{e(a)}</li>" for a in ed.get("actions", []))

    nav = []
    if prev_date:
        nav.append(f'<a href="{prefix}editie/{prev_date}.html">← Vorige editie</a>')
    nav.append(f'<a href="{prefix}archief/">Archief</a>')
    if next_date:
        nav.append(f'<a href="{prefix}editie/{next_date}.html">Volgende editie →</a>')

    sidebar = ""
    if actions:
        sidebar += f'<div class="box actions"><h3>Actiepunten</h3><ol>{actions}</ol></div>'
    if briefs:
        sidebar += f'<div class="box briefs"><h3>Kort nieuws</h3><ul>{briefs}</ul></div>'

    body = f"""
  <div class="layout">
    <main>{lead_html}
      <div class="sections">{sections_html}
      </div>
    </main>
    <aside class="sidebar">{sidebar}</aside>
  </div>
  <nav class="edition-nav">{' '.join(nav)}</nav>"""
    return page(f"{TITLE} · {nl_date(ed['date'])}", nl_date(ed["date"]), number, body, prefix)


def page(title, datestr, number, body, prefix):
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Inter:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<div class="paper">
  <header class="masthead">
    <div class="meta-row"><span>{e(datestr)}</span><span>Google Ads · Social · Search · Privacy</span><span>{e(number)}</span></div>
    <h1><a href="{prefix}">{TITLE}</a></h1>
    <p class="tagline">Elke ochtend het belangrijkste advertentienieuws, samengevat voor het team</p>
  </header>
  {body}
  <footer>Automatisch samengesteld uit Google, Meta, TikTok, LinkedIn, Microsoft, Search Engine Land, Search Engine Roundtable, PPC Land, Social Media Today, Emerce, Adformatie, Frankwatching en meer. Controleer de bron voordat je handelt.</footer>
</div>
</body>
</html>
"""


def main():
    eds = sorted(
        (json.loads(p.read_text(encoding="utf-8")) for p in EDITIONS.glob("*.json")),
        key=lambda x: x["date"],
    )
    if not eds:
        raise SystemExit("Geen edities gevonden in editions/")
    (PUBLIC / "editie").mkdir(parents=True, exist_ok=True)
    (PUBLIC / "archief").mkdir(parents=True, exist_ok=True)

    for i, ed in enumerate(eds):
        prev_d = eds[i - 1]["date"] if i > 0 else None
        next_d = eds[i + 1]["date"] if i + 1 < len(eds) else None
        num = f"Editie {i + 1}"
        (PUBLIC / "editie" / f"{ed['date']}.html").write_text(
            render_edition(ed, num, prev_d, next_d, "../"), encoding="utf-8")
        if i == len(eds) - 1:
            (PUBLIC / "index.html").write_text(
                render_edition(ed, num, prev_d, None, ""), encoding="utf-8")

    rows = "".join(
        f'<li><a href="../editie/{ed["date"]}.html"><span class="adate">{e(nl_date(ed["date"]))}</span>'
        f'<span class="atitle">{e(ed["lead"]["title"])}</span></a></li>'
        for ed in reversed(eds)
    )
    archive = f'<main class="archive"><h2>Archief</h2><ul>{rows}</ul></main>'
    (PUBLIC / "archief" / "index.html").write_text(
        page(f"{TITLE} · Archief", nl_date(eds[-1]["date"]), f"{len(eds)} edities", archive, "../"),
        encoding="utf-8")
    print(f"Gebouwd: {len(eds)} editie(s), laatste {eds[-1]['date']}")


if __name__ == "__main__":
    main()
