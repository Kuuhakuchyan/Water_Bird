from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.shortcuts import render
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from app_monitor.views import (
    ObservationViewSet, ZoneViewSet, TransectViewSet,
    index_view, UserProfileViewSet, RegisterViewSet,
    SpeciesViewSet, ArticleViewSet, ProductViewSet,
)

# === 1. 注册 API 路由 ===
router = DefaultRouter()
router.register(r'species', SpeciesViewSet)
router.register(r'observations', ObservationViewSet, basename='observation')
router.register(r'zones', ZoneViewSet)
router.register(r'transects', TransectViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'auth', RegisterViewSet, basename='auth')
router.register(r'articles', ArticleViewSet)
router.register(r'products', ProductViewSet)

# === 2. 定义 URL 模式 ===
urlpatterns = [
    # 首页
    path('', index_view, name='home'),

    # 观鸟上报表单页面
    path('report/', lambda r: render(r, 'report.html'), name='report'),

    # 个人中心页面
    path('profile/', lambda r: render(r, 'profile.html'), name='profile'),

    # 游戏页面
    path('bird-guess/', lambda r: render(r, 'bird-guess.html'), name='bird_guess'),
    path('bird-runner/', lambda r: render(r, 'bird-runner.html'), name='bird_runner'),
    path('wetland-restorer/', lambda r: render(r, 'wetland-restorer.html'), name='wetland_restorer'),
    path('migration/', lambda r: render(r, 'migration.html'), name='migration'),
    path('wetland-detective/', lambda r: render(r, 'wetland-detective.html'), name='wetland_detective'),
    path('floating-island/', lambda r: render(r, 'floating-island.html'), name='floating_island'),

    # 物种百科（含详情页）
    path('species/', lambda r: render(r, 'species.html'), name='species'),
    re_path(r'^species/(?P<species_id>\d+)/$', lambda r, species_id: render(r, 'species-detail.html'), name='species_detail'),

    # 科普文章（含详情页）
    path('articles/', lambda r: render(r, 'articles.html'), name='articles'),
    re_path(r'^articles/(?P<article_id>\d+)/$', lambda r, article_id: render(r, 'article-detail.html'), name='article_detail'),

    # 登录页面
    path('login/', lambda r: render(r, 'login.html'), name='login'),

    # 管理后台
    path('admin/', admin.site.urls),

    # API 接口
    path('api/', include(router.urls)),

    # 登录接口（Token 认证）
    path('api/login/', obtain_auth_token, name='api_token_auth'),
]

# === 3. 核心修复：强制让 Django 处理静态文件 ===
# 这部分代码解决了 Gunicorn 下 Admin 后台没有样式的问题
# 它会拦截 /static/ 和 /media/ 开头的请求，并直接返回文件
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]