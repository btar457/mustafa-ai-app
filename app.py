import streamlit as st
from groq import Groq
import requests

# إعداد الصفحة
st.set_page_config(page_title="Mustafa AI Assistant", page_icon="🤖")

# تنسيق الواجهة ودعم العربية
st.markdown("""
<style>
    .stApp { text-align: right; direction: rtl; }
    [data-testid="stChatMessageContent"] { text-align: right; direction: rtl; }
</style>
""", unsafe_allow_context=True)

st.title("🤖 مساعد مصطفى الذكي")

# إعداد الـ API
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"])

# صندوق الإدخال
if prompt := st.chat_input("اسألني أي شيء أو اطلب صورة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if any(word in prompt for word in ["ارسم", "صورة", "تخيل", "draw"]):
            try:
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=1024&height=1024&seed=42"
                st.image(img_url, caption="تم توليدها بواسطة مساعد مصطفى")
                st.session_state.messages.append({"role": "assistant", "content": "تفضل هذه الصورة:", "image": img_url})
            except:
                st.error("عذراً، فشل توليد الصورة.")
        else:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                full_res = response.choices[0].message.content
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")
