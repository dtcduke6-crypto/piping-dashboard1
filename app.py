import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Piping & Structure Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F0F4F8; }
    .block-container { padding-top: 1rem; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #2E75B6;
        margin-bottom: 10px;
    }
    .metric-card.green  { border-left-color: #70AD47; }
    .metric-card.orange { border-left-color: #ED7D31; }
    .metric-card.red    { border-left-color: #FF0000; }
    .metric-card.purple { border-left-color: #7030A0; }
    .metric-title  { font-size:13px; color:#6B7280; font-weight:600; margin:0; }
    .metric-value  { font-size:32px; font-weight:800; margin:4px 0 0 0; }
    .metric-sub    { font-size:12px; color:#9CA3AF; margin:2px 0 0 0; }
    .section-title {
        font-size:18px; font-weight:700; color:#1F3864;
        border-bottom:3px solid #2E75B6;
        padding-bottom:6px; margin:20px 0 14px 0;
    }
    div[data-testid="stMetricValue"] { font-size: 28px; }
    .stTabs [data-baseweb="tab"] { font-size:15px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ──────────────────────────────────────────────────────────────────────
# Activities with Plan%, Actual%, Unit, Total Qty, Actual Qty
activities = [
    # name, discipline, plan%, actual%, unit, total_qty, actual_qty, plan_start, plan_finish, category
    ("Isometric Drawing Review",      "PIPING", 100, 100, "Nos",    45,   45,   "01-May-25","07-May-25","A. Piping Fab"),
    ("Material Procurement",          "PIPING", 100, 100, "Lot",    1,    1,    "08-May-25","21-May-25","A. Piping Fab"),
    ("Pipe Cutting & Beveling",       "PIPING", 85,  80,  "Jt",     800,  680,  "22-May-25","01-Jun-25","A. Piping Fab"),
    ("Pipe Fitting & Alignment",      "PIPING", 75,  70,  "Spool",  250,  195,  "05-Jun-25","17-Jun-25","A. Piping Fab"),
    ("Welding (Shop)",                "PIPING", 65,  60,  "Jt",     800,  510,  "12-Jun-25","03-Jul-25","A. Piping Fab"),
    ("NDT / Radiography",             "QA/QC",  50,  45,  "Jt",     640,  420,  "03-Jul-25","10-Jul-25","A. Piping Fab"),
    ("PWHT",                          "PIPING", 40,  38,  "Jt",     120,  80,   "10-Jul-25","15-Jul-25","A. Piping Fab"),
    ("Hydro Test (Shop)",             "PIPING", 30,  28,  "Spool",  250,  90,   "17-Jul-25","22-Jul-25","A. Piping Fab"),
    ("Spool Dispatch",                "PIPING", 25,  22,  "Spool",  250,  85,   "24-Jul-25","27-Jul-25","A. Piping Fab"),
    ("GA Drawing Review",             "CIVIL",  100, 100, "Nos",    30,   30,   "29-May-25","03-Jun-25","B. Structure Fab"),
    ("Cutting & Marking",             "CIVIL",  80,  75,  "MT",     120,  88,   "05-Jun-25","13-Jun-25","B. Structure Fab"),
    ("Assembly & Fit-up",             "CIVIL",  62,  58,  "MT",     120,  75,   "12-Jun-25","24-Jun-25","B. Structure Fab"),
    ("Welding of Structure",          "CIVIL",  55,  50,  "MT",     120,  65,   "26-Jun-25","10-Jul-25","B. Structure Fab"),
    ("Blasting & Painting (Shop)",    "CIVIL",  35,  30,  "Sq.M",   2400, 1520, "17-Jul-25","24-Jul-25","B. Structure Fab"),
    ("Support/Hanger Installation",   "PIPING", 55,  50,  "Nos",    380,  210,  "24-Jul-25","03-Aug-25","C. Piping Erection"),
    ("Spool Erection & Alignment",    "PIPING", 20,  18,  "Spool",  250,  55,   "07-Aug-25","28-Aug-25","C. Piping Erection"),
    ("Field Welding",                 "PIPING", 18,  15,  "Jt",     400,  72,   "14-Aug-25","04-Sep-25","C. Piping Erection"),
    ("Field NDT / DP Test",           "QA/QC",  8,   6,   "Jt",     320,  52,   "04-Sep-25","11-Sep-25","C. Piping Erection"),
    ("Pressure / Hydro Test (Field)", "PIPING", 5,   3,   "System", 8,    2,    "11-Sep-25","18-Sep-25","C. Piping Erection"),
    ("Insulation & Cladding",         "PIPING", 2,   0,   "Sq.M",   1800, 0,    "18-Sep-25","25-Sep-25","C. Piping Erection"),
    ("Foundation Check & Grouting",   "CIVIL",  80,  75,  "Nos",    48,   38,   "31-Jul-25","05-Aug-25","D. Structure Erection"),
    ("Column Erection",               "CIVIL",  60,  55,  "MT",     45,   28,   "07-Aug-25","17-Aug-25","D. Structure Erection"),
    ("Beam & Grating Installation",   "CIVIL",  20,  18,  "MT",     55,   12,   "21-Aug-25","02-Sep-25","D. Structure Erection"),
    ("Ladder / Handrail",             "CIVIL",  5,   0,   "RMT",    320,  0,    "04-Sep-25","12-Sep-25","D. Structure Erection"),
    ("Final Alignment & Leveling",    "CIVIL",  2,   0,   "Nos",    48,   0,    "18-Sep-25","23-Sep-25","D. Structure Erection"),
    ("Pre-comm Walk-through",         "QA/QC",  1,   0,   "Nos",    1,    0,    "25-Sep-25","28-Sep-25","E. QA/QC & Handover"),
    ("Punch List Clearance",          "QA/QC",  1,   0,   "Nos",    1,    0,    "02-Oct-25","07-Oct-25","E. QA/QC & Handover"),
    ("As-built Documentation",        "PIPING", 1,   0,   "Set",    1,    0,    "02-Oct-25","07-Oct-25","E. QA/QC & Handover"),
    ("Final Inspection (Client/PMC)", "QA/QC",  0,   0,   "Nos",    1,    0,    "09-Oct-25","12-Oct-25","E. QA/QC & Handover"),
    ("Mechanical Completion Cert.",   "ALL",    0,   0,   "Doc",    1,    0,    "16-Oct-25","18-Oct-25","E. QA/QC & Handover"),
]

df = pd.DataFrame(activities, columns=[
    "Activity","Discipline","Plan%","Actual%","Unit",
    "Total_Qty","Actual_Qty","Plan_Start","Plan_Finish","Category"
])
df["Balance_Qty"] = df["Total_Qty"] - df["Actual_Qty"]
df["Qty_Pct"]     = (df["Actual_Qty"] / df["Total_Qty"] * 100).round(1)
df["Deviation"]   = df["Actual%"] - df["Plan%"]

# S-Curve Data
weeks = [f"W{i}" for i in range(1,25)]
plan_cum   = [2,4,6,9,12,16,20,25,30,36,42,48,54,60,65,70,75,79,83,87,90,94,97,100]
actual_cum = [1,3,5,8,10,14,17,22,27,33,39,45,50,56,60,65,70,74,78,82,86,90,94,97]

# Manpower
manpower_data = {
    "Trade":["Welder GTAW","Welder SMAW","Pipe Fitter","Struct. Fitter",
              "Rigger/Helper","Scaffolder","Grinder","Painter","QC Inspector","Supervisor"],
    "Planned":[12,10,8,6,8,6,10,4,2,3],
    "Actual": [10,9,8,6,8,5,9,3,2,3]
}
df_mp = pd.DataFrame(manpower_data)
df_mp["Variance"] = df_mp["Actual"] - df_mp["Planned"]

# DPR activity progress
dpr_data = {
    "Activity":["Pipe Spool Fab","Pipe Fitting","Pipe Welding","NDT/RT",
                 "Hydro Test","Structure Fab","Pipe Erection","Struct. Erection","Painting","Field Welding"],
    "Unit":["Spool","Spool","Jt","Jt","Spool","MT","Spool","MT","Sq.M","Jt"],
    "Total_Qty":[250,250,800,800,250,120,250,120,800,400],
    "Cum_Plan": [180,170,550,510,100,80,60,30,400,80],
    "Cum_Actual":[165,155,510,480,90,75,55,28,380,72],
    "Today_Plan":[8,8,25,20,10,5,10,4,30,15],
    "Today_Actual":[7,6,22,18,8,4,8,3,28,12],
}
df_dpr = pd.DataFrame(dpr_data)
df_dpr["Balance"]   = df_dpr["Total_Qty"] - df_dpr["Cum_Actual"]
df_dpr["Pct_Done"]  = (df_dpr["Cum_Actual"]/df_dpr["Total_Qty"]*100).round(1)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Project Control")
    st.markdown("**Fabrication & Erection**")
    st.markdown("---")
    st.markdown(f"📅 **Report Date:** {date.today().strftime('%d-%b-%Y')}")
    st.markdown("📍 **Project:** Piping & Structure")
    st.markdown("🏢 **Client:** ___________")
    st.markdown("---")

    disc_filter = st.multiselect(
        "Filter by Discipline",
        options=["PIPING","CIVIL","QA/QC","ALL"],
        default=["PIPING","CIVIL","QA/QC","ALL"]
    )
    cat_filter = st.multiselect(
        "Filter by Category",
        options=df["Category"].unique().tolist(),
        default=df["Category"].unique().tolist()
    )
    st.markdown("---")
    st.markdown("### 📊 Overall Progress")
    overall_plan   = round(df["Plan%"].mean(), 1)
    overall_actual = round(df["Actual%"].mean(), 1)
    st.progress(overall_actual/100)
    st.markdown(f"**Plan:** {overall_plan}% | **Actual:** {overall_actual}%")
    delta = overall_actual - overall_plan
    color = "🟢" if delta >= 0 else "🔴"
    st.markdown(f"{color} **Deviation: {delta:+.1f}%**")

# ─── FILTER DATA ───────────────────────────────────────────────────────────────
df_filtered = df[df["Discipline"].isin(disc_filter) & df["Category"].isin(cat_filter)]

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='color:#1F3864;font-size:28px;margin-bottom:4px;'>
🏗️ Fabrication & Erection — Project Dashboard
</h1>
<p style='color:#6B7280;font-size:14px;margin-top:0;'>
Micro Planning | DPR | Quantity Tracking | Resource Loading
</p>
""", unsafe_allow_html=True)

# ─── KPI CARDS ─────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)

total_qty_sum   = df["Total_Qty"].sum()
actual_qty_sum  = df["Actual_Qty"].sum()
balance_qty_sum = df["Balance_Qty"].sum()
overall_qty_pct = round(actual_qty_sum/total_qty_sum*100,1)

with c1:
    st.markdown(f"""<div class="metric-card">
    <p class="metric-title">📋 Total Activities</p>
    <p class="metric-value" style="color:#1F3864;">{len(df)}</p>
    <p class="metric-sub">Filtered: {len(df_filtered)}</p></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card green">
    <p class="metric-title">✅ Plan Progress</p>
    <p class="metric-value" style="color:#70AD47;">{overall_plan}%</p>
    <p class="metric-sub">Baseline Schedule</p></div>""", unsafe_allow_html=True)
with c3:
    act_color = "green" if overall_actual >= overall_plan else "orange" if overall_actual >= overall_plan*0.9 else "red"
    act_hex   = "#70AD47" if overall_actual >= overall_plan else "#ED7D31" if overall_actual >= overall_plan*0.9 else "#FF0000"
    st.markdown(f"""<div class="metric-card {act_color}">
    <p class="metric-title">🔨 Actual Progress</p>
    <p class="metric-value" style="color:{act_hex};">{overall_actual}%</p>
    <p class="metric-sub">As of today</p></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card purple">
    <p class="metric-title">📦 Total Qty</p>
    <p class="metric-value" style="color:#7030A0;">{total_qty_sum:,}</p>
    <p class="metric-sub">All units combined</p></div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="metric-card green">
    <p class="metric-title">✅ Actual Qty Done</p>
    <p class="metric-value" style="color:#70AD47;">{actual_qty_sum:,}</p>
    <p class="metric-sub">{overall_qty_pct}% of total</p></div>""", unsafe_allow_html=True)
with c6:
    st.markdown(f"""<div class="metric-card red">
    <p class="metric-title">⏳ Balance Qty</p>
    <p class="metric-value" style="color:#FF0000;">{balance_qty_sum:,}</p>
    <p class="metric-sub">Remaining to complete</p></div>""", unsafe_allow_html=True)

st.markdown("---")

# ─── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Micro Plan & Qty",
    "📊 S-Curve",
    "📋 DPR",
    "👷 Resource Loading",
    "🔧 Weld Summary"
])

# ══════════════════════════════════════════════════════
# TAB 1: MICRO PLAN + QTY TRACKING
# ══════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([3,2])

    with col_l:
        st.markdown('<div class="section-title">📅 Activity Progress (Plan vs Actual %)</div>', unsafe_allow_html=True)

        # Gantt-style bar chart (Plan vs Actual)
        fig_gantt = go.Figure()
        cats = df_filtered["Activity"].tolist()[::-1]
        plans   = df_filtered["Plan%"].tolist()[::-1]
        actuals = df_filtered["Actual%"].tolist()[::-1]

        fig_gantt.add_trace(go.Bar(
            name="Plan %", y=cats, x=plans,
            orientation='h', marker_color="#BDD7EE",
            text=[f"{v}%" for v in plans],
            textposition="inside", textfont=dict(color="#1E3A8A", size=9)
        ))
        fig_gantt.add_trace(go.Bar(
            name="Actual %", y=cats, x=actuals,
            orientation='h', marker_color="#70AD47",
            text=[f"{v}%" for v in actuals],
            textposition="inside", textfont=dict(color="white", size=9)
        ))
        fig_gantt.update_layout(
            barmode="overlay", height=max(500, len(cats)*22+60),
            margin=dict(l=10,r=10,t=10,b=10),
            xaxis=dict(title="Progress %", range=[0,110]),
            legend=dict(orientation="h", y=1.02, x=0),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">📦 Quantity Tracking</div>', unsafe_allow_html=True)

        # Qty progress per activity (horizontal bars)
        df_qty = df_filtered[df_filtered["Total_Qty"] > 1].copy()
        fig_qty = go.Figure()
        fig_qty.add_trace(go.Bar(
            name="Total Qty", y=df_qty["Activity"], x=df_qty["Total_Qty"],
            orientation='h', marker_color="#E5E7EB",
        ))
        fig_qty.add_trace(go.Bar(
            name="Actual Qty Done", y=df_qty["Activity"], x=df_qty["Actual_Qty"],
            orientation='h', marker_color="#ED7D31",
            text=[f"{v} {u}" for v,u in zip(df_qty["Actual_Qty"], df_qty["Unit"])],
            textposition="inside", textfont=dict(color="white", size=9)
        ))
        fig_qty.update_layout(
            barmode="overlay",
            height=max(450, len(df_qty)*22+60),
            margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(orientation="h", y=1.02),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="Quantity"
        )
        st.plotly_chart(fig_qty, use_container_width=True)

    # ── Detailed Table
    st.markdown('<div class="section-title">📋 Detailed Activity Table (Plan vs Actual)</div>', unsafe_allow_html=True)

    def color_deviation(val):
        if isinstance(val, (int,float)):
            if val >= 0: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
            elif val >= -5: return 'background-color:#FEF3C7;color:#92400E;font-weight:bold'
            else: return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
        return ''

    def color_qty_pct(val):
        try:
            v = float(str(val).replace('%',''))
            if v >= 80: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
            elif v >= 40: return 'background-color:#FEF3C7;color:#92400E;font-weight:bold'
            else: return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
        except: return ''

    display_cols = ["Activity","Category","Discipline","Plan%","Actual%","Deviation",
                    "Unit","Total_Qty","Actual_Qty","Balance_Qty","Qty_Pct"]
    df_show = df_filtered[display_cols].rename(columns={
        "Plan%":"Plan %","Actual%":"Actual %","Total_Qty":"Total Qty",
        "Actual_Qty":"Actual Qty","Balance_Qty":"Balance Qty","Qty_Pct":"Qty %"
    })
    df_show["Qty %"] = df_show["Qty %"].apply(lambda x: f"{x}%")

    styled = df_show.style\
        .applymap(color_deviation, subset=["Deviation"])\
        .applymap(color_qty_pct, subset=["Qty %"])\
        .set_properties(**{'text-align':'center'})\
        .format({"Plan %":"{:.0f}%","Actual %":"{:.0f}%","Deviation":"{:+.0f}%"})
    st.dataframe(styled, use_container_width=True, height=400)

# ══════════════════════════════════════════════════════
# TAB 2: S-CURVE
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">📊 S-Curve — Planned vs Actual Cumulative Progress</div>', unsafe_allow_html=True)

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Scatter(
        x=weeks, y=plan_cum, name="Plan %",
        mode="lines+markers",
        line=dict(color="#2E75B6", width=3, dash="dash"),
        marker=dict(size=7, symbol="circle"),
        fill="tozeroy", fillcolor="rgba(46,117,182,0.08)"
    ))
    fig_sc.add_trace(go.Scatter(
        x=weeks, y=actual_cum, name="Actual %",
        mode="lines+markers",
        line=dict(color="#ED7D31", width=3),
        marker=dict(size=8, symbol="circle-open", line=dict(width=2)),
        fill="tozeroy", fillcolor="rgba(237,125,49,0.10)"
    ))
    # Shade deviation area
    fig_sc.add_trace(go.Scatter(
        x=weeks+weeks[::-1],
        y=[max(0,a-p) for a,p in zip(actual_cum,plan_cum)] + [0]*len(weeks),
        fill="toself", fillcolor="rgba(112,173,71,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Ahead of Schedule", showlegend=True
    ))
    fig_sc.update_layout(
        height=420,
        yaxis=dict(title="Cumulative Progress %", range=[0,110], ticksuffix="%"),
        xaxis=dict(title="Week"),
        legend=dict(orientation="h", y=1.08),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10,r=10,t=30,b=10)
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    # S-Curve table
    st.markdown('<div class="section-title">📋 Week-wise Progress Table</div>', unsafe_allow_html=True)
    df_sc = pd.DataFrame({
        "Week": weeks,
        "Plan Cum%": [f"{v}%" for v in plan_cum],
        "Actual Cum%": [f"{v}%" for v in actual_cum],
        "Deviation": [f"{a-p:+}%" for a,p in zip(actual_cum,plan_cum)],
        "Plan Weekly%": [f"{plan_cum[i]-plan_cum[i-1] if i>0 else plan_cum[i]}%" for i in range(24)],
        "Actual Weekly%": [f"{actual_cum[i]-actual_cum[i-1] if i>0 else actual_cum[i]}%" for i in range(24)],
    })

    def color_dev_str(val):
        try:
            v = int(val.replace('%','').replace('+',''))
            if v >= 0: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
            else: return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
        except: return ''

    st.dataframe(df_sc.style.applymap(color_dev_str, subset=["Deviation"]),
                 use_container_width=True, height=320)

# ══════════════════════════════════════════════════════
# TAB 3: DPR
# ══════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📋 Daily Progress Report (DPR)</div>', unsafe_allow_html=True)

    # DPR Header info
    d1,d2,d3,d4 = st.columns(4)
    with d1: st.text_input("Project Name", value="Piping & Structure Project")
    with d2: st.date_input("Report Date", value=date.today())
    with d3: st.text_input("Report No.", value="DPR-001")
    with d4: st.selectbox("Weather", ["Clear","Cloudy","Rainy","Windy"])

    st.markdown("---")

    # Manpower
    st.markdown('<div class="section-title">👷 Manpower Deployment</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        def mp_color(val):
            if isinstance(val,(int,float)):
                if val >= 0: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
                else: return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
            return ''
        st.dataframe(df_mp.style.applymap(mp_color, subset=["Variance"]),
                     use_container_width=True, height=280)
    with m2:
        fig_mp = go.Figure()
        fig_mp.add_trace(go.Bar(name="Planned", x=df_mp["Trade"],
                                 y=df_mp["Planned"], marker_color="#BDD7EE"))
        fig_mp.add_trace(go.Bar(name="Actual", x=df_mp["Trade"],
                                 y=df_mp["Actual"], marker_color="#70AD47"))
        fig_mp.update_layout(barmode="group", height=260,
                              margin=dict(l=5,r=5,t=5,b=60),
                              plot_bgcolor="white", paper_bgcolor="white",
                              legend=dict(orientation="h", y=1.1),
                              xaxis_tickangle=-30)
        st.plotly_chart(fig_mp, use_container_width=True)

    # Activity Progress
    st.markdown('<div class="section-title">⚙️ Activity-wise Progress Today</div>', unsafe_allow_html=True)
    df_dpr["Balance"]  = df_dpr["Total_Qty"] - df_dpr["Cum_Actual"]
    df_dpr["Pct_Done"] = (df_dpr["Cum_Actual"]/df_dpr["Total_Qty"]*100).round(1)

    def pct_bar(val):
        try:
            v = float(val)
            color = "#70AD47" if v>=60 else ("#ED7D31" if v>=30 else "#FF6B6B")
            return f'background-color:{color}20;color:{"#14532D" if v>=60 else "#92400E" if v>=30 else "#991B1B"};font-weight:bold'
        except: return ''

    df_dpr_show = df_dpr.rename(columns={
        "Total_Qty":"Total Qty","Cum_Plan":"Cum Plan","Cum_Actual":"Cum Actual",
        "Today_Plan":"Today Plan","Today_Actual":"Today Actual","Pct_Done":"% Done"
    })
    st.dataframe(df_dpr_show.style.applymap(pct_bar, subset=["% Done"]),
                 use_container_width=True, height=300)

    # Pie chart by category
    st.markdown('<div class="section-title">📊 Category-wise Qty Progress</div>', unsafe_allow_html=True)
    p1,p2 = st.columns(2)
    with p1:
        cat_group = df.groupby("Category").agg({"Total_Qty":"sum","Actual_Qty":"sum"}).reset_index()
        fig_pie = px.pie(cat_group, values="Actual_Qty", names="Category",
                         title="Actual Qty Done by Category",
                         color_discrete_sequence=["#2E75B6","#70AD47","#ED7D31","#7030A0","#FF0000"])
        fig_pie.update_layout(height=300, margin=dict(l=5,r=5,t=40,b=5))
        st.plotly_chart(fig_pie, use_container_width=True)
    with p2:
        fig_bar2 = go.Figure()
        fig_bar2.add_trace(go.Bar(name="Total Qty", x=cat_group["Category"],
                                   y=cat_group["Total_Qty"], marker_color="#E5E7EB"))
        fig_bar2.add_trace(go.Bar(name="Actual Qty Done", x=cat_group["Category"],
                                   y=cat_group["Actual_Qty"], marker_color="#ED7D31"))
        fig_bar2.update_layout(barmode="overlay", height=300,
                                margin=dict(l=5,r=5,t=40,b=5),
                                title="Total vs Actual Qty by Category",
                                plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_bar2, use_container_width=True)

# ══════════════════════════════════════════════════════
# TAB 4: RESOURCE LOADING
# ══════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">👷 Resource Loading Chart — Weekly Manpower Plan</div>', unsafe_allow_html=True)

    resource_plan = {
        "Welder GTAW":[2,4,6,8,10,12,12,12,14,14,14,14,12,12,12,10,10,10,8,8,6,6,4,2],
        "Welder SMAW":[1,2,4,6,8,10,10,10,12,12,12,12,10,10,10,8,8,8,6,6,4,4,2,1],
        "Pipe Fitter":[2,4,6,8,8,8,8,8,8,8,8,8,6,6,6,6,4,4,4,4,3,3,2,1],
        "Struct. Fitter":[0,0,2,4,6,8,8,8,8,8,8,6,6,6,4,4,4,4,2,2,2,2,1,0],
        "Rigger/Helper":[2,4,6,8,8,8,8,8,8,8,6,6,6,6,6,6,4,4,4,4,3,3,2,1],
        "Painter":[0,0,0,2,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,2,2,1,1],
        "QC Inspector":[1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1],
        "Supervisor":[2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2],
    }
    totals = [sum(resource_plan[t][i] for t in resource_plan) for i in range(24)]

    fig_res = go.Figure()
    colors = ["#2E75B6","#70AD47","#ED7D31","#7030A0","#FF6B6B","#FFC107","#17A2B8","#6C757D"]
    for idx, (trade, vals) in enumerate(resource_plan.items()):
        fig_res.add_trace(go.Bar(
            name=trade, x=weeks, y=vals,
            marker_color=colors[idx % len(colors)],
            text=vals, textposition="inside", textfont=dict(size=8)
        ))
    fig_res.add_trace(go.Scatter(
        x=weeks, y=totals, name="Total Headcount",
        mode="lines+markers+text",
        line=dict(color="#1F3864", width=3),
        marker=dict(size=8),
        text=totals, textposition="top center",
        textfont=dict(size=9, color="#1F3864", family="Arial Black")
    ))
    fig_res.update_layout(
        barmode="stack", height=460,
        yaxis_title="No. of Workers",
        xaxis_title="Week",
        legend=dict(orientation="h", y=-0.2, x=0),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10,r=10,t=10,b=80)
    )
    st.plotly_chart(fig_res, use_container_width=True)

    # Resource heatmap table
    st.markdown('<div class="section-title">📋 Manpower Heatmap Table</div>', unsafe_allow_html=True)
    df_res = pd.DataFrame(resource_plan, index=weeks).T
    df_res["Peak"] = df_res.max(axis=1)
    df_res["Total"] = df_res.drop("Peak",axis=1).sum(axis=1)
    st.dataframe(df_res.style.background_gradient(cmap="Blues",
                                                    subset=weeks,
                                                    vmin=0),
                 use_container_width=True, height=300)

# ══════════════════════════════════════════════════════
# TAB 5: WELD SUMMARY
# ══════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🔧 Weld Joint Summary Register</div>', unsafe_allow_html=True)

    weld_data = {
        "Sr":[1,2,3,4,5,6,7,8],
        "ISO/DWG"  :["P-101-A","P-101-A","P-102-B","P-102-B","P-103-C","P-104-D","P-105-E","P-106-F"],
        "Line No." :["12\"-CS-A1A","12\"-CS-A1A","6\"-SS-B1B","6\"-SS-B1B","3\"-CS-A1A","8\"-CS-A3A","10\"-CS-A1A","2\"-SS-B2B"],
        "Size"     :["12\"","12\"","6\"","6\"","3\"","8\"","10\"","2\""],
        "Joint No.":["J-001","J-002","J-003","J-004","J-005","J-006","J-007","J-008"],
        "Welder ID":["W-101","W-101","W-202","W-202","W-103","W-104","W-101","W-202"],
        "WPS"      :["WPS-01","WPS-01","WPS-04","WPS-04","WPS-02","WPS-01","WPS-01","WPS-04"],
        "Date"     :["01-May-25","01-May-25","02-May-25","02-May-25","03-May-25","03-May-25","04-May-25","04-May-25"],
        "RT Req?"  :["Yes","Yes","Yes","Yes","No","Yes","Yes","Yes"],
        "RT Result":["Accept","Accept","Pending","Reject","N/A","Accept","Pending","Accept"],
        "Status"   :["Cleared","Cleared","Pending NDT","Repair","Cleared","Cleared","Pending","Cleared"],
    }
    df_weld = pd.DataFrame(weld_data)

    # KPI
    w1,w2,w3,w4 = st.columns(4)
    with w1: st.metric("Total Joints", len(df_weld))
    with w2: st.metric("Cleared ✅", len(df_weld[df_weld["Status"]=="Cleared"]))
    with w3: st.metric("Pending ⏳", len(df_weld[df_weld["Status"].isin(["Pending NDT","Pending"])]))
    with w4: st.metric("Repair ❌", len(df_weld[df_weld["Status"]=="Repair"]))

    def weld_status_color(val):
        colors = {
            "Cleared":"background-color:#DCFCE7;color:#14532D;font-weight:bold",
            "Repair":"background-color:#FFE4E1;color:#991B1B;font-weight:bold",
            "Pending NDT":"background-color:#FEF3C7;color:#92400E;font-weight:bold",
            "Pending":"background-color:#F3E8FF;color:#6B21A8;font-weight:bold",
        }
        return colors.get(val,"")

    def rt_result_color(val):
        if val=="Accept": return "background-color:#DCFCE7;color:#14532D;font-weight:bold"
        elif val=="Reject": return "background-color:#FFE4E1;color:#991B1B;font-weight:bold"
        elif val=="Pending": return "background-color:#FEF3C7;color:#92400E;font-weight:bold"
        return ""

    st.dataframe(df_weld.style
                 .applymap(weld_status_color, subset=["Status"])
                 .applymap(rt_result_color,   subset=["RT Result"]),
                 use_container_width=True, height=300)

    # Pie
    p1,p2 = st.columns(2)
    with p1:
        status_counts = df_weld["Status"].value_counts()
        fig_wp = px.pie(values=status_counts.values, names=status_counts.index,
                        title="Weld Status Distribution",
                        color_discrete_map={
                            "Cleared":"#70AD47","Repair":"#FF6B6B",
                            "Pending NDT":"#FFC107","Pending":"#7030A0"})
        fig_wp.update_layout(height=280, margin=dict(l=5,r=5,t=40,b=5))
        st.plotly_chart(fig_wp, use_container_width=True)
    with p2:
        rt_counts = df_weld[df_weld["RT Req?"]=="Yes"]["RT Result"].value_counts()
        fig_rt = px.pie(values=rt_counts.values, names=rt_counts.index,
                        title="RT Result Distribution",
                        color_discrete_map={"Accept":"#70AD47","Reject":"#FF6B6B","Pending":"#FFC107"})
        fig_rt.update_layout(height=280, margin=dict(l=5,r=5,t=40,b=5))
        st.plotly_chart(fig_rt, use_container_width=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#9CA3AF;font-size:12px;'>
🏗️ Fabrication & Erection Project Dashboard | 
Generated: {} | 
For internal use only
</div>
""".format(date.today().strftime('%d-%b-%Y')), unsafe_allow_html=True)
