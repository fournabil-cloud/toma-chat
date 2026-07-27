import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from PIL import Image
import urllib.parse
import requests
from io import BytesIO
import base64
import os
import re
from pypdf import PdfReader
from duckduckgo_search import DDGS
from gtts import gTTS

# --- دالة موثوقة لتحميل وصياغة الصورة (Logo) ---
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return None

LOGO_FILE = "logo.png"
logo_b64 = get_image_base64(LOGO_FILE)

# -- إعداد الصفحة --
st.set_page_config(
    page_title="TOMA CHAT Pro", 
    page_icon=LOGO_FILE if os.path.exists(LOGO_FILE) else "⚡", 
    layout="wide"
)

# تعيين المفتاح المباشر تلقائياً
DEFAULT_API_KEY = "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"

if "theme" not in st.session_state:
    st.session_state.theme = "داكن (Dark)"

is_dark = st.session_state.theme == "داكن (Dark)"
bg_color = "#121212" if is_dark else "#F8F9FA"
card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#212529"
sidebar_bg = "#181818" if is_dark else "#F1F3F5"
sidebar_text = "#E0E0E0" if is_dark else "#333333"
input_bg = "#2D2D2D" if is_dark else "#FFFFFF"
input_text = "#FFFFFF" if is_dark else "#000000"
accent_color = "#10A37F"

# --- أكواد CSS التجميلية ---
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        }}
        
        .main .block-container {{
            padding-bottom: 140px !important;
            max-width: 1100px !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
            border-left: 1px solid #2A2A2A;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #FFFFFF !important;
            font-weight: 600;
        }}
        [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p {{
            color: {sidebar_text} !important;
        }}

        #MainMenu, header, footer {{ visibility: hidden; }}
        
        .header-container {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
        }}
        .header-logo {{
            width: 55px;
            height: 55px;
            border-radius: 12px;
            object-fit: contain;
        }}
        .sidebar-logo {{
            display: block;
            margin: 0 auto 15px auto;
            width: 130px;
            height: auto;
            border-radius: 16px;
            object-fit: contain;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 8px;
            color: #AAAAAA;
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {accent_color} !important;
            color: #FFFFFF !important;
        }}

        [data-testid="stChatInput"] {{
            position: fixed;
            bottom: 25px;
            right: 25px;
            left: 380px;
            width: auto;
            background-color: transparent;
            z-index: 1000;
        }}
        
        @media (max-width: 992px) {{
            [data-testid="stChatInput"] {{
                left: 25px;
            }}
        }}

        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg};
            color: {input_text};
            border-radius: 14px;
            border: 1px solid #444444;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }}

        .stButton > button {{
            background-color: {accent_color};
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            background-color: #0E8E6D;
            border: none;
        }}
        .stDownloadButton > button {{
            background-color: #2B6CB0;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
        }}
    </style>
""", unsafe_allow_html=True)

# --- دالة لتحويل النص إلى صوت ---
def text_to_speech(text):
    try:
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        lang = 'ar' if has_arabic else 'en'
        tts = gTTS(text=text[:500], lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception:
        return None

# --- استخراج كود HTML لللمعاينة المباشرة ---
def extract_html_code(text):
    match = re.search(r'```html\s*(.*?)\s*
