import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF # مكتبة إنشاء التقارير الرسمية

# --- دالة إنشاء التقرير الفني (PDF) ---
def create_pdf_report(load, device, panels):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SSE Global Engineering - Official Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Client System: {device}", ln=True)
    pdf.cell(200, 10, txt=f"Total Load: {load} Watt", ln=True)
    pdf.cell(200, 10, txt=f"Recommended Panels: {panels}", ln=True)
    pdf.cell(200, 10, txt="Verified by: Eng. Shahd - AI System", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- الجزء المتبقي من الواجهة الذكية ---
if st.sidebar.button("تصدير التقرير الفني الموثق (PDF)"):
    panels, _, _ = get_analysis(load, device, cost) # باستخدام المحرك السابق
    pdf_data = create_pdf_report(load, device, panels)
    st.sidebar.download_button(
        label="📥 تحميل التقرير الآن",
        data=pdf_data,
        file_name="SSE_Engineering_Report.pdf",
        mime="application/pdf"
    )
    st.sidebar.success("تم تجهيز التقرير للهندسة!")

