import streamlit as st
import requests
from datetime import date, datetime, timedelta
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="league_admin_persona")


HOURS = list(range(6, 22))
DAYS = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]


def apply_styles():
    st.markdown("""
        <style>
            .venue-table {
                width: 100%;
                border-collapse: collapse;
                font-family: monospace;
                font-size: 14px;
                border: 2px solid #333;
            }
            .venue-table th {
                border: 1.5px solid #555;
                padding: 10px 6px;
                text-align: center;
                background: #f5f5f5;
                font-weight: bold;
                font-size: 15px;
            }
            .venue-table td {
                border: 1px solid #bbb;
                padding: 8px 6px;
                vertical-align: top;
                min-width: 90px;
                min-height: 60px;
                height: 60px;
            }
            .time-cell {
                font-weight: bold;
                font-size: 15px;
                text-align: right;
                padding-right: 10px;
                white-space: nowrap;
                background: #fafafa;
                border-right: 2px solid #555 !important;
                width: 80px;
            }
            .court-chip {
                display: inline-block;
                border: 1.5px solid #555;
                border-radius: 4px;
                padding: 3px 8px;
                margin: 2px 5px 2px 0;
                font-size: 13px;
                font-family: monospace;
                background: white;
                white-space: nowrap;
            }
            .court-chip.unavailable {
                background: #ffe8e8;
                border-color: #c61717;
                color: #c61717;
            }
        </style>
    """, unsafe_allow_html=True)


def fetch_venues():
    try:
        r = requests.get(f"{API_BASE}/venues", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def fetch_timeslots(venue_id):
    try:
        r = requests.get(f"{API_BASE}/venues/{venue_id}/timeslots", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def get_week_start(d):
    return d - timedelta(days=d.weekday())


def fmt_hour(h):
    if h == 12:
        return "12:00pm"
    if h > 12:
        return f"{h-12}:00pm"
    return f"{h}:00am"

def parse_slot_datetime(raw):
    if not raw:
        return None
    try:
        return datetime.strptime(str(raw), "%a, %d %b %Y %H:%M:%S GMT")
    except ValueError:
        return None

def parse_slot_date(raw):
    dt = parse_slot_datetime(raw)
    return dt.date() if dt else None


def parse_slot_hour(raw):
    dt = parse_slot_datetime(raw)
    return dt.hour if dt else None


def show():
    apply_styles()

    st.markdown("<h1 style='font-family:monospace; text-align:center;'>Venue Schedule</h1>",
                unsafe_allow_html=True)

    if "week_offset" not in st.session_state:
        st.session_state["week_offset"] = 0

    venues = fetch_venues()
    if not venues:
        st.info("No venues available.")
        return

    venue_map = {v.get("name", f"Venue {v['id']}"): v["id"] for v in venues}

    col_label, col_select = st.columns([1, 3])
    with col_label:
        st.markdown("<div style='font-family:monospace; font-size:18px; font-weight:bold; padding-top:8px;'>Select Venue</div>",
                    unsafe_allow_html=True)
    with col_select:
        selected_name = st.selectbox("venue", list(venue_map.keys()),
                                     label_visibility="collapsed")
    venue_id = venue_map[selected_name]

    today = date.today()
    week_start = get_week_start(today) + timedelta(weeks=st.session_state["week_offset"])
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    week_label = f"Week of {week_start.strftime('%-m/%-d/%Y')}"

    # Build lookup: {date: {hour: [chip_text]}}
    slots = fetch_timeslots(venue_id)
    lookup = {}
    for s in slots:
        dt = parse_slot_datetime(s.get("slot_start_time"))
        if dt is None:
            continue
        d, h = dt.date(), dt.hour
        label = s.get("league_name") or s.get("sport") or f"Slot {s.get('id','')}"
        lookup.setdefault(d, {}).setdefault(h, []).append({
            "label": label,
            "available": bool(s.get("is_available", True)),
        })

    nav_col1, nav_col2, nav_col3 = st.columns([1, 8, 1])
    with nav_col1:
        if st.button("＜", use_container_width=True):
            st.session_state["week_offset"] -= 1
            st.rerun()
    with nav_col2:
        st.markdown(
            f"<div style='text-align:center; font-family:monospace; font-size:18px; font-weight:bold; padding-top:6px;'>{week_label}</div>",
            unsafe_allow_html=True,
        )
    with nav_col3:
        if st.button("＞", use_container_width=True):
            st.session_state["week_offset"] += 1
            st.rerun()

    header_cells = "<th style='width:80px;'></th>"
    for i, day in enumerate(DAYS):
        d = week_dates[i]
        header_cells += (f"<th>{day}<br><span style='font-weight:normal;font-size:12px;'>"
                         f"{d.strftime('%-m/%-d')}</span></th>")

    rows_html = ""
    for hour in HOURS:
        row = f"<td class='time-cell'>{fmt_hour(hour)}</td>"
        for i in range(7):
            d = week_dates[i]
            entries = lookup.get(d, {}).get(hour, [])
            if entries:
                chip_parts = []
                for e in entries:
                    cls = "court-chip" if e["available"] else "court-chip unavailable"
                    chip_parts.append(f"<div class='{cls}'>{e['label']}</div>")
                chips = "".join(chip_parts)
                row += f"<td>{chips}</td>"
            else:
                row += "<td></td>"
        rows_html += f"<tr>{row}</tr>"

    st.html(f"""
    <div style="overflow-x:auto;">
        <table class="venue-table">
            <thead><tr>{header_cells}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """)


show()
