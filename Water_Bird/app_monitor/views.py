from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Q, F
from datetime import timedelta
import logging

# DRF related imports
from rest_framework import viewsets, permissions, status, serializers, generics
from rest_framework.decorators import action
from rest_framework.response import Response

# Get logger
logger = logging.getLogger('app_monitor')

# === 引入模型 ===
# 确保包含 Product, UserProfile
from .models import ObservationRecord, WetlandZone, MonitoringRoute, Product, UserProfile, SpeciesInfo, Article, ExchangeRecord, SpeciesImage
from django.contrib.auth.models import User

# === 引入序列化器 ===
from .serializers import (
    ObservationRecordSerializer,
    WetlandZoneSerializer,
    MonitoringRouteSerializer,
    ProductSerializer,
    UserInfoSerializer,
    UserRegisterSerializer,
    UserProfileUpdateSerializer,
    UserAvatarUpdateSerializer,
    SpeciesInfoSerializer,
    SpeciesImageSerializer,
    ArticleSerializer,
    ExchangeRecordSerializer,
)


# ==========================================
# 0. 用户注册视图 /api/auth/register/
# ==========================================
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserInfoSerializer(user).data,
                'token': token.key,
                'message': '注册成功'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 1. 监测点位视图 /api/zones/
# ==========================================
class ZoneViewSet(viewsets.ModelViewSet):
    queryset = WetlandZone.objects.all()
    serializer_class = WetlandZoneSerializer


# ==========================================
# 1b. 物种列表视图 /api/species/
# ==========================================
class SpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SpeciesInfo.objects.all().order_by('name_cn')
    serializer_class = SpeciesInfoSerializer
    permission_classes = [permissions.AllowAny]


# ==========================================
# 1c. 物种图片库视图 /api/species-images/
# ==========================================
class SpeciesImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SpeciesImage.objects.all().order_by('-is_featured', '-views', '-created_at')
    serializer_class = SpeciesImageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        species_id = self.request.query_params.get('species_id')
        if species_id:
            queryset = queryset.filter(species_id=species_id)
        return queryset

    # 设置精选图片：指定某张图片为某物种的封面
    @action(detail=True, methods=['post'], url_path='set-featured')
    def set_featured(self, request, pk=None):
        """将指定图片设为该物种的精选封面图。
        请求体：{ "species_id": 123 }（可选，API会自动从图片对象获取）
        """
        image = self.get_object()
        species_id = request.data.get('species_id') or image.species_id

        # 将同物种其他图片的 is_featured 设为 False
        SpeciesImage.objects.filter(species_id=species_id).exclude(pk=image.pk).update(is_featured=False)
        # 将指定图片设为精选
        image.is_featured = True
        image.save(update_fields=['is_featured'])

        # 重新获取该物种的封面图 URL
        from app_monitor.serializers import SpeciesInfoSerializer
        species = SpeciesInfo.objects.get(pk=species_id)
        cover_url = SpeciesInfoSerializer(species, context={'request': request}).data.get('cover_image_url')

        return Response({
            'success': True,
            'image_id': image.pk,
            'species_id': species_id,
            'cover_image_url': cover_url,
            'message': f'已将图片设为 {image.species.name_cn} 的精选封面'
        })

    # 批量设置精选（一次性设置多个图片的精选状态）
    @action(detail=False, methods=['post'], url_path='batch-set-featured')
    def batch_set_featured(self, request):
        """批量设置精选图片。
        请求体：{ "image_ids": [1, 2, 3] } — 第一个为精选
        """
        image_ids = request.data.get('image_ids', [])
        if not image_ids:
            return Response({'success': False, 'message': '请提供 image_ids'}, status=400)

        featured_id = image_ids[0] if image_ids else None
        species_id = None

        # 获取第一个图片的物种ID
        if featured_id:
            try:
                first_img = SpeciesImage.objects.get(pk=featured_id)
                species_id = first_img.species_id
            except SpeciesImage.DoesNotExist:
                return Response({'success': False, 'message': f'图片 {featured_id} 不存在'}, status=404)

        # 清除该物种所有精选状态
        if species_id:
            SpeciesImage.objects.filter(species_id=species_id).update(is_featured=False)

        # 设置新的精选
        updated = SpeciesImage.objects.filter(pk__in=image_ids).update(is_featured=True)

        return Response({
            'success': True,
            'featured_id': featured_id,
            'species_id': species_id,
            'updated_count': updated,
            'message': '精选图片已更新'
        })


