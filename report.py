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


# =========================
# File Upload Section (Sidebar + Expand/Collapse)
# =========================
with st.sidebar:
    with st.expander("📂 Upload Data Files", expanded=False):  
        actual_file = st.file_uploader("Upload File Actual", type=["xlsx", "xls"], key="actual")
        target_file = st.file_uploader("Upload File Target", type=["xlsx", "xls"], key="target")

# =========================
# Load Data
# =========================
df_actual, df_target = None, None

if actual_file is not None:
    try:
        df_actual = pd.read_excel(actual_file)
        size_mb = actual_file.size / (1024 * 1024)
        st.sidebar.caption(f"📄 File Actual: {actual_file.name} ({size_mb:.2f} MB)")
    except Exception as e:
        st.error(f"Gagal membaca file Actual: {e}")

if target_file is not None:
    try:
        df_target = pd.read_excel(target_file)
        size_mb = target_file.size / (1024 * 1024)
        st.sidebar.caption(f"🎯 File Target: {target_file.name} ({size_mb:.2f} MB)")
    except Exception as e:
        st.error(f"Gagal membaca file Target: {e}")

# =========================
# Tentukan DataFrame utama
# =========================
df_raw = None
if df_actual is not None:
    df_raw = df_actual.copy()
elif df_target is not None:
    df_raw = df_target.copy()

if df_raw is None:
    st.warning("⚠️ Silakan upload minimal 1 file (Actual atau Target).")
    st.stop()

# Normalisasi nama kolom biar tidak sensitif huruf besar / spasi
df = normalize_columns(df_raw)

# =========================
# Mapping Kolom (Normalisasi)
# =========================
col_dp_date = match_col(df, ["dp date", "delivery date", "tanggal pengiriman", "dp_date", "tanggal_pengiriman"]) or "dp date"
col_qty     = match_col(df, ["qty", "quantity", "volume"]) or "qty"
col_sales   = match_col(df, ["sales man", "salesman", "sales name", "sales_name"]) or "sales man"
col_dp_no   = match_col(df, ["dp no", "ritase", "dp_no", "trip"]) or "dp no"
col_area    = match_col(df, ["area"]) or None
col_plant   = match_col(df, ["plant name", "plant", "plant_name"]) or None
col_distance= match_col(df, ["distance", "jarak"]) or None
col_truck   = match_col(df, ["truck no", "truck", "truck_no", "nopol", "vehicle"]) or None
col_endcust = match_col(df, ["end customer name", "end customer", "customer", "end_customer"]) or None

# Validasi kolom wajib
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

# Pastikan format tanggal & angka benar
df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# =========================
# Preprocessing Data
# =========================
df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# Variabel Global
DF_DATE = col_dp_date
DF_QTY  = col_qty
DF_SLS  = col_sales
DF_TRIP = col_dp_no
DF_AREA = col_area
DF_PLNT = col_plant
DF_DIST = col_distance
DF_TRCK = col_truck
DF_ENDC = col_endcust

# =========================
# Filter Section (Expander)
# =========================
with st.expander("🔍 Filter Data", expanded=True):
    # --- Date Filter ---
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", df[col_dp_date].min())
    with col2:
        end_date = st.date_input("End Date", df[col_dp_date].max())

    # --- Area & Plant Filter ---
    col3, col4 = st.columns(2)
    with col3:
        area_options = ["All"]
        if col_area and col_area in df.columns:
            area_options += sorted(df[col_area].dropna().unique().tolist())
        area = st.selectbox("Area", area_options)

    with col4:
        plant_options = ["All"]
        if col_plant and col_plant in df.columns:
            plant_options += sorted(df[col_plant].dropna().unique().tolist())
        plant = st.selectbox("Plant Name", plant_options)

    # --- Reset Filter Button ---
    reset = st.button("🔄 Reset Filter")
    if reset:
        start_date = df[col_dp_date].min()
        end_date   = df[col_dp_date].max()
        area = "All"
        plant = "All"
        
# =========================
# Build Filtered DataFrame (WAJIB sebelum KPI & Chart)
# =========================
if DF_DATE not in df.columns:
    st.error("Kolom tanggal utama tidak ditemukan setelah mapping.")
    st.stop()

# Mask tanggal
mask = (df[DF_DATE].dt.date >= start_date) & (df[DF_DATE].dt.date <= end_date)

# Mask area
if DF_AREA and DF_AREA in df.columns and area != "All":
    mask &= df[DF_AREA].astype(str) == str(area)

