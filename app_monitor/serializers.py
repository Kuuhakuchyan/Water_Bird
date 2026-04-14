from rest_framework import serializers
# 引入所有需要的模型
from .models import ObservationRecord, WetlandZone, MonitoringRoute, Product, UserProfile, SpeciesInfo
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


# ==========================================
# 0. 用户注册序列化器
# ==========================================
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "两次密码输入不一致"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


# ==========================================
# 1. 商品序列化器 (用于积分商城)
# ==========================================
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# ==========================================
# 2. 用户信息序列化器 (用于个人中心)
# ==========================================
class UserInfoSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(source='profile.score', read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'score', 'avatar']


# ==========================================
# 2b. 用户资料更新序列化器 (支持修改邮箱和头像)
# ==========================================
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['email']

    def update(self, instance, validated_data):
        email = validated_data.get('email', None)
        if email is not None:
            instance.email = email
            instance.save(update_fields=['email'])
        return instance


class UserAvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar']

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')
        if avatar is not None:
            instance.avatar = avatar
            instance.save(update_fields=['avatar'])
        return instance


# ==========================================
# 0b. 物种列表序列化器
# ==========================================
class SpeciesInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesInfo
        fields = ['id', 'name_cn', 'name_latin', 'order', 'family', 'protection_level', 'distribution_habit']


# ==========================================
# 3. 监测样线 (保留原逻辑)
# ==========================================
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


# ==========================================
# 4. 监测点位 (保留原逻辑)
# ==========================================
class WetlandZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = WetlandZone
        fields = '__all__'


# ==========================================
# 5. 观测记录 (核心：兼容修复版)
# ==========================================
class ObservationRecordSerializer(serializers.ModelSerializer):
    # --- A. 必须恢复的旧字段 (为了让前端地图不报错) ---
    # 前端找的是 x 和 y，而不是 lat 和 lng
    x = serializers.SerializerMethodField()
    y = serializers.SerializerMethodField()

    # 前端找的是 reporter_name
    reporter_name = serializers.SerializerMethodField()

    # --- B. 新功能的字段 (后台管理用) ---
    uploader_name = serializers.ReadOnlyField(source='uploader.username')
    species_name = serializers.ReadOnlyField(source='species.name_cn')
    species_protection = serializers.ReadOnlyField(source='species.protection_level')
    zone_name = serializers.ReadOnlyField(source='zone.name')

    # --- C. 备用新字段 (建议前端以后慢慢迁移到这两个字段) ---
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = ObservationRecord
        fields = [
            'id',
            'image',
            'description',
            'observation_time',
            'count',
            'status',  # 新增：审核状态
            'species', 'zone',  # ID 字段

            # === 显示字段 ===
            'species_name',
            'species_protection',
            'zone_name',

            # === 坐标字段 (新旧共存) ===
            'x', 'y',  # 🚑 旧前端救命字段
            'lat', 'lng',  # ✨ 新前端推荐字段

            # === 人员字段 (新旧共存) ===
            'reporter_name',  # 🚑 旧前端救命字段
            'uploader_name'  # ✨ 新后台字段
        ]
        read_only_fields = ['status', 'uploader', 'observation_time']

    # ---------------------------------------------------
    # 逻辑实现：无论数据怎么存，都转换成前端能看懂的样子
    # ---------------------------------------------------

    def get_x(self, obj):
        # 逻辑：优先取 GIS 坐标点的 X，没有则取关联区域的经度
        if hasattr(obj, 'location') and obj.location:
            return obj.location.x
        if obj.zone:
            return obj.zone.longitude
        return None

    def get_y(self, obj):
        # 逻辑：优先取 GIS 坐标点的 Y，没有则取关联区域的纬度
        if hasattr(obj, 'location') and obj.location:
            return obj.location.y
        if obj.zone:
            return obj.zone.latitude
        return None

    # 为了方便以后迁移，lat/lng 直接复用 x/y 的逻辑
    def get_lng(self, obj):
        return self.get_x(obj)

    def get_lat(self, obj):
        return self.get_y(obj)

    def get_reporter_name(self, obj):
        # 逻辑：这行代码同时兼容了新数据(uploader)和旧数据(reporter)
        # 1. 优先显示“上传者”(新功能)
        if obj.uploader:
            return obj.uploader.username
        # 2. 如果没有上传者，尝试显示“上报人”(旧数据)
        if obj.reporter:
            return obj.reporter.username
        # 3. 如果都没有
        return "匿名用户"