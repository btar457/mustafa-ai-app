import streamlit as st
from groq import Groq
import requests
import time
import re
import io
import json
import os
from datetime import datetime
from PIL import Image

# ====================== إعدادات ======================
st.set_page_config(page_title="Mustafa Engineering Global", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #0e1117; color: white; }
    div.stButton > button { border-radius: 12px; height: 3.8em; background-color: #2e7d32; color: white; border: none; width: 100%; font-weight: bold; }
    .chat-message { border-radius: 15px; padding: 12px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ====================== Secrets (مهم جداً) ======================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY") or os.getenv("NEWS_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ أضف GROQ_API_KEY في .streamlit/secrets.toml")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ====================== حفظ المحادثات (SQLite بسيط) ======================
import sqlite3

def init_db():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (id INTEGER PRIMARY KEY, title TEXT, timestamp TEXT, messages TEXT)''')
    conn.commit()
    conn.close()

def save_conversation(title, messages):
    conn = sqlite3.connect('chats.db
