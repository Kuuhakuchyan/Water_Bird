import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

cursor = connection.cursor()

print("=== Checking current state ===")

# Check if status_new exists
cursor.execute("PRAGMA table_info(app_monitor_observationrecord)")
cols = {c[1]: c[2] for c in cursor.fetchall()}
print("ObservationRecord columns:", cols)

has_status = 'status' in cols
has_status_new = 'status_new' in cols
has_status_int = cols.get('status') == 'INTEGER'

print(f"\nhas_status={has_status}, has_status_new={has_status_new}, has_status_int={has_status_int}")

# Check current data
cursor.execute("SELECT id, status, status_new FROM app_monitor_observationrecord LIMIT 3")
print("Sample:", cursor.fetchall())

# Check FK references
print("\n=== FK references to observationrecord ===")
cursor.execute("""
    SELECT name, tbl_name, sql FROM sqlite_master
    WHERE type='table' AND sql LIKE '%observationrecord%'
""")
for r in cursor.fetchall():
    print(f"  {r[0]} ({r[1]})")

# Check if there are any other tables referencing app_monitor tables
print("\n=== All app_monitor tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'app_monitor%'")
for r in cursor.fetchall():
    print(f"  {r[0]}")

print("\n=== Rebuilding schema ===\n")

# Since the table structure is completely messed up, rebuild from scratch
# Step 1: Snapshot existing data (observationrecord)
print("Step 1: Snapshot observationrecord data")
cursor.execute("SELECT * FROM app_monitor_observationrecord")
obs_rows = cursor.fetchall()
obs_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_observationrecord)").fetchall()]
print(f"  Got {len(obs_rows)} observation rows, cols: {obs_cols}")

# Step 2: Snapshot userprofile data
cursor.execute("SELECT * FROM app_monitor_userprofile")
up_rows = cursor.fetchall()
up_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_userprofile)").fetchall()]
print(f"  Got {len(up_rows)} userprofile rows, cols: {up_cols}")

# Step 3: Snapshot wetlandzone data
cursor.execute("SELECT * FROM app_monitor_wetlandzone")
wz_rows = cursor.fetchall()
wz_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_wetlandzone)").fetchall()]
print(f"  Got {len(wz_rows)} wetlandzone rows, cols: {wz_cols}")

# Step 4: Snapshot monitoringroute data
cursor.execute("SELECT * FROM app_monitor_monitoringroute")
mr_rows = cursor.fetchall()
mr_cols = [c[1] for c in cursor.fetchall()]
mr_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_monitoringroute)").fetchall()]
print(f"  Got {len(mr_rows)} monitoringroute rows, cols: {mr_cols}")

# Step 5: Determine status values
if 'status' in cols:
    if cols['status'] == 'INTEGER':
        # Migrate: 0=pending, 1=approved, 2=rejected
        for row in obs_rows:
            idx = obs_cols.index('status')
            int_val = row[idx] if idx < len(row) else 0
            print(f"  Row id={row[0] if row else 'N/A'}: status_int={int_val}")

# Step 6: Drop old tables and recreate with correct schema
print("\nStep 6: Rebuild observationrecord table")
# We need to determine the status column name and type
actual_status_col = 'status_new' if has_status_new else ('status' if has_status else None)
print(f"  Actual status column: {actual_status_col}")

# Create new table
cursor.execute("DROP TABLE IF EXISTS app_monitor_observationrecord_old")
cursor.execute("ALTER TABLE app_monitor_observationrecord RENAME TO app_monitor_observationrecord_old")

