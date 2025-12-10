from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

# DRF 相关引用
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# GIS 相关引用 (确保安装了 PostGIS 扩展，否则以下 Point 相关代码可能会报错)
try:
    from django.contrib.gis.geos import Point
    from django.contrib.gis.measure import D
except ImportError:
    Point = None
    D = None

# 模型与序列化器
from .models import ObservationRecord, WetlandZone
# 引入我们在 serializers.py 中定义的两个序列化器
from .serializers import ObservationRecordSerializer, WetlandZoneSerializer
from .utils import smart_identify_bird  # AI 识别工具


# === 1. 监测点位视图 (对应前端 /api/zones/) ===
class ZoneViewSet(viewsets.ModelViewSet):
    """
    API 视图集：处理监测点位 (Station/Zone)
    前端用于在地图上绘制固定的观测站图标
    """
    queryset = WetlandZone.objects.all()
    serializer_class = WetlandZoneSerializer


# === 2. 观测记录视图 (对应前端 /api/observations/) ===
class ObservationViewSet(viewsets.ModelViewSet):
    """
    API 视图集：处理移动端上传和前端地图数据请求
    """
    # 按时间倒序排列，确保前端先看到最新数据
    queryset = ObservationRecord.objects.all().order_by('-observation_time')
    serializer_class = ObservationRecordSerializer

    # === 功能: 500米预警分析 (GIS功能) ===
    @action(detail=False, methods=['get'])
    def nearby_alert(self, request):
        # 如果没有安装 GIS 库，直接返回错误
        if not Point:
            return Response({'error': 'GIS libraries not installed'}, status=501)

        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))

            # 构造中心点 (WGS84 坐标系)
            p = Point(lng, lat, srid=4326)

            # 查询距离点 p 500米范围内的记录
            # 注意：这要求 ObservationRecord 模型中必须有名为 location 的 PointField
            birds = ObservationRecord.objects.filter(
                location__dwithin=(p, D(m=500))
            )
            serializer = self.get_serializer(birds, many=True)
            return Response(serializer.data)
        except Exception as e:
            # 生产环境建议记录日志
            print(f"GIS Alert Error: {e}")
            return Response({'error': str(e)}, status=400)

    # === 功能: MVT 矢量瓦片输出 (Mapbox Vector Tiles) ===
    # 用于前端高性能渲染海量点位 (可选功能)
    @action(detail=False, methods=['get'], url_path='tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)')
    def tiles(self, request, z, x, y):
        """
        生成 Mapbox Vector Tiles (MVT)
        URL 示例: /api/observations/tiles/10/50/50/
        """
        # SQL 查询：将几何数据转换为 MVT 二进制格式
        # 注意：这里假设数据库表名为 app_monitor_observationrecord，且有 location 几何字段
        sql = """
              WITH mvtgeom AS (SELECT ST_AsMVTGeom( \
                                              location, \
                                              ST_TileEnvelope(%s, %s, %s), \
                                              4096, 256, true \
                                      ) AS geom, \
                                      id, \
                                      status \
                               FROM app_monitor_observationrecord \
                               WHERE ST_Intersects(location, ST_TileEnvelope(%s, %s, %s)))
              SELECT ST_AsMVT(mvtgeom.*, 'layer_birds') \
              FROM mvtgeom; \
              """
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [z, x, y, z, x, y])
                row = cursor.fetchone()
                tile = row[0] if row else b''

            if not tile:
                return HttpResponse(b'', content_type="application/vnd.mapbox-vector-tile")
            return HttpResponse(tile, content_type="application/vnd.mapbox-vector-tile")
        except Exception as e:
            print(f"Tile Error: {e}")
            return HttpResponse(status=500)


# === 3. 页面视图 ===
def index_view(request):
    """
    首页视图：渲染前端地图页面
    """
    # 确保你的 templates 文件夹下有 index.html
    return render(request, 'index.html')


