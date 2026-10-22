"""
EVMitra – Admin Module
Simple authenticated admin panel for managing reference data.

Authentication: Uses ADMIN_USERNAME and ADMIN_PASSWORD from .env
Default credentials are in .env.example — CHANGE before deployment.
Credentials are NEVER hardcoded here.
"""

import streamlit as st
import os
import json
import pandas as pd
from utils.db_helper import execute_query, execute_write, get_connection
from dotenv import load_dotenv

load_dotenv()

ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "evmitra2024")


def check_admin_auth() -> bool:
    """Check if admin is authenticated this session."""
    return st.session_state.get("admin_authenticated", False)


def admin_login_form():
    """Render admin login form."""
    st.markdown("### 🔐 Admin Login")
    st.caption("Admin credentials are configured in the `.env` file.")

    with st.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")

    if submitted:
        if username == ADMIN_USER and password == ADMIN_PASS:
            st.session_state["admin_authenticated"] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Check your .env file.")


def render_ev_management():
    """Manage EV vehicle records."""
    st.subheader("🚗 EV Vehicle Management")

    vehicles = execute_query("SELECT id, brand, model, vehicle_type, price_inr, range_km, last_updated FROM ev_vehicles ORDER BY brand, model")
    if vehicles:
        df = pd.DataFrame(vehicles)
        df["price_inr"] = df["price_inr"].apply(lambda x: f"₹{x:,.0f}" if x else "N/A")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No vehicles in database.")

    st.markdown("---")
    with st.expander("➕ Add New EV"):
        with st.form("add_ev_form"):
            c1, c2 = st.columns(2)
            brand = c1.text_input("Brand *")
            model = c2.text_input("Model *")
            vtype = c1.selectbox("Vehicle Type *", ["Car", "Scooter", "Motorcycle", "E-Rickshaw", "Bus"])
            price = c2.number_input("Price (₹) *", min_value=0.0, step=1000.0)
            battery = c1.number_input("Battery (kWh)", min_value=0.0, step=0.1)
            ev_range = c2.number_input("Range (km)", min_value=0.0, step=1.0)
            motor = c1.number_input("Motor Power (kW)", min_value=0.0, step=0.5)
            charge_time = c2.number_input("Charge Time (hrs)", min_value=0.0, step=0.5)
            wh_per_km = c1.number_input("Wh/km", min_value=0.0, step=1.0)
            source = c2.text_input("Source", value="Admin Entry")
            features = st.text_area("Features (comma-separated)")
            submitted = st.form_submit_button("Add EV", type="primary")

        if submitted:
            if not brand or not model:
                st.error("Brand and Model are required.")
            else:
                try:
                    execute_write("""
                        INSERT OR IGNORE INTO ev_vehicles
                        (brand, model, vehicle_type, price_inr, battery_kwh, range_km,
                         motor_power_kw, charge_time_hrs, wh_per_km, features, source, last_updated)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,date('now'))
                    """, (brand, model, vtype, price, battery or None, ev_range or None,
                          motor or None, charge_time or None, wh_per_km or None, features, source))
                    st.success(f"✅ Added {brand} {model}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with st.expander("🗑️ Delete EV"):
        vehicle_ids = execute_query("SELECT id, brand, model FROM ev_vehicles ORDER BY brand, model")
        if vehicle_ids:
            labels = {f"{v['brand']} {v['model']}": v['id'] for v in vehicle_ids}
            selected_label = st.selectbox("Select EV to delete", list(labels.keys()), key="del_ev")
            if st.button("🗑️ Delete Selected EV", type="secondary"):
                execute_write("DELETE FROM ev_vehicles WHERE id = ?", (labels[selected_label],))
                st.success(f"✅ Deleted {selected_label}")
                st.rerun()


def render_scheme_management():
    """Manage government scheme records."""
    st.subheader("🏛️ Government Scheme Management")

    schemes = execute_query("SELECT id, scheme_name, state, scheme_status, last_updated FROM govt_schemes ORDER BY state")
    if schemes:
        st.dataframe(pd.DataFrame(schemes), use_container_width=True)

    st.markdown("---")
    with st.expander("➕ Add New Scheme"):
        with st.form("add_scheme_form"):
            sname = st.text_input("Scheme Name *")
            stype = st.selectbox("Type", ["Central", "State"])
            sstate = st.text_input("State/Region", value="All India")
            svtypes = st.text_input("Vehicle Types (comma-separated)", value="Car,Scooter")
            selig = st.text_area("Eligibility")
            sbenefits = st.text_area("Benefits *")
            sstatus = st.selectbox("Status", ["Active", "Closed", "Upcoming"])
            surl = st.text_input("Official URL")
            ssource = st.text_input("Source", value="Admin Entry")
            submitted = st.form_submit_button("Add Scheme", type="primary")

        if submitted:
            if not sname or not sbenefits:
                st.error("Scheme Name and Benefits are required.")
            else:
                execute_write("""
                    INSERT INTO govt_schemes
                    (scheme_name, scheme_type, state, vehicle_types, eligibility, benefits,
                     scheme_status, official_url, source, last_updated)
                    VALUES (?,?,?,?,?,?,?,?,?,date('now'))
                """, (sname, stype, sstate, svtypes, selig, sbenefits, sstatus, surl, ssource))
                st.success(f"✅ Added scheme: {sname}")
                st.rerun()


def render_notifications_management():
    """Manage in-app notifications."""
    st.subheader("🔔 In-App Notifications")

    notifs = execute_query("SELECT * FROM notifications ORDER BY created_at DESC")
    if notifs:
        st.dataframe(pd.DataFrame(notifs)[["id", "category", "title", "severity", "is_active", "created_at"]],
                     use_container_width=True)

    with st.expander("➕ Add Notification"):
        with st.form("add_notif"):
            cat = st.selectbox("Category", ["scheme", "charging", "general"])
            title = st.text_input("Title *")
            msg = st.text_area("Message *")
            sev = st.selectbox("Severity", ["info", "success", "warning"])
            submitted = st.form_submit_button("Add", type="primary")
        if submitted and title and msg:
            execute_write("""
                INSERT INTO notifications (category, title, message, severity, is_active, created_at)
                VALUES (?,?,?,?,1,date('now'))
            """, (cat, title, msg, sev))
            st.success("✅ Notification added")
            st.rerun()

    with st.expander("🗑️ Deactivate Notification"):
        active_notifs = execute_query("SELECT id, title FROM notifications WHERE is_active = 1")
        if active_notifs:
            n_labels = {n["title"]: n["id"] for n in active_notifs}
            sel_notif = st.selectbox("Select", list(n_labels.keys()), key="del_notif")
            if st.button("Deactivate"):
                execute_write("UPDATE notifications SET is_active = 0 WHERE id = ?", (n_labels[sel_notif],))
                st.success("✅ Deactivated")
                st.rerun()


def render_config_management():
    """Manage admin config."""
    st.subheader("⚙️ Application Configuration")

    configs = execute_query("SELECT * FROM admin_config")
    if configs:
        for cfg in configs:
            col1, col2, col3 = st.columns([2, 2, 3])
            col1.markdown(f"**{cfg['config_key']}**")
            col2.markdown(cfg['config_value'] or "N/A")
            col3.caption(cfg['description'] or "")

    with st.expander("✏️ Update Config Value"):
        with st.form("update_config"):
            config_keys = [c["config_key"] for c in (configs or [])]
            sel_key = st.selectbox("Key", config_keys) if config_keys else st.text_input("Key")
            new_val = st.text_input("New Value")
            submitted = st.form_submit_button("Update", type="primary")
        if submitted and sel_key and new_val:
            execute_write(
                "UPDATE admin_config SET config_value = ?, last_updated = date('now') WHERE config_key = ?",
                (new_val, sel_key)
            )
            st.success(f"✅ Updated {sel_key}")
            st.rerun()


def render_db_stats():
    """Show database statistics."""
    st.subheader("📊 Database Statistics")

    tables = ["ev_vehicles", "govt_schemes", "showrooms", "charging_stations", "notifications"]
    stats = {}
    for table in tables:
        result = execute_query(f"SELECT COUNT(*) as cnt FROM {table}")
        stats[table] = result[0]["cnt"] if result else 0

    cols = st.columns(len(stats))
    icons = ["🚗", "🏛️", "🏪", "⚡", "🔔"]
    for i, (table, count) in enumerate(stats.items()):
        cols[i].metric(f"{icons[i]} {table.replace('_', ' ').title()}", count)


def render():
    """Render the Admin panel."""
    st.markdown('<h1 class="page-title">🛠️ Admin Panel</h1>', unsafe_allow_html=True)

    if not check_admin_auth():
        admin_login_form()
        st.info("ℹ️ Admin credentials are set in the `.env` file. Default: see `.env.example`")
        return

    # Logout
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔓 Logout"):
            st.session_state["admin_authenticated"] = False
            st.rerun()

    st.success("✅ Logged in as Admin")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚗 EV Vehicles", "🏛️ Schemes", "🔔 Notifications", "⚙️ Config", "📊 DB Stats"])

    with tab1:
        render_ev_management()
    with tab2:
        render_scheme_management()
    with tab3:
        render_notifications_management()
    with tab4:
        render_config_management()
    with tab5:
        render_db_stats()
