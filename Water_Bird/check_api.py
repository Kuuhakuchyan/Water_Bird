import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()

# Check which app_monitor migrations are recorded
cursor.execute("SELECT name, applied FROM django_migrations WHERE app='app_monitor'")
for row in cursor.fetchall():
    print(f'  {row[0]} - {row[1]}')

# Check actual table schema
cursor.execute('PRAGMA table_info(app_monitor_observationrecord)')
cols = {c[1]: c[2] for c in cursor.fetchall()}
print('ObservationRecord - Has description?', 'description' in cols)
print('ObservationRecord - Has uploader_id?', 'uploader_id' in cols)

cursor.execute('PRAGMA table_info(app_monitor_wetlandzone)')
cols = {c[1]: c[2] for c in cursor.fetchall()}
print('WetlandZone - Has location?', 'location' in cols)

cursor.execute('PRAGMA table_info(app_monitor_monitoringroute)')
cols = {c[1]: c[2] for c in cursor.fetchall()}
print('MonitoringRoute - Has path_geom?', 'path_geom' in cols)
print('MonitoringRoute - Has path_coordinates?', 'path_coordinates' in cols)

# Try the API
from rest_framework.test import APIRequestFactory
from app_monitor.views import ZoneViewSet, TransectViewSet, ObservationViewSet

factory = APIRequestFactory()
req_z = factory.get('/api/zones/')
vs = ZoneViewSet.as_view({'get': 'list'})(req_z)
print('\nzones API:', vs.status_code)

req_t = factory.get('/api/transects/')
vs = TransectViewSet.as_view({'get': 'list'})(req_t)
print('transects API:', vs.status_code)

req_o = factory.get('/api/observations/')
vs = ObservationViewSet.as_view({'get': 'list'})(req_o)
print('observations API:', vs.status_code)
if vs.status_code >= 400:
    print('ERROR:', vs.data)
