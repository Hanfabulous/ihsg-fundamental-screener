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
# 📈 Fungsi Grafik IHSG
# ========================== #
def tampilkan_chart_ihsg():
    st.subheader("📈 Grafik IHSG (Candlestick + MA20 + MA50)")

    try:
        data = yf.download("^JKSE", period="2y", interval="1d")

        if data.empty:
            st.error("❌ Data IHSG kosong atau gagal diunduh.")
            return

        # Bersihkan kolom MultiIndex jika ada
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [f"{col[0]}_{col[1]}" for col in data.columns]

        rename_map = {col: col.replace("_^JKSE", "") for col in data.columns if "_^JKSE" in col}
        data = data.rename(columns=rename_map)

        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in data.columns for col in required_cols):
            st.error("❌ Data candlestick tidak lengkap.")
            st.write("Kolom yang tersedia:", data.columns.tolist())
            return

        # Tambahkan MA
        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["MA50"] = data["Close"].rolling(window=50).mean()
        data["VolumeAvg20"] = data["Volume"].rolling(window=20).mean()
        data = data.reset_index()

        # Siapkan data untuk chart (harus dropna MA)
        data_chart = data.dropna(subset=["MA20", "MA50"])

        # ============================= #
        # ✅ Data IHSG Hari Terakhir
        # ============================= #
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
        st.write("📋 Data IHSG Terakhir:")
        st.dataframe(pd.DataFrame([last_data]))

        # ============================= #
        # ✅ 7 Hari Terakhir
        # ============================= #
        st.markdown("### 📆 Data IHSG 7 Hari Terakhir:")
        st.dataframe(data[["Date", "Open", "High", "Low", "Close", "Volume"]].dropna().tail(7).reset_index(drop=True))

        # ============================= #
        # 📈 Plot Candlestick + MA
        # ============================= #
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

    except Exception as e:
        st.error(f"❌ Gagal menampilkan grafik IHSG: {e}")

# ========================== #
# 🚀 Fungsi Gainers & Losers
# ========================== #
def tampilkan_top_gainers_losers():
    st.subheader("🚀 Top Gainers & 📉 Losers Per Sektor (Hari Ini)")

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
        "Kesehatan" : ["KLBF", "SIDO", "KAEF", "MIKA", "SILO", "INAF", "TSPC", "IRRA", "YFA", "HEAL", "PRDA", "SAME", "MERK", "PEHA", "OBAT",
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

    semua_ticker = []
    sektor_ticker_map = {}

    # Buat mapping ticker -> sektor dan tambahkan .JK
    for sektor, daftar in sektor_map.items():
        tickers_jk = [f"{t}.JK" if not t.endswith(".JK") else t for t in daftar]
        sektor_ticker_map[sektor] = tickers_jk
        semua_ticker.extend(tickers_jk)

    try:
        harga = yf.download(semua_ticker, period="2d", interval="1d")["Close"]
        returns = harga.pct_change().iloc[-1].dropna()

        for sektor, ticker_list in sektor_ticker_map.items():
            st.markdown(f"### 🏭 {sektor}")
            df = returns[returns.index.isin(ticker_list)]

            if df.empty:
                st.info("Tidak ada data return untuk sektor ini.")
                continue

            df = df.sort_values(ascending=False)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🚀 Top Gainers:**")
                for ticker, ret in df.head(3).items():
                    st.markdown(f"- `{ticker}`: {ret*100:.2f}%")

            with col2:
                st.markdown("**📉 Top Losers:**")
                for ticker, ret in df.tail(3).items():
                    st.markdown(f"- `{ticker}`: {ret*100:.2f}%")

            st.markdown("---")

    except Exception as e:
        st.warning(f"Gagal mengambil data gainers/losers sektoral: {e}")


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
