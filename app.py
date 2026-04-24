import streamlit as st
from groq import Groq
import tensorflow as tf # لمحركك الجديد
import numpy as np
import requests
import time
import io
from PIL import Image

# 1. الواجهة الاحترافية (Custom CSS)
st.set_page_config(page_title="Mustafa AI - Ultimate Edition", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-card { background: #1d1d1d; padding: 20px; border-radius: 15px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# 2. إعداد الذاكرة والـ API
if "messages" not in st.session_state:
    st.session_state.messages = []

client = Groq(api_key="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")

# 3. القائمة الجانبية (الأدوات المتقدمة)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    st.title("🛠️ أدوات المهندس")
    mode = st.selectbox("اختر وضع المعالجة", ["الدردشة الذكية", "توليد الصور (GANs)", "تحليل الملفات"])
    
    uploaded_file = st.file_uploader("ارفع مخطط أو ملف بيانات", type=['pdf', 'png', 'jpg', 'csv'])
    if uploaded_file:
        st.info(f"تم استقبال ملف: {uploaded_file.name}")

# 4. محرك المعالجة الرئيسي
if mode == "الدردشة الذكية":
    st.title("💬 العقل الذكي - مصطفى")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("تحدث معي بعمق..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 جاري البحث والتحليل العميق..."):
                clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "أنت مساعد مهندس ذكي وفائق القدرة."}] + clean_history
                )
                res = completion.choices[0].message.content
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})

elif mode == "توليد الصور (GANs)":
    st.title("🖼️ مختبر الصور المتقدم")
    desc = st.text_input("صف الصورة التي يتخيلها عقلك...")
    if st.button("توليد الصورة الآن"):
        with st.spinner("🚀 جاري تفعيل شبكة GANs للتوليد..."):
            img_url = f"https://pollinations.ai/p/{requests.utils.quote(desc)}?width=1024&height=1024&seed={int(time.time())}"
            st.image(img_url, caption="نتيجة المعالجة الاحترافية", use_container_width=True)
            st.balloons()

# زر المسح
if st.sidebar.button("🗑️ مسح الجلسة"):
    st.session_state.messages = []
    st.rerun()
