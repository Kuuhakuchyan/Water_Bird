import random
from .models import SpeciesInfo


def smart_identify_bird(image_file):
    """
    模拟 AI 识别服务
    实际部署时，这里会调用 PyTorch/TensorFlow 加载的模型
    """
    # 1. 模拟模型推理 (耗时 < 5秒)
    # 假设模型识别出这张图是 "白头鹤"
    predicted_bird_name = "白头鹤"
    confidence = 0.92  # 模拟置信度 > 85%

    # 2. 查询数据库获取“郑州本地化习性”
    try:
        bird_info = SpeciesInfo.objects.get(name_cn=predicted_bird_name)
        habit = bird_info.distribution_habit
        # 如果数据库里是空的，就给个默认值
        if not habit:
            habit = "郑州湿地主要越冬区为花园口段"
    except SpeciesInfo.DoesNotExist:
        habit = "暂无本地分布数据"

    return {
        "species": predicted_bird_name,
        "confidence": f"{confidence * 100}%",
        "habit": habit,
        "message": "识别成功，满足观鸟爱好者需求"
    }