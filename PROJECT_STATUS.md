# Project Status: HuskyLeague (DataGrippers)

**Course:** CS 3200 — Database Design (Spring 2026, Northeastern University)  
**Team:** DataGrippers  
**Last Updated:** 2026-04-20

---

## What This Is

A university intramural sports league management system. It supports four user roles — Player, Coach, League Admin, and Analyst — each with a dedicated UI persona. The system manages leagues, teams, games, venues, disputes, and analytics.

---

## Architecture

| Layer | Technology | Port |
|---|---|---|
| Frontend | Streamlit (Python) | 8501 |
| Backend API | Flask (Python) | 4000 |
| Database | MySQL 9 | 3200 |
| Deployment | Docker / docker-compose | — |

The three services run as Docker containers with hot-reload volumes for development.

---

## Database Schema (20 Tables)

**Core entities:** `League`, `Team`, `Player`, `Team_Membership`, `Venue`, `Venue_Time_Slot`  
**Game flow:** `Game`, `Game_Result`, `Score_Submission`, `Dispute`  
**Engagement:** `Player_Game_Stats`, `Analytics_Report`, `Venue_Review`, `Notification`, `Team_Message`, `Free_Agent_Request`

---

## API Blueprints

| Blueprint | Prefix | Key Capabilities |
|---|---|---|
| `leagues.py` | `/leagues` | CRUD, standings, free agents, disputes |
| `teams.py` | `/teams` | CRUD, schedule, head-to-head records |
| `team_members.py` | `/teams/<id>/members` | Roster management, role/designation updates |
| `games.py` | `/games` | Scheduling, score submission, dispute management |
| `players.py` | `/players` | Registration, profile, schedule, stats, notifications |
| `venues.py` | `/venues` | CRUD, time slots, reviews |
| `analytics.py` | `/analytics` | Participation, venue utilization, forfeit rates |
| `notifications.py` | `/notifications` | League-wide broadcast notifications |

---

## Frontend Pages (12 total)

**Player:** Browse Profile, Browse Leagues, Scheduled Games  
**Coach:** Team Dashboard, Manage Team, Form Team  
**League Admin:** Venue Schedule, Manage Leagues, Manage Disputes  
**Analyst:** Intramural Report, Venue Report, Team Report

---

## What's Working

- Full CRUD for leagues, teams, players, venues, and games
- Role-based navigation (session state controls which pages are visible)
- Standings calculation via SQL JOINs (wins, losses, points)
- Head-to-head records between teams
- Player stats aggregation (points, goals, assists, wins, attendance)
- Score submission and dispute workflow (submit → review → resolve)
- Free agent request flow (post → accept/reject)
- League-wide notification broadcast
- Venue reviews with multi-category ratings
- Analytics dashboard: participation trends, venue utilization, forfeit rates
- All SQL uses parameterized queries (no raw string injection)
- Docker-based local dev with live reload

---

## Known Gaps / Issues

### API Exists, No UI
These endpoints are fully implemented in the backend but no frontend page exposes them:

| Feature | Endpoint | Affected Persona |
|---|---|---|
| Register as free agent | `POST /leagues/<id>/free-agents` | Player |
| Submit game score | `POST /games/<id>/scores` | Coach |
| File a dispute | `POST /games/<id>/disputes` | Coach |
| View notifications | `GET /players/<id>/notifications` | Player |

### Cross-Persona Access (No Role Guards)
No page checks `st.session_state['role']` before rendering. Pages only check whether a specific key (e.g. `player_id`, `team_id`) exists in session state, meaning:
- A user who manually navigates to another persona's page will see it if the right session keys happen to be set
- Coach and Player both use `player_id` in session — logging in as one leaves stale state for the other
- All three league admin pages never validate `league_id` is set before making API calls
- **Fix:** each page should redirect to `Home.py` if `st.session_state.get("role")` does not match the expected persona

### Redundant / Broken
- **`role` vs `designation` mismatch:** `coach_form_team.py` sends `role` to the team members API; `coach_manage_team.py` sends `designation`. The API accepts both silently, masking the inconsistency.
- **`analyst_id` is dead state:** set to hardcoded `1` in session but never used by any API call.
- **"Upload Team Logo"** button in `coach_form_team.py` is disabled with no API backing it.

### Security
- **No real authentication.** Login is a persona selection dropdown — no passwords, no tokens.
- **No server-side authorization.** API endpoints do not check the caller's role; the frontend is the only access control layer.

### Data Integrity
- Some `Team_Membership.designation` fields should be `NOT NULL` but aren't constrained.
- Multi-step operations (e.g., schedule game + assign venue slot) are not wrapped in transactions, so partial failures can leave inconsistent state.
- No server-side input validation — API accepts wrong types silently (e.g., `roster_limit` as string vs integer).
- Score submission allows multiple players to submit conflicting scores with no auto-merge or majority logic.

### Performance
- No indexes on high-cardinality foreign key columns (`Game`, `Team_Membership`).
- Some dynamic query building uses f-strings in `leagues.py` — functional but fragile if filter parameters change.

### Stubs
- `ml_models/model01.py` is a placeholder; no real ML predictions are wired in.

---

## Sample Data (in DDL)

- **3 Leagues:** Fall Soccer (Beginner, 2025), Fall Basketball (Intermediate, 2025), Spring Volleyball (Advanced, 2026)
- **3 Teams:** Red Storm, Blue Thunder, Gold Spikers
- **5 Players** with memberships, game stats, and notifications
- **3 Venues** with time slots and reviews
- **3 Games** including one resolved dispute and one pending dispute

---

## Running Locally

```bash
# Start all containers
docker-compose up -d

# Access points
# App:  http://localhost:8501
# API:  http://localhost:4000
# DB:   mysql -h 127.0.0.1 -P 3200 -u root -p HuskyLeague
```

---

## Key File Locations

| What | Where |
|---|---|
| SQL schema + seed data | [database-files/01_HuskyLeague_DDL.sql](database-files/01_HuskyLeague_DDL.sql) |
| Flask app entry | [api/backend/rest_entry.py](api/backend/rest_entry.py) |
| API blueprints | [api/backend/blueprints/](api/backend/blueprints/) |
| Streamlit home / login | [app/src/Home.py](app/src/Home.py) |
| Navigation / RBAC | [app/src/modules/nav.py](app/src/modules/nav.py) |
| Frontend pages | [app/src/pages/](app/src/pages/) |
| Docker config | [docker-compose.yaml](docker-compose.yaml) |
