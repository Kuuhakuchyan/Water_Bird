import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

cursor = connection.cursor()

# List all app_monitor tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'app_monitor%'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)

# Full schema for each
for table in tables:
    print(f"\n=== {table} ===")
    cursor.execute(f"PRAGMA table_info({table})")
    for c in cursor.fetchall():
        print(f"  {c[1]}: {c[2]}")
