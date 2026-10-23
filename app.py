import streamlit as st
import numpy as np
from pathlib import Path
from scipy import ndimage
from PIL import Image
from io import BytesIO
import re
import requests
import os
import math

from dotenv import load_dotenv

from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    BBox,
    CRS,
    MimeType
)
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TARANG",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

RESULTS_DIR = BASE_DIR / "tarang_results"
RESULTS_DIR.mkdir(exist_ok=True)

ENV_FILE = BASE_DIR / ".env"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)

CLIENT_ID = (
    os.getenv("COPERNICUS_CLIENT_ID")
    or os.getenv("SH_CLIENT_ID")
    or os.getenv("CLIENT_ID")
)

CLIENT_SECRET = (
    os.getenv("COPERNICUS_CLIENT_SECRET")
    or os.getenv("SH_CLIENT_SECRET")
    or os.getenv("CLIENT_SECRET")
)

COPERNICUS_BASE_URL = "https://sh.dataspace.copernicus.eu"

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)


# ============================================================
# SENTINEL CONFIGURATION
# ============================================================

def create_sentinel_config():
    if not CLIENT_ID or not CLIENT_SECRET:
        return None

    config = SHConfig()

    config.sh_client_id = CLIENT_ID
    config.sh_client_secret = CLIENT_SECRET
    config.sh_token_url = TOKEN_URL
    config.sh_base_url = COPERNICUS_BASE_URL

    return config


SENTINEL_CONFIG = create_sentinel_config()


if SENTINEL_CONFIG is not None:
    # Streamlit reruns can reuse the same Python process. Reuse the
    # custom DataCollection if it was already registered; otherwise register it.
    try:
        S2_COLLECTION = DataCollection.s2l2a_taraang
    except AttributeError:
        S2_COLLECTION = DataCollection.SENTINEL2_L2A.define_from(
            "s2l2a_taraang",
            service_url=COPERNICUS_BASE_URL
        )
else:
    S2_COLLECTION = None


# ============================================================
# UI PREFERENCES + MULTILINGUAL QUERY SUPPORT
# ============================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "language" not in st.session_state:
    st.session_state.language = "English"

LANGUAGE_OPTIONS = ["English", "Hindi", "Hinglish"]

UI_TEXT = {
    "English": {
        "change_analysis": "Change Analysis",
        "explore_data": "Explore Data",
        "methodology": "Methodology",
        "workspace": "WORKSPACE",
        "current_analysis": "CURRENT ANALYSIS",
        "location": "LOCATION",
        "period": "PERIOD",
        "dataset": "DATASET",
        "language": "Language",
        "dark_mode": "Dark Mode",
        "analysis_query": "Analysis query",
        "analyze": "Analyze Change  →",
        "query_interpretation": "Query interpretation",
        "satellite_retrieval": "SATELLITE RETRIEVAL",
        "retrieving": "Retrieving multi-temporal imagery",
        "change_intelligence": "CHANGE INTELLIGENCE",
        "detected_change": "Detected change",
        "temporal_comparison": "TEMPORAL COMPARISON",
        "see_change": "See the change",
        "before": "Before",
        "after": "After",
        "change_detection": "Change Detection",
        "evidence": "EVIDENCE VIEW",
        "location_section": "LOCATION",
        "resolved": "Resolved study area",
        "download_map": "Download Change Map",
        "download_report": "Download Analysis Report",
    },
    "Hindi": {
        "change_analysis": "परिवर्तन विश्लेषण",
        "explore_data": "डेटा देखें",
        "methodology": "कार्यप्रणाली",
        "workspace": "कार्य क्षेत्र",
        "current_analysis": "वर्तमान विश्लेषण",
        "location": "स्थान",
        "period": "अवधि",
        "dataset": "डेटासेट",
        "language": "भाषा",
        "dark_mode": "डार्क मोड",
        "analysis_query": "विश्लेषण प्रश्न",
        "analyze": "परिवर्तन का विश्लेषण  →",
        "query_interpretation": "प्रश्न की समझ",
        "satellite_retrieval": "सैटेलाइट डेटा",
        "retrieving": "बहु-समय सैटेलाइट इमेजरी प्राप्त की जा रही है",
        "change_intelligence": "परिवर्तन विश्लेषण",
        "detected_change": "पता चला परिवर्तन",
        "temporal_comparison": "समय तुलना",
        "see_change": "परिवर्तन देखें",
        "before": "पहले",
        "after": "बाद में",
        "change_detection": "परिवर्तन पहचान",
        "evidence": "प्रमाण दृश्य",
        "location_section": "स्थान",
        "resolved": "चयनित अध्ययन क्षेत्र",
        "download_map": "परिवर्तन मानचित्र डाउनलोड करें",
        "download_report": "विश्लेषण रिपोर्ट डाउनलोड करें",
    },
    "Hinglish": {
        "change_analysis": "Change Analysis",
        "explore_data": "Data Explore Karein",
        "methodology": "Methodology",
        "workspace": "WORKSPACE",
        "current_analysis": "CURRENT ANALYSIS",
        "location": "LOCATION",
        "period": "PERIOD",
        "dataset": "DATASET",
        "language": "Language",
        "dark_mode": "Dark Mode",
        "analysis_query": "Analysis query",
        "analyze": "Change Analyze Karein  →",
        "query_interpretation": "Query samajh",
        "satellite_retrieval": "SATELLITE RETRIEVAL",
        "retrieving": "Multi-temporal imagery retrieve ho rahi hai",
        "change_intelligence": "CHANGE INTELLIGENCE",
        "detected_change": "Detected change",
        "temporal_comparison": "TEMPORAL COMPARISON",
        "see_change": "Change dekhein",
        "before": "Before",
        "after": "After",
        "change_detection": "Change Detection",
        "evidence": "EVIDENCE VIEW",
        "location_section": "LOCATION",
        "resolved": "Resolved study area",
        "download_map": "Change Map Download",
        "download_report": "Analysis Report Download",
    },
}


