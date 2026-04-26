import streamlit as st
from groq import Groq
import requests
import time
import random

# ====================== إعدادات الواجهة: الحل النهائي للخطوط العشوائية ======================
st.set_page_config(page_title="Mustafa King AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    /* إغلاق كافة الثغرات التي تسمح بظهور خطوط عمودية أو نصوص متداخلة */
    html, body, [class*="css"], .stMarkdown, p, div {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* إصلاح العنوان الذي كان يظهر بشكل طولي في الموبايل */
    .app-title {
        font-size: 2rem;
        font-weight: 900;
        color: #1e3a8a;
        text-align: center !important;
        width: 100%;
        display: block;
        margin: 20px 0;
    }

    /* تنظيف الشاشة من أي حدود (Borders) افتراضية تسبب الخط العمودي */
    [data-testid="stSidebar"], [data-testid="stVerticalBlock"], .stChatMessage {
        border: none !important;
    }

    /* تنسيق الصورة لضمان التحميل السلس */
    .stImage > img {
        border-radius: 15px;
        border: 2px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ====================== تهيئة المحركات (Groq API) ======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "gallery" not in st.session_state: st.session_state.gallery = []

# ====================== القائمة الجانبية المستقرة ======================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚙️ الإعدادات</h2>", unsafe_allow_html=True)
    mode = st.radio("اختر الوضع المخصص:", ["💬 الدردشة الذكية", "🎨 توليد الصور", "🔍 التحليل العميق"])
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.chat_history = []
        st.session_state.gallery = []
        st.rerun()

st.markdown(f'<div class="app-title">{mode}</div>', unsafe_allow_html=True)

# ====================== الأنماط التشغيلية ======================

# 1. وضع الدردشة (Streaming & Logic)
if mode == "💬 الدردشة الذكية":
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("تحدث معي يا مصطفى..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            res_box = st.empty()
            full_ans = ""
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "أنت مساعد مهندس خبير وصريح."}] + st.session_state.chat_history[-8:],
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_ans += chunk.choices[0].delta.content
                        res_box.markdown(full_ans + "▌")
                res_box.markdown(full_ans)
                st.session_state.chat_history.append({"role": "assistant", "content": full_ans})
            except:
                st.error("تأكد من مفتاح الـ API الخاص بك.")

# 2. وضع توليد الصور (الإصلاح الجذري لمشكلة الـ 0 والتعليق)
elif mode == "🎨 توليد الصور":
    st.info("اكتب وصفك وسأقوم بتوليد صورة احترافية فوراً.")
    
    # استخدام حاوية مستقلة لضمان استقرار الإدخال في الموبايل
    user_p = st.text_area("وصف الصورة:", placeholder="غزال في غابة ليلية تحت ضوء القمر...", key="unique_img_input")
    
    if st.button("🚀 ابدأ التوليد"):
        if user_p:
            with st.spinner("🎨 جاري الرسم..."):
                # محاولة تحسين البرومبت للغة الإنجليزية (إذا فشل الـ API سيستخدم النص الأصلي)
                try:
                    enhance = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Translate and enhance to detailed image prompt. English only."},
                                  {"role": "user", "content": user_p}]
                    )
                    final_p = enhance.choices[0].message.content
                except:
                    final_p = user_p

                # بناء الرابط بأسلوب يمنع الـ Caching وفشل التحميل
                seed = random.randint(1, 9999999)
                img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(final_p)}?width=1024&height=1024&nologo=true&seed={seed}&v={time.time()}"
                
                # تخزين في الجلسة لعرض الصور تحت بعضها
                st.session_state.gallery.insert(0, {"url": img_url, "prompt": user_p})

    # عرض الجاليري (الأحدث دائماً في الأعلى)
    for item in st.session_state.gallery:
        with st.container():
            st.markdown(f"**النتيجة لـ:** {item['prompt']}")
            st.image(item['url'], use_container_width=True)
            st.markdown("---")

# 3. وضع التحليل العميق
elif mode == "🔍 التحليل العميق":
    query = st.text_area("أدخل الموضوع الذي تود تحليله هندسياً أو تقنياً:")
    if st.button("🔎 بدء التحليل"):
        with st.spinner("جاري التفكير والتحليل..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "أنت باحث تقني خبير."}, {"role": "user", "content": query}]
            )
            st.markdown(res.choices[0].message.content)

st.markdown("<br><p style='text-align:center; color:silver;'>Mustafa King AI | Professional Development</p>", unsafe_allow_html=True)
