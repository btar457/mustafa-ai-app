import streamlit as st
from groq import Groq
import requests
import sqlite3
import json
from datetime import datetime
import re
import io
import time
import random
from PIL import Image

# ====================== إعدادات الصفحة والتنسيق (UI/UX) ======================
st.set_page_config(page_title="Mustafa AI Pro", page_icon="🤖", layout="wide")

# CSS متطور لإصلاح الخطوط العشوائية وضمان تجربة RTL احترافية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* إزالة الخطوط العمودية العشوائية التي قد تظهر في الحاويات */
    div[data-testid="stChatMessage"], .stMarkdown, .stVerticalBlock {
        border-right: none !important;
        border-left: none !important;
    }

    .stApp { background-color: #f8fafc; }

    /* تحسين شكل فقاعات الدردشة */
    .stChatMessage {
        border-radius: 15px !important;
        margin-bottom: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #edf2f7 !important;
    }
    
    .stChatMessage.user { background-color: #eff6ff !important; border-left: 4px solid #3b82f6 !important; }
    .stChatMessage.assistant { background-color: #ffffff !important; border-left: 4px solid #10b981 !important; }

    .main-header {
        font-size: 2.5rem;
        font-weight: 900;
        color: #1e3a8a;
        text-align: center !important;
        margin-bottom: 30px;
    }

    /* تحسين الأزرار */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        font-weight: 700;
        border: none;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== تهيئة المحركات والقواعد ======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

def get_db_connection():
    conn = sqlite3.connect('mustafa_vfinal.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      role TEXT, content TEXT, timestamp DATETIME, tool_mode TEXT)''')
        conn.commit()

init_db()

# تهيئة مخازن الجلسة
if "messages" not in st.session_state: st.session_state.messages = []
if "img_url" not in st.session_state: st.session_state.img_url = None
if "img_desc" not in st.session_state: st.session_state.img_desc = None

# ====================== الوظائف الذكية ======================

def enhance_image_prompt(user_input):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Convert this Arabic/English prompt into a hyper-detailed English image generation prompt. Focus on 8k, cinematic lighting, and realistic textures. Output only the prompt."},
                      {"role": "user", "content": user_input}]
        )
        return response.choices[0].message.content.strip()
    except:
        return user_input

def save_msg(role, content, mode):
    with get_db_connection() as conn:
        conn.execute("INSERT INTO chat_history (role, content, timestamp, tool_mode) VALUES (?, ?, ?, ?)",
                     (role, content, datetime.now(), mode))

# ====================== القائمة الجانبية ======================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>Mustafa AI ⚙️</h2>", unsafe_allow_html=True)
    tool_mode = st.radio("الوضع المخصص:", 
        ["💬 المساعد الذكي", "🎨 توليد صور احترافية", "🔍 البحث الفائق", "👁️ تحليل الرؤية"])
    
    st.markdown("---")
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        st.session_state.img_url = None
        st.rerun()

# ====================== التنفيذ حسب الوضع ======================
st.markdown(f'<h1 class="main-header">{tool_mode}</h1>', unsafe_allow_html=True)

# --- 1. المساعد الذكي ---
if tool_mode == "💬 المساعد الذكي":
    # عرض التاريخ
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("تحدث معي..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        save_msg("user", prompt, "Chat")

        with st.chat_message("assistant"):
            res_area = st.empty()
            full_res = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "أنت مهندس ذكي ومساعد محترف."}] + st.session_state.messages[-10:],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_area.markdown(full_res + "▌")
            res_area.markdown(full_res)
            
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        save_msg("assistant", full_res, "Chat")

# --- 2. توليد الصور (تم إصلاح مشكلة التكرار والخطوط) ---
elif tool_mode == "🎨 توليد صور احترافية":
    st.info("اكتب وصفك وسأقوم بتحويله لبرومبت احترافي وتوليد الصورة فوراً.")
    
    with st.form(key="img_form", clear_on_submit=False):
        user_prompt = st.text_area("وصف الصورة:", placeholder="مثال: مدينة مستقبلية في المريخ...")
        generate_btn = st.form_submit_button("🚀 توليد الآن")

    if generate_btn and user_prompt:
        with st.spinner("🎨 جاري العمل على اللوحة..."):
            enhanced = enhance_image_prompt(user_prompt)
            # إضافة معايير عشوائية (Cache Busting) لضمان نجاح التوليد المتكرر
            seed = random.randint(1, 999999)
            t = int(time.time())
            
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(enhanced)}?width=1024&height=1024&nologo=true&seed={seed}&t={t}"
            
            st.session_state.img_url = img_url
            st.session_state.img_desc = user_prompt
            save_msg("system", f"Image: {user_prompt}", "ImageGen")

    if st.session_state.img_url:
        st.markdown(f"**النتيجة لـ:** {st.session_state.img_desc}")
        st.image(st.session_state.img_url, use_container_width=True)
        st.markdown(f"🔍 **البورميت المستخدم:** `{enhance_image_prompt(st.session_state.img_desc)}`")

# --- 3. البحث الفائق ---
elif tool_mode == "🔍 البحث الفائق":
    query = st.text_input("عن ماذا نبحث اليوم؟")
    if st.button("بدء التحليل"):
        with st.spinner("جاري التحليل العميق..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "أنت باحث أكاديمي."}, {"role": "user", "content": query}]
            )
            st.write(res.choices[0].message.content)

# --- 4. تحليل الرؤية ---
else:
    uploaded = st.file_uploader("ارفع صورة للتحليل", type=["png", "jpg", "jpeg"])
    if uploaded:
        st.image(uploaded, caption="تم رفع الصورة")
        st.warning("يتطلب هذا النمط إعداد Groq Vision API.")

st.markdown("---")
st.caption("Mustafa King AI | vFinal Pro 🚀")
