"""
EVMitra – EV Owner Analytics Module
Analyze your personal EV usage from CSV data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.validation import validate_owner_csv


SAMPLE_CSV_PATH = "data/sample_owner_analytics.csv"

REQUIRED_COLUMNS_INFO = """
| Column | Required | Type | Description |
|--------|----------|------|-------------|
| `date` | ✅ Yes | Date (YYYY-MM-DD) | Date of the trip/log |
| `distance_km` | ✅ Yes | Number | Distance driven in km |
| `energy_consumed_kwh` | ✅ Yes | Number | Energy consumed in kWh |
| `charging_cost_inr` | Optional | Number | Cost of charging in ₹ |
| `temperature_c` | Optional | Number | Ambient temperature in °C |
| `notes` | Optional | Text | Any notes |
"""


def compute_analytics(df: pd.DataFrame, tariff: float) -> dict:
    """Compute analytics from validated owner dataframe."""
    df = df.copy()
    df["wh_per_km"] = (df["energy_consumed_kwh"] * 1000) / df["distance_km"]
    df["est_cost_inr"] = df["energy_consumed_kwh"] * tariff

    total_km = df["distance_km"].sum()
    total_energy = df["energy_consumed_kwh"].sum()
    avg_wh_per_km = df["wh_per_km"].mean()
    avg_daily_km = df["distance_km"].mean()
    total_cost = df.get("charging_cost_inr", pd.Series(dtype=float)).sum()
    if total_cost == 0:
        total_cost = df["est_cost_inr"].sum()

    # Range estimate: battery_kwh / avg consumption
    # Without battery info we just show avg efficiency
    cost_per_km = total_cost / total_km if total_km > 0 else 0

    return {
        "df": df,
        "total_km": round(total_km, 1),
        "total_energy": round(total_energy, 2),
        "avg_wh_per_km": round(avg_wh_per_km, 1),
        "avg_daily_km": round(avg_daily_km, 1),
        "total_cost": round(total_cost, 2),
        "cost_per_km": round(cost_per_km, 2),
        "num_days": len(df),
    }


def render_kpi_cards(analytics: dict):
    """Display KPI metric cards."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📏 Total Distance", f"{analytics['total_km']:,} km")
    c2.metric("⚡ Total Energy", f"{analytics['total_energy']:,} kWh")
    c3.metric("💡 Avg Efficiency", f"{analytics['avg_wh_per_km']} Wh/km")
    c4.metric("📅 Avg Daily Drive", f"{analytics['avg_daily_km']} km")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("💰 Est. Total Cost", f"₹{analytics['total_cost']:,.0f}")
    c6.metric("💰 Cost per km", f"₹{analytics['cost_per_km']:.2f}/km")
    c7.metric("📊 Days Logged", f"{analytics['num_days']}")
    c8.metric("🗓️ Period", f"{analytics['df']['date'].min().date()} to {analytics['df']['date'].max().date()}")


def render_charts(df: pd.DataFrame):
    """Render analytics charts."""
    st.markdown("---")
    st.subheader("📈 Analytics Charts")

    # 1. Distance over time
    fig1 = px.line(df, x="date", y="distance_km",
                   title="Daily Distance Driven (km)",
                   labels={"distance_km": "Distance (km)", "date": "Date"},
                   color_discrete_sequence=["#00d4ff"])
    fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#e2e8f0"))
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Energy consumption trend
    fig2 = px.line(df, x="date", y="energy_consumed_kwh",
                   title="Daily Energy Consumed (kWh)",
                   labels={"energy_consumed_kwh": "Energy (kWh)", "date": "Date"},
                   color_discrete_sequence=["#7c3aed"])
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#e2e8f0"))
    st.plotly_chart(fig2, use_container_width=True)

    # 3. Efficiency trend
    fig3 = px.scatter(df, x="date", y="wh_per_km",
                      title="Energy Efficiency over Time (Wh/km) — Lower is Better",
                      trendline="ols",
                      color_discrete_sequence=["#f59e0b"],
                      labels={"wh_per_km": "Efficiency (Wh/km)", "date": "Date"})
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#e2e8f0"))
    st.plotly_chart(fig3, use_container_width=True)

    # 4. Cost trend
    fig4 = px.bar(df, x="date", y="est_cost_inr",
                  title="Estimated Daily Charging Cost (₹)",
                  labels={"est_cost_inr": "Cost (₹)", "date": "Date"},
                  color_discrete_sequence=["#10b981"])
    fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#e2e8f0"))
    st.plotly_chart(fig4, use_container_width=True)

    # 5. Temperature vs Efficiency (if temperature column exists)
    if "temperature_c" in df.columns and df["temperature_c"].notna().any():
        df_temp = df.dropna(subset=["temperature_c"])
        fig5 = px.scatter(df_temp, x="temperature_c", y="wh_per_km",
                          title="Temperature vs Efficiency",
                          labels={"temperature_c": "Temperature (°C)", "wh_per_km": "Wh/km"},
                          color_discrete_sequence=["#ef4444"],
                          trendline="ols")
        fig5.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font=dict(color="#e2e8f0"))
        st.plotly_chart(fig5, use_container_width=True)

    # 6. Weekly summary
    df["week"] = df["date"].dt.isocalendar().week.astype(str)
    weekly = df.groupby("week").agg(
        total_km=("distance_km", "sum"),
        total_energy=("energy_consumed_kwh", "sum")
    ).reset_index()
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(x=weekly["week"], y=weekly["total_km"], name="Distance (km)", marker_color="#00d4ff"))
    fig6.add_trace(go.Bar(x=weekly["week"], y=weekly["total_energy"] * 10, name="Energy × 10 (kWh)", marker_color="#7c3aed"))
    fig6.update_layout(
        title="Weekly Summary",
        barmode="group",
        xaxis_title="Week Number",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig6, use_container_width=True)


