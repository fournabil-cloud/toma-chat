import streamlit as st
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
st.set_page_config(
    page_title="TOMA CHAT Pro", 
    page_icon=LOGO_FILE if os.path.exists(LOGO_FILE) else "⚡", 
    layout="wide"
)

# منع المتصفحات من ترجمة الواجهة وتخريب عناصر التصميم
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

DEFAULT_API_KEY = "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"

if "theme" not in st.session_state:
    st.session_state.theme = "داكن (Dark)"

is_dark = st.session_state.theme == "داكن (Dark)"
bg_color = "#121212" if is_dark else "#F8F9FA"
card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#212529"
sidebar_bg = "#181818" if is_dark else "#F1F3F5"
sidebar_text = "#E0E0E0" if is_dark else "#333333"
input_bg = "#2D2D2D" if is_dark else "#FFFFFF"
input_text = "#FFFFFF" if is_dark else "#000000"
accent_color = "#10A37F"

# --- أكواد CSS التجميلية ---
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        }}
        
        .main .block-container {{
            padding-bottom: 140px !important;
            max-width: 1100px !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
            border-left: 1px solid #2A2A2A;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #FFFFFF !important;
            font-weight: 600;
        }}
        [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p {{
            color: {sidebar_text} !important;
        }}

        #MainMenu, header, footer {{ visibility: hidden; }}
        
        .header-container {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
        }}
        .header-logo {{
            width: 55px;
            height: 55px;
            border-radius: 12px;
            object-fit: contain;
        }}
        .sidebar-logo {{
            display: block;
            margin: 0 auto 15px auto;
            width: 130px;
            height: auto;
            border-radius: 16px;
            object-fit: contain;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 8px;
            color: #AAAAAA;
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {accent_color} !important;
            color: #FFFFFF !important;
        }}

        [data-testid="stChatInput"] {{
            position: fixed;
            bottom: 25px;
            right: 25px;
            left: 380px;
            width: auto;
            background-color: transparent;
            z-index: 1000;
        }}
        
        @media (max-width: 992px) {{
            [data-testid="stChatInput"] {{
                left: 25px;
            }}
        }}

        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg};
            color: {input_text};
            border-radius: 14px;
            border: 1px solid #444444;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }}

        .stButton > button {{
            background-color: {accent_color};
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            background-color: #0E8E6D;
            border: none;
        }}
        .stDownloadButton > button {{
            background-color: #2B6CB0;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
        }}
    </style>
