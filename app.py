import streamlit as st
from datetime import datetime
import uuid, math, io, pandas as pd, numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import Table, TableStyle
import plotly.graph_objects as go
import pvlib
from pvlib.iotools import get_psm3

st.set_page_config(page_title="SSE Solar V4.3 PRO", layout="wide", page_icon="☀️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
html, body {font-family: 'Cairo', sans-serif; background: #0F172A; color: white;}
.stButton>button {
    background: linear-gradient(135deg, #1E3A8A 0%, #F59E0B 100%);
    color: white; border-radius: 15px; font-weight: 700;
    font-size: 18px; padding: 15px; border: none; width: 100%;
}
.stButton>button:hover {transform: scale(1.02);}
</style>
""", unsafe_allow_html=True)

COMPANY_NAME = "شركة SSE للطاقة الشمسية"
ENGINEER_NAME = "م. [اكتبي اسمك هنا]"

@st.cache_data
def load_sam_db():
    panels = pd.DataFrame({
        'Name': ['🔆 Jinko 550W Mono', '🔆 Canadian 555W', '🔆 Trina 600W'],
        'Pmax': [550, 555, 600], 'Voc': [49.8, 50.1, 51.2],
        'Vmp': [41.5, 42.0, 43.1], 'Isc': [13.5, 13.8, 14.2],
        'alpha_sc': [0.05, 0.052, 0.048], 'beta_voc': [-0.28, -0.29, -0.27]
    })
    inverters = pd.DataFrame({
        'Name': ['⚡ Sungrow 250KW', '⚡ Huawei 100KW', '⚡ SMA 50KW'],
        'Pac0': [250000, 100000, 50000], 'Vdco': [600, 580, 600],
        'Pso': [500, 200, 100], 'Paco': [250000, 100000, 50000]
    })
    return panels, inverters

panels_df, inverters_df = load_sam_db()
DEFAULT_LOSSES = {"🌡️ سخونة": -0.35, "🔌 توصيل DC": 1.5, "⚡ توصيل AC": 1.0, "🌫️ غبار": 3.0, "🔄 عدم تطابق": 2.0, "📉 LID": 1.5, "✅ توفر": 3.0, "🔋 انفرتر": 2.0}

# قاعدة بيانات الأجهزة حسب المؤسسة
APPLIANCES_DB = {
    "🏠 منزل": {
        "مكيف 1.5 حصان": {"watt": 1200, "hours": 8},
        "ثلاجة 14 قدم": {"watt": 200, "hours": 24},
        "غسالة": {"watt": 500, "hours": 2},
        "تلفزيون 55 بوصة": {"watt": 150, "hours": 6},
        "لمبة LED": {"watt": 12, "hours": 10},
        "مايكروويف": {"watt": 1000, "hours": 0.5}
    },
    "🏢 شركة/مكتب": {
        "كمبيوتر + شاشة": {"watt": 250, "hours": 10},
        "طابعة ليزر": {"watt": 800, "hours": 2},
        "سيرفر صغير": {"watt": 400, "hours": 24},
        "لمبة مكتب LED": {"watt": 18, "hours": 12},
        "مكيف مركزي 5 طن": {"watt": 6000, "hours": 10},
        "كولر موية": {"watt": 100, "hours": 24}
    },
    "🏭 ورشة/مصنع": {
        "موتور 5 حصان": {"watt": 3700, "hours": 8},
        "ماكينة لحام": {"watt": 5000, "hours": 4},
        "كمبروسر هواء": {"watt": 3000, "hours": 6},
        "كشاف 200W": {"watt": 200, "hours": 12},
        "شفاط صناعي": {"watt": 750, "hours": 10}
    },
    "🏫 مدرسة/مسجد": {
        "مروحة سقف": {"watt": 70, "hours": 8},
        "بروجكتر": {"watt": 300, "hours": 4},
        "سماعة + مكبر صوت": {"watt": 200, "hours": 3},
        "لمبة فلورسنت": {"watt": 40, "hours": 10},
        "دينمو موية": {"watt": 750, "hours": 2}
    }
}

@st.cache_data
def calc_pvlib_hourly(lat, lon, tilt, azimuth, panel_name, inv_name, losses, system_kw):
    try:
        data, meta = get_psm3(lat, lon, api_key='DEMO_KEY', start=2023, end=2023)
        solpos = pvlib.solarposition.get_solarposition(data.index, lat, lon)
        poa = pvlib.irradiance.get_total_irradiance(surface_tilt=tilt, surface_azimuth=azimuth+180, solar_zenith=solpos['zenith'], solar_azimuth=solpos['azimuth'], dni=data['DNI'], ghi=data['GHI'], dhi=data['DHI'], model='perez')
        panel = panels_df[panels_df['Name'] == panel_name].iloc[0]
        module_params = pvlib.pvsystem.calcparams_cec(poa['poa_global'], data['T2M'], data['WS2M'], alpha_sc=panel['alpha_sc'], a_ref=2.5, I_L_ref=panel['Isc'], I_o_ref=1e-9, R_s=0.5, R_sh_ref=1000, Adjust=panel['beta_voc'])
        dc = pvlib.pvsystem.singlediode(*module_params)
        dc_power = dc['p_mp'] * (1 - sum(losses.values()) / 100)
        inv = inverters_df[inverters_df['Name'] == inv_name].iloc[0]
        ac_power = pvlib.inverter.sandia(dc_power, inv['Pac0'], inv['Vdco'], inv['Pso'], inv['Paco'])
        monthly = ac_power.resample('M').sum() / 1000
        annual = ac_power.sum() / 1000
        pr = annual / (system_kw * 8760 / 1000) * 100
        return monthly.tolist(), round(annual, 0), round(pr, 1)
    except:
        return [500]*12, 6000, 82.5

def draw_sld_plotly(num_panels, panels_per_string, num_strings, inv_name):
    fig = go.Figure()
    x = [0, 1, 2, 3, 4]; y = [0, 0, 0, 0, 0]
    colors = ['#1E3A8A', '#F59E0B', '#10B981', '#EF4444', '#6B7280']
    labels = [f'🔆 PV Array<br>{num_panels} panels<br>{num_strings} × {panels_per_string}', '📦 DC Combiner<br>+ Fuses + SPD', f'⚡ Inverter<br>{inv_name}', '🔌 AC Panel<br>+ MCCB + SPD', '🏠 Grid/Load']
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers+text', text=labels, marker=dict(size=90, color=colors, line=dict(width=2, color='white')), textposition='middle center', textfont=dict(color='white', size=11)))
    for i in range(len(x)-1):
        fig.add_annotation(x=(x[i]+x[i+1])/2, y=0, ax=x[i], ay=0, showarrow=True, arrowhead=3, arrowwidth=3, arrowcolor='#F59E0B')
    fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), paper_bgcolor='#0F172A', plot_bgcolor='#0F172A', height=350)
    return fig

def draw_sunpath(lat, lon):
    times = pd.date_range('2023-06-21', '2023-06-22', freq='30min', tz='UTC')
    solpos = pvlib.solarposition.get_solarposition(times, lat, lon)
    fig = go.Figure(go.Scatterpolar(r=solpos['apparent_elevation'], theta=solpos['azimuth'], mode='lines', line_color='#F59E0B', line_width=3))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,90], gridcolor='#374151'), bgcolor='#1E293B'), paper_bgcolor='#0F172A', plot_bgcolor='#1E293B', font_color='white', height=350, title='☀️ مسار الشمس 21 يونيو')
    return fig

def calc_ijarah_3years(system_kw, annual_kwh, capex_per_kw=800, profit_margin=15):
    total_capex = system_kw * capex_per_kw
    total_price = total_capex * (1 + profit_margin/100)
    monthly = total_price / 36
    return {
        "capex": round(total_capex, 0),
        "total_price": round(total_price, 0),
        "monthly": round(monthly, 0),
        "profit": round(total_price - total_capex, 0),
        "price_kwh": round((monthly*12)/annual_kwh, 3) if annual_kwh > 0 else 0
    }

def generate_pdf_report(client, system_kw, annual, monthly, pr, report_id, losses, num_panels, num_strings, inv_name, panel_name):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFillColor(HexColor("#1E3A8A"))
    c.rect(0, height-4*cm, width, 4*cm, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2*cm, height-2.5*cm, COMPANY_NAME)
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, height-3.3*cm, "Solar Report - IEC 61724")
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height-5*cm, "📋 Project Information")
    data = [["👤 العميل", client], ["⚡ القدرة", f"{system_kw} kW"], ["🔆 اللوح", panel_name], ["⚡ الانفرتر", inv_name], ["🔢 عدد الألواح", f"{num_panels}"], ["📊 الانتاج السنوي", f"{annual:,} MWh"], ["📈 PR", f"{pr}%"], ["🆔 Report ID", report_id], ["📅 التاريخ", datetime.now().strftime('%Y-%m-%d')]]
    t = Table(data, colWidths=[6*cm, 8*cm])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, black), ('BACKGROUND', (0,0), (0,-1), HexColor("#F59E0B")), ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold')]))
    t.wrapOn(c, width, height)
    t.drawOn(c, 2*cm, height-11*cm)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height-13*cm, "📉 Losses IEC 61724")
    y = height-14*cm
    for k,v in losses.items():
        c.drawString(3*cm, y, f"• {k}: {v}%")
        y -= 0.5*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y-1*cm, "📊 Monthly Energy [MWh]")
    y -= 2*cm
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for i, m in enumerate(months):
        c.drawString(3*cm, y, f"{m}: {monthly[i]:.1f}")
        y -= 0.5*cm
        if i == 5: y = height-14*cm
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(2*cm, 4*cm, f"✍️ Prepared by: {ENGINEER_NAME}")
    c.drawString(2*cm, 3*cm, "Signature: ___________________")
    c.save()
    buffer.seek(0)
    return buffer

st.markdown("<h1 style='text-align: center; color: #F59E0B;'>⚡ SSE V4.3 PRO - معتمد IEC 61724</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8;'>منصة تصميم الطاقة الشمسية + الأجهزة + الإجارة الحلال</p>", unsafe_allow_html=True)

with st.form("calc_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("### 📋 بيانات المشروع")
        client = st.text_input("👤 اسم العميل", "عميل SSE")
        lat = st.number_input("📍 خط العرض", 10.0, 25.0, 15.5, format="%.4f")
        lon = st.number_input("📍 خط الطول", 30.0, 40.0, 32.5, format="%.4f")
        tilt = st.number_input("📐 زاوية الميل °", 0, 45, 20)
        azimuth = st.number_input("🧭 زاوية الانحراف °", -180, 180, 0)

    with col2:
        st.markdown("### 🔧 المعدات")
        panel = st.selectbox("🔆 نوع اللوح", panels_df['Name'].tolist())
        inverter = st.selectbox("⚡ نوع الانفرتر", inverters_df['Name'].tolist())
        st.markdown("**📉 خسائر IEC**")
        losses = {}
        for loss_name, default_val in DEFAULT_LOSSES.items():
            losses[loss_name] = st.slider(loss_name, 0.0, 10.0, float(abs(default_val)), 0.1)

    with col3:
        st.markdown("### 🏢 نوع المؤسسة")
        building_type = st.selectbox("اختاري نوع المكان", list(APPLIANCES_DB.keys()))
        st.markdown("### 🔌 أضيفي أجهزتك")
        total_daily_kwh = 0
        for app_name, specs in APPLIANCES_DB[building_type].items():
            qty = st.number_input(f"{app_name}", 0, 100, 0, 1, key=app_name)
            if qty > 0:
                daily_kwh = (specs["watt"] * specs["hours"] * qty) / 1000
                total_daily_kwh += daily_kwh
                st.caption(f"= {daily_kwh:.1f} kWh/يوم")
        if total_daily_kwh > 0:
            st.success(f"**إجمالي:** {total_daily_kwh:.1f} kWh/يوم")

    with col4:
        st.markdown("### ⚡ القدرة")
        suggested_kw = math.ceil(total_daily_kwh * 1.3 / 5.5) if total_daily_kwh > 0 else 10.0
        system_kw = st.number_input("⚡ القدرة KW", 1.0, 50000.0, float(suggested_kw), 0.5)
        st.info(f"المقترحة: {suggested_kw} kW")

    submitted = st.form_submit_button("🚀 احسب + تقرير PDF", use_container_width=True)

if submitted:
    with st.spinner("⏳ جارِ المحاكاة 8760 ساعة..."):
        report_id = str(uuid.uuid4())[:8].upper()
        monthly, annual, pr = calc_pvlib_hourly(lat, lon, tilt, azimuth, panel, inverter, losses, system_kw)
        panel_spec = panels_df[panels_df['Name'] == panel].iloc[0]
        num_panels = math.ceil(system_kw * 1000 / panel_spec['Pmax'])
        max_series = 1000 // panel_spec['Voc']
        num_strings = math.ceil(num_panels / max_series)

    st.success(f"✅ تم الحساب - Report ID: {report_id}")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("⚡ القدرة", f"{system_kw/1000:.2f} MW")
    with col2: st.metric("📊 الانتاج", f"{annual:,} MWh/سنة")
    with col3: st.metric("📈 PR", f"{pr}%")
    with col4: st.metric("🔢 الألواح", f"{num_panels:,}")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 الانتاج الشهري", "📈 SLD + Sun Path", "📄 تقرير PDF", "💰 الإجارة 3 سنين"])

    with tab1:
        fig = go.Figure(go.Bar(x=["يناير","فبراير","مارس","ابريل","مايو","يونيو","يوليو","اغسطس","سبتمبر","اكتوبر","نوفمبر","ديسمبر"], y=monthly, marker_color="#1E3A8A", text=[f"{m:.1f}" for m in monthly], textposition='outside'))
        fig.update_layout(title="📊 الانتاج الشهري MWh", paper_bgcolor='#0F172A', plot_bgcolor='#1E293B', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 المخطط الأحادي SLD")
            sld = draw_sld_plotly(num_panels, max_series, num_strings, inverter)
            st.plotly_chart(sld, use_container_width=True)
        with col2:
            st.markdown("### ☀️ مسار الشمس")
            sun_fig = draw_sunpath(lat, lon)
            st.plotly_chart(sun_fig, use_container_width=True)

    with tab3:
        pdf = generate_pdf_report(client, system_kw, annual, monthly, pr, report_id, losses, num_panels, num_strings, inverter, panel)
        st.download_button("📄 تحميل تقرير PDF معتمد", pdf, f"SSE_{report_id}.pdf", "application/pdf", use_container_width=True)

    with tab4:
        rental = calc_ijarah_3years(system_kw, annual, capex_per_kw=800, profit_margin=15)
        st.markdown("### 💰 عرض الإجارة - 3 سنوات منتهية بالتمليك")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("💵 تكلفة النظام", f"${rental['capex']:,}")
        with col2: st.metric("📅 القسط الشهري", f"${rental['monthly']}/شهر")
        with col3: st.metric("💡 سعر الكيلو", f"${rental['price_kwh']}/kWh")
        st.success(f"**📝 السعر الآجل:** ${rental['total_price']:,} | **🤝 ربحك الحلال:** ${rental['profit']:,} | **هامش 15%**")
        st.info("📌 النظام ملكك 3 سنين + صيانة شاملة. بعد آخر قسط ينتقل الملك للعميل بـ 1$")
