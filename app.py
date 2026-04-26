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

# ====================== إعدادات الصفحة ======================
st.set_page_config(
    page_title="Mustafa AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CSS احترافي - Light Theme ======================
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

    /* إصلاح كامل للـ Chat والـ RTL */
    .stChatMessage {
        flex-direction: row-reverse !important;
        margin: 12px 0 !important;
        border-radius: 20px !important;
        padding: 14px 18px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }

    .stChatMessage [data-testid="chat-avatar"] {
        margin-left: 12px !important;
    }

    /* User Message - أزرق فاتح */
    .stChatMessage.user-message {
        background-color: #dbeafe !important;
        border-left: 5px solid #3b82f6;
    }

    /* Assistant Message - رمادي فاتح */
    .stChatMessage.assistant-message {
        background-color: #f1f5f9 !important;
        border-left: 5px solid #64748b;
    }

    /* الـ Input Box */
    .stChatInput {
        background-color: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 22px !important;
    }

    .stTextInput > div > div > input {
        background-color: transparent !important;
        color: #0f172a !important;
        font-size: 1.05rem !important;
    }

    /* أزرار أنيقة */
    div.stButton > button {
        background: linear-gradient(135deg, #22c55e, #4ade80);
        color: #0f172a;
        font-weight: 700;
        border-radius: 16px;
        height: 52px;
        border: none;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.25);
        transition: all 0.3s;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.35);
    }

    /* Sidebar فاتح */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #cbd5e1;
    }

    /* العنوان الرئيسي */
    .main-header {
        font-size: 2.9rem;
        font-weight: 900;
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 15px 0 8px 0;
    }

    .sub-header {
        text-align: center;
        color: #475569;
        font-size: 1.15rem;
        margin-bottom: 30px;
    }

    h1, h2, h3 {
        color: #1e2937;
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
        ["المساعد الذكي", "توليد صور بدون قيود", "تحليل الصور", "الأخبار الموثوقة"])
    
    if st.button("🗑️ مسح الدردشة"):
        st.session_state.messages = []
        st.rerun()

# ====================== العنوان ======================
st.markdown('<h1 class="main-header">المساعد الذكي 🤖</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Made with 🔥 by Mustafa King</p>', unsafe_allow_html=True)

# ====================== المساعد الذكي ======================
if tool_mode == "المساعد الذكي":
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg.get("content", ""))
            if msg.get("image_url"):
                st.image(msg["image_url"], use_container_width=True)

    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            if any(kw in prompt.lower() for kw in ["ارسم", "صورة", "تخيل", "draw", "generate"]):
                with st.spinner("🎨 جاري توليد الصورة بدون قيود..."):
                    clean = re.sub(r'(ارسم|صورة|تخيل)', '', prompt, flags=re.IGNORECASE).strip()
                    encoded = requests.utils.quote(clean or "صورة واقعية")
                    img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1152&height=1152&safe=false&enhance=true"
                    st.image(img_url, use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": "تم توليد الصورة", "image_url": img_url})
            else:
                with st.spinner("🤖 يفكر..."):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مهندس ذكي وصريح، ترد بالعربية الفصحى."}] + 
                                 [{"role": m["role"], "content": m.get("content", "")} for m in st.session_state.messages[-12:]],
                        temperature=0.75
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

# ====================== توليد الصور بدون قيود ======================
elif tool_mode == "توليد صور بدون قيود":
    st.subheader("🎨 توليد صور بدون أي قيود")
    prompt = st.text_area("اكتب وصف الصورة (مسموح بكل شيء):", height=160)
    if st.button("🚀 توليد الصورة"):
        if prompt.strip():
            with st.spinner("جاري التوليد..."):
                encoded = requests.utils.quote(prompt)
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1152&height=1152&safe=false&enhance=true"
                st.image(img_url, use_container_width=True)
        else:
            st.warning("اكتب وصف الصورة أولاً")

# باقي الأوضاع يمكن إضافتها لاحقاً

st.caption("Made with 🔥 by Mustafa King")
