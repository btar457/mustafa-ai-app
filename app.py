import streamlit as st
from groq import Groq
import requests
import time
import re
import pandas as pd
from PIL import Image
import io

# 1. إعدادات العرض الاحترافي (Professional UI)
st.set_page_config(page_title="Mustafa Super-App PRO", page_icon="💎", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #ddd; }
    .stApp { background: linear-gradient(to bottom, #ffffff, #f0f2f5); }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #007bff; color: white; }
</style>
""", unsafe_allow_html=True)

# 2. إعداد المحركات (Engines)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. شريط جانبي متطور للتعامل مع الملفات (Advanced File Handling)
with st.sidebar:
    st.title("📂 مركز التحكم")
    uploaded_file = st.file_uploader("ارفع ملف (PDF, Excel, CSV, Image)", type=['pdf', 'xlsx', 'csv', 'png', 'jpg'])
    if uploaded_file:
        st.success(f"تم تحميل: {uploaded_file.name}")
        # هنا يمكن إضافة منطق قراءة الملفات وتحليلها لاحقاً
    
    st.write("---")
    if st.button("🗑️ مسح الجلسة الذكية"):
        st.session_state.messages = []
        st.rerun()

# 4. عرض المحادثة بتنسيق احترافي
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_url" in message:
            st.image(message["image_url"], use_container_width=True)

# 5. منطق المعالجة المتقدم (Advanced Logic)
if prompt := st.chat_input("اسألني بعمق، اطلب صورة، أو حلل ملفاً..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # أداة توليد الصور المتقدمة (Image Generation Tool)
        if any(word in prompt.lower() for word in ["ارسم", "صورة", "تخيل", "draw", "image"]):
            with st.spinner("🎨 جاري الرسم الاحترافي..."):
                clean_desc = re.sub(r'(ارسم|صورة|تخيل|draw|image)', '', prompt).strip()
                seed = int(time.time())
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={seed}"
                st.image(img_url, caption="النتيجة النهائية", use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": f"تم توليد صورة لـ: {clean_desc}", "image_url": img_url})
        
        # أداة التفكير المنطقي والبحث العميق (Deep Reasoning)
        else:
            with st.spinner("🔍 جاري التفكير بعمق (Deep Reasoning)..."):
                try:
                    # نظام تنظيف الذاكرة لضمان عدم حدوث خطأ 400
                    clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "image_url" not in m]
                    
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "أنت مساعد مصطفى الفائق. مهندس ميكانيك خبير، عبقري في التحليل المنطقي. أجب بأسلوب احترافي وعميق."},
                            *clean_history
                        ],
                        temperature=0.5 # للتركيز والمنطق
                    )
                    res = completion.choices[0].message.content
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                except Exception as e:
                    st.error(f"خطأ تقني: {e}")
