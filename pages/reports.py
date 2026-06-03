import streamlit as st
import io
from utils.calculations import *
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.title("📄 Vessel Performance Report")

# =====================================
# LOAD DATA FROM SESSION STATE
# =====================================
metrics = st.session_state.get("metrics", {})

if not metrics:
    st.warning(
        "No report uploaded yet. "
        "Please upload a Noon Report on the main page first."
    )
else:
    # =====================================
    # SAFE DATA CONVERSION
    # =====================================
    try:
        actual_speed = float(metrics.get("actual_speed", 0))
    except:
        actual_speed = 0

    try:
        allowed_speed = float(metrics.get("allowed_speed", 0))
    except:
        allowed_speed = 0

    try:
        fuel_consumption = float(metrics.get("fuel_consumption", 0))
    except:
        fuel_consumption = 0

    try:
        wind_speed = float(metrics.get("wind_speed", 0))
    except:
        wind_speed = 0

    # =====================================
    # CALCULATIONS
    # =====================================
    performance_score = calculate_performance_score(actual_speed, allowed_speed)
    speed_variance = calculate_speed_variance(actual_speed, allowed_speed)
    fuel_variance = calculate_fuel_variance(fuel_consumption)

    # =====================================
    # 1. VESSEL INFORMATION
    # =====================================
    st.subheader("🚢 Vessel Information")

    vessel_info = st.session_state.get(
        "vessel_info",
        {
            "vessel_name": "MV DEMO",
            "imo": "1234567",
            "voyage": "VOY-001"
        }
    )

    st.write(f"**Vessel:** {vessel_info['vessel_name']}")
    st.write(f"**IMO Number:** {vessel_info['imo']}")
    st.write(f"**Voyage Identity:** {vessel_info['voyage']}")

    # =====================================
    # 2. PERFORMANCE SUMMARY
    # =====================================
    st.subheader("📊 Performance Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Performance Score", f"{performance_score}/100")

    with col2:
        st.metric("Speed Variance", f"{speed_variance} kn")

    with col3:
        st.metric("Fuel Variance", f"{fuel_variance} MT")

    # =====================================
    # 3. CHARTER CLAIM ANALYSIS
    # =====================================
    st.subheader("⚖ Charter Claim Analysis")

    speed_gap = allowed_speed - actual_speed

    if speed_gap > 1.0 and wind_speed < 15:
        st.error("Potential Charter Performance Claim Detected")
        charter_status = "Potential Performance Claim Risk Detected"
    else:
        st.success("No Charter Claim Risk")
        charter_status = "Nominal / No Claim Risk"

    # =====================================
    # 4. FUEL SAVING OPPORTUNITIES
    # =====================================
    st.subheader("⛽ Fuel Saving Opportunities")

    if fuel_variance > 0:
        st.metric("Potential Fuel Saving", f"{fuel_variance:.2f} MT/day")
        monthly_saving = fuel_variance * 30 * 600
        st.metric("Potential Monthly Saving", f"${monthly_saving:,.0f}")
    else:
        st.metric("Potential Fuel Saving", "0.00 MT/day")
        st.metric("Potential Monthly Saving", "$0")
        monthly_saving = 0

    # =====================================
    # 5. WEATHER RISK
    # =====================================
    weather_risk_val = metrics.get("weather_risk", "LOW")

    st.subheader("🌦 Weather Risk")

    if weather_risk_val == "HIGH":
        st.error("HIGH Weather Risk")
    elif weather_risk_val == "MEDIUM":
        st.warning("MEDIUM Weather Risk")
    else:
        st.success("LOW Weather Risk")

    # =====================================
    # 6. EXPORT REPORT ENGINE (PDF GENERATOR)
    # =====================================
    st.markdown("---")
    st.subheader("📥 Export Report")

    # In-memory document constructor
    def generate_pdf(vinfo, score, speed_var, fuel_var, risk, claim):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor("#0F172A"), spaceAfter=15)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor("#1E3A8A"), spaceBefore=12, spaceAfter=8)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#334155"), leading=14)
        
        # Report Headers
        story.append(Paragraph("NautiMind Voyage Intelligence Report", title_style))
        story.append(Paragraph("Executive Performance Analysis & Diagnostics Summary", body_style))
        story.append(Spacer(1, 15))
        
        # Vessel Info Table
        story.append(Paragraph("🚢 Vessel Particulars", section_style))
        v_data = [
            [Paragraph("<b>Vessel Name:</b>", body_style), Paragraph(str(vinfo['vessel_name']), body_style),
             Paragraph("<b>IMO Number:</b>", body_style), Paragraph(str(vinfo['imo']), body_style)],
            [Paragraph("<b>Voyage No:</b>", body_style), Paragraph(str(vinfo['voyage']), body_style),
             Paragraph("<b>Performance Score:</b>", body_style), Paragraph(f"{score}/100", body_style)]
        ]
        t1 = Table(v_data, colWidths=[120, 140, 120, 140])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t1)
        story.append(Spacer(1, 15))
        
        # Analytics Table
        story.append(Paragraph("📊 Operational Diagnostic Performance Metrics", section_style))
        metrics_data = [
            ["Key Performance Parameter", "Analysis / Variance Threshold Value"],
            ["Speed Variance Profile", f"{speed_var} kn"],
            ["Bunker Consumption Variance", f"{fuel_var} MT"],
            ["Weather Risk Stratum Profile", str(risk)],
            ["Charter Performance Claim Status", str(claim)]
        ]
        t2 = Table(metrics_data, colWidths=[260, 260])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t2)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # Create the PDF file stream
    pdf_data = generate_pdf(
        vinfo=vessel_info,
        score=performance_score,
        speed_var=speed_variance,
        fuel_var=fuel_variance,
        risk=weather_risk_val,
        claim=charter_status
    )

    # Clean executive download button
    st.download_button(
        label="📄 Download Voyage PDF Report",
        data=pdf_data,
        file_name=f"NautiMind_Voyage_Report_{vessel_info['voyage']}.pdf",
        mime="application/pdf"
    )