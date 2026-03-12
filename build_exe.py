# -*- coding: utf-8 -*-
"""
================================================================================
打包脚本 - 专业级正五行择日软件
================================================================================
使用 PyInstaller 打包应用程序为独立的可执行文件

使用方法:
    python build_exe.py

可选参数:
    --clean     清理之前的构建文件
    --onedir    创建单目录版本（默认单文件）
    --debug     启用调试模式
    
注意:
    PyInstaller 不支持 Python 3.13+，本脚本会自动检测并使用
    兼容的 Python 版本（3.11 或 3.12）进行打包。
================================================================================
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


SUPPORTED_PYTHON_VERSIONS = ['3.11', '3.12', '3.10']


def find_compatible_python():
    """
    查找兼容 PyInstaller 的 Python 版本
    
    Returns:
        str: 兼容的 Python 可执行文件路径，如果找不到则返回 None
    """
    print("检测可用的 Python 版本...")
    
    try:
        result = subprocess.run(
            ['py', '-0'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        installed_versions = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line.startswith('-V:'):
                parts = line.split()
                if parts:
                    version_str = parts[0].replace('-V:', '')
                    if version_str.endswith('*'):
                        version_str = version_str[:-1]
                    installed_versions.append(version_str)
        
        print(f"  已安装的 Python 版本: {', '.join(installed_versions)}")
        
        for supported in SUPPORTED_PYTHON_VERSIONS:
            for installed in installed_versions:
                if installed.startswith(supported):
                    try:
                        check_result = subprocess.run(
                            ['py', f'-{installed}', '-c', 'import sys; print(sys.executable)'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if check_result.returncode == 0:
                            python_path = check_result.stdout.strip()
                            print(f"  ✓ 选择 Python {installed}: {python_path}")
                            return f'py -{installed}'
                    except Exception:
                        continue
        
        return None
        
    except Exception as e:
        print(f"  检测 Python 版本时出错: {e}")
        return None


def check_dependencies(python_cmd=None):
    """检查依赖是否安装"""
    print("检查依赖...")
    
    required_packages = [
        ('PyInstaller', 'pyinstaller'),
        ('lunar_python', 'lunar_python'),
        ('loguru', 'loguru'),
    ]
    
    if python_cmd:
        check_cmd = python_cmd.split() + ['-c', 'import sys; import importlib; [importlib.import_module(sys.argv[1]) if len(sys.argv) > 1 else None]']
    
    missing = []
    for import_name, display_name in required_packages:
        try:
            if python_cmd:
                result = subprocess.run(
                    python_cmd.split() + ['-c', f'import {import_name}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    raise ImportError()
            else:
                __import__(import_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            missing.append(display_name)
            print(f"  ✗ {display_name} (未安装)")
    
    if missing:
        pip_cmd = f"{python_cmd} -m pip" if python_cmd else "pip"
        print(f"\n缺少以下依赖，请先安装:")
        print(f"  {pip_cmd} install {' '.join(missing)}")
        return False
    
    print("所有依赖已安装\n")
    return True


def clean_build():
    """清理构建文件"""
    print("正在清理构建文件...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.spec', '*.pyc', '*.pyo']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  已删除: {dir_name}/")
            except Exception as e:
                print(f"  删除失败 {dir_name}/: {e}")
    
    for pattern in files_to_remove:
        for file_path in Path('.').glob(pattern):
            try:
                file_path.unlink()
                print(f"  已删除: {file_path}")
            except Exception as e:
                print(f"  删除失败 {file_path}: {e}")
    
    for pycache in Path('.').rglob('__pycache__'):
        try:
            shutil.rmtree(pycache)
            print(f"  已删除: {pycache}")
        except Exception as e:
            pass
    
    print("清理完成\n")


def run_tests(python_cmd=None):
    """运行测试确保程序正常"""
    print("运行测试...")
    
    cmd = python_cmd.split() if python_cmd else [sys.executable]
    cmd.extend(['run_tests.py', '--sizhu'])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("  ✓ 测试通过\n")
            return True
        else:
            print("  ✗ 测试失败")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"  测试运行出错: {e}")
        return False


def build_executable(python_cmd=None, on_dir=False, debug=False):
    """构建可执行文件"""
    print("开始打包...")
    
    spec_file = '专业级正五行择日软件.spec'
    
    cmd = python_cmd.split() if python_cmd else [sys.executable]
    cmd.extend(['-m', 'PyInstaller', spec_file, '--clean'])
    
    if debug:
        cmd.append('--debug=all')
    
    print(f"运行命令: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✓ 打包成功!")
            return True
        else:
            print("\n✗ 打包失败")
            return False
            
    except Exception as e:
        print(f"\n打包出错: {e}")
        return False


def show_result():
    """显示打包结果"""
    print("\n" + "="*60)
    print("打包结果")
    print("="*60)
    
    exe_path = Path('dist') / '专业级正五行择日软件.exe'
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"可执行文件: {exe_path.absolute()}")
        print(f"文件大小: {size_mb:.2f} MB")
        print("\n使用说明:")
        print("  1. 将 exe 文件复制到任意位置")
        print("  2. 双击运行即可，无需安装 Python")
        print("  3. 首次启动可能需要几秒钟")
    else:
        print("未找到生成的可执行文件")
        print("请检查打包日志了解详情")
    
    print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='打包专业级正五行择日软件')
    parser.add_argument('--clean', action='store_true', help='清理构建文件')
    parser.add_argument('--onedir', action='store_true', help='创建单目录版本')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--skip-tests', action='store_true', help='跳过测试')
    parser.add_argument('--python', type=str, help='指定 Python 版本 (如 3.11)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("专业级正五行择日软件 - 打包工具")
    print("="*60 + "\n")
    
    python_cmd = None
    
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if current_version in SUPPORTED_PYTHON_VERSIONS:
        print(f"当前 Python 版本 {current_version} 支持 PyInstaller\n")
    else:
        print(f"当前 Python 版本 {current_version} 不支持 PyInstaller")
        print(f"支持的版本: {', '.join(SUPPORTED_PYTHON_VERSIONS)}\n")
        
        python_cmd = find_compatible_python()
        
        if args.python:
            python_cmd = f'py -{args.python}'
            print(f"使用指定的 Python 版本: {args.python}\n")
        elif not python_cmd:
            print("错误: 未找到兼容的 Python 版本")
            print(f"请安装 Python {' 或 '.join(SUPPORTED_PYTHON_VERSIONS)} 并安装依赖:")
            print(f"  py -3.11 -m pip install pyinstaller lunar_python loguru")
            sys.exit(1)
    
    if args.clean:
        clean_build()
    
    if not check_dependencies(python_cmd):
        sys.exit(1)
    
    if not args.skip_tests:
        if not run_tests(python_cmd):
            print("\n警告: 测试未通过，建议修复问题后再打包")
            response = input("是否继续打包? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    if build_executable(python_cmd, on_dir=args.onedir, debug=args.debug):
        show_result()
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
