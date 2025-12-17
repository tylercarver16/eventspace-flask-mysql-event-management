from flask import Blueprint, render_template, request
from utils.db import get_db_connection

bp = Blueprint('predictor', __name__, url_prefix='/predict')

@bp.route('/', methods=['GET'])
def show_weekday_trends():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # weekday booking frequency per venue
    cursor.execute("""
        SELECT 
            v.venue_id,
            v.venue_name,
            DAYOFWEEK(b.event_date) AS weekday,
            COUNT(*) AS bookings_on_day
        FROM venues v
        LEFT JOIN bookings b ON v.venue_id = b.venue_id
        GROUP BY v.venue_id, weekday
    """)
    
    raw_data = cursor.fetchall()
    cursor.close()
    conn.close()

    # map venue_id to booking counts per weekday
    venue_stats = {}
    for row in raw_data:
        venue_id = row['venue_id']
        venue_name = row['venue_name']
        weekday = row['weekday']
        count = row['bookings_on_day']

        if venue_id not in venue_stats:
            venue_stats[venue_id] = {
                'venue_name': venue_name,
                'weekday_counts': {i: 0 for i in range(1, 8)},
                'total': 0
            }

        venue_stats[venue_id]['weekday_counts'][weekday] += count
        venue_stats[venue_id]['total'] += count

    # counts to percentages
    venue_trends = []
    for stats in venue_stats.values():
        total = stats['total'] or 1  # divide by zero
        percentages = [
            int((stats['weekday_counts'][i] / total) * 100) for i in range(1, 8)
        ]
        venue_trends.append({
            'venue_name': stats['venue_name'],
            'percentages': percentages
        })

    return render_template('predict.html', venue_trends=venue_trends)
