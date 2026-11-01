#!/usr/bin/env python3
"""Load seed/*.json and research/mu/episodes.jsonl into the arc_* tables (Sonor Supabase, anon key read
from the workspace sonor-db.js — nothing hard-coded). Upserts, so it is safe to re-run.
Usage: python3 tools/arc_load.py [seed|episodes|links FILE|all]"""
import json, os, re, sys, urllib.request, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
db = open(os.path.join(ROOT, "..", "sonor-db.js")).read()
URL = re.search(r"SONOR_SUPABASE_URL\s*=\s*'([^']+)'", db).group(1)
# --- Supabase key (2026-11-01): service key from env / Mac Keychain first, anon key only as fallback ---
def _sonor_sb_key(fallback=""):
    import os as _os, subprocess as _sp, sys as _sys
    k = (_os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not k and _sys.platform == "darwin":
        try:
            k = _sp.run(["security", "find-generic-password", "-a", "sonor", "-s", "sonor-supabase-service", "-w"],
                        capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            k = ""
    return k or fallback
KEY = re.search(r"SONOR_SUPABASE_ANON\s*=\s*'([^']+)'", db).group(1)
KEY = _sonor_sb_key(KEY)
def up(table, rows, conflict):
    keys = sorted({k for r in rows for k in r})  # PostgREST bulk insert needs identical keys
    rows = [{k: r.get(k, {} if k in ("metadata", "value") else [] if k in ("tags", "links", "aliases") else None) for k in keys} for r in rows]
    for i in range(0, len(rows), 200):
        body = json.dumps(rows[i:i+200]).encode()
        r = urllib.request.Request(f"{URL}/rest/v1/{table}?on_conflict={conflict}", data=body, method="POST", headers={
            "apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"})
        try: urllib.request.urlopen(r, timeout=60)
        except urllib.error.HTTPError as e: print("ERR", table, e.code, e.read()[:400].decode()); raise
    print(f"{table}: {len(rows)}")
def get(path):
    r = urllib.request.Request(f"{URL}/rest/v1/{path}", headers={"apikey": KEY, "Authorization": "Bearer " + KEY})
    return json.load(urllib.request.urlopen(r, timeout=60))
def patch(table, flt, body):
    r = urllib.request.Request(f"{URL}/rest/v1/{table}?{flt}", data=json.dumps(body).encode(), method="PATCH", headers={
        "apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json", "Prefer": "return=minimal"})
    urllib.request.urlopen(r, timeout=60)
def retire_stale_links(new):
    """The anon key cannot delete (Sonor RLS law), so links a re-match no longer produces are retired:
    confidence 0 + metadata.retired. Readers filter confidence > 0. Manual links are never touched."""
    keep = {(l["a_type"], l["a_id"], l["b_type"], l["b_id"], l["relation"]) for l in new}
    old = get("arc_links?select=id,a_type,a_id,b_type,b_id,relation&matched_by=in.(keyword,claude,import)&confidence=gt.0&limit=10000")
    n = 0
    for o in old:
        if (o["a_type"], o["a_id"], o["b_type"], o["b_id"], o["relation"]) not in keep:
            patch("arc_links", "id=eq." + o["id"], {"confidence": 0, "metadata": {"retired": True}}); n += 1
    print("links retired:", n)
def seed(n): return json.load(open(os.path.join(ROOT, "seed", n + ".json")))
def load_seed():
    up("arc_categories", seed("categories"), "key"); up("arc_tags", seed("tags"), "key")
    up("arc_shows", seed("shows"), "key"); up("arc_settings", seed("settings"), "key")
    cases = seed("cases"); priv = {c["id"] for c in cases if c.get("private")}
    # private cases are hidden from the anon key (RLS), so upsert can't touch them; they are written with the service role (Claude, via MCP)
    up("arc_cases", [c for c in cases if not c.get("private")], "id")
    up("arc_sources", [s for s in seed("sources") if s["case_id"] not in priv], "case_id,name,url")
    if os.path.exists(os.path.join(ROOT, "seed", "cases_extra.json")): up("arc_cases", seed("cases_extra"), "id")
    up("arc_entities", seed("entities"), "id")
    links = seed("links"); up("arc_links", links, "a_type,a_id,b_type,b_id,relation"); retire_stale_links(links)
    if priv: print("private cases skipped (service-role only):", ", ".join(sorted(priv)))
def load_episodes(path=os.path.join(ROOT, "research", "mu", "episodes.jsonl")):
    rows, seen = [], set()
    for l in open(path):
        e = json.loads(l); slug = e["url"].rstrip("/").split("/")[-1].lower()
        if slug in seen: continue
        seen.add(slug)
        try: rel = datetime.datetime.strptime(e["date"], "%b %d, %Y").date().isoformat()
        except Exception: rel = (e["ym"].replace("/", "-") + "-01") if e.get("ym") else None
        rows.append(dict(id=slug, show="mu", no=e.get("no") or None, title=e["title"], url=e["url"], released=rel,
                         ym=e.get("ym"), plus=bool(e.get("plus")), notes=e.get("notes", ""), links=e.get("links", [])))
    up("arc_episodes", rows, "id")
def load_links(path):
    up("arc_links", json.load(open(path)), "a_type,a_id,b_type,b_id,relation")
a = sys.argv[1] if len(sys.argv) > 1 else "all"
if a in ("seed", "all"): load_seed()
if a in ("episodes", "all"): load_episodes()
if a == "links": load_links(sys.argv[2])
