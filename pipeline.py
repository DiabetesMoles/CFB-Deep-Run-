from __future__ import annotations
import asyncio
from .provider import CFBD
from .features import build,vector
from .engine import estimate,simulate
from .config import settings
LABELS={"off_edge":"Overall offense","def_edge":"Overall defense","pass_match":"Passing matchup","opp_pass_match":"Opponent passing matchup","rush_match":"Rushing matchup","opp_rush_match":"Opponent rushing matchup","success_match":"Down-to-down efficiency","opp_success_match":"Opponent efficiency","explosive_match":"Explosive-play matchup","opp_explosive_match":"Opponent explosive plays","havoc_match":"Defensive disruption","opp_havoc_match":"Opponent disruption","core_edge":"Overall team rating","elo_edge":"Elo rating","srs_edge":"Strength rating","talent_edge":"Roster talent","recent_edge":"Recent form"}
def explain(k,v,a,b):
 bside=k.startswith("opp_");fav=b if (v>0 and bside) or (v<0 and not bside) else a;s=abs(float(v));degree="Strong" if s>=20 else "Moderate" if s>=10 else "Slight"
 return {"title":LABELS.get(k,k.replace("_"," ").title()),"favored":fav,"summary":f"{degree} advantage for {fav}"}
class Pipeline:
 def __init__(self):self.p=CFBD()
 async def run(self,a,b,year):
  ba,bb,g=await asyncio.gather(self.p.team(a,year),self.p.team(b,year),self.p.matchup(a,b,year));ta,tb=build(a,ba),build(b,bb);home=0;neutral=0;weather=None;wp=0
  if g:
   neutral=int(bool(g.get("neutralSite")));home=1 if g.get("homeTeam")==a and not neutral else -1 if g.get("homeTeam")==b and not neutral else 0;weather=await self.p.game_weather(g.get("id"));wr=weather[0] if isinstance(weather,list) and weather else {};wind=wr.get("windSpeed") if isinstance(wr,dict) else None;temp=wr.get("temperature") if isinstance(wr,dict) else None
   if isinstance(wind,(int,float)):wp+=max(0,wind-12)*.6
   if isinstance(temp,(int,float)):wp+=max(0,32-temp)*.15+max(0,temp-90)*.08
  x=vector(ta,tb,home,neutral,wp);margin,total,prob,status=estimate(x,ta,tb);pred=simulate(a,b,margin,total,prob,settings.simulations)
  diffs=sorted([(k,v) for k,v in x.items() if k not in ("home_a","neutral","weather_penalty")],key=lambda z:abs(z[1]),reverse=True)[:5];coverage=round(min(ta.completeness,tb.completeness),1);confidence="High" if coverage>=85 else "Medium" if coverage>=65 else "Low"
  return {"version":"2.0","matchup":{"team_a":a,"team_b":b,"season":year,"game":g},"prediction":pred,"model_status":status,"confidence":{"data_pct":coverage,"label":confidence},"top_factors":[explain(k,v,a,b) for k,v in diffs],"weather":weather,"market_raw":{"team_a":ba.get("lines"),"team_b":bb.get("lines")}}
