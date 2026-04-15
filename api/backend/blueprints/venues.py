from flask import Blueprint, jsonify, current_app
from backend.db_connection import get_db
from mysql.connector import Error

venues = Blueprint("venues", __name__)


# 1. All venues
@venues.route("/venues", methods=["GET"])
def get_all_venues():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /venues")

        cursor.execute("SELECT * FROM Venue")
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} venues")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_venues: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# 2. Time slots for a venue
@venues.route("/venues/<int:venue_id>/timeslots", methods=["GET"])
def get_venue_timeslots(venue_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /venues/{venue_id}/timeslots")

        query = """SELECT vts.id, vts.slot_date, vts.slot_start_time,
                          vts.slot_end_time, vts.is_available,
                          l.league_name, l.sport
                   FROM Venue_Time_Slot vts
                   JOIN League l ON vts.league_id = l.id
                   WHERE vts.venue_id = %s
                   ORDER BY vts.slot_date, vts.slot_start_time"""

        cursor.execute(query, (venue_id,))
        results = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(results)} time slots for venue {venue_id}")
        return jsonify(results), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_venue_timeslots: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
