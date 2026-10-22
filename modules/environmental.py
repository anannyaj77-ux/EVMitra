"""
EVMitra – Environmental Impact Module
Estimates CO2 emissions avoided, petrol saved, and money saved by driving EV.

Methodology:
    CO2 Avoided (kg) = Petrol Avoided (litres) × 2.31 kg CO₂/litre
    
    CO2 factor source: IPCC / Central Pollution Control Board approx.
    (Petrol: ~2.31 kg CO₂ per litre combusted)
    
    IMPORTANT:
    - Results are ESTIMATES only.
    - EVs have upstream emissions (manufacturing, power generation).
    - This calculator estimates only DIRECT VEHICLE TAILPIPE emissions avoided.
    - We do NOT claim EVs have zero lifecycle emissions.
    - Results are NOT "official carbon credits" — they are informational estimates.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.calculations import calculate_ev_cost, calculate_petrol_cost, calculate_co2_avoided


CO2_FACTOR = 2.31  # kg CO2 per litre of petrol combusted (IPCC/CPCB approx.)
CO2_SOURCE = "IPCC 2006 Guidelines for National Greenhouse Gas Inventories / CPCB approximation"


def render():
    """Render the Environmental Impact page."""
    st.markdown('<h1 class="page-title">🌱 Environmental Impact</h1>', unsafe_allow_html=True)
    st.markdown("Understand the estimated environmental benefits of choosing an Electric Vehicle over a petrol vehicle.")

    st.warning("""
    **Important Note:** These are **estimates of tailpipe/direct emissions avoided** only. 
    Electric vehicles have upstream emissions from manufacturing and electricity generation. 
    Results shown here are **NOT official carbon credits** and should not be presented as such.
    """)

    st.markdown("---")
    st.subheader("📏 Enter Your Driving Data")

    col1, col2 = st.columns(2)
    with col1:
        distance = st.number_input("Total Distance (km)", min_value=1.0, max_value=1000000.0,
                                    value=15000.0, step=500.0,
                                    help="Total distance driven (e.g., annual distance)")
        wh_per_km = st.number_input("EV Consumption (Wh/km)", min_value=10.0, max_value=500.0,
                                     value=120.0, step=5.0,
                                     help="Your EV's energy consumption in Wh per km")
        tariff = st.number_input("Electricity Tariff (₹/kWh)", min_value=1.0, max_value=20.0,
                                  value=8.0, step=0.5)

    with col2:
        mileage = st.number_input("Equivalent Petrol Mileage (km/L)", min_value=5.0, max_value=50.0,
                                   value=15.0, step=0.5,
                                   help="The mileage of the petrol car you would have driven")
        petrol_price = st.number_input("Petrol Price (₹/litre)", min_value=50.0, max_value=200.0,
                                        value=105.0, step=1.0)

        with st.expander("ℹ️ CO₂ Factor Used"):
            st.markdown(f"""
            **CO₂ emission factor:** {CO2_FACTOR} kg CO₂ per litre of petrol combusted
            
            **Source:** {CO2_SOURCE}
            
            This is an approximate average. Actual factor may vary.
            """)

    st.markdown("---")

    if st.button("🌿 Calculate Environmental Impact", type="primary", use_container_width=True):
        ev_result = calculate_ev_cost(distance, wh_per_km, tariff)
        petrol_result = calculate_petrol_cost(distance, mileage, petrol_price)
        co2_avoided = calculate_co2_avoided(petrol_result["litres_used"], CO2_FACTOR)
        money_saved = petrol_result["cost_inr"] - ev_result["cost_inr"]

        st.markdown("---")
        st.subheader(f"🌍 Estimated Environmental Impact for {distance:,.0f} km")

        # KPI cards
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🌿 Est. CO₂ Avoided", f"{co2_avoided:,.0f} kg",
                  help="Estimated tailpipe CO₂ avoided vs equivalent petrol vehicle")
        k2.metric("🛢️ Petrol Avoided", f"{petrol_result['litres_used']:,.1f} L",
                  help="Litres of petrol not burned")
        k3.metric("💰 Money Saved", f"₹{money_saved:,.0f}",
                  help="Running cost savings vs petrol vehicle")
        k4.metric("⚡ Energy Consumed", f"{ev_result['energy_kwh']:,.1f} kWh")

        # Equivalence comparisons (fun facts)
        trees_equivalent = co2_avoided / 21  # ~21 kg CO2 absorbed per tree per year
        homes_equivalent = co2_avoided / 2000  # ~2000 kg CO2 per avg Indian home per year

        st.markdown("---")
        st.subheader("🌳 What Does This Mean?")
        e1, e2, e3 = st.columns(3)
        e1.metric("🌳 Trees needed 1 year to absorb", f"≈ {trees_equivalent:.0f} trees",
                  help="Approx. 21 kg CO₂/tree/year absorbed (rough estimate)")
        e2.metric("🏠 Home energy equivalent", f"≈ {homes_equivalent:.2f} homes",
                  help="Rough equivalent in avg Indian home annual CO₂")
        e3.metric("🌿 CO₂ per km avoided", f"≈ {co2_avoided/distance*1000:.0f} g/km",
                  help="Grams of CO₂ per km compared to petrol vehicle")

        # Visual gauge
        max_co2 = petrol_result["litres_used"] * CO2_FACTOR
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=co2_avoided,
            title={"text": "Est. CO₂ Avoided (kg)", "font": {"color": "#e2e8f0"}},
            delta={"reference": 0, "increasing": {"color": "#10b981"}},
            gauge={
                "axis": {"range": [0, max_co2 * 1.1], "tickcolor": "#e2e8f0"},
                "bar": {"color": "#10b981"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, max_co2 * 0.4], "color": "rgba(255,200,0,0.2)"},
                    {"range": [max_co2 * 0.4, max_co2 * 0.7], "color": "rgba(0,200,100,0.2)"},
                    {"range": [max_co2 * 0.7, max_co2 * 1.1], "color": "rgba(0,150,255,0.2)"},
                ],
            },
            number={"font": {"color": "#10b981", "size": 40}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=300,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Comparison bar
        fig_bar = go.Figure(go.Bar(
            x=["EV (est. upstream\nemissions varies)", "Petrol Vehicle\n(tailpipe only)"],
            y=[0, co2_avoided],  # EV tailpipe = 0; petrol tailpipe = co2_avoided
            marker_color=["#10b981", "#ef4444"],
            text=["0 kg (tailpipe)", f"{co2_avoided:,.0f} kg"],
            textposition="outside",
        ))
        fig_bar.update_layout(
            title="Estimated Tailpipe CO₂ Emissions Comparison",
            yaxis_title="CO₂ (kg)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=350,
            annotations=[{
                "x": 0, "y": co2_avoided * 0.1,
                "text": "EV has zero tailpipe\nemissions during driving",
                "showarrow": False,
                "font": {"color": "#10b981", "size": 10},
            }]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Noise impact
        st.markdown("---")
        st.subheader("🔇 Noise Impact")
        st.info("""
        **Electric vehicles produce significantly less noise** than petrol vehicles during operation:
        - EVs are virtually silent at low speeds (< 30 km/h)
        - Tyre and wind noise become dominant above 50-60 km/h (same as petrol vehicles)
        - Reduced urban noise pollution benefits communities, especially near schools and hospitals
        
        *Quantitative dB measurements vary by model and conditions. This is a qualitative assessment.*
        """)

        st.caption(f"*CO₂ factor used: {CO2_FACTOR} kg/litre. Source: {CO2_SOURCE}. All results are estimates.*")

        # Save to history
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({
            "action": "Environmental Impact",
            "result": f"Est. CO₂ avoided: {co2_avoided:,.0f} kg | Petrol saved: {petrol_result['litres_used']:,.1f}L",
            "prefs": f"Distance: {distance:,.0f} km",
        })
