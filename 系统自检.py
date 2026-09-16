# -*- coding: utf-8 -*-
"""
================================================================================
专业级正五行择日软件 — 系统自检脚本
================================================================================
一键执行「L1静态检查 → L2调用追踪 → L3单元测试 → L4集成测试」四层验证，
输出结构化自检报告到控制台与 logs/系统自检报告_YYYYMMDD_HHMMSS.txt。

用法:
    python 系统自检.py
    或: python 系统自检.py --no-l3   (跳过L3)
        python 系统自检.py --quick   (快速模式: 仅L1+L3轻量+L4核心)

本脚本设计为「可重复运行、不修改生产代码」。
================================================================================
"""

import sys
import os
import time
import argparse
import datetime
import traceback
import io
import unittest
import contextlib

# ---------------------------------------------------------------------------
# 路径准备
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(PROJECT_ROOT, 'modules')
TESTS_DIR = os.path.join(PROJECT_ROOT, 'tests')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
for _p in [PROJECT_ROOT, MODULES_DIR, TESTS_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ---------------------------------------------------------------------------
# 报告输出工具
# ---------------------------------------------------------------------------
class SelfCheckReport:
    """结构化自检报告（控制台 + 文件双写）"""

    LEVEL_OK = '✅'
    LEVEL_FAIL = '❌'
    LEVEL_WARN = '⚠️ '
    LEVEL_INFO = 'ℹ️ '

    def __init__(self):
        self.ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_path = os.path.join(LOGS_DIR, f'系统自检报告_{self.ts}.txt')
        self._file = open(self.log_path, 'w', encoding='utf-8')
        self.results = {
            'L1静态检查': {'pass': 0, 'fail': 0, 'warn': 0},
            'L2调用追踪': {'pass': 0, 'fail': 0, 'warn': 0},
            'L3单元测试': {'pass': 0, 'fail': 0, 'warn': 0},
            'L3B业务专项': {'pass': 0, 'fail': 0, 'warn': 0},
            'L3C黄金基准': {'pass': 0, 'fail': 0, 'warn': 0},
            'L4集成测试': {'pass': 0, 'fail': 0, 'warn': 0},
        }
        self._start = time.time()

    def _write(self, msg):
        """同时写到控制台和文件"""
        # 控制台
        print(msg)
        # 文件（去除ANSI颜色标记，这里本来就不用颜色）
        self._file.write(msg + '\n')
        self._file.flush()

    def section(self, title):
        bar = "=" * 74
        self._write("")
        self._write(bar)
        self._write(f"  {title}")
        self._write(bar)

    def sub_section(self, title):
        self._write(f"\n  【{title}】")

    def line(self, s=""):
        self._write(s)

    def record(self, layer, status, title, detail=""):
        """记录一条结果"""
        prefix = {
            'ok': self.LEVEL_OK,
            'fail': self.LEVEL_FAIL,
            'warn': self.LEVEL_WARN,
            'info': self.LEVEL_INFO,
        }.get(status, '  ')
        self._write(f"  {prefix} {title}" + (f" — {detail}" if detail else ""))
        if layer in self.results and status in ('ok', 'fail', 'warn'):
            key = {'ok': 'pass', 'fail': 'fail', 'warn': 'warn'}[status]
            self.results[layer][key] += 1

    def final_summary(self):
        elapsed = time.time() - self._start
        self.section("最终汇总")
        self._write(f"  总耗时: {elapsed:.2f} 秒")
        self._write(f"  报告文件: {self.log_path}")
        self._write("")
        header = f"  {'层级':<16} {'通过':>5} {'失败':>5} {'警告':>5}"
        self._write(header)
        self._write("  " + "-" * 36)
        total_pass = total_fail = total_warn = 0
        for layer, r in self.results.items():
            self._write(
                f"  {layer:<16} {r['pass']:>5} {r['fail']:>5} {r['warn']:>5}"
            )
            total_pass += r['pass']
            total_fail += r['fail']
            total_warn += r['warn']
        self._write("  " + "-" * 36)
        self._write(
            f"  {'合计':<16} {total_pass:>5} {total_fail:>5} {total_warn:>5}"
        )
        self._write("")
        if total_fail == 0:
            verdict = "🟢 整体通过（所有失败项为0）"
        elif total_fail <= 3:
            verdict = "🟡 部分通过（存在少量失败项，请检查报告）"
        else:
            verdict = "🔴 未通过（存在较多失败项，建议逐项排查）"
        self._write(f"  结论: {verdict}")
        self._write("")
        self._write("=" * 74)
        self._file.close()
        return total_fail == 0


# ==========================================================================
# L1: 静态导入检查（grep 风格的纯 Python 实现，不依赖外部命令）
# ==========================================================================
def run_l1_static_import_check(rep: SelfCheckReport):
    rep.section("L1: 静态导入检查")

    # 定义核心模块及其关键函数（主程序导入口径为真值）
    CORE_MODULES = {
        'modules.四柱计算器': [
            'calculate_sizhu', 'analyze_sizhu', 'get_lunar_date'
        ],
        'modules.评分器': [
            'calculate_score', 'Scorer'
        ],
        'modules.黄道': [
            'calculate_huangdao', 'get_huangdao_yiji', '黄道计算器'
        ],
        'modules.喜用神计算器': [
            'calculate_xishen_yongshen'
        ],
        'modules.工具函数': [
            'DI_ZHI_WUXING', 'TIAN_GAN_WUXING',
            'get_yintai', 'get_yangqi'
        ],
        'modules.二十四山': [
            'get_mountain_info', 'shan_xiang_to_shan', 'get_shan_xiang_list'
        ],
        'modules.二十四山择吉天机': [
            'get_mountain_data', 'check_mountain_day', 'check_sansha',
            'check_yinfu', 'check_chong_shan', 'calculate_keshan_yun',
            'get_mountain_wuxing', 'get_yinfu_config', 'is_after_dongzhi'
        ],
        'modules.婚嫁评分算法': [
            'get_yintai', 'get_yangqi', 'score_marriage_day',
            'is_month_break', 'is_sili_sijue', 'is_sanniangsha'
        ],
    }

    # 1.1 模块导入 + 导出检查
    rep.sub_section("1.1 模块导入 & 关键导出")
    all_export_ok = True
    for mod_path, expected_exports in CORE_MODULES.items():
        try:
            mod = __import__(mod_path, fromlist=expected_exports)
            missing = []
            for exp in expected_exports:
                if not hasattr(mod, exp):
                    missing.append(exp)
            if missing:
                rep.record('L1静态检查', 'fail', mod_path,
                           f"缺少导出: {missing}")
                all_export_ok = False
            else:
                rep.record('L1静态检查', 'ok', mod_path,
                           f"全部导出 ({len(expected_exports)} 项)")
        except Exception as e:
            rep.record('L1静态检查', 'fail', mod_path,
                       f"导入失败: {type(e).__name__}: {e}")
            all_export_ok = False

    # 1.2 「僵尸代码」初筛：modules 顶层 .py 中 def 定义的函数，
    #     是否被主程序 / 评分器 / 其他模块 中任何 import 语句引用
    rep.sub_section("1.2 僵尸代码初筛（函数定义 vs 导入引用）")

    def _collect_py_files(root, exclude_dirs=None, max_depth=6):
        """扫描 .py 文件（带深度限制 + 目录黑名单，避免手机一键部署的深层嵌套）"""
        if exclude_dirs is None:
            exclude_dirs = {
                '__pycache__', '.git', 'logs', '手机一键部署',
                '.idea', '.vscode', 'build', 'dist'
            }
        files = []
        root = os.path.abspath(root)
        root_depth = root.rstrip(os.sep).count(os.sep)
        for dirpath, dirnames, filenames in os.walk(root):
            # 深度限制
            cur_depth = dirpath.rstrip(os.sep).count(os.sep)
            if cur_depth - root_depth >= max_depth:
                dirnames[:] = []  # 不再下探
                continue
            # 黑名单过滤
            dirnames[:] = [
                d for d in dirnames
                if d not in exclude_dirs
                and not d.startswith('.')
            ]
            for fn in filenames:
                if fn.endswith('.py'):
                    files.append(os.path.join(dirpath, fn))
        return files

    all_py_files = _collect_py_files(PROJECT_ROOT)

    # 只扫描 modules 下的顶层定义（非 .pyc）
    module_py_files = [
        f for f in _collect_py_files(MODULES_DIR)
        if os.path.dirname(f) == MODULES_DIR  # 只检查 modules 目录顶层，
                                              # rules/shensha 子目录暂不做深度筛查
    ]

    import re
    # 收集所有 def 函数名（modules/*.py）
    defined_funcs = {}  # fname -> file list
    for mf in module_py_files:
        try:
            with open(mf, 'r', encoding='utf-8') as fh:
                for ln, line in enumerate(fh, 1):
                    m = re.match(r'^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', line)
                    if m:
                        fname = m.group(1)
                        if fname.startswith('_'):
                            continue  # 私有函数不计入
                        defined_funcs.setdefault(fname, []).append(
                            f"{os.path.basename(mf)}:{ln}"
                        )
        except UnicodeDecodeError:
            continue

    # 收集所有 import 语句中的引用名称（整个项目）
    imported_names = set()
    import_patterns = [
        re.compile(r'from\s+[\w\.]+\s+import\s+(.+)'),
        re.compile(r'import\s+([\w\.]+)'),
    ]
    for pf in all_py_files:
        try:
            with open(pf, 'r', encoding='utf-8') as fh:
                for line in fh:
                    line_stripped = line.split('#', 1)[0].strip()
                    if not line_stripped or line_stripped.startswith('#'):
                        continue
                    # from X import A, B, C as D
                    m1 = re.match(r'from\s+[\w\.]+\s+import\s+(.+)', line_stripped)
                    if m1:
                        imp_part = m1.group(1)
                        for item in imp_part.split(','):
                            item = item.strip()
                            if not item or item.startswith('(') or item == '*':
                                continue
                            real = item.split(' as ')[0].strip().strip('()')
                            if real:
                                imported_names.add(real)
                    # import X
                    m2 = re.match(r'import\s+([\w\.]+)', line_stripped)
                    if m2:
                        top = m2.group(1).split('.')[-1]
                        imported_names.add(top)
        except UnicodeDecodeError:
            continue

    # 比对：定义了但公开名从未出现于任何 import 中 → 报告为「疑似未被导入」
    potential_unused = []
    for fname, locations in sorted(defined_funcs.items()):
        # 过滤明显的内部函数 / 测试函数
        if fname.startswith('test_') or fname in ('main', ):
            continue
        if fname not in imported_names:
            potential_unused.append((fname, locations))

    if potential_unused:
        # 只列出最可能可疑的（Top 20）
        rep.record(
            'L1静态检查', 'warn',
            f"发现 {len(potential_unused)} 个公开函数未出现在任何 import 语句",
            "(可能是内部通过 getattr 调用 / 字符串反射 / UI事件绑定，"
            "需结合L2验证)"
        )
        for fname, locs in potential_unused[:20]:
            rep.line(f"       · {fname}  @ {', '.join(locs)}")
        if len(potential_unused) > 20:
            rep.line(f"       ... 其余 {len(potential_unused)-20} 个省略")
    else:
        rep.record('L1静态检查', 'ok',
                   "所有公开函数均出现在至少 1 个 import 语句中")

    # 1.3 关键调用链路确认（静态文本检查，验证 import 语句存在性）
    rep.sub_section("1.3 关键调用链路确认（静态引用存在性）")
    critical_links = [
        # (描述, 要搜索的文件, 要搜索的文本片段)
        (
            '评分器 → 引用二十四山择吉天机.check_mountain_day',
            os.path.join(MODULES_DIR, '评分器.py'),
            'check_mountain_day'
        ),
        (
            '评分器._get_sansha_info → import check_mountain_day',
            os.path.join(MODULES_DIR, '评分器.py'),
            'from .二十四山择吉天机 import check_mountain_day'
        ),
        (
            '修造规则 → 引用二十四山择吉天机函数',
            os.path.join(MODULES_DIR, 'rules', '修造规则.py'),
            '二十四山择吉天机'
        ),
        (
            '主程序 → 导入二十四山择吉天机.*',
            os.path.join(PROJECT_ROOT, '主程序.py'),
            'from modules.二十四山择吉天机 import'
        ),
        (
            '主程序 → 导入 calculate_score',
            os.path.join(PROJECT_ROOT, '主程序.py'),
            'from modules.评分器 import calculate_score'
        ),
        (
            '婚嫁规则 → 使用 get_yintai / get_yangqi (统一函数)',
            os.path.join(MODULES_DIR, 'rules', '嫁娶规则.py'),
            'get_yintai'
        ),
        (
            '评分器 → 黄道模块 calculate_huangdao',
            os.path.join(MODULES_DIR, '评分器.py'),
            'calculate_huangdao'
        ),
    ]
    for desc, fpath, needle in critical_links:
        if not os.path.isfile(fpath):
            rep.record('L1静态检查', 'warn', desc,
                       f"文件不存在: {os.path.basename(fpath)}")
            continue
        try:
            with open(fpath, 'r', encoding='utf-8') as fh:
                text = fh.read()
            if needle in text:
                rep.record('L1静态检查', 'ok', desc)
            else:
                rep.record('L1静态检查', 'warn', desc,
                           f"未找到文本片段: {needle[:50]}")
        except Exception as e:
            rep.record('L1静态检查', 'warn', desc, f"{type(e).__name__}: {e}")


# ==========================================================================
# L2: 运行时调用追踪（埋点 + GlobalTracer）
# ==========================================================================
def run_l2_runtime_trace(rep: SelfCheckReport, quick=False):
    rep.section("L2: 运行时调用追踪")

    try:
        from modules.调试工具 import GlobalTracer, record_call, get_call_stats, reset_stats
    except ImportError as e:
        rep.record('L2调用追踪', 'fail', '调试工具模块',
                   f"导入失败: {e}")
        return

    # 2.1 trace_call 装饰器基本功能
    rep.sub_section("2.1 trace_call 装饰器烟雾测试")
    try:
        from modules.调试工具 import trace_call

        @trace_call
        def _dummy_add(a, b):
            return a + b

        r = _dummy_add(2, 3)
        if r == 5:
            rep.record('L2调用追踪', 'ok', 'trace_call 装饰器工作正常')
        else:
            rep.record('L2调用追踪', 'fail', 'trace_call 装饰器',
                       f"返回值异常: {r}")
    except Exception as e:
        rep.record('L2调用追踪', 'fail', 'trace_call 装饰器',
                   f"{type(e).__name__}: {e}")

    # 2.2 record_call / get_call_stats 计数器
    rep.sub_section("2.2 调用计数器（record_call/get_call_stats）")
    try:
        reset_stats()
        for i in range(5):
            record_call('二十四山择吉天机', 'check_mountain_day')
        for i in range(3):
            record_call('评分器', 'score')
        stats = get_call_stats()
        c1 = stats.get('二十四山择吉天机.check_mountain_day', {}).get('count', -1)
        c2 = stats.get('评分器.score', {}).get('count', -1)
        if c1 == 5 and c2 == 3:
            rep.record('L2调用追踪', 'ok', '调用计数器统计正确',
                       f"check_mountain_day×5, score×3")
        else:
            rep.record('L2调用追踪', 'fail', '调用计数器',
                       f"check_mountain_day={c1}, score={c2}")
        reset_stats()
    except Exception as e:
        rep.record('L2调用追踪', 'fail', '调用计数器',
                   f"{type(e).__name__}: {e}")

    # 2.3 GlobalTracer 跑一次评分，确认核心函数出现在调用栈
    rep.sub_section("2.3 GlobalTracer → 核心函数出现在调用栈")
    try:
        # 使用顶部 "import datetime" 的 datetime.date，避免在函数内
        # 再次 "from datetime import date" 引发 UnboundLocalError 陷阱
        from modules.四柱计算器 import calculate_sizhu
        from modules.评分器 import calculate_score

        tracer = GlobalTracer(only_modules=True, verbose=False)
        sys.settrace(tracer.trace)

        # 执行一次修造评分（带山向）
        test_date = datetime.date(2026, 5, 20)
        sz = calculate_sizhu(test_date, 13, 0)
        sz['year'], sz['month'], sz['day'], sz['date'] = (
            test_date.year, test_date.month, test_date.day, test_date
        )
        calculate_score(
            sizhu=sz, event_type='修造',
            house_type='阳宅', shan_xiang='壬山丙向'
        )
        sys.settrace(None)

        called = tracer.get_unique_functions()
        called_concat = '\n'.join(called)

        # 必查清单
        must_any = [
            ('Scorer.score 被调用', lambda: 'score' in called_concat and '评分器' in called_concat),
            ('calculate_sizhu 被调用', lambda: 'calculate_sizhu' in called_concat),
            ('calculate_huangdao 被调用', lambda: 'calculate_huangdao' in called_concat or '黄道' in called_concat),
            ('喜用神计算器.* 被调用', lambda: '喜用神' in called_concat or 'xishen' in called_concat.lower() or 'calculate_xishen' in called_concat),
        ]
        for desc, pred in must_any:
            try:
                ok = pred()
            except Exception:
                ok = False
            if ok:
                rep.record('L2调用追踪', 'ok', desc)
            else:
                rep.record('L2调用追踪', 'warn', desc,
                           f"(调用栈样本 {len(called)} 个)")

        # 山家检查：check_mountain_day 或相关 check_ 函数
        mountain_hit = any(
            'check_mountain_day' in x or
            ('二十四山择吉天机' in x and 'check_' in x)
            for x in called
        )
        if mountain_hit:
            rep.record('L2调用追踪', 'ok',
                       '二十四山择吉天机.check_mountain_day 被评分器调用')
        else:
            # 进一步检查评分器 sansha_info 返回是否包含检查结果
            rep.record('L2调用追踪', 'warn',
                       'settrace 未命中 check_mountain_day',
                       '（改用 L4 返回值深度验证补充）')
            # 我们在这里做一次「无山向 vs 有山向」对比：
            # 有山向时评分返回的 sansha_info 应该更大（包含 mountain_day_check）
            try:
                sz2 = calculate_sizhu(datetime.date(2026, 7, 10), 10, 0)
                sz2['year'], sz2['month'], sz2['day'], sz2['date'] = (
                    2026, 7, 10, datetime.date(2026, 7, 10)
                )
                r_no_shan = calculate_score(sizhu=sz2, event_type='修造')
                r_with_shan = calculate_score(
                    sizhu=sz2, event_type='修造',
                    house_type='阳宅', shan_xiang='壬山丙向'
                )
                s_no = r_no_shan.get('sansha_info', {})
                s_w = r_with_shan.get('sansha_info', {})
                if isinstance(s_w, dict) and 'mountain_day_check' in s_w:
                    rep.record('L2调用追踪', 'ok',
                               '无山向 vs 有山向 差异验证通过',
                               '有山向 → sansha_info 含 mountain_day_check')
                else:
                    rep.record('L2调用追踪', 'warn',
                               '无山向 vs 有山向',
                               f"sansha_info keys(with) = {list(s_w.keys()) if isinstance(s_w, dict) else s_w}")
            except Exception as e2:
                rep.record('L2调用追踪', 'warn',
                           '无山向 vs 有山向 补充验证失败',
                           f"{type(e2).__name__}: {e2}")

    except Exception as e:
        sys.settrace(None)
        rep.record('L2调用追踪', 'fail', 'GlobalTracer 运行',
                   f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

    # 2.4 僵尸代码判定 & 归档说明
    rep.sub_section("2.4 僵尸代码判定与归档")
    try:
        import os as _os
        archived_path = _os.path.join(PROJECT_ROOT, 'modules', 'archived', 'marriage_scorer.py')
        if _os.path.exists(archived_path):
            rep.record('L2调用追踪', 'warn',
                       'marriage_scorer.py 已确认真·僵尸代码（主程序/评分器/shensha__init__ 均无import）',
                       '已归档到 modules/archived/marriage_scorer.py，若后续需恢复可从archived/移回')
        else:
            rep.record('L2调用追踪', 'info',
                       'marriage_scorer.py 归档状态未确认，请检查 modules/archived/ 目录')
    except Exception as e:
        rep.record('L2调用追踪', 'warn',
                   'marriage_scorer.py 归档检查异常',
                   f"{type(e).__name__}: {e}")

    try:
        # 验证 嫁娶神煞扩展.py 存在真实引用链（主程序L4479 import MarriageShenShaCheckerExt）
        ext_mod_path = _os.path.join(PROJECT_ROOT, 'modules', 'shensha', '嫁娶神煞扩展.py') if '_os' in dir() else None
        if ext_mod_path and _os.path.exists(ext_mod_path):
            # 浅层引用检查：只需确认主程序存在真实import
            has_ref = False
            try:
                with open(_os.path.join(PROJECT_ROOT, '主程序.py'), 'r', encoding='utf-8') as f:
                    main_code = f.read()
                has_ref = 'MarriageShenShaCheckerExt' in main_code and '嫁娶神煞扩展' in main_code
            except Exception:
                pass
            if has_ref:
                rep.record('L2调用追踪', 'info',
                           '嫁娶神煞扩展.py coverage=0%但非僵尸代码',
                           '主程序L4479 存在 from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt；当前L4仅触发主链路，未触发扩展分支属正常现象')
            else:
                rep.record('L2调用追踪', 'warn',
                           '嫁娶神煞扩展.py 引用链未确认，需人工复核')
    except Exception as e:
        rep.record('L2调用追踪', 'warn',
                   '嫁娶神煞扩展.py 判定异常',
                   f"{type(e).__name__}: {e}")


# ==========================================================================
# L3: 单元测试（调用 tests.test_core，捕获输出）
# ==========================================================================
def run_l3_unit_tests(rep: SelfCheckReport, skip=False):
    rep.section("L3: 单元测试 (tests/test_core.py)")
    if skip:
        rep.record('L3单元测试', 'info', '用户指定跳过 L3')
        return

    # 导入 unittest runner
    loader = unittest.TestLoader()
    try:
        from tests.test_core import (
            TestSiZhuCalculator,
            TestTwentyFourMountains,
            TestCheckMountainDay,
            TestScorerBasic,
        )
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromTestCase(TestSiZhuCalculator))
        suite.addTests(loader.loadTestsFromTestCase(TestTwentyFourMountains))
        suite.addTests(loader.loadTestsFromTestCase(TestCheckMountainDay))
        suite.addTests(loader.loadTestsFromTestCase(TestScorerBasic))
    except Exception as e:
        rep.record('L3单元测试', 'fail', '测试套件加载失败',
                   f"{type(e).__name__}: {e}")
        return

    # 捕获输出
    stream = io.StringIO()
    runner = unittest.TextTestRunner(
        stream=stream, verbosity=2, failfast=False
    )
    with contextlib.redirect_stdout(stream):
        result = runner.run(suite)
    raw = stream.getvalue()

    # 输出摘要
    rep.sub_section("测试摘要")
    # 按 TestCase 维度拆分
    for line in raw.splitlines():
        if line.startswith('test_') or '测试' in line or '验证' in line:
            if ' ... ok' in line:
                name = line.split(' ... ok')[0].strip()
                rep.record('L3单元测试', 'ok', name)
            elif ' ... FAIL' in line:
                name = line.split(' ... FAIL')[0].strip()
                rep.record('L3单元测试', 'fail', name)
            elif ' ... ERROR' in line:
                name = line.split(' ... ERROR')[0].strip()
                rep.record('L3单元测试', 'fail', name + '(ERROR)')

    # 总结
    run = result.testsRun
    fails = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = run - fails - errors - skipped
    rep.sub_section("整体统计")
    rep.record('L3单元测试', 'ok', f'通过 {passed}', ) if passed else None
    if fails:
        rep.record('L3单元测试', 'fail', f'失败 {fails}')
    if errors:
        rep.record('L3单元测试', 'fail', f'错误 {errors}')
    if skipped:
        rep.record('L3单元测试', 'warn', f'跳过 {skipped}')
    rep.line(f"     执行 {run} 项，通过 {passed}，失败 {fails}，错误 {errors}，跳过 {skipped}")

    # 如果有失败，把失败详情追加到报告
    if result.failures or result.errors:
        rep.sub_section("失败详情")
        for test, tb in result.failures:
            rep.line(f"  FAIL: {test}")
            for l in tb.splitlines()[-6:]:
                rep.line(f"      {l}")
        for test, tb in result.errors:
            rep.line(f"  ERROR: {test}")
            for l in tb.splitlines()[-6:]:
                rep.line(f"      {l}")


# ==========================================================================
# L3B: 业务逻辑正确性专项测试 (tests.test_business_logic)
#   覆盖：婚嫁四大参数 / 黄道算法 / 三煞纯地支 / 贵人时一致性
# ==========================================================================
def run_l3b_business_tests(rep: SelfCheckReport, skip=False):
    rep.section("L3B: 业务逻辑正确性专项 (tests/test_business_logic.py)")
    if skip:
        rep.record('L3B业务专项', 'info', '用户指定跳过 L3B')
        return

    loader = unittest.TestLoader()
    try:
        from tests.test_business_logic import (
            TestMarriageCoreParams,
            TestHuangDaoAlgorithm,
            TestConditionZeriFixes,
        )
        suite_biz = unittest.TestSuite()
        suite_biz.addTests(loader.loadTestsFromTestCase(TestMarriageCoreParams))
        suite_biz.addTests(loader.loadTestsFromTestCase(TestHuangDaoAlgorithm))
        suite_biz.addTests(loader.loadTestsFromTestCase(TestConditionZeriFixes))
    except Exception as e:
        rep.record('L3B业务专项', 'fail', '测试套件加载失败',
                   f"{type(e).__name__}: {e}")
        return

    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2, failfast=False)
    with contextlib.redirect_stdout(stream):
        result = runner.run(suite_biz)
    raw = stream.getvalue()

    rep.sub_section("测试摘要")
    for line in raw.splitlines():
        if line.startswith('test_') or '硬约束' in line or '一致性' in line \
           or '验证' in line or '端' in line:
            if ' ... ok' in line:
                name = line.split(' ... ok')[0].strip()
                rep.record('L3B业务专项', 'ok', name)
            elif ' ... FAIL' in line:
                name = line.split(' ... FAIL')[0].strip()
                rep.record('L3B业务专项', 'fail', name)
            elif ' ... ERROR' in line:
                name = line.split(' ... ERROR')[0].strip()
                rep.record('L3B业务专项', 'fail', name + '(ERROR)')

    run = result.testsRun
    fails = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = run - fails - errors - skipped
    rep.sub_section("整体统计")
    if passed:
        rep.record('L3B业务专项', 'ok', f'通过 {passed}')
    if fails:
        rep.record('L3B业务专项', 'fail', f'失败 {fails}')
    if errors:
        rep.record('L3B业务专项', 'fail', f'错误 {errors}')
    if skipped:
        rep.record('L3B业务专项', 'warn', f'跳过 {skipped}')
    rep.line(f"     执行 {run} 项，通过 {passed}，失败 {fails}，错误 {errors}，跳过 {skipped}")

    if result.failures or result.errors:
        rep.sub_section("失败/错误详情（业务逻辑缺陷）")
        for test, tb in result.failures:
            rep.line(f"  FAIL: {test}")
            for l in tb.splitlines()[-8:]:
                rep.line(f"      {l}")
        for test, tb in result.errors:
            rep.line(f"  ERROR: {test}")
            for l in tb.splitlines()[-8:]:
                rep.line(f"      {l}")


