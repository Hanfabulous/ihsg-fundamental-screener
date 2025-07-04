# Struktur multi-page Streamlit untuk Investrade Trading Tools

# ===================================== #
# File: Home.py (Halaman Utama)
# ===================================== #
import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import feedparser

st.set_page_config(page_title="Investrade Trading Tools", layout="wide")
st.title("📊 Investrade Trading Tools")

st.markdown("""
Selamat datang di tools trading saham IHSG.

Tools ini dibuat untuk para trader maupun investor saham Indonesia, di mana analisa prediksi di tools ini menggunakan bantuan **Machine Learning**.
""")

# Jam sekarang
jakarta_tz = pytz.timezone("Asia/Jakarta")
st.markdown(f"🕒 Waktu sekarang: {datetime.now(jakarta_tz).strftime('%H:%M:%S')} WIB")

# ====== Fungsi Ambil Berita dari RSS ====== #
def tampilkan_berita_kolom():
    sumber_rss = {
        "CNBC Indonesia": "https://www.cnbcindonesia.com/rss",
        "Yahoo Finance": "https://finance.yahoo.com/rss/topstories"
    }

    filter_kata_kunci = ["saham", "market", "ihsg", "bursa", "emiten", "investor", "trading"]

    col1, col2 = st.columns(2)
    for sumber, kolom in zip(sumber_rss.items(), [col1, col2]):
        nama, url = sumber
        with kolom:
            kolom.markdown(f"### 🗞️ {nama}")
            try:
                feed = feedparser.parse(url)
                hitung = 0
                for entry in feed.entries[:15]:
                    judul = entry.title.lower()
                    if any(kata in judul for kata in filter_kata_kunci):
                        # Ambil gambar jika ada
                        img_url = None
                        if "media_content" in entry and entry.media_content:
                            img_url = entry.media_content[0].get("url")
                        elif "enclosures" in entry and entry.enclosures:
                            img_url = entry.enclosures[0].get("href")

                        if img_url:
                            kolom.image(img_url, width=100)
                        kolom.markdown(f"🔹 [{entry.title}]({entry.link})", unsafe_allow_html=True)
                        kolom.markdown("---")
                        hitung += 1
                    if hitung >= 5:
                        break
                if hitung == 0:
                    kolom.info("Tidak ada berita pasar terkini.")
            except Exception as e:
                kolom.warning(f"Gagal memuat berita dari {nama}: {e}")

# ====== Tampilkan Berita ====== #
get_news()

# ====== Chart IHSG ====== #
st.subheader("📈 Grafik IHSG")
try:
    data = yf.download("^JKSE", period="6mo", interval="1d")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='IHSG'))
    fig.update_layout(title="Chart IHSG", xaxis_title="Tanggal", yaxis_title="Harga")
    st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Gagal mengambil data IHSG.")

# ====== Top 10 Gainer & Loser ====== #
st.subheader("🚀 Top 10 Gainer Hari Ini & 📉 Top 10 Loser Hari Ini")

tickers = ["BBRI.JK", "BBCA.JK", "PGAS.JK", "TLKM.JK", "ANTM.JK", "UNVR.JK", "ASII.JK", "BMRI.JK", "MDKA.JK", "ADRO.JK"]
try:
    harga = yf.download(tickers, period="2d", interval="1d")["Close"]
    returns = harga.pct_change().iloc[-1].dropna().sort_values(ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚀 Gainers")
        for idx, val in returns.head(10).items():
            st.markdown(f"**{idx}**: {val*100:.2f}%")
    with col2:
        st.markdown("### 📉 Losers")
        for idx, val in returns.tail(10).items():
            st.markdown(f"**{idx}**: {val*100:.2f}%")
except:
    st.warning("Gagal menghitung Top Gainer dan Loser.")

# ====== Navigasi Menu ====== #
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
