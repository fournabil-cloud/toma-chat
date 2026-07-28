import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="TOMA CHAT Pro", layout="wide", initial_sidebar_state="expanded"
)

# 2. كود الـ CSS للوضع الداكن (ضعه هنا ليعمل على كل التطبيق)
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; color: #ffffff; }
    .stTextInput input, .stTextArea textarea { background-color: #21262d !important; color: #ffffff !important; border-color: #30363d !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #21262d !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. أكواد تطبيقك الأصلية كاملة (أضف هنا الشريط العلوي، لوحة الأدوات، والمرفقات التي كانت موجودة لديك مسبقاً)
