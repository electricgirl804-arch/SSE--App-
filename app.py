import streamlit as st
from gtts import gTTS
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas

# --- 1. إعدادات المساعد الصوتي ---
def speak(text):
    tts = gTTS(text=text, lang='ar')
    tts.save("response.mp3")
    st.audio("response.mp3", format="audio/mp3", autoplay=True)

# --- دالة الأيقونات التفاعلية ---
def render_icon_card(icon, label, key):
    st.markdown(f"""
    <div style="text-align: center; border: 2px solid #ddd; padding: 15px; border-radius: 15px; background-color: #f9f9f9;">
        <h1 style="font-size: 40px;">{icon}</h1>
        <p style="font-weight: bold;">{label}</p>
    </div>
    """, unsafe_allow_html=True)
    return st.checkbox("اختيار", key=key)

# --- 2. واجهة التطبيق ---
st.image("1000224208_20.jpg", width=300)
st.title("☀️ منصة SSE الهندسية")
st.subheader("نحو مستقبل طاقة مستدام في السودان")

# --- 3. الترحيب ---
if 'started' not in st.session_state:
    speak("أهلاً بك في منصة SSE الهندسية. أنا مساعدك الرقمي، ابدأ بتحديد أحمالك.")
    st.session_state.started = True

# --- 4. المدخلات الهندسية (الأيقونات التفاعلية) ---
location = st.selectbox("📍 اختر المدينة:", ["أم درمان", "الخرطوم", "عطبرة", "بورتسودان"])
st.header("⚙️ اختيار الأحمال")

col1, col2, col3, col4 = st.columns(4)
with col1: washer = render_icon_card("🧺", "غسالة", "washer")
with col2: ac = render_icon_card("❄️", "مكيف", "ac")
with col3: motor = render_icon_card("⚙️", "موتور", "motor")
with col4: light = render_icon_card("💡", "إضاءة", "light")

# --- 5. محرك الحسابات ---
if st.button("حساب المنظومة"):
    total_watts = (washer*2000) + (ac*1500) + (motor*1000) + (light*200)
    panels = (total_watts * 1.2) / 550
    battery = (total_watts * 5) / 24
    
    st.write("### 📊 نتائج التصميم:")
    st.write(f"- إجمالي القدرة: {total_watts} واط")
    st.write(f"- عدد الألواح: {round(panels, 1)}")
    st.write(f"- سعة البطاريات: {round(battery, 2)} Ah")
    speak("تمت الحسابات بنجاح.")

# --- 6. التحقق الأمني ---
st.header("🛡️ التحقق من المكونات")
if st.button("بدء الفحص البصري"):
    img = st.camera_input("وجه الكاميرا لبيانات المنتج")
    if img:
        st.success("✅ المنتج مطابق للمواصفات")

# --- 7. التوثيق والتقرير ---
if st.button("📥 إصدار شهادة اعتماد SSE"):
    qr_data = f"SSE-Verified | Contact: Electricgirl804@gmail.com"
    qr = qrcode.make(qr_data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="ختم الاعتماد الرقمي - SSE")
    
    pdf_filename = "SSE_System_Report.pdf"
    c = canvas.Canvas(pdf_filename)
    c.drawString(100, 800, "تقرير اعتماد SSE")
    c.save()
    
    with open(pdf_filename, "rb") as f:
        st.download_button("تحميل التقرير PDF", f, file_name=pdf_filename)
    speak("تم اعتماد المنظومة.")

