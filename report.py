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
    accent = "#7C3AED"
    accent_light = "#A78BFA"
    font_color = "#fff"
else:
    chart_template = "plotly_white"
    base_bg = "#FFFFFF"
    card_bg = "#F8FAFC"
    text_color = "#111827"
    accent = "#2563EB"
    accent_light = "#60A5FA"
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

def bar_desc(df, x, y, title, color_base, color_highlight, template="plotly_white", is_avg=False):
    if df.empty:
        return None
    data = df.copy()
    data[y] = pd.to_numeric(data[y], errors="coerce").fillna(0)
    data = data.sort_values(y, ascending=False)
    max_val = data[y].max()
    colors = [color_highlight if v == max_val else color_base for v in data[y]]
    fig = px.bar(data, x=x, y=y, template=template, title=title)
    fig.update_traces(marker_color=colors)
    label_fmt = ",.0f"
    fig.update_traces(
        texttemplate=f"%{{y:{label_fmt}}}",
        textposition="outside",
        cliponaxis=False
    )
    fig.update_layout(xaxis_title=None, yaxis_title=None, bargap=0.35)
    fig.update_yaxes(tickformat=label_fmt)
    return fig

# ========== UPLOAD DATA ==========
uploaded = st.file_uploader("📂 Upload File Excel Delivery (2MB–50MB)", type=["xlsx", "xls"], key="actual")
target_uploaded = st.file_uploader("📁 Upload File Target Volume (Plant/Area, optional)", type=["xlsx", "xls"], key="target")

if uploaded is None:
    st.info("Silakan upload file Excel delivery terlebih dahulu (ukuran 2MB–50MB).")
    st.stop()

size_mb = uploaded.size / (1024 * 1024)
if size_mb < 2 or size_mb > 50:
    st.error("⚠️ File harus berukuran antara 2MB - 50MB")
    st.stop()

try:
    xls = pd.ExcelFile(uploaded)
    df_raw = xls.parse(0)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

df = normalize_columns(df_raw)

col_dp_date = match_col(df, ["dp date", "delivery date", "tanggal pengiriman", "dp_date", "tanggal_pengiriman"]) or "dp date"
col_qty     = match_col(df, ["qty", "quantity", "volume"]) or "qty"
col_sales   = match_col(df, ["sales man", "salesman", "sales name", "sales_name"]) or "sales man"
col_dp_no   = match_col(df, ["dp no", "ritase", "dp_no", "trip"]) or "dp no"
col_area    = match_col(df, ["area"]) or None
col_plant   = match_col(df, ["plant name", "plant", "plant_name"]) or None
col_distance= match_col(df, ["distance", "jarak"]) or None
col_truck   = match_col(df, ["truck no", "truck", "truck_no", "nopol", "vehicle"]) or None
col_endcust = match_col(df, ["end customer name", "end customer", "customer", "end_customer"]) or None

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

df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

DF_DATE = col_dp_date
DF_QTY  = col_qty
DF_SLS  = col_sales
DF_TRIP = col_dp_no
DF_AREA = col_area
DF_PLNT = col_plant
DF_DIST = col_distance
DF_TRCK = col_truck
DF_ENDC = col_endcust

# ========== SIDEBAR FILTERS ==========
st.sidebar.header("🔍 Filter Data")
min_d = df[DF_DATE].min().date()
max_d = df[DF_DATE].max().date()
start_date = st.sidebar.date_input("Start Date", min_d)
end_date   = st.sidebar.date_input("End Date", max_d)

if DF_AREA:
    areas = ["All"] + sorted(df[DF_AREA].dropna().astype(str).unique().tolist())
    sel_area = st.sidebar.selectbox("Area", areas)
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
    sel_plant = st.sidebar.selectbox("Plant Name", plants)
else:
    sel_plant = "All"

if st.sidebar.button("🔄 Reset Filter"):
    st.experimental_rerun()

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
    ("⚖️ Avg Load/Trip<br><span style='font-size:11px'>(Total Volume : Total Trip)</span>", fmtN0(avg_load_trip)),
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

# =========================
# DASHBOARD LOGISTIC
# =========================
st.markdown("<div class='section-title'>📦 Logistic</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>🚚 Delivery Performance per Day</div>", unsafe_allow_html=True)

# CHART VOLUME PER PLANT (with target if uploaded)
if DF_PLNT:
    vol_plant = (
        df_f.groupby(DF_PLNT, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Actual"})
    )
    if target_uploaded is not None:
        df_target = pd.read_excel(target_uploaded)
        df_target.columns = df_target.columns.str.strip().str.lower()
        # cari kolom plant dan target
        plant_col = [c for c in df_target.columns if "plant" in c][0]
        target_col = [c for c in df_target.columns if "target" in c][0]
        df_target = df_target.rename(columns={plant_col: "Plant Name", target_col: "Target"})
        merged = pd.merge(
            vol_plant.rename(columns={DF_PLNT: "Plant Name"}),
            df_target[["Plant Name", "Target"]],
            on="Plant Name", how="left"
        )
        df_plot = merged.melt(id_vars="Plant Name", value_vars=["Actual", "Target"], var_name="Type", value_name="Volume")
        fig3 = px.bar(
            df_plot, x="Plant Name", y="Volume", color="Type", barmode="group", text="Volume",
            color_discrete_sequence=[accent, "#F59E42"], template=chart_template,
            title="Total Volume per Plant Name (Actual vs Target)"
        )
        fig3.update_traces(textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        fig3 = bar_desc(vol_plant, DF_PLNT, "Actual", "Total Volume per Plant Name", accent, accent_light, chart_template)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)

# CHART VOLUME PER AREA (with target if uploaded)
if DF_AREA:
    vol_area_bar = (
        df_f.groupby(DF_AREA, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Actual"})
    )
    if target_uploaded is not None:
        df_target = pd.read_excel(target_uploaded)
        df_target.columns = df_target.columns.str.strip().str.lower()
        area_col = [c for c in df_target.columns if "area" in c][0]
        target_col = [c for c in df_target.columns if "target" in c][0]
        df_target = df_target.rename(columns={area_col: "Area", target_col: "Target"})
        merged = pd.merge(
            vol_area_bar.rename(columns={DF_AREA: "Area"}),
            df_target[["Area", "Target"]],
            on="Area", how="left"
        )
        df_plot = merged.melt(id_vars="Area", value_vars=["Actual", "Target"], var_name="Type", value_name="Volume")
        fig_area = px.bar(
            df_plot, x="Area", y="Volume", color="Type", barmode="group", text="Volume",
            color_discrete_sequence=[accent, "#F59E42"], template=chart_template,
            title="Total Volume per Area (Actual vs Target)"
        )
        fig_area.update_traces(textposition='outside')
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        fig_area = bar_desc(vol_area_bar, DF_AREA, "Actual", "Total Volume per Area", accent, accent_light, chart_template)
        if fig_area:
            st.plotly_chart(fig_area, use_container_width=True)

# Tambahkan chart lain sesuai kebutuhan (avg per day, truck, dsb.)
