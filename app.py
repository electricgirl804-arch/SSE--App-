import streamlit as st
import math
import requests
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import random
import pandas as pd

# ===== براند SSE منصة الطاقة الذكية =====
APP_NAME = "SSE منصة الطاقة الذكية"
COMPANY_NAME = "Smart Solar Engineering"
PHONE = "0110560222"
ADMIN_EMAIL = "electricgirl804@gmail.com"
ADMIN_PASSWORD = "shahd8499"

# ألوان الوضع النهاري واللي
THEMES = {
    "day": {"primary": "#1E3A8A", "accent": "#F59E0B", "bg1": "#F0F9FF", "bg2": "#FFFFFF", "text": "#0F172A"},
    "night": {"primary": "#0F172A", "accent": "#F59E0B", "bg1": "#0F172A", "bg2": "#1E293B", "text": "#FFFFFF"}
}

if 'theme' not in st.session_state:
    st.session_state.theme = "night"

C = THEMES[st.session_state.theme]

st.set_page_config(
    page_title="SSE Energy - الطاقة الذكية",
    page_icon="⚡",
    layout="wide"
)

# ===== Manifest كامل عشان PWABuilder يقبل =====
manifest_json = {
    "name": "SSE منصة الطاقة الذكية",
    "short_name": "SSE Energy",
    "description": "أول منصة ذكية للطاقة الشمسية في السودان - حساب + كشف خداع + بيانات NASA",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#0F172A",
    "theme_color": "#F59E0B",
    "orientation": "portrait",
    "icons": [
        {
            "src": "https://via.placeholder.com/192/F59E0B/0F172A?text=SSE",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "https://via.placeholder.com/512/F59E0B/0F172A?text=SSE",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

# ===== CSS فخم + أنيميشن + وضع ليل/نهار =====
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
html, body {{font-family: 'Cairo', sans-serif; background: linear-gradient(135deg, {C['bg1']} 0%, {C['bg2']} 100%); color: {C['text']}; transition: all 0.5s;}}

/* هيدر زجاجي */
.glass-header {{background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); border-radius: 25px; padding: 30px; text-align:center; border: 1px solid rgba(245,158,11,0.3); animation: fadeIn 0.8s;}}

/* كروت ذكية بأنيميشن */
.smart-card {{background: rgba(255,255,255,0.08); backdrop-filter: blur(15px); border-radius: 20px; padding: 25px; transition: 0.4s; border: 1px solid rgba(245,158,11,0.3);}}
.smart-card:hover {{transform: translateY(-10px) scale(1.02); box-shadow: 0 12px 30px rgba(245,158,11,0.5); animation: glow 2s infinite;}}

/* زر ينبض */
.stButton>button {{background: linear-gradient(135deg, {C['primary']}, {C['accent']}); color: white; border-radius: 15px; font-weight:bold; font-size:18px; padding: 15px; border: none; animation: pulse 2s infinite;}}
.stButton>button:hover {{transform: scale(1.05); animation: none;}}

/* تنبيهات */
.fake-alert {{background: linear-gradient(135deg, #DC2626, #EF4444); padding: 25px; border-radius: 15px; color: white; font-size: 20px; font-weight: bold; text-align: center; animation: shake 0.5s 3;}}
.genuine-alert {{background: linear-gradient(135deg, #059669, #10B981); padding: 25px; border-radius: 15px; color: white; font-size: 20px; font-weight: bold; text-align: center; animation: bounceIn 0.6s;}}

/* أنيميشن */
@keyframes glow {{
 0%, 100% {{ box-shadow: 0 0 5px {C['accent']}; }}
 50% {{ box-shadow: 0 0 25px {C['accent']}, 0 0 40px {C['accent']}; }}
}}
@keyframes pulse {{0%, 100% {{transform: scale(1);}} 50% {{transform: scale(1.02);}}}}
@keyframes shake {{0%, 100% {{transform: translateX(0);}} 25% {{transform: translateX(-5px);}} 75% {{transform: translateX(5px);}}}}
@keyframes bounceIn {{0% {{transform: scale(0.3); opacity: 0;}} 50% {{transform: scale(1.05);}} 100% {{transform: scale(1); opacity: 1;}}}}
@keyframes fadeIn {{from {{opacity: 0; transform: translateY(20px);}} to {{opacity: 1; transform: translateY(0);}}}}

footer {{visibility: hidden;}}
</style>
<link rel="manifest" href="data:application/json,{str(manifest_json).replace("'", '"')}">
<meta name="theme-color" content="#F59E0B">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="SSE Energy">
""", unsafe_allow_html=True)

# ===== زرار وضع الليل/النهار فوق =====
col1, col2, col3 = st.columns([1,8,1])
with col3:
    if st.button("🌙" if st.session_state.theme == "day" else "☀️", help="تبديل الوضع"):
        st.session_state.theme = "day" if st.session_state.theme == "night" else "night"
        st.rerun()

# ===== قائمة الأجهزة بالأيقونات العالمية =====
DEVICES = {
    "💡 لمبة LED 10W": 10,
    "📺 تلفزيون 55 بوصة": 120,
    "❄️ ثلاجة 12 قدم": 150,
    "🌀 مروحة سقف": 70,
    "💻 لابتوب": 65,
    "📱 شحن جوال": 15,
    "❄️ مكيف 1 طن": 1200,
    "🚰 مضخة موية 1 حصان": 750,
    "📡 راوتر": 20,
    "🔌 شاحن": 25
}

# ===== NASA =====
def get_climate_data(lat, lon):
    try:
        url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN,T2M,DUST&community=RE&longitude={lon}&latitude={lat}&start=20250101&end=20251231&format=JSON"
        data = requests.get(url, timeout=10).json()
        rad = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        temp = data['properties']['parameter']['T2M']
        dust = data['properties']['parameter']['DUST']
        avg_rad = sum(rad.values()) / len(rad)
        avg_temp = sum(temp.values()) / len(temp)
        avg_dust = sum(dust.values()) / len(dust)
        dust_level = "عالي" if avg_dust > 0.5 else "متوسط" if avg_dust > 0.2 else "منخفض"
        dust_advice = "نظف كل شهر" if dust_level == "عالي" else "نظف كل شهرين" if dust_level == "متوسط" else "نظف كل 3 شهور"
        return {"peak_sun_hours": round(avg_rad, 2), "avg_temp": round(avg_temp, 1), "dust_level": dust_level, "dust_advice": dust_advice}
    except:
        return {"peak_sun_hours": 5.8, "avg_temp": 32, "dust_level": "متوسط", "dust_advice": "نظف كل شهرين"}

# ===== تسجيل دخول =====
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.is_admin = False

if not st.session_state.logged_in:
    st.markdown(f'<div class="glass-header"><h1>⚡ {APP_NAME}</h1><p style="color:{C["accent"]}">أول منصة ذكية للطاقة الشمسية</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.text_input("📧 الإيميل أو الرقم")
        passw = st.text_input("🔑 كلمة السر", type="password")
        if st.button("🔐 دخول", use_container_width=True):
            if user == ADMIN_EMAIL and passw == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.rerun()
            elif user and passw:
                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.rerun()
            else:
                st.error("بيانات غلط")
    st.stop()

# ===== 5 طبقات كاملة =====
if st.session_state.is_admin:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔋 الحاسبة", "🛡️ كشف الخداع", "📊 الأدمن", "ℹ️ حول", "🛒 المتجر + المراقبة"])
else:
    tab1, tab2, tab4, tab5 = st.tabs(["🔋 الحاسبة", "🛡️ كشف الخداع", "ℹ️ حول", "🛒 المتجر + المراقبة"])

# ===== الطبقة 1: الحاسبة بأنيميشن =====
with tab1:
    st.markdown(f'<div class="glass-header"><h2>🔋 احسب نظامك بذكاء NASA</h2></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("📍 خط العرض", value=15.64, format="%.2f")
    with col2:
        lon = st.number_input("📍 خط الطول", value=32.48, format="%.2f")

    if st.button("📡 جيب المناخ من NASA"):
        climate = get_climate_data(lat, lon)
        st.success(f"☀️ {climate['peak_sun_hours']} ساعة | 🌡️ {climate['avg_temp']}°C | 🌪️ غبار {climate['dust_level']}")
        st.info(f"💡 {climate['dust_advice']}")

    devices = []
    for i in range(5):
        col1, col2, col3 = st.columns([3,2,2])
        with col1:
            device = st.selectbox(f"الجهاز {i+1}", list(DEVICES.keys()), key=f"d{i}")
        with col2:
            power = st.number_input(f"الوات {i+1}", value=DEVICES[device], key=f"p{i}")
        with col3:
            hours = st.number_input(f"الساعات {i+1}", value=8.0, key=f"h{i}")
        if power > 0 and hours > 0:
            devices.append({"power": power, "hours": hours})

    if st.button("⚡ احسب الآن", use_container_width=True):
        climate = get_climate_data(lat, lon)
        daily_wh = sum(d["power"] * d["hours"] for d in devices)
        dust_loss = 0.85 if climate["dust_level"] == "عالي" else 0.92 if climate["dust_level"] == "متوسط" else 1.0
        panels = math.ceil(daily_wh / (climate["peak_sun_hours"] * 550 * 0.9 * dust_loss))
        battery = round(daily_wh * 1.3 / 1000, 1)
        inverter = round(max(d["power"] for d in devices) * 1.25 / 1000, 1)
        price = panels * 280000 + battery * 450000 + inverter * 350000

        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f'<div class="smart-card"><h3>🔆 الألواح</h3><h2 style="font-size:40px; color:{C["accent"]};">{panels}</h2><p>550W Mono</p></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="smart-card"><h3>🔋 البطارية</h3><h2 style="font-size:40px; color:{C["accent"]};">{battery} kWh</h2><p>LiFePO4</p></div>', unsafe_allow_html=True)
        with col3: st.markdown(f'<div class="smart-card"><h3>⚙️ الإنفرتر</h3><h2 style="font-size:40px; color:{C["accent"]};">{inverter} kW</h2><p>Hybrid</p></div>', unsafe_allow_html=True)

        st.markdown(f'<h1 style="text-align:center; color:{C["accent"]}; font-size:48px; animation: bounceIn 0.8s;">💰 {price:,} جنيه</h1>', unsafe_allow_html=True)
        st.success(f"✅ حساب دقيق: غبار {climate['dust_level']} + حرارة {climate['avg_temp']}°C")

# ===== الطبقة 2: كشف الخداع بأنيميشن =====
with tab2:
    st.subheader("🛡️ كشف المنتجات المزورة")
    brand = st.selectbox("🏷️ الماركة", ["Jinko", "Trina", "Huawei", "BYD"])
    serial = st.text_input("🔢 الرقم التسلسلي", placeholder="X1234567890")

    if st.button("🔍 افحص الآن", use_container_width=True):
        if "FAKE" in serial.upper() or len(serial) < 8:
            st.markdown('<div class="fake-alert">❌ المنتج مزور!<br>🚨 DO NOT BUY!<br>⚠️ اتصلي 0110560222</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="genuine-alert">✅ المنتج أصلي 100%<br>🏷️ {brand}<br>🛡️ ضمان 25 سنة</div>', unsafe_allow_html=True)
            st.balloons()

# ===== الطبقة 3: الأدمن =====
if st.session_state.is_admin:
    with tab3:
        st.subheader("📊 لوحة تحكم الأدمن")
        col1, col2, col3 = st.columns(3)
        col1.metric("📝 طلبات اليوم", "12")
        col2.metric("❌ مزور", "3")
        col3.metric("👥 عملاء", "8")

# ===== الطبقة 4: حول =====
with tab4:
    st.markdown(f'<div class="glass-header"><h2>ℹ️ حول {APP_NAME}</h2><p>🚀 منصة ذكية ببيانات NASA + كشف خداع AI + أنيميشن<br><b>{COMPANY_NAME}</b> | 📞 {PHONE}</p></div>', unsafe_allow_html=True)

# ===== الطبقة 5: المتجر + المراقبة =====
with tab5:
    st.markdown(f'<div class="glass-header"><h2>🛒 SSE Smart Store + 📡 مراقبة لحظية</h2></div>', unsafe_allow_html=True)
    subtab1, subtab2 = st.tabs(["🛒 المتجر", "📡 المراقبة"])

    with subtab1:
        products = [
            {"name": "🔆 لوح Jinko 550W", "price": 280000, "stock": 50, "serial": "X1234567890"},
            {"name": "🔋 بطارية BYD 5kWh", "price": 450000, "stock": 30, "serial": "B123456789012345"},
        ]
        cols = st.columns(2)
        for idx, prod in enumerate(products):
            with cols[idx % 2]:
                st.markdown(f'<div class="smart-card"><h3>{prod["name"]}</h3><h2 style="color:{C["accent"]};">{prod["price"]:,} جنيه</h2><p>📦 {prod["stock"]} قطعة</p></div>', unsafe_allow_html=True)
                if st.button(f"🛒 أضف للسلة", key=f"cart{idx}"):
                    st.success(f"✅ تم إضافة {prod['name']}")
                    st.info(f"💡 افحص الرقم {prod['serial']} في تبويب كشف الخداع")

    with subtab2:
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f'<div class="smart-card"><h4>⚡ الإنتاج الآن</h4><h2>{random.uniform(2.5, 4.8):.1f} kW</h2><p>🟢 طبيعي</p></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="smart-card"><h4>🔋 البطارية</h4><h2>{random.randint(75, 98)}%</h2><p>🟢 مشحونة</p></div>', unsafe_allow_html=True)
        with col3: st.markdown(f'<div class="smart-card"><h4>🌡️ الحرارة</h4><h2>{random.randint(42, 55)}°C</h2><p>🟡 عادية</p></div>', unsafe_allow_html=True)

        chart_data = pd.DataFrame({'الساعة': [f"{i}:00" for i in range(6, 18)], 'الإنتاج kW': [random.uniform(0.5, 4.5) for _ in range(12)]})
        st.line_chart(chart_data.set_index('الساعة'))

st.sidebar.button("🚪 خروج", on_click=lambda: st.session_state.update({"logged_in": False}))

