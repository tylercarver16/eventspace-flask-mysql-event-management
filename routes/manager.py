from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.db import get_db_connection

bp = Blueprint('manager', __name__, url_prefix='/manager')

@bp.route('/')
def dashboard():
    return render_template('manager.html')

@bp.route('/bookings')
def view_bookings():
    filters = {
        "booking_id": request.args.get('booking_id', '').strip(),
        "client_name": request.args.get('client_name', '').strip(),
        "event_name": request.args.get('event_name', '').strip(),
        "event_type": request.args.get('event_type', '').strip(),
        "venue_name": request.args.get('venue_name', '').strip(),
        "event_date": request.args.get('event_date', '').strip(),
        "booking_date": request.args.get('booking_date', '').strip()
    }

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get total bookings count (before filtering)
    cursor.execute("SELECT COUNT(*) AS count FROM bookings")
    total_bookings = cursor.fetchone()['count']

    # Filtered query
    query = """
        SELECT 
            b.booking_id,
            b.booking_date,
            b.event_date,
            c.name AS client_name,
            c.email AS client_email,
            e.event_name,
            e.event_type,
            v.venue_name
        FROM bookings b
        JOIN clients c ON b.client_id = c.id
        JOIN events e ON b.event_id = e.event_id
        JOIN venues v ON b.venue_id = v.venue_id
        WHERE 1=1
    """
    params = []

    if filters["booking_id"]:
        query += " AND b.booking_id = %s"
        params.append(filters["booking_id"])

    if filters["client_name"]:
        query += " AND c.name LIKE %s"
        params.append(f"%{filters['client_name']}%")

    if filters["event_name"]:
        query += " AND e.event_name LIKE %s"
        params.append(f"%{filters['event_name']}%")

    if filters["event_type"]:
        query += " AND e.event_type LIKE %s"
        params.append(f"%{filters['event_type']}%")

    if filters["venue_name"]:
        query += " AND v.venue_name LIKE %s"
        params.append(f"%{filters['venue_name']}%")

    if filters["event_date"]:
        query += " AND b.event_date = %s"
        params.append(filters["event_date"])

    if filters["booking_date"]:
        query += " AND b.booking_date = %s"
        params.append(filters["booking_date"])

    query += " ORDER BY b.booking_id ASC"

    cursor.execute(query, params)
    bookings = cursor.fetchall()

    #convert dates
    from datetime import datetime
    for booking in bookings:
        if isinstance(booking['event_date'], str):
            booking['event_date'] = datetime.strptime(booking['event_date'], '%Y-%m-%d')
        if isinstance(booking['booking_date'], str):
            booking['booking_date'] = datetime.strptime(booking['booking_date'], '%Y-%m-%d')

    cursor.close()
    conn.close()

    return render_template('manager_bookings.html', bookings=bookings, filters=filters, total_bookings=total_bookings)


@bp.route('/venues/add', methods=['GET', 'POST'])
def add_venue():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        venue_name = request.form['venue_name']
        venue_adr = request.form['venue_adr']
        capacity = request.form['capacity']
        facilities = request.form['facilities']

        if not venue_name or not capacity or not venue_adr:
            flash('Please fill out all required fields.')
            return redirect(url_for('manager.add_venue'))

        cursor.execute("""
            INSERT INTO venues (venue_name, venue_adr, capacity, facilities)
            VALUES (%s, %s, %s, %s)
        """, (venue_name, venue_adr, capacity, facilities))
        conn.commit()

    cursor.execute("""
    SELECT v.venue_id, v.venue_name, v.venue_adr, v.capacity, v.facilities,
           COUNT(b.booking_id) AS booking_count
    FROM venues v
    LEFT JOIN bookings b ON v.venue_id = b.venue_id
    GROUP BY v.venue_id
    ORDER BY v.venue_id DESC
    """)
    venues = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('manager_add_venue.html', venues=venues)


@bp.route('/venues/delete/<int:venue_id>')
def delete_venue(venue_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # no deletion if there are bookings
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE venue_id = %s", (venue_id,))
    count = cursor.fetchone()[0]

    if count > 0:
        flash('Cannot delete venue: it has existing bookings.', 'danger')
    else:
        cursor.execute("DELETE FROM venues WHERE venue_id = %s", (venue_id,))
        conn.commit()
        flash('Venue deleted successfully.', 'success')

    cursor.close()
    conn.close()
    return redirect(url_for('manager.add_venue'))

@bp.route('/venues/edit/<int:venue_id>', methods=['GET', 'POST'])
def edit_venue(venue_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        venue_name = request.form['venue_name']
        venue_adr = request.form['venue_adr']
        capacity = request.form['capacity']
        facilities = request.form['facilities']

        cursor.execute("""
            UPDATE venues
            SET venue_name = %s, venue_adr = %s, capacity = %s, facilities = %s
            WHERE venue_id = %s
        """, (venue_name, venue_adr, capacity, facilities, venue_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Venue updated successfully!')
        return redirect(url_for('manager.add_venue'))

    cursor.execute("SELECT * FROM venues WHERE venue_id = %s", (venue_id,))
    venue = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('manager_edit_venue.html', venue=venue)


@bp.route('/bookings/edit/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("""
            SELECT 
                b.booking_id, b.booking_date, b.event_date,
                b.venue_id, b.client_id, b.event_id,
                c.name AS client_name, c.email AS client_email,
                e.event_name, e.event_type, e.description,
                v.venue_name
            FROM bookings b
            JOIN clients c ON b.client_id = c.id
            JOIN events e ON b.event_id = e.event_id
            JOIN venues v ON b.venue_id = v.venue_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        booking = cursor.fetchone()

        cursor.execute("SELECT venue_id, venue_name FROM venues")
        venues = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('manager_edit_bookings.html', booking=booking, venues=venues)

    data = request.form
    cursor.execute("UPDATE clients SET name = %s, email = %s WHERE id = %s",
                   (data['client_name'], data['client_email'], data['client_id']))
    cursor.execute("UPDATE events SET event_name = %s, event_type = %s, description = %s WHERE event_id = %s",
                   (data['event_name'], data['event_type'], data['description'], data['event_id']))
    cursor.execute("UPDATE bookings SET event_date = %s, venue_id = %s WHERE booking_id = %s",
                   (data['event_date'], data['venue_id'], booking_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Booking updated successfully.")
    return redirect(url_for('manager.view_bookings'))

@bp.route('/bookings/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT event_id FROM bookings WHERE booking_id = %s", (booking_id,))
    result = cursor.fetchone()
    event_id = result['event_id'] if result else None

    cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
    conn.commit()

    if event_id:
        cursor.execute("SELECT COUNT(*) AS count FROM bookings WHERE event_id = %s", (event_id,))
        count = cursor.fetchone()['count']

        if count == 0:
            cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
            conn.commit()

    cursor.close()
    conn.close()

    flash("Booking deleted successfully.")
    return redirect(url_for('manager.view_bookings'))
