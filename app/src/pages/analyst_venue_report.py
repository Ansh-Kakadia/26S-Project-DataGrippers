import streamlit as st
import requests
import plotly.graph_objects as go
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="analyst_persona")


CHART_COLOR = "#a8c8e8"
CHART_BG = "white"
FONT_MONO = "Courier New, monospace"
FONT_STYLE = dict(family=FONT_MONO, size=12, color="#111")

UNDER_THRESH = 30
OVER_THRESH = 70


def utilization_chart(venues, rates):
    colors = []
    for v in rates:
        if v < UNDER_THRESH:
            colors.append("#f4a261")
        elif v >= OVER_THRESH:
            colors.append("#c61717")
        else:
            colors.append(CHART_COLOR)
    fig = go.Figure(go.Bar(
        x=venues, y=rates,
        marker_color=colors,
        marker_line_color="#555",
        marker_line_width=1,
        text=[f"{v}%" for v in rates],
        textposition="outside",
        textfont=dict(family=FONT_MONO, size=11, color="#111"),
    ))
    fig.update_layout(
        title=dict(text="Venue Utilization", font=dict(family=FONT_MONO, size=14, color="#111"), x=0.44, xref="paper"),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        font=FONT_STYLE,
        margin=dict(l=40, r=20, t=50, b=60),
        height=320,
        yaxis=dict(ticksuffix="%", range=[0, 100], showgrid=True, gridcolor="#eee"),
        xaxis=dict(showgrid=False),
    )
    return fig


def rating_chart(labels, values, title):
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=CHART_COLOR,
        marker_line_color="#6699bb",
        marker_line_width=1,
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(family=FONT_MONO, size=14, color="#111"), x=0.4, xref="paper"),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        font=FONT_STYLE,
        margin=dict(l=40, r=20, t=50, b=40),
        height=260,
        yaxis=dict(showgrid=True, gridcolor="#eee", range=[0, 5]),
        xaxis=dict(showgrid=False),
    )
    return fig


def apply_styles():
    st.markdown("""
        <style>
            div[data-testid="stSelectbox"] label { display: none; }
            .util-summary {
                font-family: monospace;
                font-size: 15px;
                padding: 12px 0 4px 0;
            }
            .util-flags {
                font-family: monospace;
                font-size: 15px;
                line-height: 1.8;
            }
            .flag { font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)


def fetch_json(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error on {path}: {e}")
    return []


def show():
    apply_styles()

    st.markdown("<h2 style='font-family:monospace; margin-bottom:4px;'>Venue Report</h2>",
                unsafe_allow_html=True)

    util = fetch_json("/analytics/venues")
    venues_all = fetch_json("/venues")

    if not util:
        st.info("No venue utilization data available.")
        return

    venue_names = [row.get("name", "") for row in util]
    rates = []
    for row in util:
        total = int(row.get("total_slots") or 0)
        used = int(row.get("used_slots") or 0)
        rate = round((used / total) * 100) if total else 0
        rates.append(rate)

    fig = utilization_chart(venue_names, rates)
    st.plotly_chart(fig, use_container_width=True)

    avg = round(sum(rates) / len(rates)) if rates else 0
    under = [f"{n} ({v}%)" for n, v in zip(venue_names, rates) if v < UNDER_THRESH]
    over = [f"{n} ({v}%)" for n, v in zip(venue_names, rates) if v >= OVER_THRESH]

    st.html(f"""
    <div class="util-summary">Average Utilization Rate: {avg}%</div>
    <hr style="border:none; border-top:2px solid #333; margin:6px 0 10px 0;">
    <div class="util-flags">
        <div>Underutilized (&lt;{UNDER_THRESH}%): <span class="flag" style="color:#c96a00;">{', '.join(under) or 'None'}</span></div>
        <div>Overbooked (&ge;{OVER_THRESH}%): <span class="flag" style="color:#c61717;">{', '.join(over) or 'None'}</span></div>
    </div>
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family:monospace;'>Venue Reviews</h3>", unsafe_allow_html=True)

    if not venues_all:
        st.info("No venues available.")
        return

    name_to_id = {v["name"]: v["id"] for v in venues_all}
    selected_name = st.selectbox("Select venue", list(name_to_id.keys()),
                                 label_visibility="collapsed")
    selected_id = name_to_id[selected_name]

    reviews = fetch_json(f"/venues/{selected_id}/reviews")

    if not reviews:
        st.markdown(
            "<div style='font-family:monospace;color:#888;padding:8px;'>No reviews for this venue.</div>",
            unsafe_allow_html=True,
        )
        return

    def avg_field(key):
        vals = [r[key] for r in reviews if r.get(key) is not None]
        return round(sum(vals) / len(vals), 2) if vals else 0

    labels = ["Overall", "Field Quality", "Lighting", "Parking"]
    values = [
        avg_field("overall_rating"),
        avg_field("field_quality_rating"),
        avg_field("lighting_rating"),
        avg_field("parking_rating"),
    ]
    st.plotly_chart(
        rating_chart(labels, values, f"Average Ratings — {selected_name}"),
        use_container_width=True,
    )

    st.markdown(
        f"<div style='font-family:monospace;'>{len(reviews)} review(s)</div>",
        unsafe_allow_html=True,
    )
    for r in reviews[:10]:
        name = f"{r.get('first_name') or ''} {r.get('last_name') or ''}".strip() or "Anonymous"
        stars = "★" * int(r.get("overall_rating") or 0)
        date = (r.get("last_reviewed_date") or "").split(" ")[0]
        text = r.get("text") or ""
        st.html(f"""
        <div style="border:1px solid #ccc; border-radius:6px; padding:10px 14px;
                    margin-bottom:8px; font-family:monospace;">
            <div><b>{name}</b> <span style='color:#c96a00;'>{stars}</span>
                 <span style='color:#888; float:right;'>{date}</span></div>
            <div style="margin-top:6px;">{text}</div>
        </div>
        """)


show()
