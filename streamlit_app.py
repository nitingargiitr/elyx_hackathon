# streamlit_app.py
import json
import re
import uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st
from dateutil import parser as dateparser
from streamlit_timeline import timeline  # (ok if unused)
import plotly.express as px
import plotly.graph_objects as go
from pyvis.network import Network  # (ok if unused)
import streamlit.components.v1 as components  # (ok if unused)

# ----------------------------------------------------------
# Config
# ----------------------------------------------------------
st.set_page_config(page_title="Elyx Health – Member Journey", layout="wide", page_icon="🏥")
DATA_DIR = Path("elyx_conversations")
TEAM_MEMBERS = ["Ruby", "Dr. Warren", "Advik", "Carla", "Rachel", "Neel"]
ROLE_ICON = {"Ruby": "🧭", "Dr. Warren": "🩺", "Advik": "📈", "Carla": "🥗", "Rachel": "🏋", "Neel": "🧠", "Member": "👤"}



def render_professional_header(member_name="Rohan Patel"):
    st.markdown("""
    <style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .elyx-header {
        background: linear-gradient(270deg, #667eea, #764ba2, #4facfe);
        background-size: 600% 600%;
        animation: gradientShift 20s ease infinite;
        padding: 35px 15px 25px 15px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        font-family: Arial, sans-serif;
        position: relative;
    }
    .elyx-title {
        font-size: 42px;
        font-weight: bold;
        margin: 0 0 10px 0;
        text-shadow: 1px 1px 8px rgba(0,0,0,0.6);
        letter-spacing: 1px;
    }
    .elyx-subtitle {
        font-size: 16px;
        margin: 0 0 18px 0;
        opacity: 0.95;
        font-style: italic;
    }
    .elyx-username {
        background: rgba(255,255,255,0.18);
        display: inline-block;
        padding: 8px 20px;
        border-radius: 25px;
        font-size: 15px;
        font-weight: bold;
        letter-spacing: 0.5px;
        box-shadow: 0 0 10px rgba(255,255,255,0.4);
        margin-bottom: 18px;
    }
    .elyx-stats {
        margin-top: 10px;
    }
    .elyx-badge {
        display: inline-block;
        padding: 10px 16px;
        margin: 6px 8px;
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        font-size: 14px;
        font-weight: bold;
        letter-spacing: 0.4px;
        transition: background 0.3s ease;
        box-shadow: inset 0 0 8px rgba(255,255,255,0.25);
    }
    .elyx-badge:hover {
        background: rgba(255,255,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="elyx-header">
        <div class="elyx-title">🏥 Elyx Health</div>
        <div class="elyx-subtitle">Transforming Wellness with Data, Care & Intelligence</div>
        <div class="elyx-username"> 👱‍♂ {member_name}</div>
        <div class="elyx-stats">
            <span class="elyx-badge">👥 120+ Members</span>
            <span class="elyx-badge">🩺 6 Specialists</span>
            <span class="elyx-badge">📊 92% Goal Success</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------
# CSS (WhatsApp style chat )
# ----------------------------------------------------------
st.markdown("""
<style>
.stApp{background:#0b141a;color:#e9edef}
section[data-testid="stSidebar"]{background:#081419}
.kpi{background:#111b21;border-radius:10px;padding:12px}

/* Remove default Streamlit padding */
.block-container {
    padding-top: 1rem;
}

.chat-wrap {
  background:#111b21;
  border-radius:12px;
  padding:12px;
  max-height:70vh;
  overflow:auto;
}
.msg-row {
  display:flex; 
  margin:8px 0;
  align-items:flex-end;
}
.msg-row.me {justify-content:flex-end;}
.msg-row.them {justify-content:flex-start;}

.msg-container {
  max-width:65%;
  display:flex;
  flex-direction:column;
}

.sender-name {
  font-size:12px;
  font-weight:bold;
  margin-bottom:2px;
  padding:0 4px;
}
.me .sender-name {
  color:#4fc3f7;
  text-align:right;
}
.them .sender-name {
  color:#81c784;
  text-align:left;
}

.bubble {
  padding:10px 12px;
  border-radius:10px;
  font-size:14px;
  line-height:1.4;
  position:relative;
  word-wrap:break-word;
  white-space:pre-wrap;
}
.me .bubble {
  background:#005c4b;
  color:white;
  border-bottom-right-radius:4px;
}
.them .bubble {
  background:#202c33;
  color:#e9edef;
  border-bottom-left-radius:4px;
}
.meta {
  font-size:11px;
  color:#9aa6ae;
  margin-top:4px;
  text-align:right;
}
.date-sep {
  text-align:center;
  margin:12px 0;
  color:#9aa6ae;
  font-size:12px;
  background:#1c272d;
  display:inline-block;
  padding:4px 10px;
  border-radius:12px;
}

/* Decisions list cards */
.decision-card{
  background:#111b21;border:1px solid #1f2c33;border-radius:10px;
  padding:12px;margin-bottom:10px
}
.decision-type{font-weight:600;padding:4px 8px;border-radius:8px;background:#1f2c33;margin-right:8px}
.tag-pill{font-size:11px;padding:2px 8px;border:1px solid #2a3942;border-radius:999px;margin-right:6px;color:#9aa6ae}
.small-meta{font-size:12px;color:#9aa6ae}

/* Enhanced styling for the main content */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    border: 1px solid rgba(255,255,255,0.1);
}

.stTabs [aria-selected="true"] {
    background-color: rgba(102, 126, 234, 0.2) !important;
    border-color: rgba(102, 126, 234, 0.5) !important;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# Utils
# ----------------------------------------------------------
def parse_timestamp(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    try:
        dt = dateparser.parse(ts)
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%m/%d/%Y %I:%M %p"):
            try:
                dt = datetime.strptime(ts, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except:
                continue
    return None


def ensure_message_ids(messages: List[Dict[str, Any]]) -> None:
    for i, m in enumerate(messages):
        if "mid" not in m:
            if "id" in m and isinstance(m["id"], str):
                m["mid"] = m["id"]
            else:
                m["mid"] = f"m{(i + 1):05d}"


def load_month_files():
    import calendar

    files = list(DATA_DIR.glob("*.json"))

    def month_key(f):
        month_name = f.stem.split("_")[0]
        try:
            return list(calendar.month_name).index(month_name)
        except ValueError:
            return 13

    files = sorted(files, key=month_key)
    months = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for m in data:
                # normalize key 'message' -> 'text' if present
                if "message" in m and "text" not in m:
                    m["text"] = m.pop("message")
            months.append({"label": f.stem, "file": f.name, "data": data})
        except Exception as e:
            st.error(f"Error loading {f.name}: {e}")
    return months


def is_team_sender(sender: str) -> bool:
    return bool(sender and any(n.lower() in sender.lower() for n in TEAM_MEMBERS))


def get_sender_icon(sender: str) -> str:
    """Get emoji icon for sender"""
    for role, icon in ROLE_ICON.items():
        if role.lower() in sender.lower():
            return icon
    return "👤"


# ----------------------------------------------------------
# Chat
# ----------------------------------------------------------
def render_chat(messages: List[Dict[str, Any]]):
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    last_date = None

    for msg in messages:
        sender = msg.get("sender", "Unknown")
        text = (msg.get("text", "") or "").strip()
        if not text:
            continue
        ts = msg.get("timestamp", "")
        dt = parse_timestamp(ts)
        timestr = dt.strftime("%I:%M %p") if dt else ""

        # date pill
        if dt:
            date_only = dt.date()
            if last_date != date_only:
                today = datetime.now().date()
                if date_only == today:
                    label = "Today"
                elif date_only == today - timedelta(days=1):
                    label = "Yesterday"
                else:
                    label = dt.strftime("%B %d, %Y")
                st.markdown(
                    f"<div style='display:flex;justify-content:center;align-items:center;margin:10px 0;'><div class='date-sep'>{label}</div></div>",
                    unsafe_allow_html=True,
                )
                last_date = date_only

        align = "them" if is_team_sender(sender) else "me"

        # Get sender icon
        icon = get_sender_icon(sender)
        sender_display = f"{icon} {sender}"

        st.markdown(
            f"""<div class="msg-row {align}">
                    <div class="msg-container">
                        <div class="sender-name">{sender_display}</div>
                        <div class="bubble">{text}<div class="meta">{timestr}</div></div>
                    </div>
                </div>""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------------
# Sankey
# ----------------------------------------------------------
_DECISION_RULES: List[Tuple[str, re.Pattern]] = [
    ("plan_update", re.compile(r"(plan|protocol|update|revised|v\d)", re.I)),
    ("order_labs", re.compile(r"(blood|panel|test|apob|hs-?crp|ogtt|lipid|scan|mri)", re.I)),
    ("adaptation", re.compile(r"(travel|stress|snack|late night|missed|non-?adherence|skip)", re.I)),
    ("nutrition", re.compile(r"(diet|macro|protein|carb|fat|calorie|meal|coach)", re.I)),
    ("followup", re.compile(r"(follow up|check[- ]?in|review|touch base)", re.I)),
]


def extract_decisions(messages: List[Dict[str, Any]]) -> pd.DataFrame:
    ensure_message_ids(messages)
    rows = []
    for idx, m in enumerate(messages):
        text = (m.get("text", "") or "")
        sender = m.get("sender", "Unknown")
        if not text:
            continue
        ts = parse_timestamp(m.get("timestamp", "")) or datetime.fromtimestamp(0, tz=timezone.utc)
        if is_team_sender(sender):
            for t, pat in _DECISION_RULES:
                if pat.search(text):
                    rows.append({
                        "timestamp": ts,
                        "mid": m.get("mid"),
                        "sender": sender,
                        "type": t,
                        "details": text.strip(),
                        "index": idx,
                    })
    return pd.DataFrame(rows)


def build_sankey_from_messages(messages: List[Dict[str, Any]]):
    dec_df = extract_decisions(messages)
    if dec_df.empty:
        return [], {"source": [], "target": [], "value": []}

    nodes, node_index = [], {}
    links = {"source": [], "target": [], "value": []}

    def add_node(name):
        if name in node_index:
            return node_index[name]
        idx = len(nodes)
        nodes.append(name)
        node_index[name] = idx
        return idx

    for _, row in dec_df.iterrows():
        actor = row["sender"]
        decision = f"DECISION: {row['details'][:50]}..."

        actor_idx = add_node(actor)
        decision_idx = add_node(decision)

        links["source"].append(actor_idx)
        links["target"].append(decision_idx)
        links["value"].append(1)

        # Look for context
        context_msgs = messages[max(0, row["index"] - 3):row["index"]]
        for cm in context_msgs:
            cause_label = f"{cm['sender']}: {cm['text'][:40]}..."
            cause_idx = add_node(cause_label)
            links["source"].append(cause_idx)
            links["target"].append(actor_idx)
            links["value"].append(1)

    return nodes, links


def render_sankey_rationale(messages: List[Dict[str, Any]]):
    nodes, links = build_sankey_from_messages(messages)
    if not nodes or not links["source"]:
        st.info("No decision flows found.")
        return

    node_colors = []
    for n in nodes:
        if n.startswith("DECISION"):
            node_colors.append("#6BCB77")
        elif any(tm in n for tm in TEAM_MEMBERS):
            node_colors.append("#4D96FF")
        else:
            node_colors.append("#FFD93D")

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            label=nodes,
            pad=25,
            thickness=22,
            color=node_colors
        ),
        link=dict(
            source=links["source"],
            target=links["target"],
            value=links["value"],
            color="rgba(180,180,180,0.3)"
        )
    )])

    fig.update_layout(
        title_text="🕸 Cause → Actor → Decision (Conversation Rationale)",
        font=dict(size=12, color="#E9EDEF"),
        paper_bgcolor="#0b141a",
        plot_bgcolor="#0b141a",
        height=700
    )
    st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------------
# Recovery extraction for decisions
# ----------------------------------------------------------
def extract_recovery_data(messages: List[Dict[str, Any]]) -> float:
    """Extract average recovery percentage from messages"""
    recovery_values = []
    for m in messages:
        text = (m.get("text", "") or "")
        # Look for recovery patterns
        m_rec = (
                re.search(r"\brecovery[:\s\-]?(\d{1,3})\s*%?", text, re.I) or
                re.search(r"(\d{1,3})\s*%?\s*recovery", text, re.I)
        )
        if m_rec:
            recovery_val = int(m_rec.group(1))
            if 0 <= recovery_val <= 100:  # Valid recovery percentage
                recovery_values.append(recovery_val)

    return np.mean(recovery_values) if recovery_values else None


# ----------------------------------------------------------
# Decisions
# ----------------------------------------------------------
def _tags_from_text(text: str) -> List[str]:
    tags = set(re.findall(r"#([\w-]+)", text))
    low = text.lower()
    if re.search(r"\b(whoop|garmin|hrv|recovery|sleep|readiness)\b", low):
        tags.add("wearable")
    if re.search(r"\b(travel|stress|busy|deadline|sick|injury|missed|skip)\b", low):
        tags.add("lifestyle")
    if re.search(r"(apob|hs-crp|ogtt|lipid|scan|mri)", low):
        tags.add("diagnostic")
    if re.search(r"(plan|protocol|update|revised|v\d)", low):
        tags.add("plan")
    return sorted(tags)


def _context_messages(messages: List[Dict[str, Any]], center_index: int, window: int = 2) -> List[Dict[str, Any]]:
    lo = max(0, center_index - window)
    hi = min(len(messages), center_index + window + 1)
    return messages[lo:hi]


def render_decisions_tab(messages: List[Dict[str, Any]]):
    st.markdown("### 🧭 Traceable Decisions")
    df = extract_decisions(messages)

    # Extract average recovery for this month
    avg_recovery = extract_recovery_data(messages)

    if df.empty:
        st.info("No decisions detected for this month.")
        return

    # Filters
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        type_filter = st.multiselect("Decision Type", options=sorted(df["type"].unique()),
                                     default=sorted(df["type"].unique()))
    with c2:
        min_ts, max_ts = df["timestamp"].min(), df["timestamp"].max()
        start, end = st.date_input("Range", value=(min_ts.date(), max_ts.date()))
    with c3:
        # Extract tags from decisions
        all_tags = []
        for _, row in df.iterrows():
            tags = _tags_from_text(row["details"])
            all_tags.extend(tags)
        tag_options = sorted(set(all_tags))
        tag_filter = st.multiselect("Tags", options=tag_options, default=[])

    search = st.text_input("Search text", value="")

    # Apply filters
    mask = df["type"].isin(type_filter)
    mask &= df["timestamp"].dt.date.between(pd.to_datetime(start).date(), pd.to_datetime(end).date())
    if search:
        mask &= df["details"].str.contains(search, case=False, na=False)
    if tag_filter:
        mask &= df.apply(lambda row: any(tag in _tags_from_text(row["details"]) for tag in tag_filter), axis=1)
    fdf = df[mask].copy()

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Decisions", f"{len(fdf)}")
    k2.metric("Types", f"{fdf['type'].nunique()}")
    k3.metric("Actors", f"{fdf['sender'].nunique()}")
    k4.metric("Avg Recovery", f"{avg_recovery:.1f}%" if avg_recovery is not None else "–")

    # Mini bar by type
    by_type = fdf.groupby("type")["mid"].count().reset_index().rename(columns={"mid": "count"})
    if not by_type.empty:
        fig = px.bar(by_type, x="type", y="count", title="Decisions by Type", color="type")
        fig.update_layout(template="plotly_dark", height=280, xaxis_title=None, yaxis_title=None, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Decision cards
    st.markdown("#### Items")
    for _, row in fdf.iterrows():
        ts_str = row["timestamp"].strftime("%b %d, %Y • %I:%M %p")
        tags = _tags_from_text(row["details"])
        tags_html = "".join([f"<span class='tag-pill'>#{t}</span>" for t in tags])
        st.markdown(
            f"""
            <div class="decision-card">
                <div class="small-meta">{ts_str} · <b>{row['sender']}</b> · 
                <span class="decision-type">{row['type']}</span></div>
                <div style="margin-top:6px">{row['details']}</div>
                <div style="margin-top:8px">{tags_html}</div>
                <div class="small-meta" style="margin-top:6px">
                    Message ID: <code>{row['mid']}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.expander("Show context"):
            ctx = _context_messages(messages, int(row["index"]), window=2)
            render_chat(ctx)

    # Export
    csv = fdf.drop(columns=["index"]).to_csv(index=False).encode("utf-8")
    st.download_button("Download decisions CSV", data=csv, file_name="decisions.csv", use_container_width=True)


# ----------------------------------------------------------
# Exports
# ----------------------------------------------------------
def exports(messages):
    st.download_button("Download messages JSON", data=json.dumps(messages, default=str, indent=2).encode("utf-8"),
                       file_name="messages.json")


# Main
# ----------------------------------------------------------
def main():
    render_professional_header()

    months = load_month_files()
    if not months:
        st.error("No JSON files in ./elyx_conversations.")
        return

    # Month picker
    month_labels = [m["label"] for m in months]
    sel_label = st.sidebar.selectbox("Month", month_labels, index=len(months) - 1)
    sel = next(m for m in months if m["label"] == sel_label)
    messages = sel["data"]
    ensure_message_ids(messages)

    # Sidebar
    total = len(messages);
    parsed = sum(1 for m in messages if parse_timestamp(m.get("timestamp", "")))
    st.sidebar.markdown(f"Messages: {total}  \n*Parsed timestamps:* {parsed}")

    # Filters
    senders = sorted({m.get("sender", "") for m in messages if m.get("sender")})
    sender_filter = st.sidebar.multiselect("Filter sender", options=senders, default=[])
    keyword = st.sidebar.text_input("Search keyword", value="")

    # Extended Sidebar – Member panel
    st.sidebar.markdown("---")
    st.sidebar.header("Member")
    st.sidebar.subheader("Rohan Patel")
    st.sidebar.caption("46 • Male • Singapore")
    st.sidebar.write("*Health Goals*")
    health_pattern = r"(heart disease|cardiovascular|cvd|blood pressure|bp|cholesterol|lipid|apob|diabetes|glucose|ogtt|obesity|weight|bmi|inflammation|hs-?crp)"

    all_msgs = []
    for mth in months:
        all_msgs.extend(mth["data"])

    exclude_pattern = r"(test|check|screen|rule out|monitor|diagnostic|possible|suspect|scan)"

    goal_candidates = []
    for m in all_msgs:
        text = (m.get("text", "") or "")
        sender = m.get("sender", "")
        if not text:
            continue

        if re.search(health_pattern, text, re.I):
            if is_team_sender(sender) and re.search(exclude_pattern, text, re.I):
                continue
            goal_candidates.append(text)

    extracted_terms = set()
    for g in goal_candidates:
        matches = re.findall(health_pattern, g, re.I)
        for m_ in matches:
            extracted_terms.add(m_.lower())
    if extracted_terms:
        for term in sorted(extracted_terms):
            st.sidebar.markdown(f"- {term.capitalize()}")
    else:
        st.sidebar.info("No explicit health goals detected in chats.")
    st.sidebar.divider()
    st.sidebar.write("*Success Metrics*")
    st.sidebar.markdown("ApoB / Lipids, BP, hs-CRP, Cognitive scores, Sleep (Garmin/Whoop), Stress (HRV)")
    st.sidebar.divider()

    def message_matches(m):
        if sender_filter and m.get("sender", "") not in sender_filter:
            return False
        if keyword and keyword.lower() not in (m.get("text", "") or "").lower():
            return False
        return True

    display_messages = [m for m in messages if message_matches(m)] if (sender_filter or keyword) else messages

    tabs = st.tabs(["💬 Chat", "🕸 Sankey", "🧭 Decisions", "⬇ Export"])

    with tabs[0]:
        st.subheader(f"Chat – {sel_label}")
        if not display_messages:
            st.info("No messages match filters.")
        else:
            render_chat(display_messages)

    with tabs[1]:
        render_sankey_rationale(messages)

    with tabs[2]:
        render_decisions_tab(messages)

    with tabs[3]:
        st.subheader("Export")
        exports(messages)


if __name__ == "__main__":
    main()