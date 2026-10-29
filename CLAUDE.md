# STUDIO - Missions Archive (v1.1.0)

> Repo: `sonor-missions-archive` · Pages: https://sonorltd.github.io/sonor-missions-archive/ · app_key `missions-archive`
> Type: side-project, island-ok. Personal, under STUDIO (thread 3 · Missions), created 2026-10-29. **Not Sonor Smart Homes work**: no customer data, no Sonor branding.

The cross-referenced case file behind **Sacred Missions Map**. It holds every case (UFO / cryptid / ghost / folklore reports, Paul Sinclair's Truth Proof reports, personal accounts), every Mysterious Universe episode with its show notes, people / places / themes / waves, a free log, and a generic **link table that connects anything to anything**. The archive is the master; the map is a consumer.

## Spine / platform
- Spine: n/a (exempt — personal STUDIO side-project, not a Sonor staff app; no SonorShell / kit). Theme `missions` (the map's OS-antiquity look, light + dark).
- Shared seams consumed: `sonor-db.js` (synced copy at repo root — Supabase URL + anon key + `versions.report`), `data/sonor-brand.js` (synced; marks the folder as a shared-file consumer so `sync-everything.sh` keeps `sonor-db.js` current).
- Brand overrides: own palette and fonts (IM Fell English / SC + Alegreya Sans) — deviates from GRAPHITE-FIRST on purpose, 2026-10-29, same reason as Sacred Missions Map.

## Data — Sonor Supabase, `arc_*` tables (nothing hard-coded in the app)
| Table | What |
|---|---|
| `arc_types` | Object types (case, episode, entity, log, source, site): table, title field, icon, and `metadata` = tab on/off, list columns, filters, search fields, **form fields**, child tables. The UI is built from this. |
| `arc_relations` | Relation names + inverse labels (covered in / covers, witness, investigated by, located at, same wave, …). |
| `arc_links` | **Anything ↔ anything**: `a_type,a_id → b_type,b_id`, relation, note, `excerpt` (the part of the show notes about that case only), confidence, matched_by (manual / claude / keyword / import). The anon key cannot delete — superseded auto links are retired (`confidence 0`, `metadata.retired`) and readers filter `confidence > 0`. |
| `arc_cases` | Cases. `private` rows (personal accounts) are hidden from the anon key by RLS and written by Claude with the service role only. |
| `arc_sources` | Sources per case. |
| `arc_episodes` | Podcast episodes (Mysterious Universe: 1,307, scraped 2026-10-29), show notes, show-notes links, full-text index `fts`. |
| `arc_entities` | People, places, themes, events / waves, books, organisations, creatures, media — kind from `arc_categories`. |
| `arc_log` | Free notes / investigation log. |
| `arc_categories` / `arc_tags` / `arc_shows` / `arc_settings` | Lookups: category labels + colours (light + dark), tags, shows, app settings (home, map links). |
Views: `v_arc_case_episodes`, `v_arc_counts`. RLS: anon select / insert / update, never delete.

New kind of thing? Add a row to `arc_types` (+ a table if it needs its own fields) — links and the UI pick it up. New relation? A row in `arc_relations`.

## Data flows
- **In:** `tools/mu_scrape.py` (MU archive → `research/mu/episodes.jsonl`, resumable, stdlib) → `tools/arc_load.py episodes`. `seed/*.json` → `tools/arc_load.py seed` (lookups, types, cases, sources, entities, links; upserts, safe to re-run). Cases first came from the Sacred Missions artifact database (2026-10-29).
- **Out:** Sacred Missions Map report cards show the MU episodes for a case (`mu` field on the artifact's `reports` docs + `data/reports.json` for Pages) with only the matched excerpt. The map artifact cannot fetch from Supabase (sandbox), so Claude syncs archive → map on request.

## Rules
- Show-notes excerpts on a case carry **only the text about that case** (matching sentences + the show-notes links that name it) — MU episodes cover several topics.
- Auto matches are reviewed; generic subject episodes (Loch Ness, Cannock Chase…) link to the place / theme entity, not to every sighting there.
- Personal accounts stay private (RLS) and never go into a public snapshot.

## Timeline
- v1.1.0 — 2026-10-29: decade / status / grouped-tag / links-to filters (from `arc_types.metadata.filters`); Occult & ritual sites category (49 cases).
- v1.0.0 — 2026-10-29: created. Schema, 787 cases, 927 sources, 1,307 MU episodes, 8 entities, ~430 links; UI built from `arc_types`.
