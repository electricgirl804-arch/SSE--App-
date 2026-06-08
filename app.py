import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# 1. إعدادات الصفحة - وضع الشاشة العريضة للتابلت
st.set_page_config(page_title="SSE Global Engineering AI", layout="wide")

# 2. التنسيق البصري (CSS) - تصميم واجهة التابلت الهندسية
st.markdown("""
    <style>
    .stApp { background-color: #0b1c24; color: #ffffff; }
    .card { 
        background: #162128; 
        padding: 20px; 
        border-radius: 20px; 
        border: 1px solid #FFD700; 
        box-shadow: 0 4px 10px rgba(255, 215, 0, 0.2); 
        margin-bottom: 20px; 
    }
    .title { color: #FFD700; text-align: center; font-weight: bold; margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #FFD700; color: #000; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. لوحة تسجيل الدخول (كلمة السر: shahd8499)
st.markdown("<h1 class='title'>⚡ SSE Global Engineering - AI Dashboard</h1>", unsafe_allow_html=True)
pwd = st.sidebar.text_input("كلمة سر المهندسة:", type="password")

if pwd == "shahd8499":
    st.sidebar.success("تم تفعيل النظام بنجاح")
    
    # تقسيم الواجهة إلى 3 أعمدة (Grid System)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    # العمود الأول: بيانات الموقع
    with col1:
        st.markdown("<div class='card'><h3>📍 بيانات الموقع</h3>", unsafe_allow_html=True)
        st.write(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")
        st.write("**الإحداثيات:** 15.55 N, 32.48 E")
        st.write("**الحالة:** متصل (NASA POWER)")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # العمود الثاني: المساعد الذكي
    with col2:
        st.markdown("<div class='card'><h3>🤖 المساعد الذكي (ALAgent)</h3>", unsafe_allow_html=True)
        st.image("https://api.dicebear.com/7.x/adventurer/svg?seed=Shahd", width=120)
        st.write("أهلاً م/ شهد. أنا نظامك الميداني الذكي. كيف يمكنني مساعدتك اليوم؟")
        if st.button("بدء التحليل الميداني"):
            st.info("جاري فحص الأحمال ومطابقة المواصفات...")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # العمود الثالث: المراقبة والتوثيق
    with col3:
        st.markdown("<div class='card'><h3>📊 الحمل اللحظي (W)</h3>", unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(mode="gauge+number", value=4110, gauge={'bar': {'color': "#FFD700"}}))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<div class='card'><h3>📸 التوثيق الميداني</h3>", unsafe_allow_html=True)
        st.camera_input("التقاط صورة للمعايرة")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<center><h2>⚠️ الرجاء إدخال كلمة السر الخاصة بالمهندسة للوصول للنظام</h2></center>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3064/3064155.png", width=200)

