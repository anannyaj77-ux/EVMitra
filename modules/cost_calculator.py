"""
EVMitra – EV vs Petrol Cost Calculator
Interactive calculator comparing EV running costs vs petrol vehicle.

Formulas:
    EV:
        energy_kWh = distance_km × wh_per_km / 1000
        ev_cost = energy_kWh × electricity_tariff_per_kWh

    Petrol:
        petrol_litres = distance_km / mileage_kmpl
        petrol_cost = petrol_litres × petrol_price_per_litre

    Savings = petrol_cost - ev_cost

All results are ESTIMATES. Actual costs vary with driving conditions.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.calculations import calculate_ev_cost, calculate_petrol_cost, calculate_savings


def render():
    """Render the Cost Calculator page."""
    st.markdown('<h1 class="page-title">💰 EV vs Petrol Cost Calculator</h1>', unsafe_allow_html=True)
    st.markdown("Compare the estimated running cost of an Electric Vehicle vs a Petrol vehicle.")
    st.info("⚠️ All results are **ESTIMATES** based on the values you enter. Actual costs depend on driving conditions, battery health, traffic, and current fuel prices.")

    with st.expander("📐 How the calculation works", expanded=False):
        st.markdown("""
        **EV Running Cost:**
        ```
        Energy (kWh)  = Distance (km) × EV Consumption (Wh/km) ÷ 1000
        EV Cost (₹)   = Energy (kWh) × Electricity Tariff (₹/kWh)
        ```
        
        **Petrol Vehicle Running Cost:**
        ```
        Fuel Used (L) = Distance (km) ÷ Mileage (km/L)
        Petrol Cost   = Fuel Used (L) × Petrol Price (₹/L)
        ```
        
        **Savings:**
        ```
        Savings = Petrol Cost − EV Cost
        ```
        
        A positive savings value means the EV is cheaper to run.
        """)

    st.markdown("---")
    st.subheader("⚙️ Input Parameters")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📏 Distance & Period**")
        period = st.selectbox("Calculation Period",
                               ["Daily", "Monthly (30 days)", "Annual (365 days)", "Custom Distance"],
                               help="Select the time period for comparison")

        if period == "Custom Distance":
            distance = st.number_input("Total Distance (km)", min_value=1.0, max_value=1000000.0,
                                        value=10000.0, step=100.0)
        elif period == "Daily":
            daily_km = st.number_input("Daily Distance (km)", min_value=1.0, max_value=1000.0,
                                        value=40.0, step=5.0)
            distance = daily_km
        elif period == "Monthly (30 days)":
            daily_km = st.number_input("Daily Distance (km)", min_value=1.0, max_value=1000.0,
                                        value=40.0, step=5.0)
            distance = daily_km * 30
        else:  # Annual
            daily_km = st.number_input("Daily Distance (km)", min_value=1.0, max_value=1000.0,
                                        value=40.0, step=5.0)
            distance = daily_km * 365

        st.markdown("**⚡ EV Parameters**")
        wh_per_km = st.number_input("EV Energy Consumption (Wh/km)",
                                     min_value=10.0, max_value=500.0, value=120.0, step=5.0,
                                     help="Typical Indian EVs: 80-200 Wh/km. Check your EV specs.")
        electricity_tariff = st.number_input("Electricity Tariff (₹/kWh)",
                                              min_value=1.0, max_value=20.0, value=8.0, step=0.5,
                                              help="Residential tariff in India: ₹6–12/kWh typically")

    with col2:
        st.markdown("**⛽ Petrol Vehicle Parameters**")
        petrol_mileage = st.number_input("Petrol Vehicle Mileage (km/L)",
                                          min_value=5.0, max_value=50.0, value=15.0, step=0.5,
                                          help="Typical Indian car: 12-18 km/L; 2-wheeler: 40-60 km/L")
        petrol_price = st.number_input("Petrol Price (₹/litre)",
                                        min_value=50.0, max_value=200.0, value=105.0, step=1.0,
                                        help="Petrol price varies by city. Check current local prices.")

        st.markdown("**🏠 Optional: EV Purchase Details**")
        ev_price = st.number_input("EV Purchase Price (₹) — Optional", min_value=0, max_value=10000000,
                                    value=0, step=10000,
                                    help="Leave 0 to skip purchase cost comparison")
        petrol_price_vehicle = st.number_input("Equivalent Petrol Vehicle Price (₹) — Optional",
                                                min_value=0, max_value=5000000, value=0, step=10000,
                                                help="Leave 0 to skip purchase cost comparison")

    st.markdown("---")

    if st.button("🧮 Calculate Savings", type="primary", use_container_width=True):
        # Validate
        if distance <= 0:
            st.error("Distance must be greater than zero.")
            return

        ev_result = calculate_ev_cost(distance, wh_per_km, electricity_tariff)
        petrol_result = calculate_petrol_cost(distance, petrol_mileage, petrol_price)
        savings = calculate_savings(ev_result["cost_inr"], petrol_result["cost_inr"])

        st.markdown("---")
        st.subheader(f"📊 Results for {distance:,.0f} km ({period})")

        # KPI Cards
        k1, k2, k3 = st.columns(3)
        k1.metric("⚡ EV Running Cost", f"₹{ev_result['cost_inr']:,.0f}",
                  help=f"Energy used: {ev_result['energy_kwh']} kWh")
        k2.metric("⛽ Petrol Running Cost", f"₹{petrol_result['cost_inr']:,.0f}",
                  help=f"Fuel used: {petrol_result['litres_used']} litres")
        k3.metric("💰 Estimated Savings", f"₹{savings:,.0f}",
                  delta=f"EV is {'cheaper' if savings >= 0 else 'costlier'}",
                  delta_color="normal" if savings >= 0 else "inverse")

        # Additional breakdowns
        st.markdown("---")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("🔋 Energy Consumed", f"{ev_result['energy_kwh']} kWh")
        d2.metric("🛢️ Petrol Avoided", f"{petrol_result['litres_used']} L")
        d3.metric("💡 EV Cost/km", f"₹{ev_result['cost_inr']/distance:.2f}/km")
        d4.metric("⛽ Petrol Cost/km", f"₹{petrol_result['cost_inr']/distance:.2f}/km")

        # Period extrapolations
        if period not in ["Annual (365 days)", "Custom Distance"]:
            st.markdown("---")
            st.subheader("📅 Extrapolated Savings")
            if period == "Daily":
                monthly_saving = savings * 30
                annual_saving = savings * 365
            elif period == "Monthly (30 days)":
                monthly_saving = savings
                annual_saving = savings * 12

            e1, e2 = st.columns(2)
            e1.metric("📅 Monthly Savings", f"₹{monthly_saving:,.0f}")
            e2.metric("📆 Annual Savings", f"₹{annual_saving:,.0f}")

        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["⚡ EV Cost", "⛽ Petrol Cost"],
            y=[ev_result['cost_inr'], petrol_result['cost_inr']],
            marker_color=["#10b981", "#ef4444"],
            text=[f"₹{ev_result['cost_inr']:,.0f}", f"₹{petrol_result['cost_inr']:,.0f}"],
            textposition="outside",
        ))
        fig.update_layout(
            title=f"Cost Comparison for {distance:,.0f} km",
            yaxis_title="Cost (₹)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Breakeven if purchase prices given
        if ev_price > 0 and petrol_price_vehicle > 0:
            extra_cost = ev_price - petrol_price_vehicle
            if extra_cost > 0 and savings > 0:
                # How many km to break even
                savings_per_km = savings / distance
                breakeven_km = extra_cost / savings_per_km
                st.markdown("---")
                st.subheader("🎯 Breakeven Analysis (Purchase Cost Considered)")
                b1, b2, b3 = st.columns(3)
                b1.metric("Extra Cost of EV", f"₹{extra_cost:,.0f}")
                b2.metric("Savings per km", f"₹{savings_per_km:.3f}/km")
                b3.metric("Breakeven at", f"{breakeven_km:,.0f} km")
                st.caption(f"*After {breakeven_km:,.0f} km of driving, the EV becomes more economical total.*")
            elif extra_cost <= 0:
                st.success(f"✅ The EV is cheaper to buy too (by ₹{abs(extra_cost):,.0f})! You're ahead from day one.")

        # Save to history
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({
            "action": "Cost Calculator",
            "result": f"Savings: ₹{savings:,.0f} over {distance:,.0f} km ({period})",
            "prefs": f"EV: ₹{ev_result['cost_inr']:,.0f} | Petrol: ₹{petrol_result['cost_inr']:,.0f}",
        })
