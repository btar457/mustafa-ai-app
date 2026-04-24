Import streamlit as st
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import numpy as np
import logging
import speech_recognition as sr
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# تعريف سجل الأحداث
logging.basicConfig(level=logging.INFO)

# تعريف نموذج التعلم العميق
def load_model():
    model = keras.Sequential([
        keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Flatten(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# تعريف دالة التحليل
def analyze_image(image):
    model = load_model()
    image = np.array(image)
    image = image.reshape((1, 224, 224, 3))
    prediction = model.predict(image)
    return prediction

# تعريف دالة التعرف على الكلام
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="ar-EG")
            return text
        except sr.UnknownValueError:
            return " لم يتم التعرف على الكلام "

# تعريف دالة تحليل النصوص
def analyze_text(text):
    model = AutoModelForSequenceClassification.from_pretrained("bert-base-arabic")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-arabic")
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(inputs["input_ids"], attention_mask=inputs["attention_mask"])
    return outputs

# تعريف الواجهة المستخدم
st.title("Mustafa AI App")
st.write(" هذا تطبيق مصمم لتحليل الصور و النصوص و الكلام ")

# تعريف نافذة التحميل
upload_file = st.file_uploader("تحميل الصورة", type=["jpg", "jpeg", "png"])

if upload_file is not None:
    image = Image.open(upload_file)
    prediction = analyze_image(image)
    st.write("النتيجة : ", prediction)

# تعريف نافذة التعرف على الكلام
if st.button("التعرف على الكلام"):
    text = recognize_speech()
    st.write("النتيجة : ", text)

# تعريف نافذة تحليل النصوص
text_input = st.text_input("أدخل النص")
if st.button("تحليل النص"):
    outputs = analyze_text(text_input)
    st.write("النتيجة : ", outputs)
