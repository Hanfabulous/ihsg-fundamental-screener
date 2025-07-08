# ===================================== #
# Home.py - Halaman Utama
# ===================================== #

import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf
import pandas as pd
import numpy as np
import feedparser
import plotly.graph_objects as go
import requests
import time
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
from urllib.parse import urlparse, parse_qs
import plotly.graph_objects as go

try:
    from bs4 import BeautifulSoup
except ImportError:
    st.error("❌ Modul `beautifulsoup4` belum terinstal. Tambahkan ke `requirements.txt` dan rerun.")
    st.stop()


# ========================== #
# 🔧 Konfigurasi Awal
# ========================== #
st.set_page_config(page_title="Investrade Trading Tools", layout="wide")
# ============================ #
# 🎨 CSS untuk memperbesar font
# ============================ #
st.markdown("""
    <style>
        body, div, table, th, td, p, span, input, label {
            font-size: 18px !important;  /* default: 12px; jadi 1.5x */
        }
        h1, h2, h3, h4 {
            font-size: 1.5em !important;
        }
        .stDataFrame th, .stDataFrame td {
            font-size: 16px !important;
        }
    </style>
""", unsafe_allow_html=True)


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

def tampilkan_teknikal():
    import ta  # Pastikan ta (technical analysis) sudah diinstal: pip install ta

    st.subheader("📉 Analisa Teknikal Saham")
    st.markdown("Tools ini menampilkan indikator teknikal dan prediksi harga menggunakan LSTM.")

    # === Input ===
    ticker_input = st.text_input("Masukkan Ticker (contoh: BBRI)", value="BBRI").upper()
    ticker = ticker_input + ".JK"

    timeframe = st.selectbox("Pilih Timeframe", ["15m", "30m", "1h", "4h", "1d", "1wk", "1mo"], index=4)

    indikator_dipilih = st.multiselect(
        "Pilih Indikator",
        ["Volume", "MACD", "RSI", "Alligator", "MA", "Bollinger Bands", "Ichimoku Cloud", "OBV", "Stochastic", "LSTM Predict"],
        default=["Volume", "MA"]
    )

    ma_period = st.number_input("Panjang Moving Average", min_value=1, value=20)

    st.success(f"Menampilkan analisa teknikal untuk {ticker} dengan timeframe {timeframe}")

    # === Unduh Data ===
    interval_map = {
        "15m": "15m", "30m": "30m", "1h": "60m", "4h": "240m",
        "1d": "1d", "1wk": "1wk", "1mo": "1mo"
    }

    period_map = {
        "15m": "7d", "30m": "7d", "1h": "30d", "4h": "60d",
        "1d": "6mo", "1wk": "2y", "1mo": "5y"
    }

    data = yf.download(ticker, period=period_map[timeframe], interval=interval_map[timeframe])
    if data.empty:
        st.error("❌ Gagal mengambil data harga.")
        return

    # === Hitung Indikator ===
    df = data.copy()
    df.dropna(inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close Price', line=dict(color='white')))

    if "Volume" in indikator_dipilih:
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', yaxis='y2'))

    if "MA" in indikator_dipilih:
        df['MA'] = df['Close'].rolling(ma_period).mean()
        fig.add_trace(go.Scatter(x=df.index, y=df['MA'], name=f"MA {ma_period}", line=dict(dash='dot')))

    if "RSI" in indikator_dipilih:
        rsi = ta.momentum.RSIIndicator(df['Close']).rsi()
        fig.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI", yaxis='y3'))

    if "MACD" in indikator_dipilih:
        macd = ta.trend.MACD(df['Close'])
        fig.add_trace(go.Scatter(x=df.index, y=macd.macd(), name='MACD', yaxis='y3'))

    if "Bollinger Bands" in indikator_dipilih:
        bb = ta.volatility.BollingerBands(df['Close'])
        fig.add_trace(go.Scatter(x=df.index, y=bb.bollinger_hband(), name='Upper BB', line=dict(color='lightblue')))
        fig.add_trace(go.Scatter(x=df.index, y=bb.bollinger_lband(), name='Lower BB', line=dict(color='lightblue')))

    if "OBV" in indikator_dipilih:
        obv = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
        fig.add_trace(go.Scatter(x=df.index, y=obv, name="OBV", yaxis='y4'))

    if "Stochastic" in indikator_dipilih:
        sto = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        fig.add_trace(go.Scatter(x=df.index, y=sto.stoch(), name='Stochastic %K', yaxis='y3'))

    # === Tambahkan Prediksi ML Dummy ===
    if "LSTM Predict" in indikator_dipilih:
        import random
        last_date = df.index[-1]
        pred_dir = random.choice(["Naik 🚀", "Sideways 😐", "Turun 📉"])
        st.info(f"📈 Prediksi LSTM (next trend): **{pred_dir}** per {last_date.date()} (dummy)")

    # === Layout Plot ===
    fig.update_layout(
        title=f"Grafik {ticker} dengan indikator terpilih",
        xaxis=dict(domain=[0, 1]),
        yaxis=dict(title="Harga", side='left'),
        yaxis2=dict(title="Volume", overlaying='y', side='right', showgrid=False),
        height=600,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================ #
# 📌 KONFIGURASI DAN PETA TICKER
# ============================ #
sektor_map = {
    "Teknologi": ["GOTO", "BUKA", "EMTK", "WIFI", "WIRG", "MTDL", "DMMX", "DCII", "MLPT", "ELIT", "PTSN", "EDGE", "JATI",
                  "LUCK", "KREN", "MCAS", "KIOS", "MSTI", "CYBR", "DIVA", "IOTF", "NFCX", "AWAN", "ZYRX", "TRON", "AXIO",
                  "TFAS", "BELI", "UVCR", "AREA", "HDIT", "TECH", "TOSK", "MPIX", "ATIC", "ENVY", "GLVA", "LMAS", "IRSX", "SKYB"],
    "Energi": ["ADRO", "PGAS", "PTBA", "ITMG", "HRUM", "BUMI", "PTRO", "MEDC", "ADMR", "ELSA", "AKRA", "INDY", "AADI",
               "CUAN", "RAJA", "BSSR", "ENRG", "RATU", "TOBA", "DOID", "DEWA", "GEMS", "ABMM", "BYAN", "TPMA", "MBAP",
               "KKGI", "BULL", "SOCI", "FIRE", "SGER", "DSSA", "BIPI", "WINS", "HUMI", "PSSI", "MBSS", "SMMT", "IATA",
               "CGAS", "BOSS", "UNIQ", "TEBE", "MAHA", "COAL", "LEAD", "JSKY", "BOAT", "TCPI", "BSML", "ITMA", "ATLA",
               "SICO", "MCOL", "APEX", "MYOH", "RMKE", "PKPK", "RUIS", "RIGS", "BESS", "SEMA", "HILL", "SHIP", "DWGL",
               "GTBO", "ARII", "TRAM", "WOWS", "PTIS", "ALII", "RGAS", "CNKO", "GTSI", "AIMS", "TAMU", "KOPI", "BBRM",
               "HITS", "INPS", "MKAP", "SUNI", "MTFN", "SURE", "CBRE", "RMKO", "CANI", "ARTI", "SMRU", "SUGI"],
    "Basic Industrial" : ["ANTM", "SMGR", "INTP", "BRPT", "INCO", "MDKA", "TINS", "INKP", "BRMS", "TPIA", "TKIM", "AMMN", "ESSA", "MBMA", "PSAB",
                "KRAS", "WSBP", "WTON", "SMBR", "NCKL", "NICL", "DKFT", "AGII", "AVIA", "DAAZ", "ISSP", "ARCI", "NIKL", "ZINC", "EKAD",
                "FPNI", "PBID", "BAJA", "AYLS", "SMGA", "SOLA", "PACK", "OKAS", "GDST", "CLPI", "NICE", "SPMA", "BLES", "LTLS", "SAMF",
                "ADMG", "CITA", "KAYU", "BEBS", "SMCB", "PICO", "OPMS", "MDKI", "BATR", "DGWG", "SULI", "HKMU", "BMSR", "SRSN", "SQMI",
                "SMLE", "PDPP", "ESIP", "FWCT", "PURE", "CHEM", "SBMA", "UNIC", "TBMS", "SWAT", "INCI", "ALDO", "PPRI", "SMKL", "OBMD",
                "IGAR", "BTON", "GGRP", "IFII", "KDSI", "IPOL", "PTMR", "IFSH", "INAI", "MOLI", "INCF", "ALKA", "INTD", "INRU", "DPNS",
                "EPAC", "AKPI", "CMNT", "NPGF", "CTBN", "KMTR", "APLI", "TDPM", "TIRT", "YPAS", "TRST", "LMSH", "ALMI", "FASW", "TALF",
                "KKES", "BRNA", "ETWA", "SIMA", "KBRI", "JKSW"],
    "Kesehatan" : ["KLBF", "SIDO", "KAEF", "MIKA", "SILO", "INAF", "TSPC", "IRRA", "[YFA", "HEAL", "PRDA", "SAME", "MERK", "PEHA", "OBAT",
                "DGNS", "DVLA", "SOHO", "CARE", "PRIM", "SRAJ", "MMIX", "BMHS", "OMED", "SURI", "LABS", "MEDS", "PEVE", "HALO", "RSCH",
                "MTMH", "SCPI", "IKPM", "RSGK", "PRAY"],
    "Transportasi" : ["GIAA", "SMDR", "BIRD", "ASSA", "TMAS", "IMJS", "CMPP", "HAIS", "NELY", "JAYA", "WEHA", "KJEN", "PURA", "TNCA", "TRUK",
                "MITI", "HATM", "SAPX", "MPXL", "AKSI", "SDMU", "LAJU", "ELPI", "TRJA", "GTRA", "HELI", "DEAL", "TAXI", "BPTR", "KLAS",
                "LRNA", "SAFE", "MIRA", "BLTA"],
    "Infrastruktur" : ["TLKM", "ADHI", "WIKA", "JSMR", "WSKT", "PTPP", "EXCL", "BREN", "PGEO", "ISAT", "TOWR", "TOTL", "DATA", "IPCC", "MTEL",
                "WEGE", "SSIA", "INET", "KEEN", "LINK", "ACST", "JKON", "CMNP", "HGII", "CENT", "IPCM", "JAST", "NRCA", "PPRE", "GMFI",
                "META", "MPOW", "PBSA", "KARW", "TGRA", "ARKO", "DGIK", "CASS", "KRYA", "BDKR", "OASA", "KOKA", "KBLV", "BALI", "BUKK",
                "PTDU", "GHON", "GOLD", "TOPS", "MORA", "MTPS", "PORT", "IDPR", "KETR", "RONY", "TAMA", "SUPR", "HADE", "ASLI", "PTPW",
                "IBST", "LCKM", "BTEL", "MTRA", "POWR", "TBIG", "FREN"],
    "Keuangan" : ["BBCA", "BBRI", "BMRI", "BBNI", "BRIS", "BBTN", "ARTO", "BNGA", "BJTM", "BTPS", "SRTG", "AGRO", "BBKP", "BJBR", "NISP",
                "PNLF", "BDMN", "BFIN", "BBHI", "BABP", "BNLI", "BANK", "PNBS", "INPC", "BNII", "ADMF", "CFIN", "PNBN", "BTPN",
                "BGTG", "MEGA", "BACA", "BCAP", "TUGU", "BNBA", "BEKS", "PALM", "MAYA", "BVIC", "BSIM", "PNIN", "PANS", "AMAR", "MCOR",
                "NOBU", "DNET", "DNAR", "AGRS", "BKSW", "TRIM", "JMAS", "WOMF", "AHAP", "BINA", "SMMA", "BCIC", "MTWI", "MFIN", "VICO",
                "BMAS", "SDRA", "LPGI", "AMAG", "PEGE", "BBSI", "LIFE", "PADI", "VTNY", "LPPS", "VINS", "CASA", "POLA", "AMOR", "APIC",
                "ASDM", "FUJI", "GSMF", "VRNA", "TRUS", "BHAT", "HDFA", "MREI", "STAR", "ASMI", "ASJT", "YOII", "BPFI", "ASBI", "ASRM",
                "BBLD", "TIFA", "TIFA", "BBMD", "NICK", "RELI", "BPII", "MASB", "YULE", "POOL", "SFAN", "ABDA", "BSWD", "DEFI", "OCAP",
                "PLAS"],
    "Industri" : ["ASII", "UNTR", "HEXA", "BHIT", "TOTO", "ARNA", "SMIL", "LABA", "MARK", "ASGR", "KBLI", "NAIK", "KOBX", "SPTO", "MLIA",
                "CAKK", "PTMP", "CCSI", "GPSO", "INDX", "BNBR", "DYAN", "JTPE", "SKRN", "SCCO", "KBLM", "IMPC", "VISI", "MHKI", "LION",
                "MUTU", "VOKS", "ZBRA", "AMFG", "SINI", "BLUE", "IKAI", "HOPE", "JECC", "BINO", "IKBI", "PIPA", "ICON", "NTBK", "ARKA",
                "AMIN", "SOSS", "MFMI", "KIAS", "KONI", "TIRA", "KUAS", "PADA", "HYGN", "APII", "CRSN", "CTTH", "MDRN", "FOLK", "KOIN",
                "INTA", "KPAL", "IBFN", "TRIL", "KRAH"],
    "Properti" : ["CTRA", "BSDE", "PWON", "SMRA", "PANI", "KIJA", "DMAS", "CBDK", "ASRI", "APLN", "LPKR", "DILD", "BKSL", "PPRO", "BEST",
                "LPCK", "JRPT", "BSBK", "GPRA", "MDLN", "SMDM", "BCIP", "KSIX", "TRIN", "MMLP", "PAMG", "REAL", "KBAG", "CITY", "INDO",
                "BAPA", "ADCP", "LAND", "NZIA", "DUTI", "AMAN", "CSIS", "MTLA", "RBMS", "ASPI", "SATU", "PURI", "DADA", "RODA", "BBSS",
                "HOMI", "WINR", "FMII", "ELTY", "PLIN", "POLL", "TRUE", "VAST", "MKPI", "EMDE", "PUDP", "SAGE", "RDTX", "LPLI", "ATAP",
                "URBN", "UANG", "BKDP", "RISE", "MPRO", "MTSM", "BAPI", "GMTD", "TARA", "DART", "NASA", "GRIA", "CBPE", "KOCI", "INPP",
                "BIPP", "MYRX", "POSA", "OMRE", "RIMO", "POLI", "BIKA", "GAMA", "CPRI", "ROCK", "NIRO", "LCGP", "FORZ", "ARMY", "COWL"],
    "Siklikal" : ["MNCN", "LPPF", "SCMA", "ACES", "ERAA", "GJTL", "MAPI", "MAPI", "AUTO", "MPMX", "BMTR", "RALS", "FILM", "HRTA", "SMSM",
                "IMAS", "MAPA", "KPIG", "WOOD", "SRIL", "MSIN", "IPTV", "KAQI", "FAST", "DOOH", "MINA", "CNMA", "JIHD", "SLIS", "NETV",
                "DRMA", "MARI", "ABBA", "PZZA", "MSKY", "DOSS", "INDR", "VKTR", "YELO", "MDIY", "ASLC", "EAST", "PBRX", "FORU", "PJAA",
                "TMPO", "VERN", "GOLF", "RAAM", "PANR", "BUVA", "TOYS", "FUTR", "BOLA", "BELL", "ACRO", "VIVA", "ERAL", "ECII", "BAYU",
                "INDS", "LPIN", "TRIS", "CARS", "MAPB", "GDYR", "PART", "KICI", "KOTA", "ERTX", "PSKT", "TELE", "DUCK", "BIMA", "LMPI",
                "SONA", "BABY", "RAFI", "UFOE", "NATO", "UNTD", "BAIK", "HRME", "GWSA", "CINT", "LIVE", "BOGA", "JSPT", "SHID", "BIKE",
                "ENAK", "FITT", "BAUT", "BRAM", "MASA", "ESTA", "INOV", "RICY", "MICE", "MDIA", "MAMI", "CSAP", "POLY", "ZATA", "PMJS",
                "SBAT", "BOLT", "SNLK", "DIGI", "DEPO", "BATA", "PTSP", "SOTS", "TOOL", "DFAM", "PGLI", "ZONE", "MKNT", "TYRE", "IIKP",
                "SCNP", "GEMA", "CBMF", "SSTM", "ESTI", "SWID", "PNSE", "HOME", "JGLE", "ARGO", "BLTZ", "TFCO", "PDES", "GLOB", "KDTN",
                "ARTA", "NUSA", "GRPH", "MYTX", "AKKU", "MGNA", "CSMI", "CLAY", "PRAS", "MABA", "CNTX", "TRIO", "UNIT", "HOTL", "HDTX",
                "NIPS"],
    "Non-Siklikal" : ["UNVR", "INDF", "ICBP", "GGRM", "AALI", "MYOR", "JPFA", "CPIN", "LSIP", "HMSP", "AMRT", "ULTJ", "CLEO", "MLPL", "TAPG",
                "WIIM", "HOKI", "GOOD", "SIMP", "MPPA", "GZCO", "DSNG", "CAMP", "SSMS", "MAIN", "SMAR", "MIDI", "ROTI", "TBLA", "AISA",
                "CMRY", "SGRO", "ANJT", "BWPT", "CPRO", "JARR", "PMMP", "KINO", "CEKA", "ADES", "WMUU", "BISI", "KEJU", "NASI", "CSRA",
                "BEEF", "PTPS", "MRAT", "UCID", "BUDI", "JAWA", "WAPO", "NEST", "ITIC", "MLBI", "GULA", "IKAN", "COCO", "RANC", "DMND",
                "BRRC", "STAA", "FOOD", "STTP", "DLTA", "ISEA", "DSFI", "EPMT", "TGUK", "STRK", "DEWI", "GUNA", "ASHA", "IPPE", "NSSS",
                "SKLT", "BTEK", "AYAM", "OILS", "SDPC", "HERO", "ANDI", "PCAR", "SKBM", "MGRO", "PSGO", "UNSP", "PSDN", "MBTO", "TGKA",
                "PNGO", "KMDS", "MSJA", "TCID", "TAYS", "MKTR", "TLDN", "WINE", "KPAS", "PGUN", "VICI", "ENZO", "BOBA", "DAYA", "BUAH",
                "FISH", "SIPD", "WMPP", "CRAB", "TRGU", "AGAR", "DPUM", "FAPA", "CBUT", "BEER", "ALTO", "MAXI", "MAGP", "LAPD", "GOLL",
                "WICO"]
}
tickers = []
ticker_to_sector = {}
for sektor, daftar in sektor_map.items():
    for t in daftar:
        ticker_jk = t + ".JK"
        tickers.append(ticker_jk)
        ticker_to_sector[ticker_jk] = sektor

# ============================ #
# 📊 FUNGSIONALITAS FUNDAMENTAL
# ============================ #
def tampilkan_fundamental():
    st.subheader("📊 ZONA FUNDAMENTAL")

    @st.cache_data(ttl=3600)
    def ambil_data(ticker_list):
        hasil = []
        for t in ticker_list:
            try:
                info = yf.Ticker(t).info
                hasil.append({
                    "Ticker": t,
                    "Name": info.get("longName", "-"),
                    "Price": info.get("currentPrice", np.nan),
                    "PER": info.get("trailingPE", np.nan),
                    "PBV": info.get("priceToBook", np.nan),
                    "ROE": info.get("returnOnEquity", np.nan),
                    "Div Yield": info.get("dividendYield", np.nan),
                    "Expected PER": info.get("forwardPE", np.nan),
                    "Sektor": ticker_to_sector.get(t, "-")
                })
            except Exception as e:
                print(f"[ERROR] Gagal ambil data untuk {t}: {e}")
                continue
        return pd.DataFrame(hasil)

    with st.spinner("🔄 Mengambil data dari Yahoo Finance..."):
        df = ambil_data(tickers)

    kolom_numerik = ['PER', 'PBV', 'ROE', 'Div Yield', 'Expected PER']
    semua_kolom = ['Ticker', 'Name', 'Price'] + kolom_numerik + ['Sektor']

    if df is None or df.empty:
        st.warning("⚠️ Data fundamental kosong.")
        df = pd.DataFrame(columns=semua_kolom)

    for kol in semua_kolom:
        if kol not in df.columns:
            df[kol] = np.nan

    for kol in kolom_numerik:
        df[kol] = pd.to_numeric(df[kol], errors='coerce')
    df['ROE'] = df['ROE'] * 100
    df['Div Yield'] = df['Div Yield'] * 100

    # Sidebar Filter
    st.sidebar.header("📌 Filter Screener")
    semua_sektor = sorted(sektor_map.keys())
    sektor_terpilih = st.sidebar.multiselect("Pilih Sektor", semua_sektor, default=semua_sektor)

    min_roe = st.sidebar.slider("Min ROE (%)", 0.0, 100.0, 10.0)
    max_per = st.sidebar.slider("Max PER", 0.0, 100.0, 25.0)
    max_pbv = st.sidebar.slider("Max PBV", 0.0, 10.0, 3.0)
    max_forward_per = st.sidebar.slider("Max Expected PER", 0.0, 100.0, 25.0)

    # Filter data
    df_filter = df.dropna(subset=['PER', 'PBV', 'ROE', 'Expected PER']).copy()
    df_filter = df_filter[
        (df_filter['Sektor'].isin(sektor_terpilih)) &
        (df_filter['ROE'] >= min_roe) &
        (df_filter['PER'] <= max_per) &
        (df_filter['PBV'] <= max_pbv) &
        (df_filter['Expected PER'] <= max_forward_per)
    ]

    # Buat kolom HTML Ticker clickable
    df_filter["Ticker_Link"] = df_filter["Ticker"].apply(
        lambda x: f"<a href='/?tkr={x}' target='_self' style='color:#40a9ff;text-decoration:none;'>{x}</a>"
    )

    # Tangani ticker detail dari URL
    # ============================ #
# 📁 Sidebar Navigasi
# ============================ #
query_params = st.query_params
ticker_qs = query_params.get("tkr", None)

if ticker_qs:
    st.session_state["ticker_diklik"] = ticker_qs
    st.session_state["menu"] = "Detail"
else:
    with st.sidebar:
        st.header("📁 Menu Navigasi")
        st.session_state["menu"] = st.radio(
            "Pilih Halaman", ["Home", "Trading Page", "Teknikal", "Fundamental"],
            key="sidebar_menu"
        )
# ============================ #
# 📊 Detail Ticker
# ============================ #
def tampilkan_detail(ticker):
    st.markdown(f"---\n### 🔍 Detail Ticker: `{ticker}`")

    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info

        st.markdown(f"**Nama:** {info.get('longName', '-')}\n")
        st.markdown(f"**Harga:** {info.get('currentPrice', '-')}\n")
        st.markdown(f"**PER:** {info.get('trailingPE', '-')}\n")
        st.markdown(f"**PBV:** {info.get('priceToBook', '-')}\n")
        roe = info.get('returnOnEquity')
        st.markdown(f"**ROE:** {round(roe*100, 2)} %" if roe else "ROE: -")
        dy = info.get('dividendYield')
        st.markdown(f"**Dividend Yield:** {round(dy*100, 2)} %" if dy else "Dividend Yield: -")
        st.markdown(f"**Expected PER:** {info.get('forwardPE', '-')}\n")
        st.markdown(f"**Sektor:** {ticker_to_sector.get(ticker, '-')}\n")

        st.markdown("### 📈 Historis PER dan PBV (8 Kuartal Terakhir)")
        earnings = tkr.quarterly_earnings
        balance = tkr.quarterly_balance_sheet
        hist = tkr.history(period="2y", interval="3mo")

        if earnings.empty or balance.empty or hist.empty:
            st.warning("❌ Data kuartalan tidak lengkap.")
            return

        df_hist = pd.DataFrame()
        df_hist["Price"] = hist["Close"].tail(8)
        df_hist["EPS"] = earnings["Earnings"].iloc[:8].values
        df_hist["PER"] = df_hist["Price"] / df_hist["EPS"]

        equity = balance.loc["TotalStockholderEquity"].iloc[:8]
        shares = info.get("sharesOutstanding")
        if shares:
            bvps = equity.values / shares
            df_hist["PBV"] = df_hist["Price"].values / bvps
        else:
            df_hist["PBV"] = np.nan

        df_hist.index = df_hist.index.strftime("%Y-Q%q")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist["PER"], name="PER", mode='lines+markers'))
        fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist["PBV"], name="PBV", mode='lines+markers'))
        fig.update_layout(title="PER dan PBV Historis (8 Kuartal)", xaxis_title="Kuartal", yaxis_title="Rasio")
        st.plotly_chart(fig, use_container_width=True)

        if st.button("🔙 Kembali ke Screener"):
            st.session_state["menu"] = "Fundamental"
            st.experimental_set_query_params()  # Hapus ?tkr dari URL
            st.rerun()


    except Exception as e:
        st.error(f"Gagal memuat detail: {e}")

