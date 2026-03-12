# -*- coding: utf-8 -*-
"""
================================================================================
八字排盘独立运行脚本
================================================================================
单独运行八字排盘功能，无需通过主程序

使用方法：
1. 直接运行此脚本
2. 在弹出的对话框中输入出生信息和性别
3. 点击"开始排盘"查看详细八字分析
================================================================================
"""

import tkinter as tk
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.八字可视化模块 import show_bazi_input_dialog


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    root.title("八字排盘")
    root.geometry("200x100")
    
    # 居中显示
    root.update_idletasks()
    width = 200
    height = 100
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 创建启动按钮
    button = tk.Button(
        root, 
        text="开始八字排盘", 
        command=lambda: show_bazi_input_dialog(root),
        width=20,
        height=2
    )
    button.pack(pady=30)
    
    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()
