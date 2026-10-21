# -*- coding: utf-8 -*-
"""轻重层专项·三库力度描述扫描（只读，词表冻结 v1.0）

口径：
  - 语料：协纪 C:\\Temp\\xj_full（279216-279254）｜考原 C:\\Temp\\xl_full（359075-359081）
          ｜陈书 C:\\Temp\\czx_full\\czx_pages.json
  - 全卷扫、无抽样；按句切分（。！？；换行），命中句 + 前后各 1 句留档
  - 力度标记：其力/轻微/最重/甚于/次于/大煞/小煞/大忌/尤忌/犹忌/止忌/
              上吉/次吉/中吉/大吉/小疵/屡用/无害/不可用/切忌/百事 等
输出：weight_scan.json（每项命中句全集）＋控制台力度句摘要。
用法：python scan_weight.py
退出码：0=正常 1=异常
"""
import hashlib
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')

XJ = r'C:\Temp\xj_full'
XL = r'C:\Temp\xl_full'
CZX = r'C:\Temp\czx_full\czx_pages.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'weight_scan.json')

TERMS = {
    '土府': ['土府'],
    '土王用事': ['土王用事', '土王'],
    '地囊': ['地囊'],
    '三煞': ['三煞', '三殺'],
    '月破': ['月破'],
    '月厌': ['月厌', '月厭'],
    '月刑': ['月刑'],
    '月害': ['月害'],
    '劫煞': ['劫煞'],
    '灾煞': ['灾煞', '災煞'],
    '岁煞': ['岁煞', '歲煞'],
    '月煞': ['月煞'],
    '大时': ['大时', '大時'],
    '天吏': ['天吏', '致死'],
    '归忌': ['归忌', '歸忌'],
    '往亡': ['往亡'],
    '四废': ['四废', '四廢'],
    '五墓': ['五墓'],
    '八专': ['八专', '八專'],
    '四击': ['四击', '四擊'],
    '四忌': ['四忌'],
    '月德合': ['月德合'],
    '反支': ['反支'],
    '飞廉': ['飞廉', '飛廉'],
    '伏断': ['伏断', '伏斷'],
    '不将': ['不将', '不將'],
    '天恩': ['天恩'],
    '受死日': ['受死'],
    '红嘴朱雀': ['红嘴朱雀', '紅嘴朱雀'],
    '鸣吠日': ['鸣吠', '鳴吠'],
    '鸣吠对': ['鸣吠对', '鳴吠對'],
}

MARKERS = ['其力', '轻微', '最重', '最凶', '尤重', '尤毒', '甚于', '次于',
           '重于', '轻于', '大煞', '小煞', '大凶', '小凶', '大忌', '小忌',
           '尤忌', '犹忌', '止忌', '皆忌', '不忌', '不得与', '可比',
           '上吉', '次吉', '中吉', '大吉', '小疵', '屡用', '无害',
           '不可用', '切忌', '不宜', '百事', '诸事']

SPLIT = re.compile(r'[。！？；\n]')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load():
    corp = []
    for n in range(279216, 279255):
        p = os.path.join(XJ, '%d.txt' % n)
        corp.append(('协纪', str(n), open(p, encoding='utf-8',
                                           errors='replace').read(), sha(p)))
    for n in range(359075, 359082):
        p = os.path.join(XL, '%d.txt' % n)
        corp.append(('考原', str(n), open(p, encoding='utf-8',
                                          errors='replace').read(), sha(p)))
    pages = json.load(open(CZX, encoding='utf-8'))
    for pg, txt in pages:
        corp.append(('陈书', 'p%d' % pg, txt or '', ''))
    return corp


def sentences(txt):
    out = []
    for s in SPLIT.split(txt):
        s = s.strip().replace('　', '')
        if s:
            out.append(s)
    return out


def main():
    corp = load()
    res = {'manifest': [], 'terms': {}, 'markers': MARKERS}
    for book, chap, txt, h in corp:
        res['manifest'].append({'book': book, 'chap': chap,
                                'chars': len(txt), 'sha256': h})

    for name, variants in TERMS.items():
        hits = []
        for book, chap, txt, _ in corp:
            ss = sentences(txt)
            seen_idx = set()
            low = txt
            for v in variants:
                start = 0
                while True:
                    i = low.find(v, start)
                    if i < 0:
                        break
                    start = i + len(v)
                    # 定位句号：按累计长度找所在句
                    acc = 0
                    idx = None
                    for k, s in enumerate(ss):
                        if acc <= i < acc + len(s) + 1:
                            idx = k
                            break
                        acc += len(s) + 1
                    if idx is None or idx in seen_idx:
                        continue
                    seen_idx.add(idx)
                    own = ss[idx]
                    ctx = '。'.join(ss[max(0, idx - 1): idx + 2])
                    marks = [m for m in MARKERS if m in ctx]
                    hits.append({'book': book, 'chap': chap, 'term': v,
                                 'sentence': own[:300], 'ctx': ctx[:600],
                                 'markers': marks})
            # 同一章内按句去重
        # dedupe by (book,chap,sentence)
        uniq = {}
        for h in hits:
            uniq[(h['book'], h['chap'], h['sentence'])] = h
        hits = list(uniq.values())
        by = {}
        for h in hits:
            by[h['book']] = by.get(h['book'], 0) + 1
        marked = [h for h in hits if h['markers']]
        res['terms'][name] = {
            'total': len(hits),
            'by_book': by,
            'marked_total': len(marked),
            'hits': hits,
        }

    json.dump(res, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('=' * 100)
    print('[A] 命中总数 / 力度句数')
    print('=' * 100)
    for name, v in res['terms'].items():
        print(f"{name:<10}命中={v['total']:<5}力度句={v['marked_total']:<5}"
              f"{v['by_book']}")
    print('\n' + '=' * 100)
    print('[B] 力度句摘要（每项最多 12 条，去重）')
    print('=' * 100)
    for name, v in res['terms'].items():
        ms = [h for h in v['hits'] if h['markers']]
        print('\n### ' + name + f'  ({len(ms)} 条力度句)')
        shown = set()
        for h in ms:
            s = h['ctx']
            key = s[:80]
            if key in shown:
                continue
            shown.add(key)
            print(f"  [{h['book']} {h['chap']}] {s}")
            if len(shown) >= 12:
                break
    print('\n->', OUT)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print('FAIL:', repr(e))
        sys.exit(1)
