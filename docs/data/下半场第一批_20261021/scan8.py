# -*- coding: utf-8 -*-
"""第一批 8 项三库穷尽扫描（只读，词表冻结 v1.0）
语料：协纪 C:\\Temp\\xj_full\\279216-279254 ｜ 考原 C:\\Temp\\xl_full\\359075-359081 ｜ 陈书 C:\\Temp\\czx_full\\czx_pages.json
方法：全卷扫、无抽样；每命中取 ±140 字上下文；输出 JSON 供逐条核读。
"""
import json, os, io, sys, hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

XJ = r'C:\Temp\xj_full'
XL = r'C:\Temp\xl_full'
CZX = r'C:\Temp\czx_full\czx_pages.json'
OUT = r'C:\Temp\scan8.json'

# 词表冻结 v1.0：正名 + 繁体/异体变体
TERMS = {
    '天恩': ['天恩'],
    '不将': ['不将', '不將'],
    '飞廉': ['飞廉', '飛廉'],
    '伏断': ['伏断', '伏斷'],
    '反支': ['反支'],
    '月德合': ['月德合'],
    '归忌': ['归忌', '歸忌'],
    '天吏': ['天吏', '致死'],
}
WIN = 140


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load():
    corp = []
    for n in range(279216, 279255):
        p = os.path.join(XJ, '%d.txt' % n)
        corp.append(('协纪', str(n), open(p, encoding='utf-8', errors='replace').read(), sha(p)))
    for n in range(359075, 359082):
        p = os.path.join(XL, '%d.txt' % n)
        corp.append(('考原', str(n), open(p, encoding='utf-8', errors='replace').read(), sha(p)))
    pages = json.load(open(CZX, encoding='utf-8'))
    for pg, txt in pages:
        corp.append(('陈书', 'p%d' % pg, txt or '', ''))
    return corp


def main():
    corp = load()
    res = {'manifest': [], 'totals': {}, 'hits': {}}
    for book, chap, txt, h in corp:
        res['manifest'].append({'book': book, 'chap': chap, 'chars': len(txt), 'sha256': h})
    for name, variants in TERMS.items():
        hits = []
        for book, chap, txt, _ in corp:
            for v in variants:
                start = 0
                while True:
                    i = txt.find(v, start)
                    if i < 0:
                        break
                    hits.append({'book': book, 'chap': chap, 'term': v,
                                 'ctx': txt[max(0, i - WIN): i + len(v) + WIN].replace('\n', ' ')})
                    start = i + len(v)
        res['hits'][name] = hits
        by = {}
        for hh in hits:
            by[hh['book']] = by.get(hh['book'], 0) + 1
        res['totals'][name] = {'total': len(hits), 'by_book': by,
                               'chaps': sorted({hh['chap'] for hh in hits})}
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in res['totals'].items():
        print(k, v['total'], v['by_book'])
        print('   ', v['chaps'])
    print('->', OUT)


if __name__ == '__main__':
    main()
