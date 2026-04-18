import streamlit as st
import requests
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="player_persona")


def apply_styles():
    st.markdown("""
        <style>
            .profile-badge {
                display: inline-flex;
                align-items: center;
                gap: 14px;
                font-family: monospace;
                font-size: 32px;
                font-weight: 600;
            }
            .profile-initials {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                border: 2px solid #333;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 20px;
                font-family: monospace;
            }
            .profile-role {
                font-family: monospace;
                font-size: 18px;
                color: #555;
                margin-left: 8px;
            }
            .season-card {
                border: 2px solid #333;
                margin-bottom: 20px;
                font-family: monospace;
            }
            .season-header {
                display: flex;
                gap: 40px;
                padding: 12px 16px;
                border-bottom: 2px solid #333;
                font-size: 16px;
                background-color: #f8f8f8;
            }
            .season-header span {
                font-weight: 500;
            }
            .stats-table {
                width: 100%;
                border-collapse: collapse;
                font-family: monospace;
                font-size: 14px;
            }
            .stats-table th {
                background-color: #f0f0f0;
                padding: 10px 14px;
                text-align: center;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            .stats-table td {
                padding: 12px 14px;
                text-align: center;
                border: 1px solid #ddd;
            }
        </style>
    """, unsafe_allow_html=True)


def fetch_player(player_id):
    try:
        r = requests.get(f"{API_BASE}/players/{player_id}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error fetching player: {e}")
    return None


def fetch_stats(player_id, season=None):
    try:
        params = {"season": season} if season else {}
        r = requests.get(f"{API_BASE}/players/{player_id}/stats",
                         params=params, timeout=5)
        if r.status_code == 200:
            return r.json() or {}
    except requests.RequestException as e:
        st.error(f"API error fetching stats: {e}")
    return {}


def show():
    apply_styles()

    player_id = st.session_state.get("player_id")
    if not player_id:
        st.warning("No player logged in. Return to Home.")
        return

    player = fetch_player(player_id)
    if not player:
        st.error("Player not found.")
        return

    first = player.get("first_name") or st.session_state.get("first_name", "")
    last = player.get("last_name", "")
    initials = (first[0] if first else "?").upper()
    full_name = f"{first} {last}".strip()

    col1, col2 = st.columns([3, 2])
    with col1:
        st.html(f"""
            <div style="display:flex; align-items:center; gap:14px;">
                <div class="profile-initials">{initials}</div>
                <span class="profile-badge" style="font-size:32px;">{full_name}</span>
            </div>
        """)
    with col2:
        st.markdown(
            f"<div class='profile-role'>{player.get('email','')} · "
            f"{player.get('university','')}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    season_input = st.text_input(
        "Filter stats by season (year, e.g. 2025). Leave blank for all seasons.",
        value="",
    )
    season = season_input.strip() or None
    stats = fetch_stats(player_id, season)

    label_map = [
        ("games_played", "Games Played"),
        ("total_points", "Total Points"),
        ("total_goals", "Total Goals"),
        ("total_assists", "Total Assists"),
        ("total_wins", "Total Wins"),
        ("games_attended", "Games Attended"),
    ]
    headers = "".join(f"<th>{label}</th>" for _, label in label_map)
    values = "".join(
        f"<td>{stats.get(key) if stats.get(key) is not None else 0}</td>"
        for key, _ in label_map
    )

    season_label = f"Season {season}" if season else "All Seasons"

    st.html(f"""
    <div class="season-card">
        <div class="season-header">
            <span>{season_label}</span>
            <span>Career Totals</span>
        </div>
        <table class="stats-table">
            <thead><tr>{headers}</tr></thead>
            <tbody><tr>{values}</tr></tbody>
        </table>
    </div>
    """)


show()
