import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="player_persona")


def fetch_leagues(season=None, search=None):
    try:
        params = {}
        if season:
            params["season"] = season
        if search:
            params["search"] = search
        r = requests.get(f"{API_BASE}/leagues", params=params, timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def fetch_free_agent_requests(league_id):
    try:
        r = requests.get(f"{API_BASE}/leagues/{league_id}/free-agents", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return []


def register_free_agent(league_id, player_id):
    try:
        r = requests.post(
            f"{API_BASE}/leagues/{league_id}/free-agents",
            json={"player_id": player_id},
            timeout=5,
        )
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def show():
    st.title("Leagues")

    col1, col2 = st.columns([2, 3])
    with col1:
        season = st.text_input("Season", placeholder="e.g. 2026",
                               label_visibility="collapsed")
    with col2:
        search = st.text_input("Search", placeholder="Search sport or league name...",
                               label_visibility="collapsed")

    leagues = fetch_leagues(season.strip() or None, search.strip() or None)

    if leagues:
        df = pd.DataFrame(leagues)
        df["Reg Window"] = (
            df["registration_start"].str.split(" ").str[0].fillna("")
            + " – "
            + df["registration_end"].str.split(" ").str[0].fillna("")
        )
        display = df[["sport", "league_name", "skill_level", "Reg Window", "status", "season"]].rename(
            columns={
                "sport": "Sport",
                "league_name": "League",
                "skill_level": "Skill",
                "status": "Status",
                "season": "Season",
            }
        )
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No leagues found.")

    st.divider()

    st.subheader("Register as Free Agent")
    st.caption("Select a league to post yourself as a free agent. A coach can then pick you up.")

    player_id = st.session_state.get("player_id")
    if not player_id:
        st.warning("No player logged in. Return to Home.")
        return

    league_options = {
        f"{l.get('league_name', '')} ({l.get('sport', '')}, {l.get('season', '')})": l.get("id")
        for l in leagues
    }

    if not league_options:
        st.write("No leagues available to register for.")
        return

    c1, c2 = st.columns([4, 2])
    with c1:
        selected_label = st.selectbox("League", list(league_options.keys()),
                                      label_visibility="collapsed")
    with c2:
        if st.button("Register as Free Agent", type="primary", use_container_width=True):
            target_id = league_options[selected_label]
            if register_free_agent(target_id, player_id):
                st.success(f"Request submitted for {selected_label}.")
                st.rerun()
            else:
                st.error("Request failed. You may already be registered.")

    selected_id = league_options.get(selected_label)
    if selected_id:
        fa_requests = fetch_free_agent_requests(selected_id)
        my_requests = [r for r in fa_requests if r.get("player_id") == player_id]
        if my_requests:
            req = my_requests[-1]
            status = req.get("status", "")
            req_date = (req.get("request_date") or "").split(" ")[0]
            st.info(f"Your request for this league: **{status}** · submitted {req_date}")


show()
