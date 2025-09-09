[file name]: image.png
[file content begin]
# Daily Delivery Monitoring

## Create List Order
- Total city order 2025 m³  
- Total Plant 2  

## List Order
- Total city Delivery 1361 m³  
- Total City Remains 193 m³  
- Total City Cancell 471 m³  
- Total Project Remain 3  

---

### Qty Delivery by Status
- Pending Delivered  
- Canceled  

---

### Plant Performance
- City Order  
- City Delivery  
- City Remains  

---

### Qty Order Per Day
- City Order Per Day  
- City Order Per Day  

---

### Daily Delivery Summary
- **Daily Delivery Denpasar**  
- Volume order: 1455 M3  
- Volume Delivered: 100 M3  
- Volume Remain: 103 M3  
- Project Remain: 1  

---

### Daily Delivery Glanyar
- Volume order: 570 M3  
- Volume Delivered: 263 M3  
- Volume Remain: 90 M3  
- Project Remain: 2  

---

### Prosentase Pencapalian: 76%  
- Prosentase Pencapalian: 46%


[file content end]

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# ========== FUTURISTIC CSS ==========
st.markdown(
    f"""
    <style>
      .main {{
        background: radial-gradient(circle at 20% 20%, {base_bg}, #1b2735, #090a0f);
        color:{text_color};
      }}
      .main::before {{
        content: "";
        position: fixed;
        top:0;left:0;right:0;bottom:0;
        background-image: linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
        background-size: 40px 40px;
        z-index:0;
      }}
      h1,h2,h3,h4,.section-title {{
        text-shadow: 0 0 8px {accent}, 0 0 16px {accent_light};
        color:{text_color} !important;
      }}
      .metric-card {{
        background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 70%, {accent}22 100%);
        border: 1px solid {accent}33; border-radius: 18px; padding: 16px; 
        box-shadow: 0 0 12px {accent}55, inset 0 0 25px {accent_light}11;
      }}
      .metric-value {{
        font-size: 26px; font-weight: 800; color: {font_color} !important;
        text-shadow: 0 0 6px {accent};
      }}
      .metric-label {{
        font-size: 12px; opacity: .8; text-transform: uppercase; letter-spacing:.03em;
        color: {font_color} !important;
      }}
      .progress-container {{
        background: rgba(255,255,255,0.1); 
        border-radius: 10px; 
        height: 20px; 
        margin: 10px 0;
        overflow: hidden;
      }}
      .progress-bar {{
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, {accent}, {accent_light});
        text-align: center;
        line-height: 20px;
        color: white;
        font-weight: bold;
        font-size: 12px;
      }}
      .section-title {{ font-size: 22px; font-weight: 800; margin: 8px 0 6px 0; }}
      .subtitle {{ font-size: 16px; opacity:.95; margin: 8px 0 8px 0; }}
      .city-card {{
        background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 70%, {accent}22 100%);
        border: 1px solid {accent}33; border-radius: 18px; padding: 16px; 
        box-shadow: 0 0 12px {accent}55, inset 0 0 25px {accent_light}11;
        margin-bottom: 20px;
      }}
      /* scrollbar */
      ::-webkit-scrollbar {{ width: 10px; }}
      ::-webkit-scrollbar-track {{ background: #0b0e17; }}
      ::-webkit-scrollbar-thumb {{ background: linear-gradient({accent}, {accent_light}); border-radius: 10px; }}
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

# Tentukan warna background sesuai mode
if mode == "Dark":
    bg_plot = "rgba(10,10,30,0.9)"
    bg_paper = "rgba(5,5,20,1)"
    txt_color = "white"
else:  # Light mode
    bg_plot = "white"
    bg_paper = "white"
    txt_color = "black"

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

    label_fmt = ",.0f" if not is_avg else ".2f"
    fig.update_traces(
        texttemplate=f"%{{y:{label_fmt}}}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_title=None, yaxis_title=None, bargap=0.35,
        coloraxis_showscale=False,
        plot_bgcolor=bg_plot,
        paper_bgcolor=bg_paper,
        font=dict(color=txt_color)
    )

    fig.update_yaxes(linecolor=accent, gridcolor=accent_light)
    fig.update_xaxes(linecolor=accent, gridcolor=accent_light)

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

if actual_file is None:
    st.info("Silakan upload file Actual terlebih dahulu (ukuran 0.5MB–50MB).")
    st.stop()

# Optional: batasi ukuran file
size_mb = actual_file.size / (1024 * 1024)
if size_mb < 0.5 or size_mb > 50:
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
                df[df[DF_AREA].ast(str) == str(sel_area)][DF_PLNT]
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

# ========== DASHBOARD LAYOUT INSPIRED BY IMAGE ==========
st.markdown("<div class='section-title'>📊 Delivery Monitoring Dashboard</div>", unsafe_allow_html=True)

# Create List Order Section
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='section-title'>📋 Create List Order</div>", unsafe_allow_html=True)
    
    # Create metrics for list order
    total_city_order = 2025
    total_plant = 2
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Total City Order</div>
            <div class='metric-value'>{total_city_order:,} m³</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Plant</div>
            <div class='metric-value'>{total_plant}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown("<div class='section-title'>📝 List Order</div>", unsafe_allow_html=True)
    
    # Create metrics for list order details
    total_city_delivery = 1361
    total_city_remains = 193
    total_city_cancel = 471
    total_project_remain = 3
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Total City Delivery</div>
            <div class='metric-value'>{total_city_delivery:,} m³</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Total City Remains</div>
            <div class='metric-value'>{total_city_remains:,} m³</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Total City Cancel</div>
            <div class='metric-value'>{total_city_cancel:,} m³</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Project Remain</div>
            <div class='metric-value'>{total_project_remain}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Qty Delivery by Status Section
st.markdown("<div class='section-title'>📦 Qty Delivery by Status</div>", unsafe_allow_html=True)

status_col1, status_col2 = st.columns(2)

with status_col1:
    # Create a pie chart for delivery status
    status_data = pd.DataFrame({
        'Status': ['Delivered', 'Pending', 'Canceled'],
        'Value': [70, 20, 10]
    })
    
    fig_status = px.pie(status_data, values='Value', names='Status', 
                        title='Delivery Status Distribution',
                        color_discrete_sequence=futur_colors)
    fig_status.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_status, use_container_width=True)

with status_col2:
    # Create metrics for delivery status
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Pending Delivered</div>
            <div class='metric-value'>20%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Canceled</div>
            <div class='metric-value'>10%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Plant Performance Section
st.markdown("<div class='section-title'>🏭 Plant Performance</div>", unsafe_allow_html=True)

plant_data = pd.DataFrame({
    'Plant': ['Plant A', 'Plant B', 'Plant C'],
    'City Order': [1000, 800, 600],
    'City Delivery': [800, 650, 500],
    'City Remains': [200, 150, 100]
})

fig_plant = px.bar(plant_data, x='Plant', y=['City Order', 'City Delivery', 'City Remains'],
                   title='Plant Performance Metrics', barmode='group',
                   color_discrete_sequence=futur_colors)
st.plotly_chart(fig_plant, use_container_width=True)

# Qty Order Per Day Section
st.markdown("<div class='section-title'>📅 Qty Order Per Day</div>", unsafe_allow_html=True)

# Generate sample daily data
dates = pd.date_range(start=datetime.now().date() - pd.Timedelta(days=7), 
                      end=datetime.now().date(), freq='D')
daily_data = pd.DataFrame({
    'Date': dates,
    'City Order Per Day': np.random.randint(100, 300, size=len(dates))
})

fig_daily = px.line(daily_data, x='Date', y='City Order Per Day',
                    title='Daily City Orders', markers=True,
                    color_discrete_sequence=[futur_colors[0]])
st.plotly_chart(fig_daily, use_container_width=True)

# Daily Delivery Summary Section
st.markdown("<div class='section-title'>🚚 Daily Delivery Summary</div>", unsafe_allow_html=True)

delivery_col1, delivery_col2 = st.columns(2)

with delivery_col1:
    st.markdown("<div class='city-card'>", unsafe_allow_html=True)
    st.markdown("**Daily Delivery Denpasar**")
    
    denpasar_order = 1455
    denpasar_delivered = 100
    denpasar_remain = 103
    denpasar_project_remain = 1
    denpasar_completion = (denpasar_delivered / denpasar_order) * 100 if denpasar_order > 0 else 0
    
    st.markdown(f"Volume order: {denpasar_order} M3")
    st.markdown(f"Volume Delivered: {denpasar_delivered} M3")
    st.markdown(f"Volume Remain: {denpasar_remain} M3")
    st.markdown(f"Project Remain: {denpasar_project_remain}")
    
    # Progress bar
    st.markdown(f"<div class='progress-container'><div class='progress-bar' style='width: {denpasar_completion}%'>{denpasar_completion:.1f}%</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with delivery_col2:
    st.markdown("<div class='city-card'>", unsafe_allow_html=True)
    st.markdown("**Daily Delivery Glanyar**")
    
    glanyar_order = 570
    glanyar_delivered = 263
    glanyar_remain = 90
    glanyar_project_remain = 2
    glanyar_completion = (glanyar_delivered / glanyar_order) * 100 if glanyar_order > 0 else 0
    
    st.markdown(f"Volume order: {glanyar_order} M3")
    st.markdown(f"Volume Delivered: {glanyar_delivered} M3")
    st.markdown(f"Volume Remain: {glanyar_remain} M3")
    st.markdown(f"Project Remain: {glanyar_project_remain}")
    
    # Progress bar
    st.markdown(f"<div class='progress-container'><div class='progress-bar' style='width: {glanyar_completion}%'>{glanyar_completion:.1f}%</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Completion Percentage Section
st.markdown("<div class='section-title'>📊 Prosentase Pencapaian</div>", unsafe_allow_html=True)

comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    completion_1 = 76
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Prosentase Pencapaian</div>
            <div class='progress-container' style='margin-top: 10px;'>
                <div class='progress-bar' style='width: {completion_1}%'>{completion_1}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with comp_col2:
    completion_2 = 46
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>Prosentase Pencapaian</div>
            <div class='progress-container' style='margin-top: 10px;'>
                <div class='progress-bar' style='width: {completion_2}%'>{completion_2}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
