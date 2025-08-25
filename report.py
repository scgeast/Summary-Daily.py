import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# =========================
# Page Config & Theme Toggle
# =========================
st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery And Sales", layout="wide")

# -- Sidebar: Pilihan Mode --
st.sidebar.header("🎨 Display Mode")
mode = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

# -- Skema warna futuristik (biru/ungu neon) --
if mode == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#0b0f19"      # latar gelap kebiruan
    card_bg = "#0f172a"      # panel gelap
    text_color = "#FFFFFF"   # teks putih
    accent = "#7C3AED"       # ungu neon
    accent_light = "#A78BFA" # ungu muda (highlight)
else:
    chart_template = "plotly_white"
    base_bg = "#FFFFFF"      # latar terang
    card_bg = "#F8FAFC"      # panel terang
    text_color = "#111827"   # teks gelap
    accent = "#2563EB"       # biru neon
    accent_light = "#60A5FA" # biru muda (highlight)

# -- Sedikit CSS untuk kartu KPI & heading --
st.markdown(
    f"""
    <style>
      .main {{ background-color: {base_bg}; color:{text_color}; }}
      .metric-card {{
        background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 70%, {accent}22 100%);
        border: 1px solid {accent}33; border-radius: 18px; padding: 16px; box-shadow: 0 10px 30px #00000022;
      }}
      .metric-value {{ font-size: 26px; font-weight: 800; color:{text_color}; }}
      .metric-label {{ font-size: 12px; opacity: .8; text-transform: uppercase; letter-spacing:.03em; }}
      .section-title {{ font-size: 22px; font-weight: 800; margin: 8px 0 6px 0; color:{text_color}; }}
      .subtitle {{ font-size: 16px; opacity:.95; margin: 8px 0 8px 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Header + Realtime Clock
# =========================
st.markdown(
    f"""
    <div style='display:flex; align-items:center; justify-content:space-between;'>
      <h1 style='margin:0;color:{text_color}'>🚀 Dashboard Monitoring Delivery And Sales</h1>
      <div style='opacity:.9;color:{text_color};font-weight:600;'>⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# Helper Functions (Normalisasi & Visual)
# =========================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalisasi nama kolom agar pencarian kolom menjadi robust.
    - Lowercase
    - Hilangkan newline/spasi ganda
    - Trim spasi kiri/kanan
    """
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
    """Cari kolom pertama yang cocok dari daftar kandidat.
    - Pencocokan exact dulu, lalu partial (substring).
    - Kolom DataFrame diasumsikan sudah dinormalisasi oleh normalize_columns().
    """
    cols = list(df.columns)
    for cand in candidates:
        # exact match
        for c in cols:
            if c == cand:
                return c
        # partial match
        for c in cols:
            if cand in c:
                return c
    return None  # jika tidak ditemukan


def bar_desc(df, x, y, title, color_base, color_highlight, template="plotly_white", is_avg=False):
    """Helper membuat bar chart terurut desc + highlight nilai maksimum.
    - df: DataFrame yang sudah ringkas (x, y).
    - is_avg: True jika metrik adalah rata-rata → label tanpa desimal (sesuai requirement Avg tanpa koma).
    - Warna bar maksimum menggunakan color_highlight.
    - Semua label angka ditampilkan (textposition='outside').
    """
    if df.empty:
        return None
    data = df.copy()
    data[y] = pd.to_numeric(data[y], errors="coerce").fillna(0)
    data = data.sort_values(y, ascending=False)  # sort besar → kecil (kiri → kanan)
    max_val = data[y].max()

    # Susun warna: bar tertinggi pakai highlight
    colors = [color_highlight if v == max_val else color_base for v in data[y]]

    fig = px.bar(data, x=x, y=y, template=template, title=title)
    fig.update_traces(marker_color=colors)

    # Format label: Avg → tanpa desimal; lainnya → tanpa desimal juga, sesuai rule angka ribuan.
    label_fmt = ",.0f"  # semua label tanpa desimal

    fig.update_traces(
        texttemplate=f"%{{y:{label_fmt}}}",
        textposition="outside",
        cliponaxis=False  # agar label tidak terpotong sumbu
    )
    fig.update_layout(xaxis_title=None, yaxis_title=None, bargap=0.35)
    fig.update_yaxes(tickformat=label_fmt)
    return fig

# =========================
# Upload Excel + Validasi Ukuran
# =========================
uploaded = st.file_uploader("📂 Upload File Excel (2MB–50MB)", type=["xlsx", "xls"])

if uploaded is None:
    st.info("Silakan upload file Excel terlebih dahulu (ukuran 2MB–50MB).")
    st.stop()

# Validasi ukuran (byte → MB)
size_mb = uploaded.size / (1024 * 1024)
if size_mb < 2 or size_mb > 50:
    st.error("⚠️ File harus berukuran antara 2MB - 50MB")
    st.stop()

# Baca sheet pertama secara aman
try:
    xls = pd.ExcelFile(uploaded)
    df_raw = xls.parse(0)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

# =========================
# Normalisasi & Pemetaan Kolom
# =========================
df = normalize_columns(df_raw)

# Catatan: daftar kandidat mencakup variasi penulisan & underscore
col_dp_date = match_col(df, ["dp date", "delivery date", "tanggal pengiriman", "dp_date", "tanggal_pengiriman"]) or "dp date"
col_qty     = match_col(df, ["qty", "quantity", "volume"]) or "qty"
col_sales   = match_col(df, ["sales man", "salesman", "sales name", "sales_name"]) or "sales man"
col_dp_no   = match_col(df, ["dp no", "ritase", "dp_no", "trip"]) or "dp no"
col_area    = match_col(df, ["area"]) or None
col_plant   = match_col(df, ["plant name", "plant", "plant_name"]) or None
col_distance= match_col(df, ["distance", "jarak"]) or None
col_truck   = match_col(df, ["truck no", "truck", "truck_no", "nopol", "vehicle"]) or None
col_endcust = match_col(df, ["end customer name", "end customer", "customer", "end_customer"]) or None

# Validasi kolom wajib: tanggal, qty, sales, dp no
required_map = {
    col_dp_date: "Dp Date",
    col_qty:     "Qty",
    col_sales:   "Sales Man",
    col_dp_no:   "Dp No",
}
missing = [k for k in required_map.keys() if (k is None or k not in df.columns)]
if missing:
    # Tampilkan label yang mudah dipahami pengguna
    label_missing = [required_map.get(m, str(m)) for m in missing]
    st.error("Kolom wajib tidak ditemukan: " + ", ".join(label_missing))
    st.stop()

# Konversi tipe & sanitasi nilai dasar
# - Tanggal → datetime (drop baris tanggal NaT)
# - Qty → numerik (NaN → 0)
df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# Canonical alias agar referensi ringkas di bawah
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
# Sidebar Filters (Date, Area, Plant + Reset)
# =========================
st.sidebar.header("🔍 Filter Data")

# Rentang tanggal dari data (pakai .date() agar widget date_input nyaman)
min_d = df[DF_DATE].min().date()
max_d = df[DF_DATE].max().date()
start_date = st.sidebar.date_input("Start Date", min_d)
end_date   = st.sidebar.date_input("End Date", max_d)

# Filter Area (jika kolom ada)
if DF_AREA:
    areas = ["All"] + sorted(df[DF_AREA].dropna().astype(str).unique().tolist())
    sel_area = st.sidebar.selectbox("Area", areas)
else:
    sel_area = "All"

# Filter Plant dependen Area
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

# Tombol reset → rerun aplikasi supaya nilai kembali default
if st.sidebar.button("🔄 Reset Filter"):
    st.experimental_rerun()

# Terapkan filter ke dataframe
mask = (df[DF_DATE].dt.date >= start_date) & (df[DF_DATE].dt.date <= end_date)
if DF_AREA and sel_area != "All":
    mask &= df[DF_AREA].astype(str) == str(sel_area)
if DF_PLNT and sel_plant != "All":
    mask &= df[DF_PLNT].astype(str) == str(sel_plant)

df_f = df.loc[mask].copy()

# Span hari untuk perhitungan rata-rata per hari
day_span = max((end_date - start_date).days + 1, 1)

# =========================
# Summarize (KPI Cards)
# =========================
st.markdown("<div class='section-title'>🧭 Summarize</div>", unsafe_allow_html=True)

kpi_cols = st.columns(6)

# Formatter: tanpa desimal + koma ribuan
fmt0 = lambda x: f"{int(x):,}" if pd.notna(x) else "0"
fmtN0 = lambda x: f"{x:,.0f}" if pd.notna(x) else "0"

# Hitung KPI utama
tot_area  = df_f[DF_AREA].nunique() if DF_AREA else 0
tot_plant = df_f[DF_PLNT].nunique() if DF_PLNT else 0
tot_vol   = float(df_f[DF_QTY].sum())
# Total truck unik (jika kolom ada)
tot_truck = df_f[DF_TRCK].nunique() if (DF_TRCK and DF_TRCK in df_f.columns) else 0
# Total trip (unique dp no) untuk menghindari double count
tot_trip  = df_f[DF_TRIP].nunique() if DF_TRIP in df_f.columns else 0
# Avg volume per day (keseluruhan range filter)
avg_vol_day = (tot_vol / day_span) if day_span > 0 else 0
# Avg load per trip (Total Volume / Total Trip); sesuai requirement tidak gunakan desimal pada label
avg_load_trip = (tot_vol / tot_trip) if tot_trip > 0 else 0

# Render kartu KPI bergaya futuristik
kpis = [
    ("🌍 Total Area", fmt0(tot_area)),
    ("🏭 Total Plant", fmt0(tot_plant)),
    ("📦 Total Volume", fmtN0(tot_vol)),
    ("📅 Avg Volume / Day", fmtN0(avg_vol_day)),
    ("🚛 Total Truck", fmt0(tot_truck)),
    ("🧾 Total Trip", fmt0(tot_trip)),
    ("⚖️ Avg Load per Trip", fmtN0(avg_load_trip)),
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
# Switcher: Pilih Dashboard
# =========================
st.markdown("<div class='section-title'>🎛️ Pilih Dashboard</div>", unsafe_allow_html=True)
pick = st.radio("", ["Logistic", "Sales & End Customer"], horizontal=True)

# ----------------------------------------------------
# DASHBOARD 1: LOGISTIC
# ----------------------------------------------------
if pick == "Logistic":
    st.markdown("<div class='section-title'>📦 Logistic</div>", unsafe_allow_html=True)

    # ---------- A. Delivery Performance per Day ----------
    st.markdown("<div class='subtitle'>🚚 Delivery Performance per Day</div>", unsafe_allow_html=True)

    # Chart 1: Total Volume / Day
    vol_day = (
        df_f.groupby(DF_DATE, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Total Volume"})
    )
    fig1 = bar_desc(vol_day, DF_DATE, "Total Volume", "Total Volume / Day", accent, accent_light, chart_template)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Total Volume per Area (Pie)
    if DF_AREA:
        vol_area = (
            df_f.groupby(DF_AREA, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Volume"})
            .sort_values("Volume", ascending=False)
        )
        fig2 = px.pie(
            vol_area, names=DF_AREA, values="Volume", template=chart_template,
            title="Total Volume per Area (Pie)"
        )
        # Tampilkan label + tarik slice terbesar sedikit (highlight)
        fig2.update_traces(
            textposition='inside',
            texttemplate='%{label}<br>%{value:,.0f} (%{percent})',
            pull=[0.08 if i == 0 else 0 for i in range(len(vol_area))]
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Total Volume per Plant Name
    if DF_PLNT:
        vol_plant = (
            df_f.groupby(DF_PLNT, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Total Volume"})
        )
        fig3 = bar_desc(vol_plant, DF_PLNT, "Total Volume", "Total Volume per Plant Name", accent, accent_light, chart_template)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)

    # Chart 4: Avg Volume / Day per Area (Total per Area / hari)
    if DF_AREA:
        avg_area = df_f.groupby(DF_AREA, as_index=False)[DF_QTY].sum()
        avg_area["Avg/Day"] = avg_area[DF_QTY] / day_span
        fig4 = bar_desc(avg_area[[DF_AREA, "Avg/Day"]], DF_AREA, "Avg/Day", "Avg Volume / Day per Area", accent, accent_light, chart_template, is_avg=True)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)

    # Chart 5: Avg Volume / Day per Plant Name (Total Plant / hari)
    if DF_PLNT:
        avg_plant = df_f.groupby(DF_PLNT, as_index=False)[DF_QTY].sum()
        avg_plant["Avg/Day"] = avg_plant[DF_QTY] / day_span
        fig5 = bar_desc(avg_plant[[DF_PLNT, "Avg/Day"]], DF_PLNT, "Avg/Day", "Avg Volume / Day per Plant Name", accent, accent_light, chart_template, is_avg=True)
        if fig5:
            st.plotly_chart(fig5, use_container_width=True)

    # ---------- B. Truck Utilization ----------
    st.markdown("<div class='subtitle'>🚛 Truck Utilization</div>", unsafe_allow_html=True)

    if DF_TRCK:
        # Chart 1: Total Volume per Truck (Sum Qty per Truck No)
        truck_vol = (
            df_f.groupby(DF_TRCK, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Total Volume"})
        )
        fig6 = bar_desc(truck_vol, DF_TRCK, "Total Volume", "Total Volume per Truck", accent, accent_light, chart_template)
        if fig6:
            st.plotly_chart(fig6, use_container_width=True)

        # Chart 2: Total Trip per Truck (unique DP No per Truck)
        trips_per_truck = (
            df_f.groupby(DF_TRCK, as_index=False)[DF_TRIP]
            .nunique()
            .rename(columns={DF_TRIP: "Total Trip"})
        )
        fig7 = bar_desc(trips_per_truck, DF_TRCK, "Total Trip", "Total Trip per Truck", accent, accent_light, chart_template)
        if fig7:
            st.plotly_chart(fig7, use_container_width=True)

        # Chart 3: Avg Load per Trip per Truck = Volume Truck / Trip Truck
        avg_load = pd.merge(truck_vol, trips_per_truck, on=DF_TRCK, how='left')
        avg_load["Avg Load/Trip"] = np.where(avg_load["Total Trip"]>0, avg_load["Total Volume"] / avg_load["Total Trip"], 0)
        fig8 = bar_desc(avg_load[[DF_TRCK, "Avg Load/Trip"]], DF_TRCK, "Avg Load/Trip", "Avg Load per Trip per Truck", accent, accent_light, chart_template, is_avg=True)
        if fig8:
            st.plotly_chart(fig8, use_container_width=True)

        # Chart 4: Avg Trip per Truck per Day = Total Trip Truck / Total Hari Filter
        avg_trip_day = trips_per_truck.copy()
        avg_trip_day["Avg Trip/Day"] = avg_trip_day["Total Trip"] / day_span if day_span>0 else 0
        fig9 = bar_desc(avg_trip_day[[DF_TRCK, "Avg Trip/Day"]], DF_TRCK, "Avg Trip/Day", "Avg Trip per Truck per Day", accent, accent_light, chart_template, is_avg=True)
        if fig9:
            st.plotly_chart(fig9, use_container_width=True)
    else:
        st.info("Kolom Truck No tidak ditemukan. Bagian Truck Utilization memerlukan kolom `Truck No`.")

    # ---------- C. Distance Analysis ----------
    st.markdown("<div class='subtitle'>📏 Distance Analysis</div>", unsafe_allow_html=True)
    if DF_DIST is None:
        st.info("Kolom Distance tidak ditemukan di file. Bagian Distance Analysis dilewati.")
    else:
        if DF_AREA:
            dist_area = (
                df_f.groupby(DF_AREA, as_index=False)[DF_DIST]
                .mean()
                .rename(columns={DF_DIST: "Avg Distance"})
            )
            fig10 = bar_desc(dist_area, DF_AREA, "Avg Distance", "Avg Distance per Area", accent, accent_light, chart_template, is_avg=True)
            if fig10:
                st.plotly_chart(fig10, use_container_width=True)
        if DF_PLNT:
            dist_plant = (
                df_f.groupby(DF_PLNT, as_index=False)[DF_DIST]
                .mean()
                .rename(columns={DF_DIST: "Avg Distance"})
            )
            fig11 = bar_desc(dist_plant, DF_PLNT, "Avg Distance", "Avg Distance per Plant", accent, accent_light, chart_template, is_avg=True)
            if fig11:
                st.plotly_chart(fig11, use_container_width=True)

# ----------------------------------------------------
# DASHBOARD 2: SALES & END CUSTOMER
# ----------------------------------------------------
if pick == "Sales & End Customer":
    st.markdown("<div class='section-title'>💼 Sales & End Customer Performance</div>", unsafe_allow_html=True)

    # A. Sales
    st.markdown("<div class='subtitle'>🧑‍💼 Sales</div>", unsafe_allow_html=True)
    sales = (
        df_f.groupby(DF_SLS, as_index=False)[DF_QTY]
        .sum()
        .rename(columns={DF_QTY: "Total Volume"})
    )
    figA = bar_desc(sales, DF_SLS, "Total Volume", "Total Volume per Sales Man", accent, accent_light, chart_template)
    if figA:
        st.plotly_chart(figA, use_container_width=True)

    # B. End Customer
    if DF_ENDC:
        st.markdown("<div class='subtitle'>👥 End Customer</div>", unsafe_allow_html=True)
        endc = (
            df_f.groupby(DF_ENDC, as_index=False)[DF_QTY]
            .sum()
            .rename(columns={DF_QTY: "Total Volume"})
        )
        figB = bar_desc(endc, DF_ENDC, "Total Volume", "Total Volume per End Customer Name", accent, accent_light, chart_template)
        if figB:
            st.plotly_chart(figB, use_container_width=True)
    else:
        st.info("Kolom End Customer Name tidak ditemukan di file.")

# =========================
# Export (Filtered Data → Excel)
# =========================
# Catatan: Streamlit akan membuat file di memori; pengguna mengunduh langsung.
export_name = "dashboard_export.xlsx"
if st.button("📥 Export ke Excel"):
    try:
        # Tulis hanya data yang sudah terfilter agar sesuai tampilan dashboard
        out_buf = pd.ExcelWriter(export_name, engine="xlsxwriter")
        df_f.to_excel(out_buf, index=False, sheet_name="FilteredData")
        out_buf.close()
        with open(export_name, "rb") as f:
            st.download_button("Download File", data=f.read(), file_name=export_name)
        st.success("✅ Data berhasil diexport ke Excel!")
    except Exception as e:
        st.error(f"Gagal export: {e}")
