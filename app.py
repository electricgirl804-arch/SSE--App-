import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io
import requests

st.set_page_config(page_title="حاسبة الطاقة الشمسية - السودان", layout="wide")

# 1. قاعدة بيانات الألواح والانفرترات
PANELS = {
    "Jinko 550W Mono": {"pmax": 550, "eff": 21.5},
    "Trina 545W Mono": {"pmax": 545, "eff": 21.3},
    "Canadian 540W Mono": {"pmax": 540, "eff": 21.1}
}

INVERTERS = {
    "Growatt 5kW": {"eff": 97.5},
    "Solis 5kW": {"eff": 97.8},
    "Huawei 5kW": {"eff": 98.2}
}

# 2. قاعدة بيانات الأجهزة - وات + ساعات التشغيل
DEVICES = {
    "💡 لمبة LED 12W": {"watt": 12, "hours": 8},
    "🌀 مروحة سقف 75W": {"watt": 75, "hours": 10},
    "❄️ مكيف اسبلت 1.5 حصان": {"watt": 1200, "hours": 8},
    "🧊 ثلاجة 12 قدم": {"watt": 150, "hours": 24},
    "📺 شاشة 43 بوصة": {"watt": 80, "hours": 6},
    "💻 لابتوب": {"watt": 65, "hours": 8},
    "🔌 شاحن موبايل": {"watt": 15, "hours": 3},
    "💧 مضخة موية 1 حصان": {"watt": 750, "hours": 2},
    "🧺 غسالة 7 كيلو": {"watt": 500, "hours": 1},
    "🍕 ميكروويف": {"watt": 1000, "hours": 0.5}
}

def calc_pvlib_hourly(lat, lon, tilt, azimuth, panel_name, inv_name, losses, system_kw):
    """نجيب بيانات الإشعاع من ناسا NREL مباشر بدون pvlib"""
    try:
        api_key = st.secrets["NREL_API_KEY"]
    except:
        st.error("⚠️ أضيفي NREL_API_KEY في Settings → Secrets")
        return [0]*12, 0, 0

    url = f"https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?wkt=POINT({lon}%20{lat})&names=2023&leap_day=false&utc=false&api_key={api_key}"

    try:
        df = pd.read_csv(url, skiprows=2)
        annual_ghi = df['GHI'].sum() / 1000 # kWh/m2/year

        pr = 100 - sum(losses.values()) # Performance Ratio
        annual_kwh = system_kw * annual_ghi * (pr/100) * 0.85

        # توزيع شهري واقعي للسودان
        monthly_factors = [0.07, 0.08, 0.10, 0.11, 0.10, 0.08, 0.08, 0.08, 0.09, 0.10, 0.08, 0.06]
        monthly = [round(annual_kwh * f) for f in monthly_factors]

        return monthly, round(annual_kwh/1000, 1), round(pr, 1)
    except Exception as e:
        st.error(f"❌ خطأ في جلب بيانات ناسا: {e}")
        return [0]*12, 0, 0

def generate_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-2*cm, "تقرير نظام الطاقة الشمسية - السودان")

    c.setFont("Helvetica", 11)
    y = height-4*cm
    for key, value in data.items():
        c.drawString(2*cm, y, f"{key}: {value}")
        y -= 0.8*cm

    c.save()
    buffer.seek(0)
    return buffer

# 3. الواجهة
st.title("☀️ حاسبة أنظمة الطاقة الشمسية - أم درمان")
st.caption("بيانات الإشعاع من ناسا NREL + حساب الحمل بالأجهزة")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. موقع المشروع")
    lat = st.number_input("خط العرض Lat", value=15.6, format="%.4f")
    lon = st.number_input("خط الطول Lon", value=32.5, format="%.4f")
    tilt = st.slider("زاوية الميل Tilt", 0, 45, 15)
    azimuth = st.slider("زاوية الاتجاه Azimuth", 0, 360, 180)

with col2:
    st.subheader("2. المكونات")
    panel_name = st.selectbox("نوع اللوح", list(PANELS.keys()))
    inv_name = st.selectbox("نوع الانفرتر", list(INVERTERS.keys()))

# 4. حساب الحمل من الأجهزة
st.subheader("2.5 حساب الحمل من الأجهزة 🏠🏢")
col_a, col_b = st.columns(2)
selected_devices = []

with col_a:
    st.write("**أجهزة المنزل**")
    for device, specs in list(DEVICES.items())[:5]:
        qty = st.number_input(device, 0, 20, 0, key=device)
        if qty > 0:
            selected_devices.append(qty * specs["watt"] * specs["hours"])

with col_b:
    st.write("**أجهزة المؤسسة**")
    for device, specs in list(DEVICES.items())[5:]:
        qty = st.number_input(device, 0, 20, 0, key=device)
        if qty > 0:
            selected_devices.append(qty * specs["watt"] * specs["hours"])

# نحسب القدرة المقترحة
if selected_devices:
    daily_kwh = sum(selected_devices) / 1000
    system_kw = round(daily_kwh / 5.5, 2) # 5.5 ساعات ذروة السودان
    st.success(f"⚡ الاستهلاك اليومي: {daily_kwh} kWh | القدرة المقترحة: {system_kw} kW")
else:
    system_kw = st.number_input("أو دخلي القدرة يدوي kW", 1.0, 100.0, 5.0)

st.subheader("3. الفواقد %")
col3, col4, col5 = st.columns(3)
with col3:
    soiling = st.slider("الأتربة Soiling", 0, 20, 5)
    shading = st.slider("التظليل Shading", 0, 20, 3)
with col4:
    snow = st.slider("الغبار/الثلوج Snow", 0, 10, 0)
    mismatch = st.slider("Mismatch", 0, 5, 2)
with col5:
    wiring = st.slider("الأسلاك Wiring", 0, 5, 2)
    availability = st.slider("التوفر Availability", 90, 100, 98)

losses = {"Soiling": soiling, "Shading": shading, "Snow": snow,
          "Mismatch": mismatch, "Wiring": wiring, "Availability": 100-availability}

if st.button("احسب الإنتاج السنوي", type="primary"):
    with st.spinner("جاري جلب بيانات ناسا..."):
        monthly, annual_mwh, pr = calc_pvlib_hourly(lat, lon, tilt, azimuth, panel_name, inv_name, losses, system_kw)

    if annual_mwh > 0:
        st.success(f"✅ الإنتاج السنوي المتوقع: {annual_mwh} MWh | Performance Ratio: {pr}%")

        months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                  'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        df_chart = pd.DataFrame({"الشهر": months, "الإنتاج kWh": monthly})
        fig = px.bar(df_chart, x="الشهر", y="الإنتاج kWh", title="الإنتاج الشهري")
        st.plotly_chart(fig, use_container_width=True)

        report_data = {
            "الموقع": f"{lat}, {lon}",
            "القدرة": f"{system_kw} kW",
            "الألواح": panel_name,
            "الانفرتر": inv_name,
            "الإنتاج السنوي": f"{annual_mwh} MWh",
            "PR": f"{pr}%"
        }

        pdf = generate_pdf(report_data)
        st.download_button("📄 تحميل PDF", pdf, "solar_report.pdf", "application/pdf")

st.caption("ملاحظة: بدون pvlib - متوافق 100% مع Streamlit Cloud")
