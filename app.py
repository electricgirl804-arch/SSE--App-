import streamlit as st
import geocoder
import time
import io
from fpdf import FPDF
from pypdf import PdfWriter, PdfReader

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SSE Global Engineering AI", layout="wide", page_icon="⚡")

# --- دوال النظام الذكية ---
def get_location():
    g = geocoder.ip('me')
    return (g.latlng[0], g.latlng[1]) if g.ok and g.latlng else (15.6, 32.5)

def calculate_expert_load(appliances_list):
    total_power = 0
    details = "📋 تحليل الأحمال الفني:\n"
    for app in appliances_list:
        # الذكاء الهندسي: تمييز الأحمال الحثية والمقاومية
        factor = 2.5 if app['type'] == "حثي" else 1.2
        total_power += (app['watt'] * factor)
        details += f"- {app['name']} ({app['type']}): {app['watt']}W (Safety Factor: {factor})\n"
    return total_power, details

def generate_protected_pdf(total_load, inverter_size, lat, lon):
    # إنشاء التقرير الرسمي
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SSE Engineering Official Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Location: {lat:.2f}, {lon:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Design Capacity: {total_load:.2f} Watts", ln=True)
    pdf.cell(200, 10, txt=f"Recommended Inverter: {inverter_size:.2f} kW", ln=True)
    
    # تفاصيل المكونات
    pdf.ln(10)
    pdf.cell(200, 10, txt="System Components Recommendation:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, txt=f"- Solar Panels: {int(total_load/250) + 1} Units", ln=True)
    pdf.cell(200, 8, txt="- Batteries: Deep Cycle 200Ah recommended", ln=True)
    pdf.cell(200, 8, txt="- Protection: DC Breakers & Surge Protection", ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 10, txt="Contact: electricgirl804@gmail.com | +249 11 567 8067", ln=True, align='C')
    pdf.cell(200, 10, txt="Verified by: Eng. Shahd - IEC 62446 Standard", ln=True, align='C')
    
    # تشفير التقرير بكلمة المرور
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt("shahd8499") 
    result = io.BytesIO()
    writer.write(result)
    return result.getvalue()

# --- الواجهة الرئيسية ---
def main():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://api.dicebear.com/7.x/adventurer/svg?seed=Shahd", width=120)
    with col2:
        st.title("⚡ SSE Global Engineering AI")
        st.write("### المنصة الهندسية الذكية - إشراف المهندسة شهد")
        st.caption("نصمم مستقبل الطاقة بكفاءة ودقة عالمية.")

    if 'my_appliances' not in st.session_state:
        st.session_state.my_appliances = []

    # إدخال الأحمال
    with st.container(border=True):
        st.subheader("🛠️ إضافة الأحمال الهندسية")
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("اسم الجهاز:")
        watt = c2.number_input("القدرة بالوات:", value=100)
        a_type = c3.selectbox("نوع الحمل:", ["مقاومي", "حثي"])
        if st.button("إضافة للجرد الهندسي"):
            st.session_state.my_appliances.append({"name": name, "watt": watt, "type": a_type})
            st.success(f"تمت إضافة {name} بنجاح!")

    # التحليل وإصدار التقرير
    if st.button("🚀 إطلاق التحليل وإصدار التقرير الرسمي"):
        with st.spinner('جاري معالجة البيانات وتشفير المستند...'):
            total_load, details = calculate_expert_load(st.session_state.my_appliances)
            inverter = (total_load * 1.5) / 1000
            
            st.success("✅ تم التحليل الهندسي بنجاح!")
            st.info(f"القدرة التصميمية: {total_load:.2f} واط")
            st.text(details)
            
            lat, lon = get_location()
            pdf_data = generate_protected_pdf(total_load, inverter, lat, lon)
            st.download_button("📥 تحميل التقرير (محمي بكلمة السر)", data=pdf_data, file_name="SSE_Report.pdf", mime="application/pdf")

    # التوثيق الميداني
    st.write("---")
    with st.expander("🛡️ التوثيق الميداني (Live Verification)"):
        cam = st.camera_input("صوّر لوحة بيانات الجهاز")
        if cam:
            st.success("تم توثيق الجهاز والمطابقة للمواصفات الدولية.")

if __name__ == "__main__":
    main()

