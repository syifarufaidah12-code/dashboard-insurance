import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Biaya Asuransi", layout="wide")

st.title("Dashboard Biaya Asuransi Kesehatan")

def ku(age):
    if age <= 29:
        return "18-29"
    elif age <= 39:
        return "30-39"
    elif age <= 49:
        return "40-49"
    else:
        return "50-64"


def kbmi(bmi):
    if bmi < 18.5:
        return "Kurus"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obesitas"


@st.cache_data
def load_data():
    df = pd.read_csv("insurance.csv")
    df["kelompok_usia"] = df["age"].apply(ku)
    df["kategori_bmi"] = df["bmi"].apply(kbmi)
    return df


df = load_data()

urutan_usia = ["18-29", "30-39", "40-49", "50-64"]
urutan_bmi = ["Kurus", "Normal", "Overweight", "Obesitas"]

st.sidebar.header("Filter Dashboard")

usia_pilihan = st.sidebar.multiselect("Kelompok Usia", urutan_usia, default=urutan_usia)
perokok_pilihan = st.sidebar.multiselect(
    "Status Perokok", sorted(df["smoker"].unique()), default=sorted(df["smoker"].unique())
)
wilayah_pilihan = st.sidebar.multiselect(
    "Wilayah", sorted(df["region"].unique()), default=sorted(df["region"].unique())
)

filtered = df[
    (df["kelompok_usia"].isin(usia_pilihan))
    & (df["smoker"].isin(perokok_pilihan))
    & (df["region"].isin(wilayah_pilihan))
]

if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan filter.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah Peserta", f"{len(filtered):,}")
c2.metric("Total Biaya", f"$ {filtered['charges'].sum():,.0f}")
c3.metric("Rata-rata Biaya", f"$ {filtered['charges'].mean():,.0f}")
c4.metric("Rata-rata BMI", f"{filtered['bmi'].mean():.1f}")

st.divider()


col1, col2 = st.columns(2)

#Line chart: rata-rata biaya per usia
with col1:
    data = filtered.groupby("age", as_index=False)["charges"].mean()
    fig = px.line(data, x="age", y="charges", markers=True,
                  title="Rata-rata Biaya per Usia",
                  labels={"age": "Usia", "charges": "Rata-rata Biaya ($)"})
    st.plotly_chart(fig, width="stretch")

#Bar chart: rata-rata biaya per kategori BMI
with col2:
    data = filtered.groupby("kategori_bmi", as_index=False)["charges"].mean()
    fig = px.bar(data, x="kategori_bmi", y="charges", text_auto=".2s",
                 title="Rata-rata Biaya per Kategori BMI",
                 category_orders={"kategori_bmi": urutan_bmi},
                 labels={"kategori_bmi": "Kategori BMI", "charges": "Rata-rata Biaya ($)"})
    st.plotly_chart(fig, width="stretch")

col3, col4 = st.columns(2)

#Pie chart: proporsi perokok
with col3:
    data = filtered["smoker"].value_counts().reset_index()
    data.columns = ["smoker", "jumlah"]
    fig = px.pie(data, names="smoker", values="jumlah", hole=0.4,
                 title="Proporsi Perokok")
    st.plotly_chart(fig, width="stretch")

#Scatter plot: BMI vs biaya
with col4:
    fig = px.scatter(filtered, x="bmi", y="charges", color="smoker",
                     title="Hubungan BMI dan Biaya",
                     labels={"bmi": "BMI", "charges": "Biaya ($)", "smoker": "Perokok"})
    st.plotly_chart(fig, width="stretch")

#Histogram: distribusi biaya
fig = px.histogram(filtered, x="charges", nbins=30,
                   title="Distribusi Biaya Medis",
                   labels={"charges": "Biaya ($)"})
st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("Data Peserta")
st.dataframe(filtered, width="stretch", hide_index=True)