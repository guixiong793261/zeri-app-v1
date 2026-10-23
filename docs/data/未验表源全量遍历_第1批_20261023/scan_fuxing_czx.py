# -*- coding: utf-8 -*-
"""陈书轨·福星条目核读扫描（001 §164 归档完整性补充）
扫描 C:\\Temp\\czx_full\\part_*.json，定位「福星」全部命中，留档前后各 80 字上下文。
基线调和（001 §164）：三库取证批 Grep count=16 为【行】计口径；本扫描按【出现次】
计为 17——差 1 处＝目录句「附錄福星訣啓人篇」在 part_00/part_0000 两分片重复收录
（同一底本两次数字化）。17 处已逐条核读定案（见 czx_fuxing_hits.json）：
part_0113×6（福星贵人起例詩訣＝淮南子派，与协纪卷七逐字同）、part_0226×3
（附錄福星訣全文同派互证）、part_00/0000 目录×2、part_0565/0678 宜忌列×3、
part_0452×1（「生福星」五行生克语境，伪共现排除）。
命中数 != 17 → 退出码 1。
输出：本目录 czx_fuxing_hits.json（含页码与上下文，证据链归档）。
"""
import os
import re
import sys
import glob
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_GLOB = r"C:\Temp\czx_full\part_*.json"
OUT = os.path.join(HERE, "czx_fuxing_hits.json")
BASELINE = 17

hits = []
files = sorted(glob.glob(SRC_GLOB))
if not files:
    print("[FAIL] 未找到分片：%s" % SRC_GLOB)
    sys.exit(1)

for fp in files:
    with open(fp, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    page = None
    m_page = None
    for m in re.finditer(r"福星", text):
        # 就近向前找最近的 "page": N
        head = text[: m.start()]
        m_page = re.findall(r'"page"\s*:\s*(\d+)', head)
        page = int(m_page[-1]) if m_page else None
        ctx = text[max(0, m.start() - 80): m.end() + 80]
        hits.append({"file": os.path.basename(fp), "page": page,
                     "pos": m.start(), "context": ctx})

print("[INFO] 分片数=%d 命中数=%d（基线 %d）" % (len(files), len(hits), BASELINE))
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"baseline": BASELINE, "total": len(hits), "hits": hits},
              f, ensure_ascii=False, indent=1)
print("[OK] 已写出", OUT)

if len(hits) != BASELINE:
    print("[FAIL] 命中数 %d != 基线 %d，须人工核读" % (len(hits), BASELINE))
    sys.exit(1)
print("ALL GREEN：陈书福星条目 %d 处已留档（页码+上下文）" % len(hits))
sys.exit(0)
