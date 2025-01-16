import sqlite3

# Connect to the database
conn = sqlite3.connect('university_info.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS info (
    topic TEXT PRIMARY KEY,
    details TEXT
)
''')

# Sample data to insert
sample_data = [
    ("admissions", "Admissions are open from January 10 to March 31. Apply online."),
    ("library", "The library is open 24/7 for students. Remember to bring your ID."),
    ("sports", "Our sports center offers yoga, swimming, and gym facilities. It's open from 6 AM to 10 PM."),
    ("scholarship", "Scholarship applications are open until March 15. Good luck!"),
    ("events", "The Spring Fest is on April 10. Don't miss it!"),
    ("parking", "Parking is available near the east gate. A valid parking permit is required."),
    ("courses", "Course registration for the Fall semester starts on April 1."),
    ("hostels", "Campus hostels provide comfortable accommodation. Contact the hostel office for booking.")
]

# Insert data into the table
for topic, details in sample_data:
    cursor.execute('INSERT OR REPLACE INTO info (topic, details) VALUES (?, ?)', (topic, details))

# Commit and close the connection
conn.commit()
conn.close()

print("Database populated successfully.")
