import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

cursor = connection.cursor()

print("=== Checking current ObservationRecord state ===")
cursor.execute("PRAGMA table_info(app_monitor_observationrecord)")
print("Columns:", [(c[1], c[2]) for c in cursor.fetchall()])

cursor.execute("SELECT status, status_new FROM app_monitor_observationrecord LIMIT 3")
print("Sample status/status_new values:", cursor.fetchall())

print("\n=== Fixing schema ===")

# 1. Drop the _obs_backup if it exists
try:
    cursor.execute("DROP TABLE IF EXISTS _obs_backup")
    print("  ~ Dropped _obs_backup")
except Exception as e:
    print(f"  ~ _obs_backup drop: {e}")

# 2. Create a new table with correct schema (drop and recreate)
try:
    cursor.execute("""
        CREATE TABLE app_monitor_observationrecord_new (
            id INTEGER PRIMARY KEY,
            observation_time DATE,
            count INTEGER,
            image VARCHAR(100),
            status VARCHAR(10),
            description TEXT,
            reporter_id BIGINT,
            species_id BIGINT,
            zone_id BIGINT,
            uploader_id INTEGER,
            location_json TEXT
        )
    """)
    print("  + Created new schema table")
except Exception as e:
    print(f"  + new table: {e}")

# 3. Copy data from old table
try:
    cursor.execute("""
        INSERT INTO app_monitor_observationrecord_new
            (id, observation_time, count, image, description, reporter_id, species_id, zone_id, uploader_id, location_json)
        SELECT
            id, observation_time, count, image, description, reporter_id, species_id, zone_id, uploader_id, NULL
        FROM app_monitor_observationrecord
    """)
    print("  ~ Data copied")
except Exception as e:
    print(f"  ~ copy data: {e}")

# 4. Migrate status: try INTEGER, then VARCHAR
try:
    updated = cursor.execute("""
        UPDATE app_monitor_observationrecord_new
        SET status = CASE CAST(status AS INTEGER)
            WHEN 0 THEN 'pending'
            WHEN 1 THEN 'approved'
            WHEN 2 THEN 'rejected'
            ELSE 'pending'
        END
        WHERE status IS NOT NULL
    """).rowcount
    print(f"  ~ INTEGER status migrated ({updated} rows)")
except Exception as e:
    # status might already be VARCHAR
    try:
        cursor.execute("""
            UPDATE app_monitor_observationrecord_new
            SET status = COALESCE(
                CASE status
                    WHEN 'pending' THEN 'pending'
                    WHEN 'approved' THEN 'approved'
                    WHEN 'rejected' THEN 'rejected'
                    ELSE NULL
                END,
                'pending'
            )
        """)
        print("  ~ VARCHAR status normalized")
    except Exception as e2:
        print(f"  ~ status normalize: {e2}")

# 5. Drop old table and rename new one
try:
    cursor.execute("DROP TABLE app_monitor_observationrecord")
    print("  ~ Dropped old table")
except Exception as e:
    print(f"  ~ drop old: {e}")

try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord_new RENAME TO app_monitor_observationrecord")
    print("  ~ Renamed new table to observationrecord")
except Exception as e:
    print(f"  ~ rename: {e}")

# 6. Add JSON columns to other tables
for col, table in [
    ('location', 'app_monitor_wetlandzone'),
    ('path_geom', 'app_monitor_monitoringroute'),
]:
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col}_json TEXT")
        print(f"  + Added {table}.{col}_json")
    except Exception as e:
        print(f"  ~ {table}.{col}_json: {e}")

# 7. Verify final schema
print("\n=== Final schema ===")
for table in ['app_monitor_observationrecord', 'app_monitor_wetlandzone',
              'app_monitor_monitoringroute', 'app_monitor_userprofile']:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"  {table}: {cols}")

# 8. Test API endpoints
print("\n=== Testing API ===")
from rest_framework.test import APIRequestFactory
from app_monitor.views import ZoneViewSet, TransectViewSet, ObservationViewSet

factory = APIRequestFactory()
req_z = factory.get('/api/zones/')
vs = ZoneViewSet.as_view({'get': 'list'})(req_z)
print(f"zones API: {vs.status_code}")

req_t = factory.get('/api/transects/')
vs = TransectViewSet.as_view({'get': 'list'})(req_t)
print(f"transects API: {vs.status_code}")

req_o = factory.get('/api/observations/')
vs = ObservationViewSet.as_view({'get': 'list'})(req_o)
print(f"observations API: {vs.status_code}")
if vs.status_code >= 400:
    print(f"ERROR: {vs.data}")
else:
    print(f"Data count: {len(vs.data)}")

print("\nDone!")
