import streamlit as st
import requests
from datetime import datetime
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="coach_persona")

DISPUTE_TYPES = ["Score Dispute", "Other"]


def apply_styles():
    st.markdown("""
        <style>
            .dash-label {
                font-family: monospace;
                font-size: 14px;
                color: #555;
                margin-bottom: 6px;
            }
            .game-card {
                border: 1.5px solid #ccc;
                padding: 14px 18px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: monospace;
            }
            .game-card:last-child { margin-bottom: 0; }
            .game-matchup { font-size: 18px; font-weight: bold; }
            .game-date { font-size: 16px; color: #444; }
            .standings-table {
                width: 100%;
                border-collapse: collapse;
                font-family: monospace;
                font-size: 14px;
            }
            .standings-table th {
                border: 1.5px solid #ccc;
                padding: 8px 12px;
                text-align: center;
                font-weight: bold;
                background: #f5f5f5;
            }
            .standings-table td {
                border: 1.5px solid #ccc;
                padding: 8px 12px;
                text-align: center;
            }
            .standings-table tr.my-team td {
                font-weight: bold;
                background: #fff8f8;
            }
            .h2h-box {
                border: 2px solid #333;
                padding: 24px 20px;
                font-family: monospace;
            }
            .h2h-title {
                font-size: 26px;
                font-weight: bold;
                text-align: center;
                font-family: monospace;
                margin-bottom: 18px;
            }
            .h2h-scores {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin: 20px 0;
            }
            .h2h-team-box {
                border: 2.5px solid #333;
                border-radius: 16px;
                padding: 20px 40px;
                text-align: center;
                font-family: monospace;
                min-width: 160px;
            }
            .h2h-team-name { font-weight: bold; font-size: 18px; }
            .h2h-wins { font-size: 15px; margin-top: 4px; }
            .h2h-dash { font-size: 24px; color: #333; }
            .h2h-history-box {
                border: 1.5px solid #ccc;
                margin-top: 16px;
                max-height: 240px;
                overflow-y: auto;
            }
            .h2h-row {
                display: flex;
                justify-content: center;
                gap: 60px;
                padding: 12px 20px;
                border-bottom: 1px solid #eee;
                font-family: monospace;
                font-size: 15px;
            }
            .h2h-row:last-child { border-bottom: none; }
            .win  { color: #2e7d32; font-weight: bold; }
            .loss { color: #c61717; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)


def fetch_json(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error on {path}: {e}")
    return None


def fmt_game_date(raw):
    if not raw:
        return ""
    s = str(raw).split(" ")[0]
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        day = d.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return d.strftime(f"%a, %b {day}{suffix}")
    except ValueError:
        return s


def submit_score(game_id, player_id, home_score, away_score):
    try:
        r = requests.post(
            f"{API_BASE}/games/{game_id}/scores",
            json={"player_id": player_id, "home_score": home_score,
                  "away_score": away_score, "status": "Pending"},
            timeout=5,
        )
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def file_dispute(game_id, team_id, dispute_type, description):
    try:
        r = requests.post(
            f"{API_BASE}/games/{game_id}/disputes",
            json={"submitted_by_team_id": team_id,
                  "dispute_type": dispute_type,
                  "description": description},
            timeout=5,
        )
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def show():
    apply_styles()

    team_id = st.session_state.get("team_id")
    if not team_id:
        st.warning("No team in session. Return to Home.")
        return

    team = fetch_json(f"/teams/{team_id}")
    if not team:
        st.error("Team not found.")
        return

    team_name = team.get("name", f"Team {team_id}")
    league_id = team.get("league_id")

    st.markdown(f"<h1 style='font-family:monospace; text-align:center;'>{team_name}</h1>",
                unsafe_allow_html=True)

    # ---- Upcoming Games ----
    st.markdown('<div class="dash-label">Upcoming Games</div>', unsafe_allow_html=True)
    games = fetch_json(f"/teams/{team_id}/schedule?status=Scheduled") or []
    if not games:
        games = fetch_json(f"/teams/{team_id}/schedule") or []

    if not games:
        st.html('<div style="border:2px solid #333; padding:12px; font-family:monospace; color:#888;">'
                'No upcoming games.</div>')
    else:
        games_html = ""
        for g in games[:5]:
            home = g.get("home_team_name", "")
            away = g.get("away_team_name", "")
            opp = away if home == team_name else home
            games_html += f"""
            <div class="game-card">
                <span class="game-matchup">{team_name} vs. {opp}</span>
                <span class="game-date">{fmt_game_date(g.get('game_date'))}</span>
            </div>"""
        st.html(f'<div style="border:2px solid #333; padding:12px;">{games_html}</div>')

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Division Standings ----
    st.markdown('<div class="dash-label">Division Standings</div>', unsafe_allow_html=True)
    standings = fetch_json(f"/leagues/{league_id}/standings") or []
    if not standings:
        st.html('<div style="border:2px solid #333; padding:12px; font-family:monospace; color:#888;">'
                'No standings available.</div>')
    else:
        rows = ""
        for s in standings:
            row_class = "my-team" if s.get("team_id") == team_id else ""
            rows += (f"<tr class='{row_class}'><td>{s.get('rank','')}</td>"
                     f"<td>{s.get('team_name','')}</td>"
                     f"<td>{s.get('wins',0)}</td>"
                     f"<td>{s.get('losses',0)}</td></tr>")
        st.html(f"""
        <div style="border:2px solid #333; padding:12px;">
            <table class="standings-table">
                <thead><tr><th>Rank</th><th>Team</th><th>W</th><th>L</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Head-to-Head ----
    opponents = team.get("head_to_head") or []
    opp_map = {o.get("opponent_name", f"Team {o['opponent_id']}"): o["opponent_id"]
               for o in opponents if o.get("opponent_id")}

    if not opp_map:
        st.html('<div class="h2h-box"><div class="h2h-title">Head-to-Head</div>'
                '<div style="text-align:center; color:#888;">No opponent history yet.</div></div>')
        return

    selected_name = st.selectbox("Opponent", list(opp_map.keys()),
                                 label_visibility="collapsed")
    opp_id = opp_map[selected_name]
    h2h = fetch_json(f"/teams/{team_id}/h2h/{opp_id}") or {
        "my_wins": 0, "their_wins": 0, "history": [],
    }

    history_rows = ""
    for game in h2h.get("history", []):
        result = game.get("result", "")
        cls = "win" if result == "W" else "loss"
        my_score = game.get("my_score", 0)
        opp_score = game.get("opp_score", 0)
        game_date = fmt_game_date(game.get("game_date"))
        label = f"{result} {my_score} - {opp_score}"
        history_rows += f"""
        <div class="h2h-row">
            <span>{game_date}</span>
            <span class="{cls}">{label}</span>
        </div>"""

    if not history_rows:
        history_rows = ('<div style="padding:20px; text-align:center; color:#888;">'
                        'No prior games.</div>')

    st.html(f"""
    <div class="h2h-box">
        <div class="h2h-title">Head-to-Head</div>
        <div class="h2h-scores">
            <div class="h2h-team-box">
                <div class="h2h-team-name">{team_name}</div>
                <div class="h2h-wins">{h2h.get('my_wins',0)} Wins</div>
            </div>
            <span class="h2h-dash">—</span>
            <div class="h2h-team-box">
                <div class="h2h-team-name">{selected_name}</div>
                <div class="h2h-wins">{h2h.get('their_wins',0)} Wins</div>
            </div>
        </div>
        <div class="h2h-history-box">{history_rows}</div>
    </div>
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # ================================================================
    # BUILD GAME SELECTOR (shared by submit score + file dispute)
    # ================================================================
    all_games = fetch_json(f"/teams/{team_id}/schedule") or []
    player_id = st.session_state.get("player_id")

    if all_games:
        game_options = {
            f"#{g['game_id']} — {g.get('home_team_name','')} vs {g.get('away_team_name','')} "
            f"({(g.get('game_date') or '').split(' ')[0]})": g["game_id"]
            for g in all_games
            if "game_id" in g
        }
    else:
        game_options = {}

    # ================================================================
    # SUBMIT SCORE
    # ================================================================
    st.subheader("Submit Score")

    if not game_options:
        st.write("No games found for this team.")
    else:
        score_game_label = st.selectbox("Game", list(game_options.keys()),
                                        key="score_game_select")
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            home_score = st.number_input("Home Score", min_value=0, value=0,
                                         key="home_score_input")
        with c2:
            away_score = st.number_input("Away Score", min_value=0, value=0,
                                         key="away_score_input")
        with c3:
            st.write("")
            if st.button("Submit Score", type="primary", use_container_width=True):
                if not player_id:
                    st.error("No player in session.")
                else:
                    gid = game_options[score_game_label]
                    if submit_score(gid, player_id, int(home_score), int(away_score)):
                        st.success(f"Score submitted for game #{gid}.")
                    else:
                        st.error("Submission failed.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ================================================================
    # FILE DISPUTE
    # ================================================================
    st.subheader("File a Dispute")

    if not game_options:
        st.write("No games found for this team.")
    else:
        d1, d2 = st.columns([4, 2])
        with d1:
            dispute_game_label = st.selectbox("Game", list(game_options.keys()),
                                              key="dispute_game_select")
        with d2:
            dispute_type = st.selectbox("Type", DISPUTE_TYPES, key="dispute_type_select")
        dispute_desc = st.text_area(
            "Description",
            placeholder="Describe the issue clearly (e.g. incorrect score recorded, player misconduct)…",
            key="dispute_desc_input", height=100,
        )
        if st.button("File Dispute", type="primary"):
            if not dispute_desc.strip():
                st.warning("Please enter a description.")
            else:
                gid = game_options[dispute_game_label]
                if file_dispute(gid, team_id, dispute_type, dispute_desc.strip()):
                    st.success(f"Dispute filed for game #{gid}.")
                    st.rerun()
                else:
                    st.error("Dispute submission failed.")


show()
