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

# إعداد الألوان الأساسية بناءً على المظهر
is_dark = st.session_state.theme == "داكن (Dark)"
bg_color = "#212121" if is_dark else "#F9F9F9"
text_color = "#FFFFFF" if is_dark else "#111111"
sidebar_bg = "#171717" if is_dark else "#EDEDED"
sidebar_text = "#F0F0F0" if is_dark else "#202020" # لون نصوص القائمة الجانبية (ناصع)
chat_bg = "#343541" if is_dark else "#E5E5EA"
input_bg = "#2F2F2F" if is_dark else "#FFFFFF"
input_text = "#FFFFFF" if is_dark else "#000000"

# --- أكواد CSS محسنة لإصلاح وضوح الكتابة بالكامل ---
st.markdown(f"""
    <style>
        /* 1. ضبط الخلفية والنص الأساسي */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        /* 2. تحسين وضوح القائمة الجانبية (Sidebar) بالكامل */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
            color: {sidebar_text};
            border-left: 1px solid #303030;
        }}
        
        /* تلوين العناوين (Headers) داخل القائمة الجانبية */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: {sidebar_text} !important;
            font-weight: 700;
        }}

        /* تلوين نصوص التسميات (Labels) فوق خانات الإدخال والقوائم في الـ Sidebar */
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {{
            color: {sidebar_text} !important;
            font-size: 15px !important;
            font-weight: 500;
        }}

        /* تلوين النصوص داخل خانات الإدخال والقوائم المنسدلة في الـ Sidebar */
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div,
        [data-testid="stSidebar"] .stTextInput input {{
            color: {input_text} !important;
            background-color: {input_bg} !important;
        }}

        /* 3. تحسين وضوح العناوين والفقرات في الواجهة الرئيسية */
        .main .stMarkdown h1, .main .stMarkdown h2, .main .stMarkdown h3 {{
            color: {text_color} !important;
            font-weight: 800;
        }}
        
        /* تلوين العناوين من نوع (Subheader) مثل ":المرفقات وأدوات الصور" */
        .main h3[data-testid="stHeader"] {{
            color: {text_color} !important;
            font-size: 24px !important;
            margin-top: 25px;
            margin-bottom: 15px;
        }}

        .main label[data-testid="stWidgetLabel"] p {{
            color: {text_color} !important;
            font-size: 16px !important;
        }}

        /* 4. إخفاء القوائم الافتراضية وتحسين الشات */
        #MainMenu, header, footer {{ visibility: hidden; }}
        [data-testid="stChatInput"] {{
            position: fixed;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            width: 70%;
            background-color: {bg_color};
            z-index: 100;
        }}
        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg};
            color: {input_text};
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #454545;
            font-size: 16px;
        }}
        [data-testid="stChatMessageAssistant"] {{
            background-color: {chat_bg};
            color: {text_color};
            border-radius: 10px;
        }}
        .stButton > button {{
            background-color: #19C37D;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
            font-size: 16px;
        }}
        .stButton > button:hover {{
            background-color: #1A7F64;
            border: none;
        }}
        
        /* تحسين مظهر مستطيلات الرفع */
        [data-testid="stFileUploadDropzone"] {{
            background-color: {input_bg};
            border: 2px dashed #454545;
            border-radius: 10px;
        }}
        [data-testid="stFileUploadDropzone"] p {{
            color: {text_color} !important;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ TOMA CHAT Pro")

# --- إدارة جلسات المحادثة ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "محادثة جديدة 1"

# --- القائمة الجانبية (Sidebar) المحسنة ---
with st.sidebar:
    st.header("⚙️ إعدادات TOMA")
    api_key_input = st.text_input("أدخل مفتاح Groq API Key:", type="password", key="groq_api_key_v2")

    st.divider()
    new_theme = st.selectbox("مظهر التطبيق:", ["داكن (Dark)", "فاتح (Light)"], index=0 if is_dark else 1, key="theme_selector_v2")
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

# --- المنطق الأساسي للتطبيق ---
if api_key_input:
    clean_api_key = api_key_input.strip()
    try:
        client = Groq(api_key=clean_api_key)
        system_instruction = persona_prompts.get(persona_choice, "أنت مساعد ذكي.")
        messages = st.session_state.sessions[st.session_state.current_session]

        # عرض تاريخ المحادثة
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

        # --- أدوات المستندات والصور في الواجهة الرئيسية ---
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

        # --- إدخال الشات الأساسي ---
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
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("TOMA يفكر..."):
                    try:
                        # 1. إذا كان الملف صورة (Vision)
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
                        
                        # 2. إذا كان الملف PDF أو TXT (RAG بسيط)
                        elif file_type in ["pdf", "txt"]:
                            if file_type == "pdf":
                                doc_text = extract_text_from_pdf(uploaded_file)
                            else:
                                doc_text = uploaded_file.getvalue().decode("utf-8")

                            augmented_prompt = f"المستند المرفق:\n\"\"\"\n{doc_text[:15000]}\n\"\"\"\n\nبناءً على المستند أعلاه، إجابة السؤال التالي:\n{prompt}"
                            
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
                            # إضافة سياق المحادثة (آخر 10 رسائل لضمان السرعة)
                            for m in messages[-10:]:
                                if m.get("content") and "طلب توليد صورة:" not in m["content"]:
                                    groq_messages.append({"role": m["role"], "content": m["content"]})

                            completion = client.chat.completions.create(
                                model=model_choice,
                                messages=groq_messages,
                                temperature=0.7,
                            )
                        
                        bot_response = completion.choices[0].message.content
                        st.markdown(bot_response)
                        messages.append({"role": "assistant", "content": bot_response})
                        
                    except Exception as api_e:
                        st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {api_e}")
            st.rerun()

    except Exception as e:
        st.error(f"حدث خطأ في الإعداد: {e}")
else:
    # رسالة الترحيب عند عدم وجود مفتاح
    st.markdown(f"""
    <div style="background-color: {chat_bg}; color: {text_color}; padding: 30px; border-radius: 15px; text-align: center; margin-top: 50px;">
        <h2 style="color: {text_color} !important;">👋 أهلاً بك في TOMA CHAT Pro!</h2>
        <p style="font-size: 18px; margin-top: 15px;">لبدء استخدام التطبيق وتحليل الملفات ورسم الصور بسرعات خارقة، يرجى إدخال <b>مفتاح Groq API Key</b> الخاص بك في الشريط الجانبي.</p>
    </div>
    """, unsafe_allow_html=True)
