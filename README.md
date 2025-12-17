# EventSpace  
**Web-Based Event Planning & Venue Management System**

EventSpace is a **database-driven web application** built with Flask and MySQL to streamline the process of planning and managing events. It provides both public-facing booking functionality and an administrative management interface, allowing users to browse venues, create bookings, manage events, and analyze historical booking trends.

The system was designed to reflect real-world event planning workflows and emphasizes **relational database design, data integrity, and practical analytics**.

---

## Key Features

### Event & Venue Management
- Create, view, update, and delete events, venues, clients, and bookings
- Prevent invalid operations using foreign key–aware logic (e.g., blocking deletion of venues with active bookings)
- Store venue details including capacity, location, and facilities

### Venue Discovery & Booking
- Browse venues with advanced filtering by:
  - Name
  - Minimum capacity
  - Facility keywords
  - Date availability (excluding already-booked venues)
- Sort venues by popularity (booking frequency) or capacity
- Submit bookings that automatically link clients, events, and venues

### Administrative Dashboard
- View and manage all bookings in a centralized interface
- Filter bookings across joined relational data:
  - Clients
  - Events
  - Venues
  - Booking and event dates
- Edit or delete bookings with safe cascading logic

### Smart Venue Booking Trend Analyzer (Advanced Feature)
- Analyzes **historical booking data** to identify booking frequency by weekday for each venue
- Uses SQL aggregation functions (`COUNT`, `DAYOFWEEK`) to compute trends
- Converts raw counts into percentage-based usage patterns
- Provides transparent, data-backed insights rather than probabilistic predictions

---

## Architecture Overview

EventSpace follows a **modular Flask architecture** using the application factory pattern.

### Backend
- Flask application factory (`create_app`)
- Blueprint-based routing for separation of concerns:
  - `main` – public pages
  - `booking` – venue discovery and booking workflow
  - `manager` – administrative tools
  - `predictor` – analytical features
- Parameterized SQL queries to prevent injection and maintain clarity

### Database Design
- Relational MySQL schema designed from an E-R model
- Core entities:
  - `clients`
  - `venues`
  - `events`
  - `bookings`
- Database normalized to **BCNF**
- Explicit foreign key constraints ensure referential integrity
- Aggregation and join queries support reporting and analytics

### Frontend
- Server-rendered HTML using Jinja2 templates
- Dynamic data passed from Flask routes to templates
- Structured layouts with reusable base templates

---

## Data Generation & Testing Utilities

- **`data_gen.py`**
  - Uses the Faker library to generate realistic test data
  - Populates the database with:
    - 100 clients
    - 100 events
    - 50 venues
    - 50,000+ bookings
  - Event dates are biased toward weekends to simulate real-world booking behavior

- **`clear_data.py`**
  - Truncates all tables safely
  - Temporarily disables foreign key checks
  - Resets auto-increment counters for repeatable testing

These utilities allow meaningful trend analysis and realistic demonstrations.

---

## Tech Stack

- **Backend:** Python, Flask  
- **Database:** MySQL  
- **Templating:** Jinja2  
- **Data Generation:** Faker  
- **Frontend:** HTML, CSS  
- **Architecture:** Flask application factory, Blueprints  

---

## Running Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m flask run
