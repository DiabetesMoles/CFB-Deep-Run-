from __future__ import annotations
import numpy as np,joblib
from pathlib import Path
from .config import settings
FEATURES=["off_edge","def_edge","pass_match","opp_pass_match","rush_match","opp_rush_match",
"success_match","opp_success_match","explosive_match","opp_explosive_match","havoc_match","opp_havoc_match",
"core_edge","elo_edge","srs_edge","talent_edge","recent_edge","home_a","neutral","weather_penalty"]
FALLBACK=np.array([.10,.10,.08,-.08,.06,-.06,.05,-.05,.04,-.04,.035,-.035,.08,.05,.04,.03,.03,2.3,0,-.08])
def load():
 p=Path(settings.model_path)
 return joblib.load(p) if p.exists() else None
def estimate(x):
 X=np.array([[float(x[k]) for k in FEATURES]])
 m=load()
 if m:
  margin=float(m["margin"].predict(X)[0]);total=float(m["total"].predict(X)[0])
  prob=float(m["win"].predict_proba(X)[0,1])
  return margin,total,prob,"trained"
 margin=float(np.dot(X[0],FALLBACK));total=float(np.clip(55-.3*x["weather_penalty"],34,84))
 prob=float(1/(1+np.exp(-margin/7.5)))
 return margin,total,prob,"fallback_uncalibrated"
def simulate(a,b,margin,total,prob,n):
 rng=np.random.default_rng(2026);am=max(3,(total+margin)/2);bm=max(3,(total-margin)/2)
 pace=rng.normal(0,4.5,n);A=np.maximum(0,np.rint(am+pace+rng.normal(0,8.5,n)));B=np.maximum(0,np.rint(bm+pace+rng.normal(0,8.5,n)))
 M=A-B;T=A+B;sp=float(np.mean(A>B)+.5*np.mean(A==B))
 return {"score":{a:round(float(A.mean()),1),b:round(float(B.mean()),1)},"margin":round(float(M.mean()),1),
 "total":round(float(T.mean()),1),"win_probability":{a:round(prob,4),b:round(1-prob,4)},
 "simulation_win_probability":{a:round(sp,4),b:round(1-sp,4)},
 "margin_80":[float(np.percentile(M,10)),float(np.percentile(M,90))],
 "total_80":[float(np.percentile(T,10)),float(np.percentile(T,90))],"simulations":n}
