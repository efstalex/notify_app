
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from dateutil import tz
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="Notify App", page_icon="🔔", layout="wide")

TZ = tz.gettz("Europe/Athens")

@st.cache_resource
def get_conn():
    conn = sqlite3.connect("notify.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT,
            due_utc TEXT NOT NULL,
            created_utc TEXT NOT NULL,
            channel TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)
    return conn

def insert_reminder(conn, title, message, due_dt_local, channel):
    due_utc = (due_dt_local.astimezone(tz.UTC)).isoformat()
    created_utc = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO reminders (title, message, due_utc, created_utc, channel, status) VALUES (?,?,?,?,?,?)",
        (title, message, due_utc, created_utc, channel, "pending"),
    )
    conn.commit()

def read_reminders(conn, include_sent=False):
    q = "SELECT id, title, message, due_utc, created_utc, channel, status FROM reminders"
    if not include_sent:
        q += " WHERE status='pending'"
    q += " ORDER BY datetime(due_utc) ASC"
    rows = conn.execute(q).fetchall()
    df = pd.DataFrame(rows, columns=["id","title","message","due_utc","created_utc","channel","status"])
    if not df.empty:
        df["due_local"] = (
            pd.to_datetime(df["due_utc"], utc=True)
            .dt.tz_convert("Europe/Athens")
            .dt.tz_localize(None)
        )
        df["created_local"] = (
            pd.to_datetime(df["created_utc"], utc=True)
            .dt.tz_convert("Europe/Athens")
            .dt.tz_localize(None)
        )
    return df

def mark_sent(conn, rid):
    conn.execute("UPDATE reminders SET status='sent' WHERE id=?", (rid,))
    conn.commit()

def send_email(subject, body):
    cfg = st.secrets.get("smtp", None)
    if not cfg:
        raise RuntimeError("SMTP not configured in .streamlit/secrets.toml")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = cfg.get("from", cfg.get("user"))
    msg["To"] = cfg["to"]
    with smtplib.SMTP(cfg["host"], int(cfg.get("port", 587))) as server:
        server.starttls()
        server.login(cfg["user"], cfg["password"])
        server.sendmail(msg["From"], [cfg["to"]], msg.as_string())

with st.sidebar:
    st.title("🔔 Notify App")
    st.caption("Create reminders and optionally email them when due.")
    st.divider()
    st.subheader("Quick actions")
    if st.button("Run due check now"):
        st.session_state["_run_check"] = True
    if st.button("Reset Session State"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

st.title("Create a Reminder")
conn = get_conn()

with st.form("new_reminder"):
    title = st.text_input("Title", placeholder="e.g., Send weekly report")
    message = st.text_area("Message (optional)", placeholder="What should happen?")
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Due date", value=datetime.now(TZ).date())
    with col2:
        time = st.time_input("Due time", value=(datetime.now(TZ) + timedelta(minutes=30)).time())
    channel = st.selectbox("Channel", ["in-app", "email"])
    submitted = st.form_submit_button("Add reminder", type="primary")
    if submitted:
        if not title.strip():
            st.error("Title is required.")
        else:
            due_local = datetime.combine(date, time).replace(tzinfo=TZ)
            insert_reminder(conn, title.strip(), message.strip(), due_local, channel)
            st.success("Reminder added!")

st.divider()
st.subheader("Upcoming Reminders")

show_sent = st.checkbox("Show sent reminders", value=False)
df = read_reminders(conn, include_sent=show_sent)
if df.empty:
    st.info("No reminders yet. Add one above.")
else:
    st.dataframe(df[["id","title","due_local","channel","status","message"]], use_container_width=True)

    from datetime import datetime as _dt
    now_utc = _dt.utcnow()
    if st.button("Check and send due reminders") or st.session_state.get("_run_check", False):
        sent_count = 0
        for _, row in df.iterrows():
            due_utc = pd.to_datetime(row["due_utc"], utc=True).to_pydatetime()
            if row["status"] == "pending" and due_utc <= now_utc:
                if row["channel"] == "email":
                    try:
                        subject = f"[Notify App] {row['title']}"
                        body = row["message"] or "(no message)"
                        send_email(subject, body)
                        mark_sent(conn, int(row["id"]))
                        sent_count += 1
                    except Exception as e:
                        st.warning(f"Email failed for id={row['id']}: {e}")
                else:
                    mark_sent(conn, int(row["id"]))
                    st.toast(f"Reminder: {row['title']}", icon="🔔")
                    sent_count += 1
        st.session_state["_run_check"] = False
        st.success(f"Processed {sent_count} due reminder(s).")

st.caption("Time zone: Europe/Athens")