EXTRA_UI = {
    "English": {
        "hero_title":"Understand how places change.","hero_text":"Ask a question in natural language and TARANG resolves the location, retrieves Sentinel-2 imagery and compares different years.","location_ready":"Dynamic Delhi location retrieval ready",
        "analysis_title":"What do you want to investigate?","analysis_help":"Describe a location, time period and change in natural language.","urban":"Urban Expansion","vegetation":"Vegetation Loss","water":"Water Change","infrastructure":"Infrastructure Change",
        "location":"Location","start":"Start","end":"End","analysis":"Analysis","engine":"Analysis engine ready","detected":"Detected change","potential":"Potential changed area","study_changed":"Study area changed","zones":"Change zones","largest":"Largest zone",
        "interpretation":"Change interpretation","temporal":"TEMPORAL COMPARISON","see":"See the change","before":"Before","after":"After","change_detection":"Change Detection","evidence":"EVIDENCE VIEW","evidence_title":"Where the spectral signal changed most",
        "evidence_help":"Brighter pixels represent stronger change within the detected zones. This view is an analytical aid, not a higher-resolution satellite product.","found":"What TARANG found","resolved":"Resolved study area","latitude":"Latitude","longitude":"Longitude","confidence":"Query confidence","footprint":"Analysis footprint","automated":"Automated interpretation",
        "explorer":"DATA EXPLORER","explore_title":"Explore satellite imagery.","explore_text":"View imagery retrieved by TARANG for your latest analysis.","run_first":"Run a change analysis first.","method_title":"How TARANG detects change.","method_text":"Natural language is converted into a geographic search area and a temporal satellite analysis.","pipeline":"ANALYSIS PIPELINE","pipeline_title":"From question to change map","limitation_title":"Important limitation",
        "limitation":"Satellite spectral analysis identifies potential change zones. It does not by itself confirm individual buildings, structural safety or illegal construction.","download_map":"Download Change Map","download_report":"Download Analysis Report"
    },
    "Hindi": {
        "hero_title":"जानें कि स्थान कैसे बदलते हैं।","hero_text":"प्राकृतिक भाषा में प्रश्न पूछें और TARANG स्थान को समझकर Sentinel-2 इमेजरी प्राप्त करता है और अलग-अलग वर्षों की तुलना करता है।","location_ready":"दिल्ली के स्थान की गतिशील खोज तैयार है",
        "analysis_title":"आप क्या जांचना चाहते हैं?","analysis_help":"स्थान, समय अवधि और परिवर्तन को सामान्य भाषा में लिखें।","urban":"शहरी विस्तार","vegetation":"वनस्पति हानि","water":"जल परिवर्तन","infrastructure":"बुनियादी ढांचा परिवर्तन",
        "location":"स्थान","start":"आरंभ","end":"अंत","analysis":"विश्लेषण","engine":"विश्लेषण इंजन तैयार है","detected":"पता चला परिवर्तन","potential":"संभावित परिवर्तित क्षेत्र","study_changed":"अध्ययन क्षेत्र में परिवर्तन","zones":"परिवर्तन क्षेत्र","largest":"सबसे बड़ा क्षेत्र",
        "interpretation":"परिवर्तन की व्याख्या","temporal":"समय तुलना","see":"परिवर्तन देखें","before":"पहले","after":"बाद में","change_detection":"परिवर्तन पहचान","evidence":"प्रमाण दृश्य","evidence_title":"जहां सैटेलाइट संकेत सबसे अधिक बदला",
        "evidence_help":"उज्ज्वल पिक्सेल अधिक मजबूत परिवर्तन दिखाते हैं। यह विश्लेषणात्मक दृश्य है, उच्च-रिज़ॉल्यूशन सैटेलाइट उत्पाद नहीं।","found":"TARANG ने क्या पाया","resolved":"निर्धारित अध्ययन क्षेत्र","latitude":"अक्षांश","longitude":"देशांतर","confidence":"प्रश्न विश्वसनीयता","footprint":"विश्लेषण क्षेत्र","automated":"स्वचालित व्याख्या",
        "explorer":"डेटा एक्सप्लोरर","explore_title":"सैटेलाइट इमेजरी देखें।","explore_text":"अपने नवीनतम विश्लेषण में प्राप्त TARANG इमेजरी देखें।","run_first":"पहले परिवर्तन विश्लेषण चलाएं।","method_title":"TARANG परिवर्तन कैसे पहचानता है।","method_text":"प्राकृतिक भाषा को भौगोलिक खोज क्षेत्र और समय-आधारित सैटेलाइट विश्लेषण में बदला जाता है।","pipeline":"विश्लेषण प्रक्रिया","pipeline_title":"प्रश्न से परिवर्तन मानचित्र तक","limitation_title":"महत्वपूर्ण सीमा",
        "limitation":"सैटेलाइट स्पेक्ट्रल विश्लेषण संभावित परिवर्तन क्षेत्रों की पहचान करता है। यह अकेले किसी भवन, संरचनात्मक सुरक्षा या अवैध निर्माण की पुष्टि नहीं करता।","download_map":"परिवर्तन मानचित्र डाउनलोड करें","download_report":"विश्लेषण रिपोर्ट डाउनलोड करें"
    },
    "Hinglish": {
        "hero_title":"Samjhein ki places kaise change hote hain.","hero_text":"Natural language mein question poochhein aur TARANG location samajhkar Sentinel-2 imagery retrieve karta hai aur different years compare karta hai.","location_ready":"Delhi location retrieval ready hai",
        "analysis_title":"Aap kya investigate karna chahte hain?","analysis_help":"Location, time period aur change ko natural language mein likhein.","urban":"Urban Expansion","vegetation":"Vegetation Loss","water":"Water Change","infrastructure":"Infrastructure Change",
        "location":"Location","start":"Start","end":"End","analysis":"Analysis","engine":"Analysis engine ready hai","detected":"Detected change","potential":"Potential changed area","study_changed":"Study area changed","zones":"Change zones","largest":"Largest zone",
        "interpretation":"Change interpretation","temporal":"TEMPORAL COMPARISON","see":"Change dekhein","before":"Before","after":"After","change_detection":"Change Detection","evidence":"EVIDENCE VIEW","evidence_title":"Jahan spectral signal sabse zyada badla",
        "evidence_help":"Brighter pixels stronger change dikhate hain. Yeh analytical view hai, higher-resolution satellite product nahi.","found":"TARANG ne kya find kiya","resolved":"Resolved study area","latitude":"Latitude","longitude":"Longitude","confidence":"Query confidence","footprint":"Analysis footprint","automated":"Automated interpretation",
        "explorer":"DATA EXPLORER","explore_title":"Satellite imagery explore karein.","explore_text":"Latest analysis mein retrieved TARANG imagery dekhein.","run_first":"Pehle change analysis run karein.","method_title":"TARANG change kaise detect karta hai.","method_text":"Natural language ko geographic search area aur temporal satellite analysis mein convert kiya jata hai.","pipeline":"ANALYSIS PIPELINE","pipeline_title":"Question se change map tak","limitation_title":"Important limitation",
        "limitation":"Satellite spectral analysis potential change zones identify karta hai. Yeh individual buildings, structural safety ya illegal construction ko confirm nahi karta.","download_map":"Change Map Download","download_report":"Analysis Report Download"
    }
}
EXTRA_FALLBACK_UI = {
    "satellite_intelligence": {"English":"SATELLITE INTELLIGENCE","Hindi":"सैटेलाइट इंटेलिजेंस","Hinglish":"SATELLITE INTELLIGENCE"},
    "analysis_query": {"English":"Analysis query","Hindi":"विश्लेषण प्रश्न","Hinglish":"Analysis query"},
    "analyze": {"English":"Analyze Change  →","Hindi":"परिवर्तन का विश्लेषण करें  →","Hinglish":"Analyze Change  →"},
    "satellite_retrieval": {"English":"SATELLITE RETRIEVAL","Hindi":"सैटेलाइट डेटा प्राप्ति","Hinglish":"SATELLITE RETRIEVAL"},
    "change_intelligence": {"English":"CHANGE INTELLIGENCE","Hindi":"परिवर्तन विश्लेषण","Hinglish":"CHANGE INTELLIGENCE"},
    "location_section": {"English":"LOCATION","Hindi":"स्थान","Hinglish":"LOCATION"},
}

def ui(key, **kwargs):
    # Prefer the expanded multilingual labels; fall back to the original labels.
    value = EXTRA_UI.get(st.session_state.language, {}).get(key)
    if value is None:
        value = UI_TEXT.get(st.session_state.language, {}).get(key, key)
    return value.format(**kwargs) if kwargs else value

# Backward-compatible alias for patched page components.
ui2 = ui


def normalize_multilingual_query(query):
    """Normalize common Hindi/Hinglish satellite-analysis phrases to the
    English intent vocabulary used by the existing parser. This keeps one
    analysis engine for all supported input languages.
    """
    text = re.sub(r"\\s+", " ", query.strip())

    # Common Delhi locality names in Devanagari + common variants.
    location_map = {
        "कश्मीरी गेट": "Kashmere Gate",
        "काश्मीरी गेट": "Kashmere Gate",
        "द्वारका": "Dwarka",
        "रोहिणी": "Rohini",
        "साकेत": "Saket",
        "नजफगढ़": "Najafgarh",
        "करोल बाग": "Karol Bagh",
        "सुल्तानपुरी": "Sultanpuri",
        "पीतमपुरा": "Pitampura",
        "जनकपुरी": "Janakpuri",
    }
    for src, dst in location_map.items():
        text = text.replace(src, dst)

    # Hindi words/phrases.
    hindi_map = {
        "शहरी विस्तार": "urban expansion",
        "शहरी विकास": "urban development",
        "निर्माण": "construction",
        "इमारत": "building",
        "इमारतें": "buildings",
        "हरियाली": "greenery",
        "वनस्पति": "vegetation",
        "पेड़": "tree cover",
        "हरित क्षेत्र": "green cover",
        "वनों की कटाई": "deforestation",
        "पानी": "water",
        "जल": "water",
        "जल निकाय": "water body",
        "झील": "lake",
        "नदी": "river",
        "तालाब": "pond",
        "सड़क": "road",
        "सड़कें": "roads",
        "राजमार्ग": "highway",
        "बुनियादी ढांचा": "infrastructure",
        "परिवर्तन": "change",
        "बदलाव": "change",
        "दिखाएं": "show",
        "दिखाओ": "show",
        "बताएं": "show",
        "खोजें": "find",
        "पहचानें": "detect",
        "विश्लेषण करें": "analyze",
        "तुलना करें": "compare",
        "के बीच": "between",
        "से": "from",
        "तक": "to",
        "में": "in",
        "के आसपास": "around",
        "पास": "near",
        "कितना": "how much",
        "कितनी": "how much",
        "हुआ": "changed",
        "हुई": "changed",
        "कम हुई": "loss",
        "घटी": "loss",
    }
    # Longest phrases first avoids partial replacements.
    for src in sorted(hindi_map, key=len, reverse=True):
        text = text.replace(src, hindi_map[src])

    # Common Hinglish phrasing.
    hinglish = {
        "mein": "in", "me": "in", "ke aas paas": "around", "ke paas": "near",
        "dikhao": "show", "dikhaye": "show", "batao": "show", "karo": "analyze",
        "badlav": "change", "badlaav": "change", "hariyali": "greenery",
        "paudhe": "vegetation", "paani": "water", "jheel": "lake", "nadi": "river",
        "talab": "pond", "sadak": "road", "sadakein": "roads", "nirman": "construction",
        "vikas": "development", "shehri vistar": "urban expansion", "kitna badha": "increased",
        "kam hua": "loss", "kam hui": "loss", "ke beech": "between", "se": "from",
    }
    for src in sorted(hinglish, key=len, reverse=True):
        text = re.sub(rf"\\b{re.escape(src)}\\b", hinglish[src], text, flags=re.I)

    return text


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --app-bg: #06111c;
    --surface: #081925;
    --surface-2: #0b1f2d;
    --border: #172f40;
    --text: #e8eef5;
    --muted: #8198aa;
    --sidebar: #050c14;
    --accent: #38a9ef;
}

