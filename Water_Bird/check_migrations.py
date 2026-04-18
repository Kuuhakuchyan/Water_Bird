import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT id, name, app FROM django_migrations WHERE app='app_monitor' ORDER BY id")
for row in cur.fetchall():
    print(row)
conn.close()
