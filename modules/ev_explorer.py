"""
EVMitra – EV Explorer Module
Browse, search, filter and sort EV listings.
"""

import streamlit as st
import pandas as pd
from utils.db_helper import execute_query


def load_vehicles(filters: dict = None) -> pd.DataFrame:
    """Load vehicles from database, applying optional filters."""
    query = "SELECT * FROM ev_vehicles WHERE 1=1"
    params = []

    if filters:
        if filters.get("brand") and filters["brand"] != "All":
            query += " AND brand = ?"
            params.append(filters["brand"])
        if filters.get("vehicle_type") and filters["vehicle_type"] != "All":
            query += " AND vehicle_type = ?"
            params.append(filters["vehicle_type"])
        if filters.get("min_price") is not None:
            query += " AND price_inr >= ?"
            params.append(filters["min_price"])
        if filters.get("max_price") is not None:
            query += " AND price_inr <= ?"
            params.append(filters["max_price"])
        if filters.get("min_range") is not None:
            query += " AND (range_km >= ? OR range_km IS NULL)"
            params.append(filters["min_range"])
        if filters.get("max_range") is not None:
            query += " AND (range_km <= ? OR range_km IS NULL)"
            params.append(filters["max_range"])
        if filters.get("min_battery") is not None:
            query += " AND (battery_kwh >= ? OR battery_kwh IS NULL)"
            params.append(filters["min_battery"])
        if filters.get("fast_charge_only"):
            query += " AND fast_charge_supported = 1"
        if filters.get("search_term"):
            query += " AND (brand LIKE ? OR model LIKE ? OR features LIKE ?)"
            term = f"%{filters['search_term']}%"
            params.extend([term, term, term])

    rows = execute_query(query, params)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_ev_card(ev: dict, idx: int):
    """Render a single EV as an information card."""
    fast_badge = "⚡ Fast Charge" if ev.get("fast_charge_supported") else ""
    price_str = f"₹{ev['price_inr']:,.0f}" if ev.get("price_inr") else "N/A"
    range_str = f"{ev['range_km']} km" if ev.get("range_km") else "N/A"
    battery_str = f"{ev['battery_kwh']} kWh" if ev.get("battery_kwh") else "N/A"
    motor_str = f"{ev['motor_power_kw']} kW" if ev.get("motor_power_kw") else "N/A"
    speed_str = f"{ev['top_speed_kmh']} km/h" if ev.get("top_speed_kmh") else "N/A"
    charge_str = f"{ev['charge_time_hrs']}h" if ev.get("charge_time_hrs") else "N/A"
    wh_str = f"{ev['wh_per_km']} Wh/km" if ev.get("wh_per_km") else "N/A"

    features = ev.get("features", "") or ""
    feature_list = [f.strip() for f in features.split(",") if f.strip()][:5]
    feature_chips = " ".join([f"`{f}`" for f in feature_list])

    with st.container():
        feature_chips_html = ""
        if feature_list:
            chips = "".join(
                f'<span style="background:rgba(0,212,255,0.1);color:#00d4ff;border:1px solid #00d4ff;'
                f'border-radius:12px;padding:2px 10px;font-size:0.72rem;font-weight:600;'
                f'margin-right:4px;white-space:nowrap;">{f}</span>'
                for f in feature_list
            )
            feature_chips_html = f'<div style="margin-top:0.6rem;display:flex;flex-wrap:wrap;gap:4px;">{chips}</div>'

        source_text = ev.get('source', 'EVMitra Database')
        updated_text = ev.get('last_updated', 'N/A')

        st.markdown(f"""
<div class="ev-card">
    <div class="ev-card-header">
        <span class="ev-badge">{ev.get('vehicle_type', '')}</span>
        {f'<span class="ev-badge-fast">{fast_badge}</span>' if fast_badge else ''}
    </div>
    <h3 class="ev-title">{ev.get('brand', '')} {ev.get('model', '')}</h3>
    <div class="ev-price">{price_str}</div>
    <div class="ev-specs-grid">
        <div class="ev-spec"><span class="spec-label">🔋 Battery</span><span class="spec-value">{battery_str}</span></div>
        <div class="ev-spec"><span class="spec-label">🛣️ Range</span><span class="spec-value">{range_str}</span></div>
        <div class="ev-spec"><span class="spec-label">⚡ Motor</span><span class="spec-value">{motor_str}</span></div>
        <div class="ev-spec"><span class="spec-label">🏎️ Top Speed</span><span class="spec-value">{speed_str}</span></div>
        <div class="ev-spec"><span class="spec-label">🔌 Charge Time</span><span class="spec-value">{charge_str}</span></div>
        <div class="ev-spec"><span class="spec-label">💡 Efficiency</span><span class="spec-value">{wh_str}</span></div>
    </div>
    {feature_chips_html}
    <div style="margin-top:0.6rem;font-size:0.72rem;color:#64748b;">
        📌 Source: {source_text} | Last updated: {updated_text}
    </div>
</div>
""", unsafe_allow_html=True)
        st.divider()


