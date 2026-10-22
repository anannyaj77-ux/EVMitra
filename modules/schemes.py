"""
EVMitra – Government Schemes Module
Displays EV-related government subsidies and schemes with filters.
"""

import streamlit as st
import pandas as pd
from utils.db_helper import execute_query


def load_schemes(filters: dict = None) -> list[dict]:
    """Load schemes from database with optional filters."""
    query = "SELECT * FROM govt_schemes WHERE 1=1"
    params = []

    if filters:
        if filters.get("state") and filters["state"] != "All":
            if filters["state"] == "Central (All India)":
                query += " AND (state = 'All India' OR scheme_type = 'Central')"
            else:
                query += " AND (state = ? OR state = 'All India')"
                params.append(filters["state"])
        if filters.get("vehicle_type") and filters["vehicle_type"] != "All":
            query += " AND vehicle_types LIKE ?"
            params.append(f"%{filters['vehicle_type']}%")
        if filters.get("status") and filters["status"] != "All":
            query += " AND scheme_status LIKE ?"
            params.append(f"%{filters['status']}%")

    query += " ORDER BY scheme_type, state"
    return execute_query(query, params)


def render_scheme_card(scheme: dict):
    """Render a government scheme card."""
    status = scheme.get("scheme_status", "Unknown")
    status_color = "#10b981" if "Active" in status else "#f59e0b" if "Closed" in status else "#6b7280"
    status_icon = "✅" if "Active" in status else "⚠️" if "Closed" in status else "ℹ️"

    subsidy_text = ""
    if scheme.get("subsidy_amount"):
        subsidy_text = f"₹{scheme['subsidy_amount']:,.0f}/kWh"
    if scheme.get("max_subsidy"):
        subsidy_text += f" (max ₹{scheme['max_subsidy']:,.0f})"

    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {scheme.get('scheme_name','')}")
        with col2:
            st.markdown(f"**{status_icon} {status}**")

        mc1, mc2, mc3 = st.columns(3)
        mc1.markdown(f"**Type:** {scheme.get('scheme_type','')}")
        mc2.markdown(f"**Region:** {scheme.get('state','')}")
        mc3.markdown(f"**Vehicles:** {scheme.get('vehicle_types','').replace(',', ', ')}")

        st.markdown(f"**📋 Benefits:**\n{scheme.get('benefits','')}")

        if scheme.get("eligibility"):
            st.markdown(f"**👤 Eligibility:** {scheme.get('eligibility','')}")

        if subsidy_text:
            st.markdown(f"**💰 Subsidy:** {subsidy_text}")

        validity = ""
        if scheme.get("valid_from"):
            validity += f"From: {scheme['valid_from']}"
        if scheme.get("valid_until"):
            validity += f" | Until: {scheme['valid_until']}"
        if validity:
            st.markdown(f"**📅 Validity:** {validity}")

        if scheme.get("official_url"):
            st.markdown(f"🔗 [Official Source]({scheme['official_url']})")

        source_text = scheme.get('source', 'EVMitra Reference Data')
        updated_text = scheme.get('last_updated', 'N/A')
        st.caption(f"📌 Source: {source_text} | Last updated: {updated_text}")
        st.divider()


def render():
    """Render the Government Schemes page."""
    st.markdown('<h1 class="page-title">🏛️ Government EV Schemes</h1>', unsafe_allow_html=True)
    st.markdown("Explore central and state government subsidies, incentives and policies for electric vehicles in India.")

    st.info("""
    ⚠️ **Disclaimer:** Scheme details are based on publicly available official sources. 
    Schemes may change or expire. Always verify current status on the **official government website** 
    before making a purchase decision. Source and last-updated date are shown for each scheme.
    """)

    # Notifications
    notifs = execute_query("SELECT * FROM notifications WHERE category = 'scheme' AND is_active = 1 ORDER BY created_at DESC")
    if notifs:
        st.markdown("### 🔔 Scheme Alerts")
        for n in notifs:
            if n["severity"] == "success":
                st.success(f"**{n['title']}** — {n['message']}")
            elif n["severity"] == "warning":
                st.warning(f"**{n['title']}** — {n['message']}")
            else:
                st.info(f"**{n['title']}** — {n['message']}")
        st.markdown("---")

    # Filters
    with st.sidebar:
        st.markdown("### 🎛️ Scheme Filters")
        states = ["All", "Central (All India)", "Maharashtra", "Delhi", "Gujarat",
                  "Karnataka", "Tamil Nadu", "Telangana", "Rajasthan"]
        sel_state = st.selectbox("State / Region", states, key="scheme_state")
        sel_type = st.selectbox("Vehicle Type", ["All", "Car", "Scooter", "Motorcycle", "Bus", "E-Rickshaw"],
                                 key="scheme_vtype")
        sel_status = st.selectbox("Status", ["All", "Active", "Closed"], key="scheme_status")

    filters = {"state": sel_state, "vehicle_type": sel_type, "status": sel_status}
    schemes = load_schemes(filters)

    if not schemes:
        st.warning("No schemes found matching your filters. Try adjusting the filters.")
        return

    st.markdown(f"**{len(schemes)} scheme(s) found**")
    st.markdown("---")

    for scheme in schemes:
        render_scheme_card(scheme)
