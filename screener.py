# ===================================== #
# Home.py - Halaman Utama
# ===================================== #

import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf
import pandas as pd
import feedparser
import plotly.graph_objects as go
import requests
import time
try:
    from bs4 import BeautifulSoup
except ImportError:
    st.error("❌ Modul `beautifulsoup4` belum terinstal. Tambahkan ke `requirements.txt` dan rerun.")
    st.stop()


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
# 🗞️ Fungsi: Ambil Berita
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
                        img_url = None
                        if "media_content" in entry:
                            img_url = entry.media_content[0].get("url")
                        elif "enclosures" in entry:
                            img_url = entry.enclosures[0].get("href")

                        isi = entry.get("summary", "")
                        paragraf_pertama = isi.split("</p>")[0] if "</p>" in isi else isi.split(".")[0] + "."

                        with kolom.container():
                            col_img, col_teks = kolom.columns([1, 2])
                            if img_url:
                                col_img.image(img_url, width=300)
                            with col_teks:
                                col_teks.markdown(f"🔹 **[{entry.title}]({entry.link})**", unsafe_allow_html=True)
                                col_teks.markdown(f"<p style='font-size:14px'>{paragraf_pertama}</p>", unsafe_allow_html=True)

                        kolom.markdown("---")
                        hitung += 1
                    if hitung >= 5:
                        break
                if hitung == 0:
                    kolom.info("Tidak ada berita relevan.")
            except Exception as e:
                kolom.warning(f"Gagal ambil berita dari {nama}: {e}")