# Mask plant
if DF_PLNT and DF_PLNT in df.columns and plant != "All":
    mask &= df[DF_PLNT].astype(str) == str(plant)

df_filtered = df.loc[mask].copy()

# Span hari (inklusif)
day_span = max((end_date - start_date).days + 1, 1)

# Kalau kosong kasih info
if df_filtered.empty:
    st.info("Tidak ada data sesuai filter yang dipilih.")


# =========================
# SUMMARIZE (KPI CARDS)
# =========================
st.markdown("<div class='section-title'>🧭 Summarize</div>", unsafe_allow_html=True)
kpi_cols = st.columns(7)

fmt0  = lambda x: f"{int(x):,}" if pd.notna(x) else "0"
fmtN0 = lambda x: f"{x:,.0f}" if pd.notna(x) else "0"

tot_area   = df_filtered[DF_AREA].nunique() if DF_AREA and DF_AREA in df_filtered.columns else 0
tot_plant  = df_filtered[DF_PLNT].nunique() if DF_PLNT and DF_PLNT in df_filtered.columns else 0
tot_vol    = float(df_filtered[DF_QTY].sum()) if DF_QTY in df_filtered.columns else 0
tot_truck  = df_filtered[DF_TRCK].nunique() if DF_TRCK and DF_TRCK in df_filtered.columns else 0
tot_trip   = df_filtered[DF_TRIP].nunique() if DF_TRIP and DF_TRIP in df_filtered.columns else 0
avg_vol_day   = (tot_vol / day_span) if day_span > 0 else 0
avg_load_trip = (tot_vol / tot_trip) if tot_trip > 0 else 0

with kpi_cols[0]:
    st.metric("Total Area", fmt0(tot_area))
with kpi_cols[1]:
    st.metric("Total Plant", fmt0(tot_plant))
with kpi_cols[2]:
    st.metric("Total Volume", fmtN0(tot_vol))
with kpi_cols[3]:
    st.metric("Total Truck", fmt0(tot_truck))
with kpi_cols[4]:
    st.metric("Total Trip", fmt0(tot_trip))
with kpi_cols[5]:
    st.metric("Avg Volume / Day", fmtN0(avg_vol_day))
with kpi_cols[6]:
    st.metric("Avg Load / Trip", fmtN0(avg_load_trip))
    
    st.markdown("<hr style='opacity:.2;'>", unsafe_allow_html=True)

# ========== SWITCH DASHBOARD ==========
st.markdown("<div class='section-title'>🎛️ Pilih Dashboard</div>", unsafe_allow_html=True)
pick = st.radio("", ["Logistic", "Sales & End Customer"], horizontal=True)

# =========================
# LOGISTIC PERFORMANCE
# =========================
if pick == "Logistic":
    st.markdown("<div class='section-title'>🚚 Logistic Performance</div>", unsafe_allow_html=True)

   # --- Volume per Area (Bar Chart) ---
