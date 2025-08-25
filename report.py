import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery And Sales", layout="wide")

# ========== THEME & COLOR ==========
st.sidebar.header("🎨 Display Mode")
mode = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if mode == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#0b0f19"
    card_bg = "#0f172a"
    text_color = "#FFFFFF"
    accent = "#00E5FF"       # Cyan Neon
    accent_light = "#FF00FF" # Magenta Neon
    futur_colors = ["#00E5FF", "#FF00FF", "#39FF14", "#FFEA00", "#FF4D4D"]
    font_color = "#fff"
else:
    chart_template = "plotly_white"
    base_bg = "#FFFFFF"
    card_bg = "#F8FAFC"
    text_color = "#111827"
    accent = "#2563EB"
    accent_light = "#7C3AED"
    futur_colors = ["#2563EB", "#7C3AED", "#06B6D4", "#D946EF", "#F59E0B"]
    font_color = "#111827"

st.markdown(
    f"""
    <style>
      .main {{ background-color: {base_bg}; color:{text_color}; }}
      .metric-card {{
        background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 70%, {accent}22 100%);
        border: 1px solid {accent}33; border-radius: 18px; padding: 16px; box-shadow: 0 10px 30px #00000022;
      }}
      .metric-value {{
        font-size: 26px; font-weight: 800; color: {font_color} !important;
      }}
      .metric-label {{
        font-size: 12px; opacity: .8; text-transform: uppercase; letter-spacing:.03em;
        color: {font_color} !important;
      }}
      .section-title {{ font-size: 22px; font-weight: 800; margin: 8px 0 6px 0; color:{text_color}; }}
      .subtitle {{ font-size: 16px; opacity:.95; margin: 8px 0 8px 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style='display:flex; align-items:center; justify-content:space-between;'>
      <h1 style='margin:0;color:{text_color}'>🚀 Dashboard Monitoring Delivery And Sales</h1>
      <div style='opacity:.9;color:{text_color};font-weight:600;'>⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</div>
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
    label_fmt = ",.0f"
    fig.update_traces(
        texttemplate=f"%{{y:{label_fmt}}}",
        textposition="outside",
        cliponaxis=False
    )
    fig.update_layout(
        xaxis_title=None, yaxis_title=None, bargap=0.35,
        coloraxis_showscale=False
    )
    fig.update_yaxes(tickformat=label_fmt)
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
    return fig

# ---------- GROUP BAR CHART ----------
def group_bar(df, x, y, color, title):
    if df.empty:
        return None
    fig = px.bar(
        df, x=x, y=y, color=color, template=chart_template,
        title=title, barmode="group", color_discrete_sequence=futur_colors
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
    return fig


# ========== UPLOAD DATA DI SIDEBAR ==========
st.sidebar.header("📂 Upload File Data")
actual_file = st.sidebar.file_uploader("Upload File Actual (Excel)", type=["xlsx", "xls"])
target_file = st.sidebar.file_uploader("Upload File Target (Excel)", type=["xlsx", "xls"])

if actual_file is None:
    st.info("Silakan upload file Actual terlebih dahulu (ukuran 2MB–50MB).")
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
        vol_area = df_f.groupby(DF_AREA, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"}).sort_values("Total Volume", ascending=False)
        fig2 = bar_desc(vol_area, DF_AREA, "Total Volume", "Total Volume per Area (Bar)", accent, accent_light, chart_template)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)

        # Trend checkbox
        show_trend_area = st.checkbox("Tampilkan Trend Volume per Area", key="trend_area")
        if show_trend_area:
            trend_area = df_f.groupby([DF_DATE, DF_AREA], as_index=False)[DF_QTY].sum()
            fig2_line = px.line(trend_area, x=DF_DATE, y=DF_QTY, color=DF_AREA, markers=True,
                                title="Trend Volume per Area", template=chart_template)
            st.plotly_chart(fig2_line, use_container_width=True)

    # Chart: Total Volume / Day
    vol_day = df_f.groupby(DF_DATE, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
    fig1 = bar_desc(vol_day, DF_DATE, "Total Volume", "Total Volume / Day", accent, accent_light, chart_template)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

    show_trend_day = st.checkbox("Tampilkan Trend Total Volume / Day", key="trend_day")
    if show_trend_day:
        fig1_line = px.line(vol_day, x=DF_DATE, y="Total Volume", markers=True,
                            title="Trend Total Volume / Day", template=chart_template)
        st.plotly_chart(fig1_line, use_container_width=True)

    # Truck Utilization - Trend per Truck
    if DF_TRCK:
        avg_load = df_f.groupby([DF_DATE, DF_TRCK], as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
        show_truck_trend = st.checkbox("Tampilkan Trend Load per Truck", key="trend_truck")
        if show_truck_trend:
            fig_truck_trend = px.line(avg_load, x=DF_DATE, y="Total Volume", color=DF_TRCK, markers=True,
                                      title="Trend Volume per Truck", template=chart_template)
            st.plotly_chart(fig_truck_trend, use_container_width=True)

# ----------------------------------------------------
# SALES & END CUSTOMER
# ----------------------------------------------------
if pick == "Sales & End Customer":
    st.markdown("<div class='section-title'>💼 Sales & End Customer Performance</div>", unsafe_allow_html=True)

    # Sales
    if DF_SLS:
        sales = df_f.groupby(DF_SLS, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
        figA = bar_desc(sales, DF_SLS, "Total Volume", "Total Volume per Sales Man", accent, accent_light, chart_template)
        if figA:
            st.plotly_chart(figA, use_container_width=True)

        # Trend checkbox
        show_trend_sales = st.checkbox("Tampilkan Trend per Sales Man", key="trend_sales")
        if show_trend_sales:
            trend_sales = df_f.groupby([DF_DATE, DF_SLS], as_index=False)[DF_QTY].sum()
            figA_line = px.line(trend_sales, x=DF_DATE, y=DF_QTY, color=DF_SLS, markers=True,
                                title="Trend Volume per Sales Man", template=chart_template)
            st.plotly_chart(figA_line, use_container_width=True)

    # End Customer
    if DF_ENDC:
        endc = df_f.groupby(DF_ENDC, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
        figB = bar_desc(endc, DF_ENDC, "Total Volume", "Total Volume per End Customer Name", accent, accent_light, chart_template)
        if figB:
            st.plotly_chart(figB, use_container_width=True)

        # Trend checkbox
        show_trend_endc = st.checkbox("Tampilkan Trend per End Customer", key="trend_endc")
        if show_trend_endc:
            trend_endc = df_f.groupby([DF_DATE, DF_ENDC], as_index=False)[DF_QTY].sum()
            figB_line = px.line(trend_endc, x=DF_DATE, y=DF_QTY, color=DF_ENDC, markers=True,
                                title="Trend Volume per End Customer", template=chart_template)
            st.plotly_chart(figB_line, use_container_width=True)
