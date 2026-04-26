import streamlit as st
import requests
import time
import random
from groq import Groq

# 1. إلغاء أي تنسيقات CSS قد تسبب تداخل (الحل الجذري لمشكلة النصوص الطولية)
st.set_page_config(page_title="Mustafa Pro", layout="centered")

# 2. تهيئة المحرك بمفتاحك (تأكد من صحة المفتاح في Secrets)
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "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"))

# 3. واجهة بسيطة جداً (Tabs) لمنع تداخل القوائم الجانبية في الموبايل
tab1, tab2 = st.tabs(["💬 الشات", "🎨 الصور"])

# --- محرك الشات ---
with tab1:
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    if p := st.chat_input("اكتب سؤالك هنا..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)
        try:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": p}])
            ans = res.choices[0].message.content
            with st.chat_message("assistant"): st.write(ans)
            st.session_state.msgs.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"فشل API الشات: {e}")

# --- محرك الصور (الحل النهائي لمشكلة رقم 0 وفشل التكرار) ---
with tab2:
    st.write("### مولد الصور المستقر")
    # استخدام Key ديناميكي يعتمد على الوقت لضمان تحديث الحقل في كل مرة
    p_img = st.text_input("وصف الصورة:", key="img_input_main")
    
    if st.button("توليد الآن 🚀"):
        if p_img:
            # إضافة (Container) فارغ يتم تحديثه فوراً
            placeholder = st.empty()
            with placeholder.container():
                st.warning("جاري المعالجة... انتظر ظهور الصورة")
                
                # استخدام تقنية الـ Cache Busting لضمان عدم تكرار "0" أو الصورة القديمة
                ts = int(time.time())
                seed = random.randint(1, 1000000)
                # الرابط المباشر والقوي
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(p_img)}?width=1024&height=1024&seed={seed}&nologo=true&v={ts}"
                
                # عرض الصورة مع رابط التحميل لضمان الاستجابة
                st.image(url, caption=f"تم التوليد: {p_img}", use_container_width=True)
                st.markdown(f"[🔗 رابط مباشر للصورة]({url})")
