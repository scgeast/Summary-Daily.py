import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Page Config
# =========================
st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery & Sales", layout="wide")

# =========================
# Custom CSS (Dark Futuristic Style)
# =========================
st.markdown("""
<style>
    body {background-color: #0e1117;}
    .main {background-color: #0e1117; color: #e0e0e0;}
    .section-title {font-size:22px; font-weight:bold; margin-top:25px; margin-bottom:10px; color:#00FFFF;}
    .metric-card {
        padding:15px; border-radius:12px;
        background:linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color:white; text-align:center; box-shadow: 0px 4px 10px rgba(0,255,255,0.2);
    }
    .metric-value {font-size:26px; font-weight:bold; color:#00FFFF;}
    .metric-label {font-size:14px; color:#aaa;}
</style>
""", unsafe_allow_html=True)

# =========================
# Upload File
# =========================
with st.expander("📂 Upload File Data", expanded=False):  
    actual_file = st.file_uploader("Upload File Actual (Excel)", type=["xlsx", "xls"])
    target_file = st.file_uploader("Upload File Target (Excel)", type=["xlsx", "xls"])

# =========================
# Load Data
# =========================
df_actual, df_target = None, None

if actual_file is None:
    st.warning("⚠️ Silakan upload file Actual terlebih dahulu.")
else:
    df_actual = pd.read_excel(actual_file)
    st.success("✅ File Actual berhasil diupload.")

if target_file is not None:
    df_target = pd.read_excel(target_file)
    st.info("📂 File Target berhasil diupload.")

# =========================
# Filter Data
# =========================
with st.expander("🔎 Filter Data", expanded=True):  
    if df_actual is not None:
        # Contoh kolom filter, sesuaikan dengan struktur file Anda
        area_filter = st.multiselect("Pilih Area", df_actual["Area"].unique() if "Area" in df_actual else [])
        plant_filter = st.multiselect("Pilih Plant", df_actual["Plant"].unique() if "Plant" in df_actual else [])

        # Filter diterapkan
        df_filtered = df_actual.copy()
        if area_filter:
            df_filtered = df_filtered[df_filtered["Area"].isin(area_filter)]
        if plant_filter:
            df_filtered = df_filtered[df_filtered["Plant"].isin(plant_filter)]
    else:
        df_filtered = pd.DataFrame()

# =========================
# KPI Summary
# =========================
if not df_filtered.empty:
    st.markdown("<div class='section-title'>📊 KPI Summary</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df_filtered['Area'].nunique()}</div><div class='metric-label'>Total Area</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df_filtered['Plant'].nunique()}</div><div class='metric-label'>Plant</div></div>", unsafe_allow_html=True)
    with col3:
        if "Qty" in df_filtered:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{df_filtered['Qty'].sum():,.0f}</div><div class='metric-label'>Volume</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'><div class='metric-value'>98%</div><div class='metric-label'>Performance</div></div>", unsafe_allow_html=True)

# =========================
# Chart Section
# =========================
if not df_filtered.empty:
    with st.expander("📈 Delivery Performance", expanded=True):
        if "Salesman" in df_filtered and "Qty" in df_filtered:
            fig1 = px.bar(df_filtered, x="Salesman", y="Qty", title="Delivery by Salesman", color="Salesman")
            st.plotly_chart(fig1, use_container_width=True)

    with st.expander("🚚 Truck Utilization", expanded=False):
        if "Truck" in df_filtered and "Utilization" in df_filtered:
            fig2 = px.pie(df_filtered, names="Truck", values="Utilization", title="Truck Utilization")
            st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📦 Sales & Customer Performance", expanded=False):
        if "Customer" in df_filtered and "Qty" in df_filtered and "Salesman" in df_filtered:
            fig3 = px.bar(df_filtered, x="Customer", y="Qty", color="Salesman", barmode="group", title="Sales Volume per Customer")
            st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📉 Trend Analysis", expanded=False):
        if "Tanggal" in df_filtered and "Ritase" in df_filtered:
            fig4 = px.line(df_filtered, x="Tanggal", y="Ritase", title="Trend Ritase")
            st.plotly_chart(fig4, use_container_width=True)
