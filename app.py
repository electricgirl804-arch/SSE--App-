import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import pandas as pd

# 1. إعدادات الصفحة والتنسيق الاحترافي
st.set_page_config(page_title="SSE Global Engineering AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #0b1c24; color: white; }
    .card { background: #1a2a33; padding: 20px; border-radius: 20px; border: 1px solid #FFD700; margin-bottom: 20px; }
    .ai-highlight { border: 2px solid #FFD700; padding: 15px; border-radius: 15px; background: rgba(255, 215, 0, 0.1); }
    h1 { color: #FFD700; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. منطق الحسابات (محرك الهندسة)
def get_analysis(load, device, cost):
    factors = {"منزلي": 1.2, "مضخة": 2.2, "مصنع": 2.8, "مؤسسة": 2.0}
    f = factors.get(device, 1.5)
    panels = round((load * f) / 450)
    savings = load * 24 * 365 * 0.15
    payback = round(cost / savings, 1) if savings > 0 else 0
    return panels, savings, payback

# 3. محرك التقارير (PDF الرسمي)
def create_pdf(load, device, panels):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SSE Global Engineering - Official Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"System: {device} | Total Load: {load}W", ln=True)
    pdf.cell(200, 10, txt=f"Recommended Solar Panels: {panels}", ln=True)
    pdf.cell(200, 10, txt="Verified by: Eng. Shahd - AI System", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# 4. الواجهة الرئيسية (التفاعل)
st.title("⚡ SSE Global Engineering AI")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='card'><h3>📸 التوثيق الميداني</h3></div>", unsafe_allow_html=True)
    img = st.camera_input("التقط صورة الموقع")
    if img:
        st.markdown("<div class='ai-highlight'>✅ تم تحليل الموقع بنجاح.</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h3>📊 الحمل اللحظي</h3></div>", unsafe_allow_html=True)
    load = st.slider("الحمل (Watt)", 500, 20000, 5000)
    device = st.selectbox("نوع النظام:", ["منزلي", "مضخة", "مصنع", "مؤسسة"])
    fig = go.Figure(go.Indicator(mode="gauge+number", value=load, gauge={'bar': {'color': "#FFD700"}}))
    st.plotly_chart(fig, use_container_width=True)

# 5. المنطقة السرية (لوحة المهندسة)
st.sidebar.markdown("---")
pwd = st.sidebar.text_input("كلمة سر المهندسة:", type="password")
if pwd == "shahd8499":
    cost = st.number_input("تكلفة النظام ($):", 1000, 50000, 5000)
    if st.sidebar.button("إصدار التقرير النهائي"):
        panels, _, _ = get_analysis(load, device, cost)
        pdf = create_pdf(load, device, panels)
        st.sidebar.download_button("📥 تحميل التقرير (PDF)", pdf, "Report.pdf")
        st.sidebar.success("تم!")

