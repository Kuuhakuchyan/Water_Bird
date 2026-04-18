import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

for table in ['app_monitor_product', 'app_monitor_article', 'app_monitor_exchangerecord']:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    row = cur.fetchone()
    print(f"{table}: {'EXISTS' if row else 'MISSING'}")

# Get UserProfile columns
cur.execute("PRAGMA table_info(app_monitor_userprofile)")
print("\n=== UserProfile columns ===")
for row in cur.fetchall():
    print(f"  {row[1]} ({row[2]})")

# Get ObservationRecord columns
cur.execute("PRAGMA table_info(app_monitor_observationrecord)")
print("\n=== ObservationRecord columns ===")
for row in cur.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()
