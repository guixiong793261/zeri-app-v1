# -*- coding: utf-8 -*-
"""
单文件版整合脚本 v2（2026-09-22 重写）

旧版缺陷（本版根治）：
1. 手工 MODULES 列表永远过时——rules/shensha 检查器经事项标准.py 的
   importlib 派发表懒加载，静态清单根本列不全；
2. 纯文本拼接不处理 import——产物首行 `from modules.xxx import` 立即
   ModuleNotFoundError（旧产物实测启动即崩）。

v2 方案：
- 依赖双源动态发现：主程序静态 import 扫描 + 事项标准.py 派发表 AST 解析
  （RULE_CHECKER_CLASSES / SHENSHA_CHECKER_CLASSES / 兜底 / 修造扩展），
  再 BFS 静态依赖闭包 → 清单永不需手工维护；
- meta_path 内嵌加载：全部模块源码 zlib+base64 内嵌，sys.meta_path 拦截
  `modules.*` 的 import 交给原生导入机制（相对导入 / 循环依赖 /
  importlib 动态派发 / 部分初始化语义全兼容），主程序源码原样保留。

用法：
    python integrate_single_file.py            # 生成正式产物
    python integrate_single_file.py --smoke    # 生成冒烟验证版并运行（验证 import 链）
    python integrate_single_file.py --verify   # 生成正式产物并启动 6 秒验证 GUI

退出码：0 成功 / 1 失败（可挂 CI）。
"""
import ast
import base64
import os
import re
import subprocess
import sys
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
MODDIR = os.path.join(ROOT, 'modules')
MAIN_FILE = os.path.join(ROOT, '主程序.py')
STANDARD_FILE = os.path.join(MODDIR, '事项标准.py')
OUT_FILE = os.path.join(ROOT, '手机一键部署', '单文件版', '择日软件完整版.py')

# 不入包的明确排除：归档件与独立工具（无运行时引用，且校准工具顶层可能有写盘副作用）
EXCLUDE_DIRS = {'archived'}

RE_FROM_MODULES = re.compile(r'^\s*from\s+(modules(?:\.[\w\u4e00-\u9fff]+)+)\s+import', re.M)
RE_IMPORT_MODULES = re.compile(r'^\s*import\s+(modules(?:\.[\w\u4e00-\u9fff]+)+)', re.M)
RE_REL = re.compile(r'^\s*from\s+(\.+)([\w\u4e00-\u9fff]*)\s+import', re.M)
RE_BARE = re.compile(r'^\s*from\s+([\w\u4e00-\u9fff]+)\s+import', re.M)

# 派发表变量名（事项标准.py）——动态加载的检查器全部经此表，静态扫描抓不到
DISPATCH_VARS = (
    'RULE_CHECKER_CLASSES',      # rules 派发表
    'SHENSHA_CHECKER_CLASSES',   # shensha 派发表
    'GENERIC_RULE_CLASS',        # rules 通用兜底
    'GENERIC_SHENSHA_CLASS',     # shensha 通用兜底
    'CONSTRUCTION_SHENSHA_EXT_CLASS',  # 修造扩展（评分器显式使用）
)


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


# ---------------- 模块文件收集 ----------------

