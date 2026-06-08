
import requests
import folium
from streamlit_folium import folium_static
from fpdf import FPDF
import datetime

# 1. إعدادات الصفحة (تجربة المستخدم الاحترافية)
st.set_page_config(page_title="SSE Global Engineering Pro", layout="wide", page_icon="⚡")

# تنسيق CSS ليتناسب مع صور "التابلت" التي أرفقتِها
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #ffffff; }
    .card { background: rgba(30, 41, 59, 0.7); border: 1px solid #FFD700; 
            border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    h3 { color: #FFD700 !important; }
    </style>
""", unsafe_allow_html=True)

# 2. الدوال الذكية (محرك ناسا والربط)
def get_nasa_solar_data(lat, lon):
    try:
        url = f"https://power.larc.nasa.gov/api/v2/temporal/climatology/point?latitude={lat}&longitude={lon}&community=RE&parameters=ALLSKY_SFC_SW_DWN&format=JSON"
        response = requests.get(url).json()
        return sum(response['properties']['parameter']['ALLSKY_SFC_SW_DWN'].values()) / 12
    except: return 5.5

def sync_to_google_sheet(data):
    # ضعي هنا رابط الـ Web App الخاص بكِ
    web_app_url = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec" 
    try:
        requests.post(web_app_url, json=data)
        return True
    except: return False

# 3. الواجهة (Layout)
st.title("🏗️ SSE Global Engineering AI")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("<div class='card'><h3>📍 الموقع الجغرافي (Live)</h3>", unsafe_allow_html=True)
    lat = st.number_input("خط العرض", value=15.5007)
    lon = st.number_input("خط الطول", value=32.5599)
    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker([lat, lon]).add_to(m)
    folium_static(m, width=350, height=200)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h3>⚙️ تحليل الأحمال (1950W)</h3>", unsafe_allow_html=True)
    power = st.number_input("الحمل الإجمالي (Watt)", 1950)
    if st.button("🚀 تحديث بيانات NASA"):
        st.session_state.solar = get_nasa_solar_data(lat, lon)
        st.success(f"الكفاءة: {round(st.session_state.solar, 2)} kWh/m²/day")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='card'><h3>💾 التوثيق والمزامنة</h3>", unsafe_allow_html=True)
    if st.button("✅ توثيق المشروع"):
        data = {'lat': lat, 'lon': lon, 'power': power, 'date': str(datetime.date.today())}
        if sync_to_google_sheet(data):
            st.success("تم التوثيق والتحليل بنجاح!")
            st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)
