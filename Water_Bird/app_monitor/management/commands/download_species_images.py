"""
Download species images from Wikimedia Commons and save to local media library.
Fixed: ASCII-safe output for Windows Latin-1 terminals, fallback image support.
"""
import os
import sys
import time
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from app_monitor.models import SpeciesInfo, SpeciesImage

COMMONS_API_URL = 'https://commons.wikimedia.org/w/api.php'
USER_AGENT = 'WaterBirdApp/1.0 (Yellow River Eco Ark)'

FALLBACK_IMAGES = {
    '大天鹅': 'https://upload.wikimedia.org/wikipedia/commons/2/28/Cygnus_cygnus.jpg',
    '白鹭': 'https://upload.wikimedia.org/wikipedia/commons/9/91/Egretta_garzetta.jpg',
    '鸿雁': 'https://upload.wikimedia.org/wikipedia/commons/1/15/Anser_cygnoides.jpg',
    '黑鹳': 'https://upload.wikimedia.org/wikipedia/commons/8/8c/Ciconia_nigra.jpg',
    '东方白鹳': 'https://upload.wikimedia.org/wikipedia/commons/0/03/Stamp_of_India_-_1994_-_Colnect_163829_-_Oriental_White_Stork_Ciconia_boyciana.jpeg',
    '灰鹤': 'https://upload.wikimedia.org/wikipedia/commons/f/f8/Grus_grus.jpg',
    '普通鸬鹚': 'https://upload.wikimedia.org/wikipedia/commons/c/ce/Phalacrocorax_carbo.jpg',
    '斑嘴鸭': 'https://upload.wikimedia.org/wikipedia/commons/3/39/Anas_zonorhyncha.jpg',
    '白头鹤': 'https://upload.wikimedia.org/wikipedia/commons/2/25/Grus_monacha.jpg',
    '豆雁': 'https://upload.wikimedia.org/wikipedia/commons/e/ea/Anser_fabalis.jpg',
    '苍鹭': 'https://upload.wikimedia.org/wikipedia/commons/d/d3/Ardea_cinerea.jpg',
    '绿头鸭': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Anas_platyrhynchos.jpg',
    '夜鹭': 'https://upload.wikimedia.org/wikipedia/commons/a/a1/Nycticorax_nycticorax.jpg',
    '黑水鸡': 'https://upload.wikimedia.org/wikipedia/commons/2/26/Gallinula_chloropus.jpg',
    '白骨顶': 'https://upload.wikimedia.org/wikipedia/commons/2/20/Fulica_atra.jpg',
    '凤头麦鸡': 'https://upload.wikimedia.org/wikipedia/commons/2/29/Vanellus_vanellus.jpg',
    '金眶鸻': 'https://upload.wikimedia.org/wikipedia/commons/d/df/Charadrius_dubius.jpg',
    '普通翠鸟': 'https://upload.wikimedia.org/wikipedia/commons/f/ff/Alcedo_atthis.jpg',
    '斑鱼狗': 'https://upload.wikimedia.org/wikipedia/commons/0/04/Ceryle_rudis.jpg',
    '小天鹅': 'https://upload.wikimedia.org/wikipedia/commons/4/4a/Cygnus_bewickii_01.jpg',
    '灰雁': 'https://upload.wikimedia.org/wikipedia/commons/d/d8/Anser_anser.jpg',
    '白额雁': 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Greater_white-fronted_goose_in_flight-1045.jpg',
    '翘鼻麻鸭': 'https://upload.wikimedia.org/wikipedia/commons/f/fc/Tadorna_tadorna_2.jpg',
    '赤颈鸭': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Mareca_penelope.jpg',
    '绿翅鸭': 'https://upload.wikimedia.org/wikipedia/commons/d/d5/Anas_crecca.jpg',
    '赤膀鸭': 'https://upload.wikimedia.org/wikipedia/commons/d/de/Mareca_strepera.jpg',
    '普通秋沙鸭': 'https://upload.wikimedia.org/wikipedia/commons/9/95/Mergus_merganser.jpg',
    '中华秋沙鸭': 'https://upload.wikimedia.org/wikipedia/commons/9/97/Scaly-sided_Merganser_RWD.jpg',
    '白秋沙鸭': 'https://upload.wikimedia.org/wikipedia/commons/2/2e/Mergellus_albellus.jpg',
    '鹌鹑': 'https://upload.wikimedia.org/wikipedia/commons/d/de/Coturnix_coturnix.jpg',
    '环颈雉': 'https://upload.wikimedia.org/wikipedia/commons/9/9f/Phasianus_colchicus.jpg',
    '黑翅长脚鹬': 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Himantopus_hemantopus.jpg',
    '反嘴鹬': 'https://upload.wikimedia.org/wikipedia/commons/6/62/Recurvirostra_avosetta_2.jpg',
    '红嘴鸥': 'https://upload.wikimedia.org/wikipedia/commons/8/8b/Chroicocephalus_ridibundus.jpg',
    '普通燕鸥': 'https://upload.wikimedia.org/wikipedia/commons/3/3f/Sterna_hirundo.jpg',
    '白琵鹭': 'https://upload.wikimedia.org/wikipedia/commons/2/2d/Platalea_leucorodia.jpg',
    '戴胜': 'https://upload.wikimedia.org/wikipedia/commons/2/25/Upupa_epops.jpg',
    '大斑啄木鸟': 'https://upload.wikimedia.org/wikipedia/commons/3/3f/Dendrocopos_major.jpg',
    '大杜鹃': 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Cuculus_canorus.jpg',
    '红隼': 'https://upload.wikimedia.org/wikipedia/commons/6/6e/Falco_tinnunculus.jpg',
    '游隼': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Falco_peregrinus.jpg',
    '雀鹰': 'https://upload.wikimedia.org/wikipedia/commons/3/31/Accipiter_nisus.jpg',
    '苍鹰': 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Accipiter_gentilis.jpg',
    '普通鵟': 'https://upload.wikimedia.org/wikipedia/commons/d/dc/Buteo_japonicus_108780228.jpg',
    '白尾鹞': 'https://upload.wikimedia.org/wikipedia/commons/8/87/Circus_cyaneus.jpg',
    '黑翅鸢': 'https://upload.wikimedia.org/wikipedia/commons/4/49/Elanus_caeruleus.jpg',
    '纵纹腹小鸮': 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Athene_noctua.jpg',
    '长耳鸮': 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Asio_otus.jpg',
    '短耳鸮': 'https://upload.wikimedia.org/wikipedia/commons/7/7e/Asio_flammeus.jpg',
    '八哥': 'https://upload.wikimedia.org/wikipedia/commons/8/83/Acridotheres_cristatellus.jpg',
    '灰椋鸟': 'https://upload.wikimedia.org/wikipedia/commons/4/47/Spodiopsar_cineraceus.jpg',
    '灰喜鹊': 'https://upload.wikimedia.org/wikipedia/commons/0/00/Cyanopica_cyanus.jpg',
    '喜鹊': 'https://upload.wikimedia.org/wikipedia/commons/3/33/Pica_pica.jpg',
    '松鸦': 'https://upload.wikimedia.org/wikipedia/commons/f/f2/Garrulus_glandarius.jpg',
    '北红尾鸲': 'https://upload.wikimedia.org/wikipedia/commons/7/7e/Phoenicurus_auroreus.jpg',
    '红喉歌鸲': 'https://upload.wikimedia.org/wikipedia/commons/f/f7/Luscinia_calliope.jpg',
    '蓝喉歌鸲': 'https://upload.wikimedia.org/wikipedia/commons/5/54/Luscinia_svecica.jpg',
    '黑枕黄鹂': 'https://upload.wikimedia.org/wikipedia/commons/7/78/Oriolus_chinensis.jpg',
    '树麻雀': 'https://upload.wikimedia.org/wikipedia/commons/d/d6/Passer_montanus.jpg',
    '白鹡鸰': 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Motacilla_alba.jpg',
    '灰鹡鸰': 'https://upload.wikimedia.org/wikipedia/commons/0/0a/Motacilla_cinerea.jpg',
    '小鹀': 'https://upload.wikimedia.org/wikipedia/commons/7/73/Emberiza_pusilla.jpg',
    '黄喉鹀': 'https://upload.wikimedia.org/wikipedia/commons/5/56/Emberiza_elegans.jpg',
    '金翅雀': 'https://upload.wikimedia.org/wikipedia/commons/5/51/Chloris_sinica_MHNT_226_%C3%8Ele_s_Kouriles_HdB.jpg',
    '黄雀': 'https://upload.wikimedia.org/wikipedia/commons/5/5b/Spinus_spinus.jpg',
    '燕雀': 'https://upload.wikimedia.org/wikipedia/commons/3/3a/Fringilla_montifringilla.jpg',
    '红颈滨鹬': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Calidris_ruficollis.jpg',
    '黑腹滨鹬': 'https://upload.wikimedia.org/wikipedia/commons/b/b9/Calidris_alpina.jpg',
    '青脚鹬': 'https://upload.wikimedia.org/wikipedia/commons/3/3c/Tringa_nebularia.jpg',
    '白腰草鹬': 'https://upload.wikimedia.org/wikipedia/commons/8/8c/Common_Sandpiper_%28Actitis_hypoleucos%29%2C_Sfax%2C_Tunisia.jpg',
    '遗鸥': 'https://upload.wikimedia.org/wikipedia/commons/3/31/Relict_Gull.jpg',
}

