from django.apps import AppConfig

class AppMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Water_Bird.app_monitor'
    verbose_name = '湿地监测系统'  # 【汉化关键】左侧菜单一级标题

    def ready(self):
        import Water_Bird.app_monitor.signals