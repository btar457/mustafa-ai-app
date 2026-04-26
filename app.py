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
st.set_page_config(page_title="Mustafa Engineering Global", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #0e1117; color: white; }
    div.stButton > button { 
        border-radius: 12px; height: 3.8em; background-color: #2e7d32; 
        color: white; border: none; width: 100%; font-weight: bold; 
    }
</style>
""", unsafe_allow_html=True)

# ====================== Groq Client ======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or "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"

client = Groq(api_key=GROQ_API_KEY)

# ====================== قاعدة بيانات لحفظ المحادثات ======================
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

# ====================== Session State ======================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None

# ====================== Sidebar ======================
with st.sidebar:
    st.header("⚙️ مركز التحكم")
    tool_mode = st.radio("اختر وضع التشغيل:", 
                        ["المساعد الذكي", "توليد صور بدون قيود", "تحليل الصور", "الأخبار الموثوقة"])
    
    st.markdown("---")
    st.subheader("💾 المحادثات المحفوظة")
    
    for cid, title, ts in load_conversations():
        if st.button(f"📄 {title[:35]}...", key=f"load_{cid}"):
            st.session_state.messages = load_conversation(cid)
            st.session_state.current_conv_id = cid
            st.rerun()
    
    if st.button("💾 حفظ المحادثة الحالية"):
        if st.session_state.messages:
            title = st.text_input("عنوان المحادثة", value=f"محادثة {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            if st.button("تأكيد الحفظ"):
                save_conversation(title, st.session_state.messages)
                st.success("✅ تم حفظ المحادثة")
                st.rerun()
    
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        st.session_state.current_conv_id = None
        st.rerun()

# ====================== توليد الصور بدون قيود ======================
if tool_mode == "توليد صور بدون قيود":
    st.header("🎨 توليد صور بدون أي قيود")
    prompt = st.text_area("وصف الصورة (اكتب أي شيء بدون خوف):", height=130,
                         placeholder="فتاة عربية عارية في وضع مثير، تفاصيل واقعية، إضاءة درامية...")
    
    if st.button("🚀 توليد الصورة"):
        if prompt.strip():
            with st.spinner("جاري التوليد بدون فلاتر..."):
                clean = re.sub(r'(ارسم|صورة|تخيل)', '', prompt).strip()
                encoded = requests.utils.quote(clean or "صورة واقعية")
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&safe=false&enhance=true"
                st.image(img_url, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": f"صورة: {clean}", "image_url": img_url})
        else:
            st.warning("اكتب وصف الصورة")

# ====================== تحليل الصور ======================
elif tool_mode == "تحليل الصور":
    st.header("👁️ تحليل الصور")
    uploaded = st.file_uploader("ارفع صورة", type=['png', 'jpg', 'jpeg'])
    
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, use_container_width=True)
        
        if st.button("تحليل الصورة"):
            with st.spinner("جاري التحليل..."):
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_base64 = buffered.getvalue()
                
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "حلل الصورة بعمق بالعربية"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                        ]
                    }]
                )
                answer = response.choices[0].message.content
                st.write(answer)

# ====================== الأخبار ======================
elif tool_mode == "الأخبار الموثوقة":
    st.header("🌍 الأخبار الموثوقة")
    with st.spinner("جاري جلب الأخبار..."):
        try:
            url = "https://newsapi.org/v2/top-headlines?country=ae&category=technology&apiKey=f7b8849b2c3a4d87a4a905a5d7c3b2e5"
            resp = requests.get(url).json()
            for art in resp.get("articles", [])[:5]:
                st.subheader(art.get("title", ""))
                st.write(art.get("description", ""))
                st.markdown(f"[رابط]({art.get('url')})")
                st.markdown("---")
        except:
            st.error("فشل جلب الأخبار")

# ====================== المساعد الذكي ======================
else:
    st.header("🤖 المساعد الذكي")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg.get("content", ""))
            if "image_url" in msg:
                st.image(msg["image_url"], use_container_width=True)
    
    if prompt := st.chat_input("اكتب رسالتك..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            if any(word in prompt.lower() for word in ["ارسم", "صورة", "تخيل", "draw"]):
                with st.spinner("جاري توليد الصورة..."):
                    clean = re.sub(r'(ارسم|صورة|تخيل)', '', prompt).strip()
                    encoded = requests.utils.quote(clean or "صورة")
                    img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&safe=false"
                    st.image(img_url, use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": f"صورة مولدة", "image_url": img_url})
            else:
                with st.spinner("يفكر..."):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مهندس ذكي."}] + 
                                 [{"role": m["role"], "content": m.get("content", "")} for m in st.session_state.messages[-10:]],
                        temperature=0.7
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

st.caption("Made with 🔥 by Mustafa King")
