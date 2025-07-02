# screener.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Screener Fundamental IHSG", layout="wide")
st.title("📊 Screener Fundamental IHSG")

# === Daftar sektor dan ticker (.JK sudah ditambahkan) ===
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

# Konversi ke .JK dan buat mapping ticker ke sektor
tickers = []
ticker_to_sector = {}  # mapping ticker -> sektor
for sektor, daftar in sektor_map.items():
    for t in daftar:
        ticker_jk = t + ".JK"
        tickers.append(ticker_jk)
        ticker_to_sector[ticker_jk] = sektor

# === Ambil data fundamental dari Yahoo Finance ===
@st.cache_data(ttl=3600)
def ambil_data(tickers):
    data = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            data.append({
                'Ticker': t,
                'Name': info.get('longName', '-'),
                'Price': info.get('currentPrice', None),
                'PER': info.get('trailingPE', None),
                'PBV': info.get('priceToBook', None),
                'ROE': info.get('returnOnEquity', None),
                'Div Yield': info.get('dividendYield', None),
                'Sektor': ticker_to_sector.get(t, '-')
                'Expected PER': info.get('forwardPE', None),
            })
        except:
            continue
    return pd.DataFrame(data)

with st.spinner("🔄 Mengambil data Yahoo Finance..."):
    df = ambil_data(tickers)

# Tampilkan kolom yang tersedia untuk debug
st.write("🛠️ Kolom tersedia:", df.columns.tolist())

# 👇 Debug: Cek beberapa baris data
st.write("Contoh data:", df.head())

# Pastikan kolom numerik
for col in ['PER', 'PBV', 'ROE', 'Div Yield']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

if 'Expected PER' in df.columns:
    df['Expected PER'] = pd.to_numeric(df['Expected PER'], errors='coerce')

# Sidebar filter
st.sidebar.header("📌 Filter")
semua_sektor = sorted(df['Sektor'].dropna().unique())
sektor_pilihan = st.sidebar.multiselect("Pilih Sektor", semua_sektor, default=semua_sektor)
min_roe = st.sidebar.slider("Min ROE (%)", 0.0, 100.0, 10.0)
max_per = st.sidebar.slider("Max PER", 0.0, 100.0, 25.0)
max_pbv = st.sidebar.slider("Max PBV", 0.0, 10.0, 3.0)

# Pastikan semua kolom filter tersedia
kolom_wajib = ['PER', 'PBV', 'ROE']
kolom_tersedia = [kol for kol in kolom_wajib if kol in df.columns]

if len(kolom_tersedia) < 3:
    st.error("❌ Kolom PER, PBV, atau ROE tidak tersedia di sebagian besar data.")
    st.dataframe(df)
    st.stop()

# Filter
df_clean = df.dropna(subset=['PER', 'PBV', 'ROE', 'Expected PER'])
df_clean['ROE'] = df_clean['ROE'] * 100
df_clean['Div Yield'] = df_clean['Div Yield'] * 100

hasil = df_clean[
    (df_clean['Sektor'].isin(sektor_pilihan)) &
    (df_clean['ROE'] >= min_roe) &
    (df_clean['PER'] <= max_per) &
    (df_clean['PBV'] <= max_pbv) &
    (df_clean['Expected PER']
]

# Tampilkan hasil
st.subheader("📈 Hasil Screening")
st.dataframe(hasil.sort_values(by='ROE', ascending=False).reset_index(drop=True))

# Per sektor
st.markdown("## 📂 Hasil per Sektor")
for sektor in sorted(hasil['Sektor'].unique()):
    st.markdown(f"### 🔸 {sektor}")
    df_sektor = hasil[hasil['Sektor'] == sektor]
    st.dataframe(df_sektor.reset_index(drop=True))
