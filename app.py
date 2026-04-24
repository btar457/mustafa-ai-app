import streamlit as st
from groq import Groq
import requests
import time
import re
from PIL import Image
import io

# 1. إعدادات الواجهة (احترافية، بسيطة، ومتجاوبة مع S23)
st.set_page_config(page_title="Mustafa AI Global", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #0e1117; color: white; }
    /* تنسيق الحاويات لتبدو كبطاقات هندسية */
    div.stButton > button { border-radius: 10px; height: 3em; background-color: #2e7d32; color: white; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 نظام مصطفى المتكامل (Mustafa AI)")
st.write("تحليل نصوص، توليد صور، وتعامل مع ملفات.")

# 2. إعداد الذاكرة والـ API
if "messages" not in st.session_state:
    st.session_state.messages = []

# مفتاح Groq الخاص بك (المخ الذكي)
client = Groq(api_key="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")

# 3. القائمة الجانبية (مركز التحكم)
with st.sidebar:
    st.header("📂 الأدوات المتقدمة")
    uploaded_file = st.file_uploader("ارفع ملف (صورة أو بيانات)", type=['png', 'jpg', 'csv', 'pdf'])
    if uploaded_file:
        st.success(f"تم تحميل: {uploaded_file.name}")
    
    st.markdown("---")
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        st.rerun()

# 4. عرض المحادثة التاريخية
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_url" in message:
            st.image(message["image_url"], use_container_width=True)

# 5. منطق المعالجة الشامل (Logic)
if prompt := st.chat_input("اطلب تحليل نص، توليد صورة، أو استشارة هندسية..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # ميزة توليد الصور (تخيل)
        if any(w in prompt for w in ["ارسم", "صورة", "تخيل"]):
            with st.spinner("🎨 جاري ابتكار الصورة..."):
                clean_desc = re.sub(r'(ارسم|صورة|تخيل)', '', prompt).strip()
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={int(time.time())}"
                st.image(img_url, caption="نتيجة التوليد المتقدم")
                st.session_state.messages.append({"role": "assistant", "content": f"تم توليد صورة لـ: {clean_desc}", "image_url": img_url})
        
        # ميزة التحليل المنطقي العميق (Groq)
        else:
            with st.spinner("🔍 تحليل ذكي..."):
                try:
                    # تصفية الذاكرة من أي بيانات غير نصية لمنع خطأ 400
                    clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "image_url" not in m]
                    
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile", # أقوى نموذج متاح للبحث العميق
                        messages=[{"role": "system", "content": "أنت مساعد مصطفى، مهندس ميكانيك خبير من الناصرية. أجب بالعربية بدقة هندسية ومنطقية."}] + clean_history,
                        temperature=0.6
                    )
                    res = completion.choices[0].message.content
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                except Exception as e:
                    st.error(f"⚠️ واجه النظام صعوبة. تأكد من اتصال الإنترنت.")