if DF_AREA and DF_AREA in df_filtered.columns and DF_QTY in df_filtered.columns:
    vol_area = (
        df_filtered.groupby(DF_AREA, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Volume"})
        .sort_values("Volume", ascending=False)
    )
    fig_area = px.bar(
        vol_area, x=DF_AREA, y="Volume", template=chart_template,
        title="Total Volume per Area (Bar)", text_auto=True,
        color=DF_AREA, color_discrete_sequence=futur_colors
    )
    fig_area.update_layout(
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0,
            xanchor="left"
        )
    )
    st.plotly_chart(fig_area, use_container_width=True)

    # --- Volume per Plant ---
    if DF_PLNT and DF_PLNT in df_filtered.columns and DF_QTY in df_filtered.columns:
        vol_plant = (
            df_filtered.groupby(DF_PLNT, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Actual"})
        )
        fig_plant = px.bar(
            vol_plant, x=DF_PLNT, y="Actual", template=chart_template,
            title="Total Volume per Plant", text_auto=True
        )
        st.plotly_chart(fig_plant, use_container_width=True)

    # --- Truck Utilization ---
    if DF_TRCK and DF_TRIP and DF_TRCK in df_filtered.columns and DF_TRIP in df_filtered.columns:
        truck_util = (
            df_filtered.groupby(DF_TRCK, as_index=False)[DF_TRIP]
            .nunique()
            .rename(columns={DF_TRIP: "Total Trip"})
        )
        fig_truck = px.bar(
            truck_util, x=DF_TRCK, y="Total Trip", template=chart_template,
            title="Truck Utilization", text_auto=True
        )
        st.plotly_chart(fig_truck, use_container_width=True)

   # --- Average Load / Trip per Truck (Tanpa Legend) ---
if DF_TRCK and DF_TRIP and DF_QTY and DF_TRCK in df_filtered.columns and DF_TRIP in df_filtered.columns:
    # Total volume per truck
    truck_volume = (
        df_filtered.groupby(DF_TRCK, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Total Volume"})
    )

    # Total trip per truck
    truck_util = (
        df_filtered.groupby(DF_TRCK, as_index=False)[DF_TRIP]
        .nunique()
        .rename(columns={DF_TRIP: "Total Trip"})
    )

    # Gabungkan volume & trip
    truck_stats = pd.merge(truck_volume, truck_util, on=DF_TRCK)

    # Hitung Avg Load per Trip
    truck_stats["Avg Load / Trip"] = truck_stats["Total Volume"] / truck_stats["Total Trip"]

    # Sort descending
    truck_stats = truck_stats.sort_values("Avg Load / Trip", ascending=False)

    # Buat bar chart tanpa legend
    fig_avg_load = px.bar(
        truck_stats, x=DF_TRCK, y="Avg Load / Trip",
        template=chart_template,
        title="Average Load per Trip per Truck",
        text_auto=True,
        color=DF_TRCK,
        color_discrete_sequence=futur_colors
    )
    fig_avg_load.update_layout(showlegend=False, yaxis_title="Avg Load / Trip")
    st.plotly_chart(fig_avg_load, use_container_width=True)

    # --- Distance Analysis ---
    if DF_DIST and DF_DIST in df_filtered.columns:
        if DF_AREA and DF_AREA in df_filtered.columns:
            dist_area = (
                df_filtered.groupby(DF_AREA, as_index=False)[DF_DIST]
                .mean()
                .rename(columns={DF_DIST: "Avg Distance"})
            )
            fig_dist = px.bar(
                dist_area, x=DF_AREA, y="Avg Distance", template=chart_template,
                title="Average Distance per Area", text_auto=True
            )
            st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("Kolom Distance tidak ditemukan di file.")

# --- Average Distance per Plant (2 digit desimal) ---
if DF_PLNT and DF_DIST and DF_PLNT in df_filtered.columns and DF_DIST in df_filtered.columns:
    dist_plant = (
        df_filtered.groupby(DF_PLNT, as_index=False)[DF_DIST]
        .mean()
        .rename(columns={DF_DIST: "Avg Distance"})
        .sort_values("Avg Distance", ascending=False)
    )

    fig_dist_plant = px.bar(
        dist_plant,
        x=DF_PLNT,
        y="Avg Distance",
        template=chart_template,
        title="Average Distance per Plant",
        color=DF_PLNT,
        color_discrete_sequence=futur_colors
    )

    # Atur label angka 2 digit desimal
    fig_dist_plant.update_traces(
        texttemplate="%{y:.2f}",  # 2 angka desimal
        textposition="inside"
    )

    # Hilangkan legend supaya chart lebih bersih
    fig_dist_plant.update_layout(showlegend=False, yaxis_title="Avg Distance")
    st.plotly_chart(fig_dist_plant, use_container_width=True)


# =========================
# SALES PERFORMANCE
# =========================
elif pick == "Sales & End Customer":
    st.markdown("<div class='section-title'>💰 Sales Performance</div>", unsafe_allow_html=True)

    # --- Volume per Salesman ---
    if DF_SLS and DF_SLS in df_filtered.columns and DF_QTY in df_filtered.columns:
        vol_sales = (
            df_filtered.groupby(DF_SLS, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Volume"})
            .sort_values("Volume", ascending=False)
        )
        fig_sales = px.bar(
            vol_sales, x=DF_SLS, y="Volume", template=chart_template,
            title="Total Volume per Salesman", text_auto=True
        )
        st.plotly_chart(fig_sales, use_container_width=True)

    # --- Volume per End Customer ---
    if DF_ENDC and DF_ENDC in df_filtered.columns and DF_QTY in df_filtered.columns:
        vol_endcust = (
            df_filtered.groupby(DF_ENDC, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Volume"})
            .sort_values("Volume", ascending=False)
        )
        fig_endcust = px.bar(
            vol_endcust.head(15), x=DF_ENDC, y="Volume", template=chart_template,
            title="Top 15 End Customer by Volume", text_auto=True
        )
        st.plotly_chart(fig_endcust, use_container_width=True)
