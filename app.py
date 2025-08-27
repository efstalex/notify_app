import streamlit as st
import pandas as pd

st.set_page_config(page_title="My Streamlit App", page_icon="🚀", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("🚀 My Streamlit App")
    st.markdown("Use the pages below to explore the app.")
    st.divider()
    st.subheader("Quick actions")
    if st.button("Reset Session"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

st.title("Home")
st.write("Welcome! This is your starter Streamlit app.")

# --- Simple demo widgets ---
uploaded = st.file_uploader("Upload a CSV to preview", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    st.success(f"Loaded {len(df):,} rows.")
    st.dataframe(df.head(50), use_container_width=True)

st.info("Navigate to **Dashboard** and **About** pages from the sidebar (upper-left).")