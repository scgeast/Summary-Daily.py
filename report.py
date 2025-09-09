import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery And Sales", layout="wide")

# ========== NEW THEME BASED ON IMAGE ==========
# Using colors inspired by the example image
st.sidebar.header("🎨 Display Mode")
mode = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if mode == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#1a1a2e"  # Dark blue background
    card_bg = "#16213e"  # Slightly lighter dark blue
    text_color = "#FFFFFF"
    accent = "#0fccce"   # Cyan accent from image
    accent_light = "#00adb5" # Lighter cyan
    futur_colors = ["#0fccce", "#00adb5", "#ff5722", "#ff9a3c", "#e84545"]
    font_color = "#fff"
else:
    chart_template = "plotly_white"
    base_bg = "#f0f5f9"  # Light blue-gray background
    card_bg = "#ffffff"  # White cards
    text_color = "#222831"  # Dark text
    accent = "#0fccce"   # Cyan accent from image
    accent_light = "#00adb5" # Lighter cyan
    futur_colors = ["#0fccce", "#00adb5", "#ff5722", "#ff9a3c", "#e84545"]
    font_color = "#222831"

# ========== UPDATED CSS WITH IMAGE-INSPIRED STYLING ==========
st.markdown(
    f"""
    <style>
      .main {{
        background-color: {base_bg};
        color: {text_color};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      }}
      h1, h2, h3, h4, .section-title {{
        color: {text_color} !important;
        font-weight: 600;
        border-left: 4px solid {accent};
        padding-left: 10px;
      }}
      .metric-card {{
        background-color: {card_bg};
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-top: 3px solid {accent};
      }}
      .metric-value {{
        font-size: 24px;
        font-weight: 700;
        color: {accent} !important;
      }}
      .metric-label {{
        font-size: 12px;
        color: {text_color} !important;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }}
      .city-card {{
        background-color: {card_bg};
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 3px solid {accent};
      }}
      .progress-container {{
        background: rgba(15, 204, 206, 0.2);
        border-radius: 5px;
        height: 20px;
        margin: 10px 0;
        overflow: hidden;
      }}
      .progress-bar {{
        height: 100%;
        border-radius: 5px;
        background: {accent};
        text-align: center;
        line-height: 20px;
        color: white;
        font-weight: bold;
        font-size: 12px;
      }}
      /* Styling for data upload section */
      .stExpander {{
        background-color: {card_bg};
        border-radius: 8px;
        border: 1px solid rgba(15, 204, 206, 0.3);
      }}
      /* Radio button styling */
      .stRadio > div {{
        background-color: {card_bg};
        padding: 10px;
        border-radius: 8px;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style='display:flex; align-items:center; justify-content:space-between;'>
      <h1 style='margin:0;color:{text_color}'>🚚 Dashboard Monitoring Delivery And Sales</h1>
      <div style='opacity:.9;color:{text_color};font-weight:600;'>⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========== HELPER FUNCTIONS (SAME AS BEFORE) ==========
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
    bg_plot = "rgba(26, 26, 46, 0.9)"
    bg_paper = "rgba(22, 33, 62, 1)"
    txt_color = "white"
else:  # Light mode
    bg_plot = "white"
    bg_paper = "white"
    txt_color = "#222831"

# ---------- CHART FUNCTIONS (SAME AS BEFORE) ----------
def bar_desc(df, x, y, title, color_base, color_highlight, template="plotly_white", is_avg=False):
    if df.empty:
        return None
    data = df.copy()
    data[y] = pd.to_numeric(data[y], errors="coerce").fillna(0)
    data = data.sort_values(y, ascending=False)

    fig = px.bar(
        data, x=x, y=y, template=template, title=title,
        color=data[y], color_continuous_scale=[color_base, color_highlight]
    )

    label_fmt = ",.0f" if not is_avg else ".2f"
    fig.update_traces(
        texttemplate=f"%{{y:{label_fmt}}}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_title=None, yaxis_title=None, bargap=0.35,
        coloraxis_showscale=False,
        plot_bgcolor=bg_plot,
        paper_bgcolor=bg_paper,
        font=dict(color=txt_color)
    )

    return fig

def pie_chart(df, names, values, title):
    if df.empty:
        return None
    fig = px.pie(
        df, names=names, values=values, template=chart_template,
        title=title, hole=0.35, color_discrete_sequence=[accent, accent_light]
    )
    fig.update_traces(textinfo="percent+label")
    return fig

def group_bar(df, x, y, color, title):
    if df.empty:
        return None
    fig = px.bar(
        df, x=x, y=y, color=color, template=chart_template,
        title=title, barmode="group", color_discrete_sequence=[accent, accent_light]
    )
    return fig

def line_chart(df, x, y, title):
    if df.empty:
        return None
    fig = px.line(
        df, x=x, y=y, template=chart_template,
        title=title, markers=True, color_discrete_sequence=[accent]
    )
    return fig

# ========== UPLOAD DATA DI SIDEBAR ==========
st.sidebar.header("📂 Upload File Data")
actual_file = st.sidebar.file_uploader("Upload File Actual (Excel)", type=["xlsx", "xls"])

if actual_file is None:
    st.info("Silakan upload file Actual terlebih dahulu (ukuran 0.5MB–50MB).")
    st.stop()

# Optional: batasi ukuran file
size_mb = actual_file.size / (1024 * 1024)
if size_mb < 0.5 or size_mb > 50:
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
with st.expander("🔍 Filter Data", expanded=True):
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

    if st.button("🔄 Reset Filter"):
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
st.markdown("<div class='section-title'>🧭 Summarize</div>", unsafe_allow_html=True)
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
    ("🌍 Total Area", fmt0(tot_area)),
    ("🏭 Total Plant", fmt0(tot_plant)),
    ("📦 Total Volume", fmtN0(tot_vol)),
    ("📅 Avg Vol/Day", fmtN0(avg_vol_day)),
    ("🚛 Total Truck", fmt0(tot_truck)),
    ("🧾 Total Trip", fmt0(tot_trip)),
    ("⚖️ Avg Load/Trip", fmtN0(avg_load_trip)),
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

st.markdown("<hr style='opacity:.2;'>", unsafe_allow_html=True)

# ========== SWITCH DASHBOARD ==========
st.markdown("<div class='section-title'>🎛️ Pilih Dashboard</div>", unsafe_allow_html=True)
pick = st.radio("", ["Logistic", "Sales & End Customer"], horizontal=True)

# ----------------------------------------------------
# LOGISTIC
# ----------------------------------------------------
if pick == "Logistic":
    st.markdown("<div class='section-title'>📦 Logistic</div>", unsafe_allow_html=True)

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
            title="Total Volume per Area (Bar)",
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
    fig1 = bar_desc(vol_day, DF_DATE, "Total Volume", "Total Volume / Day", accent, accent_light, chart_template)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

    # Chart Volume per Plant
    if DF_PLNT:
        vol_plant = (
            df_f.groupby(DF_PLNT, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Actual"})
        )
        fig3 = bar_desc(vol_plant, DF_PLNT, "Actual", "Total Volume per Plant Name", accent, accent_light, chart_template)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)

    # Chart Avg Volume / Day per Area
    if DF_AREA:
        avg_area = df_f.groupby(DF_AREA, as_index=False)[DF_QTY].sum()
        avg_area["Avg/Day"] = avg_area[DF_QTY] / day_span
        fig4 = bar_desc(avg_area[[DF_AREA, "Avg/Day"]], DF_AREA, "Avg/Day", "Avg Volume / Day per Area", accent, accent_light, chart_template, is_avg=True)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)

    # Chart Avg Volume / Day per Plant
    if DF_PLNT:
        avg_plant = df_f.groupby(DF_PLNT, as_index=False)[DF_QTY].sum()
        avg_plant["Avg/Day"] = avg_plant[DF_QTY] / day_span
        fig5 = bar_desc(avg_plant[[DF_PLNT, "Avg/Day"]], DF_PLNT, "Avg/Day", "Avg Volume / Day per Plant Name", accent, accent_light, chart_template, is_avg=True)
        if fig5:
            st.plotly_chart(fig5, use_container_width=True)

    # Truck Utilization
    st.markdown("<div class='subtitle'>🚛 Truck Utilization</div>", unsafe_allow_html=True)
    if DF_TRCK:
        truck_vol = (
            df_f.groupby(DF_TRCK, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Total Volume"})
        )
        fig6 = bar_desc(truck_vol, DF_TRCK, "Total Volume", "Total Volume per Truck", accent, accent_light, chart_template)
        if fig6:
            st.plotly_chart(fig6, use_container_width=True)

        trips_per_truck = (
            df_f.groupby(DF_TRCK, as_index=False)[DF_TRIP]
            .nunique()
            .rename(columns={DF_TRIP: "Total Trip"})
        )
        fig7 = bar_desc(trips_per_truck, DF_TRCK, "Total Trip", "Total Trip per Truck", accent, accent_light, chart_template)
        if fig7:
            st.plotly_chart(fig7, use_container_width=True)

        avg_load = pd.merge(truck_vol, trips_per_truck, on=DF_TRCK, how='left')
        avg_load["Avg Load/Trip"] = np.where(avg_load["Total Trip"]>0, avg_load["Total Volume"] / avg_load["Total Trip"], 0)
        fig8 = bar_desc(avg_load[[DF_TRCK, "Avg Load/Trip"]], DF_TRCK, "Avg Load/Trip", "Avg Load per Trip per Truck", accent, accent_light, chart_template, is_avg=True)
        if fig8:
            st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info("Kolom Truck No tidak ditemukan.")

    # Distance Analysis
    st.markdown("<div class='subtitle'>📏 Distance Analysis</div>", unsafe_allow_html=True)
    if DF_DIST is None:
        st.info("Kolom Distance tidak ditemukan di file.")
    else:
        if DF_AREA:
            dist_area = (
                df_f.groupby(DF_AREA, as_index=False)[DF_DIST]
                .mean()
                .rename(columns={DF_DIST: "Avg Distance"})
            )
            fig10 = bar_desc(dist_area, DF_AREA, "Avg Distance", "Avg Distance per Area", accent, accent_light, chart_template, is_avg=True)
            if fig10:
                st.plotly_chart(fig10, use_container_width=True)
        if DF_PLNT:
            dist_plant = (
                df_f.groupby(DF_PLNT, as_index=False)[DF_DIST]
                .mean()
                .rename(columns={DF_DIST: "Avg Distance"})
            )
            fig11 = bar_desc(dist_plant, DF_PLNT, "Avg Distance", "Avg Distance per Plant", accent, accent_light, chart_template, is_avg=True)
            if fig11:
                st.plotly_chart(fig11, use_container_width=True)

# ----------------------------------------------------
# DASHBOARD 2: SALES & END CUSTOMER
# ----------------------------------------------------
if pick == "Sales & End Customer":
    st.markdown("<div class='section-title'>💼 Sales & End Customer Performance</div>", unsafe_allow_html=True)

    # Sales
    st.markdown("<div class='subtitle'>🧑‍💼 Sales</div>", unsafe_allow_html=True)
    sales = (
        df_f.groupby(DF_SLS, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Total Volume"})
    )
    figA = bar_desc(sales, DF_SLS, "Total Volume", "Total Volume per Sales Man", accent, accent_light, chart_template)
    if figA:
        st.plotly_chart(figA, use_container_width=True)

    # End Customer - Opsi pilihan
    if DF_ENDC:
        st.markdown("<div class='subtitle'>👥 End Customer</div>", unsafe_allow_html=True)
        
        # Tambahkan opsi untuk memilih tampilan
        view_option = st.radio(
            "Tampilkan:", 
            ["Semua Customer", "Top 25 Customer"], 
            horizontal=True
        )
        
        endc = (
            df_f.groupby(DF_ENDC, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Total Volume"})
            .sort_values("Total Volume", ascending=False)
        )
        
        if view_option == "Top 25 Customer":
            endc = endc.head(25)
            title = "Top 25 End Customers by Total Volume"
        else:
            title = "Total Volume per End Customer Name"
        
        figB = bar_desc(endc, DF_ENDC, "Total Volume", title, accent, accent_light, chart_template)
        if figB:
            st.plotly_chart(figB, use_container_width=True)
    else:
        st.info("Kolom End Customer Name tidak ditemukan di file.")
