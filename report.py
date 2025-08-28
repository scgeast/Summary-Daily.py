import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery And Sales", layout="wide")

# ========== ENHANCED FUTURISTIC THEME & COLOR ==========
st.sidebar.header("🎨 Display Mode")
mode = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if mode == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#0a0a0f"
    card_bg = "#0f1419"
    text_color = "#FFFFFF"
    accent = "#00E5FF"       # Cyan Neon
    accent_light = "#FF00FF" # Magenta Neon
    accent_green = "#39FF14" # Neon Green
    accent_yellow = "#FFEA00" # Neon Yellow
    futur_colos = ["#00E5FF", "#FF00FF", "#39FF14", "#FFEA00", "#FF4D4D", "#8A2BE2", "#00FFFF"]
    font_color = "#fff"
    grid_color = "rgba(0, 229, 255, 0.1)"
    particle_color = "rgba(0, 229, 255, 0.3)"
else:
    chart_template = "plotly_white"
    base_bg = "#f0f2f6"
    card_bg = "#ffffff"
    text_color = "#111827"
    accent = "#2563EB"
    accent_light = "#7C3AED"
    accent_green = "#059669"
    accent_yellow = "#D97706"
    futur_colors = ["#2563EB", "#7C3AED", "#06B6D4", "#D946EF", "#F59E0B", "#8B5CF6", "#10B981"]
    font_color = "#111827"
    grid_color = "rgba(37, 99, 235, 0.1)"
    particle_color = "rgba(37, 99, 235, 0.2)"

