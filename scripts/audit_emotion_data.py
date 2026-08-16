#!/usr/bin/env python3
"""核查 word-association.html 内嵌情感数据与主语料的口径差异。"""
import re, json, csv, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / 'word-association.html').read_text(encoding='utf-8')

m = re.search(r'var data = (\[.*?\]);', html, re.S)
raw = m.group(1)

# 去尾逗号、去行注释等常见 JS 容错
raw = re.sub(r'//[^\n]*', '', raw)
clean = re.sub(r',\s*([}\]])', r'\1', raw)
try:
    arr = json.loads(clean)
except json.JSONDecodeError as e:
    print('JSON 解析失败:', e)
    ctx = clean.splitlines()
    ln = e.lineno
    print('\n'.join(f'{i+1}: {ctx[i]}' for i in range(max(0, ln-4), min(len(ctx), ln+3))))
    sys.exit(1)

print('=== 情感页内嵌数据 ===')
print('记录数:', len(arr))

DIMS = ['壮怀逸兴', '孤愤悲慨', '死生超然', '同袍之谊', '家国义愤', '功名热望', '功名幻灭', '苍茫孤寂']

# 量程核查
out_of_range = []
vals_all = []
for i, r in enumerate(arr):
    for d in DIMS:
        v = r.get(d)
        if v is None:
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            out_of_range.append((i, r.get('author'), r.get('title_cn'), d, v, '非数值'))
            continue
        vals_all.append(f)
        if f < 0 or f > 10:
            out_of_range.append((i, r.get('author'), r.get('title_cn'), d, v, '超出0-10'))
print('\n=== 量程核查（页面标注 0-10 分）===')
print('取值范围: min=%s max=%s' % (min(vals_all), max(vals_all)))
print('超出 0-10 的记录数:', len(out_of_range))
for row in out_of_range[:30]:
    print('  ', row)

# 与主语料比对
with open(ROOT / 'data' / 'poetry_with_detailed_clusters_sankey.csv', encoding='utf-8-sig') as f:
    corpus = list(csv.DictReader(f))
corpus_keys = {(r['作者'].strip(), r['诗歌名'].strip()) for r in corpus}
corpus_titles = {r['诗歌名'].strip() for r in corpus}

emo_keys = [(r.get('author', '').strip(), r.get('title_cn', '').strip()) for r in arr]
emo_set = set(emo_keys)

print('\n=== 与主语料(100条)比对 ===')
print('情感页记录数:', len(emo_keys), ' 去重后:', len(emo_set))
dup = [k for k, c in Counter(emo_keys).items() if c > 1]
print('情感页内部重复:', dup)

extra = emo_set - corpus_keys
missing = corpus_keys - emo_set
print('\n情感页有、主语料没有的 (作者,标题):', len(extra))
for k in sorted(extra):
    # 标题在但作者不同?
    note = '标题在语料中但作者不同' if k[1] in corpus_titles else '标题完全不在语料中'
    print('  ', k, '--', note)
print('\n主语料有、情感页没有的:', len(missing))
for k in sorted(missing):
    print('  ', k)

# 作者分布
print('\n情感页作者数:', len({a for a, _ in emo_set}))
print('主语料作者数:', len({r['作者'].strip() for r in corpus}))
