"""
EVMitra – History Module
Displays the local session-based activity history (no login required).
"""

import streamlit as st


def render():
    """Render the History page."""
    st.markdown('<h1 class="page-title">📜 Activity History</h1>', unsafe_allow_html=True)
    st.markdown("Your recent activity in this EVMitra session.")

    st.info("""
    ℹ️ **How History Works:**
    - History is stored in your **browser session only** (no login required, no server storage)
    - It will be cleared when you close or refresh the browser
    - Because there is no user account, history cannot be synced across devices
    """)

    history = st.session_state.get("history", [])

    if not history:
        st.markdown("""
        <div style="text-align:center; padding:60px; color:#6b7280;">
            <h3>No History Yet</h3>
            <p>Start using EVMitra features and your activity will appear here.</p>
            <p>Try: Find My EV → Cost Calculator → Environmental Impact</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"**{len(history)} activities recorded this session**")
    st.markdown("---")

    # Display most recent first
    for i, item in enumerate(reversed(history)):
        action = item.get("action", "Unknown")
        result = item.get("result", "")
        prefs = item.get("prefs", "")

        icons = {
            "Find My EV": "🎯",
            "Cost Calculator": "💰",
            "Environmental Impact": "🌱",
            "Owner Analytics": "📊",
        }
        icon = icons.get(action, "📌")

        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"## {icon}")
                st.caption(f"#{len(history) - i}")
            with col2:
                st.markdown(f"**{action}**")
                if result:
                    st.markdown(f"📋 {result}")
                if prefs:
                    st.caption(f"⚙️ {prefs}")
            st.divider()

    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.history = []
        st.success("History cleared!")
        st.rerun()

    # Compare shortlist
    compare_list = st.session_state.get("compare_list", [])
    if compare_list:
        st.markdown("---")
        st.subheader("⚖️ Saved Comparison Shortlist")
        for ev in compare_list:
            st.markdown(f"• {ev}")
        if st.button("🗑️ Clear Comparison List"):
            st.session_state.compare_list = []
            st.rerun()
