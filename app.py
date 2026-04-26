import streamlit as st
from groq import Groq
import requests
import time
import re
from PIL import Image
import io

# 1. إعدادات الواجهة النظيفة (Native Streamlit) لضمان الوضوح على S23
st.set_page_config(page_title="Mustafa Engineering Global", layout="wide")

# تخصيص واجهة المستخدم بشكل بسيط لضمان المتانة
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #0e1117; color: white; }
    /* تنسيق أزرار الأوامر الكبيرة */
    div.stButton > button { 
        border-radius: 10px; height: 3.5em; background-color: #2e7d32; 
        color: white; border: none; width: 100%; font-weight: bold; 
    }
</style>
""", unsafe_allow_html=True)

# 2. تهيئة الذاكرة و APIS
if "messages" not in st.session_state: st.session_state.messages = []
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# 3. شريط التحكم الجانبي (مركز الميزات المتقدمة)
with st.sidebar:
    st.header("⚙️ مركز التحكم")
    tool_mode = st.radio("اختر وضع التشغيل", ["المساعد الذكي", "تحليل الصور", "الأخبار الموثوقة"])
    st.markdown("---")
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.messages = []
        st.rerun()

# 4. محرك الأخبار الموثوقة (News Mode)
if tool_mode == "الأخبار الموثوقة":
    st.header("🌎 موجز الأخبار العالمية الموثوقة")
    # محرك أخبار خارجي لضمان الموثوقية
    NEWS_API_URL = "https://newsapi.org/v2/top-headlines?country=ae&category=technology&apiKey=f7b8849b2c3a4d87a4a905a5d7c3b2e5"
    
    with st.spinner("🔍 جاري جلب أحدث الأخبار التقنية والهندسية..."):
        try:
            response = requests.get(NEWS_API_URL).json()
            articles = response.get("articles", [])[:5] # أهم 5 أخبار
            
            if articles:
                for idx, article in enumerate(articles):
                    st.subheader(f"{idx+1}. {article['title']}")
                    st.write(f"المصدر: {article['source']['name']}")
                    st.write(article['description'])
                    st.markdown(f"({article['url']})")
                    st.markdown("---")
            else:
                st.warning("عذراً، لا توجد أخبار متاحة حالياً.")
        except:
            st.error("فشل الاتصال بمحرك الأخبار.")

# 5. محرك تحليل الصور (Image Analysis Mode)
elif tool_mode == "تحليل الصور":
    st.header("👁️ محرك تحليل وفهم الصور")
    uploaded_image = st.file_uploader("ارفع صورة (مخطط، قطعة ميكانيكية، منظر)...", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_image:
        # عرض الصورة المرفوعة
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("تحليل محتوى الصورة"):
            with st.spinner("🔍 جاري قراءة الصورة بعمق وتحليل ما بداخلها..."):
                # استخدام محرك Groq Vision (إذا توفر) أو الرد السحابي
                # للتوضيح: هنا سنستخدم محرك Groq Vision للرد
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview", # نموذج Groq المخصص للرؤية
                    messages=[
                        {"role": "user", "content": "حلل هذه الصورة الهندسية أو الواقعية بعمق، واشرح ما بداخلها بوضوح وباللغة العربية، وخاصة إذا كان بها تفاصيل ميكانيكية."}
                    ]
                )
                res_text = response.choices[0].message.content
                st.write(res_text)

# 6. المساعد الذكي وتوليد الصور (Chat Mode with Generation)
else:
    st.header("🤖 المساعد الهندسي المتكامل")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image_url" in message: st.image(message["image_url"])

    if prompt := st.chat_input("تحدث، اطلب استشارة، أو اطلب تخيل صورة..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.chat_message("assistant"):
            # محرك توليد الصور حسب الوصف
            if any(w in prompt for w in ["ارسم", "صورة", "تخيل"]):
                with st.spinner("🎨 جاري التوليد الاحترافي..."):
                    clean_desc = re.sub(r'(ارسم|صورة|تخيل)', '', prompt).strip()
                    if not clean_desc: clean_desc = "شيء جميل وميكانيكي"
                    img_url = f"https://pollinations.ai/p/{requests.utils.quote(clean_desc)}?width=1024&height=1024&seed={int(time.time())}"
                    st.image(img_url)
                    st.session_state.messages.append({"role": "assistant", "content": f"تم توليد صورة لـ: {clean_desc}", "image_url": img_url})
            
            # محرك التحليل النصي والبحث العميق
            else:
                with st.spinner("🔍 تفكير ذكي..."):
                    try:
                        clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if "image_url" not in m]
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": "أنت مساعد مهندس ميكانيك ذكي."}] + clean_history
                        )
                        answer = response.choices[0].message.content
                        st.write(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except:
                        st.error("عذراً، فشل المخ الذكي في الرد.")
