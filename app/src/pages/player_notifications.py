import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks, API_BASE
SideBarLinks(show_home=False, userAuthStatus="player_persona")


def fetch_notifications(player_id, unread_only=False):
    try:
        params = {"unread_only": "true"} if unread_only else {}
        r = requests.get(f"{API_BASE}/players/{player_id}/notifications",
                         params=params, timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        st.error(f"API error: {e}")
    return []


def show():
    player_id = st.session_state.get("player_id")
    if not player_id:
        st.warning("No player logged in. Return to Home.")
        return

    first = st.session_state.get("first_name", "")
    st.title(f"{first}'s Notifications" if first else "Notifications")

    unread_only = st.checkbox("Show unread only", value=False)
    notifications = fetch_notifications(player_id, unread_only)

    unread_count = sum(1 for n in notifications if not n.get("is_read"))
    if unread_count:
        st.caption(f"{unread_count} unread notification{'s' if unread_count != 1 else ''}")

    if not notifications:
        st.info("No notifications found.")
        return

    df = pd.DataFrame(notifications)
    df["Status"] = df["is_read"].apply(lambda x: "Read" if x else "New")
    df["Sent At"] = df["sent_at"].apply(
        lambda x: str(x)[:16].replace("T", " ") if x else ""
    )
    display = df[["Status", "message", "notification_type", "Sent At"]].rename(
        columns={"message": "Message", "notification_type": "Type"}
    )
    st.dataframe(display, use_container_width=True, hide_index=True)


show()
