from __future__ import annotations
from dataclasses import dataclass
import math
@dataclass
class Team:
 team:str; offense:float=50; defense:float=50; pass_off:float=50; rush_off:float=50
 pass_def:float=50; rush_def:float=50; success_off:float=50; success_def:float=50
 explosive_off:float=50; explosive_def:float=50; havoc:float=50; havoc_allowed:float=50
 core:float=50; elo:float=50; srs:float=50; talent:float=50; recent:float=50
 returning:float=50; portal:float=50; completeness:float=0
def flat(x,p=""):
 o={}
 if isinstance(x,dict):
  for k,v in x.items():
   q=(p+"."+str(k) if p else str(k)).lower()
   if isinstance(v,(dict,list)):o.update(flat(v,q))
   elif isinstance(v,(int,float)) and not isinstance(v,bool):o[q]=float(v)
 elif isinstance(x,list):
  for v in x[:10]:o.update(flat(v,p))
 return o
def get(n,*tokens,exclude=()):
 for k,v in n.items():
  if all(t in k for t in tokens) and not any(t in k for t in exclude):return v
def sc(v,kind="rate",inv=False):
 if v is None:return 50
 if kind=="ppa":s=50+30*math.tanh(v/.35)
 elif kind=="elo":s=50+25*math.tanh((v-1500)/350)
 elif kind=="rating":s=50+25*math.tanh(v/15)
 elif 0<=v<=1:s=v*100
 elif 0<=v<=100:s=v
 else:s=50+15*math.tanh(v/4)
 s=max(0,min(100,s));return 100-s if inv else s
def build(team,b):
 n=flat(b.get("advanced",{}));t=Team(team)
 t.offense=sc(get(n,"offense","ppa") or get(n,"offense","epa"),"ppa")
 t.defense=sc(get(n,"defense","ppa") or get(n,"defense","epa"),"ppa",True)
 t.pass_off=sc(get(n,"offense","passing","ppa") or get(n,"passing","ppa",exclude=("defense",)),"ppa")
 t.rush_off=sc(get(n,"offense","rushing","ppa") or get(n,"rushing","ppa",exclude=("defense",)),"ppa")
 t.pass_def=sc(get(n,"defense","passing","ppa"),"ppa",True);t.rush_def=sc(get(n,"defense","rushing","ppa"),"ppa",True)
 t.success_off=sc(get(n,"offense","success"));t.success_def=sc(get(n,"defense","success"),inv=True)
 t.explosive_off=sc(get(n,"offense","explos"));t.explosive_def=sc(get(n,"defense","explos"),inv=True)
 t.havoc=sc(get(n,"defense","havoc"));t.havoc_allowed=sc(get(n,"offense","havoc"),inv=True)
 core=b.get("core");row=core[0] if isinstance(core,list) and core else {}
 if isinstance(row,dict):t.core=sc(row.get("overall"),"rating")
 elo=b.get("elo");row=elo[-1] if isinstance(elo,list) and elo else {}
 if isinstance(row,dict):t.elo=sc(row.get("elo"),"elo")
 srs=b.get("srs");row=srs[0] if isinstance(srs,list) and srs else {}
 if isinstance(row,dict):t.srs=sc(row.get("rating"),"rating")
 games=b.get("games");ms=[]
 if isinstance(games,list):
  for g in games:
   hp,ap=g.get("homePoints"),g.get("awayPoints")
   if isinstance(hp,(int,float)) and isinstance(ap,(int,float)):
    m=hp-ap if g.get("homeTeam")==team else ap-hp if g.get("awayTeam")==team else None
    if m is not None:ms.append((g.get("week",0),m))
 if ms:
  ms=sorted(ms)[-5:];t.recent=max(0,min(100,50+sum(m for _,m in ms)/len(ms)))
 ok=sum(not(isinstance(v,dict) and "_error" in v) for v in b.values());t.completeness=100*ok/max(1,len(b))
 return t
def vector(a,b,home=0,neutral=0,weather_penalty=0):
 return {"off_edge":a.offense-b.offense,"def_edge":a.defense-b.defense,
 "pass_match":a.pass_off-b.pass_def,"opp_pass_match":b.pass_off-a.pass_def,
 "rush_match":a.rush_off-b.rush_def,"opp_rush_match":b.rush_off-a.rush_def,
 "success_match":a.success_off-b.success_def,"opp_success_match":b.success_off-a.success_def,
 "explosive_match":a.explosive_off-b.explosive_def,"opp_explosive_match":b.explosive_off-a.explosive_def,
 "havoc_match":a.havoc-b.havoc_allowed,"opp_havoc_match":b.havoc-a.havoc_allowed,
 "core_edge":a.core-b.core,"elo_edge":a.elo-b.elo,"srs_edge":a.srs-b.srs,
 "talent_edge":a.talent-b.talent,"recent_edge":a.recent-b.recent,
 "home_a":home,"neutral":neutral,"weather_penalty":weather_penalty}