body:has(.tarang-light-mode) {
    --app-bg: #f5f8fb;
    --surface: #ffffff;
    --surface-2: #f1f5f8;
    --border: #d7e0e7;
    --text: #102132;
    --muted: #617587;
    --sidebar: #ffffff;
    --accent: #087fca;
}

.stApp {
    background: var(--app-bg);
    color: var(--text);
}

.tarang-light-mode { display:none; }

.block-container {
    max-width: 1500px;
    padding-top: 0.7rem !important;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    background: #050c14 !important;
    border-right: 1px solid #172735;
}

section[data-testid="stSidebar"] > div {
    background: #050c14 !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 1rem;
}

.brand {
    display: flex;
    align-items: center;
    gap: 9px;
    color: white;
    font-size: 1.4rem;
    font-weight: 750;
}

.brand-subtitle {
    color: #6f879b;
    font-size: 0.69rem;
    margin-top: 4px;
    margin-bottom: 25px;
}

.nav-title {
    color: #5d7890;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: #0a1723;
    color: #9db1c1;
    border: 1px solid #1a2d3d;
    border-radius: 9px;
    min-height: 38px;
    font-size: 0.79rem;
    margin-bottom: 5px;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #10283b;
    color: white;
    border-color: #318bc4;
}

.analysis-card {
    background: #091521;
    border: 1px solid #1a2d3d;
    border-radius: 11px;
    padding: 13px;
    margin-top: 8px;
}

.analysis-row {
    padding: 4px 0 11px;
    margin-bottom: 9px;
    border-bottom: 1px solid #172936;
}

.analysis-row:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 2px;
}

.analysis-label {
    color: #5d7890;
    font-size: 0.60rem;
    font-weight: 700;
    letter-spacing: 1px;
}

.analysis-value {
    color: #dce7ef;
    font-size: 0.79rem;
    margin-top: 3px;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 7px 4px 13px;
    border-bottom: 1px solid #172735;
    margin-bottom: 22px;
}

.top-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}

.top-logo {
    width: 37px;
    height: 37px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #118bd4, #075486);
    font-size: 1.2rem;
}

.top-name {
    color: white;
    font-size: 1.15rem;
    font-weight: 750;
    letter-spacing: 1.3px;
}

.top-tagline {
    color: #688096;
    font-size: 0.62rem;
}

.top-status {
    display: flex;
    align-items: center;
    gap: 7px;
    color: #8fa5b7;
    font-size: 0.70rem;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #36d694;
    display: inline-block;
}

.hero {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(
            circle at 90% 45%,
            rgba(35,130,190,0.20),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #102b41,
            #081722
        );
    border: 1px solid #1c4964;
    border-radius: 18px;
    padding: 32px 38px;
    margin-bottom: 27px;
    min-height: 210px;
}

.hero-glow {
    position: absolute;
    right: -100px;
    top: -130px;
    width: 390px;
    height: 390px;
    border-radius: 50%;
    border: 1px solid rgba(76,174,232,0.12);
    box-shadow: 0 0 100px rgba(25,130,200,0.10);
}

.eyebrow {
    color: #55b4f4;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 1.7px;
    margin-bottom: 8px;
}

.hero-title {
    color: white;
    font-size: 2.2rem;
    font-weight: 750;
    letter-spacing: -1px;
    margin-bottom: 9px;
}

.hero-text {
    color: #9cb3c5;
    font-size: 0.91rem;
    line-height: 1.6;
    max-width: 720px;
}

.hero-status {
    color: #7891a4;
    font-size: 0.70rem;
    margin-top: 17px;
}

.section-label {
    color: #55b4f4;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}

.section-title {
    color: white;
    font-size: 1.23rem;
    font-weight: 700;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background: #0a1723;
    border: 1px solid #192d3e;
    border-radius: 11px;
    padding: 14px;
}

div[data-testid="stMetricLabel"] {
    color: #70879a !important;
    font-size: 0.69rem !important;
}

div[data-testid="stMetricValue"] {
    color: #f5f8fb !important;
    font-size: 1.3rem !important;
}

textarea {
    background: #091724 !important;
    color: #eaf2f8 !important;
    border: 1px solid #20384b !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
}

.stButton > button {
    background: #0b1926;
    color: #a9bdcc;
    border: 1px solid #20384b;
    border-radius: 9px;
    min-height: 40px;
    font-size: 0.79rem;
}

.stButton > button:hover {
    background: #10283b;
    color: white;
    border-color: #318bc4;
}

.stButton > button[kind="primary"] {
    background: #147dcc;
    border: 1px solid #2897e5;
    color: white;
    font-weight: 700;
}

.finding {
    background: #0a1723;
    border: 1px solid #1a2e3e;
    border-left: 3px solid #3096d6;
    border-radius: 8px;
    padding: 13px 15px;
    margin-bottom: 8px;
    color: #aebfcd;
    font-size: 0.81rem;
    line-height: 1.55;
}

.finding strong {
    color: white;
}

.info-card {
    background: #0a1723;
    border: 1px solid #1a2d3d;
    border-radius: 11px;
    padding: 18px;
    min-height: 125px;
}

.info-card-title {
    color: white;
    font-size: 0.90rem;
    font-weight: 650;
    margin-bottom: 7px;
}

.info-card-text {
    color: #8198aa;
    font-size: 0.75rem;
    line-height: 1.55;
}

.method-card {
    background: #0a1723;
    border: 1px solid #1a2d3d;
    border-radius: 11px;
    padding: 15px 11px;
    min-height: 112px;
}

.method-number {
    color: #45aaf0;
    font-size: 0.66rem;
    font-weight: 700;
    margin-bottom: 7px;
}

.method-name {
    color: white;
    font-size: 0.79rem;
    font-weight: 650;
}

.method-description {
    color: #6e8699;
    font-size: 0.67rem;
    margin-top: 5px;
    line-height: 1.4;
}

button[data-baseweb="tab"] {
    color: #7890a3;
    font-size: 0.81rem;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #55b4f4;
}

.footer {
    text-align: center;
    color: var(--muted);
    font-size: 0.65rem;
    margin-top: 35px;
}


/* Strong light-mode readability overrides */
body:has(.tarang-light-mode) .stApp,
body:has(.tarang-light-mode) .main,
body:has(.tarang-light-mode) .block-container {
    color: #102132 !important;
}

body:has(.tarang-light-mode) section[data-testid="stSidebar"] .stButton > button,
body:has(.tarang-light-mode) .stButton > button {
    background: #ffffff !important;
    color: #173047 !important;
    border: 1px solid #cbd8e2 !important;
}

body:has(.tarang-light-mode) section[data-testid="stSidebar"] .stButton > button:hover,
body:has(.tarang-light-mode) .stButton > button:hover {
    background: #eef5f9 !important;
    color: #075f91 !important;
    border-color: #58a9d8 !important;
}

body:has(.tarang-light-mode) .stButton > button[kind="primary"],
body:has(.tarang-light-mode) .stButton > button[data-testid="baseButton-primary"] {
    background: #147dcc !important;
    color: #ffffff !important;
    border-color: #2897e5 !important;
}

body:has(.tarang-light-mode) .analysis-card,
body:has(.tarang-light-mode) .finding,
body:has(.tarang-light-mode) .info-card,
body:has(.tarang-light-mode) .method-card {
    background: #ffffff !important;
    color: #102132 !important;
    border-color: #d7e0e7 !important;
}

body:has(.tarang-light-mode) .analysis-value,
body:has(.tarang-light-mode) .finding,
body:has(.tarang-light-mode) .info-card,
body:has(.tarang-light-mode) .method-card {
    color: #173047 !important;
}

body:has(.tarang-light-mode) .finding strong,
body:has(.tarang-light-mode) .info-card-title,
body:has(.tarang-light-mode) .method-name,
body:has(.tarang-light-mode) .analysis-value {
    color: #102132 !important;
}

body:has(.tarang-light-mode) .analysis-row {
    border-bottom-color: #dfe7ed !important;
}

body:has(.tarang-light-mode) textarea,
body:has(.tarang-light-mode) input {
    background: #ffffff !important;
    color: #102132 !important;
    border-color: #cbd8e2 !important;
}

body:has(.tarang-light-mode) textarea::placeholder,
body:has(.tarang-light-mode) input::placeholder {
    color: #718596 !important;
    opacity: 1 !important;
}

body:has(.tarang-light-mode) div[data-testid="stMetricValue"],
body:has(.tarang-light-mode) div[data-testid="stMetricLabel"] {
    color: #102132 !important;
}

body:has(.tarang-light-mode) button[data-baseweb="tab"] {
    color: #526b7d !important;
}

body:has(.tarang-light-mode) button[data-baseweb="tab"][aria-selected="true"] {
    color: #087fca !important;
}

body:has(.tarang-light-mode) [data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #102132 !important;
    border-color: #cbd8e2 !important;
}

body:has(.tarang-light-mode) [data-baseweb="select"] * {
    color: #102132 !important;
}


/* FINAL LIGHT MODE: Streamlit metric cards must also switch surfaces */
body:has(.tarang-light-mode) div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #cfdbe4 !important;
    border-radius: 11px !important;
    box-shadow: none !important;
}

