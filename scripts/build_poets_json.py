#!/usr/bin/env python3
"""生成 data/poets.json：五位高频诗人的档案、诗作、系年与双轨得分。"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / 'data'

XIA = ['壮怀逸兴', '同袍之谊', '家国义愤', '死生超然']
SHI = ['功名热望', '功名幻灭', '孤愤悲慨', '苍茫孤寂']

# 每位诗人的策展信息（人名章、场景、一句定场诗）
CURATED = {
    '骆宾王': dict(order=1, epithet='初唐孤愤', scene='帝京阙下',
                   signature='不学燕丹客，空歌易水寒',
                   signature_from='送郑少府入辽共赋侠客远从戎',
                   note='初唐最早举起侠义之笔的人。讨武檄文名动天下，下落成谜——他的一生比诗更像侠客。'),
    '王维': dict(order=2, epithet='少年意气', scene='终南山色',
                 signature='孰知不向边庭苦，纵死犹闻侠骨香',
                 signature_from='杂曲歌辞 少年行四首 三',
                 note='写尽少年游侠的意气，自己走向山水田园。侠气是他回望青春的方式。'),
    '李白': dict(order=3, epithet='最侠客', scene='江湖舟楫',
                 signature='十步杀一人，千里不留行',
                 signature_from='杂曲歌辞 侠客行',
                 note='十五好剑术，遍干诸侯。语料中侠客气质最盛的诗人——他几乎把自己活成了诗里的侠客。'),
    '高适': dict(order=4, epithet='边塞仕途', scene='塞外孤城',
                 signature='未知肝胆向谁是，令人却忆平原君',
                 signature_from='杂曲歌辞 邯郸少年行',
                 note='写边塞最雄浑的人，情感结构却最"诗人"。他的边塞不是江湖，是仕途。'),
    '杜甫': dict(order=5, epithet='乱世孤愤', scene='乱世烽烟',
                 signature='渔阳豪侠地，击鼓吹笙竽',
                 signature_from='横吹曲辞 后出塞五首 四',
                 note='亲历安史之乱后，侠在他笔下从少年意气变成了乱世疮痍。侠气至此，归于沉郁。'),
}

def main():
    sankey = [r for r in csv.DictReader(open(D / 'poetry_with_detailed_clusters_sankey.csv', encoding='utf-8-sig'))]
    dates = {(r['author'], r['title_original']): r for r in csv.DictReader(open(D / 'poem_dates.csv', encoding='utf-8-sig'))}
    periods = {r['author']: r for r in csv.DictReader(open(D / 'author_activity_periods.csv', encoding='utf-8-sig'))}
    emo = {(r['author'], r['title_cn']): r for r in csv.DictReader(open(D / 'emotion_scores.csv', encoding='utf-8-sig'))}

    poets = []
    for name, cur in CURATED.items():
        p = periods.get(name, {})
        # 去重后的诗作
        seen, poems = set(), []
        for r in sankey:
            if r['作者'] != name:
                continue
            key = r['诗歌名']
            if key in seen:
                continue
            seen.add(key)
            d = dates.get((name, key), {})
            status = d.get('timeline_status', '')
            if status.startswith('duplicate'):
                continue  # 重复收录（诗题异文），只保留主记录
            # 情志表诗题不带"杂曲歌辞"等前缀，需剥离后再匹配
            e = emo.get((name, key))
            if not e:
                import re
                stripped = re.sub(r'^\S*(?:歌辞|曲辞|古题序)\s', '', key)
                e = emo.get((name, stripped), {})
            year = d.get('timeline_year', '')
            entry = {
                'title': key,
                'cluster': r['聚类类别'],
                'year': round(float(year)) if year else None,
                'status': ('observed' if status.startswith('observed')
                           else 'inferred' if status.startswith('inferred')
                           else 'unavailable'),
                'date_label': d.get('date_label', ''),
                'text': r['诗歌原文'],
            }
            if e:
                entry['xia'] = round(sum(int(e[dim]) for dim in XIA) / 4, 2)
                entry['shi'] = round(sum(int(e[dim]) for dim in SHI) / 4, 2)
            poems.append(entry)
        poems.sort(key=lambda x: (x['year'] is None, x['year'] or 9999))

        emos = [x for x in poems if 'xia' in x]
        dual = round(sum(x['xia'] for x in emos) / len(emos) - sum(x['shi'] for x in emos) / len(emos), 2) if emos else 0

        poets.append({
            'name': name,
            'order': cur['order'],
            'birth': p.get('birth_year', ''),
            'death': p.get('death_year', ''),
            'activity': [p.get('activity_start', ''), p.get('activity_end', '')],
            'epithet': cur['epithet'],
            'scene': cur['scene'],
            'signature': cur['signature'],
            'signature_from': cur['signature_from'],
            'note': cur['note'],
            'dual': dual,
            'clusters': {c: sum(1 for x in poems if x['cluster'] == c) for c in {x['cluster'] for x in poems}},
            'poems': poems,
        })

    poets.sort(key=lambda x: x['order'])
    out = D / 'poets.json'
    out.write_text(json.dumps({'poets': poets}, ensure_ascii=False, indent=1), encoding='utf-8')
    for p in poets:
        print(p['name'], f"{p['birth']}-{p['death']}", f"双轨 {p['dual']:+.2f}", len(p['poems']), '首', p['clusters'])
    print('->', out)

if __name__ == '__main__':
    main()
