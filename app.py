import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="TOMA CHAT Pro", page_icon="⚡", layout="centered")

if "theme" not in st.session_state:
    st.session_state.theme = "داكن (Dark)"

bg_color = "#212121" if st.session_state.theme == "داكن (Dark)" else "#F9F9F9"
text_color = "#FFFFFF" if st.session_state.theme == "داكن (Dark)" else "#111111"
chat_bg = "#343541" if st.session_state.theme == "داكن (Dark)" else "#E5E5EA"
input_bg = "#2F2F2F" if st.session_state.theme == "داكن (Dark)" else "#FFFFFF"
input_text = "#FFFFFF" if st.session_state.theme == "داكن (Dark)" else "#000000"

st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: sans-serif; }}
        h1 {{ color: {text_color}; text-align: center; font-size: 36px; margin-bottom: 20px; }}
        #MainMenu, header, footer {{ visibility: hidden; }}
        [data-testid="stChatInput"] {{ position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); width: 65%; background-color: {bg_color}; }}
        [data-testid="stChatInput"] textarea {{ background-color: {input_bg}; color: {input_text}; border-radius: 8px; padding: 12px; border: 1px solid #404040; }}
        [data-testid="stChatMessageAssistant"] {{ background-color: {chat_bg}; color: {text_color}; }}
        .stButton > button {{ background-color: #19C37D; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; width: 100%; }}
        .stButton > button:hover {{ background-color: #1A7F64; }}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ TOMA CHAT Pro")

if "sessions" not in st.session_state:
    st.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "محادثة جديدة 1"

with st.sidebar:
    st.header("⚙️ إعدادات TOMA")
    api_key_input = st.text_input("أدخل مفتاح Google API Key:", type="password")

    st.divider()
    new_theme = st.selectbox("مظهر التطبيق:", ["داكن (Dark)", "فاتح (Light)"], index=0 if st.session_state.theme == "داكن (Dark)" else 1)
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.divider()
    st.subheader("💬 المحادثات المحفوظة")
    session_names = list(st.session_state.sessions.keys())
    selected_session = st.selectbox("اختر المحادثة:", session_names, index=session_names.index(st.session_state.current_session))
    
    if selected_session != st.session_state.current_session:
        st.session_state.current_session = selected_session
        st.rerun()

    if st.button("➕ محادثة جديدة"):
        new_name = f"محادثة جديدة {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
        st.rerun()

    st.divider()
    # الاعتماد على النموذج النشط والمستقر المتاح لجميع الحسابات
    model_choice = st.selectbox(
        "اختر نموذج الذكاء الاصطناعي:",
        ["gemini-2.0-flash"],
        key="model_v2026_fixed"
    )

    persona_choice = st.selectbox(
        "اختر شخصية ونمط TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"]
    )

    st.divider()
    if st.button("🗑️ مسح المحادثة الحالية"):
        st.session_state.sessions[st.session_state.current_session] = []
        st.rerun()

persona_prompts = {
    "مساعد عام ذكي وودود": "أنت مساعد ذكي ودود ومفيد جداً، أجب بلغة واضحة ودقيقة.",
    "خبير برمجة وتقنية (محترف)": "أنت خبير برمجة وتقنية محترف، قدم أكواد نظيفة، مشروحة بدقة.",
    "كاتب محتوى ومبدع": "أنت كاتب محتوى ومبدع محترف، اكتب بصياغة جذابة، بليغة، ومؤثرة.",
    "مستشار تسويق وأعمال": "أنت مستشار تسويق وأعمال، قدم استراتيجيات ذكية وحلول عملية لنمو المشاريع.",
    "مختصر ومباشر جداً": "كن مختصراً ومباشراً قدر الإمكان، دون حشو أو إطالة."
}

if api_key_input:
    clean_api_key = api_key_input.strip()
    try:
        client = genai.Client(api_key=clean_api_key)
        system_instruction = persona_prompts.get(persona_choice, "أنت مساعد ذكي.")
        messages = st.session_state.sessions[st.session_state.current_session]

        for idx, message in enumerate(messages):
            with st.chat_message(message["role"]):
                if "image" in message and message["image"] is not None:
                    st.image(message["image"], caption="الصورة المرفقة", width=250)
                st.markdown(message["content"])

        uploaded_file = st.file_uploader("📷 رفع صورة لتحليلها (اختياري):", type=["jpg", "jpeg", "png"])
        prompt = st.chat_input("اكتب رسالتك...")

        if prompt:
            img_to_send = Image.open(uploaded_file) if uploaded_file else None
            messages.append({"role": "user", "content": prompt, "image": img_to_send})
            
            with st.chat_message("user"):
                if img_to_send:
                    st.image(img_to_send, caption="الصورة المرفقة", width=250)
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("TOMA يفكر..."):
                    contents = []
                    if img_to_send:
                        contents.append(img_to_send)
                    contents.append(prompt)

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=contents,
                        config={'system_instruction': system_instruction}
                    )
                    
                    bot_response = response.text
                    st.markdown(bot_response)
                    messages.append({"role": "assistant", "content": bot_response, "image": None})
            st.rerun()

    except Exception as e:
        st.error(f"حدث خطأ في الاتصال: {e}")
else:
    st.info("👋 أهلاً بك في تطبيق **TOMA CHAT Pro**! يرجى إدخال مفتاح Google API Key الخاص بك في الشريط الجانبي لبدء الدردشة.")
