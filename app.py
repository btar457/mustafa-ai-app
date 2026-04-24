import streamlit as st
from groq import Groq
import requests
import time
import re
import pandas as pd
from PIL import Image

# 1. إعداد الصفحة بهوية هندسية نظيفة
st.set_page_config(page_title="Mustafa AI Pro", layout="wide")

# 2. تنسيق CSS مبسط ومستقر (يمنع الخطوط العشوائية)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        text-align: right;
        direction: rtl;
    }
    
    /* خلفية داكنة ثابتة ومريحة للعين */
    .stApp {
        background-color: #0e1117;
    }

    /* تنسيق فقاعات الدردشة لتبدو كبطاقات احترافية */
    [data-testid="stChatMessage"] {
        background-color: #161b22;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }

    /* تحسين وضوح مدخلات النص */
    .stChatInput textarea {
        background-color: #0d1117 !important;
        color: white !important;
        border-color: #30363d !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. إعداد الذاكرة والـ API
if "messages" not in st.session_state:
    st.session_state.messages = []

client = Groq(api_key="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")

# 4. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.title("📂 المختبر الهندسي")
    uploaded_file = st.file_uploader("ارفع ملف (PDF/CSV/Image)", type=['pdf', 'csv', 'png', 'jpg', 'xlsx'])
    if uploaded_file:
        st.success(f"تم استقبال: {uploaded_file.name}")
    
    st.markdown("---")
    if st.button("🗑️ البدء بجلسة جديدة"):
        st.session_state.messages = []
        st.rerun()

# 5. عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_url" in message:
            st.image(message["image_url"], use_container_width=True)

# 6. منطق المعالجة
if prompt := st.chat_input("تحدث، اطلب صورة، أو حلل بياناتك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # طلب توليد صور
        if any(word in prompt.lower() for word in ["ارسم", "صورة", "تخيل", "draw", "image"]):
            with st.spinner("🎨 جاري التوليد..."):
                clean_desc = re.sub(r'(ارسم|صورة|تخيل|draw|image)', '', prompt).strip()
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={int(time.time())}"
                st.image(img_url, caption=f"خيال مصطفى: {clean_desc}", use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": f"تم التوليد: {clean_desc}", "image_url": img_url})
        
        # طلب تحليل نصي
        else:
            with st.spinner("🔍 تحليل عميق..."):
                try:
                    # تصفية الذاكرة لمنع خطأ 400
                    clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "image_url" not in m]
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مصطفى الفائق. مهندس ميكانيك خبير. أجب بالعربي بوضوح."}] + clean_history
                    )
                    res_text = response.choices[0].message.content
                    st.markdown(res_text)
                    st.session_state.messages.append({"role": "assistant", "content": res_text})
                except Exception as e:
                    st.error(f"خطأ: {e}")
