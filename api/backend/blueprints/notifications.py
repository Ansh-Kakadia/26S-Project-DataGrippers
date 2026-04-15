from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

notifications = Blueprint("notifications", __name__)


# 1. Get notifications for a league
@notifications.route("/notifications/league/<int:league_id>", methods=["GET"])
def get_league_notifications(league_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /notifications/league/{league_id}")

        query = "SELECT * FROM Notification WHERE league_id = %s ORDER BY sent_at DESC"
        cursor.execute(query, (league_id,))
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} notifications for league {league_id}")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_league_notifications: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 2. Mark notification as read
@notifications.route("/notifications/<int:notification_id>", methods=["PUT"])
def mark_notification_read(notification_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /notifications/{notification_id}")

        cursor.execute("SELECT id FROM Notification WHERE id = %s", (notification_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Notification not found"}), 404

        cursor.execute("UPDATE Notification SET is_read = TRUE WHERE id = %s", (notification_id,))
        get_db().commit()

        current_app.logger.info(f"Marked notification {notification_id} as read")
        return jsonify({"message": "Notification marked as read"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in mark_notification_read: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
