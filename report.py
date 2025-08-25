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
# Load Data
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

# =========================
# Filter Section
# =========================
with st.expander("🎛️ Filter Data", expanded=True):
    st.write("Pilih filter untuk menyesuaikan dashboard:")

    if "Tanggal" in df.columns:
        tanggal = st.multiselect("Pilih Tanggal", options=df["Tanggal"].unique())
        if tanggal:
            df = df[df["Tanggal"].isin(tanggal)]

    if "Area" in df.columns:
        area = st.multiselect("Pilih Area", options=df["Area"].unique())
        if area:
            df = df[df["Area"].isin(area)]

    if "Plant" in df.columns:
        plant = st.multiselect("Pilih Plant", options=df["Plant"].unique())
        if plant:
            df = df[df["Plant"].isin(plant)]

df_filtered = df.copy()

# =========================
# Summary Section
# =========================
with st.expander("📊 Summary KPI", expanded=True):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if "Qty" in df_filtered.columns:
            st.metric("Total Volume", f"{df_filtered['Qty'].sum():,.0f}")
        else:
            st.metric("Total Volume", "N/A")

    with c2:
        if "Ritase" in df_filtered.columns:
            st.metric("Total Ritase", f"{df_filtered['Ritase'].sum():,.0f}")
        else:
            st.metric("Total Ritase", "N/A")

    with c3:
        if "Truck" in df_filtered.columns:
            st.metric("Jumlah Truck", f"{df_filtered['Truck'].nunique():,.0f}")
        else:
            st.metric("Jumlah Truck", "N/A")

    with c4:
        if "Salesman" in df_filtered.columns:
            st.metric("Jumlah Salesman", f"{df_filtered['Salesman'].nunique():,.0f}")
        else:
            st.metric("Jumlah Salesman", "N/A")

# =========================
# Chart Section (with fallback)
# =========================
if not df_filtered.empty:

    with st.expander("📈 Delivery Performance", expanded=True):
        if "Salesman" in df_filtered.columns and "Qty" in df_filtered.columns:
            fig1 = px.bar(df_filtered, x="Salesman", y="Qty", title="Delivery by Salesman", color="Salesman")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Kolom 'Salesman' dan 'Qty' tidak ditemukan. Menampilkan contoh chart.")
            dummy = df_filtered.head(10).reset_index()
            fig1 = px.bar(dummy, x=dummy.index, y=dummy[dummy.columns[0]], title="Dummy Chart - Delivery")
            st.plotly_chart(fig1, use_container_width=True)

    with st.expander("🚚 Truck Utilization", expanded=False):
        if "Truck" in df_filtered.columns and "Utilization" in df_filtered.columns:
            fig2 = px.pie(df_filtered, names="Truck", values="Utilization", title="Truck Utilization")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Kolom 'Truck' dan 'Utilization' tidak ditemukan. Menampilkan contoh chart.")
            dummy = df_filtered.head(10).reset_index()
            fig2 = px.pie(dummy, names=dummy.index, values=dummy[dummy.columns[0]], title="Dummy Chart - Utilization")
            st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📦 Sales & Customer Performance", expanded=False):
        if "Customer" in df_filtered.columns and "Qty" in df_filtered.columns and "Salesman" in df_filtered.columns:
            fig3 = px.bar(df_filtered, x="Customer", y="Qty", color="Salesman", barmode="group", title="Sales Volume per Customer")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Kolom 'Customer', 'Qty', 'Salesman' tidak lengkap. Menampilkan contoh chart.")
            dummy = df_filtered.head(10).reset_index()
            fig3 = px.bar(dummy, x=dummy.index, y=dummy[dummy.columns[0]], title="Dummy Chart - Sales & Customer")
            st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📉 Trend Analysis", expanded=False):
        if "Tanggal" in df_filtered.columns and "Ritase" in df_filtered.columns:
            fig4 = px.line(df_filtered, x="Tanggal", y="Ritase", title="Trend Ritase")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Kolom 'Tanggal' dan 'Ritase' tidak ditemukan. Menampilkan contoh chart.")
            dummy = df_filtered.reset_index()
            fig4 = px.line(dummy, x=dummy.index, y=dummy[dummy.columns[0]], title="Dummy Chart - Trend")
            st.plotly_chart(fig4, use_container_width=True)
