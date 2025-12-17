from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.db import get_db_connection
from datetime import date

bp = Blueprint('booking', __name__)

@bp.route('/venues')
def venues():
    name_filter = request.args.get('name', '').strip()
    capacity_filter = request.args.get('capacity', '').strip()
    date_filter = request.args.get('date', '').strip()
    facilities_filter = request.args.getlist('facilities')
    sort_by = request.args.get('sort_by', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT v.*, COUNT(b.booking_id) AS booking_count
        FROM venues v
        LEFT JOIN bookings b ON v.venue_id = b.venue_id
        WHERE 1=1
    """
    params = []

    if name_filter:
        query += " AND v.venue_name LIKE %s"
        params.append(f"%{name_filter}%")

    if capacity_filter.isdigit():
        query += " AND v.capacity >= %s"
        params.append(capacity_filter)

    if date_filter:
        query += """
            AND v.venue_id NOT IN (
                SELECT venue_id FROM bookings WHERE event_date = %s
            )
        """
        params.append(date_filter)

    for facility in facilities_filter:
        query += " AND v.facilities LIKE %s"
        params.append(f"%{facility}%")

    query += " GROUP BY v.venue_id"

    if sort_by == "popularity":
        query += " ORDER BY booking_count DESC"
    elif sort_by == "capacity":
        query += " ORDER BY v.capacity DESC"

    cursor.execute(query, params)
    venues = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('venues.html', venues=venues)


@bp.route('/book')
def book():
    selected_venue_id = request.args.get('venue_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT venue_id, venue_name, capacity FROM venues")
    venues = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('book.html', venues=venues, selected_venue_id=selected_venue_id)

@bp.route('/submit_booking', methods=['POST'])
def submit_booking():
    data = request.form
    client_name = data['client_name']
    contact_info = data['contact_info']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM clients WHERE name = %s AND email = %s", (client_name, contact_info))
    client = cursor.fetchone()

    if not client:
        cursor.execute("INSERT INTO clients (name, email) VALUES (%s, %s)", (client_name, contact_info))
        conn.commit()
        client_id = cursor.lastrowid
    else:
        client_id = client['id']

    cursor.execute("""
        INSERT INTO events (event_name, event_type, event_date, description)
        VALUES (%s, %s, %s, %s)
    """, (data['event_name'], data['event_type'], data['event_date'], data['description']))
    conn.commit()
    event_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO bookings (booking_date, event_date, client_id, venue_id, event_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (date.today(), data['event_date'], client_id, data['venue_id'], event_id))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Booking submitted successfully!')
    return redirect(url_for('main.home'))
