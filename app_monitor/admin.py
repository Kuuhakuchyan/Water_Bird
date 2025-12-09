from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import SpeciesInfo, WetlandZone, MonitoringRoute, UserProfile, ObservationRecord, AIDetectionResult
from datetime import datetime

# ====================
# 0. 全局后台配置
# ====================
admin.site.site_header = '湿地监测管理后台'
admin.site.site_title = '湿地监测系统'
admin.site.index_title = '系统管理'


# ====================
# 1. 资源映射配置 (超级导入版)
# ====================

# (1) 观测记录导入配置 (核心：一次性导入所有信息)
class ObservationRecordResource(resources.ModelResource):
    # 定义 Excel 列名与数据库外键的对应
    species = fields.Field(column_name='中文名', attribute='species', widget=ForeignKeyWidget(SpeciesInfo, 'name_cn'))
    zone = fields.Field(column_name='loc', attribute='zone', widget=ForeignKeyWidget(WetlandZone, 'name'))

    # 映射简单字段
    observation_time = fields.Field(attribute='observation_time', column_name='date')
    count = fields.Field(attribute='count', column_name='abundance')

    class Meta:
        model = ObservationRecord
        # 即使 Excel 里没有 ID，我们用这三个字段组合来判断唯一性，防止重复
        import_id_fields = ('species', 'zone', 'observation_time')
        # 声明要导入的字段
        fields = ('species', 'zone', 'observation_time', 'count')
        exclude = ('id',)

    # 【核心逻辑】：在导入每一行之前，先把 物种 和 点位 处理好
    def before_import_row(self, row, **kwargs):
        # --- A. 处理日期格式 (解决 2022/12/11 报错) ---
        date_str = str(row.get('date', '')).strip()
        if '/' in date_str:
            try:
                # 把 2022/12/11 转换成 2022-12-11
                dt = datetime.strptime(date_str, '%Y/%m/%d')
                row['date'] = dt.strftime('%Y-%m-%d')
            except ValueError:
                pass  # 如果转换失败，就让它按原样报错提示

        # --- B. 自动保存物种信息 (目、科、保护级别) ---
        name_cn = str(row.get('中文名', '')).strip()
        row['中文名'] = name_cn  # 去空格

        if name_cn:
            # 准备要更新/创建的数据
            species_defaults = {
                'name_latin': str(row.get('species', '')).strip(),
                'order': str(row.get('目', '')).strip(),
                'family': str(row.get('科', '')).strip(),
                'protection_level': str(row.get('保护级别', '')).strip()
            }
            # 如果 '保护级别' 是空的 (NaN)，存为 "无" 或空字符串
            if species_defaults['protection_level'] in ['nan', 'NaN', 'None']:
                species_defaults['protection_level'] = ''

            # 强行更新或创建物种 (保证数据库里一定有这个鸟，且信息是最新的)
            SpeciesInfo.objects.update_or_create(
                name_cn=name_cn,
                defaults=species_defaults
            )

        # --- C. 自动保存点位信息 (经纬度) ---
        loc_name = str(row.get('loc', '')).strip()
        row['loc'] = loc_name  # 去空格

        if loc_name:
            # 尝试提取经纬度
            try:
                x_val = float(row.get('x'))
                y_val = float(row.get('y'))
            except (ValueError, TypeError):
                x_val, y_val = None, None

            zone_defaults = {}
            if x_val is not None and y_val is not None:
                zone_defaults['longitude'] = x_val
                zone_defaults['latitude'] = y_val

            # 强行更新或创建点位
            WetlandZone.objects.update_or_create(
                name=loc_name,
                defaults=zone_defaults
            )


# (2) 其他简单的 Resource (保留以备单独导入使用)
class WetlandZoneResource(resources.ModelResource):
    name = fields.Field(attribute='name', column_name='loc')
    longitude = fields.Field(attribute='longitude', column_name='x')
    latitude = fields.Field(attribute='latitude', column_name='y')

    class Meta:
        model = WetlandZone
        import_id_fields = ('name',)
        fields = ('name', 'longitude', 'latitude')


class SpeciesInfoResource(resources.ModelResource):
    name_cn = fields.Field(attribute='name_cn', column_name='中文名')

    class Meta:
        model = SpeciesInfo
        import_id_fields = ('name_cn',)


# ====================
# 2. 管理后台注册
# ====================

@admin.register(SpeciesInfo)
class SpeciesInfoAdmin(ImportExportModelAdmin):
    resource_class = SpeciesInfoResource
    list_display = ('name_cn', 'name_latin', 'order', 'family', 'protection_level')
    search_fields = ('name_cn', 'name_latin')
    list_filter = ('protection_level', 'order')


@admin.register(WetlandZone)
class WetlandZoneAdmin(LeafletGeoAdmin, ImportExportModelAdmin):
    resource_class = WetlandZoneResource
    list_display = ('name', 'longitude', 'latitude')
    search_fields = ('name',)
    settings_overrides = {'DEFAULT_CENTER': (34.75, 113.62), 'DEFAULT_ZOOM': 10}


@admin.register(ObservationRecord)
class ObservationRecordAdmin(ImportExportModelAdmin):
    resource_class = ObservationRecordResource
    # 显示所有关键信息
    list_display = ('species', 'zone', 'observation_time', 'count', 'status')
    list_filter = ('status', 'observation_time', 'zone')
    search_fields = ('species__name_cn', 'zone__name')
    date_hierarchy = 'observation_time'

    actions = ['approve_records', 'reject_records']

    def approve_records(self, request, queryset):
        queryset.update(status=1)

    approve_records.short_description = "批量审核通过"

    def reject_records(self, request, queryset):
        queryset.update(status=2)

    reject_records.short_description = "批量驳回"


# 其他注册
@admin.register(MonitoringRoute)
class MonitoringRouteAdmin(LeafletGeoAdmin):
    list_display = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points')


@admin.register(AIDetectionResult)
class AIDetectionResultAdmin(admin.ModelAdmin):
    list_display = ('species_name', 'confidence', 'created_at')