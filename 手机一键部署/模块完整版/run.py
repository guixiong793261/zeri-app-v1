# -*- coding: utf-8 -*-
# ASCII 文件名入口（run.py）
# 部分手机 Python IDE（如"Python编译器IDE"）的项目扫描器对中文文件名支持不佳，
# 用本文件作为入口：在 APP 内打开本文件点运行即可，功能与"启动择日软件.py"完全相同。
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def _check():
    missing = []
    try:
        import tkinter  # noqa: F401
    except ImportError:
        missing.append("tkinter（图形界面库）")
    try:
        import sxtwl  # noqa: F401
    except ImportError:
        missing.append("sxtwl（农历转换库）")
    if missing:
        print("=" * 50)
        print("缺少依赖，程序暂时无法启动：")
        for m in missing:
            print("  - " + m)
        print("请在本 APP 的【终端/Terminal】里执行：pip install sxtwl")
        print("（或在 APP 的模块/pip 管理界面里搜索 sxtwl 安装），装完重新运行 run.py")
        print("=" * 50)
        return False
    if not os.path.isdir(os.path.join(current_dir, "modules")):
        print("错误：找不到 modules 文件夹！")
        print("请把整个部署包完整解压/复制到同一文件夹后再运行 run.py。")
        print("当前目录：" + current_dir)
        return False
    if not os.path.exists(os.path.join(current_dir, "主程序.py")):
        print("错误：找不到 主程序.py，须与 run.py 放在同一文件夹。")
        print("当前目录：" + current_dir)
        return False
    return True


def main():
    print("=" * 50)
    print("专业级正五行择日软件")
    print("=" * 50)
    if not _check():
        return
    try:
        from 主程序 import ZeriApp
        import tkinter as tk
        root = tk.Tk()
        ZeriApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("运行错误：%s" % e)
        print("请将本屏全部内容截图反馈。")


if __name__ == "__main__":
    main()
