import streamlit as st
from groq import Groq
import requests
import time
import re

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="Mustafa Brain V4", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { text-align: right; direction: rtl; }
    [data-testid="stChatMessageContent"] { text-align: right; direction: rtl; }
    div.stSpinner > div { direction: ltr; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ العقل الفائق: النسخة المستقرة")

# 2. تعريف المفاتيح والمكتبات
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# 3. إدارة الذاكرة بشكل صارم
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة (مع حماية ضد البيانات التالفة)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_url" in message:
            st.image(message["image_url"], use_container_width=True)

# 4. محرك المعالجة الرئيسي
if prompt := st.chat_input("تحدث معي أو اطلب صورة..."):
    # إضافة طلب المستخدم للذاكرة
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # أولاً: التحقق إذا كان الطلب "صورة"
        image_keywords = ["ارسم", "صورة", "تخيل", "draw", "image", "imagine"]
        if any(word in prompt.lower() for word in image_keywords):
            with st.spinner("🎨 جاري ابتكار الصورة..."):
                try:
                    # استخراج الوصف فقط
                    clean_desc = re.sub(r'|'.join(image_keywords), '', prompt, flags=re.IGNORECASE).strip()
                    seed = int(time.time())
                    img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={seed}&nologo=true"
                    
                    st.image(img_url, caption=f"خيال مصطفى: {clean_desc}", use_container_width=True)
                    # تخزين الصورة في الذاكرة للعرض فقط
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"لقد رسمت لك: {clean_desc}", 
                        "image_url": img_url
                    })
                except Exception as e:
                    st.error("فشل محرك الصور، حاول مرة أخرى.")
        
        # ثانياً: معالجة النصوص (مع نظام تنظيف الذاكرة الصارم)
        else:
            with st.spinner("🔍 تفكير منطقي..."):
                try:
                    # القائمة النظيفة: نرسل فقط النصوص (role و content) لـ Groq
                    # هذا يمنع خطأ 400 نهائياً لأنه يحذف أي مفاتيح إضافية مثل image_url
                    api_messages = []
                    api_messages.append({"role": "system", "content": "أنت مساعد مهندس مصطفى الذكي. تتذكر السياق وتجيب بالعربي."})
                    
                    for m in st.session_state.messages:
                        api_messages.append({"role": m["role"], "content": str(m["content"])})

                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=api_messages,
                        temperature=0.7
                    )
                    
                    response = completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"حدث خطأ في استجابة المحرك: {e}")

# 5. شريط التحكم الجانبي
with st.sidebar:
    st.header("إدارة التطبيق")
    if st.button("🗑️ مسح الذاكرة (حل المشاكل)"):
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    st.write("موديل التفكير: Llama 3.3 70B")