# ==========================================
# 2. 监测样线视图 /api/transects/
# ==========================================
class TransectViewSet(viewsets.ModelViewSet):
    queryset = MonitoringRoute.objects.all()
    serializer_class = MonitoringRouteSerializer


# ==========================================
# 3. 观测记录视图 /api/observations/ (核心)
# ==========================================
class ObservationViewSet(viewsets.ModelViewSet):
    """
    核心业务视图：
    1. 游客：只能看已通过(approved)的数据
    2. 登录用户：能看已通过 + 自己上传(pending/rejected)的数据
    3. 管理员：能看所有数据
    4. 上传：自动关联用户，自动加分
    """
    serializer_class = ObservationRecordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 游客只读，登录可写

    def get_queryset(self):
        # 默认按时间倒序
        queryset = ObservationRecord.objects.all().order_by('-observation_time')

        user = self.request.user

        # A. 管理员/巡护员: 看所有
        if user.is_staff:
            return queryset

        # B. 登录的普通用户: 看 '已通过' | '我自己上传的'
        if user.is_authenticated:
            return queryset.filter(
                Q(status='approved') | Q(uploader=user)
            )

        # C. 游客: 只看 '已通过'
        return queryset.filter(status='approved')

    def perform_create(self, serializer):
        """
        When user POSTs observation data, auto-associate user and award points.
        Uses atomic transaction + explicit get-then-create to prevent race conditions
        where concurrent submissions could both try to create UserProfile.
        """
        user = self.request.user
        with transaction.atomic():
            record = serializer.save(uploader=user)
            try:
                profile = UserProfile.objects.select_for_update().get(user=user)
            except UserProfile.DoesNotExist:
                try:
                    profile = UserProfile.objects.create(user=user, score=10)
                except transaction.TransactionManagementError:
                    profile = UserProfile.objects.select_for_update().get(user=user)
                else:
                    logger.info(
                        "Observation uploaded: user=%s record_id=%s, created profile with score=10",
                        user.username, record.id
                    )
                    return
            profile.score = F('score') + 10
            profile.save(update_fields=['score'])
            profile.refresh_from_db()
            logger.info(
                "Observation uploaded: user=%s record_id=%s, score awarded=10, total=%s",
                user.username, record.id, profile.score
            )

    # === GIS 功能: 附近预警 ===
    @action(detail=False, methods=['get'])
    def nearby_alert(self, request):
        # SQLite 不支持 PostGIS 空间查询，返回空
        return Response([])

    # === GIS 功能: MVT 矢量瓦片 ===
    @action(detail=False, methods=['get'], url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)')
    def tiles(self, request, z, x, y):
        # SQLite 不支持矢量瓦片，返回空
        return HttpResponse(b'', content_type="application/vnd.mapbox-vector-tile")


# ==========================================
# 4. 商品/积分商城视图 /api/products/
# ==========================================
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # POST /api/products/{id}/redeem/
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def redeem(self, request, pk=None):
        product = self.get_object()
        user = request.user

        try:
            with transaction.atomic():
                profile = UserProfile.objects.select_for_update().get(user=user)
                product = Product.objects.select_for_update().get(pk=product.pk)

                if product.stock <= 0:
                    return Response({"error": "商品库存不足"}, status=400)

                if profile.score < product.price:
                    return Response({
                        "error": f"积分不足，还需要 {product.price - profile.score} 分"
                    }, status=400)

                spent = product.price
                profile.score = F('score') - spent
                profile.save(update_fields=['score'])
                profile.refresh_from_db()

                product.stock = F('stock') - 1
                product.save(update_fields=['stock'])
                product.refresh_from_db()

                ExchangeRecord.objects.create(
                    user=user,
                    product=product,
                    points_spent=spent,
                    status='pending'
                )

                logger.info(
                    "Redemption: user=%s redeemed=%s (price=%s), remaining_score=%s, stock=%s",
                    user.username, product.name, spent, profile.score, product.stock
                )

                return Response({
                    "message": f"成功兑换: {product.name}",
                    "remaining_score": profile.score
                })
        except UserProfile.DoesNotExist:
            return Response({"error": "用户档案不存在"}, status=400)
        except Product.DoesNotExist:
            return Response({"error": "商品不存在"}, status=400)

    # GET /api/products/me/exchanges/  <-- 用户查看自己的兑换记录
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='me/exchanges')
    def my_exchanges(self, request):
        records = ExchangeRecord.objects.filter(user=request.user).order_by('-created_at')
        serializer = ExchangeRecordSerializer(records, many=True, context={'request': request})
        return Response(serializer.data)


