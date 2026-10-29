import json,re,collections,time
CANON=[("avebury","avebury"),("ben macdui","EXISTING:am-fear-liath-mor-ben-macdui-1891"),("big grey man","EXISTING:am-fear-liath-mor-ben-macdui-1891"),("findhorn","findhorn"),("gef the talking","gef"),
 ("hairy hands","hairy-hands"),("man-monkey","man-monkey"),("luminous owls","norfolk-owls"),("rougham","rougham"),("silbury hill crop","silbury-2009"),("stonehenge","stonehenge")]
cases=[x for x in json.load(open('case_index2.json'))]; cid={c['id'] for c in cases}
def key(c):
  t=c['title'].lower()
  for k,v in CANON:
    if k in t: return v
  return re.sub(r'[^a-z0-9]+','-',t).strip('-')[:40].strip('-')
groups=collections.OrderedDict(); links=[]; themes=[]
for i in range(1,5):
  d=json.load(open(f'mu_part{i}.json'))
  for c in d['new_cases']:
    eps=[{'episode_id':c['episode_id'],'excerpt':c.get('excerpt',''),'evidence':c.get('evidence','notes')}]+[dict(e) for e in (c.get('extra_episodes') or c.get('also_episodes') or [])]
    groups.setdefault(key(c),[]).append((c,eps))
  links+=d['links']; themes+=d['themes']
new=[];L=[]
def conf(ev): return 0.5 if ev=='link-title' else 0.75 if ev in ('web','episode-page') else 0.85
for k,items in groups.items():
  if k.startswith('EXISTING:'):
    cidx=k.split(':',1)[1]
    for c,eps in items:
      for e in eps: L.append(dict(a_type='case',a_id=cidx,b_type='episode',b_id=e['episode_id'],relation='covered_in',excerpt=e.get('excerpt',''),matched_by='claude',confidence=conf(e.get('evidence')),note='evidence: '+str(e.get('evidence','notes'))))
    continue
  best=max((c for c,_ in items),key=lambda c:len(c.get('desc','')))
  src=[];seen=set()
  for c,_ in items:
    for s in c.get('sources',[]):
      if s.get('url') and s['url'] not in seen: seen.add(s['url']); src.append({'name':s['name'],'url':s['url']})
  tags=sorted({t for c,_ in items for t in c.get('tags',[])})
  y=re.match(r'(\d{3,4})',best.get('date') or '')
  idv=k+('-'+y.group(1) if y and not k.endswith(y.group(1)) else '')
  while idv in cid: idv+='-mu'
  case=dict(id=idv,title=best['title'],cat=best.get('cat','other'),date=best.get('date',''),place=best['place'],lat=float(best['lat']),lon=float(best['lon']),desc=best['desc'],tags=tags,sources=src)
  new.append(case)
  for c,eps in items:
    for e in eps: L.append(dict(a_type='case',a_id=idv,b_type='episode',b_id=e['episode_id'],relation='covered_in',excerpt=e.get('excerpt',''),matched_by='claude',confidence=conf(e.get('evidence')),note='evidence: '+str(e.get('evidence','notes'))))
for l in links:
  assert l['case_id'] in cid, l['case_id']
  L.append(dict(a_type='case',a_id=l['case_id'],b_type='episode',b_id=l['episode_id'],relation='covered_in',excerpt=l.get('excerpt',''),matched_by='claude',confidence=conf(l.get('evidence')),note='evidence: '+str(l.get('evidence','notes'))+((' · '+l['note']) if l.get('note') else '')))
ents={}
for t in themes:
  tid=re.sub(r'[^a-z0-9]+','-',t['theme'].lower()).strip('-')
  ents[tid]=t['theme']
  L.append(dict(a_type='entity',a_id=tid,b_type='episode',b_id=t['episode_id'],relation='covered_in',excerpt=t.get('excerpt',''),matched_by='claude',confidence=conf(t.get('evidence')),note=('evidence: '+t['evidence']) if t.get('evidence') else ''))
# Paul Sinclair house case -> entity
for c in new:
  if 'Sinclair' in c['title']: L.append(dict(a_type='case',a_id=c['id'],b_type='entity',b_id='paul-sinclair',relation='related',excerpt='',matched_by='claude',confidence=1,note=''))
  if 'Green Stone' in c['title'] or 'Ranton' in c['title']: pass
gs=[c['id'] for c in new if 'Green Stone' in c['title']]
if len(gs)==2: L.append(dict(a_type='case',a_id=gs[0],b_type='case',b_id=gs[1],relation='related',excerpt='',matched_by='claude',confidence=1,note='The Green Stone affair'))
# dedupe links
seen=set();LL=[]
for l in L:
  k=(l['a_type'],l['a_id'],l['b_type'],l['b_id'],l['relation'])
  if k in seen: continue
  seen.add(k); LL.append(l)
json.dump({'new':new,'links':LL,'entities':ents},open('mu_merged.json','w'),ensure_ascii=False,indent=1)
print(len(new),'new cases',len(LL),'links',len(ents),'theme ids'); print(sorted(ents)[:80])
