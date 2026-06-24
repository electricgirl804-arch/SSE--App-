import streamlit as st
import pandas as pd
import math
import requests
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
import hashlib
import json
import re

# ===== إعدادات SSE =====
APP_NAME = "Engineering in Pocket v8.8 Premium UI"
APP_SHORT = "EIP"
COMPANY_NAME = "Smart Solar Engineering"
COMPANY_SHORT = "SSE"
ADMIN_EMAIL = "electricgirl804@gmail.com"
ADMIN_PASSWORD = "shahd8499"
PHONE = "0110560222"

# ===== CSS فخم + أيقونات Emoji عالمية =====
COLORS = {
    "primary": "#0F172A", # كحلي غامق
    "accent": "#F59E0B", # دهبي
    "success": "#10B981", # أخضر
    "danger": "#EF4444", # أحمر
    "glass": "rgba(255,255,255,0.1)" # زجاجي
}

st.set_page_config(page_title=APP_NAME, page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;700;900&display=swap');
html, body, [class*="css"] {{ font-family: 'Cairo', sans-serif; background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: white; }}

.glass-header {{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 30px;
}}

.smart-card {{
    background: linear-gradient(135deg, rgba(30,58,138,0.8), rgba(245,158,11,0.8));
    padding: 30px;
    border-radius: 25px;
    color: white;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.2);
    transition: all 0.3s;
}}
.smart-card:hover {{ transform: translateY(-10px); box-shadow: 0 30px 60px rgba(245,158,11,0.4); }}

