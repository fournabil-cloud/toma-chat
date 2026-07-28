import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="TOMA CHAT Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. كود الـ CSS المتقدم (الوضع الداكن + ضبط الاتجاه العربي RTL بالكامل)
st.markdown(
    """
    <style>
    /* فرض اتجاه الكتابة من اليمين ليسار ودعم اللغة العربية */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }
    
    /* خلفية التطبيق العامة */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* خلفية الشريط الجانبي */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        color: #ffffff;
        direction: rtl;
        text-align: right;
    }
    
    /* تنسيق صناديق الكتابة */
    .stTextInput input, .stTextArea textarea {
        background-color: #21262d !important;
        color: #ffffff !important;
        border-color: #30363d !important;
        text-align: right;
    }
    
    /* تنسيق القوائم المنسدلة */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #21262d !important;
        color: #ffffff !important;
    }
    
    /* النصوص والعناوين العامة */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
    }
    
    /* صندوق الكتابة السفلي للدردشة */
    .stChatInput input {
        background-color: #21262d !important;
        color: #ffffff !important;
        text-align: right;
    }

    /* لوحة الأدوات (Expander) */
    .streamlit-expanderHeader {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d;
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. الشريط الجانبي (Sidebar) مع شعارك الحقيقي
with st.sidebar:
    # عرض شعارك الخاص (تأكد من مطابقة اسم الملف هنا مع اسم الصورة في مشروعك)
    try:
        st.image("logo.png", use_column_width=True)
    except:
        # كود احتياطي في حال لم يتم العثور على اسم الملف تماماً
        st.image("ChatGPT Image 27 يوليو 2026، 10_39_53 م.png", use_column_width=True)

    st.markdown("---")

    groq_key = st.text_input("مفتاح Groq API:", type="password")

    st.markdown("---")
    web_search = st.checkbox("بحث الويب المباشر")
    deep_search = st.checkbox("وضع البحث العميق")
    voice_reading = st.checkbox("القراءة الصوتية التلقائية")
    html_preview = st.checkbox("معاينة أكواد HTML/Web", value=True)

    st.markdown("---")
    model_choice = st.selectbox(
        "النموذج الذكي:",
        ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
    )
    
    persona_choice = st.selectbox(
        "شخصية TOMA:",
        ["مساعد عام ذكي وودود"]
    )

    st.markdown("---")
    st.markdown("### إدارة المحادثات")
    chat_mode = st.selectbox("اختر محادثة:", ["محادثة جديدة 1"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ جديدة"):
            st.session_state.messages = []
    with col2:
        if st.button("🗑️ مسح"):
            st.session_state.messages = []

# 4. الواجهة الرئيسية
st.title("TOMA CHAT Pro")

# لوحة الأدوات وتوليد الصور
with st.expander("🛠️ لوحة الأدوات والمرفقات الذكية وتوليد الصور", expanded=True):
    st.write("مرحباً بك في لوحة التحكم. يمكنك تفعيل الأدوات أو إرفاق الملفات هنا.")
    image_prompt = st.text_input("وصف الصورة المراد توليدها (اختياري):")
    if st.button("🎨 توليد الصورة"):
        if image_prompt:
            st.info("جاري معالجة طلب توليد الصورة...")
        else:
            st.warning("الرجاء كتابة وصف الصورة أولاً.")

# 5. نظام المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("... اكتب رسالتك هنا")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("جاري المعالجة...")
        response_placeholder.markdown("أهلاً بك! أنا جاهز لتلقي أوامرك.")
