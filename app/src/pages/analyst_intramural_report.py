import streamlit as st
import requests
import plotly.graph_objects as go
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="analyst_persona")


CHART_COLOR = "#a8c8e8"
CHART_BG = "white"
FONT_MONO = "Courier New, monospace"


def bar_chart(x, y, title, y_tickformat=None):
    fig = go.Figure(go.Bar(
        x=x, y=y,
        marker_color=CHART_COLOR,
        marker_line_color="#6699bb",
        marker_line_width=1,
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(family=FONT_MONO, size=14, color="#111"), x=0.43, xref="paper"),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        font=dict(family=FONT_MONO, size=12, color="#111"),
        margin=dict(l=40, r=20, t=40, b=40),
        height=280,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#eee", tickformat=y_tickformat or ""),
    )
    return fig


def apply_styles():
    st.markdown("""
        <style>
            div[data-testid="stSelectbox"] label { display: none; }
            .report-table {
                width: 100%;
                border-collapse: collapse;
                font-family: monospace;
                font-size: 14px;
                border: 2px solid #333;
                margin-bottom: 16px;
            }
            .report-table th {
                border: 1px solid #555;
                padding: 8px 14px;
                text-align: center;
                background: #f5f5f5;
            }
            .report-table td {
                border: 1px solid #aaa;
                padding: 8px 14px;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)


def fetch_json(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params or {}, timeout=5)
        if r.status_code == 200:
            return r.json()
        st.warning(f"{path} → HTTP {r.status_code}")
    except requests.RequestException as e:
        st.error(f"API error on {path}: {e}")
    return []


def show():
    apply_styles()

    st.markdown(
        "<h2 style='font-family:monospace; margin-bottom:2px;'>Intramural Activity Report</h2>",
        unsafe_allow_html=True,
    )

    participation = fetch_json("/analytics/participation")
    demand = fetch_json("/analytics/demand")
    forfeits = fetch_json("/analytics/forfeits", params={"filter": "sport"})

    seasons = sorted({int(row["season"]) for row in participation if row.get("season") is not None}, reverse=True)
    if not seasons:
        st.info("No participation data yet.")
        return

    col_select, _ = st.columns([2, 5])
    with col_select:
        selected = st.selectbox("Season", seasons, label_visibility="collapsed")

    st.markdown(
        f"<div style='font-family:monospace; color:#555; margin-bottom:16px;'>Season {selected} Report</div>",
        unsafe_allow_html=True,
    )

    season_rows = [r for r in participation if int(r.get("season") or 0) == selected]

    rows_html = ""
    sports = []
    counts = []
    for r in season_rows:
        sport = r.get("sport", "")
        count = int(r.get("total_players") or 0)
        sports.append(sport)
        counts.append(count)
        rows_html += f"<tr><td>{sport}</td><td>{count}</td></tr>"

    st.html(f"""
    <table class="report-table">
        <thead>
            <tr><th colspan="2" style="text-align:left; padding:10px 14px;">Participation Overview</th></tr>
            <tr><th>Sport</th><th>Participants</th></tr>
        </thead>
        <tbody>{rows_html or '<tr><td colspan="2">No data.</td></tr>'}</tbody>
    </table>
    """)

    if sports:
        st.plotly_chart(
            bar_chart(sports, counts, "Total Participation per Sport"),
            use_container_width=True,
        )

    forfeit_sports = [r.get("sport", "") for r in forfeits]
    forfeit_rates = [round(float(r.get("forfeit_rate") or 0) * 100, 1) for r in forfeits]
    if forfeit_sports:
        st.plotly_chart(
            bar_chart(forfeit_sports, forfeit_rates,
                      "Forfeit Rate per Sport (%)", y_tickformat=".1f"),
            use_container_width=True,
        )

    demand_labels = [f"{r.get('sport','')} · {r.get('season','')}" for r in demand]
    demand_counts = [int(r.get("total_agent_requests") or 0) for r in demand]
    if demand_labels:
        st.plotly_chart(
            bar_chart(demand_labels, demand_counts,
                      "Free Agent Registration Demand"),
            use_container_width=True,
        )


show()
