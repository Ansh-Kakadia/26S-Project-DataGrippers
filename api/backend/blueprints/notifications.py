from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

notifications = Blueprint("analytics", __name__)


## Send league wide notification
@notifications.route("/notification", methods=["GET"])
def get_league_wide_notifications():
    cursor = get_db().cursor(dictionary=True)
    query = 'SELECT * FROM Notifications WHERE 1=1'
    
    try:
        current_app.logger.info("GET /notification")
        league_id = request.args.get("league_id")
        if league_id:
            query += f' AND league_id = {league_id}'
        else: 
            return jsonify({"error": "%s is required"}), 400
            
        cursor.execute(query, (league_id,))
        results = cursor.fetchall()
        
        current_app.logger.info(f'Retrieved {len(results)} data results for notifications')
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f'Database error in get_league_wide_notifications: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()    
    
