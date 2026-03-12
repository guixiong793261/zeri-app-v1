# -*- coding: utf-8 -*-
"""
专业级日课评分系统
用于对择日日课进行专业评分和分析
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import date, datetime
import json
import os
import sys

# 添加项目根目录到路径（用于直接运行此文件）
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from modules.四柱计算器 import calculate_sizhu, analyze_sizhu
from modules.高精度农历转换 import get_lunar_converter
from modules.评分器 import calculate_score
from modules.喜用神计算器 import calculate_xishen_yongshen


class DayScoreWindow:
    """日课评分系统主窗口"""
    
    def __init__(self, master=None):
        """初始化"""
        if master is None:
            self.window = tk.Tk()
            self.window.title("专业级日课评分系统")
        else:
            self.window = tk.Toplevel(master)
            self.window.title("专业级日课评分系统")
        
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置为屏幕的85%大小
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.state('zoomed')  # 窗口最大化
        
        # 数据存储
        self.date_list = []
        self.scoring_results = []
        self.owners_info = []
        
        # 创建界面
        self.create_widgets()
    
    def import_results(self, results, event_type, owners_data):
        """从主程序导入择日结果
        
        Args:
            results: 主程序的择日结果列表
            event_type: 事项类型
            owners_data: 事主数据列表
        """
        try:
            # 设置事项类型
            self.event_var.set(event_type)
            self.update_owners_frame()
            
            # 填充事主信息
            for i, owner_data in enumerate(owners_data):
                if i < len(self.owners_info):
                    self.owners_info[i]['year'].set(str(owner_data.get('year', '')))
                    self.owners_info[i]['month'].set(str(owner_data.get('month', '')))
                    self.owners_info[i]['day'].set(str(owner_data.get('day', '')))
                    self.owners_info[i]['hour'].set(str(owner_data.get('hour', 12)))
                    self.owners_info[i]['minute'].set(str(owner_data.get('minute', 0)))
                    
                    # 自动计算四柱
                    self.calculate_owner_sizhu(
                        self.owners_info[i]['year'],
                        self.owners_info[i]['month'],
                        self.owners_info[i]['day'],
                        self.owners_info[i]['hour'],
                        self.owners_info[i]['minute'],
                        self.owners_info[i]['name'],
                        self.owners_info[i]['sizhu_var'],
                        self.owners_info[i]['xishen_var'],
                        self.owners_info[i]['yongshen_var'],
                        self.owners_info[i].get('fuzi_var')
                    )
            
            # 导入择日结果到列表
            for result in results:
                date_str = result.get('date', '')
                if date_str and date_str not in self.date_list:
                    self.date_list.append(date_str)
                    
                    # 准备显示数据
                    score = result.get('score', 0)
                    level = result.get('level', '未知')
                    sizhu = result.get('sizhu', {})
                    
                    # 处理sizhu可能是字符串或字典的情况
                    if isinstance(sizhu, str):
                        sizhu_str = sizhu
                        # 尝试从字符串解析四柱
                        sizhu_parts = sizhu_str.split()
                        if len(sizhu_parts) == 4:
                            sizhu_dict = {
                                '年柱': sizhu_parts[0],
                                '月柱': sizhu_parts[1],
                                '日柱': sizhu_parts[2],
                                '时柱': sizhu_parts[3]
                            }
                        else:
                            sizhu_dict = {}
                    else:
                        sizhu_dict = sizhu
                        sizhu_str = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
                    
                    # 从detail字段中获取详细信息
                    detail = result.get('detail', {})
                    
                    # 获取详细得分信息
                    score_details = result.get('score_details', detail.get('score_details', {}))
                    yueling_score = score_details.get('月令得分', 0)
                    xishen_score = score_details.get('喜用神得分', 0)
                    huangdao_score = score_details.get('黄道得分', 0)
                    
                    # 添加到Treeview
                    self.date_treeview.insert('', tk.END, values=(date_str, score, level, sizhu_str, yueling_score, xishen_score, huangdao_score))
                    
                    # 如果结果包含评分信息，也添加到评分结果中
                    if 'score' in result and 'level' in result:
                        # 从detail字段中获取详细信息
                        detail = result.get('detail', {})
                        
                        score_result = {
                            'date': date_str,
                            'score': score,
                            'level': level,
                            'reason': result.get('reason', detail.get('reason', '')),
                            'sizhu': sizhu_dict,
                            'event_type': event_type,
                            'owners_detail': [],
                            'huangdao_info': result.get('huangdao_info', detail.get('huangdao_info', {})),
                            'wu_xing_result': result.get('wu_xing_result', detail.get('wu_xing_result', {})),
                            'yi_list': result.get('yi_list', detail.get('yi_list', [])),
                            'ji_list': result.get('ji_list', detail.get('ji_list', [])),
                            'shensha_list': result.get('shensha_list', detail.get('shensha_list', [])),
                            'score_details': result.get('score_details', detail.get('score_details', {}))
                        }
                        self.scoring_results.append(score_result)
            
            messagebox.showinfo("成功", f"成功导入 {len(results)} 个择日结果到评分系统")
            
        except Exception as e:
            messagebox.showerror("错误", f"导入结果失败：{str(e)}")
    
    def run(self):
        """运行日课评分系统"""
        # 确保窗口显示在最前面
        self.window.lift()
        self.window.focus_force()
        
        # 如果是主窗口（Tk），使用mainloop
        # 如果是子窗口（Toplevel），使用wait_window等待窗口关闭
        if isinstance(self.window, tk.Tk):
            self.window.mainloop()
        else:
            # 对于Toplevel窗口，确保它可见并等待用户交互
            self.window.transient(self.window.master)
            self.window.grab_set()
            self.window.wait_window()
    
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
        title_label = ttk.Label(self.main_frame, text="专业级日课评分系统", 
                               font=("微软雅黑", 24, "bold"))
        title_label.pack(pady=20)
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.main_frame, text="日课输入", padding="20")
        input_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # 事项类型选择
        event_frame = ttk.Frame(input_frame)
        event_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(event_frame, text="事项类型:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.event_var = tk.StringVar(value="嫁娶")
        events = ["嫁娶", "修造", "动土", "入宅", "开业", "出行", "安床", "作灶", "安葬"]
        event_combo = ttk.Combobox(event_frame, textvariable=self.event_var, 
                                   values=events, state="readonly", width=20, font=("微软雅黑", 12))
        event_combo.pack(side=tk.LEFT, padx=10)
        event_combo.bind("<<ComboboxSelected>>", lambda e: self.update_owners_frame())
        
        # 输入方式选择
        input_mode_frame = ttk.Frame(input_frame)
        input_mode_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_mode_frame, text="输入方式:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.input_mode = tk.StringVar(value="date")
        ttk.Radiobutton(input_mode_frame, text="按日期", variable=self.input_mode, 
                       value="date", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(input_mode_frame, text="按四柱", variable=self.input_mode, 
                       value="sizhu", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=10)
        
        # 日期输入框
        self.date_frame = ttk.Frame(input_frame)
        self.date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.date_frame, text="日期 (YYYY-MM-DD):", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.date_entry = ttk.Entry(self.date_frame, width=20, font=("微软雅黑", 12))
        self.date_entry.pack(side=tk.LEFT, padx=10)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # 时间输入
        ttk.Label(self.date_frame, text="时间 (HH:MM):", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.time_entry = ttk.Entry(self.date_frame, width=10, font=("微软雅黑", 12))
        self.time_entry.pack(side=tk.LEFT, padx=10)
        self.time_entry.insert(0, "12:00")
        
        # 为日期和时间输入框绑定键盘导航
        self._bind_entry_navigation([self.date_entry, self.time_entry])
        
        # 四柱输入框
        self.sizhu_frame = ttk.Frame(input_frame)
        # 默认隐藏
        
        ttk.Label(self.sizhu_frame, text="年柱:", font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
        self.sizhu_entries = []
        for i, label in enumerate(["年柱", "月柱", "日柱", "时柱"]):
            entry = ttk.Entry(self.sizhu_frame, width=10, font=("微软雅黑", 12))
            entry.pack(side=tk.LEFT, padx=5)
            self.sizhu_entries.append(entry)
        
        # 为四柱输入框绑定键盘导航
        self._bind_entry_navigation(self.sizhu_entries)
        
        # 事主信息区域
        self.owners_frame = ttk.LabelFrame(self.main_frame, text="事主信息", padding="20")
        self.owners_frame.pack(fill=tk.X, pady=10, padx=20)
        self.update_owners_frame()
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Button(button_frame, text="添加日课", command=self.add_date, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="添加四柱", command=self.add_sizhu, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="日课评分", command=self.start_scoring, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="对比分析", command=self.compare_analysis, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="保存分析", command=self.save_single_analysis, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="导出报告", command=self.export_report, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="导入文件", command=self.import_file, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="清空列表", command=self.clear_dates, width=18).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="帮助", command=self.show_help, width=18).pack(side=tk.RIGHT, padx=8)
        
        # 日课列表
        list_frame = ttk.LabelFrame(self.main_frame, text="日课列表", padding="20")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # 创建Treeview控件替代Listbox，显示更多信息
        columns = ('date', 'score', 'level', 'sizhu', 'yueling', 'xishen', 'huangdao')
        self.date_treeview = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 设置列标题
        self.date_treeview.heading('date', text='日期/四柱')
        self.date_treeview.heading('score', text='评分')
        self.date_treeview.heading('level', text='等级')
        self.date_treeview.heading('sizhu', text='四柱')
        self.date_treeview.heading('yueling', text='月令得分')
        self.date_treeview.heading('xishen', text='喜用神得分')
        self.date_treeview.heading('huangdao', text='黄道得分')
        
        # 设置列宽
        self.date_treeview.column('date', width=150)
        self.date_treeview.column('score', width=80, anchor='center')
        self.date_treeview.column('level', width=80, anchor='center')
        self.date_treeview.column('sizhu', width=200)
        self.date_treeview.column('yueling', width=80, anchor='center')
        self.date_treeview.column('xishen', width=80, anchor='center')
        self.date_treeview.column('huangdao', width=80, anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.date_treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.date_treeview.config(yscrollcommand=scrollbar.set)
        
        # 绑定双击事件
        self.date_treeview.bind('<Double-1>', self.on_date_double_click)
        
        self.date_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.main_frame, text="评分结果", padding="20")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, font=("微软雅黑", 11))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        self.result_text.tag_configure("gold", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        self.result_text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
    
    def update_owners_frame(self):
        """更新事主信息框架"""
        # 清空现有组件
        for widget in self.owners_frame.winfo_children():
            widget.destroy()
        
        self.owners_info = []
        event_type = self.event_var.get()
        
        # 添加提示标签
        if event_type != "嫁娶":
            hint_label = ttk.Label(self.owners_frame, text="（提示：以下事主信息为可选，可根据需要填写）", 
                                   foreground="gray", font=("微软雅黑", 11, "italic"))
            hint_label.pack(anchor=tk.W, pady=(0, 10))
        
        if event_type == "嫁娶":
            # 婚嫁需要新娘新郎（必填）
            owners = ["新娘", "新郎"]
        elif event_type == "安葬":
            # 安葬需要死者（逝者）和孝子（家属）
            owners = ["死者", "孝子1", "孝子2", "孝子3"]
        elif event_type in ["修造", "动土", "入宅", "装修", "作灶", "开业", "出行", "安床"]:
            # 修建类事项、作灶、开业、出行、安床，事主1-4可选（可填可不填）
            owners = ["事主1", "事主2", "事主3", "事主4"]
        else:
            # 其他事项，事主可选（可填可不填）
            owners = ["事主"]
        
        # 存储所有输入框以便键盘导航
        all_entries = []
        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=8)
            
            # 日期输入行
            date_row = ttk.Frame(owner_frame)
            date_row.pack(fill=tk.X, pady=5)
            
            ttk.Label(date_row, text=f"{owner}:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5, pady=5)
            
            # 婚嫁事项默认填充日期，其他事项默认为空（可选）
            if event_type == "嫁娶":
                year_var = tk.StringVar(value=str(date.today().year - 20))
                month_var = tk.StringVar(value=str(1))
                day_var = tk.StringVar(value=str(1))
                hour_var = tk.StringVar(value=str(12))
                minute_var = tk.StringVar(value=str(0))
            else:
                year_var = tk.StringVar()
                month_var = tk.StringVar()
                day_var = tk.StringVar()
                hour_var = tk.StringVar(value="12")
                minute_var = tk.StringVar(value="0")
            
            ttk.Label(date_row, text="年:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            year_entry = ttk.Entry(date_row, textvariable=year_var, width=8, font=("微软雅黑", 12))
            year_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(year_entry)
            
            ttk.Label(date_row, text="月:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            month_entry = ttk.Entry(date_row, textvariable=month_var, width=6, font=("微软雅黑", 12))
            month_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(month_entry)
            
            ttk.Label(date_row, text="日:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            day_entry = ttk.Entry(date_row, textvariable=day_var, width=6, font=("微软雅黑", 12))
            day_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(day_entry)
            
            ttk.Label(date_row, text="时:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            hour_entry = ttk.Entry(date_row, textvariable=hour_var, width=6, font=("微软雅黑", 12))
            hour_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(hour_entry)
            
            ttk.Label(date_row, text="分:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
            minute_entry = ttk.Entry(date_row, textvariable=minute_var, width=6, font=("微软雅黑", 12))
            minute_entry.pack(side=tk.LEFT, padx=5)
            all_entries.append(minute_entry)
            
            # 四柱显示
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=5)
            
            ttk.Label(sizhu_row, text="四柱:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
            sizhu_var = tk.StringVar(value="未计算")
            sizhu_label = ttk.Label(sizhu_row, textvariable=sizhu_var, font=("微软雅黑", 12, "bold"))
            sizhu_label.pack(side=tk.LEFT, padx=5)
            
            # 喜用神显示
            xishen_var = tk.StringVar(value="")
            yongshen_var = tk.StringVar(value="")
            
            xishen_row = ttk.Frame(owner_frame)
            xishen_row.pack(fill=tk.X, pady=5)
            
            ttk.Label(xishen_row, text="喜用神:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, textvariable=xishen_var, foreground="blue", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, text="  用神:", width=8, font=("微软雅黑", 12)).pack(side=tk.LEFT)
            ttk.Label(xishen_row, textvariable=yongshen_var, foreground="green", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=5)
            
            # 夫星子星显示（婚嫁专用）
            fuzi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                fuzi_row = ttk.Frame(owner_frame)
                fuzi_row.pack(fill=tk.X, pady=5)
                
                ttk.Label(fuzi_row, text="夫星/子星:", width=10, font=("微软雅黑", 12)).pack(side=tk.LEFT, padx=5)
                ttk.Label(fuzi_row, textvariable=fuzi_var, foreground="purple", font=("微软雅黑", 11)).pack(side=tk.LEFT, padx=5)
            
            # 计算按钮
            calc_btn = ttk.Button(owner_frame, text="计算四柱", 
                                 command=lambda y=year_var, m=month_var, d=day_var, 
                                 h=hour_var, mi=minute_var, o=owner, s=sizhu_var, 
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var: 
                                 self.calculate_owner_sizhu(y, m, d, h, mi, o, s, x, yg, fz))
            calc_btn.pack(anchor=tk.W, padx=5, pady=2)
            
            # 保存事主信息
            owner_info = {
                'name': owner,
                'year': year_var,
                'month': month_var,
                'day': day_var,
                'hour': hour_var,
                'minute': minute_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var
            }
            
            self.owners_info.append(owner_info)
            
            # 添加自动转换功能 - 当输入框内容变化时自动计算
            def auto_calculate(event):
                try:
                    year_val = year_var.get()
                    month_val = month_var.get()
                    day_val = day_var.get()
                    hour_val = hour_var.get()
                    minute_val = minute_var.get()
                    
                    if year_val and month_val and day_val and hour_val and minute_val:
                        year = int(year_val)
                        month = int(month_val)
                        day = int(day_val)
                        hour = int(hour_val)
                        minute = int(minute_val)
                        
                        # 验证日期有效性
                        date(year, month, day)
                        if 0 <= hour < 24 and 0 <= minute < 60:
                            # 延迟计算，避免频繁触发
                            self.window.after(500, lambda: 
                                self.calculate_owner_sizhu(year_var, month_var, day_var, 
                                                          hour_var, minute_var, owner, 
                                                          sizhu_var, xishen_var, yongshen_var, 
                                                          fuzi_var))
                except:
                    pass
            
            # 绑定输入框事件
            year_entry.bind('<KeyRelease>', auto_calculate)
            month_entry.bind('<KeyRelease>', auto_calculate)
            day_entry.bind('<KeyRelease>', auto_calculate)
            hour_entry.bind('<KeyRelease>', auto_calculate)
            minute_entry.bind('<KeyRelease>', auto_calculate)
        
        # 为所有事主输入框绑定键盘导航
        self._bind_entry_navigation(all_entries)
    
    def _bind_entry_navigation(self, entries):
        """为输入框绑定键盘导航功能"""
        if not entries:
            return
            
        def on_key_down(event, idx):
            """向下/向右移动到下一个输入框"""
            if idx < len(entries) - 1:
                entries[idx + 1].focus_set()
                entries[idx + 1].select_range(0, tk.END)
            return "break"
        
        def on_key_up(event, idx):
            """向上/向左移动到上一个输入框"""
            if idx > 0:
                entries[idx - 1].focus_set()
                entries[idx - 1].select_range(0, tk.END)
            return "break"
        
        def on_key_right(event, idx):
            """向右移动到下一个输入框"""
            # 检查光标是否在最后
            widget = event.widget
            if widget.index(tk.INSERT) >= len(widget.get()):
                if idx < len(entries) - 1:
                    entries[idx + 1].focus_set()
                    entries[idx + 1].select_range(0, tk.END)
                    return "break"
            return None
        
        def on_key_left(event, idx):
            """向左移动到上一个输入框"""
            # 检查光标是否在开头
            widget = event.widget
            if widget.index(tk.INSERT) == 0:
                if idx > 0:
                    entries[idx - 1].focus_set()
                    entries[idx - 1].select_range(0, tk.END)
                    return "break"
            return None
        
        for i, entry in enumerate(entries):
            # 绑定方向键
            entry.bind('<Down>', lambda e, idx=i: on_key_down(e, idx))
            entry.bind('<Up>', lambda e, idx=i: on_key_up(e, idx))
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, idx))
    
    def calculate_owner_sizhu(self, year_var, month_var, day_var, hour_var, minute_var, 
                              owner, sizhu_var, xishen_var, yongshen_var, fuzi_var=None):
        """计算事主四柱"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            
            target_date = date(year, month, day)
            sizhu = calculate_sizhu(target_date, hour, minute)
            analysis = analyze_sizhu(sizhu)
            
            # 显示四柱
            sizhu_text = f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}"
            sizhu_var.set(sizhu_text)
            
            # 显示喜用神 - 使用统一的喜用神计算器
            xishen, yongshen = calculate_xishen_yongshen(sizhu, analysis)
            xishen_var.set(xishen)
            yongshen_var.set(yongshen)
            
            # 婚嫁事项显示夫星子星
            if fuzi_var and self.event_var.get() == "嫁娶" and owner == "新娘":
                fuzi = analysis.get('夫星子星', {})
                fu_xing = fuzi.get('fu', '')
                zi_xing = fuzi.get('zi', '')
                if fu_xing or zi_xing:
                    fuzi_var.set(f"夫星: {fu_xing}, 子星: {zi_xing}")
            
        except ValueError as e:
            messagebox.showwarning("警告", f"请输入有效的日期时间: {e}")
    
    def toggle_input_mode(self):
        """切换输入方式"""
        if self.input_mode.get() == "date":
            self.date_frame.pack(fill=tk.X, pady=5)
            self.sizhu_frame.pack_forget()
        else:
            self.date_frame.pack_forget()
            self.sizhu_frame.pack(fill=tk.X, pady=5)
    
    def add_date(self):
        """添加日期到列表"""
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            datetime.strptime(time_str, '%H:%M')
            
            # 组合日期和时间
            date_time_str = f"{date_str} {time_str}"
            
            if date_time_str not in self.date_list:
                self.date_list.append(date_time_str)
                # 添加到Treeview
                self.date_treeview.insert('', tk.END, values=(date_time_str, '', '', ''))
            else:
                messagebox.showwarning("警告", "该日期时间已在列表中")
        except ValueError:
            messagebox.showwarning("警告", "日期格式错误，请使用YYYY-MM-DD格式\n时间格式错误，请使用HH:MM格式")
    
    def add_sizhu(self):
        """添加四柱到列表"""
        nian_zhu = self.sizhu_entries[0].get().strip()
        yue_zhu = self.sizhu_entries[1].get().strip()
        ri_zhu = self.sizhu_entries[2].get().strip()
        shi_zhu = self.sizhu_entries[3].get().strip()
        
        # 验证四柱格式
        if not all([nian_zhu, yue_zhu, ri_zhu, shi_zhu]):
            messagebox.showwarning("警告", "请完整填写四柱")
            return
        
        for zhu, name in [(nian_zhu, "年柱"), (yue_zhu, "月柱"), (ri_zhu, "日柱"), (shi_zhu, "时柱")]:
            if len(zhu) != 2:
                messagebox.showwarning("警告", f"{name}格式错误，应为两个字（如：甲子）")
                return
        
        # 生成四柱字符串
        sizhu_str = f"{nian_zhu} {yue_zhu} {ri_zhu} {shi_zhu}"
        
        # 检查是否已存在
        if sizhu_str in self.date_list:
            messagebox.showwarning("警告", "该四柱已存在")
            return
        
        # 添加到列表
        self.date_list.append(sizhu_str)
        # 添加到Treeview
        self.date_treeview.insert('', tk.END, values=(sizhu_str, '', '', sizhu_str))
        
        # 清空输入框
        for entry in self.sizhu_entries:
            entry.delete(0, tk.END)
    
    def clear_dates(self):
        """清空日期"""
        self.date_list = []
        # 清空Treeview
        for item in self.date_treeview.get_children():
            self.date_treeview.delete(item)
        self.scoring_results = []
    
    def start_scoring(self):
        """开始评分"""
        # 根据当前输入方式获取日课
        input_mode = self.input_mode.get()
        
        if input_mode == "date":
            # 按日期输入
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                datetime.strptime(time_str, '%H:%M')
                current_rike = f"{date_str} {time_str}"
            except ValueError:
                messagebox.showwarning("警告", "日期格式错误，请使用YYYY-MM-DD格式\n时间格式错误，请使用HH:MM格式")
                return
        else:
            # 按四柱输入
            nian_zhu = self.sizhu_entries[0].get().strip()
            yue_zhu = self.sizhu_entries[1].get().strip()
            ri_zhu = self.sizhu_entries[2].get().strip()
            shi_zhu = self.sizhu_entries[3].get().strip()
            
            # 验证四柱格式
            if not all([nian_zhu, yue_zhu, ri_zhu, shi_zhu]):
                messagebox.showwarning("警告", "请完整填写四柱")
                return
            
            for zhu, name in [(nian_zhu, "年柱"), (yue_zhu, "月柱"), (ri_zhu, "日柱"), (shi_zhu, "时柱")]:
                if len(zhu) != 2:
                    messagebox.showwarning("警告", f"{name}格式错误，应为两个字（如：甲子）")
                    return
            
            current_rike = f"{nian_zhu} {yue_zhu} {ri_zhu} {shi_zhu}"
        
        # 检查是否已存在
        if current_rike in self.date_list:
            messagebox.showwarning("警告", "该日课已评分")
            return
        
        event_type = self.event_var.get()
        
        # 获取事主信息
        owners_detail = []
        for info in self.owners_info:
            try:
                year = int(info['year'].get())
                month = int(info['month'].get())
                day = int(info['day'].get())
                hour = int(info['hour'].get())
                minute = int(info['minute'].get())
                
                target_date = date(year, month, day)
                sizhu = calculate_sizhu(target_date, hour, minute)
                analysis = analyze_sizhu(sizhu)
                
                owner_detail = {
                    'name': info['name'],
                    'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'xishen': info['xishen_var'].get(),
                    'yongshen': info['yongshen_var'].get(),
                    'fu_xing': '',
                    'zi_xing': ''
                }
                
                if event_type == "嫁娶" and info.get('fuzi_var'):
                    fuzi_str = info['fuzi_var'].get()
                    if '夫星:' in fuzi_str:
                        parts = fuzi_str.split(', ')
                        owner_detail['fu_xing'] = parts[0].replace('夫星: ', '')
                        if len(parts) > 1:
                            owner_detail['zi_xing'] = parts[1].replace('子星: ', '')
                
                owners_detail.append(owner_detail)
            except ValueError:
                # 跳过未填写的事主
                pass
        
        # 评分当前日课
        try:
            # 判断是日期还是四柱
            if len(current_rike.split()) == 4 and all(len(zhu) == 2 for zhu in current_rike.split()):
                # 这是四柱格式（如：甲子 乙丑 丙寅 丁卯）
                parts = current_rike.split()
                sizhu = {
                    '年柱': parts[0],
                    '月柱': parts[1],
                    '日柱': parts[2],
                    '时柱': parts[3],
                    'year_gan': parts[0][0],
                    'year_zhi': parts[0][1],
                    'month_gan': parts[1][0],
                    'month_zhi': parts[1][1],
                    'day_gan': parts[2][0],
                    'day_zhi': parts[2][1],
                    'hour_gan': parts[3][0],
                    'hour_zhi': parts[3][1]
                }
                display_date = f"四柱: {current_rike}"
            else:
                # 这是日期时间格式（如：2025-03-03 14:30）
                parts = current_rike.split()
                if len(parts) == 2:
                    date_part = parts[0]
                    time_part = parts[1]
                    hour, minute = map(int, time_part.split(':'))
                    score_date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                    sizhu = calculate_sizhu(score_date_obj, hour, minute)
                    display_date = current_rike
                else:
                    # 兼容旧格式（只有日期）
                    score_date_obj = datetime.strptime(current_rike, '%Y-%m-%d').date()
                    sizhu = calculate_sizhu(score_date_obj, 12, 0)
                    display_date = current_rike
            
            # 使用calculate_score进行评分
            score_result = calculate_score(sizhu, event_type, owners_detail)
            result = {
                'date': display_date,
                'score': score_result['score'],
                'level': score_result['level'],
                'reason': score_result.get('reason', ''),
                'sizhu': sizhu,
                'event_type': event_type,
                'owners_detail': owners_detail,
                'huangdao_info': score_result.get('huangdao_info', {}),
                'wu_xing_result': score_result.get('wu_xing_result', {}),
                'yi_list': score_result.get('yi_list', []),
                'ji_list': score_result.get('ji_list', []),
                'shensha_list': score_result.get('shensha_list', [])
            }
            
            # 添加到列表
            self.date_list.append(current_rike)
            
            # 准备显示数据
            score = result['score']
            level = result['level']
            sizhu = result['sizhu']
            sizhu_str = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
            
            # 获取详细得分信息
            score_details = score_result.get('score_details', {})
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            
            # 添加到Treeview
            self.date_treeview.insert('', tk.END, values=(current_rike, score, level, sizhu_str, yueling_score, xishen_score, huangdao_score))
            self.scoring_results.append(result)
            
            # 显示结果
            self.show_single_result(result)
            
            # 确保日课评分系统窗口获得焦点后再显示消息框
            self.window.lift()
            self.window.focus_force()
            messagebox.showinfo("成功", f"日课评分完成！\n评分：{result['score']} 分\n等级：{result['level']}")
            
        except Exception as e:
            # 确保日课评分系统窗口获得焦点后再显示错误消息框
            self.window.lift()
            self.window.focus_force()
            messagebox.showerror("错误", f"评分失败: {str(e)}")
            return
    
    def on_date_double_click(self, event):
        """双击日课显示详细信息"""
        selected = self.date_treeview.selection()
        if not selected:
            return
        
        item = selected[0]
        date_str = self.date_treeview.item(item, 'values')[0]
        
        # 查找对应的评分结果
        result = None
        for r in self.scoring_results:
            if r['date'] == date_str:
                result = r
                break
        
        if result:
            self.show_single_result(result)
    
    def _insert_colored_text(self, text, tag=None):
        """插入带颜色的文本"""
        if tag:
            self.result_text.insert(tk.END, text, tag)
        else:
            self.result_text.insert(tk.END, text)
    
    def show_single_result(self, result):
        """显示单个评分结果"""
        self.result_text.delete(1.0, tk.END)
        
        # 构建详细结果文本
        self._insert_colored_text("""
╔════════════════════════════════════════════════════════════════════╗
║                         日课评分结果                               ║
╚════════════════════════════════════════════════════════════════════╝

【基本信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        self._insert_colored_text(f"  日期: {result['date']}\n")
        self._insert_colored_text(f"  综合评分: {result['score']} 分\n")
        
        # 等级评定（如果有星星，用金色显示）
        level = result['level']
        self._insert_colored_text("  等级评定: ")
        if '★' in level:
            star_count = level.count('★')
            other_text = level.replace('★', '').strip()
            self._insert_colored_text('★' * star_count, "gold_star")
            if other_text:
                self._insert_colored_text(f" {other_text}")
            self._insert_colored_text("\n")
        else:
            self._insert_colored_text(f"{level}\n")
        
        self._insert_colored_text("\n")
        
        # 评分详情
        self._insert_colored_text("""【评分详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        score_details = result.get('score_details', {})
        if score_details:
            wuxing_score = score_details.get('五行评分', 100)
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            total_score = score_details.get('总分', result['score'])
            
            self._insert_colored_text(f"  五行评分：{wuxing_score} 分\n")
            
            # 五行评分详细得分
            wu_xing_result = result.get('wu_xing_result', {})
            score_breakdown = wu_xing_result.get('score_breakdown', {})
            if score_breakdown:
                self._insert_colored_text(f"    ├─ 基础分：{score_breakdown.get('基础分', 100)} 分\n")
                shensha_score = score_breakdown.get('神煞得分', 0)
                if shensha_score != 0:
                    self._insert_colored_text(f"    ├─ 神煞得分：{shensha_score:+d} 分\n")
                yi_score = score_breakdown.get('宜事得分', 0)
                if yi_score != 0:
                    self._insert_colored_text(f"    ├─ 宜事得分：+{yi_score} 分\n")
                ji_score = score_breakdown.get('忌事得分', 0)
                if ji_score != 0:
                    self._insert_colored_text(f"    ├─ 忌事得分：{ji_score} 分\n")
                zhangsheng = score_breakdown.get('十二长生得分', 0)
                if zhangsheng != 0:
                    self._insert_colored_text(f"    ├─ 十二长生得分：{zhangsheng:+d} 分\n")
                zhizhi = score_breakdown.get('地支关系得分', 0)
                if zhizhi != 0:
                    self._insert_colored_text(f"    ├─ 地支关系得分：{zhizhi:+d} 分\n")
                nayin = score_breakdown.get('纳音匹配得分', 0)
                if nayin != 0:
                    self._insert_colored_text(f"    └─ 纳音匹配得分：{nayin:+d} 分\n")
            
            self._insert_colored_text(f"  月令得分：{yueling_score:+d} 分\n")
            
            # 月令详细得分
            yueling_detail = score_details.get('月令详细', {})
            if yueling_detail:
                self._insert_colored_text(f"    ├─ 旺衰得分：{yueling_detail.get('旺衰得分', 0):+d} 分\n")
                self._insert_colored_text(f"    └─ 支支关系得分：{yueling_detail.get('支支关系得分', 0):+d} 分\n")
            
            self._insert_colored_text(f"  喜用神得分：{xishen_score:+d} 分\n")
            self._insert_colored_text(f"  黄道得分：{huangdao_score:+d} 分\n")
            self._insert_colored_text(f"  ─────────────────────────────────\n")
            self._insert_colored_text(f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {huangdao_score:+d} = {total_score} 分\n")
            self._insert_colored_text(f"  总分：{total_score} 分\n")
        else:
            self._insert_colored_text("  暂无详细得分数据\n")
        
        self._insert_colored_text("\n")
        
        # 月令分析
        self._insert_colored_text("""【月令分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
        # 从reason中提取月令信息
        reason = result.get('reason', '')
        yueling_info = ""
        for part in reason.split('；'):
            if '月令：' in part:
                yueling_info = part.replace('月令：', '')
                break
        
        if yueling_info:
            self._insert_colored_text(f"  {yueling_info}\n")
        else:
            self._insert_colored_text("  月令分析：暂无数据\n")
        
        self._insert_colored_text("\n")
        
        # 四柱信息
        if result.get('sizhu'):
            sizhu = result['sizhu']
            self._insert_colored_text(f"""【四柱八字】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  年柱: {sizhu['年柱']}    月柱: {sizhu['月柱']}
  日柱: {sizhu['日柱']}    时柱: {sizhu['时柱']}

  【天干五行】
    年干: {sizhu['年柱'][0]}    月干: {sizhu['月柱'][0]}    日干: {sizhu['日柱'][0]}    时干: {sizhu['时柱'][0]}
  【地支五行】
    年支: {sizhu['年柱'][1]}    月支: {sizhu['月柱'][1]}    日支: {sizhu['日柱'][1]}    时支: {sizhu['时柱'][1]}

""")
        
        # 五行分析
        if result.get('wu_xing_result'):
            wu_xing = result['wu_xing_result']
            self._insert_colored_text(f"""【五行分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  五行评分: {wu_xing.get('score', 'N/A')} 分
""")
            if wu_xing.get('reason'):
                self._insert_colored_text(f"  五行评语: {wu_xing['reason']}\n")
            if wu_xing.get('details'):
                details = wu_xing['details']
                
                # 1. 天干地支五行
                if details.get('天干五行'):
                    self._insert_colored_text("\n  【天干地支五行】\n")
                    for pillar, info in details['天干五行'].items():
                        self._insert_colored_text(f"    {pillar}: {info['天干']}({info['天干五行']}) {info['地支']}({info['地支五行']})\n")
                
                # 2. 地支关系（三合、六合、六冲、六害、三刑）
                if details.get('地支关系') and len(details['地支关系']) > 0:
                    self._insert_colored_text("\n  【地支关系】\n")
                    for relation in details['地支关系']:
                        self._insert_colored_text(f"    • {relation}\n")
                else:
                    self._insert_colored_text("\n  【地支关系】\n    无明显合冲刑害关系\n")
                
                # 3. 十二长生
                if details.get('十二长生'):
                    self._insert_colored_text("\n  【十二长生】\n")
                    for pillar, state in details['十二长生'].items():
                        self._insert_colored_text(f"    {pillar}: {state}\n")
                
                # 4. 纳音五行
                if details.get('纳音五行'):
                    self._insert_colored_text("\n  【纳音五行】\n")
                    for pillar, nayin in details['纳音五行'].items():
                        self._insert_colored_text(f"    {pillar}: {nayin}\n")
                
                # 5. 吉神（天德、月德）
                if details.get('吉神') and len(details['吉神']) > 0:
                    self._insert_colored_text("\n  【吉神】\n")
                    for jishen in details['吉神']:
                        self._insert_colored_text(f"    ✓ {jishen}\n")
                else:
                    self._insert_colored_text("\n  【吉神】\n    无天德月德等吉神\n")
                
                # 6. 日主旺衰
                if details.get('日主旺衰'):
                    self._insert_colored_text(f"\n  【日主旺衰】\n    {details['日主旺衰']}\n")
                
                # 7. 五行生克
                if details.get('五行生克') and len(details['五行生克']) > 0:
                    self._insert_colored_text("\n  【五行生克】\n")
                    for relation in details['五行生克']:
                        self._insert_colored_text(f"    • {relation}\n")
            if wu_xing.get('wang_xiang'):
                self._insert_colored_text(f"  旺相分析: {wu_xing['wang_xiang']}\n")
            if wu_xing.get('ke_zhi'):
                self._insert_colored_text(f"  克制关系: {wu_xing['ke_zhi']}\n")
            self._insert_colored_text("\n")
        
        # 黄道信息
        if result.get('huangdao_info'):
            huangdao = result['huangdao_info']
            self._insert_colored_text("""【黄道信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            if huangdao.get('da_huang_dao'):
                da_hd = huangdao['da_huang_dao']
                self._insert_colored_text(f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})\n")
                if da_hd.get('description'):
                    self._insert_colored_text(f"    说明: {da_hd['description']}\n")
            if huangdao.get('xiao_huang_dao'):
                xiao_hd = huangdao['xiao_huang_dao']
                self._insert_colored_text(f"  小黄道: {xiao_hd.get('name', 'N/A')} ({xiao_hd.get('type', 'N/A')})\n")
                if xiao_hd.get('description'):
                    self._insert_colored_text(f"    说明: {xiao_hd['description']}\n")
            self._insert_colored_text(f"  黄道等级: {huangdao.get('huang_dao_level', 'N/A')}\n\n")
        
        # 宜忌信息
        if result.get('yi_list') or result.get('ji_list'):
            self._insert_colored_text("""【宜忌信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            if result.get('yi_list'):
                yi_items = result['yi_list'] if isinstance(result['yi_list'], list) else result['yi_list'].split(', ')
                self._insert_colored_text(f"  宜: {', '.join(yi_items)}\n")
            if result.get('ji_list'):
                ji_items = result['ji_list'] if isinstance(result['ji_list'], list) else result['ji_list'].split(', ')
                self._insert_colored_text(f"  忌: {', '.join(ji_items)}\n")
            self._insert_colored_text("\n")
        
        # 神煞信息
        if result.get('shensha_list'):
            self._insert_colored_text("""【神煞信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            for shensha in result['shensha_list']:
                name = shensha.get('name', '')
                desc = shensha.get('description', '')
                self._insert_colored_text(f"  • {name}: {desc}\n")
            self._insert_colored_text("\n")
        
        # 评语
        if result.get('reason'):
            self._insert_colored_text(f"""【综合评语】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {result['reason']}

""")
        
        # 事主匹配分析
        if result.get('owners_detail'):
            self._insert_colored_text("""【事主匹配分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
            for owner in result['owners_detail']:
                self._insert_colored_text(f"  【{owner.get('name', '事主')}】\n")
                self._insert_colored_text(f"    出生日期: {owner.get('birth_date', 'N/A')}\n")
                self._insert_colored_text(f"    四柱: {owner.get('sizhu', 'N/A')}\n")
                if owner.get('xishen'):
                    self._insert_colored_text(f"    喜神: {owner['xishen']}\n")
                if owner.get('yongshen'):
                    self._insert_colored_text(f"    用神: {owner['yongshen']}\n")
                if owner.get('fu_xing'):
                    self._insert_colored_text(f"    夫星: {owner['fu_xing']}\n")
                if owner.get('zi_xing'):
                    self._insert_colored_text(f"    子星: {owner['zi_xing']}\n")
                if owner.get('match_result'):
                    self._insert_colored_text(f"    匹配结果: {owner['match_result']}\n")
                self._insert_colored_text("\n")
        
        self._insert_colored_text("""
╔════════════════════════════════════════════════════════════════════╗
║              评分完成！可继续添加日课进行对比分析                  ║
╚════════════════════════════════════════════════════════════════════╝""")
    
    def compare_analysis(self):
        """对比分析 - 对比多个日课的评分结果"""
        # 从Treeview获取日期列表
        dates = []
        for item in self.date_treeview.get_children():
            values = self.date_treeview.item(item, 'values')
            if values:
                dates.append(values[0])
        
        if len(dates) < 2:
            messagebox.showwarning("提示", "请至少添加两个日课进行对比")
            return
        
        # 检查是否所有日课都已评分
        scored_dates = [result['date'] for result in self.scoring_results]
        unscored_dates = [date for date in dates if date not in scored_dates]
        
        # 如果有未评分的日课，自动进行评分
        if unscored_dates:
            # 自动评分未评分的日课
            event_type = self.event_var.get()
            
            # 获取事主信息
            owners_detail = []
            for info in self.owners_info:
                try:
                    year = int(info['year'].get())
                    month = int(info['month'].get())
                    day = int(info['day'].get())
                    hour = int(info['hour'].get())
                    minute = int(info['minute'].get())
                    
                    target_date = date(year, month, day)
                    sizhu = calculate_sizhu(target_date, hour, minute)
                    analysis = analyze_sizhu(sizhu)
                    
                    owner_detail = {
                        'name': info['name'],
                        'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                        'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                        'xishen': info['xishen_var'].get(),
                        'yongshen': info['yongshen_var'].get(),
                        'fu_xing': '',
                        'zi_xing': ''
                    }
                    
                    if event_type == "嫁娶" and info.get('fuzi_var'):
                        fuzi_str = info['fuzi_var'].get()
                        if '夫星:' in fuzi_str:
                            parts = fuzi_str.split(', ')
                            owner_detail['fu_xing'] = parts[0].replace('夫星: ', '')
                            if len(parts) > 1:
                                owner_detail['zi_xing'] = parts[1].replace('子星: ', '')
                    
                    owners_detail.append(owner_detail)
                except ValueError:
                    # 跳过未填写的事主
                    pass
            
            # 对每个未评分的日课进行评分
            for date_str in unscored_dates:
                try:
                    # 判断是日期还是四柱
                    if len(date_str.split()) == 4 and all(len(zhu) == 2 for zhu in date_str.split()):
                        # 这是四柱格式（如：甲子 乙丑 丙寅 丁卯）
                        parts = date_str.split()
                        sizhu = {
                            '年柱': parts[0],
                            '月柱': parts[1],
                            '日柱': parts[2],
                            '时柱': parts[3],
                            'year_gan': parts[0][0],
                            'year_zhi': parts[0][1],
                            'month_gan': parts[1][0],
                            'month_zhi': parts[1][1],
                            'day_gan': parts[2][0],
                            'day_zhi': parts[2][1],
                            'hour_gan': parts[3][0],
                            'hour_zhi': parts[3][1]
                        }
                        display_date = f"四柱: {date_str}"
                    else:
                        # 这是日期时间格式（如：2025-03-03 14:30）
                        parts = date_str.split()
                        if len(parts) == 2:
                            date_part = parts[0]
                            time_part = parts[1]
                            hour, minute = map(int, time_part.split(':'))
                            score_date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                            sizhu = calculate_sizhu(score_date_obj, hour, minute)
                            display_date = date_str
                        else:
                            # 兼容旧格式（只有日期）
                            score_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                            sizhu = calculate_sizhu(score_date_obj, 12, 0)
                            display_date = date_str
                    
                    # 使用calculate_score进行评分
                    score_result = calculate_score(sizhu, event_type, owners_detail)
                    result = {
                        'date': display_date,
                        'score': score_result['score'],
                        'level': score_result['level'],
                        'reason': score_result.get('reason', ''),
                        'sizhu': sizhu,
                        'event_type': event_type,
                        'owners_detail': owners_detail,
                        'huangdao_info': score_result.get('huangdao_info', {}),
                        'wu_xing_result': score_result.get('wu_xing_result', {}),
                        'yi_list': score_result.get('yi_list', []),
                        'ji_list': score_result.get('ji_list', []),
                        'shensha_list': score_result.get('shensha_list', [])
                    }
                    
                    # 添加到评分结果
                    self.scoring_results.append(result)
                    
                except Exception as e:
                    print(f"自动评分 {date_str} 出错: {e}")
                    continue
        
        # 再次检查评分结果数量
        if not self.scoring_results or len(self.scoring_results) < 2:
            messagebox.showinfo("提示", "请先点击'日课评分'按钮对至少两个日课进行评分，然后再进行对比分析")
            return
        
        # 创建对比分析窗口
        compare_window = tk.Toplevel(self.window)
        compare_window.title("日课对比分析")
        compare_window.geometry("900x700")
        
        # 创建主框架和滚动条
        main_frame = ttk.Frame(compare_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 结果显示
        result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("微软雅黑", 10))
        result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        result_text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        
        # 按评分排序
        sorted_results = sorted(self.scoring_results, key=lambda x: x['score'], reverse=True)
        
        # 按钮区域
        button_frame = ttk.Frame(compare_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="保存分析", command=lambda: self.save_analysis(result_text, sorted_results, self.event_var.get())).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="关闭窗口", command=compare_window.destroy).pack(side=tk.RIGHT, padx=10)
        
        result_text.insert(tk.END, "=" * 70 + "\n")
        result_text.insert(tk.END, "                    日课对比分析报告\n")
        result_text.insert(tk.END, "=" * 70 + "\n\n")
        
        result_text.insert(tk.END, f"对比日课数量: {len(sorted_results)}\n")
        result_text.insert(tk.END, f"事项类型: {self.event_var.get()}\n")
        result_text.insert(tk.END, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 显示事主信息
        if self.owners_info:
            result_text.insert(tk.END, "【事主信息】\n\n")
            for info in self.owners_info:
                try:
                    year = info['year'].get()
                    month = info['month'].get()
                    day = info['day'].get()
                    if year and month and day:
                        result_text.insert(tk.END, f"  {info['name']}: ")
                        result_text.insert(tk.END, f"{year}年{month}月{day}日 ")
                        if info.get('sizhu_var'):
                            result_text.insert(tk.END, f"四柱: {info['sizhu_var'].get()} ")
                        if info.get('xishen_var') and info['xishen_var'].get():
                            result_text.insert(tk.END, f"喜神: {info['xishen_var'].get()} ")
                        if info.get('yongshen_var') and info['yongshen_var'].get():
                            result_text.insert(tk.END, f"用神: {info['yongshen_var'].get()} ")
                        if info.get('fuzi_var') and info['fuzi_var'].get():
                            result_text.insert(tk.END, f"{info['fuzi_var'].get()}")
                        result_text.insert(tk.END, "\n")
                except:
                    pass
            result_text.insert(tk.END, "\n")
        
        # 显示排名概览
        result_text.insert(tk.END, "【评分排名概览】\n\n")
        result_text.insert(tk.END, f"{'排名':<6}{'日期/四柱':<25}{'评分':<10}{'等级':<15}\n")
        result_text.insert(tk.END, "-" * 70 + "\n")
        for i, result in enumerate(sorted_results, 1):
            date_display = result['date'][:22] if len(result['date']) > 22 else result['date']
            level = result['level']
            
            # 插入排名、日期、评分
            result_text.insert(tk.END, f"第{i}名  {date_display:<25}{result['score']:<10}")
            
            # 如果有星星，用金色显示
            if '★' in level:
                star_count = level.count('★')
                other_text = level.replace('★', '').strip()
                result_text.insert(tk.END, '★' * star_count, "gold_star")
                if other_text:
                    result_text.insert(tk.END, f" {other_text}")
            else:
                result_text.insert(tk.END, level)
            result_text.insert(tk.END, "\n")
        result_text.insert(tk.END, "\n")
        
        # 显示详细信息
        result_text.insert(tk.END, "=" * 70 + "\n")
        result_text.insert(tk.END, "【详细分析报告】\n")
        result_text.insert(tk.END, "=" * 70 + "\n\n")
        
        for i, result in enumerate(sorted_results, 1):
            result_text.insert(tk.END, f"╔════════════════════════════════════════════════════════════════════╗\n")
            result_text.insert(tk.END, f"║  第 {i} 名{' ' * (58 - len(str(i)))}║\n")
            result_text.insert(tk.END, f"╚════════════════════════════════════════════════════════════════════╝\n\n")
            
            result_text.insert(tk.END, f"【基本信息】\n")
            result_text.insert(tk.END, "-" * 70 + "\n")
            result_text.insert(tk.END, f"  日期: {result['date']}\n")
            result_text.insert(tk.END, f"  综合评分: {result['score']} 分\n")
            result_text.insert(tk.END, f"  等级评定: ")
            
            # 如果有星星，用金色显示
            level = result['level']
            if '★' in level:
                star_count = level.count('★')
                other_text = level.replace('★', '').strip()
                result_text.insert(tk.END, '★' * star_count, "gold_star")
                if other_text:
                    result_text.insert(tk.END, f" {other_text}")
            else:
                result_text.insert(tk.END, level)
            result_text.insert(tk.END, "\n\n")
            
            # 四柱信息
            if result.get('sizhu'):
                sizhu = result['sizhu']
                result_text.insert(tk.END, "【四柱八字】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  年柱: {sizhu['年柱']}    月柱: {sizhu['月柱']}\n")
                result_text.insert(tk.END, f"  日柱: {sizhu['日柱']}    时柱: {sizhu['时柱']}\n\n")
                
                # 天干地支五行
                result_text.insert(tk.END, "  【天干五行】\n")
                result_text.insert(tk.END, f"    年干: {sizhu['年柱'][0]}    月干: {sizhu['月柱'][0]}    日干: {sizhu['日柱'][0]}    时干: {sizhu['时柱'][0]}\n")
                result_text.insert(tk.END, "  【地支五行】\n")
                result_text.insert(tk.END, f"    年支: {sizhu['年柱'][1]}    月支: {sizhu['月柱'][1]}    日支: {sizhu['日柱'][1]}    时支: {sizhu['时柱'][1]}\n\n")
            
            # 五行分析
            if result.get('wu_xing_result'):
                wu_xing = result['wu_xing_result']
                result_text.insert(tk.END, "【五行分析】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  五行评分: {wu_xing.get('score', 'N/A')} 分\n")
                if wu_xing.get('reason'):
                    result_text.insert(tk.END, f"  五行评语: {wu_xing['reason']}\n")
                
                # 显示详细分析
                if wu_xing.get('details'):
                    details = wu_xing['details']
                    
                    # 1. 天干地支五行
                    if details.get('天干五行'):
                        result_text.insert(tk.END, "\n  【天干地支五行】\n")
                        for pillar, info in details['天干五行'].items():
                            result_text.insert(tk.END, f"    {pillar}: {info['天干']}({info['天干五行']}) {info['地支']}({info['地支五行']})\n")
                    
                    # 2. 地支关系（三合、六合、六冲、六害、三刑）
                    if details.get('地支关系') and len(details['地支关系']) > 0:
                        result_text.insert(tk.END, "\n  【地支关系】\n")
                        for relation in details['地支关系']:
                            result_text.insert(tk.END, f"    • {relation}\n")
                    else:
                        result_text.insert(tk.END, "\n  【地支关系】\n    无明显合冲刑害关系\n")
                    
                    # 3. 十二长生状态
                    if details.get('十二长生') and len(details['十二长生']) > 0:
                        result_text.insert(tk.END, "\n  【十二长生状态】\n")
                        for pillar, state in details['十二长生'].items():
                            result_text.insert(tk.END, f"    {pillar}: {state}\n")
                    
                    # 4. 纳音五行
                    if details.get('纳音五行') and len(details['纳音五行']) > 0:
                        result_text.insert(tk.END, "\n  【纳音五行】\n")
                        for pillar, nayin in details['纳音五行'].items():
                            result_text.insert(tk.END, f"    {pillar}: {nayin}\n")
                    
                    # 5. 吉神（天德、月德）
                    if details.get('吉神') and len(details['吉神']) > 0:
                        result_text.insert(tk.END, "\n  【吉神】\n")
                        for jishen in details['吉神']:
                            result_text.insert(tk.END, f"    ✓ {jishen}\n")
                    
                    # 6. 日主旺衰
                    if details.get('日主旺衰'):
                        result_text.insert(tk.END, "\n  【日主旺衰】\n")
                        result_text.insert(tk.END, f"    {details['日主旺衰']}\n")
                    
                    # 7. 五行生克
                    if details.get('五行生克') and len(details['五行生克']) > 0:
                        result_text.insert(tk.END, "\n  【五行生克关系】\n")
                        for relation in details['五行生克']:
                            result_text.insert(tk.END, f"    • {relation}\n")
                
                result_text.insert(tk.END, "\n")
            
            # 黄道信息
            if result.get('huangdao_info'):
                huangdao = result['huangdao_info']
                result_text.insert(tk.END, "【黄道信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                if huangdao.get('da_huang_dao'):
                    da_hd = huangdao['da_huang_dao']
                    result_text.insert(tk.END, f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})\n")
                    if da_hd.get('description'):
                        result_text.insert(tk.END, f"    说明: {da_hd['description']}\n")
                if huangdao.get('xiao_huang_dao'):
                    xiao_hd = huangdao['xiao_huang_dao']
                    result_text.insert(tk.END, f"  小黄道: {xiao_hd.get('name', 'N/A')} ({xiao_hd.get('type', 'N/A')})\n")
                    if xiao_hd.get('description'):
                        result_text.insert(tk.END, f"    说明: {xiao_hd['description']}\n")
                result_text.insert(tk.END, f"  黄道等级: {huangdao.get('huang_dao_level', 'N/A')}\n\n")
            
            # 宜忌信息
            if result.get('yi_list') or result.get('ji_list'):
                result_text.insert(tk.END, "【宜忌信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                if result.get('yi_list'):
                    yi_items = result['yi_list'] if isinstance(result['yi_list'], list) else result['yi_list'].split(', ')
                    result_text.insert(tk.END, f"  宜: {', '.join(yi_items)}\n")
                if result.get('ji_list'):
                    ji_items = result['ji_list'] if isinstance(result['ji_list'], list) else result['ji_list'].split(', ')
                    result_text.insert(tk.END, f"  忌: {', '.join(ji_items)}\n")
                result_text.insert(tk.END, "\n")
            
            # 神煞信息
            if result.get('shensha_list'):
                result_text.insert(tk.END, "【神煞信息】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                for shensha in result['shensha_list']:
                    name = shensha.get('name', '')
                    desc = shensha.get('description', '')
                    result_text.insert(tk.END, f"  • {name}: {desc}\n")
                result_text.insert(tk.END, "\n")
            
            # 评语
            if result.get('reason'):
                result_text.insert(tk.END, "【综合评语】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                result_text.insert(tk.END, f"  {result['reason']}\n\n")
            
            # 事主匹配分析
            if result.get('owners_detail'):
                result_text.insert(tk.END, "【事主匹配分析】\n")
                result_text.insert(tk.END, "-" * 70 + "\n")
                for owner in result['owners_detail']:
                    result_text.insert(tk.END, f"  【{owner.get('name', '事主')}】\n")
                    result_text.insert(tk.END, f"    出生日期: {owner.get('birth_date', 'N/A')}\n")
                    result_text.insert(tk.END, f"    四柱: {owner.get('sizhu', 'N/A')}\n")
                    if owner.get('xishen'):
                        result_text.insert(tk.END, f"    喜神: {owner['xishen']}\n")
                    if owner.get('yongshen'):
                        result_text.insert(tk.END, f"    用神: {owner['yongshen']}\n")
                    if owner.get('fu_xing'):
                        result_text.insert(tk.END, f"    夫星: {owner['fu_xing']}\n")
                    if owner.get('zi_xing'):
                        result_text.insert(tk.END, f"    子星: {owner['zi_xing']}\n")
                    if owner.get('match_result'):
                        result_text.insert(tk.END, f"    匹配结果: {owner['match_result']}\n")
                    result_text.insert(tk.END, "\n")
    
    def export_report(self):
        """导出评分报告"""
        if not self.scoring_results:
            messagebox.showwarning("提示", "没有评分结果可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导出评分报告"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("日课评分报告\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"事项类型: {self.event_var.get()}\n")
                f.write(f"评分日课数量: {len(self.scoring_results)}\n\n")
                
                # 按评分排序
                sorted_results = sorted(self.scoring_results, key=lambda x: x['score'], reverse=True)
                
                for i, result in enumerate(sorted_results, 1):
                    f.write(f"【第 {i} 名】\n")
                    f.write(f"日期: {result['date']}\n")
                    f.write(f"评分: {result['score']} 分\n")
                    f.write(f"等级: {result['level']}\n")
                    
                    if result.get('sizhu'):
                        sizhu = result['sizhu']
                        f.write(f"四柱: {sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}\n")
                    
                    if result.get('reason'):
                        f.write(f"评语: {result['reason']}\n")
                    
                    f.write("-" * 40 + "\n\n")
            
            messagebox.showinfo("成功", f"报告已导出到:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def import_file(self):
        """从文件导入日期"""
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="导入日期文件"
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            
            if file_path.endswith('.json'):
                # 导入JSON格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理主程序导出的格式
                    if isinstance(data, dict) and 'results' in data:
                        for item in data['results']:
                            if isinstance(item, dict) and 'date' in item:
                                date_str = item['date']
                                try:
                                    datetime.strptime(date_str, '%Y-%m-%d')
                                    if date_str not in self.date_list:
                                        self.date_list.append(date_str)
                                        self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                        imported_count += 1
                                except ValueError:
                                    pass
                    # 处理其他格式
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                date_str = item
                            elif isinstance(item, dict) and 'date' in item:
                                date_str = item['date']
                            else:
                                continue
                            
                            try:
                                datetime.strptime(date_str, '%Y-%m-%d')
                                if date_str not in self.date_list:
                                        self.date_list.append(date_str)
                                        self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                        imported_count += 1
                            except ValueError:
                                pass
            else:
                # 导入文本格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 尝试提取日期（格式：YYYY-MM-DD）
                        import re
                        date_match = re.search(r'日期：(\d{4}-\d{2}-\d{2})', line) or re.search(r'\d{4}-\d{2}-\d{2}', line)
                        if date_match:
                            date_str = date_match.group(1)
                            if date_str not in self.date_list:
                                self.date_list.append(date_str)
                                self.date_treeview.insert('', tk.END, values=(date_str, '', '', '', '', '', ''))
                                imported_count += 1
            
            if imported_count > 0:
                messagebox.showinfo("成功", f"成功导入 {imported_count} 个日期")
            else:
                messagebox.showinfo("提示", "没有找到有效的日期")
            
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def save_single_analysis(self):
        """保存单个日课分析结果"""
        try:
            # 获取当前显示的内容
            content = self.result_text.get(1.0, tk.END)
            
            if not content.strip():
                messagebox.showwarning("提示", "没有分析结果可保存")
                return
            
            # 弹出文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="保存日课分析结果",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            if file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
            # 保存为JSON文件
            elif file_path.endswith('.json'):
                # 尝试从当前显示的内容中提取关键信息
                # 这里简化处理，实际项目中可以更详细地解析
                json_data = {
                    'analysis_type': '单个日课分析',
                    'event_type': self.event_var.get(),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'content': content
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_analysis(self, result_text, sorted_results, event_type):
        """保存对比分析结果"""
        try:
            # 获取当前显示的内容
            content = result_text.get(1.0, tk.END)
            
            if not content.strip():
                messagebox.showwarning("提示", "没有分析结果可保存")
                return
            
            # 弹出文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title="保存日课对比分析结果",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            if file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
            # 保存为JSON文件
            elif file_path.endswith('.json'):
                # 构建JSON数据
                json_data = {
                    'analysis_type': '对比分析',
                    'event_type': event_type,
                    'comparison_count': len(sorted_results),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results': [
                        {
                            'date': result['date'],
                            'score': result['score'],
                            'level': result['level'],
                            'reason': result.get('reason', ''),
                            'sizhu': result.get('sizhu', {})
                        }
                        for result in sorted_results
                    ],
                    'content': content
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"分析结果已保存到：{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        日课评分系统使用说明：
        
        1. 选择事项类型：根据需要选择对应的事项类型
        2. 输入日课：可以选择按日期输入或按四柱输入
        3. 填写事主信息：根据事项类型填写相关人员信息
        4. 添加日课：将日课添加到列表中
        5. 日课评分：对当前输入的日课进行评分
        6. 对比分析：对多个日课进行对比分析
        7. 保存分析：保存当前分析结果
        8. 导出报告：导出所有评分结果
        9. 导入文件：从文件导入日期
        
        注意事项：
        - 事主信息为可选，可根据实际情况填写
        - 对比分析需要至少两个日课
        - 保存功能支持文本和JSON格式
        """
        messagebox.showinfo("帮助", help_text)


def main():
    """主函数 - 直接运行日课评分系统"""
    try:
        app = DayScoreWindow()
        app.run()
    except Exception as e:
        import traceback
        print(f"启动错误: {e}")
        traceback.print_exc()
        input("按回车键退出...")


if __name__ == "__main__":
    main()