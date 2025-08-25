import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🚀 Sales & Delivery Performance", layout="wide")

# =========================
# THEME & COLORS
# =========================
st.sidebar.header("🎨 Display Mode")
mode = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if mode == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#0b0f19"
    card_bg = "#0f172a"
    text_color = "#FFFFFF"
    futur_colors = ["#00E5FF", "#FF00FF", "#39FF14", "#FFEA00", "#FF4D4D"]
else:
    chart_template = "plotly_white"
    base_bg = "#FFFFFF"
    card_bg = "#F8FAFC"
    text_color = "#111827"
    futur_colors = ["#2563EB", "#7C3AED", "#06B6D4", "#D946EF", "#F59E0B"]

st.markdown(f"""
<style>
    .main {{ background-color: {base_bg}; color:{text_color}; }}
    .section-title {{ font-size: 22px; font-weight: 800; margin: 8px 0 6px 0; color:{text_color}; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:center'>
<h1 style='margin:0;color:{text_color}'>🚀 Sales & Delivery Performance</h1>
<div style='opacity:.9;color:{text_color};font-weight:600;'>⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def normalize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
    return df

def match_col(df, candidates):
    for cand in candidates:
        for c in df.columns:
            if c == cand or cand in c:
                return c
    return None

# =========================
# UPLOAD FILES
# =========================
with st.sidebar.expander("📂 Upload Data Files", expanded=False):
    actual_file = st.file_uploader("Upload File Actual", type=["xlsx", "xls"], key="actual")
    target_file = st.file_uploader("Upload File Target", type=["xlsx", "xls"], key="target")

df_raw = None
if actual_file: df_raw = pd.read_excel(actual_file)
elif target_file: df_raw = pd.read_excel(target_file)
else:
    st.warning("⚠️ Upload minimal 1 file (Actual atau Target).")
    st.stop()

df = normalize_columns(df_raw)

# =========================
# MAPPING COLUMNS
# =========================
col_dp_date = match_col(df, ["dp date","delivery date","tanggal pengiriman"])
col_qty     = match_col(df, ["qty","quantity","volume"])
col_sales   = match_col(df, ["sales man","salesman","sales name"])
col_dp_no   = match_col(df, ["dp no","ritase","trip"])
col_area    = match_col(df, ["area"])
col_plant   = match_col(df, ["plant name","plant"])
col_distance= match_col(df, ["distance","jarak"])
col_truck   = match_col(df, ["truck no","truck","nopol","vehicle"])
col_endcust = match_col(df, ["end customer","end_customer"])

# =========================
# VALIDASI KOLOM
# =========================
required_cols = [col_dp_date, col_qty, col_sales, col_dp_no]
for c in required_cols:
    if c not in df.columns:
        st.error(f"Kolom wajib '{c}' tidak ditemukan!")
        st.stop()

# =========================
# FORMAT DATA
# =========================
df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# =========================
# FILTER DATA
# =========================
with st.expander("🔍 Filter Data", expanded=True):
    start_date = st.date_input("Start Date", df[col_dp_date].min())
    end_date = st.date_input("End Date", df[col_dp_date].max())

    area_options = ["All"] + sorted(df[col_area].dropna().unique()) if col_area in df.columns else ["All"]
    area = st.selectbox("Area", area_options)

    plant_options = ["All"] + sorted(df[col_plant].dropna().unique()) if col_plant in df.columns else ["All"]
    plant = st.selectbox("Plant Name", plant_options)

mask = (df[col_dp_date].dt.date >= start_date) & (df[col_dp_date].dt.date <= end_date)
if col_area in df.columns and area!="All": mask &= df[col_area]==area
if col_plant in df.columns and plant!="All": mask &= df[col_plant]==plant
df_filtered = df.loc[mask].copy()
day_span = max((end_date-start_date).days+1,1)

if df_filtered.empty:
    st.info("Tidak ada data sesuai filter yang dipilih.")

# =========================
# KPI CARDS
# =========================
st.markdown("<div class='section-title'>🧭 KPI Summary</div>", unsafe_allow_html=True)
kpi_cols = st.columns(7)
st.metric("Total Area", df_filtered[col_area].nunique() if col_area in df_filtered.columns else 0)
st.metric("Total Plant", df_filtered[col_plant].nunique() if col_plant in df_filtered.columns else 0)
st.metric("Total Volume", df_filtered[col_qty].sum() if col_qty in df_filtered.columns else 0)
st.metric("Total Truck", df_filtered[col_truck].nunique() if col_truck in df_filtered.columns else 0)
st.metric("Total Trip", df_filtered[col_dp_no].nunique() if col_dp_no in df_filtered.columns else 0)
st.metric("Avg Volume/Day", df_filtered[col_qty].sum()/day_span if day_span>0 else 0)
st.metric("Avg Load/Trip", df_filtered[col_qty].sum()/df_filtered[col_dp_no].nunique() if df_filtered[col_dp_no].nunique()>0 else 0)

st.markdown("<hr style='opacity:.2;'>", unsafe_allow_html=True)

# =========================
# SALES & DELIVERY CHARTS
# =========================
st.markdown("<div class='section-title'>📊 Sales & Delivery Performance</div>", unsafe_allow_html=True)

# 1. Volume per Area
if col_area in df_filtered.columns and col_qty in df_filtered.columns:
    vol_area = df_filtered.groupby(col_area, as_index=False)[col_qty].sum().sort_values(col_qty,ascending=False)
    fig = px.bar(vol_area, x=col_area, y=col_qty, template=chart_template,
                 title="Total Volume per Area", text_auto=True, color=col_area, color_discrete_sequence=futur_colors)
    st.plotly_chart(fig, use_container_width=True)

# 2. Volume per Plant
if col_plant in df_filtered.columns and col_qty in df_filtered.columns:
    vol_plant = df_filtered.groupby(col_plant, as_index=False)[col_qty].sum()
    fig = px.bar(vol_plant, x=col_plant, y=col_qty, template=chart_template,
                 title="Total Volume per Plant", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# 3. Truck Utilization
if col_truck in df_filtered.columns and col_dp_no in df_filtered.columns:
    truck_util = df_filtered.groupby(col_truck, as_index=False)[col_dp_no].nunique().rename(columns={col_dp_no:"Total Trip"})
    fig = px.bar(truck_util, x=col_truck, y="Total Trip", template=chart_template, title="Truck Utilization", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# 4. Avg Load / Trip per Truck
if col_truck in df_filtered.columns and col_dp_no in df_filtered.columns and col_qty in df_filtered.columns:
    truck_vol = df_filtered.groupby(col_truck, as_index=False)[col_qty].sum()
    truck_trip = df_filtered.groupby(col_truck, as_index=False)[col_dp_no].nunique()
    truck_stats = pd.merge(truck_vol, truck_trip, on=col_truck)
    truck_stats["Avg Load/Trip"] = truck_stats[col_qty]/truck_stats[col_dp_no]
    fig = px.bar(truck_stats, x=col_truck, y="Avg Load/Trip", template=chart_template,
                 title="Average Load per Trip per Truck", text_auto=True, color=col_truck, color_discrete_sequence=futur_colors)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 5. Avg Distance per Area
if col_distance in df_filtered.columns and col_area in df_filtered.columns:
    dist_area = df_filtered.groupby(col_area, as_index=False)[col_distance].mean().rename(columns={col_distance:"Avg
