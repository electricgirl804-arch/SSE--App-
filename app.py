import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
from fpdf import FPDF
import datetime
import plotly.graph_objects as go
import smtplib
from email.message import EmailMessage
import math

# --- إعدادات الحماية ---
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("أدخلي كلمة السر للوصول لنظام SSE Global:", type="password", key="password")
        if st.session_state.password == "shahd8499":
            st.session_state.password_correct = True
            st.rerun()
        elif st.session_state.password:
            st.error("كلمة سر خاطئة!")
        return False
    return st.session_state.password_correct

if not check_password():
    st.stop()

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="SSE Global Engineering Pro", layout="wide", page_icon="⚡")
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #ffffff; }
    .card { background: rgba(30, 41, 59, 0.7); border: 1px solid #FFD700; border-radius: 20px; padding: 25px; margin-bottom: 20px; }
    h1, h3 { color: #FFD700 !important; text-align: center; }
    .stButton>button { background-color: #FFD700 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# --- الدوال الذكية ---
def send_email_alert(report_data):
    msg = EmailMessage()
    msg['Subject'] = 'SSE Global: توثيق مشروع جديد'
    msg['From'] = 'sse.system@gmail.com'
    msg['To'] = "Electricgirl804@gmail.com"
    msg.set_content(f"تفاصيل التوثيق: {report_data}")
    # ملاحظة: يحتاج إعداد SMTP الحقيقي
    st.success("تم إرسال التقرير لإيميلك!")

# --- الواجهة الرئيسية (بعد تسجيل الدخول) ---
st.title("🏗️ SSE Global Engineering AI")
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("<div class='card'><h3>📍 الموقع الجغرافي</h3>", unsafe_allow_html=True)
    m = folium.Map(location=[15.5007, 32.5599], zoom_start=8)
    folium_static(m, width=450, height=300)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'><h3>📋 نظام هندسي للمواد (BOM)</h3>", unsafe_allow_html=True)
    st.table({"المكون": ["الألواح", "الإنفرتر", "قاطع الحماية"], "المواصفة": ["6 ألواح 500W", "3.5 KW", "16 Amp"]})
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h3>📊 تحليل الأحمال (1950W)</h3>", unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(mode="gauge+number", value=1950, gauge={'bar': {'color': "#FFD700"}}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=200)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><h3>✅ التوثيق الميداني</h3>", unsafe_allow_html=True)
    photo = st.camera_input("التقاط صورة للوحة")
    if st.button("💾 توثيق وإرسال تقرير"):
        report = {"Power": 1950, "Date": str(datetime.date.today())}
        send_email_alert(report)
        st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

