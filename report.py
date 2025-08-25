import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🚚 Dashboard Sales & Delivery Performance", layout="wide")

# ================= THEME & COLOR =================
st.sidebar.header("🎨 Display Mode")
mode = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if mode == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#0b0f19"
    card_bg = "#0f172a"
    text_color = "#FFFFFF"
    accent = "#00E5FF"
    accent_light = "#FF00FF"
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

st.markdown(f"""
<style>
.main {{ background-color: {base_bg}; color:{text_color}; }}
.metric-card {{
    background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 70%, {accent}22 100%);
    border: 1px solid {accent}33; border-radius: 18px; padding: 16px; box-shadow: 0 10px 30px #00000022;
}}
.metric-value {{ font-size: 26px; font-weight: 800; color: {font_color} !important; }}
.metric-label {{ font-size: 12px; opacity: .8; text-transform: uppercase; letter-spacing:.03em; color: {font_color} !important; }}
.section-title {{ font-size: 22px; font-weight: 800; margin: 8px 0 6px 0; color:{text_color}; }}
.subtitle {{ font-size: 16px; opacity:.95; margin: 8px 0 8px 0; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:space-between;'>
  <h1 style='margin:0;color:{text_color}'>🚀 Dashboard Sales & Delivery Performance</h1>
  <div style='opacity:.9;color:{text_color};font-weight:600;'>⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# ================= HELPER =================
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
    if df.empty: return None
    data = df.copy()
    data[y] = pd.to_numeric(data[y], errors="coerce").fillna(0)
    data = data.sort_values(y, ascending=False)
    fig = px.bar(
        data, x=x, y=y, template=template, title=title,
        color=data[y], color_continuous_scale=futur_colors
    )
    label_fmt = ",.0f"
    fig.update_traces(texttemplate=f"%{{y:{label_fmt}}}", textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title=None, yaxis_title=None, bargap=0.35, coloraxis_showscale=False)
    fig.update_yaxes(tickformat=label_fmt)
    return fig

# ================= UPLOAD DATA =================
with st.expander("📂 Upload File Data", expanded=True):  
    actual_file = st.file_uploader("Upload File Actual (Excel)", type=["xlsx", "xls"])
    target_file = st.file_uploader("Upload File Target (Excel, optional)", type=["xlsx", "xls"])

if actual_file is None:
    st.info("Silakan upload file Excel delivery terlebih dahulu (ukuran 2MB–50MB).")
    st.stop()

try:
    xls = pd.ExcelFile(actual_file)
    df_raw = xls.parse(0)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

df = normalize_columns(df_raw)

# ================= MATCH COLUMNS =================
col_dp_date = match_col(df, ["dp date","delivery date","tanggal pengiriman","dp_date","tanggal_pengiriman"]) or "dp date"
col_qty     = match_col(df, ["qty","quantity","volume"]) or "qty"
col_sales   = match_col(df, ["sales man","salesman","sales name","sales_name"]) or "sales man"
col_dp_no   = match_col(df, ["dp no","ritase","dp_no","trip"]) or "dp no"
col_endcust = match_col(df, ["end customer name","end customer","customer","end_customer"]) or None

required_map = {col_dp_date:"Dp Date", col_qty:"Qty", col_sales:"Sales Man", col_dp_no:"Dp No"}
missing = [k for k in required_map.keys() if (k is None or k not in df.columns)]
if missing:
    label_missing = [required_map.get(m,str(m)) for m in missing]
    st.error("Kolom wajib tidak ditemukan: "+", ".join(label_missing))
    st.stop()

df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# ================= FILTER DATA =================
st.markdown("<div class='section-title'>🔍 Filter Data</div>", unsafe_allow_html=True)
min_d = df[col_dp_date].min().date()
max_d = df[col_dp_date].max().date()
start_date, end_date = st.columns(2)
with start_date:
    start_date = st.date_input("Start Date", min_d)
with end_date:
    end_date   = st.date_input("End Date", max_d)

mask = (df[col_dp_date].dt.date >= start_date) & (df[col_dp_date].dt.date <= end_date)
df_f = df.loc[mask].copy()
day_span = max((end_date - start_date).days + 1,1)

# ================= KPI CARDS =================
st.markdown("<div class='section-title'>🧭 Summarize</div>", unsafe_allow_html=True)
kpi_cols = st.columns(7)
tot_vol   = df_f[col_qty].sum()
tot_trip  = df_f[col_dp_no].nunique() if col_dp_no in df_f.columns else 0
avg_vol_day = tot_vol/day_span
avg_load_trip = tot_vol/tot_trip if tot_trip>0 else 0

kpis = [("📦 Total Volume", f"{tot_vol:,.0f}"),
        ("📅 Avg Vol/Day", f"{avg_vol_day:,.0f}"),
        ("🧾 Total Trip", f"{tot_trip:,}"),
        ("⚖️ Avg Load/Trip", f"{avg_load_trip:,.0f}")]

for col, (label,value) in zip(kpi_cols,kpis):
    with col:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='opacity:.2;'>", unsafe_allow_html=True)

# ================= DASHBOARD SALES & DELIVERY =================
st.markdown("<div class='section-title'>💼 Sales & Delivery Performance</div>", unsafe_allow_html=True)

# Chart: Total Volume per Sales
sales = df_f.groupby(col_sales, as_index=False)[col_qty].sum().rename(columns={col_qty:"Total Volume"})
fig_sales = bar_desc(sales, col_sales, "Total Volume", "Total Volume per Sales Man", accent, accent_light, chart_template)
if fig_sales:
    st.plotly_chart(fig_sales, use_container_width=True)

# Chart: Total Volume per End Customer
if col_endcust:
    endc = df_f.groupby(col_endcust, as_index=False)[col_qty].sum().rename(columns={col_qty:"Total Volume"})
    fig_endc = bar_desc(endc, col_endcust, "Total Volume", "Total Volume per End Customer", accent, accent_light, chart_template)
    if fig_endc:
        st.plotly_chart(fig_endc, use_container_width=True)
else:
    st.info("Kolom End Customer Name tidak ditemukan di file.")
