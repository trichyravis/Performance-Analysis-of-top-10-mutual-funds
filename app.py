from __future__ import annotations

import io
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Top 10 Mutual Fund Analytics | Mountain Path Academy", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

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

TARGETS = {
    "Quant Small Cap": ["Quant Small Cap Fund Direct Plan Growth"],
    "Nippon India Small Cap": ["Nippon India Small Cap Fund - Direct Plan - Growth Plan"],
    "Motilal Oswal Midcap": ["Motilal Oswal Midcap Fund-Direct Plan-Growth Option"],
    "HDFC Mid-Cap Opportunities": ["HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth Option"],
    "Bandhan Small Cap": ["Bandhan Small Cap Fund-Direct Plan-Growth"],
    "SBI Small Cap": ["SBI Small Cap Fund - DIRECT PLAN - Growth"],
    "Franklin India Smaller Companies": ["Franklin India Smaller Companies Fund-Direct-Growth"],
    "Invesco India Mid Cap": ["Invesco India Mid Cap Fund - Direct Plan - Growth"],
    "HSBC Small Cap": ["HSBC Small Cap Fund - Direct Growth"],
    "ICICI Pru Infrastructure": ["ICICI Prudential Infrastructure Fund - Direct Plan Growth"],
}

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
    out={}
    for short, wishes in TARGETS.items():
        hit=pd.DataFrame()
        for w in wishes:
            hit=names[names.schemeName.str.lower()==w.lower()]
            if not hit.empty: break
        if hit.empty:
            tokens=[t for t in short.lower().split() if len(t)>3]
            hit=names[names.schemeName.str.lower().apply(lambda s: all(t in s for t in tokens)) & names.schemeName.str.lower().str.contains("direct") & names.schemeName.str.lower().str.contains("growth")]
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

def metrics(nav):
    rows=[]
    for n in nav:
        s=nav[n].dropna(); r=s.pct_change().dropna(); downside=r[r<0].std()*np.sqrt(252)
        ann=r.mean()*252; vol=r.std()*np.sqrt(252); dd=max_dd(s)
        rows.append([n,cagr(s),ann,vol,ann/vol if vol else np.nan,ann/downside if downside else np.nan,dd,r.quantile(.05),r[r<=r.quantile(.05)].mean()])
    return pd.DataFrame(rows,columns=["Fund","CAGR","Annual Return","Volatility","Sharpe*","Sortino*","Max Drawdown","Daily VaR 95%","Daily CVaR 95%"]).set_index("Fund")

