"""
Enrich the species gallery by fetching multiple images per species from Wikimedia Commons.
Uses batch API requests for speed (one API call per species instead of many per image).
"""
import os
import sys
import time
import requests
from django.core.management.base import BaseCommand
from app_monitor.models import SpeciesInfo, SpeciesImage

COMMONS_API_URL = 'https://commons.wikimedia.org/w/api.php'
USER_AGENT = 'WaterBirdApp/1.0 (Yellow River Eco Ark)'

NAME_TRANSLATIONS = {
    '大天鹅': 'Whooper Swan', '白鹭': 'Little Egret', '鸿雁': 'Swan Goose',
    '黑鹳': 'Black Stork', '东方白鹳': 'Oriental White Stork', '灰鹤': 'Common Crane',
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

NON_IMAGE_EXTS = {'.djvu', '.pdf', '.svg', '.ogg', '.mid', '.webm', '.mp3', '.mp4', '.flac'}


def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        safe = msg.encode('ascii', 'replace').decode('ascii')
        print(safe)


def find_images_batch(species_name_cn, latin_name=None, max_images=5):
    """Find multiple image URLs from Wikimedia Commons using batch API - ONE request per species."""
    en_name = NAME_TRANSLATIONS.get(species_name_cn)
    headers = {'User-Agent': USER_AGENT}
    results = []

    # Build search terms
    search_terms = []
    if en_name:
        search_terms.append(en_name)
    if latin_name:
        search_terms.append(latin_name.replace(' ', '_'))

    seen_titles = set()

    for term in search_terms:
        if len(results) >= max_images:
            break

        # One batch search request per term
        search_params = {
            'action': 'query', 'format': 'json', 'list': 'search',
            'srsearch': term, 'srnamespace': 6, 'srlimit': 15, 'origin': '*',
        }
        try:
            resp = requests.get(COMMONS_API_URL, params=search_params, headers=headers, timeout=15)
            data = resp.json()
            search_results = data.get('query', {}).get('search', [])
            if not search_results:
                continue

            # Collect file titles for batch image lookup
            titles = []
            for result in search_results:
                title = result.get('title', '')
                if not title.lower().startswith('file:'):
                    title = 'File:' + title
                lower_title = title.lower()
                if any(lower_title.endswith(ext) for ext in NON_IMAGE_EXTS):
                    continue
                if title in seen_titles:
                    continue
                titles.append(title)

            if not titles:
                continue

            # BATCH: one request for all images at once
            img_params = {
                'action': 'query', 'format': 'json',
                'titles': '|'.join(titles),
                'prop': 'pageimages', 'pithumbsize': 800, 'origin': '*',
            }
            img_resp = requests.get(COMMONS_API_URL, params=img_params, headers=headers, timeout=15)
            img_data = img_resp.json()
            pages = img_data.get('query', {}).get('pages', {})

            for page_id, page in pages.items():
                if page_id == '-1':
                    continue
                if 'thumbnail' in page:
                    thumb_url = page['thumbnail']['source']
                    title = page.get('title', '').replace('File:', '')
                    if len(results) < max_images:
                        results.append({
                            'url': thumb_url,
                            'title': title,
                            'source': 'wikimedia',
                        })
                        seen_titles.add('File:' + title)

        except Exception:
            pass

        time.sleep(0.15)  # polite rate limiting

    return results[:max_images]


class Command(BaseCommand):
    help = 'Enrich species gallery with multiple images per species from Wikimedia Commons'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0,
                            help='Limit number of species to process (0 = all)')
        parser.add_argument('--max-images', type=int, default=5,
                            help='Maximum images per species (default: 5)')

    def handle(self, *args, **options):
        max_images = options.get('max_images', 5)
        limit = options.get('limit', 0)

        species_list = SpeciesInfo.objects.all().order_by('name_cn')
        total = species_list.count()
        log(f'\n=== Enriching gallery: {total} species, up to {max_images} images each ===')
        log('Using batch API requests for speed (1 request per species per search term)\n')

        added = skipped = failed = 0

        for i, species in enumerate(species_list):
            existing_count = SpeciesImage.objects.filter(species=species).count()

            if (i + 1) % 20 == 0:
                log(f'--- Progress: {i+1}/{total} species processed ---')

            log(f'[{i+1}/{total}] {species.name_cn} (已有 {existing_count} 张)')

            if existing_count >= max_images:
                skipped += 1
                continue

            # Find images - now uses batch requests (much faster)
            images = find_images_batch(
                species.name_cn,
                species.name_latin,
                max_images=max_images
            )

            if not images:
                log(f'  -> No images found')
                failed += 1
                continue

            log(f'  -> Found {len(images)} image(s)')

            # Avoid duplicate URLs
            existing_urls = set(
                SpeciesImage.objects.filter(species=species)
                .exclude(image_url='')
                .values_list('image_url', flat=True)
            )

            saved = 0
            for idx, img_info in enumerate(images):
                if img_info['url'] in existing_urls:
                    continue

                try:
                    is_featured = (idx == 0)
                    SpeciesImage.objects.create(
                        species=species,
                        image_url=img_info['url'],
                        caption=img_info['title'],
                        source='wikimedia',
                        source_url=f'https://commons.wikimedia.org/wiki/{img_info["title"]}',
                        is_featured=is_featured,
                    )
                    existing_urls.add(img_info['url'])
                    saved += 1
                    log(f'    [{idx+1}] Added: {img_info["title"][:50]}')
                except Exception as e:
                    pass

            added += saved

            if limit > 0 and (i + 1) >= limit:
                log(f'\nLimit reached: {limit} species processed')
                break

        log(f'\n{"="*50}')
        log(f'Enrichment complete!')
        log(f'  New images added: {added}')
        log(f'  Skipped (sufficient images): {skipped}')
        log(f'  No images found: {failed}')
        log(f'  Total species: {total}')
        log(f'{"="*50}')
