import streamlit as st
from groq import Groq
import requests
import time
import re

# 1. إعداد الصفحة بهوية بصرية احترافية
st.set_page_config(page_title="Mustafa Super-Brain", page_icon="🤯", layout="wide")

# 2. تنسيق الواجهة ودعم العربية (RTL) بشكل كامل
st.markdown("""
<style>
    .stApp { text-align: right; direction: rtl; background-color: #f4f6f9; }
    [data-testid="stChatMessageContent"] { text-align: right; direction: rtl; font-family: 'Arial', sans-serif; font-size: 1.1rem; }
    div.stSpinner > div { direction: ltr; }
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0);}
</style>
""", unsafe_allow_html=True)

st.title("🤯 العقل الفائق (Mustafa Super-Brain)")
st.caption("تفكير منطقي، ذاكرة كاملة، وأداة تخيل صور مدمجة (Grok Style).")

# 3. إعداد الـ API الخاص بـ Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# 4. إعداد الذاكرة ودورة حياة المحادثة (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة التاريخية
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            # استخدام عرض Container Width لملء الشاشة على S23
            st.image(message["image"], use_container_width=True)

# 5. دوال الأدوات الخارجية (External Tools)

def generate_image_tool(user_prompt):
    """أداة تخيل وتوليد صور: Grok Style"""
    # تنظيف النص للحصول على الوصف الفني فقط
    clean_description = re.sub(r'(ارسم|صورة|تخيل|draw|image|imagine)', '', user_prompt, flags=re.IGNORECASE).strip()
    
    if not clean_description:
        return None, "عذراً يا مصطفى، لم أفهم وصف الصورة جيداً. هل يمكنك إعادة كتابته؟"

    with st.spinner("🚀 Grok Style Imaging: جاري الاتصال بمحرك التخيل وتوليد الصورة..."):
        try:
            # تحويل النص لرابط متوافق مع Pollinations
            encoded_prompt = requests.utils.quote(clean_description)
            # استخدام seed متغير لضمان صورة جديدة كل مرة
            seed = int(time.time())
            img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
            
            # التأكد من أن الرابط يعمل (اختياري لكن مفيد للاستقرار)
            # requests.head(img_url, timeout=5) 
            
            return img_url, f"✅ تم تخيل الصورة بناءً على وصفك: {clean_description}"
        except Exception as e:
            return None, f"❌ فشل محرك التخيل في الاتصال. الخطأ: {e}"

def generate_text_response(chat_history):
    """دالة التفكير المنطقي النصي مع معالجة الأخطاء"""
    with st.spinner("🔍 Deep Thought: جاري التفكير بعمق وتحليل السياق..."):
        try:
            # الموديل الأكبر للتفكير الأعمق والذاكرة
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "أنت مساعد مهندس مصطفى، مساعد فائق الذكاء، تستخدم التفكير المنطقي العميق. تتذكر كل تاريخ المحادثة. تجيب باللغة العربية بوضوح واسهاب عند الحاجة."},
                    *chat_history # إرسال الذاكرة بالكامل
                ],
                temperature=0.6, # توازن بين الإبداع والدقة المنطقية
                max_tokens=3000
            )
            return completion.choices[0].message.content, None
        except Exception as e:
            return None, f"⚠️ واجه العقل الفائق صعوبة في صياغة الرد الآن. حاول مرة أخرى. (الخطأ: {e})"

# 6. منطقة الإدخال والمعالجة (Input Loop)
if prompt := st.chat_input("تحدث معي، أو اطلب تخيل صورة..."):
    # 1. حفظ وعرض سؤال المستخدم في الذاكرة
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. تحليل الطلب: هل هو نص أم صورة؟ (Decision Making)
    is_image_request = any(word in prompt.lower() for word in ["ارسم", "صورة", "تخيل", "draw", "image", "imagine"])

    with st.chat_message("assistant"):
        # الحالة الأولى: تفعيل أداة الصور
        if is_image_request:
            img_url, status_msg = generate_image_tool(prompt)
            if img_url:
                st.image(img_url, caption=status_msg, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "content": status_msg, "image": img_url})
            else:
                st.error(status_msg)
                st.session_state.messages.append({"role": "assistant", "content": status_msg})
        
        # الحالة الثانية: تفعيل محرك التفكير النصي
        else:
            text_response, error_msg = generate_text_response(st.session_state.messages)
            if text_response:
                st.markdown(text_response)
                st.session_state.messages.append({"role": "assistant", "content": text_response})
            else:
                st.error(error_msg)
                # لا نحفظ رسالة الخطأ في الذاكرة لكي لا تفسد سياق المحادثة مستقبلاً

# 7. زر Sidebar لإدارة الجلسة
st.sidebar.title("إعدادات الجلسة")
if st.sidebar.button("🗑️ مسح الذاكرة والبدء من جديد"):
    st.session_state.messages = []
    st.rerun()
