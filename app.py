
from __future__ import annotations

import io
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Top 25 Mutual Fund Analytics | Mountain Path Academy", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

NAVY, NAVY2, BLUE, GOLD, GOLD2, PALE = "#081F3A", "#0B2545", "#124A78", "#F3C84B", "#D4A017", "#EEF3F8"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;600;700&display=swap');
.stApp{background:linear-gradient(135deg,#F7F9FC,#EEF3F8);font-family:'Source Sans 3',sans-serif;color:#102A43}
h1,h2,h3{font-family:'Playfair Display',serif!important;color:#0B2545!important}
.hero{background:linear-gradient(115deg,#081F3A 0%,#124A78 70%,#A97908 100%);padding:1.45rem 1.7rem;border-radius:18px;border:1px solid #D4A017;box-shadow:0 8px 24px #081f3a28;margin-bottom:1rem}
.hero h1,.hero p{color:white!important;margin:.1rem 0}.hero b{color:#F3C84B}
.kpi{background:white;border:1px solid #DCE6F0;border-top:5px solid #D4A017;border-radius:14px;padding:1rem;min-height:112px;box-shadow:0 5px 16px #081f3a16}.kpi .v{font-size:1.65rem;font-weight:800;color:#0B3B67}.kpi .l{font-weight:700;color:#506784}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B2545,#153F69)}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] label p{color:#F3C84B!important;font-weight:700!important}
section[data-testid="stSidebar"] .stMarkdown p,section[data-testid="stSidebar"] small{color:white}
section[data-testid="stSidebar"] [data-baseweb="select"]>div,section[data-testid="stSidebar"] input{background:white!important;color:#0B2545!important;-webkit-text-fill-color:#0B2545!important}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:8px;flex-wrap:wrap}
[data-testid="stTabs"] button{background:#0B3B67!important;border:2px solid #D4A017!important;border-radius:10px!important;padding:.65rem .85rem!important;height:auto!important}
[data-testid="stTabs"] button p{color:#F3C84B!important;font-size:1rem!important;font-weight:800!important}
[data-testid="stTabs"] button[aria-selected="true"]{background:linear-gradient(135deg,#F3C84B,#D4A017)!important}
[data-testid="stTabs"] button[aria-selected="true"] p{color:#081F3A!important}
.stButton button,.stDownloadButton button{background:#0B3B67!important;color:white!important;border:2px solid #D4A017!important;font-weight:800!important}.stButton button:hover,.stDownloadButton button:hover{background:#D4A017!important;color:#081F3A!important}
.pill{background:#F3C84B;color:#081F3A;padding:.55rem .8rem;border-radius:9px;font-weight:800;margin:.5rem 0 1rem}
.note{background:#FFF8DE;border-left:5px solid #D4A017;padding:.8rem;border-radius:8px}
.footer{background:#081F3A;color:white;padding:1.2rem;border-radius:14px;text-align:center;margin-top:1.5rem;border-top:4px solid #D4A017}.footer a{color:#F3C84B!important;font-weight:700}
</style>
""", unsafe_allow_html=True)

# A balanced educational universe: five established Direct–Growth schemes in each
# of five diversified-equity categories. Scheme aliases handle AMC name changes.
# AUM is deliberately used as an eligibility/ranking input only when a verified
# value is maintained. The public MFAPI NAV feed does not publish scheme AUM.
FUND_UNIVERSE = {
    # Large Cap
    "Nippon India Large Cap": {"category": "Large Cap", "aliases": ["Nippon India Large Cap Fund - Direct Plan Growth Plan", "Nippon India Large Cap Fund - Direct Plan - Growth Plan"]},
    "ICICI Pru Large Cap": {"category": "Large Cap", "aliases": ["ICICI Prudential Large Cap Fund - Direct Plan Growth", "ICICI Prudential Bluechip Fund - Direct Plan - Growth"]},
    "HDFC Large Cap": {"category": "Large Cap", "aliases": ["HDFC Large Cap Fund - Direct Plan - Growth Option", "HDFC Top 100 Fund -Direct Plan - Growth Option"]},
    "Canara Robeco Large Cap": {"category": "Large Cap", "aliases": ["Canara Robeco Large Cap Fund - Direct Plan - Growth Option", "Canara Robeco Bluechip Equity Fund - Direct Plan - Growth Option"]},
    "Baroda BNP Paribas Large Cap": {"category": "Large Cap", "aliases": ["Baroda BNP Paribas Large Cap Fund - Direct Plan - Growth Option"]},
    # Flexi Cap
    "Parag Parikh Flexi Cap": {"category": "Flexi Cap", "aliases": ["Parag Parikh Flexi Cap Fund - Direct Plan - Growth", "Parag Parikh Flexi Cap Fund-Direct-Growth"]},
    "HDFC Flexi Cap": {"category": "Flexi Cap", "aliases": ["HDFC Flexi Cap Fund - Direct Plan - Growth Option"]},
    "JM Flexicap": {"category": "Flexi Cap", "aliases": ["JM Flexicap Fund (Direct) - Growth Option", "JM Flexicap Fund - Direct Plan - Growth Option"]},
    "Franklin India Flexi Cap": {"category": "Flexi Cap", "aliases": ["Franklin India Flexi Cap Fund - Direct - Growth", "Franklin India Flexi Cap Fund-Direct-Growth"]},
    "Quant Flexi Cap": {"category": "Flexi Cap", "aliases": ["quant Flexi Cap Fund - Direct Plan Growth", "Quant Flexi Cap Fund Direct Plan Growth"]},
    # Large & Mid Cap
    "Motilal Oswal Large & Midcap": {"category": "Large & Mid Cap", "aliases": ["Motilal Oswal Large and Midcap Fund-Direct Plan-Growth Option"]},
    "ICICI Pru Large & Mid Cap": {"category": "Large & Mid Cap", "aliases": ["ICICI Prudential Large & Mid Cap Fund - Direct Plan Growth"]},
    "HDFC Large & Mid Cap": {"category": "Large & Mid Cap", "aliases": ["HDFC Large and Mid Cap Fund - Direct Plan - Growth Option"]},
    "Bandhan Core Equity": {"category": "Large & Mid Cap", "aliases": ["Bandhan Core Equity Fund-Direct Plan-Growth", "IDFC Core Equity Fund - Direct Plan - Growth"]},
    "Edelweiss Large & Mid Cap": {"category": "Large & Mid Cap", "aliases": ["Edelweiss Large & Mid Cap Fund - Direct Plan - Growth Option"]},
    # Mid Cap
    "Motilal Oswal Midcap": {"category": "Mid Cap", "aliases": ["Motilal Oswal Midcap Fund-Direct Plan-Growth Option"]},
    "HDFC Mid-Cap Opportunities": {"category": "Mid Cap", "aliases": ["HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth Option"]},
    "Nippon India Growth Mid Cap": {"category": "Mid Cap", "aliases": ["Nippon India Growth Fund - Direct Plan Growth Plan", "Nippon India Growth Fund - Direct Plan - Growth Plan"]},
    "Kotak Midcap": {"category": "Mid Cap", "aliases": ["Kotak Midcap Fund - Direct Plan - Growth", "Kotak Emerging Equity Scheme - Direct Plan - Growth"]},
    "Invesco India Mid Cap": {"category": "Mid Cap", "aliases": ["Invesco India Mid Cap Fund - Direct Plan - Growth"]},
    # Small Cap
    "Nippon India Small Cap": {"category": "Small Cap", "aliases": ["Nippon India Small Cap Fund - Direct Plan - Growth Plan"]},
    "Bandhan Small Cap": {"category": "Small Cap", "aliases": ["Bandhan Small Cap Fund-Direct Plan-Growth"]},
    "SBI Small Cap": {"category": "Small Cap", "aliases": ["SBI Small Cap Fund - DIRECT PLAN - Growth"]},
    "HDFC Small Cap": {"category": "Small Cap", "aliases": ["HDFC Small Cap Fund - Direct Plan - Growth Option"]},
    "Franklin India Smaller Companies": {"category": "Small Cap", "aliases": ["Franklin India Smaller Companies Fund-Direct-Growth"]},
}
TARGETS = {name: meta["aliases"] for name, meta in FUND_UNIVERSE.items()}
CATEGORIES = ["Large Cap", "Flexi Cap", "Large & Mid Cap", "Mid Cap", "Small Cap"]
MIN_HISTORY_YEARS = 5

def req_json(url):
    r = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"}); r.raise_for_status(); return r.json()

@st.cache_data(ttl=86400, show_spinner=False)
def catalogue():
    return req_json("https://api.mfapi.in/mf")

@st.cache_data(ttl=21600, show_spinner=False)
def nav_history(code):
    raw=req_json(f"https://api.mfapi.in/mf/{code}")
    x=pd.DataFrame(raw.get("data",[]));
    if x.empty: return pd.Series(dtype=float)
    x["date"]=pd.to_datetime(x["date"],dayfirst=True,errors="coerce"); x["nav"]=pd.to_numeric(x["nav"],errors="coerce")
    return x.dropna().drop_duplicates("date").sort_values("date").set_index("date")["nav"]

def resolve_targets(cat):
    names=pd.DataFrame(cat)
    if names.empty or "schemeName" not in names or "schemeCode" not in names: return {}
    scheme_names=names.schemeName.fillna("").str.lower()
    out={}
    for short, wishes in TARGETS.items():
        hit=pd.DataFrame()
        for w in wishes:
            hit=names[scheme_names==w.lower()]
            if not hit.empty: break
        if hit.empty:
            tokens=[t for t in short.lower().replace("&"," ").split() if len(t)>3 and t not in {"india","fund"}]
            hit=names[scheme_names.apply(lambda s: all(t in s for t in tokens)) & scheme_names.str.contains("direct") & scheme_names.str.contains("growth")]
        if not hit.empty: out[short]=int(hit.iloc[0].schemeCode)
    return out

def load_all(selected):
    try: codes=resolve_targets(catalogue())
    except Exception: codes={}
    series={}; errors=[]
    for name in selected:
        try:
            s=nav_history(codes[name]);
            if len(s)>50: series[name]=s
            else: errors.append(name)
        except Exception: errors.append(name)
    return pd.concat(series,axis=1).sort_index().ffill(limit=5) if series else pd.DataFrame(), errors

def period_start(idx, label):
    end=idx.max(); years={"1 Year":1,"3 Years":3,"5 Years":5}.get(label)
    if years: return end-pd.DateOffset(years=years)
    if label=="YTD": return pd.Timestamp(end.year,1,1)
    return idx.min()

def sliced(nav,label):
    return nav.loc[nav.index>=period_start(nav.index,label)].dropna(how="all")

def cagr(s):
    s=s.dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return (s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else np.nan

def max_dd(s):
    w=s/s.iloc[0]; return (w/w.cummax()-1).min()

def history_years(s):
    s=s.dropna()
    return (s.index[-1]-s.index[0]).days/365.25 if len(s)>1 else 0

def rolling_consistency(s, years=3):
    """Share of rolling periods with a positive annualised return."""
    s=s.dropna()
    window=252*years
    if len(s)<=window: return np.nan
    rolling=(s/s.shift(window))**(1/years)-1
    return (rolling.dropna()>0).mean()

def percentile_score(x, higher_is_better=True):
    x=x.replace([np.inf,-np.inf],np.nan)
    if x.notna().sum()==0: return pd.Series(0.5,index=x.index)
    filled=x.fillna(x.median())
    score=filled.rank(pct=True,method="average")
    return score if higher_is_better else 1-score+1/len(score)

def metrics(nav):
    rows=[]
    for n in nav:
        s=nav[n].dropna(); r=s.pct_change().dropna(); downside=r[r<0].std()*np.sqrt(252)
        ann=r.mean()*252; vol=r.std()*np.sqrt(252); dd=max_dd(s)
        rows.append([n,cagr(s),ann,vol,ann/vol if vol else np.nan,ann/downside if downside else np.nan,downside,dd,rolling_consistency(s),r.quantile(.05),r[r<=r.quantile(.05)].mean()])
    return pd.DataFrame(rows,columns=["Fund","CAGR","Annual Return","Volatility","Sharpe*","Sortino*","Downside Risk","Max Drawdown","Rolling Consistency","Daily VaR 95%","Daily CVaR 95%"]).set_index("Fund")

def selection_score(nav):
    """Five-year category-relative score using the published methodology."""
    five=sliced(nav,"5 Years")
    base=metrics(five)
    base["Category"]=[FUND_UNIVERSE[n]["category"] for n in base.index]
    base["History (years)"]=[history_years(nav[n]) for n in base.index]
    base["Eligible"]=(base["History (years)"]>=MIN_HISTORY_YEARS)
    parts=[]
    for _,g in base.groupby("Category",sort=False):
        s=pd.DataFrame(index=g.index)
        s["5Y CAGR score"]=percentile_score(g["CAGR"])*20
        s["Sharpe score"]=percentile_score(g["Sharpe*"])*20
        s["Rolling consistency score"]=percentile_score(g["Rolling Consistency"])*20
        s["Downside-risk score"]=percentile_score(g["Downside Risk"],False)*15
        # Max drawdown is negative: a value closer to zero is better.
        s["Drawdown score"]=percentile_score(g["Max Drawdown"])*15
        # MFAPI does not publish AUM. Keep the 10-point component neutral and
        # disclose it rather than presenting an invented live AUM value.
        s["AUM score (neutral)"]=5.0
        parts.append(s)
    scores=pd.concat(parts) if parts else pd.DataFrame(index=base.index)
    scores["Composite / 100"]=scores.sum(axis=1)
    return base.join(scores).sort_values(["Category","Composite / 100"],ascending=[True,False])

def fmt_pct(x): return "—" if pd.isna(x) else f"{x:.2%}"
def chart(fig,h=460):
    fig.update_layout(height=h,margin=dict(l=20,r=20,t=55,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="white",font=dict(color=NAVY2),title_font=dict(color=NAVY2,family="Playfair Display"),legend_title_text="")
    return fig
def kpi(label,value): st.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div></div>',unsafe_allow_html=True)

st.markdown(f'<div class="hero"><h1>📈 Top 25 Mutual Fund Performance Analytics</h1><p><b>Mountain Path Academy</b> · Five categories · Five-year eligibility · Transparent quantitative ranking · Updated {date.today():%d %B %Y}</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📈 Analysis Controls")
    selected_categories=st.multiselect("Fund categories",CATEGORIES,default=CATEGORIES)
    available=[n for n,v in FUND_UNIVERSE.items() if v["category"] in selected_categories]
    chosen=st.multiselect("Fund universe",available,default=available)
    horizon=st.selectbox("Ranking horizon",["1 Year","3 Years","5 Years","YTD","Since Available"],index=1)
    primary=st.selectbox("Detailed fund",chosen or list(TARGETS))
    st.markdown(f'<div class="pill">Selected: {primary}</div>',unsafe_allow_html=True)
    investment=st.number_input("Lump-sum investment (₹)",10000,10000000,100000,10000)
    sip=st.number_input("Monthly SIP (₹)",500,1000000,10000,500)
    if st.button("↻ Refresh live NAV data",use_container_width=True): st.cache_data.clear(); st.rerun()
    st.markdown("---\n**Prof. V. Ravichandran**  \nFounder, The Mountain Path Academy  \n[Academy](https://themountainpathacademy.com/) · [LinkedIn](https://www.linkedin.com/in/trichyravis/) · [GitHub](https://github.com/trichyravis)")

if not chosen: st.warning("Select at least one fund from the sidebar."); st.stop()
with st.spinner("Loading latest mutual-fund NAV history…"):
    nav,failed=load_all(chosen)
if nav.empty:
    st.error("Live NAV data could not be loaded. Please use Refresh after checking internet access."); st.stop()
if failed: st.warning("Unavailable funds skipped: "+", ".join(failed))
short_history=[n for n in nav if history_years(nav[n])<MIN_HISTORY_YEARS]
if short_history:
    st.warning("Excluded for having less than five years of available NAV history: "+", ".join(short_history))
    nav=nav.drop(columns=short_history)
if nav.empty:
    st.error("None of the selected funds currently meets the minimum five-year NAV-history rule."); st.stop()

pnav=sliced(nav,horizon); m=metrics(pnav).sort_values("CAGR",ascending=False); primary=primary if primary in nav else nav.columns[0]
best=m.index[0]; rank=int(m.index.get_loc(primary)+1) if primary in m.index else 0
c1,c2,c3,c4,c5=st.columns(5)
with c1:kpi("Period leader",best)
with c2:kpi("Leader CAGR",fmt_pct(m.iloc[0]["CAGR"]))
with c3:kpi("Lowest volatility",m["Volatility"].idxmin())
with c4:kpi("Best Sharpe*",m["Sharpe*"].idxmax())
with c5:kpi(f"{primary} rank",f"#{rank} of {len(m)}")

tabs=st.tabs(["Executive Dashboard","Returns","Risk Analytics","Rolling Returns","SIP & Lump Sum","Correlation","Fund Detail","Selection & Ranking","Methodology","How to Navigate"])

with tabs[0]:
    st.subheader(f"Performance snapshot · {horizon}")
    norm=pnav.div(pnav.apply(lambda s:s.dropna().iloc[0] if not s.dropna().empty else np.nan))*100
    st.plotly_chart(chart(px.line(norm,title="Growth of ₹100 (NAV-normalised)",labels={"value":"Indexed wealth","date":"Date"})),use_container_width=True)
    a,b=st.columns(2)
    with a: st.plotly_chart(chart(px.bar(m.reset_index(),x="Fund",y="CAGR",color="CAGR",color_continuous_scale=["#A7C7E7",GOLD,NAVY2],title="CAGR ranking")),use_container_width=True)
    with b: st.plotly_chart(chart(px.scatter(m.reset_index(),x="Volatility",y="CAGR",size=m["Sharpe*"].abs().fillna(0)+.1,color="Sharpe*",hover_name="Fund",title="Risk–return map",color_continuous_scale="Blues")),use_container_width=True)
    st.caption("*Sharpe and Sortino are educational excess-return proxies using a 0% risk-free rate.")

with tabs[1]:
    st.subheader("Trailing and calendar-year returns")
    horizons={"1Y":1,"3Y":3,"5Y":5}
    tr={}
    for n in nav:
        tr[n]={k:cagr(nav[n].loc[nav.index>=nav.index.max()-pd.DateOffset(years=y)]) for k,y in horizons.items()}
    trailing=pd.DataFrame(tr).T
    st.dataframe(trailing.style.format("{:.2%}"),use_container_width=True)
    yr=nav.resample("YE").last().pct_change(); yr.index=yr.index.year
    st.plotly_chart(chart(px.bar(yr.reset_index().melt("date"),x="date",y="value",color="variable",barmode="group",title="Calendar-year NAV returns",labels={"date":"Year","value":"Return","variable":"Fund"}),520),use_container_width=True)

with tabs[2]:
    st.subheader("Risk, downside and drawdown diagnostics")
    st.dataframe(m.style.format({c:"{:.2%}" for c in ["CAGR","Annual Return","Volatility","Downside Risk","Max Drawdown","Rolling Consistency","Daily VaR 95%","Daily CVaR 95%"]}).format({"Sharpe*":"{:.2f}","Sortino*":"{:.2f}"}),use_container_width=True)
    dd=pnav.div(pnav.cummax())-1
    st.plotly_chart(chart(px.line(dd,title="Drawdown from prior NAV peak",labels={"value":"Drawdown","date":"Date"}),500),use_container_width=True)

with tabs[3]:
    st.subheader("Rolling 1-year return consistency")
    roll=(nav/nav.shift(252)-1).dropna(how="all")
    st.plotly_chart(chart(px.line(roll,title="Rolling 252-trading-day return",labels={"value":"Rolling return","date":"Date"}),500),use_container_width=True)
    summary=pd.DataFrame({"Average":roll.mean(),"Minimum":roll.min(),"Maximum":roll.max(),"Positive periods":(roll>0).mean()})
    st.dataframe(summary.style.format("{:.2%}"),use_container_width=True)

with tabs[4]:
    st.subheader("Investment outcome simulator")
    wealth=pnav.div(pnav.apply(lambda s:s.dropna().iloc[0]))*investment
    lumpsum=wealth.iloc[-1].sort_values(ascending=False)
    monthly=nav.resample("ME").last().pct_change().fillna(0)
    sip_values={}
    for n in monthly:
        v=0
        for r in monthly[n].dropna(): v=(v+sip)*(1+r)
        sip_values[n]=v
    sim=pd.DataFrame({"Lump-sum final value":lumpsum,"Total SIP invested":sip*len(monthly),"SIP final value":pd.Series(sip_values)}).dropna()
    st.dataframe(sim.style.format("₹{:,.0f}"),use_container_width=True)
    st.plotly_chart(chart(px.bar(sim.reset_index(),x="index",y=["Lump-sum final value","SIP final value"],barmode="group",title="Simulated final values",labels={"index":"Fund","value":"₹"}),500),use_container_width=True)

with tabs[5]:
    st.subheader("Diversification and correlation")
    corr=pnav.pct_change(fill_method=None).corr()
    st.plotly_chart(chart(px.imshow(corr,text_auto=".2f",color_continuous_scale="RdBu_r",zmin=-1,zmax=1,title="Daily return correlation matrix"),620),use_container_width=True)
    st.markdown('<div class="note">High correlation means funds may behave similarly. Holding many highly correlated funds does not necessarily create meaningful diversification.</div>',unsafe_allow_html=True)

with tabs[6]:
    st.subheader(primary)
    s=nav[primary].dropna(); r=s.pct_change().dropna(); pm=m.loc[primary] if primary in m.index else metrics(s.to_frame(primary)).iloc[0]
    q1,q2,q3,q4=st.columns(4)
    with q1:kpi("Latest NAV",f"₹{s.iloc[-1]:,.2f}")
    with q2:kpi("CAGR",fmt_pct(pm["CAGR"]))
    with q3:kpi("Volatility",fmt_pct(pm["Volatility"]))
    with q4:kpi("Max drawdown",fmt_pct(pm["Max Drawdown"]))
    st.plotly_chart(chart(px.line(s,title=f"{primary} NAV history",labels={"value":"NAV","date":"Date"}),470),use_container_width=True)
    st.plotly_chart(chart(px.histogram(r,nbins=60,title="Daily-return distribution",marginal="box",color_discrete_sequence=[BLUE]),400),use_container_width=True)

with tabs[7]:
    st.subheader("Five-year category-relative selection and ranking")
    selection=selection_score(nav)
    selection["Category Rank"]=selection.groupby("Category")["Composite / 100"].rank(method="min",ascending=False).astype(int)
    eligible=selection[selection["Eligible"]].sort_values(["Category","Category Rank"])
    show_cols=["Category","Category Rank","History (years)","CAGR","Sharpe*","Rolling Consistency","Downside Risk","Max Drawdown","Composite / 100"]
    st.dataframe(
        eligible[show_cols].style.format({
            "History (years)":"{:.1f}","CAGR":"{:.2%}","Sharpe*":"{:.2f}",
            "Rolling Consistency":"{:.2%}","Downside Risk":"{:.2%}",
            "Max Drawdown":"{:.2%}","Composite / 100":"{:.1f}"
        }),use_container_width=True
    )
    category_choice=st.selectbox("Scorecard chart category",["All Categories"]+CATEGORIES)
    plotted=eligible if category_choice=="All Categories" else eligible[eligible["Category"]==category_choice]
    st.plotly_chart(chart(px.bar(plotted.reset_index(),x="Fund",y="Composite / 100",color="Category",title="Transparent multi-factor scorecard"),540),use_container_width=True)
    export=m.join(selection.drop(columns=["CAGR","Annual Return","Volatility","Sharpe*","Sortino*","Downside Risk","Max Drawdown","Rolling Consistency","Daily VaR 95%","Daily CVaR 95%"],errors="ignore")).reset_index()
    csv=export.to_csv(index=False).encode()
    bio=io.BytesIO()
    with pd.ExcelWriter(bio,engine="openpyxl") as w:
        export.to_excel(w,index=False,sheet_name="Ranking"); nav.to_excel(w,sheet_name="NAV History"); pnav.pct_change().to_excel(w,sheet_name="Daily Returns")
        pd.DataFrame([
            ["Minimum NAV history","5 years","Eligibility filter"],
            ["Plan type","Direct–Growth","Eligibility filter"],
            ["Category representation","5 funds × 5 categories","Universe construction"],
            ["Five-year CAGR","20%","Higher is better"],
            ["Sharpe ratio","20%","Higher is better; 0% risk-free proxy"],
            ["Rolling-return consistency","20%","Share of positive 3-year rolling annualised returns"],
            ["Downside risk","15%","Lower is better"],
            ["Maximum drawdown","15%","Closer to zero is better"],
            ["Category-wise AUM","10%","Neutral pending a verified scheme-AUM source"],
        ],columns=["Criterion","Rule / Weight","Treatment"]).to_excel(w,index=False,sheet_name="Methodology")
    d1,d2=st.columns(2)
    d1.download_button("⬇ Download ranking CSV",csv,"top_25_mutual_fund_ranking.csv","text/csv",use_container_width=True)
    d2.download_button("⬇ Download complete Excel",bio.getvalue(),"top_25_mutual_fund_analytics.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    st.caption("Funds are scored within their own category. The composite score is an educational model—not a recommendation or official rating.")

with tabs[8]:
    st.subheader("Selection methodology and interpretation")
    st.markdown("""
### Universe construction

- **25 diversified-equity schemes:** five each from Large Cap, Flexi Cap, Large & Mid Cap, Mid Cap and Small Cap.
- **Plan rule:** Direct–Growth variants only, avoiding mixing Regular plans or payout options.
- **History rule:** at least five years of NAV history available from the public data feed.
- **Category rule:** funds are ranked against peers in the same category; a small-cap return is not treated as directly comparable with a large-cap return.

### Composite score

| Quantitative criterion | Weight | Scoring direction |
|---|---:|---|
| Five-year CAGR | 20% | Higher is better |
| Sharpe ratio | 20% | Higher is better |
| Positive three-year rolling-return consistency | 20% | Higher is better |
| Annualised downside risk | 15% | Lower is better |
| Maximum drawdown | 15% | A smaller loss is better |
| Category-wise AUM | 10% | Neutral until verified scheme AUM is supplied |

Each measured factor is converted to a **within-category percentile score**. This avoids allowing the naturally higher risk and return of small-cap funds to dominate lower-risk categories.

### Important AUM disclosure

The live MFAPI/AMFI-linked NAV endpoint used by this project does not provide scheme-level AUM. The model therefore assigns every fund the same neutral 5/10 AUM contribution instead of displaying or scoring an unverified number. Once a dated AMC/AMFI AUM file is added, the app can calculate the AUM percentile automatically without changing the other weights.
""")
    st.info("The displayed 25-fund universe is a balanced educational comparison set. It is not a claim that these are permanently the 25 best funds in India.")

with tabs[9]:
    st.subheader("How to navigate this app")
    st.markdown("""
1. Select the fund universe in the sidebar and choose a ranking horizon.
2. Select one fund for detailed diagnosis; the gold confirmation pill shows the active choice.
3. Start with **Executive Dashboard** for the ranking, indexed wealth and risk–return position.
4. Use **Returns** to compare trailing CAGR and calendar-year performance.
5. Use **Risk Analytics** for volatility, Sharpe, Sortino, VaR, CVaR and drawdowns.
6. Use **Rolling Returns** to judge consistency instead of relying on one start/end date.
7. Enter lump-sum and SIP amounts to run the educational investment simulation.
8. Review **Correlation** before assuming that several funds provide diversification.
9. Review **Selection & Ranking** for the category-relative composite score and downloads.
10. Read **Methodology** for eligibility rules, factor weights and the AUM data limitation.

**Interpretation caution:** Past NAV performance does not assure future returns. Compare funds within suitable categories, review expense ratios, exit loads, taxes, portfolio concentration and investment objectives before taking a decision.
""")
    st.info("Data source: public NAV history supplied through MFAPI/AMFI-linked records. NAV is not adjusted here for investor-specific tax, load or expense differences beyond what is reflected in the published plan NAV.")

st.markdown("""<div class="footer"><b>The Mountain Path Academy</b><br>Developed by Prof. V. Ravichandran · Visiting Professor & Professor of Practice at leading business schools<br><a href="https://themountainpathacademy.com/">Academy</a> · <a href="https://www.linkedin.com/in/trichyravis/">LinkedIn</a> · <a href="https://github.com/trichyravis">GitHub</a><br><small>Educational analytics project · Not investment advice · © 2026 The Mountain Path Academy</small></div>""",unsafe_allow_html=True)
