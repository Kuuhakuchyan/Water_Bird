import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Check what 0005 migration is supposed to do
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='app_monitor_aidetectionresult'")
row = cur.fetchone()
print("=== app_monitor_aidetectionresult ===")
print(row[0] if row else "NOT FOUND")

# Check UserProfile schema
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='app_monitor_userprofile'")
row = cur.fetchone()
print("\n=== app_monitor_userprofile ===")
print(row[0] if row else "NOT FOUND")

# Check ObservationRecord schema
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='app_monitor_observationrecord'")
row = cur.fetchone()
print("\n=== app_monitor_observationrecord ===")
print(row[0] if row else "NOT FOUND")

conn.close()
