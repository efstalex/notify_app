
import streamlit as st

st.title("About this Notify App")
st.write("This app is a minimal reminder system built with Streamlit.")
st.write("Add reminders with a local time (Europe/Athens) and store them in a local SQLite database (notify.db).")
st.write("Use the 'Check and send due reminders' button to process reminders that are due.")
st.write("If SMTP is configured in .streamlit/secrets.toml, email reminders will be sent; otherwise they are skipped.")
st.write("Do not commit .streamlit/secrets.toml (it should be in .gitignore).")
