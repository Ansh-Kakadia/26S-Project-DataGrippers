import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks, API_BASE
from Style import apply_bold_button_styles

st.set_page_config(layout='wide')
st.session_state['authenticated'] = False

SideBarLinks(show_home=True)
apply_bold_button_styles()

logger.info("Loading the Home page of the app")
st.title('Husky League')
st.write('#### Hi! Who would you like to log in as?')


def fetch(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException:
        pass
    return []


# ── Player ────────────────────────────────────────────────────────────────────
st.markdown("**Player**")
players = fetch("/players")
if players:
    player_options = {f"{p['first_name']} {p['last_name']} ({p['email']})": p for p in players}
    chosen_player = player_options[st.selectbox("Select a player", list(player_options.keys()))]
    if st.button("Log in as Player", type="primary", use_container_width=True):
        st.session_state.update({
            'authenticated': True,
            'role': 'player_persona',
            'first_name': chosen_player['first_name'],
            'player_id': chosen_player['id'],
        })
        logger.info(f"Logging in as Player id={chosen_player['id']}")
        st.switch_page('pages/player_browse_profile.py')
else:
    st.warning("Could not load players from the API.")

st.markdown("---")

# ── Coach ─────────────────────────────────────────────────────────────────────
st.markdown("**Coach (Team Captain)**")
teams = fetch("/teams")
if teams:
    team_options = {
        f"{t['name']} — {t['sport']} ({t['captain_first_name']} {t['captain_last_name']})": t
        for t in teams
    }
    chosen_team = team_options[st.selectbox("Select a team", list(team_options.keys()))]
    if st.button("Log in as Coach", type="primary", use_container_width=True):
        st.session_state.update({
            'authenticated': True,
            'role': 'coach_persona',
            'first_name': chosen_team['captain_first_name'],
            'player_id': chosen_team['captain_id'],
            'team_id': chosen_team['id'],
        })
        logger.info(f"Logging in as Coach, team id={chosen_team['id']}")
        st.switch_page('pages/coach_team_dashboard.py')
else:
    st.warning("Could not load teams from the API.")

st.markdown("---")

# ── League Admin ──────────────────────────────────────────────────────────────
st.markdown("**League Administrator**")
leagues = fetch("/leagues")
if leagues:
    league_options = {
        f"{l['league_name']} ({l['sport']}, {l['season']})": l
        for l in leagues
    }
    chosen_league = league_options[st.selectbox("Select a league", list(league_options.keys()))]
    if st.button("Log in as League Admin", type="primary", use_container_width=True):
        st.session_state.update({
            'authenticated': True,
            'role': 'league_admin_persona',
            'first_name': 'Admin',
            'league_id': chosen_league['id'],
        })
        logger.info(f"Logging in as League Admin, league id={chosen_league['id']}")
        st.switch_page('pages/league_admin_venue_schedule.py')
else:
    st.warning("Could not load leagues from the API.")

st.markdown("---")

# ── Analyst ───────────────────────────────────────────────────────────────────
st.markdown("**Sports Analyst**")
if st.button("Log in as Sports Analyst", type="primary", use_container_width=True):
    st.session_state.update({
        'authenticated': True,
        'role': 'analyst_persona',
        'first_name': 'Analyst',
        'analyst_id': 1,
    })
    logger.info("Logging in as Sports Analyst Persona")
    st.switch_page('pages/analyst_intramural_report.py')
