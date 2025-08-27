
import streamlit as st
import pandas as pd
import sqlite3

st.title("📊 Dashboard")
st.caption("Overview of reminders and activity.")

@st.cache_resource
def get_conn():
    return sqlite3.connect("notify.db", check_same_thread=False)

def load_df(conn, include_sent=True):
    q = "SELECT id, title, message, due_utc, created_utc, channel, status FROM reminders ORDER BY datetime(due_utc) ASC"
    rows = conn.execute(q).fetchall()
    df = pd.DataFrame(rows, columns=["id","title","message","due_utc","created_utc","channel","status"])
    if df.empty:
        return df
    df["due_utc"] = pd.to_datetime(df["due_utc"], utc=True)
    df["created_utc"] = pd.to_datetime(df["created_utc"], utc=True)
    df["due_local"] = df["due_utc"].dt.tz_convert("Europe/Athens").dt.tz_localize(None)
    df["created_local"] = df["created_utc"].dt.tz_convert("Europe/Athens").dt.tz_localize(None)
    if not include_sent:
        df = df[df["status"] != "sent"]
    return df

conn = get_conn()
df = load_df(conn, include_sent=True)

if df.empty:
    st.info("No data yet — create reminders on the Home page.")
else:
    total = len(df)
    pending = int((df["status"]=="pending").sum())
    sent = int((df["status"]=="sent").sum())
    email_ct = int((df["channel"]=="email").sum())
    inapp_ct = int((df["channel"]=="in-app").sum())
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total", total)
    c2.metric("Pending", pending)
    c3.metric("Sent", sent)
    c4.metric("Email", email_ct)
    c5.metric("In-app", inapp_ct)

    st.divider()
    st.subheader("Timeline (local time)")
    st.line_chart(df.set_index("due_local")[["id"]].rename(columns={"id":"reminders"}))

    st.subheader("All reminders")
    st.dataframe(df[["id","title","due_local","channel","status","message"]], use_container_width=True)
