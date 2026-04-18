import streamlit as st
import requests
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="player_persona")


def apply_styles():
    st.markdown("""
        <style>
            .schedule-table {
                width: 100%;
                border-collapse: collapse;
                font-family: monospace;
                font-size: 15px;
                border: 2px solid #333;
            }
            .schedule-table th {
                background-color: #f0f0f0;
                padding: 12px 16px;
                text-align: left;
                border: 1px solid #ccc;
                font-weight: bold;
            }
            .schedule-table td {
                padding: 14px 16px;
                border: 1px solid #ddd;
            }
            .schedule-table tr:hover td {
                background-color: #f9f9f9;
            }
            .profile-badge {
                display: inline-flex;
                align-items: center;
                gap: 10px;
                font-family: monospace;
                font-size: 40px;
                font-weight: 600;
            }
            .profile-initials {
                width: 55px;
                height: 55px;
                border-radius: 50%;
                border: 2px solid #333;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 20px;
                font-family: monospace;
            }
        </style>
    """, unsafe_allow_html=True)


def fetch_schedule(player_id):
    try:
        r = requests.get(f"{API_BASE}/players/{player_id}/schedule", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def fmt_game_time(game_date, game_time):
    date_part = (game_date or "").split(" ")[0]
    time_part = (game_time or "").split(" ")[-1][:5] if game_time else ""
    return f"{date_part} {time_part}".strip()


def show():
    apply_styles()

    player_id = st.session_state.get("player_id")
    if not player_id:
        st.warning("No player logged in. Return to Home.")
        return

    col1, col2 = st.columns([3, 2])
    with col1:
        first = st.session_state.get("first_name", "Maya")
        initials = (first[0]).upper() if first else "M"
        st.html(f"""
            <div class="profile-badge">
                <span class="profile-initials">{initials}</span>
                <span>{first}</span>
            </div>
        """)
    with col2:
        st.markdown(
            "<h1 style='text-align:right; font-family:monospace;'>Schedule</h1>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["**Games**", "Trainings", "Meetings"])

    games = fetch_schedule(player_id)

    with tab1:
        if not games:
            st.markdown(
                "<div style='font-family:monospace;color:#888;padding:16px;'>"
                "No games scheduled.</div>",
                unsafe_allow_html=True,
            )
        else:
            rows_html = ""
            for g in games:
                rows_html += f"""
                <tr>
                    <td>{g.get('venue_name','')}</td>
                    <td>{g.get('home_team_name','')}</td>
                    <td>{g.get('away_team_name','')}</td>
                    <td>{fmt_game_time(g.get('game_date'), g.get('game_time'))}</td>
                    <td>{g.get('sport','')}</td>
                    <td>{g.get('status','')}</td>
                </tr>
                """
            st.html(f"""
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Location</th>
                        <th>Home</th>
                        <th>Away</th>
                        <th>Time</th>
                        <th>Sport</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """)

    with tab2:
        st.markdown(
            "<div style='font-family:monospace;color:#888;padding:16px;'>"
            "No trainings scheduled. Trainings are not tracked in the current system.</div>",
            unsafe_allow_html=True,
        )

    with tab3:
        st.markdown(
            "<div style='font-family:monospace;color:#888;padding:16px;'>"
            "No meetings scheduled. See team messages on your team page.</div>",
            unsafe_allow_html=True,
        )


show()
