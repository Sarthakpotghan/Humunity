#!/usr/bin/env python3
"""
Quick fix: Update NGO user coordinates in SQLite database.
"""

import sqlite3

DB_PATH = "humunity.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check current NGO users
cursor.execute("SELECT id, name, email, lat, lng, role FROM users WHERE role = 'ngo'")
ngos = cursor.fetchall()

print("Current NGO users:")
for ngo in ngos:
    print(f"  ID: {ngo[0]}, Name: {ngo[1]}, Email: {ngo[2]}, Lat: {ngo[3]}, Lng: {ngo[4]}")

# Update NGO coordinates to Pune center
PUNE_LAT = 18.5204
PUNE_LNG = 73.8567

cursor.execute(
    "UPDATE users SET lat = ?, lng = ? WHERE role = 'NGO' AND (lat IS NULL OR lng IS NULL)",
    (PUNE_LAT, PUNE_LNG)
)

rows_updated = cursor.rowcount
conn.commit()
conn.close()

print(f"\nSuccessfully updated {rows_updated} NGO user(s) with coordinates:")
print(f"  lat = {PUNE_LAT}, lng = {PUNE_LNG}")