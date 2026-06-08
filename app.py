import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import math

# إعداد الصفحة لتكون واسعة واحترافية
st.set_page_config(page_title="SSE Global | Engineering Pro", layout="wide", page_icon="⚡")

# التصميم المتقدم (Advanced CSS)
st.markdown("""
    <style>
    /* تحسين الخلفية وتأثير الزجاج */
    .stApp { background: linear-gradient(135deg, #050a0d 0%, #1a2a33 100%); color: #ffffff; }
    
    /* تصميم الكروت (Cards) */
    .card { 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(15px); 
        border: 1px solid rgba(255, 215, 0, 0.3); 
        border-radius: 25px; 
        padding: 30px; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }
    
    /* تنسيق العناوين */
    h1 { color: #FFD700 !important; text-align: center; font-weight: 800 !important; }
    h3 { color: #FFD700 !important; margin-bottom: 20px !important; }
    
    /* تنسيق الأزرار */
    .stButton>button {
        background-color: #FFD700 !important;
        color: #000 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# 1. محرك ناسا للبيانات الواقعية (تم الإبقاء عليه)
def get_nasa_solar_data(lat, lon):
    try:
        url = f"https://power.larc.nasa.gov/api/v2/temporal/climatology/point?latitude={lat}&longitude={lon}&community=RE&parameters=ALLSKY_SFC_SW_DWN&format=JSON"
        response = requests.get(url).json()
        data = response['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        return sum(data.values()) / len(data)
    except:
        return 5.5

st.title("🏗️ SSE Global Engineering Pro")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='card'><h3>🛰️ الربط الميداني والمدخلات</h3>", unsafe_allow_html=True)
    lat = st.number_input("خط العرض:", value=15.5007)
    lon = st.number_input("خط الطول:", value=32.5599)
    if st.button("🚀 تحديث البيانات من أقمار ناسا"):
        st.session_state.solar_val = get_nasa_solar_data(lat, lon)
        st.success(f"تم الربط بنجاح: {round(st.session_state.solar_val, 2)} kWh/m²/day")
    
    power = st.number_input("إجمالي الحمل (Watt):", 1000, 50000000, 5000)
    system_cost = st.number_input("تكلفة النظام ($):", 5000)
    elec_price = st.number_input("سعر الكيلوواط ($):", 0.15)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'><h3>💡 التحليل الهيكلي للجدوى</h3>", unsafe_allow_html=True)
    # ... [هنا نضع محرك الحسابات] ...
    # (النتائج ستظهر بشكل جمالي داخل هذا الكارت)
    st.markdown("</div>", unsafe_allow_html=True)

