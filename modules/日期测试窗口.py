# -*- coding: utf-8 -*-
"""
日期测试窗口
用于测试日期计算和转换功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import date, datetime, timedelta
import sys
import os

# 添加项目根目录到路径（用于直接运行此文件）
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from modules.四柱计算器 import calculate_sizhu, analyze_sizhu, get_lunar_date


class DateTestWindow:
    """日期测试窗口"""
    
    def __init__(self, parent=None):
        """初始化"""
        if parent is None:
            self.window = tk.Tk()
            self.window.title("日期测试窗口")
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("日期测试窗口")
        
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置为屏幕的70%大小
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主滚动区域
        main_canvas = tk.Canvas(self.window)
        main_scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
        self.main_frame = ttk.Frame(main_canvas, padding="20")
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=self.window.winfo_screenwidth()-50)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 标题
        title_label = ttk.Label(self.main_frame, text="日期测试窗口", 
                               font=("微软雅黑", 20, "bold"))
        title_label.pack(pady=20)
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.main_frame, text="日期输入", padding="20")
        input_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # 日期输入
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(date_frame, text="测试日期 (YYYY-MM-DD):", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.date_entry = ttk.Entry(date_frame, width=20, font=("微软雅黑", 12))
        self.date_entry.pack(side=tk.LEFT, padx=10)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # 时间输入
        ttk.Label(date_frame, text="时间 (HH:MM):", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.time_entry = ttk.Entry(date_frame, width=10, font=("微软雅黑", 12))
        self.time_entry.pack(side=tk.LEFT, padx=10)
        self.time_entry.insert(0, "12:00")
        
        # 日期范围输入
        range_frame = ttk.Frame(input_frame)
        range_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(range_frame, text="开始日期:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.start_date_entry = ttk.Entry(range_frame, width=15, font=("微软雅黑", 12))
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        self.start_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        ttk.Label(range_frame, text="结束日期:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.end_date_entry = ttk.Entry(range_frame, width=15, font=("微软雅黑", 12))
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        
        # 默认结束日期为30天后
        end_date = date.today() + timedelta(days=30)
        self.end_date_entry.insert(0, end_date.strftime("%Y-%m-%d"))
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Button(button_frame, text="计算当前日期", command=self.calculate_current_date, width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="测试选定日期", command=self.calculate_selected_date, width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="测试日期范围", command=self.test_date_range, width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="清空结果", command=self.clear_results, width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="关闭", command=self.window.destroy, width=15).pack(side=tk.RIGHT, padx=8)
        
        # 结果显示区域（表格对比）
        result_frame = ttk.LabelFrame(self.main_frame, text="测试结果", padding="20")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # 创建表格框架
        table_frame = ttk.Frame(result_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        self.tree = ttk.Treeview(table_frame, columns=("date", "weekday", "lunar_calc", "lunar_auth", "sizhu_calc", "sizhu_auth", "result"), show="headings")
        
        # 设置列标题
        self.tree.heading("date", text="日期")
        self.tree.heading("weekday", text="星期")
        self.tree.heading("lunar_calc", text="计算农历")
        self.tree.heading("lunar_auth", text="权威农历")
        self.tree.heading("sizhu_calc", text="计算四柱")
        self.tree.heading("sizhu_auth", text="权威四柱")
        self.tree.heading("result", text="判断结果")
        
        # 设置列宽
        self.tree.column("date", width=100)
        self.tree.column("weekday", width=80)
        self.tree.column("lunar_calc", width=120)
        self.tree.column("lunar_auth", width=120)
        self.tree.column("sizhu_calc", width=180)
        self.tree.column("sizhu_auth", width=180)
        self.tree.column("result", width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def calculate_current_date(self):
        """计算当前日期"""
        try:
            # 获取当前日期时间
            current_date = date.today()
            current_time = datetime.now().strftime("%H:%M")
            
            # 更新输入框
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, current_date.strftime("%Y-%m-%d"))
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, current_time)
            
            # 计算并显示结果
            self.calculate_date(current_date, 12, 0)
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
    
    def calculate_selected_date(self):
        """计算选定日期"""
        try:
            # 获取输入的日期和时间
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            
            # 解析日期
            test_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # 解析时间
            hour, minute = map(int, time_str.split(":"))
            
            # 计算并显示结果
            self.calculate_date(test_date, hour, minute)
        except ValueError as e:
            messagebox.showwarning("警告", f"日期格式错误：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
    
    def calculate_date(self, test_date, hour, minute):
        """计算日期相关信息"""
        try:
            # 初始化变量
            lunar = {}
            sizhu = {}
            
            # 清空结果
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 获取计算结果
            # 农历信息
            try:
                lunar = get_lunar_date(test_date)
                lunar_calc = f"{lunar.get('month', '未知')}{lunar.get('day', '未知')}"
            except Exception as e:
                lunar_calc = f"错误：{str(e)}"
            
            # 四柱信息
            try:
                sizhu = calculate_sizhu(test_date, hour, minute)
                sizhu_calc = f"{sizhu.get('年柱', '未知')} {sizhu.get('月柱', '未知')} {sizhu.get('日柱', '未知')} {sizhu.get('时柱', '未知')}"
            except Exception as e:
                sizhu_calc = f"错误：{str(e)}"
            
            # 获取权威参考
            if test_date == date(2026, 3, 11):
                lunar_auth = "正月廿三"
                sizhu_auth = "丙午 辛卯 甲申 庚午"
            elif test_date == date(2026, 1, 1):
                lunar_auth = "十一月廿二"
                sizhu_auth = "乙巳 戊子 丁未 丙午"
            elif test_date == date(2026, 2, 14):
                lunar_auth = "正月初七"
                sizhu_auth = "丙午 庚寅 壬戌 丙午"
            elif test_date == date(2026, 3, 12):
                lunar_auth = "正月廿四"
                sizhu_auth = "丙午 辛卯 乙酉 庚辰"
            elif test_date == date(2026, 3, 13):
                lunar_auth = "正月廿五"
                sizhu_auth = "丙午 辛卯 丙戌 庚寅"
            elif test_date == date(2026, 3, 14):
                lunar_auth = "正月廿六"
                sizhu_auth = "丙午 辛卯 丁亥 庚寅"
            elif test_date == date(2026, 3, 15):
                lunar_auth = "正月廿七"
                sizhu_auth = "丙午 辛卯 戊子 庚寅"
            elif test_date == date(2026, 3, 16):
                lunar_auth = "正月廿八"
                sizhu_auth = "丙午 辛卯 己丑 庚寅"
            elif test_date == date(2026, 3, 17):
                lunar_auth = "正月廿九"
                sizhu_auth = "丙午 辛卯 庚寅 庚寅"
            elif test_date == date(2026, 3, 18):
                lunar_auth = "正月三十"
                sizhu_auth = "丙午 辛卯 壬辰 壬寅"
            elif test_date == date(2026, 3, 19):
                lunar_auth = "二月初一"
                sizhu_auth = "丙午 辛卯 癸巳 甲寅"
            else:
                lunar_auth = "无参考"
                sizhu_auth = "无参考"
            
            # 判断是否正确
            if test_date in [date(2026, 3, 11), date(2026, 1, 1), date(2026, 2, 14),
                           date(2026, 3, 12), date(2026, 3, 13), date(2026, 3, 14),
                           date(2026, 3, 15), date(2026, 3, 16), date(2026, 3, 17),
                           date(2026, 3, 18), date(2026, 3, 19)]:
                # 移除农历中的年份
                calc_lunar = lunar_calc
                if '年' in calc_lunar:
                    calc_lunar = calc_lunar.split('年')[1]
                
                is_lunar_correct = lunar_auth == calc_lunar
                is_sizhu_correct = sizhu_auth == sizhu_calc
                is_correct = is_lunar_correct and is_sizhu_correct
                
                if is_correct:
                    result = "✓ 正确"
                else:
                    result = "✗ 错误"
            else:
                result = "无法判断"
            
            # 添加到表格
            self.tree.insert("", tk.END, values=(
                test_date.strftime("%Y-%m-%d"),
                self.get_weekday(test_date),
                lunar_calc,
                lunar_auth,
                sizhu_calc,
                sizhu_auth,
                result
            ))
            
            # 成功提示
            messagebox.showinfo("成功", "日期测试计算完成！")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
    
    def clear_results(self):
        """清空结果"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def test_date_range(self):
        """测试日期范围"""
        try:
            # 获取用户输入的日期范围
            start_date_str = self.start_date_entry.get().strip()
            end_date_str = self.end_date_entry.get().strip()
            
            # 解析日期
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # 验证日期范围
            if start_date > end_date:
                messagebox.showwarning("警告", "开始日期不能晚于结束日期")
                return
            
            # 计算日期范围天数
            days_count = (end_date - start_date).days + 1
            
            if days_count > 365:
                if not messagebox.askyesno("确认", f"日期范围包含{days_count}天，计算可能需要较长时间，是否继续？"):
                    return
            
            # 清空结果
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 显示日期范围内的所有日期
            correct_count = 0
            total_count = 0
            
            for i in range(days_count):
                test_date = start_date + timedelta(days=i)
                try:
                    # 获取计算结果
                    lunar = get_lunar_date(test_date)
                    lunar_calc = f"{lunar.get('month', '未知')}{lunar.get('day', '未知')}"
                    
                    sizhu = calculate_sizhu(test_date, 8, 0)
                    sizhu_calc = f"{sizhu.get('年柱', '未知')} {sizhu.get('月柱', '未知')} {sizhu.get('日柱', '未知')} {sizhu.get('时柱', '未知')}"
                    
                    # 获取权威参考
                    if test_date == date(2026, 3, 11):
                        lunar_auth = "正月廿三"
                        sizhu_auth = "丙午 辛卯 甲申 庚午"
                    elif test_date == date(2026, 1, 1):
                        lunar_auth = "十一月廿二"
                        sizhu_auth = "乙巳 戊子 丁未 丙午"
                    elif test_date == date(2026, 2, 14):
                        lunar_auth = "正月初七"
                        sizhu_auth = "丙午 庚寅 壬戌 丙午"
                    elif test_date == date(2026, 3, 12):
                        lunar_auth = "正月廿四"
                        sizhu_auth = "丙午 辛卯 乙酉 庚辰"
                    elif test_date == date(2026, 3, 13):
                        lunar_auth = "正月廿五"
                        sizhu_auth = "丙午 辛卯 丙戌 庚寅"
                    elif test_date == date(2026, 3, 14):
                        lunar_auth = "正月廿六"
                        sizhu_auth = "丙午 辛卯 丁亥 庚寅"
                    elif test_date == date(2026, 3, 15):
                        lunar_auth = "正月廿七"
                        sizhu_auth = "丙午 辛卯 戊子 庚寅"
                    elif test_date == date(2026, 3, 16):
                        lunar_auth = "正月廿八"
                        sizhu_auth = "丙午 辛卯 己丑 庚寅"
                    elif test_date == date(2026, 3, 17):
                        lunar_auth = "正月廿九"
                        sizhu_auth = "丙午 辛卯 庚寅 庚寅"
                    elif test_date == date(2026, 3, 18):
                        lunar_auth = "正月三十"
                        sizhu_auth = "丙午 辛卯 壬辰 壬寅"
                    elif test_date == date(2026, 3, 19):
                        lunar_auth = "二月初一"
                        sizhu_auth = "丙午 辛卯 癸巳 甲寅"
                    else:
                        lunar_auth = "无参考"
                        sizhu_auth = "无参考"
                    
                    # 判断是否正确
                    if test_date in [date(2026, 3, 11), date(2026, 1, 1), date(2026, 2, 14),
                                   date(2026, 3, 12), date(2026, 3, 13), date(2026, 3, 14),
                                   date(2026, 3, 15), date(2026, 3, 16), date(2026, 3, 17),
                                   date(2026, 3, 18), date(2026, 3, 19)]:
                        # 移除农历中的年份
                        calc_lunar = lunar_calc
                        if '年' in calc_lunar:
                            calc_lunar = calc_lunar.split('年')[1]
                        
                        is_lunar_correct = lunar_auth == calc_lunar
                        is_sizhu_correct = sizhu_auth == sizhu_calc
                        is_correct = is_lunar_correct and is_sizhu_correct
                        
                        if is_correct:
                            result = "✓ 正确"
                            correct_count += 1
                        else:
                            result = "✗ 错误"
                        total_count += 1
                    else:
                        result = "无法判断"
                    
                    # 添加到表格
                    self.tree.insert("", tk.END, values=(
                        test_date.strftime("%Y-%m-%d"),
                        self.get_weekday(test_date),
                        lunar_calc,
                        lunar_auth,
                        sizhu_calc,
                        sizhu_auth,
                        result
                    ))
                except Exception as e:
                    # 添加错误信息到表格
                    self.tree.insert("", tk.END, values=(
                        test_date.strftime("%Y-%m-%d"),
                        self.get_weekday(test_date),
                        f"错误：{str(e)}",
                        "",
                        "",
                        "",
                        "错误"
                    ))
            
            # 成功提示
            if total_count > 0:
                accuracy = (correct_count / total_count) * 100
                messagebox.showinfo("成功", f"日期范围测试完成！共测试{days_count}天\n准确率：{accuracy:.2f}%")
            else:
                messagebox.showinfo("成功", f"日期范围测试完成！共测试{days_count}天")
        except ValueError as e:
            messagebox.showwarning("警告", f"日期格式错误：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"测试失败：{str(e)}")
    
    def get_weekday(self, date_obj):
        """获取星期"""
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[date_obj.weekday()]


if __name__ == "__main__":
    # 直接运行测试窗口
    window = DateTestWindow()
    window.window.mainloop()
