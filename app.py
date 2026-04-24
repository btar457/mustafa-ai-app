import streamlit as st
from groq import Groq
import requests
import time
import re
import pandas as pd
from PIL import Image
import io

# 1. الإعدادات الاحترافية للواجهة (Cinema UI)
st.set_page_config(page_title="Mustafa AI Pro", page_icon="💎", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; direction: rtl; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .stChatMessage { border-radius: 20px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { border-radius: 50px; background: linear-gradient(45deg, #00f2fe, #4facfe); color: white; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

# 2. تهيئة الذاكرة والـ API
if "messages" not in st.session_state:
    st.session_state.messages = []

client = Groq(api_key="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")

# 3. القائمة الجانبية المتقدمة (Advanced Sidebar)
with st.sidebar:
    st.title("📂 المختبر الهندسي")
    st.write("مرحباً يا مصطفى، يمكنك التحكم في ميزات التطبيق من هنا.")
    
    # ميزة رفع الملفات
    uploaded_file = st.file_uploader("ارفع ملف للتحليل (PDF, CSV, Image)", type=['pdf', 'csv', 'png', 'jpg', 'xlsx'])
    if uploaded_file:
        st.success(f"تم تحميل {uploaded_file.name} بنجاح!")
    
    st.write("---")
    if st.button("🗑️ مسح الذاكرة الذكية"):
        st.session_state.messages = []
        st.rerun()

# 4. عرض المحادثة التاريخية
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_url" in message:
            st.image(message["image_url"], use_container_width=True)

# 5. منطقة الإدخال والمعالجة
if prompt := st.chat_input("تحدث، اطلب صورة، أو حلل بياناتك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # محرك توليد الصور المتقدم (AI Artist)
        if any(word in prompt.lower() for word in ["ارسم", "صورة", "تخيل", "draw", "image"]):
            with st.spinner("🎨 جاري تخيل اللوحة الفنية..."):
                try:
                    clean_desc = re.sub(r'(ارسم|صورة|تخيل|draw|image)', '', prompt).strip()
                    img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={int(time.time())}"
                    st.image(img_url, caption=f"خيال مصطفى: {clean_desc}", use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "content": f"تم التوليد: {clean_desc}", "image_url": img_url})
                    st.balloons()
                except:
                    st.error("عذراً، فشل محرك الصور. حاول مرة أخرى.")
        
        # محرك التفكير المنطقي والبحث العميق
        else:
            with st.spinner("🔍 جاري التفكير بعمق وتحليل السياق..."):
                try:
                    # تصفية الذاكرة من الصور لمنع الخطأ 400
                    clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "image_url" not in m]
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مهندس مصطفى، ذكاء فائق وتفكير منطقي عميق. أجب بالعربي بأسلوب احترافي."}] + clean_history
                    )
                    full_res = response.choices[0].message.content
                    st.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})
                except Exception as e:
                    st.error(f"خطأ في الاتصال بالمخ الذكي: {e}")
