from rest_framework import serializers
from .models import ObservationRecord, WetlandZone, MonitoringRoute


# 1. 监测样线
class MonitoringRouteSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    class Meta:
        model = MonitoringRoute
        fields = ['id', 'name', 'description', 'path']

    def get_path(self, obj):
        # 将 MultiLineString 转换为 Leaflet 坐标数组 [[lat, lng], ...]
        if obj.path_geom:
            lines = []
            for line in obj.path_geom:
                # 调换坐标顺序: 数据库(x,y) -> Leaflet(y,x)
                lines.append([[pt[1], pt[0]] for pt in line.coords])
            return lines
        return []


# 2. 监测点位
class WetlandZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = WetlandZone
        fields = '__all__'


# 3. 观测记录 (核心)
class ObservationRecordSerializer(serializers.ModelSerializer):
    # 手动提取关联字段，防止前端读取嵌套对象时出错
    x = serializers.ReadOnlyField(source='zone.longitude')
    y = serializers.ReadOnlyField(source='zone.latitude')

    # 提取物种信息
    species_name = serializers.ReadOnlyField(source='species.name_cn')
    species_protection = serializers.ReadOnlyField(source='species.protection_level')  # 保护等级

    # 提取关联信息
    reporter_name = serializers.ReadOnlyField(source='reporter.username')
    zone_name = serializers.ReadOnlyField(source='zone.name')

    class Meta:
        model = ObservationRecord
        fields = [
            'id', 'image', 'observation_time', 'count', 'status',
            'species_name', 'species_protection',  # 关键字段
            'reporter_name', 'zone_name',
            'x', 'y'
        ]