import streamlit as st
from groq import Groq
import requests
import time
import re

# 1. إعدادات أساسية لضمان استقرار العرض على S23
st.set_page_config(page_title="Mustafa AI Clean", layout="centered")

# 2. تهيئة الذاكرة في بداية الكود لتجنب أخطاء الأسطر المتأخرة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. إعداد الاتصال بـ Groq
client = Groq(api_key="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")

st.title("🤖 مساعد مصطفى الذكي")
st.write("النسخة المستقرة - بدون أخطاء عرض")

# 4. عرض الرسائل السابقة بشكل بسيط
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"])

# 5. معالجة الإدخال الجديد
if prompt := st.chat_input("تحدث معي هنا..."):
    # حفظ وإظهار رسالة المستخدم فوراً
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # فحص إذا كان الطلب صورة
        if any(w in prompt for w in ["ارسم", "صورة", "تخيل"]):
            with st.spinner("🎨 جاري التوليد..."):
                # السطر 66 المصحح: تنظيف النص بشكل آمن
                clean_desc = re.sub(r'(ارسم|صورة|تخيل)', '', prompt).strip()
                if not clean_desc: clean_desc = "شيء جميل"
                
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={int(time.time())}"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": f"تم توليد صورة لـ: {clean_desc}", "image_url": img_url})
        
        # الرد النصي (إصلاح السطر 66 وما بعده في معالجة الذاكرة)
        else:
            with st.spinner("🔍 تفكير..."):
                try:
                    # تصفية الذاكرة: نرسل فقط role و content كـ نصوص واضحة
                    clean_history = []
                    for m in st.session_state.messages:
                        if "image_url" not in m: # نبعث النصوص بس عشان ما يصير Error 400
                            clean_history.append({"role": m["role"], "content": str(m["content"])})

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مهندس ميكانيك ذكي."}] + clean_history
                    )
                    
                    answer = response.choices[0].message.content
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error("حدث خطأ في معالجة النص، حاول كتابة رسالة قصيرة.")

# القائمة الجانبية
with st.sidebar:
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()