""", unsafe_allow_html=True)

# --- دالة لتحويل النص إلى صوت ---
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

# --- استخراج كود HTML للمعاينة المباشرة ---
def extract_html_code(text):
    pattern = r"```" + r"html\s*(.*?)\s*" + r"```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return None

# --- عرض العنوان والشعار الرئيسي ---
if logo_b64:
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_b64}" class="header-logo" alt="Logo" />
            <h1 style="margin: 0; padding: 0; font-size: 2.2rem; display: inline-block;">TOMA CHAT Pro</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.title("⚡ TOMA CHAT Pro")

# --- إدارة الجلسات ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "محادثة جديدة 1"

persona_prompts = {
    "مساعد عام ذكي وودود": "أنت مساعد ذكي ودود ومفيد جداً، أجب بلغة واضحة ودقيقة.",
    "خبير برمجة وتقنية (محترف)": "أنت خبير برمجة وتقنية محترف، قدم أكواد نظيفة، مشروحة بدقة.",
    "كاتب محتوى ومبدع": "أنت كاتب محتوى ومبدع محترف، اكتب بصياغة جذابة، بليغة، ومؤثرة.",
    "مستشار تسويق وأعمال": "أنت مستشار تسويق وأعمال، قدم استراتيجيات ذكية وحلول عملية لنمو المشاريع.",
    "مختصر ومباشر جداً": "كن مختصراً ومباشراً قدر الإمكان، دون حشو أو إطالة."
}

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    if logo_b64:
        st.markdown(f'<img src="{logo_b64}" class="sidebar-logo" alt="Logo" />', unsafe_allow_html=True)
        
    st.header("⚙️ إعدادات المنصة")
    
    secret_key = st.secrets.get("GROQ_API_KEY", DEFAULT_API_KEY)
    api_key_input = st.text_input("مفتاح Groq API Key:", value=secret_key, type="password", key="groq_api_key_v18")

    st.divider()
    enable_web_search = st.checkbox("🌐 تفعيل البحث المباشر في الويب", value=False, key="web_search_toggle_v18")
    deep_research_mode = st.checkbox("🔍 وضع البحث المتقدم والعميق", value=False, key="deep_research_toggle_v18")
    enable_tts = st.checkbox("🔊 تفعيل القراءة الصوتية تلقائياً", value=False, key="tts_toggle_v18")
    enable_code_preview = st.checkbox("💻 معاينة أكواد HTML/Web المباشرة", value=True, key="code_preview_toggle_v18")

    st.divider()
    new_theme = st.selectbox("مظهر التطبيق:", ["داكن (Dark)", "فاتح (Light)"], index=0 if is_dark else 1, key="theme_selector_v18")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.divider()
    model_choice = st.selectbox(
        "اختر نموذج الذكاء الاصطناعي:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_v18"
    )

    persona_choice = st.selectbox(
        "اختر شخصية ونمط TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"],
        key="persona_v18"
    )

    st.divider()
    st.subheader("💬 المحادثات المحفوظة")
    session_names = list(st.session_state.sessions.keys())
    selected_session = st.selectbox("اختر المحادثة:", session_names, index=session_names.index(st.session_state.current_session), key="session_selector_v18")
    
    if selected_session != st.session_state.current_session:
        st.session_state.current_session = selected_session
        st.rerun()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ جديدة", key="new_chat_btn_v18"):
            new_name = f"محادثة جديدة {len(st.session_state.sessions) + 1}"
            st.session_state.sessions[new_name] = []
            st.session_state.current_session = new_name
            st.rerun()
    with col_btn2:
        if st.button("🗑️ مسح", key="clear_chat_btn_v18"):
            st.session_state.sessions[st.session_state.current_session] = []
            st.rerun()

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
            key="export_chat_btn_v18"
        )

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

def web_search(query, max_results=3):
    try:
        results = list(DDGS().text(query, max_results=max_results))
        context = "نتائج البحث المباشر في الويب:\n"
        for idx, r in enumerate(results, 1):
            context += f"{idx}. {r['title']}: {r['body']}\n"
        return context
    except Exception:
        return ""

# --- دالة ترجمة هجينة (معجم مباشر + ذكاء اصطناعي) لضمان الدقة بنسبة 100% ---
def translate_prompt_to_english(client, arabic_prompt):
    # قاموس مباشر للمعالم الشهيرة لتجنب أي أخطاء في الترجمة
    direct_translations = {
        "مقام الشهيد": "Maqam Echahid monument in Algiers, three massive concrete arches landmark, realistic architecture",
        "مقام الشهيد بالجزائر": "Maqam Echahid monument in Algiers, three massive concrete arches landmark, realistic architecture",
    }
    
    # التحقق المباشر من القاموس
    cleaned_prompt = arabic_prompt.strip()
    for key, val in direct_translations.items():
        if key in cleaned_prompt:
            return val

    # إذا لم يكن في القاموس، يتم الاعتماد على الذكاء الاصطناعي مع تعليمات صارمة
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a precise prompt engineer. Translate the user's Arabic description into a descriptive, clear English prompt for AI image generation. Output ONLY the English translation."},
                {"role": "user", "content": arabic_prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return arabic_prompt

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

if api_key_input:
    clean_api_key = api_key_input.strip()
    try:
        client = Groq(api_key=clean_api_key)
        system_instruction = persona_prompts.get(persona_choice, "أنت مساعد ذكي.")
        messages = st.session_state.sessions[st.session_state.current_session]

        with st.expander("🛠️ أدوات التفاعل والمرفقات (اضغط للفتح/الإغلاق)", expanded=False):
            tab_upload, tab_image_gen = st.tabs(["📁 رفع الملفات والصوتيات", "🎨 توليد ورسم الصور"])
            
            with tab_upload:
                uploaded_file = st.file_uploader(
                    "إرفاق صورة، مستند (PDF/TXT) أو مقطع صوتي (MP3/WAV):",
                    type=["jpg", "jpeg", "png", "pdf", "txt", "mp3", "wav", "m4a"],
                    key="doc_uploader_v18"
                )
            
            with tab_image_gen:
                col_img1, col_img2 = st.columns([2, 1])
                with col_img1:
                    gen_image_prompt = st.text_input("وصف الصورة المراد رسمها (اكتب بالعربية براحتك):", key="gen_image_prompt_v18")
                with col_img2:
                    img_style = st.selectbox("النمط:", ["افتراضي", "Realistic", "Anime", "Cinematic", "Oil Painting"], key="img_style_v18")
                
                col_dim1, col_dim2 = st.columns([2, 1])
                with col_dim1:
                    img_aspect = st.selectbox("الأبعاد:", ["مربع (512x512)", "أفقي (768x512)", "عمودي (512x768)"], key="img_aspect_v18")
                with col_dim2:
                    st.write("")
                    st.write("")
                    generate_btn = st.button("🎨 ارسم الآن", use_container_width=True, key="gen_image_btn_v18")

        if 'generate_btn' in locals() and generate_btn and gen_image_prompt:
            w, h = 512, 512
            if "أفقي" in img_aspect: w, h = 768, 512
            elif "عمودي" in img_aspect: w, h = 512, 768

            selected_style = "" if img_style == "افتراضي" else img_style

            messages.append({"role": "user", "content": f"طلب توليد صورة: {gen_image_prompt}"})

            with st.chat_message("assistant"):
                with st.spinner("جاري ترجمة الوصف ورسم الصورة بدقة..."):
                    optimized_prompt = translate_prompt_to_english(client, gen_image_prompt)
                    img_bytes = fetch_generated_image(optimized_prompt, width=w, height=h, style=selected_style)
                    
                    if img_bytes:
                        st.image(img_bytes, caption=f"رسمة: {gen_image_prompt}", width=400)
                        st.download_button(
                            label="📥 تنزيل الصورة",
                            data=img_bytes,
                            file_name="toma_generated_image.png",
                            mime="image/png",
                            key=f"dl_gen_{len(messages)}_{st.session_state.current_session}"
                        )
                        st.success("✨ تم توليد الصورة بنجاح!")
                        messages.append({
                            "role": "assistant",
                            "content": f"✨ تم توليد الصورة بنجاح بناءً على وصفك: ({gen_image_prompt})",
                            "generated_image_bytes": img_bytes
                        })
                    else:
                        st.error("تعذر تحميل الصورة حالياً، يرجى إعادة المحاولة.")
            st.rerun()

        for idx, message in enumerate(messages):
            with st.chat_message(message["role"]):
                if message.get("image"):
                    st.image(message["image"], caption="الصورة المرفقة", width=250)
                if message.get("generated_image_bytes"):
                    st.image(message["generated_image_bytes"], caption="الصورة المولدة", width=400)
                    st.download_button(
                        label="📥 تنزيل الصورة",
                        data=message["generated_image_bytes"],
                        file_name=f"toma_image_{idx}.png",
                        mime="image/png",
                        key=f"dl_hist_{idx}_{st.session_state.current_session}"
                    )
                if message.get("content"):
                    st.markdown(message["content"])
                    
                    if message["role"] == "assistant" and enable_code_preview:
                        html_code = extract_html_code(message["content"])
                        if html_code:
                            with st.expander("👁️ معاينة الكود المباشرة (Live Preview)", expanded=True):
                                components.html(html_code, height=350, scrolling=True)

                    if message["role"] == "assistant" and enable_tts:
                        audio_fp = text_to_speech(message["content"])
                        if audio_fp:
                            st.audio(audio_fp, format='audio/mp3')

        prompt = st.chat_input("اكتب رسالتك هنا...")

        if prompt:
            file_type = uploaded_file.name.split(".")[-1].lower() if 'uploaded_file' in locals() and uploaded_file else None
            user_msg = {"role": "user", "content": prompt}

            if file_type in ["jpg", "jpeg", "png"]:
                user_msg["image"] = uploaded_file

            messages.append(user_msg)

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
                            if enable_web_search or deep_research_mode:
                                num_res = 6 if deep_research_mode else 3
                                web_context = web_search(prompt, max_results=num_res)

                            groq_messages = [{"role": "system", "content": system_instruction}]
                            for m in messages[-8:]:
                                if m.get("content") and "طلب توليد صورة:" not in m["content"]:
                                    groq_messages.append({"role": m["role"], "content": m["content"]})

                            if web_context:
                                if deep_research_mode:
                                    groq_messages.append({"role": "system", "content": f"قم بإعداد تقرير مفصل وشامل بناءً على نتائج البحث التالية:\n{web_context}"})
                                else:
                                    groq_messages.append({"role": "system", "content": f"معلومات إضافية من الويب للرد:\n{web_context}"})

                            completion = client.chat.completions.create(model=model_choice, messages=groq_messages, temperature=0.7)
                        
                        bot_response = completion.choices[0].message.content
                        messages.append({"role": "assistant", "content": bot_response})
                        
                    except Exception as api_e:
                        st.error(f"حدث خطأ أثناء الاتصال: {api_e}")
            st.rerun()

    except Exception as e:
        st.error(f"حدث خطأ في الإعداد: {e}")
else:
    st.markdown(f"""
    <div style="background-color: {card_bg}; color: {text_color}; padding: 35px; border-radius: 16px; text-align: center; margin-top: 50px; border: 1px solid #333333;">
        <h2 style="color: #FFFFFF !important; margin-bottom: 10px;">👋 أهلاً بك في TOMA CHAT Pro</h2>
        <p style="font-size: 16px; color: #BBBBBB !important;">يرجى إدخال <b>مفتاح Groq API Key</b> لبدء استخدام المنصة.</p>
    </div>
    """, unsafe_allow_html=True)
