"""
插入黄河湿地模拟观测数据，包含多种珍稀鸟类和不同区域
"""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from app_monitor.models import (
    SpeciesInfo, WetlandZone, ObservationRecord, Article
)


ZONES = [
    {"name": "黄河湿地中段", "lat": 34.82, "lng": 113.55},
    {"name": "花园口监测点", "lat": 34.87, "lng": 113.62},
    {"name": "黄河公路桥段", "lat": 34.79, "lng": 113.48},
    {"name": "湿地保育区", "lat": 34.85, "lng": 113.58},
    {"name": "黄河鸟类栖息地A", "lat": 34.90, "lng": 113.65},
    {"name": "黄河鸟类栖息地B", "lat": 34.76, "lng": 113.42},
    {"name": "生态修复示范区", "lat": 34.88, "lng": 113.52},
    {"name": "黄河湿地北段", "lat": 34.95, "lng": 113.70},
]

SPECIES = [
    {"name_cn": "大天鹅", "name_latin": "Cygnus cygnus", "order": "雁形目", "family": "鸭科",
     "protection_level": "国家二级", "distribution_habit": "每年10月至次年3月在此越冬，常成群活动于开阔水域。"},
    {"name_cn": "白鹭", "name_latin": "Egretta garzetta", "order": "鹈形目", "family": "鹭科",
     "protection_level": "三有动物", "distribution_habit": "全年可见，常在浅水中觅食，繁殖期成对活动。"},
    {"name_cn": "鸿雁", "name_latin": "Anser cygnoides", "order": "雁形目", "family": "鸭科",
     "protection_level": "国家二级", "distribution_habit": "迁徙季节途经此地，夜间集群休息。"},
    {"name_cn": "黑鹳", "name_latin": "Ciconia nigra", "order": "鹳形目", "family": "鹳科",
     "protection_level": "国家一级", "distribution_habit": "珍稀夏候鸟，繁殖期4-7月，对水质要求极高。"},
    {"name_cn": "东方白鹳", "name_latin": "Ciconia boyciana", "order": "鹳形目", "family": "鹳科",
     "protection_level": "国家一级", "distribution_habit": "全球濒危物种，在此有稳定越冬种群。"},
    {"name_cn": "灰鹤", "name_latin": "Grus grus", "order": "鹤形目", "family": "鹤科",
     "protection_level": "国家二级", "distribution_habit": "大型涉禽，每年10月大批迁来，集群觅食。"},
    {"name_cn": "普通鸬鹚", "name_latin": "Phalacrocorax carbo", "order": "鲣鸟目", "family": "鸬鹚科",
     "protection_level": "三有动物", "distribution_habit": "擅长潜水捕鱼，常在树枝上晾翅。"},
    {"name_cn": "斑嘴鸭", "name_latin": "Anas zonorhyncha", "order": "雁形目", "family": "鸭科",
     "protection_level": "三有动物", "distribution_habit": "常见野鸭，常与其他鸭类混群活动。"},
    {"name_cn": "白头鹤", "name_latin": "Grus monacha", "order": "鹤形目", "family": "鹤科",
     "protection_level": "国家一级", "distribution_habit": "全球数量稀少，在此有重要越冬地。"},
    {"name_cn": "豆雁", "name_latin": "Anser fabalis", "order": "雁形目", "family": "鸭科",
     "protection_level": "三有动物", "distribution_habit": "迁徙季节常见，成V字队形飞行。"},
    {"name_cn": "苍鹭", "name_latin": "Ardea cinerea", "order": "鹈形目", "family": "鹭科",
     "protection_level": "三有动物", "distribution_habit": "大型鹭类，站立不动伺机捕鱼，俗称老等。"},
    {"name_cn": "绿头鸭", "name_latin": "Anas platyrhynchos", "order": "雁形目", "family": "鸭科",
     "protection_level": "三有动物", "distribution_habit": "家鸭祖先，常见且适应性强，全年活动。"},
]

