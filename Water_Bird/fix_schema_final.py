import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

cursor = connection.cursor()

print("=== Fixing database schema ===\n")

# 1. Rename status_new -> status
try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord RENAME COLUMN status_new TO status")
    print("  ~ status_new renamed to status")
except Exception as e:
    print(f"  ~ status rename: {e}")

# 2. Drop BLOB location column from observationrecord
try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord DROP COLUMN location")
    print("  ~ Dropped observationrecord.location (BLOB)")
except Exception as e:
    print(f"  ~ observationrecord.location drop: {e}")

# 3. Add location_json to observationrecord
try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord ADD COLUMN location_json TEXT")
    print("  + Added observationrecord.location_json")
except Exception as e:
    print(f"  ~ observationrecord.location_json: {e}")

# 4. Drop BLOB location from wetlandzone (if it exists)
try:
    cursor.execute("ALTER TABLE app_monitor_wetlandzone DROP COLUMN location")
    print("  ~ Dropped wetlandzone.location (BLOB)")
except Exception as e:
    print(f"  ~ wetlandzone.location drop: {e}")

# 5. Add location_json to wetlandzone
try:
    cursor.execute("ALTER TABLE app_monitor_wetlandzone ADD COLUMN location_json TEXT")
    print("  + Added wetlandzone.location_json")
except Exception as e:
    print(f"  ~ wetlandzone.location_json: {e}")

# 6. Recreate monitoringroute with path_geom_json
try:
    cursor.execute("SELECT id, name, path_coordinates, description FROM app_monitor_monitoringroute")
    mr_rows = cursor.fetchall()

    cursor.execute("DROP TABLE IF EXISTS app_monitor_monitoringroute_old")
    cursor.execute("ALTER TABLE app_monitor_monitoringroute RENAME TO app_monitor_monitoringroute_old")

    cursor.execute("""
        CREATE TABLE app_monitor_monitoringroute (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            description TEXT,
            path_geom_json TEXT
        )
    """)
    print("  + Created new monitoringroute table")

    for row in mr_rows:
        new_row = [row[0], row[1], row[3], row[2]]  # id, name, description, path_geom_json=path_coordinates
        placeholders = ','.join(['?' for _ in new_row])
        cursor.execute(f"INSERT INTO app_monitor_monitoringroute VALUES ({placeholders})", new_row)
    print(f"  ~ Copied {cursor.rowcount} monitoringroute rows")

    cursor.execute("DROP TABLE app_monitor_monitoringroute_old")
    print("  ~ Cleaned up old monitoringroute")
except Exception as e:
    print(f"  ~ monitoringroute rebuild: {e}")

# 7. Fix userprofile
try:
    up_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_userprofile)").fetchall()]
    if 'points' in up_cols and 'score' not in up_cols:
        cursor.execute("ALTER TABLE app_monitor_userprofile RENAME COLUMN points TO score")
        print("  ~ Renamed points -> score")
    if 'avatar' not in up_cols:
        cursor.execute("ALTER TABLE app_monitor_userprofile ADD COLUMN avatar VARCHAR(100)")
        print("  + Added avatar")
except Exception as e:
    print(f"  ~ userprofile fix: {e}")

# Verify
print("\n=== Final schema ===")
for table in ['app_monitor_observationrecord', 'app_monitor_wetlandzone',
              'app_monitor_monitoringroute', 'app_monitor_userprofile']:
    cols = [c[1] for c in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
    print(f"  {table}: {cols}")

# Test APIs
print("\n=== API test ===")
from rest_framework.test import APIRequestFactory
from app_monitor.views import ZoneViewSet, TransectViewSet, ObservationViewSet

factory = APIRequestFactory()
for name, vs_cls, path in [
    ('zones', ZoneViewSet, '/api/zones/'),
    ('transects', TransectViewSet, '/api/transects/'),
    ('observations', ObservationViewSet, '/api/observations/'),
]:
    req = factory.get(path)
    vs = vs_cls.as_view({'get': 'list'})(req)
    status = "OK" if vs.status_code < 400 else f"ERROR: {vs.data}"
    print(f"  {name}: {vs.status_code} {status}")

print("\nDone!")