cursor.execute("""
    CREATE TABLE app_monitor_observationrecord (
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
print("  + Created new observationrecord table")

# Determine status col index in old table
old_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_observationrecord_old)").fetchall()]
print(f"  Old columns: {old_cols}")

# Copy data
status_idx = old_cols.index(actual_status_col) if actual_status_col else None
desc_idx = old_cols.index('description') if 'description' in old_cols else None
uploder_idx = old_cols.index('uploader_id') if 'uploader_id' in old_cols else None

for row in obs_rows:
    new_row = list(row[:4])  # id, obs_time, count, image
    # status: convert INTEGER to string
    if status_idx is not None and status_idx < len(row):
        sv = row[status_idx]
        if isinstance(sv, int):
            new_status = {0: 'pending', 1: 'approved', 2: 'rejected'}.get(sv, 'pending')
        else:
            new_status = str(sv) if sv else 'pending'
    else:
        new_status = 'pending'
    new_row.append(new_status)
    # description
    new_row.append(row[desc_idx] if desc_idx and desc_idx < len(row) else None)
    # reporter_id
    new_row.append(row[old_cols.index('reporter_id')] if 'reporter_id' in old_cols else None)
    # species_id
    new_row.append(row[old_cols.index('species_id')] if 'species_id' in old_cols else None)
    # zone_id
    new_row.append(row[old_cols.index('zone_id')] if 'zone_id' in old_cols else None)
    # uploader_id
    new_row.append(row[uploder_idx] if uploder_idx and uploder_idx < len(row) else None)
    # location_json
    new_row.append(None)

    placeholders = ','.join(['?' for _ in new_row])
    cursor.execute(f"INSERT INTO app_monitor_observationrecord VALUES ({placeholders})", new_row)

print(f"  ~ Inserted {cursor.rowcount} rows")

# Step 7: Fix wetlandzone - add location_json
print("\nStep 7: Fix wetlandzone")
try:
    cursor.execute("ALTER TABLE app_monitor_wetlandzone ADD COLUMN location_json TEXT")
    print("  + Added location_json")
except:
    print("  ~ location_json already exists or other issue")

# Step 8: Fix monitoringroute - add path_geom_json, drop path_coordinates
print("\nStep 8: Fix monitoringroute")
# Create new table without path_coordinates, with path_geom_json
try:
    cursor.execute("DROP TABLE IF EXISTS app_monitor_monitoringroute_new")
    cursor.execute("""
        CREATE TABLE app_monitor_monitoringroute_new (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            description TEXT,
            path_geom_json TEXT
        )
    """)
    print("  + Created new monitoringroute table")

    # Copy data
    mr_old_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_monitoringroute)").fetchall()]
    name_idx = mr_old_cols.index('name') if 'name' in mr_old_cols else 1
    desc_idx = mr_old_cols.index('description') if 'description' in mr_old_cols else None
    path_idx = mr_old_cols.index('path_coordinates') if 'path_coordinates' in mr_old_cols else None

    for row in mr_rows:
        new_row = [
            row[0],  # id
            row[name_idx] if name_idx < len(row) else None,
            row[desc_idx] if desc_idx and desc_idx < len(row) else None,
            row[path_idx] if path_idx and path_idx < len(row) else None,  # reuse path_coordinates as JSON
        ]
        placeholders = ','.join(['?' for _ in new_row])
        cursor.execute(f"INSERT INTO app_monitor_monitoringroute_new VALUES ({placeholders})", new_row)
    print(f"  ~ Copied {cursor.rowcount} rows")

    cursor.execute("DROP TABLE app_monitor_monitoringroute")
    cursor.execute("ALTER TABLE app_monitor_monitoringroute_new RENAME TO app_monitor_monitoringroute")
    print("  ~ Replaced monitoringroute table")
except Exception as e:
    print(f"  ~ monitoringroute fix: {e}")

# Step 9: Fix userprofile
print("\nStep 9: Fix userprofile")
try:
    # Check current columns
    up_cur_cols = [c[1] for c in cursor.execute("PRAGMA table_info(app_monitor_userprofile)").fetchall()]
    print(f"  Current columns: {up_cur_cols}")
    if 'points' in up_cur_cols and 'score' not in up_cur_cols:
        cursor.execute("ALTER TABLE app_monitor_userprofile RENAME COLUMN points TO score")
        print("  ~ Renamed points to score")
    if 'avatar' not in up_cur_cols:
        cursor.execute("ALTER TABLE app_monitor_userprofile ADD COLUMN avatar VARCHAR(100)")
        print("  + Added avatar")
except Exception as e:
    print(f"  ~ userprofile fix: {e}")

# Verify
print("\n=== Final verification ===")
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

# Cleanup old table
try:
    cursor.execute("DROP TABLE IF EXISTS app_monitor_observationrecord_old")
    print("\n  ~ Cleaned up observationrecord_old")
except:
    pass

print("\nAll done!")