# ========================== #
# 📈 Fungsi: Grafik IHSG & Data
# ========================== #
def tampilkan_chart_ihsg():
    st.subheader("📈 Grafik IHSG (Candlestick + MA20 + MA50)")
    try:
        data = yf.download(tickers="^JKSE", period="2y", interval="1d", group_by='ticker')

        if isinstance(data.columns, pd.MultiIndex):
            data = data['^JKSE']

        if data.empty:
            st.error("❌ Data IHSG kosong atau gagal diunduh.")
            return

        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["MA50"] = data["Close"].rolling(window=50).mean()
        data["VolumeAvg20"] = data["Volume"].rolling(window=20).mean()
        data = data.reset_index()
        data_chart = data.dropna(subset=["MA20", "MA50"])

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data_chart["Date"],
            open=data_chart["Open"],
            high=data_chart["High"],
            low=data_chart["Low"],
            close=data_chart["Close"],
            name="Candlestick",
            increasing_line_color="green",
            decreasing_line_color="red"
        ))
        fig.add_trace(go.Scatter(x=data_chart["Date"], y=data_chart["MA20"], name="MA20", line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=data_chart["Date"], y=data_chart["MA50"], name="MA50", line=dict(color='blue')))

        fig.update_layout(
            title="📊 Grafik IHSG (Candlestick + MA)",
            xaxis_title="Tanggal",
            yaxis_title="Harga",
            template="plotly_dark",
            height=600,
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # 📋 Data IHSG Terakhir
        last_valid_row = data[data["Volume"].notna()].iloc[-1]
        last_data = {
            "Tanggal": last_valid_row["Date"].date(),
            "Open": last_valid_row["Open"],
            "High": last_valid_row["High"],
            "Low": last_valid_row["Low"],
            "Close": last_valid_row["Close"],
            "Volume Hari Ini": last_valid_row["Volume"],
            "Rata-Rata Volume (20 Hari)": last_valid_row["VolumeAvg20"]
        }
        st.markdown("### 📋 Data IHSG Terakhir:")
        st.dataframe(pd.DataFrame([last_data]))

        # 📆 Data 7 Hari Terakhir
        st.markdown("### 📆 Data IHSG 7 Hari Terakhir:")
        st.dataframe(data[["Date", "Open", "High", "Low", "Close", "Volume"]].dropna().tail(7).reset_index(drop=True))

    except Exception as e:
        st.error(f"❌ Gagal menampilkan grafik IHSG: {e}")

# ========================== #
# 📊 Fungsi: Data Sektoral IDX
# ========================== #
def tampilkan_sektoral_idx():
    st.subheader("🏭 Data Sektoral IDX")
    url = "https://www.idx.co.id/id/market-data/sectoral-index/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        tabel = soup.select_one("table.table")  
        df = pd.read_html(str(tabel))[0]
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Gagal mengambil data sektoral IDX: {e}")

def tampilkan_fundamental():
    st.subheader("📊 ZONA FUNDAMENTAL")
    import numpy as np
    from urllib.parse import urlparse, parse_qs
    from st_aggrid import AgGrid, GridOptionsBuilder

    # === Daftar sektor dan ticker (.JK) ===
    sektor_map = {...}  # <-- gunakan sektor_map besar dari skrip Anda

    tickers = []
    ticker_to_sector = {}
    for sektor, daftar in sektor_map.items():
        for t in daftar:
            ticker_jk = t + ".JK"
            tickers.append(ticker_jk)
            ticker_to_sector[ticker_jk] = sektor

    @st.cache_data(ttl=3600)
    def ambil_data(tickers):
        data = []
        for t in tickers:
            try:
                info = yf.Ticker(t).info
                data.append({
                    'Ticker': t,
                    'Name': info.get('longName', '-'),
                    'Price': info.get('currentPrice'),
                    'PER': info.get('trailingPE'),
                    'PBV': info.get('priceToBook'),
                    'ROE': info.get('returnOnEquity'),
                    'Div Yield': info.get('dividendYield'),
                    'Sektor': ticker_to_sector.get(t, '-'),
                    'Expected PER': info.get('forwardPE'),
                })
            except:
                continue
        return pd.DataFrame(data)

    with st.spinner("🔄 Mengambil data Yahoo Finance..."):
        df = ambil_data(tickers)

    kolom_numerik = ['PER', 'PBV', 'ROE', 'Div Yield', 'Expected PER']
    for kol in kolom_numerik:
        df[kol] = pd.to_numeric(df[kol], errors='coerce')

    # Sidebar filter
    st.sidebar.header("📌 Filter")
    semua_sektor = sorted(df['Sektor'].dropna().unique())
    sektor_pilihan = st.sidebar.multiselect("Pilih Sektor", semua_sektor, default=semua_sektor)
    min_roe = st.sidebar.slider("Min ROE (%)", 0.0, 100.0, 10.0)
    max_per = st.sidebar.slider("Max PER", 0.0, 100.0, 25.0)
    max_pbv = st.sidebar.slider("Max PBV", 0.0, 10.0, 3.0)
    max_forward_per = st.sidebar.slider("Max Expected PER", 0.0, 100.0, 25.0)

    kolom_wajib = ['PER', 'PBV', 'ROE']
    if not all(k in df.columns for k in kolom_wajib):
        st.error("❌ Kolom PER, PBV, atau ROE tidak tersedia.")
        st.dataframe(df)
        return

    df_clean = df.dropna(subset=['PER', 'PBV', 'ROE', 'Expected PER']).copy()
    df_clean['ROE'] *= 100
    df_clean['Div Yield'] *= 100

    hasil = df_clean[
        (df_clean['Sektor'].isin(sektor_pilihan)) &
        (df_clean['ROE'] >= min_roe) &
        (df_clean['PER'] <= max_per) &
        (df_clean['PBV'] <= max_pbv) &
        (df_clean['Expected PER'] <= max_forward_per)
    ]

    st.subheader("📈 Hasil Screening")
    st.markdown("Klik ticker untuk melihat detail 👇", unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(
        hasil[['Ticker', 'Name', 'Price', 'PER', 'PBV', 'ROE', 'Div Yield', 'Sektor', 'Expected PER']]
    )
    gb.configure_default_column(sortable=True, filter=True)
    gb.configure_side_bar()

    AgGrid(
        hasil,
        gridOptions=gb.build(),
        theme='light',
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=True,
        height=350
    )

    # Detail ticker
    query_params = st.query_params
    ticker_qs = query_params.get("tkr", None)
    if ticker_qs:
        st.session_state["ticker_diklik"] = ticker_qs

    def tampilkan_detail_ticker(ticker):
        st.markdown(f"---\n## 📌 Detail Ticker: `{ticker}`")
        try:
            info = yf.Ticker(ticker).info
            st.markdown(f"**Nama Saham:** {info.get('longName', '-')}")
            st.markdown(f"**Harga Saat Ini:** {info.get('currentPrice', '-')}") 
            st.markdown(f"**PER:** {info.get('trailingPE', '-')}") 
            st.markdown(f"**PBV:** {info.get('priceToBook', '-')}") 
            st.markdown(f"**ROE:** {round(info.get('returnOnEquity', 0)*100, 2) if info.get('returnOnEquity') else '-'} %") 
            st.markdown(f"**Dividend Yield:** {round(info.get('dividendYield', 0)*100, 2) if info.get('dividendYield') else '-'} %") 
            st.markdown(f"**Expected PER:** {info.get('forwardPE', '-')}") 
            st.markdown(f"**Sektor:** {ticker_to_sector.get(ticker, '-')}") 
        except Exception as e:
            st.error(f"❌ Gagal mengambil data detail: {e}")

    if st.session_state.get("ticker_diklik"):
        tampilkan_detail_ticker(st.session_state["ticker_diklik"])

    st.markdown("## 📂 Hasil per Sektor")
    for sektor in sorted(hasil['Sektor'].unique()):
        st.markdown(f"### 🔸 {sektor}")
        df_sektor = hasil[hasil['Sektor'] == sektor].copy()
        st.dataframe(
            df_sektor[['Ticker', 'Name', 'Price', 'PER', 'PBV', 'ROE', 'Div Yield', 'Expected PER']],
            use_container_width=True,
            height=300
        )
        
# ========================== #
# 📁 Sidebar Navigasi
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
    tampilkan_sektoral_idx()

elif menu == "Trading Page":
    st.header("📈 Trading Page")
    st.info("Menampilkan indeks global, komoditas, sinyal beli, EIDO, strategi.")
    st.markdown("_🛠️ Akan diisi dari file `Trading_Page.py`_")

elif menu == "Teknikal":
    st.header("📉 Analisa Teknikal Saham")
    st.info("Masukkan kode saham (contoh: `BBRI.JK`) untuk melihat indikator.")
    st.markdown("_🛠️ Akan diisi dari file `Teknikal.py`_")

elif menu == "Fundamental":
    st.header("📊 Screener Fundamental Saham")
    st.info("Filter saham berdasarkan PER, PBV, ROE, dividen, dan lainnya.")
    st.markdown("_🛠️ Akan diisi dari file `Fundamental.py`_")
    tampilkan_fundamental()