NAME_TRANSLATIONS = {
    '大天鹅': 'Whooper Swan', '白鹭': 'Little Egret', '鸿雁': 'Swan Goose',
    '黑鹳': 'Black Stork', '东方白鹳': 'Oriental Stork', '灰鹤': 'Common Crane',
    '普通鸬鹚': 'Great Cormorant', '斑嘴鸭': 'Indian Spot-billed Duck',
    '白头鹤': 'Hooded Crane', '豆雁': 'Taiga Bean Goose', '苍鹭': 'Grey Heron',
    '绿头鸭': 'Mallard', '夜鹭': 'Black-crowned Night Heron',
    '黑水鸡': 'Common Moorhen', '白骨顶': 'Eurasian Coot',
    '凤头麦鸡': 'Northern Lapwing', '金眶鸻': 'Little Ringed Plover',
    '普通翠鸟': 'Common Kingfisher', '斑鱼狗': 'Pied Kingfisher',
    '小天鹅': 'Tundra Swan', '灰雁': 'Greylag Goose',
    '白额雁': 'Greater White-fronted Goose', '翘鼻麻鸭': 'Common Shelduck',
    '赤颈鸭': 'Eurasian Wigeon', '绿翅鸭': 'Common Teal',
    '赤膀鸭': 'Gadwall', '罗纹鸭': 'Falcated Duck',
    '赤嘴潜鸭': 'Red-crested Pochard', '凤头潜鸭': 'Ferruginous Duck',
    '普通秋沙鸭': 'Common Merganser', '中华秋沙鸭': 'Scaly-sided Merganser',
    '白秋沙鸭': 'Smew', '鹌鹑': 'Common Quail', '环颈雉': 'Common Pheasant',
    '黑翅长脚鹬': 'Black-winged Stilt', '反嘴鹬': 'Pied Avocet',
    '黑尾塍鹬': 'Black-tailed Godwit', '白腰杓鹬': 'Eurasian Curlew',
    '大滨鹬': 'Great Knot', '红嘴鸥': 'Black-headed Gull',
    '普通燕鸥': 'Common Tern', '白琵鹭': 'Eurasian Spoonbill',
    '戴胜': 'Eurasian Hoopoe', '大斑啄木鸟': 'Great Spotted Woodpecker',
    '星头啄木鸟': 'Grey-capped Pygmy Woodpecker',
    '灰头绿啄木鸟': 'Grey-faced Woodpecker', '大杜鹃': 'Common Cuckoo',
    '四声杜鹃': 'Indian Cuckoo', '红隼': 'Common Kestrel',
    '红脚隼': 'Amur Falcon', '游隼': 'Peregrine Falcon',
    '雀鹰': 'Eurasian Sparrowhawk', '日本松雀鹰': 'Japanese Sparrowhawk',
    '苍鹰': 'Northern Goshawk', '普通鵟': 'Eastern Buzzard',
    '大鵟': 'Upland Buzzard', '白尾鹞': 'Hen Harrier',
    '鹊鹞': 'Pied Harrier', '黑翅鸢': 'Black-winged Kite',
    '白头鹞': 'Western Marsh Harrier', '纵纹腹小鸮': 'Little Owl',
    '长耳鸮': 'Long-eared Owl', '短耳鸮': 'Short-eared Owl',
    '领鸺鹠': 'Collared Owlet', '斑头鸺鹠': 'Asian Barred Owlet',
    '草鸮': 'Eastern Grass Owl', '东方大苇莺': 'Oriental Reed Warbler',
    '黑眉苇莺': 'Black-browed Reed Warbler', '纯色山鹪莺': 'Plain Prinia',
    '棕扇尾莺': 'Zitting Cisticola', '小鸦鹃': 'Lesser Coucal',
    '噪鹃': 'Asian Koel', '八哥': 'Crested Myna',
    '灰椋鸟': 'White-cheeked Starling', '丝光椋鸟': 'Red-billed Starling',
    '黑领椋鸟': 'Black-collared Starling', '灰喜鹊': 'Azure-winged Magpie',
    '喜鹊': 'Eurasian Magpie', '达乌里寒鸦': 'Daurian Jackdaw',
    '小嘴乌鸦': 'Carrion Crow', '大嘴乌鸦': 'Large-billed Crow',
    '白颈鸦': 'Collared Crow', '松鸦': 'Eurasian Jay',
    '红尾水鸲': 'Plumbeous Redstart', '白顶溪鸲': 'White-capped Redstart',
    '北红尾鸲': 'Daurian Redstart', '红喉姬鹟': 'Red-breasted Flycatcher',
    '白眉姬鹟': 'Yellow-rumped Flycatcher', '鸲姬鹟': 'Narcissus Flycatcher',
    '北灰鹟': 'Asian Brown Flycatcher', '乌鹟': 'Dark-sided Flycatcher',
    '灰纹鹟': 'Grey-streaked Flycatcher', '红喉歌鸲': 'Siberian Rubythroat',
    '蓝喉歌鸲': 'Bluethroat', '黑枕黄鹂': 'Black-naped Oriole',
    '黑卷尾': 'Black Drongo', '灰卷尾': 'Ashy Drongo',
    '发冠卷尾': 'Hair-crested Drongo', '寿带鸟': 'Asian Paradise Flycatcher',
    '山麻雀': 'Russet Sparrow', '树麻雀': 'Eurasian Tree Sparrow',
    '白鹡鸰': 'White Wagtail', '灰鹡鸰': 'Grey Wagtail',
    '黄头鹡鸰': 'Citrine Wagtail', '黄鹡鸰': 'Eastern Yellow Wagtail',
    '小鹀': 'Little Bunting', '黄眉鹀': 'Yellow-browed Bunting',
    '白眉鹀': "Tristram's Bunting", '栗耳鹀': 'Chestnut-eared Bunting',
    '黄喉鹀': 'Yellow-throated Bunting', '灰头鹀': 'Black-faced Bunting',
    '三道眉草鹀': 'Ochre-rumped Bunting', '燕雀': 'Brambling',
    '金翅雀': 'Grey-capped Greenfinch', '黑头蜡嘴雀': 'Japanese Grosbeak',
    '黑尾蜡嘴雀': 'Chinese Grosbeak', '锡嘴雀': 'Hawfinch',
    '苍头燕雀': 'Common Chaffinch', '黄雀': 'Eurasian Siskin',
    '红颈滨鹬': 'Red-necked Stint', '青脚滨鹬': "Temminck's Stint",
    '弯嘴滨鹬': 'Curlew Sandpiper', '黑腹滨鹬': 'Dunlin',
    '白腰草鹬': 'Common Sandpiper', '林鹬': 'Wood Sandpiper',
    '青脚鹬': 'Common Greenshank', '红脚鹬': 'Common Redshank',
    '泽鹬': 'Marsh Sandpiper', '鹤鹬': 'Spotted Redshank',
    '矸鹬': 'Green Sandpiper', '扇尾沙锥': 'Great Snipe',
    '针尾沙锥': "Swinhoe's Snipe", '勺嘴鹬': 'Spoon-billed Sandpiper',
    '小青脚鹬': "Nordmann's Greenshank", '遗鸥': 'Relict Gull',
}

