import os
from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource  # 引入这个工具帮您看列名
from app_monitor.models import WetlandZone, MonitoringRoute


class Command(BaseCommand):
    help = '导入中文名称的 SHP 文件（自动侦测列名版）'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        shp_dir = os.path.join(base_dir, 'data')

        print(f"📂 正在文件夹中寻找数据: {shp_dir}")

        # ==========================================
        # 1. 配置中文文件名 (这里改成了您刚才提供的名字)
        # ==========================================
        # 注意：.prj 是附属文件，代码里必须写 .shp
        point_file = '水鸟监测点.shp'
        route_file = '水鸟监测样线.shp'

        point_path = os.path.join(shp_dir, point_file)
        route_path = os.path.join(shp_dir, route_file)

        # ====================
        # 2. 开始处理监测点位
        # ====================
        if os.path.exists(point_path):
            print(f"\n🔍 发现点位文件: {point_file}")

            # --- 智能侦测：先看看您的 SHP 里到底有哪些列 ---
            try:
                ds = DataSource(point_path)
                layer = ds[0]
                print(f"ℹ️  SHP文件包含的列名有: {layer.fields}")

                # 猜测：如果列名里有 'Name' 就用 'Name'，如果有 '名称' 就用 '名称'
                shp_field_name = 'Name'  # 默认猜它叫 Name
                if '名称' in layer.fields:
                    shp_field_name = '名称'
                elif 'name' in layer.fields:  # 小写的情况
                    shp_field_name = 'name'

                print(f"🎯 决定使用 '{shp_field_name}' 这一列作为点位名称")

                # 定义映射
                zone_mapping = {
                    'name': shp_field_name,  # 动态使用刚才侦测到的列名
                    'location': 'POINT',
                }

                lm = LayerMapping(WetlandZone, point_path, zone_mapping, transform=True, encoding='utf-8')
                lm.save(strict=True, verbose=True)
                print("✅ 监测点位导入成功！")

            except Exception as e:
                print(f"❌ 点位导入失败: {e}")
        else:
            print(f"⚠️  未找到文件: {point_file} (请确认它在 data 文件夹里)")

        # ====================
        # 3. 开始处理监测样线
        # ====================
        if os.path.exists(route_path):
            print(f"\n🔍 发现样线文件: {route_file}")

            try:
                ds = DataSource(route_path)
                layer = ds[0]
                print(f"ℹ️  SHP文件包含的列名有: {layer.fields}")

                # 同样进行智能猜测
                shp_field_name = 'Name'
                if '名称' in layer.fields:
                    shp_field_name = '名称'
                elif 'name' in layer.fields:
                    shp_field_name = 'name'
                elif 'Id' in layer.fields:
                    shp_field_name = 'Id'

                print(f"🎯 决定使用 '{shp_field_name}' 这一列作为路线名称")

                route_mapping = {
                    'name': shp_field_name,
                    'path_geom': 'MULTILINESTRING',  # 这里的类型很重要
                }

                lm = LayerMapping(MonitoringRoute, route_path, route_mapping, transform=True, encoding='utf-8')
                lm.save(strict=True, verbose=True)
                print("✅ 监测样线导入成功！")

            except Exception as e:
                print(f"❌ 样线导入失败: {e}")
                print("💡 提示：如果报错 Geometry type does not match，请告诉我 SHP 的几何类型是啥")
        else:
            print(f"⚠️  未找到文件: {route_file}")

        print("\n🏁 程序运行结束")