import streamlit as str_app
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
str_app.set_page_config(
    page_title="TOMA CHAT Pro", 
    page_icon=LOGO_FILE if os.path.exists(LOGO_FILE) else "⚡", 
    layout="wide"
)

# حقن مكتبة FontAwesome للأيقونات الاحترافية ومنع الترجمة التلقائية للمتصفح
str_app.markdown("""
    <meta name="google" content="notranslate">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)

DEFAULT_API_KEY = "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"

if "theme" not in str_app.session_state:
    str_app.session_state.theme = "فاتح (Light)"

# --- ثيم جديد بنمط Gemini ---
is_dark = str_app.session_state.theme == "داكن (Dark)"
bg_color = "#FFFFFF" if not is_dark else "#121212"
card_bg = "#F8F9FA" if not is_dark else "#1E1E1E"
text_color = "#212529" if not is_dark else "#FFFFFF"
sidebar_bg = "#F1F3F5" if not is_dark else "#181818"
sidebar_text = "#333333" if not is_dark else "#E0E0E0"
input_bg = "#FFFFFF" if not is_dark else "#2D2D2D"
input_text = "#000000" if not is_dark else "#FFFFFF"
accent_color = "#10A37F"

# --- أكواد CSS التجميلية (معدلة لواجهة Gemini) ---
str_app.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        }}
        
        .main .block-container {{
            padding-bottom: 180px !important;
            max-width: 900px !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
            border-right: 1px solid #E0E0E0;
            box-shadow: none;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {sidebar_text} !important;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 15px;
        }}
        [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p {{
            color: {sidebar_text} !important;
            font-size: 0.9rem;
        }}

        #MainMenu, header, footer {{ visibility: hidden; }}
        
        .header-container {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 40px;
            padding-top: 20px;
        }}
        .header-logo {{
            width: 60px;
            height: 60px;
            border-radius: 16px;
            object-fit: contain;
        }}
        .header-title {{
            margin: 0; 
            padding: 0; 
            font-size: 2.5rem; 
            display: inline-block;
            font-weight: 700;
            color: {text_color};
        }}
        .sidebar-logo {{
            display: block;
            margin: 10px auto 30px auto;
            width: 150px;
            height: auto;
            border-radius: 18px;
            object-fit: contain;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 5px;
            background-color: transparent;
            border-bottom: 1px solid #E0E0E0;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 45px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 8px 8px 0 0;
            color: {text_color};
            font-weight: 600;
            font-size: 0.95rem;
            border: none;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: transparent !important;
            color: {accent_color} !important;
            border-bottom: 3px solid {accent_color} !important;
        }}

        [data-testid="stChatInput"] {{
            position: fixed;
            bottom: 30px;
            right: 50px;
            left: 380px;
            width: auto;
            background-color: transparent;
            z-index: 1000;
        }}
        
        @media (max-width: 992px) {{
            [data-testid="stChatInput"] {{
                left: 50px;
                right: 50px;
            }}
        }}

        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg};
            color: {input_text};
            border-radius: 24px;
            border: 1px solid #DADCE0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            padding: 15px 20px;
            font-size: 1rem;
        }}

        .stButton > button {{
            background-color: {card_bg};
            color: {text_color};
            font-weight: 600;
            border-radius: 20px;
            border: 1px solid #DADCE0;
            transition: all 0.2s ease;
            padding: 8px 20px;
        }}
        .stButton > button:hover {{
            background-color: #E8EAED;
            border: 1px solid #DADCE0;
        }}
        .stDownloadButton > button {{
            background-color: {accent_color};
            color: white;
            font-weight: 600;
            border-radius: 20px;
            border: none;
        }}
        
        .stCheckbox label p {{
            font-size: 0.9rem !important;
            color: {sidebar_text} !important;
        }}
        
        hr {{ border-top: 1px solid #E0E0E0 !important; margin: 15px 0 !important; }}

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

# --- استخراج كود HTML للمعاينة المباشرة ---
def extract_html_code(text):
    pattern = r"```" + r"html\s*(.*?)\s*" + r"```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return None

# --- عرض العنوان والشعار الرئيسي (معدل لواجهة Gemini) ---
if logo_b64:
    str_app.markdown(f"""
        <div class="header-container">
            <img src="{logo_b64}" class="header-logo" alt="Logo" />
            <h1 class="header-title">TOMA CHAT Pro</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    str_app.title("⚡ TOMA CHAT Pro")

# --- إدارة الجلسات ---
if "sessions" not in str_app.session_state:
    str_app.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in str_app.session_state:
    str_app.session_state.current_session = "محادثة جديدة 1"

persona_prompts = {
    "مساعد عام ذكي وودود": "أنت مساعد ذكي ودود ومفيد جداً، أجب بلغة واضحة ودقيقة.",
    "خبير برمجة وتقنية (محترف)": "أنت خبير برمجة وتقنية محترف، قدم أكواد نظيفة، مشروحة بدقة.",
    "كاتب محتوى ومبدع": "أنت كاتب محتوى ومبدع محترف، اكتب بصياغة جذابة، بليغة، ومؤثرة.",
    "مستشار تسويق وأعمال": "أنت مستشار تسويق وأعمال، قدم استراتيجيات ذكية وحلول عملية لنمو المشاريع.",
    "مختصر ومباشر جداً": "كن مختصراً ومباشراً قدر الإمكان، دون حشو أو إطالة."
}

# --- القائمة الجانبية (Sidebar) بأيقونات FontAwesome ---
with str_app.sidebar:
    if logo_b64:
        str_app.markdown(f'<img src="{logo_b64}" class="sidebar-logo" alt="Logo" />', unsafe_allow_html=True)
        
    str_app.markdown("### <i class='fa-solid fa-sliders' style='margin-left: 8px;'></i> إعدادات المنصة", unsafe_allow_html=True)
    
    secret_key = str_app.secrets.get("GROQ_API_KEY", DEFAULT_API_KEY)
    api_key_input = str_app.text_input("مفتاح Groq API Key:", value=secret_key, type="password", key="groq_api_key_v22")

    str_app.markdown("<hr>", unsafe_allow_html=True)
    enable_web_search = str_app.checkbox("🌐 البحث المباشر في الويب", value=False, key="web_search_toggle_v22")
    deep_research_mode = str_app.checkbox("🔍 وضع البحث المتقدم", value=False, key="deep_research_toggle_v22")
    enable_tts = str_app.checkbox("🔊 القراءة الصوتية تلقائياً", value=False, key="tts_toggle_v22")
    enable_code_preview = str_app.checkbox("💻 معاينة أكواد HTML/Web", value=True, key="code_preview_toggle_v22")

    str_app.markdown("<hr>", unsafe_allow_html=True)
    new_theme = str_app.selectbox("🎨 مظهر التطبيق:", ["داكن (Dark)", "فاتح (Light)"], index=1 if not is_dark else 0, key="theme_selector_v22")
    if new_theme != str_app.session_state.theme:
        str_app.session_state.theme = new_theme
        str_app.rerun()

    str_app.divider()
    model_choice = str_app.selectbox(
        "🧠 نموذج الذكاء الاصطناعي:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_v22"
    )

    persona_choice = str_app.selectbox(
        "🎭 شخصية ونمط TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"],
        key="persona_v22"
    )

    str_app.markdown("<hr>", unsafe_allow_html=True)
    str_app.markdown("### <i class='fa-solid fa-comments' style='margin-left: 8px;'></i> المحادثات المحفوظة", unsafe_allow_html=True)
    session_names = list(str_app.session_state.sessions.keys())
    selected_session = str_app.selectbox("اختر المحادثة:", session_names, index=session_names.index(str_app.session_state.current_session), key="session_selector_v22")
    
    if selected_session != str_app.session_state.current_session:
        str_app.session_state.current_session = selected_session
        str_app.rerun()

    col_btn1, col_btn2 = str_app.columns(2)
    with col_btn1:
        if str_app.button("➕ جديدة", key="new_chat_btn_v22"):
            new_name = f"محادثة جديدة {len(str_app.session_state.sessions) + 1}"
            str_app.session_state.sessions[new_name] = []
            str_app.session_state.current_session = new_name
            str_app.rerun()
    with col_btn2:
        if str_app.button("🗑️ مسح", key="clear_chat_btn_v22"):
            str_app.session_state.sessions[str_app.session_state.current_session] = []
            str_app.rerun()

    current_chat_data = str_app.session_state.sessions[str_app.session_state.current_session]
    chat_text_export = ""
    for msg in current_chat_data:
        if msg.get("content"):
            role_label = "المستخدم" if msg["role"] == "user" else "TOMA"
            chat_text_export += f"{role_label}: {msg['content']}\n\n"
    
    if chat_text_export:
        str_app.download_button(
            label="📄 تصدير المحادثة (TXT)",
            data=chat_text_export,
            file_name=f"{str_app.session_state.current_session}.txt",
            mime="text/plain",
            key="export_chat_btn_v22"
        )

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def web_search(query, max_results=3):
    try:
        results = list(DDGS().text(query, max_results=max_results))
        context = "نتائج البحث المباشر في الويب:\n"
        for idx, r in enumerate(results, 1):
            context += f"{idx}. {r['title']}: {r['body']}\n"
        return
