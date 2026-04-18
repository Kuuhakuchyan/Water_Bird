from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app_monitor.models import (
    SpeciesInfo, WetlandZone, MonitoringRoute,
    UserProfile, ObservationRecord, Product, Article, ExchangeRecord
)
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = '添加模拟数据来测试系统功能（不修改任何数据库结构）'

    def handle(self, *args, **options):
        self.stdout.write('=== 开始添加模拟数据 ===\n')

        # 1. 管理员/测试用户
        # 注意: UserProfile 会通过 Django 信号自动创建，这里只需要确保用户存在
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True, 'email': 'admin@test.com'}
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        # 信号已自动创建 UserProfile，只需确保积分正确
        profile, _ = UserProfile.objects.get_or_create(user=admin)
        profile.score = 500
        profile.save()
        self.stdout.write(f'  管理员: admin / admin123 (积分: {profile.score})\n')

        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'is_staff': False, 'email': 'test@test.com'}
        )
        if created:
            test_user.set_password('test123')
            test_user.save()
        # 信号已自动创建 UserProfile
        profile2, _ = UserProfile.objects.get_or_create(user=test_user)
        if created:
            profile2.score = 120
            profile2.save()
        self.stdout.write(f'  测试用户: testuser / test123 (积分: {profile2.score})\n')

        # 2. 物种数据
        species_list = [
            ('大天鹅', 'Cygnus cygnus', '雁形目', '鸭科', '国家二级保护', '雁鸭类，冬季常在开阔水域集群越冬。'),
            ('小天鹅', 'Cygnus columbianus', '雁形目', '鸭科', '国家二级保护', '体型比大天鹅小，喙部黄色区域较少。'),
            ('白鹤', 'Grus leucogeranus', '鹤形目', '鹤科', '国家一级保护', '全球濒危物种，迁徙途经此地。'),
            ('灰鹤', 'Grus grus', '鹤形目', '鹤科', '国家二级保护', '北方繁殖，南方越冬，种群稳定。'),
            ('东方白鹳', 'Ciconia boyciana', '鹳形目', '鹳科', '国家一级保护', '大型涉禽，喜在湿地浅水区觅食。'),
            ('黑鹳', 'Ciconia nigra', '鹳形目', '鹳科', '国家一级保护', '体羽以黑色为主，腹部白色，珍稀鸟类。'),
            ('白头鹤', 'Grus monacha', '鹤形目', '鹤科', '国家一级保护', '头顶白色，体灰色，湿地繁殖。'),
            ('丹顶鹤', 'Grus japonensis', '鹤形目', '鹤科', '国家一级保护', '中国著名珍禽，繁殖于东北湿地。'),
            ('豆雁', 'Anser fabalis', '雁形目', '鸭科', '三有保护', '大型雁类，秋季迁徙集群，数量众多。'),
            ('鸿雁', 'Anser cygnoides', '雁形目', '鸭科', '国家二级保护', '著名家鹅祖先，湿地草丛中觅食。'),
            ('绿头鸭', 'Anas platyrhynchos', '雁形目', '鸭科', '三有保护', '最常见的野鸭，适应能力强。'),
            ('斑嘴鸭', 'Anas zonorhyncha', '雁形目', '鸭科', '三有保护', '喙端黑色，喜静水环境。'),
            ('普通鸬鹚', 'Phalacrocorax carbo', '鲣鸟目', '鸬鹚科', '三有保护', '潜水捕鱼高手，湿地常见留鸟。'),
            ('大白鹭', 'Ardea alba', '鹈形目', '鹭科', '三有保护', '全身雪白，繁殖期具饰羽。'),
            ('苍鹭', 'Ardea cinerea', '鹈形目', '鹭科', '三有保护', '大型鹭类，俗称"老等"，喜在浅水站立。'),
            ('普通翠鸟', 'Alcedo atthis', '佛法僧目', '翠鸟科', '三有保护', '羽色艳丽，俯冲入水捕鱼。'),
            ('黑翅长脚鹬', 'Himantopus himantopus', '鸻形目', '反嘴鹬科', '三有保护', '腿长红色，黑色翅膀，优雅涉禽。'),
            ('金眶鸻', 'Charadrius dubius', '鸻形目', '鸻科', '三有保护', '小型鸻类，眼圈金黄色，沙滩常见。'),
            ('白腰杓鹬', 'Numenius arquata', '鸻形目', '鹬科', '国家二级保护', '喙长而下弯，滩涂觅食。'),
            ('银鸥', 'Larus argentatus', '鸻形目', '鸥科', '三有保护', '体型较大，杂食性，冬季常见。'),
        ]

        species_created = []
        for name_cn, latin, order, family, protection, habit in species_list:
            sp, created = SpeciesInfo.objects.get_or_create(
                name_cn=name_cn,
                defaults={
                    'name_latin': latin,
                    'order': order,
                    'family': family,
                    'protection_level': protection,
                    'distribution_habit': habit,
                }
            )
            species_created.append(sp)
            if created:
                self.stdout.write(f'  + 物种: {name_cn}\n')

        self.stdout.write(f'  共 {len(species_created)} 个物种（已去重）\n')

        # 3. 监测点位
        zones_data = [
            ('郑州黄河湿地中段', 113.55, 34.82, True, '保持安静，避免大声喧哗惊扰鸟类'),
            ('黄河湿地公园观测点', 113.58, 34.85, False, '请沿木栈道观鸟，不要进入草丛'),
            ('黄河老田庵段', 113.52, 34.79, True, '远离深水区，穿戴救生设备'),
            ('黄河九堡段', 113.60, 34.88, False, '春秋季候鸟高峰期，建议清晨观测'),
            ('黄河柳园口段', 113.65, 34.91, False, '冬季注意保暖，穿防滑鞋'),
            ('黄河湿地自然保护区核心区', 113.48, 34.75, True, '核心区需申请进入许可，禁止投喂'),
            ('黄河湿地恢复区东段', 113.70, 34.95, False, '人工恢复湿地，鸟类正在适应中'),
            ('黄河荥阳段', 113.30, 34.78, False, '靠近城区，观鸟同时注意人身安全'),
        ]

        zones_created = []
        for name, lng, lat, is_hot, tips in zones_data:
            zone, created = WetlandZone.objects.get_or_create(
                name=name,
                defaults={
                    'longitude': lng,
                    'latitude': lat,
                    'location': {'type': 'Point', 'coordinates': [lng, lat]},
                    'is_hotspot': is_hot,
                    'observation_tips': tips,
                }
            )
            zones_created.append(zone)
            if created:
                self.stdout.write(f'  + 监测点位: {name}\n')

        # 4. 监测样线
        routes_data = [
            ('黄河湿地中段巡护样线', [
                [113.55, 34.82], [113.56, 34.83], [113.57, 34.84], [113.58, 34.85]
            ]),
            ('黄河湿地公园巡护样线', [
                [113.57, 34.83], [113.58, 34.84], [113.59, 34.85], [113.60, 34.86]
            ]),
            ('黄河老田庵巡护样线', [
                [113.50, 34.78], [113.51, 34.79], [113.52, 34.80], [113.53, 34.81]
            ]),
        ]

        for route_name, coords in routes_data:
            route, created = MonitoringRoute.objects.get_or_create(
                name=route_name,
                defaults={
                    'path_geom': {'type': 'MultiLineString', 'coordinates': [coords]},
                    'description': f'监测样线：{route_name}',
                }
            )
            if created:
                self.stdout.write(f'  + 样线: {route_name}\n')

        # 5. 观测记录（测试数据）
        today = date.today()
        observation_count = 0
        statuses = ['approved', 'approved', 'approved', 'pending', 'rejected']

        for i in range(30):
            days_ago = random.randint(0, 30)
            obs_date = today - timedelta(days=days_ago)
            zone = random.choice(zones_created)
            species = random.choice(species_created)
            count = random.randint(1, 15)
            status = random.choice(statuses)
            uploader = admin if i % 3 == 0 else test_user

            # 用 id 最大的那条记录来判断是否已存在，避免 unique constraint
            existing = ObservationRecord.objects.filter(
                species=species,
                zone=zone,
                observation_time=obs_date
            ).order_by('-id').first()

            if not existing:
                ObservationRecord.objects.create(
                    species=species,
                    zone=zone,
                    observation_time=obs_date,
                    count=count,
                    status=status,
                    uploader=uploader,
                    description=f'在{zone.name}观测到{species.name_cn}约{count}只。',
                )
                observation_count += 1

        self.stdout.write(f'  + 新增观测记录: {observation_count} 条\n')

        # 6. 积分商城商品
        products_data = [
            ('观鸟望远镜（入门款）', 200, '适合初学者的便携式双筒望远镜', 15, 'products/placeholder.jpg'),
            ('观鸟图鉴：《中国水鸟》', 100, '收录了中国主要水鸟的识别特征和分布信息', 30, 'products/placeholder.jpg'),
            ('定制鸟巢箱', 150, '手工木质，适合悬挂于庭院花园', 10, 'products/placeholder.jpg'),
            ('湿地保护纪念徽章', 50, '限量版金属徽章，收藏价值高', 50, 'products/placeholder.jpg'),
            ('观鸟笔记本', 30, '专用记录本，含物种识别表格和点位记录页', 100, 'products/placeholder.jpg'),
            ('野生动物保护T恤', 80, '纯棉面料，印有湿地保护主题图案', 25, 'products/placeholder.jpg'),
            ('专业鸟类喂食器', 60, '防松鼠设计，适合庭院使用', 20, 'products/placeholder.jpg'),
            ('郑州黄河湿地明信片套装', 20, '含8张精美湿地鸟类照片', 200, 'products/placeholder.jpg'),
        ]
        for pname, price, desc, stock, img in products_data:
            prod, created = Product.objects.get_or_create(
                name=pname,
                defaults={
                    'price': price,
                    'image': img,
                    'description': desc,
                    'stock': stock,
                }
            )
            if created:
                self.stdout.write(f'  + 商品: {pname}\n')

        # 7. 科普文章
        articles_data = [
            ('黄河湿地：水鸟迁徙的重要驿站', '栖息地保护',
             '黄河湿地国家级自然保护区是东亚-澳大利亚西亚候鸟迁徙路线上的重要驿站。每年春秋两季，数以万计的候鸟在此停歇补给。'),
            ('白鹤的越冬之旅', '物种保护',
             '白鹤是全球极危物种，迁徙距离超过5000公里。郑州黄河湿地是它们的重要中转站。保护湿地就是保护白鹤的未来。'),
            ('观鸟礼仪：做一个文明的观鸟人', '生态知识',
             '观鸟时应保持安静，穿着隐蔽色服装，与鸟类保持100米以上距离。不投喂、不追逐、不使用播放鸟鸣的电子设备。'),
            ('湿地生态系统的多重价值', '生态知识',
             '湿地被誉为"地球之肾"，具有涵养水源、净化水质、调节气候、储存碳汇等多重生态功能。保护湿地就是保护我们自己的生存环境。'),
            ('郑州黄河湿地保护工作进展', '保护动态',
             '近年来，郑州市持续推进黄河湿地保护修复工作，湿地面积稳步恢复，水鸟种类和数量逐年增加，生态环境显著改善。'),
        ]

        for title, cat, content in articles_data:
            article, created = Article.objects.get_or_create(
                title=title,
                defaults={
                    'category': cat,
                    'content': f'<h2>{title}</h2><p>{content}</p><p>详细内容请关注郑州黄河湿地保护区的后续报道。</p>',
                    'author': admin,
                }
            )
            if created:
                self.stdout.write(f'  + 文章: {title}\n')

        self.stdout.write('\n=== 模拟数据添加完成 ===\n')
        self.stdout.write(f'  管理员: admin / admin123\n')
        self.stdout.write(f'  测试用户: testuser / test123\n')
