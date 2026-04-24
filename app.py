import streamlit as st
from groq import Groq
import requests
import time
import re

# 1. إعداد الصفحة (نظام مركزي بسيط جداً لضمان الوضوح)
st.set_page_config(page_title="Mustafa AI", layout="centered")

# 2. حذف كل أكواد CSS المخصصة التي تسبب الخطوط العشوائية
# نعتمد فقط على التنسيق التلقائي لـ Streamlit الذي يتوافق مع S23

st.title("🤖 مساعد مصطفى الذكي")
st.write("---") # خط فاصل بسيط لفصل العنوان عن المحادثة

# 3. إعداد الذاكرة والـ API
if "messages" not in st.session_state:
    st.session_state.messages = []

client = Groq(api_key="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")

# 4. عرض المحادثة (استخدام المكونات الأصلية فقط)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "image_url" in message:
            st.image(message["image_url"], use_container_width=True)

# 5. منطقة الإدخال والمعالجة
if prompt := st.chat_input("تحدث معي، أو اطلب تخيل صورة..."):
    # إضافة رسالة المستخدم للذاكرة
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # ميزة الصور (توليد خارجي)
        if any(w in prompt for w in ["ارسم", "صورة", "تخيل"]):
            with st.spinner("🎨 جاري التوليد..."):
                clean_desc = re.sub(r'(ارسم|صورة|تخيل)', '', prompt).strip()
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={int(time.time())}"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": f"تم توليد: {clean_desc}", "image_url": img_url})
        
        # الرد النصي الذكي
        else:
            with st.spinner("🔍 تفكير..."):
                try:
                    # تصفية الذاكرة لمنع خطأ 400
                    clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "image_url" not in m]
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "أنت مساعد مصطفى، مهندس خبير. أجب بالعربي بوضوح."}] + clean_history
                    )
                    res_text = response.choices[0].message.content
                    st.write(res_text)
                    st.session_state.messages.append({"role": "assistant", "content": res_text})
                except Exception as e:
                    st.error("عذراً، حدث خطأ في الاتصال.")

# 6. شريط جانبي نظيف
with st.sidebar:
    st.header("⚙️ الإعدادات")
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages =
