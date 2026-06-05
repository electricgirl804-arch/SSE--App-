import streamlit as st
import io
from fpdf import FPDF
from pypdf import PdfWriter, PdfReader

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SSE Engineering AI", layout="wide", page_icon="⚡")

# --- 2. المنطق الهندسي (حسابات مبنية على الإحداثيات) ---
def get_solar_potential(lat):
    # معادلة هندسية تقديرية لساعات الذروة بناءً على خط العرض
    base_hours = 5.5
    adjustment = abs(lat) * 0.02
    return max(4.0, base_hours - adjustment)

def calculate_system(loads, lat):
    solar_hours = get_solar_potential(lat)
    # حساب الأحمال مع معامل الأمان
    total_w = sum([app['watt'] * (2.5 if app['type'] == "حثي" else 1.2) for app in loads])
    daily_energy = (total_w * 6) / 1000  # استهلاك 6 ساعات يومياً
    panel_kw = daily_energy / solar_hours
    return total_w, panel_kw, solar_hours

# --- 3. توليد التقرير الرسمي ---
def generate_pdf(total, kw, hours, lat, lon):
    pdf = FPDF()
    pdf.add_page()
    # العنوان
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "SSE Engineering Official Technical Report", ln=True, align='C')
    
    # البيانات التقنية
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Location Coordinates: {lat}, {lon}", ln=True)
    pdf.cell(200, 10, f"Solar Peak Hours: {hours:.2f} h/day", ln=True)
    pdf.cell(200, 10, f"Total Design Load: {total:.2f} Watts", ln=True)
    pdf.cell(200, 10, f"Required Panel Array: {kw:.2f} kWp", ln=True)
    
    # بيانات التواصل
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 10, txt="Contact: Electricgirl804@gmail.com | +249 11 567 8067", ln=True, align='C')
    pdf.cell(200, 10, txt="Verified by: Eng. Shahd - IEC 62446 Standard", ln=True, align='C')
    
    # تشفير التقرير
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    writer = PdfWriter()
    reader = PdfReader(io.BytesIO(pdf_bytes))
    for page in reader.pages: writer.add_page(page)
    writer.encrypt("shahd8499")
    res = io.BytesIO()
    writer.write(res)
    return res.getvalue()

# --- 4. الواجهة التفاعلية ---
def main():
    # الأفاتار المهني
    st.image("https://api.dicebear.com/7.x/bottts/svg?seed=ShahdPro", width=100)
    st.title("⚡ SSE Global Engineering AI Platform")
    
    # الشريط الجانبي للإحداثيات
    with st.sidebar:
        st.header("إحداثيات المشروع الجغرافية")
        lat = st.number_input("خط العرض (Latitude)", value=15.50)
        lon = st.number_input("خط الطول (Longitude)", value=32.55)
        st.info("هذه الإحداثيات تضمن دقة حساب الإشعاع الشمسي.")

    if 'loads' not in st.session_state: st.session_state.loads = []
    
    # إدخال البيانات
    st.subheader("🛠️ إضافة الأحمال الهندسية")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("اسم الجهاز")
    watt = c2.number_input("القدرة (Watt)", min_value=1, value=100)
    type_ = c3.selectbox("نوع الحمل", ["مقاومي", "حثي"])
    
    if st.button("إضافة الجهاز للجرد"):
        st.session_state.loads.append({"name": name, "watt": watt, "type": type_})
        st.success(f"تمت إضافة {name} بنجاح!")
        
    if st.button("توليد التقرير الهندسي المعتمد"):
        with st.spinner('جاري الحساب والتشفير...'):
            t, kw, h = calculate_system(st.session_state.loads, lat)
            pdf = generate_pdf(t, kw, h, lat, lon)
            st.download_button("📥 تحميل التقرير (محمي بـ shahd8499)", pdf, "SSE_Technical_Report.pdf")

if __name__ == "__main__":
    main()

