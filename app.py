import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="TOMA CHAT Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. إعداد الشريط الجانبي والشعار واختيار الثيم
with st.sidebar:
    try:
        st.image("logo.png", use_column_width=True)
    except:
        st.image("ChatGPT Image 27 يوليو 2026، 10_39_53 م.png", use_column_width=True)

    st.markdown("---")
    
    # خيار تبديل الألوان (الثيم)
    theme_mode = st.selectbox(
        "🎨 مظهر الواجهة:", 
        ["الوضع الداكن (Dark)", "الوضع الفاتح (Light)"]
    )

# ضبط الألوان بناءً على اختيار الثيم
if theme_mode == "الوضع الداكن (Dark)":
    bg_color = "#0e1117"
    sidebar_bg = "#161b22"
    text_color = "#ffffff"
    input_bg = "#21262d"
    border_color = "#30363d"
else:
    bg_color = "#ffffff"
    sidebar_bg = "#f0f2f6"
    text_color = "#000000"
    input_bg = "#ffffff"
    border_color = "#d1d5db"

# 3. حقن الـ CSS المعدل
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        color: {text_color};
        direction: rtl;
        text-align: right;
    }}
    .main .block-container {{
        direction: rtl;
        text-align: right;
    }}
    .stTextInput input, .stTextArea textarea {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
        direction: rtl;
        text-align: right;
    }}
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        direction: rtl;
    }}
    h1, h2, h3, h4, h5, h6, p, span, label {{
        color: {text_color} !important;
    }}
    .stChatInput input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        direction: rtl;
        text-align: right;
    }}
    .streamlit-expanderHeader {{
        background-color: {sidebar_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color};
        direction: rtl;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. محتوى الشريط الجانبي المتقدم
with st.sidebar:
    st.markdown("---")
    groq_key = st.text_input("مفتاح Groq API:", type="password", placeholder="أدخل مفتاحك هنا...")

    st.markdown("---")
    st.markdown("### ⚙️ الإعدادات والأدوات")
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
        ["مساعد عام ذكي وودود", "مطور برمجيات خبير", "كاتب محتوى محترف"]
    )

    st.markdown("---")
    st.markdown("### 🕒 إدارة المحادثات")
    chat_mode = st.selectbox("اختر محادثة:", ["محادثة جديدة 1"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ جديدة"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🗑️ مسح"):
            st.session_state.messages = []
            st.rerun()

# 5. الواجهة الرئيسية للدردشة وتوليد الصور
st.title("TOMA CHAT Pro")

# لوحة الأدوات وتوليد الصور الفاعلة
with st.expander("🛠️ لوحة الأدوات والمرفقات الذكية وتوليد الصور", expanded=False):
    st.write("قم بتفعيل الأدوات المساعدة أو أدخل وصفاً دقيقاً لتوليد صورة فورية عبر الذكاء الاصطناعي.")
    
    col_img1, col_img2 = st.columns([3, 1])
    with col_img1:
        image_prompt = st.text_input("وصف الصورة المراد توليدها:", placeholder="مثال: A futuristic glowing cybernetic wolf...")
    with col_img2:
        st.write("")
        st.write("")
        gen_btn = st.button("🎨 توليد الصورة الآن")
        
    if gen_btn:
        if image_prompt:
            with st.spinner("جاري إرسال الوصف لمحرك توليد الصور ورسم اللوحة..."):
                import urllib.parse
                # استخدام محرك مجاني وعالي الجودة لتوليد الصور مباشرة بناءً على الوصف النصي
                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                
                st.success("تم توليد الصورة بنجاح!")
                st.image(image_url, caption=f"الوصف: {image_prompt}", use_column_width=True)
        else:
            st.warning("الرجاء كتابة وصف الصورة في الحقل المخصص أولاً.")

# 6. نظام إدارة الذاكرة وعرض الرسائل
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("... اكتب رسالتك هنا أو اطلب شيئاً من TOMA")

if user_input:
    if not groq_key:
        st.toast("⚠️ تنبيه: لم تقم بإدخال مفتاح Groq API في الشريط الجانبي!", icon="🚨")
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("TOMA يفكر ويقوم بإعداد الرد..."):
            if groq_key:
                bot_response = f"أهلاً بك يا نبيل! لقد استلمت رسالتك وأعمل بنموذج ({model_choice}) مع تفعيل شخصية ({persona_choice}). كيف يمكنني مساعدتك أكثر في مشروعك؟"
            else:
                bot_response = "أهلاً بك! يرجى إدخال مفتاح `Groq API Key` من الشريط الجانبي لكي أتمكن من الرد عليك بشكل كامل."
            
            st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
