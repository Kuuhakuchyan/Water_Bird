from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import ObservationRecord, SpeciesInfo, AIDetectionResult, WetlandZone


# 1. 设置内联显示 (保持不变)
class AIResultInline(admin.TabularInline):
    model = AIDetectionResult
    extra = 0
    readonly_fields = ('confidence', 'count')


# 2. 观测记录管理 (升级为 Leaflet 地图)
@admin.register(ObservationRecord)
class ObservationRecordAdmin(LeafletGeoAdmin):
    list_display = ('id_short', 'user', 'upload_time', 'ai_verified')
    list_filter = ('ai_verified', 'upload_time')
    inlines = [AIResultInline]

    # 启用 Leaflet 的高级编辑功能
    settings_overrides = {
        'DEFAULT_CENTER': (34.90, 113.65),
        'DEFAULT_ZOOM': 11,
    }

    def id_short(self, obj):
        return str(obj.id)[:8]

    id_short.short_description = "记录ID"

    # === 关键修改：引入自定义 CSS (加了版本号 v=2.0 强制刷新) ===
    class Media:
        css = {
            'all': ('app_monitor/css/admin_custom.css?v=2.0',)
        }


# 3. 湿地分区管理 (升级为 Leaflet 地图)
@admin.register(WetlandZone)
class WetlandZoneAdmin(LeafletGeoAdmin):
    list_display = ('name', 'zone_type')

    # === 关键修改：引入自定义 CSS (加了版本号 v=2.0 强制刷新) ===
    class Media:
        css = {
            'all': ('app_monitor/css/admin_custom.css?v=2.0',)
        }


# 4. 物种库管理 (普通表，保持不变)
@admin.register(SpeciesInfo)
class SpeciesInfoAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'protected_level')