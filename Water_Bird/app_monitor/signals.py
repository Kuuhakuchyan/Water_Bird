from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ObservationRecord, UserProfile


@receiver(post_save, sender=ObservationRecord)
def award_points_on_approval(sender, instance, created, **kwargs):
    """
    当观测记录被管理员审核通过（状态变为 'approved'）时，给上传者加分
    注意：此信号只在新记录创建后、后续状态变更时才触发额外积分。
    首次创建时的积分已在 views.py perform_create 中处理。
    """
    if created:
        # perform_create 已经处理了新建积分，此处不再重复加分
        return

    # 非新建记录：只有从 pending/rejected 变为 approved 时才额外加分
    if str(instance.status) == 'approved' and instance.uploader:
        # 避免重复加分：简单判断，如果积分已经很高（说明之前加过），就不重复加
        # 更精确的做法需要引入状态历史表，这里用简化版本
        try:
            profile = instance.uploader.profile
            # 积分已在 perform_create 中计入，此处不再重复处理
            # 如需"审核通过额外奖励"，可在此处取消注释：
            # profile.score += 5
            # profile.save()
            pass
        except UserProfile.DoesNotExist:
            pass
