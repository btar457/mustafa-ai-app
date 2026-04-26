import streamlit as st
from groq import Groq
import requests
import sqlite3
import json
from datetime import datetime
import re

# إعدادات الصفحة المتقدمة
st.set_page_config(page_title="Mustafa AI Pro", page_icon="🚀", layout="wide")

# تصميم احترافي مع دعم الـ RTL الكامل
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;500;700&display=swap');
    * { font-family: 'Noto Sans Arabic', sans-serif; direction: rtl; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #e2e8f0; }
    .stChatFloatingInputContainer { bottom: 20px; }
    /* تحسين شكل الصور المنبثقة */
    .stImage img { border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# الاتصال بقاعدة البيانات (نسخة محسنة)
def get_db_connection():
    conn = sqlite3.connect('mustafa_v2.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      role TEXT, content TEXT, timestamp DATETIME)''')
        conn.commit()

init_db()

# تهيئة Groq
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "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"))

# وظيفة تحسين البرومبت للصور (Prompt Engineering)
def enhance_image_prompt(user_input):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a professional stable diffusion prompt engineer. Convert the user request into a high-detail English prompt. Focus on lighting, texture, and 8k resolution. Output only the prompt."} ,
                      {"role": "user", "content": user_input}]
        )
        return response.choices[0].message.content
    except:
        return user_input

# --- الواجهة الجانبية ---
with st.sidebar:
    st.title("👨‍💻 Mustafa King")
    st.info("النسخة الاحترافية v2.0")
    mode = st.selectbox("وضع العمل", ["المساعد المهندس", "توليد الصور الفني", "البحث العميق"])
    if st.button("🗑️ مسح الذاكرة"):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM chat_history")
        st.session_state.messages = []
        st.rerun()

# استرجاع الرسائل من قاعدة البيانات عند بدء التشغيل
if "messages" not in st.session_state:
    with get_db_connection() as conn:
        rows = conn.execute("SELECT role, content FROM chat_history ORDER BY timestamp ASC").fetchall()
        st.session_state.messages = [{"role": row["role"], "content": row["content"]} for row in rows]

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# منطق التعامل مع الإدخال
if prompt := st.chat_input("كيف يمكنني مساعدتك يا مصطفى؟"):
    # عرض رسالة المستخدم وحفظها
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with get_db_connection() as conn:
        conn.execute("INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
                     ("user", prompt, datetime.now()))

    # استجابة البوت
    with st.chat_message("assistant"):
        # حالة توليد الصور
        if any(word in prompt for word in ["ارسم", "صورة", "image", "draw"]):
            with st.spinner("🎨 نخطط اللوحة الآن..."):
                enhanced_prompt = enhance_image_prompt(prompt)
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(enhanced_prompt)}?width=1024&height=1024&nologo=true&seed={int(datetime.now().timestamp())}"
                st.image(img_url, caption="تم التوليد بواسطة محرك Mustafa AI")
                full_response = f"لقد قمت بتوليد صورة بناءً على وصفك المحسن: \n\n `{enhanced_prompt}`"
                st.markdown(full_response)
        
        # حالة الدردشة (Streaming)
        else:
            response_placeholder = st.empty()
            full_response = ""
            
            # محرك الـ Streaming للحصول على تجربة احترافية
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "أنت مهندس خبير ومساعد ذكي. إجاباتك دقيقة، تقنية، ومباشرة."}] + 
                         st.session_state.messages[-10:],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
        # حفظ استجابة البوت
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        with get_db_connection() as conn:
            conn.execute("INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
                         ("assistant", full_response, datetime.now()))