# ==========================================
# 5. 用户档案视图 /api/profiles/
# ==========================================
class UserProfileUpdateScoreSerializer(serializers.Serializer):
    """Score update serializer — uses delta instead of absolute value to prevent
    clients from overwriting the score to arbitrary values."""
    delta = serializers.IntegerField(required=True, help_text="积分增量，正数增加，负数减少")

    def update(self, instance, validated_data):
        delta = validated_data['delta']
        instance.score = F('score') + delta
        instance.save(update_fields=['score'])
        instance.refresh_from_db()
        return instance


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    # GET /api/profiles/me/  <-- Frontend fetches current user info
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    # PATCH /api/profiles/me/score/  <-- Game completion score update (uses delta)
    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def score(self, request):
        serializer = UserProfileUpdateScoreSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                profile = UserProfile.objects.select_for_update().get(user=request.user)
                serializer.update(profile, serializer.validated_data)
                logger.info(
                    "Score updated: user=%s delta=%s new_score=%s",
                    request.user.username, serializer.validated_data['delta'], profile.score
                )
                return Response({'score': profile.score})
        return Response(serializer.errors, status=400)

    # PUT /api/profiles/me/  <-- 更新个人资料
    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        user = request.user
        profile = user.profile

        # 更新邮箱
        email = request.data.get('email')
        if email is not None:
            user.email = email
            user.save(update_fields=['email'])

        return Response(UserInfoSerializer(user).data)

    # POST /api/profiles/me/avatar/  <-- 上传头像
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='me/avatar')
    def upload_avatar(self, request):
        profile = request.user.profile
        serializer = UserAvatarUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'avatar': request.build_absolute_uri(profile.avatar.url) if profile.avatar else None,
                'message': '头像上传成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 7. 科普文章视图 /api/articles/
# ==========================================
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # 禁用分页，确保前端分类筛选能看到所有文章

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def view(self, request, pk=None):
        article = self.get_object()
        with transaction.atomic():
            Article.objects.filter(pk=article.pk).update(views=F('views') + 1)
            article.refresh_from_db()
        logger.info("Article viewed: id=%s title=%s views=%s", article.pk, article.title, article.views)
        return Response({'views': article.views})


# ==========================================
# 6. 普通页面视图 (热点推荐)
# ==========================================
def index_view(request):
    return render(request, 'index.html')


def get_todays_hotspot(request):
    three_days_ago = timezone.now().date() - timedelta(days=3)

    # 只统计 '已通过' (approved) 的记录
    hot_zone_data = ObservationRecord.objects.filter(
        observation_time__gte=three_days_ago,
        status='approved'
    ).values('zone').annotate(total_count=Sum('count')).order_by('-total_count').first()

    recommendation_data = {}

    if hot_zone_data and hot_zone_data['zone']:
        try:
            zone = WetlandZone.objects.get(id=hot_zone_data['zone'])
            # 获取最新且已通过的记录
            latest_record = ObservationRecord.objects.filter(
                zone=zone,
                status='approved'
            ).order_by('-observation_time').first()

            bird_name = "珍稀鸟类"
            if latest_record and latest_record.species:
                bird_name = latest_record.species.name_cn

            tips = getattr(zone, 'observation_tips', "请保持安全距离观赏")

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
    return {
        "title": "今日推荐：郑州黄河湿地中段",
        "tips": "保持100米以上距离，避免干扰",
        "location": "黄河湿地"
    }