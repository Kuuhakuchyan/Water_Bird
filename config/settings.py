import os
from pathlib import Path

# 构建路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥 (开发环境)
SECRET_KEY = 'django-insecure-custom-key-for-xuan'
DEBUG = True
ALLOWED_HOSTS = ['*']

# === 1. 应用注册 (SimpleUI 必须在最前) ===
INSTALLED_APPS = [
    'simpleui',  # 后台美化主题 (必须是第一行)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # GIS 与 API 核心库
    'django.contrib.gis',  # GeoDjango 核心
    'rest_framework',  # API 接口框架
    'rest_framework_gis',
    'import_export',  # 导入导出支持
    'leaflet',  # GIS 后台地图控件
    'corsheaders',
    'app_monitor',  # 我们的监控 App
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 【汉化关键】必须添加 LocaleMiddleware，且放在 Session 之后，Common 之前
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# === 2. PostGIS 数据库配置 ===
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'Yellow River',  # 数据库名
        'USER': 'postgres',
        'PASSWORD': '111111',  # 您的密码
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# === 3. 环境变量配置 (Windows GDAL 修复) ===
# 注意：如果您更新了 OSGeo4W，gdal312.dll 里的数字可能会变，请留意
OSGEO4W_ROOT = r"C:\Users\Xuan\AppData\Local\Programs\OSGeo4W"

# 关键：修复 PROJ 路径，避免 OGR failure
os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, "share", "proj")
os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, "bin") + ";" + os.environ['PATH']

GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, "bin", "gdal312.dll")
GEOS_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, "bin", "geos_c.dll")
os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_ROOT, "share", "gdal")

# === 4. 品牌与文件配置 ===
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
# 增加 STATIC_ROOT 以支持 collectstatic 命令 (部署时需要)
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === 5. GIS 配置 ===
TDT_KEY = '0de0375367832014891a9f40e0e42911'

LEAFLET_CONFIG = {
    # 1. 默认视野 (郑州)
    'DEFAULT_CENTER': (34.75, 113.62),
    'DEFAULT_ZOOM': 10,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
    'RESET_VIEW': False,
    'SCALE': 'metric',
    'ATTRIBUTION_PREFIX': 'Powered by Django-Leaflet & Tianditu',

    # 2. 底图配置 (TILES)
    'TILES': [
        (
            '天地图矢量底图',  # 1. 名称
            f'http://t0.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={{z}}&TILEROW={{y}}&TILECOL={{x}}&tk={TDT_KEY}',
            # 2. URL
            {'attribution': '天地图'}  # 3. 参数(不能为空)
        ),
        (
            '天地图卫星影像',
            f'http://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={{z}}&TILEROW={{y}}&TILECOL={{x}}&tk={TDT_KEY}',
            {'attribution': '天地图'}
        ),
    ],

    # 3. 叠加层配置 (OVERLAYS)
    'OVERLAYS': [
        (
            '天地图地名注记(文字)',
            f'http://t0.tianditu.gov.cn/cva_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={{z}}&TILEROW={{y}}&TILECOL={{x}}&tk={TDT_KEY}',
            {'attribution': '天地图'}
        ),
        (
            '卫星图注记(文字)',
            f'http://t0.tianditu.gov.cn/cia_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cia&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={{z}}&TILEROW={{y}}&TILECOL={{x}}&tk={TDT_KEY}',
            {'attribution': '天地图'}
        ),
    ],
}

# === 6. SimpleUI 后台美化配置 ===
SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False
SIMPLEUI_LOGO = 'https://cdn-icons-png.flaticon.com/512/2913/2913520.png'
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'

# 【汉化界面标题】
SIMPLEUI_HOME_TITLE = '黄河生态监测平台'  # 浏览器标签页标题
SIMPLEUI_SITE_TITLE = '黄河生态监测平台'  # 登录页/顶部标题
SIMPLEUI_INDEX_TITLE = '监测系统后台'    # 首页标题

SIMPLEUI_ICON = {
    '物种信息': 'fas fa-dove',  # 修改为更准确的鸟类图标
    '观测记录': 'fas fa-binoculars',  # 修改为望远镜
    '监测点位': 'fas fa-map-marker-alt',
    '监测样线': 'fas fa-route',
    '模型识别记录': 'fas fa-robot',
    '用户积分档案': 'fas fa-user-circle',
    '认证和授权': 'fas fa-shield-alt',
}