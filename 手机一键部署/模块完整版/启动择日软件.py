# -*- coding: utf-8 -*-
"""
启动脚本 - 运行专业级正五行择日软件
支持非交互式环境（手机）
"""
import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加当前目录到 Python 路径
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 检查并提示安装依赖
def check_dependencies():
    """检查必要的依赖库"""
    missing = []

    try:
        import tkinter
    except ImportError:
        missing.append('tkinter')

    try:
        import sxtwl
    except ImportError:
        missing.append('sxtwl (农历转换库)')

    if missing:
        print("=" * 50)
        print("警告：缺少以下依赖库：")
        for lib in missing:
            print(f"  - {lib}")
        print("=" * 50)
        print("请先安装缺失的库再运行程序")
        print()
        return False
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("专业级正五行择日软件")
    print("=" * 50)
    print()

    # 检查依赖
    if not check_dependencies():
        return

    # 检查 modules 目录
    modules_dir = os.path.join(current_dir, 'modules')
    if not os.path.exists(modules_dir):
        print("错误：找不到 modules 文件夹！")
        print(f"请确保 {modules_dir} 存在")
        return

    # 运行主程序
    try:
        from 主程序 import ZeriApp
        import tkinter as tk

        root = tk.Tk()
        app = ZeriApp(root)
        root.mainloop()
    except Exception as e:
        print(f"运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
