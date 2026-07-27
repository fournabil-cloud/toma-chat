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

# --- ثيم GEMINI الأبيض الاحترافي ---
bg_color = "#FFFFFF" 
card_bg_color = "#F8F9FA" 
text_color = "#202124" 
sidebar_bg_color = "#F5F5F5" 
sidebar_text_color = "#5F6368" 
input_bg_color = "#FFFFFF" 
input_border_color = "#DADCE0" 
accent_color = "#1A73E8"

# --- أكواد CSS المحدثة لفرض شكل جميناي ---
str_app.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
            font-family: 'Google Sans', Roboto, Helvetica, Arial, sans-serif !important;
        }}
        
        .main .block-container {{
            padding-top: 60px !important;
            padding-bottom: 150px !important;
            max-width: 1000px !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_color} !important;
            border-right: none !important;
            padding-top: 20px !important;
        }}
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {sidebar_text_color} !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            font-weight: 500 !important;
            margin-bottom: 15px !important;
            padding-left: 15px !important;
        }}
        
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {{
            color: {sidebar_text_color} !important;
            font-size: 0.95rem !important;
        }}

        #MainMenu, header, footer {{ visibility: hidden; }}
        
        .header-container {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 50px;
        }}
        .header-logo {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            object-fit: contain;
        }}
        .header-title {{
            font-size: 1.6rem !important;
            color: {text_color} !important;
            font-weight: 500 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .sidebar-logo {{
            display: block;
            margin: 0 auto 40px auto;
            width: 120px;
            height: auto;
            border-radius: 12px;
        }}

        [data-testid="stChatInput"] {{
            background-color: transparent !important;
            border: none !important;
            position: fixed !important;
            bottom: 20px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 700px !important;
            max-width: 90% !important;
        }}
        
        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg_color} !important;
            color: {text_color} !important;
            border: 1px solid {input_border_color} !important;
            border-radius: 30px !important;
            padding: 15px 25px !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: #9AA0A6 !important;
        }}

        .stButton > button {{
            background-color: {card_bg_color} !important;
            color: {text_color} !important;
            border: 1px solid {input_border_color} !important;
            border-radius: 18px !important;
            font-weight: 500 !important;
            padding: 6px 15px !important;
            transition: all 0.2s !important;
            font-size: 0.9rem !important;
        }}
        .stButton > button:hover {{
            background-color: #E8EAED !important;
            border-color: #DADCE0 !important;
        }}
        
        .stDownloadButton > button {{
            background-color: {accent_color} !important;
            color: white !important;
            border: none !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px !important;
            background-color: transparent !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {card_bg_color} !important;
            border: 1px solid {input_border_color} !important;
            border-radius: 12px !important;
            color: {text_color} !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: #E8EAF6 !important;
            color: {accent_color} !important;
            border-color: #C5CAE9 !important;
        }}

        .stChatMessage {{
            padding: 15px 0 !important;
            gap: 15px !important;
        }}
        .stChatMessage p {{
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }}
        [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {{
            border-radius: 50% !important;
            width: 36px !important;
            height: 36px !important;
        }}
        [data-testid="stChatMessageAvatarAssistant"] {{
            background-color: transparent !important;
        }}

        .stSelectbox label, .stTextInput label, .stCheckbox label {{
            font-weight: 500 !important;
        }}
        
        .stExpander {{
            border: 1px solid {input_border_color} !important;
            border-radius: 12px !important;
            background-color: {card_bg_color} !important;
        }}
        
        hr {{
            border-top: 1px solid {input_border_color} !important;
            margin: 20px 0 !important;
        }}

    </style>
""", unsafe_allow_html=True)

# --- دوال النظام ---
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

def extract_html_code(text):
    pattern = r"```" + r"html\s*(.*?)\s*" + r"```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    return None

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
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional visual prompt engineer. Translate Arabic to clear English visual prompt. Output ONLY the final English prompt."},
                {"role": "user", "content": arabic_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return arabic_prompt

def fetch_generated_image(prompt, width=512, height=512, style=""):
    full_prompt = f"{prompt}, {style}, masterpiece" if style else f"{prompt}, masterpiece"
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

# --- واجهة العنوان والشعار ---
if logo_b64:
    str_app.markdown(f"""
        <div class="header-container">
            <img src="{logo_b64}" class="header-logo" alt="Logo" />
            <h1 class="header-title">TOMA CHAT Pro</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    str_app.title("⚡ TOMA CHAT Pro")

# --- إدارة الجلسات والشخصيات ---
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

# --- القائمة الجانبية (Sidebar) المحدثة ---
with str_app.sidebar:
    if logo_b64:
        str_app.markdown(f'<img src="{logo_b64}" class="sidebar-logo" alt="Logo" />', unsafe_allow_html=True)
        
    str_app.markdown("### <i class='fa-solid fa-sliders' style='margin-left: 10px;'></i> الإعدادات", unsafe_allow_html=True)
    
    secret_key = str_app.secrets.get("GROQ_API_KEY", DEFAULT_API_KEY)
    api_key_input = str_app.text_input("Groq API Key:", value=secret_key, type="password", key="groq_api_key_v24")

    str_app.markdown("<hr>", unsafe_allow_html=True)
    enable_web_search = str_app.checkbox("🌐 بحث الويب المباشر", value=False, key="web_search_toggle_v24")
    deep_research_mode = str_app.checkbox("🔍 وضع البحث العميق", value=False, key="deep_research_toggle_v24")
    enable_tts = str_app.checkbox("🔊 القراءة الصوتية التلقائية", value=False, key="tts_toggle_v24")
    enable_code_preview = str_app.checkbox("💻 معاينة أكواد HTML/Web", value=True, key="code_preview_toggle_v24")

    str_app.divider()
    model_choice = str_app.selectbox(
        "🧠 النموذج الذكي:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-11b-vision-preview"],
        key="groq_model_v24"
    )

    persona_choice = str_app.selectbox(
        "🎭 شخصية TOMA:",
        ["مساعد عام ذكي وودود", "خبير برمجة وتقنية (محترف)", "كاتب محتوى ومبدع", "مستشار تسويق وأعمال", "مختصر ومباشر جداً"],
        key="persona_v24"
    )

    str_app.markdown("<hr>", unsafe_allow_html=True)
    str_app.markdown("### <i class='fa-solid fa-clock-rotate-left' style='margin-left: 10px;'></i> المحادثات", unsafe_allow_html=True)
    session_names = list(str_app.session_state.sessions.keys())
    selected_session = str_app.selectbox("اختر محادثة:", session_names, index=session_names.index(str_app.session_state.current_session), key="session_selector_v24")
    
    if selected_session != str_app.session_state.current_session:
        str_app.session_state.current_session = selected_session
        str_app.rerun()

    col_btn1, col_btn2 = str_app.columns(2)
    with col_btn1:
        if str_app.button("➕ جديدة", key="new_chat_btn_v24", use_container_width=True):
            new_name = f"محادثة جديدة {len(str_app.session_state.sessions) + 1}"
            str_app.session_state.sessions[new_name] = []
            str_app.session_state.current_session = new_name
            str_app.rerun()
    with col_btn2:
        if str_app.button("🗑️ مسح", key="clear_chat_btn_v24", use_container_width=True):
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
            key="export_chat_btn_v24"
        )

