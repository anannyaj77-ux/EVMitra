"""
EVMitra – Find My EV (Recommendation Module)
Rule-based + weighted scoring recommendation engine.

Methodology:
    Score = Σ (weight_i × component_score_i) — max 100 points
    
    Components and weights:
        Price match         : 30%
        Range adequacy      : 30%
        Vehicle type match  : 20%
        Charging preference : 10%
        Brand preference    : 10%

    Hard filters applied first (budget ×1.15 max, vehicle type if strict).
    Top 3 ranked by score are returned with explanations.

    This is a transparent, rule-based weighted scoring system.
    It is NOT a machine learning recommendation.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db_helper import execute_query
from utils.calculations import recommendation_score, generate_recommendation_reasons


def load_all_vehicles() -> list[dict]:
    """Load all vehicles from the database."""
    return execute_query("SELECT * FROM ev_vehicles")


def apply_hard_filters(vehicles: list[dict], prefs: dict) -> list[dict]:
    """Remove clearly unsuitable vehicles."""
    filtered = []
    budget = prefs.get("budget", float("inf"))
    vehicle_type = prefs.get("vehicle_type", "Any")
    required_range = prefs.get("required_range_km", 0)

    for ev in vehicles:
        price = ev.get("price_inr", 0) or 0
        ev_range = ev.get("range_km", 0) or 0
        ev_type = ev.get("vehicle_type", "")

        # Hard filter: price must be within 120% of budget
        if budget > 0 and price > budget * 1.20:
            continue

        # Hard filter: range must be at least 50% of required range
        if required_range > 0 and ev_range < required_range * 0.50:
            continue

        # Soft type filter (don't hard-filter, just lower score)
        filtered.append(ev)

    return filtered


def get_recommendations(prefs: dict) -> list[dict]:
    """
    Get top 3 EV recommendations with scores and reasons.
    
    Returns list of dicts: {ev, score, reasons}
    """
    all_vehicles = load_all_vehicles()
    if not all_vehicles:
        return []

    # Apply hard filters
    candidates = apply_hard_filters(all_vehicles, prefs)

    if not candidates:
        return []

    # Score each candidate
    scored = []
    for ev in candidates:
        score = recommendation_score(ev, prefs)
        reasons = generate_recommendation_reasons(ev, prefs)
        scored.append({"ev": ev, "score": score, "reasons": reasons})

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:3]


def render():
    """Render the Find My EV recommendation page."""
    st.markdown('<h1 class="page-title">🎯 Find My EV</h1>', unsafe_allow_html=True)
    st.markdown("Answer a few questions and we'll find the **Top 3 EVs** that best match your needs.")

    with st.expander("ℹ️ How does the recommendation work?", expanded=False):
        st.markdown("""
        **EVMitra uses a transparent, rule-based weighted scoring system:**
        
        | Factor | Weight | Description |
        |--------|--------|-------------|
        | Price match | 30% | How well the EV price fits your budget |
        | Range adequacy | 30% | Whether the EV range covers your daily distance |
        | Vehicle type | 20% | Whether the EV type matches your preference |
        | Charging | 10% | Fast charge availability if preferred |
        | Brand | 10% | Brand preference match |
        
        EVs are first filtered to remove clearly unsuitable options, then scored out of 100.
        
        **This is NOT machine learning** – it is a transparent scoring system so you can understand and verify each recommendation.
        """)

    st.markdown("---")
    st.subheader("📝 Your Preferences")

    col1, col2 = st.columns(2)

    with col1:
        budget = st.number_input("💰 Budget (₹)", min_value=50000, max_value=10000000,
                                  value=1500000, step=50000,
                                  help="Your maximum budget for the EV purchase")
        daily_km = st.number_input("🛣️ Daily Distance (km)", min_value=10, max_value=500,
                                    value=40, step=5,
                                    help="How many km you drive per day on average")
        required_range = st.number_input("🔋 Minimum Required Range (km)", min_value=50, max_value=800,
                                          value=min(daily_km * 2 + 30, 800), step=10,
                                          help="Safety buffer: typically 2× daily distance")

        vehicle_type = st.selectbox("🚗 Preferred Vehicle Type",
                                     ["Any", "Car", "Scooter", "Motorcycle", "E-Rickshaw"],
                                     help="Select your preferred vehicle category")

    with col2:
        brand_pref = st.selectbox("🏷️ Brand Preference",
                                   ["Any", "Tata", "MG", "Hyundai", "Kia", "BYD",
                                    "Mahindra", "Ola Electric", "Ather Energy", "TVS",
                                    "Bajaj", "Hero Electric", "Revolt", "Tork Motors"])
        home_charging = st.checkbox("🏠 I have home charging available", value=True)
        fast_charge_pref = st.checkbox("⚡ I prefer fast charging capability", value=False)

        st.markdown("**Priority Weightings** *(for your awareness)*")
        st.caption("The scoring always uses: Price 30%, Range 30%, Type 20%, Charging 10%, Brand 10%")

    st.markdown("---")

    if st.button("🔍 Find My EV", type="primary", use_container_width=True):
        prefs = {
            "budget": budget,
            "daily_km": daily_km,
            "required_range_km": required_range,
            "vehicle_type": vehicle_type,
            "brand_preference": brand_pref,
            "home_charging": home_charging,
            "fast_charge_preference": fast_charge_pref,
        }

        with st.spinner("Analyzing EVs for you..."):
            recommendations = get_recommendations(prefs)

        if not recommendations:
            st.warning("""
            😕 No EVs matched your requirements.
            
            **Try these adjustments:**
            - Increase your budget
            - Reduce the minimum required range
            - Change vehicle type to 'Any'
            - Remove brand preference
            """)
            return

        st.markdown("---")
        st.subheader(f"🏆 Top {len(recommendations)} EV Recommendations for You")

        # Score chart
        names = [f"{r['ev']['brand']} {r['ev']['model']}" for r in recommendations]
        scores = [r["score"] for r in recommendations]
        colors = ["#ffd700", "#c0c0c0", "#cd7f32"][:len(recommendations)]

        fig = go.Figure(go.Bar(
            x=scores, y=names, orientation='h',
            marker_color=colors[::-1],
            text=[f"{s}/100" for s in scores[::-1]],
            textposition="auto",
        ))
        fig.update_layout(
            title="Recommendation Suitability Scores",
            xaxis_title="Score (out of 100)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=220,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Individual recommendation cards
        medals = ["🥇", "🥈", "🥉"]
        for rank, rec in enumerate(recommendations):
            ev = rec["ev"]
            score = rec["score"]
            reasons = rec["reasons"]

            with st.container():
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-rank">{medals[rank]} Rank #{rank+1} — Suitability Score: {score}/100</div>
                    <h3 class="ev-title">{ev.get('brand','')} {ev.get('model','')}</h3>
                    <div class="ev-price">₹{ev.get('price_inr',0):,.0f}</div>
                </div>
                """, unsafe_allow_html=True)

                kc1, kc2, kc3, kc4 = st.columns(4)
                kc1.metric("🔋 Battery", f"{ev.get('battery_kwh','N/A')} kWh")
                kc2.metric("🛣️ Range", f"{ev.get('range_km','N/A')} km")
                kc3.metric("⚡ Motor", f"{ev.get('motor_power_kw','N/A')} kW")
                kc4.metric("🔌 Charge", f"{ev.get('charge_time_hrs','N/A')}h")

                st.markdown("**Why this EV was recommended:**")
                for reason in reasons:
                    st.markdown(f"  ✅ {reason}")

                fast_note = "⚡ Fast charging supported" if ev.get("fast_charge_supported") else "🔌 Standard charging"
                st.caption(f"{fast_note} | {ev.get('vehicle_type','')} | Source: {ev.get('source','N/A')}")
                st.divider()

        # Save to history
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({
            "action": "Find My EV",
            "result": f"Top pick: {recommendations[0]['ev']['brand']} {recommendations[0]['ev']['model']} (Score: {recommendations[0]['score']}/100)",
            "prefs": f"Budget ₹{budget:,.0f}, Daily {daily_km}km, Type: {vehicle_type}",
        })
