# Dagelijkse run: Het Advertentie Dagblad

Je maakt elke ochtend de nieuwe editie van een interne krant over advertising-nieuws voor een Nederlands marketingbureau (Google Ads, Meta, TikTok, LinkedIn, Microsoft Ads, search, privacy, Nederlandse markt). Schrijf in helder, zakelijk Nederlands.

## Stappen

1. **Bepaal de datum** van vandaag (Europe/Amsterdam) en kijk in `editions/` wat de vorige editie was. Neem nieuws mee dat sinds de vorige editie verscheen (op maandag: vanaf vrijdag). Herhaal geen items die al in eerdere edities stonden, tenzij er echt nieuwe ontwikkelingen zijn.

2. **Check alle bronnen** uit `SOURCES.md`. Gebruik WebSearch (mode "extended" voor recent nieuws) en WebFetch om de pagina's zelf te lezen. Draai zoekopdrachten per bron/kanaal parallel. Minimaal:
   - Google Ads: Google Ads & Commerce blog, Google Ads Help announcements, Search Engine Land, Search Engine Roundtable, PPC Land
   - Meta: Meta for Business news, PPC Land, Social Media Today, Jon Loomer
   - TikTok / LinkedIn / Pinterest / Snapchat / Reddit: Social Media Today, officiële business-blogs
   - Microsoft Advertising blog
   - Privacy en regelgeving (DMA, consent, cookies)
   - Nederland: Emerce, Adformatie, Frankwatching, Marketingfacts, MarketingTribune, DDMA
   - Community: r/PPC, r/googleads, r/FacebookAds (alleen als er een duidelijke, breed gedeelde trend of bug is)

3. **Selecteer en weeg.** Kies het ene verhaal met de meeste impact voor adverteerders als `lead`. Geef elk item een `impact`: `hoog` (vraagt actie of verandert prestaties/meting), `middel` (relevant, nieuwe mogelijkheid), `laag` (goed om te weten). Typisch 8–16 items in totaal; liever minder en relevant dan veel ruis. Een rustige dag mag een korte editie zijn.

4. **Controleer feiten.** Alleen nieuws met een bron-URL die je echt hebt gezien. Zeg het eerlijk als bronnen elkaar tegenspreken. Gebruik officiële bronnen waar mogelijk. Verzin geen datums of cijfers.

5. **Schrijf `editions/YYYY-MM-DD.json`** volgens het schema hieronder (kijk naar een bestaande editie als voorbeeld).

6. **Test de build:** `python3 build.py`. Dit schrijft `public/` (wordt niet gecommit; Vercel bouwt zelf). Draait het niet zonder fouten, los dan je JSON op.

7. **Commit alleen het nieuwe editiebestand** en push naar `main` met bericht `Editie YYYY-MM-DD`. Vercel bouwt en deployt automatisch.

## Schema

```json
{
  "date": "YYYY-MM-DD",
  "lead": {
    "kicker": "Kanaal · Onderwerp",
    "title": "Kop",
    "summary": ["alinea 1", "alinea 2"],
    "why": "Wat betekent dit voor ons / welke actie",
    "sources": [{"name": "Bron", "url": "https://..."}]
  },
  "sections": [
    {"name": "Google Ads", "items": [
      {"title": "...", "summary": "2-3 zinnen", "impact": "hoog|middel|laag",
       "sources": [{"name": "...", "url": "..."}]}
    ]}
  ],
  "briefs": [{"title": "...", "source": "...", "url": "..."}],
  "actions": ["Concreet actiepunt voor het team"]
}
```

Vaste sectienamen (laat lege secties weg): `Google Ads`, `Meta`, `TikTok, LinkedIn & overig social`, `Microsoft Advertising`, `Search & AI`, `Privacy & regelgeving`, `Nederland`, `Uit de community`.

## Regels

- Wijzig `build.py`, `public/style.css` en eerdere edities niet.
- Geen artikelen letterlijk overnemen: vat samen in eigen woorden.
- Mislukt de build of push, stop dan en meld de fout. Push geen kapotte site.
