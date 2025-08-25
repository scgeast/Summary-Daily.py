import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# PAGE CONFIG & THEME
# =========================
st.set_page_config(page_title="🚚 Sales & Delivery Dashboard", layout="wide")

# === THEME ===
st.sidebar.header("🎨 Display Mode")
mode = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if mode == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#0b0f19"
    card_bg = "#0f172a"
    text_color = "#FFFFFF"
    futur_colors = ["#00E5FF", "#FF00FF", "#39FF14", "#FFEA00", "#FF4D4D"]
    font_color = "#fff"
else:
    chart_template = "plotly_white"
    base_bg = "#FFFFFF"
    card_bg = "#F8FAFC"
    text_color = "#111827"
    futur_colors = ["#2563EB", "#7C3AED", "#06B6D4", "#D946EF", "#F59E0B"]
    font_color = "#111827"

# === STYLE ===
st.markdown(f"""
<style>
  .main {{ background-color: {base_bg}; color:{text_color}; }}
  .metric-card {{
    background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 70%, #00000022 100%);
    border-radius: 18px; padding: 16px;
  }}
  .metric-value {{ font-size:26px; font-weight:800; color:{font_color} !important; }}
  .metric-label {{ font-size:12px; opacity:.8; color:{font_color} !important; }}
  .section-title {{ font-size:22px; font-weight:800; margin:8px 0 6px 0; color:{text_color}; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:center;'>
  <h1 style='margin:0;color:{text_color}'>🚀 Sales & Delivery Dashboard</h1>
  <div style='opacity:.9;color:{text_color};font-weight:600;'>⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def normalize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)
    return df

def match_col(df, candidates):
    for cand in candidates:
        for c in df.columns:
            if c == cand or cand in c:
                return c
    return None

# =========================
# UPLOAD FILE
# =========================
with st.sidebar.expander("📂 Upload Data Files"):
    actual_file = st.file_uploader("Upload File Actual", type=["xlsx", "xls"])
    target_file = st.file_uploader("Upload File Target", type=["xlsx", "xls"])

df = None
if actual_file:
    df = pd.read_excel(actual_file)
elif target_file:
    df = pd.read_excel(target_file)

if df is None:
    st.warning("⚠️ Silakan upload minimal 1 file.")
    st.stop()

df = normalize_columns(df)

# =========================
# COLUMN MAPPING
# =========================
col_date = match_col(df, ["dp_date", "delivery_date", "tanggal_pengiriman"])
col_qty  = match_col(df, ["qty", "quantity", "volume"])
col_sales= match_col(df, ["salesman", "sales", "sales_name"])
col_truck= match_col(df, ["truck", "truck_no", "vehicle"])
col_trip = match_col(df, ["dp_no", "trip", "ritase"])
col_area = match_col(df, ["area"])
col_plant= match_col(df, ["plant"])
col_endcust = match_col(df, ["customer", "end_customer", "end_customer_name"])

# Validasi kolom wajib
required = [col_date, col_qty, col_sales, col_trip]
if any(c is None for c in required):
    st.error("Kolom wajib tidak ditemukan.")
    st.stop()

# =========================
# FORMAT DATA
# =========================
df[col_date] = pd.to_datetime(df[col_date], errors="coerce")
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# =========================
# FILTER
# =========================
with st.expander("🔍 Filter Data", expanded=True):
    start_date = st.date_input("Start Date", df[col_date].min())
    end_date   = st.date_input("End Date", df[col_date].max())

    area_options = ["All"] + sorted(df[col_area].dropna().unique()) if col_area else ["All"]
    area = st.selectbox("Area", area_options)

    plant_options = ["All"] + sorted(df[col_plant].dropna().unique()) if col_plant else ["All"]
    plant = st.selectbox("Plant", plant_options)

# Filter dataframe
mask = (df[col_date].dt.date >= start_date) & (df[col_date].dt.date <= end_date)
if col_area and area != "All":
    mask &= df[col_area] == area
if col_plant and plant != "All":
    mask &= df[col_plant] == plant
df_filtered = df.loc[mask]

if df_filtered.empty:
    st.info("Data kosong sesuai filter.")
    st.stop()

# =========================
# KPI CARDS
# =========================
st.markdown("<div class='section-title'>🧭 Summarize</div>", unsafe_allow_html=True)
kpi_cols = st.columns(7)

tot_area  = df_filtered[col_area].nunique() if col_area else 0
tot_plant = df_filtered[col_plant].nunique() if col_plant else 0
tot_vol   = df_filtered[col_qty].sum()
tot_truck = df_filtered[col_truck].nunique() if col_truck else 0
tot_trip  = df_filtered[col_trip].nunique()
day_span  = max((end_date - start_date).days+1,1)
avg_vol_day = tot_vol/day_span
avg_load_trip = tot_vol/tot_trip if tot_trip>0 else 0

fmt = lambda x: f"{x:,.0f}"

with kpi_cols[0]: st.metric("Total Area", fmt(tot_area))
with kpi_cols[1]: st.metric("Total Plant", fmt(tot_plant))
with kpi_cols[2]: st.metric("Total Volume", fmt(tot_vol))
with kpi_cols[3]: st.metric("Total Truck", fmt(tot_truck))
with kpi_cols[4]: st.metric("Total Trip", fmt(tot_trip))
with kpi_cols[5]: st.metric("Avg Volume/Day", fmt(avg_vol_day))
with kpi_cols[6]: st.metric("Avg Load/Trip", fmt(avg_load_trip))

st.markdown("<hr style='opacity:.2;'>", unsafe_allow_html=True)

# =========================
# SALES & DELIVERY PERFORMANCE
# =========================
st.markdown("<div class='section-title'>💰 Sales & Delivery Performance</div>", unsafe_allow_html=True)

# --- Volume per Salesman ---
if col_sales:
    vol_sales = df_filtered.groupby(col_sales)[col_qty].sum().reset_index().sort_values(col_qty, ascending=False)
    fig_sales = px.bar(vol_sales, x=col_sales, y=col_qty, text_auto=True,
                       template=chart_template, color=col_sales, color_discrete_sequence=futur_colors)
    fig_sales.update_layout(showlegend=False, yaxis_title="Volume")
    st.plotly_chart(fig_sales, use_container_width=True)

# --- Volume per End Customer (Top 15) ---
if col_endcust:
    vol_cust = df_filtered.groupby(col_endcust)[col_qty].sum().reset_index().sort_values(col_qty, ascending=False).head(15)
    fig_cust = px.bar(vol_cust, x=col_endcust, y=col_qty, text_auto=True,
                      template=chart_template, color=col_endcust, color_discrete_sequence=futur_colors)
    fig_cust.update_layout(showlegend=False, yaxis_title="Volume")
    st.plotly_chart(fig_cust, use_container_width=True)
