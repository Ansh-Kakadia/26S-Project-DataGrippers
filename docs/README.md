# HuskyLeague — User Guide

Intramural sports league management for Northeastern University.

## Starting the App

```bash
# Copy and configure environment
cp api/.env.template api/.env
# Edit api/.env: change DB_NAME=ngo_db → DB_NAME=HuskyLeague

# Start all services
docker compose up -d
```

| Service  | URL                    |
|----------|------------------------|
| Frontend | http://localhost:8501  |
| API      | http://localhost:4000  |
| MySQL    | localhost:3200         |

```bash
# Stop
docker compose down
```

After code changes, click **Always Rerun** in the browser (hot reload is active).

---

## Personas

### Player — Maya

A student who plays intramural soccer and volleyball to stay active and socialize. Wants a fast, clean interface to find leagues, check her schedule, and track personal stats without fighting broken navigation.

**What you can do:**
- Browse and search leagues by sport, skill level, and season
- Request to join a team or register as a free agent for auto-placement
- View a personalized schedule of upcoming games with times and venues
- Track personal stats across seasons (games played, wins, goals/points scored)
- Rate and review venues after games (field quality, lighting, parking)
- Receive notifications for schedule changes, cancellations, and score updates

**How to use:**
1. On the Home page, select **Player**
2. Use **Browse Leagues** to find and join a league
3. Check **My Schedule** for upcoming games
4. View **My Profile** to see stats and season history
5. Open **Notifications** to stay up to date on changes

---

### Team Captain / Coach — Allan

A senior who captains an intramural basketball team each semester. Needs reliable tools for roster management, score submission, and team communication — without the platform getting in the way.

**What you can do:**
- Create a new team and invite players by email/username or from the free agent pool
- Manage the roster: add, remove, or designate substitute players
- Submit game scores and flag disputed calls for admin review
- View team schedule, standings position, and head-to-head records
- Message teammates through a team bulletin board
- Request schedule changes or report conflicts to league administrators

**How to use:**
1. On the Home page, select **Team Captain**
2. Use **My Team** to build and manage your roster
3. After games, go to **Submit Score** to record results
4. Check **Standings** to see your position in the league
5. Use **Team Board** to send messages to your team

---

### League Administrator — Derrick

A campus recreation coordinator who oversees all intramural programming. Wants an admin experience that automates scheduling, centralizes dispute resolution, and keeps students happy.

**What you can do:**
- Create and configure seasons: sport, division tiers, roster limits, and rules
- Auto-generate round-robin or bracket schedules from team count and venue availability
- Assign and manage venue/time-slot allocations across concurrent leagues
- Resolve disputed scores and issue forfeits, warnings, or suspensions
- Remove or deactivate teams that drop mid-season and adjust schedules
- Push league-wide announcements for rules, cancellations, or policy changes

**How to use:**
1. On the Home page, select **League Admin**
2. Use **Manage Leagues** to create seasons and configure rules
3. Use **Schedule Builder** to auto-generate the game schedule
4. Open **Venues** to allocate time slots and avoid double-bookings
5. Go to **Disputes** to review and resolve flagged scores
6. Use **Announcements** to push communications to all participants

---

### Sports Analyst — Dr. Priya

Associate Director of Recreation Analytics. Needs real-time dashboards to replace the manual export-and-build-it-yourself workflow that currently eats days of prep time before every planning meeting.

**What you can do:**
- View participation trends across sports, semesters, and demographics
- Analyze venue utilization rates to identify under- or over-booked facilities
- Track forfeiture and no-show rates by sport, division, and time slot
- Compare competitive balance metrics (point differentials, standings spread) across divisions
- Monitor registration demand over time to forecast which leagues to expand or cut
- Generate end-of-season reports summarizing key metrics for budget and planning

**How to use:**
1. On the Home page, select **Sports Analyst**
2. Open **Participation Report** for trend data across sports and semesters
3. Open **Venue Report** for utilization analysis
4. Open **Team Report** for competitive balance and forfeit metrics
5. Use **Intramural Report** for a full end-of-season summary to export for planning
