from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

teams = Blueprint("teams", __name__)


# 1. Get team details
@teams.route("/teams/<int:team_id>", methods=["GET"])
def get_team(team_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /teams/{team_id}")

        query = """SELECT t.id, t.name, t.status,
                          p.first_name AS captain_first_name,
                          p.last_name AS captain_last_name,
                          l.league_name, l.sport
                   FROM Team t
                   JOIN Player p ON t.captain_id = p.id
                   JOIN League l ON t.league_id = l.id
                   WHERE t.id = %s"""

        cursor.execute(query, (team_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Team not found"}), 404

        current_app.logger.info(f"Retrieved team {team_id}")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_team: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 2. Create team
@teams.route("/teams", methods=["POST"])
def create_team():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /teams")

        data = request.get_json()

        required = ["name", "captain_id", "league_id"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        query = """INSERT INTO Team (name, status, captain_id, league_id)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (data["name"], data.get("status", "Active"),
                               data["captain_id"], data["league_id"]))
        get_db().commit()

        current_app.logger.info(f"Created team with id {cursor.lastrowid}")
        return jsonify({"message": "Team created successfully",
                        "team_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_team: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 3. Update team
@teams.route("/teams/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /teams/{team_id}")

        data = request.get_json()

        cursor.execute("SELECT id FROM Team WHERE id = %s", (team_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Team not found"}), 404

        allowed_fields = ["name", "status", "captain_id", "league_id"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(team_id)
        query = f"UPDATE Team SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, params)
        get_db().commit()

        current_app.logger.info(f"Updated team {team_id}")
        return jsonify({"message": "Team updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_team: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 4. Delete team
@teams.route("/teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /teams/{team_id}")

        cursor.execute("SELECT id FROM Team WHERE id = %s", (team_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Team not found"}), 404

        cursor.execute("DELETE FROM Team WHERE id = %s", (team_id,))
        get_db().commit()

        current_app.logger.info(f"Deleted team {team_id}")
        return jsonify({"message": "Team deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_team: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