# ASCII-safe output helper
def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        safe = msg.encode('ascii', 'replace').decode('ascii')
        print(safe)


NON_IMAGE_EXTS = {'.djvu', '.pdf', '.svg', '.ogg', '.mid', '.webm', '.mp3', '.mp4', '.flac'}

def find_image_url(species_name_cn, latin_name=None):
    # Priority 1: direct fallback URL
    if species_name_cn in FALLBACK_IMAGES:
        return {'url': FALLBACK_IMAGES[species_name_cn], 'title': species_name_cn, 'source': 'wikimedia'}

    en_name = NAME_TRANSLATIONS.get(species_name_cn)
    headers = {'User-Agent': USER_AGENT}

    # Strategy 1: search by English name (most reliable for birds)
    search_terms = []
    if en_name:
        search_terms.append(en_name)
    if latin_name:
        search_terms.append(latin_name.replace(' ', '_'))

    for term in search_terms:
        result = _search_commons(term, headers)
        if result:
            return result

    # Strategy 2: search by Chinese name + filter out non-images
    result = _search_commons(species_name_cn, headers, filter_non_images=True)
    if result:
        return result

    # Strategy 3: search by Chinese name without filter
    result = _search_commons(species_name_cn, headers, filter_non_images=False)
    if result:
        return result

    return None


