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

# --- ثيم GEMINI الأبيض الاحترافي ---
# تم فرض الألوان الفاتحة والخطوط النظيفة لمنع الشاشة السوداء
bg_color = "#FFFFFF" 
card_bg_color = "#F8F9FA" 
text_color = "#202124" 
sidebar_bg_color = "#F5F5F5" 
sidebar_text_color = "#5F6368" 
input_bg_color = "#FFFFFF" 
input_border_color = "#DADCE0" 
accent_color = "#1A73E8" # لون أزرق جميناي المميز
success_color = "#188038"

# --- أكواد CSS المحدثة لفرض شكل جميناي ---
str_app.markdown(f"""
    <style>
        /* تطبيق الثيم العام وإجبار الخلفية البيضاء */
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
            font-family: 'Google Sans', Roboto, Helvetica, Arial, sans-serif !important;
        }}
        
        /* توسيع منطقة العمل الرئيسية */
        .main .block-container {{
            padding-top: 60px !important;
            padding-bottom: 150px !important;
            max-width: 1000px !important;
        }}

        /* القائمة الجانبية - Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color} !important;
            border-right: none !important;
            padding-top: 20px !important;
        }}
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {sidebar_text_color} !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            font-weight: 500 !important;
            margin-bottom: 15px !important;
            padding-left: 15px !important;
        }}
        
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {{
            color: {sidebar_text_color} !important;
            font-size: 0.95rem !important;
        }}

        /* إخفاء شعار Streamlit الافتراضي والقائمة العلوية */
        #MainMenu, header, footer {{ visibility: hidden; }}
        
        /* اللوجو والعنوان العلوي */
        .header-container {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 50px;
        }}
        .header-logo {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            object-fit: contain;
        }}
        .header-title {{
            font-size: 1.6rem !important;
            color: {text_color} !important;
            font-weight: 500 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .sidebar-logo {{
            display: block;
            margin: 0 auto 40px auto;
            width: 120px;
            height: auto;
            border-radius: 12px;
        }}

        /* منطقة الإدخال - Chat Input */
        [data-testid="stChatInput"] {{
            background-color: transparent !important;
            border: none !important;
            position: fixed !important;
            bottom: 20px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 700px !important;
            max-width: 90% !important;
        }}
        
        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg_color} !important;
            color: {text_color} !important;
            border: 1px solid {input_border_color} !important;
            border-radius: 30px !important;
            padding: 15px 25px !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: #9AA0A6 !important;
        }}

        /* الأزرار - Buttons */
        .stButton > button {{
            background-color: {card_bg_color} !important;
            color: {text_color} !important;
            border: 1px solid {input_border_color} !important;
            border-radius: 18px !important;
            font-weight: 500 !important;
            padding: 6px 15px !important;
            transition: all 0.2s !important;
            font-size: 0.9rem !important;
        }}
        .stButton > button:hover {{
            background-color: #E8EAED !important;
            border-color: #DADCE0 !important;
        }}
        
        .stDownloadButton > button {{
            background-color: {accent_color} !important;
            color: white !important;
            border: none !important;
        }}

        /* تبويبات الأدوات - Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px !important;
            background-color: transparent !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {card_bg_color} !important;
            border: 1px solid {input_border_color} !important;
            border-radius: 12px !important;
            color: {text_color} !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: #E8EAF6 !important;
            color: {accent_color} !important;
            border-color: #C5CAE9 !important;
        }}

        /* رسائل الشات */
        .stChatMessage {{
            padding: 15px 0 !important;
            gap: 15px !important;
        }}
        .stChatMessage p {{
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }}
        /* أيقونة المستخدم والذكاء الاصطناعي */
        [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {{
            border-radius: 50% !important;
            width: 36px !important;
            height: 36px !important;
        }}
        [data-testid="stChatMessageAvatarAssistant"] {{
            background-color: transparent !important;
        }}

        /* عناصر النموذج الجانبي */
        .stSelectbox label, .stTextInput label, .stCheckbox label {{
            font-weight: 500 !important;
        }}
        
        /* تحسين شكل الـ Expander */
        .stExpander {{
            border: 1px solid {input_border_color} !important;
            border-radius: 12px !important;
            background-color: {card_bg_color} !important;
        }}
        
        /* خطوط الفصل */
        hr {{
            border-top: 1px solid {input_border_color} !important;
            margin: 20px 0 !important;
        }}

    </style>
""", unsafe_allow_html=True)

# --- دوال النظام ---
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

def extract_html_code(text):
    pattern = r"```" + r"html\s*(.*?)\s*" + r"```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return None

# --- واجهة العنوان والشعار ---
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
    st.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in str_app.session_state:
    st.session_state.current_session = "محادثة جديدة 1"

# --- القائمة الجانبية (Sidebar) المحدثة ---
with str_app.sidebar:
    if logo_b64:
        str_app.markdown(f'<img src="{logo_b64}" class="sidebar-logo" alt="Logo" />', unsafe_allow_html=True)
        
    str_app.markdown("### <i class='fa-solid fa-sliders' style='margin-left: 10px;'></i> الإعدادات", unsafe_allow_html=True)
    
    secret_key = str_app.secrets.get("GROQ_API_KEY", DEFAULT_API_KEY)
    api_key_input = str_app.text_input("Groq API Key:", value=secret_key, type="password", key="groq_api_key_v23")

    str_app.markdown("<hr>", unsafe_allow_html=True)
    enable_web_search = str_app.checkbox("🌐 بحث الويب المباشر", value=False, key="web_search_toggle_v23")
    deep_research_mode = str_app.checkbox("🔍 وضع البحث العميق", value=False, key="deep_research_toggle_v23")
    enable_tts = str_app.checkbox("🔊 القراءة الصوتية التلقائية", value=False, key="tts_toggle_v23")
    enable_code_preview = str_app.checkbox("💻 معاينة أكواد HTML/Web", value=True, key="code_preview_toggle_v23")

    str_app.divider()
    model_choice = str_app.selectbox(
        "🧠 النموذج الذكي:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_v23"
    )

    persona_choice = str_app.selectbox(
        "🎭 شخصية TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"],
        key="persona_v23"
    )

    str_app.markdown("<hr>", unsafe_allow_html=True)
    str_app.markdown("### <i class='fa-solid fa-clock-rotate-left' style='margin-left: 10px;'></i> المحادثات", unsafe_allow_html=True)
    session_names = list(str_app.session_state.sessions.keys())
    selected_session = str_app.selectbox("اختر محادثة:", session_names, index=session_names.index(str_app.session_state.current_session), key="session_selector_v23")
    
    if selected_session != str_app.session_state.current_session:
        str_app.session_state.current_session = selected_session
        str_app.rerun()

    col_btn1, col_btn2 = str_app.columns(2)
    with col_btn1:
        if str_app.button("➕ جديدة", key="new_chat_btn_v23", use_container_width=True):
            new_name = f"محادثة جديدة {len(str_app.session_state.sessions) + 1}"
            str_app.session_state.sessions[new_name] = []
            str_app.session_state.current_session = new_name
            str_app.rerun()
    with col_btn2:
        if str_app.button("🗑️ مسح", key="clear_chat_btn_v23", use_container_width=True):
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