# ============================ #
# 📊 Screener Fundamental
# ============================ #
def tampilkan_fundamental():
    st.subheader("📊 ZONA FUNDAMENTAL")

    @st.cache_data(ttl=3600)
    def ambil_data(ticker_list):
        hasil = []
        for t in ticker_list:
            try:
                info = yf.Ticker(t).info
                hasil.append({
                    "Ticker": t,
                    "Name": info.get("longName", "-"),
                    "Price": info.get("currentPrice", np.nan),
                    "PER": info.get("trailingPE", np.nan),
                    "PBV": info.get("priceToBook", np.nan),
                    "ROE": info.get("returnOnEquity", np.nan),
                    "Div Yield": info.get("dividendYield", np.nan),
                    "Expected PER": info.get("forwardPE", np.nan),
                    "Sektor": ticker_to_sector.get(t, "-")
                })
            except:
                continue
        return pd.DataFrame(hasil)

    df = ambil_data(tickers)
    kolom_numerik = ['PER', 'PBV', 'ROE', 'Div Yield', 'Expected PER']
    for kol in kolom_numerik:
        df[kol] = pd.to_numeric(df[kol], errors='coerce')
    df['ROE'] *= 100
    df['Div Yield'] *= 100

    st.sidebar.header("📌 Filter Screener")
    sektor_terpilih = st.sidebar.multiselect("Pilih Sektor", sorted(sektor_map.keys()), default=sorted(sektor_map.keys()))
    min_roe = st.sidebar.slider("Min ROE (%)", 0.0, 100.0, 10.0)
    max_per = st.sidebar.slider("Max PER", 0.0, 100.0, 25.0)
    max_pbv = st.sidebar.slider("Max PBV", 0.0, 10.0, 3.0)
    max_forward_per = st.sidebar.slider("Max Expected PER", 0.0, 100.0, 25.0)

    df_filter = df.dropna(subset=kolom_numerik)
    df_filter = df_filter[
        (df_filter['Sektor'].isin(sektor_terpilih)) &
        (df_filter['ROE'] >= min_roe) &
        (df_filter['PER'] <= max_per) &
        (df_filter['PBV'] <= max_pbv) &
        (df_filter['Expected PER'] <= max_forward_per)
    ]

    st.markdown("## 📂 Hasil Screening per Sektor")

    if df_filter.empty:
        st.info("Tidak ada saham yang lolos filter.")
        return

    for sektor in sorted(df_filter['Sektor'].unique()):
        df_sektor = df_filter[df_filter['Sektor'] == sektor]
        st.markdown(f"### 🔸 {sektor}")

        df_tampil = df_sektor[["Ticker", "Name", "Price", "PER", "PBV", "ROE", "Div Yield", "Expected PER"]].copy()
        gb = GridOptionsBuilder.from_dataframe(df_tampil)
        gb.configure_default_column(sortable=True, filter=True, resizable=True)
        gb.configure_column(
            "Ticker",
            header_name="Ticker",
            cellRenderer=JsCode("""
                class ClickableTicker {
                    init(params) {
                        this.eGui = document.createElement('a');
                        this.eGui.href = '/?tkr=' + params.value;
                        this.eGui.target = '_self';
                        this.eGui.innerText = params.value;
                        this.eGui.style.color = '#40a9ff';
                        this.eGui.style.textDecoration = 'none';
                    }
                    getGui() {
                        return this.eGui;
                    }
                }
            """),
            editable=False
        )

        AgGrid(
            df_tampil,
            gridOptions=gb.build(),
            allow_unsafe_jscode=True,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=True,
            height=300,
            enable_enterprise_modules=False
        )

