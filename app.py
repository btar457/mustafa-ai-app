import streamlit as st
from groq import Groq
import requests

# إعدادات الصفحة لتظهر بشكل تطبيق محترف
st.set_page_config(page_title="Mustafa AI Assistant", page_icon="🚀")

# إضافة CSS لدعم اللغة العربية (من اليمين لليسار)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div.stButton > button { width: 100%; }
    </style>
    """, unsafe_allow_context=True)

st.title("🤖 مساعد مصطفى الذكي")
st.info("اسألني أي سؤال أو اطلب مني رسم صورة (مثلاً: ارسم نمر في غابة)")

# إعداد الـ API
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"])

# صندوق الإدخال
if prompt := st.chat_input("اكتب سؤالك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # منطق توليد الصور
        if any(word in prompt for word in ["ارسم", "صورة", "تخيل", "draw"]):
            img_url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=1024&height=1024&seed=42"
            st.markdown("تفضل، هذه الصورة التي طلبتها:")
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": "تم توليد الصورة بنجاح", "image": img_url})
        else:
            # منطق الرد النصي من Groq
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                full_response = response.choices[0].message.content
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
