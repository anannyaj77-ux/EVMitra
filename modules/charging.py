"""
EVMitra – Charging Stations Module
Discover EV charging stations by city with map links.

Note: Data is from EVMitra reference database, NOT live availability.
      Live availability is not claimed.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_helper import execute_query


def load_stations(city: str = None, charger_type: str = None) -> list[dict]:
    """Load charging stations with optional filters."""
    query = "SELECT * FROM charging_stations WHERE 1=1"
    params = []

    if city and city.strip() and city != "All Cities":
        query += " AND (city LIKE ? OR state LIKE ?)"
        params.extend([f"%{city}%", f"%{city}%"])
    if charger_type and charger_type != "All":
        query += " AND charger_types LIKE ?"
        params.append(f"%{charger_type}%")

    query += " ORDER BY city, station_name"
    return execute_query(query, params)


def render_station_card(station: dict):
    """Render a charging station card."""
    h24 = "🕐 24×7" if station.get("is_24x7") else "⏰ Check hours"
    chargers = station.get("charger_types", "").replace(",", " | ")
    power_str = f"{station.get('max_power_kw', 'N/A')} kW" if station.get("max_power_kw") else "N/A"
    connectors = station.get("num_connectors", "N/A")

    with st.container():
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"#### ⚡ {station.get('station_name', '')}")
            st.markdown(f"🏢 Operator: **{station.get('operator', 'N/A')}** | {h24}")
        with c2:
            if station.get("google_maps_url"):
                st.markdown(f"[🗺️ Open in Maps]({station['google_maps_url']})")

        sc1, sc2, sc3 = st.columns(3)
        sc1.markdown(f"**📍 Location:** {station.get('city', '')}, {station.get('state', '')}")
        sc2.markdown(f"**⚡ Max Power:** {power_str}")
        sc3.markdown(f"**🔌 Connectors:** {connectors}")

        st.markdown(f"**📟 Charger Types:** {chargers}")
        if station.get("address"):
            st.markdown(f"**📫 Address:** {station.get('address', '')}")
        if station.get("pricing_info"):
            st.markdown(f"**💰 Pricing:** {station.get('pricing_info', '')}")
        if station.get("phone"):
            st.markdown(f"**📞 Phone:** {station.get('phone', '')}")

        source = station.get('data_source', 'EVMitra Reference Database')
        updated = station.get('last_updated', 'N/A')
        st.caption(f"📌 Source: {source} | Last updated: {updated} | ⚠️ This is reference data, NOT live availability.")
        st.divider()


def render():
    """Render the Charging Stations page."""
    st.markdown('<h1 class="page-title">⚡ Charging Stations</h1>', unsafe_allow_html=True)
    st.markdown("Find EV charging stations near you or in any city.")

    st.warning("""
    ⚠️ **Data Notice:** Charging station data shown here is from EVMitra's reference database. 
    **Live availability is NOT shown** — please check the station operator's app or website for real-time availability.
    Station details may have changed. Always verify before visiting.
    """)

    # Charging alerts
    notifs = execute_query("SELECT * FROM notifications WHERE category = 'charging' AND is_active = 1")
    if notifs:
        for n in notifs:
            st.info(f"🔔 **{n['title']}** — {n['message']}")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        city_search = st.text_input("🔍 Search City or State",
                                     placeholder="e.g., Mumbai, Delhi, Bengaluru, Maharashtra...",
                                     key="charging_city")
    with col2:
        charger_type = st.selectbox("Charger Type",
                                     ["All", "CCS2", "CHAdeMO", "Type2", "AC", "DC Fast"],
                                     key="charging_type")
    with col3:
        only_24x7 = st.checkbox("24×7 Only", key="charging_24x7")

    # Load stations
    stations = load_stations(city_search.strip() if city_search else None, charger_type)

    if only_24x7:
        stations = [s for s in stations if s.get("is_24x7")]

    if not stations:
        st.warning(f"""
        🔍 No charging stations found for '{city_search or 'all cities'}' with selected filters.
        
        **Try:**
        - Searching a different city name
        - Removing the charger type filter
        - Using Google Maps directly: [Search EV charging stations near me](https://maps.google.com/?q=EV+charging+stations+near+me)
        """)
        return

    # Summary
    cities_found = sorted(set(s.get("city", "") for s in stations))
    st.success(f"**{len(stations)} station(s) found** across {len(cities_found)} city/cities: {', '.join(cities_found)}")

    # Quick stats
    q1, q2, q3 = st.columns(3)
    q1.metric("Total Stations", len(stations))
    q2.metric("Cities Covered", len(cities_found))
    q3.metric("24×7 Stations", sum(1 for s in stations if s.get("is_24x7")))

    st.markdown("---")

    # City overview chart
    city_counts = {}
    for s in stations:
        c = s.get("city", "Unknown")
        city_counts[c] = city_counts.get(c, 0) + 1

    if len(city_counts) > 1:
        fig = px.bar(
            x=list(city_counts.keys()),
            y=list(city_counts.values()),
            labels={"x": "City", "y": "Stations"},
            title="Stations by City",
            color_discrete_sequence=["#00d4ff"],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    for station in stations:
        render_station_card(station)

    # Google Maps fallback
    st.markdown("---")
    st.subheader("🗺️ Find More Stations")
    st.markdown("""
    For the most up-to-date charging station locations, use these resources:
    
    - [🗺️ Google Maps: EV Charging Stations](https://maps.google.com/?q=EV+charging+station)
    - [⚡ Tata Power EZ Charge Network](https://www.tatapowerezcharge.com/)
    - [🔌 Ather Grid Map](https://www.atherenergy.com/grid)
    - [⚡ Jio-bp EV Hubs](https://jiobp.com/ev/)
    - [🛢️ BPCL Pulse](https://bpclpulse.in/)
    - [🔋 CHARGE+ZONE](https://www.chargezone.co.in/)
    """)
