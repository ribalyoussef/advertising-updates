# Het Advertentie Dagblad

Dagelijkse krant met het belangrijkste nieuws over Google Ads, social advertising, search en privacy.

- `editions/` : één JSON-bestand per editie
- `build.py` : bouwt `public/` (statische site, alleen Python-standaardbibliotheek)
- `ROUTINE.md` : instructies voor de dagelijkse Claude-run
- `SOURCES.md` : de bronnenlijst

Vercel draait `python3 build.py` en serveert `public/`; elke push naar `main` deployt.
