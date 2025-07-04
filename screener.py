# Struktur multi-page Streamlit untuk Investrade Trading Tools

# ===================================== #
# File: Home.py (Halaman Utama)
# ===================================== #
import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Investrade Trading Tools", layout="wide")
st.title("📊 Investrade Trading Tools")

st.markdown("""
Selamat datang di tools trading saham IHSG.

Tools ini dibuat untuk para trader maupun investor saham Indonesia, di mana analisa prediksi di tools ini menggunakan bantuan **Machine Learning**.
""")

# Jam sekarang
jakarta_tz = pytz.timezone("Asia/Jakarta")
st.markdown(f"🕒 Waktu sekarang: {datetime.now(jakarta_tz).strftime('%H:%M:%S')} WIB")

# ====== Konten Utama Halaman ====== #

st.subheader("📰 Berita Terbaru")
st.markdown("_🔄 Akan menampilkan feed berita saham dan ekonomi terbaru dari sumber terpercaya._")

st.subheader("📈 Grafik IHSG (Realtime atau Snapshot)")
st.markdown("_🔄 Akan menampilkan grafik IHSG dari Yahoo Finance / API lainnya._")

st.subheader("🚀 Top 10 Gainer Hari Ini")
st.markdown("_🔄 Daftar saham dengan kenaikan tertinggi berdasarkan data terbaru._")

st.subheader("📉 Top 10 Loser Hari Ini")
st.markdown("_🔄 Daftar saham dengan penurunan tertinggi berdasarkan data terbaru._")

# Menu navigasi
with st.sidebar:
    st.header("📁 Menu")
    menu = st.radio("Pilih Halaman", ["Home", "Trading Page", "Teknikal", "Fundamental"])

if menu == "Trading Page":
    st.header("📈 Trading Page")
    st.info("Menampilkan Fear & Greed Index, Komoditas, Index Dunia, IHSG, EIDO, Signal Buy, Rekap Ticker Aktif/Tidak Aktif, dan cara menggunakan signal ini.")
    st.markdown("_🔄 Konten halaman ini akan diisi di file Trading_Page.py_")

elif menu == "Teknikal":
    st.header("📉 Analisa Teknikal Saham")
    st.info("Silakan masukkan kode saham (misalnya `BBRI.JK`) untuk melihat chart dan memilih indikator seperti RSI, MACD, Ichimoku, dll.")
    st.markdown("_🔄 Konten halaman ini akan diisi di file Teknikal.py_")

elif menu == "Fundamental":
    st.header("📊 Screener Fundamental Saham")
    st.info("Menampilkan filter fundamental seperti PER, PBV, ROE, Dividend Yield, dll.")
    st.markdown("_🔄 Konten halaman ini akan diisi di file Fundamental.py (dari screener.py kamu sekarang)_")
