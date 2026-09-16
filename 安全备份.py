# -*- coding: utf-8 -*-
"""
================================================================================
安全备份脚本（防自引用嵌套）
================================================================================
用法：
    python 安全备份.py                # 备份整个项目
    python 安全备份.py 主程序.py modules   # 只备份指定的子目录/文件（相对项目根）

为什么不会再出现 "备份\\完整系统备份_xxx\\备份\\..." 的无限嵌套：
1. 【物理隔离】备份目标建在【项目父目录】下的 "_项目备份" 区，
   与被备份项目平级、绝不在项目目录内部 —— 从根上杜绝 copytree 把自己复制进去。
2. 【断言拦截】启动时校验：若备份目标落在项目目录树内，立即报错中止，不执行。
3. 【枚举排除】复制时强制跳过 备份/backup/__pycache__/build/dist/.git/logs 等目录，
   即使将来手工改了目标位置也是双保险。
4. 【失败即报】任何复制错误都收集并打印，绝不静默吞错后谎称完成。

旧事故根因：手动在资源管理器里"复制整个项目文件夹（其内部已含'备份'子目录）
再粘贴进'备份'文件夹"，反复进行导致自引用嵌套、路径超 260 字符无法删除。
今后请一律用本脚本备份，不要手动整目录复制进项目内的"备份"文件夹。
================================================================================
"""

import os
import sys
import shutil
import datetime

# 项目根 = 本脚本所在目录（脚本复制到任意项目根都能自动定位）
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_NAME = os.path.basename(PROJECT_ROOT.rstrip('/\\'))

# 备份区：项目【父目录】下的 "_项目备份"（与项目平级，物理隔离，绝不嵌套进项目）
BACKUP_ROOT = os.path.join(os.path.dirname(PROJECT_ROOT), '_项目备份')

# 复制时一律排除的目录名（双保险，第 3 道防线）
EXCLUDE_DIR_NAMES = {'备份', 'backup', 'backups', '__pycache__', 'build', 'dist',
                     '.git', '.uploads', '.idea', '.vscode', 'logs', 'log',
                     '_项目备份'}
EXCLUDE_FILE_EXTS = {'.pyc', '.pyo'}


def _is_excluded_dir(name):
    """目录名是否应排除：命中黑名单，或名称里含'备份'/'backup'字样。"""
    low = name.lower()
    return (name in EXCLUDE_DIR_NAMES
            or '备份' in name
            or 'backup' in low)


def _ignore_func(directory, names):
    """shutil.copytree 的 ignore 回调：返回需跳过的文件/目录名集合。"""
    skipped = []
    for n in names:
        full = os.path.join(directory, n)
        if os.path.isdir(full):
            if _is_excluded_dir(n):
                skipped.append(n)
        elif os.path.splitext(n)[1].lower() in EXCLUDE_FILE_EXTS:
            skipped.append(n)
    return skipped


def main():
    targets = sys.argv[1:] or ['.']  # 默认备份整个项目
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dst_base = os.path.join(BACKUP_ROOT, PROJECT_NAME + '_' + stamp)

    # ---- 第 2 道防线：断言备份目标不在项目目录树内 ----
    try:
        common = os.path.commonpath([os.path.abspath(dst_base), PROJECT_ROOT])
    except ValueError:
        common = ''
    if os.path.normpath(common) == os.path.normpath(PROJECT_ROOT):
        print('✗ 安全拦截：备份目标位于项目目录内部，会造成自引用嵌套，已中止。')
        print('  项目根：%s' % PROJECT_ROOT)
        print('  目标  ：%s' % dst_base)
        return 1

    os.makedirs(dst_base, exist_ok=False)
    print('=' * 60)
    print('项目：%s' % PROJECT_NAME)
    print('备份到（项目外，物理隔离）：%s' % dst_base)
    print('=' * 60)

    errors = []
    ok = 0
    for rel in targets:
        src = os.path.normpath(os.path.join(PROJECT_ROOT, rel))
        dst = os.path.normpath(os.path.join(dst_base, rel))
        # 额外防护：源路径不允许指向项目外（防止误传 ../../）
        if os.path.normpath(os.path.commonpath([src, PROJECT_ROOT])) != os.path.normpath(PROJECT_ROOT):
            errors.append('源路径超出项目范围，已跳过: %s' % rel)
            continue
        if not os.path.exists(src):
            errors.append('源不存在: %s' % rel)
            continue
        try:
            if os.path.isdir(src):
                os.makedirs(dst, exist_ok=True)
                shutil.copytree(src, dst, dirs_exist_ok=True, ignore=_ignore_func)
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
            print('✓ 已备份: %s' % rel)
            ok += 1
        except Exception as e:
            errors.append('%s -> %s' % (rel, str(e)[:150]))

    print('-' * 60)
    if errors:
        print('✗ 完成，但有 %d 项失败（成功 %d 项）：' % (len(errors), ok))
        for e in errors:
            print('  - ' + e)
        print('\n请勿把失败当作成功；修复后重新运行本脚本即可。')
        return 2
    print('✓ 全部完成：成功 %d 项' % ok)
    print('备份位置：%s' % dst_base)
    return 0


if __name__ == '__main__':
    sys.exit(main())
