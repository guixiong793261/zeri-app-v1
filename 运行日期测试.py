# -*- coding: utf-8 -*-
"""
日期测试窗口启动脚本
直接运行此文件来打开日期测试窗口
"""

if __name__ == "__main__":
    print("正在启动日期测试窗口...")
    
    try:
        from modules.日期测试窗口 import open_date_test_window
        open_date_test_window()
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        
    
        input("\n按回车键退出...")
