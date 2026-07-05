# -*- coding: utf-8 -*-
"""
================================================================================
PyInstaller 打包配置文件
================================================================================
使用方法:
    1. 安装PyInstaller: pip install pyinstaller
    2. 执行打包: pyinstaller 优版五行择日.spec
       或 python build_exe.py
================================================================================
"""

import os
import sys
import PyInstaller.__main__

# 项目路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_PATH = os.path.join(PROJECT_ROOT, 'dist')
BUILD_PATH = os.path.join(PROJECT_ROOT, 'build')

def build_exe():
    """构建EXE文件"""
    print("=" * 60)
    print("正在构建 EXE 文件: 优版五行择日")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs(DIST_PATH, exist_ok=True)
    os.makedirs(BUILD_PATH, exist_ok=True)
    
    # PyInstaller 参数
    args = [
        os.path.join(PROJECT_ROOT, '主程序.py'),  # 主程序路径
        '--name=优版五行择日',                      # 输出文件名
        '--onedir',                                # 打包为文件夹模式
        '--windowed',                              # Windows窗口模式（无控制台）
        '--icon=NONE',                             # 无图标（避免图标问题）
        '--clean',                                 # 清理临时文件
        f'--distpath={DIST_PATH}',                # 输出目录
        f'--workpath={BUILD_PATH}',               # 构建目录
        '--noconfirm',                            # 覆盖已存在的文件
        
        # 添加数据文件
        '--add-data=modules;modules',             # modules目录
        '--add-data=images;images',               # images目录（如果存在）
        '--add-data=sounds;sounds',               # sounds目录（如果存在）
        
        # 隐藏模块（排除不需要的）
        '--exclude-module=tkinter',
        '--exclude-module=logging',
        
        # 优化
        '--optimize=2',
    ]
    
    # 检查images目录是否存在
    images_path = os.path.join(PROJECT_ROOT, 'images')
    if not os.path.exists(images_path):
        print("注意: images 目录不存在，将跳过")
        args = [a for a in args if not a.startswith('--add-data=images')]
    
    # 检查sounds目录是否存在
    sounds_path = os.path.join(PROJECT_ROOT, 'sounds')
    if not os.path.exists(sounds_path):
        print("注意: sounds 目录不存在，将跳过")
        args = [a for a in args if not a.startswith('--add-data=sounds')]
    
    print(f"主程序: {os.path.join(PROJECT_ROOT, '主程序.py')}")
    print(f"输出目录: {DIST_PATH}")
    print()
    
    # 执行打包
    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 60)
        print("✓ 打包完成!")
        print(f"✓ EXE 文件位置: {os.path.join(DIST_PATH, '优版五行择日', '优版五行择日.exe')}")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 打包失败: {e}")
        print("=" * 60)
        return False
    
    return True

if __name__ == '__main__':
    build_exe()