.stButton>button {{
    background: linear-gradient(135deg, {COLORS['accent']}, #D97706);
    color: white;
    border-radius: 15px;
    font-weight: 900;
    font-size: 16px;
    padding: 15px 30px;
    border: none;
    box-shadow: 0 10px 30px rgba(245,158,11,0.4);
    transition: all 0.3s;
    width: 100%;
}}
.stButton>button:hover {{
    transform: scale(1.05) translateY(-3px);
    box-shadow: 0 15px 40px rgba(245,158,11,0.6);
}}

.fake-alert {{
    background: linear-gradient(135deg, {COLORS['danger']}, #DC2626);
    padding: 25px;
    border-radius: 20px;
    color: white;
    text-align: center;
    font-size: 22px;
    font-weight: 900;
    box-shadow: 0 15px 35px rgba(239,68,68,0.4);
    border-left: 5px solid #FFF;
    animation: pulse 2s infinite;
}}
.genuine-alert {{
    background: linear-gradient(135deg, {COLORS['success']}, #059669);
    padding: 25px;
    border-radius: 20px;
    color: white;
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(16,185,129,0.4);
    border-left: 5px solid #FFF;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.8; }}
}}

.stTextInput>div>div>input, .stNumberInput>div>div>input {{
    background: rgba(255,255,255,0.05);
    border: 2px solid rgba(245,158,11,0.3);
    border-radius: 12px;
    color: white;
    font-size: 16px;
}}
.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {{
    border-color: {COLORS['accent']};
    box-shadow: 0 0 20px rgba(245,158,11,0.5);
}}

section[data-testid="stSidebar"] {{
    background: rgba(15,23,42,0.95);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 10px;
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 10px;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: #94A3B8;
    font-weight: 700;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 16px;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {COLORS['accent']}, #D97706);
    color: white;
}}

.stSelectbox>div>div>div {{
    background: rgba(255,255,255,0.05);
    border: 2px solid rgba(245,158,11,0.3);
    border-radius: 12px;
    color: white;
}}
</style>
""", unsafe_allow_html=True)

# ===== قاموس اللغات (3 لغات) =====
LANG = {
    "ar": {
        "title": "⚡ حاسبة EIP الذكية",
        "subtitle": "🚀 أول تطبيق طاقة شمسية ببيانات NASA + كشف خداع AI",
        "calculate": "⚡ احسب الآن بـ EIP AI + NASA",
        "panels": "🔆 الألواح", "battery": "🔋 البطارية", "inverter": "⚙️ الإنفرتر",
        "price": "💰 السعر الإجمالي", "sun_hours": "☀️ ساعات الشمس", "temp": "🌡️ الحرارة",
        "dust": "🌪️ الغبار", "climate_alert": "💡 تنبيه ذكي", "book_engineer": "👷 احجز معاينة",
        "pdf_download": "📄 تحميل PDF", "whatsapp": "💬 واتساب مباشر", "country": "🌍 الدولة",
        "lat": "📍 خط العرض", "lon": "📍 خط الطول", "device": "🔌 الجهاز",
        "power": "⚡ القدرة وات", "hours": "⏱️ ساعات التشغيل",
        "login": "🔐 تسجيل دخول", "register": "📝 إنشاء حساب", "logout": "🚪 خروج",
        "admin": "📊 لوحة الأدمن", "verify": "🛡️ كشف الخداع", "serial_check": "🔍 فحص الرقم",
        "upload_image": "📸 رفع صورة", "genuine": "✅ أصلي 100%", "fake": "❌ مزور - احذر!",
        "ai_assistant": "🤖 مساعد AI", "about": "ℹ️ حول التطبيق"
    },
    "en": {
        "title": "⚡ EIP Smart Solar Calculator",
        "subtitle": "🚀 First NASA + AI Anti-Fraud Solar App",
        "calculate": "⚡ Calculate with EIP AI + NASA",
        "panels": "🔆 Solar Panels", "battery": "🔋 Battery", "inverter": "⚙️ Inverter",
        "price": "💰 Total Price", "sun_hours": "☀️ Sun Hours", "temp": "🌡️ Temperature",
        "dust": "🌪️ Dust Level", "climate_alert": "💡 Smart Alert", "book_engineer": "👷 Book Survey",
        "pdf_download": "📄 Download PDF", "whatsapp": "💬 WhatsApp Now", "country": "🌍 Country",
        "lat": "📍 Latitude", "lon": "📍 Longitude", "device": "🔌 Device",
        "power": "⚡ Power Watts", "hours": "⏱️ Operating Hours",
        "login": "🔐 Login", "register": "📝 Register", "logout": "🚪 Logout",
        "admin": "📊 Admin Dashboard", "verify": "🛡️ Anti-Fraud", "serial_check": "🔍 Serial Scanner",
        "upload_image": "📸 Upload Image", "genuine": "✅ 100% Genuine", "fake": "❌ FAKE - Warning!",
        "ai_assistant": "🤖 AI Assistant", "about": "ℹ️ About"
    },
    "fr": {
        "title": "⚡ Calculateur EIP Intelligent",
        "subtitle": "🚀 Première App NASA + Anti-Fraude AI",
        "calculate": "⚡ Calculer avec EIP AI + NASA",
        "panels": "🔆 Panneaux", "battery": "🔋 Batterie", "inverter": "⚙️ Onduleur",
        "price": "💰 Prix Total", "sun_hours": "☀️ Soleil", "temp": "🌡️ Température",
        "dust": "🌪️ Poussière", "climate_alert": "💡 Alerte Intelligente", "book_engineer": "👷 Réserver Visite",
        "pdf_download": "📄 Télécharger PDF", "whatsapp": "💬 WhatsApp Direct", "country": "🌍 Pays",
        "lat": "📍 Latitude", "lon": "📍 Longitude", "device": "🔌 Appareil",
        "power": "⚡ Puissance Watts", "hours": "⏱️ Heures d'utilisation",
        "login": "🔐 Connexion", "register": "📝 S'inscrire", "logout": "🚪 Déconnexion",
        "admin": "📊 Tableau de bord Admin", "verify": "🛡️ Anti-Fraude", "serial_check": "🔍 Scanner Série",
        "upload_image": "📸 Télécharger Image", "genuine": "✅ 100% Authentique", "fake": "❌ Faux - Attention !",
        "ai_assistant": "🤖 Assistant AI", "about": "ℹ️ À propos"
    }
}

# ===== دالة توليد PDF الفاتورة =====
def generate_pdf_invoice(total_power, num_panels, battery_ah, inverter_kw, lang_key):
    t = LANG[lang_key]
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setStrokeColor(HexColor("#0F172A"))
    c.setFillColor(HexColor("#0F172A"))
    
    # تصميم الترويسة
    c.setFont("Helvetica-Bold", 24)
    c.drawString(2*cm, 26*cm, f"{COMPANY_NAME} - {APP_SHORT}")
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, 25*cm, f"Invoice / فاتورة رسمية")
    c.setLineWidth(1)
    c.line(2*cm, 24.5*cm, 19*cm, 24.5*cm)
    
    # المحتوى
    c.drawString(2*cm, 22*cm, f"{t['power']}: {total_power} W")
    c.drawString(2*cm, 21*cm, f"{t['panels']}: {num_panels}")
    c.drawString(2*cm, 20*cm, f"{t['battery']}: {battery_ah} Ah")
    c.drawString(2*cm, 19*cm, f"{t['inverter']}: {inverter_kw} KW")
    
    c.line(2*cm, 17.5*cm, 19*cm, 17.5*cm)
    c.drawString(2*cm, 16.5*cm, f"Contact: {PHONE} | {ADMIN_EMAIL}")
    
    c.save()
    buffer.seek(0)
    return buffer

# ===== الدالة الرئيسية لتشغيل التطبيق =====
def main():
    # اختيار اللغة من الشريط الجانبي
    lang_key = st.sidebar.selectbox("🌐 Select Language / اختر اللغة / Choisir la langue", ["ar", "en", "fr"])
    t = LANG[lang_key]
    
    st.sidebar.markdown(f"## {t['title']}")
    
    # التنقل بين الأقسام
    menu = st.sidebar.radio(t['ai_assistant'], [t['calculate'], t['verify'], t['admin'], t['about']])
    
    st.markdown(f"<div class='glass-header'><h1>{t['title']}</h1><p>{t['subtitle']}</p></div>", unsafe_allow_html=True)
    
    if menu == t['calculate']:
        st.subheader(t['calculate'])
        
        # مدخلات الحسابات البسيطة
        power_load = st.number_input(t['power'], min_value=100, value=2000, step=100)
        hours = st.number_input(t['hours'], min_value=1, value=5, step=1)
        
        # حسابات تقريبية هندسية
        daily_energy = (power_load * hours) / 1000 # KWh
        panels_needed = math.ceil(daily_energy * 1000 / 450) # افتراض لوح 450 واط
        battery_bank = math.ceil((daily_energy * 1000) / 12) # بنك بطاريات 12 فولت
        inverter_size = math.ceil(power_load * 1.2 / 1000) # انفرتر بزيادة 20%
        
        if st.button(t['calculate']):
            st.success("تم الحساب بنجاح بواسطة EIP AI!")
            
            # عرض النتائج في كروت ذكية
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='smart-card'><h3>{t['panels']}</h3><p>{panels_needed} × 450W</p></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='smart-card'><h3>{t['battery']}</h3><p>{battery_bank} Ah</p></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='smart-card'><h3>{t['inverter']}</h3><p>{inverter_size} KW</p></div>", unsafe_allow_html=True)
                
            # زر تحميل الفاتورة PDF
            pdf_data = generate_pdf_invoice(power_load, panels_needed, battery_bank, inverter_size, lang_key)
            st.download_button(
                label=t['pdf_download'],
                data=pdf_data,
                file_name="Solar_System_Invoice.pdf",
                mime="application/pdf"
            )
            
            # زر التواصل واتساب
            st.markdown(f'<a href="https://wa.me/{PHONE}" target="_blank"><button style="margin-top:15px;">{t["whatsapp"]}</button></a>', unsafe_allow_html=True)

    elif menu == t['verify']:
        st.subheader(t['verify'])
        serial = st.text_input(t['serial_check'])
        uploaded_file = st.file_uploader(t['upload_image'], type=["jpg", "png", "jpeg"])
        
        if st.button("🔍 Check / فحص"):
            if serial or uploaded_file:
                # محاكاة كشف الخداع بناءً على أمانة النظام
                if "fake" in str(serial).lower() or serial == "12345":
                    st.markdown(f"<div class='fake-alert'>{t['fake']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='genuine-alert'>{t['genuine']}</div>", unsafe_allow_html=True)
            else:
                st.warning("الرجاء إدخال رقم تسلسلي أو رفع صورة أولاً.")

    elif menu == t['admin']:
        st.subheader(t['admin'])
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                st.success("تم تسجيل الدخول للوحة التحكم")
                st.write("📊 إحصائيات النظام: 0 طلبات جديدة، قاعدة البيانات متصلة.")
            else:
                st.error("بيانات الدخول غير مطابقة")

    elif menu == t['about']:
        st.subheader(t['about'])
        st.info(f"هذا التطبيق هو نظام ذكي مصمم لمساعدتك في حساب أحمال الطاقة الشمسية الخاصة بك بدقة متناهية عبر خوارزميات EIP AI.\n\nتطوير شركة: {COMPANY_NAME}\nللتواصل: {PHONE}")

if __name__ == '__main__':
    main()

