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
5. 婚嫁择日需提供新娘新郎的完整出生信息（含日柱）以计算夫子星
6. 造葬择日使用动态计算的山方煞、克山运、星曜煞等函数，更准确
7. 静态数据中的山方煞、克山运仅供参考，建议以动态计算为准

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
from modules.评分器 import calculate_score, Scorer
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
        file_menu.add_command(label="保存事主信息", command=self.save_owners_info)
        file_menu.add_command(label="加载事主信息", command=self.load_owners_info)
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
        
        # 创建主滚动区域 - 添加水平和垂直滚动条
        main_frame_container = ttk.Frame(self.root)
        main_frame_container.pack(fill=tk.BOTH, expand=True)
        
        main_canvas = tk.Canvas(main_frame_container, bg="#ffffff")
        v_scrollbar = ttk.Scrollbar(main_frame_container, orient="vertical", command=main_canvas.yview)
        h_scrollbar = ttk.Scrollbar(main_frame_container, orient="horizontal", command=main_canvas.xview)
        
        self.main_frame = ttk.Frame(main_canvas, padding="10", style="MainFrame.TFrame")
        
        # 配置滚动
        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        # 创建窗口并保存ID
        window_id = main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # 绑定窗口大小变化事件，动态调整Canvas宽度
        def on_window_resize(event):
            canvas_width = main_frame_container.winfo_width() - 40  # 进一步缩小宽度
            if canvas_width > 0:
                main_canvas.itemconfig(window_id, width=canvas_width)
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # 绑定窗口大小变化事件
        main_frame_container.bind("<Configure>", on_window_resize)
        
        # 配置Canvas和滚动条
        main_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 配置滚动条样式 - 增大三角按键
        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar", 
                       arrowsize=20,  # 增大垂直滚动条箭头大小
                       width=20)     # 增大滚动条宽度
        style.configure("Custom.Horizontal.TScrollbar", 
                       arrowsize=20,  # 增大水平滚动条箭头大小
                       width=20)     # 增大滚动条宽度
        
        # 应用自定义样式
        v_scrollbar.configure(style="Custom.Vertical.TScrollbar")
        h_scrollbar.configure(style="Custom.Horizontal.TScrollbar")
        
        # 布局 - 调整滚动条位置，使其更容易触摸
        main_canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 5))  # 右边留出空间
        v_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5))    # 垂直滚动条向左移动
        h_scrollbar.grid(row=1, column=0, sticky="ew", pady=(5, 0))    # 水平滚动条向上移动
        
        # 配置网格权重
        main_frame_container.grid_rowconfigure(0, weight=1)
        main_frame_container.grid_columnconfigure(0, weight=1)
        
        # 绑定鼠标滚轮（垂直滚动）
        main_canvas.bind("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        # 绑定Shift+鼠标滚轮（水平滚动）
        main_canvas.bind("<Shift-MouseWheel>", lambda e: main_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 添加触摸移动功能
        self._touch_start_x = 0
        self._touch_start_y = 0
        self._touch_start_scroll_x = 0
        self._touch_start_scroll_y = 0
        
        # 绑定触摸事件
        main_canvas.bind("<Button-1>", self._on_touch_start)
        main_canvas.bind("<B1-Motion>", self._on_touch_move)
        
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
        
        # 输出方式选择
        ttk.Label(form_frame, text="输出方式：", font=("微软雅黑", 8, "bold")).grid(row=0, column=2, sticky=tk.W, pady=6, padx=22)
        self.output_mode_var = tk.StringVar(value="全部显示")
        output_mode_combo = ttk.Combobox(form_frame, textvariable=self.output_mode_var, 
                                         values=["全部显示", "仅显示无扣分"], width=20, state="readonly", 
                                         font=("微软雅黑", 8))
        output_mode_combo.grid(row=0, column=3, sticky=tk.W, pady=6, padx=9)
        
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
        
        ttk.Button(button_frame, text="分析年份", command=self.analyze_year, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="分析月份", command=self.analyze_month, 
                  width=12).pack(side=tk.LEFT, padx=6)
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
        
        # 上下布局区域（事主信息在上，择日结果在下）
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # 上方：事主信息
        self.owners_frame = ttk.LabelFrame(content_frame, text="事主信息", padding="10")
        self.owners_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10), padx=5)
        self.update_owners_frame()
        
        # 下方：择日结果
        result_frame = ttk.LabelFrame(content_frame, text="择日结果", padding="10")
        result_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(10, 0), padx=5)

        # 输出模式选择区域
        output_mode_frame = ttk.Frame(result_frame)
        output_mode_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(output_mode_frame, text="输出模式：", font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=(0, 8))

        self.output_mode_var = tk.StringVar(value="normal")
        output_mode_radio_frame = ttk.Frame(output_mode_frame)
        output_mode_radio_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 垂直排列单选按钮，适应屏幕
        ttk.Radiobutton(output_mode_radio_frame, text="正常平分（含扣分）",
                       variable=self.output_mode_var, value="normal").pack(side=tk.TOP, anchor=tk.W, pady=2)
        ttk.Radiobutton(output_mode_radio_frame, text="无扣分输出（各项满分）",
                       variable=self.output_mode_var, value="nodeduct").pack(side=tk.TOP, anchor=tk.W, pady=2)

        # 按钮区域
        result_button_frame = ttk.Frame(result_frame)
        result_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 垂直排列按钮，适应屏幕
        ttk.Button(result_button_frame, text="全部导入到评分系统", 
                  command=self.import_all_to_score_system, width=25).pack(side=tk.TOP, pady=2, fill=tk.X)
        ttk.Button(result_button_frame, text="清空结果", 
                  command=self.clear_results, width=25).pack(side=tk.TOP, pady=2, fill=tk.X)
        
        # 结果列表包装器 - 使用网格布局
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 结果列表
        columns = ("日期/四柱", "评分", "等级", "四柱", "五行得分", "月令得分", "喜用神得分", "黄道得分", "地支关系", "吉神信息", "利月", "事主信息")
        self.result_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        # 设置列宽 - 适应屏幕
        self.result_tree.column("日期/四柱", width=80)
        self.result_tree.column("评分", width=35, anchor=tk.CENTER)
        self.result_tree.column("等级", width=40, anchor=tk.CENTER)
        self.result_tree.column("四柱", width=100)
        self.result_tree.column("五行得分", width=45, anchor=tk.CENTER)
        self.result_tree.column("月令得分", width=45, anchor=tk.CENTER)
        self.result_tree.column("喜用神得分", width=50, anchor=tk.CENTER)
        self.result_tree.column("黄道得分", width=45, anchor=tk.CENTER)
        self.result_tree.column("地支关系", width=80)
        self.result_tree.column("吉神信息", width=80)
        self.result_tree.column("利月", width=45, anchor=tk.CENTER)
        self.result_tree.column("事主信息", width=100)
        
        # 设置列标题
        for col in columns:
            self.result_tree.heading(col, text=col, anchor=tk.CENTER)
        
        # 滚动条 - 添加垂直和水平滚动条
        tree_v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.result_tree.yview)
        tree_h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=tree_v_scrollbar.set, xscrollcommand=tree_h_scrollbar.set)
        
        # 使用网格布局 - 调整滚动条位置，使其更容易触摸
        self.result_tree.grid(row=0, column=0, sticky="nsew", padx=(0, 5))  # 右边留出空间
        tree_v_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5))    # 垂直滚动条向左移动
        tree_h_scrollbar.grid(row=1, column=0, sticky="ew", pady=(5, 0))    # 水平滚动条向上移动
        
        # 配置网格权重
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定双击事件
        self.result_tree.bind("<Double-1>", self.on_result_double_click)
        
        # 绑定鼠标悬停效果
        self.result_tree.bind("<Motion>", self.on_tree_motion)
        
        # 绑定触摸事件到结果树
        self.result_tree.bind("<Button-1>", self._on_tree_touch_start)
        self.result_tree.bind("<B1-Motion>", self._on_tree_touch_move)
        self.result_tree.bind("<ButtonRelease-1>", self._on_tree_touch_end)
        
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
        
        # 存储所有输入框以便键盘导航
        all_entries = []
        
        # 方案名称行
        plan_row = ttk.Frame(self.owners_frame)
        plan_row.pack(fill=tk.X, pady=2)
        ttk.Label(plan_row, text="方案名称:").pack(side=tk.LEFT, padx=5)
        self.plan_name_var = tk.StringVar(value="")
        plan_entry = ttk.Entry(plan_row, textvariable=self.plan_name_var, width=20)
        plan_entry.pack(side=tk.LEFT, padx=2)
        all_entries.append(plan_entry)

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
            owners = ["死者", "孝子1", "孝子2", "孝子3"]
        elif event_type in ["修造", "动土", "入宅", "作灶", "开业", "出行", "安床"]:
            owners = ["事主1", "事主2", "事主3", "事主4"]
        else:
            owners = ["事主"]
        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=3)
            
            # 日期输入行
            date_row = ttk.Frame(owner_frame)
            date_row.pack(fill=tk.X, pady=2)
            
            # 姓名输入框（可编辑）
            name_var = tk.StringVar(value=owner)
            ttk.Label(date_row, text="姓名:").pack(side=tk.LEFT, padx=5, pady=2)
            name_entry = ttk.Entry(date_row, textvariable=name_var, width=8)
            name_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(name_entry)
            
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
            
            # 公历/农历切换
            calendar_type_var = tk.StringVar(value='solar')  # 'solar' 或 'lunar'
            ttk.Label(date_row, text="日历:").pack(side=tk.LEFT, padx=(10, 0))
            ttk.Radiobutton(date_row, text="公历", variable=calendar_type_var, value='solar', width=4).pack(side=tk.LEFT, padx=1)
            ttk.Radiobutton(date_row, text="农历", variable=calendar_type_var, value='lunar', width=4).pack(side=tk.LEFT, padx=1)
            
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
            
            # 生肖显示
            zodiac_var = tk.StringVar(value="")
            ttk.Label(sizhu_row, text="生肖:").pack(side=tk.LEFT, padx=(20, 0))
            ttk.Label(sizhu_row, textvariable=zodiac_var, 
                     font=("微软雅黑", 10, "bold"), foreground="blue").pack(side=tk.LEFT, padx=2)
            
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
            fu_xing_var = tk.StringVar(value="")
            zi_xing_var = tk.StringVar(value="")
            fuzi_var = tk.StringVar(value="")
            yintai_var = tk.StringVar(value="")
            yangqi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                # 夫星显示
                fu_xing_row = ttk.Frame(owner_frame)
                fu_xing_row.pack(fill=tk.X, pady=2)
                
                ttk.Label(fu_xing_row, text="夫星:", width=10).pack(side=tk.LEFT, padx=5)
                ttk.Label(fu_xing_row, textvariable=fu_xing_var, foreground="purple").pack(side=tk.LEFT, padx=5)
                
                # 子星显示
                zi_xing_row = ttk.Frame(owner_frame)
                zi_xing_row.pack(fill=tk.X, pady=2)
                
                ttk.Label(zi_xing_row, text="子星:", width=10).pack(side=tk.LEFT, padx=5)
                ttk.Label(zi_xing_row, textvariable=zi_xing_var, foreground="purple").pack(side=tk.LEFT, padx=5)
                
                # 阴胎阳气显示（仅新娘）
                if owner == "新娘":
                    yintai_row = ttk.Frame(owner_frame)
                    yintai_row.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(yintai_row, text="阴胎:", width=10).pack(side=tk.LEFT, padx=5)
                    ttk.Label(yintai_row, textvariable=yintai_var, foreground="green").pack(side=tk.LEFT, padx=5)
                    
                    yangqi_row = ttk.Frame(owner_frame)
                    yangqi_row.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(yangqi_row, text="阳气:", width=10).pack(side=tk.LEFT, padx=5)
                    ttk.Label(yangqi_row, textvariable=yangqi_var, foreground="red").pack(side=tk.LEFT, padx=5)
                    
                    # 保存为实例变量，供calculate_owner_sizhu方法使用
                    self.yintai_var = yintai_var
                    self.yangqi_var = yangqi_var
            
            # 计算按钮
            calc_btn = ttk.Button(owner_frame, text="计算四柱", 
                                 command=lambda y=year_var, m=month_var, d=day_var, 
                                 h=hour_var, mi=minute_var, g=gender_var, o=owner, s=sizhu_var, 
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var, yt=yintai_var, yq=yangqi_var,
                                 ct=calendar_type_var, z=zodiac_var, fx=fu_xing_var, zx=zi_xing_var: 
                                 self.calculate_owner_sizhu(y, m, d, h, mi, g, o, s, x, yg, fz, yt, yq, ct, z, fx, zx))
            calc_btn.pack(side=tk.LEFT, padx=5, pady=2)
             
             # 八字排盘详情按钮
            detail_btn = ttk.Button(owner_frame, text="八字排盘详情", 
                                   command=lambda y=year_var, m=month_var, d=day_var, 
                                   h=hour_var, mi=minute_var, g=gender_var, o=owner: 
                                   self.show_owner_bazi_detail(y, m, d, h, mi, g, o))
            detail_btn.pack(side=tk.LEFT, padx=5, pady=2)
            
            # 保存事主信息
            owner_info = {
                'name': name_var,
                'role': owner,
                'year': year_var,
                'month': month_var,
                'day': day_var,
                'hour': hour_var,
                'minute': minute_var,
                'gender': gender_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var,
                'yintai_var': yintai_var,
                'yangqi_var': yangqi_var
            }
            self.owners_info.append(owner_info)
        
        # 为所有输入框绑定键盘导航
        self._bind_entry_navigation(all_entries)
    
    def analyze_year(self):
        """分析年份吉凶"""
        try:
            # 获取事项类型
            event_type = self.event_var.get()
            
            # 获取事主信息
            owners = []
            for owner_info in self.owners_info:
                try:
                    # 添加防御性检查
                    year_str = owner_info['year'].get() if hasattr(owner_info['year'], 'get') else owner_info.get('year', '')
                    month_str = owner_info['month'].get() if hasattr(owner_info['month'], 'get') else owner_info.get('month', '')
                    day_str = owner_info['day'].get() if hasattr(owner_info['day'], 'get') else owner_info.get('day', '')
                    
                    # 检查是否填写了日期（年、月、日都必须填写）
                    if not (year_str and month_str and day_str):
                        continue
                    
                    hour_str = owner_info['hour'].get() if hasattr(owner_info['hour'], 'get') else owner_info.get('hour', '12')
                    minute_str = owner_info['minute'].get() if hasattr(owner_info['minute'], 'get') else owner_info.get('minute', '0')
                    gender = owner_info['gender'].get() if hasattr(owner_info['gender'], 'get') else owner_info.get('gender', '')
                    
                    year = int(year_str)
                    month = int(month_str)
                    day = int(day_str)
                    hour = int(hour_str)
                    minute = int(minute_str)
                    
                    name = owner_info['name'].get() if hasattr(owner_info['name'], 'get') else owner_info.get('name', '')
                    role = owner_info.get('role', '')
                    
                    # 检查日期有效性
                    try:
                        birth_date = date(year, month, day)
                    except ValueError as e:
                        # 处理无效日期，使用当月最后一天
                        import calendar
                        last_day = calendar.monthrange(year, month)[1]
                        birth_date = date(year, month, last_day)
                    
                    owner = {
                        'name': name,
                        'role': role,
                        'birth_date': birth_date,
                        'birth_hour': hour,
                        'birth_minute': minute,
                        '性别': gender
                    }
                    owners.append(owner)
                except (ValueError, AttributeError):
                    # 跳过未填写的事主或格式错误的事主
                    pass
            
            # 获取年份范围
            start_date_str = self.start_date.get()
            end_date_str = self.end_date.get()
            
            # 解析日期字符串获取年份
            try:
                start_year = int(start_date_str.split('-')[0])
                end_year = int(end_date_str.split('-')[0])
            except (IndexError, ValueError):
                messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
                return
            
            if start_year > end_year:
                messagebox.showerror("错误", "开始年份不能大于结束年份")
                return
            
            # 获取山向信息
            shan_xiang = getattr(self, 'shan_xiang', None)
            shan_xiang_value = shan_xiang.get() if shan_xiang else None
            
            # 获取兼向信息
            jian_xiang = getattr(self, 'jian_xiang', None)
            jian_xiang_value = jian_xiang.get() if jian_xiang else None
            
            # 创建评分器
            scorer = Scorer()
            
            # 分析年份
            results = []
            for year in range(start_year, end_year + 1):
                analysis = scorer.analyze_year(year, event_type, owners, shan_xiang_value, jian_xiang_value)
                results.append(analysis)
            
            # 显示年份分析结果
            self.show_year_analysis(results)
            
        except Exception as e:
            messagebox.showwarning("警告", f"分析年份时出错: {e}")
    
    def show_year_analysis(self, results):
        """显示年份分析结果"""
        # 创建结果窗口
        window = tk.Toplevel(self.root)
        window.title("年份分析结果")
        window.geometry("800x600")
        window.resizable(True, True)
        
        # 创建结果表格
        frame = ttk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        tree = ttk.Treeview(frame, columns=("year", "year_gz", "level", "score", "suitable", "reasons"), show="headings")
        
        # 设置列标题
        tree.heading("year", text="年份")
        tree.heading("year_gz", text="干支")
        tree.heading("level", text="等级")
        tree.heading("score", text="分数")
        tree.heading("suitable", text="是否适合")
        tree.heading("reasons", text="原因")
        
        # 设置列宽 - 压缩前面列宽，给原因列更多空间
        tree.column("year", width=60)
        tree.column("year_gz", width=60)
        tree.column("level", width=50)
        tree.column("score", width=50)
        tree.column("suitable", width=60)
        tree.column("reasons", width=450)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加数据
        for result in results:
            suitable = "是" if result['suitable'] else "否"
            reasons = "; ".join(result['reasons']) if result['reasons'] else "无"
            
            tree.insert("", tk.END, values=(
                result['year'],
                result['year_gz'],
                result['level'],
                result['score'],
                suitable,
                reasons
            ))
        
        # 添加选择按钮
        button_frame = ttk.Frame(window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_select():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                year = int(item['values'][0])
                # 更新主界面的年份范围
                # 设置开始日期和结束日期为该年的1月1日到12月31日
                self.start_date.set(f"{year}-01-01")
                self.end_date.set(f"{year}-12-31")
                window.destroy()
                # 自动进入月份分析
                self.analyze_month()
            else:
                messagebox.showinfo("提示", "请选择一个年份")
        
        ttk.Button(button_frame, text="选择此年份并分析月份", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def analyze_month(self):
        """分析月份吉凶"""
        try:
            # 获取事项类型
            event_type = self.event_var.get()
            
            # 获取事主信息
            owners = []
            for owner_info in self.owners_info:
                try:
                    # 添加防御性检查
                    year_str = owner_info['year'].get() if hasattr(owner_info['year'], 'get') else owner_info.get('year', '')
                    month_str = owner_info['month'].get() if hasattr(owner_info['month'], 'get') else owner_info.get('month', '')
                    day_str = owner_info['day'].get() if hasattr(owner_info['day'], 'get') else owner_info.get('day', '')
                    
                    # 检查是否填写了日期（年、月、日都必须填写）
                    if not (year_str and month_str and day_str):
                        continue
                    
                    hour_str = owner_info['hour'].get() if hasattr(owner_info['hour'], 'get') else owner_info.get('hour', '12')
                    minute_str = owner_info['minute'].get() if hasattr(owner_info['minute'], 'get') else owner_info.get('minute', '0')
                    gender = owner_info['gender'].get() if hasattr(owner_info['gender'], 'get') else owner_info.get('gender', '')
                    
                    year = int(year_str)
                    month = int(month_str)
                    day = int(day_str)
                    hour = int(hour_str)
                    minute = int(minute_str)
                    
                    name = owner_info['name'].get() if hasattr(owner_info['name'], 'get') else owner_info.get('name', '')
                    role = owner_info.get('role', '')
                    
                    # 检查日期有效性
                    try:
                        birth_date = date(year, month, day)
                    except ValueError as e:
                        # 处理无效日期，使用当月最后一天
                        import calendar
                        last_day = calendar.monthrange(year, month)[1]
                        birth_date = date(year, month, last_day)
                    
                    owner = {
                        'name': name,
                        'role': role,
                        'birth_date': birth_date,
                        'birth_hour': hour,
                        'birth_minute': minute,
                        '性别': gender
                    }
                    owners.append(owner)
                except (ValueError, AttributeError):
                    # 跳过未填写的事主或格式错误的事主
                    pass
            
            # 获取年份
            start_date_str = self.start_date.get()
            try:
                year = int(start_date_str.split('-')[0])
            except (IndexError, ValueError):
                messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
                return
            
            # 获取山向信息
            shan_xiang = getattr(self, 'shan_xiang', None)
            shan_xiang_value = shan_xiang.get() if shan_xiang else None
            
            # 创建评分器
            scorer = Scorer()
            
            # 分析月份
            results = []
            for month in range(1, 13):
                analysis = scorer.analyze_month(year, month, event_type, owners, shan_xiang_value)
                results.append(analysis)
            
            # 显示月份分析结果
            self.show_month_analysis(results, year)
            
        except ValueError as e:
            messagebox.showwarning("警告", f"请输入有效的年份: {e}")
    
    def show_month_analysis(self, results, year):
        """显示月份分析结果"""
        # 创建结果窗口
        window = tk.Toplevel(self.root)
        window.title(f"{year}年月份分析结果")
        window.geometry("800x600")
        window.resizable(True, True)
        
        # 创建结果表格
        frame = ttk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        tree = ttk.Treeview(frame, columns=("month", "month_gz", "level", "score", "suitable", "reasons"), show="headings")
        
        # 设置列标题
        tree.heading("month", text="月份")
        tree.heading("month_gz", text="干支")
        tree.heading("level", text="等级")
        tree.heading("score", text="分数")
        tree.heading("suitable", text="是否适合")
        tree.heading("reasons", text="原因")
        
        # 设置列宽 - 压缩前面列宽，给原因列更多空间
        tree.column("month", width=50)
        tree.column("month_gz", width=60)
        tree.column("level", width=50)
        tree.column("score", width=50)
        tree.column("suitable", width=60)
        tree.column("reasons", width=480)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加数据
        for result in results:
            suitable = "是" if result['suitable'] else "否"
            reasons = "; ".join(result['reasons']) if result['reasons'] else "无"
            
            tree.insert("", tk.END, values=(
                result['month'],
                result['month_gz'],
                result['level'],
                result['score'],
                suitable,
                reasons
            ))
        
        # 添加选择按钮
        button_frame = ttk.Frame(window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_select():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                month = int(item['values'][0])
                # 更新主界面的日期范围
                # 设置日期为该月的1日到最后一日
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                self.start_date.set(f"{year}-{month:02d}-01")
                self.end_date.set(f"{year}-{month:02d}-{last_day:02d}")
                window.destroy()
                # 自动开始择日计算
                self.start_calculation()
            else:
                messagebox.showinfo("提示", "请选择一个月份")
        
        ttk.Button(button_frame, text="选择此月份并开始择日", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=window.destroy).pack(side=tk.RIGHT, padx=5)
    
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

    def save_owners_info(self):
        """保存事主信息到JSON文件（支持多方案）"""
        import json
        import os
        
        plan_name = self.plan_name_var.get().strip()
        if not plan_name:
            messagebox.showwarning("提示", "请先输入方案名称再保存")
            return
        
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        file_path = os.path.join(data_dir, 'owners_plans.json')
        
        # 读取已有方案
        all_plans = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_plans = json.load(f)
            except:
                all_plans = {}
        
        # 提取当前事主信息
        save_data = []
        for owner_info in self.owners_info:
            # 添加防御性检查
            name = owner_info['name'].get() if hasattr(owner_info['name'], 'get') else owner_info.get('name', '')
            year = owner_info['year'].get() if hasattr(owner_info['year'], 'get') else owner_info.get('year', '')
            month = owner_info['month'].get() if hasattr(owner_info['month'], 'get') else owner_info.get('month', '')
            day = owner_info['day'].get() if hasattr(owner_info['day'], 'get') else owner_info.get('day', '')
            hour = owner_info['hour'].get() if hasattr(owner_info['hour'], 'get') else owner_info.get('hour', '')
            minute = owner_info['minute'].get() if hasattr(owner_info['minute'], 'get') else owner_info.get('minute', '')
            gender = owner_info['gender'].get() if hasattr(owner_info['gender'], 'get') else owner_info.get('gender', '')
            sizhu = owner_info['sizhu_var'].get() if hasattr(owner_info['sizhu_var'], 'get') else owner_info.get('sizhu_var', '')
            xishen = owner_info['xishen_var'].get() if hasattr(owner_info['xishen_var'], 'get') else owner_info.get('xishen_var', '')
            yongshen = owner_info['yongshen_var'].get() if hasattr(owner_info['yongshen_var'], 'get') else owner_info.get('yongshen_var', '')
            fuzi = owner_info['fuzi_var'].get() if hasattr(owner_info['fuzi_var'], 'get') else owner_info.get('fuzi_var', '')
            
            owner_data = {
                'name': name,
                'role': owner_info.get('role', ''),
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'minute': minute,
                'gender': gender,
                'sizhu': sizhu,
                'xishen': xishen,
                'yongshen': yongshen,
                'fuzi': fuzi
            }
            save_data.append(owner_data)
        
        # 以事项类型+方案名称为key保存
        event_type = self.event_var.get()
        plan_key = f"{event_type}__{plan_name}"
        all_plans[plan_key] = {
            'event_type': event_type,
            'plan_name': plan_name,
            'owners': save_data
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_plans, f, ensure_ascii=False, indent=2)
            existing_count = len([k for k in all_plans if k.startswith(f"{event_type}__")])
            messagebox.showinfo("保存成功", f"方案「{plan_name}」已保存\n当前{event_type}类共有 {existing_count} 个方案")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存事主信息时出错：{e}")

    def load_owners_info(self):
        """从JSON文件加载事主信息（弹出方案选择窗口）"""
        import json
        import os
        
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        file_path = os.path.join(data_dir, 'owners_plans.json')
        
        if not os.path.exists(file_path):
            messagebox.showinfo("提示", "没有找到保存的事主信息文件")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_plans = json.load(f)
        except Exception as e:
            messagebox.showerror("加载失败", f"读取文件出错：{e}")
            return
        
        if not all_plans:
            messagebox.showinfo("提示", "没有已保存的方案")
            return
        
        # 弹出方案选择窗口
        select_win = tk.Toplevel(self.root)
        select_win.title("选择要加载的方案")
        select_win.geometry("450x400")
        select_win.transient(self.root)
        select_win.grab_set()
        
        ttk.Label(select_win, text="已保存的方案列表：", font=("微软雅黑", 11, "bold")).pack(pady=10)
        
        # 列表框
        list_frame = ttk.Frame(select_win)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        plan_listbox = tk.Listbox(list_frame, font=("微软雅黑", 10), yscrollcommand=scrollbar.set)
        plan_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=plan_listbox.yview)
        
        # 按当前事项类型过滤并显示
        event_type = self.event_var.get()
        current_plans = []
        other_plans = []
        for key, plan_data in all_plans.items():
            if plan_data.get('event_type') == event_type:
                current_plans.append((key, plan_data))
            else:
                other_plans.append((key, plan_data))
        
        if current_plans:
            plan_listbox.insert(tk.END, f"--- {event_type}类方案 ---")
            for key, plan_data in current_plans:
                owners_count = len(plan_data.get('owners', []))
                plan_listbox.insert(tk.END, f"  {plan_data['plan_name']}（{owners_count}个事主）")
        
        if other_plans:
            plan_listbox.insert(tk.END, f"--- 其他事项方案 ---")
            for key, plan_data in other_plans:
                owners_count = len(plan_data.get('owners', []))
                plan_listbox.insert(tk.END, f"  [{plan_data.get('event_type', '')}] {plan_data['plan_name']}（{owners_count}个事主）")
        
        # 按钮区域
        btn_frame = ttk.Frame(select_win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_load():
            selection = plan_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请选择一个方案", parent=select_win)
                return
            
            idx = selection[0]
            # 计算实际方案索引（跳过分隔行）
            actual_idx = 0
            all_items = list(all_plans.items())
            for i, (key, plan_data) in enumerate(all_items):
                if plan_data.get('event_type') == event_type:
                    actual_idx = i
                    break
            
            # 找到选中的方案
            selected_idx = idx
            display_items = []
            if current_plans:
                display_items.append(None)  # 分隔行
                for k, p in current_plans:
                    display_items.append((k, p))
            if other_plans:
                display_items.append(None)  # 分隔行
                for k, p in other_plans:
                    display_items.append((k, p))
            
            selected_item = display_items[selected_idx]
            if selected_item is None:
                messagebox.showwarning("提示", "请选择具体的方案（非分隔行）", parent=select_win)
                return
            
            plan_key, plan_data = selected_item
            self._apply_loaded_plan(plan_data)
            select_win.destroy()
        
        def on_delete():
            selection = plan_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请选择一个方案", parent=select_win)
                return
            
            idx = selection[0]
            display_items = []
            if current_plans:
                display_items.append(None)
                for k, p in current_plans:
                    display_items.append((k, p))
            if other_plans:
                display_items.append(None)
                for k, p in other_plans:
                    display_items.append((k, p))
            
            selected_item = display_items[idx]
            if selected_item is None:
                return
            
            plan_key, plan_data = selected_item
            result = messagebox.askyesno("确认删除", f"确定要删除方案「{plan_data['plan_name']}」吗？", parent=select_win)
            if result:
                del all_plans[plan_key]
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(all_plans, f, ensure_ascii=False, indent=2)
                    select_win.destroy()
                    self.load_owners_info()
                except Exception as e:
                    messagebox.showerror("删除失败", f"删除方案时出错：{e}", parent=select_win)
        
        ttk.Button(btn_frame, text="加载选中方案", command=on_load).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中方案", command=on_delete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=select_win.destroy).pack(side=tk.RIGHT, padx=5)

    def _apply_loaded_plan(self, plan_data):
        """将加载的方案应用到界面"""
        # 切换事项类型（如果不同）
        loaded_event = plan_data.get('event_type', '')
        if loaded_event and loaded_event != self.event_var.get():
            self.event_var.set(loaded_event)
            self.update_owners_frame()
        
        # 设置方案名称
        self.plan_name_var.set(plan_data.get('plan_name', ''))
        
        # 填充事主信息
        load_data = plan_data.get('owners', [])
        for i, owner_data in enumerate(load_data):
            if i < len(self.owners_info):
                owner_info = self.owners_info[i]
                owner_info['name'].set(owner_data.get('name', ''))
                owner_info['year'].set(owner_data.get('year', ''))
                owner_info['month'].set(owner_data.get('month', ''))
                owner_info['day'].set(owner_data.get('day', ''))
                owner_info['hour'].set(owner_data.get('hour', ''))
                owner_info['minute'].set(owner_data.get('minute', ''))
                owner_info['gender'].set(owner_data.get('gender', '男'))
                owner_info['sizhu_var'].set(owner_data.get('sizhu', '未计算'))
                owner_info['xishen_var'].set(owner_data.get('xishen', ''))
                owner_info['yongshen_var'].set(owner_data.get('yongshen', ''))
                owner_info['fuzi_var'].set(owner_data.get('fuzi', ''))
        
        messagebox.showinfo("加载成功", f"方案「{plan_data.get('plan_name', '')}」已加载")

    def calculate_owner_sizhu(self, year_var, month_var, day_var, hour_var, minute_var, 
                              gender_var, owner, sizhu_var, xishen_var, yongshen_var, fuzi_var, 
                              yintai_var=None, yangqi_var=None, calendar_type_var=None, zodiac_var=None,
                              fu_xing_var=None, zi_xing_var=None):
        """计算事主四柱"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            gender = gender_var.get()
            
            # 判断是公历还是农历 - 添加防御性检查
            calendar_type = 'solar'
            if calendar_type_var and hasattr(calendar_type_var, 'get'):
                calendar_type = calendar_type_var.get()
            
            if calendar_type == 'lunar':
                # 农历转公历
                from modules.高精度农历转换 import get_lunar_converter
                converter = get_lunar_converter()
                solar_date = converter.lunar_to_solar(year, month, day, hour, minute, 0)
                year = solar_date['year']
                month = solar_date['month']
                day = solar_date['day']
            
            # 使用八字排盘模块获取详细信息
            panpan = BaZiPanPan(year, month, day, hour, minute, gender)
            panpan_result = panpan.get_panpan_result()
            
            # 显示四柱
            sizhu_text = f"{panpan_result['四柱']['年柱']} {panpan_result['四柱']['月柱']} {panpan_result['四柱']['日柱']} {panpan_result['四柱']['时柱']}"
            sizhu_var.set(sizhu_text)
            
            # 显示生肖 - 添加防御性检查
            if zodiac_var and hasattr(zodiac_var, 'set'):
                year_zhi = panpan_result['四柱']['年柱'][1] if len(panpan_result['四柱']['年柱']) > 1 else ''
                zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                             '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
                zodiac = zodiac_map.get(year_zhi, '')
                zodiac_var.set(zodiac)
            
            # 显示喜用神 - 使用统一的喜用神计算器
            # 从sizhu中获取天干地支信息
            sizhu_info = {
                'year_gan': panpan_result['四柱']['年柱'][0] if panpan_result['四柱']['年柱'] else '',
                'year_zhi': panpan_result['四柱']['年柱'][1] if len(panpan_result['四柱']['年柱']) > 1 else '',
                'month_gan': panpan_result['四柱']['月柱'][0] if panpan_result['四柱']['月柱'] else '',
                'month_zhi': panpan_result['四柱']['月柱'][1] if len(panpan_result['四柱']['月柱']) > 1 else '',
                'day_gan': panpan_result['四柱']['日柱'][0] if panpan_result['四柱']['日柱'] else '',
                'day_zhi': panpan_result['四柱']['日柱'][1] if len(panpan_result['四柱']['日柱']) > 1 else '',
                'hour_gan': panpan_result['四柱']['时柱'][0] if panpan_result['四柱']['时柱'] else '',
                'hour_zhi': panpan_result['四柱']['时柱'][1] if len(panpan_result['四柱']['时柱']) > 1 else ''
            }
            xishen, yongshen = calculate_xishen_yongshen(sizhu_info)
            xishen_var.set(xishen)
            yongshen_var.set(yongshen)
            
            # 夫星子星（婚嫁专用）
            if self.event_var.get() == "嫁娶" and owner == "新娘":
                # 从八字分析中获取夫星子星信息
                from modules.工具函数 import get_fuzi, get_yintai, get_yangqi
                year_gan = sizhu_info['year_gan']
                year_zhi = sizhu_info['year_zhi']
                month_gan = sizhu_info.get('month_gan', '甲')
                month_zhi = sizhu_info.get('month_zhi', '子')
                if year_gan and year_zhi:
                    # 计算夫星子星（基于年干年支）
                    fuzi_info = get_fuzi(year_gan, year_zhi)
                    fu = fuzi_info.get('fu', '未知')
                    zi = fuzi_info.get('zi', '未知')
                    if fu_xing_var and hasattr(fu_xing_var, 'set'):
                        fu_xing_var.set(fu)
                    if zi_xing_var and hasattr(zi_xing_var, 'set'):
                        zi_xing_var.set(zi)
                    
                    # 计算阴胎（以新娘月柱为基准）
                    yintai = get_yintai(month_gan, month_zhi)
                    
                    # 计算阳气（以新郎月柱为基准）
                    yangqi = '未知'
                    for owner_info in self.owners_info:
                        if owner_info.get('role') == '新郎':
                            groom_month_gan = ''
                            groom_month_zhi = ''
                            if 'sizhu_var' in owner_info and hasattr(owner_info['sizhu_var'], 'get'):
                                groom_sizhu = owner_info['sizhu_var'].get()
                                if groom_sizhu:
                                    # 解析月柱：格式为"年柱 月柱 日柱 时柱"
                                    parts = groom_sizhu.split()
                                    if len(parts) >= 2:
                                        groom_month = parts[1]
                                        groom_month_gan = groom_month[:1]
                                        groom_month_zhi = groom_month[1:] if len(groom_month) > 1 else ''
                            if groom_month_gan and groom_month_zhi:
                                yangqi = get_yangqi(groom_month_gan, groom_month_zhi)
                            break
                    
                    # 显示阴胎和阳气
                    if yintai_var and hasattr(yintai_var, 'set'):
                        yintai_var.set(f"阴胎: {yintai if yintai else '未知'}")
                    if yangqi_var and hasattr(yangqi_var, 'set'):
                        yangqi_var.set(f"阳气: {yangqi if yangqi else '未知'}")
                else:
                    if fu_xing_var and hasattr(fu_xing_var, 'set'):
                        fu_xing_var.set("未知")
                    if zi_xing_var and hasattr(zi_xing_var, 'set'):
                        zi_xing_var.set("未知")
                    if yintai_var and hasattr(yintai_var, 'set'):
                        yintai_var.set("阴胎: 未知")
                    if yangqi_var and hasattr(yangqi_var, 'set'):
                        yangqi_var.set("阳气: 未知")
            
            # 保存详细的事主信息到owners_data中
            # 这里可以将panpan_result保存到全局变量中，供后续使用
            # 例如：self.owners_data = panpan_result
            
        except ValueError as e:
            messagebox.showwarning("警告", f"请输入有效的日期时间: {e}")
        except Exception as e:
            messagebox.showwarning("警告", f"日期转换失败: {e}")
    
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
                    # 添加防御性检查
                    year_str = owner['year'].get() if hasattr(owner['year'], 'get') else owner.get('year', '')
                    month_str = owner['month'].get() if hasattr(owner['month'], 'get') else owner.get('month', '')
                    day_str = owner['day'].get() if hasattr(owner['day'], 'get') else owner.get('day', '')
                    
                    # 检查是否填写了日期
                    if not (year_str and month_str and day_str):
                        continue
                    
                    hour_str = owner['hour'].get() if hasattr(owner['hour'], 'get') else owner.get('hour', '12')
                    minute_str = owner['minute'].get() if hasattr(owner['minute'], 'get') else owner.get('minute', '0')
                    
                    year = int(year_str)
                    month = int(month_str)
                    day = int(day_str)
                    hour = int(hour_str)
                    minute = int(minute_str)
                    gender = owner['gender'].get() if hasattr(owner['gender'], 'get') else owner.get('gender', '')
                    
                    # 计算年干支
                    try:
                        birth_date = date(year, month, day)
                    except ValueError as e:
                        # 处理无效日期，使用当月最后一天
                        import calendar
                        last_day = calendar.monthrange(year, month)[1]
                        birth_date = date(year, month, last_day)
                        messagebox.showwarning("日期修正", f"您输入的日期 {year}-{month}-{day} 无效，已自动修正为 {year}-{month}-{last_day}")
                    
                    owner_sizhu = calculate_sizhu(birth_date, hour, minute)
                    year_gan = owner_sizhu.get('year_gan', '')
                    year_zhi = owner_sizhu.get('year_zhi', '')
                    
                    # 获取日柱信息（用于婚嫁评分算法）
                    day_gan = owner_sizhu.get('day_gan', '')
                    day_zhi = owner_sizhu.get('day_zhi', '')
                    
                    # 构建完整的事主信息
                    name = owner['name'].get() if hasattr(owner['name'], 'get') else owner.get('name', '')
                    owner_data = {
                        'name': name,
                        'role': owner.get('role', ''),
                        'birth_date': birth_date,
                        'birth_hour': hour,
                        'birth_minute': minute,
                        '性别': gender,
                        '年干': year_gan,
                        '年支': year_zhi,
                        '日干': day_gan,
                        '日支': day_zhi,
                        '生肖': year_zhi
                    }
                    
                    # 如果有喜用神信息，也添加进去
                    if 'xishen_var' in owner:
                        xishen_val = owner['xishen_var'].get() if hasattr(owner['xishen_var'], 'get') else owner.get('xishen_var', '')
                        if xishen_val:
                            owner_data['xishen'] = xishen_val
                    if 'yongshen_var' in owner:
                        yongshen_val = owner['yongshen_var'].get() if hasattr(owner['yongshen_var'], 'get') else owner.get('yongshen_var', '')
                        if yongshen_val:
                            owner_data['yongshen'] = yongshen_val
                    
                    owners_data.append(owner_data)
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
                
                # 添加公历年份、月份和日期到sizhu，用于月份分析
                sizhu['year'] = current.year
                sizhu['month'] = current.month
                sizhu['day'] = current.day
                sizhu['date'] = current  # 添加date键，用于规则检查
                
                # 获取农历
                try:
                    lunar = get_lunar_date(current)
                    lunar_str = f"{lunar['month']}{lunar['day']}"
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
                wuxing_score = score_details.get('五行评分', 100)
                yueling_score = score_details.get('月令得分', 0)
                xishen_score = score_details.get('喜用神得分', 0)
                huangdao_score = score_details.get('黄道得分', 0)
                
                # 提取地支关系和吉神信息
                wu_xing_result = score_result.get('wu_xing_result', {})
                wu_xing_details = wu_xing_result.get('details', {})
                dizhi_relations = wu_xing_details.get('地支关系', [])
                jishen_list = wu_xing_details.get('吉神', [])
                
                # 格式化地支关系文本
                if dizhi_relations:
                    import re
                    dizhi_text_list = []
                    for relation in dizhi_relations:
                        if '三合' in relation:
                            match = re.search(r'三合(.)局', relation)
                            if match:
                                dizhi_text_list.append(f"三合{match.group(1)}局")
                            else:
                                dizhi_text_list.append('三合')
                        elif '六合' in relation:
                            dizhi_text_list.append('六合')
                        elif '六冲' in relation:
                            dizhi_text_list.append('六冲')
                        elif '六害' in relation:
                            dizhi_text_list.append('六害')
                        elif '三刑' in relation:
                            dizhi_text_list.append('三刑')
                        elif '相破' in relation:
                            dizhi_text_list.append('相破')
                        else:
                            dizhi_text_list.append(relation[:10])
                    dizhi_text = ', '.join(dizhi_text_list[:2])
                else:
                    dizhi_text = '-'
                
                # 格式化吉神信息文本
                if jishen_list:
                    jishen_text_list = []
                    for jishen in jishen_list:
                        if '天德贵人' in jishen:
                            jishen_text_list.append('天德贵人')
                        elif '月德贵人' in jishen:
                            jishen_text_list.append('月德贵人')
                        elif '天乙贵人' in jishen:
                            jishen_text_list.append('天乙贵人')
                        elif '文昌贵人' in jishen:
                            jishen_text_list.append('文昌贵人')
                        elif '禄神' in jishen:
                            jishen_text_list.append('禄神')
                        elif '福星' in jishen:
                            jishen_text_list.append('福星')
                        else:
                            jishen_text_list.append(jishen[:6])
                    jishen_text = ', '.join(jishen_text_list[:2])
                else:
                    jishen_text = '-'
                
                # 提取大利月/小利月信息（婚嫁专用）
                daliyue_text = '-'
                if event_type in ['嫁娶', '订婚', '纳采']:
                    shensha_list = score_result.get('shensha_list', [])
                    for shensha in shensha_list:
                        if isinstance(shensha, dict):
                            shensha_name = shensha.get('name', '')
                            if shensha_name == '大利月':
                                daliyue_text = '大利月'
                                break
                            elif shensha_name == '小利月':
                                daliyue_text = '小利月'
                                break
                
                # 构建事主信息文本
                owner_text = []
                for i, owner in enumerate(self.owners_info[:3], 1):  # 只显示前3个事主
                    name = ''
                    if 'name' in owner:
                        name = owner['name'].get() if hasattr(owner['name'], 'get') else owner.get('name', '')
                    elif '姓名' in owner:
                        name = owner['姓名']
                    
                    gender = ''
                    if 'gender' in owner:
                        gender = owner['gender'].get() if hasattr(owner['gender'], 'get') else owner.get('gender', '')
                    elif '性别' in owner:
                        gender = owner['性别']
                    
                    role = ''
                    if 'role' in owner:
                        role = owner['role'].get() if hasattr(owner['role'], 'get') else owner.get('role', '')
                    elif '角色' in owner:
                        role = owner['角色']
                    
                    if name:
                        owner_info = name
                        if gender:
                            owner_info += f"({gender})"
                        if role:
                            owner_info += f"-{role}"
                        owner_text.append(owner_info)
                
                owners_text = '; '.join(owner_text) if owner_text else '-'
                
                # 保存结果
                result = {
                    'date': current.strftime("%Y-%m-%d"),
                    'lunar': lunar_str,
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'score': score_result['score'],
                    'level': score_result['level'],
                    'wuxing_score': wuxing_score,
                    'yueling_score': yueling_score,
                    'xishen_score': xishen_score,
                    'huangdao_score': huangdao_score,
                    'dizhi_relation': dizhi_text,
                    'jishen': jishen_text,
                    'daliyue': daliyue_text,
                    'owners': owners_text,
                    'detail': score_result
                }
                
                # 筛选：只保留吉及以上的日课，过滤掉不吉的日课
                # 提取评分和等级
                score = score_result['score']
                level = score_result['level']
                yi_list = score_result.get('yi_list', [])
                ji_list = score_result.get('ji_list', [])
                shensha_list = score_result.get('shensha_list', [])
                
                # 过滤条件1：过滤0分的日课
                wu_xing_hege = score > 0
                # 过滤条件2：过滤等级为凶的日课
                is_not_xiong = '凶' not in level
                # 过滤条件3：过滤忌列表中包含当前事项类型的日课
                has_ji_event = event_type in ji_list
                
                # 过滤条件4和5：检查神煞中是否有不宜当前事项类型的信息和严重凶煞信息
                has_buyi_event = False
                has_serious_xiong_shen = False
                for shensha in shensha_list:
                    # 检查神煞元素的类型
                    if isinstance(shensha, dict):
                        # 如果是字典，获取描述或名称
                        shensha_desc = shensha.get('description', '') or shensha.get('name', '')
                    else:
                        # 如果是字符串，直接使用
                        shensha_desc = str(shensha)
                    
                    # 检查是否包含不宜信息
                    if f'不宜{event_type}' in shensha_desc or f'忌{event_type}' in shensha_desc:
                        has_buyi_event = True
                    
                    # 检查是否包含严重凶煞信息
                    serious_xiong_keywords = ['大凶', '绝对不可用', '不宜', '忌']
                    for keyword in serious_xiong_keywords:
                        if keyword in shensha_desc:
                            has_serious_xiong_shen = True
                            break
                    
                    if has_buyi_event and has_serious_xiong_shen:
                        break
                
                # 综合过滤条件
                if wu_xing_hege and is_not_xiong and not has_ji_event and not has_buyi_event and not has_serious_xiong_shen:
                    # 获取输出方式选择
                    output_mode = self.output_mode_var.get()
                    
                    # 如果选择"无扣分输出"，检查是否有扣分项
                    if output_mode == "nodeduct":
                        # 检查五行部分的扣分
                        wu_xing_result = score_result.get('wu_xing_result', {})
                        has_deduction = wu_xing_result.get('has_deduction', False)
                        
                        # 检查其他扣分（月令得分、黄道得分、喜用神得分）
                        score_details = score_result.get('score_details', {})
                        yueling_score = score_details.get('月令得分', 0)
                        huangdao_score = score_details.get('黄道得分', 0)
                        xishen_score = score_details.get('喜用神得分', 0)
                        
                        # 检查是否有扣分（任何得分项为负都视为有扣分）
                        if has_deduction or yueling_score < 0 or huangdao_score < 0 or xishen_score < 0:
                            # 有扣分项，跳过
                            current += timedelta(days=1)
                            continue
                    
                    self.results.append(result)
                
                current += timedelta(days=1)
            
            # 按评分从高到低排序
            self.results.sort(key=lambda x: x['score'], reverse=True)
            
            # 清空树形视图并重新添加排序后的结果
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            for result in self.results:
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
                    result['wuxing_score'],
                    result['yueling_score'],
                    result['xishen_score'],
                    result['huangdao_score'],
                    result['dizhi_relation'],
                    result['jishen'],
                    result.get('daliyue', '-'),
                    result.get('owners', '-')
                ), tags=(row_tag,))
            
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
        
        # 提取大利月/小利月信息
        daliyue_info = result.get('daliyue', '-')
        event_type = self.event_var.get()
        
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
        
        # 如果是婚嫁择日，显示大利月/小利月信息
        if event_type in ['嫁娶', '订婚', '纳采'] and daliyue_info != '-':
            text.insert(tk.END, f"\n利月：{daliyue_info}")
        
        # 插入事主信息
        text.insert(tk.END, "\n\n【事主信息】")
        text.insert(tk.END, "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # 导入必要的模块
        from modules.喜用神计算器 import calculate_xishen_yongshen
        
        owners_info = getattr(self, 'owners_info', [])
        if owners_info:
            for i, owner_info in enumerate(owners_info[:4], 1):  # 只显示前4个事主
                name = ""
                if 'name' in owner_info:
                    name = owner_info['name'].get() if hasattr(owner_info['name'], 'get') else owner_info.get('name', '')
                elif '姓名' in owner_info:
                    name = owner_info['姓名']
                
                gender = ""
                if 'gender' in owner_info:
                    gender = owner_info['gender'].get() if hasattr(owner_info['gender'], 'get') else owner_info.get('gender', '')
                elif '性别' in owner_info:
                    gender = owner_info['性别']
                
                if name:
                    text.insert(tk.END, f"\n  事主{i}：{name}")
                    if gender:
                        text.insert(tk.END, f"（{gender}）")
                    
                    # 显示事主的公历和农历日期、四柱、喜用神
                    if 'year' in owner_info:
                        try:
                            # 添加防御性检查
                            year_val = owner_info['year'].get() if hasattr(owner_info['year'], 'get') else owner_info.get('year', '')
                            month_val = owner_info['month'].get() if hasattr(owner_info['month'], 'get') else owner_info.get('month', '')
                            day_val = owner_info['day'].get() if hasattr(owner_info['day'], 'get') else owner_info.get('day', '')
                            
                            birth_date = date(
                                int(year_val),
                                int(month_val),
                                int(day_val)
                            )
                            # 添加防御性检查
                            hour_val = owner_info['hour'].get() if hasattr(owner_info['hour'], 'get') else owner_info.get('hour', '12')
                            minute_val = owner_info['minute'].get() if hasattr(owner_info['minute'], 'get') else owner_info.get('minute', '0')
                            birth_hour = int(hour_val)
                            birth_minute = int(minute_val)
                            
                            # 使用原来的八字排盘模块计算四柱
                            from modules.八字排盘 import BaZiPanPan
                            panpan = BaZiPanPan(birth_date.year, birth_date.month, birth_date.day, birth_hour, birth_minute, gender)
                            panpan_result = panpan.get_panpan_result()
                            
                            # 获取四柱信息
                            year_zhu = panpan_result['四柱']['年柱'] if '年柱' in panpan_result['四柱'] else '未知'
                            month_zhu = panpan_result['四柱']['月柱'] if '月柱' in panpan_result['四柱'] else '未知'
                            day_zhu = panpan_result['四柱']['日柱'] if '日柱' in panpan_result['四柱'] else '未知'
                            hour_zhu = panpan_result['四柱']['时柱'] if '时柱' in panpan_result['四柱'] else '未知'
                            sizhu_text = f"{year_zhu} {month_zhu} {day_zhu} {hour_zhu}"
                            
                            # 计算喜用神
                            sizhu_info = {
                                'year_gan': year_zhu[:1] if year_zhu else '',
                                'year_zhi': year_zhu[1:] if len(year_zhu) > 1 else '',
                                'month_gan': month_zhu[:1] if month_zhu else '',
                                'month_zhi': month_zhu[1:] if len(month_zhu) > 1 else '',
                                'day_gan': day_zhu[:1] if day_zhu else '',
                                'day_zhi': day_zhu[1:] if len(day_zhu) > 1 else '',
                                'hour_gan': hour_zhu[:1] if hour_zhu else '',
                                'hour_zhi': hour_zhu[1:] if len(hour_zhu) > 1 else ''
                            }
                            xishen, yongshen = calculate_xishen_yongshen(sizhu_info)
                            
                            # 显示事主详细信息
                            text.insert(tk.END, f"\n    公历：{birth_date}")
                            
                            # 计算农历日期
                            try:
                                from modules.高精度农历转换 import HighPrecisionLunar
                                lunar_converter = HighPrecisionLunar()
                                lunar_info = lunar_converter._get_lunar_info_sxtwl(birth_date.year, birth_date.month, birth_date.day, 12, 0, 0)
                                lunar_str = f"{lunar_info['lunar_year']}年{lunar_info['lunar_month']}月{lunar_info['lunar_day']}日"
                                if lunar_info['is_leap']:
                                    lunar_str = f"{lunar_info['lunar_year']}年闰{lunar_info['lunar_month']}月{lunar_info['lunar_day']}日"
                                text.insert(tk.END, f"\n    农历：{lunar_str}")
                            except Exception as e:
                                text.insert(tk.END, "\n    农历：未知")
                            
                            text.insert(tk.END, f"\n    四柱：{sizhu_text}")
                            
                            # 显示生肖
                            zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                                         '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
                            year_zhi = year_zhu[1:] if len(year_zhu) > 1 else ''
                            zodiac = zodiac_map.get(year_zhi, '')
                            if zodiac:
                                text.insert(tk.END, "（")
                                text.insert(tk.END, zodiac, "zodiac")
                                text.insert(tk.END, "）")
                                text.tag_config("zodiac", foreground="blue")
                            
                            text.insert(tk.END, f"\n    喜用神：{xishen}")
                            
                            # 如果是嫁娶，显示新娘的夫子星、阴胎、阳气
                            if event_type in ['嫁娶', '订婚', '纳采', '结婚'] and gender == '女':
                                try:
                                    from modules.工具函数 import get_fuzi, get_yintai, get_yangqi
                                    
                                    day_gan = day_zhu[:1] if day_zhu else ''
                                    day_zhi = day_zhu[1:] if len(day_zhu) > 1 else ''
                                    month_gan = month_zhu[:1] if month_zhu else '甲'
                                    month_zhi = month_zhu[1:] if len(month_zhu) > 1 else '子'
                                    year_gan = year_zhu[:1] if year_zhu else ''
                                    year_zhi_part = year_zhu[1:] if len(year_zhu) > 1 else ''
                                    
                                    if year_gan and year_zhi_part:
                                        # 计算夫星子星（基于年干年支）
                                        fuzi_info = get_fuzi(year_gan, year_zhi_part)
                                        fu = fuzi_info.get('fu', '未知')
                                        zi = fuzi_info.get('zi', '未知')
                                        
                                        # 计算阴胎（以新娘月柱为基准）
                                        yintai = get_yintai(month_gan, month_zhi)
                                        
                                        # 计算阳气（以新郎月柱为基准）
                                        yangqi = '未知'
                                        for groom_info in owners_info:
                                            groom_gender = groom_info['gender'].get() if hasattr(groom_info['gender'], 'get') else groom_info.get('gender', '')
                                            if groom_gender == '男' and groom_info != owner_info:
                                                groom_sizhu_var = groom_info.get('sizhu_var')
                                                if groom_sizhu_var and hasattr(groom_sizhu_var, 'get'):
                                                    groom_sizhu = groom_sizhu_var.get()
                                                    if groom_sizhu:
                                                        parts = groom_sizhu.split()
                                                        if len(parts) >= 2:
                                                            groom_month = parts[1]
                                                            groom_month_gan = groom_month[:1]
                                                            groom_month_zhi = groom_month[1:] if len(groom_month) > 1 else ''
                                                            if groom_month_gan and groom_month_zhi:
                                                                yangqi = get_yangqi(groom_month_gan, groom_month_zhi)
                                                break
                                        
                                        text.insert(tk.END, f"\n    夫星：{fu}")
                                        text.insert(tk.END, f"\n    子星：{zi}")
                                        text.insert(tk.END, f"\n    阴胎：{yintai}")
                                        text.insert(tk.END, f"\n    阳气：{yangqi}")
                                except:
                                    pass
                        except:
                            pass
        else:
            text.insert(tk.END, "\n  暂无事主信息")
        
        content = f"""

【评分详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        # 显示详细得分
        score_details = detail.get('score_details', {})
        if score_details:
            wuxing_score = score_details.get('五行评分', 100)
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            total_score = score_details.get('总分', result['score'])
            
            content += f"  五行评分：{wuxing_score} 分\n"
            
            # 五行评分详细得分
            wu_xing_result = detail.get('wu_xing_result', {})
            score_breakdown = wu_xing_result.get('score_breakdown', {})
            if score_breakdown:
                content += f"    ├─ 基础分：{score_breakdown.get('基础分', 100)} 分\n"
                shensha_score = score_breakdown.get('神煞得分', 0)
                if shensha_score != 0:
                    content += f"    ├─ 神煞得分：{shensha_score:+d} 分\n"
                yi_score = score_breakdown.get('宜事得分', 0)
                if yi_score != 0:
                    content += f"    ├─ 宜事得分：+{yi_score} 分\n"
                ji_score = score_breakdown.get('忌事得分', 0)
                if ji_score != 0:
                    content += f"    ├─ 忌事得分：{ji_score} 分\n"
                zhangsheng = score_breakdown.get('十二长生得分', 0)
                if zhangsheng != 0:
                    content += f"    ├─ 十二长生得分：{zhangsheng:+d} 分\n"
                zhizhi = score_breakdown.get('地支关系得分', 0)
                if zhizhi != 0:
                    content += f"    ├─ 地支关系得分：{zhizhi:+d} 分\n"
                nayin = score_breakdown.get('纳音匹配得分', 0)
                if nayin != 0:
                    content += f"    └─ 纳音匹配得分：{nayin:+d} 分\n"
            
            # 显示婚嫁评分详情（夫星受克等）
            marriage_details = detail.get('marriage_details', [])
            if marriage_details:
                for detail_name, detail_score in marriage_details:
                    if detail_score != 0:
                        content += f"    {'├─' if score_breakdown else ''}{detail_name}：{detail_score:+d} 分\n"
            
            content += f"  月令得分：{yueling_score:+d} 分\n"
            
            # 月令详细得分
            yueling_detail = score_details.get('月令详细', {})
            if yueling_detail:
                content += f"    ├─ 旺衰得分：{yueling_detail.get('旺衰得分', 0):+d} 分\n"
                content += f"    └─ 支支关系得分：{yueling_detail.get('支支关系得分', 0):+d} 分\n"
            
            content += f"  喜用神得分：{xishen_score:+d} 分\n"
            content += f"  黄道得分：{huangdao_score:+d} 分\n"
            content += f"  ─────────────────────────────────\n"
            content += f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {huangdao_score:+d} = {total_score} 分\n"
            content += f"  总分：{total_score} 分\n"
        else:
            content += "  暂无详细得分数据\n"
        
        # 月令分析
        content += f"""
【月令分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        reason = detail.get('reason', '')
        yueling_info = ""
        for part in reason.split('；'):
            if '月令：' in part:
                yueling_info = part.replace('月令：', '')
                break
        
        if yueling_info:
            content += f"  {yueling_info}\n"
        else:
            content += "  月令分析：暂无数据\n"
        
        # 四柱信息
        sizhu = detail.get('sizhu', {})
        if sizhu:
            content += f"""
【四柱八字】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  年柱: {sizhu.get('年柱', 'N/A')}    月柱: {sizhu.get('月柱', 'N/A')}
  日柱: {sizhu.get('日柱', 'N/A')}    时柱: {sizhu.get('时柱', 'N/A')}

  【天干五行】
    年干: {sizhu.get('年柱', 'N/A')[0] if sizhu.get('年柱') else 'N/A'}    月干: {sizhu.get('月柱', 'N/A')[0] if sizhu.get('月柱') else 'N/A'}    日干: {sizhu.get('日柱', 'N/A')[0] if sizhu.get('日柱') else 'N/A'}    时干: {sizhu.get('时柱', 'N/A')[0] if sizhu.get('时柱') else 'N/A'}
  【地支五行】
    年支: {sizhu.get('年柱', 'N/A')[1] if sizhu.get('年柱') else 'N/A'}    月支: {sizhu.get('月柱', 'N/A')[1] if sizhu.get('月柱') else 'N/A'}    日支: {sizhu.get('日柱', 'N/A')[1] if sizhu.get('日柱') else 'N/A'}    时支: {sizhu.get('时柱', 'N/A')[1] if sizhu.get('时柱') else 'N/A'}

"""
        
        # 五行分析
        wu_xing_result = detail.get('wu_xing_result', {})
        if wu_xing_result:
            content += f"""【五行分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  五行评分: {wu_xing_result.get('score', 'N/A')} 分
"""
            if wu_xing_result.get('reason'):
                content += f"  五行评语: {wu_xing_result['reason']}\n"
            
            wu_xing_details = wu_xing_result.get('details', {})
            if wu_xing_details:
                # 1. 天干地支五行
                if wu_xing_details.get('天干五行'):
                    content += "\n  【天干地支五行】\n"
                    for pillar, info in wu_xing_details['天干五行'].items():
                        content += f"    {pillar}: {info['天干']}({info['天干五行']}) {info['地支']}({info['地支五行']})\n"
                
                # 2. 地支关系（三合、六合、六冲、六害、三刑）
                if wu_xing_details.get('地支关系') and len(wu_xing_details['地支关系']) > 0:
                    content += "\n  【地支关系】\n"
                    for relation in wu_xing_details['地支关系']:
                        content += f"    • {relation}\n"
                else:
                    content += "\n  【地支关系】\n    无明显合冲刑害关系\n"
                
                # 3. 十二长生
                if wu_xing_details.get('十二长生'):
                    content += "\n  【十二长生】\n"
                    for pillar, state in wu_xing_details['十二长生'].items():
                        content += f"    {pillar}: {state}\n"
                
                # 4. 纳音五行
                if wu_xing_details.get('纳音五行'):
                    content += "\n  【纳音五行】\n"
                    for pillar, nayin in wu_xing_details['纳音五行'].items():
                        content += f"    {pillar}: {nayin}\n"
                
                # 5. 吉神（天德、月德）
                if wu_xing_details.get('吉神') and len(wu_xing_details['吉神']) > 0:
                    content += "\n  【吉神】\n"
                    for jishen in wu_xing_details['吉神']:
                        content += f"    ✓ {jishen}\n"
                else:
                    content += "\n  【吉神】\n    无天德月德等吉神\n"
                
                # 6. 日主旺衰
                if wu_xing_details.get('日主旺衰'):
                    content += f"\n  【日主旺衰】\n    {wu_xing_details['日主旺衰']}\n"
                
                # 7. 五行生克
                if wu_xing_details.get('五行生克') and len(wu_xing_details['五行生克']) > 0:
                    content += "\n  【五行生克】\n"
                    for relation in wu_xing_details['五行生克']:
                        content += f"    • {relation}\n"
            
            if wu_xing_result.get('wang_xiang'):
                content += f"  旺相分析: {wu_xing_result['wang_xiang']}\n"
            if wu_xing_result.get('ke_zhi'):
                content += f"  克制关系: {wu_xing_result['ke_zhi']}\n"
            content += "\n"
        
        # 黄道信息
        huangdao_info = detail.get('huangdao_info', {})
        if huangdao_info:
            content += """【黄道信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            if huangdao_info.get('da_huang_dao'):
                da_hd = huangdao_info['da_huang_dao']
                content += f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})\n"
                if da_hd.get('description'):
                    content += f"    说明: {da_hd['description']}\n"
            if huangdao_info.get('xiao_huang_dao'):
                xiao_hd = huangdao_info['xiao_huang_dao']
                content += f"  小黄道: {xiao_hd.get('name', 'N/A')} ({xiao_hd.get('type', 'N/A')})\n"
                if xiao_hd.get('description'):
                    content += f"    说明: {xiao_hd['description']}\n"
            content += f"  黄道等级: {huangdao_info.get('huang_dao_level', 'N/A')}\n\n"
        
        # 宜忌信息
        content += f"""【宜忌信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        yi_list = detail.get('yi_list', [])
        ji_list = detail.get('ji_list', [])
        if yi_list:
            yi_items = yi_list if isinstance(yi_list, list) else yi_list.split(', ')
            content += f"  宜: {', '.join(yi_items)}\n"
        if ji_list:
            ji_items = ji_list if isinstance(ji_list, list) else ji_list.split(', ')
            content += f"  忌: {', '.join(ji_items)}\n"
        content += "\n"
        
        # 神煞信息
        shensha_list = detail.get('shensha_list', [])
        if shensha_list:
            content += """【神煞信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            # 按分值排序显示
            sorted_shensha = sorted(shensha_list, key=lambda x: x.get('score', 0), reverse=True)
            for shensha in sorted_shensha:
                name = shensha.get('name', '')
                desc = shensha.get('description', '')
                score = shensha.get('score', 0)
                if score > 0:
                    mark = '✓'
                elif score < 0:
                    mark = '✗'
                else:
                    mark = '○'
                content += f"  {mark} {name}（{score:+.0f}分）: {desc}\n"
            content += "\n"
        
        # 评语
        if detail.get('reason'):
            content += f"""【综合评语】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {detail['reason']}

"""
        
        # 修造专属信息（动土方位、时辰吉凶、扶山相主等）
        event_type = self.event_var.get()
        construction_events = ['修造', '动土', '装修']
        if event_type in construction_events:
            try:
                from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
                from modules.四柱计算器 import calculate_sizhu
                
                zuoshan = None
                zhuming = None
                
                shan_xiang_val2 = getattr(self, 'shan_xiang', None)
                if shan_xiang_val2 and shan_xiang_val2.get() and '山' in shan_xiang_val2.get():
                    zuoshan = shan_xiang_val2.get().split('山')[0].strip()
                
                # 从owners_info中获取事主信息
                owners_info = getattr(self, 'owners_info', [])
                if owners_info:
                    try:
                        owner_info = owners_info[0]
                        if 'year_var' in owner_info:
                            birth_date = date(
                                int(owner_info['year_var'].get()),
                                int(owner_info['month_var'].get()),
                                int(owner_info['day_var'].get())
                            )
                            birth_hour = int(owner_info['hour_var'].get())
                            birth_minute = int(owner_info['minute_var'].get())
                            owner_sizhu = calculate_sizhu(birth_date, birth_hour, birth_minute)
                            zhuming = owner_sizhu.get('年柱', '')
                    except:
                        pass
                
                # 构建sizhu字典
                detail_sizhu = {
                    'year_gan': detail.get('sizhu', {}).get('年柱', '')[:1] if detail.get('sizhu', {}).get('年柱') else '',
                    'year_zhi': detail.get('sizhu', {}).get('年柱', '')[1:] if detail.get('sizhu', {}).get('年柱') else '',
                    'month_gan': detail.get('sizhu', {}).get('月柱', '')[:1] if detail.get('sizhu', {}).get('月柱') else '',
                    'month_zhi': detail.get('sizhu', {}).get('月柱', '')[1:] if detail.get('sizhu', {}).get('月柱') else '',
                    'day_gan': detail.get('sizhu', {}).get('日柱', '')[:1] if detail.get('sizhu', {}).get('日柱') else '',
                    'day_zhi': detail.get('sizhu', {}).get('日柱', '')[1:] if detail.get('sizhu', {}).get('日柱') else '',
                    'hour_gan': detail.get('sizhu', {}).get('时柱', '')[:1] if detail.get('sizhu', {}).get('时柱') else '',
                    'hour_zhi': detail.get('sizhu', {}).get('时柱', '')[1:] if detail.get('sizhu', {}).get('时柱') else '',
                }
                
                checker = ConstructionShenShaCheckerExt(zuoshan=zuoshan, zhuming=zhuming)
                
                # 扶山相主补龙信息
                if zuoshan:
                    content += """【修造择日分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    if zuoshan:
                        content += f"  坐山：{zuoshan}"
                        xiangshan_list = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                                         '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
                        try:
                            idx = xiangshan_list.index(zuoshan)
                            xiang = xiangshan_list[(idx + 12) % 24]
                            content += f"  向方：{xiang}\n"
                        except:
                            content += "\n"
                    
                    if zhuming:
                        content += f"  主命：{zhuming}\n"
                    
                    # 显示神煞分类
                    shensha_items = detail.get('shensha_list', [])
                    fushan_items = []
                    xiangzhu_items = []
                    shanjia_items = []
                    direction_items = []
                    hour_items = []
                    jianchu_items = []
                    other_items = []
                    
                    for s in shensha_items:
                        name = s.get('name', '')
                        score = s.get('score', 0)
                        desc = s.get('description', '')
                        tag = f"{name}: {desc}（{score:+.0f}分）"
                        
                        if '扶山' in name or '相主' in name or '补龙' in name or '冲主' in name or '克山' in name:
                            fushan_items.append(tag)
                        elif '山家' in name or '冲山' in name:
                            shanjia_items.append(tag)
                        elif '方位' in name or '到方' in name:
                            direction_items.append(tag)
                        elif '时' in name:
                            hour_items.append(tag)
                        elif '建除' in name:
                            jianchu_items.append(tag)
                        else:
                            other_items.append(tag)
                    
                    if fushan_items:
                        content += "\n  【扶山·相主·补龙】\n"
                        for item in fushan_items:
                            content += f"    • {item}\n"
                    
                    if shanjia_items:
                        content += "\n  【山家吉凶】\n"
                        for item in shanjia_items:
                            content += f"    • {item}\n"
                    
                    if direction_items:
                        content += "\n  【动土方位凶煞】\n"
                        for item in direction_items:
                            content += f"    • {item}\n"
                    
                    if hour_items:
                        content += "\n  【时辰吉凶】\n"
                        for item in hour_items:
                            content += f"    • {item}\n"
                    
                    if jianchu_items:
                        content += "\n  【建除十二神】\n"
                        for item in jianchu_items:
                            content += f"    • {item}\n"
                    
                    # 吉利动土方位推荐
                    lucky_directions = checker.get_lucky_directions(detail_sizhu)
                    safe_dirs = [d for d in lucky_directions if d['分值'] == 0]
                    danger_dirs = [d for d in lucky_directions if d['分值'] < 0]
                    
                    content += "\n  【二十四山动土方位吉凶】\n"
                    content += "  （0分=安全可用，负分=犯煞不宜）\n"
                    
                    # 按八方位分组显示
                    fangwei_groups = {
                        '北方': ['壬', '子', '癸'],
                        '东北': ['丑', '艮', '寅'],
                        '东方': ['甲', '卯', '乙'],
                        '东南': ['辰', '巽', '巳'],
                        '南方': ['丙', '午', '丁'],
                        '西南': ['未', '坤', '申'],
                        '西方': ['庚', '酉', '辛'],
                        '西北': ['戌', '乾', '亥']
                    }
                    
                    for fang_name, shans in fangwei_groups.items():
                        content += f"\n    {fang_name}："
                        dir_infos = []
                        # 创建方位到信息的映射，方便查找
                        direction_map = {d['方位']: d for d in lucky_directions}
                        for shan in shans:
                            d = direction_map.get(shan, {'分值': 0, '说明': ['无煞']})
                            if d['分值'] == 0:
                                dir_infos.append(f"{shan}(0分)")
                            else:
                                sha_names = '、'.join(d['说明'])
                                dir_infos.append(f"{shan}({d['分值']}分:{sha_names})")
                        content += '  '.join(dir_infos) + '\n'
                    
                    if safe_dirs:
                        safe_names = '、'.join([f"{d['方位']}({d['分值']}分)" for d in safe_dirs])
                        content += f"\n  ★ 安全方位（共{len(safe_dirs)}个）：{safe_names}\n"
                    if danger_dirs:
                        content += f"  ✗ 犯煞方位（共{len(danger_dirs)}个）："
                        for d in danger_dirs:
                            content += f"\n    {d['方位']}（{d['分值']}分）：{'、'.join(d['说明'])}"
                        content += "\n"
                    
                    # 吉利时辰推荐
                    lucky_hours = checker.get_lucky_hours(detail_sizhu)
                    good_hours = [h for h in lucky_hours if h['分值'] > 0]
                    bad_hours = [h for h in lucky_hours if h['分值'] < 0]
                    ok_hours = [h for h in lucky_hours if h['分值'] == 0]
                    
                    content += "\n  【十二时辰动土吉凶】\n"
                    content += "  （正分=吉时，0分=平，负分=凶时）\n"
                    
                    # 按时辰顺序显示
                    hour_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                    for zhi in hour_order:
                        for h in lucky_hours:
                            if h['地支'] == zhi:
                                if h['分值'] > 0:
                                    mark = '★'
                                    reasons_str = '、'.join(h['说明'])
                                    content += f"    {mark} {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                                elif h['分值'] < 0:
                                    mark = '✗'
                                    reasons_str = '、'.join(h['说明'])
                                    content += f"    {mark} {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                                else:
                                    content += f"      {h['天干']}{h['地支']}时 {h['时辰']}  平\n"
                                break
                    
                    if good_hours:
                        good_names = '、'.join([f"{h['天干']}{h['地支']}" for h in good_hours])
                        content += f"\n  ★ 吉利时辰（共{len(good_hours)}个）：{good_names}\n"
                    if bad_hours:
                        bad_names = '、'.join([f"{h['天干']}{h['地支']}" for h in bad_hours])
                        content += f"  ✗ 凶时（共{len(bad_hours)}个）：{bad_names}\n"
                    
                    content += "\n"
                
            except Exception as e:
                content += f"\n【修造分析】\n  分析出错：{str(e)}\n"
        
        # 嫁娶专属信息（吉利时辰、大利月等）
        marriage_events = ['嫁娶', '订婚', '纳采', '结婚']
        if event_type in marriage_events:
            try:
                from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt
                from modules.四柱计算器 import calculate_sizhu
                
                bride_gan = None
                bride_zhi = None
                groom_gan = None
                groom_zhi = None
                
                # 从owners_info中获取事主信息
                owners_info = getattr(self, 'owners_info', [])
                owners = []
                for owner_info in owners_info:
                    owner_data = {}
                    if 'gender' in owner_info:
                        owner_data['性别'] = owner_info['gender'].get() if hasattr(owner_info['gender'], 'get') else owner_info.get('gender', '')
                    if 'year' in owner_info:
                        try:
                            # 添加防御性检查
                            year_val = owner_info['year'].get() if hasattr(owner_info['year'], 'get') else owner_info.get('year', '')
                            month_val = owner_info['month'].get() if hasattr(owner_info['month'], 'get') else owner_info.get('month', '')
                            day_val = owner_info['day'].get() if hasattr(owner_info['day'], 'get') else owner_info.get('day', '')
                            hour_val = owner_info['hour'].get() if hasattr(owner_info['hour'], 'get') else owner_info.get('hour', '12')
                            minute_val = owner_info['minute'].get() if hasattr(owner_info['minute'], 'get') else owner_info.get('minute', '0')
                            
                            owner_data['birth_date'] = date(
                                int(year_val),
                                int(month_val),
                                int(day_val)
                            )
                            owner_data['birth_hour'] = int(hour_val)
                            owner_data['birth_minute'] = int(minute_val)
                        except (ValueError, AttributeError):
                            pass
                    owners.append(owner_data)
                
                if owners:
                    for owner in owners:
                        gender = owner.get('性别', '') or owner.get('gender', '')
                        if gender == '女':
                            bride_gan = owner.get('年干', '') or owner.get('year_gan', '')
                            bride_zhi = owner.get('生肖', '') or owner.get('年支', '') or owner.get('year_zhi', '')
                            if not bride_gan and owner.get('birth_date'):
                                try:
                                    birth_date = owner['birth_date']
                                    if isinstance(birth_date, str):
                                        from datetime import datetime
                                        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                                    if hasattr(birth_date, 'year'):
                                        owner_sizhu = calculate_sizhu(birth_date,
                                            owner.get('birth_hour', 12),
                                            owner.get('birth_minute', 0))
                                        bride_gan = owner_sizhu.get('年柱', '')[:1]
                                        bride_zhi = owner_sizhu.get('年柱', '')[1:]
                                except:
                                    pass
                        elif gender == '男':
                            groom_gan = owner.get('年干', '') or owner.get('year_gan', '')
                            groom_zhi = owner.get('生肖', '') or owner.get('年支', '') or owner.get('year_zhi', '')
                            if not groom_gan and owner.get('birth_date'):
                                try:
                                    birth_date = owner['birth_date']
                                    if isinstance(birth_date, str):
                                        from datetime import datetime
                                        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                                    if hasattr(birth_date, 'year'):
                                        owner_sizhu = calculate_sizhu(birth_date,
                                            owner.get('birth_hour', 12),
                                            owner.get('birth_minute', 0))
                                        groom_gan = owner_sizhu.get('年柱', '')[:1]
                                        groom_zhi = owner_sizhu.get('年柱', '')[1:]
                                except:
                                    pass
                
                detail_sizhu = {
                    'year_gan': detail.get('sizhu', {}).get('年柱', '')[:1] if detail.get('sizhu', {}).get('年柱') else '',
                    'year_zhi': detail.get('sizhu', {}).get('年柱', '')[1:] if detail.get('sizhu', {}).get('年柱') else '',
                    'month_gan': detail.get('sizhu', {}).get('月柱', '')[:1] if detail.get('sizhu', {}).get('月柱') else '',
                    'month_zhi': detail.get('sizhu', {}).get('月柱', '')[1:] if detail.get('sizhu', {}).get('月柱') else '',
                    'day_gan': detail.get('sizhu', {}).get('日柱', '')[:1] if detail.get('sizhu', {}).get('日柱') else '',
                    'day_zhi': detail.get('sizhu', {}).get('日柱', '')[1:] if detail.get('sizhu', {}).get('日柱') else '',
                    'hour_gan': detail.get('sizhu', {}).get('时柱', '')[:1] if detail.get('sizhu', {}).get('时柱') else '',
                    'hour_zhi': detail.get('sizhu', {}).get('时柱', '')[1:] if detail.get('sizhu', {}).get('时柱') else '',
                }
                
                checker = MarriageShenShaCheckerExt(
                    bride_gan=bride_gan, bride_zhi=bride_zhi,
                    groom_gan=groom_gan, groom_zhi=groom_zhi
                )
                
                content += """【嫁娶择日分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                # 地支到生肖的映射
                zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                             '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
                
                if bride_gan and bride_zhi:
                    bride_zodiac = zodiac_map.get(bride_zhi, '')
                    content += f"  新娘：{bride_gan}{bride_zhi}年生"
                    if bride_zodiac:
                        content += f"（{bride_zodiac}）"
                    content += "\n"
                if groom_gan and groom_zhi:
                    groom_zodiac = zodiac_map.get(groom_zhi, '')
                    content += f"  新郎：{groom_gan}{groom_zhi}年生"
                    if groom_zodiac:
                        content += f"（{groom_zodiac}）"
                    content += "\n"
                
                daliyue_info = checker.get_daliyue_info(detail_sizhu)
                content += f"\n  【利月分析】\n"
                content += f"    大利月：{'、'.join(daliyue_info['大利月']) if daliyue_info['大利月'] else '无'}\n"
                content += f"    小利月：{'、'.join(daliyue_info['小利月']) if daliyue_info['小利月'] else '无'}\n"
                content += f"    当前月份：{daliyue_info['当前月份状态']}\n"
                
                shensha_items = detail.get('shensha_list', [])
                jiri_items = []
                xiongri_items = []
                chonghe_items = []
                liyue_items = []
                other_items = []
                
                for s in shensha_items:
                    name = s.get('name', '')
                    score = s.get('score', 0)
                    desc = s.get('description', '')
                    tag = f"{name}（{score:+.0f}分）: {desc}"
                    
                    if '大利月' in name or '小利月' in name:
                        liyue_items.append(tag)
                    elif '日' in name and '吉' in desc:
                        jiri_items.append(tag)
                    elif '日' in name and ('忌' in desc or '凶' in desc or '大忌' in desc):
                        xiongri_items.append(tag)
                    elif '冲' in name or '合' in name:
                        chonghe_items.append(tag)
                    elif '煞' in name or '忌' in name:
                        xiongri_items.append(tag)
                    else:
                        other_items.append(tag)
                
                if liyue_items:
                    content += "\n  【利月神煞】\n"
                    for item in liyue_items:
                        content += f"    • {item}\n"
                
                if jiri_items:
                    content += "\n  【吉日神煞】\n"
                    for item in jiri_items:
                        content += f"    ✓ {item}\n"
                
                if xiongri_items:
                    content += "\n  【凶日神煞】\n"
                    for item in xiongri_items:
                        content += f"    ✗ {item}\n"
                
                if chonghe_items:
                    content += "\n  【冲合关系】\n"
                    for item in chonghe_items:
                        content += f"    • {item}\n"
                
                lucky_hours = checker.get_lucky_hours(detail_sizhu)
                # 吉利时辰：分值>0 且 未禁用
                good_hours = [h for h in lucky_hours if h['分值'] > 0 and not h.get('禁用', False)]
                # 凶时：分值<0 或 已禁用
                bad_hours = [h for h in lucky_hours if h['分值'] < 0 or h.get('禁用', False)]
                
                content += "\n  【十二时辰婚嫁吉凶】\n"
                content += "  （正分=吉时，0分=平，负分=凶时，禁用=不可用）\n"
                
                hour_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                for zhi in hour_order:
                    for h in lucky_hours:
                        if h['地支'] == zhi:
                            if h.get('禁用', False):
                                mark = '✗'
                                reasons_str = '、'.join(h['说明'])
                                content += f"    {mark} {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            elif h['分值'] > 0:
                                mark = '★'
                                reasons_str = '、'.join(h['说明'])
                                content += f"    {mark} {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            elif h['分值'] < 0:
                                mark = '✗'
                                reasons_str = '、'.join(h['说明'])
                                content += f"    {mark} {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            else:
                                content += f"      {h['天干']}{h['地支']}时 {h['时辰']}  平\n"
                            break
                
                if good_hours:
                    good_names = '、'.join([f"{h['天干']}{h['地支']}" for h in good_hours])
                    content += f"\n  ★ 吉利时辰（共{len(good_hours)}个）：{good_names}\n"
                if bad_hours:
                    bad_names = '、'.join([f"{h['天干']}{h['地支']}" for h in bad_hours])
                    content += f"  ✗ 凶时/禁用（共{len(bad_hours)}个）：{bad_names}\n"
                
                content += "\n"
                
            except Exception as e:
                content += f"\n【嫁娶分析】\n  分析出错：{str(e)}\n"
        
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
                        result_24 = selector.evaluate_by_name(
                            shan_name, year_gz, month_gz, day_gz, hour_gz
                        )
                        
                        if result_24.get('success'):
                            content += f"\n\n【正体五行分析】\n"
                            content += f"山向：{shan_xiang_val.get()}（坐山：{shan_name}）\n"
                            content += f"兼向：正中（正向）\n"
                            content += f"等级：{result_24.get('level', '?')}\n"
                            content += f"得分：{result_24.get('score', '?')}\n"
                            if 'summary' in result_24:
                                summary = result_24['summary']
                                content += f"坐山得分：{summary.get('mountain_score', 'N/A')}\n"
                        else:
                            content += f"\n\n【正体五行分析】\n"
                            content += f"山向：{shan_xiang_val.get()}（坐山：{shan_name}）\n"
                            content += f"分析失败：{result_24.get('error', '未知错误')}\n"
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
                        # 从detail中获取宜/忌列表
                        detail = result.get('detail', {})
                        yi_list = detail.get('yi_list', [])
                        ji_list = detail.get('ji_list', [])
                        f.write(f"宜：{', '.join(yi_list) if yi_list else '-'}\n")
                        f.write(f"忌：{', '.join(ji_list) if ji_list else '-'}\n")
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
                                result.get('score', '-'),
                                result.get('level', '-'),
                                result.get('sizhu', result.get('四柱', '-')),
                                result.get('wuxing_score', '-'),
                                result.get('yueling_score', '-'),
                                result.get('xishen_score', '-'),
                                result.get('huangdao_score', '-'),
                                result.get('dizhi_relation', '-'),
                                result.get('jishen', result.get('yi', '-')),
                                result.get('daliyue', '-'),
                                result.get('owners', '-')
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
                                result.get('score', '-'),
                                result.get('level', '-'),
                                result.get('sizhu', result.get('四柱', '-')),
                                result.get('wuxing_score', '-'),
                                result.get('yueling_score', '-'),
                                result.get('xishen_score', '-'),
                                result.get('huangdao_score', '-'),
                                result.get('dizhi_relation', '-'),
                                result.get('jishen', result.get('yi', '-')),
                                result.get('daliyue', '-'),
                                result.get('owners', '-')
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
                            result.get('score', '-'),
                            result.get('level', '-'),
                            result.get('sizhu', result.get('四柱', '-')),
                            result.get('wuxing_score', '-'),
                            result.get('yueling_score', '-'),
                            result.get('xishen_score', '-'),
                            result.get('huangdao_score', '-'),
                            result.get('dizhi_relation', '-'),
                            result.get('jishen', result.get('yi', '-')),
                            result.get('daliyue', '-'),
                            result.get('owners', '-')
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
            # 传递主程序窗口作为master参数，创建Toplevel窗口
            score_window = DayScoreWindow(master=self.root)
            
            # 准备事主数据
            owners_data = []
            for owner in self.owners_info:
                try:
                    # 添加防御性检查
                    year_str = owner['year'].get() if hasattr(owner['year'], 'get') else owner.get('year', '')
                    month_str = owner['month'].get() if hasattr(owner['month'], 'get') else owner.get('month', '')
                    day_str = owner['day'].get() if hasattr(owner['day'], 'get') else owner.get('day', '')
                    
                    # 检查是否填写了日期
                    if not (year_str and month_str and day_str):
                        continue
                    
                    hour_str = owner['hour'].get() if hasattr(owner['hour'], 'get') else owner.get('hour', '12')
                    minute_str = owner['minute'].get() if hasattr(owner['minute'], 'get') else owner.get('minute', '0')
                    
                    owners_data.append({
                        'year': int(year_str),
                        'month': int(month_str),
                        'day': int(day_str),
                        'hour': int(hour_str),
                        'minute': int(minute_str)
                    })
                except:
                    pass
            
            # 导入当前事项类型和事主数据
            score_window.import_results(
                self.results if hasattr(self, 'results') else [],
                self.event_var.get(),
                owners_data
            )
            
            # 直接启动日课评分系统
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
                    # 添加防御性检查
                    year_str = owner['year'].get() if hasattr(owner['year'], 'get') else owner.get('year', '')
                    month_str = owner['month'].get() if hasattr(owner['month'], 'get') else owner.get('month', '')
                    day_str = owner['day'].get() if hasattr(owner['day'], 'get') else owner.get('day', '')
                    
                    # 检查是否填写了日期
                    if not (year_str and month_str and day_str):
                        continue
                    
                    hour_str = owner['hour'].get() if hasattr(owner['hour'], 'get') else owner.get('hour', '12')
                    minute_str = owner['minute'].get() if hasattr(owner['minute'], 'get') else owner.get('minute', '0')
                    
                    owners_data.append({
                        'year': int(year_str),
                        'month': int(month_str),
                        'day': int(day_str),
                        'hour': int(hour_str),
                        'minute': int(minute_str)
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
   - 婚嫁：新娘新郎信息必填（需完整出生日期推算日柱）
   - 安葬：死者信息必填
   - 其他事项：事主信息可选

7. 婚嫁择日说明
   - 夫子星、阴胎、阳气需新娘日柱才能准确计算
   - 时辰评分包含：大黄道、小黄道、贵人时、禄神时等
   - 日破时、冲命时自动标记为禁用，不参与排序
   - 五不遇时算法已修正（时干克日干，阴阳相同，位移差4）

8. 造葬择日说明
   - 山方煞：动态计算（戊己日+辰戌支），静态数据仅供参考
   - 克山运：动态计算（按年干推算山运纳音），静态数据可能错误
   - 星曜煞：动态计算（按山家五行判断忌日）
   - 三煞检查：按二十四山三合局归属判断
   - 阴府：区分正阴府（双干全）和傍阴府（单干见）

9. 模块职责
   - 婚嫁神煞扩展模块：负责时辰吉利值、大利月、夫子星等
   - 婚嫁神煞主模块：负责三娘煞、阴错阳差、红纱、杨公忌等日禁
   - 二十四山模块：负责造葬择日的山家专用检查
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

    def _on_touch_start(self, event):
        """触摸开始事件"""
        self._touch_start_x = event.x
        self._touch_start_y = event.y
        self._touch_start_scroll_x = event.widget.xview()[0]
        self._touch_start_scroll_y = event.widget.yview()[0]

    def _on_touch_move(self, event):
        """触摸移动事件"""
        if hasattr(self, '_touch_start_x') and hasattr(self, '_touch_start_y'):
            delta_x = event.x - self._touch_start_x
            delta_y = event.y - self._touch_start_y
            
            # 计算滚动距离（反向滚动）
            scroll_delta_x = -delta_x / event.widget.winfo_width()
            scroll_delta_y = -delta_y / event.widget.winfo_height()
            
            # 应用滚动
            new_x = max(0, min(1, self._touch_start_scroll_x + scroll_delta_x))
            new_y = max(0, min(1, self._touch_start_scroll_y + scroll_delta_y))
            
            event.widget.xview_moveto(new_x)
            event.widget.yview_moveto(new_y)

    def _on_touch_end(self, event):
        """触摸结束事件"""
        # 重置触摸状态
        self._touch_start_x = 0
        self._touch_start_y = 0
        self._touch_start_scroll_x = 0
        self._touch_start_scroll_y = 0

    def _on_tree_touch_start(self, event):
        """结果列表触摸开始事件"""
        # 检查是否点击了项目（避免干扰选择）
        item = self.result_tree.identify_row(event.y)
        if item:
            # 如果点击了项目，不启动触摸滚动
            self._touch_start_x = 0
            self._touch_start_y = 0
        else:
            # 否则启动触摸滚动
            self._on_touch_start(event)

    def _on_tree_touch_move(self, event):
        """结果列表触摸移动事件"""
        # 只有当触摸开始坐标不为0时才执行滚动
        if self._touch_start_x != 0 or self._touch_start_y != 0:
            self._on_touch_move(event)

    def _on_tree_touch_end(self, event):
        """结果列表触摸结束事件"""
        self._on_touch_end(event)

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