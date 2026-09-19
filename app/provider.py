from __future__ import annotations
import asyncio,httpx
from .config import settings
class CFBD:
    def __init__(self):self.h={"Authorization":f"Bearer {settings.api_key}"}
    async def get(self,path,**params):
        if not settings.api_key:raise RuntimeError("CFBD_API_KEY missing")
        params={k:v for k,v in params.items() if v is not None}
        async with httpx.AsyncClient(timeout=45) as c:
            r=await c.get(settings.base_url+path,params=params,headers=self.h)
            r.raise_for_status();return r.json()
    async def safe(self,path,**p):
        try:return await self.get(path,**p)
        except Exception as e:return {"_error":str(e)}
    async def team(self,team,year):
        calls=[
          self.safe("/games",year=year,team=team,seasonType="regular"),
          self.safe("/stats/season/advanced",year=year,team=team),
          self.safe("/ratings/core",year=year,team=team),
          self.safe("/ratings/elo",year=year,team=team),
          self.safe("/ratings/srs/expanded",year=year,team=team,classification="fbs"),
          self.safe("/roster",year=year,team=team),
          self.safe("/talent",year=year,team=team),
          self.safe("/player/returning",year=year,team=team),
          self.safe("/player/portal",year=year,team=team),
          self.safe("/lines",year=year,team=team)]
        vals=await asyncio.gather(*calls)
        return dict(zip(["games","advanced","core","elo","srs","roster","talent","returning","portal","lines"],vals))
    async def matchup(self,a,b,year):
        gs=await self.safe("/games",year=year,team=a,seasonType="regular")
        if not isinstance(gs,list):return None
        matches=[g for g in gs if b.casefold() in (str(g.get("homeTeam","")).casefold(),str(g.get("awayTeam","")).casefold())]
        future=[g for g in matches if g.get("homePoints") is None]
        return (future or matches or [None])[0]
    async def game_weather(self,game_id):
        return await self.safe("/games/weather",gameId=game_id) if game_id else None
    async def advanced_box(self,game_id):
        return await self.safe("/game/box/advanced",id=game_id)
