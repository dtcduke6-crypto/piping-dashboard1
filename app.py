import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import io

st.set_page_config(
    page_title="Piping & Structure Dashboard",
    page_icon="ðŸ—ï¸",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #F0F4F8; }
    .block-container { padding-top: 1rem; }
    .metric-card {
        background: white; border-radius: 12px;
        padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #2E75B6; margin-bottom: 10px;
    }
    .metric-card.green  { border-left-color: #70AD47; }
    .metric-card.orange { border-left-color: #ED7D31; }
    .metric-card.red    { border-left-color: #FF0000; }
    .metric-card.purple { border-left-color: #7030A0; }
    .metric-title { font-size:12px; color:#6B7280; font-weight:600; margin:0; }
    .metric-value { font-size:30px; font-weight:800; margin:4px 0 0 0; }
    .metric-sub   { font-size:11px; color:#9CA3AF; margin:2px 0 0 0; }
    .section-title {
        font-size:17px; font-weight:700; color:#1F3864;
        border-bottom:3px solid #2E75B6;
        padding-bottom:5px; margin:16px 0 12px 0;
    }
    .upload-box {
        background: white; border-radius: 16px;
        padding: 30px; text-align: center;
        border: 2px dashed #2E75B6;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DEFAULT DATA (jab tak file upload na ho)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
DEFAULT_ACTIVITIES = [
    ("Isometric Drawing Review",      "PIPING", 100,100,"Nos",   45,  45, "A. Piping Fab"),
    ("Material Procurement",          "PIPING", 100,100,"Lot",   1,   1,  "A. Piping Fab"),
    ("Pipe Cutting & Beveling",       "PIPING", 85, 80, "Jt",   800, 680, "A. Piping Fab"),
    ("Pipe Fitting & Alignment",      "PIPING", 75, 70, "Spool",250, 195, "A. Piping Fab"),
    ("Welding (Shop)",                "PIPING", 65, 60, "Jt",   800, 510, "A. Piping Fab"),
    ("NDT / Radiography",             "QA/QC",  50, 45, "Jt",   640, 420, "A. Piping Fab"),
    ("PWHT",                          "PIPING", 40, 38, "Jt",   120, 80,  "A. Piping Fab"),
    ("Hydro Test (Shop)",             "PIPING", 30, 28, "Spool",250, 90,  "A. Piping Fab"),
    ("Spool Dispatch",                "PIPING", 25, 22, "Spool",250, 85,  "A. Piping Fab"),
    ("GA Drawing Review",             "CIVIL",  100,100,"Nos",  30,  30,  "B. Structure Fab"),
    ("Cutting & Marking",             "CIVIL",  80, 75, "MT",   120, 88,  "B. Structure Fab"),
    ("Assembly & Fit-up",             "CIVIL",  62, 58, "MT",   120, 75,  "B. Structure Fab"),
    ("Welding of Structure",          "CIVIL",  55, 50, "MT",   120, 65,  "B. Structure Fab"),
    ("Blasting & Painting (Shop)",    "CIVIL",  35, 30, "Sq.M",2400,1520, "B. Structure Fab"),
    ("Support/Hanger Install",        "PIPING", 55, 50, "Nos",  380, 210, "C. Piping Erection"),
    ("Spool Erection & Alignment",    "PIPING", 20, 18, "Spool",250, 55,  "C. Piping Erection"),
    ("Field Welding",                 "PIPING", 18, 15, "Jt",   400, 72,  "C. Piping Erection"),
    ("Field NDT / DP Test",           "QA/QC",  8,  6,  "Jt",   320, 52,  "C. Piping Erection"),
    ("Hydro Test (Field)",            "PIPING", 5,  3,  "System",8,  2,   "C. Piping Erection"),
    ("Insulation & Cladding",         "PIPING", 2,  0,  "Sq.M",1800,0,   "C. Piping Erection"),
    ("Foundation Check & Grouting",   "CIVIL",  80, 75, "Nos",  48,  38,  "D. Structure Erection"),
    ("Column Erection",               "CIVIL",  60, 55, "MT",   45,  28,  "D. Structure Erection"),
    ("Beam & Grating Installation",   "CIVIL",  20, 18, "MT",   55,  12,  "D. Structure Erection"),
    ("Ladder / Handrail",             "CIVIL",  5,  0,  "RMT",  320, 0,   "D. Structure Erection"),
    ("Pre-comm Walk-through",         "QA/QC",  1,  0,  "Nos",  1,   0,   "E. QA/QC & Handover"),
    ("Punch List Clearance",          "QA/QC",  1,  0,  "Nos",  1,   0,   "E. QA/QC & Handover"),
    ("Final Inspection (Client/PMC)", "QA/QC",  0,  0,  "Nos",  1,   0,   "E. QA/QC & Handover"),
    ("Mechanical Completion Cert.",   "ALL",    0,  0,  "Doc",  1,   0,   "E. QA/QC & Handover"),
]

def make_default_df():
    df = pd.DataFrame(DEFAULT_ACTIVITIES, columns=[
        "Activity","Discipline","Plan%","Actual%","Unit",
        "Total_Qty","Actual_Qty","Category"
    ])
    df["Balance_Qty"] = df["Total_Qty"] - df["Actual_Qty"]
    df["Qty_Pct"]     = (df["Actual_Qty"] / df["Total_Qty"].replace(0,1) * 100).round(1)
    df["Deviation"]   = df["Actual%"] - df["Plan%"]
    return df

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# EXCEL FILE PARSER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def parse_excel(uploaded_file):
    """
    Aapki Piping_Structure_v3.xlsx file padhta hai.
    Sheet: "ðŸ“… Micro Plan (Gantt)"
    Columns expected:
      A=Sr, B=Activity, C=Discipline, D=Duration,
      E=Plan Start, F=Plan Finish, G=Actual Start, H=Actual Finish,
      I=Plan%, J=Actual%, K=Unit, L=Total Qty, M=Actual Qty,
      N=Balance Qty (formula), O=Qty% (formula)
    """
    try:
        xf = pd.ExcelFile(uploaded_file)
        sheet_names = xf.sheet_names
        
        # Sheet 1 â€” Micro Plan
        gantt_sheet = None
        for s in sheet_names:
            if "Micro" in s or "Gantt" in s or "gantt" in s or "micro" in s:
                gantt_sheet = s
                break
        if gantt_sheet is None:
            gantt_sheet = sheet_names[0]

        # Row 4 = header (index 3), data from row 5 (index 4)
        raw = pd.read_excel(uploaded_file, sheet_name=gantt_sheet,
                            header=3, engine="openpyxl")
        raw.columns = [str(c).strip() for c in raw.columns]

        # Rename columns by position (A=0,B=1,...O=14)
        col_map = {
            raw.columns[0]:  "Sr",
            raw.columns[1]:  "Activity",
            raw.columns[2]:  "Discipline",
            raw.columns[3]:  "Duration",
            raw.columns[4]:  "Plan_Start",
            raw.columns[5]:  "Plan_Finish",
            raw.columns[6]:  "Actual_Start",
            raw.columns[7]:  "Actual_Finish",
            raw.columns[8]:  "Plan_pct_raw",
            raw.columns[9]:  "Actual_pct_raw",
            raw.columns[10]: "Unit",
            raw.columns[11]: "Total_Qty",
            raw.columns[12]: "Actual_Qty",
            raw.columns[13]: "Balance_Qty_raw",
            raw.columns[14]: "Qty_Pct_raw",
        }
        raw = raw.rename(columns=col_map)

        # Keep only activity rows (not section headers, not empty)
        df = raw[raw["Activity"].notna()].copy()
        df = df[df["Sr"].notna() & (df["Sr"] != "")].copy()

        # Clean % values (could be 0.75 or "75%" or 75)
        def clean_pct(val):
            try:
                v = float(str(val).replace('%','').replace(' ',''))
                return v if v > 1 else v * 100
            except:
                return 0.0

        df["Plan%"]      = df["Plan_pct_raw"].apply(clean_pct)
        df["Actual%"]    = df["Actual_pct_raw"].apply(clean_pct)
        df["Total_Qty"]  = pd.to_numeric(df["Total_Qty"],  errors='coerce').fillna(0)
        df["Actual_Qty"] = pd.to_numeric(df["Actual_Qty"], errors='coerce').fillna(0)
        df["Balance_Qty"]= df["Total_Qty"] - df["Actual_Qty"]
        df["Qty_Pct"]    = (df["Actual_Qty"] / df["Total_Qty"].replace(0,1) * 100).round(1)
        df["Deviation"]  = df["Actual%"] - df["Plan%"]

        # Date columns
        for dcol in ["Plan_Start","Plan_Finish","Actual_Start","Actual_Finish"]:
            df[dcol] = pd.to_datetime(df[dcol], errors='coerce')

        # Category â€” try to infer from activity name prefix
        def guess_cat(name):
            n = str(name).strip()
            if n.startswith("A."): return "A. Piping Fab"
            elif n.startswith("B."): return "B. Structure Fab"
            elif n.startswith("C."): return "C. Piping Erection"
            elif n.startswith("D."): return "D. Structure Erection"
            elif n.startswith("E."): return "E. QA/QC & Handover"
            return "Other"

        df["Category"] = df["Activity"].apply(guess_cat)

        # â”€â”€ S-Curve sheet
        df_sc = None
        for s in sheet_names:
            if "S-Curve" in s or "scurve" in s.lower() or "curve" in s.lower() or "DPR" in s:
                try:
                    sc_raw = pd.read_excel(uploaded_file, sheet_name=s,
                                           header=2, engine="openpyxl")
                    if len(sc_raw.columns) >= 4:
                        sc_raw.columns = [str(c) for c in sc_raw.columns]
                        df_sc = sc_raw.iloc[:24].copy()
                except:
                    pass
                break

        return df, df_sc, sheet_names, gantt_sheet, None

    except Exception as e:
        return None, None, [], "", str(e)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SIDEBAR â€” FILE UPLOAD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with st.sidebar:
    st.markdown("## ðŸ—ï¸ Project Control")
    st.markdown("---")

    st.markdown("### ðŸ“‚ File Upload")
    uploaded_file = st.file_uploader(
        "Apni Excel file yahan upload karo",
        type=["xlsx","xls"],
        help="Piping_Structure_v3.xlsx ya koi bhi project Excel"
    )

    if uploaded_file:
        st.success(f"âœ… File loaded:\n`{uploaded_file.name}`")
        df, df_sc, sheet_names, active_sheet, err = parse_excel(uploaded_file)
        if err:
            st.error(f"âŒ Error: {err}")
            df = make_default_df()
            data_source = "âš ï¸ Default Data (file error)"
        else:
            data_source = f"ðŸ“„ {uploaded_file.name}"
            st.info(f"Sheet: **{active_sheet}**\n\n{len(df)} activities loaded")
    else:
        df = make_default_df()
        data_source = "ðŸ“Š Demo Data (file upload karo)"
        st.info("ðŸ‘† Upar apni Excel file upload karo\n\nAbhi demo data dikh raha hai")

    st.markdown(f"**Source:** {data_source}")
    st.markdown(f"ðŸ“… **Date:** {date.today().strftime('%d-%b-%Y')}")
    st.markdown("---")

    # Filters
    st.markdown("### ðŸ” Filters")
    disc_opts = df["Discipline"].unique().tolist() if len(df) > 0 else ["PIPING","CIVIL","QA/QC"]
    disc_filter = st.multiselect("Discipline", options=disc_opts, default=disc_opts)

    cat_opts = df["Category"].unique().tolist() if len(df) > 0 else []
    cat_filter = st.multiselect("Category", options=cat_opts, default=cat_opts)

    st.markdown("---")
    if len(df) > 0:
        op = round(df["Plan%"].mean(),1)
        oa = round(df["Actual%"].mean(),1)
        st.markdown("### ðŸ“Š Overall Progress")
        st.progress(oa/100)
        st.markdown(f"**Plan:** {op}%")
        st.markdown(f"**Actual:** {oa}%")
        delta = oa - op
        st.markdown(f"{'ðŸŸ¢' if delta>=0 else 'ðŸ”´'} **Deviation: {delta:+.1f}%**")

# â”€â”€â”€ Apply filters â”€â”€â”€
if len(df) > 0 and disc_filter and cat_filter:
    df_f = df[df["Discipline"].isin(disc_filter) & df["Category"].isin(cat_filter)]
else:
    df_f = df.copy()

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HEADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
st.markdown("""
<h1 style='color:#1F3864;font-size:26px;margin-bottom:2px;'>
ðŸ—ï¸ Fabrication & Erection â€” Project Dashboard
</h1>
<p style='color:#6B7280;font-size:13px;margin-top:0;'>
Micro Planning | DPR | Quantity Tracking | Resource Loading
</p>
""", unsafe_allow_html=True)

# Upload prompt if no file
if not uploaded_file:
    st.markdown("""
    <div class="upload-box">
        <h3 style="color:#2E75B6;">ðŸ“‚ Apni Project Excel File Upload Karo</h3>
        <p style="color:#6B7280;">Sidebar mein "Browse files" click karo aur <b>Piping_Structure_v3.xlsx</b> select karo</p>
        <p style="color:#9CA3AF;font-size:13px;">Abhi neeche Demo Data dikh raha hai</p>
    </div>
    """, unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# KPI CARDS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
tq  = int(df_f["Total_Qty"].sum())
aq  = int(df_f["Actual_Qty"].sum())
bq  = int(df_f["Balance_Qty"].sum())
qp  = round(aq/max(tq,1)*100,1)
op2 = round(df_f["Plan%"].mean(),1)  if len(df_f)>0 else 0
oa2 = round(df_f["Actual%"].mean(),1) if len(df_f)>0 else 0

c1,c2,c3,c4,c5,c6 = st.columns(6)
cards = [
    (c1, "ðŸ“‹ Activities",    str(len(df_f)),           f"Total: {len(df)}",    "blue"),
    (c2, "ðŸ“… Plan %",        f"{op2}%",                "Baseline schedule",    "green"),
    (c3, "ðŸ”¨ Actual %",      f"{oa2}%",                f"Dev: {oa2-op2:+.1f}%","orange" if oa2<op2 else "green"),
    (c4, "ðŸ“¦ Total Qty",     f"{tq:,}",                "All units",            "purple"),
    (c5, "âœ… Actual Qty",    f"{aq:,}",                f"{qp}% of total",      "green"),
    (c6, "â³ Balance Qty",   f"{bq:,}",                "Remaining",            "red"),
]
for col, title, val, sub, clr in cards:
    with col:
        hex_map = {"blue":"#2E75B6","green":"#70AD47","orange":"#ED7D31","purple":"#7030A0","red":"#FF0000"}
        st.markdown(f"""<div class="metric-card {clr}">
        <p class="metric-title">{title}</p>
        <p class="metric-value" style="color:{hex_map[clr]};">{val}</p>
        <p class="metric-sub">{sub}</p></div>""", unsafe_allow_html=True)

st.markdown("---")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TABS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "ðŸ“… Micro Plan & Qty",
    "ðŸ“Š S-Curve",
    "ðŸ“‹ DPR",
    "ðŸ‘· Resource Loading",
    "ðŸ”§ Weld Summary"
])

# â”€â”€ TAB 1 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with tab1:
    if len(df_f) == 0:
        st.warning("Koi data nahi mila selected filters mein.")
    else:
        col_l, col_r = st.columns([3,2])
        with col_l:
            st.markdown('<div class="section-title">ðŸ“… Plan vs Actual Progress %</div>', unsafe_allow_html=True)
            cats    = df_f["Activity"].tolist()[::-1]
            plans   = df_f["Plan%"].tolist()[::-1]
            actuals = df_f["Actual%"].tolist()[::-1]
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Plan %",  y=cats, x=plans,   orientation='h',
                                  marker_color="#BDD7EE",
                                  text=[f"{v:.0f}%" for v in plans],
                                  textposition="inside", textfont=dict(color="#1E3A8A",size=9)))
            fig.add_trace(go.Bar(name="Actual %",y=cats, x=actuals, orientation='h',
                                  marker_color="#70AD47",
                                  text=[f"{v:.0f}%" for v in actuals],
                                  textposition="inside", textfont=dict(color="white",size=9)))
            fig.update_layout(barmode="overlay", height=max(480,len(cats)*22+60),
                              margin=dict(l=5,r=5,t=10,b=10),
                              xaxis=dict(title="Progress %",range=[0,110]),
                              legend=dict(orientation="h",y=1.04),
                              plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">ðŸ“¦ Total vs Actual Qty</div>', unsafe_allow_html=True)
            dq = df_f[df_f["Total_Qty"]>1].copy()
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="Total Qty",  y=dq["Activity"], x=dq["Total_Qty"],
                                   orientation='h', marker_color="#E5E7EB"))
            fig2.add_trace(go.Bar(name="Actual Qty", y=dq["Activity"], x=dq["Actual_Qty"],
                                   orientation='h', marker_color="#ED7D31",
                                   text=[f"{v} {u}" for v,u in zip(dq["Actual_Qty"],dq["Unit"])],
                                   textposition="inside", textfont=dict(color="white",size=9)))
            fig2.update_layout(barmode="overlay", height=max(480,len(dq)*22+60),
                               margin=dict(l=5,r=5,t=10,b=10),
                               legend=dict(orientation="h",y=1.04),
                               plot_bgcolor="white", paper_bgcolor="white",
                               xaxis_title="Quantity")
            st.plotly_chart(fig2, use_container_width=True)

        # Detail table
        st.markdown('<div class="section-title">ðŸ“‹ Activity Detail Table</div>', unsafe_allow_html=True)

        show_cols = ["Activity","Category","Discipline","Plan%","Actual%","Deviation",
                     "Unit","Total_Qty","Actual_Qty","Balance_Qty","Qty_Pct"]
        available = [c for c in show_cols if c in df_f.columns]
        df_show = df_f[available].rename(columns={
            "Plan%":"Plan %","Actual%":"Actual %","Total_Qty":"Total Qty",
            "Actual_Qty":"Actual Qty","Balance_Qty":"Balance Qty","Qty_Pct":"Qty %"
        }).copy()
        if "Qty %" in df_show.columns:
            df_show["Qty %"] = df_show["Qty %"].apply(lambda x: f"{x:.1f}%")

        def color_dev(val):
            try:
                v = float(val)
                if v>=0: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
                elif v>=-5: return 'background-color:#FEF3C7;color:#92400E;font-weight:bold'
                else: return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
            except: return ''

        def color_qp(val):
            try:
                v = float(str(val).replace('%',''))
                if v>=80: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
                elif v>=40: return 'background-color:#FEF3C7;color:#92400E;font-weight:bold'
                else: return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
            except: return ''

        styled = df_show.style
        if "Deviation" in df_show.columns:
            styled = styled.map(color_dev, subset=["Deviation"])
        if "Qty %" in df_show.columns:
            styled = styled.map(color_qp, subset=["Qty %"])
        fmt_dict = {}
        if "Plan %" in df_show.columns:   fmt_dict["Plan %"]   = "{:.0f}%"
        if "Actual %" in df_show.columns: fmt_dict["Actual %"] = "{:.0f}%"
        if "Deviation" in df_show.columns:fmt_dict["Deviation"]= "{:+.0f}%"
        if fmt_dict: styled = styled.format(fmt_dict)

        st.dataframe(styled, use_container_width=True, height=380)

        # Excel download button
        buf = io.BytesIO()
        df_f[available].to_excel(buf, index=False)
        buf.seek(0)
        st.download_button(
            "â¬‡ï¸ Filtered Data Download karo (Excel)",
            data=buf,
            file_name=f"project_data_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# â”€â”€ TAB 2: S-CURVE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with tab2:
    st.markdown('<div class="section-title">ðŸ“Š S-Curve â€” Cumulative Progress</div>', unsafe_allow_html=True)
    weeks      = [f"W{i}" for i in range(1,25)]
    plan_cum   = [2,4,6,9,12,16,20,25,30,36,42,48,54,60,65,70,75,79,83,87,90,94,97,100]
    actual_cum = [1,3,5,8,10,14,17,22,27,33,39,45,50,56,60,65,70,74,78,82,86,90,94,97]

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Scatter(x=weeks, y=plan_cum, name="Plan %",
        mode="lines+markers", line=dict(color="#2E75B6",width=3,dash="dash"),
        marker=dict(size=7), fill="tozeroy", fillcolor="rgba(46,117,182,0.07)"))
    fig_sc.add_trace(go.Scatter(x=weeks, y=actual_cum, name="Actual %",
        mode="lines+markers", line=dict(color="#ED7D31",width=3),
        marker=dict(size=8,symbol="circle-open",line=dict(width=2)),
        fill="tozeroy", fillcolor="rgba(237,125,49,0.09)"))
    fig_sc.update_layout(height=400,
        yaxis=dict(title="Cumulative %",range=[0,110],ticksuffix="%"),
        xaxis_title="Week",
        legend=dict(orientation="h",y=1.08),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig_sc, use_container_width=True)

    df_sc2 = pd.DataFrame({
        "Week":weeks,
        "Plan Cum%": [f"{v}%" for v in plan_cum],
        "Actual Cum%":[f"{v}%" for v in actual_cum],
        "Deviation":[f"{a-p:+}%" for a,p in zip(actual_cum,plan_cum)],
        "Plan Wkly%":[f"{plan_cum[i]-(plan_cum[i-1] if i>0 else 0)}%" for i in range(24)],
        "Actual Wkly%":[f"{actual_cum[i]-(actual_cum[i-1] if i>0 else 0)}%" for i in range(24)],
    })
    def color_dev_s(v):
        try:
            n = int(str(v).replace('%','').replace('+',''))
            if n>=0: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
            else:    return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
        except: return ''
    st.dataframe(df_sc2.style.map(color_dev_s,subset=["Deviation"]),
                 use_container_width=True, height=320)

# â”€â”€ TAB 3: DPR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with tab3:
    st.markdown('<div class="section-title">ðŸ“‹ Daily Progress Report</div>', unsafe_allow_html=True)
    d1,d2,d3,d4 = st.columns(4)
    with d1: st.text_input("Project", value="Piping & Structure")
    with d2: st.date_input("Report Date", value=date.today())
    with d3: st.text_input("Report No.", value="DPR-001")
    with d4: st.selectbox("Weather",["Clear","Cloudy","Rainy","Windy"])

    st.markdown("---")
    st.markdown('<div class="section-title">ðŸ‘· Manpower Today</div>', unsafe_allow_html=True)

    mp_data = {"Trade":["Welder GTAW","Welder SMAW","Pipe Fitter","Struct. Fitter",
                          "Rigger/Helper","Scaffolder","Grinder","Painter","QC Inspector","Supervisor"],
               "Planned":[12,10,8,6,8,6,10,4,2,3],
               "Actual": [10,9,8,6,8,5,9,3,2,3]}
    df_mp = pd.DataFrame(mp_data)
    df_mp["Variance"] = df_mp["Actual"]-df_mp["Planned"]

    m1,m2 = st.columns(2)
    with m1:
        def mp_c(v):
            if isinstance(v,(int,float)): return ('background-color:#DCFCE7;color:#14532D' if v>=0 else 'background-color:#FFE4E1;color:#991B1B')+';font-weight:bold'
            return ''
        st.dataframe(df_mp.style.map(mp_c,subset=["Variance"]),use_container_width=True,height=280)
    with m2:
        fig_mp = go.Figure()
        fig_mp.add_trace(go.Bar(name="Planned",x=df_mp["Trade"],y=df_mp["Planned"],marker_color="#BDD7EE"))
        fig_mp.add_trace(go.Bar(name="Actual", x=df_mp["Trade"],y=df_mp["Actual"], marker_color="#70AD47"))
        fig_mp.update_layout(barmode="group",height=260,margin=dict(l=5,r=5,t=5,b=60),
                              plot_bgcolor="white",paper_bgcolor="white",
                              legend=dict(orientation="h",y=1.1),xaxis_tickangle=-30)
        st.plotly_chart(fig_mp,use_container_width=True)

    st.markdown('<div class="section-title">âš™ï¸ Activity Progress</div>', unsafe_allow_html=True)
    dpr = {"Activity":["Pipe Spool Fab","Pipe Fitting","Pipe Welding","NDT/RT",
                         "Hydro Test","Structure Fab","Pipe Erection","Struct. Erection","Painting","Field Welding"],
           "Unit":["Spool","Spool","Jt","Jt","Spool","MT","Spool","MT","Sq.M","Jt"],
           "Total":[250,250,800,800,250,120,250,120,800,400],
           "Cum Plan":[180,170,550,510,100,80,60,30,400,80],
           "Cum Actual":[165,155,510,480,90,75,55,28,380,72],
           "Today Plan":[8,8,25,20,10,5,10,4,30,15],
           "Today Actual":[7,6,22,18,8,4,8,3,28,12]}
    df_dpr = pd.DataFrame(dpr)
    df_dpr["Balance"]  = df_dpr["Total"]-df_dpr["Cum Actual"]
    df_dpr["% Done"]   = (df_dpr["Cum Actual"]/df_dpr["Total"]*100).round(1)

    def pct_c(v):
        try:
            f=float(v)
            if f>=60: return 'background-color:#DCFCE7;color:#14532D;font-weight:bold'
            elif f>=30: return 'background-color:#FEF3C7;color:#92400E;font-weight:bold'
            else: return 'background-color:#FFE4E1;color:#991B1B;font-weight:bold'
        except: return ''
    st.dataframe(df_dpr.style.map(pct_c,subset=["% Done"]),
                 use_container_width=True,height=300)

# â”€â”€ TAB 4: RESOURCE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with tab4:
    st.markdown('<div class="section-title">ðŸ‘· Resource Loading â€” Weekly Manpower</div>', unsafe_allow_html=True)
    weeks = [f"W{i}" for i in range(1,25)]
    res = {
        "Welder GTAW":[2,4,6,8,10,12,12,12,14,14,14,14,12,12,12,10,10,10,8,8,6,6,4,2],
        "Welder SMAW":[1,2,4,6,8,10,10,10,12,12,12,12,10,10,10,8,8,8,6,6,4,4,2,1],
        "Pipe Fitter":[2,4,6,8,8,8,8,8,8,8,8,8,6,6,6,6,4,4,4,4,3,3,2,1],
        "Struct. Fitter":[0,0,2,4,6,8,8,8,8,8,8,6,6,6,4,4,4,4,2,2,2,2,1,0],
        "Rigger/Helper":[2,4,6,8,8,8,8,8,8,8,6,6,6,6,6,6,4,4,4,4,3,3,2,1],
        "Painter":[0,0,0,2,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,2,2,1,1],
        "QC Inspector":[1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1],
        "Supervisor":[2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2],
    }
    totals=[sum(res[t][i] for t in res) for i in range(24)]
    colors=["#2E75B6","#70AD47","#ED7D31","#7030A0","#FF6B6B","#FFC107","#17A2B8","#6C757D"]
    fig_r=go.Figure()
    for idx,(trade,vals) in enumerate(res.items()):
        fig_r.add_trace(go.Bar(name=trade,x=weeks,y=vals,marker_color=colors[idx%len(colors)],
                                text=vals,textposition="inside",textfont=dict(size=8)))
    fig_r.add_trace(go.Scatter(x=weeks,y=totals,name="Total",mode="lines+markers+text",
        line=dict(color="#1F3864",width=3),marker=dict(size=8),
        text=totals,textposition="top center",textfont=dict(size=9,color="#1F3864")))
    fig_r.update_layout(barmode="stack",height=440,yaxis_title="Workers",xaxis_title="Week",
                         legend=dict(orientation="h",y=-0.25),
                         plot_bgcolor="white",paper_bgcolor="white",margin=dict(l=5,r=5,t=5,b=80))
    st.plotly_chart(fig_r,use_container_width=True)

    df_res=pd.DataFrame(res,index=weeks).T
    st.dataframe(df_res.style.background_gradient(cmap="Blues",vmin=0),
                 use_container_width=True,height=280)

# â”€â”€ TAB 5: WELD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with tab5:
    st.markdown('<div class="section-title">ðŸ”§ Weld Joint Summary Register</div>', unsafe_allow_html=True)
    wd={"Sr":[1,2,3,4,5,6,7,8],
        "ISO":["P-101-A","P-101-A","P-102-B","P-102-B","P-103-C","P-104-D","P-105-E","P-106-F"],
        "Line":["12\"-CS","12\"-CS","6\"-SS","6\"-SS","3\"-CS","8\"-CS","10\"-CS","2\"-SS"],
        "Size":["12\"","12\"","6\"","6\"","3\"","8\"","10\"","2\""],
        "Joint":["J-001","J-002","J-003","J-004","J-005","J-006","J-007","J-008"],
        "Welder":["W-101","W-101","W-202","W-202","W-103","W-104","W-101","W-202"],
        "WPS":["WPS-01","WPS-01","WPS-04","WPS-04","WPS-02","WPS-01","WPS-01","WPS-04"],
        "Date":["01-May","01-May","02-May","02-May","03-May","03-May","04-May","04-May"],
        "RT":["Accept","Accept","Pending","Reject","N/A","Accept","Pending","Accept"],
        "Status":["Cleared","Cleared","Pending NDT","Repair","Cleared","Cleared","Pending","Cleared"]}
    df_w=pd.DataFrame(wd)
    w1,w2,w3,w4=st.columns(4)
    with w1: st.metric("Total Joints",len(df_w))
    with w2: st.metric("Cleared âœ…",len(df_w[df_w["Status"]=="Cleared"]))
    with w3: st.metric("Pending â³",len(df_w[df_w["Status"].isin(["Pending NDT","Pending"])]))
    with w4: st.metric("Repair âŒ",len(df_w[df_w["Status"]=="Repair"]))

    def ws_c(v):
        m={"Cleared":"background-color:#DCFCE7;color:#14532D","Repair":"background-color:#FFE4E1;color:#991B1B",
           "Pending NDT":"background-color:#FEF3C7;color:#92400E","Pending":"background-color:#F3E8FF;color:#6B21A8"}
        return m.get(v,"")+";font-weight:bold" if v in m else ""
    def rt_c(v):
        if v=="Accept": return "background-color:#DCFCE7;color:#14532D;font-weight:bold"
        elif v=="Reject": return "background-color:#FFE4E1;color:#991B1B;font-weight:bold"
        elif v=="Pending": return "background-color:#FEF3C7;color:#92400E;font-weight:bold"
        return ""
    st.dataframe(df_w.style.map(ws_c,subset=["Status"]).map(rt_c,subset=["RT"]),
                 use_container_width=True,height=280)

    p1,p2=st.columns(2)
    with p1:
        sc=df_w["Status"].value_counts()
        fig_pw=px.pie(values=sc.values,names=sc.index,title="Weld Status",
            color_discrete_map={"Cleared":"#70AD47","Repair":"#FF6B6B","Pending NDT":"#FFC107","Pending":"#7030A0"})
        fig_pw.update_layout(height=260,margin=dict(l=5,r=5,t=35,b=5))
        st.plotly_chart(fig_pw,use_container_width=True)
    with p2:
        rc=df_w[df_w["RT"]!="N/A"]["RT"].value_counts()
        fig_rt=px.pie(values=rc.values,names=rc.index,title="RT Result",
            color_discrete_map={"Accept":"#70AD47","Reject":"#FF6B6B","Pending":"#FFC107"})
        fig_rt.update_layout(height=260,margin=dict(l=5,r=5,t=35,b=5))
        st.plotly_chart(fig_rt,use_container_width=True)

st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#9CA3AF;font-size:12px;'>ðŸ—ï¸ Fabrication & Erection Dashboard | {date.today().strftime('%d-%b-%Y')}</div>",
            unsafe_allow_html=True)
