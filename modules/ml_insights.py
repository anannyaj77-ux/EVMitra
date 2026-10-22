"""
EVMitra – ML Insights Module
EV Range Prediction using trained ML model.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import numpy as np
from ml.predict import predict_range, load_metadata


def render():
    """Render the Machine Learning Insights page."""
    st.markdown('<h1 class="page-title">🤖 ML Insights – EV Range Prediction</h1>', unsafe_allow_html=True)
    st.markdown("Use a trained Machine Learning model to predict the estimated range of an EV based on its specifications.")

    # Model info
    metadata = load_metadata()

    with st.expander("📚 About the ML Model", expanded=False):
        if metadata:
            st.markdown(f"""
            **Target Variable:** EV Range (km) — predicts how far an EV can travel on a full charge.
            
            **Why Range?** Range is the most practically useful and objectively measurable prediction target 
            supported by the available dataset (battery capacity, motor power, energy consumption).
            
            **Features Used:**
            | Feature | Description |
            |---------|-------------|
            | `battery_kwh` | Battery capacity in kWh |
            | `motor_power_kw` | Motor output power in kW |
            | `wh_per_km` | Energy consumption in Wh/km |
            | `vehicle_type` | Category of vehicle (Car/Scooter/Motorcycle/E-Rickshaw) |
            
            **Models Compared:**
            1. Linear Regression
            2. Random Forest Regressor
            3. Gradient Boosting Regressor
            
            **Best Model Selected:** {metadata.get('model_name', 'N/A')} (highest R²)
            
            **Training Data:** EVMitra curated EV specs database + physically-plausible synthetic augmentation.
            
            **Dataset Note:** {metadata.get('dataset_note', '')}
            """)

            st.markdown("**Actual Model Evaluation Metrics (from training):**")
            metrics = metadata.get("metrics", {})
            if metrics:
                for name, m in metrics.items():
                    st.markdown(f"- **{name}:** MAE = {m.get('mae','N/A')} km | RMSE = {m.get('rmse','N/A')} km | R² = {m.get('r2','N/A')}")

            best = metadata.get("best_model_metrics", {})
            if best:
                b1, b2, b3 = st.columns(3)
                b1.metric("MAE", f"{best.get('mae','N/A')} km", help="Mean Absolute Error — avg prediction error in km")
                b2.metric("RMSE", f"{best.get('rmse','N/A')} km", help="Root Mean Squared Error")
                b3.metric("R²", f"{best.get('r2','N/A')}", help="Coefficient of Determination — closer to 1.0 is better")

            st.caption(f"Trained on: {metadata.get('trained_on', 'N/A')} | Train size: {metadata.get('train_size', 'N/A')} | Test size: {metadata.get('test_size', 'N/A')}")
        else:
            st.warning("Model not yet trained. Please run `python ml/train_model.py` to train the model.")

    st.markdown("---")
    st.subheader("🔮 Predict EV Range")
    st.markdown("Enter EV specifications to get a predicted range from the trained model.")

    col1, col2 = st.columns(2)
    with col1:
        battery_kwh = st.number_input("🔋 Battery Capacity (kWh)", min_value=0.5, max_value=150.0,
                                       value=40.0, step=0.5)
        motor_power_kw = st.number_input("⚡ Motor Power (kW)", min_value=1.0, max_value=400.0,
                                          value=100.0, step=1.0)
    with col2:
        wh_per_km = st.number_input("💡 Energy Consumption (Wh/km)", min_value=10.0, max_value=500.0,
                                     value=120.0, step=5.0,
                                     help="Typical: Car ~100-150, Scooter ~20-40, Motorcycle ~20-30")
        vehicle_type = st.selectbox("🚗 Vehicle Type", ["Car", "Scooter", "Motorcycle", "E-Rickshaw"])

    if st.button("🤖 Predict Range", type="primary", use_container_width=True):
        result = predict_range(battery_kwh, motor_power_kw, wh_per_km, vehicle_type)

        st.markdown("---")
        st.subheader("📊 Prediction Results")

        col_ml, col_physics = st.columns(2)
        with col_ml:
            st.metric(
                f"🤖 ML Model Prediction",
                f"{result['predicted_range_km']} km",
                help=f"Model: {result.get('model_name','N/A')}"
            )
            st.caption(f"Model: {result.get('model_name','N/A')}")

        with col_physics:
            st.metric(
                "📐 Physics-Based Estimate",
                f"{result['physics_range_km']} km",
                help="range = (battery_kWh × 1000) / wh_per_km"
            )
            st.caption("Formula: (battery_kWh × 1000) ÷ wh_per_km")

        if result.get("error"):
            st.warning(f"⚠️ Note: {result['error']}")

        # Visualization
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["ML Model Prediction", "Physics Estimate"],
            y=[result["predicted_range_km"], result["physics_range_km"]],
            marker_color=["#00d4ff", "#7c3aed"],
            text=[f"{result['predicted_range_km']} km", f"{result['physics_range_km']} km"],
            textposition="outside",
        ))
        fig.update_layout(
            title="Predicted Range Comparison",
            yaxis_title="Range (km)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info("""
        **Interpreting Results:**
        - The ML model prediction is based on patterns learned from the EV database
        - The physics estimate uses a direct formula: `range = (battery × 1000) ÷ efficiency`
        - Actual range varies with driving conditions, temperature, speed, and payload
        - Manufacturer claimed range is measured under controlled conditions
        """)

    # Range sensitivity analysis
    st.markdown("---")
    st.subheader("📈 Range Sensitivity Analysis")
    st.markdown("How does range change as battery capacity varies? (holding other specs constant)")

    sensitivity_wh = st.slider("Efficiency for Sensitivity (Wh/km)", 20.0, 300.0, 120.0, 5.0,
                                key="sensitivity_wh")

    battery_range = list(range(5, 105, 5))
    range_vals = [(b * 1000 / sensitivity_wh) for b in battery_range]

    fig2 = px.line(
        x=battery_range, y=range_vals,
        labels={"x": "Battery Capacity (kWh)", "y": "Estimated Range (km)"},
        title=f"Range vs Battery Capacity (at {sensitivity_wh} Wh/km)",
        color_discrete_sequence=["#00d4ff"]
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=350,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("*This is a direct physics relationship: Range = (Battery kWh × 1000) ÷ Efficiency (Wh/km)*")
