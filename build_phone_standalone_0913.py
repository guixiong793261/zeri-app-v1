# -*- coding: utf-8 -*-
"""
玄空飞星手机独立版构建器（内联 4 模块）

将 modules/ 中 4 个模块（工具函数、高精度农历转换、四柱计算器、玄空飞星引擎）
内联进 .玄空飞星_日课展示手机版.py，前导与 GUI 主体保持不变。

原理：
- 读取现有产物，按 `# 【内联模块】{name}` 标记切出前导 / 4 模块段 / GUI 主体；
- 用 modules/ 中 4 模块的新鲜源码（经 import 处理）替换 4 段；
- import 处理：注释掉指向 4 个内联模块的 try/except import 块（名称已全局化），
  非内联模块 import（真太阳时/八字分析工具/八字工具整合等）保持 try/except 兜底；
- 拼接写回产物。

用法：
    python build_phone_standalone_0913.py            # 生成产物
    python build_phone_standalone_0913.py --smoke    # 生成并冒烟验证（非 GUI）

退出码：0 成功 / 1 失败（可挂 CI）。
"""
import os
import re
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
MODDIR = os.path.join(ROOT, 'modules')
OUT_FILE = os.path.join(ROOT, '.玄空飞星_日课展示手机版.py')

# 内联的 4 个模块（顺序 = 拼接顺序 = 依赖顺序）
INLINED_MODULES = ['工具函数', '高精度农历转换', '四柱计算器', '玄空飞星引擎']
_INLINED_SET = set(INLINED_MODULES)

# 产物内联段标记
HEADER_RE = re.compile(r'# 【内联模块】(.+?)（构建自 modules/')
# GUI 主体起始标记（手机版特有，区别于桌面版）
GUI_MARKER = '#  GUI 界面 (手机自适应)'


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


# ---------------- 产物切分 ----------------

def split_product(text):
    """按 4 个内联模块标记切分 → (前导, {name: 段源码}, GUI主体)"""
    positions = []
    for m in HEADER_RE.finditer(text):
        name = m.group(1)
        if name in _INLINED_SET:
            positions.append((m.start(), name))
    if len(positions) != 4:
        fail(f'产物内联段数异常，期望 4 个，实际 {len(positions)}: '
             f'{[p[1] for p in positions]}')

    sections = {}
    preamble = text[:positions[0][0]]
    for i, (pos, name) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        sections[name] = text[pos:end]

    # 最后一段（玄空飞星引擎）= 模块源码 + GUI 主体，需在 GUI_MARKER 处切
    last_name = positions[-1][1]
    last_section = sections[last_name]
    gui_pos = last_section.find(GUI_MARKER)
    if gui_pos == -1:
        fail(f'产物中未找到 GUI 主体标记: {GUI_MARKER}')
    # GUI 主体从 GUI_MARKER 所在行的上一行 `# ====` 起
    line_start = last_section.rfind('\n', 0, gui_pos)
    sep_start = last_section.rfind('\n', 0, line_start)
    gui_body = last_section[sep_start:]
    sections[last_name] = last_section[:sep_start]
    return preamble, sections, gui_body


# ---------------- import 处理 ----------------

def _parse_import_names(lines, start_idx):
    """从 `from X import ...` 行解析导入的本地名列表（处理多行括号与 as 别名）。"""
    m = re.match(r'\s*from .+?\s+import\s+(.+)', lines[start_idx])
    rest = m.group(1) if m else ''
    if '(' in rest and ')' not in rest:
        k = start_idx + 1
        while k < len(lines) and ')' not in lines[k]:
            rest += ' ' + lines[k].strip()
            k += 1
        if k < len(lines):
            rest += ' ' + lines[k].strip()
    rest = rest.strip().strip('()').strip()
    names = []
    for part in rest.split(','):
        part = part.strip()
        if not part:
            continue
        if ' as ' in part:
            part = part.split(' as ')[-1].strip()
        names.append(part)
    return names


