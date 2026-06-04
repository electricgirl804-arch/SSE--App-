import streamlit as st
import geocoder
import datetime
import math
from fpdf import FPDF
from io import BytesIO
from gtts import gTTS

# --- 1. الدوال التفاعلية ---
def speak(text):
    try:
        tts = gTTS(text=text, lang='ar')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
    except: pass

def calculate_system(total_watts, battery_capacity, dod):
    daily_energy = total_watts * 5
    panels = math.ceil(daily_energy / (450 * 4 * 0.8))
    batteries = math.ceil(daily_energy / (12 * battery_capacity * dod))
    inverter = math.ceil(total_watts * 1.25)
    breaker = math.ceil((total_watts / 12) * 1.25)
    return panels, batteries, inverter, breaker

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SSE Engineering Certified Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    for k, v in data.items(): pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 2. إعدادات النظام ---
st.set_page_config(page_title="SSE - النظام الميداني المتكامل", layout="centered")
st.markdown("""
    <style>
    .card { background: white; padding: 25px; border-radius: 25px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 8px solid #2c3e50; }
    .alert { background-color: #ffcccc; color: #cc0000; padding: 20px; border-radius: 15px; font-weight: bold; text-align: center; }
    .success-box { background-color: #f1f8e9; border: 2px solid #27ae60; padding: 20px; border-radius: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if 'devices' not in st.session_state: st.session_state.devices = {}

st.title("☀️ SSE Engineering")
tab1, tab2, tab3 = st.tabs(["👋 الترحيب", "⚙️ التصميم", "🛡️ التوثيق"])

# تبويب 1: الترحيب
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if st.button("🔊 استمع للترحيب"): speak("أهلاً بك في منصة اس اس اي الهندسية. رفيقك الرقمي لضمان كفاءة طاقتك.")
    g = geocoder.ip('me')
    st.metric("الموقع الجغرافي", f"{g.lat if g.lat else 15.5:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

# تبويب 2: التصميم والإنذار
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    name = st.text_input("اسم الجهاز:")
    power = st.number_input("القدرة (وات):", min_value=10)
    if st.button("➕ إضافة للجرد"): st.session_state.devices[name] = power
    
    total = sum(st.session_state.devices.values())
    if total > 5000:
        st.markdown("<div class='alert'>⚠️ إنذار: الحمل يتجاوز السعة المصممة!</div>", unsafe_allow_html=True)
        speak("تنبيه، الحمل الزائد يتجاوز القدرة المصممة للنظام.")
    
    cap = st.number_input("سعة البطارية (Ah):", value=200)
    dod = st.slider("عمق التفريغ (DoD %):", 10, 50, 20) / 100
    
    if total > 0:
        p, b, inv, br = calculate_system(total, cap, dod)
        st.table({"المكون": ["ألواح", "بطاريات", "أنفرتر", "قاطع"], "النتيجة": [f"{p} لوح", f"{b} بطارية", f"{inv}W", f"{br}A"]})
    st.markdown("</div>", unsafe_allow_html=True)

# تبويب 3: التوثيق والخاتمة
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    img = st.camera_input("افحص الموقع لالاعتماد")
    if img:
        st.success("تم التوثيق بنجاح!")
        speak("تم اعتماد المشروع بنجاح، شكراً لثقتكم في نظام اس اس اي.")
        st.markdown("<div class='success-box'><h2>✅ تم الاعتماد الهندسي</h2><p>SSE Engineering - الجودة عنواننا</p></div>", unsafe_allow_html=True)
        pdf = create_pdf({"التاريخ": str(datetime.date.today()), "الحمل الكلي": str(sum(st.session_state.devices.values()))})
        st.download_button("📥 تحميل التقرير الختامي", data=pdf, file_name="SSE_Final_Report.pdf")
    st.markdown("</div>", unsafe_allow_html=True)

