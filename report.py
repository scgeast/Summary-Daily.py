import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="🚀 Dashboard Monitoring Delivery And Sales",
    layout="wide"
)

# =========================
# Custom CSS (Futuristic Neon Theme)
# =========================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Poppins:wght@300;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(90deg, #00F5D4, #9B5DE5, #F15BB5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 8px #00F5D4;
    }

    .neon-card {
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        background: rgba(20,20,30,0.8);
        box-shadow: 0px 0px 15px rgba(0,245,212,0.6);
        color: #FFFFFF;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #00F5D4;
        text-shadow: 0px 0px 6px #9B5DE5;
    }

    .metric-label {
        font-size: 14px;
        font-weight: 400;
        color: #BBBBBB;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.subheader("🎨 Display Mode")
    mode = st.radio("Pilih Mode", ["Light", "Dark"], index=1)

    st.subheader("🔍 Filter Data")
    start_date = st.date_input("Start Date", datetime(2025,8,1))
    end_date = st.date_input("End Date", datetime(2025,8,24))
    area = st.selectbox("Area", ["EAST INDONESIA","WEST INDONESIA"])
    plant = st.selectbox("Plant Name", ["All","Plant A","Plant B"])

    if st.button("Reset Filter"):
        st.experimental_rerun()

# =========================
# Title
# =========================
col1, col2 = st.columns([8,2])
with col1:
    st.markdown("<h1 class='main-title'>🚀 Dashboard Monitoring Delivery And Sales</h1>", unsafe_allow_html=True)
with col2:
    st.write("⏱", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

# =========================
# Upload Files
# =========================
st.subheader("📂 Upload File Excel Delivery (2MB–50MB)")
upload_file = st.file_uploader("Upload Delivery File", type=["xlsx","xls"])

st.subheader("📂 Upload File Target Volume (Optional)")
upload_target = st.file_uploader("Upload Target File", type=["xlsx","xls"])

# =========================
# Dummy Data (contoh)
# =========================
if upload_file is None:
    df = pd.DataFrame({
        "Tanggal":["2025-08-01","2025-08-02","2025-08-03"],
        "Volume":[500,600,550],
        "Truck":[20,22,23],
        "Trip":[100,105,98],
        "Sales":["A","B","A"],
        "Customer":["Cust1","Cust2","Cust1"]
    })
else:
    df = pd.read_excel(upload_file)

# =========================
# Summarize Cards
# =========================
st.markdown("### ⏱ Summarize")
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.markdown("<div class='neon-card'><div class='metric-value'>1</div><div class='metric-label'>TOTAL AREA</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='neon-card'><div class='metric-value'>7</div><div class='metric-label'>TOTAL PLANT</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='neon-card'><div class='metric-value'>{df['Volume'].sum():,}</div><div class='metric-label'>TOTAL VOLUME</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='neon-card'><div class='metric-value'>{int(df['Volume'].mean()):,}</div><div class='metric-label'>AVG VOL/DAY</div></div>", unsafe_allow_html=True)
with col5:
    st.markdown(f"<div class='neon-card'><div class='metric-value'>{df['Truck'].sum():,}</div><div class='metric-label'>TOTAL TRUCK</div></div>", unsafe_allow_html=True)
with col6:
    st.markdown(f"<div class='neon-card'><div class='metric-value'>{df['Trip'].sum():,}</div><div class='metric-label'>TOTAL TRIP</div></div>", unsafe_allow_html=True)
with col7:
    st.markdown("<div class='neon-card'><div class='metric-value'>5</div><div class='metric-label'>AVG LOAD/TRIP</div></div>", unsafe_allow_html=True)

# =========================
# Tabs
# =========================
tab1, tab2 = st.tabs(["🚚 Logistic Dashboard","📊 Sales Dashboard"])

with tab1:
    st.subheader("📦 Daily Delivery Volume")
    fig = px.bar(df, x="Tanggal", y="Volume", color="Tanggal",
                 color_discrete_sequence=["#00F5D4","#9B5DE5","#F15BB5"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚛 Truck Utilization")
    fig2 = px.line(df, x="Tanggal", y="Truck",
                   markers=True, line_shape="spline",
                   color_discrete_sequence=["#9B5DE5"])
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("👨‍💼 Sales Performance")
    sales_perf = df.groupby("Sales")["Volume"].sum().reset_index()
    fig3 = px.pie(sales_perf, values="Volume", names="Sales",
                  color_discrete_sequence=["#00F5D4","#9B5DE5","#F15BB5"])
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🏢 Customer Performance")
    cust_perf = df.groupby("Customer")["Volume"].sum().reset_index()
    fig4 = px.bar(cust_perf, x="Customer", y="Volume",
                  color="Customer", text_auto=True,
                  color_discrete_sequence=["#00F5D4","#9B5DE5","#F15BB5"])
    st.plotly_chart(fig4, use_container_width=True)
