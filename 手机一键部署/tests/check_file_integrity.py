# -*- coding: utf-8 -*-
"""
文件完整性 pre-commit 检查（2026-10-19，001 §125.7/§127 观察项 1）
======================================================================
动机：§125.7 记录 主程序.py:3436 曾被发现意外注入乱码（键盘误触类），
§207 记录会话状态消息被误粘贴进 .py 致 SyntaxError。为防外部编辑源
再次注入，提交前对目标文件做三项完整性检查：

1. 行尾一致性：同一文件不得混用 CRLF 与裸 LF（仓库策略见 .gitattributes：
   存储 LF，工作区 CRLF；混用即外部注入/工具改写特征）。CR-only 亦报错。
2. 非预期字符：禁止 NUL、U+FFFD、以及 Unicode 类别 Cc/Cf/Cs/Co/Cn
   （控制字符/零宽格式/代理/私用/未分配），仅放行 \t \n \r。
3. 可编译性（仅 .py）：py_compile 编译通过（外部粘贴大段裸文本会致
   SyntaxError，§207 事故的强拦截）。

用法：
  python tests/check_file_integrity.py                # 默认扫 主程序.py
  python tests/check_file_integrity.py a.py b.py      # 指定文件
  python tests/check_file_integrity.py --staged       # 钩子模式：扫暂存 .py
  python tests/check_file_integrity.py --all          # 全仓 tracked .py

退出码 0=全过 1=有失败（供 pre-commit / CI 使用）。
"""
import io
import os
import sys
import subprocess
import py_compile
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TARGETS = ['主程序.py']

# 放行的控制字符（字节级）
_ALLOWED_CTRL = {'\t', '\n', '\r'}
_FAIL_CATEGORIES = {'Cc', 'Cf', 'Cs', 'Co', 'Cn'}

FAILS = []


def _rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except Exception:
        return p


def _git_lines(args):
    r = subprocess.run(['git'] + args, cwd=ROOT, capture_output=True, text=True)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def check_line_endings(path):
    data = open(path, 'rb').read()
    crlf = data.count(b'\r\n')
    lf = data.count(b'\n') - crlf
    cr = data.count(b'\r') - crlf
    name = _rel(path)
    if cr > 0:
        FAILS.append('%s: CR-only 行尾 %d 处（异常）' % (name, cr))
    if crlf > 0 and lf > 0:
        FAILS.append('%s: 行尾混用 CRLF=%d / 裸LF=%d（外部注入特征）' % (name, crlf, lf))
    return crlf, lf, cr


def check_nonprint(path):
    data = open(path, 'rb').read()
    name = _rel(path)
    if b'\x00' in data:
        FAILS.append('%s: 含 NUL 字节' % name)
    text = data.decode('utf-8', errors='replace')
    bad = []
    for i, ch in enumerate(text):
        if ch in _ALLOWED_CTRL:
            continue
        if ch == '\ufeff' and i == 0:
            continue  # 行首 UTF-8 BOM 签名，合法
        if ch == '\ufffd':
            bad.append((i, ch, 'U+FFFD 替换符'))
            continue
        import unicodedata
        cat = unicodedata.category(ch)
        if cat in _FAIL_CATEGORIES:
            bad.append((i, ch, cat))
    if bad:
        # 转行号定位（前 5 处）
        line_of = {}
        ln = 1
        for idx, ch in enumerate(text):
            line_of[idx] = ln
            if ch == '\n':
                ln += 1
        detail = '; '.join('行%d %r(%s)' % (line_of[i], c, r) for i, c, r in bad[:5])
        FAILS.append('%s: 非预期字符 %d 处：%s' % (name, len(bad), detail))
    return len(bad)


def check_compile(path):
    if not path.endswith('.py'):
        return True
    name = _rel(path)
    try:
        with tempfile.TemporaryDirectory() as td:
            py_compile.compile(path, cfile=os.path.join(td, 'x.pyc'),
                               doraise=True, quiet=2)
        return True
    except py_compile.PyCompileError as e:
        FAILS.append('%s: py_compile 失败：%s' % (name, str(e).splitlines()[0]))
        return False


def main(argv):
    mode = 'default'
    files = []
    for a in argv:
        if a == '--staged':
            mode = 'staged'
        elif a == '--all':
            mode = 'all'
        else:
            files.append(a)

    if mode == 'staged':
        files = [f for f in _git_lines(['diff', '--cached', '--name-only',
                                        '--diff-filter=ACM']) if f.endswith('.py')]
    elif mode == 'all':
        files = [f for f in _git_lines(['ls-files', '*.py'])]
    elif not files:
        files = DEFAULT_TARGETS

    # 转为绝对路径
    abs_files = [f if os.path.isabs(f) else os.path.join(ROOT, f) for f in files]
    if mode in ('staged', 'all'):
        abs_files = [f for f in abs_files if os.path.exists(f)]

    if not abs_files:
        print('[OK] 无目标文件（%s 模式无 .py）' % mode)
        return 0

    for f in abs_files:
        check_line_endings(f)
        check_nonprint(f)
        check_compile(f)

    print('检查文件 %d 个（模式=%s）' % (len(abs_files), mode))
    if FAILS:
        print('FAIL: %d 项' % len(FAILS))
        for x in FAILS:
            print(' -', x)
        return 1
    print('ALL PASS：行尾一致 + 无非预期字符 + py_compile OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
