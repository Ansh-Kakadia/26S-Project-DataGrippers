import streamlit as st
import requests
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="player_persona")


def apply_table_styles():
    st.markdown("""
        <style>
            .league-table {
                width: 100%;
                border-collapse: collapse;
                font-family: monospace;
                font-size: 15px;
                border: 2px solid #333;
            }
            .league-table th {
                background-color: #f0f0f0;
                padding: 12px 16px;
                text-align: left;
                border: 1px solid #ccc;
                font-weight: bold;
                font-size: 15px;
            }
            .league-table td {
                padding: 14px 16px;
                border: 1px solid #ddd;
                vertical-align: middle;
            }
            .league-table tr:hover td {
                background-color: #f9f9f9;
            }
            .status-active { color: #2e7d32; font-weight: bold; }
            .status-pending { color: #c96a00; font-weight: bold; }
            .status-finished { color: #c61717; font-weight: bold; }
            .league-link {
                color: #1a56db;
                text-decoration: underline;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)


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


def fmt_date(raw):
    if not raw:
        return ""
    return raw.split(" ")[0] if isinstance(raw, str) else str(raw)


def show():
    apply_table_styles()
    st.title("Leagues")

    col1, col2 = st.columns([2, 3])
    with col1:
        season = st.text_input(
            "Season (year)", placeholder="e.g. 2026",
            label_visibility="collapsed",
        )
    with col2:
        search = st.text_input(
            "Search", placeholder="Search sport or league name...",
            label_visibility="collapsed",
        )

    leagues = fetch_leagues(season.strip() or None, search.strip() or None)

    rows_html = ""
    for l in leagues:
        status = l.get("status", "")
        status_class = {
            "Active": "status-active",
            "Pending": "status-pending",
            "Finished": "status-finished",
        }.get(status, "")
        reg_range = f"{fmt_date(l.get('registration_start'))} - {fmt_date(l.get('registration_end'))}"
        rows_html += f"""
        <tr>
            <td>{l.get('sport','')}</td>
            <td><span class="league-link">{l.get('league_name','')}</span></td>
            <td>{l.get('skill_level','')}</td>
            <td>{reg_range}</td>
            <td><span class="{status_class}">{status}</span></td>
            <td>{l.get('season','')}</td>
        </tr>
        """

    table_html = f"""
    <table class="league-table">
        <thead>
            <tr>
                <th>Sport</th>
                <th>League</th>
                <th>Skill</th>
                <th>Reg Start - End</th>
                <th>Status</th>
                <th>Season</th>
            </tr>
        </thead>
        <tbody>
            {rows_html if rows_html else '<tr><td colspan="6" style="text-align:center; padding:20px;">No leagues found.</td></tr>'}
        </tbody>
    </table>
    """
    st.html(table_html)


show()
