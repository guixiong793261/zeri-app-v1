# -*- coding: utf-8 -*-
"""
================================================================================
专业级正五行择日软件 - 主程序
================================================================================
【系统概述】
本软件是一款基于传统正五行择日理论的专业择日工具，采用"五行为主，黄道为用"的
双层架构设计，支持嫁娶、安葬、修造、开业等各类民事择日需求。

【核心架构】
1. 第一层（核心筛选）：正五行模块
   - 功能：补龙、扶山、相主，避开三杀、冲山等大忌
   - 作用：系统的"否决权"模块，五行不合格直接淘汰
   - 权重：占评分60%

2. 第二层（优选排序）：大小黄道模块
   - 大黄道：十二神（青龙、明堂、天刑、朱雀、金匮、天德、白虎、玉堂、司命等）
   - 小黄道：十二建星（建、除、满、平、定、执、破、危、成、收、开、闭）
   - 作用：系统的"加分项"，在五行合格基础上优化选择
   - 权重：占评分40%

【评分规则】
- 基础分：100分
- 吉神加分：每个吉神+5~15分（根据重要性）
- 凶神减分：每个凶神-8~20分（根据严重性）
- 宜事加分：每项宜事+10分
- 忌事减分：每项忌事-15分
- 黄道调整：黄道大吉+10分，黑道-5分

【星级等级划分】
⭐⭐⭐⭐⭐ (5星) = 上吉（130分以上）：五行大吉 + 黄道大吉，首选推荐
⭐⭐⭐⭐ (4星) = 大吉（120-129分）：五行大吉，诸事皆宜
⭐⭐⭐ (3星) = 吉（100-119分）：五行合格 + 黄道吉，可用
⭐⭐ (2星) = 中吉/次吉（80-99分）：五行合格但有小忌，可用但需谨慎
⭐ (1星) = 平（60-79分）：五行平平，仅适合小事
❌ (0星) = 凶（<60分）：五行凶或犯大忌，坚决不用

【冲突处理原则】
1. 五行大吉 + 黄道大吉 → ⭐⭐⭐⭐⭐ 上吉（首选）
2. 五行大吉 + 黄道黑道 → ⭐⭐ 次吉（可用，需化解）
3. 五行平平 + 黄道大吉 → ⭐ 平（小事可用）
4. 五行凶 + 任何黄道 → ❌ 凶（坚决不用）

【使用流程】
1. 选择事项类型（嫁娶、安葬、修造等）
2. 设置日期范围（开始日期、结束日期）
3. 输入事主信息（生辰八字，可选）
4. 点击"开始择日"进行计算
5. 查看结果列表，了解每日评分和宜忌
6. 可导出结果或导入日课评分系统进行详细分析

【文件结构】
- 主程序.py：GUI主界面，程序入口
- modules/四柱计算器.py：四柱八字计算（年柱、月柱、日柱、时柱）
- modules/评分器.py：综合评分算法
- modules/黄道.py：黄道吉日计算
- modules/shensha/：各类神煞定义和检查
- modules/rules/：各类事项择日规则
- modules/日课评分系统.py：日课评分和对比分析工具
- modules/日期测试窗口.py：日期计算转换测试窗口

【技术说明】
- 使用tkinter构建GUI界面
- 采用传统历法计算四柱八字
- 支持农历和公历转换
- 内置多种神煞和择日规则
- 可导出JSON格式的择日记录

【注意事项】
1. 本软件计算结果仅供参考，重要事项建议咨询专业择日师
2. 事主信息为可选输入，但提供后可获得更精准的分析
3. 修造类事项需要选择山向和宅型
4. 系统会自动避开明显的大凶之日

【版本信息】
版本: 1.0.0
更新日期: 2026年
作者: 专业择日团队
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import date, datetime, timedelta
import json
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.四柱计算器 import calculate_sizhu, analyze_sizhu, get_lunar_date
from modules.评分器 import calculate_score
from modules.工具函数 import DI_ZHI_WUXING
from modules.喜用神计算器 import calculate_xishen_yongshen
from modules.八字排盘 import BaZiPanPan
from modules.八字可视化模块 import show_bazi_dialog, show_bazi_from_birth, show_bazi_input_dialog
from modules.二十四山 import (
    get_shan_xiang_list, shan_xiang_to_shan, shan_to_shan_xiang,
    SHAN_XIANG_12, SHAN_XIANG_24, ZhengTiWuXingSelectorDB
)
from modules.电子罗盘 import CompassFrame, CompassDialog, show_compass_dialog

# 导入节气计算模块
try:
    import sxtwl
    HAS_SXTWL = True
except ImportError:
    HAS_SXTWL = False

class ZeriApp:
    """择日软件主应用类
    
    功能说明：
    -----------
    1. 事项选择：支持嫁娶、安葬、修造、开业等12类事项
    2. 日期设置：可设置择日的时间范围
    3. 事主信息：支持输入多个事主的生辰八字（年月日时分）
    4. 择日计算：根据正五行理论计算每日吉凶
    5. 结果展示：显示日期、四柱、评分、等级、宜忌等信息
    6. 记录管理：支持保存、查看、导出择日记录
    7. 日课评分：可将结果导入评分系统进行详细分析
    8. 日期测试：日期计算转换测试窗口
    
    使用示例：
    -----------
    >>> root = tk.Tk()
    >>> app = ZeriApp(root)
    >>> root.mainloop()
    """
    
    def __init__(self, root):
        """初始化主应用
        
        Args:
            root: tkinter根窗口
        """
        print("初始化ZeriApp...")
        self.root = root
        self.root.title("专业级正五行择日软件 v1.0")
        
        # 获取屏幕尺寸并设置窗口大小
        print("获取屏幕尺寸...")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 设置为屏幕的90%大小
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        print(f"窗口大小: {window_width}x{window_height}")
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        print(f"窗口位置: {x},{y}")
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        print("设置窗口大小和位置成功")
        
        self.root.state('zoomed')  # 窗口最大化
        print("窗口最大化成功")
        
        # 确保窗口显示
        self.root.deiconify()
        print("窗口显示成功")
        
        # 数据存储
        self.results = []  # 择日结果
        self.records = []  # 历史记录
        self.owners_info = []  # 事主信息
        print("初始化数据存储成功")
        
        # 创建界面
        print("创建菜单栏...")
        self.create_menu()
        print("创建菜单栏成功")
        
        print("创建界面组件...")
        self.create_widgets()
        print("创建界面组件成功")
        
        # 加载历史记录
        print("加载历史记录...")
        self.load_records()
        print("加载历史记录成功")
        
        print("ZeriApp初始化完成")
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出结果", command=self.export_results)
        file_menu.add_command(label="导入文件", command=self.import_file)
        file_menu.add_command(label="查看记录", command=self.view_records)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="八字可视化", command=self.open_bazi_panpan)
        tools_menu.add_separator()
        tools_menu.add_command(label="节气查询", command=self.show_solar_terms)
        tools_menu.add_separator()
        tools_menu.add_command(label="日课评分系统", command=self.open_score_system)
        tools_menu.add_command(label="日期测试窗口", command=self.open_date_test)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_widgets(self):
        """创建主界面组件"""
        # 配置全局样式
        self.configure_styles()
        
        # 创建主滚动区域
        main_canvas = tk.Canvas(self.root, bg="#ffffff")
        main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.main_frame = ttk.Frame(main_canvas, padding="20", style="MainFrame.TFrame")
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=self.root.winfo_screenwidth()-50)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 标题区域
        title_frame = ttk.Frame(self.main_frame, style="TitleFrame.TFrame")
        title_frame.pack(fill=tk.X, pady=8, padx=20)
        
        title_label = ttk.Label(title_frame, text="专业级正五行择日软件", 
                               font=("微软雅黑", 18, "bold"), style="Title.TLabel")
        title_label.pack(pady=4)
        
        subtitle_label = ttk.Label(title_frame, text="精准择日，趋吉避凶", 
                                  font=("微软雅黑", 9), style="Subtitle.TLabel")
        subtitle_label.pack()
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.main_frame, text="择日设置", padding="8")
        input_frame.pack(fill=tk.X, pady=6, padx=20)
        
        # 左侧：择日设置表单
        form_frame = ttk.Frame(input_frame)
        form_frame.grid(row=0, column=0, sticky=tk.W, padx=6)
        
        # 事项选择
        ttk.Label(form_frame, text="事项类型：", font=("微软雅黑", 8, "bold")).grid(row=0, column=0, sticky=tk.W, pady=6, padx=4)
        self.event_var = tk.StringVar(value="嫁娶")
        event_combo = ttk.Combobox(form_frame, textvariable=self.event_var, 
                                   values=["嫁娶", "修造", "动土", "入宅", "开业", 
                                          "出行", "安床", "作灶", "移徙", "入学", "求医",
                                          "签约", "安葬"], width=20, state="readonly", 
                                   font=("微软雅黑", 8))
        event_combo.grid(row=0, column=1, sticky=tk.W, pady=6, padx=9)
        event_combo.bind("<<ComboboxSelected>>", self.on_event_change)
        
        # 日期范围
        ttk.Label(form_frame, text="开始日期：", font=("微软雅黑", 8, "bold")).grid(row=1, column=0, sticky=tk.W, pady=6, padx=4)
        self.start_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        start_entry = ttk.Entry(form_frame, textvariable=self.start_date, width=20, 
                               font=("微软雅黑", 8))
        start_entry.grid(row=1, column=1, sticky=tk.W, pady=6, padx=9)
        
        ttk.Label(form_frame, text="结束日期：", font=("微软雅黑", 8, "bold")).grid(row=1, column=2, sticky=tk.W, pady=6, padx=22)
        end = date.today() + timedelta(days=30)
        self.end_date = tk.StringVar(value=end.strftime("%Y-%m-%d"))
        end_entry = ttk.Entry(form_frame, textvariable=self.end_date, width=20, 
                             font=("微软雅黑", 8))
        end_entry.grid(row=1, column=3, sticky=tk.W, pady=6, padx=9)
        
        # 为日期输入框绑定键盘导航
        self._bind_entry_navigation([start_entry, end_entry])
        
        # 右侧：择日图案显示
        self.pattern_frame = ttk.LabelFrame(input_frame, text="择日图案", padding="6")
        self.pattern_frame.grid(row=0, column=1, sticky=tk.E, padx=(22, 6))
        
        # 创建图案显示画布
        self.pattern_canvas = tk.Canvas(self.pattern_frame, width=120, height=120, bg="#f8f9fa", 
                                       highlightthickness=2, highlightbackground="#007bff")
        self.pattern_canvas.pack(pady=4)
        
        # 初始显示默认图案
        self.update_pattern()
        
        # 绑定事项类型变化事件
        self.event_var.trace_add('write', self.update_pattern)
        
        # 特殊选项（根据事项类型显示）
        self.special_frame = ttk.LabelFrame(self.main_frame, text="特殊选项", padding="8")
        self.special_frame.pack(fill=tk.X, pady=6, padx=20)
        self.update_special_options()
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=8, padx=20)
        
        ttk.Button(button_frame, text="开始择日", command=self.start_calculation, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="日课评分", command=self.open_score_system, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="日期测试", command=self.open_date_test, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="导出结果", command=self.export_results, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="导入文件", command=self.import_file, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="查看记录", command=self.view_records, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="帮助", command=self.show_help, 
                  width=12).pack(side=tk.RIGHT, padx=6)
        
        # 左右分栏区域（事主信息在左，择日结果在右）
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=20)
        
        # 左侧：事主信息
        self.owners_frame = ttk.LabelFrame(content_frame, text="事主信息", padding="20")
        self.owners_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 20))
        self.owners_frame.configure(width=400)
        self.update_owners_frame()
        
        # 右侧：择日结果
        result_frame = ttk.LabelFrame(content_frame, text="择日结果", padding="20")
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # 按钮区域
        result_button_frame = ttk.Frame(result_frame)
        result_button_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(result_button_frame, text="全部导入到评分系统", 
                  command=self.import_all_to_score_system, width=25).pack(side=tk.LEFT, padx=10)
        ttk.Button(result_button_frame, text="清空结果", 
                  command=self.clear_results, width=15).pack(side=tk.LEFT, padx=10)
        
        # 结果列表
        columns = ("日期/四柱", "评分", "等级", "四柱", "月令得分", "喜用神得分", "黄道得分")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        # 设置列宽
        self.result_tree.column("日期/四柱", width=120)
        self.result_tree.column("评分", width=60, anchor=tk.CENTER)
        self.result_tree.column("等级", width=80, anchor=tk.CENTER)
        self.result_tree.column("四柱", width=180)
        self.result_tree.column("月令得分", width=70, anchor=tk.CENTER)
        self.result_tree.column("喜用神得分", width=80, anchor=tk.CENTER)
        self.result_tree.column("黄道得分", width=70, anchor=tk.CENTER)
        
        # 设置列标题
        for col in columns:
            self.result_tree.heading(col, text=col, anchor=tk.CENTER)
        
        # 滚动条
        tree_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # 结果列表包装器
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.result_tree.bind("<Double-1>", self.on_result_double_click)
        
        # 绑定鼠标悬停效果
        self.result_tree.bind("<Motion>", self.on_tree_motion)
        
        # 为不同星级设置行背景色
        self.result_tree.tag_configure('5star', background='#FFF9E6')  # 淡金色背景
        self.result_tree.tag_configure('4star', background='#F0F8FF')  # 淡蓝色背景
        self.result_tree.tag_configure('3star', background='#F0FFF0')  # 淡绿色背景
        self.result_tree.tag_configure('2star', background='#FFF5EE')  # 淡橙色背景
        self.result_tree.tag_configure('1star', background='#F5F5F5')  # 淡灰色背景
    
    def configure_styles(self):
        """配置界面样式"""
        style = ttk.Style()
        
        # 主题设置
        style.theme_use('clam')
        
        # 主框架样式
        style.configure('MainFrame.TFrame', background='#ffffff')
        
        # 标题框架样式
        style.configure('TitleFrame.TFrame', background='#007bff')
        
        # 标题样式
        style.configure('Title.TLabel', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 28, 'bold'))
        
        # 副标题样式
        style.configure('Subtitle.TLabel', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 14))
        
        # 卡片样式
        style.configure('Card.TLabelframe', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 12, 'bold'),
                       borderwidth=2,
                       relief='groove')
        
        # 表单框架样式
        style.configure('Form.TFrame', background='#ffffff')
        
        # 标签样式
        style.configure('Label.TLabel', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 12, 'bold'))
        
        # 输入框样式
        style.configure('Entry.TEntry', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 12),
                       borderwidth=2,
                       relief='solid')
        
        # 下拉框样式
        style.configure('Combobox.TCombobox', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 12),
                       borderwidth=2,
                       relief='solid')
        
        # 按钮框架样式
        style.configure('ButtonFrame.TFrame', background='#ffffff')
        
        # 主按钮样式
        style.configure('Primary.TButton', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 11, 'bold'),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Primary.TButton', 
                  background=[('active', '#0069d9')])
        
        # 次要按钮样式
        style.configure('Secondary.TButton', 
                       background='#6c757d',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Secondary.TButton', 
                  background=[('active', '#5a6268')])
        
        # 信息按钮样式
        style.configure('Info.TButton', 
                       background='#17a2b8',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Info.TButton', 
                  background=[('active', '#138496')])
        
        # 危险按钮样式
        style.configure('Danger.TButton', 
                       background='#dc3545',
                       foreground='white',
                       font=('微软雅黑', 11),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Danger.TButton', 
                  background=[('active', '#c82333')])
        
        # 内容框架样式
        style.configure('ContentFrame.TFrame', background='#ffffff')
        
        # 树形视图样式
        style.configure('Treeview.Treeview', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 10),
                       rowheight=25,
                       fieldbackground='#ffffff',
                       borderwidth=1,
                       relief='solid')
        
        # 树形视图标题样式
        style.configure('Treeview.Heading', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 10, 'bold'),
                       padding=(10, 5))
        
        # 树形视图悬停样式
        style.map('Treeview.Treeview', 
                  background=[('selected', '#cce7ff'), ('!selected', '#ffffff')],
                  foreground=[('selected', '#007bff'), ('!selected', '#333333')])
        
        # 滚动条样式
        style.configure('Scrollbar.Vertical.TScrollbar', 
                       background='#ffffff',
                       troughcolor='#e0e0e0',
                       borderwidth=0)
    
    def on_tree_motion(self, event):
        """树形视图鼠标悬停效果"""
        # 鼠标悬停在树形视图上时的效果
        pass
    
    def update_pattern(self, *args):
        """根据事项类型更新择日图案"""
        event_type = self.event_var.get()
        
        # 清空画布
        self.pattern_canvas.delete("all")
        
        # 中心坐标（画布大小为120×120）
        center_x = 60
        center_y = 60
        
        # 根据事项类型绘制不同的图案
        if event_type == "嫁娶":
            # 绘制双喜图案
            self._draw_double_happiness(center_x, center_y)
        elif event_type == "修造":
            # 绘制建筑图案
            self._draw_construction(center_x, center_y)
        elif event_type == "动土":
            # 绘制土地图案
            self._draw_earth(center_x, center_y)
        elif event_type == "入宅":
            # 绘制房屋图案
            self._draw_house(center_x, center_y)
        elif event_type == "开业":
            # 绘制开业图案
            self._draw_business(center_x, center_y)
        elif event_type == "出行":
            # 绘制出行图案
            self._draw_travel(center_x, center_y)
        elif event_type == "安床":
            # 绘制安床图案
            self._draw_bed(center_x, center_y)
        elif event_type == "作灶":
            # 绘制作灶图案
            self._draw_kitchen(center_x, center_y)
        elif event_type == "移徙":
            # 绘制移徙图案
            self._draw_moving(center_x, center_y)
        elif event_type == "入学":
            # 绘制入学图案
            self._draw_study(center_x, center_y)
        elif event_type == "求医":
            # 绘制求医图案
            self._draw_medical(center_x, center_y)
        elif event_type == "签约":
            # 绘制签约图案
            self._draw_contract(center_x, center_y)
        elif event_type == "安葬":
            # 绘制安葬图案
            self._draw_burial(center_x, center_y)
        else:
            # 默认图案
            self._draw_default_pattern(center_x, center_y)
    
    def _draw_double_happiness(self, x, y):
        """绘制双喜图案"""
        # 红色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ff6b6b")
        
        # 双喜字
        self.pattern_canvas.create_text(x, y, text="囍", font=("微软雅黑", 60, "bold"), fill="red")
    
    def _draw_construction(self, x, y):
        """绘制建筑图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#4ecdc4")
        
        # 建筑物
        self.pattern_canvas.create_rectangle(x-50, y-30, x+50, y+50, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x-60, y-30, x, y-60, x+60, y-30, fill="#ff6b6b")
        
        # 窗户
        self.pattern_canvas.create_rectangle(x-30, y, x-10, y+20, fill="#45b7d1")
        self.pattern_canvas.create_rectangle(x+10, y, x+30, y+20, fill="#45b7d1")
    
    def _draw_earth(self, x, y):
        """绘制土地图案"""
        # 棕色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#8b4513")
        
        # 土地
        self.pattern_canvas.create_rectangle(x-60, y, x+60, y+60, fill="#d2b48c")
        
        # 植物
        self.pattern_canvas.create_line(x-20, y, x-20, y-30, width=3, fill="#228b22")
        self.pattern_canvas.create_line(x, y, x, y-40, width=3, fill="#228b22")
        self.pattern_canvas.create_line(x+20, y, x+20, y-30, width=3, fill="#228b22")
        
        # 树叶
        self.pattern_canvas.create_oval(x-30, y-35, x-10, y-15, fill="#32cd32")
        self.pattern_canvas.create_oval(x-10, y-45, x+10, y-25, fill="#32cd32")
        self.pattern_canvas.create_oval(x+10, y-35, x+30, y-15, fill="#32cd32")
    
    def _draw_house(self, x, y):
        """绘制房屋图案"""
        # 绿色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#4ecdc4")
        
        # 房屋
        self.pattern_canvas.create_rectangle(x-50, y-20, x+50, y+50, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x-60, y-20, x, y-50, x+60, y-20, fill="#ff6b6b")
        
        # 门
        self.pattern_canvas.create_rectangle(x-15, y+10, x+15, y+50, fill="#8b4513")
        
        # 窗户
        self.pattern_canvas.create_rectangle(x-30, y-10, x-10, y+10, fill="#45b7d1")
        self.pattern_canvas.create_rectangle(x+10, y-10, x+30, y+10, fill="#45b7d1")
    
    def _draw_business(self, x, y):
        """绘制开业图案"""
        # 金色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ffd93d")
        
        # 钱袋
        self.pattern_canvas.create_oval(x-40, y-10, x+40, y+50, fill="#8b4513")
        self.pattern_canvas.create_rectangle(x-40, y+10, x+40, y+50, fill="#8b4513")
        
        # 钱币
        self.pattern_canvas.create_oval(x-20, y-30, x-5, y-15, fill="#ffd700")
        self.pattern_canvas.create_oval(x+5, y-30, x+20, y-15, fill="#ffd700")
        self.pattern_canvas.create_oval(x-15, y-20, x-10, y-15, fill="#8b4513")
        self.pattern_canvas.create_oval(x+10, y-20, x+15, y-15, fill="#8b4513")
    
    def _draw_travel(self, x, y):
        """绘制出行图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#45b7d1")
        
        # 交通工具（汽车）
        self.pattern_canvas.create_rectangle(x-40, y, x+30, y+30, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x+30, y, x+40, y-10, x+40, y+40, x+30, y+30, fill="#f7f7f7")
        
        # 车轮
        self.pattern_canvas.create_oval(x-30, y+30, x-10, y+50, fill="#333333")
        self.pattern_canvas.create_oval(x+10, y+30, x+30, y+50, fill="#333333")
        
        # 车窗
        self.pattern_canvas.create_rectangle(x-30, y+5, x+20, y+20, fill="#45b7d1")
    
    def _draw_bed(self, x, y):
        """绘制安床图案"""
        # 紫色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#9b59b6")
        
        # 床
        self.pattern_canvas.create_rectangle(x-50, y+10, x+50, y+50, fill="#f7f7f7")
        self.pattern_canvas.create_rectangle(x-60, y, x+60, y+10, fill="#8b4513")
        
        # 枕头
        self.pattern_canvas.create_rectangle(x-40, y-20, x-10, y+10, fill="#ff6b6b")
        self.pattern_canvas.create_rectangle(x+10, y-20, x+40, y+10, fill="#ff6b6b")
        
        # 被子
        self.pattern_canvas.create_rectangle(x-50, y-10, x+50, y+10, fill="#4ecdc4")
    
    def _draw_kitchen(self, x, y):
        """绘制作灶图案"""
        # 橙色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ff9f43")
        
        # 灶台
        self.pattern_canvas.create_rectangle(x-40, y+10, x+40, y+50, fill="#8b4513")
        
        # 锅
        self.pattern_canvas.create_oval(x-30, y-10, x+30, y+10, fill="#333333")
        
        # 火焰
        self.pattern_canvas.create_polygon(x, y+10, x-10, y+30, x+10, y+30, fill="#ff6b6b")
        self.pattern_canvas.create_polygon(x, y+15, x-8, y+25, x+8, y+25, fill="#ffd93d")
    
    def _draw_moving(self, x, y):
        """绘制移徙图案"""
        # 绿色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#44bd32")
        
        # 箱子
        self.pattern_canvas.create_rectangle(x-40, y-20, x+40, y+40, fill="#f7f7f7")
        self.pattern_canvas.create_rectangle(x-45, y-25, x+45, y-20, fill="#8b4513")
        
        # 提手
        self.pattern_canvas.create_oval(x-15, y-30, x-5, y-20, fill="#333333")
        self.pattern_canvas.create_oval(x+5, y-30, x+15, y-20, fill="#333333")
        
        # 装饰
        self.pattern_canvas.create_line(x-30, y, x+30, y, fill="#333333")
        self.pattern_canvas.create_line(x-30, y+15, x+30, y+15, fill="#333333")
    
    def _draw_study(self, x, y):
        """绘制入学图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#3498db")
        
        # 书本
        self.pattern_canvas.create_rectangle(x-40, y-30, x+40, y+30, fill="#f7f7f7")
        self.pattern_canvas.create_line(x-40, y, x+40, y, fill="#333333")
        
        # 书本页数
        self.pattern_canvas.create_line(x-35, y-25, x+35, y-25, fill="#333333", width=2)
        self.pattern_canvas.create_line(x-35, y-15, x+35, y-15, fill="#333333")
        self.pattern_canvas.create_line(x-35, y+15, x+35, y+15, fill="#333333")
        self.pattern_canvas.create_line(x-35, y+25, x+35, y+25, fill="#333333", width=2)
    
    def _draw_medical(self, x, y):
        """绘制求医图案"""
        # 白色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#f7f7f7")
        
        # 红十字
        self.pattern_canvas.create_rectangle(x-30, y-10, x+30, y+10, fill="#ff6b6b")
        self.pattern_canvas.create_rectangle(x-10, y-30, x+10, y+30, fill="#ff6b6b")
        
        # 医疗标志
        self.pattern_canvas.create_oval(x-40, y-40, x+40, y+40, outline="#3498db", width=3)
    
    def _draw_contract(self, x, y):
        """绘制签约图案"""
        # 黄色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#ffd93d")
        
        # 合同
        self.pattern_canvas.create_rectangle(x-50, y-30, x+50, y+30, fill="#f7f7f7")
        
        # 文字线条
        self.pattern_canvas.create_line(x-40, y-15, x+40, y-15, fill="#333333")
        self.pattern_canvas.create_line(x-40, y, x+40, y, fill="#333333")
        self.pattern_canvas.create_line(x-40, y+15, x+40, y+15, fill="#333333")
        
        # 印章
        self.pattern_canvas.create_oval(x+20, y-20, x+40, y, fill="#ff6b6b")
    
    def _draw_burial(self, x, y):
        """绘制安葬图案"""
        # 灰色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#95a5a6")
        
        # 墓碑
        self.pattern_canvas.create_rectangle(x-30, y-40, x+30, y+20, fill="#f7f7f7")
        
        # 墓基
        self.pattern_canvas.create_rectangle(x-40, y+20, x+40, y+30, fill="#8b4513")
        
        # 十字架
        self.pattern_canvas.create_line(x, y-50, x, y-30, fill="#333333", width=3)
        self.pattern_canvas.create_line(x-15, y-40, x+15, y-40, fill="#333333", width=3)
    
    def _draw_default_pattern(self, x, y):
        """绘制默认图案"""
        # 浅蓝色背景
        self.pattern_canvas.create_oval(x-80, y-80, x+80, y+80, fill="#d1ecf1")
        
        # 日历图标
        self.pattern_canvas.create_rectangle(x-40, y-30, x+40, y+30, fill="#f7f7f7")
        
        # 日历标题
        self.pattern_canvas.create_rectangle(x-40, y-30, x+40, y-15, fill="#3498db")
        
        # 日历日期
        self.pattern_canvas.create_text(x, y+5, text="择日", font=("微软雅黑", 20, "bold"), fill="#333333")
    
    def update_special_options(self):
        """根据事项类型更新特殊选项"""
        # 清空现有组件
        for widget in self.special_frame.winfo_children():
            widget.destroy()
        
        event_type = self.event_var.get()
        special_entries = []
        
        if event_type in ["修造", "动土", "入宅"]:
            # 宅型选择
            ttk.Label(self.special_frame, text="宅型：").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.house_type = tk.StringVar(value="阳宅")
            house_combo = ttk.Combobox(self.special_frame, textvariable=self.house_type, 
                        values=["阳宅", "阴宅"], width=10, state="readonly")
            house_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            special_entries.append(house_combo)
            
            # 山向选择（使用二十四山模块的完整山向列表）
            ttk.Label(self.special_frame, text="山向：").grid(row=0, column=2, sticky=tk.W, padx=5)
            self.shan_xiang = tk.StringVar()
            # 使用二十四山模块获取完整的24山向列表
            shan_xiangs = get_shan_xiang_list(use_24_shan=True)
            shan_combo = ttk.Combobox(self.special_frame, textvariable=self.shan_xiang, 
                        values=shan_xiangs, width=12, state="readonly")
            shan_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
            special_entries.append(shan_combo)
            
            # 兼向选择（改为下拉菜单）
            ttk.Label(self.special_frame, text="兼向：").grid(row=0, column=4, sticky=tk.W, padx=5)
            self.jian_xiang = tk.StringVar()
            self.jian_xiang_combo = ttk.Combobox(self.special_frame, textvariable=self.jian_xiang,
                                                  values=["正中", "兼左", "兼右"], width=10, state="readonly")
            self.jian_xiang_combo.grid(row=0, column=5, sticky=tk.W, padx=5)
            special_entries.append(self.jian_xiang_combo)
            self.jian_xiang.set("正中")  # 默认正中
            # 绑定山向变化时更新兼向选项
            self.shan_xiang.trace_add('write', self._update_jianxiang_options)
            
            # 电子罗盘按钮
            ttk.Button(self.special_frame, text="罗盘", width=6,
                      command=self._show_compass_dialog).grid(row=0, column=6, sticky=tk.W, padx=5)
            
        elif event_type == "作灶":
            ttk.Label(self.special_frame, text="灶向：").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.zao_xiang = tk.StringVar()
            zao_combo = ttk.Combobox(self.special_frame, textvariable=self.zao_xiang, 
                        values=["东", "南", "西", "北", "东南", "东北", "西南", "西北"], 
                        width=10, state="readonly")
            zao_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            special_entries.append(zao_combo)
            
            ttk.Label(self.special_frame, text="灶位：").grid(row=0, column=2, sticky=tk.W, padx=5)
            self.zao_wei = tk.StringVar()
            wei_combo = ttk.Combobox(self.special_frame, textvariable=self.zao_wei, 
                        values=["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"], 
                        width=10, state="readonly")
            wei_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
            special_entries.append(wei_combo)
            
        elif event_type == "安床":
            ttk.Label(self.special_frame, text="床位朝向：").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.chuang_wei = tk.StringVar()
            chuang_combo = ttk.Combobox(self.special_frame, textvariable=self.chuang_wei, 
                        values=["东", "南", "西", "北", "东南", "东北", "西南", "西北"], 
                        width=10, state="readonly")
            chuang_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            special_entries.append(chuang_combo)
        
        # 为特殊选项的输入框绑定键盘导航
        if special_entries:
            self._bind_entry_navigation(special_entries)
    
    def update_owners_frame(self):
        """更新事主信息框架"""
        # 清空现有组件
        for widget in self.owners_frame.winfo_children():
            widget.destroy()
        
        self.owners_info = []
        event_type = self.event_var.get()
        
        # 添加提示标签
        if event_type != "嫁娶":
            hint_label = ttk.Label(self.owners_frame, 
                                   text="（提示：以下事主信息为可选，可根据需要填写）", 
                                   foreground="gray", font=("微软雅黑", 9, "italic"))
            hint_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 根据事项类型确定事主
        if event_type == "嫁娶":
            owners = ["新娘", "新郎"]
        elif event_type == "安葬":
            # 安葬需要死者（逝者）和孝子（家属）
            owners = ["死者", "孝子1", "孝子2", "孝子3"]
        elif event_type in ["修造", "动土", "入宅", "作灶", "开业", "出行", "安床"]:
            owners = ["事主1", "事主2", "事主3", "事主4"]
        else:
            owners = ["事主"]
        
        # 存储所有输入框以便键盘导航
        all_entries = []
        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=3)
            
            # 日期输入行
            date_row = ttk.Frame(owner_frame)
            date_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(date_row, text=f"{owner}:", width=10).pack(side=tk.LEFT, padx=5, pady=2)
            
            # 默认值设置
            if event_type == "嫁娶":
                year_var = tk.StringVar(value=str(date.today().year - 25))
                month_var = tk.StringVar(value=str(1))
                day_var = tk.StringVar(value=str(1))
            else:
                year_var = tk.StringVar()
                month_var = tk.StringVar()
                day_var = tk.StringVar()
            
            hour_var = tk.StringVar(value="12")
            minute_var = tk.StringVar(value="0")
            
            # 性别选择
            if event_type == "嫁娶":
                # 嫁娶事项根据角色默认性别
                gender_var = tk.StringVar(value='女' if owner == '新娘' else '男')
            else:
                # 其他事项默认性别为男
                gender_var = tk.StringVar(value='男')
            
            ttk.Label(date_row, text="性别:").pack(side=tk.LEFT, padx=(10, 0))
            ttk.Radiobutton(date_row, text="男", variable=gender_var, value='男', width=3).pack(side=tk.LEFT, padx=2)
            ttk.Radiobutton(date_row, text="女", variable=gender_var, value='女', width=3).pack(side=tk.LEFT, padx=2)
            
            ttk.Label(date_row, text="年:").pack(side=tk.LEFT)
            year_entry = ttk.Entry(date_row, textvariable=year_var, width=6)
            year_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(year_entry)
            
            ttk.Label(date_row, text="月:").pack(side=tk.LEFT)
            month_entry = ttk.Entry(date_row, textvariable=month_var, width=4)
            month_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(month_entry)
            
            ttk.Label(date_row, text="日:").pack(side=tk.LEFT)
            day_entry = ttk.Entry(date_row, textvariable=day_var, width=4)
            day_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(day_entry)
            
            ttk.Label(date_row, text="时:").pack(side=tk.LEFT)
            hour_entry = ttk.Entry(date_row, textvariable=hour_var, width=4)
            hour_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(hour_entry)
            
            ttk.Label(date_row, text="分:").pack(side=tk.LEFT)
            minute_entry = ttk.Entry(date_row, textvariable=minute_var, width=4)
            minute_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(minute_entry)
            
            # 四柱显示行
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(sizhu_row, text="四柱:", width=10).pack(side=tk.LEFT, padx=5)
            sizhu_var = tk.StringVar(value="未计算")
            ttk.Label(sizhu_row, textvariable=sizhu_var, 
                     font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=5)
            
            # 喜用神显示行
            xishen_var = tk.StringVar(value="")
            yongshen_var = tk.StringVar(value="")
            
            xishen_row = ttk.Frame(owner_frame)
            xishen_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(xishen_row, text="喜神:", width=10).pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, textvariable=xishen_var, foreground="blue").pack(side=tk.LEFT, padx=5)
            ttk.Label(xishen_row, text="  用神:").pack(side=tk.LEFT)
            ttk.Label(xishen_row, textvariable=yongshen_var, foreground="green").pack(side=tk.LEFT, padx=5)
            
            # 夫星子星显示（婚嫁专用）
            fuzi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                fuzi_row = ttk.Frame(owner_frame)
                fuzi_row.pack(fill=tk.X, pady=2)
                
                ttk.Label(fuzi_row, text="夫星/子星:", width=10).pack(side=tk.LEFT, padx=5)
                ttk.Label(fuzi_row, textvariable=fuzi_var, foreground="purple").pack(side=tk.LEFT, padx=5)
            
            # 计算按钮
            calc_btn = ttk.Button(owner_frame, text="计算四柱", 
                                 command=lambda y=year_var, m=month_var, d=day_var, 
                                 h=hour_var, mi=minute_var, g=gender_var, o=owner, s=sizhu_var, 
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var: 
                                 self.calculate_owner_sizhu(y, m, d, h, mi, g, o, s, x, yg, fz))
            calc_btn.pack(side=tk.LEFT, padx=5, pady=2)
            
            # 八字排盘详情按钮
            detail_btn = ttk.Button(owner_frame, text="八字排盘详情", 
                                   command=lambda y=year_var, m=month_var, d=day_var, 
                                   h=hour_var, mi=minute_var, g=gender_var, o=owner: 
                                   self.show_owner_bazi_detail(y, m, d, h, mi, g, o))
            detail_btn.pack(side=tk.LEFT, padx=5, pady=2)
            
            # 保存事主信息
            owner_info = {
                'name': owner,
                'year': year_var,
                'month': month_var,
                'day': day_var,
                'hour': hour_var,
                'minute': minute_var,
                'gender': gender_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var
            }
            self.owners_info.append(owner_info)
        
        # 为所有输入框绑定键盘导航
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
            # Tab键默认就是下一个，不需要额外绑定
            # Shift+Tab键默认就是上一个，不需要额外绑定
    
    def calculate_owner_sizhu(self, year_var, month_var, day_var, hour_var, minute_var, 
                              gender_var, owner, sizhu_var, xishen_var, yongshen_var, fuzi_var):
        """计算事主四柱"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            gender = gender_var.get()
            
            # 使用八字排盘模块获取详细信息
            panpan = BaZiPanPan(year, month, day, hour, minute, gender)
            panpan_result = panpan.get_panpan_result()
            
            # 显示四柱
            sizhu_text = f"{panpan_result['基本信息']['四柱']['年柱']} {panpan_result['基本信息']['四柱']['月柱']} {panpan_result['基本信息']['四柱']['日柱']} {panpan_result['基本信息']['四柱']['时柱']}"
            sizhu_var.set(sizhu_text)
            
            # 显示喜用神 - 使用统一的喜用神计算器
            # 从sizhu中获取天干地支信息
            sizhu_info = {
                'year_gan': panpan_result['基本信息']['四柱']['年柱'][0] if panpan_result['基本信息']['四柱']['年柱'] else '',
                'year_zhi': panpan_result['基本信息']['四柱']['年柱'][1] if len(panpan_result['基本信息']['四柱']['年柱']) > 1 else '',
                'month_gan': panpan_result['基本信息']['四柱']['月柱'][0] if panpan_result['基本信息']['四柱']['月柱'] else '',
                'month_zhi': panpan_result['基本信息']['四柱']['月柱'][1] if len(panpan_result['基本信息']['四柱']['月柱']) > 1 else '',
                'day_gan': panpan_result['基本信息']['四柱']['日柱'][0] if panpan_result['基本信息']['四柱']['日柱'] else '',
                'day_zhi': panpan_result['基本信息']['四柱']['日柱'][1] if len(panpan_result['基本信息']['四柱']['日柱']) > 1 else '',
                'hour_gan': panpan_result['基本信息']['四柱']['时柱'][0] if panpan_result['基本信息']['四柱']['时柱'] else '',
                'hour_zhi': panpan_result['基本信息']['四柱']['时柱'][1] if len(panpan_result['基本信息']['四柱']['时柱']) > 1 else ''
            }
            xishen, yongshen = calculate_xishen_yongshen(sizhu_info)
            xishen_var.set(xishen)
            yongshen_var.set(yongshen)
            
            # 夫星子星（婚嫁专用）
            if self.event_var.get() == "嫁娶" and owner == "新娘":
                # 从八字分析中获取夫星子星信息
                from modules.工具函数 import get_fuzi
                day_gan = sizhu_info['day_gan']
                if day_gan:
                    fuzi_info = get_fuzi(day_gan)
                    fu = fuzi_info.get('fu', '未知')
                    zi = fuzi_info.get('zi', '未知')
                    fuzi_var.set(f"夫星: {fu}, 子星: {zi}")
                else:
                    fuzi_var.set("夫星: 未知, 子星: 未知")
            
            # 保存详细的事主信息到owners_data中
            # 这里可以将panpan_result保存到全局变量中，供后续使用
            # 例如：self.owners_data = panpan_result
            
        except ValueError as e:
            messagebox.showwarning("警告", f"请输入有效的日期时间: {e}")
    
    def show_owner_bazi_detail(self, year_var, month_var, day_var, hour_var, minute_var, gender_var, owner):
        """显示事主八字排盘详情"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            gender = gender_var.get()
            
            # 使用八字排盘模块获取详细信息
            panpan = BaZiPanPan(year, month, day, hour, minute, gender)
            panpan_result = panpan.get_panpan_result()
            
            # 显示八字排盘详情对话框
            show_bazi_dialog(self.root, panpan_result)
            
        except ValueError as e:
            messagebox.showwarning("警告", f"请输入有效的日期时间: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"显示八字排盘详情失败：{str(e)}")
    
    def _show_compass_dialog(self):
        """显示电子罗盘对话框"""
        initial_shan_xiang = None
        if hasattr(self, 'shan_xiang') and self.shan_xiang.get():
            initial_shan_xiang = self.shan_xiang.get()
        
        def on_compass_select(shan_xiang: str, degree: float):
            """罗盘选择回调"""
            if shan_xiang and hasattr(self, 'shan_xiang'):
                self.shan_xiang.set(shan_xiang)
                
                # 更新兼向显示
                if hasattr(self, 'jian_xiang'):
                    # 根据度数自动识别兼向
                    from modules.电子罗盘 import CompassConverter
                    converter = CompassConverter()
                    mountain = shan_xiang_to_shan(shan_xiang)
                    jianxiang = converter.get_jianxiang(mountain, degree)
                    if jianxiang:
                        self.jian_xiang.set(jianxiang)
                    else:
                        self.jian_xiang.set("正中")
        
        show_compass_dialog(self.root, initial_shan_xiang, on_compass_select)
    
    def _update_jianxiang_options(self, *args):
        """根据山向更新兼向选项"""
        shan_xiang = self.shan_xiang.get()
        if not shan_xiang:
            return
        
        # 获取坐山名称
        mountain = shan_xiang_to_shan(shan_xiang)
        
        # 获取相邻的山
        from modules.二十四山 import TWENTY_FOUR_MOUNTAINS_DATA
        mountains = [data[1] for data in TWENTY_FOUR_MOUNTAINS_DATA]
        
        if mountain in mountains:
            idx = mountains.index(mountain)
            left_shan = mountains[(idx - 1) % len(mountains)]
            right_shan = mountains[(idx + 1) % len(mountains)]
            
            # 更新兼向选项
            options = ["正中", f"兼{left_shan}", f"兼{right_shan}"]
            self.jian_xiang_combo['values'] = options
            self.jian_xiang.set("正中")  # 重置为正中
    
    def on_event_change(self, event=None):
        """事项类型改变时的处理"""
        self.update_special_options()
        self.update_owners_frame()
    
    def start_calculation(self):
        """开始择日计算"""
        try:
            # 获取日期范围
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d").date()
            
            if start > end:
                messagebox.showerror("错误", "开始日期不能晚于结束日期")
                return
            
            # 清空之前的结果
            self.results = []
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 获取事主信息
            owners_data = []
            for owner in self.owners_info:
                try:
                    year = int(owner['year'].get())
                    month = int(owner['month'].get())
                    day = int(owner['day'].get())
                    hour = int(owner['hour'].get())
                    minute = int(owner['minute'].get())
                    owners_data.append({
                        'name': owner['name'],
                        'birth_date': date(year, month, day),
                        'birth_hour': hour,
                        'birth_minute': minute
                    })
                except (ValueError, TypeError):
                    pass
            
            # 获取特殊选项
            event_type = self.event_var.get()
            house_type = getattr(self, 'house_type', None)
            shan_xiang = getattr(self, 'shan_xiang', None)
            zao_xiang = getattr(self, 'zao_xiang', None)
            zao_wei = getattr(self, 'zao_wei', None)
            chuang_wei = getattr(self, 'chuang_wei', None)
            
            # 计算每日吉凶
            current = start
            while current <= end:
                # 计算四柱
                sizhu = calculate_sizhu(current, 12, 0)
                
                # 获取农历
                try:
                    lunar = get_lunar_date(current)
                    lunar_str = f"{lunar['月']}{lunar['日']}"
                except:
                    lunar_str = "-"
                
                # 计算评分
                score_result = calculate_score(
                    sizhu, 
                    event_type, 
                    owners_data,
                    house_type.get() if house_type else None,
                    shan_xiang.get() if shan_xiang else None,
                    zao_xiang.get() if zao_xiang else None,
                    zao_wei.get() if zao_wei else None,
                    chuang_wei.get() if chuang_wei else None
                )
                
                # 提取各项得分
                score_details = score_result.get('score_details', {})
                yueling_score = score_details.get('月令得分', 0)
                xishen_score = score_details.get('喜用神得分', 0)
                huangdao_score = score_details.get('黄道得分', 0)
                
                # 保存结果
                result = {
                    'date': current.strftime("%Y-%m-%d"),
                    'lunar': lunar_str,
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'score': score_result['score'],
                    'level': score_result['level'],
                    'yueling_score': yueling_score,
                    'xishen_score': xishen_score,
                    'huangdao_score': huangdao_score,
                    'detail': score_result
                }
                
                # 筛选：只保留吉及以上的日课，过滤掉不吉的日课
                # 等级：❌ 凶 → 过滤掉
                if '❌ 凶' not in result['level']:
                    self.results.append(result)
                    
                    # 根据等级设置行标签（用于颜色区分）
                    level = result['level']
                    if '★★★★★' in level:
                        row_tag = '5star'
                    elif '★★★★' in level:
                        row_tag = '4star'
                    elif '★★★' in level:
                        row_tag = '3star'
                    elif '★★' in level:
                        row_tag = '2star'
                    elif '★' in level:
                        row_tag = '1star'
                    else:
                        row_tag = ''
                    
                    # 添加到树形视图
                    self.result_tree.insert("", tk.END, values=(
                        result['date'],
                        result['score'],
                        result['level'],
                        result['sizhu'],
                        result['yueling_score'],
                        result['xishen_score'],
                        result['huangdao_score']
                    ), tags=(row_tag,))
                
                current += timedelta(days=1)
            
            # 保存到记录
            self.save_record()
            
            messagebox.showinfo("完成", f"择日计算完成！\n共计算 {(end - start).days + 1} 天")
            
        except Exception as e:
            messagebox.showerror("错误", f"计算出错：{str(e)}")
    
    def on_result_double_click(self, event):
        """双击结果查看详情"""
        selected = self.result_tree.selection()
        if not selected:
            return
        
        item = self.result_tree.item(selected[0])
        values = item['values']
        
        # 查找完整结果
        date_str = values[0]
        result = None
        for r in self.results:
            if r['date'] == date_str:
                result = r
                break
        
        if not result:
            return
        
        # 显示详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"日课详情 - {date_str}")
        detail_window.geometry("550x500")
        
        # 创建主框架
        main_frame = ttk.Frame(detail_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文本显示区域
        text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        
        detail = result['detail']
        
        # 插入基本信息
        text.insert(tk.END, f"""
日期：{result['date']}
农历：{result['lunar']}
四柱：{result['sizhu']}
评分：{result['score']} 分
等级：""")
        
        # 如果有星星，用金色显示
        level = result['level']
        if '★' in level:
            star_count = level.count('★')
            other_text = level.replace('★', '').strip()
            text.insert(tk.END, '★' * star_count, "gold_star")
            if other_text:
                text.insert(tk.END, f" {other_text}")
        else:
            text.insert(tk.END, level)
        
        content = f"""

【评分详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        # 显示详细得分
        score_details = detail.get('score_details', {})
        if score_details:
            content += f"  基础分：{score_details.get('基础分', 100)} 分\n"
            content += f"  月令得分：{score_details.get('月令得分', 0):+d} 分\n"
            
            # 月令详细得分
            yueling_detail = score_details.get('月令详细', {})
            if yueling_detail:
                content += f"    └─ 旺衰得分：{yueling_detail.get('旺衰得分', 0):+d} 分\n"
                content += f"    └─ 支支关系得分：{yueling_detail.get('支支关系得分', 0):+d} 分\n"
            
            content += f"  喜用神得分：{score_details.get('喜用神得分', 0):+d} 分\n"
            content += f"  黄道得分：{score_details.get('黄道得分', 0):+d} 分\n"
            content += f"  ─────────────────────────────────\n"
            content += f"  总分：{score_details.get('总分', result['score'])} 分\n"
        else:
            content += "  暂无详细得分数据\n"
        
        content += f"""
【宜】
{chr(10).join(detail['yi_list']) if detail['yi_list'] else '无'}

【忌】
{chr(10).join(detail['ji_list']) if detail['ji_list'] else '无'}

【神煞】
"""
        for shensha in detail['shensha_list']:
            content += f"- {shensha['name']}: {shensha['description']}\n"
        
        content += f"\n【评语】\n{detail['reason']}"
        
        # 添加二十四山分析（如果有山向信息）
        shan_xiang_val = getattr(self, 'shan_xiang', None)
        if shan_xiang_val and shan_xiang_val.get():
            try:
                # 使用二十四山选择器分析
                selector = ZhengTiWuXingSelectorDB()
                shan_name = shan_xiang_to_shan(shan_xiang_val.get())
                sizhu = result['sizhu'].split()
                if len(sizhu) >= 4:
                    year_gz = sizhu[0]
                    month_gz = sizhu[1]
                    day_gz = sizhu[2]
                    hour_gz = sizhu[3]
                    
                    # 获取兼向
                    jianxiang = ""
                    if hasattr(self, 'jian_xiang'):
                        jianxiang = self.jian_xiang.get()
                    
                    # 使用分金五行评价
                    if jianxiang and jianxiang != "正中":
                        result_fengjin = selector.evaluate_with_fengjin(
                            shan_name, jianxiang, year_gz, month_gz, day_gz, hour_gz,
                            use_fengjin_wuxing=True
                        )
                        
                        content += f"\n\n【分金五行分析】\n"
                        content += f"山向：{shan_xiang_val.get()}（坐山：{shan_name}）\n"
                        content += f"兼向：{jianxiang}\n"
                        content += f"分金：第{result_fengjin.get('fengjin_index', '?')}分金（{result_fengjin.get('fengjin_ganzhi', '?')}）\n"
                        content += f"分金五行：{result_fengjin.get('fengjin_wuxing', '?')}（{result_fengjin.get('nayin_name', '?')}）\n"
                        content += f"正体五行：{result_fengjin.get('zhengti_wuxing', '?')}\n"
                        content += f"等级：{result_fengjin.get('level', '?')}\n"
                        content += f"得分：{result_fengjin.get('score', '?')}\n"
                        if result_fengjin.get('details'):
                            content += f"详情：\n"
                            for d in result_fengjin['details']:
                                content += f"  {d}\n"
                    else:
                        # 正向使用正体五行
                        level, score, detail_24 = selector.evaluate_by_name(
                            shan_name, year_gz, month_gz, day_gz, hour_gz
                        )
                        
                        content += f"\n\n【正体五行分析】\n"
                        content += f"山向：{shan_xiang_val.get()}（坐山：{shan_name}）\n"
                        content += f"兼向：正中（正向）\n"
                        content += f"等级：{level}\n"
                        content += f"得分：{score}\n"
                        if 'summary' in detail_24:
                            summary = detail_24['summary']
                            content += f"坐山得分：{summary.get('mountain_score', 'N/A')}\n"
            except Exception as e:
                content += f"\n\n【二十四山分析】\n分析出错：{str(e)}\n"
        
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_detail():
            """保存日课详情"""
            file_path = filedialog.asksaveasfilename(
                title="保存日课详情",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            try:
                # 保存为文本文件
                if file_path.endswith('.txt'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("成功", f"日课详情已保存到：{file_path}")
                
                # 保存为JSON文件
                elif file_path.endswith('.json'):
                    json_data = {
                        'date': result['date'],
                        'lunar': result['lunar'],
                        'sizhu': result['sizhu'],
                        'score': result['score'],
                        'level': result['level'],
                        'yi_list': detail['yi_list'],
                        'ji_list': detail['ji_list'],
                        'shensha_list': detail['shensha_list'],
                        'reason': detail['reason']
                    }
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("成功", f"日课详情已保存到：{file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")
        
        ttk.Button(button_frame, text="保存详情", command=save_detail).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=detail_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def export_results(self):
        """导出结果"""
        if not self.results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="导出择日结果"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                # 导出JSON格式
                export_data = {
                    'event_type': self.event_var.get(),
                    'start_date': self.start_date.get(),
                    'end_date': self.end_date.get(),
                    'results': self.results
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                # 导出文本格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("择日结果报告\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"事项类型：{self.event_var.get()}\n")
                    f.write(f"日期范围：{self.start_date.get()} 至 {self.end_date.get()}\n\n")
                    
                    # 按评分排序
                    sorted_results = sorted(self.results, key=lambda x: x['score'], reverse=True)
                    
                    for result in sorted_results:
                        f.write(f"日期：{result['date']}\n")
                        f.write(f"农历：{result['lunar']}\n")
                        f.write(f"四柱：{result['sizhu']}\n")
                        f.write(f"评分：{result['score']} 分\n")
                        f.write(f"等级：{result['level']}\n")
                        f.write(f"宜：{result['yi']}\n")
                        f.write(f"忌：{result['ji']}\n")
                        f.write("-" * 40 + "\n\n")
            
            messagebox.showinfo("成功", f"结果已导出到：\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def import_file(self):
        """导入文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="导入择日结果文件"
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
                        self.results = data['results']
                        self.event_var.set(data.get('event_type', '嫁娶'))
                        self.start_date.set(data.get('start_date', ''))
                        self.end_date.set(data.get('end_date', ''))
                        imported_count = len(self.results)
                        
                        # 刷新显示
                        for item in self.result_tree.get_children():
                            self.result_tree.delete(item)
                        
                        for result in self.results:
                            self.result_tree.insert("", tk.END, values=(
                                result['date'],
                                result.get('lunar', '-'),
                                result['sizhu'],
                                result.get('score', '-'),
                                result.get('level', '-'),
                                result.get('yi', '-'),
                                result.get('ji', '-')
                            ))
                    
                    # 处理其他JSON格式（如评分系统导出的）
                    elif isinstance(data, list):
                        self.results = []
                        for item in data:
                            if isinstance(item, dict) and 'date' in item:
                                # 构建标准格式
                                result = {
                                    'date': item['date'],
                                    'lunar': item.get('lunar', '-'),
                                    'sizhu': item.get('sizhu', '-'),
                                    'score': item.get('score', 0),
                                    'level': item.get('level', '-'),
                                    'yi': item.get('yi', '-'),
                                    'ji': item.get('ji', '-'),
                                    'detail': item.get('detail', {})
                                }
                                self.results.append(result)
                                imported_count += 1
                        
                        # 刷新显示
                        for item in self.result_tree.get_children():
                            self.result_tree.delete(item)
                        
                        for result in self.results:
                            self.result_tree.insert("", tk.END, values=(
                                result['date'],
                                result.get('lunar', '-'),
                                result['sizhu'],
                                result.get('score', '-'),
                                result.get('level', '-'),
                                result.get('yi', '-'),
                                result.get('ji', '-')
                            ))
            
            else:
                # 导入文本格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # 尝试解析文本格式
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        # 尝试匹配日期格式 (YYYY-MM-DD)
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                        if date_match:
                            date_str = date_match.group(1)
                            # 检查是否已存在
                            if not any(r['date'] == date_str for r in self.results):
                                result = {
                                    'date': date_str,
                                    'lunar': '-',
                                    'sizhu': '-',
                                    'score': '-',
                                    'level': '-',
                                    'yi': '-',
                                    'ji': '-',
                                    'detail': {}
                                }
                                self.results.append(result)
                                imported_count += 1
                    
                    # 刷新显示
                    for item in self.result_tree.get_children():
                        self.result_tree.delete(item)
                    
                    for result in self.results:
                        self.result_tree.insert("", tk.END, values=(
                            result['date'],
                            result.get('lunar', '-'),
                            result['sizhu'],
                            result.get('score', '-'),
                            result.get('level', '-'),
                            result.get('yi', '-'),
                            result.get('ji', '-')
                        ))
            
            if imported_count > 0:
                messagebox.showinfo("成功", f"已导入 {imported_count} 条记录")
            else:
                messagebox.showwarning("提示", "未找到可导入的记录，请检查文件格式")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")
    
    def view_records(self):
        """查看历史记录"""
        records_window = tk.Toplevel(self.root)
        records_window.title("历史记录")
        records_window.geometry("600x400")
        
        text = scrolledtext.ScrolledText(records_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        if not self.records:
            text.insert(tk.END, "暂无历史记录")
        else:
            for i, record in enumerate(self.records, 1):
                text.insert(tk.END, f"\n【记录 {i}】\n")
                text.insert(tk.END, f"时间：{record.get('time', '未知')}\n")
                text.insert(tk.END, f"事项：{record.get('event', '未知')}\n")
                text.insert(tk.END, f"日期范围：{record.get('start', '')} 至 {record.get('end', '')}\n")
                text.insert(tk.END, f"结果数量：{record.get('count', 0)} 天\n")
                text.insert(tk.END, "-" * 40 + "\n")
        
        text.config(state=tk.DISABLED)
    
    def save_record(self):
        """保存记录"""
        record = {
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'event': self.event_var.get(),
            'start': self.start_date.get(),
            'end': self.end_date.get(),
            'count': len(self.results)
        }
        self.records.append(record)
        
        # 保存到文件
        try:
            with open("择日记录.json", 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记录失败：{e}")
    
    def load_records(self):
        """加载历史记录"""
        try:
            if os.path.exists("择日记录.json"):
                with open("择日记录.json", 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
        except Exception as e:
            print(f"加载记录失败：{e}")
    
    def open_score_system(self):
        """打开日课评分系统"""
        try:
            from modules.日课评分系统 import DayScoreWindow
            score_window = DayScoreWindow()
            
            # 如果有当前结果，导入到评分系统
            if self.results:
                owners_data = []
                for owner in self.owners_info:
                    try:
                        owners_data.append({
                            'year': int(owner['year'].get()),
                            'month': int(owner['month'].get()),
                            'day': int(owner['day'].get()),
                            'hour': int(owner['hour'].get()),
                            'minute': int(owner['minute'].get())
                        })
                    except:
                        pass
                
                score_window.import_results(
                    self.results,
                    self.event_var.get(),
                    owners_data
                )
            
            score_window.run()
        except Exception as e:
            messagebox.showerror("错误", f"打开评分系统失败：{str(e)}")
    
    def import_all_to_score_system(self):
        """将所有择日结果导入到评分系统"""
        if not self.results:
            messagebox.showwarning("提示", "没有可导入的择日结果")
            return
        
        try:
            from modules.日课评分系统 import DayScoreWindow
            score_window = DayScoreWindow()
            
            # 准备事主数据
            owners_data = []
            for owner in self.owners_info:
                try:
                    owners_data.append({
                        'year': int(owner['year'].get()),
                        'month': int(owner['month'].get()),
                        'day': int(owner['day'].get()),
                        'hour': int(owner['hour'].get()),
                        'minute': int(owner['minute'].get())
                    })
                except:
                    pass
            
            # 导入结果
            score_window.import_results(
                self.results,
                self.event_var.get(),
                owners_data
            )
            
            score_window.run()
        except Exception as e:
            messagebox.showerror("错误", f"导入到评分系统失败：{str(e)}")
    
    def clear_results(self):
        """清空择日结果"""
        if not self.results:
            return
        
        if messagebox.askyesno("确认", "确定要清空所有择日结果吗？"):
            self.results = []
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            messagebox.showinfo("成功", "择日结果已清空")


    def open_date_test(self):
        """打开日期测试窗口"""
        try:
            from modules.日期测试窗口 import DateTestWindow
            DateTestWindow(parent=self.root)
        except Exception as e:
            messagebox.showerror("错误", f"打开日期测试窗口失败：{str(e)}")
    
    def open_bazi_panpan(self):
        """打开八字排盘"""
        try:
            # 测试show_bazi_input_dialog是否存在
            print("开始调用show_bazi_input_dialog")
            show_bazi_input_dialog(self.root)
            print("show_bazi_input_dialog调用成功")
        except Exception as e:
            print(f"错误：{str(e)}")
            messagebox.showerror("错误", f"打开八字排盘失败：{str(e)}")
    
    def show_help(self):
        """显示帮助文档"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("800x600")
        
        # 创建 Notebook
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 帮助内容
        help_sections = [
            ("系统概述", """
【系统概述】

本软件是一款基于传统正五行择日理论的专业择日工具。

【核心特点】
1. 双层架构：正五行审核 + 黄道优选
2. 智能评分：基础分100分，根据神煞、宜忌自动加减
3. 多事项支持：13类常见民事择日
4. 事主分析：支持八字输入，相主分析
5. 详细报告：宜忌、神煞、评分、等级一应俱全

【星级等级】
⭐⭐⭐⭐⭐ (5星) = 上吉 - 首选推荐
⭐⭐⭐⭐ (4星) = 大吉 - 诸事皆宜
⭐⭐⭐ (3星) = 吉 - 可用
⭐⭐ (2星) = 中吉/次吉 - 需谨慎
⭐ (1星) = 平 - 仅适合小事
❌ (0星) = 凶 - 坚决不用
"""),
            ("使用流程", """
【基本使用流程】

1. 选择事项类型
   从下拉框选择需要择日的事项（嫁娶、安葬、修造等）

2. 设置日期范围
   输入开始日期和结束日期（格式：YYYY-MM-DD）

3. 输入事主信息（可选但推荐）
   填写事主的出生年月日时分
   点击"计算四柱"查看八字和喜用神
   婚嫁事项会显示夫星子星

4. 特殊选项
   修造类：选择宅型和山向
   作灶：选择灶向和灶位
   安床：选择床位朝向

5. 开始择日
   点击"开始择日"按钮
   系统会计算日期范围内的每日吉凶

6. 查看结果
   结果按日期显示在列表中
   双击可查看详细信息

7. 导出或评分
   点击"导出结果"保存为文本或JSON文件
   点击"日课评分"进行详细分析
   点击"日期测试"查看日期转换信息
"""),
            ("评分规则", """
【评分算法】

基础分：100分

神煞加减分：
  大吉神（+15分）：天德、月德等
  吉神（+10分）：青龙、明堂等
  小吉神（+5分）：福星、禄神等
  小凶神（-8分）：劫煞、灾煞等
  凶神（-15分）：五黄、三杀等
  大凶神（-20分）：岁破、月破等

宜忌加减分：
  宜事匹配：+10分/项
  忌事冲突：-15分/项

黄道调整：
  大黄道吉：+10分
  大黄道凶：-5分

【星级标准】
⭐⭐⭐⭐⭐ (5星) = 上吉（130分以上）
⭐⭐⭐⭐ (4星) = 大吉（120-129分）
⭐⭐⭐ (3星) = 吉（100-119分）
⭐⭐ (2星) = 中吉/次吉（80-99分）
⭐ (1星) = 平（60-79分）
❌ (0星) = 凶（<60分）
"""),
            ("注意事项", """
【注意事项】

1. 计算精度
   - 四柱计算精确到分钟
   - 节气交接时刻会影响月柱

2. 地域差异
   - 不同流派有不同算法
   - 本软件采用传统通用算法

3. 使用建议
   - 重要事项建议多方验证
   - 软件结果仅供参考

4. 数据备份
   - 定期备份择日记录
   - 记录文件：择日记录.json

5. 冲突处理
   - 五行大吉 + 黄道大吉 → 首选
   - 五行大吉 + 黄道黑道 → 可用
   - 五行平平 + 黄道大吉 → 小事可用
   - 五行凶 + 任何黄道 → 坚决不用

6. 事主信息
   - 婚嫁：新娘新郎信息必填
   - 安葬：死者信息必填
   - 其他事项：事主信息可选
""")
        ]
        
        for title, content in help_sections:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=title)
            
            text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, padx=10, pady=10)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, content)
            text.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)
    
    def show_solar_terms(self):
        """显示节气查询对话框"""
        if not HAS_SXTWL:
            messagebox.showwarning("警告", "sxtwl库未安装，无法查询节气信息")
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("节气查询")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 年份选择
        input_frame = ttk.Frame(dialog, padding="20")
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="选择年份:", font=('微软雅黑', 12)).pack(side=tk.LEFT, padx=5)
        
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(input_frame, textvariable=year_var, width=10, font=('微软雅黑', 12))
        year_combo['values'] = [str(y) for y in range(1900, 2101)]
        year_combo.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = ttk.Frame(dialog, padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ("节气", "公历日期", "时间", "月柱")
        tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=20)
        
        tree.column("节气", width=80, anchor=tk.CENTER)
        tree.column("公历日期", width=120, anchor=tk.CENTER)
        tree.column("时间", width=100, anchor=tk.CENTER)
        tree.column("月柱", width=80, anchor=tk.CENTER)
        
        for col in columns:
            tree.heading(col, text=col, anchor=tk.CENTER)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def update_solar_terms():
            """更新节气显示"""
            try:
                year = int(year_var.get())
                
                # 清空树形视图
                for item in tree.get_children():
                    tree.delete(item)
                
                # 获取节气数据
                jq_list = sxtwl.getJieQiByYear(year)
                jq_names = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
                           '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
                           '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
                           '立冬', '小雪', '大雪', '冬至', '小寒', '大寒']
                
                # 月的地支对应
                jie_to_month = {
                    0: '寅', 2: '卯', 4: '辰', 6: '巳', 8: '午', 10: '未',
                    12: '申', 14: '酉', 16: '戌', 18: '亥', 20: '子', 22: '丑',
                }
                
                # 五虎遁
                wu_hu_dun = {
                    '甲': '丙', '己': '丙',
                    '乙': '戊', '庚': '戊',
                    '丙': '庚', '辛': '庚',
                    '丁': '壬', '壬': '壬',
                    '戊': '甲', '癸': '甲'
                }
                
                tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
                di_zhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                
                # 获取年干
                day_obj = sxtwl.fromSolar(year, 6, 15)  # 年中日期
                year_gz = day_obj.getYearGZ()
                year_gan = tian_gan[year_gz.tg]
                
                # 添加到树形视图
                for i in range(24):
                    dd = sxtwl.JD2DD(jq_list[i].jd)
                    date_str = f"{int(dd.Y)}-{int(dd.M):02d}-{int(dd.D):02d}"
                    time_str = f"{int(dd.h):02d}:{int(dd.m):02d}:{int(dd.s):02d}"
                    
                    # 计算月柱（只对"节"计算）
                    if i in jie_to_month:
                        month_zhi = jie_to_month[i]
                        base_gan = wu_hu_dun.get(year_gan, '丙')
                        base_index = tian_gan.index(base_gan)
                        month_zhi_index = di_zhi.index(month_zhi)
                        offset = (month_zhi_index - 2 + 12) % 12
                        month_gan_index = (base_index + offset) % 10
                        month_gan = tian_gan[month_gan_index]
                        month_pillar = f"{month_gan}{month_zhi}"
                    else:
                        month_pillar = "-"
                    
                    tree.insert("", tk.END, values=(jq_names[i], date_str, time_str, month_pillar))
                
            except Exception as e:
                messagebox.showerror("错误", f"查询失败：{str(e)}")
        
        # 查询按钮
        ttk.Button(input_frame, text="查询", command=update_solar_terms).pack(side=tk.LEFT, padx=10)
        
        # 关闭按钮
        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)
        
        # 初始加载
        update_solar_terms()
    
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", 
            "专业级正五行择日软件 v1.0\n\n"
            "基于传统正五行择日理论\n"
            "采用'五行为主，黄道为用'架构\n\n"
            "功能特点：\n"
            "- 支持13类事项择日\n"
            "- 智能评分和星级显示\n"
            "- 事主八字分析\n"
            "- 日课评分对比\n"
            "- 节气查询\n"
            "- 日期转换测试\n\n"
            "版本: 1.0.0\n"
            "更新日期: 2026年\n"
            "作者: 专业择日团队"
        )

def main():
    """主函数"""
    print("开始启动程序...")
    try:
        print("创建根窗口...")
        root = tk.Tk()
        print(f"根窗口创建成功: {root}")
        root.title("专业级正五行择日软件")
        print("创建应用实例...")
        app = ZeriApp(root)
        print(f"应用实例创建成功: {app}")
        print("进入主循环...")
        root.mainloop()
    except Exception as e:
        import traceback
        print(f"启动错误: {e}")
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