ARTICLES = [
    {
        "title": "黄河湿地黑鹳：空中大熊猫的守护之路",
        "summary": "黑鹳是国家一级保护动物，全球数量不足3000只。黄河湿地是它们重要的迁徙通道，本文讲述科研人员如何追踪和保护这一珍稀物种。",
        "content": "黑鹳（Ciconia nigra）是一种体态优美、性情机警的大型涉禽，被列入世界自然保护联盟濒危物种红色名录濒危等级。在我国，黑鹳被定为国家一级重点保护野生动物，因其稀有程度和科研价值，被称为空中的大熊猫。\n\n黄河湿地郑州段是黑鹳重要的迁徙停歇地。每年春季3-4月和秋季9-10月，大批黑鹳会途经此地，补充能量后继续北飞或南迁。近年来，随着当地生态保护力度加大，黑鹳在此停留的时间明显延长，部分个体甚至留下来越冬。\n\n保护措施：\n1. 建立黑鹳保护区，限制人类活动干扰\n2. 实施湿地生态修复，扩大浅水觅食区\n3. 开展黑鹳卫星追踪研究，掌握迁徙规律\n4. 加强宣传，提高公众保护意识",
        "views": 342
    },
    {
        "title": "观鸟入门：如何在黄河湿地识别常见水鸟",
        "summary": "黄河湿地是中部地区重要的水鸟栖息地。本文介绍12种常见水鸟的识别特征，让你从小白快速进阶。",
        "content": "黄河湿地生物多样性丰富，是中部地区最重要的水鸟栖息地之一。以下是12种最常见的水鸟识别指南：\n\n1. 白鹭（Egretta garzetta）\n   识别特征：全身雪白，嘴黑色，腿黑色但趾黄绿色。常在浅水中涉行，捕食小鱼。\n\n2. 苍鹭（Ardea cinerea）\n   识别特征：体型大，灰色调，头顶有黑色冠羽。站立不动等待猎物，俗称老等。\n\n3. 绿头鸭（Anas platyrhynchos）\n   识别特征：雄鸭头颈绿色，具白色颈环；雌鸭全身褐色带深色斑纹。\n\n4. 斑嘴鸭（Anas zonorhyncha）\n   识别特征：嘴黑色而端黄，整体棕褐色。\n\n5. 大天鹅（Cygnus cygnus）\n   识别特征：全身白色，嘴黑而基部黄斑，体型硕大。飞翔时可见黑色飞羽。\n\n6. 灰鹤（Grus grus）\n   识别特征：通体灰色，头颈黑色，眼后有白色条纹延伸至下体。",
        "views": 567
    },
    {
        "title": "黄河湿地生态修复：从盐碱荒滩到鸟类天堂",
        "summary": "过去十年，黄河湿地经历了从退化到修复的转变。本文回顾生态修复历程，展望湿地保护未来。",
        "content": "黄河湿地郑州段曾面临严重的生态退化问题。过度农业开发、挖沙取土、工业排污导致湿地面积锐减，水质恶化，鸟类种类和数量大幅下降。\n\n2015年起，郑州市启动黄河湿地生态修复工程：\n\n1. 清退违规建设项目，恢复湿地水面\n2. 种植本土水生植物，净化水质\n3. 建设生态隔离带，减少人为干扰\n4. 恢复浅水漫滩，为涉禽提供觅食场所\n\n修复成效：\n- 湿地面积恢复至历史较高水平\n- 水质从劣V类提升至III类\n- 鸟类记录从68种增加到127种\n- 国家一级保护鸟类从2种增加到5种",
        "views": 289
    },
    {
        "title": "候鸟迁徙：跨越洲际的奇妙旅程",
        "summary": "每年春秋，数百万候鸟跨越千山万水迁徙。黄河湿地为何成为它们的必经之路？",
        "content": "候鸟迁徙是自然界最壮观的生命现象之一。每年春秋两季，数以百万计的鸟类沿着东亚-澳大利亚西亚迁飞路线往返繁殖地和越冬地。\n\n黄河中下游湿地正处于这条迁徙路线的关键节点。\n\n为什么候鸟偏爱黄河湿地？\n1. 地理位置优越：正好处于南北迁徙路线的中间\n2. 食物资源丰富：浅水湿地适合涉禽觅食\n3. 隐蔽条件好：宽阔的芦苇荡提供栖息场所\n4. 干扰相对较少：周边社区保护意识增强\n\n鸟类导航的奥秘：\n鸟类依靠太阳、星星、地磁场甚至嗅觉进行导航。研究发现，部分鸟类能感知地球磁场并将其作为内置GPS。",
        "views": 421
    },
]