body:has(.tarang-light-mode) div[data-testid="stMetric"] *,
body:has(.tarang-light-mode) div[data-testid="stMetricLabel"] *,
body:has(.tarang-light-mode) div[data-testid="stMetricValue"] * {
    color: #102132 !important;
}

body:has(.tarang-light-mode) div[data-testid="stMetricLabel"] {
    color: #526b7d !important;
}

body:has(.tarang-light-mode) div[data-testid="stMetricValue"] {
    color: #102132 !important;
}

body:has(.tarang-light-mode) .finding {
    background: #ffffff !important;
    border-color: #cfdbe4 !important;
    color: #102132 !important;
}

body:has(.tarang-light-mode) .finding strong {
    color: #102132 !important;
}

body:has(.tarang-light-mode) .analysis-card {
    background: #ffffff !important;
    border-color: #cfdbe4 !important;
}

body:has(.tarang-light-mode) .analysis-value {
    color: #173047 !important;
}

body:has(.tarang-light-mode) .analysis-label {
    color: #587184 !important;
}

/* Theme overrides */
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background: var(--sidebar) !important; }
.block-container { color: var(--text); }
.stMarkdown, .stCaption, label, p, h1, h2, h3, h4, h5, h6 { color: var(--text); }
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: var(--text) !important; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] { background: var(--surface) !important; color: var(--text) !important; }
[data-testid="stTextInput"] input, textarea { color: var(--text) !important; }

</style>
""",
    unsafe_allow_html=True
)

if not st.session_state.dark_mode:
    st.markdown('<div class="tarang-light-mode"></div>', unsafe_allow_html=True)


# ============================================================
# QUERY UNDERSTANDING
# ============================================================

def understand_query(query):
    text = normalize_multilingual_query(query).lower()
    text = re.sub(r"\s+", " ", text.strip())

    years = [int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    start_year = years[0] if len(years) >= 1 else None
    end_year = years[1] if len(years) >= 2 else None

    change_groups = {
        "Urban Expansion": ["urban", "urban growth", "urban expansion", "city expansion", "built-up", "built up", "builtup", "construction", "constructed", "development", "developed", "building", "buildings", "settlement", "settlements", "city growth"],
        "Vegetation Loss": ["vegetation", "vegetation loss", "vegetation decline", "green cover", "green-cover", "greenery", "forest", "deforestation", "tree cover", "plant cover", "loss of vegetation", "loss of green cover"],
        "Water Change": ["water", "water change", "water body", "waterbody", "lake", "lakes", "river", "rivers", "pond", "ponds", "reservoir", "wetland", "wetlands", "water loss", "water expansion"],
        "Infrastructure Change": ["infrastructure", "road", "roads", "highway", "highways", "expressway", "railway", "metro", "transport", "transportation", "road development", "road construction"]
    }

    change_type = "Unknown"
    # More specific groups first so "water body" is not confused with generic terms.
    for label in ["Vegetation Loss", "Water Change", "Infrastructure Change", "Urban Expansion"]:
        if any(k in text for k in change_groups[label]):
            change_type = label
            break

    location = "Unknown"
    location_text = re.sub(r"\b(?:19|20)\d{2}\b", "", text)
    location_text = re.sub(r"\b(?:show|find|detect|identify|analyze|analyse|compare|measure|check|track|study|investigate|tell me|please|how has|how did|what is|what are)\b", " ", location_text)

    patterns = [
        r"\b(?:in|around|near|at|over)\s+(.+?)\s+(?:between|from|during|over)\b",
        r"\b(?:in|around|near|at|over)\s+(.+?)\s*$"
    ]
    for pattern in patterns:
        m = re.search(pattern, location_text, flags=re.I)
        if m:
            candidate = m.group(1).strip(" .,!?")
            candidate = re.sub(r"\b(?:urban|vegetation|water|infrastructure|change|growth|loss|expansion)\b", " ", candidate, flags=re.I).strip(" .,!?")
            if candidate:
                location = candidate.title()
                break

    if location != "Unknown":
        location = re.sub(r"^(the|area of|area|region of|locality of|locality|location of)\s+", "", location, flags=re.I).strip().title()

    detected = sum([location != "Unknown", start_year is not None, end_year is not None, change_type != "Unknown"])
    confidence = int(detected / 4 * 100)

    return {"location": location, "start_year": start_year, "end_year": end_year, "change_type": change_type, "confidence": confidence}


# ============================================================
# LOCAL BOUNDING BOX# ============================================================
# LOCAL BOUNDING BOX
# ============================================================

def make_local_bbox(
    lat,
    lon,
    lat_radius=0.025,
    lon_radius=0.025
):

    return [
        lon - lon_radius,
        lat - lat_radius,
        lon + lon_radius,
        lat + lat_radius
    ]


# ============================================================
# DYNAMIC DELHI LOCATION RETRIEVAL
# ============================================================

@st.cache_data(ttl=86400)
def geocode_delhi_location(location):

    query = f"{location}, Delhi, India"

    try:

        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "limit": 5,
                "addressdetails": 1
            },
            headers={
                "User-Agent":
                    "TARANG-SIH-Prototype/1.0"
            },
            timeout=15
        )

        response.raise_for_status()

        results = response.json()

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }

    if not results:

        return {
            "status": "not_found",
            "message": (
                f"Could not find '{location}' "
                "using the geographic search service."
            )
        }

    # --------------------------------------------------------
    # FIND A RESULT THAT IS ACTUALLY IN DELHI
    # --------------------------------------------------------

    selected = None

    for result in results:

        address = result.get(
            "address",
            {}
        )

        display_name = (
            result.get(
                "display_name",
                ""
            )
            .lower()
        )

        state = (
            address.get(
                "state",
                ""
            )
            .lower()
        )

        state_district = (
            address.get(
                "state_district",
                ""
            )
            .lower()
        )

        city = (
            address.get(
                "city",
                ""
            )
            .lower()
        )

        county = (
            address.get(
                "county",
                ""
            )
            .lower()
        )

        is_delhi = (

            "delhi" in state

            or

            "delhi" in state_district

            or

            "delhi" in city

            or

            "delhi" in county

            or

            "delhi" in display_name

        )

        is_india = (
            "india" in display_name
            or
            address.get(
                "country",
                ""
            ).lower() == "india"
        )

        if is_delhi and is_india:

            selected = result

            break

    if selected is None:

        return {
            "status": "outside_delhi",
            "message": (
                f"'{location}' was found, "
                "but it does not appear to be "
                "inside Delhi."
            )
        }

    # --------------------------------------------------------
    # COORDINATES
    # --------------------------------------------------------

    lat = float(
        selected["lat"]
    )

    lon = float(
        selected["lon"]
    )

    # --------------------------------------------------------
    # BOUNDING BOX
    # --------------------------------------------------------

    bbox_raw = selected.get(
        "boundingbox"
    )

    bbox = None

    if bbox_raw and len(bbox_raw) == 4:

        south = float(
            bbox_raw[0]
        )

        north = float(
            bbox_raw[1]
        )

        west = float(
            bbox_raw[2]
        )

        east = float(
            bbox_raw[3]
        )

        width = east - west
        height = north - south

        # Use locality boundary only when
        # it is reasonably sized.

        if (
            width > 0
            and height > 0
            and width <= 0.20
            and height <= 0.20
        ):

            bbox = [
                west,
                south,
                east,
                north
            ]

    # For satellite analysis, deliberately use a compact local study
    # footprint around the resolved point instead of the full geocoder
    # administrative/locality boundary. This prevents large areas from
    # being squeezed into a small raster and keeps the visual detail
    # useful for a prototype. The geocoder bbox is still retained by
    # the source response but is not used as the image footprint.
    bbox = make_local_bbox(
        lat,
        lon,
        lat_radius=0.025,
        lon_radius=0.025
    )

    return {
        "status": "success",
        "name": location.title(),
        "lat": lat,
        "lon": lon,
        "bbox": bbox,
        "display_name": selected.get(
            "display_name",
            location
        ),
        "source": "OpenStreetMap / Nominatim"
    }


# ============================================================
# RGB EVALSCRIPT
# ============================================================

RGB_EVALSCRIPT = """

