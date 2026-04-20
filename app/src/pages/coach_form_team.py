import streamlit as st
import requests
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="coach_persona")


SKILL_LEVELS = ["Beginner", "Recreational", "Intermediate", "Competitive"]
ROLES = ["Player", "Asst. Coach", "Analyst"]
NUM_INVITE_ROWS = 4


def apply_styles():
    st.markdown("""
        <style>
            .invite-label {
                font-family: monospace;
                font-size: 15px;
                margin-bottom: 12px;
                color: #333;
            }
            div[data-testid="stTextInput"] label,
            div[data-testid="stSelectbox"] label {
                display: none;
            }
            div[data-testid="stButton"] {
                margin-top: 4px;
            }
        </style>
    """, unsafe_allow_html=True)


def fetch_leagues():
    try:
        r = requests.get(f"{API_BASE}/leagues", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def create_team(name, captain_id, league_id):
    try:
        r = requests.post(
            f"{API_BASE}/teams",
            json={"name": name, "captain_id": captain_id, "league_id": league_id},
            timeout=5,
        )
        if r.status_code in (200, 201):
            return r.json()
        st.error(f"Create team failed: {r.status_code} {r.text}")
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return None


def invite_member(team_id, player_id, role):
    try:
        r = requests.post(
            f"{API_BASE}/teams/{team_id}/members",
            json={"player_id": player_id, "role": role,
                  "join_method": "Invite", "status": "Inactive"},
            timeout=5,
        )
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def show():
    apply_styles()
    st.markdown("<h1 style='font-family:monospace; text-align:center;'>Form Team</h1>",
                unsafe_allow_html=True)

    captain_id = st.session_state.get("player_id")
    if not captain_id:
        st.warning("No player logged in. Return to Home.")
        return

    leagues = fetch_leagues()
    if not leagues:
        st.info("No leagues available.")
        return

    league_map = {
        f"{l.get('league_name','')} ({l.get('sport','')})": l["id"]
        for l in leagues
    }

    col_name, _ = st.columns([2, 5])
    with col_name:
        team_name = st.text_input("team_name", placeholder="Team Name",
                                  label_visibility="collapsed", key="team_name_input")

    col1, col2, col3, spacer, col4 = st.columns([2, 2, 2, 3, 2])
    with col1:
        league_label = st.selectbox("League", list(league_map.keys()),
                                    label_visibility="collapsed")
    with col2:
        st.selectbox("Skill Level", SKILL_LEVELS, label_visibility="collapsed",
                     key="skill_input")
    with col3:
        st.button("Upload Team Logo", use_container_width=True, disabled=True)
    with col4:
        finalize = st.button("Finalize", type="primary", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="invite-label">Invite Players (by player_id)</div>',
                unsafe_allow_html=True)

    if "invite_rows" not in st.session_state:
        st.session_state["invite_rows"] = [
            {"player_id": "", "role": ROLES[0]} for _ in range(NUM_INVITE_ROWS)
        ]

    for i, row in enumerate(st.session_state["invite_rows"]):
        c1, c2 = st.columns([4, 2])
        with c1:
            st.session_state["invite_rows"][i]["player_id"] = st.text_input(
                f"pid_{i}",
                value=row["player_id"],
                placeholder="Player ID",
                label_visibility="collapsed",
            )
        with c2:
            st.session_state["invite_rows"][i]["role"] = st.selectbox(
                f"role_{i}",
                ROLES,
                index=ROLES.index(row["role"]),
                label_visibility="collapsed",
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("+ Add Player"):
        st.session_state["invite_rows"].append({"player_id": "", "role": ROLES[0]})
        st.rerun()

    if finalize:
        if not team_name.strip():
            st.warning("Team name required.")
            return
        league_id = league_map[league_label]
        result = create_team(team_name.strip(), captain_id, league_id)
        if not result:
            return
        team_id = result.get("team_id")
        st.session_state["team_id"] = team_id

        invited = 0
        for row in st.session_state["invite_rows"]:
            pid = row["player_id"].strip()
            if not pid.isdigit():
                continue
            if invite_member(team_id, int(pid), row["role"]):
                invited += 1

        st.success(f"Team '{team_name}' created (id={team_id}). "
                   f"Invited {invited} player(s).")
        st.session_state["invite_rows"] = [
            {"player_id": "", "role": ROLES[0]} for _ in range(NUM_INVITE_ROWS)
        ]


show()