# --- التشغيل الأساسي ---
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
                    key="doc_uploader_v24"
                )
            
            with tab_image_gen:
                col_img1, col_img2 = str_app.columns([2, 1])
                with col_img1:
                    gen_image_prompt = str_app.text_input("وصف الصورة المراد رسمها:", key="gen_image_prompt_v24")
                with col_img2:
                    img_style = str_app.selectbox("النمط الفني:", ["افتراضي", "Realistic", "Anime", "Cinematic", "Oil Painting"], key="img_style_v24")
                
                col_dim1, col_dim2 = str_app.columns([2, 1])
                with col_dim1:
                    img_aspect = str_app.selectbox("أبعاد الصورة:", ["مربع (512x512)", "أفقي (768x512)", "عمودي (512x768)"], key="img_aspect_v24")
                with col_dim2:
                    str_app.write("")
                    str_app.write("")
                    generate_btn = str_app.button("🎨 ارسم الآن", use_container_width=True, key="gen_image_btn_v24")

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
    <div style="background-color: {card_bg_color}; color: {text_color}; padding: 35px; border-radius: 16px; text-align: center; margin-top: 50px; border: 1px solid {input_border_color};">
        <h2 style="color: {text_color} !important; margin-bottom: 10px;">👋 أهلاً بك في TOMA CHAT Pro</h2>
        <p style="font-size: 16px; color: #5F6368 !important;">يرجى إدخال <b>مفتاح Groq API Key</b> لبدء استخدام المنصة.</p>
    </div>
    """, unsafe_allow_html=True)
