import streamlit as st

# 1. إعدادات الصفحة (يجب أن تكون أول أمر Streamlit في الملف)
st.set_page_config(page_title="TOMA CHAT Pro", layout="wide")

# 2. أضف كود CSS هنا مباشرة (السطر المناسب لتبدأ الواجهة بالوضع الداكن)
st.markdown(
    """
    <style>
    /* خلفية التطبيق العامة */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* خلفية الشريط الجانبي */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        color: #ffffff;
    }
    
    /* تنسيق صناديق الإدخال */
    .stTextInput input, .stTextArea textarea {
        background-color: #21262d !important;
        color: #ffffff !important;
        border-color: #30363d !important;
    }
    
    /* تنسيق القوائم المنسدلة */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #21262d !important;
        color: #ffffff !important;
    }
    
    /* النصوص العامة والعناوين */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. ابدأ بقية كود وتصميم تطبيقك هنا...
