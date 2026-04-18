import urllib.request, json

resp = urllib.request.urlopen('http://127.0.0.1:8000/api/articles/', timeout=5)
data = json.loads(resp.read())

if isinstance(data, dict):
    data = data.get('results', data)

articles = data
from collections import Counter
counts = Counter(a.get('category', 'NONE') for a in articles)
print('API 返回文章数:', len(articles))
print('分类统计:', dict(counts))

# 检查是否有中文分类
for a in articles:
    cat = a.get('category', '')
    if cat not in ('habitat', 'species', 'knowledge', 'news', '全部'):
        print(f'异常分类: id={a["id"]}, category=[{cat}], title={a.get("title","")[:30]}')
