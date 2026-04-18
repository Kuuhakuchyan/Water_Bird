import urllib.request, re

resp = urllib.request.urlopen('http://127.0.0.1:8000/articles/', timeout=5)
html = resp.read().decode('utf-8')

tabs = re.findall(r'data-cat="([^"]+)"', html)
print('分类标签 data-cat 值:', tabs)

nums = re.findall(r'id="(totalCount|habitatCount|speciesCount|knowledgeCount|newsCount)"', html)
print('统计数字 ID:', nums)

funcs = re.findall(r'function (\w+)\(', html)
target = ['loadArticles','filterArticles','setCategory','applyFilters','renderCards']
print('关键JS函数:', [f for f in funcs if f in target])

title = re.search(r'<title>(.*?)</title>', html)
print('页面title:', title.group(1) if title else '未找到')

# 检查是否有中文分类
if '栖息地保护' in html or '物种保护' in html:
    print('WARNING: 模板中包含中文分类标签!')
if 'habitat' in html and 'species' in html:
    print('OK: 模板中包含英文分类代码')
