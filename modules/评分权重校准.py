# -*- coding: utf-8 -*-
"""
================================================================================
神煞分值单向生成器（以 modules/事项标准.SHENSHA_SCORES 为唯一事实源）
================================================================================
用途：
    以 modules/事项标准.py 的 SHENSHA_SCORES 单一表为唯一事实源，扫描
    modules/shensha/*.py 源码里的 _add_shensha('名称', 旧默认分, '描述') 调用，
    把"调用处默认分值"同步成表中对应 (事项, 神煞名) 的统一值。

    运行时真正的取值链是：
        神煞基类._add_shensha → shensha_score(_std_event, name, default)
        → 命中 SHENSHA_SCORES 用表值，否则用调用处默认值
    因此本脚本不会改变运行时评分行为，仅让源码默认值与单一事实源一致，
    消除"源码默认值与表值不一致"的隐患，方便阅读与维护。

设计要点：
    1. AST 解析（非正则），只识别真正的 _add_shensha(...) 调用，
       不会误改注释或字符串里的同形文本；
    2. 只处理 args[0] 为字面字符串、args[1] 为字面整数 的调用形式；
       跳过 f-string 动态名、变量名、关键字参数、字典批量等动态形态；
    3. 默认 dry-run，仅打印 diff；加 --apply 才写盘；
    4. 写盘时保留 CRLF / LF / 原始 BOM，记录前后 MD5；
    5. 摘要输出"实际变更数"而非配置值。

用法：
    python modules/评分权重校准.py             # dry-run 预览
    python modules/评分权重校准.py --apply     # 实际写盘
    python modules/评分权重校准.py --dir <path> --apply   # 指定 shensha 目录
================================================================================
"""

import argparse
import ast
import hashlib
import os
import sys

# ==================== 1. 文件 → 规范事项 映射 ====================
# 与 modules/事项标准.py 中 SHENSHA_CHECKER_CLASSES 一致；继承类随父类事项。
# 通用神煞.py 的检查器未被打 _std_event 戳，运行时走 ('*', name) 通配分支，
# 故此处用 '*' 与运行时取数链对齐。
FILE_EVENT_MAP = {
    '嫁娶神煞.py':     '嫁娶',
    '嫁娶神煞扩展.py': '嫁娶',
    '修造神煞.py':     '修造',
    '修造神煞扩展.py': '修造',
    '动土神煞.py':     '动土',
    '拆舍神煞.py':     '拆舍',
    '入宅神煞.py':     '入宅',
    '作灶神煞.py':     '作灶',
    '开业神煞.py':     '开业',
    '出行神煞.py':     '出行',
    '安葬神煞.py':     '安葬',
    '安床神煞.py':     '安床',
    '通用神煞.py':     '*',
}

# 跳过的文件（无 _add_shensha 调用，或是基类/非派发入口）
SKIP_FILES = {
    '__init__.py',
    '神煞基类.py',
    'marriage_shensha.py',   # 已确认无 _add_shensha 调用
}


def list_shensha_files(shensha_dir):
    """返回需要处理的 shensha 文件名（已排序，已过滤）。"""
    result = []
    try:
        names = sorted(os.listdir(shensha_dir))
    except FileNotFoundError:
        return result
    for fn in names:
        if not fn.endswith('.py') or fn.startswith('__'):
            continue
        if fn in SKIP_FILES:
            continue
        if fn not in FILE_EVENT_MAP:
            continue
        result.append(fn)
    return result


