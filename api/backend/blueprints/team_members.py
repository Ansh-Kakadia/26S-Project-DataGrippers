from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

team_members = Blueprint("team_members", __name__)


# 1. Get members of a team
@team_members.route("/team-members/team/<int:team_id>", methods=["GET"])
def get_team_members(team_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /team-members/team/{team_id}")

        query = """SELECT tm.id, tm.date_joined, tm.designation, tm.status,
                          tm.role, tm.join_method,
                          p.id AS player_id, p.first_name, p.last_name, p.email
                   FROM Team_Membership tm
                   JOIN Player p ON tm.player_id = p.id
                   WHERE tm.team_id = %s"""

        cursor.execute(query, (team_id,))
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} members for team {team_id}")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_team_members: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 2. Add team member (invite)
@team_members.route("/team-members", methods=["POST"])
def add_team_member():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("POST /team-members")

        data = request.get_json()

        required = ["team_id", "player_id"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        query = """INSERT INTO Team_Membership
                       (team_id, player_id, role, join_method, status, date_joined)
                   VALUES (%s, %s, %s, %s, %s, NOW())"""
        cursor.execute(query, (data["team_id"], data["player_id"],
                               data.get("role", "Player"),
                               data.get("join_method", "Invite"),
                               data.get("status", "Active")))
        get_db().commit()

        current_app.logger.info(f"Added member with id {cursor.lastrowid}")
        return jsonify({"message": "Member added successfully",
                        "member_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"Database error in add_team_member: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 3. Update member (status, role, designation)
@team_members.route("/team-members/<int:member_id>", methods=["PUT"])
def update_team_member(member_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /team-members/{member_id}")

        data = request.get_json()

        cursor.execute("SELECT id FROM Team_Membership WHERE id = %s", (member_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Member not found"}), 404

        allowed_fields = ["status", "role", "designation"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(member_id)
        query = f"UPDATE Team_Membership SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, params)
        get_db().commit()

        current_app.logger.info(f"Updated member {member_id}")
        return jsonify({"message": "Member updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_team_member: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 4. Remove member
@team_members.route("/team-members/<int:member_id>", methods=["DELETE"])
def remove_team_member(member_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /team-members/{member_id}")

        cursor.execute("SELECT id FROM Team_Membership WHERE id = %s", (member_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Member not found"}), 404

        cursor.execute("DELETE FROM Team_Membership WHERE id = %s", (member_id,))
        get_db().commit()

        current_app.logger.info(f"Removed member {member_id}")
        return jsonify({"message": "Member removed successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in remove_team_member: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
