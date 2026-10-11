from datetime import date, datetime
from collections import Counter
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, add_entry, get_entries, add_post, get_posts, add_reaction, flag_post, get_stats

st.set_page_config(page_title="EchoSpace", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<style>
:root { --ink:#243447; --muted:#68778a; --mint:#dff4eb; --lav:#eee8ff; --coral:#ffe8df; }
.stApp { background: linear-gradient(135deg,#f8fbff 0%,#f5fbf8 55%,#fbf7ff 100%); color:var(--ink); }
.block-container { max-width: 1180px; padding-top: 1.6rem; padding-bottom: 3rem; }
.hero { background:linear-gradient(120deg,#e0f5ed,#eee8ff); padding:2rem 2.2rem; border-radius:24px; border:1px solid #e6edf3; }
.hero h1 { font-size:2.6rem; margin:0; color:#243447; }
.hero p { color:#506176; font-size:1.08rem; margin-bottom:0; }
.pill { display:inline-block; background:white; border:1px solid #e3eaf0; padding:.35rem .7rem; border-radius:999px; margin:.15rem; color:#526274; font-size:.85rem; }
div[data-testid="stMetric"] { background:#fff; padding:1rem; border-radius:16px; border:1px solid #e7edf1; }
div.stButton > button { border-radius:12px; }
.small-note { color:#68778a; font-size:.88rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🌿 EchoSpace")
    st.caption("A quieter corner of the internet.")
    page = st.radio("Navigate", ["Home", "Share anonymously", "Mood journal", "My insights", "Community guidelines"])
    st.divider()
    st.caption("Privacy-first demo")
    st.caption("No account or public profile is required.")

if page == "Home":
    st.markdown("""<div class="hero">
    <span class="pill">ANONYMOUS BY DESIGN</span><span class="pill">GENTLE COMMUNITY</span>
    <h1>Some days need a little space.</h1>
    <p>Share what’s on your mind, notice your feelings, and offer kindness—without putting your name to it.</p>
    </div>""", unsafe_allow_html=True)
    st.write("")
    c1,c2,c3 = st.columns(3)
    stats = get_stats()
    c1.metric("Community notes", stats["posts"])
    c2.metric("Supportive reactions", stats["reactions"])
    c3.metric("Mood check-ins", stats["entries"])
    st.write("")
    left,right = st.columns([1.2, .8], gap="large")
    with left:
        st.subheader("A small reminder")
        st.info("You don’t have to turn every feeling into a lesson. Sometimes naming it is enough.")
        st.markdown("### Start wherever you are")
        a,b = st.columns(2)
        with a:
            st.markdown("**🫧 Share a thought**")
            st.write("Write anonymously and let it out.")
            if st.button("Open the community", use_container_width=True):
                st.session_state["jump"] = "Share anonymously"
                st.rerun()
        with b:
            st.markdown("**🌱 Check in with yourself**")
            st.write("Log a mood and add a private note.")
            if st.button("Open mood journal", use_container_width=True):
                st.session_state["jump"] = "Mood journal"
                st.rerun()
    with right:
        st.subheader("A gentle check-in")
        mood = st.select_slider("How are you feeling right now?", options=["Very low","Low","Okay","Good","Great"], value="Okay")
        prompts = {"Very low":"What would make the next ten minutes a little safer or softer?",
                   "Low":"What is one thing you wish someone understood today?",
                   "Okay":"What is taking up most of your mental space?",
                   "Good":"What has helped you feel like yourself today?",
                   "Great":"What small moment would you like to remember?"}
        st.success(prompts[mood])
        st.caption("This quick check-in is not saved unless you use the Mood journal page.")
    st.divider()
    st.caption("EchoSpace is a peer-support and reflection project, not therapy or crisis care.")

elif page == "Share anonymously":
    st.title("🫧 Share anonymously")
    st.write("You can share a feeling, a small win, or something you’re still figuring out.")
    st.caption("Please don’t include names, phone numbers, addresses, or other identifying details.")
    with st.form("share_form", clear_on_submit=True):
        category = st.selectbox("What kind of note is this?", ["Just need to vent","A small win","Looking for encouragement","Something I learned","Offering kindness"])
        body = st.text_area("Your note", max_chars=700, height=150, placeholder="Write as much or as little as you need…")
        trigger = st.checkbox("I’ve checked that this post does not identify me or someone else.")
        submitted = st.form_submit_button("Share with the community", type="primary")
        if submitted:
            if len(body.strip()) < 8:
                st.error("Please add a little more detail (at least 8 characters).")
            elif not trigger:
                st.warning("Please confirm that your note does not identify anyone.")
            elif re.search(r'(?i)(\b[\w.+-]+@[\w-]+\.[\w.-]+\b|\b\d{10}\b|https?://)', body):
                st.warning("This note may contain contact information or a link. Remove it before posting.")
            else:
                add_post(category, body.strip())
                st.success("Your note has been shared anonymously.")
                st.rerun()
    st.divider()
    st.subheader("Community notes")
    posts = get_posts()
    if not posts:
        st.info("The community is quiet for now. You could be the first to share a kind note.")
    for p in posts:
        with st.container(border=True):
            st.caption(f'{p["category"]}  ·  {p["created_at"]}')
            st.write(p["body"])
            col1,col2,col3 = st.columns([1,1,4])
            for label, emoji in [("I hear you","💛"),("Sending strength","🌱")]:
                with (col1 if label=="I hear you" else col2):
                    if st.button(f"{emoji} {label} · {p['reactions'].get(label,0)}", key=f"react_{p['id']}_{label}"):
                        add_reaction(p["id"], label)
                        st.rerun()
            with col3:
                with st.popover("Report note"):
                    reason = st.selectbox("Reason", ["Personal information","Harmful or abusive","Spam or unrelated"], key=f"reason_{p['id']}")
                    if st.button("Submit report", key=f"flag_{p['id']}"):
                        flag_post(p["id"], reason)
                        st.success("Thanks. This demo records the report for review.")
elif page == "Mood journal":
    st.title("🌱 Mood journal")
    st.write("A private-feeling space to notice patterns. Entries are stored locally in this app’s SQLite database.")
    with st.form("mood_form", clear_on_submit=True):
        d = st.date_input("Date", value=date.today(), max_value=date.today())
        mood = st.select_slider("Mood", options=["Very low","Low","Okay","Good","Great"], value="Okay")
        tags = st.multiselect("What might be connected?", ["Study","Work","Family","Friends","Rest","Health","Movement","Something else"])
        note = st.text_area("Optional note (private to this app database)", max_chars=1000, placeholder="What do you want to remember about today?")
        save = st.form_submit_button("Save check-in", type="primary")
        if save:
            add_entry(str(d), mood, ", ".join(tags), note.strip())
            st.success("Check-in saved.")
            st.rerun()
    entries = get_entries()
    st.divider()
    st.subheader("Recent check-ins")
    if entries:
        for e in entries[:10]:
            with st.container(border=True):
                st.markdown(f"**{e['mood']}** · {e['entry_date']}")
                if e["tags"]: st.caption(e["tags"])
                if e["note"]: st.write(e["note"])
    else:
        st.info("No check-ins yet. Your first entry can be just one word.")
elif page == "My insights":
    st.title("📈 My insights")
    entries = get_entries()
    if not entries:
        st.info("Save a few mood check-ins to see your personal trends here.")
    else:
        df = pd.DataFrame(entries)
        order = ["Very low","Low","Okay","Good","Great"]
        df["score"] = df["mood"].map({m:i+1 for i,m in enumerate(order)})
        df["entry_date"] = pd.to_datetime(df["entry_date"])
        c1,c2 = st.columns(2)
        c1.metric("Check-ins recorded", len(df))
        c2.metric("Most common mood", df["mood"].mode().iloc[0])
        trend = df.sort_values("entry_date").groupby("entry_date", as_index=False)["score"].mean()
        fig = px.line(trend, x="entry_date", y="score", markers=True, range_y=[1,5], title="Mood over time")
        fig.update_layout(yaxis_title="Mood score (1–5)", xaxis_title="", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        counts = df["mood"].value_counts().reindex(order, fill_value=0).reset_index()
        counts.columns = ["Mood","Check-ins"]
        fig2 = px.bar(counts, x="Mood", y="Check-ins", title="Mood distribution")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
        st.download_button("Download my check-ins as CSV", df.drop(columns=["score"]).to_csv(index=False).encode("utf-8"), "echospace_mood_checkins.csv", "text/csv")
        st.caption("These charts help you reflect; they do not diagnose or explain the cause of a mood.")
else:
    st.title("🧭 Community guidelines")
    st.markdown("""
    ### Be gentle with each other
    - Respond with kindness; advice is optional, listening is valuable.
    - Respect different experiences. Avoid judgment, insults, harassment, or discrimination.
    - Do not share personal details about yourself or another person.
    - Do not post medical claims, diagnoses, or instructions that could put someone at risk.
    - Use the report option for unsafe, identifying, abusive, or spam content.
    - This demo is not monitored in real time. Do not rely on it for urgent help.

    ### A note about safety
    EchoSpace is a student web-technology project, not a mental-health service. If you may hurt yourself or someone else, contact local emergency services or a trusted person immediately. In India, emergency number **112** is available for urgent assistance.

    ### Privacy
    This version uses a local SQLite database. It does not implement accounts, encryption, deployment-grade moderation, or guaranteed anonymity against a server operator. Do not deploy with real sensitive disclosures without adding security, moderation, retention controls, and a clear privacy policy.
    """)
st.markdown("---")
st.caption("EchoSpace · A student project for thoughtful, anonymous peer support.")
