from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

leagues = Blueprint("leagues", __name__)


# 1. All leagues with optional filters
@leagues.route("/leagues", methods=["GET"])
def get_all_leagues():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /leagues")

        season = request.args.get("season")
        status = request.args.get("status")
        search = request.args.get("search")

        query = "SELECT * FROM League WHERE 1=1"
        params = []

        if season:
            query += " AND season = %s"
            params.append(season)
        if status:
            query += " AND status = %s"
            params.append(status)
        if search:
            query += " AND (sport LIKE %s OR league_name LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        cursor.execute(query, params)
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} leagues")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_leagues: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 2. Single league
@leagues.route("/leagues/<int:league_id>", methods=["GET"])
def get_league(league_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /leagues/{league_id}")

        cursor.execute("SELECT * FROM League WHERE id = %s", (league_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "League not found"}), 404

        current_app.logger.info(f"Retrieved league {league_id}")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_league: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 3. Update league settings
@leagues.route("/leagues/<int:league_id>", methods=["PUT"])
def update_league(league_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /leagues/{league_id}")

        data = request.get_json()

        cursor.execute("SELECT id FROM League WHERE id = %s", (league_id,))
        if not cursor.fetchone():
            return jsonify({"error": "League not found"}), 404

        allowed_fields = ["league_name", "sport", "roster_limit", "skill_level",
                          "registration_start", "registration_end", "rules",
                          "status", "schedule_type", "division_tier", "season"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(league_id)
        query = f"UPDATE League SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, params)
        get_db().commit()

        current_app.logger.info(f"Updated league {league_id}")
        return jsonify({"message": "League updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_league: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 4. Teams in a league
@leagues.route("/leagues/<int:league_id>/teams", methods=["GET"])
def get_league_teams(league_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /leagues/{league_id}/teams")

        query = """SELECT t.id, t.name, t.status,
                          p.first_name AS captain_first_name,
                          p.last_name AS captain_last_name
                   FROM Team t
                   JOIN Player p ON t.captain_id = p.id
                   WHERE t.league_id = %s"""

        cursor.execute(query, (league_id,))
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} teams for league {league_id}")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_league_teams: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 5. Disputes in a league
@leagues.route("/leagues/<int:league_id>/disputes", methods=["GET"])
def get_league_disputes(league_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /leagues/{league_id}/disputes")

        query = """SELECT d.id, d.dispute_type, d.status, d.description,
                          d.resolution, d.is_resolved,
                          ht.name AS home_team_name,
                          awt.name AS away_team_name,
                          st.name AS submitted_by_team_name,
                          gr.home_score, gr.away_score
                   FROM Dispute d
                   JOIN Game g ON d.game_id = g.id
                   JOIN Team ht ON g.home_team_id = ht.id
                   JOIN Team awt ON g.away_team_id = awt.id
                   JOIN Team st ON d.submitted_by_team_id = st.id
                   LEFT JOIN Game_Result gr ON g.id = gr.game_id
                   WHERE g.league_id = %s"""

        cursor.execute(query, (league_id,))
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} disputes for league {league_id}")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_league_disputes: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 6. Resolve a dispute (accept/reject)
@leagues.route("/leagues/disputes/<int:dispute_id>", methods=["PUT"])
def resolve_dispute(dispute_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /leagues/disputes/{dispute_id}")

        data = request.get_json()

        cursor.execute("SELECT id FROM Dispute WHERE id = %s", (dispute_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Dispute not found"}), 404

        status = data.get("status", "Resolved")
        resolution = data.get("resolution", "")
        is_resolved = data.get("is_resolved", True)

        query = """UPDATE Dispute
                   SET status = %s, resolution = %s, is_resolved = %s,
                       resolution_date = NOW()
                   WHERE id = %s"""
        cursor.execute(query, (status, resolution, is_resolved, dispute_id))
        get_db().commit()

        current_app.logger.info(f"Resolved dispute {dispute_id}")
        return jsonify({"message": "Dispute updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in resolve_dispute: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
