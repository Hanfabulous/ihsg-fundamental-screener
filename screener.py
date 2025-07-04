# ===================================== #
# Home.py - Halaman Utama
# ===================================== #

import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf
import feedparser
import plotly.graph_objects as go
import urllib.parse

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
# 📰 Fungsi Tampilkan Berita Saham
# ========================== #
def tampilkan_berita(col_target):
    st.markdown("## 🗞️ Berita Pasar Terkini")

    def ambil_dari_rss(nama, url):
        try:
            feed = feedparser.parse(url)
            hasil = []

            for entry in feed.entries[:10]:
                judul = entry.title.lower()
                if any(k in judul for k in ["saham", "market", "ihsg", "bursa", "emiten", "investor", "trading"]):
                    img_url = None
                    if "media_content" in entry:
                        img_url = entry.media_content[0].get("url")
                    elif "enclosures" in entry:
                        img_url = entry.enclosures[0].get("href")
                    isi = entry.get("summary", "")
                    paragraf_pertama = isi.split("</p>")[0] if "</p>" in isi else isi.split(".")[0] + "."
                    hasil.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": paragraf_pertama,
                        "img": img_url
                    })
                    if len(hasil) >= 3:
                        break
            return hasil
        except:
            return []

    def ambil_dari_google_news(topik="saham indonesia"):
        hasil = []
        try:
            q = urllib.parse.quote(topik)
            rss_url = f"https://news.google.com/rss/search?q={q}&hl=id&gl=ID&ceid=ID:id"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:5]:
                summary = entry.summary.split(".")[0] + "."
                hasil.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": summary,
                    "img": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Google_News_icon.png"
                })
            return hasil
        except:
            return []

    semua_berita = []
    semua_berita += ambil_dari_rss("CNBC", "https://www.cnbcindonesia.com/rss")
    semua_berita += ambil_dari_rss("Yahoo", "https://finance.yahoo.com/rss/topstories")
    if not semua_berita:
        semua_berita = ambil_dari_google_news()

    if semua_berita:
        for berita in semua_berita:
            with col_target.container():
                col_img, col_teks = col_target.columns([1, 3])
                if berita["img"]:
                    col_img.image(berita["img"], width=100)
                with col_teks:
                    col_teks.markdown(f"🔹 **[{berita['title']}]({berita['link']})**", unsafe_allow_html=True)
                    col_teks.markdown(f"<p style='font-size:14px'>{berita['summary']}</p>", unsafe_allow_html=True)
            col_target.markdown("---")
    else:
        col_target.info("Tidak ada berita yang bisa ditampilkan.")

# ========================== #
# 📈 Fungsi Grafik IHSG
# ========================== #
def tampilkan_chart_ihsg():
    st.subheader("📈 Grafik IHSG")
    data = yf.download("^JKSE", period="1y", interval="1d")
    if data.empty or "Close" not in data.columns:
        st.error("❌ Data IHSG kosong atau gagal diunduh.")
        return
    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()
    data_clean = data.dropna(subset=["Close", "MA20", "MA50"]).reset_index()

    st.write("📋 Data IHSG Terakhir:")
    st.dataframe(data_clean[["Date", "Close", "MA20", "MA50"]].tail())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_clean["Date"], y=data_clean["Close"], name="Close", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=data_clean["Date"], y=data_clean["MA20"], name="MA20", line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=data_clean["Date"], y=data_clean["MA50"], name="MA50", line=dict(color="green")))
    fig.update_layout(
        title="📊 Grafik IHSG (Close, MA20, MA50)",
        xaxis_title="Tanggal",
        yaxis_title="Harga",
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=True
    )
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
    col_kiri, col_kanan = st.columns([2, 3])

    with col_kiri:
        tampilkan_chart_ihsg()
        tampilkan_top_gainers_losers()

    with col_kanan:
        tampilkan_berita(col_kanan)

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
