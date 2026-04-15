from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

player = Blueprint("analytics", __name__)


## Send league wide notification
@player.route("/player/notifications", methods=["GET"])
def get_unread_player_notifications():
    cursor = get_db().cursor(dictionary=True)
    query = 'SELECT * FROM Notifications WHERE is_read = False'
    
    try:
        current_app.logger.info("GET /player/notifications")
        player_id = request.args.get("player_id")
        if player_id:
            query += f' AND player_id = {player_id}'
        else: 
            return jsonify({"error": "%s is required"}), 400
            
        cursor.execute(query, (player_id,))
        results = cursor.fetchall()
        
        current_app.logger.info(f'Retrieved {len(results)} data results for notifications')
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f'Database error in get_unread_player_notifications: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()    
    
