#!/usr/bin/env python3
"""Bouwt de statische krant uit editions/*.json naar public/.

Alleen standaardbibliotheek. Gebruik: python3 build.py
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
EDITIONS = ROOT / "editions"
PUBLIC = ROOT / "public"
TITLE = "Advertising Dagblad"
LOGO_SVG = (PUBLIC / "img" / "techonomy-logo.svg").read_text(encoding="utf-8")

MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december"]
DAYS = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
IMPACT_ORDER = {"hoog": 0, "middel": 1, "laag": 2}


def e(s):
    return html.escape(str(s), quote=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def nl_date(iso):
    d = date.fromisoformat(iso)
    return f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]} {d.year}"


def sources(srcs):
    if not srcs:
        return ""
    links = "".join(
        f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])} ↗</a>' for s in srcs
    )
    return f'<div class="src">{links}</div>'


def impact_chip(level):
    level = level if level in IMPACT_ORDER else "laag"
    return f'<span class="chip chip-{level}">{level} impact</span>'


def render_edition(ed, number, prev_date, next_date, prefix):
    lead = ed["lead"]
    sections = ed.get("sections", [])
    all_items = [it for sec in sections for it in sec["items"]]
    n_high = sum(1 for it in all_items if it.get("impact") == "hoog")

    # Snelnavigatie per rubriek
    toc = "".join(
        f'<a href="#{slug(sec["name"])}">{e(sec["name"])} <span>{len(sec["items"])}</span></a>'
        for sec in sections
    )

    lead_html = f"""
      <article class="card lead">
        <p class="kicker">Hoofdartikel · {e(lead["kicker"])}</p>
        <h2>{e(lead["title"])}</h2>
        {''.join(f'<p>{e(p)}</p>' for p in lead["summary"])}
        <div class="why"><h3>Wat betekent dit voor ons?</h3><p>{e(lead["why"])}</p></div>
        {sources(lead.get("sources", []))}
      </article>"""

    sections_html = ""
    for sec in sections:
        items = sorted(sec["items"], key=lambda it: IMPACT_ORDER.get(it.get("impact"), 2))
        cards = "".join(
            f"""
          <article class="card item item-{e(it.get('impact', 'laag'))}">
            {impact_chip(it.get("impact", "laag"))}
            <h4>{e(it["title"])}</h4>
            <p>{e(it["summary"])}</p>
            {sources(it.get("sources", []))}
          </article>"""
            for it in items
        )
        sections_html += f"""
      <section class="section" id="{slug(sec["name"])}">
        <h3 class="section-title">{e(sec["name"])}</h3>
        <div class="grid">{cards}
        </div>
      </section>"""

    actions = "".join(f"<li>{e(a)}</li>" for a in ed.get("actions", []))
    briefs = "".join(
        f'<li><a href="{e(b["url"])}" target="_blank" rel="noopener">{e(b["title"])}</a><span>{e(b["source"])}</span></li>'
        for b in ed.get("briefs", [])
    )

    nav = []
    if prev_date:
        nav.append(f'<a href="{prefix}editie/{prev_date}">← Vorige editie</a>')
    nav.append(f'<a href="{prefix}archief/">Archief</a>')
    if next_date:
        nav.append(f'<a href="{prefix}editie/{next_date}">Volgende editie →</a>')

    top = ""
    if actions:
        top += f'<aside class="card actions"><h3>Actiepunten vandaag</h3><ol>{actions}</ol></aside>'

    body = f"""
    <div class="summary-bar">
      <span><strong>{len(all_items)}</strong> berichten</span>
      <span><strong>{n_high}</strong> met hoge impact</span>
      <nav class="toc">{toc}</nav>
    </div>
    <div class="top">{lead_html}{top}
    </div>
    {sections_html}
    {f'<section class="section"><h3 class="section-title">Kort nieuws</h3><ul class="card briefs">{briefs}</ul></section>' if briefs else ''}
    <nav class="edition-nav">{''.join(nav)}</nav>"""
    return page(f"{TITLE} · {nl_date(ed['date'])}", nl_date(ed["date"]), number, body, prefix)


def page(title, datestr, number, body, prefix):
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<header class="masthead">
  <div class="wrap">
    <div class="brand-row">
      <a class="logo" href="{prefix}" aria-label="Techonomy">{LOGO_SVG}</a>
      <span class="meta">{e(number)}</span>
    </div>
    <h1><a href="{prefix}">{TITLE}</a></h1>
    <p class="date">{e(datestr)}</p>
    <p class="tagline">Het belangrijkste nieuws over Google Ads, social advertising, search en privacy, elke ochtend samengevat.</p>
  </div>
</header>
<main class="wrap">
  {body}
</main>
<footer>
  <div class="wrap">Automatisch samengesteld uit officiële platformblogs, Search Engine Land, Search Engine Roundtable, PPC Land, Social Media Today, Emerce, Adformatie en meer. Controleer altijd de bron voordat je handelt.</div>
</footer>
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
        f'<li><a href="../editie/{ed["date"]}"><span class="adate">{e(nl_date(ed["date"]))}</span>'
        f'<span class="atitle">{e(ed["lead"]["title"])}</span></a></li>'
        for ed in reversed(eds)
    )
    archive = f'<section class="section"><h3 class="section-title">Archief</h3><ul class="card archive">{rows}</ul></section>'
    (PUBLIC / "archief" / "index.html").write_text(
        page(f"{TITLE} · Archief", nl_date(eds[-1]["date"]), f"{len(eds)} edities", archive, "../"),
        encoding="utf-8")
    print(f"Gebouwd: {len(eds)} editie(s), laatste {eds[-1]['date']}")


if __name__ == "__main__":
    main()
