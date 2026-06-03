import streamlit as st
import pandas as pd
import plotly.express as px

from models.performance_engine import extract_performance_data
from models.analysis_engine import analyze_performance
from models.cost_engine import calculate_cost_impact
from models.weather_engine import weather_risk
from models.trend_engine import extract_daily_trends
from models.score_engine import vessel_score

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="NautiMind",
    page_icon="🚢",
    layout="wide"
)

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("NautiMind")

page = st.sidebar.radio(
    "Navigation",
    [
        "main",
        "performance",
        "weather",
        "optimization",
        "reports"
    ]
)

# =====================================
# MAIN PAGE
# =====================================

if page == "main":

    st.title("🚢 Vessel Performance & Voyage Optimization")

    uploaded_file = st.file_uploader(
        "Upload Noon Report",
        type=["xlsx", "xls", "xlsm", "csv"]
    )

    if uploaded_file is not None:

        try:

            st.success(f"Uploaded: {uploaded_file.name}")

            excel_file = pd.ExcelFile(uploaded_file)

            st.subheader("Available Sheets")
            st.write(excel_file.sheet_names)

            # CHANGE 1: Force APR 22 if available
            if "APR 22" in excel_file.sheet_names:
                selected_sheet = "APR 22"
            else:
                selected_sheet = st.selectbox(
                    "Select Sheet",
                    excel_file.sheet_names
                )

            df = pd.read_excel(
                uploaded_file,
                sheet_name=selected_sheet,
                header=None
            )

            st.subheader(f"{selected_sheet} Report Data")
            st.dataframe(df)

            if True:

                # ==========================
                # VESSEL INFORMATION
                # ==========================

                st.subheader("🚢 Vessel Information")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Vessel",
                        "MV DEMO"
                    )

                with col2:
                    st.metric(
                        "IMO Number",
                        "1234567"
                    )

                with col3:
                    st.metric(
                        "Voyage No",
                        "VOY-001"
                    )

                # ==========================
                # PERFORMANCE METRICS
                # ==========================

                metrics = extract_performance_data(df)

                st.session_state["metrics"] = metrics

                st.subheader("📊 Performance Metrics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Allowed Speed",
                        f"{metrics['allowed_speed']} kn"
                    )

                with col2:
                    st.metric(
                        "Actual Speed",
                        f"{metrics['actual_speed']} kn"
                    )

                with col3:
                    st.metric(
                        "Fuel Consumption",
                        f"{metrics['fuel_consumption']} MT"
                    )

                with col4:
                    st.metric(
                        "Wind Speed",
                        f"{metrics['wind_speed']} kn"
                    )

                # ==========================
                # PERFORMANCE ANALYSIS
                # ==========================

                analysis = analyze_performance(metrics)

                score = vessel_score(
                    metrics,
                    analysis
                )

                st.session_state["analysis"] = analysis
                st.session_state["score"] = score

                st.subheader("🏆 Vessel Performance Score")

                st.metric(
                    "Overall Score",
                    f"{score}/100"
                )

                if score >= 85:
                    st.success("Excellent Performance")

                elif score >= 70:
                    st.warning("Average Performance")

                else:
                    st.error("Poor Performance")

                st.subheader("📈 Performance Analysis")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Speed Variance",
                        f"{analysis['speed_variance']} knots"
                    )

                with col2:
                    st.metric(
                        "Fuel Variance",
                        f"{analysis['fuel_variance']} MT"
                    )

                st.write(f"🚢 Speed Status: {analysis['speed_status']}")
                st.write(f"⛽ Fuel Status: {analysis['fuel_status']}")

                # ==========================
                # ALERTS
                # ==========================

                st.subheader("🚨 Alerts")

                if analysis["speed_status"] == "Under Speed":
                    st.error("Vessel is operating below charter speed.")

                elif analysis["speed_status"] == "Over Speed":
                    st.warning("Vessel is operating above charter speed.")

                else:
                    st.success("Vessel speed is within limits.")

                if analysis["fuel_status"] == "Over Consumption":
                    st.error("Fuel consumption exceeds benchmark.")

                else:
                    st.success("Fuel consumption is normal.")

                # ==========================
                # COMMERCIAL IMPACT
                # ==========================

                cost = calculate_cost_impact(analysis)

                st.subheader("💰 Commercial Impact")

                st.metric(
                    "Estimated Additional Fuel Cost",
                    f"${cost}"
                )

                # ==========================
                # WEATHER IMPACT
                # ==========================

                risk = weather_risk(metrics)

                metrics["weather_risk"] = risk
                st.session_state["metrics"] = metrics

                st.subheader("🌦 Weather Impact")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Wind Speed",
                        metrics.get("wind_speed", 0)
                    )

                with col2:
                    st.metric(
                        "Beaufort Scale",
                        metrics.get("beaufort_scale", 0)
                    )

                with col3:
                    st.metric(
                        "Weather Risk",
                        risk
                    )

                if risk == "HIGH":
                    st.error("High weather impact expected.")

                elif risk == "MEDIUM":
                    st.warning("Moderate weather impact expected.")

                else:
                    st.success("Low weather impact.")

                # ==========================
                # DAILY VOYAGE TRENDS
                # ==========================

                trend_data = extract_daily_trends(df)

                st.subheader("📈 Daily Voyage Trends")

                trend_df = pd.DataFrame({
                    "Date": trend_data["dates"],
                    "Speed": trend_data["speeds"],
                    "Fuel": trend_data["fuels"],
                    "Wind": trend_data["winds"]
                })

                st.dataframe(trend_df)

                fig_speed = px.line(
                    trend_df,
                    x="Date",
                    y="Speed",
                    title="Daily Speed Trend",
                    markers=True
                )

                st.plotly_chart(fig_speed, use_container_width=True)

                fig_fuel = px.line(
                    trend_df,
                    x="Date",
                    y="Fuel",
                    title="Daily Fuel Consumption Trend",
                    markers=True
                )

                st.plotly_chart(fig_fuel, use_container_width=True)

                fig_wind = px.line(
                    trend_df,
                    x="Date",
                    y="Wind",
                    title="Daily Wind Speed Trend",
                    markers=True
                )

                st.plotly_chart(fig_wind, use_container_width=True)

                st.subheader("📋 Voyage Summary")

                trend_df["Speed"] = pd.to_numeric(
                    trend_df["Speed"], errors="coerce"
                )

                trend_df["Fuel"] = pd.to_numeric(
                    trend_df["Fuel"], errors="coerce"
                )

                trend_df["Wind"] = pd.to_numeric(
                    trend_df["Wind"], errors="coerce"
                )

                trend_df = trend_df.dropna(subset=["Speed"])
                trend_df = trend_df[trend_df["Speed"] > 0]

                summary_df = pd.DataFrame({
                    "Metric": [
                        "Average Speed",
                        "Average Fuel",
                        "Average Wind"
                    ],
                    "Value": [
                        round(trend_df["Speed"].mean(), 2),
                        round(trend_df["Fuel"].mean(), 2),
                        round(trend_df["Wind"].mean(), 2)
                    ]
                })

                st.dataframe(summary_df)

                # ==========================
                # CHARTER CLAIM ANALYSIS
                # ==========================

                st.subheader("⚖ Charter Claim Analysis")

                speed_gap = (
                    metrics["allowed_speed"]
                    - metrics["actual_speed"]
                )

                if speed_gap > 1.0 and metrics["wind_speed"] < 15:
                    st.error(
                        "Potential Charter Performance Claim Detected"
                    )

                else:
                    st.success(
                        "No Charter Claim Risk"
                    )

                # ==========================
                # FUEL SAVING OPPORTUNITIES
                # ==========================

                st.subheader("⛽ Fuel Saving Opportunities")

                fuel_variance = float(
                    metrics.get("fuel_consumption", 0)
                ) - 12

                saving = max(fuel_variance, 0)

                monthly_saving = saving * 30 * 600

                col1, col2 = st.columns(2)

                with col1:
                    saving = max(fuel_variance, 0)
                    st.metric(
                        "Potential Fuel Saving",
                        f"{saving:.2f} MT/day"
                    )

                with col2:
                    st.metric(
                        "Potential Monthly Saving",
                        f"${monthly_saving:,.0f}"
                    )

            else:
                pass

        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)

