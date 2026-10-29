#!/usr/bin/env python3
"""Mysterious Universe episode archive scraper (stdlib only, resumable).
Crawls mysteriousuniverse.org podcast pages (listing pages + prev/next/related links on each
episode page) and writes research/mu/episodes.jsonl: one line per episode with title, url, date,
season.episode, plus flag, show-notes text and links. Usage: python3 tools/mu_scrape.py [seconds]"""
import re, html, json, sys, time, os, urllib.request
BASE = "https://mysteriousuniverse.org"
OUT = os.path.join(os.path.dirname(__file__), "..", "research", "mu")
EPS = os.path.join(OUT, "episodes.jsonl"); QUEUE = os.path.join(OUT, "queue.json")
POD = re.compile(r'href="((?:https?://mysteriousuniverse\.org)?/\d{4}/\d{2}/[^"#?]*podcast[^"#?]*)"', re.I)
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 160
t0 = time.time()
def get(u):
    r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (personal archive)"})
    return urllib.request.urlopen(r, timeout=25).read().decode("utf-8", "ignore")
def norm(u):
    u = u if u.startswith("http") else BASE + u
    u = u.replace("http://", "https://")
    return u if u.endswith("/") else u + "/"
def txt(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
os.makedirs(OUT, exist_ok=True)
done = set()
if os.path.exists(EPS):
    for l in open(EPS): done.add(json.loads(l)["url"])
st = json.load(open(QUEUE)) if os.path.exists(QUEUE) else {"queue": [], "seen": [], "list_pages": 0}
queue, seen = st["queue"], set(st["seen"]) | done
def add(links):
    for m in links:
        u = norm(m)
        if u not in seen: seen.add(u); queue.append(u)
# phase 1: listing pages (tag + category), stop a source after 3 pages with nothing new
for src in ("/tag/podcast?page=%d", "/category/podcasts?page=%d", "/collections/mu-podcasts-extended-editions?page=%d"):
    key = "lp_" + src; p = st.get(key, 1); dry = 0
    while dry < 3 and p < 400 and time.time() - t0 < budget * 0.4:
        try: h = get(BASE + src % p)
        except Exception: break
        n = len(queue); add(POD.findall(h)); dry = dry + 1 if len(queue) == n else 0; p += 1
    st[key] = p
# phase 2: episode pages
with open(EPS, "a") as f:
    while queue and time.time() - t0 < budget:
        u = queue.pop(0)
        if u in done: continue
        try: h = get(u)
        except Exception as e:
            print("ERR", u, e); continue
        add(POD.findall(h))
        title = txt((re.search(r'<meta property="og:title" content="([^"]+)"', h) or [None, ""])[1])
        a = h.find('class="article-detail-left"'); b = h.find('class="small-article-section"', a)
        body = h[a:b] if a > 0 else ""
        notes = txt(re.sub(r"(?s)<style.*?</style>|<script.*?</script>", " ", body))
        notes = re.sub(r"^class=\"article-detail-left\">\s*", "", notes)
        notes = re.split(r"#st-1 |Podcast Feed Get Season Feed", notes)[0].strip()
        links = []
        for m in re.finditer(r'<a [^>]*href="(http[^"]+)"[^>]*>(.*?)</a>', body, re.S):
            href = html.unescape(m.group(1)); lab = txt(m.group(2))
            if "mysteriousuniverse.org/plus" in href or "feed/podcast" in href: continue
            links.append({"text": lab, "url": href})
        date = (re.findall(r"([A-Z][a-z]{2} \d{1,2}, \d{4})", h[:a]) or [""])[0] if a > 0 else ""
        num = (re.match(r"\s*(\d+\.\d+)", title) or [None, ""])[1]
        rec = {"url": u, "title": title, "no": num, "date": date, "ym": "/".join(u.split("/")[3:5]),
               "plus": "Plus+ Extension" in notes or "plus" in u.lower().split("/")[-2],
               "notes": notes[:6000], "links": links}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); done.add(u)
st.update(queue=queue, seen=sorted(seen)); json.dump(st, open(QUEUE, "w"))
print(f"episodes: {len(done)}  queued: {len(queue)}  {time.time()-t0:.0f}s")
