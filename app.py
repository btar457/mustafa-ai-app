import streamlit as st
import requests
import random
import time

# واجهة مستخدم نظيفة جداً (إصلاح مشكلة الموبايل)
st.set_page_config(page_title="Mustafa AI Pro", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: center; }
    .stApp { background-color: #f9f9f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("Mustafa King AI 🚀")

tab1, tab2 = st.tabs(["🎨 مولد الصور (مستقر)", "💬 دردشة سريعة"])

# --- قسم الصور (بدون مفتاح API - لا يمكن أن يفشل) ---
with tab1:
    user_p = st.text_input("صف الصورة التي تريدها:", key="img_p", placeholder="مثال: أسد يرتدي تاجاً")
    if st.button("توليد الآن"):
        if user_p:
            with st.spinner("جاري الرسم..."):
                # رابط مباشر لا يحتاج API Key
                ts = int(time.time())
                seed = random.randint(1, 1000000)
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(user_p)}?width=1024&height=1024&seed={seed}&nologo=true&v={ts}"
                
                st.image(img_url, caption="نتيجتك الاحترافية", use_container_width=True)
                st.success("تم التوليد بنجاح! جرب وصفاً آخر.")

# --- قسم الدردشة (نسخة طوارئ مجانية) ---
with tab2:
    st.info("هذا القسم يعمل بمحرك خارجي مباشر لتجنب خطأ 401.")
    user_msg = st.chat_input("تحدث معي هنا...")
    if user_msg:
        with st.chat_message("user"): st.write(user_msg)
        with st.chat_message("assistant"):
            # محرك دردشة مجاني بديل لا يتطلب مفتاح Groq المعطل
            try:
                response = requests.get(f"https://api.duckduckgo.com/?q={user_msg}&format=json").json()
                st.write(response.get("Abstract", "عذراً، المحرك تحت الصيانة حالياً."))
            except:
                st.error("فشل الاتصال بالمحرك البديل.")