def _extract_int_literal(node):
    """从 AST 节点抽取整数字面量及其精确字符范围。

    覆盖两种形式：
        1. ast.Constant(int)         —— 正数字面量（如 10、25），3.8+ 也可能含折叠的负数
        2. ast.UnaryOp(USub, Constant(int))  —— 未折叠的负数字面量（如 -18、-15）

    返回 (value, lineno, col_start, col_end) 或 None。
        lineno     1-based 行号
        col_start  0-based 起始列（含）
        col_end    0-based 结束列（不含）
    """
    # 形式1：直接整数字面量（含 Python 折叠后的负数）
    if isinstance(node, ast.Constant) and isinstance(node.value, int) \
            and not isinstance(node.value, bool):
        if not hasattr(node, 'end_col_offset') or node.end_col_offset is None:
            return None
        return (node.value, node.lineno, node.col_offset, node.end_col_offset)

    # 形式2：一元负号 + 整数字面量（Python AST 对 `-18` 这种写法的标准解析）
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        operand = node.operand
        if isinstance(operand, ast.Constant) and isinstance(operand.value, int) \
                and not isinstance(operand.value, bool):
            # 需要 UnaryOp 自身和 operand 都有列范围
            if (not hasattr(node, 'col_offset') or node.col_offset is None
                    or not hasattr(operand, 'end_col_offset')
                    or operand.end_col_offset is None):
                return None
            # 跨行 UnaryOp 不存在（一行内），统一取 operand 的 lineno
            return (-operand.value, node.lineno,
                    node.col_offset, operand.end_col_offset)
    return None


def find_replacements(source, event, shensha_score_fn):
    """用 AST 找出文件中所有可替换的 _add_shensha 调用。

    替换条件：
        - func.attr == '_add_shensha'
        - args[0] 是字面 str
        - args[1] 是字面 int（含 UnaryOp(USub, Constant) 形式的负数）
        - shensha_score_fn(event, name, old) 命中表中值且与 old 不同

    返回：[(lineno, col_start, col_end, name, old_score, new_score), ...]
        lineno     1-based 行号
        col_start  0-based 起始列（含）
        col_end    0-based 结束列（不含）
    """
    try:
        tree = ast.parse(source, filename='<shensha>')
    except SyntaxError as exc:
        print(f'  ! 语法错误，跳过该文件: {exc}')
        return []

    reps = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != '_add_shensha':
            continue
        if len(node.args) < 2:
            continue
        name_arg, score_arg = node.args[0], node.args[1]
        # 名称必须是字面字符串（跳过 f-string / Name / 拼接）
        if not isinstance(name_arg, ast.Constant) or not isinstance(name_arg.value, str):
            continue
        # 分值必须是整数字面量（正数 Constant 或负数 UnaryOp(USub, Constant)）
        extracted = _extract_int_literal(score_arg)
        if extracted is None:
            continue
        old, lineno, col_start, col_end = extracted

        name = name_arg.value
        new = shensha_score_fn(event, name, old)
        if new is None or new == old:
            continue
        reps.append((lineno, col_start, col_end, name, old, new))
    return reps


def apply_replacements(source, reps):
    """把 reps 应用到 source，返回新字符串。

    保留原始行尾（CRLF / LF / CR）；按行号、列号倒序替换避免位置错位。
    """
    lines = source.splitlines(keepends=True)
    # 倒序：先处理大行号、大列号，保证同文件内多替换互不影响
    for lineno, col_start, col_end, _name, _old, new in sorted(
            reps, key=lambda r: (r[0], r[1]), reverse=True):
        idx = lineno - 1
        if idx < 0 or idx >= len(lines):
            continue
        line = lines[idx]
        # 拆出原始行尾
        if line.endswith('\r\n'):
            ending = '\r\n'
            body = line[:-2]
        elif line.endswith('\n'):
            ending = '\n'
            body = line[:-1]
        elif line.endswith('\r'):
            ending = '\r'
            body = line[:-1]
        else:
            ending = ''
            body = line
        # 替换 [col_start:col_end] 这一段整数字面量
        # 用 str(new) 即可：负数自带 '-'，正数无前导 '+'
        new_str = str(new)
        # ast 的 col_offset 对齐到字节级（UTF-8），但本表内全为 ASCII 数字，
        # 与字符级等价；为保险用 byte-safe 切片：
        body_bytes = body.encode('utf-8')
        if col_end > len(body_bytes):
            continue
        new_body = (body_bytes[:col_start] + new_str.encode('utf-8')
                    + body_bytes[col_end:]).decode('utf-8')
        lines[idx] = new_body + ending
    return ''.join(lines)


