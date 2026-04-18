from django.contrib.gis.db import models  # GIS 的 models (使用 JSONField 替代 PointField)
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ====================
# 1. 物种信息库
# ====================
class SpeciesInfo(models.Model):
    name_cn = models.CharField(max_length=100, verbose_name="中文名", unique=True)
    name_latin = models.CharField(max_length=100, verbose_name="拉丁名(species)", blank=True)
    order = models.CharField(max_length=50, verbose_name="目", blank=True)
    family = models.CharField(max_length=50, verbose_name="科", blank=True)
    protection_level = models.CharField(max_length=20, verbose_name="保护级别", blank=True)
    distribution_habit = models.TextField(
        verbose_name="郑州湿地分布习性",
        blank=True,
        default="暂无详细习性数据",
        help_text="AI识别后展示给用户的本地化习性描述"
    )

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

    # 使用 JSON 存储坐标（兼容 SQLite，支持 SHP 导入的 GeoJSON）
    location = models.JSONField(verbose_name="地图位置(JSON)", blank=True, null=True, db_column='location_json')

    is_hotspot = models.BooleanField(default=False, verbose_name="今日推荐热点")
    observation_tips = models.TextField(
        verbose_name="观鸟注意事项",
        blank=True,
        default="保持100米以上距离，避免干扰"
    )

    class Meta:
        verbose_name = "监测点位"
        verbose_name_plural = "监测点位"

    def save(self, *args, **kwargs):
        # JSON 格式：{"type": "Point", "coordinates": [lng, lat]}
        if self.location and isinstance(self.location, dict):
            coords = self.location.get('coordinates', [])
            if len(coords) >= 2:
                self.longitude = coords[0]
                self.latitude = coords[1]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MonitoringRoute(models.Model):
    name = models.CharField(max_length=100, verbose_name="路线名称")
    # 使用 JSON 存储路线坐标（兼容 SQLite，支持 SHP 导入的 GeoJSON MultiLineString）
    path_geom = models.JSONField(verbose_name="路线几何(JSON)", blank=True, null=True, db_column='path_geom_json')
    description = models.TextField(verbose_name="路线说明", blank=True)

    class Meta:
        verbose_name = "监测样线"
        verbose_name_plural = "监测样线"

    def __str__(self):
        return self.name


# ====================
# 3. 用户积分档案 (合并版)
# ====================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="用户")
    # 统一使用 score 作为积分字段名，避免歧义
    score = models.IntegerField(default=0, verbose_name="当前积分")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="头像")

    class Meta:
        verbose_name = "用户积分档案"
        verbose_name_plural = "用户积分档案"

    def __str__(self):
        return f"{self.user.username} - {self.score}分"


# 信号：自动创建 UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# ====================
# 4. 业务数据 (观测记录)
# ====================
class ObservationRecord(models.Model):
    species = models.ForeignKey(SpeciesInfo, on_delete=models.CASCADE, verbose_name="物种")
    zone = models.ForeignKey(WetlandZone, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="监测点位")
    latitude = models.FloatField(null=True, blank=True, verbose_name="纬度")
    longitude = models.FloatField(null=True, blank=True, verbose_name="经度")
    observation_time = models.DateField(verbose_name="观测日期")
    count = models.IntegerField(default=1, verbose_name="数量")
    image = models.ImageField(upload_to='observations/', blank=True, null=True, verbose_name="现场照片")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    # 审核状态 (统一使用字符串枚举)
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="审核状态")

    # 上传者 (统一使用 uploader，并为了避免冲突，使用 related_name)
    uploader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="上传者",
        related_name='uploaded_observations'
    )

    # 兼容旧字段 reporter (可选：如果你不需要保留历史数据，可以删掉这个字段)
    # 加上 related_name 防止与 uploader 冲突
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="上报人(旧)",
        related_name='reported_observations'
    )

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


# ====================
# 6. 积分商城商品
# ====================
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="商品名称")
    price = models.IntegerField(verbose_name="所需积分")
    image = models.ImageField(upload_to='products/', verbose_name="商品图片")
    description = models.TextField(blank=True, verbose_name="商品描述")
    stock = models.IntegerField(default=999, verbose_name="库存")

    class Meta:
        verbose_name = "积分商城商品"
        verbose_name_plural = "积分商城商品"

    def __str__(self):
        return self.name


# ====================
# 7. 兑换记录
# ====================
class ExchangeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="兑换用户", related_name='exchange_records')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="兑换商品")
    points_spent = models.IntegerField(verbose_name="消耗积分")
    status = models.CharField(
        max_length=20, default='pending', verbose_name="状态",
        choices=(
            ('pending', '处理中'),
            ('shipped', '已发货'),
            ('completed', '已完成'),
            ('cancelled', '已取消'),
        )
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="兑换时间")

    class Meta:
        verbose_name = "兑换记录"
        verbose_name_plural = "兑换记录"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 兑换 {self.product.name}"


# ====================
# 8. 生态科普文章
# ====================
class Article(models.Model):
    CATEGORY_CHOICES = (
        ('habitat', '栖息地保护'),
        ('species', '物种保护'),
        ('knowledge', '生态知识'),
        ('news', '保护动态'),
    )
    title = models.CharField(max_length=200, verbose_name="文章标题")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='knowledge', verbose_name="分类")
    summary = models.TextField(verbose_name="摘要", blank=True, default='')
    content = models.TextField(verbose_name="文章内容（富文本）")
    cover_image = models.ImageField(upload_to='articles/covers/', blank=True, null=True, verbose_name="封面图")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="作者")
    views = models.IntegerField(default=0, verbose_name="浏览量")
    is_published = models.BooleanField(default=True, verbose_name="是否发布")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "科普文章"
        verbose_name_plural = "科普文章"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
