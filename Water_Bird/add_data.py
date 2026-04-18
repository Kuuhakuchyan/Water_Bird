"""
批量添加更多物种百科和科普文章
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app_monitor.models import SpeciesInfo, Article
from django.contrib.auth.models import User

author = User.objects.filter(is_superuser=True).first()
if not author:
    author = User.objects.first()

print(f"Using author: {author}")

# ====================
# 物种百科数据
# ====================
species_data = [
    {'name_cn': '白鹭', 'name_latin': 'Egretta garzetta', 'order': '鹈形目', 'family': '鹭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白鹭常栖息于郑州黄河湿地、贾鲁河等水域周边，以鱼虾、昆虫为食。繁殖期在3-7月，营巢于高大树木或竹林中，巢呈浅碟状。郑州地区冬季可见少量个体停留，多数个体南迁越冬。'},
    {'name_cn': '夜鹭', 'name_latin': 'Nycticorax nycticorax', 'order': '鹈形目', 'family': '鹭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '夜鹭是郑州湿地常见的留鸟，白天常站立于池杉林或近水树枝上，黄昏后活跃觅食。食性以小鱼、蛙类、昆虫为主。繁殖期4-6月，集群营巢于密林高大乔木。'},
    {'name_cn': '苍鹭', 'name_latin': 'Ardea cinerea', 'order': '鹈形目', 'family': '鹭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '苍鹭是郑州体型最大的鹭类，俗称老等，常在水边静立数小时等待猎物。喜食鱼类，兼食蛙类和大型昆虫。秋季南迁，春季北返，在郑州为常见冬候鸟。'},
    {'name_cn': '斑嘴鸭', 'name_latin': 'Anas zonorhyncha', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '斑嘴鸭是郑州黄河湿地最常见的野鸭之一，善游泳和潜水，杂食性，以水生植物种子、嫩叶及软体动物为主。繁殖期5-7月，营巢于岸边草丛或芦苇丛中。'},
    {'name_cn': '绿头鸭', 'name_latin': 'Anas platyrhynchos', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '绿头鸭是家鸭的祖先，秋季迁徙季节在郑州湿地数量较多。雄鸟头颈呈金属绿色极易辨认。杂食性，适应能力强，常在城市公园水域栖息。'},
    {'name_cn': '黑水鸡', 'name_latin': 'Gallinula chloropus', 'order': '鹤形目', 'family': '秧鸡科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑水鸡又名红骨顶，郑州城区和郊区湿地均可见到。善潜水，以水生昆虫、软体动物和植物嫩叶为食。繁殖期4-8月，营巢于芦苇丛或香蒲丛中。'},
    {'name_cn': '白骨顶', 'name_latin': 'Fulica atra', 'order': '鹤形目', 'family': '秧鸡科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白骨顶又名骨顶鸡，郑州黄河湿地冬季常见。全身黑色，额甲白色为其标志性特征。群居性强，以水生植物和小型无脊椎动物为食。'},
    {'name_cn': '普通鸬鹚', 'name_latin': 'Phalacrocorax carbo', 'order': '鲣鸟目', 'family': '鸬鹚科', 'protection_level': '国家三有保护动物', 'distribution_habit': '鸬鹚俗称鱼鹰，郑州黄河湿地有少量分布。潜水捕鱼能力强，常在水中追逐鱼群。繁殖期3-5月，集群在悬崖或高大乔木上营巢。'},
    {'name_cn': '凤头麦鸡', 'name_latin': 'Vanellus vanellus', 'order': '鸻形目', 'family': '鸻科', 'protection_level': '国家三有保护动物', 'distribution_habit': '凤头麦鸡是郑州黄河滩涂重要的迁徙过境鸟，春季3-4月和秋季9-10月数量最多。喜栖息于开阔滩涂和浅水沼泽，以昆虫和蠕虫为食。'},
    {'name_cn': '金眶鸻', 'name_latin': 'Charadrius dubius', 'order': '鸻形目', 'family': '鸻科', 'protection_level': '国家三有保护动物', 'distribution_habit': '金眶鸻体型娇小，眼圈金黄色为其显著特征。郑州黄河湿地夏候鸟，繁殖期4-7月，在沙地或砾石滩上营巢，卵色与周围环境高度相似，是优秀的保护色。'},
    {'name_cn': '普通翠鸟', 'name_latin': 'Alcedo atthis', 'order': '佛法僧目', 'family': '翠鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '普通翠鸟又名钓鱼郎，郑州城区和郊区，只要有清澈溪流和水塘的地方都能见到。飞行迅速，常悬停于水面而后俯冲入水捕鱼。'},
    {'name_cn': '斑鱼狗', 'name_latin': 'Ceryle rudis', 'order': '佛法僧目', 'family': '翠鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '斑鱼狗是郑州体型最大的翠鸟，通体黑白斑驳，飞行姿态轻盈。喜栖息于河流、水库等开阔水域，悬停捕食技巧高超。'},
    {'name_cn': '大天鹅', 'name_latin': 'Cygnus cygnus', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '大天鹅是郑州湿地重要的冬候鸟，每年11月至次年3月可见于黄河湿地和沿黄湿地公园。全身雪白，嘴基部黄色，姿态优雅。群居性强，常数十只成群活动。'},
    {'name_cn': '小天鹅', 'name_latin': 'Cygnus columbianus', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '小天鹅体型略小于大天鹅，嘴基部黄色面积较小。郑州为小天鹅的重要迁徙停歇地，迁徙季节常见数十只至上百只的大群。'},
    {'name_cn': '鸿雁', 'name_latin': 'Anser cygnoides', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '鸿雁是家鹅的祖先，郑州黄河湿地春秋迁徙季节可见。群飞时常排成一字或人字形队列，叫声洪亮。食性以草籽和嫩叶为主。'},
    {'name_cn': '灰雁', 'name_latin': 'Anser anser', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰雁是家鹅的祖先之一，迁徙季节在郑州湿地可见。体型健壮，羽毛灰褐色。群居性强，常与鸿雁混群活动。'},
    {'name_cn': '豆雁', 'name_latin': 'Anser fabalis', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '豆雁是郑州迁徙季节最常见的大型雁类之一，常数十只至上百只集群活动。嘴黑色而具白环，喜食豆类、谷物和草叶。'},
    {'name_cn': '白额雁', 'name_latin': 'Anser albifrons', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '白额雁迁徙季节途经郑州，前额白色是其显著特征。越冬于长江中下游湿地，迁徙期间以农田残留谷物为主要食物。'},
    {'name_cn': '翘鼻麻鸭', 'name_latin': 'Tadorna tadorna', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '翘鼻麻鸭色彩艳丽，雄鸟具显著的红色嘴且向上翘起。郑州黄河湿地春秋迁徙季节有记录，喜成对或小群活动于浅水沼泽。'},
    {'name_cn': '赤颈鸭', 'name_latin': 'Mareca penelope', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '赤颈鸭雄鸟繁殖羽头颈部呈栗红色，易于辨认。郑州黄河湿地迁徙季节常见，以水生植物种子和嫩叶为主食。'},
    {'name_cn': '绿翅鸭', 'name_latin': 'Anas crecca', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '绿翅鸭体型最小的一种河鸭，春季迁徙时数量庞大。雄鸟具显著的绿色眼罩和翼镜。栖息于各类淡水湿地，杂食性。'},
    {'name_cn': '赤膀鸭', 'name_latin': 'Mareca strepera', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '赤膀鸭雄鸟繁殖期翅膀具红褐色斑块因而得名。郑州黄河湿地迁徙季节有分布，以水生植物和小型动物为食。'},
    {'name_cn': '罗纹鸭', 'name_latin': 'Mareca falcata', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '罗纹鸭雄鸟头部具独特的卷曲羽冠，辨识度高。郑州湿地为迁徙过境鸟，春秋两季可见于黄河滩涂。'},
    {'name_cn': '赤嘴潜鸭', 'name_latin': 'Netta rufina', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '赤嘴潜鸭雄鸟嘴鲜红色，头部棕红色，辨识度高。郑州地区有分布记录，喜栖息于开阔的深水湖泊，以水生植物为食。'},
    {'name_cn': '凤头潜鸭', 'name_latin': 'Aythya fuligula', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '凤头潜鸭潜水能力强，常在水下追逐小型鱼虾。郑州黄河湿地冬季常见，与其他潜鸭混群活动。'},
    {'name_cn': '普通秋沙鸭', 'name_latin': 'Mergus merganser', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '普通秋沙鸭是郑州最常见的秋沙鸭，嘴细长具锯齿状边缘，善于捕食鱼类。冬季在黄河湿地活动，潜水能力极强。'},
    {'name_cn': '中华秋沙鸭', 'name_latin': 'Mergus squamatus', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家一级重点保护野生动物', 'distribution_habit': '中华秋沙鸭是最珍稀的秋沙鸭物种，郑州黄河湿地曾有记录。冠羽显著，与普通秋沙鸭最显著的区别是胁部鳞状斑纹。对水质要求极高。'},
    {'name_cn': '白秋沙鸭', 'name_latin': 'Mergellus albellus', 'order': '雁形目', 'family': '鸭科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白秋沙鸭又名小秋沙鸭，体型最小的秋沙鸭。雄鸟几乎全白，郑州黄河湿地冬季有分布记录，喜清澈的缓流和湖泊。'},
    {'name_cn': '鹌鹑', 'name_latin': 'Coturnix coturnix', 'order': '鸡形目', 'family': '雉科', 'protection_level': '国家三有保护动物', 'distribution_habit': '鹌鹑体型小巧，隐匿于农田和草丛中，晨昏活动。郑州地区夏候鸟，繁殖期5-8月，以杂草种子和昆虫为食。'},
    {'name_cn': '环颈雉', 'name_latin': 'Phasianus colchicus', 'order': '鸡形目', 'family': '雉科', 'protection_level': '国家三有保护动物', 'distribution_habit': '环颈雉又名野鸡，雄鸟羽色华丽，具白色颈环。郑州郊区农田和荒草地常见，留鸟，以农作物种子、昆虫和嫩叶为食。'},
    {'name_cn': '黑翅长脚鹬', 'name_latin': 'Himantopus himantopus', 'order': '鸻形目', 'family': '反嘴鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑翅长脚鹬腿极长（可达40厘米），红色，姿态优雅。郑州黄河湿地夏季繁殖鸟，群体营巢于芦苇沼泽中。'},
    {'name_cn': '反嘴鹬', 'name_latin': 'Recurvirostra avosetta', 'order': '鸻形目', 'family': '反嘴鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '反嘴鹬嘴显著向上弯曲，是郑州黄河湿地最具特色的鸻鹬类之一。繁殖期4-7月，常与黑翅长脚鹬混群繁殖。'},
    {'name_cn': '黑尾塍鹬', 'name_latin': 'Limosa limosa', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑尾塍鹬体型较大，嘴长而直，郑州迁徙季节常见。春秋两季在黄河滩涂停留，以昆虫和小型甲壳动物为食。'},
    {'name_cn': '白腰杓鹬', 'name_latin': 'Numenius arquata', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白腰杓鹬嘴长而下弯，是郑州迁徙季节最常见的大型鹬类之一。在黄河滩涂觅食时，常将长嘴插入泥沙中探食。'},
    {'name_cn': '大滨鹬', 'name_latin': 'Calidris tenuirostris', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '大滨鹬是郑州迁徙季节重要的鸻鹬类，数量较多。常集群觅食于潮间带泥沙滩，以小型甲壳类和昆虫为食。'},
    {'name_cn': '红嘴鸥', 'name_latin': 'Chroicocephalus ridibundus', 'order': 'Charadriiformes', 'family': '鸥科', 'protection_level': '国家三有保护动物', 'distribution_habit': '红嘴鸥是郑州最常见的鸥类，冬季在黄河湿地可见大群。夏羽头部深褐色，冬羽头部白色。杂食性，适应性强。'},
    {'name_cn': '普通燕鸥', 'name_latin': 'Sterna hirundo', 'order': '鸻形目', 'family': '鸥科', 'protection_level': '国家三有保护动物', 'distribution_habit': '普通燕鸥是郑州黄河湿地的夏候鸟，繁殖期5-8月。空中悬停俯冲捕鱼技巧高超，营巢于沙洲或砾石滩上。'},
    {'name_cn': '东方白鹳', 'name_latin': 'Ciconia boyciana', 'order': '鹳形目', 'family': '鹳科', 'protection_level': '国家一级重点保护野生动物', 'distribution_habit': '东方白鹳是郑州黄河湿地罕见的迁徙过境鸟，数量稀少。体型高大，嘴黑色粗长，翅膀黑白相间。对湿地环境要求极高，是湿地生态系统的旗舰物种。'},
    {'name_cn': '黑鹳', 'name_latin': 'Ciconia nigra', 'order': '鹳形目', 'family': '鹳科', 'protection_level': '国家一级重点保护野生动物', 'distribution_habit': '黑鹳是郑州珍稀的迁徙鸟类，通体除下胸腹部白色外均为黑色，嘴和腿红色。在悬崖峭壁上营巢，迁徙时途经郑州。'},
    {'name_cn': '白琵鹭', 'name_latin': 'Platalea leucorodia', 'order': '鹈形目', 'family': '鹮科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '白琵鹭嘴扁平先端扩展成勺状，觅食时左右摆动嘴部滤食。郑州黄河湿地迁徙季节有记录，常与其他鹭类混群活动。'},
    {'name_cn': '戴胜', 'name_latin': 'Upupa epops', 'order': '犀鸟目', 'family': '戴胜科', 'protection_level': '国家三有保护动物', 'distribution_habit': '戴胜是郑州常见的留鸟，头具显著的扇状羽冠，羽色华丽。喜栖息于林缘、农田和庭院，以昆虫为食。繁殖期4-6月，营巢于树洞或墙壁洞穴中。'},
    {'name_cn': '大斑啄木鸟', 'name_latin': 'Dendrocopos major', 'order': '啄木鸟目', 'family': '啄木鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '大斑啄木鸟是郑州城区和郊区最常见的啄木鸟，红腹特征明显。攀爬于树干上敲击取食天牛幼虫等蛀干害虫，是森林医生。'},
    {'name_cn': '星头啄木鸟', 'name_latin': 'Yungipicus canicapillus', 'order': '啄木鸟目', 'family': '啄木鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '星头啄木鸟体型小巧，郑州城区公园和林地可见。以小型昆虫和蜘蛛为主食，常在细小树枝上觅食。'},
    {'name_cn': '灰头绿啄木鸟', 'name_latin': 'Picus canus', 'order': '啄木鸟目', 'family': '啄木鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰头绿啄木鸟是郑州体型最大的绿色啄木鸟，雄鸟头顶红色。喜栖息于山地和平原林地，地面觅食蚂蚁是其特色。'},
    {'name_cn': '大杜鹃', 'name_latin': 'Cuculus canorus', 'order': '鹃形目', 'family': '杜鹃科', 'protection_level': '国家三有保护动物', 'distribution_habit': '大杜鹃即布谷鸟，郑州夏候鸟，以其独特的布谷叫声闻名。巢寄生繁殖，将卵产于大苇莺、东方大苇莺等宿主巢中。'},
    {'name_cn': '四声杜鹃', 'name_latin': 'Cuculus micropterus', 'order': '鹃形目', 'family': '杜鹃科', 'protection_level': '国家三有保护动物', 'distribution_habit': '四声杜鹃鸣声为四声一度，郑州夏候鸟。繁殖期5-7月，以巢寄生的方式繁殖，宿主主要为灰喜鹊等鸟类。'},
    {'name_cn': '红隼', 'name_latin': 'Falco tinnunculus', 'order': '隼形目', 'family': '隼科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '红隼是郑州最常见的小型猛禽，常悬停于空中搜寻猎物，捕食老鼠、大型昆虫等。城市郊区均可见，留鸟或冬候鸟。'},
    {'name_cn': '红脚隼', 'name_latin': 'Falco amurensis', 'order': '隼形目', 'family': '隼科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '红脚隼是郑州迁徙季节较常见的猛禽，秋季常集群迁飞。以大型昆虫和小型鸟类为食，繁殖于东北地区。'},
    {'name_cn': '游隼', 'name_latin': 'Falco peregrinus', 'order': '隼形目', 'family': '隼科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '游隼飞行速度极快，俯冲捕食时速可达300公里以上，是世界上飞行最快的动物。郑州为迁徙过境鸟或冬候鸟。'},
    {'name_cn': '雀鹰', 'name_latin': 'Accipiter nisus', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '雀鹰是郑州最常见的中小型猛禽之一，雌鸟显著大于雄鸟。以雀形目小鸟为主食，捕食技巧高超。'},
    {'name_cn': '日本松雀鹰', 'name_latin': 'Accipiter gularis', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '日本松雀鹰是郑州迁徙季节较常见的猛禽，体型较小，雌雄羽色差异大。以小型鸟类和昆虫为食。'},
    {'name_cn': '苍鹰', 'name_latin': 'Accipiter gentilis', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '苍鹰是郑州体型较大的林栖猛禽，捕食野兔、雉鸡等中型猎物。繁殖期4-6月，营巢于高大乔木上。'},
    {'name_cn': '普通鵟', 'name_latin': 'Buteo japonicus', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '普通鵟是郑州最常见的猛禽之一，冬季常可见到在电杆或树顶停歇。以小型哺乳动物和大型昆虫为食。'},
    {'name_cn': '大鵟', 'name_latin': 'Buteo hemilasius', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '大鵟是郑州体型最大的鵟类，翅展可达1.5米以上。冬季在黄河滩涂和农田活动，以鼠类为主食。'},
    {'name_cn': '白尾鹞', 'name_latin': 'Circus cyaneus', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '白尾鹞是郑州黄河湿地冬季常见的猛禽，雄鸟下体白色，尾上覆羽白色显著。低空飞行搜寻猎物，捕食鼠类和小型鸟类。'},
    {'name_cn': '鹊鹞', 'name_latin': 'Circus melanoleucos', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '鹊鹞雄鸟体色似喜鹊，黑白相间，是郑州迁徙季节较常见的猛禽。喜开阔湿地和农田，低空滑翔捕食。'},
    {'name_cn': '黑翅鸢', 'name_latin': 'Elanus caeruleus', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '黑翅鸢是郑州地区近年新记录的猛禽，翅上黑色斑块和红色虹膜是其显著特征。悬停于空中搜寻猎物。'},
    {'name_cn': '白头鹞', 'name_latin': 'Circus aeruginosus', 'order': '鹰形目', 'family': '鹰科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '白头鹞是郑州黄河湿地繁殖的猛禽，在芦苇沼泽中营巢。繁殖期4-7月，以水鸟幼雏、鸟蛋和鼠类为食。'},
    {'name_cn': '纵纹腹小鸮', 'name_latin': 'Athene noctua', 'order': '鸮形目', 'family': '鸱鸮科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '纵纹腹小鸮是郑州体型最小的猫头鹰之一，常栖息于土崖、土墙洞或树洞中。白天活动，以昆虫和小型啮齿类为食。'},
    {'name_cn': '长耳鸮', 'name_latin': 'Asio otus', 'order': '鸮形目', 'family': '鸱鸮科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '长耳鸮是郑州常见的冬候鸟，迁徙季节常集群栖息于林地。耳羽显著，以鼠类为主食，是农田的重要益鸟。'},
    {'name_cn': '短耳鸮', 'name_latin': 'Asio flammeus', 'order': '鸮形目', 'family': '鸱鸮科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '短耳鸮是郑州黄河湿地冬季常见的猫头鹰，面盘显著呈心形，白天活动。栖息于开阔田野，以鼠类为主食。'},
    {'name_cn': '领鸺鹠', 'name_latin': 'Glaucidium brodiei', 'order': '鸮形目', 'family': '鸱鸮科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '领鸺鹠是郑州体型最小的猫头鹰，后脑勺有眼状斑纹，常在白天活动。鸣声单调重复，以昆虫和小型鸟类为食。'},
    {'name_cn': '斑头鸺鹠', 'name_latin': 'Glaucidium cuculoides', 'order': '鸮形目', 'family': '鸱鸮科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '斑头鸺鹠是郑州林地常见的小型猫头鹰，全身多纵纹。以昆虫、小型鸟类和鼠类为食，繁殖期4-7月。'},
    {'name_cn': '草鸮', 'name_latin': 'Tyto longimembris', 'order': '鸮形目', 'family': '草鸮科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '草鸮又名猴面鹰，面盘心形呈心脏状，郑州地区有分布记录。栖息于草丛和芦苇丛，以鼠类为主食。'},
    {'name_cn': '东方大苇莺', 'name_latin': 'Acrocephalus orientalis', 'order': '雀形目', 'family': '苇莺科', 'protection_level': '国家三有保护动物', 'distribution_habit': '东方大苇莺是郑州黄河湿地芦苇沼泽中最常见的夏候鸟之一，鸣声嘹亮复杂。以昆虫和蜘蛛为食，繁殖期5-7月，是大杜鹃的主要宿主。'},
    {'name_cn': '黑眉苇莺', 'name_latin': 'Acrocephalus bistrigiceps', 'order': '雀形目', 'family': '苇莺科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑眉苇莺体型较小，眉纹黑色显著，郑州迁徙季节常见。栖息于芦苇丛和灌丛，以昆虫为食。'},
    {'name_cn': '纯色山鹪莺', 'name_latin': 'Prinia inornata', 'order': '雀形目', 'family': '扇尾莺科', 'protection_level': '国家三有保护动物', 'distribution_habit': '纯色山鹪莺是郑州郊区常见的留鸟，尾羽较长。栖息于草丛、灌丛和农田边缘，以昆虫为食。'},
    {'name_cn': '棕扇尾莺', 'name_latin': 'Cisticola juncidis', 'order': '雀形目', 'family': '扇尾莺科', 'protection_level': '国家三有保护动物', 'distribution_habit': '棕扇尾莺体型极小，繁殖期雄鸟常在空中盘旋鸣唱。郑州郊区农田和荒草地常见，以小型昆虫为食。'},
    {'name_cn': '小鸦鹃', 'name_latin': 'Centropus bengalensis', 'order': '鹃形目', 'family': '杜鹃科', 'protection_level': '国家二级重点保护野生动物', 'distribution_habit': '小鸦鹃是郑州地区较常见的杜鹃科鸟类，不进行巢寄生，而是自己营巢繁殖。栖息于芦苇丛和灌丛，以昆虫为食。'},
    {'name_cn': '噪鹃', 'name_latin': 'Eudynamys scolopaceus', 'order': '鹃形目', 'family': '杜鹃科', 'protection_level': '国家三有保护动物', 'distribution_habit': '噪鹃是郑州夏候鸟，雄鸟通体黑色，鸣声凄厉单调，常在夜间鸣叫。以果实和昆虫为食，巢寄生繁殖。'},
    {'name_cn': '八哥', 'name_latin': 'Acridotheres cristatellus', 'order': '雀形目', 'family': '椋鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '八哥是郑州常见的留鸟，通体黑色，额羽耸立，翅具白斑。喜群居，常与家麻雀等混群活动。以昆虫和果实为食。'},
    {'name_cn': '灰椋鸟', 'name_latin': 'Spodiopsar cineraceus', 'order': '雀形目', 'family': '椋鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰椋鸟是郑州常见的冬候鸟和旅鸟，秋季迁徙时常形成数十只的大群。白天觅食于农田，夜间集群栖于高大乔木上。'},
    {'name_cn': '丝光椋鸟', 'name_latin': 'Sturnia sericeus', 'order': '雀形目', 'family': '椋鸟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '丝光椋鸟是郑州夏候鸟，雄鸟头部羽毛具丝光光泽。以昆虫和果实为食，繁殖期5-7月，营巢于树洞中。'},
    {'name_cn': '黑领椋鸟', 'name_latin': 'Garrulax pectoralis', 'order': '雀形目', 'family': '噪鹛科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑领椋鸟是郑州近年新记录的留鸟，颈部黑色领环显著。栖息于林缘和灌丛，以昆虫和果实为食。'},
    {'name_cn': '灰喜鹊', 'name_latin': 'Cyanopica cyanus', 'order': '雀形目', 'family': '鸦科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰喜鹊是郑州最常见的留鸟之一，头顶黑色，两翼和尾蓝色。群居性强，常数十只成群活动，是大杜鹃的宿主之一。以昆虫和果实为食。'},
    {'name_cn': '喜鹊', 'name_latin': 'Pica pica', 'order': '雀形目', 'family': '鸦科', 'protection_level': '国家三有保护动物', 'distribution_habit': '喜鹊是郑州最常见的留鸟之一，黑白相间，具蓝色辉光的翅膀和长尾。杂食性，适应性强，在城区和郊区均可见到。'},
    {'name_cn': '达乌里寒鸦', 'name_latin': 'Coloeus dauuricus', 'order': '雀形目', 'family': '鸦科', 'protection_level': '国家三有保护动物', 'distribution_habit': '达乌里寒鸦是郑州冬季常见的乌鸦，体型较小，颈背白色。群居性强，冬季常形成数百只的大群。'},
    {'name_cn': '小嘴乌鸦', 'name_latin': 'Corvus corone', 'order': '雀形目', 'family': '鸦科', 'protection_level': '国家三有保护动物', 'distribution_habit': '小嘴乌鸦是郑州城区和郊区常见的留鸟，嘴较细。杂食性，兼食腐肉、垃圾和昆虫。繁殖期3-5月，营巢于高大树木上。'},
    {'name_cn': '大嘴乌鸦', 'name_latin': 'Corvus macrorhynchos', 'order': '雀形目', 'family': '鸦科', 'protection_level': '国家三有保护动物', 'distribution_habit': '大嘴乌鸦是郑州体型最大的乌鸦，嘴粗大。常见于郊区和山地，杂食性，适应性强。'},
    {'name_cn': '白颈鸦', 'name_latin': 'Corvus torquatus', 'order': '雀形目', 'family': '鸦科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白颈鸦是郑州近年数量增加的留鸟，后颈白色显著。栖息于农田和湿地边缘，杂食性，以昆虫和农作物为主食。'},
    {'name_cn': '松鸦', 'name_latin': 'Garrulus glandarius', 'order': '雀形目', 'family': '鸦科', 'protection_level': '国家三有保护动物', 'distribution_habit': '松鸦是郑州林地常见的留鸟，翅具蓝色和黑色斑块。秋季有储食行为，会将橡子等埋藏于地下，有助于森林更新。'},
    {'name_cn': '红尾水鸲', 'name_latin': 'Rhyacornis fuliginosus', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '红尾水鸲是郑州溪流和水库边常见的留鸟，雄鸟尾红色显著。常在岩石上摆动尾巴，以昆虫为食。'},
    {'name_cn': '白顶溪鸲', 'name_latin': 'Phoenicurus leucocephalus', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白顶溪鸲是郑州山区溪流旁常见的留鸟，头顶白色，尾红褐色。栖息于清澈溪流附近，以水生昆虫为食。'},
    {'name_cn': '北红尾鸲', 'name_latin': 'Phoenicurus auroreus', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '北红尾鸲是郑州常见的冬候鸟和旅鸟，雄鸟具白色肩斑和橙红色尾。栖息于林缘、灌丛和农田边缘，以昆虫为食。'},
    {'name_cn': '红喉姬鹟', 'name_latin': 'Ficedula parva', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '红喉姬鹟是郑州迁徙季节常见的旅鸟，雄鸟繁殖羽喉部红色。栖息于林地和灌丛，以昆虫为食。'},
    {'name_cn': '白眉姬鹟', 'name_latin': 'Ficedula zanthopygia', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白眉姬鹟是郑州夏候鸟，雄鸟色彩鲜艳，具白色眉纹和黄色腰。繁殖于山地林地，以昆虫为食。'},
    {'name_cn': '鸲姬鹟', 'name_latin': 'Ficedula mugimaki', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '鸲姬鹟是郑州迁徙季节常见的旅鸟，雄鸟翼上具白斑。栖息于林地和园林，以昆虫为食。'},
    {'name_cn': '北灰鹟', 'name_latin': 'Muscicapa dauurica', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '北灰鹟是郑州迁徙季节常见的旅鸟，体色较灰。栖息于林地和园林，空中捕食飞虫为主要觅食方式。'},
    {'name_cn': '乌鹟', 'name_latin': 'Muscicapa sibirica', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '乌鹟是郑州迁徙季节常见的旅鸟，通体灰褐色。栖息于林地和园林，尾常上下摆动，以昆虫为食。'},
    {'name_cn': '灰纹鹟', 'name_latin': 'Muscicapa griseisticta', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰纹鹟是郑州迁徙季节较常见的旅鸟，胸侧具灰褐色条纹。栖息于林地和灌丛，以昆虫为食。'},
    {'name_cn': '红喉歌鸲', 'name_latin': 'Luscinia calliope', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '红喉歌鸲又名红点颏，是郑州著名的迁徙笼养鸟种。雄鸟繁殖羽喉部红色，鸣声动听。以昆虫和软体动物为食。'},
    {'name_cn': '蓝喉歌鸲', 'name_latin': 'Luscinia svecica', 'order': '雀形目', 'family': '鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '蓝喉歌鸲又名蓝点颏，郑州迁徙季节常见。雄鸟喉部蓝色具栗色斑点，鸣声悦耳。以昆虫和蜘蛛为食。'},
    {'name_cn': '黑枕黄鹂', 'name_latin': 'Oriolus chinensis', 'order': '雀形目', 'family': '黄鹂科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑枕黄鹂是郑州夏候鸟，雄鸟通体金黄色，枕部黑色。栖息于山地和平原林地，鸣声悦耳动听，以昆虫和果实为食。'},
    {'name_cn': '黑卷尾', 'name_latin': 'Dicrurus macrocercus', 'order': '雀形目', 'family': '卷尾科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑卷尾是郑州夏候鸟，全身黑色，尾分叉且略向上卷。繁殖期具强烈的领域性，会驱赶猛禽。以昆虫为食。'},
    {'name_cn': '灰卷尾', 'name_latin': 'Dicrurus leucophaeus', 'order': '雀形目', 'family': '卷尾科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰卷尾是郑州迁徙季节的旅鸟或夏候鸟，体色较灰。栖息于林地，以昆虫为食，空中捕食技巧高超。'},
    {'name_cn': '发冠卷尾', 'name_latin': 'Dicrurus hottentottus', 'order': '雀形目', 'family': '卷尾科', 'protection_level': '国家三有保护动物', 'distribution_habit': '发冠卷尾是郑州夏候鸟，外侧尾羽末端外卷，额部具发状羽冠。栖息于山地林地，以昆虫为食。'},
    {'name_cn': '寿带鸟', 'name_latin': 'Terpsiphone affinis', 'order': '雀形目', 'family': '王鹟科', 'protection_level': '国家三有保护动物', 'distribution_habit': '寿带鸟是郑州夏候鸟，有白色型和栗色型两种色型，雄鸟具超长的中央尾羽。栖息于山地和平原林地，以昆虫为食。'},
    {'name_cn': '山麻雀', 'name_latin': 'Passer rutilans', 'order': '雀形目', 'family': '雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '山麻雀是郑州山区林地常见的留鸟，与家麻雀相比雄鸟上体栗色更浓。栖息于山地林缘和灌丛，以种子和昆虫为食。'},
    {'name_cn': '树麻雀', 'name_latin': 'Passer montanus', 'order': '雀形目', 'family': '雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '树麻雀是郑州城区和郊区最常见的留鸟，与人类关系密切。杂食性，以农作物种子和昆虫为食，繁殖力强。'},
    {'name_cn': '白鹡鸰', 'name_latin': 'Motacilla alba', 'order': '雀形目', 'family': '鹡鸰科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白鹡鸰是郑州最常见的鹡鸰类，几乎全年可见。黑白相间，尾长且常上下摆动。栖息于溪流、池塘和农田边。'},
    {'name_cn': '灰鹡鸰', 'name_latin': 'Motacilla cinerea', 'order': '雀形目', 'family': '鹡鸰科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰鹡鸰是郑州常见的夏候鸟，雄鸟繁殖期下体黄色。栖息于清澈溪流和水边，以昆虫为食。'},
    {'name_cn': '黄头鹡鸰', 'name_latin': 'Motacilla citreola', 'order': '雀形目', 'family': '鹡鸰科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黄头鹡鸰是郑州黄河湿地繁殖的夏候鸟，雄鸟繁殖期头胸部黄色。栖息于湿地沼泽，以昆虫为食。'},
    {'name_cn': '黄鹡鸰', 'name_latin': 'Motacilla tschutschensis', 'order': '雀形目', 'family': '鹡鸰科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黄鹡鸰是郑州迁徙季节常见的旅鸟，下体黄色。栖息于湿地和农田边，以昆虫为食。'},
    {'name_cn': '小鹀', 'name_latin': 'Emberiza pusilla', 'order': '雀形目', 'family': '鹀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '小鹀是郑州迁徙季节最常见的鹀类之一，头部具栗色和黑色条纹。栖息于灌丛和农田边缘，以种子和昆虫为食。'},
    {'name_cn': '黄眉鹀', 'name_latin': 'Emberiza chrysophrys', 'order': '雀形目', 'family': '鹀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黄眉鹀是郑州迁徙季节常见的旅鸟，眉纹黄色是其显著特征。栖息于林地和灌丛，以种子和昆虫为食。'},
    {'name_cn': '白眉鹀', 'name_latin': 'Emberiza tristrami', 'order': '雀形目', 'family': '鹀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白眉鹀是郑州迁徙季节较常见的旅鸟，雄鸟具显著的白色眉纹和颧纹。栖息于山地林地，以昆虫和种子为食。'},
    {'name_cn': '栗耳鹀', 'name_latin': 'Emberiza fucata', 'order': '雀形目', 'family': '鹀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '栗耳鹀是郑州郊区常见的留鸟，胸部具栗色横带。栖息于农田和草地，以种子和昆虫为食。'},
    {'name_cn': '黄喉鹀', 'name_latin': 'Emberiza elegans', 'order': '雀形目', 'family': '鹀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黄喉鹀是郑州山区林地常见的夏候鸟，雄鸟喉部黄色醒目。栖息于山地林缘和灌丛，以昆虫和种子为食。'},
    {'name_cn': '灰头鹀', 'name_latin': 'Emberiza spodocephala', 'order': '雀形目', 'family': '鹀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '灰头鹀是郑州迁徙季节和冬季常见的鹀类，头部灰色。栖息于灌丛和农田边缘，以种子和昆虫为食。'},
    {'name_cn': '三道眉草鹀', 'name_latin': 'Emberiza cioides', 'order': '雀形目', 'family': '鹀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '三道眉草鹀是郑州郊区常见的留鸟，眉纹、颧纹和髭纹白色显著。栖息于荒草地和灌丛，以种子和昆虫为食。'},
    {'name_cn': '燕雀', 'name_latin': 'Fringilla montifringilla', 'order': '雀形目', 'family': '燕雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '燕雀是郑州迁徙季节最常见的冬候鸟之一，春秋两季数量均较多。雄鸟繁殖羽上体黑色，下体橙褐色。'},
    {'name_cn': '金翅雀', 'name_latin': 'Chloris sinica', 'order': '雀形目', 'family': '燕雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '金翅雀是郑州常见的留鸟，翅具金黄色斑块。栖息于林地、园林和农田边缘，以种子为食。'},
    {'name_cn': '黑头蜡嘴雀', 'name_latin': 'Eophona personata', 'order': '雀形目', 'family': '燕雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑头蜡嘴雀是郑州常见的冬候鸟，嘴粗大呈蜡黄色。喜食树木种子，如银杏、枫杨种子等。'},
    {'name_cn': '黑尾蜡嘴雀', 'name_latin': 'Eophona migratoria', 'order': '雀形目', 'family': '燕雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑尾蜡嘴雀是郑州迁徙季节常见的冬候鸟，嘴粗大。与黑头蜡嘴雀相似，但雄鸟头部黑色范围较小。'},
    {'name_cn': '锡嘴雀', 'name_latin': 'Coccothraustes coccothraustes', 'order': '雀形目', 'family': '燕雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '锡嘴雀是郑州冬季较常见的冬候鸟，嘴粗大而厚呈蓝灰色。栖息于林地和园林，取食树木种子。'},
    {'name_cn': '苍头燕雀', 'name_latin': 'Fringilla coelebs', 'order': '雀形目', 'family': '燕雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '苍头燕雀是郑州近年数量增加的冬候鸟，头部粉红色（雄鸟）。栖息于林地和园林，以种子和昆虫为食。'},
    {'name_cn': '黄雀', 'name_latin': 'Spinus spinus', 'order': '雀形目', 'family': '燕雀科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黄雀是郑州冬季常见的候鸟，雄鸟头胸部黄色。喜食树木种子，如枫杨、榆树种子。'},
    {'name_cn': '红颈滨鹬', 'name_latin': 'Calidris ruficollis', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '红颈滨鹬是郑州迁徙季节最常见的小型鸻鹬类之一。繁殖羽颈部红褐色，数量庞大。'},
    {'name_cn': '青脚滨鹬', 'name_latin': 'Calidris temminckii', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '青脚滨鹬是郑州迁徙季节常见的中小型滨鹬，腿黄绿色。栖息于各类淡水湿地。'},
    {'name_cn': '弯嘴滨鹬', 'name_latin': 'Calidris ferruginea', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '弯嘴滨鹬是郑州迁徙季节较常见的滨鹬，繁殖羽下体栗红色。栖息于潮间带和内陆湿地。'},
    {'name_cn': '黑腹滨鹬', 'name_latin': 'Calidris alpina', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '黑腹滨鹬是郑州迁徙季节较常见的滨鹬，繁殖羽腹部黑色。栖息于潮间带和沼泽湿地。'},
    {'name_cn': '白腰草鹬', 'name_latin': 'Tringa ochropus', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '白腰草鹬是郑州最常见的鸻鹬类之一，几乎全年可见。腰白色显著，栖息于溪流、池塘和农田。'},
    {'name_cn': '林鹬', 'name_latin': 'Tringa glareola', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '林鹬是郑州迁徙季节常见的鸻鹬类，栖息于沼泽湿地和鱼塘。尾常上下摆动，以昆虫为食。'},
    {'name_cn': '青脚鹬', 'name_latin': 'Tringa nebularia', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '青脚鹬是郑州迁徙季节最常见的鸻鹬类之一，体型较大。嘴微向上翘，栖息于沿海和内陆湿地。'},
    {'name_cn': '红脚鹬', 'name_latin': 'Tringa totanus', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '红脚鹬是郑州黄河湿地夏候鸟，腿红色醒目。栖息于沼泽和浅水区，以小型甲壳类和昆虫为食。'},
    {'name_cn': '泽鹬', 'name_latin': 'Tringa stagnatilis', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '泽鹬是郑州迁徙季节常见的鸻鹬类，体型纤细，嘴细长。栖息于沼泽和淡水湿地。'},
    {'name_cn': '鹤鹬', 'name_latin': 'Tringa erythropus', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '鹤鹬是郑州迁徙季节常见的鸻鹬类，繁殖羽通体黑色。嘴细长而黑，栖息于沼泽和浅水区。'},
    {'name_cn': '矸鹬', 'name_latin': 'Actitis hypoleucos', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '矸鹬是郑州最常见的鸻鹬类之一，迁徙季节数量多。栖息于河流、池塘边，地面活动为主。'},
    {'name_cn': '扇尾沙锥', 'name_latin': 'Gallinago gallinago', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '扇尾沙锥是郑州黄河湿地迁徙季节较常见的鹬类。嘴长而直，栖息于沼泽湿地，以泥土中的无脊椎动物为食。'},
    {'name_cn': '针尾沙锥', 'name_latin': 'Gallinago stenura', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家三有保护动物', 'distribution_habit': '针尾沙锥是郑州迁徙季节较常见的旅鸟，外侧尾羽针状。栖息于沼泽湿地，觅食于泥沙滩中。'},
    {'name_cn': '勺嘴鹬', 'name_latin': 'Calidris pygmaea', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家一级重点保护野生动物', 'distribution_habit': '勺嘴鹬是郑州黄河湿地极罕见的迁徙过境鸟，数量稀少。嘴端扩展成勺状，是世界最濒危的鸟类之一，全球数量不足700只。'},
    {'name_cn': '小青脚鹬', 'name_latin': 'Tringa guttifer', 'order': '鸻形目', 'family': '鹬科', 'protection_level': '国家一级重点保护野生动物', 'distribution_habit': '小青脚鹬是郑州黄河湿地极罕见的迁徙过境鸟，数量稀少。对栖息地要求高，迁徙季节偶有记录。'},
    {'name_cn': '遗鸥', 'name_latin': 'Ichthyaetus relictus', 'order': 'Charadriiformes', 'family': '鸥科', 'protection_level': '国家一级重点保护野生动物', 'distribution_habit': '遗鸥是郑州黄河湿地极罕见的迁徙或越冬鸟，是世界性濒危物种。对湿地环境要求极高，数量极少。'},
]

# ====================
# 科普文章数据
# ====================
articles_data = [
    {
        'title': '郑州黄河湿地：中部地区重要的候鸟迁徙通道',
        'category': 'habitat',
        'summary': '郑州黄河湿地作为我国中部地区最重要的候鸟迁徙通道之一，每年春秋两季迎接数以万计的候鸟途经此地。',
        'content': '<p>郑州黄河湿地国家级自然保护区位于河南省郑州市北部，地处黄河中下游交接地带，是我国中部地区最重要的候鸟迁徙通道之一。每年春秋两季，数以万计的候鸟在此停歇、觅食、补充能量后继续北迁或南迁。</p><h3>得天独厚的地理位置</h3><p>郑州地处我国三大候鸟迁徙通道——东亚-澳大利亚候鸟迁徙路线的重要节点。黄河河道在此变宽，形成了大面积的滩涂、沼泽和浅水区，为迁徙鸟类提供了理想的停歇场所。</p><h3>丰富的湿地资源</h3><p>保护区总面积超过15000公顷，包含了黄河主河道、滩涂、库塘、芦苇沼泽等多种湿地类型。这些不同类型的栖息地为各种生态习性的鸟类提供了多样化的选择。</p><h3>重要的生态价值</h3><p>每年春秋迁徙季节，在此记录到的鸟类超过200种，其中包括大天鹅、中华秋沙鸭、东方白鹳等国家重点保护野生动物。保护好这一迁徙通道，对于维护全球候鸟种群的健康具有重要意义。</p><h3>保护现状与挑战</h3><p>近年来，郑州市持续加大黄河湿地保护力度，实施了一系列生态修复工程。但同时，湿地周边人类活动增加、水环境污染等问题仍然存在，需要全社会共同努力保护这一宝贵的生态资源。</p>',
    },
    {
        'title': '观鸟入门：如何正确使用望远镜观察野生鸟类',
        'category': 'knowledge',
        'summary': '望远镜是观鸟最重要的工具之一，本文将介绍如何选择合适的观鸟望远镜，以及正确的使用方法。',
        'content': '<p>一副好的望远镜是观鸟爱好者的基本装备。正确选择和使用望远镜，不仅能让你更清晰地观察鸟类，还能有效保护你的视力。</p><h3>如何选择合适的望远镜</h3><p>观鸟望远镜主要有两种类型：双筒望远镜适合观察林鸟，倍数通常为8x或10x，物镜直径42mm或50mm；单筒观鸟镜适合观察水鸟和远处的鸟，倍数通常为20-60倍，需要配合三脚架使用。对于初学者，建议选择8x42或10x42的双筒望远镜，这个规格最适合大多数观鸟场景。</p><h3>正确的使用方法</h3><p>使用双筒望远镜时，首先用肉眼找到目标鸟类，然后举起望远镜直接对准目标，不要先用镜筒搜索。保持双臂夹紧身体以减少晃动。如果看不清楚，可以稍微调整焦距。</p><h3>观鸟礼仪</h3><p>观鸟时应保持安静，避免大声喧哗。不要追逐或干扰鸟类，更不要投喂食物。保持适当距离，通常建议与鸟类保持100米以上距离。使用遮阳伞可以减少阳光干扰，提高观察效果。</p>',
    },
    {
        'title': '湿地的生态服务功能：地球之肾的价值',
        'category': 'habitat',
        'summary': '湿地被誉为地球之肾，具有调节水文、净化水质、碳汇等重要生态服务功能，是人类赖以生存的重要生态系统。',
        'content': '<p>湿地是地球上生产力最高的生态系统之一，与森林、海洋并称为全球三大生态系统。湿地具有不可替代的生态服务功能，被形象地称为地球之肾。</p><h3>水文调节功能</h3><p>湿地像一块巨大的海绵，在雨季吸收和储存大量降水，在旱季缓慢释放。研究表明，1公顷湿地可蓄积1000-2000立方米的洪水。郑州黄河湿地每年可调节数百万立方米的黄河径流，有效减轻下游洪涝灾害。</p><h3>水质净化功能</h3><p>湿地中的植物、微生物和土壤共同作用，可有效去除水体中的悬浮物、氮、磷等污染物。郑州黄河湿地每年可净化处理大量黄河来水中的污染物，对改善黄河水质发挥着重要作用。</p><h3>碳汇功能</h3><p>湿地储存了全球约三分之一的土壤碳，是重要的碳汇区域。郑州黄河湿地的芦苇沼泽每年可固定大量二氧化碳，对缓解气候变化具有积极意义。</p>',
    },
    {
        'title': '大天鹅：郑州黄河湿地的冬日精灵',
        'category': 'species',
        'summary': '每年冬季，成群的大天鹅飞临郑州黄河湿地越冬，成为冬日里最动人的风景线。',
        'content': '<p>大天鹅（Cygnus cygnus）是郑州黄河湿地冬季最壮观的鸟类之一。每年11月至次年3月，成群的大天鹅从遥远的西伯利亚飞临此地，在黄河湿地嬉戏觅食，成为冬日里最动人的风景线。</p><h3>形态特征</h3><p>大天鹅体型宏大，体长约140-160厘米，翼展可达2.4米。全身羽毛雪白，嘴基部黄色、端部黑色，形成鲜明的对比。幼鸟体色灰褐色，需要经过数年才能完全变为白色。</p><h3>生活习性</h3><p>大天鹅主要在开阔的深水区活动，以水生植物的根茎、叶片和种子为主食，也会取食少量小型水生动物。它们通常成对或小群活动，繁殖期外具有强烈的群居性。</p><h3>保护状况</h3><p>大天鹅是国家二级重点保护野生动物，被列入《世界自然保护联盟濒危物种红色名录》。郑州黄河湿地作为其重要越冬地，保护好这里的湿地环境对大天鹅种群的延续至关重要。</p>',
    },
    {
        'title': '鸟类的迁徙之谜：它们如何找到回家的路？',
        'category': 'knowledge',
        'summary': '每年数以亿计的候鸟穿越千里万里完成迁徙，它们依靠什么导航系统找到目的地？科学家提出了多种假说。',
        'content': '<p>鸟类的迁徙是自然界最壮观的现象之一。每年春秋两季，数以亿计的候鸟穿越千里万里，在繁殖地和越冬地之间往返。科学家们一直在探索：它们是如何找到正确的方向的？</p><h3>太阳导航</h3><p>许多日行性鸟类依靠太阳的位置来判断方向。它们体内有精确的生物钟，可以根据太阳的位置推算出东西南北四个方向。这种太阳罗盘帮助它们在白天迁徙时保持正确航向。</p><h3>星象导航</h3><p>夜行性迁徙鸟类则利用星空进行导航。科学家发现，许多鸟类能够识别北极星的位置，并以此为参照确定北方。北半球夜间迁徙的鸟类，大多依靠这套星空罗盘导航。</p><h3>地磁场感应</h3><p>这是最令科学家惊叹的导航能力。研究表明，许多鸟类头部含有微小的磁铁矿颗粒，能够感知地球磁场的强度和方向。部分鸟类甚至能看到地球磁场的分布图！这种磁感地图帮助它们在阴天或夜间准确导航。</p><h3>郑州的迁徙通道</h3><p>郑州位于东亚-澳大利亚迁徙路线的重要节点。每年春秋季节，数万只候鸟途经此地，包括雁类、鸭类、鹬鸻类和猛禽等。</p>',
    },
    {
        'title': '保护湿地鸟类的五大行动建议',
        'category': 'news',
        'summary': '保护湿地鸟类需要每个人的参与。本文提出五项切实可行的行动建议，帮助公众参与到湿地保护中来。',
        'content': '<p>湿地鸟类面临栖息地丧失、环境污染、非法捕猎等多重威胁。保护它们需要全社会的共同参与。以下是五项每个人都可以做到的行动建议：</p><h3>1. 减少一次性塑料使用</h3><p>塑料垃圾进入湿地后会分解成微塑料，被鸟类误食或通过食物链累积。每年约有数百万只海鸟因塑料污染死亡。减少使用塑料袋、塑料餐具，选择可重复使用的物品。</p><h3>2. 支持可持续消费</h3><p>购买湿地友好认证的产品，选择有机食品，减少农业化肥和农药的使用。这些化学品最终会流入湿地，破坏鸟类栖息环境。</p><h3>3. 参与志愿服务</h3><p>加入当地环保组织，参与湿地清洁、鸟类调查等志愿活动。郑州黄河湿地保护区经常组织公众参与的保护活动。</p><h3>4. 科学观鸟</h3><p>学习正确的观鸟方法，使用双筒望远镜远距离观察。保持安静，不干扰鸟类正常活动，不追逐或惊吓鸟类。</p><h3>5. 传播保护理念</h3><p>向家人朋友宣传湿地保护的重要性，分享观鸟体验。让更多人了解和关注湿地鸟类保护。</p>',
    },
    {
        'title': '鹭类鸟类：湿地生态系统的优雅精灵',
        'category': 'species',
        'summary': '鹭类是湿地生态系统中最具代表性的鸟类类群之一，形态优雅，行为有趣，是湿地健康的指示物种。',
        'content': '<p>鹭类是一类适应湿地生活的中大型涉禽，全世界共有约60种，我国有约22种。郑州黄河湿地常见鹭类包括白鹭、夜鹭、苍鹭、大白鹭等。</p><h3>形态特征</h3><p>鹭类具有共同的外形特征：长腿、长颈、长喙，脚趾间有发达的蹼。这些特征使它们特别适应浅水涉水觅食的生活。不同种类的鹭类体型差异很大，从30厘米的小苇鳽到1.5米的大天鹅鹭不等。</p><h3>觅食技巧</h3><p>鹭类主要通过视觉捕食，发现猎物后快速伸长颈部用喙啄取。它们食性多样，包括鱼类、蛙类、昆虫、甲壳类等。苍鹭以守株待兔式的捕猎方式著称，常站立数小时等待猎物靠近。</p><h3>繁殖行为</h3><p>大多数鹭类集群繁殖，形成大型的鹭鸶巢群落。繁殖季节，鹭类会长出繁殖羽，通过求偶舞蹈吸引配偶。雏鸟为早成性，孵化后不久即可活动。</p><h3>生态指示作用</h3><p>鹭类对湿地环境变化非常敏感，被广泛用作湿地健康的指示物种。一个鹭类种类丰富、数量稳定的湿地，通常意味着生态系统健康。</p>',
    },
    {
        'title': '郑州观鸟胜地推荐：黄河湿地公园不完全指南',
        'category': 'knowledge',
        'summary': '郑州及周边有哪些值得推荐的观鸟地点？本文为你详细介绍郑州主要的观鸟胜地及其特色鸟种。',
        'content': '<p>郑州及周边地区拥有丰富的鸟类资源，以下是几个主要的观鸟胜地推荐：</p><h3>郑州黄河湿地自然保护区</h3><p>郑州黄河湿地国家级自然保护区是郑州最重要的观鸟地点。最佳观鸟季节为每年10月至次年3月。特色鸟种包括大天鹅、灰鹤、雁鸭类和各类鹬鸻类。保护区内建有观鸟屋和观景台，建议使用单筒观鸟镜。</p><h3>花园口湿地</h3><p>花园口黄河滩区是郑州城区最近的观鸟地点之一。春秋迁徙季节可看到成群的鸻鹬类水鸟。冬季常有大量雁鸭类在此停歇。</p><h3>西流湖公园</h3><p>西流湖公园位于郑州市区，是观察林鸟的好去处。常见鸟种包括灰喜鹊、喜鹊、白头鹎、珠颈斑鸠等，适合初学者练习观鸟技巧。</p><h3>郑州树木园</h3><p>郑州树木园植被丰富，是观察林鸟和猛禽的好地方。春秋迁徙季节可看到各类鹟类和柳莺。</p><h3>观鸟注意事项</h3><p>无论在哪里观鸟，都请保持安静，不干扰鸟类。带上充足的饮用水和防晒用品，穿着与自然协调的服装。</p>',
    },
    {
        'title': '濒危水鸟系列：勺嘴鹬——世界上最稀有的鸟种之一',
        'category': 'species',
        'summary': '勺嘴鹬是世界上最濒危的鸟类之一，全球种群不足700只。郑州黄河湿地偶有记录，每一笔观察记录都弥足珍贵。',
        'content': '<p>勺嘴鹬（Calidris pygmaea）是世界上最濒危的鸟类之一，被世界自然保护联盟（IUCN）列为极危物种，全球种群数量估计不足700只。</p><h3>独特的外形</h3><p>勺嘴鹬最显著的特征是它独特的喙——喙端扩展成勺状，这是它们在泥沙滩涂觅食的完美工具。它们会用这张勺子在浅水中左右摆动，滤食小型甲壳类和昆虫。</p><h3>危机四伏的生存</h3><p>勺嘴鹬面临多重威胁：繁殖地（俄罗斯西伯利亚）破坏、迁徙中途停歇地丧失、非法捕猎等。它们每年需要在繁殖地和越冬地（主要在东南亚）之间往返，任何一个环节出问题都可能导致种群崩溃。</p><h3>郑州的记录</h3><p>郑州黄河湿地作为东亚-澳大利亚迁徙路线的重要站点，偶有勺嘴鹬的记录。每一次观察记录对于研究这一物种的迁徙路线都至关重要。</p><h3>保护行动</h3><p>国际社会正在开展勺嘴鹬的拯救行动，包括人工繁殖、栖息地保护、迁徙路线监测等。保护好沿途的湿地，是拯救这一物种的关键。</p>',
    },
    {
        'title': '春季观鸟指南：三月至五月郑州鸟类观察重点',
        'category': 'knowledge',
        'summary': '春季是郑州观鸟的黄金季节，本文为你详细介绍春季各月份的观鸟重点和特色鸟种。',
        'content': '<p>春季是郑州观鸟的最佳季节之一，鸟类从南方的越冬地陆续北迁，途经郑州黄河湿地。以下是各月份的观鸟重点：</p><h3>三月份：雁鸭类高峰</h3><p>三月上中旬是雁鸭类北迁的高峰期。此时可看到大天鹅、小天鹅、鸿雁、豆雁等数十种雁鸭类在黄河滩涂集结觅食。清晨和傍晚是观察的最佳时段。</p><h3>四月份：鸻鹬类登场</h3><p>四月中下旬，大量鸻鹬类从南方飞抵郑州。勺嘴鹬、黑翅长脚鹬、反嘴鹬、白腰杓鹬等陆续出现。这个季节在黄河滩涂可以看到数百只鸻鹬类同时觅食的壮观场面。</p><h3>五月份：林鸟迁徙</h3><p>五月初是林鸟迁徙的高峰期。各种鹟类、柳莺、鸫类陆续过境。清晨在林地边缘可以听到此起彼伏的鸟鸣声，这是观鸟的最佳时节。</p><h3>春季观鸟小贴士</h3><p>春季观鸟建议早起，鸟类在清晨最为活跃。携带充足的水和防晒用品，穿着与自然协调的服装。迁徙季节天气多变，注意防寒保暖。</p>',
    },
    {
        'title': '郑州湿地生态修复：还母亲河一片绿洲',
        'category': 'habitat',
        'summary': '近年来，郑州市大力推进黄河湿地生态修复工程，通过退耕还湿、水系连通等举措，湿地生态功能逐步恢复。',
        'content': '<p>黄河是中华民族的母亲河，保护黄河湿地对区域生态安全至关重要。近年来，郑州市大力推进黄河湿地生态修复工程，取得显著成效。</p><h3>退耕还湿</h3><p>郑州市将黄河滩区内的耕地逐步退出，恢复湿地生态功能。截至目前，已累计完成退耕还湿面积超过2000公顷，种植芦苇、香蒲等湿地植物300余万株。</p><h3>水系连通</h3><p>通过打通断头河、疏通河道等措施，恢复黄河与周边湿地的水系连通。这不仅改善了湿地水文条件，也提高了区域防洪能力。</p><h3>湿地植被恢复</h3><p>人工种植和自然恢复相结合，恢复芦苇沼泽、香蒲沼泽等典型湿地植被类型。这些植被为鸟类提供了优质的栖息和繁殖场所。</p><h3>成效显著</h3><p>生态修复工程实施以来，郑州黄河湿地鸟类种类和数量均有明显增加。大天鹅、中华秋沙鸭等珍稀鸟类的记录次数逐年上升，湿地生态系统逐步恢复健康。</p>',
    },
    {
        'title': '雁鸭类水鸟：湿地生态系统的重要组成部分',
        'category': 'species',
        'summary': '雁鸭类是湿地生态系统中最具代表性的鸟类类群，本文介绍雁鸭类的基本知识以及郑州地区的常见种类。',
        'content': '<p>雁鸭类是雁形目鸭科鸟类的统称，全世界约150种，我国产约50种。郑州黄河湿地是雁鸭类重要的迁徙停歇地和越冬地。</p><h3>雁与鸭的区别</h3><p>雁类和鸭类虽同属雁形目，但形态和习性有所不同。雁类体型较大，颈长，飞行时呈人字或一字队列，如鸿雁、豆雁、天鹅等。鸭类体型较小，通常在水面活动，如绿头鸭、斑嘴鸭等。</p><h3>郑州常见雁鸭类</h3><p>郑州地区迁徙季节常见的雁类包括大天鹅、小天鹅、鸿雁、豆雁、白额雁等；常见鸭类包括斑嘴鸭、绿头鸭、绿翅鸭、赤颈鸭等。冬季在黄河湿地可看到数千只雁鸭类集群的壮观场面。</p><h3>生态功能</h3><p>雁鸭类是湿地生态系统的重要组成部分。它们取食水生植物，控制水草过度生长；通过粪便为水体提供养分；被捕食者捕食，维持食物链平衡。</p>',
    },
    {
        'title': '公民科学：普通公众如何参与鸟类监测',
        'category': 'news',
        'summary': '公民科学让普通公众也能参与到鸟类监测中来。本文介绍如何通过观鸟记录为科学研究贡献力量。',
        'content': '<p>公民科学（Citizen Science）是指普通公众参与科学研究的项目。在鸟类监测领域，公民科学发挥着越来越重要的作用，普通观鸟爱好者的观察记录可以产生宝贵的科学数据。</p><h3>如何参与</h3><p>国内外有多个鸟类记录平台供公众提交观察记录：中国观鸟记录中心（www.birdreport.cn）是国内最大的观鸟记录平台；eBird（ebird.org）是全球最大的鸟类观察记录数据库；郑州黄河湿地保护区定期组织公众参与的鸟类调查活动。</p><h3>记录什么</h3><p>每次观鸟后，记录观察地点、日期时间、物种名称、数量等信息。最好能记录下鸟类的行为（觅食、飞行、鸣唱等）。有条件的话拍摄照片作为凭证。</p><h3>数据的重要性</h3><p>这些看似简单的观察记录，累积起来可以揭示鸟类的分布变化趋势、迁徙时间规律、种群数量波动等重要信息。许多重要的科学发现都离不开公民科学数据的支撑。</p>',
    },
    {
        'title': '冬季观鸟：郑州黄河湿地的冬日候鸟',
        'category': 'knowledge',
        'summary': '冬季虽然天气寒冷，却是观察冬候鸟的最佳时节。本文介绍郑州冬季的主要观鸟目标。',
        'content': '<p>冬季是观察冬候鸟的最佳时节。虽然天气寒冷，但郑州黄河湿地此时迎来了最壮观的鸟类群落。</p><h3>冬季观鸟目标</h3><p>冬季郑州黄河湿地的主要观鸟目标包括：雁类如豆雁、灰雁、鸿雁等常形成数百只的大群；天鹅类如大天鹅、小天鹅优雅的身影是冬日最美的风景；鸭类如凤头潜鸭、红头潜鸭、普通秋沙鸭等数十种；鹬类如白腰草鹬、林鹬等留鸟冬季仍然活跃；猛禽如普通鵟、大鵟、白尾鹞等冬季较为常见。</p><h3>观鸟技巧</h3><p>冬季观鸟建议穿着保暖、防风的衣物，戴手套（方便操作望远镜）。清晨是鸟类最活跃的时段。选择视野开阔的观鸟点，如黄河大堤。携带高倍望远镜和单筒观鸟镜观察远处的水鸟。</p><h3>安全提示</h3><p>冬季黄河滩涂可能存在安全隐患，避免进入未开放区域。携带手机以备紧急联络，穿着颜色鲜亮的服装以便同伴识别。</p>',
    },
    {
        'title': '猛禽观察：天空中的顶级捕食者',
        'category': 'species',
        'summary': '猛禽是鸟类中的顶级捕食者，在生态系统中扮演着重要角色。郑州地区有哪些猛禽？如何在野外观察它们？',
        'content': '<p>猛禽是鸟类中进化最成功的类群之一，包括鹰形目和隼形目的所有种类。它们位于食物链顶端，是湿地和森林生态系统健康的重要指示物种。</p><h3>郑州可见猛禽</h3><p>郑州地区可见的猛禽超过30种，包括鹰类（雀鹰、苍鹰、普通鵟、大鵟）、鹞类（白尾鹞、鹊鹞、白头鹞）、隼类（红隼、红脚隼、游隼）、鸮类（纵纹腹小鸮、长耳鸮、短耳鸮）等。</p><h3>观察技巧</h3><p>猛禽常在开阔地带的高处停歇，如电线杆、树顶。秋季迁徙季节，常可看到猛禽借助上升气流盘旋。观鸟者可以关注天空，寻找翅膀呈V形（鹞类）或翅膀平展（鹰类）的身影。</p><h3>保护意义</h3><p>猛禽对环境变化极为敏感，其种群数量可直接反映生态系统健康状况。保护猛禽，需要保护其栖息地和猎物资源。</p>',
    },
]


def add_species():
    added = 0
    skipped = 0
    for data in species_data:
        exists = SpeciesInfo.objects.filter(name_cn=data['name_cn']).exists()
        if exists:
            skipped += 1
            print(f'  跳过已存在: {data["name_cn"]}')
            continue
        SpeciesInfo.objects.create(**data)
        added += 1
        print(f'  + 添加物种: {data["name_cn"]} ({data["name_latin"]})')
    print(f'\n物种添加完成: 新增 {added} 个，跳过 {skipped} 个已存在的')
    return added


def add_articles():
    added = 0
    skipped = 0
    for data in articles_data:
        exists = Article.objects.filter(title=data['title']).exists()
        if exists:
            skipped += 1
            print(f'  跳过已存在: {data["title"]}')
            continue
        Article.objects.create(
            **data,
            author=author,
            is_published=True,
        )
        added += 1
        print(f'  + 添加文章: {data["title"]}')
    print(f'\n文章添加完成: 新增 {added} 篇，跳过 {skipped} 篇已存在的')
    return added


if __name__ == '__main__':
    print('=' * 50)
    print('开始批量添加数据...')
    print('=' * 50)
    print()
    add_species()
    print()
    add_articles()
    print()
    print('=' * 50)
    print(f'最终统计:')
    print(f'  物种总数: {SpeciesInfo.objects.count()}')
    print(f'  文章总数: {Article.objects.count()}')
    print('=' * 50)
