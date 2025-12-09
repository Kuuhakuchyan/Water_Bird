from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ObservationRecord, UserProfile


@receiver(post_save, sender=ObservationRecord)
def award_points_on_approval(sender, instance, created, **kwargs):
    """
    当观测记录被保存，且状态变为 '1' (审核通过) 时，给用户加分
    """
    # 只有当状态是审核通过(1) 且 有具体的上报人时才加分
    # 注意：请确保 models.py 中 ObservationRecord 有 status 字段且 '1' 代表通过
    # 这里的 str(instance.status) == '1' 是为了兼容 status 可能是字符或数字的情况
    if hasattr(instance, 'status') and str(instance.status) == '1' and instance.reporter:
        # 获取或创建用户档案
        profile, _ = UserProfile.objects.get_or_create(user=instance.reporter)

        POINTS_PER_RECORD = 10

        # 简单累加积分
        profile.points += POINTS_PER_RECORD
        profile.save()

        print(f"用户 {instance.reporter.username} 贡献有效数据，获得 {POINTS_PER_RECORD} 积分！")

        # 检查是否满足兑换条件
        if profile.points >= 500:
            print("恭喜！您已满足兑换【郑州湿地观鸟指南（纸质版）】的条件")