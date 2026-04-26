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

# ====================== إعدادات احترافية + دعم عربي كامل ======================
st.set_page_config(page_title="Mustafa AI", layout="wide", initial_sidebar_state="expanded")

# CSS قوي جداً لدعم RTL + إصلاح الخطوط العشوائية + واجهة احترافية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: bidi-override !important;
    }

    .stApp {
        background-color: #0a0e17;
        color: #ffffff;
    }

    /* إصلاح الـ Chat Messages */
    .stChatMessage {
        flex-direction: row-reverse !important;
        text-align: right !important;
    }
    
    .stChatMessage [data-testid="chat-avatar"] {
        margin-left: 10px !important;
        margin-right: 0 !important;
    }

    /* إصلاح الخطوط الطولية العشوائية والـ BiDi */
    p, div, span, h1, h2, h3, h4, h5, h6, label, input, textarea, button {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: plaintext !important;
    }

    /* تحسين الـ Input والأزرار */
    .stTextInput > div > div > input {
        direction: rtl !important;
        text-align: right !important;
    }

    div.stButton > button {
        border-radius: 12px;
        height: 3.8em;
        background: linear-gradient(90deg, #2e7d32, #4caf50);
        color: white;
        font-weight: bold;
        border: none;
        width: 100%;
    }

    /* Sidebar تحسين */
    .css-1d391kg {  /* sidebar */
        background-color: #111827;
    }

    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4ade80;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================== Groq ======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or "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"
client = Groq(api_key=GROQ_API_KEY)

# ====================== قاعدة البيانات (نفس السابق) ======================
def init_db():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (id INTEGER PRIMARY KEY, title TEXT, timestamp TEXT, messages TEXT)''')
    conn.commit()
    conn.close()

def save_conversation(title, messages):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute("INSERT INTO conversations (title, timestamp, messages) VALUES (?, ?, ?)",
              (title, datetime.now().isoformat(), json.dumps(messages)))
    conn.commit()
    conn.close()

def load_conversations():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute("SELECT id, title, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 10")
    return c.fetchall()

def load_conversation(conv_id):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute("SELECT messages FROM conversations WHERE id=?", (conv_id,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

init_db()

# ====================== Session ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====================== Sidebar ======================
with st.sidebar:
    st.header("⚙️ التحكم")
    tool_mode = st.radio("اختر الوضع:", 
                        ["المساعد الذكي", "توليد صور بدون قيود", "تحليل الصور", "الأخبار"])

    st.markdown("---")
    if st.button("🗑️ مسح الدردشة"):
        st.session_state.messages = []
        st.rerun()

# ====================== العنوان الرئيسي ======================
st.markdown('<h1 class="main-header">المساعد الذكي 🤖</h1>', unsafe_allow_html=True)
st.caption("Made with 🔥 by Mustafa King")

# ====================== الوضع الرئيسي ======================
if tool_mode == "المساعد الذكي":
    # عرض الرسائل السابقة
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg.get("content", ""))
            if "image_url" in msg:
                st.image(msg["image_url"], use_container_width=True)

    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            if any(word in prompt.lower() for word in ["ارسم", "صورة", "تخيل", "draw", "generate"]):
                with st.spinner("🎨 جاري توليد الصورة بدون قيود..."):
                    clean = re.sub(r'(ارسم|صورة|تخيل|draw|generate)', '', prompt, flags=re.IGNORECASE).strip()
                    encoded = requests.utils.quote(clean or "صورة واقعية")
                    img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&safe=false&enhance=true"
                    st.image(img_url, use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": f"تم توليد الصورة", "image_url": img_url})
            else:
                with st.spinner("🤖 يفكر..."):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مهندس ذكي وصريح."}] + 
                                 [{"role": m["role"], "content": m.get("content", "")} for m in st.session_state.messages[-12:]],
                        temperature=0.75
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

elif tool_mode == "توليد صور بدون قيود":
    st.header("🎨 توليد صور بدون أي قيود")
    prompt = st.text_area("اكتب وصف الصورة (حتى لو كان NSFW أو حساس):", height=150)
    if st.button("توليد الصورة"):
        if prompt:
            with st.spinner("جاري التوليد..."):
                encoded = requests.utils.quote(prompt)
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&safe=false&enhance=true"
                st.image(img_url, use_container_width=True)

# (يمكنك إضافة باقي الأوضاع بنفس الطريقة)

st.caption("Made with 🔥 by Mustafa King")
