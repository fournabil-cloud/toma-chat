import streamlit as st
from groq import Groq
from PIL import Image
import urllib.parse
import requests
from io import BytesIO
import base64
from pypdf import PdfReader
from duckduckgo_search import DDGS

# -- إعداد الصفحة --
st.set_page_config(page_title="TOMA CHAT Pro", page_icon="⚡", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "داكن (Dark)"

is_dark = st.session_state.theme == "داكن (Dark)"
bg_color = "#212121" if is_dark else "#F9F9F9"
text_color = "#FFFFFF" if is_dark else "#111111"
sidebar_bg = "#171717" if is_dark else "#EDEDED"
sidebar_text = "#F0F0F0" if is_dark else "#202020"
chat_bg = "#343541" if is_dark else "#E5E5EA"
input_bg = "#2F2F2F" if is_dark else "#FFFFFF"
input_text = "#FFFFFF" if is_dark else "#000000"

# --- أكواد CSS المحسنة لإصلاح حجب العناصر وحل مشكلة الشريط السفلي ---
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* إضافة مساحة سفليّة كافية لمنع التغطية على المحتوى */
        .main .block-container {{
            padding-bottom: 120px !important;
        }}

        .main div[data-testid="stWidgetLabel"] p {{
            color: #FFFFFF !important;
            font-size: 15px !important;
            font-weight: 600 !important;
        }}
        .main div[data-testid="stFileUploadDropzone"] div p {{
            color: #E0E0E0 !important;
            font-size: 13px !important;
        }}
        .main h3[data-testid="stHeader"] {{
            color: #FFFFFF !important;
            font-size: 22px !important;
        }}
        
        /* القائمة الجانبية (Sidebar) */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
            color: {sidebar_text};
            border-left: 1px solid #303030;
            z-index: 99999 !important; /* لضمان عدم حجب القائمة الجانبية إطلاقاً */
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #FFFFFF !important;
        }}
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {{
            color: #E0E0E0 !important;
        }}
        
        /* تصحيح تموضع شارات وإدخال المحادثة السفلي كي لا يغطي القائمة الجانبية */
        #MainMenu, header, footer {{ visibility: hidden; }}
        
        [data-testid="stChatInput"] {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            left: 360px; /* الابتعاد عن الشريط الجانبي */
            width: auto;
            background-color: transparent;
            z-index: 1000;
        }}
        
        @media (max-width: 768px) {{
            [data-testid="stChatInput"] {{
                left: 20px;
            }}
        }}

        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg};
            color: {input_text};
            border-radius: 12px;
            border: 1px solid #454545;
        }}
        .stButton > button {{
            background-color: #19C37D;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }}
        .stDownloadButton > button {{
            background-color: #007ACC;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ TOMA CHAT Pro")

# --- إدارة الجلسات ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "محادثة جديدة 1"

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("⚙️ إعدادات TOMA")
    api_key_input = st.text_input("أدخل مفتاح Groq API Key:", type="password", key="groq_api_key_v5")

    st.divider()
    enable_web_search = st.checkbox("🌐 تفعيل البحث المباشر في الويب", value=False, key="web_search_toggle")

    st.divider()
    new_theme = st.selectbox("مظهر التطبيق:", ["داكن (Dark)", "فاتح (Light)"], index=0 if is_dark else 1, key="theme_selector_v5")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.divider()
    st.subheader("💬 المحادثات المحفوظة")
    session_names = list(st.session_state.sessions.keys())
    selected_session = st.selectbox("اختر المحادثة:", session_names, index=session_names.index(st.session_state.current_session), key="session_selector_v5")
    
    if selected_session != st.session_state.current_session:
        st.session_state.current_session = selected_session
        st.rerun()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ جديدة", key="new_chat_btn_v5"):
            new_name = f"محادثة جديدة {len(st.session_state.sessions) + 1}"
            st.session_state.sessions[new_name] = []
            st.session_state.current_session = new_name
            st.rerun()
    with col_btn2:
        if st.button("🗑️ مسح", key="clear_chat_btn_v5"):
            st.session_state.sessions[st.session_state.current_session] = []
            st.rerun()

    # تصدير المحادثة النصية
    current_chat_data = st.session_state.sessions[st.session_state.current_session]
    chat_text_export = ""
    for msg in current_chat_data:
        if msg.get("content"):
            role_label = "المستخدم" if msg["role"] == "user" else "TOMA"
            chat_text_export += f"{role_label}: {msg['content']}\n\n"
    
    if chat_text_export:
        st.download_button(
            label="📄 تصدير المحادثة (TXT)",
            data=chat_text_export,
            file_name=f"{st.session_state.current_session}.txt",
            mime="text/plain",
            key="export_chat_btn_v5"
        )

    st.divider()
    model_choice = st.selectbox(
        "اختر نموذج الذكاء الاصطناعي:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_v5"
    )

    persona_choice = st.selectbox(
        "اختر شخصية ونمط TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"],
        key="persona_v5"
    )

# --- تعريف الشخصيات ---
persona_prompts = {
    "مساعد عام ذكي وودود": "أنت مساعد ذكي ودود ومفيد جداً، أجب بلغة واضحة ودقيقة.",
    "خبير برمجة وتقنية (محترف)": "أنت خبير برمجة وتقنية محترف، قدم أكواد نظيفة، مشروحة بدقة.",
    "كاتب محتوى ومبدع": "أنت كاتب محتوى ومبدع محترف، اكتب بصياغة جذابة، بليغة، ومؤثرة.",
    "مستشار تسويق وأعمال": "أنت مستشار تسويق وأعمال، قدم استراتيجيات ذكية وحلول عملية لنمو المشاريع.",
    "مختصر ومباشر جداً": "كن مختصراً ومباشراً قدر الإمكان، دون حشو أو إطالة."
}

# --- وظائف مساعدة ---
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

def web_search(query):
    try:
        results = list(DDGS().text(query, max_results=3))
        context = "نتائج البحث المباشر في الويب:\n"
        for idx, r in enumerate(results, 1):
            context += f"{idx}. {r['title']}: {r['body']}\n"
        return context
    except Exception:
        return ""

def fetch_generated_image(prompt, width=512, height=512, style=""):
    full_prompt = f"{prompt}, {style}" if style else prompt
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.content
    except Exception:
        return None
    return None

# --- المنطق الأساسي ---
if api_key_input:
    clean_api_key = api_key_input.strip()
    try:
        client = Groq(api_key=clean_api_key)
        system_instruction = persona_prompts.get(persona_choice, "أنت مساعد ذكي.")
        messages = st.session_state.sessions[st.session_state.current_session]

        # عرض تاريخ الشات
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

        # --- أدوات المرفقات والتفاعل ---
        st.subheader("📁 أدوات التفاعل والمرفقات:")
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("📷/📄/🎙️ رفع صورة، مستند (PDF/TXT) أو صوت (MP3/WAV):", type=["jpg", "jpeg", "png", "pdf", "txt", "mp3", "wav", "m4a"], key="doc_uploader_v5")
        with col2:
            gen_image_prompt = st.text_input("🖌️ وصف الصورة المراد رسمها:", key="gen_image_prompt_v5")
            img_style = st.selectbox("نمط الرسم:", ["افتراضي", "واقعي Realistic", "أنيمي Anime", "سينمائي Cinematic", "رسم زيتي Oil Painting"], key="img_style_v5")
            img_aspect = st.selectbox("أبعاد الصورة:", ["مربع (512x512)", "أفقي (768x512)", "عمودي/ستوري (512x768)"], key="img_aspect_v5")
            generate_btn = st.button("🎨 ارسم الصورة", key="gen_image_btn_v5")

        # معالجة رسم الصورة
        if generate_btn and gen_image_prompt:
            w, h = 512, 512
            if "أفقي" in img_aspect: w, h = 768, 512
            elif "عمودي" in img_aspect: w, h = 512, 768

            selected_style = "" if img_style == "افتراضي" else img_style

            with st.chat_message("user"):
                st.markdown(f"**طلب توليد صورة:** {gen_image_prompt}")
            messages.append({"role": "user", "content": f"طلب توليد صورة: {gen_image_prompt}"})

            with st.chat_message("assistant"):
                with st.spinner("جاري جلب ورسم الصورة..."):
                    img_bytes = fetch_generated_image(gen_image_prompt, width=w, height=h, style=selected_style)
                    if img_bytes:
                        st.image(img_bytes, caption=f"رسمة: {gen_image_prompt}", width=400)
                        st.download_button(
                            label="📥 تنزيل الصورة",
                            data=img_bytes,
                            file_name="toma_image.png",
                            mime="image/png",
                            key=f"dl_new_{hash(gen_image_prompt)}"
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

        # --- خانة إدخال الرسالة ---
        prompt = st.chat_input("اكتب رسالتك هنا...")

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
                elif file_type in ["mp3", "wav", "m4a"]:
                    st.info(f"🎙️ تم إرفاق الملف الصوتي: {uploaded_file.name}")
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("TOMA يفكر..."):
                    try:
                        if file_type in ["mp3", "wav", "m4a"]:
                            transcription = client.audio.transcriptions.create(
                                file=(uploaded_file.name, uploaded_file.getvalue()),
                                model="whisper-large-v3-turbo"
                            )
                            audio_text = transcription.text
                            augmented_prompt = f"النص المستخرج من الصوت المرفق:\n\"\"\"\n{audio_text}\n\"\"\"\n\nطلب المستخدم حوله:\n{prompt}"
                            groq_messages = [{"role": "system", "content": system_instruction}, {"role": "user", "content": augmented_prompt}]
                            completion = client.chat.completions.create(model=model_choice, messages=groq_messages, temperature=0.5)

                        elif file_type in ["jpg", "jpeg", "png"]:
                            base64_img = encode_image(uploaded_file)
                            vision_messages = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
                            completion = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=vision_messages)

                        elif file_type in ["pdf", "txt"]:
                            if file_type == "pdf": doc_text = extract_text_from_pdf(uploaded_file)
                            else: doc_text = uploaded_file.getvalue().decode("utf-8")
                            augmented_prompt = f"المستند المرفق:\n\"\"\"\n{doc_text[:15000]}\n\"\"\"\n\nبناءً على المستند أعلاه، إجابة السؤال التالي:\n{prompt}"
                            groq_messages = [{"role": "system", "content": system_instruction}, {"role": "user", "content": augmented_prompt}]
                            completion = client.chat.completions.create(model=model_choice, messages=groq_messages, temperature=0.5)

                        else:
                            web_context = ""
                            if enable_web_search:
                                web_context = web_search(prompt)

                            groq_messages = [{"role": "system", "content": system_instruction}]
                            for m in messages[-8:]:
                                if m.get("content") and "طلب توليد صورة:" not in m["content"]:
                                    groq_messages.append({"role": m["role"], "content": m["content"]})

                            if web_context:
                                groq_messages.append({"role": "system", "content": f"معلومات إضافية من الويب للرد:\n{web_context}"})

                            completion = client.chat.completions.create(model=model_choice, messages=groq_messages, temperature=0.7)
                        
                        bot_response = completion.choices[0].message.content
                        st.markdown(bot_response)
                        messages.append({"role": "assistant", "content": bot_response})
                        
                    except Exception as api_e:
                        st.error(f"حدث خطأ أثناء الاتصال: {api_e}")
            st.rerun()

    except Exception as e:
        st.error(f"حدث خطأ في الإعداد: {e}")
else:
    st.markdown(f"""
    <div style="background-color: {chat_bg}; color: {text_color}; padding: 30px; border-radius: 15px; text-align: center; margin-top: 50px; border: 1px solid #454545;">
        <h2 style="color: #FFFFFF !important;">👋 أهلاً بك في TOMA CHAT Pro!</h2>
        <p style="font-size: 18px; margin-top: 15px; color: #E0E0E0 !important;">لبدء استخدام التطبيق المطور، أدخل <b>مفتاح Groq API Key</b> الخاص بك في الشريط الجانبي.</p>
    </div>
    """, unsafe_allow_html=True)
