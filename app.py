import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, time as dtime
from dateutil import tz

st.set_page_config(page_title="Notify App — Create Event", page_icon="🔵", layout="wide")
TZ = tz.gettz("Europe/Athens")

@st.cache_resource
def get_conn():
    conn = sqlite3.connect("notify.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT,
            start_utc TEXT NOT NULL,
            all_day INTEGER NOT NULL DEFAULT 0,
            channel TEXT NOT NULL,
            created_utc TEXT NOT NULL
        )
    """)
    return conn

def to_utc_iso(local_dt: datetime) -> str:
    return local_dt.astimezone(tz.UTC).isoformat()

def insert_event(conn, title, message, event_date, event_time, all_day, channel):
    if all_day:
        local_dt = datetime.combine(event_date, dtime(0, 0)).replace(tzinfo=TZ)
    else:
        local_dt = datetime.combine(event_date, event_time).replace(tzinfo=TZ)
    start_utc = to_utc_iso(local_dt)
    created_utc = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO events (title, message, start_utc, all_day, channel, created_utc) VALUES (?,?,?,?,?,?)",
        (title, message, start_utc, int(all_day), channel, created_utc),
    )
    conn.commit()

def read_events(conn, limit=200):
    rows = conn.execute(
        "SELECT id, title, message, start_utc, all_day, channel, created_utc FROM events ORDER BY datetime(start_utc) ASC LIMIT ?",
        (limit,)
    ).fetchall()
    df = pd.DataFrame(rows, columns=["id","title","message","start_utc","all_day","channel","created_utc"])
    if df.empty:
        return df
    df["start_local"] = (
        pd.to_datetime(df["start_utc"], utc=True)
        .dt.tz_convert("Europe/Athens")
        .dt.tz_localize(None)
    )
    df["created_local"] = (
        pd.to_datetime(df["created_utc"], utc=True)
        .dt.tz_convert("Europe/Athens")
        .dt.tz_localize(None)
    )
    return df

with st.sidebar:
    st.title("🔵 Notify App")
    st.caption("Minimal create-event page. Build onwards later.")

st.header("Create Event")
conn = get_conn()

with st.form("create_event"):
    title = st.text_input("Title", placeholder="e.g., Team meeting")
    message = st.text_area("Message (optional)", placeholder="Add an optional note")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        event_date = st.date_input("Event date")
    with col2:
        all_day = st.toggle("All day", value=True)
    with col3:
        default_time = dtime(9, 0)
        event_time = st.time_input("Event time", value=default_time, disabled=all_day)
    channel = st.selectbox("Channel", ["in-app", "email"])
    submitted = st.form_submit_button("Create event", type="primary")
    if submitted:
        if not title.strip():
            st.error("Title is required.")
        else:
            insert_event(conn, title.strip(), message.strip(), event_date, event_time, all_day, channel)
            st.success("Event created.")

st.subheader("Upcoming events")
df = read_events(conn, limit=200)
if df.empty:
    st.info("No events yet. Create one above.")
else:
    view = df[["id","title","start_local","all_day","channel","message"]].rename(
        columns={"start_local":"when (local)"}
    )
    st.dataframe(view, use_container_width=True)

st.caption("Times shown in local time (Europe/Athens). Stored in UTC internally.")