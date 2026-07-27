import streamlit as str_app
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
str_app.set_page_config(
    page_title="TOMA CHAT Pro", 
    page_icon=LOGO_FILE if os.path.exists(LOGO_FILE) else "⚡", 
    layout="wide"
)

# حقن مكتبة FontAwesome للأيقونات الاحترافية ومنع الترجمة التلقائية للمتصفح
str_app.markdown("""
    <meta name="google" content="notranslate">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)

DEFAULT_API_KEY = "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"

if "theme" not in str_app.session_state:
    str_app.session_state.theme = "داكن (Dark)"

is_dark = str_app.session_state.theme == "داكن (Dark)"

# تثبيت ألوان مستقرة ومريحة للعين تمنع أي شاشة سوداء أو تداخل في العناصر
bg_color = "#121212" if is_dark else "#FFFFFF"
card_bg = "#1E1E1E" if is_dark else "#F8F9FA"
text_color = "#FFFFFF" if is_dark else "#212529"
sidebar_bg = "#181818" if is_dark else "#F1F3F5"
sidebar_text = "#E0E0E0" if is_dark else "#333333"
input_bg = "#2D2D2D" if is_dark else "#FFFFFF"
input_text = "#FFFFFF" if is_dark else "#000000"
accent_color = "#10A37F"

# --- أكواد CSS والتنسيقات الاحترافية المستقرة ---
str_app.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        }}
        
        .main .block-container {{
            padding-bottom: 140px !important;
            max-width: 1100px !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-left: 1px solid #2A2A2A;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {text_color} !important;
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
            background-color: {input_bg} !important;
            color: {input_text} !important;
            border-radius: 14px;
            border: 1px solid #444444;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }}

        .stButton > button {{
            background-color: {accent_color} !important;
            color: white !important;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            background-color: #0E8E6D !important;
            border: none;
        }}
        .stDownloadButton > button {{
            background-color: #2B6CB0 !important;
            color: white !important;
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
    str_app.markdown(f"""
        <div class="header-container">
            <img src="{logo_b64}" class="header-logo" alt="Logo" />
            <h1 style="margin: 0; padding: 0; font-size: 2.2rem; display: inline-block;">TOMA CHAT Pro</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    str_app.title("⚡ TOMA CHAT Pro")

# --- إدارة الجلسات ---
if "sessions" not in str_app.session_state:
    str_app.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in str_app.session_state:
    str_app.session_state.current_session = "محادثة جديدة 1"

persona_prompts = {
    "مساعد عام ذكي وودود": "أنت مساعد ذكي ودود ومفيد جداً، أجب بلغة واضحة ودقيقة.",
    "خبير برمجة وتقنية (محترف)": "أنت خبير برمجة وتقنية محترف، قدم أكواد نظيفة، مشروحة بدقة.",
    "كاتب محتوى ومبدع": "أنت كاتب محتوى ومبدع محترف، اكتب بصياغة جذابة، بليغة، ومؤثرة.",
    "مستشار تسويق وأعمال": "أنت مستشار تسويق وأعمال، قدم استراتيجيات ذكية وحلول عملية لنمو المشاريع.",
    "مختصر ومباشر جداً": "كن مختصراً ومباشراً قدر الإمكان، دون حشو أو إطالة."
}

# --- القائمة الجانبية (Sidebar) ---
with str_app.sidebar:
    if logo_b64:
        str_app.markdown(f'<img src="{logo_b64}" class="sidebar-logo" alt="Logo" />', unsafe_allow_html=True)
        
    str_app.markdown("### <i class='fa-solid fa-sliders'></i> إعدادات المنصة", unsafe_allow_html=True)
    
    secret_key = str_app.secrets.get("GROQ_API_KEY", DEFAULT_API_KEY)
    api_key_input = str_app.text_input("مفتاح Groq API Key:", value=secret_key, type="password", key="groq_api_key_v21")

    str_app.divider()
    enable_web_search = str_app.checkbox("🌐 تفعيل البحث المباشر في الويب", value=False, key="web_search_toggle_v21")
    deep_research_mode = str_app.checkbox("🔍 وضع البحث المتقدم والعميق", value=False, key="deep_research_toggle_v21")
    enable_tts = str_app.checkbox("🔊 تفعيل القراءة الصوتية تلقائياً", value=False, key="tts_toggle_v21")
    enable_code_preview = str_app.checkbox("💻 معاينة أكواد HTML/Web المباشرة", value=True, key="code_preview_toggle_v21")

    str_app.divider()
    new_theme = str_app.selectbox("🎨 مظهر التطبيق:", ["داكن (Dark)", "فاتح (Light)"], index=0 if is_dark else 1, key="theme_selector_v21")
    if new_theme != str_app.session_state.theme:
        str_app.session_state.theme = new_theme
        str_app.rerun()

    str_app.divider()
    model_choice = str_app.selectbox(
        "🧠 اختر نموذج الذكاء الاصطناعي:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_v21"
    )

    persona_choice = str_app.selectbox(
        "🎭 اختر شخصية ونمط TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"],
        key="persona_v21"
    )

    str_app.divider()
    str_app.markdown("### <i class='fa-solid fa-comments'></i> المحادثات المحفوظة", unsafe_allow_html=True)
    session_names = list(str_app.session_state.sessions.keys())
    selected_session = str_app.selectbox("اختر المحادثة:", session_names, index=session_names.index(str_app.session_state.current_session), key="session_selector_v21")
    
    if selected_session != str_app.session_state.current_session:
        str_app.session_state.current_session = selected_session
        str_app.rerun()

    col_btn1, col_btn2 = str_app.columns(2)
    with col_btn1:
        if str_app.button("➕ جديدة", key="new_chat_btn_v21"):
            new_name = f"محادثة جديدة {len(str_app.session_state.sessions) + 1}"
            str_app.session_state.sessions[new_name] = []
            str_app.session_state.current_session = new_name
            str_app.rerun()
    with col_btn2:
        if str_app.button("🗑️ مسح", key="clear_chat_btn_v21"):
            str_app.session_state.sessions[str_app.session_state.current_session] = []
            str_app.rerun()

    current_chat_data = str_app.session_state.sessions[str_app.session_state.current_session]
    chat_text_export = ""
    for msg in current_chat_data:
        if msg.get("content"):
            role_label = "المستخدم" if msg["role"] == "user" else "TOMA"
            chat_text_export += f"{role_label}: {msg['content']}\n\n"
    
    if chat_text_export:
        str_app.download_button(
            label="📄 تصدير المحادثة (TXT)",
            data=chat_text_export,
            file_name=f"{str_app.session_state.current_session}.txt",
            mime="text/plain",
            key="export_chat_btn_v21"
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

def translate_prompt_to_english(client, arabic_prompt):
    direct_translations = {
        "مقام الشهيد": "Maqam Echahid monument Algiers, three concrete palm-frond shaped massive arches, clear sky, highly detailed architectural photography",
        "مقام الشهيد بالجزائر": "Maqam Echahid monument Algiers, three concrete palm-frond shaped massive arches, clear sky, highly detailed architectural photography",
        "جزائر": "Algiers city landscape, Mediterranean coast, white buildings, beautiful architecture",
        "مسجد": "Islamic mosque architecture, beautiful minaret and dome, detailed exterior",
    }
    
    cleaned_prompt = arabic_prompt.strip()
    for key, val in direct_translations.items():
        if key in cleaned_prompt:
            return val

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional visual prompt engineer for image generation. Translate the user's Arabic request into a clear, direct, highly accurate English visual prompt. Avoid abstract words, focus purely on physical appearance, subject, lighting, and style. Output ONLY the final English prompt string."},
                {"role": "user", "content": arabic_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return arabic_prompt

def fetch_generated_image(prompt, width=512, height=512, style=""):
    quality_modifiers = "masterpiece, highly detailed, sharp focus, professional photography"
    full_prompt = f"{prompt}, {style}, {quality_modifiers}" if style else f"{prompt}, {quality_modifiers}"
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=20)
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
        messages = str_app.session_state.sessions[str_app.session_state.current_session]

        with str_app.expander("🛠️ لوحة الأدوات والمرفقات الذكية", expanded=False):
            tab_upload, tab_image_gen = str_app.tabs(["📁 رفع الملفات والمستندات والصوتيات", "🎨 توليد ورسم الصور الاحترافية"])
            
            with tab_upload:
                uploaded_file = str_app.file_uploader(
                    "إرفاق صورة، مستند (PDF/TXT) أو مقطع صوتي (MP3/WAV):",
                    type=["jpg", "jpeg", "png", "pdf", "txt", "mp3", "wav", "m4a"],
                    key="doc_uploader_v21"
                )
            
            with tab_image_gen:
                col_img1, col_img2 = str_app.columns([2, 1])
                with col_img1:
                    gen_image_prompt = str_app.text_input("وصف الصورة المراد رسمها (اكتب بالعربية براحتك):", key="gen_image_prompt_v21")
                with col_img2:
                    img_style = str_app.selectbox("النمط الفني:", ["افتراضي", "Realistic", "Anime", "Cinematic", "Oil Painting"], key="img_style_v21")
                
                col_dim1, col_dim2 = str_app.columns([2, 1])
                with col_dim1:
                    img_aspect = str_app.selectbox("أبعاد الصورة:", ["مربع (512x512)", "أفقي (768x512)", "عمودي (512x768)"], key="img_aspect_v21")
                with col_dim2:
                    str_app.write("")
                    str_app.write("")
                    generate_btn = str_app.button("🎨 ارسم الآن", use_container_width=True, key="gen_image_btn_v21")

        if 'generate_btn' in locals() and generate_btn and gen_image_prompt:
            w, h = 512, 512
            if "أفقي" in img_aspect: w, h = 768, 512
            elif "عمودي" in img_aspect: w, h = 512, 768

            selected_style = "" if img_style == "افتراضي" else img_style

            messages.append({"role": "user", "content": f"طلب توليد صورة: {gen_image_prompt}"})

            with str_app.chat_message("assistant"):
                with str_app.spinner("جاري معالجة الوصف وضبط دقة الرسم..."):
                    optimized_prompt = translate_prompt_to_english(client, gen_image_prompt)
                    img_bytes = fetch_generated_image(optimized_prompt, width=w, height=h, style=selected_style)
                    
                    if img_bytes:
                        str_app.image(img_bytes, caption=f"رسمة: {gen_image_prompt}", width=400)
                        str_app.download_button(
                            label="📥 تنزيل الصورة",
                            data=img_bytes,
                            file_name="toma_generated_image.png",
                            mime="image/png",
                            key=f"dl_gen_{len(messages)}_{str_app.session_state.current_session}"
                        )
                        str_app.success("✨ تم توليد الصورة بدقة عالية بنجاح!")
                        messages.append({
                            "role": "assistant",
                            "content": f"✨ تم توليد الصورة بنجاح بناءً على وصفك: ({gen_image_prompt})",
                            "generated_image_bytes": img_bytes
                        })
                    else:
                        str_app.error("تعذر تحميل الصورة حالياً، يرجى إعادة المحاولة.")
            str_app.rerun()

        for idx, message in enumerate(messages):
            with str_app.chat_message(message["role"]):
                if message.get("image"):
                    str_app.image(message["image"], caption="الصورة المرفقة", width=250)
                if message.get("generated_image_bytes"):
                    str_app.image(message["generated_image_bytes"], caption="الصورة المولدة", width=400)
                    str_app.download_button(
                        label="📥 تنزيل الصورة",
                        data=message["generated_image_bytes"],
                        file_name=f"toma_image_{idx}.png",
                        mime="image/png",
                        key=f"dl_hist_{idx}_{str_app.session_state.current_session}"
                    )
                if message.get("content"):
                    str_app.markdown(message["content"])
                    
                    if message["role"] == "assistant" and enable_code_preview:
                        html_code = extract_html_code(message["content"])
                        if html_code:
                            with str_app.expander("👁️ معاينة الكود المباشرة (Live Preview)", expanded=True):
                                components.html(html_code, height=350, scrolling=True)

                    if message["role"] == "assistant" and enable_tts:
                        audio_fp = text_to_speech(message["content"])
                        if audio_fp:
                            str_app.audio(audio_fp, format='audio/mp3')

        prompt = str_app.chat_input("اكتب رسالتك هنا...")

        if prompt:
            file_type = uploaded_file.name.split(".")[-1].lower() if 'uploaded_file' in locals() and uploaded_file else None
            user_msg = {"role": "user", "content": prompt}

            if file_type in ["jpg", "jpeg", "png"]:
                user_msg["image"] = uploaded_file

            messages.append(user_msg)

            with str_app.chat_message("assistant"):
                with str_app.spinner("TOMA يفكر..."):
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
                        str_app.error(f"حدث خطأ أثناء الاتصال: {api_e}")
            str_app.rerun()

    except Exception as e:
        str_app.error(f"حدث خطأ في الإعداد: {e}")
else:
    str_app.markdown(f"""
    <div style="background-color: {card_bg}; color: {text_color}; padding: 35px; border-radius: 16px; text-align: center; margin-top: 50px; border: 1px solid #333333;">
        <h2 style="color: {text_color} !important; margin-bottom: 10px;">👋 أهلاً بك في TOMA CHAT Pro</h2>
        <p style="font-size: 16px; color: #888888 !important;">يرجى إدخال <b>مفتاح Groq API Key</b> لبدء استخدام المنصة.</p>
    </div>
    """, unsafe_allow_html=True)
