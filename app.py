"""
EVMitra – Smart Electric Vehicle Platform
==========================================
Main Streamlit application entry point.

Run with: streamlit run app.py

Author: MCA Semester 3 Mini Project
"""

import streamlit as st
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="EVMitra – Smart EV Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "EVMitra – MCA Semester 3 Mini Project | Smart Electric Vehicle Platform",
    }
)

# ── Initialize database if not present ──────────────────────────────────────
DB_PATH = os.path.join("database", "evmitra.db")
if not os.path.exists(DB_PATH):
    try:
        from database.init_db import init_database
        init_database()
    except Exception as e:
        st.error(f"Database initialization failed: {e}. Please run `python database/init_db.py` manually.")

# ── CSS Styling ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@400;700;900&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #1a2035;
    --bg-card-hover: #1e2a42;
    --accent-cyan: #00d4ff;
    --accent-purple: #7c3aed;
    --accent-green: #10b981;
    --accent-amber: #f59e0b;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border-color: #1e3a5f;
    --gradient-main: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0d1929 100%);
}

/* ── Global Reset ── */
html, body, [data-testid="stApp"] {
    background: var(--gradient-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stMain"] {
    background: transparent !important;
}
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1929 0%, #111827 100%) !important;
    border-right: 1px solid var(--border-color) !important;
}
/* ── Page Title ── */
.page-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem !important;
}
/* ── EV Card ── */
.ev-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 24px rgba(0, 212, 255, 0.05);
}
.ev-card:hover {
    border-color: var(--accent-cyan);
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.12);
    transform: translateY(-2px);
}
.ev-card-header { display:flex; gap:0.5rem; margin-bottom:0.5rem; }
.ev-badge {
    background:rgba(0,212,255,0.1); color:var(--accent-cyan);
    border:1px solid var(--accent-cyan); border-radius:20px;
    padding:2px 10px; font-size:0.75rem; font-weight:600;
}
.ev-badge-fast {
    background:rgba(245,158,11,0.1); color:var(--accent-amber);
    border:1px solid var(--accent-amber); border-radius:20px;
    padding:2px 10px; font-size:0.75rem; font-weight:600;
}
.ev-title {
    font-family:'Orbitron',monospace !important;
    font-size:1.2rem !important; font-weight:700 !important;
    color:var(--text-primary) !important; margin:0.3rem 0 !important;
}
.ev-price { font-size:1.5rem; font-weight:700; color:var(--accent-cyan); margin-bottom:0.8rem; }
.ev-specs-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:0.5rem; }
.ev-spec { display:flex; flex-direction:column; }
.spec-label { font-size:0.72rem; color:var(--text-muted); font-weight:500; }
.spec-value { font-size:0.9rem; color:var(--text-primary); font-weight:600; }
/* ── Recommendation Card ── */
.rec-card {
    background:linear-gradient(135deg,var(--bg-card) 0%,#0d1929 100%);
    border:1px solid var(--border-color); border-radius:16px;
    padding:1.2rem 1.4rem; margin-bottom:0.8rem;
    border-left:4px solid var(--accent-cyan);
}
.rec-rank { font-size:0.85rem; color:var(--accent-amber); font-weight:600; margin-bottom:0.3rem; }
/* ── Streamlit overrides ── */
.stButton>button {
    background:linear-gradient(90deg,var(--accent-cyan),var(--accent-purple)) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important; font-family:'Inter',sans-serif !important;
    padding:0.5rem 1.5rem !important; transition:all 0.3s ease !important;
}
.stButton>button:hover {
    opacity:0.9 !important; transform:translateY(-1px) !important;
    box-shadow:0 4px 20px rgba(0,212,255,0.3) !important;
}
.stButton>button[kind="secondary"] {
    background:var(--bg-card) !important;
    border:1px solid var(--border-color) !important;
    color:var(--text-secondary) !important;
}
[data-testid="stMetricValue"] { font-family:'Orbitron',monospace !important; color:var(--accent-cyan) !important; }
[data-testid="stMetricLabel"] { color:var(--text-secondary) !important; font-size:0.85rem !important; }
.stSelectbox>div>div { background:var(--bg-card) !important; border-color:var(--border-color) !important; color:var(--text-primary) !important; }
.stTextInput>div>div>input { background:var(--bg-card) !important; border-color:var(--border-color) !important; color:var(--text-primary) !important; }
.stNumberInput>div>div>input { background:var(--bg-card) !important; border-color:var(--border-color) !important; color:var(--text-primary) !important; }
div[data-testid="stExpander"] { background:var(--bg-card) !important; border:1px solid var(--border-color) !important; border-radius:10px !important; }
.stTabs [data-baseweb="tab-list"] { background:var(--bg-card) !important; border-radius:10px !important; }
.stTabs [data-baseweb="tab"] { color:var(--text-secondary) !important; }
.stTabs [aria-selected="true"] { color:var(--accent-cyan) !important; }
hr { border-color:var(--border-color) !important; }
</style>
""", unsafe_allow_html=True)


# ── Navigation ───────────────────────────────────────────────────────────────
PAGES = {
    "🏠 Home": "home",
    "🔍 EV Explorer": "explorer",
    "🎯 Find My EV": "find",
    "⚖️ Compare EVs": "compare",
    "📊 Owner Analytics": "analytics",
    "💰 Cost Calculator": "calculator",
    "🌱 Environmental Impact": "environment",
    "🏛️ Government Schemes": "schemes",
    "⚡ Charging Stations": "charging",
    "🏪 Showrooms": "showrooms",
    "🤖 ML Insights": "ml",
    "📜 History": "history",
    "🛠️ Admin": "admin",
}

# ── Session state init ───────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "history" not in st.session_state:
    st.session_state.history = []
if "compare_list" not in st.session_state:
    st.session_state.compare_list = []

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 1.5rem;">
        <div style="font-family:'Orbitron',monospace; font-size:1.6rem; font-weight:900;
                    background:linear-gradient(90deg,#00d4ff,#7c3aed);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            ⚡ EVMitra
        </div>
        <div style="color:#64748b; font-size:0.75rem; margin-top:4px;">
            Smart Electric Vehicle Platform
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    for label, page_key in PAGES.items():
        btn_type = "primary" if st.session_state.page == page_key else "secondary"
        if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
            st.session_state.page = page_key
            st.rerun()
    st.markdown("---")
    st.caption("EVMitra v1.0 | MCA Mini Project")
    st.caption("⚡ Reference data | Not financial advice")


# ── HOME PAGE ─────────────────────────────────────────────────────────────────
def render_home():
    """Render the EVMitra landing page."""
    import plotly.express as px
    import pandas as pd

    # Hero
    st.markdown("""
    <div style="text-align:center; padding:3rem 1rem 2rem;">
        <div style="font-family:'Orbitron',monospace; font-size:3.5rem; font-weight:900;
                    background:linear-gradient(90deg,#00d4ff,#7c3aed,#10b981);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    line-height:1.1; margin-bottom:1rem;">
            ⚡ EVMitra
        </div>
        <div style="font-size:1.3rem; color:#94a3b8; margin-bottom:1rem; font-weight:300;">
            Your Smart Electric Vehicle Companion
        </div>
        <div style="font-size:1rem; color:#64748b; max-width:700px; margin:0 auto 2rem;">
            Explore EVs → Find your EV → Compare → Analyze → Calculate savings → Environmental impact
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
    with c2:
        if st.button("🔍 Explore EVs", type="primary", use_container_width=True, key="home_explore"):
            st.session_state.page = "explorer"; st.rerun()
    with c3:
        if st.button("🎯 Find My EV", type="primary", use_container_width=True, key="home_find"):
            st.session_state.page = "find"; st.rerun()
    with c4:
        if st.button("💰 Cost Calc", type="primary", use_container_width=True, key="home_calc"):
            st.session_state.page = "calculator"; st.rerun()

    st.markdown("---")

    # ── VIDEO SECTION ──────────────────────────────────────────────────────────
    st.markdown('<h2 style="font-family:Orbitron,monospace; color:#00d4ff;">🎬 Electric Vehicle Showcase</h2>',
                unsafe_allow_html=True)

    video_path = os.path.join("assets", "ev_showcase.mp4")
    if os.path.exists(video_path):
        st.video(video_path)
        st.caption("▶️ EV Showcase — local file")
    else:
        # ── Working YouTube embed in a 16:9 responsive container ──────────────
        # Video: "Electric Vehicles Explained" – a stable, embeddable EV overview
        _YT_VIDEO_ID = "nFhTTJDCOM4"  # DW Planet A – "Are electric cars really better?" (embeddable)
        _YT_EMBED_URL = (
            f"https://www.youtube.com/embed/{_YT_VIDEO_ID}"
            "?autoplay=0&mute=0&controls=1&rel=0&modestbranding=1"
        )
        _YT_WATCH_URL = f"https://www.youtube.com/watch?v={_YT_VIDEO_ID}"

        # Responsive 16:9 wrapper using the padding-top trick; max-width keeps it
        # from spanning the full ultra-wide layout column.
        st.markdown(f"""
<div style="max-width:860px; margin:0 auto 1rem;">
    <div style="position:relative; padding-top:56.25%; border-radius:16px;
                overflow:hidden; border:1px solid #1e3a5f;
                box-shadow:0 8px 32px rgba(0,212,255,0.10);">
        <iframe
            id="ev-showcase-iframe"
            src="{_YT_EMBED_URL}"
            title="Electric Vehicle Showcase"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            style="position:absolute; top:0; left:0; width:100%; height:100%; border:0; border-radius:16px;"
            onerror="document.getElementById('ev-showcase-fallback').style.display='flex';
                     this.style.display='none';">
        </iframe>
        <!-- Fallback overlay shown if the iframe errors or is blocked -->
        <div id="ev-showcase-fallback"
             style="display:none; position:absolute; top:0; left:0; width:100%; height:100%;
                    background:linear-gradient(135deg,#0a0e1a 0%,#111827 100%);
                    flex-direction:column; align-items:center; justify-content:center;
                    border-radius:16px; gap:1rem;">
            <div style="font-size:3rem;">🔌</div>
            <div style="color:#94a3b8; font-size:1rem; font-family:Inter,sans-serif; text-align:center; padding:0 2rem;">
                Video unavailable in this environment.<br>
                <a href="{_YT_WATCH_URL}" target="_blank" rel="noopener"
                   style="color:#00d4ff; font-weight:600; text-decoration:none;">
                   ▶ Watch on YouTube →
                </a>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        st.caption(
            "🎬 EV overview video via YouTube · "
            f"[Watch full video on YouTube →]({_YT_WATCH_URL}) · "
            "For offline use, place `assets/ev_showcase.mp4` in the project folder."
        )

        # ── Dev setup hint — hidden inside a collapsed expander ───────────────
        with st.expander("📁 Using a local video instead?", expanded=False):
            st.markdown(
                "Place a file named **`ev_showcase.mp4`** inside the **`assets/`** folder "
                "at the project root, then restart the app. The local file will be used "
                "automatically and the YouTube embed will be hidden.",
                help="This message is intended for developers/admins setting up EVMitra."
            )

    st.markdown("---")

    # ── Platform stats ─────────────────────────────────────────────────────────
    st.markdown('<h2 style="font-family:Orbitron,monospace; color:#00d4ff;">📊 Platform Overview</h2>',
                unsafe_allow_html=True)
    try:
        from utils.db_helper import execute_query
        ev_count = execute_query("SELECT COUNT(*) as c FROM ev_vehicles")[0]["c"]
        scheme_count = execute_query("SELECT COUNT(*) as c FROM govt_schemes")[0]["c"]
        showroom_count = execute_query("SELECT COUNT(*) as c FROM showrooms")[0]["c"]
        charging_count = execute_query("SELECT COUNT(*) as c FROM charging_stations")[0]["c"]
    except Exception:
        ev_count = scheme_count = showroom_count = charging_count = "--"

    sc = st.columns(4)
    sc[0].metric("🚗 EVs in Database", ev_count)
    sc[1].metric("🏛️ Govt. Schemes", scheme_count)
    sc[2].metric("🏪 Showrooms", showroom_count)
    sc[3].metric("⚡ Charging Stations", charging_count)

    st.markdown("---")

    # ── Feature Cards ──────────────────────────────────────────────────────────
    st.markdown('<h2 style="font-family:Orbitron,monospace; color:#00d4ff;">🚀 Platform Features</h2>',
                unsafe_allow_html=True)

    features = [
        ("🔍", "EV Explorer", "Browse 25+ EVs with detailed specs, filtering, search and sorting.", "explorer"),
        ("🎯", "Find My EV", "Get Top 3 personalized recommendations with transparent scoring.", "find"),
        ("⚖️", "Compare EVs", "Side-by-side comparison of any 2 EVs with visual highlights.", "compare"),
        ("📊", "Owner Analytics", "Upload driving CSV and get efficiency trends, cost analysis, insights.", "analytics"),
        ("💰", "Cost Calculator", "Calculate EV vs petrol running costs. See annual savings with real formulas.", "calculator"),
        ("🌱", "Environmental Impact", "Estimate CO₂ tailpipe emissions avoided by switching to EV.", "environment"),
        ("🏛️", "Govt. Schemes", "Central and state EV subsidies with official sources.", "schemes"),
        ("⚡", "Charging Stations", "Find charging stations across Indian cities with map links.", "charging"),
        ("🏪", "Showrooms", "Locate EV showrooms with directions and contact info.", "showrooms"),
        ("🤖", "ML Insights", "ML-powered EV range prediction with real evaluation metrics.", "ml"),
    ]

    for i in range(0, len(features), 2):
        col1, col2 = st.columns(2)
        for col, idx in [(col1, i), (col2, i + 1)]:
            if idx < len(features):
                icon, title, desc, page_key = features[idx]
                with col:
                    st.markdown(f"""
                    <div class="ev-card">
                        <div style="font-size:2rem;">{icon}</div>
                        <h4 style="color:#00d4ff;margin:0.5rem 0 0.3rem;font-family:Orbitron,monospace;">{title}</h4>
                        <p style="color:#94a3b8;font-size:0.9rem;margin:0;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Open {title}", key=f"home_feat_{page_key}", use_container_width=True):
                        st.session_state.page = page_key
                        st.rerun()

    st.markdown("---")

    # ── Top EVs by Range chart ─────────────────────────────────────────────────
    st.markdown('<h2 style="font-family:Orbitron,monospace; color:#00d4ff;">📈 Top EVs by Claimed Range</h2>',
                unsafe_allow_html=True)
    try:
        from utils.db_helper import execute_query
        top_evs = execute_query("""
            SELECT brand || ' ' || model as name, range_km, vehicle_type
            FROM ev_vehicles WHERE range_km IS NOT NULL
            ORDER BY range_km DESC LIMIT 10
        """)
        if top_evs:
            df_top = pd.DataFrame(top_evs)
            colors = {"Car": "#00d4ff", "Scooter": "#7c3aed", "Motorcycle": "#f59e0b", "E-Rickshaw": "#10b981"}
            fig = px.bar(df_top, x="name", y="range_km",
                         color="vehicle_type", color_discrete_map=colors,
                         labels={"name": "EV Model", "range_km": "Range (km)"},
                         title="Top 10 EVs by Claimed Range (km)")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"), height=400,
                xaxis_tickangle=-30, legend=dict(bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("*Claimed range from manufacturer specifications. Actual range varies with driving conditions.*")
    except Exception:
        pass

    st.markdown("---")
    st.caption("""
    **Disclaimer:** EVMitra is an MCA Semester 3 academic mini-project.
    All data is for educational purposes. EV specifications are from manufacturer websites and public sources.
    Calculations are estimates only. Always verify before making purchase decisions.
    """)


# ── Page routing ─────────────────────────────────────────────────────────────
current_page = st.session_state.page

if current_page == "home":
    render_home()

elif current_page == "explorer":
    from modules.ev_explorer import render
    render()

elif current_page == "find":
    from modules.recommendation import render
    render()

elif current_page == "compare":
    from modules.comparison import render
    render()

elif current_page == "analytics":
    from modules.analytics import render
    render()

elif current_page == "calculator":
    from modules.cost_calculator import render
    render()

elif current_page == "environment":
    from modules.environmental import render
    render()

elif current_page == "schemes":
    from modules.schemes import render
    render()

elif current_page == "charging":
    from modules.charging import render
    render()

elif current_page == "showrooms":
    from modules.showrooms import render
    render()

elif current_page == "ml":
    from modules.ml_insights import render
    render()

elif current_page == "history":
    from modules.history import render
    render()

elif current_page == "admin":
    from modules.admin import render
    render()

else:
    render_home()