def _search_commons(term, headers, filter_non_images=False):
    """Search Wikimedia Commons and return first valid image URL"""
    params = {
        'action': 'query', 'format': 'json', 'list': 'search',
        'srsearch': term, 'srnamespace': 6, 'srlimit': 8, 'origin': '*',
    }
    try:
        resp = requests.get(COMMONS_API_URL, params=params, headers=headers, timeout=10)
        data = resp.json()
        results = data.get('query', {}).get('search', [])
        if not results:
            return None

        for result in results:
            title = result.get('title', '')
            if not title.lower().startswith('file:'):
                title = 'File:' + title

            # Filter non-image files
            if filter_non_images:
                lower_title = title.lower()
                if any(lower_title.endswith(ext) for ext in NON_IMAGE_EXTS):
                    continue

            img_params = {
                'action': 'query', 'format': 'json', 'titles': title,
                'prop': 'pageimages', 'pithumbsize': 800, 'origin': '*',
            }
            img_resp = requests.get(COMMONS_API_URL, params=img_params, headers=headers, timeout=10)
            img_data = img_resp.json()
            pages = img_data.get('query', {}).get('pages', {})

            for page_id, page in pages.items():
                if page_id == '-1':
                    continue
                if 'thumbnail' in page:
                    thumb_url = page['thumbnail']['source']
                    return {'url': thumb_url, 'title': title.replace('File:', ''), 'source': 'wikimedia'}
    except Exception:
        pass
    return None


