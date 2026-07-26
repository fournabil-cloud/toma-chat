import streamlit as st
from google import genai
from PIL import Image
import gtts
import os
import base64
from io import BytesIO

# 1. إعداد صفحة التطبيق
st.set_page_config(page_title="TOMA CHAT Pro", page_icon="⚡", layout="centered")

# 2. إعدادات الثيم والوضع (داكن / فاتح)
if "theme" not in st.session_state:
    st.session_state.theme = "داكن (Dark)"

bg_color = "#212121" if st.session_state.theme == "داكن (Dark)" else "#F9F9F9"
text_color = "#FFFFFF" if st.session_state.theme == "داكن (Dark)" else "#111111"
chat_bg = "#343541" if st.session_state.theme == "داكن (Dark)" else "#E5E5EA"
input_bg = "#2F2F2F" if st.session_state.theme == "داكن (Dark)" else "#FFFFFF"
input_text = "#FFFFFF" if st.session_state.theme == "داكن (Dark)" else "#000000"

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        h1 {{
            color: {text_color};
            text-align: center;
            font-size: 36px;
            margin-bottom: 20px;
        }}
        #MainMenu, header, footer {{
            visibility: hidden;
        }}
        [data-testid="stChatInput"] {{
            position: fixed;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            width: 65%;
            background-color: {bg_color};
        }}
        [data-testid="stChatInput"] textarea {{
            background-color: {input_bg};
            color: {input_text};
            border-radius: 8px;
            padding: 12px;
            border: 1px solid #404040;
        }}
        [data-testid="stChatMessageAssistant"] {{
            background-color: {chat_bg};
            color: {text_color};
        }}
        .stButton > button {{
            background-color: #19C37D;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
        }}
        .stButton > button:hover {{
            background-color: #1A7F64;
        }}
        .word-counter {{
            font-size: 11px;
            color: #888;
            text-align: left;
            margin-top: 5px;
        }}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ TOMA CHAT Pro")

# --- إدارة جلسات المحادثة ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"محادثة جديدة 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "محادثة جديدة 1"

# --- الشريط الجانبي للإعدادات والتحكم المتطور ---
with st.sidebar:
    st.header("⚙️ إعدادات TOMA")
    
    api_key_input = st.text_input("أدخل مفتاح Google API Key:", type="password", help="احصل على مفتاحك المجاني من Google AI Studio")

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
    
    # تصحيح أسماء النماذج لتجنب خطأ 404
    model_choice = st.selectbox(
        "اختر نموذج الذكاء الاصطناعي:",
        ["gemini-1.5-flash", "gemini-1.5-pro"],
        help="اختر النموذج المناسب للتحادث."
    )

    persona_choice = st.selectbox(
        "اختر شخصية ونمط TOMA:",
        [
            "مساعد عام ذكي وودود",
            "خبير برمجة وتقنية (محترف)",
            "كاتب محتوى ومبدع",
            "مستشار تسويق وأعمال",
            "مختصر ومباشر جداً"
        ]
    )

    st.divider()

    if st.button("🗑️ مسح المحادثة الحالية"):
        st.session_state.sessions[st.session_state.current_session] = []
        st.rerun()

    current_messages = st.session_state.sessions[st.session_state.current_session]
    if current_messages:
        chat_txt = ""
        for m in current_messages:
            role = "المستخدم" if m["role"] == "user" else "TOMA"
            chat_txt += f"{role}: {m['content']}\n" + "-"*40 + "\n"
        
        st.download_button(
            label="📥 تحميل المحادثة (.txt)",
            data=chat_txt,
            file_name=f"{st.session_state.current_session}.txt",
            mime="text/plain"
        )

    st.markdown("---")
    st.markdown("🔹 **TOMA CHAT Pro v4.1**")

persona_prompts = {
    "مساعد عام ذكي وودود": "أنت مساعد ذكي ودود ومفيد جداً، أجب بلغة واضحة ودقيقة.",
    "خبير برمجة وتقنية (محترف)": "أنت خبير برمجة وتقنية محترف، قدم أكواد نظيفة، مشروحة بدقة وبأفضل الممارسات.",
    "كاتب محتوى ومبدع": "أنت كاتُب محتوى ومبدع محترف، اكتب بصياغة جذابة، بليغة، ومؤثرة.",
    "مستشار تسويق وأعمال": "أنت مستشار تسويق وأعمال، قدم استراتيجيات ذكية وحلول عملية لنمو المشاريع.",
    "مختصر ومباشر جداً": "كن مختصراً ومباشراً قدر الإمكان، دون حشو أو إطالة."
}

# --- واجهة قوالب الأسئلة السريعة (Quick Prompts) ---
st.markdown("##### 🚀 اختصارات سريعة:")
col_q1, col_q2, col_q3, col_q4 = st.columns(4)
quick_prompt_selected = None

with col_q1:
    if st.button("💻 كتابة كود بايثون"):
        quick_prompt_selected = "اكتب لي كود بايثون احترافي ومنظم لـ: "