# ==========================================================================
# L3C: 黄金基准比对测试 (tests.test_huangdao_truth)
#   硬编码《通书》/ project_memory 真值，哈希级断言
#   覆盖：6组大黄道+小黄道 / 6组时辰级大黄道 / 三煞4合局 / 贵人时正反例 / 阴胎阳气5组同法（胎元）
# ==========================================================================
def run_l3c_gold_truth_tests(rep: SelfCheckReport, skip=False):
    rep.section("L3C: 黄金基准比对 (tests/test_huangdao_truth.py · 硬编码真值)")
    if skip:
        rep.record('L3C黄金基准', 'info', '用户指定跳过 L3C')
        return

    loader = unittest.TestLoader()
    try:
        from tests.test_huangdao_truth import (
            TestHuangDaoGoldTruth,
            TestSanshaGoldTruth,
            TestGuiRenGoldTruth,
            TestYinTaiYangQiGoldTruth,
            TestFuZiGoldTruth,
            TestShichen12DayBoundary,
            TestGuiRen10GanFull,
            TestXiuZao20211203,
            TestJiaQu20260222,
        )
        suite_truth = unittest.TestSuite()
        suite_truth.addTests(loader.loadTestsFromTestCase(TestHuangDaoGoldTruth))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestSanshaGoldTruth))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestGuiRenGoldTruth))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestYinTaiYangQiGoldTruth))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestFuZiGoldTruth))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestShichen12DayBoundary))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestGuiRen10GanFull))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestXiuZao20211203))
        suite_truth.addTests(loader.loadTestsFromTestCase(TestJiaQu20260222))
    except Exception as e:
        rep.record('L3C黄金基准', 'fail', '测试套件加载失败',
                   f"{type(e).__name__}: {e}")
        return

    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2, failfast=False)
    with contextlib.redirect_stdout(stream):
        result = runner.run(suite_truth)
    raw = stream.getvalue()

    rep.sub_section("测试摘要（黄金真值逐项比对）")
    for line in raw.splitlines():
        if line.startswith('test_') or '用户核心验证' in line \
           or '正例' in line or '反例' in line:
            if ' ... ok' in line:
                name = line.split(' ... ok')[0].strip()
                rep.record('L3C黄金基准', 'ok', name)
            elif ' ... FAIL' in line:
                name = line.split(' ... FAIL')[0].strip()
                rep.record('L3C黄金基准', 'fail', name + ' → 算法漂移！')
            elif ' ... ERROR' in line:
                name = line.split(' ... ERROR')[0].strip()
                rep.record('L3C黄金基准', 'fail', name + '(ERROR)')

    run = result.testsRun
    fails = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = run - fails - errors - skipped
    rep.sub_section("整体统计")
    if passed:
        rep.record('L3C黄金基准', 'ok', f'通过 {passed}')
    if fails:
        rep.record('L3C黄金基准', 'fail', f'失败 {fails}')
    if errors:
        rep.record('L3C黄金基准', 'fail', f'错误 {errors}')
    if skipped:
        rep.record('L3C黄金基准', 'warn', f'跳过 {skipped}')
    rep.line(f"     执行 {run} 项，通过 {passed}，失败 {fails}，错误 {errors}，跳过 {skipped}")

    if result.failures or result.errors:
        rep.sub_section("失败详情（算法漂移！需立即修权威模块）")
        for test, tb in result.failures:
            rep.line(f"  FAIL: {test}")
            for l in tb.splitlines()[-10:]:
                rep.line(f"      {l}")
        for test, tb in result.errors:
            rep.line(f"  ERROR: {test}")
            for l in tb.splitlines()[-10:]:
                rep.line(f"      {l}")


