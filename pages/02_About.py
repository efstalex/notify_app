import streamlit as st

st.title("ℹ️ About")
st.markdown(
    '''
    This is a minimal **Streamlit** starter:
    - Home page with file uploader
    - Dashboard page with cached data and charts
    - About page

    ### Next steps
    - Replace the demo data with your own.
    - Add inputs in the sidebar for user controls.
    - Use `st.cache_data`/`st.cache_resource` to speed things up.
    - Store secrets in `.streamlit/secrets.toml`.
    '''
)