def collect_files():
    """rel -> abs；含三个包的 __init__.py；排除 archived/。"""
    files = {}
    for sub, dirs, fs in os.walk(MODDIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in fs:
            if f.endswith('.py'):
                abs_ = os.path.join(sub, f)
                rel = os.path.relpath(abs_, ROOT).replace('\\', '/')
                files[rel] = abs_
    return files


def rel_to_fullname(rel):
    """modules/__init__.py -> modules；modules/shensha/X.py -> modules.shensha.X"""
    stem = rel[:-3]  # 去 .py
    if stem.endswith('/__init__'):
        stem = stem[:-len('/__init__')]
    return stem.replace('/', '.')


# ---------------- 依赖解析 ----------------

def deps_of(rel, files, name2rel):
    """静态解析该模块依赖的 modules 相对路径列表（含双轨裸名兜底）。"""
    src = open(files[rel], encoding='utf-8').read()
    out = []
    here_parts = os.path.dirname(rel).split('/')

    for m in RE_FROM_MODULES.finditer(src):
        cand = m.group(1).replace('.', '/') + '.py'
        if cand in files:
            out.append(cand)
    for m in RE_IMPORT_MODULES.finditer(src):
        cand = m.group(1).replace('.', '/') + '.py'
        if cand in files:
            out.append(cand)
    for m in RE_REL.finditer(src):
        dots, name = m.group(1), m.group(2)
        base = here_parts[:len(here_parts) - (len(dots) - 1)]
        if name:
            cand = '/'.join(base) + f'/{name}.py'
            if cand in files:
                out.append(cand)
    for m in RE_BARE.finditer(src):
        for rel2 in name2rel.get(m.group(1), []):
            out.append(rel2)
    return sorted(set(out))


def parse_dispatch_table():
    """AST 解析事项标准.py 派发表 → 动态加载的模块相对路径列表。"""
    src = open(STANDARD_FILE, encoding='utf-8').read()
    tree = ast.parse(src)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in DISPATCH_VARS:
            var = node.targets[0].id
            try:
                found[var] = ast.literal_eval(node.value)
            except ValueError:
                fail(f'{var} 派发表含非常量表达式，无法静态解析')
    missing = [v for v in DISPATCH_VARS if v not in found]
    if missing:
        fail(f'事项标准.py 缺少派发表变量: {missing}')
    mods = set()
    for var in DISPATCH_VARS:
        table = found[var]
        # 值形如 ('.rules.嫁娶规则', 'Class') 或 {ev: ('.shensha.X', 'Class')}
        items = table.values() if isinstance(table, dict) else [table]
        for spec in items:
            path = spec[0]
            mods.add('modules/' + path.lstrip('.').replace('.', '/') + '.py')
    return sorted(mods)


def build_closure():
    """seeds = 主程序静态 import + 派发表动态模块；BFS 静态闭包。"""
    files = collect_files()
    name2rel = {}
    for rel in files:
        name2rel.setdefault(os.path.basename(rel)[:-3], []).append(rel)

    main_src = open(MAIN_FILE, encoding='utf-8').read()
    seeds = set()
    for m in RE_FROM_MODULES.finditer(main_src):
        cand = m.group(1).replace('.', '/') + '.py'
        if cand in files:
            seeds.add(cand)
    for m in RE_IMPORT_MODULES.finditer(main_src):
        cand = m.group(1).replace('.', '/') + '.py'
        if cand in files:
            seeds.add(cand)
    dyn = parse_dispatch_table()
    for rel in dyn:
        if rel not in files:
            fail(f'派发表引用不存在的模块: {rel}')
        seeds.add(rel)
    # 包 __init__ 必须入包（finder 以 package 形式加载）
    for pkg_init in ('modules/__init__.py', 'modules/shensha/__init__.py',
                     'modules/rules/__init__.py'):
        if pkg_init in files:
            seeds.add(pkg_init)

    from collections import deque
    order, seen, edges = [], set(), {}
    dq = deque(sorted(seeds))
    while dq:
        cur = dq.popleft()
        if cur in seen:
            continue
        seen.add(cur)
        order.append(cur)
        for d in deps_of(cur, files, name2rel):
            if d not in seen:
                dq.append(d)

    orphans = sorted(set(files) - seen)
    return files, order, edges, orphans, sorted(seeds)


# ---------------- 产物生成 ----------------

RUNNER_HEAD = '''# -*- coding: utf-8 -*-
# 【单文件版】由 integrate_single_file.py 自动生成（{gen_date}）——勿手改
# 原理：modules 包全部源码 zlib+base64 内嵌，sys.meta_path 拦截 import 交给
#       原生导入机制（相对导入/循环依赖/importlib 动态派发全兼容），
#       主程序源码原样保留于本文件尾部。内嵌模块共 {n_mods} 个。
import base64
import importlib.util
import sys
import zlib

_EMBED_B64 = {{
'''


def build_embed(files, order):
    chunks = [RUNNER_HEAD.format(
        gen_date=__import__('datetime').date.today().isoformat(),
        n_mods=len(order))]
    for rel in order:
        fullname = rel_to_fullname(rel)
        src = open(files[rel], 'rb').read()
        b64 = base64.b64encode(zlib.compress(src, 9)).decode('ascii')
        chunks.append(f"    {fullname!r}: {b64!r},\n")
    chunks.append(
        '''}

class _EmbedFinder:
    """内嵌包加载器：拦截 modules 及其子模块的 import，从 _EMBED_B64 加载。"""
    _PKGS = ('modules', 'modules.shensha', 'modules.rules')

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self._PKGS:
            spec = importlib.util.spec_from_loader(fullname, self, origin='<embed>')
            spec.submodule_search_locations = []
            return spec
        if fullname in _EMBED_B64:
            return importlib.util.spec_from_loader(fullname, self, origin='<embed>')
        return None

    def create_module(self, spec):
        return None  # 使用默认 ModuleType

    def exec_module(self, module):
        src = _EMBED_B64.get(module.__name__)
        if src is None:
            return  # namespace 式空包（真实 modules/ 无 __init__.py，行为一致）
        # 部分模块顶层引用 __file__（如 shensha 双轨 sys.path 套路），预置虚拟路径
        module.__dict__.setdefault(
            '__file__', '<embed>/' + module.__name__.replace('.', '/') + '.py')
        code = zlib.decompress(base64.b64decode(src))
        exec(compile(code, '<embed:%s>' % module.__name__, 'exec'), module.__dict__)

sys.meta_path.insert(0, _EmbedFinder())
''')
    return ''.join(chunks)


SMOKE_TAIL = '''

# ==== SMOKE 验证段（--smoke 生成，替代主程序）====
def _smoke():
    import datetime
    from modules.四柱计算器 import calculate_sizhu, get_lunar_date
    lun = get_lunar_date(datetime.date(2026, 2, 4))
    assert isinstance(lun.get('month'), str) and lun['month'], '农历月键异常'
    sz = calculate_sizhu(datetime.date(2026, 2, 4), 12, 0)
    blob = ' '.join(str(v) for v in sz.values()) if isinstance(sz, dict) else str(sz)
    assert '丙' in blob and '午' in blob, f'2026-02-04 立春换柱(丙午年)异常: {blob[:80]}'
    from modules.事项标准 import (RULE_CHECKER_CLASSES, SHENSHA_CHECKER_CLASSES,
                               get_rule_checker, get_shensha_checker)
    for ev in RULE_CHECKER_CLASSES:
        get_rule_checker(ev)
    for ev in SHENSHA_CHECKER_CLASSES:
        get_shensha_checker(ev)
    get_rule_checker('入学')      # rules 通用兜底
    get_shensha_checker('入学')   # shensha 通用兜底
    from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
    from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt
    from modules.评分器 import Scorer, calculate_score
    import modules.婚嫁评分算法  # noqa: F401
    import modules.日课评分系统  # noqa: F401
    import modules.玄空飞星引擎  # noqa: F401
    import modules.五行择日法  # noqa: F401
    import modules.二十四山择吉天机  # noqa: F401
    print('SMOKE_OK: 内嵌import链+动态派发({}+{}检查器)+立春换柱 全通过'.format(
        len(RULE_CHECKER_CLASSES), len(SHENSHA_CHECKER_CLASSES)))
    sys.exit(0)

_smoke()
'''


def main(argv):
    smoke = '--smoke' in argv
    verify = '--verify' in argv

    print('=' * 64)
    print('单文件版整合 v2：动态依赖发现 + meta_path 内嵌加载')
    print('=' * 64)

    files, order, edges, orphans, seeds = build_closure()
    if not order:
        fail('依赖闭包为空')
    print(f'\n主程序静态 seeds {len(seeds)} 个，派发表动态模块已并入')
    n_init = sum(1 for r in order if r.endswith('/__init__.py'))
    print(f'依赖闭包共 {len(order)} 个模块（含 {n_init} 个包 __init__）')
    print(f'未入包文件 {len(orphans)} 个: {", ".join(orphans) or "无"}')

    main_src = open(MAIN_FILE, encoding='utf-8').read()
    head = build_embed(files, order)

    if smoke:
        # smoke 版：嵌入段 + 替代性验证尾（不写主程序）
        content = head + SMOKE_TAIL
        smoke_path = OUT_FILE.replace('.py', '_smoke.py')
        os.makedirs(os.path.dirname(smoke_path), exist_ok=True)
        with open(smoke_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'\n[SMOKE] 冒烟产物: {smoke_path}')
        r = subprocess.run([sys.executable, smoke_path],
                           capture_output=True, text=True, timeout=120)
        print(r.stdout[-2000:] if r.stdout else '(无stdout)')
        if r.returncode != 0:
            print(r.stderr[-3000:])
            fail(f'冒烟验证失败 returncode={r.returncode}')
        os.remove(smoke_path)
        print('[SMOKE] 冒烟验证通过，临时产物已清理')
        sys.exit(0)

    # 正式产物：嵌入段 + 主程序源码原样
    content = head + '\n\n# ' + '=' * 39 + ' 主程序源码（原样） ' + '=' * 39 + '\n\n' + main_src
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    size = os.path.getsize(OUT_FILE)
    print(f'\n[OK] 产物: {OUT_FILE}（{size:,} 字节）')

    # py_compile 校验
    import py_compile
    try:
        py_compile.compile(OUT_FILE, doraise=True)
    except py_compile.PyCompileError as e:
        fail(f'产物语法校验失败: {e}')
    print('[OK] py_compile 语法校验通过')

    # 深度链路验证：冒烟（正式产物生成后仍以 smoke 全链路 import 验证一次）
    print('\n[VERIFY] 冒烟全链路验证（内嵌 import + 动态派发）...')
    smoke_content = head + SMOKE_TAIL
    smoke_path = OUT_FILE.replace('.py', '_smoke.py')
    with open(smoke_path, 'w', encoding='utf-8') as f:
        f.write(smoke_content)
    r = subprocess.run([sys.executable, smoke_path],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        os.remove(smoke_path)
        fail(f'冒烟验证失败 returncode={r.returncode}')
    print('  ' + (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''))
    os.remove(smoke_path)

    # GUI 启动验证
    if verify:
        print('\n[VERIFY] GUI 启动 6 秒验证...')
        err_f = open(os.path.join(os.environ.get('TEMP', '.'), '_sfile_gui_err.txt'),
                     'w', encoding='utf-8')
        p = subprocess.Popen([sys.executable, OUT_FILE], stdout=subprocess.DEVNULL,
                             stderr=err_f, cwd=os.path.dirname(OUT_FILE))
        try:
            rc = p.wait(timeout=6)
            err_f.close()
            err = open(err_f.name, encoding='utf-8').read()
            if 'Traceback' in err or rc != 0:
                print(err[-2000:])
                fail(f'GUI 提前退出 rc={rc}')
            print('  进程在 6 秒内退出且无 Traceback——GUI 短暂展示后关闭？人工确认')
        except subprocess.TimeoutExpired:
            p.kill()
            err_f.close()
            err = open(err_f.name, encoding='utf-8').read()
            if 'Traceback' in err:
                print(err[-2000:])
                fail('GUI 启动后 stderr 含 Traceback')
            print('  6 秒存活 + stderr 无 Traceback —— GUI 启动正常')
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
