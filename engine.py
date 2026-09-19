from __future__ import annotations
import numpy as np,joblib
from pathlib import Path
from .config import settings
FEATURES=["off_edge","def_edge","pass_match","opp_pass_match","rush_match","opp_rush_match","success_match","opp_success_match","explosive_match","opp_explosive_match","havoc_match","opp_havoc_match","core_edge","elo_edge","srs_edge","talent_edge","recent_edge","home_a","neutral","weather_penalty"]
FALLBACK=np.array([.10,.10,.08,-.08,.06,-.06,.05,-.05,.04,-.04,.035,-.035,.08,.05,.04,.03,.03,2.3,0,-.08])
def load():
 p=Path(settings.model_path);return joblib.load(p) if p.exists() else None
def estimate(x,a=None,b=None):
 X=np.array([[float(x[k]) for k in FEATURES]]);m=load()
 if m:
  margin=float(m["margin"].predict(X)[0]);total=float(m["total"].predict(X)[0]);prob=float(m["win"].predict_proba(X)[0,1]);return margin,total,prob,"trained"
 margin=float(np.dot(X[0],FALLBACK))
 pa=27.5+.13*(a.offense-50)-.10*(b.defense-50)+.045*(a.pass_off-b.pass_def)+.04*(a.rush_off-b.rush_def)+.035*(a.success_off-b.success_def)+.025*(a.explosive_off-b.explosive_def)
 pb=27.5+.13*(b.offense-50)-.10*(a.defense-50)+.045*(b.pass_off-a.pass_def)+.04*(b.rush_off-a.rush_def)+.035*(b.success_off-a.success_def)+.025*(b.explosive_off-a.explosive_def)
 if x["home_a"]>0:pa+=1.6;pb-=.7
 elif x["home_a"]<0:pb+=1.6;pa-=.7
 w=max(0,float(x["weather_penalty"]));pa-=w*.12;pb-=w*.12
 total=float(np.clip(pa+pb,30,90));margin=float(np.clip(.55*margin+.45*(pa-pb),-45,45));prob=float(1/(1+np.exp(-margin/7.5)))
 return margin,total,prob,"deep_run_v2"
def simulate(a,b,margin,total,prob,n):
 rng=np.random.default_rng();am=max(3,(total+margin)/2);bm=max(3,(total-margin)/2);pace=rng.normal(0,4.5,n)
 A=np.maximum(0,np.rint(am+pace+rng.normal(0,8.5,n)));B=np.maximum(0,np.rint(bm+pace+rng.normal(0,8.5,n)));M=A-B;T=A+B;sp=float(np.mean(A>B)+.5*np.mean(A==B))
 return {"score":{a:round(float(A.mean()),1),b:round(float(B.mean()),1)},"margin":round(float(M.mean()),1),"total":round(float(T.mean()),1),"win_probability":{a:round(prob,4),b:round(1-prob,4)},"simulation_win_probability":{a:round(sp,4),b:round(1-sp,4)},"margin_80":[round(float(np.percentile(M,10)),1),round(float(np.percentile(M,90)),1)],"total_80":[round(float(np.percentile(T,10)),1),round(float(np.percentile(T,90)),1)],"simulations":n}
