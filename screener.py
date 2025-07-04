# ===================================== #
# Home.py - Halaman Utama
# ===================================== #

import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf
import feedparser
import plotly.graph_objects as go

# ========================== #
# 🔧 Konfigurasi Awal
# ========================== #
st.set_page_config(page_title="Investrade Trading Tools", layout="wide")

# ========================== #
# 🏷️ Header & Waktu
# ========================== #
col_kiri, col_kanan = st.columns([3, 1])
with col_kiri:
    st.markdown("""
        <h1 style='font-size: 36px;'>📊 Investrade Trading Tools</h1>
        <p style='font-size: 22px;'>Selamat datang di tools trading saham IHSG.<br><br>
        Tools ini dibuat untuk para trader maupun investor saham Indonesia, di mana analisa prediksi di tools ini menggunakan bantuan <strong>Machine Learning</strong>.</p>
    """, unsafe_allow_html=True)

with col_kanan:
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    jam_sekarang = datetime.now(jakarta_tz).strftime('%H:%M:%S')
    st.markdown(f"<p style='text-align:right; font-weight:bold; font-size:24px;'>🕒 Waktu sekarang: {jam_sekarang} WIB</p>", unsafe_allow_html=True)

# ========================== #
# 🗞️ Fungsi Ambil Berita
# ========================== #
def get_news():
    sumber_rss = {
        "CNBC Indonesia": "https://www.cnbcindonesia.com/rss",
        "Yahoo Finance": "https://finance.yahoo.com/rss/topstories"
    }
    filter_kata = ["saham", "market", "ihsg", "bursa", "emiten", "investor", "trading"]

    col1, col2 = st.columns(2)
    for (nama, url), kolom in zip(sumber_rss.items(), [col1, col2]):
        with kolom:
            kolom.markdown(f"### 🗞️ {nama}")
            try:
                feed = feedparser.parse(url)
                hitung = 0
                for entry in feed.entries[:10]:
                    judul = entry.title.lower()
                    if any(k in judul for k in filter_kata):
                        # Ambil gambar
                        img_url = None
                        if "media_content" in entry:
                            img_url = entry.media_content[0].get("url")
                        elif "enclosures" in entry:
                            img_url = entry.enclosures[0].get("href")

                        # Ambil ringkasan jika tersedia
                        ringkasan = entry.get("summary", "").strip()
                        if ringkasan == "":
                            ringkasan = "Tidak tersedia ringkasan berita."

                        # Tampilkan layout gambar + ringkasan
                        with kolom.container():
                            col_img, col_txt = kolom.columns([1, 2])
                            if img_url:
                                col_img.image(img_url, width=150)
                            col_txt.markdown(f"🔹 **[{entry.title}]({entry.link})**", unsafe_allow_html=True)
                            col_txt.markdown(f"<div style='font-size:14px'>{ringkasan}</div>", unsafe_allow_html=True)

                        kolom.markdown("---")
                        hitung += 1
                    if hitung >= 5:
                        break
                if hitung == 0:
                    kolom.info("Tidak ada berita relevan.")
            except Exception as e:
                kolom.warning(f"Gagal ambil berita dari {nama}: {e}")

# ========================== #
# 📈 Fungsi Grafik IHSG
# ========================== #
def tampilkan_chart_ihsg():
    st.subheader("📈 Grafik IHSG")

    data = yf.download("^JKSE", period="1y", interval="1d")

    if data.empty:
        st.error("❌ Data IHSG kosong atau gagal diunduh.")
        return

    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    data = data.dropna()

    st.write("📋 Data IHSG Terakhir:")
    st.dataframe(data[["Close", "MA20", "MA50"]].tail())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20", line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50", line=dict(color="green")))
    fig.update_layout(title="📊 Grafik IHSG (Close, MA20, MA50)",
                      xaxis_title="Tanggal", yaxis_title="Harga",
                      template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

# ========================== #
# 🚀 Fungsi Gainers & Losers
# ========================== #
def tampilkan_top_gainers_losers():
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
        st.warning("Gagal mengambil data top gainer & loser.")

# ========================== #
# 🧭 Sidebar Navigasi
# ========================== #
with st.sidebar:
    st.header("📁 Menu Navigasi")
    menu = st.radio("Pilih Halaman", ["Home", "Trading Page", "Teknikal", "Fundamental"])

# ========================== #
# 🌐 Routing Halaman
# ========================== #
if menu == "Home":
    get_news()
    tampilkan_chart_ihsg()
    tampilkan_top_gainers_losers()

elif menu == "Trading Page":
    st.header("📈 Trading Page")
    st.info("Konten ini menampilkan data indeks global, komoditas, sinyal beli, EIDO, dan strategi.")
    st.markdown("_🛠️ Akan diisi dari file `Trading_Page.py`_")

elif menu == "Teknikal":
    st.header("📉 Analisa Teknikal Saham")
    st.info("Masukkan kode saham (contoh: `BBRI.JK`) untuk melihat chart dan indikator.")
    st.markdown("_🛠️ Akan diisi dari file `Teknikal.py`_")

elif menu == "Fundamental":
    st.header("📊 Screener Fundamental Saham")
    st.info("Filter berdasarkan PER, PBV, ROE, Dividend Yield, dan lainnya.")
    st.markdown("_🛠️ Akan diisi dari file `Fundamental.py`_")
    st.header("📊 Screener Fundamental Saham")
    st.info("Menampilkan filter fundamental seperti PER, PBV, ROE, Dividend Yield, dll.")
    st.markdown("_🔄 Konten halaman ini akan diisi di file Fundamental.py_")
