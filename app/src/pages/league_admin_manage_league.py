import streamlit as st
import requests
from datetime import datetime
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="league_admin_persona")


SPORTS = ["Volleyball", "Basketball", "Football", "Soccer", "Tennis",
          "Hockey", "Softball", "Baseball"]
SKILL_LEVELS = ["Beginner", "Recreational", "Intermediate", "Competitive"]
STATUSES = ["Pending", "Active", "Finished"]
ROSTER_OPTS = list(range(1, 101))


def apply_styles():
    st.markdown("""
        <style>
            div[data-testid="stTextInput"] label,
            div[data-testid="stSelectbox"] label {
                display: none;
            }
            .row-label {
                font-family: monospace;
                font-size: 15px;
                text-align: right;
                padding-top: 10px;
                padding-right: 8px;
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


def fetch_league_teams(league_id):
    try:
        r = requests.get(f"{API_BASE}/leagues/{league_id}/teams", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def update_league(league_id, payload):
    try:
        r = requests.put(f"{API_BASE}/leagues/{league_id}",
                         json=payload, timeout=5)
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def update_team_status(team_id, status):
    try:
        r = requests.put(f"{API_BASE}/teams/{team_id}",
                         json={"status": status}, timeout=5)
        return r.status_code in (200, 201)
    except requests.RequestException:
        return False


def delete_team(team_id):
    try:
        r = requests.delete(f"{API_BASE}/teams/{team_id}", timeout=5)
        return r.status_code in (200, 204)
    except requests.RequestException:
        return False


def fmt_date_for_input(raw):
    if not raw:
        return ""
    s = str(raw).split(" ")[0]
    for in_fmt, out_fmt in [
        ("%Y-%m-%d", "%m/%d/%Y"),
        ("%a, %d %b %Y %H:%M:%S GMT", "%m/%d/%Y"),
    ]:
        try:
            return datetime.strptime(s if in_fmt == "%Y-%m-%d" else str(raw)[:29], in_fmt).strftime(out_fmt)
        except ValueError:
            continue
    return s


def parse_date_to_iso(mmddyyyy):
    try:
        return datetime.strptime(mmddyyyy, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def pick_index(options, value, fallback=0):
    if value in options:
        return options.index(value)
    return fallback


def show():
    apply_styles()

    st.markdown("<h1 style='font-family:monospace; text-align:center;'>Manage League</h1>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    leagues = fetch_leagues()
    if not leagues:
        st.info("No leagues available.")
        return

    league_map = {
        f"{l.get('league_name','')} ({l.get('sport','')} — {l.get('season','')})": l
        for l in leagues
    }

    lbl_col, sel_col, _ = st.columns([1.2, 3, 2])
    with lbl_col:
        st.markdown("<div style='font-family:monospace;font-size:20px;font-weight:bold;padding-top:6px;'>Select League</div>",
                    unsafe_allow_html=True)
    with sel_col:
        selected_label = st.selectbox("league_select", list(league_map.keys()),
                                      label_visibility="collapsed")

    league = league_map[selected_label]
    league_id = league["id"]

    if st.session_state.get("_last_league_id") != league_id:
        st.session_state["_last_league_id"] = league_id
        st.session_state["season_start_val"] = fmt_date_for_input(league.get("registration_start"))
        st.session_state["season_end_val"] = fmt_date_for_input(league.get("registration_end"))

    st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    left, spacer, right = st.columns([5, 1, 6])

    with left:
        st.markdown("<div style='font-family:monospace;font-size:18px;font-weight:bold;margin-bottom:8px;'>League Configuration</div>",
                    unsafe_allow_html=True)
    with right:
        st.markdown("<div style='font-family:monospace;font-size:18px;font-weight:bold;margin-bottom:8px;'>Teams Configuration</div>",
                    unsafe_allow_html=True)

    # ---- LEFT: League Config ----
    with left:
        def row(label, widget_fn):
            la, lb = st.columns([2, 3])
            with la:
                st.markdown(f"<div class='row-label'>{label}</div>", unsafe_allow_html=True)
            with lb:
                return widget_fn()

        new_name = row("League Name", lambda: st.text_input(
            "league_name", value=league.get("league_name", ""),
            label_visibility="collapsed"))
        new_sport = row("Sport:", lambda: st.selectbox(
            "sport", SPORTS,
            index=pick_index(SPORTS, league.get("sport"), 0),
            label_visibility="collapsed"))
        new_roster = row("Roster Limit:", lambda: st.selectbox(
            "roster_limit", ROSTER_OPTS,
            index=pick_index(ROSTER_OPTS, league.get("roster_limit"), 9),
            label_visibility="collapsed"))
        new_skill = row("Skill Level", lambda: st.selectbox(
            "skill_level", SKILL_LEVELS,
            index=pick_index(SKILL_LEVELS, league.get("skill_level"), 0),
            label_visibility="collapsed"))
        new_status = row("Status:", lambda: st.selectbox(
            "status", STATUSES,
            index=pick_index(STATUSES, league.get("status"), 0),
            label_visibility="collapsed"))

        la, lb = st.columns([2, 3])
        with la:
            st.markdown("<div class='row-label'>Reg Start:</div>", unsafe_allow_html=True)
        with lb:
            new_start = st.text_input("season_start_input",
                                      value=st.session_state["season_start_val"],
                                      placeholder="MM/DD/YYYY",
                                      label_visibility="collapsed")

        la, lb = st.columns([2, 3])
        with la:
            st.markdown("<div class='row-label'>Reg End:</div>", unsafe_allow_html=True)
        with lb:
            new_end = st.text_input("season_end_input",
                                    value=st.session_state["season_end_val"],
                                    placeholder="MM/DD/YYYY",
                                    label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Save Config", type="primary"):
            payload = {
                "league_name": new_name,
                "sport": new_sport,
                "roster_limit": int(new_roster),
                "skill_level": new_skill,
                "status": new_status,
            }
            iso_start = parse_date_to_iso(new_start)
            iso_end = parse_date_to_iso(new_end)
            if iso_start:
                payload["registration_start"] = iso_start
            if iso_end:
                payload["registration_end"] = iso_end
            if update_league(league_id, payload):
                st.success("League updated.")
                st.rerun()
            else:
                st.error("Update failed.")

    # ---- RIGHT: Teams ----
    with right:
        teams = fetch_league_teams(league_id)
        if not teams:
            st.markdown("<div style='font-family:monospace; color:#888; padding:20px;'>No teams in this league.</div>",
                        unsafe_allow_html=True)
        else:
            header_cols = st.columns([2.5, 2, 3])
            with header_cols[0]:
                st.markdown("<div style='font-family:monospace;font-weight:bold;padding:8px;background:#f5f5f5;border:1px solid #bbb;'>Name</div>",
                            unsafe_allow_html=True)
            with header_cols[1]:
                st.markdown("<div style='font-family:monospace;font-weight:bold;padding:8px;background:#f5f5f5;border:1px solid #bbb;'>Status</div>",
                            unsafe_allow_html=True)
            with header_cols[2]:
                st.markdown("<div style='font-family:monospace;font-weight:bold;padding:8px;background:#f5f5f5;border:1px solid #bbb;'>Actions</div>",
                            unsafe_allow_html=True)

            for t in teams:
                tid = t["id"]
                status = t.get("status", "")
                status_color = {
                    "Active": "#2e7d32",
                    "Approved": "#2e7d32",
                    "Pending": "#aaa",
                    "Inactive": "#c96a00",
                    "Rejected": "#c61717",
                }.get(status, "#333")

                cols = st.columns([2.5, 2, 3])
                with cols[0]:
                    st.markdown(f"<div style='font-family:monospace;padding:10px;border:1px solid #ddd;'>{t.get('name','')}</div>",
                                unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"<div style='font-family:monospace;padding:10px;border:1px solid #ddd;color:{status_color};font-weight:bold;'>{status}</div>",
                                unsafe_allow_html=True)
                with cols[2]:
                    bc1, bc2, bc3 = st.columns(3)
                    if status == "Pending":
                        with bc1:
                            if st.button("Accept", key=f"acc_{tid}"):
                                if update_team_status(tid, "Active"):
                                    st.rerun()
                        with bc2:
                            if st.button("Reject", key=f"rej_{tid}"):
                                if update_team_status(tid, "Rejected"):
                                    st.rerun()
                    else:
                        with bc1:
                            if st.button("Remove", key=f"del_{tid}"):
                                if delete_team(tid):
                                    st.rerun()


show()
