import streamlit as st
from groq import Groq
import requests
import time
import re

# 1. إعداد الصفحة الأساسي (بدون CSS معقد)
st.set_page_config(page_title="Mustafa AI Pro", layout="centered")

# عنوان التطبيق واضح وكبير
st.title("🤖 مساعد مصطفى المهندس")
st.write("---") # خط فاصل بسيط ونظيف

# 2. إعداد الذاكرة والـ API
if "messages" not in st.session_state:
    st.session_state.messages = []

# مفتاح Groq الخاص بك
client = Groq(api_key="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")

# 3. عرض المحادثة (باستخدام نظام الفقاعات الأصلي من Streamlit)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "image_url" in message:
            st.image(message["image_url"])

# 4. منطقة الإدخال
if prompt := st.chat_input("اسألني أي شيء أو اطلب صورة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # طلب الصور
        if any(w in prompt for w in ["ارسم", "صورة", "تخيل"]):
            with st.spinner("🎨 جاري التوليد..."):
                clean_desc = re.sub(r'(ارسم|صورة|تخيل)', '', prompt).strip()
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={int(time.time())}"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": f"تم توليد: {clean_desc}", "image_url": img_url})
        
        # الرد النصي الذكي (Groq)
        else:
            with st.spinner("🔍 جاري التفكير..."):
                try:
                    # تصفية الذاكرة من الصور لضمان عدم حدوث خطأ 400
                    clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "image_url" not in m]
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مهندس ميكانيك ذكي. أجب بالعربية بوضوح واختصار."}] + clean_history
                    )
                    res = response.choices[0].message.content
                    st.write(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                except Exception as e:
                    st.error("فشل الاتصال بالمخ الذكي، حاول مرة أخرى.")

# 5. القائمة الجانبية لإدارة الجلسة
with st.sidebar:
    st.header("⚙️ الإعدادات")
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    st.write("تم التطوير خصيصاً للمهندس مصطفى.")