//VERSION=3

function setup() {
    return {
        input: [
            {
                bands: ["B02", "B03", "B04"],
                units: "REFLECTANCE"
            }
        ],
        output: {
            bands: 3,
            sampleType: "FLOAT32"
        }
    };
}

function evaluatePixel(sample) {
    // True color order: Red = B04, Green = B03, Blue = B02.
    // Return reflectance and perform the visual stretch in Python.
    return [
        sample.B04,
        sample.B03,
        sample.B02
    ];
}

"""


# ============================================================
# ANALYSIS EVALSCRIPT
# ============================================================

ANALYSIS_EVALSCRIPT = """
//VERSION=3
function setup() {
    return {
        input: [
            {
                bands: ["B03", "B04", "B08", "B11", "SCL"],
                units: ["REFLECTANCE", "REFLECTANCE", "REFLECTANCE", "REFLECTANCE", "DN"]
            }
        ],
        output: { bands: 4, sampleType: "FLOAT32" }
    };
}

function evaluatePixel(sample) {
    if ([0,1,3,6,7,8,9,10,11].includes(sample.SCL)) {
        return [0,0,0,0];
    }
    let ndbiDen = sample.B11 + sample.B08;
    let ndviDen = sample.B08 + sample.B04;
    let ndwiDen = sample.B03 + sample.B08;
    if (ndbiDen == 0 || ndviDen == 0 || ndwiDen == 0) {
        return [0,0,0,0];
    }
    let ndbi = (sample.B11 - sample.B08) / ndbiDen;
    let ndvi = (sample.B08 - sample.B04) / ndviDen;
    let ndwi = (sample.B03 - sample.B08) / ndwiDen;
    return [ndbi, ndvi, ndwi, 1];
}
"""

# ============================================================
# FETCH SENTINEL-2 DATA# ============================================================
# FETCH SENTINEL-2 DATA
# ============================================================

def calculate_image_size(bbox, resolution_m=10):
    """Choose a practical display raster for a compact local study area.

    Sentinel-2 RGB source data are ~10 m. For a dashboard, requesting a
    moderately oversampled raster prevents the native pixels from being
    enlarged into large visible blocks. This does *not* create new spatial
    information; it only gives the browser a smoother display.
    """

    west, south, east, north = bbox
    center_lat = (south + north) / 2.0
    meters_lat = 111320.0
    meters_lon = 111320.0 * math.cos(math.radians(center_lat))

    width_m = max(1.0, (east - west) * meters_lon)
    height_m = max(1.0, (north - south) * meters_lat)

    native_w = max(64, int(round(width_m / resolution_m)))
    native_h = max(64, int(round(height_m / resolution_m)))

    # Dashboard target: keep the local scene large enough to look good
    # while preserving its aspect ratio.
    target_long_edge = 900 if resolution_m <= 10 else 480
    native_long_edge = max(native_w, native_h)
    scale = min(1.0, target_long_edge / native_long_edge)

    # For small local scenes, deliberately oversample up to the dashboard
    # target. The source remains Sentinel-2 at its native spatial detail.
    if native_long_edge < target_long_edge:
        scale = target_long_edge / native_long_edge

    width_px = max(128, int(round(native_w * scale)))
    height_px = max(128, int(round(native_h * scale)))

    max_dimension = 1400 if resolution_m <= 10 else 700
    down = min(1.0, max_dimension / max(width_px, height_px))
    width_px = max(128, int(round(width_px * down)))
    height_px = max(128, int(round(height_px * down)))

    return (width_px, height_px)


@st.cache_data(
    ttl=86400,
    show_spinner=False
)
def fetch_satellite_data_v5(
    bbox_values,
    year
):

    if SENTINEL_CONFIG is None:

        raise RuntimeError(
            "Copernicus credentials were not found."
        )

    bbox = BBox(
        bbox_values,
        crs=CRS.WGS84
    )

    start_date = (
        f"{year}-01-01"
    )

    end_date = (
        f"{year}-01-31"
    )

    # --------------------------------------------------------
    # RGB IMAGE
    # --------------------------------------------------------

    # IMPORTANT: bbox is WGS84. Therefore resolution=(10,10)
    # would use degrees, not metres. Calculate the pixel dimensions
    # for approximately 10 m Sentinel-2 sampling instead.

    rgb_size = calculate_image_size(bbox_values, resolution_m=10)

    rgb_request = SentinelHubRequest(

        evalscript=RGB_EVALSCRIPT,

        input_data=[

            SentinelHubRequest.input_data(
                data_collection=S2_COLLECTION,
                time_interval=(
                    start_date,
                    end_date
                ),
                mosaicking_order="leastCC"
            )

        ],

        responses=[

            SentinelHubRequest.output_response(
                "default",
                MimeType.TIFF
            )

        ],

        bbox=bbox,

        size=rgb_size,

        config=SENTINEL_CONFIG

    )

    rgb_data = (
        rgb_request.get_data()
    )

    if not rgb_data:

        raise RuntimeError(
            f"No RGB satellite data returned "
            f"for {year}."
        )

    rgb_raw = np.asarray(
        rgb_data[0],
        dtype=np.float32
    )

    if rgb_raw.ndim != 3 or rgb_raw.shape[2] != 3:
        raise RuntimeError(
            f"Unexpected RGB image shape returned by Sentinel Hub: "
            f"{rgb_raw.shape}"
        )

    # Convert reflectance into a visible true-color image.
    # A percentile stretch is more robust for hazy satellite scenes
    # than assuming one fixed brightness range.

    rgb = np.zeros_like(
        rgb_raw,
        dtype=np.float32
    )

    for channel in range(3):

        band = rgb_raw[:, :, channel]

        valid_values = band[
            np.isfinite(band) &
            (band > 0)
        ]

        if valid_values.size == 0:
            raise RuntimeError(
                f"RGB band {channel + 1} contained no valid "
                f"Sentinel-2 reflectance values for {year}."
            )

        low, high = np.percentile(
            valid_values,
            [2, 98]
        )

        if high <= low:
            low = float(np.min(valid_values))
            high = float(np.max(valid_values))

        if high <= low:
            rgb[:, :, channel] = 0
        else:
            rgb[:, :, channel] = (
                (band - low) /
                (high - low)
            )

    rgb = np.clip(
        rgb,
        0.0,
        1.0
    )

    # Mild gamma correction for a more natural display.
    rgb = np.power(
        rgb,
        1.0 / 1.15
    )

    rgb = (
        rgb * 255.0
    ).clip(
        0,
        255
    ).astype(
        np.uint8
    )

    # Smooth the service raster only when the dashboard needs a display resize.
    # This improves visual continuity without inventing satellite detail.
    display_img = Image.fromarray(rgb, mode="RGB")
    try:
        from PIL import ImageFilter
        display_img = display_img.filter(
            ImageFilter.UnsharpMask(radius=0.7, percent=60, threshold=4)
        )
    except Exception:
        pass
    rgb = np.asarray(display_img, dtype=np.uint8)

    # --------------------------------------------------------
    # ANALYSIS IMAGE
    # --------------------------------------------------------

    analysis_request = SentinelHubRequest(

        evalscript=ANALYSIS_EVALSCRIPT,

        input_data=[

            SentinelHubRequest.input_data(
                data_collection=S2_COLLECTION,
                time_interval=(
                    start_date,
                    end_date
                ),
                mosaicking_order="leastCC"
            )

        ],

        responses=[

            SentinelHubRequest.output_response(
                "default",
                MimeType.TIFF
            )

        ],

        bbox=bbox,

        # B11 is a native 20 m Sentinel-2 band. Since bbox is WGS84,
        # calculate the pixel dimensions in metres instead of using
        # resolution=(20,20), which would be interpreted in degrees.
        size=(768, 768),

        config=SENTINEL_CONFIG

    )

    analysis_data = (
        analysis_request.get_data()
    )

    if not analysis_data:

        raise RuntimeError(
            f"No analysis data returned "
            f"for {year}."
        )

    analysis = (
        analysis_data[0]
        .astype(np.float32)
    )

    return rgb, analysis


# ============================================================
# PIXEL AREA
# ============================================================

def calculate_pixel_area(
    bbox,
    width,
    height
):

    west, south, east, north = bbox

    center_lat = (
        south + north
    ) / 2

    meters_lat = 111320.0

    meters_lon = (
        111320.0
        *
        math.cos(
            math.radians(
                center_lat
            )
        )
    )

    total_width = (
        east - west
    ) * meters_lon

    total_height = (
        north - south
    ) * meters_lat

    pixel_width = (
        total_width
        /
        width
    )

    pixel_height = (
        total_height
        /
        height
    )

    return (
        pixel_width
        *
        pixel_height
    )


# ============================================================
# CHANGE DETECTION
# ============================================================

def detect_change(analysis_start, analysis_end, change_type):
    """Detect spatially coherent spectral change for the selected analysis mode.

    Returns a cleaned boolean mask. Thresholds are intentionally conservative
    for a prototype so isolated sensor/noise pixels do not dominate the result.
    """
    valid = (analysis_start[:, :, 3] > 0) & (analysis_end[:, :, 3] > 0)
    ndbi_s, ndbi_e = analysis_start[:, :, 0], analysis_end[:, :, 0]
    ndvi_s, ndvi_e = analysis_start[:, :, 1], analysis_end[:, :, 1]
    ndwi_s, ndwi_e = analysis_start[:, :, 2], analysis_end[:, :, 2]

    d_ndbi = ndbi_e - ndbi_s
    d_ndvi = ndvi_e - ndvi_s
    d_ndwi = ndwi_e - ndwi_s

    if change_type == "Vegetation Loss":
        # Focus on pixels that were vegetated before and show a meaningful
        # decrease in vegetation index.
        mask = valid & (ndvi_s > 0.22) & (d_ndvi < -0.12)
    elif change_type == "Water Change":
        # Capture both emergence and loss of water signal, while avoiding
        # very weak fluctuations.
        water_before = ndwi_s > 0.18
        water_after = ndwi_e > 0.18
        mask = valid & (np.abs(d_ndwi) > 0.12) & (water_before | water_after)
    elif change_type == "Infrastructure Change":
        # Built-surface transition with vegetation kept relatively low.
        mask = valid & (d_ndbi > 0.09) & (ndbi_e > -0.02) & (ndvi_e < 0.30)
    else:
        # Urban expansion: increasing built-up response without a strong
        # vegetation increase.
        mask = valid & (d_ndbi > 0.10) & (ndbi_e > 0.0) & (d_ndvi < 0.10)

    # Remove isolated speckle and close small internal gaps so the visual
    # result represents concentrated zones rather than individual pixels.
    mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
    mask = ndimage.binary_closing(mask, structure=np.ones((5, 5)))

    labeled, count = ndimage.label(mask)
    cleaned = np.zeros_like(mask, dtype=bool)
    if count == 0:
        return cleaned

    sizes = np.bincount(labeled.ravel())
    # Use a slightly larger minimum component for water because water-index
    # noise can otherwise create many tiny false hotspots.
    minimum_pixels = 18 if change_type == "Water Change" else 12
    for component_id in range(1, len(sizes)):
        if sizes[component_id] >= minimum_pixels:
            cleaned[labeled == component_id] = True
    return cleaned


def classify_change_direction(analysis_start, analysis_end, change_type, mask):
    """Provide a human-readable direction summary for the current mask."""
    if not np.any(mask):
        return "No concentrated change detected"

    if change_type == "Water Change":
        delta = analysis_end[:, :, 2] - analysis_start[:, :, 2]
        mean_delta = float(np.nanmean(delta[mask]))
        return "Water signal increased" if mean_delta > 0 else "Water signal decreased"

    if change_type in ("Urban Expansion", "Infrastructure Change"):
        delta = analysis_end[:, :, 0] - analysis_start[:, :, 0]
        mean_delta = float(np.nanmean(delta[mask]))
        return "Built-up signal increased" if mean_delta > 0 else "Built-up signal decreased"

    delta = analysis_end[:, :, 1] - analysis_start[:, :, 1]
    mean_delta = float(np.nanmean(delta[mask]))
    return "Vegetation signal decreased" if mean_delta < 0 else "Vegetation signal increased"


# Backwards-compatible name used by older code.
def detect_urban_change(analysis_start, analysis_end):
    return detect_change(analysis_start, analysis_end, "Urban Expansion")


# ============================================================
# CREATE RED OVERLAY# ============================================================
# CREATE RED OVERLAY
# ============================================================

def create_overlay(
    rgb,
    change_mask
):

    # RGB is requested at native 10 m resolution while the
    # spectral analysis is at native 20 m resolution. Resize the
    # analysis mask to the RGB canvas only for visualization, so
    # the satellite image remains the actual high-resolution base layer.
    image = np.asarray(rgb).copy()

    if image.dtype != np.uint8:
        image = np.clip(
            image,
            0,
            255
        ).astype(np.uint8)

    if change_mask.shape != image.shape[:2]:
        mask_image = Image.fromarray(
            (change_mask.astype(np.uint8) * 255),
            mode="L"
        )

        mask_image = mask_image.resize(
            (image.shape[1], image.shape[0]),
            resample=Image.Resampling.BILINEAR
        )

        display_mask = np.asarray(mask_image) / 255.0
    else:
        display_mask = change_mask.astype(float)

    # Slightly smooth the edge of the visual mask.  This is only
    # for presentation; the underlying detected pixels are unchanged.
    display_mask = ndimage.gaussian_filter(
        display_mask,
        sigma=1.2
    )
    display_mask = np.clip(display_mask, 0.0, 1.0)

    red = np.zeros_like(image)
    red[:, :, 0] = 255
    red[:, :, 1] = 35
    red[:, :, 2] = 35

    alpha = 0.72 * display_mask

    overlay = (
        image.astype(np.float32) * (1.0 - alpha[..., None])
        + red.astype(np.float32) * alpha[..., None]
    ).clip(0, 255).astype(np.uint8)

    return overlay


# ============================================================
# SAVE IMAGE
# ============================================================

def save_image(
    array,
    path
):

    Image.fromarray(
        array
    ).save(
        path
    )




def safe_filename(name):
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", name.lower()).strip("_")


def calculate_change_stats(change_mask, bbox, total_valid_pixels=None):
    height, width = change_mask.shape
    pixel_area = calculate_pixel_area(bbox, width, height)
    changed_pixels = int(np.sum(change_mask))
    changed_area = changed_pixels * pixel_area / 1_000_000
    total_area = ((bbox[2]-bbox[0]) * 111320 * math.cos(math.radians((bbox[1]+bbox[3])/2))) * ((bbox[3]-bbox[1]) * 111320) / 1_000_000
    change_pct = (changed_area / total_area * 100) if total_area > 0 else 0
    labeled, count = ndimage.label(change_mask)
    sizes = np.bincount(labeled.ravel())[1:] if count else np.array([])
    meaningful = sizes[sizes >= 12] if sizes.size else np.array([])
    hotspot_count = len(meaningful)
    largest_area = (int(np.max(meaningful)) * pixel_area / 1_000_000) if hotspot_count else 0
    return changed_area, change_pct, hotspot_count, largest_area


def change_mode_description(change_type):
    return {
        "Urban Expansion": "Areas with increasing built-up spectral response and no strong vegetation increase.",
        "Vegetation Loss": "Areas with a meaningful NDVI decrease from an initially vegetated state.",
        "Water Change": "Areas where the NDWI water signal changes substantially between the two dates.",
        "Infrastructure Change": "Areas with an increasing built-surface response under relatively low vegetation conditions.",
    }.get(change_type, "Spectral change detected from the selected temporal pair.")


def create_change_evidence_map(analysis_start, analysis_end, change_type, change_mask):
    """Create a compact evidence image showing where the selected spectral
    signal changed most strongly. This is a visualization, not a new sensor
    product.
    """
    channel = {
        "Urban Expansion": 0,
        "Infrastructure Change": 0,
        "Vegetation Loss": 1,
        "Water Change": 2,
    }.get(change_type, 0)
    delta = analysis_end[:, :, channel] - analysis_start[:, :, channel]
    values = np.nan_to_num(delta, nan=0.0, posinf=0.0, neginf=0.0)
    if np.any(change_mask):
        lo = float(np.percentile(values[change_mask], 5))
        hi = float(np.percentile(values[change_mask], 95))
    else:
        lo, hi = float(np.min(values)), float(np.max(values))
    span = max(hi - lo, 1e-6)
    normalized = np.clip((values - lo) / span, 0, 1)
    gray = (normalized * 255).astype(np.uint8)
    rgb = np.stack([gray, gray, gray], axis=-1)
    # Keep only detected regions visible; the rest stays dark so the hotspot
    # structure is immediately readable.
    mask = ndimage.gaussian_filter(change_mask.astype(float), sigma=0.8)
    alpha = np.clip(mask, 0, 1)[..., None]
    base = (rgb.astype(np.float32) * (0.20 + 0.80 * alpha)).astype(np.uint8)
    return base


def build_analysis_report(result, changed_area, change_pct, hotspot_count, largest_area, direction):
    return f"""TARANG SATELLITE CHANGE ANALYSIS REPORT\n======================================\n\nLocation: {result['location']}\nPeriod: {result['start_year']} -> {result['end_year']}\nChange type: {result['change_type']}\nDataset: Sentinel-2 L2A\nCoordinates: {result['lat']:.6f}, {result['lon']:.6f}\n\nRESULTS\n-------\nPotential changed area: {changed_area:.3f} km²\nShare of study area: {change_pct:.2f}%\nConcentrated change zones: {hotspot_count}\nLargest change zone: {largest_area:.3f} km²\nDirection: {direction}\n\nINTERPRETATION\n--------------\n{change_mode_description(result['change_type'])}\n\nIMPORTANT LIMITATION\n--------------------\nThese results are spectral change indicators derived from Sentinel-2 imagery.\nThey should not be treated as confirmation of individual buildings, legal status,\nor a ground-verified event. Cloud, seasonal and atmospheric differences can affect\ntemporal comparisons.\n"""


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:

    st.session_state.page = (
        "Change Analysis"
    )

if "query" not in st.session_state:

    st.session_state.query = (
        "Show urban expansion in Kashmere Gate "
        "between 2020 and 2025."
    )

if "last_result" not in st.session_state:

    st.session_state.last_result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.toggle(ui("dark_mode"), value=st.session_state.dark_mode, key="dark_mode")
    st.selectbox(ui("language"), LANGUAGE_OPTIONS, key="language")

    st.html(
        """
        <div class="brand">
            <span>🌊</span>
            <span>TARANG</span>
        </div>

        <div class="brand-subtitle">
            Satellite Intelligence Platform
        </div>
        """
    )

    st.html(
        f"""
        <div class="nav-title">
            {ui("workspace")}
        </div>
        """
    )

    if st.button(
        f"◉   {ui('change_analysis')}",
        use_container_width=True
    ):

        st.session_state.page = (
            "Change Analysis"
        )

    if st.button(
        f"◌   {ui('explore_data')}",
        use_container_width=True
    ):

        st.session_state.page = (
            "Explore Data"
        )

    if st.button(
        f"◌   {ui('methodology')}",
        use_container_width=True
    ):

        st.session_state.page = (
            "Methodology"
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.html(
        f"""
        <div class="nav-title">
            {ui("current_analysis")}
        </div>
        """
    )

    result = (
        st.session_state.last_result
    )

    if result:

        sidebar_location = (
            result["location"]
        )

        sidebar_period = (
            f'{result["start_year"]}'
            f' → '
            f'{result["end_year"]}'
        )

    else:

        sidebar_location = "Kashmere Gate"
        sidebar_period = "2020 → 2025"

    st.html(
        f"""
        <div class="analysis-card">

            <div class="analysis-row">

                <div class="analysis-label">
                    LOCATION
                </div>

                <div class="analysis-value">
                    {sidebar_location}
                </div>

            </div>

            <div class="analysis-row">

                <div class="analysis-label">
                    PERIOD
                </div>

                <div class="analysis-value">
                    {sidebar_period}
                </div>

            </div>

            <div class="analysis-row">

                <div class="analysis-label">
                    DATASET
                </div>

                <div class="analysis-value">
                    Sentinel-2 L2A
                </div>

            </div>

        </div>
        """
    )


# ============================================================
# TOP HEADER
# ============================================================

st.html(
    """
    <div class="topbar">

        <div class="top-brand">

            <div class="top-logo">
                🌊
            </div>

            <div>

                <div class="top-name">
                    TARANG
                </div>

                <div class="top-tagline">
                    Satellite Intelligence Platform
                </div>

            </div>

        </div>

        <div class="top-status">

            <span class="status-dot"></span>

            Analysis engine ready

        </div>

    </div>
    """
)


# ============================================================
# CHANGE ANALYSIS PAGE
# ============================================================

if st.session_state.page == "Change Analysis":

    st.html(f"""
        <div class="hero">
            <div class="hero-glow"></div>
            <div class="eyebrow">SATELLITE INTELLIGENCE</div>
            <div class="hero-title">{ui2("hero_title")}</div>
            <div class="hero-text">{ui2("hero_text")}</div>
            <div class="hero-status"><span class="status-dot"></span>&nbsp; {ui2("location_ready")}</div>
        </div>
    """)

    st.html(f"""<div class="section-label">ANALYSIS QUERY</div><div class="section-title">{ui2("analysis_title")}</div><div style="color:#70879a;font-size:0.74rem;margin-bottom:14px;">{ui2("analysis_help")}</div>""")

    current = st.session_state.last_result
    default_loc = current["location"] if current else "Kashmere Gate"
    default_start = current["start_year"] if current else 2020
    default_end = current["end_year"] if current else 2025
    q1,q2,q3,q4=st.columns(4)
    quick = [(q1,ui2("urban"),f"Show urban expansion in {default_loc} between {default_start} and {default_end}."),(q2,ui2("vegetation"),f"Show vegetation loss in {default_loc} between {default_start} and {default_end}."),(q3,ui2("water"),f"Show water change in {default_loc} between {default_start} and {default_end}."),(q4,ui2("infrastructure"),f"Show infrastructure change in {default_loc} between {default_start} and {default_end}.")]
    for col,label,text_value in quick:
        with col:
            if st.button(label,use_container_width=True):
                st.session_state.query=text_value
                st.rerun()

    query=st.text_area(ui("analysis_query"),value=st.session_state.query,height=75,label_visibility="collapsed",key="query_widget")
    st.session_state.query=query
    query_result=understand_query(query)

    p1,p2,p3,p4=st.columns(4)
    p1.metric(ui2("location"),query_result["location"])
    p2.metric(ui2("start"),query_result["start_year"] or "—")
    p3.metric(ui2("end"),query_result["end_year"] or "—")
    p4.metric(ui2("analysis"),query_result["change_type"])

    st.html(f"""<div class="finding"><strong>Query interpretation</strong><br><br>Location: <strong>{query_result['location']}</strong> &nbsp;·&nbsp; Period: <strong>{query_result['start_year'] or '—'} → {query_result['end_year'] or '—'}</strong> &nbsp;·&nbsp; Type: <strong>{query_result['change_type']}</strong> &nbsp;·&nbsp; Confidence: <strong>{query_result['confidence']}%</strong></div>""")

    analyze=st.button(ui("analyze"),type="primary",use_container_width=False)
    if analyze:
        location=query_result["location"]; start_year=query_result["start_year"]; end_year=query_result["end_year"]; change_type=query_result["change_type"]
        if location=="Unknown": st.error("I could not identify the location. Try: 'Show urban expansion in Dwarka between 2020 and 2025.'"); st.stop()
        if start_year is None or end_year is None: st.error(ui("two_years")); st.stop()
        if start_year >= end_year: st.error(ui("year_order")); st.stop()
        if change_type=="Unknown": st.error(ui("specify_change")); st.stop()
        with st.spinner(ui("finding_location", location=location)):
            location_data=geocode_delhi_location(location)
        if location_data["status"]!="success":
            st.error(location_data.get("message","Location could not be resolved.")); st.info(ui("try_locality")); st.stop()
        st.session_state.last_result={"location":location_data["name"],"start_year":start_year,"end_year":end_year,"change_type":change_type,"lat":location_data["lat"],"lon":location_data["lon"],"bbox":location_data["bbox"]}
        bbox=location_data["bbox"]

        st.divider()
        st.html("""<div class="section-label">SATELLITE RETRIEVAL</div><div class="section-title">Retrieving multi-temporal imagery</div>""")
        if SENTINEL_CONFIG is None: st.error("Copernicus credentials are not loaded. Check your .env file."); st.stop()
        progress=st.progress(0)
        try:
            progress.progress(15); rgb_start,analysis_start=fetch_satellite_data_v5(tuple(bbox),start_year)
            safe=safe_filename(location_data["name"]); save_image(rgb_start,RESULTS_DIR/f"{safe}_{start_year}.png")
            progress.progress(50); rgb_end,analysis_end=fetch_satellite_data_v5(tuple(bbox),end_year)
            save_image(rgb_end,RESULTS_DIR/f"{safe}_{end_year}.png")
            progress.progress(75)
        except Exception as error:
            progress.empty(); st.error("Satellite retrieval failed."); st.code(str(error)); st.stop()

        change_mask=detect_change(analysis_start,analysis_end,change_type)
        changed_area,change_pct,hotspot_count,largest_area=calculate_change_stats(change_mask,bbox)
        direction=classify_change_direction(analysis_start,analysis_end,change_type,change_mask)
        overlay=create_overlay(rgb_end,change_mask)
        progress.progress(100); progress.empty()

        st.html(f"""<div class="section-label">CHANGE INTELLIGENCE</div><div class="section-title">{ui2("detected")}</div>""")
        m1,m2,m3,m4=st.columns(4)
        m1.metric(ui2("potential"),f"{changed_area:.3f} km²")
        m2.metric(ui2("study_changed"),f"{change_pct:.2f}%")
        m3.metric(ui2("zones"),hotspot_count)
        m4.metric(ui2("largest"),f"{largest_area:.3f} km²")
        st.html(f"""<div class="finding"><strong>Change interpretation</strong><br><br><strong>{direction}</strong><br><span style="color:#8198aa;">{change_mode_description(change_type)}</span></div>""")

        st.markdown("<br>",unsafe_allow_html=True)
        st.html(f"""<div class="section-label">TEMPORAL COMPARISON</div><div class="section-title">{ui2("see")}</div>""")
        tab1,tab2,tab3=st.tabs([f"Before · {start_year}",f"After · {end_year}","Change Detection"])
        with tab1: st.image(rgb_start,caption=f"Before · {start_year} · Sentinel-2 true color · 10 m source",width="stretch")
        with tab2: st.image(rgb_end,caption=f"After · {end_year} · Sentinel-2 true color · 10 m source",width="stretch")
        with tab3: st.image(overlay,caption=f"Potential {change_type.lower()} highlighted in red",width="stretch")

        st.markdown("<br>",unsafe_allow_html=True)
        st.html(f"""<div class="finding"><strong>Map legend</strong><br><br><span style="display:inline-block;width:14px;height:14px;background:#ff2323;border-radius:3px;margin-right:7px;vertical-align:-2px;"></span> Red overlay = detected {change_type.lower()} signal<br><span style="color:#8198aa;">Only spatially coherent threshold-crossing pixels are highlighted.</span></div>""")

        st.html(f"""<div class="section-label">EVIDENCE VIEW</div><div class="section-title">{ui2("evidence_title")}</div><div style="color:#8198aa;font-size:.74rem;margin-bottom:12px;">{ui2("evidence_help")}</div>""")
        evidence_map = create_change_evidence_map(analysis_start, analysis_end, change_type, change_mask)
        e1, e2 = st.columns([1.7, 1])
        with e1:
            st.image(evidence_map, caption=f"{change_type} spectral evidence", width="stretch")
        with e2:
            st.html(f"""<div class="finding"><strong>What TARANG found</strong><br><br><strong>{hotspot_count}</strong> concentrated zone(s)<br><br><strong>{changed_area:.3f} km²</strong> potential change<br><br><strong>{change_pct:.2f}%</strong> of the local study footprint<br><br><strong>{direction}</strong></div>""")
        st.html(f"""<div class="section-label">LOCATION</div><div class="section-title">{ui2("resolved")}</div>""")
        a1,a2,a3,a4=st.columns(4); a1.metric(ui2("latitude"),f"{location_data['lat']:.5f}"); a2.metric(ui2("longitude"),f"{location_data['lon']:.5f}"); a3.metric("Dataset","Sentinel-2 L2A"); a4.metric(ui2("confidence"),f"{query_result['confidence']}%")
        bbox=location_data["bbox"]
        north_south_km=(bbox[3]-bbox[1])*111.32
        east_west_km=(bbox[2]-bbox[0])*111.32*math.cos(math.radians(location_data['lat']))
        st.html(f"""<div class=\"finding\"><strong>Analysis footprint</strong><br><br>{east_west_km:.2f} km × {north_south_km:.2f} km local window centered on <strong>{location_data['name']}</strong>. The imagery is sourced from Sentinel-2 at native 10 m RGB detail. The displayed raster is enlarged with high-quality Lanczos interpolation and mild sharpening for readability; no extra spatial information is created.</div>""")

        st.html(f"""<div class="finding"><strong>Automated interpretation</strong><br><br>TARANG detected approximately <strong>{changed_area:.3f} km²</strong> of potential {change_type.lower()} signal across <strong>{hotspot_count}</strong> concentrated zone(s) between {start_year} and {end_year}. <strong>{direction}</strong>. These are spectral change indicators, not confirmation of individual structures or events.</div>""")
        buffer=BytesIO(); Image.fromarray(overlay).convert("RGB").save(buffer,format="PNG")
        report_text = build_analysis_report(st.session_state.last_result, changed_area, change_pct, hotspot_count, largest_area, direction)
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(ui2("download_map"),data=buffer.getvalue(),file_name=f"{safe_filename(location_data['name'])}_change_map.png",mime="image/png",use_container_width=True)
        with d2:
            st.download_button(ui2("download_report"),data=report_text.encode("utf-8"),file_name=f"{safe_filename(location_data['name'])}_{start_year}_{end_year}_report.txt",mime="text/plain",use_container_width=True)