def process_imports(src):
    """处理内联模块间交叉 import 与非内联依赖的兜底。

    对 `try: from .{M} import ... except ImportError: from {M} import ...` 块：
    - M 属于 4 个内联模块 → 整段替换为注释（名称已全局化）
    - M 非内联 且 except 分支为 re-import → 保留 try，except 分支改为 stub 赋值
      （name = None），避免 ModuleNotFoundError 逃逸；手机 GUI 不触发这些路径
    - M 非内联 且 except 分支有真实兜底代码 → 原样保留
    """
    lines = src.split('\n')
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped == 'try:':
            indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < n and lines[j].strip() == '':
                j += 1
            target = None
            if j < n:
                m = (re.match(r'\s*from \.(.+?)\s+import', lines[j])
                     or re.match(r'\s*from (.+?)\s+import', lines[j]))
                if m:
                    target = m.group(1)
            if target is not None:
                # 找 except 行
                k = j + 1
                while k < n and not lines[k].strip().startswith(('except', 'finally')):
                    k += 1
                if k >= n:
                    out.append(' ' * indent
                               + f'# {target}已内联于本单文件前部（同名全局可直接使用）')
                    i = n
                    continue
                except_line = lines[k]
                except_indent = len(except_line) - len(except_line.lstrip())
                # except 体结束
                body_end = k + 1
                while body_end < n:
                    s = lines[body_end].strip()
                    if s == '':
                        body_end += 1
                        continue
                    cur_indent = (len(lines[body_end])
                                  - len(lines[body_end].lstrip()))
                    if cur_indent <= except_indent:
                        break
                    body_end += 1
                # 检查 except 体首条是否为 re-import
                ef = k + 1
                while ef < body_end and lines[ef].strip() == '':
                    ef += 1
                except_reimport = False
                if ef < body_end:
                    em = (re.match(r'\s*from \.(.+?)\s+import', lines[ef])
                          or re.match(r'\s*from (.+?)\s+import', lines[ef]))
                    if em:
                        except_reimport = True
                if target in _INLINED_SET:
                    out.append(' ' * indent
                               + f'# {target}已内联于本单文件前部（同名全局可直接使用）')
                elif except_reimport:
                    # 保留 try 块 + except 行，except 体改 stub
                    out.extend(lines[i:k + 1])
                    for nm in _parse_import_names(lines, j):
                        out.append(' ' * (except_indent + 4) + f'{nm} = None')
                else:
                    out.extend(lines[i:body_end])
                i = body_end
                continue
        out.append(line)
        i += 1
    return '\n'.join(out)


# ---------------- 测试块剥离 ----------------

def strip_test_blocks(src):
    """移除模块末尾的 `if __name__` 自测块。

    独立版以 __main__ 执行，模块内末尾的自测块会按拼接顺序提前运行，
    导致前向引用（如高精度农历转换测试块调用尚未内联的 calculate_sizhu）。
    仅剥离列 0 的 `if __name__` 起始块；四柱计算器顶部的路径设置块
    （`if __name__ == '__main__' and __package__ is None:`）因不是最后一个
    `if __name__` 而保留（无害）。
    """
    lines = src.split('\n')
    last_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('if __name__'):
            last_idx = i
    if last_idx == -1:
        return src
    return '\n'.join(lines[:last_idx]).rstrip() + '\n'


# ---------------- 模块特定修补 ----------------

# 内联合并全局命名空间后，模块间同名变量会互相覆盖。以下修补处理已知冲突：
# - 高精度农历转换: `from loguru import logger` 无兜底，手机端可能缺 loguru → 加兼容桩
# - 四柱计算器: `logger = logging.getLogger(__name__)` 会覆盖高精度农历转换的
#   loguru logger（后者用到 logger.remove()/add() 专有 API）→ 注释掉，沿用前者
_MODULE_PATCHES = {
    '高精度农历转换': [
        (re.compile(r'^from loguru import logger\s*$', re.MULTILINE),
         '''try:
    from loguru import logger
except ImportError:
    # 手机端可能无 loguru：注入最小兼容桩（农历模块用到 remove()/add() 等专有 API）
    import logging as _logging
    class _LoggerStub:
        def __init__(self):
            self._lg = _logging.getLogger("nongli")
        def remove(self):
            pass
        def add(self, *a, **k):
            return 0
        def __getattr__(self, name):
            return getattr(self._lg, name)
    logger = _LoggerStub()'''),
    ],
    '四柱计算器': [
        (re.compile(r'^logger = logging\.getLogger\(__name__\)\s*$', re.MULTILINE),
         '# logger 沿用农历转换块的 loguru/兼容桩实例（内联合并命名空间，勿覆盖）'),
    ],
}


