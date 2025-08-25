import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="Dashboard Monitoring Delivery And Sales L=23-51Xe", layout="wide")

color_palette = ["#00FFFF", "#8A2BE2", "#FFD700", "#00CED1", "#FF00FF", "#00FF00"]
st.sidebar.header("🎨 Pengaturan Tampilan")
theme = st.sidebar.radio("Pilih Tema", ["Gelap", "Terang"])
bg_color = "#0d0f15" if theme == "Gelap" else "white"
font_color = "white" if theme == "Gelap" else "black"

st.markdown(f"<h1 style='color:{font_color};text-align:center;'>📊 Dashboard Monitoring Delivery And Sales <span style='font-size:18px;'>(L=23-51Xe)</span></h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload file Excel Delivery", type=["xlsx", "xls"], key="delivery")

def find_col(df, patterns):
    def _norm(s): return re.sub(r"[\s_]", "", str(s).lower())
    cols_norm = {_norm(col): col for col in df.columns}
    for pat in patterns:
        pat_norm = _norm(pat)
        for k, v in cols_norm.items():
            if pat_norm == k or pat_norm in k:
                return v
    return None

field_map = {
    "Tanggal Pengiriman": ["dp date", "tanggal pengiriman", "delivery date"],
    "Volume": ["qty", "quantity", "vol"],
    "Salesman": ["sales man", "salesman", "sales name"],
    "Ritase": ["dp no", "rit", "trip"],
    "Distance": ["distance", "jarak"],
    "Plant Name": ["plant", "plant name"],
    "Area": ["area", "wilayah"],
    "Truck No": ["truck", "truck no", "truck number", "nopol"],
    "End Customer": ["end customer", "customer", "penerima"]
}

def boxed_metric(label, value, icon=""):
    st.markdown(f"""
    <div style="
        border: 2px solid {font_color};
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        background-color: {'#1f1f1f' if theme=='Gelap' else '#f5f5f5'};
        margin-bottom:10px;
    ">
        <h4 style='margin:5px;color:{font_color}'>{icon} {label}</h4>
        <p style='font-size:22px;margin:0;color:{font_color};font-weight:700'>{value}</p>
    </div>
    """, unsafe_allow_html=True)