# ============================================================
# EXPLORE DATA
# ============================================================

elif st.session_state.page == "Explore Data":
    st.html(f"""<div class="hero"><div class="hero-glow"></div><div class="eyebrow">DATA EXPLORER</div><div class="hero-title">{ui2("explore_title")}</div><div class="hero-text">{ui2("explore_text")}</div></div>""")
    result=st.session_state.last_result
    if result is None:
        st.info(ui2("run_first"))
    else:
        safe=safe_filename(result["location"]); start_path=RESULTS_DIR/f"{safe}_{result['start_year']}.png"; end_path=RESULTS_DIR/f"{safe}_{result['end_year']}.png"
        st.html(f"""<div class="section-label">CURRENT DATA</div><div class="section-title">{result['location']}</div><div style="color:#8198aa;font-size:.8rem;">{result['start_year']} → {result['end_year']} · {result.get('change_type','Urban Expansion')} · Sentinel-2 L2A</div>""")
        c1,c2=st.columns(2)
        with c1:
            st.markdown(f"**Before · {result['start_year']}**")
            if start_path.exists(): st.image(str(start_path),width="stretch")
        with c2:
            st.markdown(f"**After · {result['end_year']}**")
            if end_path.exists(): st.image(str(end_path),width="stretch")
        st.info("Imagery is retrieved from Sentinel-2 through the Copernicus Data Space service. The study-area box is a local satellite analysis area, not necessarily an administrative boundary.")


