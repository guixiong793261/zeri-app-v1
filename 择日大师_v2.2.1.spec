# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
# 顶层模块通过 importlib.import_module('玄空飞星_日课展示') 动态加载，
# 静态分析抓不到，必须显式声明，否则 exe 报 No module named '玄空飞星_日课展示'
hiddenimports += ['玄空飞星_日课展示']
hiddenimports += collect_submodules('modules')


a = Analysis(
    ['主程序.py'],
    pathex=[],
    binaries=[],
    # v2.2.1：官方四份文档随 exe 内置，单文件复制到任意机器后「帮助」仍可打开
    datas=[
        ('docs/择日大师_完整说明书_v2.2.1.pdf', 'docs'),
        ('docs/择日大师_完整说明书_v2.2.1.docx', 'docs'),
        ('docs/择日大师_用户操作手册_v2.2.1.pdf', 'docs'),
        ('docs/择日大师_算法与典据白皮书_v2.2.1.pdf', 'docs'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='择日大师_v2.2.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['五行图标.ico'],
)
