#!/usr/bin/env python3
"""抽取 HTML 内嵌数据为 data/ 下的权威 CSV。

- data/emotion_scores.csv  ：来自 word-association.html，剔除 3 条语料外记录，
  修正 8 个超出 0-10 量程的评分（多余前导 "1" 录入错误），并输出变更日志。
- data/word_frequency.csv  ：来自 词频可视化.html（283 词全量版），词语字段去空白。
"""
import re, json, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIMS = ['壮怀逸兴', '孤愤悲慨', '死生超然', '同袍之谊', '家国义愤', '功名热望', '功名幻灭', '苍茫孤寂']
EXCLUDED = {('卢照邻', '刘生'), ('卢照邻', '结客少年场行'), ('虞羽客', '结客少年场行')}


def extract_js_array(path, varname):
    html = path.read_text(encoding='utf-8')
    raw = re.search(varname + r'\s*=\s*(\[.*?\]);', html, re.S).group(1)
    raw = re.sub(r'//[^\n]*', '', raw)
    return json.loads(re.sub(r',\s*([}\]])', r'\1', raw))


def main():
    changelog = []

    # ---- 情感评分 ----
    emo = extract_js_array(ROOT / 'word-association.html', 'var data')
    rows, seen = [], set()
    for r in emo:
        key = (r['author'].strip(), r['title_cn'].strip())
        if key in EXCLUDED:
            changelog.append(f"删除语料外记录: {key[0]}《{key[1]}》")
            continue
        if key in seen:
            changelog.append(f"删除重复记录: {key[0]}《{key[1]}》")
            continue
        seen.add(key)
        row = {'author': key[0], 'title_cn': key[1]}
        for d in DIMS:
            v = int(r[d])
            if v > 10:
                fixed = v % 10
                changelog.append(f"量程修正: {key[0]}《{key[1]}》 {d} {v} -> {fixed}（多余前导 1）")
                v = fixed
            row[d] = v
        rows.append(row)
    with open(ROOT / 'data' / 'emotion_scores.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['author', 'title_cn'] + DIMS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(f'emotion_scores.csv: {len(rows)} 条')

    # ---- 词频 ----
    wf = extract_js_array(ROOT / '词频可视化.html', 'const data')
    wrows = [{'词语': r['词语'].strip(), '词频': int(r['词频']), '分类': r['分类'].strip()} for r in wf]
    wrows.sort(key=lambda r: -r['词频'])
    with open(ROOT / 'data' / 'word_frequency.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['词语', '词频', '分类'], lineterminator='\n')
        w.writeheader()
        w.writerows(wrows)
    print(f'word_frequency.csv: {len(wrows)} 条')

    log_path = ROOT / 'docs' / 'data-changelog-2026-08-16.md'
    log_path.write_text('# 数据抽取与修正日志（2026-08-16）\n\n' +
                        '\n'.join(f'- {c}' for c in changelog) + '\n', encoding='utf-8')
    print(f'变更日志: {len(changelog)} 条 -> {log_path.name}')


if __name__ == '__main__':
    main()