# ========================== #
# 🌐 Routing Halaman Awal   #
# ========================== #

query_params = st.query_params
ticker_qs = query_params.get("tkr", None)

if ticker_qs:
    st.session_state["menu"] = "Detail"
    st.session_state["ticker_diklik"] = ticker_qs
else:
    if "menu" not in st.session_state:
        st.session_state["menu"] = "Home"
    query_params = st.query_params
    ticker_qs = query_params.get("tkr", None)

with st.sidebar:
    st.header("📁 Menu Navigasi")
    if st.session_state.get("menu") != "Detail":
        st.session_state["menu"] = st.radio(
            "Pilih Halaman", ["Home", "Trading Page", "Teknikal", "Fundamental"],
            key="main_menu"  # Key harus berbeda dari yang di atas
        )
menu = st.session_state["menu"]
if menu == "Home":
    st.title("🏠 Halaman Utama")
    tampilkan_chart_ihsg()
    get_news()
    tampilkan_sektoral_idx()

elif menu == "Trading Page":
    st.header("📈 Trading Page")
    # dll...

elif st.session_state.menu == "Teknikal":
    st.header("📉 Analisa Teknikal Saham")
    ticker_input = st.text_input("Masukkan Ticker (contoh: BBRI)")
    if ticker_input:
        ticker_full = ticker_input.strip().upper() + ".JK"

        tf = st.selectbox("Pilih Timeframe", ["15m", "30m", "1h", "4h", "1d", "1wk", "1mo"], index=4)

        indikator = st.multiselect("Pilih Indikator", [
            "MACD", "RSI", "Alligator", "MA", "Bollinger Bands", "Ichimoku Cloud",
            "Volume", "OBV", "Stochastic", "LSTM Predict"
        ])

        if "MA" in indikator:
            ma_length = st.number_input("Panjang Moving Average:", min_value=1, value=20)

        st.write(f"📊 Menampilkan analisa teknikal untuk {ticker_full} dengan timeframe {tf}")
        # Analisa teknikal placeholder
        st.info("📈 Grafik teknikal dan sinyal akan muncul di sini.")
elif menu == "Fundamental":
    st.header("📊 Screener Fundamental Saham")
    tampilkan_fundamental()

elif menu == "Detail":
    ticker = st.session_state.get("ticker_diklik", None)
    if ticker:
        tampilkan_detail(ticker)
    else:
        st.warning("Ticker tidak ditemukan.")
