import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="TOMA CHAT Pro", layout="wide", initial_sidebar_state="expanded"
)

# 2. كود CSS لتفعيل الوضع الداكن وتنسيق الواجهة بالكامل
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
    
    /* تنسيق صناديق إدخال النصوص */
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
    
    /* النصوص العامة والعناوين لضمان وضوحها باللون الأبيض */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
    }
    
    /* تنسيق صندوق الإرسال السفلي */
    .stChatInput input {
        background-color: #21262d !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. محتوى الشريط الجانبي (Sidebar)
with st.sidebar:
  st.markdown("### TOMA CHAT Pro")
  st.markdown("---")

  groq_key = st.text_input("Groq API Key:", type="password")

  st.markdown("---")
  web_search = st.checkbox("بحث الويب المباشر")
  deep_search = st.checkbox("وضع البحث العميق")
  voice_reading = st.checkbox("القراءة الصوتية التلقائية")
  html_preview = st.checkbox("HTML/Web معاينة أكواد", value=True)

  st.markdown("---")
  model_choice = st.selectbox(
      "النموذج الذكي:", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
  )
  persona_choice = st.selectbox("TOMA: شخصية", ["مساعد عام ذكي وودود"])

# 4. الواجهة الرئيسية للدردشة
st.title("TOMA CHAT Pro")

# خانة كتابة الرسائل في أسفل الشاشة
user_input = st.chat_input("... اكتب رسالتك هنا")

if user_input:
  with st.chat_message("user"):
    st.write(user_input)

  with st.chat_message("assistant"):
    st.write("جاري المعالجة...")