# ============================================================
# METHODOLOGY
# ============================================================

elif st.session_state.page == "Methodology":

    st.html(
        f"""
        <div class="hero">

            <div class="hero-glow"></div>

            <div class="eyebrow">
                METHODOLOGY
            </div>

            <div class="hero-title">
                {ui2("method_title")}
            </div>

            <div class="hero-text">
                Natural language is converted into a
                geographic search area and a temporal
                satellite analysis.
            </div>

        </div>
        """
    )

    st.html(
        f"""
        <div class="section-label">
            ANALYSIS PIPELINE
        </div>

        <div class="section-title">
            {ui2("pipeline_title")}
        </div>
        """
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    methods = [

        (
            "01",
            "Semantic Query",
            "Extract location, years and change type."
        ),

        (
            "02",
            "Location Retrieval",
            "Find the requested Delhi locality geographically."
        ),

        (
            "03",
            "Satellite Data",
            "Retrieve Sentinel-2 observations for both years."
        ),

        (
            "04",
            "Spectral Analysis",
            "Compare NDBI, NDVI and NDWI signals according to the selected change type."
        ),

        (
            "05",
            "Change Zones",
            "Filter isolated pixels and identify concentrated change."
        )

    ]

    for col, item in zip(
        [c1, c2, c3, c4, c5],
        methods
    ):

        with col:

            st.html(
                f"""
                <div class="method-card">

                    <div class="method-number">
                        {item[0]}
                    </div>

                    <div class="method-name">
                        {item[1]}
                    </div>

                    <div class="method-description">
                        {item[2]}
                    </div>

                </div>
                """
            )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    i1, i2, i3 = st.columns(3)

    with i1:

        st.html(
            """
            <div class="info-card">

                <div class="info-card-title">
                    NDBI
                </div>

                <div class="info-card-text">
                    Helps identify surfaces with
                    built-up characteristics using
                    near-infrared and short-wave
                    infrared information.
                </div>

            </div>
            """
        )

    with i2:

        st.html(
            """
            <div class="info-card">

                <div class="info-card-title">
                    NDVI
                </div>

                <div class="info-card-text">
                    Provides vegetation context
                    for interpreting potential
                    urban change.
                </div>

            </div>
            """
        )

    with i3:

        st.html(
            """
            <div class="info-card">
                <div class="info-card-title">
                    NDWI
                </div>
                <div class="info-card-text">
                    Helps identify water-related spectral change using green and near-infrared information.
                </div>
            </div>
            """
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.html(
        f"""
        <div class="finding">

            <strong>
                {ui2("limitation_title")}
            </strong>

            <br>

            Satellite spectral analysis identifies
            potential change zones. It does not by itself
            confirm individual buildings, structural safety
            or illegal construction.

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">

        TARANG · Multi-Temporal Satellite Intelligence

        <br>

        Sentinel-2 L2A · Semantic Retrieval · SIH Prototype

    </div>
    """
)
