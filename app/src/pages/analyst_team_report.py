import streamlit as st
import requests
import plotly.graph_objects as go
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="analyst_persona")


CHART_BG = "white"
FONT_MONO = "Courier New, monospace"
FONT_STYLE = dict(family=FONT_MONO, size=12, color="#111")

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def record_chart(record):
    fig = go.Figure(go.Bar(
        x=list(record.keys()),
        y=list(record.values()),
        marker_color=["#4a90c4", "#c61717"],
        marker_line_color="#555",
        marker_line_width=1,
        text=list(record.values()),
        textposition="outside",
        textfont=dict(family=FONT_MONO, size=13, color="#111"),
    ))
    fig.update_layout(
        title=dict(text="Season Record", font=dict(family=FONT_MONO, size=14, color="#111"), x=0.5, xref="paper"),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        font=FONT_STYLE,
        margin=dict(l=30, r=20, t=50, b=40),
        height=260,
        yaxis=dict(showgrid=True, gridcolor="#eee"),
        xaxis=dict(showgrid=False),
    )
    return fig


def scoring_chart(labels, scored, allowed):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=scored, name="Points Scored",
                             mode="lines+markers",
                             line=dict(color="#4a90c4", width=2),
                             marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=labels, y=allowed, name="Points Allowed",
                             mode="lines+markers",
                             line=dict(color="#c61717", width=2, dash="dash"),
                             marker=dict(size=5)))
    fig.update_layout(
        title=dict(text="Avg Points Scored vs Allowed",
                   font=dict(family=FONT_MONO, size=14, color="#111"),
                   x=0.5, xref="paper"),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        font=FONT_STYLE,
        margin=dict(l=40, r=20, t=50, b=40),
        height=280,
        legend=dict(font=dict(family=FONT_MONO, size=11, color="#111")),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#eee"),
    )
    return fig


def differential_chart(labels, diff):
    colors = ["#4a90c4" if d >= 0 else "#c61717" for d in diff]
    fig = go.Figure(go.Bar(x=labels, y=diff, marker_color=colors, marker_line_width=0))
    fig.add_hline(y=0, line_color="#333", line_width=1)
    fig.update_layout(
        title=dict(text="Point Differential per Month",
                   font=dict(family=FONT_MONO, size=14, color="#111"),
                   x=0.4, xref="paper"),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        font=FONT_STYLE,
        margin=dict(l=40, r=20, t=50, b=40),
        height=260,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#eee", zeroline=False),
    )
    return fig


def apply_styles():
    st.markdown("""
        <style>
            div[data-testid="stSelectbox"] label { display: none; }
            .kpi-row {
                display: flex;
                gap: 16px;
                margin-bottom: 16px;
            }
            .kpi-box {
                flex: 1;
                border: 1.5px solid #ccc;
                border-radius: 8px;
                padding: 14px 18px;
                font-family: monospace;
                background: #fafafa;
            }
            .kpi-value {
                font-size: 26px;
                font-weight: bold;
                color: #111;
            }
            .kpi-label {
                font-size: 13px;
                color: #555;
                margin-top: 2px;
            }
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


def align_by_month(scored_rows, allowed_rows):
    """Merge by (year, month) keys from analytics rows."""
    def key_for(row):
        # rows shape: {"YEAR(g.game_date)": y, "MONTH(g.game_date)": m, "AVG...": v}
        y = None
        m = None
        avg = None
        for k, v in row.items():
            if k.startswith("YEAR"):
                y = v
            elif k.startswith("MONTH"):
                m = v
            elif k.startswith("AVG"):
                avg = float(v) if v is not None else 0
        return (y, m), (avg or 0)

    scored_map = dict(key_for(r) for r in (scored_rows or []))
    allowed_map = dict(key_for(r) for r in (allowed_rows or []))
    keys = sorted(set(scored_map.keys()) | set(allowed_map.keys()))
    labels = []
    scored = []
    allowed = []
    for (y, m) in keys:
        if y is None or m is None:
            continue
        labels.append(f"{MONTH_LABELS[int(m)-1]} {int(y)}")
        scored.append(scored_map.get((y, m), 0))
        allowed.append(allowed_map.get((y, m), 0))
    return labels, scored, allowed


def show():
    apply_styles()
    st.markdown("<h2 style='font-family:monospace; margin-bottom:4px;'>Team Report</h2>",
                unsafe_allow_html=True)

    leagues = fetch_json("/leagues") or []
    if not leagues:
        st.info("No leagues available.")
        return

    league_map = {l.get("league_name", f"League {l['id']}"): l["id"] for l in leagues}
    c1, c2, _ = st.columns([2, 2, 4])
    with c1:
        selected_league_name = st.selectbox("league", list(league_map.keys()),
                                            label_visibility="collapsed")
    league_id = league_map[selected_league_name]

    teams = fetch_json(f"/leagues/{league_id}/teams") or []
    if not teams:
        st.info("No teams in this league.")
        return

    team_map = {t.get("name", f"Team {t['id']}"): t["id"] for t in teams}
    with c2:
        selected_team_name = st.selectbox("team", list(team_map.keys()),
                                          label_visibility="collapsed")
    team_id = team_map[selected_team_name]

    st.markdown("<hr style='margin:8px 0 16px 0;'>", unsafe_allow_html=True)

    standings = fetch_json(f"/leagues/{league_id}/standings") or []
    this_row = next((s for s in standings if s.get("team_id") == team_id),
                    {"wins": 0, "losses": 0, "rank": "-"})
    wins = int(this_row.get("wins") or 0)
    losses = int(this_row.get("losses") or 0)
    games = wins + losses
    win_pct = round((wins / games) * 100) if games else 0

    st.html(f"""
    <div class="kpi-row">
        <div class="kpi-box">
            <div class="kpi-value">{wins} - {losses}</div>
            <div class="kpi-label">Win / Loss Record</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{win_pct}%</div>
            <div class="kpi-label">Win Rate</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">#{this_row.get('rank', '-')}</div>
            <div class="kpi-label">Division Rank</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{games}</div>
            <div class="kpi-label">Games Played</div>
        </div>
    </div>
    """)

    scored = fetch_json(f"/analytics/{team_id}/pts-scored") or []
    allowed = fetch_json(f"/analytics/{team_id}/pts-allowed") or []
    labels, scored_vals, allowed_vals = align_by_month(scored, allowed)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(record_chart({"W": wins, "L": losses}), use_container_width=True)
    with col2:
        if labels:
            st.plotly_chart(scoring_chart(labels, scored_vals, allowed_vals),
                            use_container_width=True)
        else:
            st.info("No monthly scoring data yet.")

    if labels:
        diff = [round(s - a, 2) for s, a in zip(scored_vals, allowed_vals)]
        st.plotly_chart(differential_chart(labels, diff), use_container_width=True)


show()
