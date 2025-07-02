# screener.py
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="📊 Screener Fundamental IHSG", layout="wide")
st.title("📊 Screener Fundamental IHSG")

# === Daftar ticker saham IHSG ===
tickers = [
    
        "AALI", "ABBA", "ABDA", "ABMM", "ACST", "ADES", "ADHI", "ADMF", "ADMG", "ADRO", "AGII", "AGRO",
          "AHAP", "AIMS", "AISA", "AKRA", "AKSI", "ALKA", "AMFG", "AMIN", "AGRS", "ANJT", "ANTM", "APEX", "APIC", "APII", "APLI", "APLN", "ARGO", "ARII", "ARNA", "ARTA", "ARTO",
          "ASBI", "ASDM", "ASGR", "ASJT", "ASMI", "ASRI", "ASRM", "ASSA", "ATIC", "AUTO", "BABP", "BACA", "BAJA",
          "BALI", "BAPA", "BATA", "BAYU", "BBCA", "BBHI", "BBKP", "BBLD", "BBMD", "BBNI", "BBRI", "BBRM", "BBTN", "BBYB",
          "BCAP", "BCIC", "BCIP", "BDMN", "BEKS", "BEST", "BFIN", "BGTG", "BHIT", "BIMA", "BINA", "BIPI", "BIPP",
          "BIRD", "BISI", "BJBR", "BJTM", "BKDP", "BKSL", "BKSW", "BLTA", "BLTZ", "BMAS", "BMRI", "BMSR", "BMTR", "BNBA",
          "BNBR", "BNGA", "BNII", "BNLI", "BOLT", "BRAM", "BRMS", "BRNA", "BRPT", "BSDE", "BSIM", "BSSR",
          "BSWD", "BTON", "BTPN", "BUDI", "BUKK", "BULL", "BUMI", "BUVA", "BVIC", "BWPT", "BYAN", "CANI",
          "CASS", "CEKA", "CENT", "CFIN", "CINT", "CITA", "CLPI", "CMNP", "CMPP", "CNKO", "COWL", "CPIN", "CPRO",
          "CSAP", "CTBN", "CTRA", "CTTH", "DART", "DEWA", "DGIK", "DILD", "DKFT", "DLTA", "DMAS", "DNAR", "DNET",
          "DOID", "DPNS", "DSFI", "DSNG", "DSSA", "DUTI", "DVLA", "DYAN", "ECII", "EKAD", "ELSA", "ELTY", "EMDE", "EMTK",
          "ENRG", "EPMT", "ERAA", "ERTX", "ESSA", "ESTI", "ETWA", "EXCL", "FAST", "FASW", "FISH", "FMII", "FORU", "FPNI",
          "FREN", "GAMA", "GDST", "GDYR", "GEMA", "GEMS", "GGRM", "GIAA", "GJTL", "GLOB", "GMTD", "GOLD", "GPRA",
          "GSMF", "GTBO", "GWSA", "GZCO", "HADE", "HDFA", "HDTX", "HERO", "HEXA", "HITS", "HMSP", "HOTL", "HRUM",
          "IATA", "IBFN", "IBST", "ICBP", "ICON", "IGAR", "IKAI", "IKBI", "IMAS", "IMJS", "IMPC", "INAF", "INAI",
          "INCI", "INCO", "INDF", "INDR", "INDS", "INDX", "INDY", "INKP", "INPC", "INPP", "INRU", "INTA", "INTD", "INTP",
          "JIHD", "JKON", "JKSW", "JPFA", "JRPT", "JSMR", "JSPT", "JTPE", "KAEF", "KARW", "KBLI", "KBLM", "KBLV",
                  "KDSI", "KIAS", "KICI", "KIJA", "KKGI", "KLBF", "KOBX", "KOIN", "KONI", "KOPI", "KPIG", "KRAH", "KRAS", "KREN",
          "LAPD", "LCGP", "LEAD", "LINK", "LION", "LMAS", "LMPI", "LMSH", "LPCK", "LPGI", "LPIN", "LPKR", "LPLI", "LPPF",
          "LPPS", "LRNA", "LSIP", "LTLS", "MAGP", "MAIN", "MAMI", "MAPI", "MASA", "MAYA", "MBAP", "MBSS", "MBTO", "MCOR",
          "MDIA", "MDKA", "MDLN", "MDRN", "MEDC", "MEGA", "MERK", "META", "MFIN", "MFMI", "MGNA", "MICE", "MIDI", "MIKA",
          "MIRA", "MITI", "MKPI", "MLBI", "MLIA", "MLPL", "MLPT", "MMLP", "MNCN", "MPMX", "MPPA", "MRAT", "MREI", "MSKY",
          "MTDL", "MTFN", "MTLA", "MTSM", "MYOH", "MYOR", "MYTX", "NELY", "NIKL", "NIPS", "NIRO", "NISP", "NOBU",
          "NRCA", "OCAP", "OKAS", "OMRE", "PADI", "PALM", "PANR", "PANS", "PBRX", "PDES", "PEGE", "PGAS", "PGLI", "PICO",
          "PJAA", "PKPK", "PLAS", "PLIN", "PNBN", "PNBS", "PNIN", "PNLF", "PNSE", "POLY", "PPRO", "PRAS", "PSAB",
          "PSDN", "PSKT", "PTBA", "PTIS", "PTPP", "PTRO", "PTSN", "PTSP", "PUDP", "PWON", "PYFA", "RODA", "ROTI",
          "RUIS", "SAFE", "SAME", "SCCO", "SCMA", "SCPI", "SDMU", "SDPC", "SDRA", "SGRO", "SHID", "SIDO", "SILO", 
          "SIMP", "SIPD", "SKBM", "SKLT", "SKYB", "SMAR", "SMBR", "SMCB", "SMDM", "SMDR", "SMGR", "SMMA", "SMMT", "SMRA",
          "SMRU", "SMSM", "SOCI", "SONA", "SPMA", "SQMI", "SRAJ", "SRSN", "SRTG", "SSIA", "SSMS", "SSTM", "STAR",
          "STTP", "SUGI", "SULI", "SUPR", "TALF", "TARA", "TAXI", "TBIG", "TBLA", "TBMS", "TCID", "TELE", "TFCO", "TGKA",
          "TIFA", "TINS", "TIRA", "TIRT", "TKIM", "TLKM", "TMAS", "TMPO", "TOBA", "TOTL", "TOTO", "TOWR", "TPIA", "TPMA",
          "TSPC", "ULTJ", "UNIC", "UNIT", "UNSP", "UNTR", "UNVR", "VICO", "VINS", "VIVA", "VOKS", "VRNA", "WAPO", "WEHA",
          "WICO", "WIIM", "WIKA", "WINS", "WOMF", "WSKT", "WTON", "YPAS", "YULE", "ZBRA", "SHIP", "CASA", "DAYA", "DPUM",
          "IDPR", "JGLE", "KINO", "MARI", "MKNT", "MTRA", "PRDA", "BOGA", "BRIS", "PORT", "CARS", "MINA", "FORZ", "CLEO",
          "TAMU", "CSIS", "TGRA", "FIRE", "KMTR", "MAPB", "WOOD", "HRTA", "HOKI", "MPOW", "MARK",
          "NASA", "MDKI", "BELL", "KIOS", "GMFI", "MTWI", "ZINC", "MCAS", "PPRE", "WEGE", "PSSI", "MORA", "DWGL", "PBID",
          "JMAS", "CAMP", "IPCM", "LCKM", "BOSS", "HELI", "INPS", "GHON", "TDPM", "DFAM", "NICK", "BTPS",
          "SPTO", "PRIM", "HEAL", "TRUK", "PZZA", "TUGU", "MSIN", "SWAT", "KPAL", "TNCA", "MAPA", "TCPI", "IPCC", "RISE",
          "BPTR", "POLL", "NFCX", "MGRO", "FILM", "LAND", "MOLI", "PANI", "DIGI", "CITY", "SAPX", "KPAS",
          "SURE", "MPRO", "DUCK", "GOOD", "SKRN", "YELO", "CAKK", "SOSS", "DEAL", "POLA", "DIVA", "LUCK",
          "URBN", "SOTS", "ZONE", "PEHA", "FOOD", "BEEF", "POLI", "CLAY", "NATO", "JAYA", "COCO", "MTPS", "CPRI", "HRME",
          "POSA", "JAST", "FITT", "BOLA", "CCSI", "SFAN", "POLU", "KJEN", "KAYU", "ITIC", "PAMG", "IPTV", "BLUE", "ENVY",
          "EAST", "LIFE", "FUJI", "KOTA", "INOV", "ARKA", "SMKL", "KEEN", "BAPI", "TFAS", "GGRP", "OPMS", "NZIA",
          "SLIS", "PURE", "IRRA", "DMMX", "SINI", "WOWS", "ESIP", "TEBE", "KEJU", "PSGO", "AGAR", "IFSH", "REAL", "IFII",
          "PMJS", "UCID", "GLVA", "PGJO", "AMAR", "CSRA", "INDO", "AMOR", "TRIN", "DMND", "PURA", "PTPW", "TAMA", "IKAN",
          "AYLS", "DADA", "ASPI", "ESTA", "BESS", "AMAN", "CARE", "SAMF", "SBAT", "KBAG", "CBMF", "RONY", "CSMI", "BBSS",
          "BHAT", "CASH", "TECH", "EPAC", "UANG", "PGUN", "SOFA", "PPGL", "TOYS", "SGER", "TRJA", "PNGO", "SCNP", "BBSI",
          "KMDS", "PURI", "SOHO", "HOMI", "ROCK", "PLAN", "PTDU", "ATAP", "VICI", "PMMP", "WIFI", "FAPA", "DCII",
          "KETR", "DGNS", "UFOE", "BANK", "EDGE", "UNIQ", "BEBS", "SNLK", "ZYRX", "LFLO", "FIMP", "TAPG", "NPGF",
          "LUCY", "ADCP", "MGLV", "TRUE", "LABA", "BUKA", "HAIS", "OILS", "GPSO", "MCOL", "MTEL", "DEPO",
          "CMRY", "WGSH", "TAYS", "RMKE", "OBMD", "AVIA", "IPPE", "NASI", "BSML", "DRMA", "ADMR", "SEMA", "ASLC",
          "NETV", "BAUT", "ENAK", "NTBK", "BIKE", "WIRG", "SICO", "GOTO", "TLDN", "MTMH", "WINR", "IBOS", "OLIV", "ASHA",
          "SWID", "TRGU", "ARKO", "CHEM", "DEWI", "AXIO", "KRYA", "HATM", "RCCC", "GULA", "JARR", "AMMS", "RAFI", "KKES",
          "ELPI", "EURO", "KLIN", "TOOL", "BUAH", "CRAB", "MEDS", "COAL", "PRAY", "CBUT", "BELI", "MKTR", "OMED", "BSBK",
          "PDPP", "KDTN", "SOUL", "ELIT", "BEER", "CBPE", "SUNI", "CBRE", "WINE", "BMBL", "PEVE", "LAJU", "FWCT", "NAYZ",
          "IRSX", "PACK", "VAST", "CHIP", "HALO", "KING", "PGEO", "FUTR", "GTRA", "HAJJ", "PIPA", "NCKL", "MENN", "AWAN",
          "MBMA", "RAAM", "DOOH", "JATI", "TYRE", "MPXL", "SMIL", "KLAS", "MAXI", "VKTR", "RELF", "AMMN", "CRSN", "HBAT",
          "GRIA", "PPRI", "ERAL", "CYBR", "MUTU", "LMAX", "KOCI", "PTPS", "BREN", "STRK", "KOKA", "LOPI", "UDNG", "CGAS",
          "NICE", "MSJA", "SMLE", "ACRO", "MANG", "MEJA", "LIVE", "HYGN", "BAIK", "VISI", "AREA", "MHKI", "ATLA", "DATA",
          "SOLA", "BATR", "SPRE", "PART", "GOLF", "ISEA", "BLES", "GUNA", "LABS", "DOSS", "NEST", "PTMR", "VERN", "DAAZ",
          "BOAT", "OASA", "POWR", "INCF", "WSBP", "PBSA", "IPOL", "ISAT", "ISSP", "ITMA", "ITMG", "JAWA", "JECC", "NAIK",
          "AADI", "MDIY", "TRIL", "TRIM", "TRIO", "TRIS", "TRST", "TRUS", "RSGK", "RUNS", "SBMA", "CMNT", "GTSI",
          "IDEA", "KUAS", "BOBA", "GRPM", "WIDI", "TGUK", "INET", "MAHA", "RMKO", "CNMA", "FOLK", "HUMI", "MSIE", "RSCH",
          "BABY", "AEGS", "IOTF", "RGAS", "MSTI", "IKPM", "AYAM", "SURI", "ASLI", "GRPH", "SMGA", "UNTD", "TOSK", "MPIX",
          "ALII", "MKAP", "SMKM", "STAA", "NANO", "ARCI", "IPAC", "MASB", "BMHS", "FLMC", "NICL", "UVCR", "ZATA", "NINE",
          "MMIX", "PADA", "ISAP", "VTNY", "HILL", "BDKR", "PTMP", "SAGE", "TRON", "CUAN", "NSSS", "RAJA", "RALS", "RANC",
          "RBMS", "RDTX", "RELI", "RICY", "RIGS","YOII","KSIX","RATU","HGII","BRRC","OBAT","DGWG","CBDK","ACES", "ADMR", "ADRO", "AKRA", "AMMN", "AMRT", "ANTM", "ARTO", "ASII", "BBCA", "BBNI",
"BBRI", "BBTN", "BMRI", "BRIS", "BRPT", "CPIN", "CTRA", "ESSA", "EXCL", "GOTO", "ICBP",
"INCO", "INDF", "INKP", "ISAT", "ITMG", "JPFA", "JSMR", "KLBF", "MAPA", "MAPI", "MBMA",
"MDKA", "MEDC", "PGAS", "PGEO", "PTBA", "SIDO", "SMGR", "SMRA", "TLKM", "TOWR", "UNTR", "UNVR"

]
tickers = [ticker + ".JK" for ticker in tickers]

# === Ambil data fundamental ===
data = []
st.info("Mengambil data, mohon tunggu...")

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
        })

    except:
        pass

df = pd.DataFrame(data)

# Drop baris yang kolom PER, PBV, ROE-nya kosong
df_clean = df.dropna(subset=['PER', 'PBV', 'ROE'])

# Konversi rasio ROE dan Div Yield dari desimal ke persen (opsional)
df_clean['ROE'] = df_clean['ROE'] * 100
df_clean['Div Yield'] = df_clean['Div Yield'] * 100

# Filter user
st.sidebar.header("📌 Filter Kriteria")
min_roe = st.sidebar.slider("Min ROE (%)", 0.0, 100.0, 10.0)
max_per = st.sidebar.slider("Max PER", 0.0, 50.0, 20.0)
max_pbv = st.sidebar.slider("Max PBV", 0.0, 10.0, 3.0)

# Apply filter
result = df_clean[
    (df_clean['ROE'] >= min_roe) &
    (df_clean['PER'] <= max_per) &
    (df_clean['PBV'] <= max_pbv)
]

# Tampilkan hasil
st.subheader("📈 Hasil Screening")
st.dataframe(result.sort_values(by='ROE', ascending=False).reset_index(drop=True))
