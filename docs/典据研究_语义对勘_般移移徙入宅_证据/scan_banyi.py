# -*- coding: utf-8 -*-
"""
w7 语义对勘——般移/移徙/入宅三词三库穷尽扫描（词表冻结 v1.0，全卷扫，无抽样）
语料：协纪 C:\\Temp\\xj_full\\279216-279254（36卷+前料，39 文件）
      考原 C:\\Temp\\xl_full\\359075-359081（提要+卷一~六，7 文件）
      陈书 C:\\Temp\\czx_full\\czx_pages.json（1130页）
输出：scan_results.json（hits 全量+全文计数）＋ manifest 段（语料 SHA256）
确定性：无随机、无抽样，同一语料复跑结果逐字节一致。
"""
import json, os, re, hashlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

XJ = r'C:\Temp\xj_full'
XL = r'C:\Temp\xl_full'
CZX = r'C:\Temp\czx_full\czx_pages.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scan_results.json')

# ---- 词表冻结 v1.0（沿用 d6 (b)轨词表同族变体，新增 般移/搬移 两变体） ----
TERMS = {
    '般移': ['般移'],
    '搬移': ['搬移'],
    '移徙': ['移徙'],
    '迁徙': ['迁徙', '遷徙'],
    '入宅': ['入宅', '歸宅', '归宅'],
    '归火': ['归火', '歸火', '入火'],
    '复合': ['移徙入宅', '入宅移居', '移徙安床', '移徙入宅安床'],
}
WIN = 120  # 上下文窗口（±字符）


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load_corpora():
    corp = []
    counts = json.load(open(os.path.join(XJ, 'counts.json'), encoding='utf-8'))
    for n in range(279216, 279255):
        p = os.path.join(XJ, '%d.txt' % n)
        txt = open(p, encoding='utf-8').read()
        corp.append({'book': '协纪辨方书', 'chap': str(n), 'juan': counts[str(n)]['juan'],
                     'text': txt, 'path': p})
    for n in range(359075, 359082):
        p = os.path.join(XL, '%d.txt' % n)
        txt = open(p, encoding='utf-8').read()
        first = txt.split('\n', 1)[0]
        m = re.search(r'卷([一二三四五六])', first)
        corp.append({'book': '御定星历考原', 'chap': str(n),
                     'juan': ('卷' + m.group(1)) if m else '提要', 'text': txt, 'path': p})
    pages = json.load(open(CZX, encoding='utf-8'))
    for pg, txt in pages:
        corp.append({'book': '陈子性藏书', 'chap': 'p%s' % pg, 'juan': '',
                     'text': txt or '', 'path': CZX})
    return corp


def main():
    corp = load_corpora()
    manifest, totals, hits = [], {}, []
    for c in corp:
        book, txt = c['book'], c['text']
        manifest.append({'book': book, 'chap': c['chap'], 'juan': c['juan'],
                         'sha256': sha(c['path']) if c['path'].endswith('.txt') else None,
                         'chars': len(txt)})
        for canon, variants in TERMS.items():
            for w in variants:
                n = txt.count(w)
                if n:
                    totals.setdefault(book, {}).setdefault(canon, 0)
                    totals[book][canon] += n
                start = 0
                for _ in range(n):
                    idx = txt.index(w, start)
                    a, b = max(0, idx - WIN), min(len(txt), idx + len(w) + WIN)
                    hits.append({
                        'book': book, 'chap': c['chap'], 'juan': c['juan'],
                        'canon': canon, 'word': w,
                        'pos': idx, 'line': txt.count('\n', 0, idx) + 1,
                        'ctx': txt[a:b].replace('\n', '⏎'),
                    })
                    start = idx + 1
    out = {'manifest': manifest, 'totals': totals, 'hits': hits}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    n_books = {}
    for h in hits:
        key = (h['book'], h['canon'])
        n_books[key] = n_books.get(key, 0) + 1
    print('全文计数（canon 级）:')
    for book, d in totals.items():
        print(' ', book, d)
    print('命中明细（canon 级条数）:')
    for (book, canon), n in sorted(n_books.items()):
        print(f'  {book} / {canon}: {n}')
    print(f'总命中: {len(hits)} -> {OUT}')


if __name__ == '__main__':
    main()
