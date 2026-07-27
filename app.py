import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse
import base64

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
    api_key_input = st.text_input("أدخل مفتاح Groq API Key:", type="password")

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
    model_choice = st.selectbox(
        "اختر نموذج النص والتحليل:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_choice"
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

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def generate_image_url(prompt):
    encoded_prompt = urllib.parse.quote(prompt)
    # رابط مباشر ومستقر ومجاني بدون حظر متصفحات
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=800&nologo=true"

if api_key_input:
    clean_api_key = api_key_input.strip()
    try:
        client = Groq(api_key=clean_api_key)
        system_instruction = persona_prompts.get(persona_choice, "أنت مساعد ذكي.")
        messages = st.session_state.sessions[st.session_state.current_session]

        for message in messages:
            with st.chat_message(message["role"]):
                if message.get("image"):
                    st.image(message["image"], caption="الصورة المرفقة", width=250)
                if message.get("generated_image_url"):
                    # عرض الصورة عبر Markdown لتفادي مشاكل التحميل في Streamlit
                    st.markdown(f"![الصورة المولدة]({message['generated_image_url']})")
                if message.get("content"):
                    st.markdown(message["content"])

        st.subheader("🎨 أدوات الصور:")
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("📷 رفع صورة لتحليلها (Vision):", type=["jpg", "jpeg", "png"])
        with col2:
            gen_image_prompt = st.text_input("🖌️ توليد صورة جديدة (اكتب الوصف هنا):")
            generate_btn = st.button("🎨 ارسم الصورة")

        # معالجة أمر توليد الصور
        if generate_btn and gen_image_prompt:
            with st.chat_message("user"):
                st.markdown(f"**طلب توليد صورة:** {gen_image_prompt}")
            messages.append({"role": "user", "content": f"طلب توليد صورة: {gen_image_prompt}"})

            with st.chat_message("assistant"):
                with st.spinner("جاري رسم الصورة الذكية..."):
                    img_url = generate_image_url(gen_image_prompt)
                    st.markdown(f"![{gen_image_prompt}]({img_url})")
                    st.markdown("✨ تم توليد الصورة بنجاح!")
                    messages.append({"role": "assistant", "content": "✨ تم توليد الصورة بنجاح!", "generated_image_url": img_url})
            st.rerun()

        prompt = st.chat_input("اكتب رسالتك...")

        if prompt:
            img_data = uploaded_file if uploaded_file else None
            messages.append({"role": "user", "content": prompt, "image": img_data})
            
            with st.chat_message("user"):
                if img_data:
                    st.image(img_data, caption="الصورة المرفقة", width=250)
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("TOMA يفكر..."):
                    if img_data:
                        base64_img = encode_image(img_data)
                        vision_messages = [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                                    }
                                ]
                            }
                        ]
                        completion = client.chat.completions.create(
                            model="llama-3.2-11b-vision-preview",
                            messages=vision_messages,
                        )
                    else:
                        groq_messages = [{"role": "system", "content": system_instruction}]
                        for m in messages:
                            if m.get("content"):
                                groq_messages.append({"role": m["role"], "content": m["content"]})

                        completion = client.chat.completions.create(
                            model=model_choice,
                            messages=groq_messages,
                            temperature=0.7,
                        )
                    
                    bot_response = completion.choices[0].message.content
                    st.markdown(bot_response)
                    messages.append({"role": "assistant", "content": bot_response})
            st.rerun()

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
else:
    st.info("👋 أهلاً بك في **TOMA CHAT Pro**! أدخل مفتاح Groq API Key في الشريط الجانبي لتفعيل الشات ورسم وتحليل الصور.")