def get_todays_hotspot(request):
    """
    获取今日观鸟热点推荐 (新功能 - 可以在前端通过 ajax 调用或独立页面使用)
    """
    # 1. 算法推荐：过去 3 天观测数量最多的点位
    three_days_ago = timezone.now().date() - timedelta(days=3)

    # 聚合查询：按点位分组，统计数量总和，取第一名
    hot_zone_data = ObservationRecord.objects.filter(
        observation_time__gte=three_days_ago
    ).values('zone').annotate(total_count=Sum('count')).order_by('-total_count').first()

    recommendation_data = {}

    if hot_zone_data and hot_zone_data['zone']:
        try:
            # 注意：values('zone') 返回的是 ID
            zone = WetlandZone.objects.get(id=hot_zone_data['zone'])

            # 2. 获取该点位最新一条记录的鸟种
            latest_record = ObservationRecord.objects.filter(zone=zone).order_by('-observation_time').first()

            # 处理关联字段可能为空的情况
            bird_name = "珍稀鸟类"
            if latest_record and latest_record.species:
                bird_name = latest_record.species.name_cn

            # 获取 observation_tips，如果模型没有该字段则使用默认值
            tips = getattr(zone, 'observation_tips', "请保持安全距离观赏，避免惊扰鸟类")

            recommendation_data = {
                "title": f"今日推荐：{zone.name}，近期有{bird_name}集群活动",
                "tips": f"观鸟注意事项：{tips}",
                "location": zone.name
            }
        except WetlandZone.DoesNotExist:
            recommendation_data = _default_hotspot()
    else:
        recommendation_data = _default_hotspot()

    return render(request, 'app_monitor/hotspot.html', {'recommendation': recommendation_data})


def _default_hotspot():
    """默认兜底数据"""
    return {
        "title": "今日推荐：郑州黄河湿地中段",
        "tips": "保持100米以上距离，避免干扰",
        "location": "黄河湿地"
    }
# app_monitor/views.py

# 引入新模型和序列化器
from .models import ObservationRecord, WetlandZone, MonitoringRoute
from .serializers import ObservationRecordSerializer, WetlandZoneSerializer, MonitoringRouteSerializer

# ... (保留 ObservationViewSet 和 ZoneViewSet) ...

# === 新增：监测样线视图 ===
class TransectViewSet(viewsets.ModelViewSet):
    """
    API: 处理监测样线
    """
    queryset = MonitoringRoute.objects.all()
    serializer_class = MonitoringRouteSerializer


# ============================================================
# ▼▼▼ 请将以下代码追加到 views.py 的最末尾 ▼▼▼
# ============================================================

from django.contrib.auth.models import User
from rest_framework import serializers


# 1. 定义一个简单的用户积分序列化器 (临时写在这里，方便你直接用)
class UserScoreSerializer(serializers.ModelSerializer):
    # 动态计算积分：上传一条记录算 10 分
    score = serializers.SerializerMethodField()
    # 动态计算上传数量
    upload_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'upload_count', 'score']

    def get_upload_count(self, obj):
        # 统计该用户关联的 ObservationRecord 数量
        # 注意：这里假设 ObservationRecord 模型里有个 'uploader' 或 'user' 字段
        # 如果你的模型里没记录是谁上传的，这里会报错。
        # 假设你的 ObservationRecord 有个外键指向 User，默认反向查询名为 observationrecord_set
        try:
            return obj.observationrecord_set.count()
        except:
            return 0

    def get_score(self, obj):
        # 简单算法：数量 x 10
        return self.get_upload_count(obj) * 10


# 2. 定义用户档案视图集
class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API: 用户积分档案
    路径: /api/profiles/
    """
    queryset = User.objects.all()
    serializer_class = UserScoreSerializer

    # 额外功能：获取当前登录用户的信息
    # 访问路径: /api/profiles/me/
    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_anonymous:
            return Response({"error": "请先登录"}, status=401)

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)