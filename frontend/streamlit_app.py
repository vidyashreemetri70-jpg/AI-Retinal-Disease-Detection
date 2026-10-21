import streamlit as st
from utils.styling import inject_global_css
from pages_logic.landing import show_landing
from pages_logic.auth import show_login, show_register
from pages_logic.dashboard import show_dashboard

st.set_page_config(
    page_title="RetinaScan AI",
    page_icon="👁️", 
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_global_css()

defaults = {
    "page": "landing",
    "portal": None,
    "user": None,
    "history_cache": None,
    "last_prediction": None,
    "multi_patients": [0],
    "multi_results": [],
    "screening_version": 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

page = st.session_state.page

if page == "landing":
    show_landing()
elif page == "login":
    show_login()
elif page == "register":
    show_register()
elif page == "dashboard":
    show_dashboard()
else:
    st.session_state.page = "landing"
    st.rerun()