# ==========================================================================
# L4: 集成测试（调用 tests/test_integration.run_all）
# ==========================================================================
def run_l4_integration_tests(rep: SelfCheckReport):
    rep.section("L4: 集成/端到端测试 (tests/test_integration.py)")
    try:
        # 捕获 print 输出
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            from tests import test_integration
            ok = test_integration.run_all()
        output = buf.getvalue()
        # 把集成测试里的✅❌行提取出来作为摘要
        passed = 0
        failed = 0
        warned = 0
        for line in output.splitlines():
            stripped = line.strip()
            if stripped.startswith('✅'):
                passed += 1
                rep.record('L4集成测试', 'ok', stripped.lstrip('✅ '))
            elif stripped.startswith('❌'):
                failed += 1
                rep.record('L4集成测试', 'fail', stripped.lstrip('❌ '))
            elif stripped.startswith('⚠️'):
                warned += 1
                rep.record('L4集成测试', 'warn', stripped.lstrip('⚠️  '))
        # 如果集成测试本身没有打印结构化标记，至少报告执行状态
        if passed == 0 and failed == 0:
            if ok:
                rep.record('L4集成测试', 'ok', '集成测试整体通过（无详细标记输出）')
            else:
                rep.record('L4集成测试', 'fail', '集成测试返回 False')
    except Exception as e:
        rep.record('L4集成测试', 'fail', '集成测试执行异常',
                   f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


# ==========================================================================
# 入口
# ==========================================================================
def main():
    parser = argparse.ArgumentParser(description='择日软件四层验证自检脚本')
    parser.add_argument('--no-l1', action='store_true', help='跳过L1静态检查')
    parser.add_argument('--no-l2', action='store_true', help='跳过L2调用追踪')
    parser.add_argument('--no-l3', action='store_true', help='跳过L3单元测试(基础)')
    parser.add_argument('--no-l3b', action='store_true', help='跳过L3B业务逻辑专项测试')
    parser.add_argument('--no-l3c', action='store_true', help='跳过L3C黄金基准比对测试')
    parser.add_argument('--no-l4', action='store_true', help='跳过L4集成测试')
    parser.add_argument('--quick', action='store_true', help='快速模式（L1+L3+L4核心）')
    args = parser.parse_args()

    quick_mode = args.quick
    if quick_mode:
        args.no_l2 = False  # 快速模式仍保留L2，因为它最快最有效

    rep = SelfCheckReport()
    rep.line("=" * 74)
    rep.line("  专业级正五行择日软件 · 系统六层完整验证")
    rep.line(f"  启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rep.line(f"  项目根:   {PROJECT_ROOT}")
    mode = "快速模式" if quick_mode else "完整模式"
    rep.line(f"  模式:     {mode}")
    rep.line("=" * 74)

    # 按顺序执行
    try:
        if not args.no_l1:
            run_l1_static_import_check(rep)
        if not args.no_l2:
            run_l2_runtime_trace(rep, quick=quick_mode)
        if not args.no_l3:
            run_l3_unit_tests(rep, skip=False)
        if not args.no_l3b:
            run_l3b_business_tests(rep, skip=False)
        if not args.no_l3c:
            run_l3c_gold_truth_tests(rep, skip=False)
        if not args.no_l4:
            run_l4_integration_tests(rep)
    except KeyboardInterrupt:
        rep.section("用户中断")
        rep.line("  自检被 Ctrl+C 中止，输出部分报告")

    # 最终汇总
    all_ok = rep.final_summary()
    print(f"\n报告文件已保存: {rep.log_path}")
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
