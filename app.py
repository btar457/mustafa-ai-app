import streamlit as st
from groq import Groq
import requests
import sqlite3
import json
from datetime import datetime
import re
import io
from PIL import Image

# ====================== إعدادات الصفحة والتصميم (RTL & Deep Customization) ======================
st.set_page_config(page_title="Mustafa AI Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;500;700&display=swap');
    * { font-family: 'Noto Sans Arabic', sans-serif; direction: rtl !important; text-align: right !important; }
    
    .stApp { background-color: #f8fafc; }
    
    /* تحسين شكل الشات */
    .stChatMessage { border-radius: 15px; margin-bottom: 15px; border: 1px solid #e2e8f0; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .stChatMessage.user { background-color: #e0f2fe; border-right: 5px solid #3b82f6; }
    .stChatMessage.assistant { background-color: white; border-right: 5px solid #10b981; }

    /* تحسين العناوين والأزرار */
    .main-header { font-size: 3rem; font-weight: 700; color: #1e3a8a; text-align: center !important; margin-bottom: 20px; }
    div.stButton > button { width: 100%; border-radius: 10px; background-color: #1e3a8a; color: white; transition: 0.3s; }
    div.stButton > button:hover { background-color: #3b82f6; border-color: #3b82f6; }
    
    .stImage img { border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.15); }
    .stTextArea textarea, .stTextInput input { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ====================== تهيئة الـ API وقاعدة البيانات ======================
# تأمين المفتاح
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

# قاعدة البيانات (sqlite3) - مفعلة لحفظ الدردشة فعلياً
def get_db_connection():
    conn = sqlite3.connect('mustafa_v3.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      role TEXT, content TEXT, timestamp DATETIME, tool_mode TEXT)''')
        conn.commit()

init_db()

# تهيئة الـ Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# ====================== وظائف العمق الهندسي ======================

# 1. تحسين البرومبت للصور (Deep Prompt Engineering)
def enhance_image_prompt(user_input):
    """تحويل الوصف السريع إلى برومبت احترافي لنموذج توليد الصور"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a professional image generation prompt engineer for Stable Diffusion. Convert user request to detailed, descriptive English prompt. Include style, lighting, resolution (8k, hyperrealistic). Only output the final prompt."} ,
                      {"role": "user", "content": user_input}]
        )
        return response.choices[0].message.content.strip()
    except:
        # في حال فشل الـ AI، قم بتنظيف النص فقط
        return re.sub(r'(ارسم|صورة|تخيل|generate|image)', '', user_input).strip()

# 2. حفظ الرسائل إلى قاعدة البيانات
def save_message(role, content, tool_mode):
    with get_db_connection() as conn:
        conn.execute("INSERT INTO chat_history (role, content, timestamp, tool_mode) VALUES (?, ?, ?, ?)",
                     (role, content, datetime.now(), tool_mode))

# 3. محرك الاستجابة الحية (Streaming Engine)
def stream_groq_response(messages):
    response_placeholder = st.empty()
    full_response = ""
    
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "أنت مساعد مهندس ذكي، صريح جداً، ومحترف."}] + messages,
        stream=True,
        temperature=0.7
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
            # إضافة رمز "▌" لإظهار الكتابة الحية
            response_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
    
    response_placeholder.markdown(full_response, unsafe_allow_html=True)
    return full_response


# ====================== الشريط الجانبي (Sidebar) ======================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚙️ لوحة التحكم</h2>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103811.png", width=100)
    
    # إعادة الأدوات المخصصة بدقة
    tool_mode = st.radio("اختر الوضع المخصص:", 
        ["💬 المساعد الذكي (الشات)", 
         "🎨 أداة توليد الصور الاحترافية", 
         "🔍 البحث والتحليل العميق", 
         "👁️ تحليل الصور VLM"])
    
    st.markdown("---")
    if st.button("🗑️ مسح ذاكرة الشات بالكامل"):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM chat_history")
        st.session_state.messages = []
        st.rerun()

# ====================== العنوان الرئيسي ======================
st.markdown(f'<h1 class="main-header">{tool_mode.split(" ", 1)[1]} 🚀</h1>', unsafe_allow_html=True)

# ====================== منطق الأدوات (Logic) ======================

# --- الوضع 1: المساعد الذكي (محسن بالـ Streaming والذاكرة) ---
if tool_mode == "💬 المساعد الذكي (الشات)":
    
    # تحميل الرسائل الخاصة بهذا الوضع فقط من قاعدة البيانات
    if not st.session_state.messages:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT role, content FROM chat_history WHERE tool_mode = ? ORDER BY timestamp ASC", 
                                 ("Chat",)).fetchall()
            st.session_state.messages = [{"role": row["role"], "content": row["content"]} for row in rows]

    # عرض التاريخ
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # إدخال المستخدم
    if prompt := st.chat_input("اكتب سؤالك الهندسي أو التقني هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        save_message("user", prompt, "Chat")

        # الاستجابة الاحترافية (Streaming)
        with st.chat_message("assistant"):
            # نرسل آخر 10 رسائل للسياق لضمان السرعة (Flash optimization)
            context = st.session_state.messages[-10:]
            final_answer = stream_groq_response(context)
        
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        save_message("assistant", final_answer, "Chat")


# --- الوضع 2: أداة توليد الصور الاحترافية (تمت إعادتها وتحسينها) ---
elif tool_mode == "🎨 أداة توليد الصور الاحترافية":
    st.subheader("تخيل، صف، ونحن سنولد الصورة بدقة عالية.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        img_prompt = st.text_area("أدخل وصف الصورة بالتفصيل (عربي أو إنجليزي):", height=150, placeholder="قطة سيبيرية بعيون زرقاء تجلس على كرسي عرش بأسلوب سينمائي...")
        aspect_ratio = st.selectbox("أبعاد الصورة:", ["1:1 (مربع)", "16:9 (سينمائي)", "9:16 (موبايل)"])
    
    with col2:
        st.info("نحن نستخدم Llama-3 لتحسين البرومبت قبل إرساله لمحرك التوليد لضمان أعلى جودة.")
        generate_btn = st.button("🚀 توليد اللوحة الفنية")

    if generate_btn and img_prompt:
        with st.spinner("🎨 جاري تحليل الوصف، تحسين البرومبت، ورسم الصورة..."):
            # 1. العمق التقني: تحسين البرومبت
            enhanced = enhance_image_prompt(img_prompt)
            st.markdown(f"**البرومبت المحسن技术:** `{enhanced}`")
            
            # 2. تحديد الأبعاد
            width, height = 1024, 1024
            if aspect_ratio == "16:9 (سينمائي)": width, height = 1280, 720
            elif aspect_ratio == "9:16 (موبايل)": width, height = 720, 1280
            
            # 3. التوليد (مع seed متغير لعدم التكرار)
            seed = int(datetime.now().timestamp())
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(enhanced)}?width={width}&height={height}&nologo=true&private=true&seed={seed}"
            
            # 4. العرض (UX محترفة)
            st.image(img_url, caption=f"تم التوليد بناءً على: {img_prompt}", use_container_width=True)
            
            # حفظ العملية في قاعدة البيانات (اختياري، كـ Content)
            save_message("assistant", f"توليد صورة: {img_prompt} | البرومبت المحسن: {enhanced} | الرابط: {img_url}", "ImageGen")
            st.success("تم توليد الصورة بنجاح!")


# --- الوضع 3: البحث والتحليل العميق (Streaming Enabled) ---
elif tool_mode == "🔍 البحث والتحليل العميق":
    st.subheader("حلل الأسواق، التقنيات، أو البيانات بأسلوب باحث محترف.")
    query = st.text_area("أدخل موضوع البحث:", placeholder="تحليل مستقبلي للطاقة المتجددة في السعودية 2030...")
    
    if st.button("🔎 ابدأ التحليل العميق"):
        if query:
            with st.chat_message("assistant"):
                # نستخدم نفس محرك الـ Streaming لكن بـ System Prompt مختلف
                system_prompt = "أنت باحث تقني واقتصادي محترف. قدم تحليلاً عميقاً، مدعماً بالأرقام (إذا توفرت سياقياً)، مهيكلاً، وبالعربية الفصحى."
                response_placeholder = st.empty()
                full_response = ""
                
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
                    stream=True,
                    temperature=0.6 # أقل قليلاً لمزيد من الدقة
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                response_placeholder.markdown(full_response, unsafe_allow_html=True)
                
                save_message("user", query, "Analysis")
                save_message("assistant", full_response, "Analysis")
        else:
            st.warning("يرجى كتابة موضوع البحث.")

# --- الوضع 4: تحليل الصور (هيكل جاهز) ---
else:
    st.subheader("رفع وتحليل الصور باستخدام نماذج الرؤية الحاسوبية (VLM)")
    uploaded_file = st.file_uploader("اختر صورة...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='الصورة المرفوعة', use_container_width=True)
        
        analysis_prompt = st.text_input("ماذا تريد أن تعرف عن هذه الصورة؟", placeholder="صف هذه الصورة بالتفصيل...")
        
        if st.button("👁️ تحليل الصورة"):
            st.warning("ميزة الـ Vision تحتاج إلى مفتاح API يدعم نماذج Llama-3-Vision (غير مفعل حالياً في هذا الهيكل). تم إعداد الهيكل البرمجي لك.")
            # هنا يتم وضع كود تحويل الصورة لـ base64 وإرسالها لـ Groq Vision API

st.markdown("---")
st.caption(f"Made with 🔥 by Mustafa King | v3.0 Pro Development | Time: {datetime.now().strftime('%H:%M')}")