# =====================================
# PERFORMANCE PAGE
# =====================================

elif page == "performance":

    st.title("📈 Vessel Performance Dashboard")

    metrics = st.session_state.get("metrics")
    analysis = st.session_state.get("analysis")
    score = st.session_state.get("score")

    if not metrics:
        st.warning(
            "No data loaded. Please upload a Noon Report on the main page first."
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Performance Score",
                f"{score}/100"
            )

        with col2:
            st.metric(
                "Speed Variance",
                f"{analysis['speed_variance']} kn"
            )

        with col3:
            st.metric(
                "Fuel Variance",
                f"{analysis['fuel_variance']} MT"
            )

        st.subheader("🚢 Speed Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Allowed Speed",
                f"{metrics['allowed_speed']} kn"
            )

        with col2:
            st.metric(
                "Actual Speed",
                f"{metrics['actual_speed']} kn"
            )

        st.write(f"Speed Status: {analysis['speed_status']}")

        st.subheader("⛽ Fuel Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Fuel Consumption",
                f"{metrics.get('fuel_consumption', 0)} MT"
            )

        with col2:
            st.metric(
                "Fuel Status",
                analysis['fuel_status']
            )

# =====================================
# WEATHER PAGE
# =====================================

elif page == "weather":

    st.title("🌦 Weather Analysis")

    st.info("Weather analysis module coming soon.")

