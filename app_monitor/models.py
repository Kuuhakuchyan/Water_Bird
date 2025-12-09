from django.contrib.gis.db import models  # 【关键】必须使用 GIS 的 models
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point


# ====================
# 1. 物种信息库
# ====================
class SpeciesInfo(models.Model):
    name_cn = models.CharField(max_length=100, verbose_name="中文名", unique=True)
    name_latin = models.CharField(max_length=100, verbose_name="拉丁名(species)", blank=True)
    order = models.CharField(max_length=50, verbose_name="目", blank=True)
    family = models.CharField(max_length=50, verbose_name="科", blank=True)
    protection_level = models.CharField(max_length=20, verbose_name="保护级别", blank=True)
    distribution_habit = models.TextField(verbose_name="郑州湿地分布习性", blank=True, default="暂无详细习性数据",
                                          help_text="AI识别后展示给用户的本地化习性描述")

    class Meta:
        verbose_name = "物种信息"
        verbose_name_plural = "物种信息"

    def __str__(self):
        return self.name_cn


# ====================
# 2. 空间数据层 (核心修改部分)
# ====================
class WetlandZone(models.Model):
    name = models.CharField(max_length=100, verbose_name="点位名称", unique=True)

    # 兼容 CSV 导入的经纬度字段
    longitude = models.FloatField(verbose_name="经度(x)", blank=True, null=True)
    latitude = models.FloatField(verbose_name="纬度(y)", blank=True, null=True)

    # 【核心】地图点位字段 (SHP 导入会填充这里)
    location = models.PointField(verbose_name="地图位置", srid=4326, blank=True, null=True,
                                 help_text="SHP导入会自动填充此字段")

    is_hotspot = models.BooleanField(default=False, verbose_name="今日推荐热点")
    observation_tips = models.TextField(verbose_name="观鸟注意事项", blank=True, default="保持100米以上距离，避免干扰")

    class Meta:
        verbose_name = "监测点位"
        verbose_name_plural = "监测点位"

    def save(self, *args, **kwargs):
        # 自动同步逻辑：
        # 1. 如果地图/SHP 提供了点，同步到经纬度文本框
        if self.location:
            self.longitude = self.location.x
            self.latitude = self.location.y
        # 2. 如果只填了经纬度(如CSV导入)，生成地图点
        elif self.longitude and self.latitude:
            self.location = Point(self.longitude, self.latitude)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MonitoringRoute(models.Model):
    name = models.CharField(max_length=100, verbose_name="路线名称")

    # 【重大修改】: 从 JSONField 改为 MultiLineStringField 以支持 SHP 导入
    # 使用 MultiLineString 是为了防错，因为有些 SHP 把一条线也存成 MultiLine
    path_geom = models.MultiLineStringField(verbose_name="路线几何", srid=4326, blank=True, null=True)

    description = models.TextField(verbose_name="路线说明", blank=True)

    class Meta:
        verbose_name = "监测样线"
        verbose_name_plural = "监测样线"

    def __str__(self):
        return self.name


# ====================
# 3. 用户激励系统
# ====================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="用户")
    points = models.IntegerField(default=0, verbose_name="当前积分")

    class Meta:
        verbose_name = "用户积分档案"
        verbose_name_plural = "用户积分档案"

    def __str__(self):
        return f"{self.user.username} - {self.points}分"


# ====================
# 4. 业务数据
# ====================
class ObservationRecord(models.Model):
    STATUS_CHOICES = ((0, '待审核'), (1, '审核通过(已发积分)'), (2, '驳回'))
    species = models.ForeignKey(SpeciesInfo, on_delete=models.CASCADE, verbose_name="物种")
    zone = models.ForeignKey(WetlandZone, on_delete=models.CASCADE, verbose_name="监测点位")
    observation_time = models.DateField(verbose_name="观测日期")
    count = models.IntegerField(default=1, verbose_name="数量")
    image = models.ImageField(upload_to='observations/', blank=True, null=True, verbose_name="现场照片")
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="上报人")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="审核状态")

    class Meta:
        ordering = ['-observation_time']
        verbose_name = "观测记录"
        verbose_name_plural = "观测记录"

    def __str__(self):
        return f"{self.observation_time} - {self.species.name_cn}"


# ====================
# 5. AI 识别历史记录
# ====================
class AIDetectionResult(models.Model):
    image = models.ImageField(upload_to='ai_records/%Y/%m/', verbose_name="识别图片")
    species_name = models.CharField(max_length=50, verbose_name="识别结果", default="未知")
    confidence = models.FloatField(verbose_name="置信度", default=0.0)
    habit_info = models.TextField(verbose_name="习性简介", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="识别时间")

    class Meta:
        verbose_name = "AI 识别记录"
        verbose_name_plural = "AI 识别记录"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.species_name} ({self.confidence:.1%})"