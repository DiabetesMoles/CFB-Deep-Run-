from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from .pipeline import Pipeline
from .config import settings

app = FastAPI(title="CFB Deep Run", version="2.0")
pipe = Pipeline()

class Req(BaseModel):
    team_a: str = Field(min_length=2)
    team_b: str = Field(min_length=2)

@app.get("/health")
async def health():
    return {
        "ok": True,
        "version": "2.0",
        "api_configured": bool(settings.api_key),
        "simulations": settings.simulations,
        "season": settings.season,
    }

@app.post("/deep-run")
async def deep(r: Req):
    if not settings.api_key:
        raise HTTPException(
            503,
            "CFBD_API_KEY is not configured yet. Add it to Railway Variables and redeploy."
        )
    a, b = r.team_a.strip(), r.team_b.strip()
    if a.casefold() == b.casefold():
        raise HTTPException(400, "Choose two different teams.")
    try:
        return await pipe.run(a, b, settings.season)
    except Exception as e:
        raise HTTPException(502, str(e))

@app.get("/", response_class=HTMLResponse)
async def ui():
    return r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#07111f">
<title>CFB Deep Run</title>
<style>
:root{--bg:#050a12;--panel:#0b1524;--panel2:#101d30;--line:#22314a;--text:#f5f8ff;--muted:#94a3b8;--accent:#4f8cff;--good:#39d98a;--warn:#ffcc66}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;background:radial-gradient(circle at 50% -10%,#17345c 0,#08111e 34%,var(--bg) 68%);color:var(--text);min-height:100vh}
.wrap{max-width:940px;margin:auto;padding:32px 18px 70px}.hero{text-align:center;padding:28px 0 20px}.ball{font-size:42px}.hero h1{font-size:clamp(32px,7vw,58px);margin:6px 0 4px;letter-spacing:-2px}.hero p{color:var(--muted);margin:0;font-size:16px}
.card{background:linear-gradient(180deg,rgba(16,29,48,.96),rgba(9,19,33,.96));border:1px solid var(--line);border-radius:22px;padding:18px;box-shadow:0 18px 60px rgba(0,0,0,.28)}
.entry{display:grid;grid-template-columns:1fr 44px 1fr;gap:12px;align-items:center}.vs{text-align:center;color:#6f83a3;font-weight:900}
label{display:block;color:#a9b6ca;font-size:12px;font-weight:800;letter-spacing:.12em;margin:0 0 7px}input{width:100%;padding:15px 14px;border-radius:13px;border:1px solid #31425e;background:#07111f;color:#fff;font-size:17px;outline:none}input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(79,140,255,.14)}
button{width:100%;margin-top:14px;padding:16px;border:0;border-radius:14px;background:linear-gradient(90deg,#2f6ff4,#66a0ff);color:white;font-weight:900;font-size:16px;letter-spacing:.04em;cursor:pointer}button:disabled{opacity:.55}
.status{margin:14px 0 0;text-align:center;color:var(--muted);min-height:22px}.hidden{display:none!important}
.score{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:14px;margin-top:18px;text-align:center}.team{font-size:clamp(17px,4vw,24px);font-weight:900}.pts{font-size:clamp(42px,10vw,72px);font-weight:950;letter-spacing:-3px}.dash{font-size:32px;color:#60708a}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}.metric{background:#07111f;border:1px solid #1e2d44;border-radius:15px;padding:14px}.metric b{font-size:22px;display:block}.metric span{font-size:12px;color:var(--muted)}
.section{margin-top:14px}.section h3{margin:0 0 10px;font-size:15px}.factors{display:grid;grid-template-columns:1fr 1fr;gap:8px}.factor{display:flex;justify-content:space-between;gap:10px;padding:11px 12px;background:#07111f;border-radius:12px;color:#c8d4e7;font-size:13px}.factor b{color:#fff}
.note{color:var(--muted);font-size:12px;line-height:1.5}.good{color:var(--good)}.warn{color:var(--warn)}
@media(max-width:680px){.entry{grid-template-columns:1fr}.vs{height:10px}.grid{grid-template-columns:1fr 1fr}.factors{grid-template-columns:1fr}.wrap{padding-top:14px}}
</style>
</head>
<body><main class="wrap">
<section class="hero"><div class="ball">🏈</div><h1>CFB Deep Run</h1><p>Two teams. Full matchup analysis. 50,000 simulations.</p></section>
<section class="card">
<div class="entry">
<div><label>TEAM 1</label><input id="a" autocomplete="off" placeholder="e.g. Ohio State"></div>
<div class="vs">VS</div>
<div><label>TEAM 2</label><input id="b" autocomplete="off" placeholder="e.g. Michigan"></div>
</div>
<button id="run">RUN DEEP ANALYSIS</button>
<div id="status" class="status">Ready.</div>
</section>

<section id="results" class="card hidden" style="margin-top:14px">
<div class="score">
<div><div id="ta" class="team"></div><div id="sa" class="pts"></div><div id="wa" class="good"></div></div>
<div class="dash">—</div>
<div><div id="tb" class="team"></div><div id="sb" class="pts"></div><div id="wb" class="good"></div></div>
</div>
<div class="grid">
<div class="metric"><b id="margin">—</b><span>PROJECTED MARGIN</span></div>
<div class="metric"><b id="total">—</b><span>PROJECTED TOTAL</span></div>
<div class="metric"><b id="sims">—</b><span>SIMULATIONS</span></div>
<div class="metric"><b id="conf">—</b><span>DATA COMPLETENESS</span></div>
</div>
<div class="section"><h3>Biggest matchup factors</h3><div id="factors" class="factors"></div></div>
<div class="section"><div id="model" class="note"></div></div>
</section>
</main>
<script>
const $=id=>document.getElementById(id), run=$("run");
const nice=s=>String(s||"").replaceAll("_"," ").replace(/\b\w/g,c=>c.toUpperCase());
run.onclick=async()=>{
 const a=$("a").value.trim(), b=$("b").value.trim();
 if(!a||!b){$("status").textContent="Enter both team names.";return}
 run.disabled=true;$("results").classList.add("hidden");$("status").textContent="Collecting data and running 50,000 simulations…";
 try{
  const q=await fetch("/deep-run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({team_a:a,team_b:b})});
  const j=await q.json(); if(!q.ok) throw new Error(j.detail||"Analysis failed.");
  const p=j.prediction, names=Object.keys(p.score);
  $("ta").textContent=names[0];$("tb").textContent=names[1];
  $("sa").textContent=Number(p.score[names[0]]).toFixed(1);$("sb").textContent=Number(p.score[names[1]]).toFixed(1);
  $("wa").textContent=(100*p.simulation_win_probability[names[0]]).toFixed(1)+"% win";
  $("wb").textContent=(100*p.simulation_win_probability[names[1]]).toFixed(1)+"% win";
  $("margin").textContent=(p.margin>=0?names[0]+" +":"")+Number(p.margin).toFixed(1);
  $("total").textContent=Number(p.total).toFixed(1);$("sims").textContent=Number(p.simulations).toLocaleString();
  $("conf").textContent=Number(j.confidence.data_pct).toFixed(0)+"%";
  $("factors").innerHTML=(j.top_factors||[]).map(x=>`<div class="factor"><span>${nice(x.factor)}</span><b>${x.team_a_edge>0?"+":""}${x.team_a_edge}</b></div>`).join("");
  $("model").textContent="Model: "+nice(j.model_status)+". Missing/unverified information is not invented; lower coverage reduces confidence.";
  $("results").classList.remove("hidden");$("status").textContent="Deep Run complete.";
 }catch(e){$("status").textContent=e.message}
 finally{run.disabled=false}
};
</script></body></html>"""
