from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

players = Blueprint("players", __name__)


# GET /players/<id> — player details
@players.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /players/{player_id}")
        cursor.execute("SELECT * FROM Player WHERE id = %s", (player_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Player not found"}), 404

        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_player: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# GET /players/<id>/schedule — personalized schedule of games with times and venues
@players.route("/players/<int:player_id>/schedule", methods=["GET"])
def get_player_schedule(player_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /players/{player_id}/schedule")

        query = """SELECT DISTINCT g.id AS game_id, g.game_time, g.game_date, g.status,
                          v.name AS venue_name, v.address AS venue_address,
                          ht.name AS home_team_name,
                          at.name AS away_team_name,
                          l.sport, l.league_name
                   FROM Game g
                   JOIN Venue v ON g.venue_id = v.id
                   JOIN Team ht ON g.home_team_id = ht.id
                   JOIN Team at ON g.away_team_id = at.id
                   JOIN League l ON g.league_id = l.id
                   JOIN Team_Membership tm ON (tm.team_id = g.home_team_id
                                               OR tm.team_id = g.away_team_id)
                   WHERE tm.player_id = %s
                   ORDER BY g.game_date, g.game_time"""
        cursor.execute(query, (player_id,))
        results = cursor.fetchall()

        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_player_schedule: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# GET /players/<id>/stats — aggregated personal stats
@players.route("/players/<int:player_id>/stats", methods=["GET"])
def get_player_stats(player_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /players/{player_id}/stats")
        season = request.args.get("season")

        query = """SELECT COUNT(pgs.game_id) AS games_played,
                          SUM(pgs.points) AS total_points,
                          SUM(pgs.goals_scored) AS total_goals,
                          SUM(pgs.assists) AS total_assists,
                          SUM(pgs.wins) AS total_wins,
                          SUM(pgs.attended) AS games_attended
                   FROM Player_Game_Stats pgs
                   JOIN Game g ON pgs.game_id = g.id
                   JOIN League l ON g.league_id = l.id
                   WHERE pgs.player_id = %s"""
        params = [player_id]

        if season:
            query += " AND l.season = %s"
            params.append(season)

        cursor.execute(query, params)
        result = cursor.fetchone()

        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_player_stats: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# GET /players/<id>/notifications — player's notifications
@players.route("/players/<int:player_id>/notifications", methods=["GET"])
def get_player_notifications(player_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        unread_only = request.args.get("unread_only", "false").lower() == "true"
        current_app.logger.info(f"GET /players/{player_id}/notifications?unread_only={unread_only}")

        query = "SELECT * FROM Notification WHERE player_id = %s"
        params = [player_id]

        if unread_only:
            query += " AND NOT is_read"

        query += " ORDER BY sent_at DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()

        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_player_notifications: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# DELETE /players/<id>/notifications — delete notifications
@players.route("/players/<int:player_id>/notifications", methods=["DELETE"])
def delete_player_notifications(player_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /players/{player_id}/notifications")

        notification_id = request.args.get("notification_id")

        if notification_id:
            cursor.execute("DELETE FROM Notification WHERE id = %s AND player_id = %s",
                           (notification_id, player_id))
        else:
            cursor.execute("DELETE FROM Notification WHERE player_id = %s", (player_id,))

        get_db().commit()
        return jsonify({"message": "Notifications deleted"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_player_notifications: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
