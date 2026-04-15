from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

players = Blueprint("players", __name__)


# 1. Get player details
@players.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /players/{player_id}")

        cursor.execute("SELECT * FROM Player WHERE id = %s", (player_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Player not found"}), 404

        current_app.logger.info(f"Retrieved player {player_id}")
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_player: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 2. Get notifications for a player
@players.route("/players/<int:player_id>/notifications", methods=["GET"])
def get_player_notifications(player_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        unread_only = request.args.get("unread_only", "false").lower() == "true"
        current_app.logger.info(
            f"GET /players/{player_id}/notifications?unread_only={unread_only}"
        )

        query = "SELECT * FROM Notification WHERE player_id = %s"
        params = [player_id]

        if unread_only:
            query += " AND NOT is_read"

        cursor.execute(query, params)
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} notifications")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(
            f"Database error in get_player_notifications: {e}"
        )
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
