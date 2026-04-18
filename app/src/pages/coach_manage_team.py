import streamlit as st
import requests
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="coach_persona")


ROLES = ["Player", "Asst. Coach", "Analyst"]

STATUS_COLORS = {
    "Active": "#2e7d32",
    "Pending": "#888",
    "Inactive": "#c96a00",
    "Declined": "#c61717",
}


def apply_styles():
    st.markdown("""
        <style>
            div[data-testid="stTextInput"] label,
            div[data-testid="stSelectbox"] label,
            div[data-testid="stTextArea"] label { display: none; }
            .section-title { font-family:monospace; font-size:22px; font-weight:bold; margin-bottom:6px; }
            .th-players { display:grid; grid-template-columns:2fr 1.5fr 1.4fr 1.2fr 1.4fr; padding:10px 14px; font-family:monospace; font-size:14px; font-weight:bold; background:#f5f5f5; border:2px solid #333; }
            .th-msgs { display:grid; grid-template-columns:2fr 5fr 1.8fr; padding:10px 14px; font-family:monospace; font-size:14px; font-weight:bold; background:#f5f5f5; border:2px solid #333; }
            .cell { font-family:monospace; font-size:14px; display:flex; align-items:center; padding: 2px 0; min-height:38px; }
        </style>
    """, unsafe_allow_html=True)


def fetch_team(team_id):
    try:
        r = requests.get(f"{API_BASE}/teams/{team_id}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return None


def fetch_members(team_id):
    try:
        r = requests.get(f"{API_BASE}/teams/{team_id}/members", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def remove_member(team_id, member_id):
    try:
        r = requests.delete(f"{API_BASE}/teams/{team_id}/members/{member_id}", timeout=5)
        return r.status_code in (200, 204)
    except requests.RequestException:
        return False


def add_member(team_id, player_id, role):
    try:
        r = requests.post(
            f"{API_BASE}/teams/{team_id}/members",
            json={"player_id": player_id, "role": role,
                  "join_method": "Invite", "status": "Pending"},
            timeout=5,
        )
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def fetch_messages(team_id):
    try:
        r = requests.get(f"{API_BASE}/teams/{team_id}/messages", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def send_message(team_id, player_id, message):
    try:
        r = requests.post(
            f"{API_BASE}/teams/{team_id}/messages",
            json={"player_id": player_id, "message": message},
            timeout=5,
        )
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def status_cell_html(status):
    sc = STATUS_COLORS.get(status, "#333")
    return f'<span style="color:{sc};font-weight:bold;font-family:monospace;font-size:14px;">{status}</span>'


def show():
    apply_styles()

    team_id = st.session_state.get("team_id")
    player_id = st.session_state.get("player_id")
    if not team_id or not player_id:
        st.warning("No team/player in session. Return to Home.")
        return

    team = fetch_team(team_id)
    team_name = team.get("name", f"Team {team_id}") if team else f"Team {team_id}"

    st.markdown(f"<h1 style='font-family:monospace;'>{team_name}</h1>",
                unsafe_allow_html=True)

    # ================================================================
    # ROSTER
    # ================================================================
    st.markdown("<div class='section-title'>Manage Players</div>", unsafe_allow_html=True)
    members = fetch_members(team_id)

    st.html('<div class="th-players"><span>Name</span><span>Role</span>'
            '<span>Date Joined</span><span>Status</span><span>Action</span></div>')

    for m in members:
        full_name = f"{m.get('first_name','')} {m.get('last_name','')}".strip()
        date_joined = (m.get("date_joined") or "").split(" ")[0]
        cols = st.columns([2, 1.5, 1.4, 1.2, 1.4])
        with cols[0]:
            st.markdown(f'<div class="cell">{full_name}</div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="cell">{m.get("role","")}</div>',
                        unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="cell">{date_joined}</div>', unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f'<div class="cell">{status_cell_html(m.get("status",""))}</div>',
                        unsafe_allow_html=True)
        with cols[4]:
            if st.button("✕ Remove", key=f"rm_{m['id']}"):
                if remove_member(team_id, m["id"]):
                    st.success(f"Removed {full_name}")
                    st.rerun()
                else:
                    st.error("Remove failed.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ================================================================
    # INVITE PLAYER
    # ================================================================
    st.markdown("<div class='section-title'>Invite Player</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 3, 2])
    with c1:
        inv_pid = st.text_input("inv_pid", placeholder="Player ID",
                                label_visibility="collapsed", key="inv_pid")
    with c2:
        inv_role = st.selectbox("inv_role", ROLES, label_visibility="collapsed",
                                key="inv_role")
    with c3:
        if st.button("Send Invite", type="primary", use_container_width=True):
            if inv_pid.strip().isdigit():
                if add_member(team_id, int(inv_pid.strip()), inv_role):
                    st.success(f"Invited player {inv_pid}")
                    st.rerun()
                else:
                    st.error("Invite failed.")
            else:
                st.warning("Player ID must be numeric.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ================================================================
    # TEAM MESSAGES (replaces Trainings + Meetings)
    # ================================================================
    st.markdown("<div class='section-title'>Team Messages</div>",
                unsafe_allow_html=True)

    messages = fetch_messages(team_id)
    st.html('<div class="th-msgs"><span>From</span><span>Message</span>'
            '<span>Sent</span></div>')

    for msg in messages:
        sender = f"{msg.get('first_name','')} {msg.get('last_name','')}".strip()
        sent_at = (msg.get("sent_at") or "").replace("T", " ").split(".")[0]
        cols = st.columns([2, 5, 1.8])
        with cols[0]:
            st.markdown(f'<div class="cell">{sender}</div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="cell">{msg.get("message","")}</div>',
                        unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="cell">{sent_at}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Send Message</div>",
                unsafe_allow_html=True)
    new_msg = st.text_area("new_msg", placeholder="Write a message to your team…",
                           label_visibility="collapsed", key="new_msg", height=100)
    if st.button("Post Message", type="primary"):
        if new_msg.strip():
            if send_message(team_id, player_id, new_msg.strip()):
                st.success("Message sent.")
                st.rerun()
            else:
                st.error("Send failed.")
        else:
            st.warning("Message empty.")


show()
