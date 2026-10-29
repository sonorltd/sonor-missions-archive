import json,re,collections
eps=[json.loads(l) for l in open('eps.jsonl')]
for e in eps: e['id']=e['url'].rstrip('/').split('/')[-1].lower(); e['text']=e['title']+'. '+e['notes']
cases={c['id']:c for c in json.load(open('seed/cases.json'))}
K={ # regex -> case ids (prefix match allowed with *)
r"Rendlesham|Bentwaters|Woodbridge":["rendlesham-1980"], r"Berwyn|Llandderfel":["berwyn-1974"],
r"Broad Haven|Welsh Triangle|Dyfed Triangle|Ripperston|Coombs|Stack Rock|Peter Paget|Randall Jones Pugh|The Uninvited":["broad-haven-1977","*ripperston","*coombs","*haven-fort","*stack-rock","pauline-coombs-reported-abduction-1977"],
r"Dodleston|Vertical Plane|Ken Webster|Tomas Harden":["the-dodleston-messages-1984"], r"Calvine":["calvine-1990"], r"Owlman|Mawnan":["owlman-1976"],
r"Enfield poltergeist|Enfield Poltergeist|Enfield":["enfield-1977"], r"Dechmont|Bob Taylor|Livingston":["dechmont-1979"], r"Ilkley":["ilkley-1987"],
r"Todmorden|Alan Godfrey|Zigmund Adamski|Adamski":["todmorden-1980"], r"Bonnybridge|Falkirk Triangle":["bonnybridge"], r"Cosford":["cosford-1993"],
r"Loch Ness|Nessie|Urquhart":["*loch-nes","*nessie","*urquhart","st-columba-and-the-river-ness-beast","tim-dinsdale-s-hump-film-loch-ness-1960","the-surgeon-s-photograph-hoax-1934","ness-mid-air-explosion-1996"],
r"Bodmin":["bodmin-beast"], r"Exmoor":["beast-of-exmoor-sheep-losses-1983"], r"Pluckley":["pluckley"], r"Borley":["borley"], r"Warminster":["warminster-1965"],
r"Kersey":["kersey-1957"], r"Aveley|Avis family":["aveley-1974"], r"Longdendale|Bleaklow":["longdendale"], r"Bold Street":["bold-street"],
r"Ben Macdui|Big Grey Man|Am Fear Liath":["am-fear-liath-mor-ben-macdui-1891"], r"Brentford Griffin":["brentford-griffin-1984"],
r"Spring[- ]?[Hh]eeled Jack":["spring-heeled-jack-in-everton-1904"], r"Black Shuck|Bungay|Blythburgh":["black-shuck-at-bungay-church-1577"],
r"Pendle":["pendle-hill-witches-2004"], r"Glamis":["glamis-castle-legends"], r"Edgehill":["phantom-battle-of-edgehill-1642"],
r"Mary King":["mary-king-s-close"], r"Raynham|Brown Lady":["brown-lady-of-raynham-hall-1936"], r"Ancient Ram":["ancient-ram-inn-1968"],
r"Kellas":["kellas-cat-caught-on-the-kellas-estate-1986"], r"Surrey Puma":["surrey-puma-1964"], r"Morag|Loch Morar":["morag-of-loch-morar-1887"],
r"Lakenheath":["lakenheath-bentwaters-radar-visual-case-1956"], r"Egryn|Mary Jones":["egryn-lights-and-the-mary-jones-revival-1904"], r"Silpho":["silpho-moor-saucer-with-copper-scrolls-1957"],
r"Solway|Templeton":["solway-firth-spaceman-photo-1964"], r"Cannock Chase":["hairy-giant-at-castle-ring-cannock-chase-2004","black-cat-near-cannock-chase-enterprise--2005"],
r"Leap Castle":["leap-castle-red-lady"], r"Loftus Hall":["loftus-hall-card-game-1775"], r"Charleville":["harriet-of-charleville-castle-1861"],
r"Sauchie":["sauchie-poltergeist-1960"], r"Thornton Heath":["thornton-heath-poltergeist-1938"], r"Bealings":["bealings-bells-1834"],
r"Emley Moor":["emley-moor-mast-police-sighting-1986"], r"Howden Moor|Peak District air|phantom aircraft":["howden-moor-booms-and-triangle-1997","howden-moor-phantom-aircraft-1997","ladybower-phantom-lancaster-1982"],
r"Bownessie|Windermere":["bownessie-photographs-windermere-2011"], r"Lough Ree":["lough-ree-monster-seen-by-three-priests-1960"], r"Teggie|Llyn Tegid|Bala":["teggie-the-llyn-tegid-monster"],
r"Moddey Dhoo|Peel Castle":["moddey-dhoo-of-peel-castle"], r"Barguest":["barguest-of-trollers-gill-1830"], r"Gwyllgi":["gwyllgi-hound-near-ruthin-1930"],
r"Shug Monkey":["shug-monkey-of-slough-hill-lane-1954"], r"Stronsay":["stronsay-beast-carcass-1808"], r"Anne Boleyn":["anne-boleyn-and-tower-green-1864"],
r"Mackenzie Poltergeist|Greyfriars":["mackenzie-poltergeist-greyfriars"], r"Souther Fell":["souther-fell-spectral-army-1745"], r"Marston Moor":["marston-moor-cavaliers-1932"],
r"Culloden":["culloden-battlefield"], r"Harvesters|Haverfordwest":["haverfordwest-harvest-abduction-claim-2009"], r"Hexham":["hexham-wolf-livestock-killings-1904"],
r"Hampton Court|Catherine Howard":["catherine-howard-hampton-court"], r"Tower of London|Martin Tower|Salt Tower":["phantom-bear-of-the-martin-tower-1816","salt-tower-presences-1957"],
r"Llancaiach":["llancaiach-fawr-manor-2018"], r"Kilmainham":["kilmainham-gaol"], r"Rutherglen":["rutherglen-poltergeist-2016"], r"Wincolmlee":["wincolmlee-police-patrol-ufo-1971"],
r"Lancaster Castle":["lancaster-castle"], r"Treasurer'?s House|Harry Martindale":["roman-soldiers-treasurer-s-house-1953"], r"Croxteth":["croxteth-hall-cctv-figure-2009"],
r"West Freugh":["west-freugh-radar-object-1957"], r"Belfast":["belfast-airport-ufo-investigation-1989"], r"Heathrow":["heathrow-controllers-boomerang-1992"],
r"Exercise Mainbrace|Topcliffe":["exercise-mainbrace-disc-over-raf-topclif-1952"], r"Woodchester":["deer-carcasses-at-woodchester-park-2012"], r"Tharston|scareship|airship wave":["tharston-scareship-airship-1909"],
r"Pontefract|Black Monk":["black-monk-of-pontefract"], r"Combermere":["combermere-abbey-ghost-photo-1891"], r"Samlesbury":["samlesbury-hall-white-lady"],
}
ids=list(cases)
def expand(t): return [i for i in ids if i.startswith(t[1:]) or (t[1:] in i)] if t.startswith('*') else [t]
links=[];rows=[]
for rx,targets in K.items():
  R=re.compile(r'\b('+rx+r')\b')
  tg=[i for t in targets for i in expand(t) if i in cases]
  for e in eps:
    if not R.search(e['text']): continue
    sents=[s.strip() for s in re.split(r'(?<=[.!?])\s+|\s{2,}',e['text']) if R.search(s)]
    ex=' … '.join(dict.fromkeys(sents))[:600]
    for c in tg:
      rows.append((c,e['no'],e['title'][:55],R.search(e['text']).group(0),ex[:200]))
      links.append(dict(a_type='case',a_id=c,b_type='episode',b_id=e['id'],relation='covered_in',excerpt=ex,matched_by='keyword',confidence=0.6,note='matched on "'+R.search(e['text']).group(0)+'"'))
json.dump(links,open('cand_links.json','w'),ensure_ascii=False)
seen=set()
for r in rows:
  k=(r[1],r[2],r[3]); 
  if k in seen: continue
  seen.add(k); print(r[1],'|',r[2],'|',r[3],'|',r[4][:170])
print(len(links), len(seen))
