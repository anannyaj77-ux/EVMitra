"""
EVMitra – EV Comparison Module
Side-by-side comparison of exactly 2 EVs.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db_helper import execute_query


def get_all_ev_labels() -> list:
    """Get all 'Brand Model' labels from the database."""
    rows = execute_query("SELECT brand, model FROM ev_vehicles ORDER BY brand, model")
    return [f"{r['brand']} {r['model']}" for r in rows]


def get_ev_by_label(label: str) -> dict | None:
    """Fetch a single EV record by 'Brand Model' label."""
    parts = label.split(" ", 1)
    if len(parts) < 2:
        return None
    brand, model = parts[0], parts[1]
    rows = execute_query(
        "SELECT * FROM ev_vehicles WHERE brand = ? AND model = ?", (brand, model)
    )
    return rows[0] if rows else None


def highlight_better(val1, val2, higher_is_better: bool = True):
    """
    Return (style1, style2) CSS class names based on which value is better.
    Returns ('better', 'worse') or ('', '') if equal/unavailable.
    """
    if val1 is None or val2 is None:
        return "", ""
    try:
        v1, v2 = float(val1), float(val2)
        if v1 == v2:
            return "", ""
        if higher_is_better:
            return ("compare-better", "compare-worse") if v1 > v2 else ("compare-worse", "compare-better")
        else:
            return ("compare-better", "compare-worse") if v1 < v2 else ("compare-worse", "compare-better")
    except (TypeError, ValueError):
        return "", ""


def render_comparison_table(ev1: dict, ev2: dict):
    """Render the side-by-side comparison table."""
    params = [
        ("Price (₹)", "price_inr", False, lambda v: f"₹{v:,.0f}" if v else "N/A"),
        ("Battery (kWh)", "battery_kwh", True, lambda v: f"{v} kWh" if v else "N/A"),
        ("Range (km)", "range_km", True, lambda v: f"{v} km" if v else "N/A"),
        ("Motor Power (kW)", "motor_power_kw", True, lambda v: f"{v} kW" if v else "N/A"),
        ("Top Speed (km/h)", "top_speed_kmh", True, lambda v: f"{v} km/h" if v else "N/A"),
        ("Charge Time (hrs)", "charge_time_hrs", False, lambda v: f"{v}h" if v else "N/A"),
        ("Energy Use (Wh/km)", "wh_per_km", False, lambda v: f"{v} Wh/km" if v else "N/A"),
        ("Fast Charge", "fast_charge_supported", True, lambda v: "✅ Yes" if v else "❌ No"),
        ("Fast Charge Time (min)", "fast_charge_time_mins", False, lambda v: f"{v} min" if v else "N/A"),
        ("Seating", "seating_capacity", True, lambda v: f"{int(v)}" if v else "N/A"),
        ("Warranty (yrs)", "warranty_years", True, lambda v: f"{v} yrs" if v else "N/A"),
        ("Vehicle Type", "vehicle_type", None, lambda v: v if v else "N/A"),
    ]

    # Header
    h_col0, h_col1, h_col2 = st.columns([2, 3, 3])
    with h_col0:
        st.markdown("**Parameter**")
    with h_col1:
        st.markdown(f"**{ev1.get('brand','')} {ev1.get('model','')}**")
    with h_col2:
        st.markdown(f"**{ev2.get('brand','')} {ev2.get('model','')}**")
    st.divider()

    for label, key, higher_is_better, fmt in params:
        v1_raw = ev1.get(key)
        v2_raw = ev2.get(key)
        v1_str = fmt(v1_raw)
        v2_str = fmt(v2_raw)

        if higher_is_better is None:
            s1, s2 = "", ""
        else:
            s1, s2 = highlight_better(v1_raw, v2_raw, higher_is_better)

        prefix1 = "✅ " if s1 == "compare-better" else ("⚠️ " if s1 == "compare-worse" else "")
        prefix2 = "✅ " if s2 == "compare-better" else ("⚠️ " if s2 == "compare-worse" else "")

        c0, c1, c2 = st.columns([2, 3, 3])
        with c0:
            st.markdown(f"**{label}**")
        with c1:
            st.markdown(f"{prefix1}{v1_str}")
        with c2:
            st.markdown(f"{prefix2}{v2_str}")

    st.divider()

    # Features
    f1 = [f.strip() for f in (ev1.get("features") or "").split(",") if f.strip()]
    f2 = [f.strip() for f in (ev2.get("features") or "").split(",") if f.strip()]
    c0, c1, c2 = st.columns([2, 3, 3])
    with c0:
        st.markdown("**Features**")
    with c1:
        st.markdown("\n".join([f"• {f}" for f in f1]) if f1 else "N/A")
    with c2:
        st.markdown("\n".join([f"• {f}" for f in f2]) if f2 else "N/A")


def render_comparison_chart(ev1: dict, ev2: dict):
    """Render a bar chart comparing key numeric specs."""
    metrics = {
        "Battery (kWh)": ("battery_kwh", 1),
        "Range (km)": ("range_km", 1),
        "Motor (kW)": ("motor_power_kw", 1),
        "Top Speed (km/h)": ("top_speed_kmh", 1),
    }

    labels = list(metrics.keys())
    v1_vals = []
    v2_vals = []

    for label, (key, scale) in metrics.items():
        v1 = ev1.get(key) or 0
        v2 = ev2.get(key) or 0
        v1_vals.append(float(v1) * scale)
        v2_vals.append(float(v2) * scale)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=f"{ev1.get('brand','')} {ev1.get('model','')}",
        x=labels, y=v1_vals,
        marker_color="#00d4ff",
        text=[str(v) for v in v1_vals],
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        name=f"{ev2.get('brand','')} {ev2.get('model','')}",
        x=labels, y=v2_vals,
        marker_color="#7c3aed",
        text=[str(v) for v in v2_vals],
        textposition="outside"
    ))

    fig.update_layout(
        barmode="group",
        title="Specification Comparison",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


def render():
    """Render the EV Comparison page."""
    st.markdown('<h1 class="page-title">⚖️ Compare EVs</h1>', unsafe_allow_html=True)
    st.markdown("Select exactly **2 EVs** to compare side-by-side.")

    all_labels = get_all_ev_labels()
    if not all_labels:
        st.error("No EVs found in the database. Please initialize the database.")
        return

    # Pre-fill from explorer shortlist if available
    prefill = st.session_state.get("compare_list", [])

    col1, col2 = st.columns(2)
    with col1:
        default1 = prefill[0] if len(prefill) > 0 and prefill[0] in all_labels else all_labels[0]
        ev1_label = st.selectbox("🚗 First EV", all_labels, index=all_labels.index(default1), key="cmp_ev1")
    with col2:
        default2 = prefill[1] if len(prefill) > 1 and prefill[1] in all_labels else all_labels[min(1, len(all_labels)-1)]
        ev2_label = st.selectbox("🚗 Second EV", all_labels, index=all_labels.index(default2), key="cmp_ev2")

    if ev1_label == ev2_label:
        st.warning("⚠️ Please select two **different** EVs for comparison.")
        return

    ev1 = get_ev_by_label(ev1_label)
    ev2 = get_ev_by_label(ev2_label)

    if not ev1 or not ev2:
        st.error("Could not load EV data. Please try again.")
        return

    st.markdown("---")
    st.subheader("📊 Specification Comparison")
    st.caption("✅ = More favorable value | ⚠️ = Less favorable value (where objectively comparable)")

    render_comparison_table(ev1, ev2)
    render_comparison_chart(ev1, ev2)

    # Estimated running cost comparison
    st.markdown("---")
    st.subheader("💰 Estimated Monthly Running Cost")
    monthly_km = st.number_input("Enter estimated monthly distance (km)", min_value=100, max_value=10000, value=1500, step=100)
    tariff = st.number_input("Electricity tariff (₹/kWh)", min_value=1.0, max_value=20.0, value=8.0, step=0.5)

    if ev1.get("wh_per_km") and ev2.get("wh_per_km"):
        cost1 = monthly_km * ev1["wh_per_km"] / 1000 * tariff
        cost2 = monthly_km * ev2["wh_per_km"] / 1000 * tariff
        cc1, cc2 = st.columns(2)
        with cc1:
            st.metric(f"{ev1['brand']} {ev1['model']}", f"₹{cost1:,.0f}/month", help=f"{ev1['wh_per_km']} Wh/km")
        with cc2:
            diff = cost2 - cost1
            st.metric(f"{ev2['brand']} {ev2['model']}", f"₹{cost2:,.0f}/month",
                      delta=f"₹{abs(diff):,.0f} {'more' if diff > 0 else 'less'}/month",
                      delta_color="inverse" if diff > 0 else "normal")
    else:
        st.info("Energy consumption data not available for running cost comparison.")

    st.caption("*Estimated based on manufacturer Wh/km figure. Actual costs depend on driving conditions.*")
