# -*- coding: utf-8 -*-
"""测试统一入口（001 §199 H2 第一批）。

把 tests/ 下所有 verify_*.py / test_*.py / check_*.py 统一接管，一键跑批：

    python tests/run_all.py                  # 全量
    python tests/run_all.py --filter 神煞     # 只跑文件名含关键字的脚本
    python tests/run_all.py --json out.json  # 机器可读结果（CI / 快照留档）
    python tests/run_all.py --timeout 600    # 单脚本超时秒数（默认 300）

退出码：全部 PASS → 0；有 FAIL/TIMEOUT → 1；运行器自身异常 → 2。

设计约束：
- 每个脚本在**独立子进程**中执行（互不污染，避免模块级状态泄漏）。
- 工作目录固定为仓根（与手工在仓根执行 python tests/xxx.py 完全等价）。
- 环境强制 UTF-8，杜绝中文输出在 Windows 默认代码页下乱码。
- 不重写任何脚本逻辑，只做调度与汇总；脚本自身 exit code 即判定依据。
"""
import argparse
import json
import os
import subprocess
import sys
import time

PREFIXES = ('verify_', 'test_', 'check_')
# 001 §214 C3（2026-11-03 拍板）：大考探针不以 verify_/test_/check_ 开头，
# 在此显式托管；--no-write 保证跑批不产生 docs 产物、不污染工作区。
EXTRA_SCRIPTS = [('大考_黄金课探针.py', ['--no-write'])]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, 'tests')


def discover(only=None):
    names = []
    for fn in sorted(os.listdir(TESTS)):
        if not fn.endswith('.py') or fn == 'run_all.py':
            continue
        if not fn.startswith(PREFIXES):
            continue
        if only and only not in fn:
            continue
        names.append((fn, []))
    for fn, extra in EXTRA_SCRIPTS:
        if not os.path.isfile(os.path.join(TESTS, fn)):
            continue
        if only and only not in fn:
            continue
        names.append((fn, list(extra)))
    return names


def run_one(fn, timeout, extra=None):
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    t0 = time.time()
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(TESTS, fn)] + list(extra or []),
            cwd=ROOT, env=env, timeout=timeout,
            capture_output=True, text=True, encoding='utf-8', errors='replace')
        code, out = p.returncode, (p.stdout or '') + (p.stderr or '')
    except subprocess.TimeoutExpired as e:
        code = 'TIMEOUT'
        out = ((e.stdout or '') if isinstance(e.stdout, str) else '')
    return {'name': fn, 'exit': code, 'sec': round(time.time() - t0, 1), 'out': out}


def tail(text, n=20):
    lines = [ln for ln in (text or '').splitlines() if ln.strip()]
    return '\n'.join(lines[-n:])


def main():
    ap = argparse.ArgumentParser(description='测试统一入口')
    ap.add_argument('--filter', default=None)
    ap.add_argument('--timeout', type=int, default=300)
    ap.add_argument('--json', default=None)
    args = ap.parse_args()

    if not os.path.isdir(TESTS):
        print('错误：找不到 tests 目录：%s' % TESTS)
        return 2
    scripts = discover(args.filter)
    if not scripts:
        print('错误：没有匹配的测试脚本（--filter=%r）' % args.filter)
        return 2

    print('=' * 72)
    print('测试统一跑批  共 %d 个脚本  仓根=%s' % (len(scripts), ROOT))
    print('=' * 72)

    results = []
    for i, (fn, extra) in enumerate(scripts, 1):
        r = run_one(fn, args.timeout, extra)
        results.append(r)
        tag = 'TIMEOUT' if r['exit'] == 'TIMEOUT' else (
            'PASS' if r['exit'] == 0 else 'FAIL')
        print('[%3d/%3d] %-6s %-6s exit=%-7s %5.1fs  %s'
              % (i, len(scripts), tag, '', r['exit'], r['sec'], fn))
        if tag != 'PASS':
            print('-' * 60)
            print(tail(r['out']))
            print('-' * 60)

    fails = [r for r in results if r['exit'] != 0]
    n_pass = len(results) - len(fails)
    total_sec = round(sum(r['sec'] for r in results), 1)

    print()
    print('=' * 72)
    print('汇总：TOTAL=%d  PASS=%d  FAIL=%d  TIMEOUT=%d  耗时=%.1fs'
          % (len(results), n_pass, len(fails),
             sum(1 for r in results if r['exit'] == 'TIMEOUT'), total_sec))
    if fails:
        print('失败清单：')
        for r in fails:
            print('  %-40s exit=%s' % (r['name'], r['exit']))
    print('=' * 72)

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({'total': len(results), 'pass': n_pass,
                       'fail': len(fails),
                       'results': [{k: r[k] for k in ('name', 'exit', 'sec')}
                                   for r in results]},
                      f, ensure_ascii=False, indent=1)
        print('已写出：%s' % args.json)

    return 1 if fails else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print('运行器异常：%s: %s' % (type(e).__name__, e))
        sys.exit(2)
