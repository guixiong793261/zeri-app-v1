# -*- coding: utf-8 -*-
"""
启动脚本 - 运行专业级正五行择日软件（手机 Pydroid 3 / 电脑通用）

================================================================
【手机上的正确打开方式】（务必按此操作，否则会提示"没有可执行的应用"）
1. 先在手机应用商店安装 Pydroid 3（Python IDE）；
2. 务必先把整个部署包【解压】到手机存储的某个文件夹
   （不能在微信/QQ/压缩包预览里直接点文件运行）；
3. 打开 Pydroid 3 → 右上角菜单(三横线) → Open（打开文件）→
   导航到解压后的文件夹，选择本文件「启动择日软件.py」→
   点底部黄色 ▶ 按钮运行。
   ⚠ 不要在手机"文件管理"里直接点击 .py 文件，也不要点 .bat
     （那是 Windows 批处理，安卓打不开，会提示"没有可执行的应用"）；
4. 首次运行若提示缺少 sxtwl（农历库）：
   Pydroid 菜单 → Terminal（终端），输入：pip install sxtwl
   （或菜单 → Pip → 搜索 sxtwl → Install），装完重新运行；
   tkinter 在 Pydroid 3 中已自带，无需安装。
================================================================
"""
import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加当前目录到 Python 路径
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def check_dependencies():
    """检查必要的依赖库，缺失时给出手机端可照做的安装步骤"""
    missing = []

    try:
        import tkinter  # noqa: F401
    except ImportError:
        missing.append('tkinter（图形界面库，Pydroid 3 一般自带；若缺失请更新 Pydroid 3）')

    try:
        import sxtwl  # noqa: F401
    except ImportError:
        missing.append('sxtwl（农历转换库）')

    if missing:
        print("=" * 50)
        print("警告：缺少以下依赖库，程序暂时无法启动：")
        for lib in missing:
            print(f"  - {lib}")
        print("=" * 50)
        print("手机 Pydroid 3 安装方法（二选一）：")
        print("  方法一：右上角菜单(三横线) → Terminal（终端），输入：")
        print("          pip install sxtwl")
        print("  方法二：菜单 → Pip → 搜索 sxtwl → 点 Install")
        print("安装完成后重新运行本文件（启动择日软件.py）即可。")
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
        print(f"当前查找位置：{modules_dir}")
        print("请确认整个部署包已【完整解压】在同一文件夹内（主程序.py 与 modules 文件夹同级）。")
        return

    # 检查主程序文件
    main_file = os.path.join(current_dir, '主程序.py')
    if not os.path.exists(main_file):
        print("错误：找不到 主程序.py！")
        print(f"当前查找位置：{main_file}")
        print("请确认整个部署包已完整解压，本启动脚本须与 主程序.py 放在同一文件夹。")
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
        print()
        print("如以上为手机端报错，请将本屏红字截图反馈，以便定位。")


if __name__ == '__main__':
    main()
