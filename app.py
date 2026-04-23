import streamlit as st
from groq import Groq
import requests
import time

# 1. إعداد الصفحة بهوية بصرية احترافية
st.set_page_config(page_title="Mustafa Deep Mind", page_icon="🧠", layout="wide")

# 2. تنسيق الواجهة ودعم العربية والخطوط المريحة
st.markdown("""
<style>
    .stApp { text-align: right; direction: rtl; background-color: #f0f2f6; }
    [data-testid="stChatMessageContent"] { text-align: right; direction: rtl; font-family: 'Arial'; }
    .stSpinner { direction: ltr; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 مساعد مصطفى: البحث العميق والذاكرة")
st.caption("هذا البوت يستخدم التفكير المنطقي (Reasoning) ويتذكر سياق حديثك بالكامل.")

# 3. إعداد الذاكرة (Session State) لضمان استمرار المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. إعداد الـ API الخاص بـ Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# 5. عرض تاريخ المحادثة من الذاكرة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"])

# 6. منطقة الإدخال والمعالجة
if prompt := st.chat_input("اطلب منه تفكير عميق، أو ارسم صورة..."):
    # إضافة سؤال المستخدم للذاكرة وعرضه
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # الحالة الأولى: طلب صورة
        if any(word in prompt for word in ["ارسم", "صورة", "تخيل", "draw"]):
            with st.spinner("🚀 جاري معالجة طلبك الفني وتوليد الصورة..."):
                try:
                    clean_prompt = prompt.replace("ارسم", "").replace("صورة", "").strip()
                    # استخدام رابط pollinations مع Seed متغير لضمان التجديد
                    img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_prompt)}?width=1024&height=1024&seed={int(time.time())}"
                    st.image(img_url, caption=f"تم التوليد بناءً على وصفك: {clean_prompt}")
                    st.session_state.messages.append({"role": "assistant", "content": "تفضل هذه الصورة:", "image": img_url})
                except Exception as e:
                    st.error("فشل المحرك في توليد الصورة، جرب وصفاً آخر.")
        
        # الحالة الثانية: التفكير المنطقي والبحث العميق
        else:
            with st.spinner("🔍 جاري التفكير بعمق وتحليل طلبك..."):
                try:
                    # إرسال تاريخ المحادثة بالكامل للموديل ليكون لديه "ذاكرة"
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "أنت مساعد ذكي للمهندس مصطفى. استخدم التفكير المنطقي العميق والبحث في المعلومات قبل الإجابة. أجب باللغة العربية بوضوح."},
                            *st.session_state.messages # هنا يتم إرسال كل الذاكرة السابقة
                        ],
                        temperature=0.7,
                        max_tokens=2048
                    )
                    full_res = response.choices[0].message.content
                    st.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})
                except Exception as e:
                    st.error(f"عذراً يا مصطفى، واجه المحرك صعوبة في التفكير: {e}")

# زر لمسح الذاكرة وبدء جلسة جديدة
if st.sidebar.button("🗑️ مسح الذاكرة"):
    st.session_state.messages = []
    st.rerun()
