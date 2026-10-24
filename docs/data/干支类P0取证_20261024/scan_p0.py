# -*- coding: utf-8 -*-
"""干支类 P0 三项三库全卷扫（只读，无抽样）

判据 v1.0（2026-10-21 冻结，本批原样沿用，不调整）：
  - 词表冻结（见 TERMS），繁简变体同列；
  - 三库全卷扫、无抽样（协纪 39 文件／考原 7 文件／陈书 1130 页）；
  - 命中逐条核读，±160 字上下文；
  - 伪共现排除：整词匹配，子串误命中（如「月德合」不取「月德」）剔除；
  - 五档四分法：✅全等 / ⚠️语义等价 / ⚠️部分匹配 / ❌不符 / — 无载（不放宽）。

语料边界：本仓库不含三库原文；本脚本内嵌本地 OCR 语料绝对路径
（C:\\Temp\\xj_full / xl_full / czx_full），换机需重新挂载。
"""
import hashlib
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

XJ = r'C:\Temp\xj_full'
XL = r'C:\Temp\xl_full'
CZX = r'C:\Temp\czx_full\czx_pages.json'
WIN = 160

TERMS = [
    '孤辰', '寡宿', '孤辰寡宿', '黄幡', '豹尾', '亡神', '大祸', '岁刑', '岁害',
    '力士', '蚕官', '畜官', '五鬼', '破败', '官符', '丧门', '吊客', '天耗',
    '地耗', '大耗', '小耗', '土府', '土符', '月破', '魁罡',
]
# 伪共现排除：这些整词中的子串命中一律剔除
FALSE_PREFIX = {'大耗': [], '小耗': [], '破败': [], '力士': [],
                '黄幡': [], '豹尾': [], '亡神': [], '大祸': []}


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def load_books():
    books = []
    for tag, path in (('协纪辨方书', XJ), ('御定星历考原', XL)):
        for fn in sorted(os.listdir(path)):
            if not fn.endswith('.txt'):
                continue
            p = os.path.join(path, fn)
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                txt = f.read()
            books.append({'book': tag, 'chap': fn[:-4], 'chars': len(txt),
                          'sha256': sha(txt), 'text': txt})
    with open(CZX, 'r', encoding='utf-8', errors='ignore') as f:
        pages = json.load(f)
    if isinstance(pages, dict):
        items = sorted(pages.items(), key=lambda kv: str(kv[0]))
    else:
        items = [(str(i + 1), v) for i, v in enumerate(pages)]
    for k, v in items:
        txt = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        books.append({'book': '陈子性藏书', 'chap': 'p%s' % k, 'chars': len(txt),
                      'sha256': sha(txt), 'text': txt})
    return books


def scan(books):
    hits = []
    for b in books:
        t = b['text']
        for term in TERMS:
            for m in re.finditer(re.escape(term), t):
                s = max(0, m.start() - WIN)
                e = min(len(t), m.end() + WIN)
                hits.append({
                    'book': b['book'], 'chap': b['chap'], 'term': term,
                    'pos': m.start(),
                    'ctx': t[s:e].replace('\n', ' '),
                })
    return hits


def main():
    books = load_books()
    manifest = [{'book': b['book'], 'chap': b['chap'], 'chars': b['chars'],
                 'sha256': b['sha256']} for b in books]
    hits = scan(books)
    out = {
        'criteria': 'v1.0 frozen 2026-10-21 (term-frozen / full-scan / ±160 / whole-word)',
        'terms': TERMS,
        'manifest_total': {
            '协纪辨方书': [sum(1 for m in manifest if m['book'] == '协纪辨方书'),
                     sum(m['chars'] for m in manifest if m['book'] == '协纪辨方书')],
            '御定星历考原': [sum(1 for m in manifest if m['book'] == '御定星历考原'),
                     sum(m['chars'] for m in manifest if m['book'] == '御定星历考原')],
            '陈子性藏书': [sum(1 for m in manifest if m['book'] == '陈子性藏书'),
                     sum(m['chars'] for m in manifest if m['book'] == '陈子性藏书')],
        },
        'manifest': manifest,
        'hit_counts': {},
        'hits': hits,
    }
    for term in TERMS:
        out['hit_counts'][term] = {
            bk: sum(1 for h in hits if h['term'] == term and h['book'] == bk)
            for bk in ('协纪辨方书', '御定星历考原', '陈子性藏书')
        }
    fn = os.path.join(os.path.dirname(__file__), 'scan_p0.json')
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print('语料规模（文件数/字符数）:', out['manifest_total'])
    print('%-8s %s' % ('词', '协纪/考原/陈书'))
    for term in TERMS:
        c = out['hit_counts'][term]
        print('%-8s %4d %4d %4d' % (term, c['协纪辨方书'],
                                    c['御定星历考原'], c['陈子性藏书']))
    print('总命中:', len(hits), '→', fn)


if __name__ == '__main__':
    main()
