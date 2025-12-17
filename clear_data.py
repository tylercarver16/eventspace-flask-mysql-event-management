import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="eventspace_db"
)
cursor = connection.cursor()

# Disable foreign key checks to avoid constraint issues while truncating
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

# Truncate the tables to clear data and reset auto-increment counters
cursor.execute("TRUNCATE TABLE bookings;")
cursor.execute("TRUNCATE TABLE clients;")
cursor.execute("TRUNCATE TABLE events;")
cursor.execute("TRUNCATE TABLE venues;")

# Re-enable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

# Commit changes and close connection
connection.commit()
cursor.close()
connection.close()

print("All data has been cleared and auto-increment counters have been reset.")
