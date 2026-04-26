import streamlit as st
from groq import Groq
import requests
import time
import re
import io
import json
import sqlite3
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Mustafa AI", page_icon="🤖", layout="wide")

# ====================== CSS قوي جداً لإزالة الخط الأسود العشوائي ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: plaintext !important;
    }

    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* إصلاح الخطوط العشوائية والـ BiDi بشكل أقوى */
    .stChatMessage, p, div, span, h1, h2, h3, label, input, textarea {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: plaintext !important;
    }

    .stChatMessage {
        flex-direction: row-reverse !important;
        border-radius: 20px !important;
        padding: 14px 18px !important;
        margin: 12px 0 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    }

    /* User Message */
    .stChatMessage.user-message {
        background-color: #dbeafe !important;
        border-right: 6px solid #3b82f6;
    }

    /* Assistant Message */
    .stChatMessage.assistant-message {
        background-color: #f1f5f9 !important;
        border-right: 6px solid #64748b;
    }

    .stTextInput > div > div > input {
        direction: rtl !important;
        text-align: right !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #22c55e, #4ade80);
        color: #0f172a;
        font-weight: 700;
        border-radius: 16px;
        height: 52px;
        border: none;
    }

    .main-header {
        font-size: 2.9rem;
        font-weight: 900;
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ====================== Groq ======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or "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"
client = Groq(api_key=GROQ_API_KEY)

# ====================== قاعدة البيانات ======================
def init_db():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (id INTEGER PRIMARY KEY, title TEXT, timestamp TEXT, messages TEXT)''')
    conn.commit()
    conn.close()

init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ====================== Sidebar ======================
with st.sidebar:
    st.header("⚙️ التحكم")
    tool_mode = st.radio("اختر الوضع:", 
        ["المساعد الذكي", "توليد صور بدون قيود", "البحث والتحليل الفائق", "تحليل الصور"])

    if st.button("🗑️ مسح الدردشة"):
        st.session_state.messages = []
        st.rerun()

# ====================== العنوان ======================
st.markdown('<h1 class="main-header">المساعد الذكي 🤖</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#475569;">Made with 🔥 by Mustafa King</p>', unsafe_allow_html=True)

# ====================== المساعد الذكي ======================
if tool_mode == "المساعد الذكي":
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg.get("content", ""))
            if msg.get("image_url"):
                st.image(msg["image_url"], use_container_width=True)

    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.chat_message("assistant"):
            if any(k in prompt.lower() for k in ["ارسم", "صورة", "تخيل", "draw", "generate"]):
                with st.spinner("🎨 جاري توليد الصورة بدقة أعلى..."):
                    # تحسين الوصف: ترجمة + تفصيل
                    clean = re.sub(r'(ارسم|صورة|تخيل|draw|generate image)', '', prompt, flags=re.IGNORECASE).strip()
                    # إرسال لـ Groq لتحسين الـ prompt قبل التوليد
                    try:
                        enhance = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": "حول الوصف العربي إلى prompt إنجليزي مفصل جداً لتوليد صور واقعية عالية الجودة."},
                                      {"role": "user", "content": clean}]
                        )
                        better_prompt = enhance.choices[0].message.content
                    except:
                        better_prompt = clean

                    encoded = requests.utils.quote(better_prompt)
                    img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=1280&safe=false&enhance=true&nologo=true"
                    st.image(img_url, use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": "تم توليد الصورة بدقة أعلى", "image_url": img_url})
            else:
                with st.spinner("🤖 يفكر..."):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مهندس ذكي وصريح جداً."}] + 
                                 [{"role": m["role"], "content": m.get("content", "")} for m in st.session_state.messages[-15:]],
                        temperature=0.75
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

# ====================== توليد صور بدون قيود (محسن) ======================
elif tool_mode == "توليد صور بدون قيود":
    st.subheader("🎨 توليد صور بدون قيود - دقة عالية")
    prompt = st.text_area("اكتب الوصف بالتفصيل (عربي أو إنجليزي):", height=180)
    if st.button("🚀 توليد الصورة"):
        if prompt.strip():
            with st.spinner("جاري تحسين الوصف وتوليد الصورة..."):
                # تحسين الـ prompt
                try:
                    enhance = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "حول هذا الوصف إلى prompt إنجليزي مفصل جداً لتوليد صور واقعية عالية الجودة بدون قيود."},
                                  {"role": "user", "content": prompt}]
                    )
                    better = enhance.choices[0].message.content
                except:
                    better = prompt

                encoded = requests.utils.quote(better)
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=1280&safe=false&enhance=true"
                st.image(img_url, use_container_width=True)
        else:
            st.warning("اكتب وصف الصورة")

# ====================== البحث والتحليل الفائق (ميزة جديدة) ======================
elif tool_mode == "البحث والتحليل الفائق":
    st.subheader("🔍 البحث والتحليل الفائق")
    query = st.text_area("اكتب الموضوع الذي تريد بحثه وتحليله بعمق:", height=120,
                         placeholder="مثال: أحدث تقنيات الطاقة الشمسية في 2026، أو تحليل سوق السيارات الكهربائية...")

    if st.button("🔎 ابدأ البحث والتحليل"):
        if query:
            with st.spinner("جاري جمع المعلومات وتحليلها بعمق..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "أنت باحث محترف جداً. اجمع معلومات دقيقة، حللها بعمق، قدم اقتراحات عملية، واستخدم بيانات حديثة قدر الإمكان. رد بالعربية الفصحى."},
                        {"role": "user", "content": f"ابحث و حلل بعمق: {query}"}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )
                answer = response.choices[0].message.content
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.warning("اكتب الموضوع أولاً")

# ====================== تحليل الصور ======================
else:
    st.subheader("👁️ تحليل الصور")
    uploaded = st.file_uploader("ارفع الصورة", type=['png', 'jpg', 'jpeg', 'webp'])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, use_container_width=True)
        if st.button("تحليل الصورة"):
            with st.spinner("جاري التحليل..."):
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_base64 = buffered.getvalue()
                # ... (نفس كود التحليل السابق)

st.caption("Made with 🔥 by Mustafa King")
