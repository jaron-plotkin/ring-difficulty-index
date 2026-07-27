"""
RDI Complete Site Generator
=============================
Generates a single index.html with three tabs:
  1. Higher/Lower game
  2. Full rankings dashboard
  3. About / methodology FAQ

Usage:
    python generate_site.py
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rdi import load_csvs, RDICalculator

def generate(series_path="all_series.csv", games_path="all_games.csv", output="index.html"):
    print("  Loading data...")
    runs = load_csvs(series_path, games_path)
    print(f"  Loaded {len(runs)} championship runs.")
    print("  Calculating RDI...")
    calc = RDICalculator()
    results = [calc.calculate(run) for run in runs]
    calc.calibrate_baseline(results)
    ranked = sorted(results, key=lambda r: r["adjusted_rings"], reverse=True)

    data = []
    for i, r in enumerate(ranked, 1):
        path = []
        for b in r["breakdowns"]:
            path.append({"round": b["round_name"], "opp": b["opponent"], "result": b["series_result"], "oqs": round(b["oqs"], 1), "cps": round(b["cps"], 1)})
        data.append({"rank": i, "champion": r["champion"], "season": r["season"], "sport": r["sport"],
            "adj": round(r["adjusted_rings"], 2), "core": round(r["core_rings"], 2), "narr": round(r["narrative_total"], 2),
            "seed": r.get("champion_seed"), "drought": r.get("narrative", {}).get("drought_years", 0) or 0, "path": path})

    data_json = json.dumps(data)
    count = len(data)
    sports = {d["sport"] for d in data}
    sport_counts = {s: sum(1 for d in data if d["sport"]==s) for s in sports}

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Ring Difficulty Index — How Much Is Your Ring Worth?</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,sans-serif;background:#0c1015;color:#e0e0e0;min-height:100vh}}
.container{{max-width:960px;margin:0 auto;padding:24px 20px}}

/* Tabs */
.tab-bar{{display:flex;gap:0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:24px}}
.tab{{padding:12px 24px;font-size:13px;font-weight:700;color:#555;cursor:pointer;border-bottom:2px solid transparent;transition:all 0.15s;text-transform:uppercase;letter-spacing:0.5px;background:none;border-top:none;border-left:none;border-right:none;font-family:inherit}}
.tab:hover{{color:#999}}
.tab.active{{color:#e8b318;border-bottom-color:#e8b318}}
.tab-content{{display:none}}.tab-content.active{{display:block}}

/* Shared */
.sport-colors .NBA{{color:#e8963e}}.sport-colors .NFL{{color:#4a8f4a}}.sport-colors .NHL{{color:#5a9fd4}}.sport-colors .MLB{{color:#c85450}}
.sc{{display:inline-block;padding:2px 7px;border-radius:3px;font-size:9px;font-weight:700;letter-spacing:0.5px}}
.sc.NBA{{color:#e8963e;background:rgba(232,150,62,0.1);border:1px solid rgba(232,150,62,0.2)}}
.sc.NFL{{color:#4a8f4a;background:rgba(74,143,74,0.1);border:1px solid rgba(74,143,74,0.2)}}
.sc.NHL{{color:#5a9fd4;background:rgba(90,159,212,0.1);border:1px solid rgba(90,159,212,0.2)}}
.sc.MLB{{color:#c85450;background:rgba(200,84,80,0.1);border:1px solid rgba(200,84,80,0.2)}}
.mono{{font-family:'JetBrains Mono',monospace}}
.btn{{padding:4px 12px;border-radius:5px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:#555;font-size:10px;font-weight:600;cursor:pointer;text-transform:uppercase;letter-spacing:0.7px;font-family:inherit;transition:all 0.15s}}
.btn.active{{border-color:currentColor;background:rgba(255,255,255,0.05)}}
.btn:hover{{color:#aaa}}

/* Game tab */
.game-stats{{display:flex;gap:20px;justify-content:center;margin-bottom:20px;flex-wrap:wrap}}
.gstat{{text-align:center}}.gstat-val{{font-size:26px;font-weight:800;font-family:'JetBrains Mono',monospace;color:#f0f0f0}}.gstat-val.streak{{color:#e8b318}}.gstat-lbl{{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#555;margin-top:2px}}
.game-area{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}}
.card{{flex:1;min-width:270px;max-width:420px;background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:18px;cursor:pointer;transition:all 0.2s;overflow:hidden}}
.card:hover:not(.revealed):not(.disabled){{border-color:rgba(255,255,255,0.15);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.3)}}
.card.disabled{{cursor:default}}.card.winner{{border-color:#4a9e6e;background:rgba(74,158,110,0.06)}}.card.loser{{border-color:#b85450;background:rgba(184,84,80,0.04)}}
.card-season{{font-size:11px;color:#666;font-family:'JetBrains Mono',monospace;margin-bottom:3px}}
.card-name{{font-size:19px;font-weight:800;color:#f0f0f0;margin-bottom:3px}}
.card-meta{{font-size:11px;color:#555;margin-bottom:10px}}
.path-row{{display:flex;justify-content:space-between;padding:3px 8px;background:rgba(255,255,255,0.02);border-radius:3px;font-size:11px;margin-bottom:2px}}
.path-row .rnd{{color:#666;font-size:9px;font-weight:600;min-width:26px}}.path-row .opp{{color:#bbb;flex:1;margin:0 6px}}.path-row .res{{font-family:'JetBrains Mono',monospace;color:#999;font-size:10px}}
.card-prompt{{text-align:center;margin-top:12px;padding:8px;background:rgba(255,255,255,0.03);border-radius:6px;font-size:12px;font-weight:600;color:#888}}
.card:hover:not(.revealed):not(.disabled) .card-prompt{{color:#e0e0e0;background:rgba(255,255,255,0.06)}}
.score-reveal{{text-align:center;margin-top:12px}}.score-reveal .rv{{font-size:32px;font-weight:900;font-family:'JetBrains Mono',monospace}}.score-reveal .rl{{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#666;margin-top:2px}}.score-reveal .rb{{font-size:10px;color:#555;margin-top:3px}}
.vs{{display:flex;align-items:center;font-size:18px;font-weight:900;color:#333;min-width:36px;justify-content:center;align-self:center}}
.result-banner{{text-align:center;margin:14px 0;padding:14px;border-radius:10px;font-size:16px;font-weight:800}}
.result-banner.correct{{background:rgba(74,158,110,0.1);color:#4a9e6e;border:1px solid rgba(74,158,110,0.2)}}
.result-banner.wrong{{background:rgba(184,84,80,0.1);color:#b85450;border:1px solid rgba(184,84,80,0.2)}}
.result-banner.tie{{background:rgba(232,179,24,0.1);color:#e8b318;border:1px solid rgba(232,179,24,0.2)}}
.next-btn{{display:block;margin:12px auto 0;padding:10px 28px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:8px;color:#e0e0e0;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit}}
.next-btn:hover{{background:rgba(255,255,255,0.1)}}
.export-area{{margin-top:24px;text-align:center;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}}

/* Rankings tab */
.search input{{width:100%;padding:8px 14px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:6px;color:#ddd;font-size:13px;font-family:inherit;outline:none;margin-bottom:12px}}
.search input:focus{{border-color:rgba(255,255,255,0.15)}}
.search input::placeholder{{color:#444}}
.filters{{display:flex;gap:5px;margin-bottom:10px;flex-wrap:wrap}}
.table-wrap{{border-radius:8px;border:1px solid rgba(255,255,255,0.05);overflow:hidden}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
thead tr{{background:rgba(255,255,255,0.02)}}
th{{padding:10px 12px;text-align:left;cursor:pointer;user-select:none;font-size:10px;text-transform:uppercase;letter-spacing:1.1px;color:#555;border-bottom:1px solid rgba(255,255,255,0.06);font-weight:600;white-space:nowrap}}
th.act{{color:#e0e0e0}}
tbody tr{{cursor:pointer;transition:background 0.12s;border-bottom:1px solid rgba(255,255,255,0.025)}}
tbody tr:hover{{background:rgba(255,255,255,0.03)}}
.bar-c{{display:flex;align-items:center;gap:8px;min-width:155px}}.bar-bg{{flex:1;height:7px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden}}.bar-f{{height:100%;border-radius:4px}}.bar-v{{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;min-width:36px;text-align:right}}
.detail{{background:rgba(255,255,255,0.025);border-radius:10px;padding:20px 24px;margin-bottom:12px;border:1px solid rgba(255,255,255,0.06)}}
.detail-scores{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:14px}}
.ds-box{{background:rgba(255,255,255,0.03);border-radius:8px;padding:10px 14px;text-align:center}}
.ds-val{{font-size:24px;font-weight:800;font-family:'JetBrains Mono',monospace}}.ds-lbl{{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#666;margin-top:2px}}
.pg{{display:grid;gap:5px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));margin-bottom:12px}}
.pc{{background:rgba(255,255,255,0.03);border-radius:5px;padding:7px 10px;border-left:3px solid #555}}.pc.fin{{border-left-color:#e8b318}}
.dist{{margin-top:20px;padding:14px 18px;background:rgba(255,255,255,0.015);border-radius:8px;border:1px solid rgba(255,255,255,0.04)}}
.dist-bars{{display:flex;align-items:flex-end;gap:1px;height:55px}}
.dist-bar{{flex:1;min-width:0;cursor:pointer;border-radius:1px 1px 0 0;transition:opacity 0.15s}}

/* About tab */
.about{{max-width:720px;line-height:1.7;color:#bbb;font-size:14px}}
.about h2{{font-size:20px;font-weight:800;color:#f0f0f0;margin:28px 0 10px;letter-spacing:-0.3px}}
.about h2:first-child{{margin-top:0}}
.about h3{{font-size:15px;font-weight:700;color:#ddd;margin:20px 0 6px}}
.about p{{margin-bottom:12px}}
.about .formula{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:12px 16px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#aaa;margin:10px 0 14px;overflow-x:auto}}
.about .faq-q{{color:#e8b318;font-weight:700;margin-top:16px;margin-bottom:4px}}
</style></head><body>
<div class="container">
<div style="text-align:center;margin-bottom:4px">
<h1 style="font-size:26px;font-weight:900;color:#f0f0f0;letter-spacing:-0.5px">🏆 Ring Difficulty Index</h1>
<p style="font-size:12px;color:#555">How much is each championship ring worth? {count} titles across NBA, NFL, NHL & MLB.</p>
</div>
<div class="tab-bar">
<button class="tab active" onclick="switchTab('game')">Game</button>
<button class="tab" onclick="switchTab('rankings')">Rankings</button>
<button class="tab" onclick="switchTab('about')">About</button>
</div>

<!-- ==================== GAME TAB ==================== -->
<div class="tab-content active" id="tab-game">
<div class="game-stats">
<div class="gstat"><div class="gstat-val" id="gTotal">0</div><div class="gstat-lbl">Played</div></div>
<div class="gstat"><div class="gstat-val" id="gCorrect">0</div><div class="gstat-lbl">Correct</div></div>
<div class="gstat"><div class="gstat-val" id="gPct">—</div><div class="gstat-lbl">Accuracy</div></div>
<div class="gstat"><div class="gstat-val streak" id="gStreak">0</div><div class="gstat-lbl">Streak</div></div>
<div class="gstat"><div class="gstat-val streak" id="gBest">0</div><div class="gstat-lbl">Best</div></div>
</div>
<div class="filters" id="gameSportToggles" style="justify-content:center;margin-bottom:16px"></div>
<div id="resultBanner"></div>
<div class="game-area" id="gameArea"></div>
<div id="nextArea"></div>
<div class="export-area">
<button class="btn" onclick="exportHistory()">Export Play History</button>
<button class="btn" onclick="exportCrowd()">Export Crowdsource Data</button>
</div>
</div>

<!-- ==================== RANKINGS TAB ==================== -->
<div class="tab-content" id="tab-rankings">
<div class="search"><input type="text" id="searchInput" placeholder="Search team or season..." oninput="renderRankings()"></div>
<div class="filters" id="rankSportFilters"></div>
<div class="filters" id="rankTierFilters"></div>
<div id="rankDetail"></div>
<div class="table-wrap"><table><thead><tr id="rankHeader"></tr></thead><tbody id="rankBody"></tbody></table></div>
<div class="dist"><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#444;margin-bottom:8px">Distribution</div><div class="dist-bars" id="distBars"></div><div style="display:flex;justify-content:space-between;margin-top:4px;font-size:9px;color:#444"><span>← HARDEST</span><span>EASIEST →</span></div></div>
</div>

<!-- ==================== ABOUT TAB ==================== -->
<div class="tab-content" id="tab-about">
<div class="about">
<h2>What is the Ring Difficulty Index?</h2>
<p>The Ring Difficulty Index (RDI) measures how impressive each championship ring is across all four major North American sports. It quantifies the arguments fans have been having for decades — "Dirk's 2011 ring is more impressive than any of KD's Warriors rings" — with a rigorous statistical framework.</p>
<p>The output is in <strong style="color:#e8b318">rings</strong> — 1.00 means an average championship run. A score of 1.58 means that title was worth about 1.6 average rings. A score of 0.65 means the path was so easy the ring is worth less than one.</p>

<h2>How is it calculated?</h2>
<p>Each championship run is broken into individual matchups (one per playoff round). Each matchup is scored on multiple dimensions, then combined with round-importance weights where later rounds count more.</p>

<h3>Core Statistical Components (65/35 split)</h3>
<p><strong>Opponent Quality Score (OQS)</strong> — 65% of the base matchup score. How good was each opponent? Uses regular-season win percentage, point differential, and SRS (Simple Rating System — a strength-of-schedule-adjusted metric), all z-scored and normalized per sport so a .600 NBA team and a .600 NFL team are evaluated on equivalent scales.</p>
<p><strong>Competitive Pressure Score (CPS)</strong> — 35% of base. How hard did the champion have to work? For series sports (NBA, NHL, MLB): series length, average margin, close-game percentage, overtime frequency, and elimination survival. For single-elimination (NFL): margin of victory and overtime.</p>

<h3>Bonus Modifiers</h3>
<p><strong>Dominance Bonus</strong> — Rewards winning short series against quality opponents. Sweeping a 60-win team earns credit; sweeping a .500 team earns almost nothing. A 7-game series gets zero dominance bonus (you went the distance).</p>
<p><strong>Clutch Bonus</strong> — Rewards trailing at halftime but winning the game, weighted by opponent quality. Requires quarter-by-quarter data (currently NBA only).</p>
<p><strong>Series Comeback Bonus</strong> — Non-linear scaling for overcoming series deficits. Being down 3-1 is exponentially more impressive than 2-1. Weighted by opponent quality and number of elimination games won.</p>

<h3>Expectation Adjustment</h3>
<p>A historically dominant regular-season team gets penalized — they were <em>supposed</em> to win. A weaker team that overperformed gets a boost. Based on the champion's own SRS: each z-score of dominance costs ~3 raw points.</p>
<div class="formula">rings = e^(0.03 × (raw_score - baseline))</div>

<h3>Narrative Modifiers (additive)</h3>
<p><strong>Championship Drought</strong> — Logarithmic bonus for ending long title droughts. The 2016 Cubs' 108-year wait (+0.36) and the Knicks' 53-year wait (+0.23) are rewarded, but with diminishing returns — the difference between 50 and 80 years is small.</p>
<p><strong>Underdog Seed</strong> — Small bonus for lower-seeded champions who faced structural disadvantages (fewer home games, tougher bracket position).</p>

<h3>Round Importance Weights</h3>
<p>Later rounds count more: the Finals/Super Bowl carries about 2.5× the weight of the first round. A legendary Finals performance can carry an otherwise average path.</p>

<h2>Data Sources</h2>
<p><strong>NBA:</strong> nba_api (stats.nba.com) — team standings, playoff game scores, quarter-by-quarter data. 1984–present.</p>
<p><strong>NFL:</strong> nfl_data_py (nflverse) — schedule data with scores. 1999–present.</p>
<p><strong>NHL:</strong> NHL API (api-web.nhle.com) — standings, playoff brackets, game scores. 1975–present.</p>
<p><strong>MLB:</strong> MLB-StatsAPI (statsapi.mlb.com) — standings, postseason game scores. 1970–present.</p>

<h2>FAQ</h2>

<p class="faq-q">Why are NHL rings rated so high compared to other sports?</p>
<p>NHL playoffs have four rounds of best-of-7 with frequent overtime games. Each OT pushes competitive pressure higher. The sheer volume of high-stakes games creates more opportunities for the model to detect difficulty. This is partially a real phenomenon (hockey playoffs ARE grueling) and partially a data artifact that may need cross-sport normalization in future versions.</p>

<p class="faq-q">Why is the 72-10 Bulls' ring (1995-96) rated below average?</p>
<p>The expectation adjustment. They were the most dominant regular-season team in NBA history — the model says they SHOULD have won. Their playoff path was also relatively easy (no opponent took them to 7 games). Dominance is penalized because an expected outcome is less impressive than an unexpected one.</p>

<p class="faq-q">Why does the drought bonus use a logarithmic curve?</p>
<p>The emotional difference between ending a 10-year drought and a 15-year drought is huge. The difference between 50 years and 55 years is negligible — it's all the same flavor of suffering. The logarithmic curve captures this diminishing return naturally.</p>

<p class="faq-q">Isn't it unfair to penalize dynasties?</p>
<p>The model penalizes <em>expected</em> dominance, not excellence. A dynasty's first ring often scores very high (Jordan's 1993 three-peat closer is #7 in NBA). It's the repeat rings where the league hasn't adjusted yet that score lower — because the champion was the overwhelming favorite.</p>

<p class="faq-q">Can I contribute data or suggest improvements?</p>
<p>Yes! Play the Higher/Lower game and export your responses — crowdsourced data helps validate whether the model's rankings match human intuition. The full source code is available on GitHub.</p>

<p class="faq-q">How should I interpret cross-sport comparisons?</p>
<p>With appropriate skepticism. The model uses the same framework across all sports, but structural differences (series length, overtime rules, season length) mean that direct comparison between, say, an NHL ring and an NFL ring involves assumptions about equivalence that are inherently debatable. Within-sport rankings are more reliable than cross-sport ones.</p>
</div>
</div>

</div><!-- /container -->

<script>
const DATA = {data_json};
const SC = {{NBA:'#e8963e',NFL:'#4a8f4a',NHL:'#5a9fd4',MLB:'#c85450'}};
function ti(adj){{ if(adj>=1.80)return{{l:'LEGENDARY',c:'#e8b318'}};if(adj>=1.40)return{{l:'ELITE',c:'#d4a017'}};if(adj>=1.00)return{{l:'SOLID',c:'#4a9e6e'}};if(adj>=0.70)return{{l:'LIGHT',c:'#7a8a99'}};return{{l:'FREEBIE',c:'#b85450'}}; }}
const TC = {{LEGENDARY:'#e8b318',ELITE:'#d4a017',SOLID:'#4a9e6e',LIGHT:'#7a8a99',FREEBIE:'#b85450'}};

// ===== TAB SWITCHING =====
function switchTab(id){{
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  event.target.classList.add('active');
  if(id==='rankings' && !rankInited) initRankings();
}}

// ===== GAME =====
let gStats={{total:0,correct:0,streak:0,best:0}};
let gHistory=[];let gCrowd={{}};
let gSports=new Set(['NBA','NFL','NHL','MLB']);
let cardA=null,cardB=null,gRevealed=false;
try{{const s=localStorage.getItem('rdi_gs');if(s){{const p=JSON.parse(s);gStats=p.s||gStats;gHistory=p.h||[];gCrowd=p.c||{{}};}}}}catch(e){{}}
function gSave(){{try{{localStorage.setItem('rdi_gs',JSON.stringify({{s:gStats,h:gHistory,c:gCrowd}}))}}catch(e){{}}}}
function gPool(){{return DATA.filter(d=>gSports.has(d.sport))}}
function gPick(){{const p=gPool();if(p.length<2)return null;let a,b;do{{a=p[~~(Math.random()*p.length)];b=p[~~(Math.random()*p.length)]}}while(a.season===b.season&&a.champion===b.champion);return[a,b]}}
function mkCard(item,side,el){{
  const s=item.seed?`#${{item.seed}} seed`:'';const dr=item.drought>=10?` · ${{item.drought}}-yr drought`:'';
  let ph='';if(item.path&&item.path.length){{ph='<div style="margin-top:8px">';item.path.forEach(p=>{{ph+=`<div class="path-row"><span class="rnd">${{p.round.replace('Conference ','').replace('Championship','Champ').replace('Stanley Cup ','SC ').replace('World Series','WS').replace('Division Series','DS').replace('Wild Card Series','WC').substring(0,10)}}</span><span class="opp">${{p.opp}}</span><span class="res">${{p.result}}</span></div>`}});ph+='</div>'}}
  const d=document.createElement('div');d.className='card';d.id='c-'+side;
  d.innerHTML=`<span class="sc ${{item.sport}}">${{item.sport}}</span><div class="card-season">${{item.season}}</div><div class="card-name">${{item.champion}}</div><div class="card-meta">${{s}}${{dr}}</div>${{ph}}<div class="card-prompt">👆 This ring is worth more</div>`;
  d.onclick=()=>{{if(!gRevealed)gChoice(side)}};el.appendChild(d)}}
function gChoice(side){{
  gRevealed=true;const ch=side==='a'?cardA:cardB;const ot=side==='a'?cardB:cardA;
  const diff=Math.abs(cardA.adj-cardB.adj);let ok=diff<0.02?true:ch.adj>=ot.adj;
  gStats.total++;if(ok){{gStats.correct++;gStats.streak++;if(gStats.streak>gStats.best)gStats.best=gStats.streak}}else gStats.streak=0;
  gHistory.push({{a:{{c:cardA.champion,s:cardA.season,sp:cardA.sport,v:cardA.adj}},b:{{c:cardB.champion,s:cardB.season,sp:cardB.sport,v:cardB.adj}},ch:side,ok,t:new Date().toISOString()}});
  const mk=[cardA.champion+' '+cardA.season,cardB.champion+' '+cardB.season].sort().join(' vs ');
  if(!gCrowd[mk])gCrowd[mk]={{}};const pk=ch.champion+' '+ch.season;gCrowd[mk][pk]=(gCrowd[mk][pk]||0)+1;
  gSave();gReveal(side,ok,diff<0.02);gUpdateStats()}}
function gReveal(side,ok,tie){{
  ['a','b'].forEach(s=>{{const c=document.getElementById('c-'+s);const it=s==='a'?cardA:cardB;const t=ti(it.adj);
  c.classList.add('revealed','disabled');c.classList.add(tie?'winner':(it.adj>=(s==='a'?cardB:cardA).adj?'winner':'loser'));
  const pr=c.querySelector('.card-prompt');pr.outerHTML=`<div class="score-reveal"><div class="rv" style="color:${{t.c}}">${{it.adj.toFixed(2)}}</div><div class="rl">${{t.l}}</div><div class="rb">Core: ${{it.core.toFixed(2)}} | Narrative: +${{it.narr.toFixed(2)}}</div></div>`}});
  const b=document.getElementById('resultBanner');
  if(tie)b.innerHTML='<div class="result-banner tie">⚡ Dead heat — both answers count!</div>';
  else if(ok)b.innerHTML=`<div class="result-banner correct">✓ Correct! ${{gStats.streak}} in a row</div>`;
  else b.innerHTML=`<div class="result-banner wrong">✗ Wrong! Streak reset</div>`;
  document.getElementById('nextArea').innerHTML='<button class="next-btn" onclick="newRound()">Next Matchup →</button>'}}
function gUpdateStats(){{document.getElementById('gTotal').textContent=gStats.total;document.getElementById('gCorrect').textContent=gStats.correct;document.getElementById('gPct').textContent=gStats.total?Math.round(gStats.correct/gStats.total*100)+'%':'—';document.getElementById('gStreak').textContent=gStats.streak;document.getElementById('gBest').textContent=gStats.best}}
function newRound(){{gRevealed=false;document.getElementById('resultBanner').innerHTML='';document.getElementById('nextArea').innerHTML='';
  const p=gPick();if(!p){{document.getElementById('gameArea').innerHTML='<p style="color:#666">Need at least 2 sports selected.</p>';return}}
  cardA=p[0];cardB=p[1];const a=document.getElementById('gameArea');a.innerHTML='';
  mkCard(cardA,'a',a);const v=document.createElement('div');v.className='vs';v.textContent='VS';a.appendChild(v);mkCard(cardB,'b',a)}}
function initGameSports(){{const c=document.getElementById('gameSportToggles');['NBA','NFL','NHL','MLB'].forEach(s=>{{const b=document.createElement('button');b.className='btn active';b.style.color=SC[s];b.textContent=s;b.onclick=()=>{{if(gSports.has(s))gSports.delete(s);else gSports.add(s);if(gSports.size===0)gSports=new Set(['NBA','NFL','NHL','MLB']);b.classList.toggle('active',gSports.has(s));if(!gRevealed)newRound()}};c.appendChild(b)}})}}
function exportHistory(){{const b=new Blob([JSON.stringify({{stats:gStats,plays:gHistory}},null,2)],{{type:'application/json'}});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download='rdi_play_history.json';a.click()}}
function exportCrowd(){{const tp={{}};gHistory.forEach(p=>{{const ch=p.ch==='a'?p.a:p.b;const ot=p.ch==='a'?p.b:p.a;[ch,ot].forEach(x=>{{const k=x.c+' '+x.s+' ('+x.sp+')';tp[k]=tp[k]||{{h:0,l:0,n:0}}}});const ck=ch.c+' '+ch.s+' ('+ch.sp+')';const ok=ot.c+' '+ot.s+' ('+ot.sp+')';tp[ck].h++;tp[ck].n++;tp[ok].l++;tp[ok].n++}});
  const sorted=Object.entries(tp).map(([k,v])=>({{ring:k,...v,rate:v.n?Math.round(v.h/v.n*100):0}})).sort((a,b)=>b.rate-a.rate);
  const b=new Blob([JSON.stringify({{total:gStats.total,rankings:sorted}},null,2)],{{type:'application/json'}});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download='rdi_crowdsource.json';a.click()}}

// ===== RANKINGS =====
let rankInited=false;
let rSports=new Set(['NBA','NFL','NHL','MLB']);let rTier='all';let rSort='adj';let rDir='desc';let rExp=null;
function initRankings(){{
  rankInited=true;
  const sf=document.getElementById('rankSportFilters');
  const allBtn=document.createElement('button');allBtn.className='btn active';allBtn.textContent='All {count}';allBtn.onclick=()=>{{rSports=new Set(['NBA','NFL','NHL','MLB']);sf.querySelectorAll('.btn').forEach(b=>b.classList.add('active'));renderRankings()}};sf.appendChild(allBtn);
  ['NBA','NFL','NHL','MLB'].forEach(s=>{{const b=document.createElement('button');b.className='btn active';b.style.color=SC[s];b.textContent=s;b.onclick=()=>{{if(rSports.has(s))rSports.delete(s);else rSports.add(s);if(rSports.size===0)rSports=new Set(['NBA','NFL','NHL','MLB']);b.classList.toggle('active',rSports.has(s));allBtn.classList.toggle('active',rSports.size===4);renderRankings()}};sf.appendChild(b)}});
  const tf=document.getElementById('rankTierFilters');
  ['all','LEGENDARY','ELITE','SOLID','LIGHT','FREEBIE'].forEach(t=>{{const b=document.createElement('button');b.className='btn'+(t==='all'?' active':'');b.style.color=TC[t]||'#999';const cnt=t==='all'?DATA.length:DATA.filter(d=>ti(d.adj).l===t).length;b.textContent=t==='all'?'All Tiers':`${{t}} ${{cnt}}`;b.onclick=()=>{{rTier=t;tf.querySelectorAll('.btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');renderRankings()}};tf.appendChild(b)}});
  renderRankings()}}
function getRanked(){{let d=[...DATA];const q=(document.getElementById('searchInput')||{{}}).value||'';if(q)d=d.filter(r=>r.champion.toLowerCase().includes(q.toLowerCase())||r.season.includes(q));if(rSports.size<4)d=d.filter(r=>rSports.has(r.sport));if(rTier!=='all')d=d.filter(r=>ti(r.adj).l===rTier);d.sort((a,b)=>{{let va=a[rSort],vb=b[rSort];if(typeof va==='string')return rDir==='asc'?va.localeCompare(vb):vb.localeCompare(va);return rDir==='asc'?va-vb:vb-va}});return d}}
function renderRankings(){{
  const cols=[['#','rank','c',38],['Champion','champion','l',null],['Year','season','l',65],['Sport','sport','c',46],['Adjusted','adj','l',185],['Core','core','c',46],['Narr','narr','c',46]];
  const hr=document.getElementById('rankHeader');hr.innerHTML='';
  cols.forEach(([lb,k,al,w])=>{{const th=document.createElement('th');th.textContent=lb+(rSort===k?(rDir==='desc'?' ▾':' ▴'):'');th.className=rSort===k?'act':'';if(al==='c')th.style.textAlign='center';if(w)th.style.width=w+'px';th.onclick=()=>{{if(rSort===k)rDir=rDir==='desc'?'asc':'desc';else{{rSort=k;rDir=k==='champion'||k==='season'?'asc':'desc'}};renderRankings()}};hr.appendChild(th)}});
  // Detail
  const dp=document.getElementById('rankDetail');
  if(rExp!==null){{const it=DATA.find(d=>d.season===rExp&&d.sport===DATA.find(x=>x.season===rExp).sport);if(it){{const t=ti(it.adj);let ph='';if(it.path&&it.path.length){{ph='<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#555;margin-bottom:5px">Playoff Path</div><div class="pg">';it.path.forEach((p,i)=>{{ph+=`<div class="pc ${{i===it.path.length-1?'fin':''}}"><div style="display:flex;justify-content:space-between"><span style="font-size:9px;font-weight:700;color:#666">${{p.round}}</span><span class="mono" style="font-size:11px;color:#bbb">${{p.result}}</span></div><div style="font-size:12px;font-weight:600;color:#ddd;margin-top:1px">vs ${{p.opp}}</div><div style="font-size:9px;color:#555;margin-top:1px">OQS: ${{p.oqs}} | CPS: ${{p.cps}}</div></div>`}});ph+='</div>'}};dp.innerHTML=`<div class="detail" style="border-color:${{t.c}}22"><div style="display:flex;justify-content:space-between;margin-bottom:12px"><div><div style="font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#666;margin-bottom:2px">${{it.season}} — ${{it.sport}}${{it.seed?' · #'+it.seed+' seed':''}}${{it.drought>0?' · '+it.drought+'-yr drought':''}}</div><div style="font-size:20px;font-weight:800;color:#f0f0f0">${{it.champion}}</div></div><button onclick="rExp=null;renderRankings()" style="background:none;border:none;color:#555;font-size:16px;cursor:pointer">✕</button></div><div class="detail-scores"><div class="ds-box"><div class="ds-val" style="color:${{t.c}}">${{it.adj.toFixed(2)}}</div><div class="ds-lbl">Adjusted</div></div><div class="ds-box"><div class="ds-val" style="color:#c8c8c8">${{it.core.toFixed(2)}}</div><div class="ds-lbl">Core</div></div><div class="ds-box"><div class="ds-val" style="color:#7ab893">+${{it.narr.toFixed(2)}}</div><div class="ds-lbl">Narrative</div></div></div>${{ph}}</div>`}}else dp.innerHTML=''}}else dp.innerHTML='';
  const f=getRanked();const tb=document.getElementById('rankBody');tb.innerHTML='';
  f.forEach((it,i)=>{{const t=ti(it.adj);const pct=Math.min(100,(it.adj/1.7)*100);const tr=document.createElement('tr');if(rExp===it.season)tr.classList.add('expanded');tr.onclick=()=>{{rExp=rExp===it.season?null:it.season;renderRankings()}};
  tr.innerHTML=`<td style="text-align:center;color:#444;font-family:'JetBrains Mono',monospace;font-size:11px">${{it.rank}}</td><td style="font-weight:600;color:#e0e0e0">${{it.champion}}${{it.drought>=30?'<span style="margin-left:5px;font-size:9px;color:rgba(212,160,23,0.5)">🏆 '+it.drought+'yr</span>':''}}</td><td class="mono" style="color:#777;font-size:11px">${{it.season}}</td><td style="text-align:center"><span class="sc ${{it.sport}}">${{it.sport}}</span></td><td><div class="bar-c"><div class="bar-bg"><div class="bar-f" style="width:${{pct}}%;background:linear-gradient(90deg,${{t.c}}66,${{t.c}})"></div></div><span class="bar-v" style="color:${{t.c}}">${{it.adj.toFixed(2)}}</span></div></td><td class="mono" style="text-align:center;color:#999;font-size:11px">${{it.core.toFixed(2)}}</td><td class="mono" style="text-align:center;color:${{it.narr>=0.10?'#7ab893':'#444'}};font-size:11px">${{it.narr>0?'+.'+String(Math.round(it.narr*100)).padStart(2,'0'):'—'}}</td>`;
  tb.appendChild(tr)}});
  // Distribution
  const sorted=[...DATA].sort((a,b)=>b.adj-a.adj);const db=document.getElementById('distBars');db.innerHTML='';
  sorted.forEach(it=>{{const t=ti(it.adj);const h=Math.max(2,(it.adj/1.7)*50);const bar=document.createElement('div');bar.className='dist-bar';bar.style.cssText=`height:${{h}}px;background:${{SC[it.sport]}};opacity:${{rExp===it.season?1:0.45}}`;bar.title=`${{it.champion}} ${{it.season}} (${{it.sport}}): ${{it.adj.toFixed(2)}}`;bar.onclick=(e)=>{{e.stopPropagation();rExp=it.season;renderRankings()}};db.appendChild(bar)}})}}

// Init
initGameSports();gUpdateStats();newRound();
</script></body></html>"""

    out_path = os.path.join(os.path.dirname(os.path.abspath(series_path)), output)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ Site saved to: {out_path}")
    print(f"    Open: start index.html")

if __name__ == "__main__":
    s = sys.argv[1] if len(sys.argv) >= 3 else "all_series.csv"
    g = sys.argv[2] if len(sys.argv) >= 3 else "all_games.csv"
    generate(s, g)
