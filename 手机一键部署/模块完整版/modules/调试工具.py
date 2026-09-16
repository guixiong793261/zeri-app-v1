# -*- coding: utf-8 -*-
"""
================================================================================
调试工具模块
================================================================================
提供运行时函数调用追踪、调用状态统计等调试功能

使用方法:
    1. 追踪装饰器:
        from .调试工具 import trace_call
        @trace_call
        def your_func(...): ...

    2. 调用状态统计:
        from .调试工具 import record_call, get_call_stats, reset_stats
        def your_func(...):
            record_call('模块名', '函数名')
            ...
================================================================================
"""

import functools
import logging
import time
import os
import sys
import threading

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------
_logger = logging.getLogger('CallTrace')
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    ))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False


# ---------------------------------------------------------------------------
# L2-A: 函数调用追踪装饰器（无侵入）
# ---------------------------------------------------------------------------
def trace_call(func):
    """
    追踪函数调用的装饰器

    用法:
        @trace_call
        def my_func(a, b):
            return a + b

    调用时会自动打印:
        - 🔍 调用: 模块名.函数名
        - ✅ 返回: 模块名.函数名 (耗时: xx.xxms)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        module_name = getattr(func, '__module__', 'unknown')
        func_name = func.__qualname__
        _logger.info(f"🔍 调用: {module_name}.{func_name}")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            _logger.info(f"✅ 返回: {module_name}.{func_name} (耗时: {elapsed:.2f}ms)")
            return result
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            _logger.error(
                f"❌ 异常: {module_name}.{func_name} "
                f"(耗时: {elapsed:.2f}ms) - {type(e).__name__}: {e}"
            )
            raise
    return wrapper


# ---------------------------------------------------------------------------
# L2-B: 调用状态统计（埋点计数器）
# ---------------------------------------------------------------------------
_call_stats_lock = threading.Lock()
_call_stats = {}


def record_call(module_name, function_name):
    """
    记录一次函数调用（埋点用）

    Args:
        module_name: 模块名称，如 '二十四山择吉天机'
        function_name: 函数名称，如 'check_mountain_day'
    """
    key = f"{module_name}.{function_name}"
    with _call_stats_lock:
        if key not in _call_stats:
            _call_stats[key] = {
                'count': 0,
                'last_call': None,
                'first_call': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        _call_stats[key]['count'] += 1
        _call_stats[key]['last_call'] = time.strftime('%Y-%m-%d %H:%M:%S')


def get_call_stats():
    """
    获取当前所有调用统计

    Returns:
        dict: {
            '模块名.函数名': {
                'count': 调用次数,
                'first_call': 首次调用时间,
                'last_call': 最后调用时间
            },
            ...
        }
    """
    with _call_stats_lock:
        return dict(_call_stats)


def reset_stats():
    """重置所有调用统计"""
    global _call_stats
    with _call_stats_lock:
        _call_stats = {}


def print_call_stats(title="调用统计报告"):
    """
    打印格式化的调用统计报告到控制台
    """
    stats = get_call_stats()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    if not stats:
        print("  (暂无调用记录)")
    else:
        print(f"  {'模块.函数':<45} {'次数':>6}  最后调用时间")
        print("  " + "-" * 68)
        for key, info in sorted(stats.items()):
            print(
                f"  {key:<45} {info['count']:>6}  "
                f"{info.get('last_call', '-')}"
            )
    print("=" * 70)
    print()


# ---------------------------------------------------------------------------
# L2-C: 全局 sys.settrace 追踪器（最细粒度，独立脚本用）
# ---------------------------------------------------------------------------
class GlobalTracer:
    """
    基于 sys.settrace 的全局调用追踪器

    用法:
        tracer = GlobalTracer(only_modules=True)
        sys.settrace(tracer.trace)
        # ... 运行代码 ...
        tracer.report()
    """

    def __init__(self, only_modules=True, modules_dir_name='modules', verbose=False):
        """
        Args:
            only_modules: 只追踪 modules 目录下的文件
            modules_dir_name: 模块目录名称（用于过滤）
            verbose: 是否打印每个调用
        """
        self.only_modules = only_modules
        self.modules_dir_name = modules_dir_name
        self.verbose = verbose
        self.calls = []
        self._call_count = {}
        self._lock = threading.Lock()
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def trace(self, frame, event, arg):
        if event != 'call':
            return self.trace

        code = frame.f_code
        filename = code.co_filename
        func_name = code.co_name

        # 过滤：只追踪项目内文件
        if self.only_modules:
            if self.modules_dir_name not in filename.replace('\\', '/'):
                return self.trace

        # 跳过调试工具自身
        if '调试工具.py' in filename:
            return self.trace

        # 简化文件名
        try:
            rel_path = os.path.relpath(filename, self.project_root)
        except ValueError:
            rel_path = os.path.basename(filename)

        key = f"{rel_path}:{func_name}"

        with self._lock:
            self._call_count[key] = self._call_count.get(key, 0) + 1
            call_idx = self._call_count[key]

        if self.verbose:
            print(f"  [调用#{call_idx}] {func_name} @ {rel_path}")

        self.calls.append({
            'time': time.time(),
            'file': rel_path,
            'func': func_name,
            'line': code.co_firstlineno
        })

        return self.trace

    def report(self, top_n=30):
        """打印追踪报告"""
        print("\n" + "=" * 70)
        print("  sys.settrace 全局调用追踪报告")
        print("=" * 70)
        print(f"  总调用次数: {len(self.calls)}")
        print(f"  唯一函数数: {len(self._call_count)}")
        print("-" * 70)
        print(f"  Top {top_n} 被调用最多的函数:")
        print(f"  {'调用点':<55} {'次数':>6}")
        print("  " + "-" * 63)
        sorted_items = sorted(
            self._call_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        for key, cnt in sorted_items:
            print(f"  {key:<55} {cnt:>6}")
        print("=" * 70)
        print()

    def get_unique_functions(self):
        """返回所有被调用过的 (文件, 函数) 集合"""
        return set(self._call_count.keys())


# ---------------------------------------------------------------------------
# L2-D: 神煞函数专用监听器（sys.settrace，只盯 shensha/黄道 目录）
# ---------------------------------------------------------------------------
# 运行时配置：
#   调试工具.DEBUG_TRACE_PICKS = True   时才实时打印
#   调用过的神煞模块会被记录到 CALLED_MODULES（用于 score 调用水印）
# ---------------------------------------------------------------------------
DEBUG_TRACE_PICKS = False
CALLED_MODULES = []   # 已调用过的神煞模块文件名集合（唯一）
_CALLED_SET = set()
_TRACE_PICKS_LOCK = threading.Lock()


def reset_called_modules():
    """在每次择日评分流程开始前重置，避免前一次择日的结果污染本次水印"""
    global CALLED_MODULES, _CALLED_SET
    with _TRACE_PICKS_LOCK:
        CALLED_MODULES = []
        _CALLED_SET = set()


def _register_module_call(filename: str):
    """把匹配到的模块文件名登记到 CALLED_MODULES（仅登记一次）"""
    fname = os.path.basename(filename)
    with _TRACE_PICKS_LOCK:
        if fname not in _CALLED_SET:
            _CALLED_SET.add(fname)
            CALLED_MODULES.append(fname)


def trace_picks(frame, event, arg):
    """
    神煞/黄道专用追踪器（对 sys.settrace 注册）

    用法：
        import modules.调试工具 as dt
        dt.DEBUG_TRACE_PICKS = True
        dt.reset_called_modules()
        sys.settrace(dt.trace_picks)
        try:
            score_result = scorer.calculate_score(...)   # 运行择日
        finally:
            sys.settrace(None)
        print(dt.CALLED_MODULES)   # 查看实际触发过哪些神煞文件
    """
    if event != 'call':
        return trace_picks
    try:
        code = frame.f_code
        filename = code.co_filename.replace('\\', '/')
        # 只盯神煞目录 + 黄道.py
        if not ('shensha' in filename or '黄道' in filename or 'huangdao' in filename.lower()):
            return trace_picks
        # 跳过调试工具自身 + 测试文件
        if '调试工具.py' in filename or filename.endswith('_test.py') or '/tests/' in filename:
            return trace_picks

        func_name = code.co_name
        # 记录被调用过的模块（用于分数水印）
        _register_module_call(filename)

        if DEBUG_TRACE_PICKS:
            rel = filename.split('/')[-1]
            _logger.info(f"🔍 [神煞触发] {rel}::{func_name}")
    except Exception:
        pass
    return trace_picks


def attach_debug_watermark(result: dict) -> dict:
    """
    调用水印：在评分结果末尾附加 _debug_called_modules 字段

    典型用法（评分器.py 最终 return 之前）：
        from modules.调试工具 import attach_debug_watermark
        return attach_debug_watermark(result)

    返回：
        dict: 原 result 附加 '_debug_called_modules' 字段
              （若 result 已有同名字段则追加不覆盖）
    """
    try:
        import copy
        out = copy.copy(result)
    except Exception:
        out = result
    try:
        out['_debug_called_modules'] = list(CALLED_MODULES)
    except Exception:
        pass
    return out


def get_called_modules_snapshot() -> list:
    """返回当前已调用模块的快照"""
    with _TRACE_PICKS_LOCK:
        return list(CALLED_MODULES)

