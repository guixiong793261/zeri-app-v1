# -*- coding: utf-8 -*-
"""
verify_e5_jiqing.py —— 批1 E5「吉庆」删除完备性 verify（001 §70）

典据（唯一权威源，逐字摘录）：
  《钦定协纪辨方书》卷三十六·辨讹「满德吉庆」条：
    「选择宗镜以满德吉庆为伪吉日信知言也今具立成於左观名例自见毋庸深辨」
  ——满德、吉庆两神并列钦定判伪，协纪赞同《选择宗镜》并删弃不用。
  原文坐标：C:\\Temp\\xj_full\\279254.txt L158-159（卷三十六辨讹）。

裁剪声明（删除形态，非对齐形态）：
  步骤4 黄金矩阵不适用（无新表）→ 降级为「删除完备性断言」：
  扫描范围内代码行（非注释）零 _is_jiqing / 零 '吉庆' 神煞名残留，
  事项标准动态导入后零 ('X','吉庆') 注册键。
  旧墓碑注释（# 2026-10 批1（001 §70）…）为有意保留的防再犯标记。

退出码：0=PASS  1=FAIL（CI 可挂）
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_ROOTS = [
    ROOT / 'modules',
    ROOT / '手机一键部署' / '模块完整版' / 'modules',
]

# 代码形态（注释行跳过）：调用面 / 发射面 / 注册面
PAT_CALL = re.compile(r'self\._is_jiqing\b')
PAT_EMIT = re.compile(r"_add_shensha\(\s*['\"]吉庆['\"]")
PAT_REG = re.compile(r"\(\s*['\"][^'\"]+['\"]\s*,\s*['\"]吉庆['\"]\s*\)\s*:")
TOMBSTONE = '批1（001 §70）'


def scan_py(root):
    problems = []
    if not root.exists():
        return problems, 0
    n = 0
    for p in sorted(root.rglob('*.py')):
        if '__pycache__' in p.parts:
            continue
        n += 1
        try:
            lines = p.read_text(encoding='utf-8').splitlines()
        except UnicodeDecodeError:
            problems.append('%s: 非UTF-8' % p)
            continue
        for i, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith('#'):
                continue
            if PAT_CALL.search(line) or PAT_EMIT.search(line) or PAT_REG.search(line):
                problems.append('%s:%d 残留吉庆代码: %s' % (p, i, s[:80]))
    return problems, n


def main():
    print('=' * 72)
    print('verify_e5_jiqing 批1 删除完备性（典据：协纪卷三十六·辨讹 满德吉庆条）')
    print('=' * 72)
    fails = []

    # 1) 静态扫描：代码行零残留
    total = 0
    for root in SCAN_ROOTS:
        problems, n = scan_py(root)
        total += n
        tag = str(root.relative_to(ROOT)) if root.is_relative_to(ROOT) else str(root)
        if problems:
            fails.extend(problems)
            print('❌ 扫描 %s（%d 文件）：%d 处残留' % (tag, n, len(problems)))
        else:
            print('✅ 扫描 %s（%d 文件）代码行零残留' % (tag, n))

    # 2) 动态导入：事项标准零 ('X','吉庆') 键
    sys.path.insert(0, str(ROOT))
    from modules import 事项标准 as std
    bad = []
    for name, val in vars(std).items():
        if isinstance(val, dict):
            for k in val:
                if isinstance(k, tuple) and len(k) == 2 and k[1] == '吉庆':
                    bad.append('%s%s' % (name, k))
    if bad:
        fails.append('事项标准残留注册: %s' % bad)
        print('❌ 事项标准动态检查：%d 处残留 %s' % (len(bad), bad))
    else:
        print('✅ 事项标准动态导入：零 (X,吉庆) 注册键')

    # 3) 墓碑标记存在（防再犯注释）
    base = (ROOT / 'modules' / 'shensha' / '神煞基类.py').read_text(encoding='utf-8')
    cnt = base.count(TOMBSTONE)
    if cnt < 2:
        fails.append('神煞基类墓碑标记不足（%d/2）' % cnt)
        print('❌ 墓碑标记 %d/2' % cnt)
    else:
        print('✅ 神煞基类墓碑标记 %d/2（发射点+谓词）' % cnt)

    # 4) 旧谓词值反断言：吉庆旧表（月支→日干）不得以任何代码形态复活
    old_table_snippets = ["'寅': '戊', '卯': '己'"]
    for snip in old_table_snippets:
        for root in SCAN_ROOTS:
            if not root.exists():
                continue
            for p in root.rglob('*.py'):
                if '__pycache__' in p.parts:
                    continue
                txt = p.read_text(encoding='utf-8')
                for i, line in enumerate(txt.splitlines(), 1):
                    if snip in line and not line.strip().startswith('#'):
                        fails.append('%s:%d 疑似吉庆旧表复活: %s' % (p, i, line.strip()[:60]))

    print('-' * 72)
    if fails:
        print('FAIL %d' % len(fails))
        for f in fails:
            print('  ✗ %s' % f)
        return 1
    print('PASS（扫描 %d 个 .py，完备性/注册/墓碑/旧表反断言全过）' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
