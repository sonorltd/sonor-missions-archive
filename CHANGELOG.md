# Changelog

## v1.3.0 — 2026-10-30
- **Category groups**: `arc_categories` rows of kind `case-group` (UFO · Ghosts · Cryptids · Strange · Ritual) with their member categories, and each case category's `metadata.group`. New **Group** filter on Cases (from `arc_types.metadata.filters`). Sacred Missions Map builds one tab per group from this.
- **Upper Tywi & Llyn Brianne** place entity linking the 14 public cases within 12 mi of the dam; five Welsh wolf-like cases added and linked to *Werewolves, dogmen & wolf-like humanoids*. The private Llyn Brianne account stays unlinked (link rows are anon-readable).
- Rule-based links (2026-10-30): witch trials, Hellfire Clubs, Crowley, 1963 black-magic scare, North Wales desecrations 1987–91, Pendle, New Forest, big cats, time slips, black dogs, werewolves, fairies, phantom aircraft, crop circles, 1909 airships.

## v1.2.0 — 2026-10-29
- Full Mysterious Universe pass over all 1,307 episodes: 90 new cases MU covered, 225 case↔episode links (each with only the show-notes text about that case and its evidence level), 51 new people / themes / events linked to their episodes, topic labels on 57 bare-titled episodes (`arc_episodes.metadata.topic`, shown after the title).
- Ritual research: 36 cases deepened (fuller accounts, sources, checked pins), 59 new occult & ritual cases (two marked `status: duplicate` and linked to the case they repeat).

## v1.1.0 — 2026-10-29
- Filters: decade, status, grouped tags (from `arc_tags.grp`, with counts), and "links to" filters (cases with / without Mysterious Universe episodes or people / places / themes) — all declared in `arc_types.metadata.filters`.
- New category **Occult & ritual sites** (49 cases) and the Love Street lead.

## v1.0.0 — 2026-10-29
First release. Data-driven archive on Sonor Supabase (`arc_*`): cases from Sacred Missions Map and Paul Sinclair's Truth Proof, the full Mysterious Universe back catalogue with show notes, people / places / themes, a log, and anything-to-anything links. Search (full text on show notes), filters, edit forms and link picker all built from the `arc_types` rows.