class Command(BaseCommand):
    help = "插入黄河湿地模拟观测数据"

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='清空现有模拟数据后再插入')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('正在清空旧数据...')
            ObservationRecord.objects.all().delete()
            SpeciesInfo.objects.all().delete()
            WetlandZone.objects.all().delete()
            Article.objects.filter(title__in=[a['title'] for a in ARTICLES]).delete()
            self.stdout.write(self.style.WARNING('  已清空所有相关数据'))

        user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@test.com'}
        )

        self.stdout.write('正在插入物种数据...')
        species_map = {}
        for sp in SPECIES:
            obj, created = SpeciesInfo.objects.get_or_create(
                name_cn=sp['name_cn'],
                defaults={
                    'name_latin': sp['name_latin'],
                    'order': sp['order'],
                    'family': sp['family'],
                    'protection_level': sp['protection_level'],
                    'distribution_habit': sp['distribution_habit'],
                }
            )
            species_map[sp['name_cn']] = obj
            if created:
                self.stdout.write('  + %s (%s)' % (sp['name_cn'], sp['protection_level']))

        self.stdout.write('正在插入监测区域...')
        zone_map = {}
        for z in ZONES:
            obj, created = WetlandZone.objects.get_or_create(
                name=z['name'],
                defaults={
                    'latitude': z['lat'],
                    'longitude': z['lng'],
                    'is_hotspot': random.random() < 0.3,
                    'observation_tips': '保持100米以上距离，避免干扰鸟类正常活动。',
                }
            )
            zone_map[z['name']] = obj
            if created:
                self.stdout.write('  + %s (%.4f, %.4f)' % (z['name'], z['lat'], z['lng']))

        self.stdout.write('正在插入科普文章...')
        admin = User.objects.filter(is_staff=True).first() or user
        for a in ARTICLES:
            obj, created = Article.objects.get_or_create(
                title=a['title'],
                defaults={
                    'summary': a['summary'],
                    'content': a['content'],
                    'author': admin,
                    'views': a['views'],
                    'is_published': True,
                }
            )
            if created:
                self.stdout.write('  + %s' % a['title'])

        self.stdout.write('正在插入观测记录...')
        now = timezone.now().date()
        records_created = 0

        for species_name, species_obj in species_map.items():
            sampled_zones = random.sample(
                list(zone_map.values()),
                min(len(zone_map), random.randint(3, 6))
            )
            for zone_obj in sampled_zones:
                record_count = random.randint(2, 5)
                for i in range(record_count):
                    days_ago = random.randint(0, 60)
                    obs_date = now - timedelta(days=days_ago)
                    count = random.choice([1, 2, 2, 3, 3, 5, 5, 8, 10, 15])
                    status = random.choices(
                        ['approved', 'pending', 'rejected'],
                        weights=[0.75, 0.20, 0.05]
                    )[0]

                    _, created = ObservationRecord.objects.get_or_create(
                        species=species_obj,
                        zone=zone_obj,
                        observation_time=obs_date,
                        defaults={
                            'count': count,
                            'status': status,
                            'uploader': user,
                            'description': '%s观测记录，于%s在%s观测到%d只。' % (
                                species_obj.name_cn, obs_date, zone_obj.name, count),
                        }
                    )
                    if created:
                        records_created += 1

        self.stdout.write(self.style.SUCCESS(
            '\n模拟数据插入完成！\n'
            '  物种: %d 种\n'
            '  区域: %d 个\n'
            '  文章: %d 篇\n'
            '  记录: %d 条\n\n'
            '测试账号: testuser / test123456'
            % (len(species_map), len(zone_map), len(ARTICLES), records_created)
        ))
