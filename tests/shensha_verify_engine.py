# -*- coding: utf-8 -*-
"""
神煞穷举验证公共引擎
=====================

每个神煞只需声明：权威真值表（硬编码）+ 软件入口适配器，其余交给本引擎。

用法（在各 verify_<神煞名>.py 中）：

    from shensha_verify_engine import ShenShaCase, run_cli

    # 权威真值表（硬编码，绝不从软件读取）
    TRUTH = {...}

    def expected(inp):
        ...  # 返回期望结果

    def adapter(inp):
        ...  # 调用软件实现，返回实际结果

    case = ShenShaCase(
        name='天乙贵人',
        inputs=[(g, z) for g in TIAN_GAN for z in DI_ZHI],
        expected=expected,
        adapter=adapter,
    )

    if __name__ == '__main__':
        run_cli([case])

CLI:
    python verify_xxx.py                # 跑本文件声明的神煞
    python verify_a_class.py --all      # 跑批次全部
    python verify_a_class.py --case 天乙贵人
    python verify_xxx.py --verbose      # 打印差异明细

退出码：0 = 全部通过，1 = 存在差异
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if sys.stderr is not None and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(errors="replace")
except Exception:
    pass


# 软件入口不可用哨兵（导入失败/异常），区别于"合法的 None 结果"
_UNAVAILABLE = object()


@dataclass
class ShenShaCase:
    """单个神煞验证用例。

    Attributes:
        name: 神煞名称（唯一，用于 --case 过滤）
        category: A/B/C 类
        description: 一句话说明
        inputs: 穷举输入空间（list of tuple）
        expected: 真值函数 inp -> 期望结果（bool 或任意可比较值）
        adapter:  软件入口适配器 inp -> 实际结果；入口不可用时返回 _UNAVAILABLE
        compare:  'eq'（默认，逐值相等）或 'bool'（仅看真假）
    """
    name: str
    expected: Callable[[Tuple], Any]
    adapter: Callable[[Tuple], Any]
    inputs: List[Tuple] = field(default_factory=list)
    category: str = 'A'
    description: str = ''
    compare: str = 'eq'


def _normalize(val: Any) -> Any:
    """归一化比较值。'未知'字符串视为未命中。"""
    if val is _UNAVAILABLE:
        return _UNAVAILABLE
    if isinstance(val, str) and val == '未知':
        return None
    if isinstance(val, tuple) and len(val) >= 1 and val[0] == '未知':
        return None
    return val


def verify_case(case: ShenShaCase, verbose: bool = False) -> Dict[str, Any]:
    """对单个神煞执行穷举验证，返回统计。"""
    total = len(case.inputs)
    hits = 0            # 期望真且软件真
    false_pos: List[Tuple] = []   # 期望假但软件真
    misses: List[Tuple] = []      # 期望真但软件假
    unequal: List[Tuple] = []     # 值不相等（非布尔型）
    unavailable = 0

    for inp in case.inputs:
        exp = _normalize(case.expected(inp))
        got = _normalize(case.adapter(inp))
        if got is _UNAVAILABLE:
            unavailable += 1
            continue

        if case.compare == 'bool':
            exp_b = bool(exp)
            got_b = bool(got)
            if exp_b and got_b:
                hits += 1
            elif got_b and not exp_b:
                false_pos.append((inp, exp, got))
            elif exp_b and not got_b:
                misses.append((inp, exp, got))
        else:  # 'eq'
            if exp == got:
                if exp:  # 只统计正向命中数
                    hits += 1
            else:
                unequal.append((inp, exp, got))

    diff_count = len(false_pos) + len(misses) + len(unequal)
    passed = (diff_count == 0) and (unavailable == 0)

    result = {
        'name': case.name,
        'category': case.category,
        'description': case.description,
        'total': total,
        'hits': hits,
        'false_pos': false_pos,
        'misses': misses,
        'unequal': unequal,
        'unavailable': unavailable,
        'passed': passed,
    }
    return result


def _print_result(r: Dict[str, Any], verbose: bool) -> None:
    if r['unavailable'] == r['total'] and r['total'] > 0:
        status = '⚪'
    elif r['passed']:
        status = '✅'
    else:
        status = '❌'
    print(f"{status} {r['name']:<12}[{r['category']}] "
          f"样本{r['total']:>5}  命中{r['hits']:>4}  "
          f"误{r['false_pos'].__len__():>3}  漏{r['misses'].__len__():>3}  "
          f"差{r['unequal'].__len__():>3}  不可用{r['unavailable']:>3}"
          f"{'  — ' + r['description'] if r['description'] else ''}")
    if verbose or not r['passed']:
        for inp, exp, got in (r['false_pos'] + r['misses'] + r['unequal'])[:20]:
            print(f"      ✗ 输入{inp}: 期望={exp!r} 实际={got!r}")
        rest = len(r['false_pos']) + len(r['misses']) + len(r['unequal']) - 20
        if rest > 0:
            print(f"      ... 还有 {rest} 处差异")


def run_cli(cases: List[ShenShaCase], argv: Optional[List[str]] = None) -> int:
    """命令行入口。cases 为该批次所有神煞用例列表。"""
    ap = argparse.ArgumentParser(description='神煞穷举验证')
    ap.add_argument('--verbose', '-v', action='store_true', help='打印差异明细')
    ap.add_argument('--case', type=str, default=None, help='只运行指定神煞名')
    ap.add_argument('--all', action='store_true', help='运行全部（默认行为）')
    args = ap.parse_args(argv)

    targets = cases
    if args.case:
        targets = [c for c in cases if c.name == args.case]
        if not targets:
            print(f"未找到神煞: {args.case}")
            print("可用项：" + "、".join(c.name for c in cases))
            return 1

    print("=" * 80)
    print(f"神煞穷举验证（{len(targets)} 项）")
    print("=" * 80)

    results = [verify_case(c, args.verbose) for c in targets]
    for r in results:
        _print_result(r, args.verbose)

    print()
    print("=" * 80)
    passed = sum(1 for r in results if r['passed'])
    notimpl = sum(1 for r in results if r['unavailable'] == r['total'] and r['total'] > 0)
    failed = len(results) - passed - notimpl
    print(f"汇总：{len(results)} 项，通过 {passed}，未实现 {notimpl}，失败 {failed}")

    if failed > 0:
        print("❌ 存在差异失败项")
        print("=" * 80)
        return 1
    if notimpl > 0:
        print(f"⚠ 已实现项全部通过；{notimpl} 项软件未实现（⚪ 标记）")
        print("=" * 80)
        return 0
    print("✅ 全部通过")
    print("=" * 80)
    return 0
