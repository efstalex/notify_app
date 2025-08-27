import streamlit as st
import pandas as pd
import numpy as np
import time

st.title("📊 Dashboard")
st.caption("A tiny example demonstrating state, tabs, and charts.")

# Generate demo data (or cache your own data load here)
@st.cache_data
def load_data(n=100):
    ts = pd.date_range("2024-01-01", periods=n, freq="D")
    values = np.random.randn(n).cumsum()
    return pd.DataFrame({"date": ts, "value": values})

df = load_data()

tab1, tab2 = st.tabs(["Overview", "Details"])

with tab1:
    st.subheader("Trend")
    st.line_chart(df.set_index("date"))

    st.subheader("KPIs")
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest value", f"{df['value'].iloc[-1]:.2f}")
    col2.metric("Mean", f"{df['value'].mean():.2f}")
    col3.metric("Std dev", f"{df['value'].std():.2f}")

with tab2:
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)
    with st.expander("Simulate a long task"):
        if st.button("Run task"):
            with st.status("Working...", expanded=True) as status:
                for i in range(5):
                    time.sleep(0.4)
                    st.write(f"Step {i+1}/5 complete")
                status.update(label="Done!", state="complete", expanded=False)