from __future__ import annotations
import asyncio
from .provider import CFBD
from .features import build,vector
from .engine import estimate,simulate
from .config import settings
class Pipeline:
 def __init__(self):self.p=CFBD()
 async def run(self,a,b,year):
  ba,bb,g=await asyncio.gather(self.p.team(a,year),self.p.team(b,year),self.p.matchup(a,b,year))
  ta,tb=build(a,ba),build(b,bb);home=0;neutral=0;weather=None;wp=0
  if g:
   neutral=int(bool(g.get("neutralSite")));home=1 if g.get("homeTeam")==a and not neutral else -1 if g.get("homeTeam")==b and not neutral else 0
   weather=await self.p.game_weather(g.get("id"))
   wr=weather[0] if isinstance(weather,list) and weather else {}
   wind=wr.get("windSpeed") if isinstance(wr,dict) else None;temp=wr.get("temperature") if isinstance(wr,dict) else None
   if isinstance(wind,(int,float)):wp+=max(0,wind-12)*.6
   if isinstance(temp,(int,float)):wp+=max(0,32-temp)*.15+max(0,temp-90)*.08
  x=vector(ta,tb,home,neutral,wp);margin,total,prob,status=estimate(x)
  pred=simulate(a,b,margin,total,prob,settings.simulations)
  diffs=sorted([(k,v) for k,v in x.items() if k not in ("home_a","neutral","weather_penalty")],key=lambda z:abs(z[1]),reverse=True)[:7]
  return {"version":"1.0","matchup":{"team_a":a,"team_b":b,"season":year,"game":g},
   "prediction":pred,"model_status":status,"confidence":{"data_pct":round(min(ta.completeness,tb.completeness),1)},
   "top_factors":[{"factor":k,"team_a_edge":round(v,2)} for k,v in diffs],
   "weather":weather,"market_raw":{"team_a":ba.get("lines"),"team_b":bb.get("lines")},
   "features":{"team_a":ta.__dict__,"team_b":tb.__dict__,"matchup":x},
   "notes":["Injuries are not fabricated: no verified injury feed is assumed.","If a trained model file exists, it is used automatically; otherwise the transparent fallback model is used."]}
