import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

cursor = connection.cursor()

print("=== Step 1: Add missing columns ===")

# ObservationRecord: description (TEXT)
try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord ADD COLUMN description TEXT")
    print("  + app_monitor_observationrecord.description added")
except Exception as e:
    print(f"  ~ app_monitor_observationrecord.description: {e}")

# ObservationRecord: uploader_id (FK to auth_user)
try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord ADD COLUMN uploader_id INTEGER")
    print("  + app_monitor_observationrecord.uploader_id added")
except Exception as e:
    print(f"  ~ app_monitor_observationrecord.uploader_id: {e}")

# ObservationRecord: status is INTEGER but should be VARCHAR, need to convert
# Add new column then drop old
try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord ADD COLUMN status_new VARCHAR(10)")
    print("  + app_monitor_observationrecord.status_new added")

    # Migrate data: 0=pending, 1=approved, 2=rejected (guess based on old migration)
    cursor.execute("""
        UPDATE app_monitor_observationrecord
        SET status_new = CASE CAST(status AS INTEGER)
            WHEN 0 THEN 'pending'
            WHEN 1 THEN 'approved'
            WHEN 2 THEN 'rejected'
            ELSE 'pending'
        END
    """)
    print("  ~ status data migrated")

    # Drop old column and rename new one
    cursor.execute("CREATE TABLE _obs_backup AS SELECT id, observation_time, count, image, status_new, description, reporter_id, species_id, zone_id, uploader_id FROM app_monitor_observationrecord")
    cursor.execute("DROP TABLE app_monitor_observationrecord")
    cursor.execute("ALTER TABLE _obs_backup RENAME TO app_monitor_observationrecord")
    print("  ~ status column converted from INTEGER to VARCHAR(10)")
except Exception as e:
    print(f"  ~ status conversion: {e}")

# WetlandZone: location (Point as BLOB placeholder)
try:
    cursor.execute("ALTER TABLE app_monitor_wetlandzone ADD COLUMN location BLOB")
    print("  + app_monitor_wetlandzone.location added (GIS placeholder)")
except Exception as e:
    print(f"  ~ app_monitor_wetlandzone.location: {e}")

# MonitoringRoute: path_geom (MultiLineString as BLOB placeholder)
try:
    cursor.execute("ALTER TABLE app_monitor_monitoringroute ADD COLUMN path_geom BLOB")
    print("  + app_monitor_monitoringroute.path_geom added (GIS placeholder)")
except Exception as e:
    print(f"  ~ app_monitor_monitoringroute.path_geom: {e}")

# UserProfile: rename points->score, add avatar
try:
    cursor.execute("ALTER TABLE app_monitor_userprofile RENAME COLUMN points TO score")
    print("  ~ app_monitor_userprofile.points renamed to score")
except Exception as e:
    print(f"  ~ rename points->score: {e}")

try:
    cursor.execute("ALTER TABLE app_monitor_userprofile ADD COLUMN avatar VARCHAR(100)")
    print("  + app_monitor_userprofile.avatar added")
except Exception as e:
    print(f"  ~ app_monitor_userprofile.avatar: {e}")

# Also need location for ObservationRecord
try:
    cursor.execute("ALTER TABLE app_monitor_observationrecord ADD COLUMN location BLOB")
    print("  + app_monitor_observationrecord.location added")
except Exception as e:
    print(f"  ~ app_monitor_observationrecord.location: {e}")

print("\n=== Step 2: Verify schema ===")
cursor.execute("PRAGMA table_info(app_monitor_observationrecord)")
print("ObservationRecord columns:", [c[1] for c in cursor.fetchall()])

cursor.execute("PRAGMA table_info(app_monitor_wetlandzone)")
print("WetlandZone columns:", [c[1] for c in cursor.fetchall()])

cursor.execute("PRAGMA table_info(app_monitor_monitoringroute)")
print("MonitoringRoute columns:", [c[1] for c in cursor.fetchall()])

cursor.execute("PRAGMA table_info(app_monitor_userprofile)")
print("UserProfile columns:", [c[1] for c in cursor.fetchall()])

print("\n=== Step 3: Test API endpoints ===")
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
    print(f"Data count: {len(vs.data) if isinstance(vs.data, list) else 'paginated'}")

print("\nDone!")
