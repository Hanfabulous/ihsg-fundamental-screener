# screener.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ============================ #
# 📌 KONFIGURASI HALAMAN
# ============================ #
st.set_page_config(page_title="Zona Fundamental", layout="wide")
st.title("📊 ZONA FUNDAMENTAL")

# ============================ #
# 🧠 INISIALISASI SESSION STATE
# ============================ #
if "ticker_diklik" not in st.session_state:
    st.session_state["ticker_diklik"] = None
    
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

if st.session_state["ticker_diklik"]:
    tampilkan_detail_ticker(st.session_state["ticker_diklik"])

# ============================ #
# 📂 TAMPILKAN PER SEKTOR
# ============================ #
st.markdown("## 📂 Hasil per Sektor")
for sektor in sorted(hasil['Sektor'].unique()):
    st.markdown(f"### 🔸 {sektor}")
    df_sektor = hasil[hasil['Sektor'] == sektor]
    st.dataframe(df_sektor.reset_index(drop=True), use_container_width=True)