# ========== ADVANCED FUTURISTIC CSS WITH ANIMATIONS ==========
st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
      
      /* Main Background with Animated Grid */
      .main {{
        background: 
          radial-gradient(circle at 25% 25%, {accent}22 0%, transparent 50%),
          radial-gradient(circle at 75% 75%, {accent_light}22 0%, transparent 50%),
          linear-gradient(135deg, {base_bg} 0%, #1a1a2e 50%, {base_bg} 100%);
        color: {text_color};
        font-family: 'Rajdhani', sans-serif;
        position: relative;
        overflow-x: hidden;
      }}
      
      /* Animated Grid Overlay */
      .main::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
          linear-gradient({grid_color} 1px, transparent 1px),
          linear-gradient(90deg, {grid_color} 1px, transparent 1px);
        background-size: 50px 50px;
        animation: gridMove 20s linear infinite;
        z-index: 0;
        pointer-events: none;
      }}
      
      /* Floating Particles */
      .main::after {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
          radial-gradient(2px 2px at 20px 30px, {particle_color}, transparent),
          radial-gradient(2px 2px at 40px 70px, {accent_light}44, transparent),
          radial-gradient(1px 1px at 90px 40px, {accent_green}66, transparent),
          radial-gradient(1px 1px at 130px 80px, {accent_yellow}44, transparent);
        background-repeat: repeat;
        background-size: 200px 100px;
        animation: particleFloat 15s ease-in-out infinite;
        z-index: 0;
        pointer-events: none;
      }}
      
      @keyframes gridMove {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(50px, 50px); }}
      }}
      
      @keyframes particleFloat {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-20px) rotate(180deg); }}
      }}
      
      @keyframes neonPulse {{
        0%, 100% {{ text-shadow: 0 0 5px {accent}, 0 0 10px {accent}, 0 0 15px {accent}; }}
        50% {{ text-shadow: 0 0 10px {accent}, 0 0 20px {accent}, 0 0 30px {accent}; }}
      }}
      
      @keyframes cardGlow {{
        0%, 100% {{ box-shadow: 0 0 15px {accent}33, inset 0 0 25px {accent_light}11; }}
        50% {{ box-shadow: 0 0 25px {accent}55, inset 0 0 35px {accent_light}22; }}
      }}
      
      @keyframes borderScan {{
        0% {{ border-image: linear-gradient(90deg, {accent} 0%, transparent 50%, transparent 100%) 1; }}
        50% {{ border-image: linear-gradient(90deg, transparent 0%, {accent} 50%, transparent 100%) 1; }}
        100% {{ border-image: linear-gradient(90deg, transparent 0%, transparent 50%, {accent} 100%) 1; }}
      }}
      
      /* Typography */
      h1, h2, h3, h4, .section-title {{
        font-family: 'Orbitron', monospace !important;
        text-shadow: 0 0 10px {accent}, 0 0 20px {accent_light};
        color: {text_color} !important;
        animation: neonPulse 3s ease-in-out infinite;
        position: relative;
        z-index: 1;
      }}
      
      /* Enhanced Metric Cards */
      .metric-card {{
        background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 70%, {accent}11 100%);
        border: 2px solid transparent;
        border-radius: 20px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        animation: cardGlow 4s ease-in-out infinite;
        transition: all 0.3s ease;
        z-index: 1;
      }}
      
      .metric-card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(45deg, {accent}11, {accent_light}11, {accent_green}11);
        border-radius: 20px;
        z-index: -1;
        animation: borderScan 3s linear infinite;
      }}
      
      .metric-card:hover {{
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 10px 30px {accent}44, inset 0 0 40px {accent_light}22;
      }}
      
      .metric-value {{
        font-family: 'Orbitron', monospace !important;
        font-size: 28px;
        font-weight: 900;
        color: {font_color} !important;
        text-shadow: 0 0 8px {accent};
        animation: neonPulse 2s ease-in-out infinite;
      }}
      
      .metric-label {{
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 13px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {font_color} !important;
        font-weight: 600;
      }}
      
      .section-title {{
        font-size: 26px;
        font-weight: 900;
        margin: 15px 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }}
      
      .subtitle {{
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 18px;
        opacity: 0.95;
        margin: 12px 0;
        font-weight: 600;
        text-shadow: 0 0 5px {accent_light};
      }}
      
      /* Enhanced Sidebar */
      .css-1d391kg {{
        background: linear-gradient(180deg, {card_bg} 0%, {base_bg} 100%);
        border-right: 2px solid {accent}33;
      }}
      
      /* Custom Scrollbar */
      ::-webkit-scrollbar {{
        width: 12px;
      }}
      ::-webkit-scrollbar-track {{
        background: {base_bg};
        border-radius: 10px;
      }}
      ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {accent}, {accent_light});
        border-radius: 10px;
        border: 2px solid {base_bg};
      }}
      ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, {accent_light}, {accent});
      }}
      
      /* Button Enhancements */
      .stButton > button {{
        background: linear-gradient(45deg, {accent}, {accent_light}) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px {accent}44 !important;
      }}
      
      .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px {accent}66 !important;
      }}
      
      /* Radio Button Styling */
      .stRadio > div {{
        background: {card_bg};
        border-radius: 15px;
        padding: 10px;
        border: 1px solid {accent}33;
      }}
      
      /* Expander Styling */
      .streamlit-expanderHeader {{
        background: linear-gradient(90deg, {card_bg}, {accent}11) !important;
        border-radius: 10px !important;
        border: 1px solid {accent}33 !important;
      }}
      
      /* Chart Container Enhancement */
      .js-plotly-plot {{
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 5px 20px {accent}22 !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style='display:flex; align-items:center; justify-content:space-between; margin-bottom: 20px; position: relative; z-index: 1;'>
      <h1 style='margin:0; color:{text_color}; font-family: "Orbitron", monospace;'>
        🚀 FUTURISTIC DELIVERY & SALES COMMAND CENTER
      </h1>
      <div style='
        background: linear-gradient(45deg, {card_bg}, {accent}22);
        padding: 10px 20px;
        border-radius: 15px;
        border: 1px solid {accent}44;
        font-family: "Orbitron", monospace;
        font-weight: 700;
        color: {text_color};
        text-shadow: 0 0 5px {accent};
        box-shadow: 0 0 15px {accent}33;
      '
        ⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========== HELPER ==========
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = (
        out.columns.astype(str)
        .str.replace("\n", " ")
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )
    return out

def match_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = list(df.columns)
    for cand in candidates:
        for c in cols:
            if c == cand:
                return c
        for c in cols:
            if cand in c:
                return c
    return None

# Tentukan warna background sesuai mode
if mode == "Dark":
    bg_plot = "rgba(10,10,30,0.9)"
    bg_paper = "rgba(5,5,20,1)"
    txt_color = "white"
else:  # Light mode
    bg_plot = "white"
    bg_paper = "white"
    txt_color = "black"

# ---------- BAR CHART ----------
def bar_desc(df, x, y, title, color_base, color_highlight, template="plotly_white", is_avg=False):
    if df.empty:
        return None
    data = df.copy()
    data[y] = pd.to_numeric(data[y], errors="coerce").fillna(0)
    data = data.sort_values(y, ascending=False)

    fig = px.bar(
        data, x=x, y=y, template=template, title=title,
        color=data[y], color_continuous_scale=futur_colors
    )

    label_fmt = ",.0f" if not is_avg else ".2f"
    fig.update_traces(
        texttemplate=f"%{{y:{label_fmt}}}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        title_font_family="Orbitron",
        title_font_size=18,
        title_font_color=txt_color,
        xaxis_title=None, yaxis_title=None, bargap=0.35,
        coloraxis_showscale=False,
        plot_bgcolor=bg_plot,
        paper_bgcolor=bg_paper,
        font=dict(color=txt_color, family="Rajdhani")
    )

    fig.update_yaxes(linecolor=accent, gridcolor=accent_light)
    fig.update_xaxes(linecolor=accent, gridcolor=accent_light)

    return fig

# ---------- PIE CHART ----------
def pie_chart(df, names, values, title):
    if df.empty:
        return None
    fig = px.pie(
        df, names=names, values=values, template=chart_template,
        title=title, hole=0.35, color_discrete_sequence=futur_colors
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        title_font_family="Orbitron",
        title_font_size=18,
        title_font_color=txt_color,
        font=dict(color=txt_color, family="Rajdhani")
    )
    return fig

# ---------- GROUP BAR CHART ----------
def group_bar(df, x, y, color, title):
    if df.empty:
        return None
    fig = px.bar(
        df, x=x, y=y, color=color, template=chart_template,
        title=title, barmode="group", color_discrete_sequence=futur_colors
    )
    fig.update_layout(
        title_font_family="Orbitron",
        title_font_size=18,
        title_font_color=txt_color,
        font=dict(color=txt_color, family="Rajdhani")
    )
    return fig

# ---------- LINE CHART ----------
def line_chart(df, x, y, title):
    if df.empty:
        return None
    fig = px.line(
        df, x=x, y=y, template=chart_template,
        title=title, markers=True, color_discrete_sequence=futur_colors
    )
    fig.update_layout(
        title_font_family="Orbitron",
        title_font_size=18,
        title_font_color=txt_color,
        font=dict(color=txt_color, family="Rajdhani")
    )
    return fig

# ========== UPLOAD DATA DI SIDEBAR ==========
st.sidebar.markdown(
    f"""
    <div style='
        background: linear-gradient(135deg, {card_bg}, {accent}11);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid {accent}33;
        margin-bottom: 20px;
    '>
        <h3 style='color: {font_color}; font-family: "Orbitron", monospace; margin: 0 0 10px 0;'>
            📂 DATA UPLOAD CENTER
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

actual_file = st.sidebar.file_uploader("Upload File Actual (Excel)", type=["xlsx", "xls"])

if actual_file is None:
    s.markdown(
        f"""
        <div style='
            background: linear-gradient(45deg, {accent}22, {accent_light}22);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            border: 2px solid {accent}44;
            box-shadow: 0 0 30px {accent}33;
        '>
            <h2 style='color: {text_color}; font-family: "Orbitron", monospace; margin-bottom: 15px;'>
                🛸 AWAITING DATA TRANSMISSION
            </h2>
            <p style='color: {text_color}; font-family: "Rajdhani", sans-serif; font-size: 18px;'>
                Please upload your Exel file (2MB–50MB) to initialize the command center
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# Optional: batasi ukuran file
size_mb = actual_file.size / (1024 * 1024)
if size_mb < 2 or size_mb > 50:
    st.error("⚠️ File harus berukuran antara 2MB - 50MB")
    st.stop()

# Baca file
try:
    xls = pd.ExcelFile(actual_file)
    df_raw = xls.parse(0)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

# Normalisasi kolom
df = normalize_columns(df_raw)

# Deteksi kolom penting
col_dp_date = match_col(df, ["dp date", "delivery date", "tanggal pengiriman", "dp_date", "tanggal_pengiriman"]) or "dp date"
col_qty     = match_col(df, ["qty", "quantity", "volume"]) or "qty"
col_sales   = match_col(df, ["sales man", "salesman", "sales name", "sales_name"]) or "sales man"
col_dp_no   = match_col(df, ["dp no", "ritase", "dp_no", "trip"]) or "dp no"
col_area    = match_col(df, ["area"]) or None
col_plant   = match_col(df, ["plant name", "plant", "plant_name"]) or None
col_distance= match_col(df, ["distance", "jarak"]) or None
col_truck   = match_col(df, ["truck no", "truck", "truck_no", "nopol", "vehicle"]) or None
col_endcust = match_col(df, ["end customer name", "end customer", "customer", "end_customer"]) or None

# Cek kolom wajib
required_map = {
    col_dp_date: "Dp Date",
    col_qty:     "Qty",
    col_sales:   "Sales Man",
    col_dp_no:   "Dp No",
}
missing = [k for k in required_map.keys() if (k is None or k not in df.columns)]
if missing:
    label_missing = [required_map.get(m, str(m)) for m in missing]
    st.error("Kolom wajib tidak ditemukan: " + ", ".join(label_missing))
    st.stop()

# Konversi tipe data
df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# Assign kolom global
DF_DATE = col_dp_date
DF_QTY  = col_qty
DF_SLS  = col_sales
DF_TRIP = col_dp_no
DF_AREA = col_area
DF_PLNT = col_plant
DF_DIST = col_distance
DF_TRCK = col_truck
DF_ENDC = col_endcust

# ========== FILTER DATA ==========
with st.expander("🔍 ADVANCED FILTER CONTROL CENTER", expanded=True:
    min_d = df[DF_DATE].min().date()
    max_d = df[DF_DATE].max().date()

    start_col, end_col = st.columns(2)
    with start_col:
        start_date = st.date_input("Start Date", min_d)
    with end_col:
        end_date = st.date_input("End Date", max_d)

    if DF_AREA:
        areas = ["All"] + sorted(df[DF_AREA].dropna().astype(str).unique().tolist())
        sel_area = st.selectbox("Area", areas)
    else:
        sel_area = "All"

    if DF_PLNT:
        if DF_AREA and sel_area != "All":
            plants = ["All"] + sorted(
                df[df[DF_AREA].astype(str) == str(sel_area)][DF_PLNT]
                .dropna().astype(str).unique().tolist()
            )
        else:
            plants = ["All"] + sorted(df[DF_PLNT].dropna().astype(str).unique().tolist())
        sel_plant = st.selectbox("Plant Name", plants)
    else:
        sel_plant = "All"

    if st.button("🔄 RESET FILTERS"):
        st.experimental_rerun()

# Apply filter mask
mask = (df[DF_DATE].dt.date >= start_date) & (df[DF_DATE].dt.date <= end_date)
if DF_AREA and sel_area != "All":
    mask &= df[DF_AREA].astype(str) == str(sel_area)
if DF_PLNT and sel_plant != "All":
    mask &= df[DF_PLNT].astype(str) == str(sel_plant)

df_f = df.loc[mask].copy()
day_span = max((end_date - start_date).days + 1, 1)

# ========== SUMMARIZE (KPI CARDS) ==========
st.markdown("<div class='sectin-title'>🧭 SYSTEM METRICS OVERVIEW</div>", unsafe_allow_html=True)
kpi_cols = st.columns(7)
fmt0 = lambda x: f"{int(x):,}" if pd.notna(x) else "0"
fmtN0 = lambda x: f"{x:,.0f}" if pd.notna(x) else "0"

tot_area  = df_f[DF_AREA].nunique() if DF_AREA else 0
tot_plant = df_f[DF_PLNT].nunique() if DF_PLNT else 0
tot_vol   = float(df_f[DF_QTY].sum())
tot_truck = df_f[DF_TRCK].nunique() if (DF_TRCK and DF_TRCK in df_f.columns) else 0
tot_trip  = df_f[DF_TRIP].nunique() if DF_TRIP in df_f.columns else 0
avg_vol_day = (tot_vol / day_span) if day_span > 0 else 0
avg_load_trip = (tot_vol / tot_trip) if tot_trip > 0 else 0

kpis = [
    ("🌍 TOTAL AREA", fmt0(tot_area)),
    ("🏭 TOTAL PLANT", fmt0(tot_plant)),
    ("📦 TOTAL VOLUME", fmtN0(tot_vol)),
    ("📅 AVG VOL/DAY", fmtN0(avg_vol_day)),
    ("🚛 TOTAL TRUCK", fmt0(tot_tru)),
    ("🧾 TOTAL TRIP", fmt0(tot_trip   ("⚖️ AVG LOAD/TRIP", fmtN0(avg_load_trip)),
]

for col, (label, value) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            "<div class='metric-card'>"
            f"<div class='metric-label'>{label}</div>"
            f"<div class='metric-value'>{value}</div>"
            "</div>",
            unsafe_allow_html=True,
        )

st.markdown(
    f"""
    <hr style='
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, {accent}, {accent_light}, transparent);
        margin: 30px 0;
        box-shadow: 0 0 10px {accent}44;
    '>
    """, 
    unsafe_allow_html=True
)

# ========== SWITCH DASHBOARD ==========
st.markdown("<div class='section-title'>🎛️ COMMAND CENTER SELECTION</div>", unsafe_allow_html=True)
pick = st.radio("", ["Logistic", "Sales & End Customer"], horizontal=True)

# ----------------------------------------------------
# LOGISTIC
# ----------------------------------------------------
if pick == "Logistic":
    st.markdown("<div class='sectin-title'>📦 LOGISTICS COMMAND CENTER</div>", unsafe_allow_html=True)

   # Chart: Total Volume per Area (Bar)
    if DF_AREA:
        vol_area = (
            df_f.groupby(DF_AREA, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Total Volume"})
            .sort_values("Total Volume", ascending=False)
        )
        fig2 = bar_desc(
            vol_area,
            x=DF_AREA,
            y="Total Volume",
            title="🌍 TOTAL VOLUME PER AREA ANALYSIS",
            color_base=accent,
            color_highlight=accent_light,
            template=chart_template
        )
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)

    # Chart: Total Volume / Day
    vol_day = (
        df_f.groupby(DF_DATE, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Total Volume"})
    )
    fig1 = bar_desc(vol_day, DF_DATE, "Total Volume", "📅 DAILY VOLUME TRACKING", accent, accent_light, chart_template)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

    # Chart Volume per Plant
    if DF_PLNT:
        vol_plant = (
            df_f.groupby(DF_PLNT, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QT: "Actual"})
        )
        fig3 = bar_desc(vol_plant, DF_PLNT, "Actual", "🏭 PLANT PERFORMANCE MATRIX", accent, accent_light, chart_template)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)

    # Chart g Volume / Day per Area
    if DF_AREA:
        avg_area = df_f.groupby(DF_AREA, as_index=False)[DF_QTY].sum()
        avg_area["Avg/Day"] = avg_area[DF_QTY] / day_span
        fig4 = bar_desc(avg_area[[DF_AREA, "Avg/Day"]], DF_AREA, "Avg/Day", "🌍 AVG VOLUME / DAY PER AREA", accent, accent_light, char_template, is_avg=True)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)

    # Chart Avg Volume / Day per Plant
    if DF_PLNT:
        avg_plant = df_f.groupby(DF_PLNT, as_index=False)[DF_QTY].sum()
        avg_plant["Avg/Day"] = avg_plant[DF_QTY] / day_span
        fig5 = bar_desc(avg_plant[[DF_PLNT, "Avg/Day"]], DF_PLNT, "Avg/Day", "🏭 AVG VOLUME / DAY PER PLANT", accent, accent_light, chart_template, is_avg=True)
        if fig5:
            st.plotly_chart(fig5, use_container_width=Tue)

    # Truck Utilization
    st.markdown("<div class='subtitle'>🚛 TRUCK UTILIZATION MATRIX</div>", unsafe_allow_html=True)
    if DF_TRCK:
        truck_vol = (
            df_f.groupby(DF_TRCK, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Total Volume"})
        )
        fig6 = bar_desc(truck_vol, DF_TRCK, "Total Volume", "🚛 TOTAL VOLUME PER TRUCK", accent, accent_light, chart_template)
        if fig6:
            st.plotly_chart(fig6, use_container_width=True)

        trips_per_truck = (
            df_f.groupby(DF_TRCK, as_index=False)[DF_TRIP]
            .nunique()
            .rename(columns={DF_TRIP: "Total Trip"})
        )
        