def apply_module_patches(name, src):
    for pattern, replacement in _MODULE_PATCHES.get(name, []):
        src, n = pattern.subn(replacement, src)
        if n == 0:
            print(f'  [WARN] {name} 未匹配修补模式: {pattern.pattern}')
    return src


# ---------------- 段构建 ----------------

def build_module_section(name):
    """读取 modules/{name}.py，剥离自测块 + 处理 import + 模块修补，返回带头部段落"""
    path = os.path.join(MODDIR, name + '.py')
    if not os.path.exists(path):
        fail(f'modules 源文件不存在: {path}')
    with open(path, encoding='utf-8') as f:
        src = f.read()
    src = strip_test_blocks(src)
    src = process_imports(src)
    src = apply_module_patches(name, src)
    header = (
        f'# 【内联模块】{name}（构建自 modules/，勿手改；改算法请改 modules 后重新构建）\n'
        f'# ======================================================================\n\n'
    )
    return header + src


# ---------------- 冒烟段 ----------------

SMOKE_TAIL = '''
# ==== PHONE_SMOKE 验证段（--smoke 生成，替代 GUI 主块）====
import datetime as _dt
_sz = calculate_sizhu(_dt.date(2026, 2, 4), 12, 0)
assert isinstance(_sz, dict) and '年柱' in _sz and '丙' in _sz['年柱'], \\
    f"丙午年换柱断言失败: {_sz}"
_conv = get_lunar_converter()
assert _conv is not None, "get_lunar_converter 返回 None"
assert callable(score_feixing), "score_feixing 不可调用"
# 飞星评分端到端：壬山丙向 丙午年甲午月（2026-02-04 立春）
_fx = score_feixing(_sz, '壬山丙向')
assert _fx is not None, "score_feixing 返回 None"
print("PHONE_SMOKE_OK: 4模块内联 + calculate_sizhu + get_lunar_converter "
      "+ score_feixing 全通过")
sys.exit(0)
'''


def main(argv):
    smoke = '--smoke' in argv
    print('=' * 60)
    print('玄空飞星手机独立版构建器：内联 4 模块')
    print('=' * 60)

    if not os.path.exists(OUT_FILE):
        fail(f'产物不存在: {OUT_FILE}')

    with open(OUT_FILE, encoding='utf-8') as f:
        product = f.read()
    preamble, sections, gui_body = split_product(product)
    print(f'前导 {len(preamble)} 字节，GUI 主体 {len(gui_body)} 字节')

    new_sections = {}
    for name in INLINED_MODULES:
        new_sections[name] = build_module_section(name)
        print(f'  内联 {name}: {len(new_sections[name])} 字节')

    # 拼接
    content = preamble
    for name in INLINED_MODULES:
        content += new_sections[name]
    content += gui_body

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    size = os.path.getsize(OUT_FILE)
    print(f'\n[OK] 产物: {OUT_FILE}（{size:,} 字节）')

    # py_compile 校验
    import py_compile
    try:
        py_compile.compile(OUT_FILE, doraise=True)
    except py_compile.PyCompileError as e:
        fail(f'py_compile 失败: {e}')
    print('[OK] py_compile 通过')

    if smoke:
        # 截断最后的 if __name__ == '__main__' 主块，追加冒烟断言
        idx = content.rfind("if __name__ == '__main__':")
        if idx == -1:
            idx = content.rfind('if __name__ == "__main__":')
        if idx == -1:
            fail('产物中未找到 __main__ 主块，无法生成冒烟版')
        smoke_content = content[:idx] + SMOKE_TAIL
        smoke_path = OUT_FILE.replace('.py', '_smoke.py')
        with open(smoke_path, 'w', encoding='utf-8') as f:
            f.write(smoke_content)
        print('\n[SMOKE] 运行冒烟验证（4 模块全局名 + 端到端飞星评分）...')
        r = subprocess.run(
            [sys.executable, smoke_path],
            capture_output=True, text=True, timeout=180,
            cwd=os.path.dirname(OUT_FILE),
        )
        print(r.stdout[-2000:] if r.stdout else '(无 stdout)')
        if r.returncode != 0:
            print('--- stderr ---')
            print(r.stderr[-4000:])
            if os.path.exists(smoke_path):
                os.remove(smoke_path)
            fail(f'冒烟失败 rc={r.returncode}')
        if os.path.exists(smoke_path):
            os.remove(smoke_path)
        print('[SMOKE] 冒烟通过，临时产物已清理')
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