def md5_hex(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def process_file(filepath, event, shensha_score_fn, dry_run=True):
    """处理单个文件，返回 (changes, md5_before, md5_after_or_None)。"""
    with open(filepath, 'rb') as f:
        raw = f.read()
    has_bom = raw.startswith(b'\xef\xbb\xbf')
    src_text = raw.decode('utf-8-sig' if has_bom else 'utf-8')
    md5_before = md5_hex(src_text)

    reps = find_replacements(src_text, event, shensha_score_fn)
    if not reps:
        return 0, md5_before, None

    print(f'\n  [{os.path.basename(filepath)}]  事项={event}  待替换 {len(reps)} 处')
    for lineno, _cs, _ce, name, old, new in reps:
        print(f'    L{lineno:4d}  {name:16s}  {old:+4d} -> {new:+4d}')

    if dry_run:
        return len(reps), md5_before, None

    new_src = apply_replacements(src_text, reps)
    md5_after = md5_hex(new_src)
    if md5_after == md5_before:
        return 0, md5_before, None

    # 写盘：保留 BOM 与 UTF-8
    out_bytes = (b'\xef\xbb\xbf' if has_bom else b'') + new_src.encode('utf-8')
    with open(filepath, 'wb') as f:
        f.write(out_bytes)
    return len(reps), md5_before, md5_after


def main():
    parser = argparse.ArgumentParser(
        description='神煞分值单向生成器（以 SHENSHA_SCORES 为唯一事实源）')
    parser.add_argument('--apply', action='store_true',
                        help='实际写盘（默认仅 dry-run 预览）')
    parser.add_argument('--dir', default=None,
                        help='覆盖 shensha 目录路径（默认 modules/shensha）')
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    # 让 import 事项标准 / from 事项标准 import shensha_score 都可用
    for p in (base_dir, project_root):
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        from 事项标准 import shensha_score as _ss_fn
    except ImportError as exc:
        print(f'无法导入 modules/事项标准.shensha_score: {exc}')
        sys.exit(2)

    shensha_dir = args.dir or os.path.join(base_dir, 'shensha')
    if not os.path.isdir(shensha_dir):
        print(f'错误: shensha 目录不存在: {shensha_dir}')
        sys.exit(1)

    files = list_shensha_files(shensha_dir)
    if not files:
        print('未找到任何可处理的 shensha 文件')
        sys.exit(0)

    mode_str = 'DRY-RUN（预览）' if not args.apply else 'APPLY（写盘）'
    print('=' * 72)
    print(f'神煞分值单向生成器  [{mode_str}]')
    print(f'事实源: modules/事项标准.SHENSHA_SCORES')
    print(f'shensha 目录: {shensha_dir}')
    print('=' * 72)

    total = 0
    md5_log = []
    for fn in files:
        filepath = os.path.join(shensha_dir, fn)
        event = FILE_EVENT_MAP[fn]
        n, md5_b, md5_a = process_file(
            filepath, event, _ss_fn, dry_run=not args.apply)
        total += n
        md5_log.append((fn, n, md5_b, md5_a))

    print()
    print('=' * 72)
    print(f'汇总: 共 {len(files)} 个文件, 实际变更 {total} 处分值')
    if not args.apply:
        if total == 0:
            print('所有源码默认值已与 SHENSHA_SCORES 一致，无需写盘。')
        else:
            print('当前为 dry-run, 未修改任何文件。')
            print('确认无误后执行: python modules/评分权重校准.py --apply')
    else:
        if total == 0:
            print('无变更，未写盘任何文件。')
        else:
            print('已写盘。MD5 前后对比:')
            for fn, n, md5_b, md5_a in md5_log:
                if n > 0:
                    print(f'  {fn:20s}  {n:3d} 处   '
                          f'{md5_b[:8]} -> {md5_a[:8]}')
            print('提示: 请运行  python 系统自检.py  验证基线 (98/1/6) 不变。')
    print('=' * 72)


if __name__ == '__main__':
    main()
