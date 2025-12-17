import mysql.connector
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="eventspace_db"
)
cursor = connection.cursor()

def generate_email_from_name(name):
    parts = name.split()
    first = parts[0].lower()
    last = parts[-1].lower()
    email = f"{first}.{last}@example.com"
    return email

def generate_event_name(event_type):
    if event_type == "Social":
        templates = [
            f"{fake.first_name()}'s Birthday",
            "Family Reunion",
            "Anniversary Party",
            "Housewarming Party",
            "Friends Gathering"
        ]
    elif event_type == "Corporate":
        templates = [
            "Team Lunch",
            "Annual Meeting",
            "Product Launch",
            "Corporate Retreat",
            "Strategy Session"
        ]
    else:  # Other
        templates = [
            "Community Fair",
            "Local Festival",
            "Charity Gala",
            "Art Exhibition",
            "Open House"
        ]
    return random.choice(templates)

def generate_venue_name():
    adjectives = ["Grand", "Elegant", "Crystal", "Majestic", "Sunset", "Golden", "Royal", "Willow", "Silver", "Riverside"]
    nouns = ["Hall", "Pavilion", "Center", "Estate", "Lounge", "Banquet Hall", "Terrace", "Gardens", "Plaza", "Ballroom"]
    return f"The {random.choice(adjectives)} {random.choice(nouns)}"

def generate_facilities():
    options = [
        "Wi-Fi", "Projector", "Sound System", "Stage", "Lighting",
        "Catering Services", "Parking", "Accessible Entrance", "Private Bar",
        "Outdoor Area", "Restrooms", "Air Conditioning", "Dance Floor",
        "Security", "Chairs & Tables", "AV Equipment", "Lounge Area"
    ]
    return ', '.join(random.sample(options, k=random.randint(4, 7)))

# higher change of weekends
def generate_weighted_event_date():
    base_date = datetime.now() + timedelta(days=random.randint(1, 365))
    weekday = base_date.weekday()  # Monday = 0, Sunday = 6

    # 40% chance to push date forward to a weekend
    if random.random() < 0.4:
        if weekday < 5:
            weekend_offset = 5 - weekday if random.random() < 0.5 else 6 - weekday
            base_date += timedelta(days=weekend_offset)
    return base_date

clients = []
for _ in range(100):  # 100 clients
    name = fake.name()
    email = generate_email_from_name(name)
    created_at = datetime.now()
    clients.append((name, email, created_at))

cursor.executemany(
    "INSERT IGNORE INTO clients (name, email, created_at) VALUES (%s, %s, %s)",
    clients
)

allowed_event_types = ["Corporate", "Social", "Other"]

events = []
for _ in range(100): # 100 events
    event_type = random.choice(allowed_event_types)
    event_name = generate_event_name(event_type)
    event_date = generate_weighted_event_date().date()
    description = "This event is invite only."
    events.append((event_name, event_type, event_date, description))

cursor.executemany(
    "INSERT IGNORE INTO events (event_name, event_type, event_date, description) VALUES (%s, %s, %s, %s)",
    events
)

venues = [(generate_venue_name(), fake.address(), random.randint(50, 500), generate_facilities()) for _ in range(50)]
cursor.executemany(
    "INSERT IGNORE INTO venues (venue_name, venue_adr, capacity, facilities) VALUES (%s, %s, %s, %s)",
    venues
)

bookings = []
for _ in range(50000): # 50,000 bookings
    client_id = random.randint(1, 100)
    event_id = random.randint(1, 100)
    venue_id = random.randint(1, 50)
    
    booking_date = datetime.now() - timedelta(days=random.randint(1, 365))
    event_date = generate_weighted_event_date().date()

    bookings.append((booking_date.date(), event_date, client_id, venue_id, event_id))

cursor.executemany(
    "INSERT IGNORE INTO bookings (booking_date, event_date, client_id, venue_id, event_id) VALUES (%s, %s, %s, %s, %s)",
    bookings
)

connection.commit()
cursor.close()
connection.close()

print("Fake data has been added to the database.")