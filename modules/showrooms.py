"""
EVMitra – Showrooms Module
Discover EV brand showrooms across India.
"""

import streamlit as st
import pandas as pd
from utils.db_helper import execute_query


def load_showrooms(city: str = None, brand: str = None) -> list[dict]:
    """Load showrooms with optional filters."""
    query = "SELECT * FROM showrooms WHERE 1=1"
    params = []

    if city and city.strip() and city != "All Cities":
        query += " AND (city LIKE ? OR state LIKE ?)"
        params.extend([f"%{city}%", f"%{city}%"])
    if brand and brand != "All":
        query += " AND brand = ?"
        params.append(brand)

    query += " ORDER BY city, brand"
    return execute_query(query, params)


def render_showroom_card(showroom: dict):
    """Render a showroom card."""
    with st.container():
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"#### 🏪 {showroom.get('showroom_name', '')}")
            st.markdown(f"**Brand:** {showroom.get('brand', '')} | **City:** {showroom.get('city', '')}, {showroom.get('state', '')}")
        with c2:
            if showroom.get("google_maps_url"):
                st.markdown(f"[🗺️ Get Directions]({showroom['google_maps_url']})")

        if showroom.get("address"):
            st.markdown(f"📫 {showroom.get('address', '')}")

        info_cols = st.columns(3)
        if showroom.get("phone"):
            info_cols[0].markdown(f"📞 {showroom.get('phone', '')}")
        if showroom.get("working_hours"):
            info_cols[1].markdown(f"🕐 {showroom.get('working_hours', '')}")
        if showroom.get("email"):
            info_cols[2].markdown(f"✉️ {showroom.get('email', '')}")

        source = showroom.get('source', 'EVMitra Reference Database')
        updated = showroom.get('last_updated', 'N/A')
        st.caption(f"📌 Source: {source} | Last updated: {updated}")
        st.divider()


def render():
    """Render the Showrooms page."""
    st.markdown('<h1 class="page-title">🏪 EV Showrooms</h1>', unsafe_allow_html=True)
    st.markdown("Find EV brand showrooms and experience centers across India.")

    st.info("📌 Showroom details are from EVMitra's reference database. Please confirm working hours and availability directly with the showroom before visiting.")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        city_search = st.text_input("🔍 Search City or State",
                                     placeholder="e.g., Mumbai, Delhi, Bengaluru, Pune...",
                                     key="showroom_city")
    with col2:
        all_brands = ["All"] + sorted(set(
            r["brand"] for r in execute_query("SELECT DISTINCT brand FROM showrooms ORDER BY brand")
        ))
        sel_brand = st.selectbox("Brand", all_brands, key="showroom_brand")

    showrooms = load_showrooms(city_search.strip() if city_search else None, sel_brand)

    if not showrooms:
        st.warning(f"""
        🔍 No showrooms found for '{city_search or 'all cities'}'{' - ' + sel_brand if sel_brand != 'All' else ''}.
        
        **Try:**
        - Searching a different city
        - Changing brand to 'All'
        - [Search on Google Maps](https://maps.google.com/?q=EV+showroom+near+me)
        """)
        return

    cities_found = sorted(set(s.get("city", "") for s in showrooms))
    st.success(f"**{len(showrooms)} showroom(s) found** in: {', '.join(cities_found)}")

    q1, q2 = st.columns(2)
    q1.metric("Total Showrooms", len(showrooms))
    q2.metric("Cities Covered", len(cities_found))

    st.markdown("---")
    for showroom in showrooms:
        render_showroom_card(showroom)

    # External links
    st.markdown("---")
    st.subheader("🔗 Find More Showrooms")
    st.markdown("""
    Use these official brand locator tools for the most up-to-date showroom lists:
    
    - [🚗 Tata Motors Dealer Locator](https://www.tatamotors.com/dealerlocator/)
    - [🚗 MG Motor Dealer Locator](https://www.mgmotor.co.in/locate-a-dealer)
    - [🛵 Ola Electric Experience Centers](https://www.olaelectric.com/test-drive)
    - [🛵 Ather Experience Centers](https://www.atherenergy.com/experience-centre)
    - [🚗 Hyundai Dealer Locator](https://www.hyundai.com/in/en/find-a-dealer.html)
    - [🚗 Mahindra Dealer Locator](https://auto.mahindra.com/locate/dealer)
    """)