# =====================================
# OPTIMIZATION PAGE
# =====================================

elif page == "optimization":

    st.title("🧭 Voyage Optimization")

    st.info("Voyage optimization module coming soon.")

# =====================================
# REPORTS PAGE
# =====================================

elif page == "reports":

    st.title("📄 Vessel Performance Report")

    metrics = st.session_state.get("metrics")
    analysis = st.session_state.get("analysis")
    score = st.session_state.get("score")

    if not metrics:
        st.warning(
            "No data loaded. Please upload a Noon Report on the main page first."
        )

    else:

        st.subheader("🚢 Vessel Information")

        st.write("Vessel: MV DEMO")
        st.write("IMO: 1234567")
        st.write("Voyage: VOY-001")

        st.subheader("📊 Performance Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Performance Score",
                f"{score}/100"
            )

        with col2:
            st.metric(
                "Speed Variance",
                f"{analysis['speed_variance']} kn"
            )

        with col3:
            st.metric(
                "Fuel Variance",
                f"{analysis['fuel_variance']} MT"
            )

        st.subheader("⚖ Charter Claim Analysis")

        if analysis["speed_variance"] < 0:
            st.error("Potential Charter Performance Claim Detected")
        else:
            st.success("No Charter Claim Risk")

        st.subheader("⛽ Fuel Saving Opportunities")

        fuel_variance = analysis["fuel_variance"]

        if fuel_variance > 0:

            st.metric(
                "Potential Fuel Saving",
                f"{fuel_variance:.2f} MT/day"
            )

            monthly_saving = fuel_variance * 30 * 600

            st.metric(
                "Potential Monthly Saving",
                f"${monthly_saving:,.0f}"
            )

        else:

            st.success(
                "Fuel consumption is already below benchmark."
            )

            st.metric(
                "Potential Fuel Saving",
                "0.00 MT/day"
            )

            st.metric(
                "Potential Monthly Saving",
                "$0"
            )
            
        st.subheader("🌦 Weather Risk")

        risk = metrics.get("weather_risk", "LOW")

        if risk == "HIGH":
            st.error("HIGH Weather Risk")

        elif risk == "MEDIUM":
            st.warning("MEDIUM Weather Risk")

        else:
            st.success("LOW Weather Risk")

        if st.button("Generate Report"):
            st.success("Report Generated Successfully")