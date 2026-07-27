import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse
import requests
from io import BytesIO
import base64
from pypdf import PdfReader

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
    api_key_input = st.text_input("أدخل مفتاح Groq API Key:", type="password", key="groq_api_key_v2")

    st.divider()
    new_theme = st.selectbox("مظهر التطبيق:", ["داكن (Dark)", "فاتح (Light)"], index=0 if st.session_state.theme == "داكن (Dark)" else 1, key="theme_selector_v2")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.divider()
    st.subheader("💬 المحادثات المحفوظة")
    session_names = list(st.session_state.sessions.keys())
    selected_session = st.selectbox("اختر المحادثة:", session_names, index=session_names.index(st.session_state.current_session), key="session_selector_v2")
    
    if selected_session != st.session_state.current_session:
        st.session_state.current_session = selected_session
        st.rerun()

    if st.button("➕ محادثة جديدة", key="new_chat_btn_v2"):
        new_name = f"محادثة جديدة {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_name] = []
        st.session_state.current_session = new_name
        st.rerun()

    st.divider()
    model_choice = st.selectbox(
        "اختر نموذج الذكاء الاصطناعي:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_v2"
    )

    persona_choice = st.selectbox(
        "اختر شخصية ونمط TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"],
        key="persona_v2"
    )

    st.divider()
    if st.button("🗑️ مسح المحادثة الحالية", key="clear_chat_btn_v2"):
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

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def fetch_generated_image(prompt):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.content
    except Exception:
        return None
    return None

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
                if message.get("generated_image_bytes"):
                    st.image(message["generated_image_bytes"], caption="الصورة المولدة", width=400)
                    st.download_button(
                        label="📥 تنزيل الصورة",
                        data=message["generated_image_bytes"],
                        file_name="toma_generated_image.png",
                        mime="image/png",
                        key=f"dl_{hash(message['content'])}"
                    )
                if message.get("content"):
                    st.markdown(message["content"])

        st.subheader("📁 المرفقات وأدوات الصور:")
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("📷/📄 رفع صورة أو مستند (PDF/TXT):", type=["jpg", "jpeg", "png", "pdf", "txt"], key="doc_uploader_v2")
        with col2:
            gen_image_prompt = st.text_input("🖌️ توليد صورة جديدة (اكتب الوصف):", key="gen_image_prompt_v2")
            generate_btn = st.button("🎨 ارسم الصورة", key="gen_image_btn_v2")

        # معالجة رسم الصورة
        if generate_btn and gen_image_prompt:
            with st.chat_message("user"):
                st.markdown(f"**طلب توليد صورة:** {gen_image_prompt}")
            messages.append({"role": "user", "content": f"طلب توليد صورة: {gen_image_prompt}"})

            with st.chat_message("assistant"):
                with st.spinner("جاري جلب ورسم الصورة..."):
                    img_bytes = fetch_generated_image(gen_image_prompt)
                    if img_bytes:
                        st.image(img_bytes, caption=f"رسمة: {gen_image_prompt}", width=400)
                        st.download_button(
                            label="📥 تنزيل الصورة",
                            data=img_bytes,
                            file_name="toma_image.png",
                            mime="image/png"
                        )
                        st.markdown("✨ تم توليد الصورة بنجاح!")
                        messages.append({
                            "role": "assistant",
                            "content": "✨ تم توليد الصورة بنجاح!",
                            "generated_image_bytes": img_bytes
                        })
                    else:
                        st.error("تعذر تحميل الصورة حالياً، يرجى إعادة المحاولة.")
            st.rerun()

        prompt = st.chat_input("اكتب رسالتك...")

        if prompt:
            file_type = uploaded_file.name.split(".")[-1].lower() if uploaded_file else None
            user_msg = {"role": "user", "content": prompt}

            if file_type in ["jpg", "jpeg", "png"]:
                user_msg["image"] = uploaded_file

            messages.append(user_msg)
            
            with st.chat_message("user"):
                if file_type in ["jpg", "jpeg", "png"]:
                    st.image(uploaded_file, caption="الصورة المرفقة", width=250)
                elif file_type in ["pdf", "txt"]:
                    st.info(f"📄 تم إرفاق المستند: {uploaded_file.name}")
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("TOMA يفكر..."):
                    # 1. إذا كان الملف صورة
                    if file_type in ["jpg", "jpeg", "png"]:
                        base64_img = encode_image(uploaded_file)
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
                    
                    # 2. إذا كان الملف PDF أو TXT
                    elif file_type in ["pdf", "txt"]:
                        if file_type == "pdf":
                            doc_text = extract_text_from_pdf(uploaded_file)
                        else:
                            doc_text = uploaded_file.getvalue().decode("utf-8")

                        augmented_prompt = f"المستند المرفق:\n\"\"\"\n{doc_text[:12000]}\n\"\"\"\n\nبناءً على المستند أعلاه، إجابة السؤال التالي:\n{prompt}"
                        
                        groq_messages = [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": augmented_prompt}
                        ]
                        completion = client.chat.completions.create(
                            model=model_choice,
                            messages=groq_messages,
                            temperature=0.5,
                        )

                    # 3. محادثة نصية عادية
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
        st.error(f"حدث خطأ في الاتصال: {e}")
else:
    st.info("👋 أهلاً بك في تطبيق **TOMA CHAT Pro**! أدخل مفتاح Groq API Key في الشريط الجانبي لبدء استخدام كافة الميزات المتقدمة.")