def render_recommendations(analytics: dict):
    """Generate intelligent owner recommendations."""
    st.markdown("---")
    st.subheader("💡 Personalized Insights & Recommendations")

    avg_wh = analytics["avg_wh_per_km"]
    avg_km = analytics["avg_daily_km"]
    cost_per_km = analytics["cost_per_km"]

    insights = []

    if avg_wh < 80:
        insights.append(("✅ Excellent efficiency!", f"Your average {avg_wh} Wh/km is very efficient. Keep up the smooth driving style.", "success"))
    elif avg_wh < 120:
        insights.append(("⚡ Good efficiency", f"Your average {avg_wh} Wh/km is good. Avoid heavy acceleration to improve further.", "info"))
    else:
        insights.append(("⚠️ High energy consumption", f"Your average {avg_wh} Wh/km is above typical. Check tyre pressure and avoid aggressive driving.", "warning"))

    if avg_km < 30:
        insights.append(("🏠 Short daily trips", f"You drive ~{avg_km} km/day on average. Most EVs are well-suited for this range. Consider overnight charging.", "info"))
    elif avg_km > 150:
        insights.append(("🛣️ Long daily commute", f"You drive ~{avg_km} km/day. Ensure your EV's range comfortably covers this with buffer.", "warning"))

    if cost_per_km < 1.0:
        insights.append(("💰 Great running cost!", f"At ₹{cost_per_km:.2f}/km, your EV is very economical.", "success"))
    elif cost_per_km < 2.0:
        insights.append(("💡 Reasonable running cost", f"₹{cost_per_km:.2f}/km — still far cheaper than petrol at ₹5-7/km for a typical petrol car.", "info"))

    for title, msg, level in insights:
        if level == "success":
            st.success(f"**{title}** — {msg}")
        elif level == "warning":
            st.warning(f"**{title}** — {msg}")
        else:
            st.info(f"**{title}** — {msg}")


def render():
    """Render the EV Owner Analytics page."""
    st.markdown('<h1 class="page-title">📊 EV Owner Analytics</h1>', unsafe_allow_html=True)
    st.markdown("Upload your driving log CSV to get personalized analytics, efficiency trends, and cost insights.")

    # Sample download info
    with st.expander("📋 Required CSV Format & Sample", expanded=False):
        st.markdown(REQUIRED_COLUMNS_INFO)
        st.markdown(f"**Download sample CSV:** Check `data/sample_owner_analytics.csv` in the project folder.")

        try:
            sample_df = pd.read_csv(SAMPLE_CSV_PATH)
            st.dataframe(sample_df.head(5), use_container_width=True)
        except Exception:
            st.caption("Sample file not found. Refer to the column table above.")

    st.markdown("---")

    tariff = st.number_input("⚡ Electricity Tariff (₹/kWh)", min_value=1.0, max_value=20.0,
                              value=8.0, step=0.5,
                              help="Used for estimating charging cost if not in CSV")

    uploaded_file = st.file_uploader("📁 Upload your driving log CSV", type=["csv"],
                                      help="CSV file with date, distance_km, energy_consumed_kwh columns")

    if uploaded_file is None:
        # Show demo with sample data
        st.info("👆 Upload your CSV above, or click below to run a demo with the sample dataset.")
        if st.button("▶️ Run Demo with Sample Data", type="secondary"):
            try:
                df_raw = pd.read_csv(SAMPLE_CSV_PATH)
                is_valid, warn_msg, df_clean = validate_owner_csv(df_raw)
                if is_valid:
                    st.session_state["analytics_df"] = df_clean
                    st.session_state["analytics_tariff"] = tariff
                    st.success("✅ Sample data loaded successfully!")
                else:
                    st.error(f"Sample data error: {warn_msg}")
            except Exception as e:
                st.error(f"Could not load sample data: {e}")
        
        if "analytics_df" not in st.session_state:
            return
        df_clean = st.session_state.get("analytics_df")
        tariff = st.session_state.get("analytics_tariff", 8.0)
    else:
        try:
            df_raw = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ Could not read file: {e}. Please upload a valid CSV.")
            return

        is_valid, warn_msg, df_clean = validate_owner_csv(df_raw)

        if not is_valid:
            st.error(f"❌ CSV Validation Failed: {warn_msg}")
            st.markdown("""
            **Required columns:** `date`, `distance_km`, `energy_consumed_kwh`
            
            Please check your file and re-upload. Refer to the sample format above.
            """)
            return

        if warn_msg:
            st.warning(f"⚠️ {warn_msg}")

        st.success(f"✅ File validated! {len(df_clean)} rows loaded.")
        st.session_state["analytics_df"] = df_clean
        st.session_state["analytics_tariff"] = tariff

    if df_clean is None or df_clean.empty:
        st.warning("No data to analyze.")
        return

    # Compute analytics
    analytics = compute_analytics(df_clean, tariff)
    df = analytics["df"]

    st.markdown("---")
    st.subheader("📊 Summary Dashboard")
    render_kpi_cards(analytics)
    render_charts(df)
    render_recommendations(analytics)

    # Save to history
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        "action": "Owner Analytics",
        "result": f"Analyzed {analytics['num_days']} days, {analytics['total_km']} km total",
        "prefs": f"Avg {analytics['avg_wh_per_km']} Wh/km, Cost ₹{analytics['cost_per_km']}/km",
    })
