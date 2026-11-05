# -*- coding: utf-8 -*-
"""
verify_d1_zhisi 批2 删除完备性（典据：协纪卷六/卷十天吏【致死】条）

批2（001 §71）：'致死日' 全删——
  《协纪》卷六月神表「天吏【致死】」、卷十用日篇按语「天吏者三合之死气也
  故又为致死」「天吏又名致死为三合死地」；《考原》359079 L143 独立致死条
  但《历例》「正月起酉逆行四仲」、曹震圭「与天吏同」——三库互校致死≡天吏
  同位异名。安葬原 _is_zhisi「正未二申…十二午」（正月起未顺行十二辰）表
  三库均无载（陈书第三参照「即三合死位…故又名致死」同位佐证；陈书安葬表
  列致死为忌与协纪忌项无安葬系分歧，按层级规则以协纪为主锚，仅标注）。
  谓词 + 发射块 + ('安葬','致死日') 注册删除；A7 悬空 ('安葬','天吏日')
  条目同批收口。基类 '天吏' -15（A7 修复后典载口径）保持不动。

检查项：
1. 两层 modules（根/手机一键部署\模块完整版）代码行零残留；
2. 动态导入事项标准：零 ('安葬','致死日')/('安葬','天吏日') 注册键，
   ('安葬','天吏') 正当条目仍在（防误删）；
3. 安葬神煞.py 墓碑 '批2（001 §71）' ≥2（发射点+谓词）；
4. 旧表复活反断言（zhisi_map 特征 '寅': '未', '卯': '申' 非注释行）。

退出码：0=PASS，1=FAIL。
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    ROOT / 'modules',
    ROOT / '手机一键部署' / '模块完整版' / 'modules',
]
TARGET = ROOT / 'modules' / 'shensha' / '安葬神煞.py'

PAT_CALL = re.compile(r'self\._is_zhisi\b')
PAT_EMIT = re.compile(r"_add_shensha\(\s*['\"]致死日['\"]")
PAT_REG = re.compile(r"\(\s*['\"]安葬['\"]\s*,\s*['\"](?:致死日|天吏日)['\"]\s*\)\s*:")
TOMBSTONE = '批2（001 §71）'
REVIVAL = re.compile(r"^\s*zhisi_map\s*=\s*\{|'寅': '未', '卯': '申'")


def is_code(line):
    s = line.strip()
    return bool(s) and not s.startswith('#')


def main():
    failed = []
    print('=' * 72)
    print('verify_d1_zhisi 批2 删除完备性（致死≡天吏同位异名，三库互校）')
    print('=' * 72)

    # 1. 三层扫描零残留
    for root in SCAN_ROOTS:
        if not root.exists():
            failed.append('扫描根不存在：%s' % root)
            continue
        hits = 0
        files = 0
        for py in root.rglob('*.py'):
            files += 1
            try:
                text = py.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                text = py.read_text(encoding='gbk', errors='ignore')
            for i, line in enumerate(text.splitlines(), 1):
                if is_code(line) and (PAT_CALL.search(line) or PAT_EMIT.search(line)
                                      or PAT_REG.search(line)):
                    hits += 1
                    failed.append('残留 %s:%d %s' % (py.relative_to(ROOT), i,
                                                    line.strip()[:60]))
        print('✅' if hits == 0 else '❌', '扫描 %s（%d 文件）代码行零残留'
              % (root.relative_to(ROOT), files))

    # 2. 动态导入事项标准
    sys.path.insert(0, str(ROOT))
    try:
        import importlib
        mod = importlib.import_module('modules.事项标准')
        scores = getattr(mod, 'SHENSHA_SCORES', None) or getattr(mod, 'SCORES', None)
        if scores is None:
            failed.append('事项标准无分值表（SHENSHA_SCORES/SCORES）')
            print('❌ 动态导入事项标准：找不到分值表')
        else:
            bad_keys = [k for k in scores
                        if k[0] == '安葬' and k[1] in ('致死日', '天吏日')]
            # 口径收口批（2026-10-21，001 §153）：('安葬','天吏') 已随天吏
            # 超范围清理删除（卷十忌列无破土/安葬，取证稿 §1.8 判 ❌）；
            # 原「防误删」断言反转为删除断言。
            gone = ('安葬', '天吏') not in scores
            if bad_keys:
                failed.append('事项标准残留注册：%s' % bad_keys)
            if not gone:
                failed.append("('安葬','天吏') 应已删（口径收口批 001 §153，"
                              "取证稿 §1.8 判 ❌）")
            print('✅' if not bad_keys and gone else '❌',
                  '动态导入事项标准：零 (安葬,致死日/天吏日) 键，(安葬,天吏) 已删'
                  '（口径收口批 001 §153）')
    except Exception as e:  # noqa: BLE001
        failed.append('动态导入失败：%r' % e)
        print('❌ 动态导入事项标准异常：%r' % e)

    # 3. 墓碑
    text = TARGET.read_text(encoding='utf-8')
    n_tomb = text.count(TOMBSTONE)
    if n_tomb < 2:
        failed.append('墓碑不足 2（实际 %d）' % n_tomb)
    print('✅' if n_tomb >= 2 else '❌', '安葬神煞墓碑标记 %d/2（发射点+谓词）' % n_tomb)

    # 4. 旧表复活反断言
    rev = [i for i, line in enumerate(text.splitlines(), 1)
           if REVIVAL.search(line) and is_code(line)]
    if rev:
        failed.append('旧 zhisi 表复活：%s' % rev)
    print('✅' if not rev else '❌', '旧表复活反断言（正未二申 zhisi_map 非注释行）')

    print('-' * 72)
    if failed:
        print('FAIL %d' % len(failed))
        for x in failed:
            print('  -', x)
        sys.exit(1)
    print('PASS（墓碑/注册/旧表反断言全过）')
    sys.exit(0)


if __name__ == '__main__':
    main()