def styled_chart(fig, height=None, font_size=12, margin=None, text_format=".2f", text_position="outside", show_legend=False, title_font_size=18):
    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color, size=font_size),
        title_font=dict(color=font_color, size=title_font_size),
        xaxis=dict(tickangle=45),
        showlegend=show_legend
    )
    if height: fig.update_layout(height=height)
    if margin: fig.update_layout(margin=margin)
    try:
        fig.update_traces(texttemplate=f"%{{text:{text_format}}}", textposition=text_position)
    except Exception:
        pass
    return fig

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    col_map = {}
    for std, alts in field_map.items():
        col_found = find_col(df, alts)
        col_map[std] = col_found if col_found else None

    for std, col in col_map.items():
        if col and col in df.columns:
            df[std] = df[col]
        else:
            df[std] = 1 if std in ["Volume", "Ritase", "Distance"] else "Unknown"

    df["Tanggal Pengiriman"] = pd.to_datetime(df["Tanggal Pengiriman"], errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0)
    df["Ritase"] = pd.to_numeric(df["Ritase"], errors="coerce").fillna(0)
    df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce").fillna(0)

    st.sidebar.header("🔎 Filter Data")
    date_min, date_max = df["Tanggal Pengiriman"].min(), df["Tanggal Pengiriman"].max()
    start_date = st.sidebar.date_input("Start Date", date_min)
    end_date = st.sidebar.date_input("End Date", date_max)
    area = st.sidebar.multiselect("Area", options=df["Area"].dropna().unique())
    plant = st.sidebar.multiselect("Plant Name", options=df["Plant Name"].dropna().unique())
    salesman = st.sidebar.multiselect("Salesman", options=df["Salesman"].dropna().unique())
    truck = st.sidebar.multiselect("Truck No", options=df["Truck No"].dropna().unique())

    if st.sidebar.button("🔄 Reset Filter"):
        st.experimental_rerun()

    df_filtered = df[
        (df["Tanggal Pengiriman"] >= pd.to_datetime(start_date)) &
        (df["Tanggal Pengiriman"] <= pd.to_datetime(end_date))
    ]
    if area:
        df_filtered = df_filtered[df_filtered["Area"].isin(area)]
    if plant:
        df_filtered = df_filtered[df_filtered["Plant Name"].isin(plant)]
    if salesman:
        df_filtered = df_filtered[df_filtered["Salesman"].isin(salesman)]
    if truck:
        df_filtered = df_filtered[df_filtered["Truck No"].isin(truck)]

    # ---- SUMMARIZE ----
    st.markdown(f"""<div style="display:flex;justify-content:center;align-items:center;">
    <img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' width='45' style='margin-right:12px;'/>
    <h2 style='color:{font_color};display:inline;'>Summarize</h2></div>""",unsafe_allow_html=True)

    total_area = df_filtered['Area'].nunique()
    total_plant = df_filtered['Plant Name'].nunique()
    total_truck = df_filtered['Truck No'].nunique()
    total_volume = df_filtered['Volume'].sum()
    avg_volume_per_day = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().mean() if not df_filtered.empty else 0
    total_trip = df_filtered['Ritase'].sum()
    avg_load_per_trip = (total_volume/total_trip) if total_trip != 0 else 0

    colA, colB, colC, colD, colE, colF, colG = st.columns(7)
    with colA: boxed_metric("Total Area", total_area, "🌐")
    with colB: boxed_metric("Total Plant", total_plant, "🏭")
    with colC: boxed_metric("Total Volume", f"{total_volume:,.2f}", "📦")
    with colD: boxed_metric("Avg Volume /Day", f"{avg_volume_per_day:,.2f}", "📅")
    with colE: boxed_metric("Total Truck", total_truck, "🚚")
    with colF: boxed_metric("Total Trip", f"{total_trip:,.0f}", "🔄")
    with colG: boxed_metric("Avg Load per Trip", f"{avg_load_per_trip:,.2f}", "⚖️")

    # ===== VOLUME PER DAY =====
    st.markdown(f"<h2 style='color:{font_color}'>📈 Volume Per Day</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        sales_trend = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().reset_index()
        fig_sales_trend = px.line(sales_trend, x="Tanggal Pengiriman", y="Volume", text="Volume", title="Volume Per Day")
        fig_sales_trend.update_traces(mode="lines+markers+text", textposition="top center")
        st.plotly_chart(styled_chart(fig_sales_trend, height=400, font_size=13, text_position="top center"),
                        use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== VOLUME PER AREA =====
    st.markdown(f"<h2 style='color:{font_color}'>📊 Volume per Area</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        area_vol = df_filtered.groupby("Area")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
        fig_area = px.bar(area_vol, x="Area", y="Volume", text="Volume", color="Area", color_discrete_sequence=color_palette)
        st.plotly_chart(styled_chart(fig_area), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== AVG DISTANCE PER AREA =====
    st.markdown(f"<h2 style='color:{font_color}'>📏 Avg Distance per Area</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        area_dist = df_filtered.groupby("Area")["Distance"].mean().reset_index().sort_values(by="Distance", ascending=False)
        fig_area_dist = px.bar(area_dist, x="Area", y="Distance", text="Distance", color="Area", color_discrete_sequence=color_palette)
        fig_area_dist.update_yaxes(title="Avg Distance")
        st.plotly_chart(styled_chart(fig_area_dist), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== VOLUME PER PLANT =====
    st.markdown(f"<h2 style='color:{font_color}'>🏭 Volume per Plant</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        plant_vol = df_filtered.groupby("Plant Name")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
        fig_plant = px.bar(plant_vol, x="Plant Name", y="Volume", text="Volume", color="Plant Name", color_discrete_sequence=color_palette)
        st.plotly_chart(styled_chart(fig_plant), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== AVG DISTANCE PER PLANT =====
    st.markdown(f"<h2 style='color:{font_color}'>📏 Avg Distance per Plant</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        plant_dist = df_filtered.groupby("Plant Name")["Distance"].mean().reset_index().sort_values(by="Distance", ascending=False)
        fig_plant_dist = px.bar(plant_dist, x="Plant Name", y="Distance", text="Distance", color="Plant Name", color_discrete_sequence=color_palette)
        fig_plant_dist.update_yaxes(title="Avg Distance")
        st.plotly_chart(styled_chart(fig_plant_dist), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== PERFORMA SALESMAN =====
    st.markdown(f"<h2 style='color:{font_color}'>👤 Performa Salesman</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        sales_perf = df_filtered.groupby("Salesman")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
        fig_salesman = px.bar(sales_perf, x="Salesman", y="Volume", text="Volume", color="Salesman", color_discrete_sequence=color_palette)
        st.plotly_chart(styled_chart(fig_salesman, height=500), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== PERFORMA CUSTOMER =====
    st.markdown(f"<h2 style='color:{font_color}'>👥 Performa End Customer</h2>", unsafe_allow_html=True)
    if not df_filtered.empty and 'End Customer' in df_filtered.columns:
        cust_perf = df_filtered.groupby("End Customer")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
        fig_customer = px.bar(cust_perf, x="End Customer", y="Volume", text="Volume", color="End Customer", color_discrete_sequence=color_palette)
        st.plotly_chart(styled_chart(fig_customer, height=500), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== UTILISASI TRUCK (TOTAL TRIP PER TRUCK & AVG DISTANCE PER TRUCK) =====
    st.markdown(f"<h2 style='color:{font_color}'>🚚 Utilisasi Truck</h2>", unsafe_allow_html=True)
    colt1, colt2 = st.columns(2)
    if not df_filtered.empty:
        # Total Trip/Ritase per Truck
        with colt1:
            truck_trip = df_filtered.groupby("Truck No")["Ritase"].sum().reset_index().sort_values(by="Ritase", ascending=False)
            fig_truck = px.bar(truck_trip, x="Truck No", y="Ritase", text="Ritase", color="Truck No", color_discrete_sequence=color_palette)
            fig_truck.update_yaxes(title="Total Trip/Ritase")
            st.plotly_chart(styled_chart(fig_truck, height=400), use_container_width=True)
        # Avg Distance per Truck
        with colt2:
            truck_dist = df_filtered.groupby("Truck No")["Distance"].mean().reset_index().sort_values(by="Distance", ascending=False)
            fig_truck_dist = px.bar(truck_dist, x="Truck No", y="Distance", text="Distance", color="Truck No", color_discrete_sequence=color_palette)
            fig_truck_dist.update_yaxes(title="Avg Distance")
            st.plotly_chart(styled_chart(fig_truck_dist, height=400), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

    # ===== AVG LOAD PER TRUCK =====
    st.markdown(f"<h2 style='color:{font_color}'>⚖️ Avg Load per Truck</h2>", unsafe_allow_html=True)
    if not df_filtered.empty:
        avg_load_truck = df_filtered.groupby("Truck No")["Volume"].mean().reset_index().sort_values(by="Volume", ascending=False)
        fig_avgload = px.bar(avg_load_truck, x="Truck No", y="Volume", text="Volume", color="Truck No", color_discrete_sequence=color_palette)
        fig_avgload.update_yaxes(title="Avg Volume per Trip")
        st.plotly_chart(styled_chart(fig_avgload, height=400), use_container_width=True)
    else:
        st.info("Tidak ada data untuk chart ini.")

else:
    st.info("Silakan upload file Excel Delivery terlebih dahulu untuk menampilkan dashboard.")