with col_q2:
    if st.button("📝 تلخيص نص"):
        quick_prompt_selected = "قم بتلخيص النص التالي بأسلوب منظم وواضح: "
with col_q3:
    if st.button("🌐 ترجمة فورية"):
        quick_prompt_selected = "ترجم النص التالي إلى العربية بدقة واحترافية: "
with col_q4:
    if st.button("🎨 توليد صورة"):
        quick_prompt_selected = "ارسم لي صورة لـ: "

# --- المنطق الأساسي للدردشة ---
if api_key_input:
    try:
        client = genai.Client(api_key=api_key_input)
        system_instruction = persona_prompts.get(persona_choice, "أنت مساعد ذكي.")

        messages = st.session_state.sessions[st.session_state.current_session]

        for idx, message in enumerate(messages):
            with st.chat_message(message["role"]):
                if "image" in message and message["image"] is not None:
                    st.image(message["image"], caption="الصورة المرفقة", width=250)
                if "generated_image" in message and message["generated_image"] is not None:
                    st.image(message["generated_image"], caption="الصورة المولدة", width=400)
                st.markdown(message["content"])
                
                words_count = len(message["content"].split())
                st.markdown(f'<div class="word-counter">عدد الكلمات: {words_count}</div>', unsafe_allow_html=True)
                
                if message["role"] == "assistant":
                    if st.button(f"🔊 استماع للرد #{idx}", key=f"tts_{idx}"):
                        try:
                            tts = gtts.gTTS(text=message["content"], lang='ar')
                            temp_audio = "temp_audio.mp3"
                            tts.save(temp_audio)
                            audio_file = open(temp_audio, 'rb')
                            audio_bytes = audio_file.read()
                            audio_base64 = base64.b64encode(audio_bytes).decode()
                            audio_html = f'<audio autoplay controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
                            st.markdown(audio_html, unsafe_allow_html=True)
                        except Exception as tts_err:
                            st.error(f"خطأ في توليد الصوت: {tts_err}")

        uploaded_file = st.file_uploader("📷 رفع صورة لتحليلها (اختياري):", type=["jpg", "jpeg", "png"])

        chat_input_val = st.chat_input("اكتب رسالتك أو اطلب توليد صورة...")
        prompt = quick_prompt_selected if quick_prompt_selected else chat_input_val

        if prompt:
            img_to_send = None
            if uploaded_file is not None:
                img_to_send = Image.open(uploaded_file)

            messages.append({"role": "user", "content": prompt, "image": img_to_send, "generated_image": None})
            with st.chat_message("user"):
                if img_to_send is not None:
                    st.image(img_to_send, caption="الصورة المرفقة", width=250)
                st.markdown(prompt)

            is_image_request = any(word in prompt.lower() for word in ["ارسم", "صورة لـ", "توليد صورة", "generate image", "draw"])

            with st.chat_message("assistant"):
                if is_image_request:
                    with st.spinner("جاري توليد الصورة بواسطة الذكاء الاصطناعي..."):
                        try:
                            result = client.models.generate_images(
                                model='imagen-3.0-generate-002',
                                prompt=prompt,
                                config=dict(
                                    number_of_images=1,
                                    output_mime_type="image/jpeg",
                                    aspect_ratio="1:1",
                                    person_generation="ALLOW_ADULT",
                                )
                            )
                            generated_img = None
                            for generated_image in result.generated_images:
                                image = Image.open(BytesIO(generated_image.image.image_bytes))
                                generated_img = image
                                st.image(image, caption="الصورة المولدة بواسطة TOMA", width=400)
                            
                            bot_response = "تفضل، هذه هي الصورة التي طلبتها بناءً على وصفك!"
                            st.markdown(bot_response)
                            messages.append({"role": "assistant", "content": bot_response, "image": None, "generated_image": generated_img})
                        except Exception as img_err:
                            response = client.models.generate_content(
                                model=model_choice,
                                contents=[prompt],
                                config={'system_instruction': system_instruction}
                            )
                            bot_response = response.text
                            st.markdown(bot_response)
                            messages.append({"role": "assistant", "content": bot_response, "image": None, "generated_image": None})
                else:
                    with st.spinner("TOMA يفكر..."):
                        contents = [prompt]
                        if img_to_send is not None:
                            contents.insert(0, img_to_send)

                        response = client.models.generate_content(
                            model=model_choice,
                            contents=contents,
                            config={
                                'system_instruction': system_instruction
                            }
                        )
                        
                        bot_response = response.text
                        st.markdown(bot_response)
                        
                        resp_words = len(bot_response.split())
                        st.markdown(f'<div class="word-counter">عدد الكلمات: {resp_words}</div>', unsafe_allow_html=True)
                
                        messages.append({"role": "assistant", "content": bot_response, "image": None, "generated_image": None})
            
            st.rerun()

    except Exception as e:
        st.error(f"حدث خطأ في الاتصال أو المفتاح: {e}")
else:
    st.info("👋 أهلاً بك في تطبيق **TOMA CHAT Pro**! يرجى إدخال مفتاح Google API Key الخاص بك في الشريط الجانبي لبدء الدردشة.")
