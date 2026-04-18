from django.apps import AppConfig

class AppMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_monitor'
    verbose_name = '湿地监测系统'  # 【汉化关键】左侧菜单一级标题

    def ready(self):
        # 确保信号加载，用于积分自动发放
        import app_monitor.signals