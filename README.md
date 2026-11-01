# Missions Archive

The case file behind [Sacred Missions Map](https://apps.sonor.co.uk/sonor-sacred-missions-map/): reports, Paul Sinclair's Truth Proof cases, every Mysterious Universe episode and its show notes, people, places, themes and a log — any of them linkable to any other.

Live: https://apps.sonor.co.uk/sonor-missions-archive/

- `index.html` — the app (all lists, fields, colours and relations come from the database)
- `seed/` — lookup / type / case data, loaded with `python3 tools/arc_load.py seed`
- `tools/mu_scrape.py` — Mysterious Universe archive scraper; `python3 tools/arc_load.py episodes` loads it
- `research/mu/` — the scraped episode archive
