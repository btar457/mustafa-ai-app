import streamlit as st
import requests
import random
import time

# 1. إعدادات الصفحة - تعطيل الـ Sidebar في الموبايل لتقليل التداخل
st.set_page_config(page_title="Mustafa Pro", layout="centered")

# 2. CSS مبسط جداً بدون أي تداخلات
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
    .stApp { background-color: #ffffff; }
    /* منع النص من التداخل العمودي */
    h1 { color: #1e3a8a; margin-bottom: 20px; font-size: 24px !important; line-height: 1.5; }
    .stImage img { border-radius: 15px; border: 2px solid #eee; }
    /* إخفاء القوائم الجانبية المزعجة في الموبايل */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("مصطفى AI - توليد الصور")

# 3. منطق توليد الصور (مستقل تماماً عن أي API Key خارجي)
if "img_history" not in st.session_state:
    st.session_state.img_history = []

prompt = st.text_input("ماذا تريد أن أرسم لك؟", placeholder="مثال: غزال في غابة..")

if st.button("توليد الآن"):
    if prompt:
        with st.spinner("جاري الرسم..."):
            # استخدام Seed عشوائي وتوقيت زمني لكسر الكاش
            seed = random.randint(1, 10**6)
            # الرابط المباشر للمحرك بدون وسيط AI لتجنب خطأ 401
            img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true&seed={seed}&v={time.time()}"
            
            # إضافة الصورة الجديدة في أول القائمة
            st.session_state.img_history.insert(0, {"url": img_url, "p": prompt})

# 4. عرض النتائج (كل الصور التي ولدت تبقى موجودة)
for img in st.session_state.img_history:
    st.markdown(f"**النتيجة لـ:** {img['p']}")
    st.image(img['url'], use_container_width=True)
    st.markdown("---")
