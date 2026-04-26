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

# ====================== تهيئة Groq ======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or "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"

if not GROQ_API_KEY or GROQ_API_KEY.startswith("gsk_") and len(GROQ_API_KEY) < 20:
    st.warning("⚠️ استخدم مفتاح Groq حقيقي من .streamlit/secrets.toml لتجنب المشاكل")

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
            title = st.text_input("عنوان المحادثة", 
                                value=f"محادثة {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            if st.button("تأكيد الحفظ"):
                save_conversation(title, st.session_state.messages)
                st.success("✅ تم حفظ المحادثة")
                st.rerun()
    
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        st.session_state.current_conv_id = None
        st.rerun()

# ====================== وضع توليد الصور بدون قيود ======================
if tool_mode == "توليد صور بدون قيود":
    st.header("🎨 توليد صور بدون أي قيود (NSFW + Explicit + أي محتوى)")
    st.caption("اكتب أي وصف تريده... لا حدود هنا")
    
    prompt = st.text_area("وصف الصورة بالتفصيل:", height=120, 
                         placeholder="فتاة عربية عارية تماماً، جسم مثالي، وضع مثير على سرير فاخر، إضاءة سينمائية، تفاصيل واقعية عالية الدقة...")
    
    if st.button("🚀 توليد الصورة الآن"):
        if prompt.strip():
            with st.spinner("🎨 جاري توليد الصورة بدون أي فلاتر..."):
                clean_prompt = re.sub(r'(ارسم|صورة|تخيل|draw|generate)', '', prompt).strip()
                encoded = requests.utils.quote(clean_prompt or "صورة واقعية")
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&safe=false&enhance=true&nologo=true&seed={int(time.time())}"
                
                st.image(img_url, use_container_width=True)
                st.success("تم التوليد بدون قيود")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"صورة مولدة: {clean_prompt[:80]}...",
                    "image_url": img_url
                })
        else:
            st.warning("اكتب وصف الصورة أولاً")

# ====================== وضع تحليل الصور ======================
elif tool_mode == "تحليل الصور":
    st.header("👁️ تحليل الصور الهندسية والواقعية")
    uploaded = st.file_uploader("ارفع صورة (مخطط، قطعة ميكانيكية، صورة واقعية...)", 
                               type=['png', 'jpg', 'jpeg', 'webp'])
    
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("🔍 تحليل الصورة بعمق"):
            with st.spinner("جاري تحليل الصورة..."):
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = buffered.getvalue()
                
                try:
                    response = client