def download_image_data(url):
    try:
        headers = {'User-Agent': USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None


def get_safe_filename(name):
    safe = name.replace('/', '_').replace('\\', '_').replace(':', '_')
    safe = ''.join(c for c in safe if c.isalnum() or c in (' ', '-', '_', '.'))
    return safe[:100]


class Command(BaseCommand):
    help = 'Download species images from Wikimedia Commons to local media'

    def add_arguments(self, parser):
        parser.add_argument('--species', type=str, help='Download for specific species only')
        parser.add_argument('--force', action='store_true', help='Re-download even if image exists')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of downloads')

    def handle(self, *args, **options):
        target = options.get('species')
        force = options.get('force', False)
        limit = options.get('limit', 0)

        if target:
            species_list = SpeciesInfo.objects.filter(name_cn=target)
            if not species_list.exists():
                self.stderr.write(self.style.ERROR(f'Species not found: {target}'))
                return
        else:
            species_list = SpeciesInfo.objects.all().order_by('name_cn')

        total = species_list.count()
        downloaded = skipped = failed = 0

        log(f'\n=== Starting download, {total} species ===\n')

        for i, species in enumerate(species_list):
            existing = SpeciesImage.objects.filter(species=species, source='wikimedia').first()
            if existing and not force:
                skipped += 1
                log(f'[{i+1}/{total}] SKIP (has image): {species.name_cn}')
                continue

            log(f'[{i+1}/{total}] Downloading: {species.name_cn}')

            info = find_image_url(species.name_cn, species.name_latin)
            if not info:
                log(f'  -> No image found')
                failed += 1
                continue

            log(f'  -> Found: {info["title"]}')
            img_data = download_image_data(info['url'])
            if not img_data:
                failed += 1
                continue

            try:
                if existing:
                    if existing.image:
                        existing.image.delete(save=True)
                    existing.delete()

                img_instance = SpeciesImage(species=species)
                safe_name = get_safe_filename(species.name_cn)
                ext = os.path.splitext(info['url'])[1]
                if not ext or len(ext) > 5:
                    ext = '.jpg'
                filename = f'{safe_name}{ext}'

                img_instance.image.save(filename, ContentFile(img_data), save=False)
                img_instance.caption = info['title']
                img_instance.source = 'wikimedia'
                img_instance.source_url = f'https://commons.wikimedia.org/wiki/{info["title"]}'
                img_instance.save()

                downloaded += 1
                log(f'  -> Saved: {filename}')

            except Exception as e:
                safe_err = str(e).encode('ascii', 'replace').decode('ascii')
                log(f'  -> Save failed: {safe_err}')
                failed += 1

            time.sleep(0.3)

            if limit > 0 and (downloaded + skipped) >= limit:
                log(f'\nDownload limit reached: {limit}')
                break

        log(f'\n{"="*50}')
        log(f'Download complete!')
        log(f'  Success: {downloaded}')
        log(f'  Skipped: {skipped}')
        log(f'  Failed:  {failed}')
        log(f'  Total:   {total}')
        log(f'{"="*50}')