def render():
    """Render the EV Explorer page."""
    st.markdown('<h1 class="page-title">🔍 EV Explorer</h1>', unsafe_allow_html=True)
    st.markdown("Browse and discover electric vehicles available in India. Use filters to narrow your search.")

    # --- Sidebar Filters ---
    with st.sidebar:
        st.markdown("### 🎛️ Filters")

        # Load all for filter options
        all_rows = execute_query("SELECT DISTINCT brand, vehicle_type FROM ev_vehicles ORDER BY brand")
        all_df = pd.DataFrame(all_rows) if all_rows else pd.DataFrame(columns=["brand", "vehicle_type"])

        brands = ["All"] + sorted(all_df["brand"].unique().tolist()) if not all_df.empty else ["All"]
        types = ["All"] + sorted(all_df["vehicle_type"].unique().tolist()) if not all_df.empty else ["All"]

        search_term = st.text_input("🔎 Search", placeholder="Brand, model, feature...")
        selected_brand = st.selectbox("Brand", brands, key="explorer_brand")
        selected_type = st.selectbox("Vehicle Type", types, key="explorer_type")

        st.markdown("**Price Range (₹ Lakhs)**")
        price_range = st.slider("Price (₹ Lakhs)", 0.0, 80.0, (0.0, 80.0), 0.5, key="explorer_price")

        st.markdown("**Range (km)**")
        range_slider = st.slider("Range (km)", 0, 800, (0, 800), 10, key="explorer_range")

        st.markdown("**Battery Capacity (kWh)**")
        battery_min = st.slider("Min Battery (kWh)", 0.0, 100.0, 0.0, 0.5, key="explorer_battery")

        fast_only = st.checkbox("⚡ Fast Charge Only", key="explorer_fast")

        st.markdown("**Sort By**")
        sort_col = st.selectbox("Sort by", ["price_inr", "range_km", "battery_kwh", "motor_power_kw"], key="explorer_sort")
        sort_asc = st.radio("Order", ["Ascending ↑", "Descending ↓"], key="explorer_sort_dir") == "Ascending ↑"

    filters = {
        "brand": selected_brand,
        "vehicle_type": selected_type,
        "min_price": price_range[0] * 100000,
        "max_price": price_range[1] * 100000,
        "min_range": range_slider[0],
        "max_range": range_slider[1],
        "min_battery": battery_min,
        "fast_charge_only": fast_only,
        "search_term": search_term.strip() if search_term else None,
    }

    df = load_vehicles(filters)

    if df.empty:
        st.warning("🔎 No EVs matched your filters. Try adjusting the filters.")
        return

    # Sort
    if sort_col in df.columns:
        df = df.sort_values(by=sort_col, ascending=sort_asc, na_position="last")

    st.markdown(f"**{len(df)} EV(s) found**")

    # Comparison shortlist
    if "compare_list" not in st.session_state:
        st.session_state.compare_list = []

    st.markdown("---")

    # Display as cards in columns
    for i in range(0, len(df), 2):
        col1, col2 = st.columns(2)
        with col1:
            row = df.iloc[i].to_dict()
            render_ev_card(row, i)
            ev_label = f"{row['brand']} {row['model']}"
            if st.button(f"➕ Add to Compare", key=f"cmp_{i}"):
                if ev_label not in st.session_state.compare_list:
                    if len(st.session_state.compare_list) >= 2:
                        st.session_state.compare_list.pop(0)
                    st.session_state.compare_list.append(ev_label)
                    st.success(f"Added {ev_label} to comparison.")
                else:
                    st.info(f"{ev_label} is already in comparison.")

        if i + 1 < len(df):
            with col2:
                row = df.iloc[i + 1].to_dict()
                render_ev_card(row, i + 1)
                ev_label = f"{row['brand']} {row['model']}"
                if st.button(f"➕ Add to Compare", key=f"cmp_{i+1}"):
                    if ev_label not in st.session_state.compare_list:
                        if len(st.session_state.compare_list) >= 2:
                            st.session_state.compare_list.pop(0)
                        st.session_state.compare_list.append(ev_label)
                        st.success(f"Added {ev_label} to comparison.")
                    else:
                        st.info(f"{ev_label} is already in comparison.")

    if st.session_state.compare_list:
        st.info(f"**Comparison Shortlist:** {', '.join(st.session_state.compare_list)}\n\nGo to **Compare EVs** in the sidebar to see the full comparison.")
