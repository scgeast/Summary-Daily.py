import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Page Config
# =========================
st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery & Sales", layout="wide")

# =========================
# Upload Section
# =========================
with st.expander("📂 Upload File Data", expanded=False):
    actual_file = st.file_uploader("Upload File Actual (Excel)", type=["xlsx", "xls"])
    target_file = st.file_uploader("Upload File Target (Excel)", type=["xlsx", "xls"])

# =========================
# Load Data + Normalisasi Kolom
# =========================
df_actual, df_target = None, None
if actual_file is not None:
    df_actual = pd.read_excel(actual_file)

if target_file is not None:
    df_target = pd.read_excel(target_file)

# Tentukan data utama
df = df_actual if df_actual is not None else df_target

if df is None:
    st.warning("⚠️ Silakan upload minimal satu file (Actual / Target).")
    st.stop()

# ---- Normalisasi Nama Kolom ----
df.columns = (
    df.columns.str.strip()        # hapus spasi depan/belakang
    .str.lower()                  # huruf kecil semua
    .str.replace(" ", "_")        # spasi jadi underscore
    .str.replace("-", "_")        # tanda - jadi underscore
)

# Alias mapping supaya tetap konsisten
col_map = {
    "qty": "qty",
    "salesman": "salesman",
    "sales_man": "salesman",
    "plant": "plant_name",
    "plant_name": "plant_name",
    "area": "area",
    "dp_no": "dp_no",
    "dp_number": "dp_no",
    "dp_date": "dp_date",
    "tanggal": "dp_date"
}
df = df.rename(columns=lambda x: col_map.get(x, x))

# =========================
# Filter Section
# =========================
with st.expander("🎛️ Filter Data", expanded=True):
    if "dp_date" in df.columns:
        tanggal = st.multiselect("Pilih Tanggal", options=df["dp_date"].unique())
        if tanggal:
            df = df[df["dp_date"].isin(tanggal)]

    if "area" in df.columns:
        area = st.multiselect("Pilih Area", options=df["area"].unique())
        if area:
            df = df[df["area"].isin(area)]

    if "plant_name" in df.columns:
        plant = st.multiselect("Pilih Plant", options=df["plant_name"].unique())
        if plant:
            df = df[df["plant_name"].isin(plant)]

df_filtered = df.copy()

# =========================
# Summary Section
# =========================
with st.expander("📊 Summary KPI", expanded=True):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if "qty" in df_filtered.columns:
            st.metric("Total Volume", f"{df_filtered['qty'].sum():,.0f}")
        else:
            st.metric("Total Volume", "N/A")

    with c2:
        if "dp_no" in df_filtered.columns:
            st.metric("Total Ritase (DP No)", f"{df_filtered['dp_no'].nunique():,.0f}")
        else:
            st.metric("Total Ritase", "N/A")

    with c3:
        if "plant_name" in df_filtered.columns:
            st.metric("Jumlah Plant", f"{df_filtered['plant_name'].nunique():,.0f}")
        else:
            st.metric("Jumlah Plant", "N/A")

    with c4:
        if "salesman" in df_filtered.columns:
            st.metric("Jumlah Salesman", f"{df_filtered['salesman'].nunique():,.0f}")
        else:
            st.metric("Jumlah Salesman", "N/A")

# =========================
# Chart Section
# =========================
if not df_filtered.empty:

    with st.expander("📈 Delivery Performance", expanded=True):
        if "salesman" in df_filtered.columns and "qty" in df_filtered.columns:
            fig1 = px.bar(df_filtered, x="salesman", y="qty", title="Delivery by Salesman", color="salesman")
            st.plotly_chart(fig1, use_container_width=True)

    with st.expander("🚚 Truck Utilization", expanded=False):
        if "dp_no" in df_filtered.columns:
            truck_util = df_filtered.groupby("dp_no").size().reset_index(name="count")
            fig2 = px.bar(truck_util, x="dp_no", y="count", title="Truck Utilization (by DP No)")
            st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📦 Sales & Customer Performance", expanded=False):
        if "area" in df_filtered.columns and "qty" in df_filtered.columns:
            fig3 = px.bar(df_filtered, x="area", y="qty", color="salesman", barmode="group", title="Sales Volume per Area")
            st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📉 Trend Analysis", expanded=False):
        if "dp_date" in df_filtered.columns and "qty" in df_filtered.columns:
            trend = df_filtered.groupby("dp_date")["qty"].sum().reset_index()
            fig4 = px.line(trend, x="dp_date", y="qty", title="Trend Volume")
            st.plotly_chart(fig4, use_container_width=True)