def fmt_pct(x): return "—" if pd.isna(x) else f"{x:.2%}"
def chart(fig,h=460):
    fig.update_layout(height=h,margin=dict(l=20,r=20,t=55,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="white",font=dict(color=NAVY2),title_font=dict(color=NAVY2,family="Playfair Display"),legend_title_text="")
    return fig
def kpi(label,value): st.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div></div>',unsafe_allow_html=True)

st.markdown(f'<div class="hero"><h1>📈 Top 10 Mutual Fund Performance Analytics</h1><p><b>Mountain Path Academy</b> · Dynamic NAV-based ranking, risk diagnostics and investment simulation · Updated {date.today():%d %B %Y}</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📈 Analysis Controls")
    chosen=st.multiselect("Fund universe",list(TARGETS),default=list(TARGETS))
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

pnav=sliced(nav,horizon); m=metrics(pnav).sort_values("CAGR",ascending=False); primary=primary if primary in nav else nav.columns[0]
best=m.index[0]; rank=int(m.index.get_loc(primary)+1) if primary in m.index else 0
c1,c2,c3,c4,c5=st.columns(5)
with c1:kpi("Period leader",best)
with c2:kpi("Leader CAGR",fmt_pct(m.iloc[0]["CAGR"]))
with c3:kpi("Lowest volatility",m["Volatility"].idxmin())
with c4:kpi("Best Sharpe*",m["Sharpe*"].idxmax())
with c5:kpi(f"{primary} rank",f"#{rank} of {len(m)}")

tabs=st.tabs(["Executive Dashboard","Returns","Risk Analytics","Rolling Returns","SIP & Lump Sum","Correlation","Fund Detail","Ranking & Downloads","How to Navigate"])

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
    st.dataframe(trailing.style.format("{:.2%}").background_gradient(cmap="YlGnBu"),use_container_width=True)
    yr=nav.resample("YE").last().pct_change(); yr.index=yr.index.year
    st.plotly_chart(chart(px.bar(yr.reset_index().melt("date"),x="date",y="value",color="variable",barmode="group",title="Calendar-year NAV returns",labels={"date":"Year","value":"Return","variable":"Fund"}),520),use_container_width=True)

with tabs[2]:
    st.subheader("Risk, downside and drawdown diagnostics")
    st.dataframe(m.style.format({c:"{:.2%}" for c in ["CAGR","Annual Return","Volatility","Max Drawdown","Daily VaR 95%","Daily CVaR 95%"]}).format({"Sharpe*":"{:.2f}","Sortino*":"{:.2f}"}).background_gradient(cmap="YlGnBu",subset=["CAGR","Sharpe*"]),use_container_width=True)
    dd=pnav.div(pnav.cummax())-1
    st.plotly_chart(chart(px.line(dd,title="Drawdown from prior NAV peak",labels={"value":"Drawdown","date":"Date"}),500),use_container_width=True)

with tabs[3]:
    st.subheader("Rolling 1-year return consistency")
    roll=(nav/nav.shift(252)-1).dropna(how="all")
    st.plotly_chart(chart(px.line(roll,title="Rolling 252-trading-day return",labels={"value":"Rolling return","date":"Date"}),500),use_container_width=True)
    summary=pd.DataFrame({"Average":roll.mean(),"Minimum":roll.min(),"Maximum":roll.max(),"Positive periods":(roll>0).mean()})
    st.dataframe(summary.style.format("{:.2%}").background_gradient(cmap="YlGnBu"),use_container_width=True)

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
    st.dataframe(sim.style.format("₹{:,.0f}").background_gradient(cmap="YlGnBu",subset=["Lump-sum final value","SIP final value"]),use_container_width=True)
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
    st.subheader("Composite educational scorecard")
    score=pd.DataFrame(index=m.index)
    for col,weight,positive in [("CAGR",35,True),("Sharpe*",25,True),("Sortino*",15,True),("Volatility",10,False),("Max Drawdown",15,True)]:
        x=m[col].replace([np.inf,-np.inf],np.nan).fillna(m[col].median()); z=(x-x.min())/(x.max()-x.min()) if x.max()!=x.min() else x*0+1
        score[col+" score"]=(z if positive else 1-z)*weight
    score["Composite / 100"]=score.sum(axis=1); score=score.sort_values("Composite / 100",ascending=False)
    st.plotly_chart(chart(px.bar(score.reset_index(),x="Fund",y="Composite / 100",color="Composite / 100",color_continuous_scale=["#A7C7E7",GOLD,NAVY2],title="Multi-factor ranking"),500),use_container_width=True)
    export=m.join(score[["Composite / 100"]]).reset_index()
    csv=export.to_csv(index=False).encode()
    bio=io.BytesIO()
    with pd.ExcelWriter(bio,engine="openpyxl") as w:
        export.to_excel(w,index=False,sheet_name="Ranking"); nav.to_excel(w,sheet_name="NAV History"); pnav.pct_change().to_excel(w,sheet_name="Daily Returns")
    d1,d2=st.columns(2)
    d1.download_button("⬇ Download ranking CSV",csv,"mutual_fund_ranking.csv","text/csv",use_container_width=True)
    d2.download_button("⬇ Download complete Excel",bio.getvalue(),"mutual_fund_analytics.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    st.caption("The composite score is an educational model—not a recommendation or official fund rating.")

with tabs[8]:
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
9. Download the complete Excel workbook from **Ranking & Downloads** for classroom work.

**Interpretation caution:** Past NAV performance does not assure future returns. Compare funds within suitable categories, review expense ratios, exit loads, taxes, portfolio concentration and investment objectives before taking a decision.
""")
    st.info("Data source: public NAV history supplied through MFAPI/AMFI-linked records. NAV is not adjusted here for investor-specific tax, load or expense differences beyond what is reflected in the published plan NAV.")

st.markdown("""<div class="footer"><b>The Mountain Path Academy</b><br>Developed by Prof. V. Ravichandran · Visiting Professor & Professor of Practice at leading business schools<br><a href="https://themountainpathacademy.com/">Academy</a> · <a href="https://www.linkedin.com/in/trichyravis/">LinkedIn</a> · <a href="https://github.com/trichyravis">GitHub</a><br><small>Educational analytics project · Not investment advice · © 2026 The Mountain Path Academy</small></div>""",unsafe_allow_html=True)
