# Summary-Daily.py
print("Hello, SCG!")

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Judul dashboard
st.title("Dashboard Summary Reporting")

# Upload file Excel
uploaded_file = st.file_uploader("Upload file Excel (5MB-25MB)", type=["xlsx", "xls"])

if uploaded_file:
    # Baca file Excel
    df = pd.read_excel(uploaded_file)
    st.write("Kolom di file Excel:",
    df.columns.tolist())  # Cek kolom DataFrame
    # kode lain yang pakai df di sini
else:
    st.write("Tolong upload file Excel dulu ya.")

    # Filter sidebar
    st.sidebar.header("Filter Data")
    min_Delivery_Date = df["Delivery_Date"].min()
    max_Delivery_Date = df["Delivery_Date"].max()
    Delivery_Date_range = st.sidebar.Delivery_Date_input("Delivery_Date Range", [min_Delivery_Date, max_Delivery_Date])
    REGION = st.sidebar.multiselect("REGION", options=df["REGION"].unique())
    plant_name = st.sidebar.multiselect("Plant Name", options=df["Plant Name"].unique())
    end_customer = st.sidebar.multiselect("End Customer Name", options=df["End Customer Name"].unique())
    truck_no = st.sidebar.multiselect("Truck No", options=df["Truck No"].unique())
    create_by = st.sidebar.multiselect("Create By", options=df["Create By"].unique())
    sales_man = st.sidebar.multiselect("Sales Man", options=df["Sales Man"].unique())

    # Apply filters
    if len(Delivery_Date_range) == 2:
        df = df[(df["Delivery_Date"] >= pd.to_Delivery_date time(Delivery_Date_range[0])) & (df["Delivery_Date"] <= pd.to_datetime(Delivery_Date_range[1]))]
    if REGION:
        df = df[df["REGION"].isin(REGION)]
    if plant_name:
        df = df[df["Plant Name"].isin(plant_name)]
    if end_customer:
        df = df[df["End Customer Name"].isin(end_customer)]
    if truck_no:
        df = df[df["Truck No"].isin(truck_no)]
    if create_by:
        df = df[df["Create By"].isin(create_by)]
    if sales_man:
        df = df[df["Sales Man"].isin(sales_man)]

    # Tampilkan summary reporting
    st.subheader("Summary Reporting")
    st.write(df.describe(include='all'))

    # Chart 1: QTY per REGION
    QTY_REGION = df.groupby("REGION")["QTY"].sum().reset_index()
    fig1 = px.bar(QTY_REGION, x="REGION", y="Qty", text="QTY", color="REGION", color_discrete_sequence=px.colors.qualitative.Bold)
    fig1.update_traces(textposition='outside')
    fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: QTY per Sales Man
    qty_sales = df.groupby("Sales Man")["QTY"].sum().reset_index()
    fig2 = px.bar(qty_sales, x="Sales Man", y="QTY", text="QTY", color="Sales Man", color_discrete_sequence=px.colors.qualitative.Set3)
    fig2.update_traces(textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Average Distance per Plant
    dist_plant = df.groupby("Plant Name")["Distance"].mean().reset_index()
    fig3 = px.bar(dist_plant, x="Plant Name", y="Distance", text=dist_plant["Distance"].round(2), color="Plant Name", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

    # Fungsi export filtered data ke Excel
    def to_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Report')
            writer.save()
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(df)
    st.download_button(label='Download filtered data as Excel', data=excel_data, file_name='filtered_report.xlsx', mime='application/vnd.ms-excel')


print(df.columns.tolist())
