import streamlit as st
import requests
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="league_admin_persona")


def apply_styles():
    st.markdown("""
        <style>
            div[data-testid="stSelectbox"] label { display: none; }
            .dispute-card {
                border: 2px solid #333;
                border-radius: 12px;
                padding: 20px 24px;
                margin-bottom: 12px;
                background: #f9f9f9;
            }
            .dispute-title {
                font-family: monospace;
                font-size: 17px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            .dispute-line {
                font-family: monospace;
                font-size: 15px;
                margin-bottom: 4px;
            }
            .dispute-meta {
                font-family: monospace;
                font-size: 14px;
                color: #444;
            }
            .status-pill {
                display: inline-block;
                padding: 3px 10px;
                border-radius: 10px;
                font-family: monospace;
                font-size: 12px;
                font-weight: bold;
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


def fetch_disputes(league_id):
    try:
        r = requests.get(f"{API_BASE}/leagues/{league_id}/disputes", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def resolve_dispute(game_id, dispute_id, resolution):
    payload = {
        "status": "Resolved",
        "resolution": resolution,
        "is_resolved": True,
    }
    try:
        r = requests.put(
            f"{API_BASE}/games/{game_id}/disputes/{dispute_id}",
            json=payload, timeout=5,
        )
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def show():
    apply_styles()

    st.markdown("<h1 style='font-family:monospace; text-align:center;'>Manage Disputes</h1>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    leagues = fetch_leagues()
    if not leagues:
        st.info("No leagues available.")
        return

    league_map = {
        f"{l.get('league_name','')} ({l.get('sport','')})": l["id"]
        for l in leagues
    }

    lbl_col, sel_col, _ = st.columns([1.2, 2, 4])
    with lbl_col:
        st.markdown("<div style='font-family:monospace;font-size:20px;font-weight:bold;padding-top:6px;'>Select League</div>",
                    unsafe_allow_html=True)
    with sel_col:
        selected_label = st.selectbox("league_select", list(league_map.keys()),
                                      label_visibility="collapsed")
    league_id = league_map[selected_label]

    st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)

    disputes = fetch_disputes(league_id)

    if not disputes:
        st.markdown("<div style='font-family:monospace; color:#888; padding:20px;'>No disputes for this league.</div>",
                    unsafe_allow_html=True)
        return

    for d in disputes:
        did = d.get("id")
        gid = d.get("game_id")
        home = d.get("home_team_name", "")
        away = d.get("away_team_name", "")
        matchup = f"{home} vs {away}"
        submitted_by = d.get("submitted_by_team_name", "")
        dispute_type = d.get("dispute_type", "")
        description = d.get("description", "")
        status = d.get("status", "")
        resolution = d.get("resolution", "")
        home_score = d.get("home_score")
        away_score = d.get("away_score")
        score_line = (f"Score: {home_score} - {away_score}"
                      if home_score is not None and away_score is not None
                      else "Score: pending")

        status_color = {"Pending": "#c96a00", "Resolved": "#2e7d32"}.get(status, "#666")
        is_resolved = bool(d.get("is_resolved"))

        cols = st.columns([5, 2])
        with cols[0]:
            st.markdown(f"""
            <div class='dispute-card'>
                <div style='display:flex; justify-content:space-between;'>
                    <div>
                        <div class='dispute-title'>{matchup}</div>
                        <div class='dispute-line'>Type: {dispute_type}</div>
                        <div class='dispute-line'>{score_line}</div>
                        <div class='dispute-line'>Description: {description}</div>
                        {f"<div class='dispute-line'>Resolution: {resolution}</div>" if resolution else ""}
                    </div>
                    <div>
                        <div class='dispute-meta'>Submitted by: {submitted_by}</div>
                        <div class='dispute-meta'>
                            <span class='status-pill' style='background:{status_color}; color:white;'>{status}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            if not is_resolved:
                if st.button("Accept", key=f"acc_{did}", use_container_width=True):
                    if resolve_dispute(gid, did, "Accepted"):
                        st.success("Accepted.")
                        st.rerun()
                    else:
                        st.error("Failed.")
                if st.button("Reject", key=f"rej_{did}", use_container_width=True):
                    if resolve_dispute(gid, did, "Rejected"):
                        st.success("Rejected.")
                        st.rerun()
                    else:
                        st.error("Failed.")
            else:
                st.markdown("<div style='font-family:monospace; color:#2e7d32; padding:10px;'>Resolved</div>",
                            unsafe_allow_html=True)


show()
