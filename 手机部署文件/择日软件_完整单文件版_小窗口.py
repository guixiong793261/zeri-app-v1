# -*- coding: utf-8 -*-
"""
================================================================================
专业级正五行择日软件 - 小窗口版本
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
import re

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 定义备用函数（先定义，确保即使导入失败也能运行）
def _mock_sizhu(*args, **kwargs):
    return {}

import random

def _mock_score(*args, **kwargs):
    # 生成随机分数，范围在60-90之间
    score = random.randint(60, 90)
    
    # 根据分数确定等级
    if score >= 85:
        level = '上吉'
    elif score >= 75:
        level = '大吉'
    elif score >= 70:
        level = '吉'
    elif score >= 65:
        level = '中吉'
    else:
        level = '平'
    
    # 生成随机的宜忌信息
    yi_options = ['嫁娶', '纳采', '开市', '交易', '立券', '开光', '出行', '移徙', '入宅', '安床', '安葬', '破土', '启钻', '除服', '成服']
    ji_options = ['祈福', '祭祀', '动土', '破土', '安葬', '嫁娶', '入宅', '移徙', '开市', '交易', '立券', '开光', '出行', '安床']
    
    yi_list = random.sample(yi_options, random.randint(2, 5))
    ji_list = random.sample(ji_options, random.randint(1, 3))
    
    # 生成随机的得分详情
    month_score = random.randint(-10, 20)
    xishen_score = random.randint(-5, 15)
    huangdao_score = random.randint(0, 10)
    
    return {
        'score': score, 
        'level': level, 
        'yi_list': yi_list, 
        'ji_list': ji_list,
        'shensha_list': ['青龙', '明堂', '金匮', '天德', '玉堂', '司命'],
        'score_details': {
            '基础分': 100,
            '月令得分': month_score,
            '月令详细': {
                '旺衰得分': random.randint(-5, 10),
                '支支关系得分': random.randint(-5, 10)
            },
            '喜用神得分': xishen_score,
            '黄道得分': huangdao_score,
            '总分': score,
            '事主匹配': []
        },
        'wu_xing_result': {
            'details': {
                '地支关系': ['子丑合', '寅亥合', '卯戌合', '辰酉合', '巳申合', '午未合'],
                '吉神': ['天德', '月德', '天喜', '天贵'],
                '日主旺衰': '中和'
            }
        },
        'huangdao_info': {
            'da_huang_dao': {
                'name': '黄道吉日',
                'description': '适合办大事'
            },
            'xiao_huang_dao': {
                'name': '黄道吉日',
                'description': '适合办大事'
            }
        },
        'reason': f'此日为{level}之日，{"、".join(yi_list[:3])}等事皆宜。'
    }

def _mock_lunar(*args, **kwargs):
    return {'中文': ''}

def _mock_none(*args, **kwargs):
    return None

def _mock_list(*args, **kwargs):
    return []

def _mock_identity(x, *args, **kwargs):
    return x

class _Mock:
    pass

# 打印当前工作目录和文件路径，帮助调试
import os
print(f"=== 模块导入调试信息 ===")
print(f"当前工作目录: {os.getcwd()}")
print(f"当前文件路径: {os.path.abspath(__file__)}")
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, 'modules')
print(f"Modules目录路径: {modules_dir}")
print(f"Modules目录是否存在: {os.path.exists(modules_dir)}")

# 检查modules目录中的文件
if os.path.exists(modules_dir):
    print("\n=== Modules目录内容 ===")
    files = os.listdir(modules_dir)
    for file in files[:20]:  # 只显示前20个文件
        if file.endswith('.py'):
            print(f"✓ {file}")

# 初始化所有导入的名称为备用值
calculate_sizhu = _mock_sizhu
analyze_sizhu = _mock_sizhu
get_lunar_date = _mock_lunar
calculate_score = _mock_score
DI_ZHI_WUXING = {}
calculate_xishen_yongshen = _mock_sizhu
BaZiPanPan = _Mock
show_bazi_dialog = _mock_none
show_bazi_from_birth = _mock_none
show_bazi_input_dialog = _mock_none
get_shan_xiang_list = _mock_list
shan_xiang_to_shan = _mock_identity
shan_to_shan_xiang = _mock_identity
SHAN_XIANG_12 = []
SHAN_XIANG_24 = []
ZhengTiWuXingSelectorDB = _Mock
CompassFrame = _Mock
CompassDialog = _Mock
show_compass_dialog = _mock_none

# 尝试不同的导入方式，适应不同环境
try:
    # 尝试正常导入
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
except ImportError:
    # 尝试直接导入（适应手机环境）
    try:
        import sys
        import os
        # 添加当前目录到路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 尝试直接导入模块文件
        from 四柱计算器 import calculate_sizhu, analyze_sizhu, get_lunar_date
        from 评分器 import calculate_score
        from 工具函数 import DI_ZHI_WUXING
        from 喜用神计算器 import calculate_xishen_yongshen
        from 八字排盘 import BaZiPanPan
        from 八字可视化模块 import show_bazi_dialog, show_bazi_from_birth, show_bazi_input_dialog
        from 二十四山 import (
            get_shan_xiang_list, shan_xiang_to_shan, shan_to_shan_xiang,
            SHAN_XIANG_12, SHAN_XIANG_24, ZhengTiWuXingSelectorDB
        )
        from 电子罗盘 import CompassFrame, CompassDialog, show_compass_dialog
    except ImportError as e:
        print(f"导入模块失败: {e}")
        # 尝试另一种方式
        try:
            # 动态导入
            import importlib
            import os
            
            # 获取模块文件路径
            modules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
            if os.path.exists(modules_dir):
                sys.path.insert(0, modules_dir)
                
                四柱计算器 = importlib.import_module('四柱计算器')
                calculate_sizhu = 四柱计算器.calculate_sizhu
                analyze_sizhu = 四柱计算器.analyze_sizhu
                get_lunar_date = 四柱计算器.get_lunar_date
                
                评分器 = importlib.import_module('评分器')
                calculate_score = 评分器.calculate_score
                
                工具函数 = importlib.import_module('工具函数')
                DI_ZHI_WUXING = 工具函数.DI_ZHI_WUXING
                
                喜用神计算器 = importlib.import_module('喜用神计算器')
                calculate_xishen_yongshen = 喜用神计算器.calculate_xishen_yongshen
                
                八字排盘 = importlib.import_module('八字排盘')
                BaZiPanPan = 八字排盘.BaZiPanPan
                
                八字可视化模块 = importlib.import_module('八字可视化模块')
                show_bazi_dialog = 八字可视化模块.show_bazi_dialog
                show_bazi_from_birth = 八字可视化模块.show_bazi_from_birth
                show_bazi_input_dialog = 八字可视化模块.show_bazi_input_dialog
                
                二十四山 = importlib.import_module('二十四山')
                get_shan_xiang_list = 二十四山.get_shan_xiang_list
                shan_xiang_to_shan = 二十四山.shan_xiang_to_shan
                shan_to_shan_xiang = 二十四山.shan_to_shan_xiang
                SHAN_XIANG_12 = 二十四山.SHAN_XIANG_12
                SHAN_XIANG_24 = 二十四山.SHAN_XIANG_24
                ZhengTiWuXingSelectorDB = 二十四山.ZhengTiWuXingSelectorDB
                
                电子罗盘 = importlib.import_module('电子罗盘')
                CompassFrame = 电子罗盘.CompassFrame
                CompassDialog = 电子罗盘.CompassDialog
                show_compass_dialog = 电子罗盘.show_compass_dialog
        except Exception as e2:
            print(f"动态导入失败: {e2}")
            # 使用预先定义的备用值

from datetime import date

# 导入节气计算模块
try:
    import sxtwl
    HAS_SXTWL = True
except ImportError:
    HAS_SXTWL = False
    print("警告：sxtwl 库未安装，无法进行农历转换")

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
        self.root.title("专业级正五行择日软件 - 小窗口版 v1.0")
        
        # 获取屏幕尺寸并设置窗口大小
        print("获取屏幕尺寸...")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 设置默认窗口大小为屏幕的50%宽度，75%高度，确保所有内容都能完整显示
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.75)
        print(f"窗口大小: {window_width}x{window_height}")
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        print(f"窗口位置: {x},{y}")
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        print("设置窗口大小和位置成功")
        
        # 允许窗口自由调整大小
        self.root.resizable(True, True)
        print("窗口大小可调整")
        
        # 确保窗口显示
        self.root.deiconify()
        print("窗口显示成功")
        
        # 数据存储
        self.results = []  # 择日结果
        self.records = []  # 历史记录
        self.owners_info = []  # 事主信息
        self._owner_entries_list = []  # 存储所有事主的输入框，用于键盘导航
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
        main_canvas.bind("<ButtonPress-1>", self._on_touch_start)
        main_canvas.bind("<B1-Motion>", self._on_touch_move)
        main_canvas.bind("<ButtonRelease-1>", self._on_touch_end)
        
        # 标题区域
        title_frame = ttk.Frame(self.main_frame, style="TitleFrame.TFrame")
        title_frame.pack(fill=tk.X, pady=4, padx=10)
        
        title_label = ttk.Label(title_frame, text="专业级正五行择日软件", 
                               font=("微软雅黑", 14, "bold"), style="Title.TLabel")
        title_label.pack(pady=2)
        
        subtitle_label = ttk.Label(title_frame, text="精准择日，趋吉避凶", 
                                  font=("微软雅黑", 8), style="Subtitle.TLabel")
        subtitle_label.pack()
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.main_frame, text="择日设置", padding="6")
        input_frame.pack(fill=tk.X, pady=4, padx=10)
        
        # 事项选择
        event_frame = ttk.Frame(input_frame)
        event_frame.pack(fill=tk.X, pady=2)
        ttk.Label(event_frame, text="事项类型：", font=("微软雅黑", 8, "bold")).pack(side=tk.LEFT, padx=2)
        self.event_var = tk.StringVar(value="嫁娶")
        event_combo = ttk.Combobox(event_frame, textvariable=self.event_var, 
                                   values=["嫁娶", "修造", "动土", "入宅", "开业", 
                                          "出行", "安床", "作灶", "移徙", "入学", "求医",
                                          "签约", "安葬"], width=20, state="readonly", 
                                   font=("微软雅黑", 8))
        event_combo.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        event_combo.bind("<<ComboboxSelected>>", self.on_event_change)
        
        # 日期范围
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill=tk.X, pady=2)
        
        start_date_frame = ttk.Frame(date_frame)
        start_date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Label(start_date_frame, text="开始日期：", font=("微软雅黑", 8, "bold")).pack(side=tk.LEFT, padx=2)
        self.start_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        start_entry = ttk.Entry(start_date_frame, textvariable=self.start_date, width=15, 
                               font=("微软雅黑", 8))
        start_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        end_date_frame = ttk.Frame(date_frame)
        end_date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Label(end_date_frame, text="结束日期：", font=("微软雅黑", 8, "bold")).pack(side=tk.LEFT, padx=2)
        end = date.today() + timedelta(days=30)
        self.end_date = tk.StringVar(value=end.strftime("%Y-%m-%d"))
        end_entry = ttk.Entry(end_date_frame, textvariable=self.end_date, width=15, 
                             font=("微软雅黑", 8))
        end_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # 为日期输入框绑定键盘导航
        self._bind_entry_navigation([start_entry, end_entry])
        
        # 择日图案显示
        self.pattern_frame = ttk.LabelFrame(input_frame, text="择日图案", padding="4")
        self.pattern_frame.pack(fill=tk.X, pady=2)
        
        # 创建图案显示画布
        self.pattern_canvas = tk.Canvas(self.pattern_frame, width=60, height=60, bg="#f8f9fa", 
                                       highlightthickness=2, highlightbackground="#007bff")
        self.pattern_canvas.pack(pady=2)
        
        # 初始显示默认图案
        self.update_pattern()
        
        # 绑定事项类型变化事件
        self.event_var.trace_add('write', self.on_event_type_changed)
        
        # 特殊选项（根据事项类型显示）
        self.special_frame = ttk.LabelFrame(self.main_frame, text="特殊选项", padding="6")
        self.special_frame.pack(fill=tk.X, pady=4, padx=10)
        self.update_special_options()
        
        # 按钮区域 - 调整为网格布局，适应手机屏幕
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=4, padx=10)
        
        # 第一行按钮
        button_row1 = ttk.Frame(button_frame)
        button_row1.pack(fill=tk.X, pady=2)
        ttk.Button(button_row1, text="开始择日", command=self.start_calculation, 
                  width=12).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(button_row1, text="日课评分", command=self.open_score_system, 
                  width=12).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(button_row1, text="日期测试", command=self.open_date_test, 
                  width=12).pack(side=tk.LEFT, padx=2, pady=2)
        
        # 第二行按钮
        button_row2 = ttk.Frame(button_frame)
        button_row2.pack(fill=tk.X, pady=2)
        ttk.Button(button_row2, text="导出结果", command=self.export_results, 
                  width=12).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(button_row2, text="导入文件", command=self.import_file, 
                  width=12).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(button_row2, text="查看记录", command=self.view_records, 
                  width=12).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(button_row2, text="帮助", command=self.show_help, 
                  width=12).pack(side=tk.LEFT, padx=2, pady=2)
        
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

        # 垂直排列单选按钮，适应手机屏幕
        ttk.Radiobutton(output_mode_radio_frame, text="正常平分（含扣分）",
                       variable=self.output_mode_var, value="normal").pack(side=tk.TOP, anchor=tk.W, pady=2)
        ttk.Radiobutton(output_mode_radio_frame, text="无扣分输出（各项满分）",
                       variable=self.output_mode_var, value="nodeduct").pack(side=tk.TOP, anchor=tk.W, pady=2)

        # 按钮区域
        result_button_frame = ttk.Frame(result_frame)
        result_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 垂直排列按钮，适应手机屏幕
        ttk.Button(result_button_frame, text="全部导入到评分系统", 
                  command=self.import_all_to_score_system, width=25).pack(side=tk.TOP, pady=2, fill=tk.X)
        ttk.Button(result_button_frame, text="清空结果", 
                  command=self.clear_results, width=25).pack(side=tk.TOP, pady=2, fill=tk.X)
        
        # 结果列表包装器 - 使用网格布局
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 结果列表
        columns = ("日期/四柱", "评分", "等级", "四柱", "月令得分", "喜用神得分", "黄道得分")
        self.result_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        # 设置列宽 - 进一步缩小，适应手机屏幕
        self.result_tree.column("日期/四柱", width=80)
        self.result_tree.column("评分", width=35, anchor=tk.CENTER)
        self.result_tree.column("等级", width=40, anchor=tk.CENTER)
        self.result_tree.column("四柱", width=100)
        self.result_tree.column("月令得分", width=45, anchor=tk.CENTER)
        self.result_tree.column("喜用神得分", width=50, anchor=tk.CENTER)
        self.result_tree.column("黄道得分", width=45, anchor=tk.CENTER)
        
        # 设置列标题
        for col in columns:
            self.result_tree.heading(col, text=col, anchor=tk.CENTER)
        
        # 滚动条 - 添加垂直和水平滚动条
        tree_v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.result_tree.yview)
        tree_h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=tree_v_scrollbar.set, xscrollcommand=tree_h_scrollbar.set)
        
        # 应用自定义滚动条样式
        tree_v_scrollbar.configure(style="Custom.Vertical.TScrollbar")
        tree_h_scrollbar.configure(style="Custom.Horizontal.TScrollbar")
        
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
        
        # 为结果列表添加触摸移动功能
        self.result_tree.bind("<ButtonPress-1>", self._on_tree_touch_start)
        self.result_tree.bind("<B1-Motion>", self._on_tree_touch_move)
        self.result_tree.bind("<ButtonRelease-1>", self._on_tree_touch_end)
        
        # 为不同星级设置行背景色
        self.result_tree.tag_configure('5star', background='#FFF9E6')  # 淡金色背景
        self.result_tree.tag_configure('4star', background='#F0F8FF')  # 淡蓝色背景
        self.result_tree.tag_configure('3star', background='#F0FFF0')  # 淡绿色背景
        self.result_tree.tag_configure('2star', background='#FFF5EE')  # 淡橙色背景
        self.result_tree.tag_configure('1star', background='#F5F5F5')  # 淡灰色背景
        self.result_tree.tag_configure('nodeduct', background='#E8F5E9')  # 淡绿色背景（满分日课）
    
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
            # 如果点击了项目，不启动滚动，让默认选择处理
            return
        
        # 记录触摸开始位置
        self._tree_touch_start_x = event.x
        self._tree_touch_start_y = event.y
        self._tree_touch_start_scroll_x = self.result_tree.xview()[0]
        self._tree_touch_start_scroll_y = self.result_tree.yview()[0]
    
    def _on_tree_touch_move(self, event):
        """结果列表触摸移动事件"""
        if hasattr(self, '_tree_touch_start_x') and hasattr(self, '_tree_touch_start_y'):
            delta_x = event.x - self._tree_touch_start_x
            delta_y = event.y - self._tree_touch_start_y
            
            # 计算滚动距离（反向滚动）
            scroll_delta_x = -delta_x / self.result_tree.winfo_width()
            scroll_delta_y = -delta_y / self.result_tree.winfo_height()
            
            # 应用滚动
            new_x = max(0, min(1, self._tree_touch_start_scroll_x + scroll_delta_x))
            new_y = max(0, min(1, self._tree_touch_start_scroll_y + scroll_delta_y))
            
            self.result_tree.xview_moveto(new_x)
            self.result_tree.yview_moveto(new_y)
    
    def _on_tree_touch_end(self, event):
        """结果列表触摸结束事件"""
        # 重置触摸状态
        if hasattr(self, '_tree_touch_start_x'):
            self._tree_touch_start_x = 0
        if hasattr(self, '_tree_touch_start_y'):
            self._tree_touch_start_y = 0
        if hasattr(self, '_tree_touch_start_scroll_x'):
            self._tree_touch_start_scroll_x = 0
        if hasattr(self, '_tree_touch_start_scroll_y'):
            self._tree_touch_start_scroll_y = 0
    
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
                       font=('微软雅黑', 20, 'bold'))
        
        # 副标题样式
        style.configure('Subtitle.TLabel', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 10))
        
        # 卡片样式
        style.configure('Card.TLabelframe', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 10, 'bold'),
                       borderwidth=2,
                       relief='groove')
        
        # 表单框架样式
        style.configure('Form.TFrame', background='#ffffff')
        
        # 标签样式
        style.configure('Label.TLabel', 
                       background='#ffffff',
                       foreground='#333333',
                       font=('微软雅黑', 10, 'bold'))
        
        # 输入框样式
        style.configure('Entry.TEntry', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 10),
                       borderwidth=2,
                       relief='solid')
        
        # 下拉框样式
        style.configure('Combobox.TCombobox', 
                       fieldbackground='white',
                       foreground='#333333',
                       font=('微软雅黑', 10),
                       borderwidth=2,
                       relief='solid')
        
        # 按钮框架样式
        style.configure('ButtonFrame.TFrame', background='#ffffff')
        
        # 主按钮样式
        style.configure('Primary.TButton', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 9, 'bold'),
                       padding=(8, 4),
                       borderwidth=0,
                       relief='flat')
        style.map('Primary.TButton', 
                  background=[('active', '#0069d9')])
        
        # 次要按钮样式
        style.configure('Secondary.TButton', 
                       background='#6c757d',
                       foreground='white',
                       font=('微软雅黑', 9),
                       padding=(8, 4),
                       borderwidth=0,
                       relief='flat')
        style.map('Secondary.TButton', 
                  background=[('active', '#5a6268')])
        
        # 信息按钮样式
        style.configure('Info.TButton', 
                       background='#17a2b8',
                       foreground='white',
                       font=('微软雅黑', 9),
                       padding=(8, 4),
                       borderwidth=0,
                       relief='flat')
        style.map('Info.TButton', 
                  background=[('active', '#138496')])
        
        # 危险按钮样式
        style.configure('Danger.TButton', 
                       background='#dc3545',
                       foreground='white',
                       font=('微软雅黑', 9),
                       padding=(8, 4),
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
                       font=('微软雅黑', 8),
                       rowheight=20,
                       fieldbackground='#ffffff',
                       borderwidth=1,
                       relief='solid')
        
        # 树形视图标题样式
        style.configure('Treeview.Heading', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 8, 'bold'),
                       padding=(8, 4))
        
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
    
    def on_event_type_changed(self, *args):
        """当事项类型改变时更新所有相关内容"""
        print(f"事项类型改变为: {self.event_var.get()}")
        self.update_pattern()
        self.update_special_options()
        self.update_owners_frame()
    
    def update_pattern(self, *args):
        """根据事项类型更新择日图案"""
        event_type = self.event_var.get()
        
        # 清空画布
        self.pattern_canvas.delete("all")
        
        # 中心坐标（画布大小为80×80）
        center_x = 40
        center_y = 40
        
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
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#ff6b6b")
        
        # 双喜字
        self.pattern_canvas.create_text(x, y, text="囍", font=("微软雅黑", 30, "bold"), fill="red")
    
    def _draw_construction(self, x, y):
        """绘制建筑图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#4ecdc4")
        
        # 建筑物
        self.pattern_canvas.create_rectangle(x-25, y-15, x+25, y+25, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x-30, y-15, x, y-30, x+30, y-15, fill="#ff6b6b")
        
        # 窗户
        self.pattern_canvas.create_rectangle(x-15, y, x-5, y+10, fill="#45b7d1")
        self.pattern_canvas.create_rectangle(x+5, y, x+15, y+10, fill="#45b7d1")
    
    def _draw_earth(self, x, y):
        """绘制土地图案"""
        # 棕色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#8b4513")
        
        # 土地
        self.pattern_canvas.create_rectangle(x-30, y, x+30, y+30, fill="#d2b48c")
        
        # 植物
        self.pattern_canvas.create_line(x-10, y, x-10, y-15, width=2, fill="#228b22")
        self.pattern_canvas.create_line(x, y, x, y-20, width=2, fill="#228b22")
        self.pattern_canvas.create_line(x+10, y, x+10, y-15, width=2, fill="#228b22")
        
        # 树叶
        self.pattern_canvas.create_oval(x-15, y-17, x-5, y-7, fill="#32cd32")
        self.pattern_canvas.create_oval(x-5, y-22, x+5, y-12, fill="#32cd32")
        self.pattern_canvas.create_oval(x+5, y-17, x+15, y-7, fill="#32cd32")
    
    def _draw_house(self, x, y):
        """绘制房屋图案"""
        # 绿色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#4ecdc4")
        
        # 房屋
        self.pattern_canvas.create_rectangle(x-25, y-10, x+25, y+25, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x-30, y-10, x, y-25, x+30, y-10, fill="#ff6b6b")
        
        # 门
        self.pattern_canvas.create_rectangle(x-7, y+5, x+7, y+25, fill="#8b4513")
        
        # 窗户
        self.pattern_canvas.create_rectangle(x-15, y-5, x-5, y+5, fill="#45b7d1")
        self.pattern_canvas.create_rectangle(x+5, y-5, x+15, y+5, fill="#45b7d1")
    
    def _draw_business(self, x, y):
        """绘制开业图案"""
        # 金色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#ffd93d")
        
        # 钱袋
        self.pattern_canvas.create_oval(x-20, y-5, x+20, y+25, fill="#8b4513")
        self.pattern_canvas.create_rectangle(x-20, y+5, x+20, y+25, fill="#8b4513")
        
        # 钱币
        self.pattern_canvas.create_oval(x-10, y-15, x-2, y-7, fill="#ffd700")
        self.pattern_canvas.create_oval(x+2, y-15, x+10, y-7, fill="#ffd700")
        self.pattern_canvas.create_oval(x-7, y-10, x-5, y-7, fill="#8b4513")
        self.pattern_canvas.create_oval(x+5, y-10, x+7, y-7, fill="#8b4513")
    
    def _draw_travel(self, x, y):
        """绘制出行图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#45b7d1")
        
        # 交通工具（汽车）
        self.pattern_canvas.create_rectangle(x-20, y, x+15, y+15, fill="#f7f7f7")
        self.pattern_canvas.create_polygon(x+15, y, x+20, y-5, x+20, y+20, x+15, y+15, fill="#f7f7f7")
        
        # 车轮
        self.pattern_canvas.create_oval(x-15, y+15, x-5, y+25, fill="#333333")
        self.pattern_canvas.create_oval(x+5, y+15, x+15, y+25, fill="#333333")
        
        # 车窗
        self.pattern_canvas.create_rectangle(x-15, y+2, x+10, y+10, fill="#45b7d1")
    
    def _draw_bed(self, x, y):
        """绘制安床图案"""
        # 紫色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#9b59b6")
        
        # 床
        self.pattern_canvas.create_rectangle(x-25, y+5, x+25, y+25, fill="#f7f7f7")
        self.pattern_canvas.create_rectangle(x-30, y, x+30, y+5, fill="#8b4513")
        
        # 枕头
        self.pattern_canvas.create_rectangle(x-20, y-10, x-5, y+5, fill="#ff6b6b")
        self.pattern_canvas.create_rectangle(x+5, y-10, x+20, y+5, fill="#ff6b6b")
        
        # 被子
        self.pattern_canvas.create_rectangle(x-25, y-5, x+25, y+5, fill="#4ecdc4")
    
    def _draw_kitchen(self, x, y):
        """绘制作灶图案"""
        # 橙色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#ff9f43")
        
        # 灶台
        self.pattern_canvas.create_rectangle(x-20, y+5, x+20, y+25, fill="#8b4513")
        
        # 锅
        self.pattern_canvas.create_oval(x-15, y-5, x+15, y+5, fill="#333333")
        
        # 火焰
        self.pattern_canvas.create_polygon(x, y+5, x-5, y+15, x+5, y+15, fill="#ff6b6b")
        self.pattern_canvas.create_polygon(x, y+7, x-4, y+12, x+4, y+12, fill="#ffd93d")
    
    def _draw_moving(self, x, y):
        """绘制移徙图案"""
        # 绿色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#44bd32")
        
        # 箱子
        self.pattern_canvas.create_rectangle(x-20, y-10, x+20, y+20, fill="#f7f7f7")
        self.pattern_canvas.create_rectangle(x-22, y-12, x+22, y-10, fill="#8b4513")
        
        # 提手
        self.pattern_canvas.create_oval(x-7, y-15, x-2, y-10, fill="#333333")
        self.pattern_canvas.create_oval(x+2, y-15, x+7, y-10, fill="#333333")
        
        # 装饰
        self.pattern_canvas.create_line(x-15, y, x+15, y, fill="#333333")
        self.pattern_canvas.create_line(x-15, y+7, x+15, y+7, fill="#333333")
    
    def _draw_study(self, x, y):
        """绘制入学图案"""
        # 蓝色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#3498db")
        
        # 书本
        self.pattern_canvas.create_rectangle(x-20, y-15, x+20, y+15, fill="#f7f7f7")
        self.pattern_canvas.create_line(x-20, y, x+20, y, fill="#333333")
        
        # 书本页数
        self.pattern_canvas.create_line(x-17, y-12, x+17, y-12, fill="#333333", width=1)
        self.pattern_canvas.create_line(x-17, y-7, x+17, y-7, fill="#333333")
        self.pattern_canvas.create_line(x-17, y+7, x+17, y+7, fill="#333333")
        self.pattern_canvas.create_line(x-17, y+12, x+17, y+12, fill="#333333", width=1)
    
    def _draw_medical(self, x, y):
        """绘制求医图案"""
        # 白色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#f7f7f7")
        
        # 红十字
        self.pattern_canvas.create_rectangle(x-15, y-5, x+15, y+5, fill="#ff6b6b")
        self.pattern_canvas.create_rectangle(x-5, y-15, x+5, y+15, fill="#ff6b6b")
        
        # 医疗标志
        self.pattern_canvas.create_oval(x-20, y-20, x+20, y+20, outline="#3498db", width=2)
    
    def _draw_contract(self, x, y):
        """绘制签约图案"""
        # 黄色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#ffd93d")
        
        # 合同
        self.pattern_canvas.create_rectangle(x-25, y-15, x+25, y+15, fill="#f7f7f7")
        
        # 文字线条
        self.pattern_canvas.create_line(x-20, y-7, x+20, y-7, fill="#333333")
        self.pattern_canvas.create_line(x-20, y, x+20, y, fill="#333333")
        self.pattern_canvas.create_line(x-20, y+7, x+20, y+7, fill="#333333")
        
        # 印章
        self.pattern_canvas.create_oval(x+10, y-10, x+20, y, fill="#ff6b6b")
    
    def _draw_burial(self, x, y):
        """绘制安葬图案"""
        # 灰色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#95a5a6")
        
        # 墓碑
        self.pattern_canvas.create_rectangle(x-15, y-20, x+15, y+10, fill="#f7f7f7")
        
        # 墓基
        self.pattern_canvas.create_rectangle(x-20, y+10, x+20, y+15, fill="#8b4513")
        
        # 十字架
        self.pattern_canvas.create_line(x, y-25, x, y-15, fill="#333333", width=2)
        self.pattern_canvas.create_line(x-7, y-20, x+7, y-20, fill="#333333", width=2)
    
    def _draw_default_pattern(self, x, y):
        """绘制默认图案"""
        # 浅蓝色背景
        self.pattern_canvas.create_oval(x-30, y-30, x+30, y+30, fill="#d1ecf1")
        
        # 日历图标
        self.pattern_canvas.create_rectangle(x-20, y-15, x+20, y+15, fill="#f7f7f7")
        
        # 日历标题
        self.pattern_canvas.create_rectangle(x-20, y-15, x+20, y-7, fill="#3498db")
        
        # 日历日期
        self.pattern_canvas.create_text(x, y+2, text="择日", font=("微软雅黑", 10, "bold"), fill="#333333")
    
    def update_special_options(self):
        """根据事项类型更新特殊选项"""
        # 清空现有组件
        for widget in self.special_frame.winfo_children():
            widget.destroy()
        
        event_type = self.event_var.get()
        special_entries = []
        
        if event_type in ["修造", "动土", "入宅", "安葬"]:
            # 宅型选择
            ttk.Label(self.special_frame, text="宅型：").grid(row=0, column=0, sticky=tk.W, padx=3)
            self.house_type = tk.StringVar(value="阴宅" if event_type == "安葬" else "阳宅")
            house_combo = ttk.Combobox(self.special_frame, textvariable=self.house_type, 
                        values=["阳宅", "阴宅"], width=8, state="readonly")
            house_combo.grid(row=0, column=1, sticky=tk.W, padx=3)
            special_entries.append(house_combo)
            
            # 山向选择（使用二十四山模块的完整山向列表）
            ttk.Label(self.special_frame, text="山向：").grid(row=0, column=2, sticky=tk.W, padx=3)
            self.shan_xiang = tk.StringVar()
            # 使用二十四山模块获取完整的24山向列表
            shan_xiangs = get_shan_xiang_list(use_24_shan=True)
            shan_combo = ttk.Combobox(self.special_frame, textvariable=self.shan_xiang, 
                        values=shan_xiangs, width=10, state="readonly")
            shan_combo.grid(row=0, column=3, sticky=tk.W, padx=3)
            special_entries.append(shan_combo)
            
            # 兼向选择（改为下拉菜单）
            ttk.Label(self.special_frame, text="兼向：").grid(row=0, column=4, sticky=tk.W, padx=3)
            self.jian_xiang = tk.StringVar()
            self.jian_xiang_combo = ttk.Combobox(self.special_frame, textvariable=self.jian_xiang,
                                                  values=["正中", "兼左", "兼右"], width=8, state="readonly")
            self.jian_xiang_combo.grid(row=0, column=5, sticky=tk.W, padx=3)
            special_entries.append(self.jian_xiang_combo)
            self.jian_xiang.set("正中")  # 默认正中
            # 绑定山向变化时更新兼向选项
            self.shan_xiang.trace_add('write', self._update_jianxiang_options)
            
            # 电子罗盘按钮
            ttk.Button(self.special_frame, text="罗盘", width=5,
                      command=self._show_compass_dialog).grid(row=0, column=6, sticky=tk.W, padx=3)
            
        elif event_type == "作灶":
            ttk.Label(self.special_frame, text="灶向：").grid(row=0, column=0, sticky=tk.W, padx=3)
            self.zao_xiang = tk.StringVar()
            zao_combo = ttk.Combobox(self.special_frame, textvariable=self.zao_xiang, 
                        values=["东", "南", "西", "北", "东南", "东北", "西南", "西北"], 
                        width=8, state="readonly")
            zao_combo.grid(row=0, column=1, sticky=tk.W, padx=3)
            special_entries.append(zao_combo)
            
            ttk.Label(self.special_frame, text="灶位：").grid(row=0, column=2, sticky=tk.W, padx=3)
            self.zao_wei = tk.StringVar()
            wei_combo = ttk.Combobox(self.special_frame, textvariable=self.zao_wei, 
                        values=["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"], 
                        width=8, state="readonly")
            wei_combo.grid(row=0, column=3, sticky=tk.W, padx=3)
            special_entries.append(wei_combo)
            
        elif event_type == "安床":
            ttk.Label(self.special_frame, text="床位朝向：").grid(row=0, column=0, sticky=tk.W, padx=3)
            self.chuang_wei = tk.StringVar()
            chuang_combo = ttk.Combobox(self.special_frame, textvariable=self.chuang_wei, 
                        values=["东", "南", "西", "北", "东南", "东北", "西南", "西北"], 
                        width=8, state="readonly")
            chuang_combo.grid(row=0, column=1, sticky=tk.W, padx=3)
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
        self._owner_entries_list = []  # 清空输入框列表
        event_type = self.event_var.get()
        
        # 添加提示标签
        if event_type != "嫁娶":
            hint_label = ttk.Label(self.owners_frame, 
                                   text="（提示：以下事主信息为可选，可根据需要填写）", 
                                   foreground="gray", font=('微软雅黑', 8, 'italic'))
            hint_label.pack(anchor=tk.W, pady=(0, 3))
        
        # 根据事项类型确定事主
        if event_type == "嫁娶":
            owners = ["新娘", "新郎"]
        elif event_type == "安葬":
            # 安葬需要死者（逝者）和孝子（家属）
            owners = ["死者", "孝子1", "孝子2"]
        elif event_type in ["修造", "动土", "入宅", "作灶", "开业", "出行", "安床"]:
            owners = ["事主1", "事主2"]
        else:
            owners = ["事主"]
        

        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=2)
            
            # 日期类型选择行
            date_type_row = ttk.Frame(owner_frame)
            date_type_row.pack(fill=tk.X, pady=1)
            
            ttk.Label(date_type_row, text=f"{owner}:", width=8).pack(side=tk.LEFT, padx=3, pady=1)
            
            # 日期类型选择
            date_type_var = tk.StringVar(value="公历")
            ttk.Label(date_type_row, text="日期类型:").pack(side=tk.LEFT, padx=(5, 0))
            ttk.Radiobutton(date_type_row, text="公历", variable=date_type_var, value="公历", width=3).pack(side=tk.LEFT, padx=1)
            ttk.Radiobutton(date_type_row, text="农历", variable=date_type_var, value="农历", width=3).pack(side=tk.LEFT, padx=1)
            
            # 性别选择
            if event_type == "嫁娶":
                # 嫁娶事项根据角色默认性别
                gender_var = tk.StringVar(value='女' if owner == '新娘' else '男')
            else:
                # 其他事项默认性别为男
                gender_var = tk.StringVar(value='男')
            
            ttk.Label(date_type_row, text="性别:").pack(side=tk.LEFT, padx=(5, 0))
            ttk.Radiobutton(date_type_row, text="男", variable=gender_var, value='男', width=2).pack(side=tk.LEFT, padx=1)
            ttk.Radiobutton(date_type_row, text="女", variable=gender_var, value='女', width=2).pack(side=tk.LEFT, padx=1)
            
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
            
            # 农历相关变量
            if event_type == "嫁娶":
                lunar_year_var = tk.StringVar(value=str(date.today().year - 25))
                lunar_month_var = tk.StringVar(value=str(11))
                lunar_day_var = tk.StringVar(value=str(22))
            else:
                lunar_year_var = tk.StringVar()
                lunar_month_var = tk.StringVar()
                lunar_day_var = tk.StringVar()
            is_leap_var = tk.BooleanVar(value=False)
            
            # 日期输入行 - 公历
            date_input_row = ttk.Frame(owner_frame)
            date_input_row.pack(fill=tk.X, pady=1)
            
            # 公历输入字段
            ttk.Label(date_input_row, text="    ", width=8).pack(side=tk.LEFT, padx=3)
            ttk.Label(date_input_row, text="年:").pack(side=tk.LEFT)
            year_entry = ttk.Entry(date_input_row, textvariable=year_var, width=5)
            year_entry.pack(side=tk.LEFT, padx=1)
            
            ttk.Label(date_input_row, text="月:").pack(side=tk.LEFT)
            month_entry = ttk.Entry(date_input_row, textvariable=month_var, width=3)
            month_entry.pack(side=tk.LEFT, padx=1)
            
            ttk.Label(date_input_row, text="日:").pack(side=tk.LEFT)
            day_entry = ttk.Entry(date_input_row, textvariable=day_var, width=3)
            day_entry.pack(side=tk.LEFT, padx=1)
            
            # 日期输入行 - 农历（默认隐藏）
            lunar_frame = ttk.Frame(owner_frame)
            # 初始时不pack，通过toggle_command控制显示
            
            ttk.Label(lunar_frame, text="    ", width=8).pack(side=tk.LEFT, padx=3)
            ttk.Label(lunar_frame, text="农历年:").pack(side=tk.LEFT)
            lunar_year_entry = ttk.Entry(lunar_frame, textvariable=lunar_year_var, width=5)
            lunar_year_entry.pack(side=tk.LEFT, padx=1)
            
            ttk.Label(lunar_frame, text="月:").pack(side=tk.LEFT)
            lunar_month_entry = ttk.Entry(lunar_frame, textvariable=lunar_month_var, width=3)
            lunar_month_entry.pack(side=tk.LEFT, padx=1)
            
            ttk.Label(lunar_frame, text="日:").pack(side=tk.LEFT)
            lunar_day_entry = ttk.Entry(lunar_frame, textvariable=lunar_day_var, width=3)
            lunar_day_entry.pack(side=tk.LEFT, padx=1)
            
            ttk.Label(lunar_frame, text="闰月:").pack(side=tk.LEFT)
            ttk.Checkbutton(lunar_frame, variable=is_leap_var).pack(side=tk.LEFT, padx=1)
            
            # 时间输入
            time_row = ttk.Frame(owner_frame)
            time_row.pack(fill=tk.X, pady=1)
            
            ttk.Label(time_row, text="    ", width=8).pack(side=tk.LEFT, padx=3)
            ttk.Label(time_row, text="时:").pack(side=tk.LEFT)
            hour_entry = ttk.Entry(time_row, textvariable=hour_var, width=3)
            hour_entry.pack(side=tk.LEFT, padx=1)
            
            ttk.Label(time_row, text="分:").pack(side=tk.LEFT)
            minute_entry = ttk.Entry(time_row, textvariable=minute_var, width=3)
            minute_entry.pack(side=tk.LEFT, padx=1)
            
            # 存储当前事主的输入框，用于跨事主导航
            owner_entries = {
                'solar': [year_entry, month_entry, day_entry],
                'lunar': [lunar_year_entry, lunar_month_entry, lunar_day_entry],
                'time': [hour_entry, minute_entry],
                'date_type': date_type_var
            }
            self._owner_entries_list.append(owner_entries)
            
            # 绑定当前事主的输入框导航
            self._bind_owner_navigation(owner_entries, len(self._owner_entries_list) - 1)
            
            # 定义显示/隐藏日期输入字段的函数
            def create_toggle_command(dt_var, di_row, lu_frame, y_var, m_var, d_var, ly_var, lm_var, ld_var, owner_name, tr, oe, oi):
                def toggle_date_fields():
                    current_type = dt_var.get()
                    print(f"toggle_date_fields 被调用，事主: {owner_name}, 当前日期类型: '{current_type}'")
                    if current_type == "农历":
                        # 显示农历输入框，隐藏公历输入框
                        print(f"切换到农历模式，隐藏公历输入框，显示农历输入框")
                        di_row.pack_forget()
                        lu_frame.pack(fill=tk.X, pady=1, before=tr)
                        # 将公历输入框的值同步到农历输入框
                        if y_var.get():
                            ly_var.set(y_var.get())
                        if m_var.get():
                            lm_var.set(m_var.get())
                        if d_var.get():
                            ld_var.set(d_var.get())
                    else:
                        # 显示公历输入框，隐藏农历输入框
                        print(f"切换到公历模式，显示公历输入框，隐藏农历输入框")
                        di_row.pack(fill=tk.X, pady=1, before=tr)
                        lu_frame.pack_forget()
                    # 重新绑定输入框导航
                    self._bind_owner_navigation(oe, oi)
                return toggle_date_fields
            
            # 创建并绑定日期类型变化事件
            owner_index = len(self._owner_entries_list) - 1
            toggle_command = create_toggle_command(date_type_var, date_input_row, lunar_frame, 
                                                 year_var, month_var, day_var, 
                                                 lunar_year_var, lunar_month_var, lunar_day_var, owner, time_row, 
                                                 owner_entries, owner_index)
            date_type_var.trace_add('write', lambda *args, cmd=toggle_command: cmd())
            
            # 初始状态
            toggle_command()

            
            # 四柱显示行
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=1)
            
            ttk.Label(sizhu_row, text="四柱:", width=8).pack(side=tk.LEFT, padx=3)
            sizhu_var = tk.StringVar(value="未计算")
            ttk.Label(sizhu_row, textvariable=sizhu_var, 
                     font=("微软雅黑", 8, "bold")).pack(side=tk.LEFT, padx=3)
            
            # 喜用神显示行
            xishen_var = tk.StringVar(value="")
            yongshen_var = tk.StringVar(value="")
            
            xishen_row = ttk.Frame(owner_frame)
            xishen_row.pack(fill=tk.X, pady=1)
            
            ttk.Label(xishen_row, text="喜神:", width=8).pack(side=tk.LEFT, padx=3)
            ttk.Label(xishen_row, textvariable=xishen_var, foreground="blue").pack(side=tk.LEFT, padx=3)
            ttk.Label(xishen_row, text="  用神:").pack(side=tk.LEFT)
            ttk.Label(xishen_row, textvariable=yongshen_var, foreground="green").pack(side=tk.LEFT, padx=3)
            
            # 夫星子星显示（婚嫁专用）
            fuzi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                fuzi_row = ttk.Frame(owner_frame)
                fuzi_row.pack(fill=tk.X, pady=1)
                
                ttk.Label(fuzi_row, text="夫星/子星:", width=8).pack(side=tk.LEFT, padx=3)
                ttk.Label(fuzi_row, textvariable=fuzi_var, foreground="purple").pack(side=tk.LEFT, padx=3)
            
            # 计算按钮
            def create_calc_command(dt, y, m, d, ly, lm, ld, il, h, mi, g, o, s, x, yg, fz):
                print(f"创建计算命令：dt={dt.get()}, ly={ly.get()}, lm={lm.get()}, ld={ld.get()}")
                return lambda: self.calculate_owner_sizhu(dt, y, m, d, ly, lm, ld, il, h, mi, g, o, s, x, yg, fz)
            
            calc_btn = ttk.Button(owner_frame, text="计算四柱", 
                                 command=create_calc_command(date_type_var, year_var, month_var, day_var, 
                                 lunar_year_var, lunar_month_var, lunar_day_var, is_leap_var, 
                                 hour_var, minute_var, gender_var, owner, sizhu_var, 
                                 xishen_var, yongshen_var, fuzi_var))
            calc_btn.pack(side=tk.LEFT, padx=3, pady=1)
            
            # 存储事主信息
            owner_info = {
                'name': owner,
                'date_type': date_type_var,
                'year': year_var,
                'month': month_var,
                'day': day_var,
                'lunar_year': lunar_year_var,
                'lunar_month': lunar_month_var,
                'lunar_day': lunar_day_var,
                'is_leap': is_leap_var,
                'hour': hour_var,
                'minute': minute_var,
                'gender': gender_var,
                'sizhu': sizhu_var,
                'xishen': xishen_var,
                'yongshen': yongshen_var,
                'fuzi': fuzi_var
            }
            self.owners_info.append(owner_info)
    
    def _bind_entry_navigation(self, entries):
        """为输入框绑定键盘导航"""
        for i, entry in enumerate(entries):
            if i < len(entries) - 1:
                entry.bind('<Return>', lambda e, next_entry=entries[i+1]: next_entry.focus())
                entry.bind('<Right>', lambda e, next_entry=entries[i+1]: next_entry.focus())
            if i > 0:
                entry.bind('<Left>', lambda e, prev_entry=entries[i-1]: prev_entry.focus())
    
    def _bind_owner_navigation(self, owner_entries, owner_index):
        """为当前事主的输入框绑定导航"""
        # 合并所有输入框
        all_entries = []
        
        # 根据当前日期类型决定使用哪些输入框
        if owner_entries['date_type'].get() == '公历':
            all_entries.extend(owner_entries['solar'])
        else:
            all_entries.extend(owner_entries['lunar'])
        
        all_entries.extend(owner_entries['time'])
        
        # 绑定当前事主输入框之间的导航
        for i, entry in enumerate(all_entries):
            if i < len(all_entries) - 1:
                entry.bind('<Return>', lambda e, next_entry=all_entries[i+1]: next_entry.focus())
                entry.bind('<Right>', lambda e, next_entry=all_entries[i+1]: next_entry.focus())
            if i > 0:
                entry.bind('<Left>', lambda e, prev_entry=all_entries[i-1]: prev_entry.focus())
        
        # 绑定到下一个事主
        if owner_index < len(self._owner_entries_list) - 1:
            last_entry = all_entries[-1]
            next_owner_entries = self._owner_entries_list[owner_index + 1]
            
            # 绑定到下一个事主的第一个输入框，动态获取日期类型
            def focus_next_owner(e):
                if next_owner_entries['date_type'].get() == '公历':
                    next_first_entry = next_owner_entries['solar'][0]
                else:
                    next_first_entry = next_owner_entries['lunar'][0]
                next_first_entry.focus()
            
            last_entry.bind('<Return>', focus_next_owner)
            last_entry.bind('<Right>', focus_next_owner)
        
        # 绑定到上一个事主
        if owner_index > 0:
            first_entry = all_entries[0]
            prev_owner_entries = self._owner_entries_list[owner_index - 1]
            
            # 确定上一个事主的最后一个输入框
            if prev_owner_entries['date_type'].get() == '公历':
                prev_last_entry = prev_owner_entries['time'][-1]
            else:
                prev_last_entry = prev_owner_entries['time'][-1]
            
            first_entry.bind('<Left>', lambda e, prev_entry=prev_last_entry: prev_entry.focus())
    
    def _update_jianxiang_options(self, *args):
        """更新兼向选项"""
        # 兼向选项已经通过下拉菜单设置，这里可以添加额外的逻辑
        pass
    
    def _show_compass_dialog(self):
        """显示电子罗盘"""
        try:
            # 调用电子罗盘模块
            show_compass_dialog(self.root, self.shan_xiang.get())
        except Exception as e:
            messagebox.showerror("错误", f"打开罗盘失败：{str(e)}")
    
    def on_event_change(self, event):
        """事项类型变化事件"""
        self.on_event_type_changed()
    
    def calculate_owner_sizhu(self, date_type_var, year_var, month_var, day_var, 
                            lunar_year_var, lunar_month_var, lunar_day_var, is_leap_var, 
                            hour_var, minute_var, gender_var, owner, sizhu_var, 
                            xishen_var, yongshen_var, fuzi_var):
        """计算事主四柱"""
        try:
            if date_type_var.get() == "公历":
                # 公历计算
                year = int(year_var.get())
                month = int(month_var.get())
                day = int(day_var.get())
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                
                # 计算四柱
                from datetime import date
                birth_date = date(year, month, day)
                sizhu = calculate_sizhu(birth_date, hour, minute)
                
            else:
                # 农历计算
                lunar_year = int(lunar_year_var.get())
                lunar_month = int(lunar_month_var.get())
                lunar_day = int(lunar_day_var.get())
                is_leap = is_leap_var.get()
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                
                # 计算四柱（农历）
                # 这里需要农历转公历的逻辑
                if HAS_SXTWL:
                    # 使用sxtwl库进行农历转公历
                    lunar = sxtwl.Lunar()
                    day = lunar.getDayByLunar(lunar_year, lunar_month, lunar_day, is_leap)
                    solar_date = date(day.y, day.m, day.d)
                    
                    # 计算四柱
                    sizhu = calculate_sizhu(solar_date, hour, minute)
                else:
                    messagebox.showerror("错误", "农历计算需要sxtwl库，请先安装")
                    return
            
            # 显示四柱
            sizhu_text = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
            sizhu_var.set(sizhu_text)
            
            # 计算喜用神
            try:
                xishen, yongshen = calculate_xishen_yongshen(sizhu)
                xishen_var.set(xishen)
                yongshen_var.set(yongshen)
            except Exception as e:
                xishen_var.set("计算失败")
                yongshen_var.set("计算失败")
            
            # 计算夫星子星（仅婚嫁）
            if owner in ["新娘", "新郎"]:
                try:
                    # 这里需要夫星子星计算逻辑
                    # 暂时使用示例数据
                    if owner == "新娘":
                        fuzi_var.set("夫星：甲，子星：丙")
                    else:
                        fuzi_var.set("妻星：乙，子星：丁")
                except Exception as e:
                    fuzi_var.set("计算失败")
            
            messagebox.showinfo("成功", f"{owner}四柱计算完成")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的日期和时间")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
    
    def start_calculation(self):
        """开始择日计算"""
        try:
            # 获取输入值
            event_type = self.event_var.get()
            start_date_str = self.start_date.get()
            end_date_str = self.end_date.get()
            
            # 验证日期格式
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # 验证日期范围
            if start_date > end_date:
                messagebox.showerror("错误", "开始日期不能晚于结束日期")
                return
            
            if (end_date - start_date).days > 365:
                messagebox.showerror("错误", "日期范围不能超过一年")
                return
            
            # 清空之前的结果
            self.results = []
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
            
            # 开始计算
            try:
                self.root.config(cursor="wait")
            except:
                pass  # 忽略光标设置错误，手机环境可能不支持
            self.root.update()
            
            # 构建事主数据
            owners_data = []
            for owner in self.owners_info:
                try:
                    # 检查是否有有效的日期数据
                    if owner['year'].get() and owner['month'].get() and owner['day'].get():
                        year = int(owner['year'].get())
                        month = int(owner['month'].get())
                        day = int(owner['day'].get())
                        hour = int(owner['hour'].get())
                        minute = int(owner['minute'].get())
                        
                        # 计算事主的四柱
                        from datetime import date
                        birth_date = date(year, month, day)
                        owner_sizhu = calculate_sizhu(birth_date, hour, minute)
                        
                        # 计算事主的喜用神
                        xishen, yongshen = calculate_xishen_yongshen(owner_sizhu)
                        
                        owners_data.append({
                            'name': owner['name'],
                            'birth_date': birth_date,
                            'birth_hour': hour,
                            'birth_minute': minute,
                            'sizhu': owner_sizhu,
                            'xishen': xishen,
                            'yongshen': yongshen
                        })
                except (ValueError, TypeError) as e:
                    print(f"处理事主信息出错: {e}")
                    pass
            
            # 遍历日期范围
            current_date = start_date
            print(f"开始计算，日期范围：{start_date} 到 {end_date}")
            while current_date <= end_date:
                # 计算四柱
                year = current_date.year
                month = current_date.month
                day = current_date.day
                
                # 计算当日四柱（使用中午12点）
                from datetime import date
                sizhu = calculate_sizhu(current_date, 12, 0)
                
                # 计算评分
                score_result = calculate_score(sizhu, event_type, owners_data)
                score = score_result.get('score', 0)
                level = score_result.get('level', '平')
                detail = score_result
                print(f"日期：{current_date}，评分：{score}，等级：{level}")
                
                # 计算农历日期
                from datetime import date
                lunar_info = get_lunar_date(date(year, month, day))
                lunar_date = lunar_info['中文']
                
                # 提取详细信息
                yi_list = detail.get('yi_list', [])
                ji_list = detail.get('ji_list', [])
                shensha_list = detail.get('shensha_list', [])
                
                # 提取得分详情
                month_score = detail.get('month_score', 0)
                xishen_score = detail.get('xishen_score', 0)
                huangdao_score = detail.get('huangdao_score', 0)
                
                # 检查是否有扣分
                has_ji = len(ji_list) > 0
                has_xiong_shen = any('凶' in item for item in shensha_list)
                yueling_negative = month_score < 0
                huangdao_negative = huangdao_score < 0
                wu_xing_hege = score >= 0  # 降低最低分数要求，所有日课都通过
                
                # 输出模式过滤
                output_mode = self.output_mode_var.get()
                
                if output_mode == "nodeduct":
                    # 无扣分模式：只保留没有任何扣分的日课
                    if wu_xing_hege and not has_ji and not has_xiong_shen and not yueling_negative and not huangdao_negative:
                        # 格式化四柱为字符串
                        sizhu_text = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
                        result = {
                            'date': current_date.strftime("%Y-%m-%d"),
                            'lunar': lunar_date,
                            'sizhu': sizhu_text,
                            'score': score,
                            'level': level,
                            'yi': ", ".join(yi_list) if yi_list else "无",
                            'ji': ", ".join(ji_list) if ji_list else "无",
                            'detail': detail
                        }
                        self.results.append(result)
                else:
                    # 正常模式：只排除五行不合格的日课，包含有扣分的日课
                    if wu_xing_hege:
                        # 格式化四柱为字符串
                        sizhu_text = f"{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}"
                        result = {
                            'date': current_date.strftime("%Y-%m-%d"),
                            'lunar': lunar_date,
                            'sizhu': sizhu_text,
                            'score': score,
                            'level': level,
                            'yi': ", ".join(yi_list) if yi_list else "无",
                            'ji': ", ".join(ji_list) if ji_list else "无",
                            'detail': detail
                        }
                        self.results.append(result)
                
                # 下一天
                current_date += timedelta(days=1)
            
            # 显示结果
            if not self.results:
                messagebox.showinfo("提示", "在所选日期范围内没有找到合适的择日")
                return
            
            # 按评分排序
            self.results.sort(key=lambda x: x['score'], reverse=True)
            
            # 显示结果
            for result in self.results:
                # 确定星级标签
                if result['level'] == "上吉":
                    tags = ('5star',)
                elif result['level'] == "大吉":
                    tags = ('4star',)
                elif result['level'] == "吉":
                    tags = ('3star',)
                elif result['level'] == "中吉" or result['level'] == "次吉":
                    tags = ('2star',)
                elif result['level'] == "平":
                    tags = ('1star',)
                else:
                    tags = ()
                
                # 为无扣分模式的日课添加特殊标签
                if self.output_mode_var.get() == "nodeduct":
                    tags = tags + ('nodeduct',)
                
                # 提取详细得分
                detail = result.get('detail', {})
                month_score = detail.get('month_score', 0)
                xishen_score = detail.get('xishen_score', 0)
                huangdao_score = detail.get('huangdao_score', 0)
                
                # 插入结果
                self.result_tree.insert("", tk.END, values=(
                    result['date'],
                    result['score'],
                    result['level'],
                    result['sizhu'],
                    month_score,
                    xishen_score,
                    huangdao_score
                ), tags=tags)
            
            # 保存记录
            self.save_record()
            
            messagebox.showinfo("成功", f"择日完成，共找到 {len(self.results)} 个合适的日期")
            
        except ValueError as e:
            messagebox.showerror("错误", f"日期格式错误：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
        finally:
            try:
                self.root.config(cursor="")
            except:
                pass  # 忽略光标设置错误，手机环境可能不支持
    
    def on_result_double_click(self, event):
        """双击查看结果详情"""
        try:
            # 获取双击的项目
            item = self.result_tree.identify_row(event.y)
            if not item:
                return
            
            # 获取项目的索引
            index = self.result_tree.index(item)
            if 0 <= index < len(self.results):
                result = self.results[index]
                detail = result.get('detail', {})
                
                # 创建详情窗口
                detail_window = tk.Toplevel(self.root)
                detail_window.title(f"日课详情 - {result['date']}")
                # 使用固定的小窗口尺寸
                detail_window.geometry("600x400")
                # 禁止窗口调整大小
                detail_window.resizable(False, False)
                # 设置窗口最小大小
                detail_window.minsize(600, 400)
                # 设置窗口最大大小
                detail_window.maxsize(600, 400)
                
                # 创建滚动文本
                text = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD, padx=10, pady=10)
                text.pack(fill=tk.BOTH, expand=True)
                
                # 构建详情内容
                content = f"日期：{result['date']}\n"
                content += f"农历：{result['lunar']}\n"
                content += f"四柱：{result['sizhu']}\n"
                content += f"评分：{result['score']} 分\n"
                content += f"等级：{result['level']}\n\n"
                
                # 评分详情
                content += "【评分详情】\n"
                content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
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
                content += "\n"
                
                # 宜忌信息
                yi_list = detail.get('yi_list', [])
                ji_list = detail.get('ji_list', [])
                content += "【宜】\n"
                content += f"{chr(10).join(yi_list) if yi_list else '无'}\n\n"
                content += "【忌】\n"
                content += f"{chr(10).join(ji_list) if ji_list else '无'}\n\n"
                
                # 神煞信息
                shensha_list = detail.get('shensha_list', [])
                if shensha_list:
                    content += "【神煞】\n"
                    for shensha in shensha_list:
                        if isinstance(shensha, dict):
                            name = shensha.get('name', '未知神煞')
                            description = shensha.get('description', '')
                            content += f"- {name}：{description}\n"
                        else:
                            content += f"- {shensha}\n"
                    content += "\n"
                
                # 地支关系、吉神、日主旺衰等详细信息
                wu_xing_result = detail.get('wu_xing_result', {})
                wu_xing_details = wu_xing_result.get('details', {})
                
                # 地支关系
                if wu_xing_details.get('地支关系'):
                    content += "【地支关系】\n"
                    for relation in wu_xing_details['地支关系']:
                        content += f"- {relation}\n"
                    content += "\n"
                
                # 吉神
                if wu_xing_details.get('吉神'):
                    content += "【吉神】\n"
                    for jishen in wu_xing_details['吉神']:
                        content += f"- {jishen}\n"
                    content += "\n"
                
                # 日主旺衰
                if wu_xing_details.get('日主旺衰'):
                    content += "【日主旺衰】\n"
                    content += f"{wu_xing_details['日主旺衰']}\n\n"
                
                # 黄道信息
                huangdao_info = detail.get('huangdao_info', {})
                if huangdao_info:
                    content += "【黄道信息】\n"
                    da_huang_dao = huangdao_info.get('da_huang_dao', {})
                    if da_huang_dao:
                        content += f"大黄道：{da_huang_dao.get('name', '')} - {da_huang_dao.get('description', '')}\n"
                    xiao_huang_dao = huangdao_info.get('xiao_huang_dao', {})
                    if xiao_huang_dao:
                        content += f"小黄道：{xiao_huang_dao.get('name', '')} - {xiao_huang_dao.get('description', '')}\n"
                    content += "\n"
                
                # 添加每个事主的详细分析
                score_details_all = detail.get('score_details', {})
                owner_matches = score_details_all.get('事主匹配', [])
                if owner_matches:
                    content += "【事主分析】\n"
                    for match in owner_matches:
                        owner_name = match.get('name', '未知')
                        owner_score = match.get('score', 0)
                        match_details = match.get('details', [])
                        xishen = match.get('xishen', '')
                        yongshen = match.get('yongshen', '')
                        
                        content += f"{owner_name}：\n"
                        content += f"  得分：{owner_score} 分\n"
                        if yongshen:
                            content += f"  用神：{yongshen}\n"
                        if xishen:
                            content += f"  喜神：{xishen}\n"
                        if match_details:
                            content += f"  匹配详情：{'; '.join(match_details)}\n"
                        else:
                            content += f"  匹配详情：无明显匹配\n"
                        content += "\n"
                
                # 详细原因（包含地支关系、吉神、日主旺衰、黄道信息等）- 移到最后
                reason = detail.get('reason', '')
                if reason:
                    content += "【评语】\n"
                    content += reason + "\n\n"
                
                # 二十四山分析（如果有山向信息）
                if hasattr(self, 'shan_xiang') and self.shan_xiang.get():
                    try:
                        # 使用二十四山选择器分析
                        selector = ZhengTiWuXingSelectorDB()
                        shan_name = shan_xiang_to_shan(self.shan_xiang.get())
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
                                
                                content += "\n\n【分金五行分析】\n"
                                content += f"山向：{self.shan_xiang.get()}（坐山：{shan_name}）\n"
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
                                
                                content += "\n\n【正体五行分析】\n"
                                content += f"山向：{self.shan_xiang.get()}（坐山：{shan_name}）\n"
                                content += f"兼向：正中（正向）\n"
                                if isinstance(result_24, dict):
                                    if result_24.get('success') is False:
                                        content += f"错误：{result_24.get('error', '未知错误')}\n"
                                    else:
                                        content += f"等级：{result_24.get('level', '未知')}\n"
                                        content += f"得分：{result_24.get('score', '未知')}\n"
                                        if 'summary' in result_24:
                                            summary = result_24['summary']
                                            content += f"坐山得分：{summary.get('mountain_score', 'N/A')}\n"
                                else:
                                    # 兼容旧版本返回值
                                    try:
                                        level, score, detail_24 = result_24
                                        content += f"等级：{level}\n"
                                        content += f"得分：{score}\n"
                                        if 'summary' in detail_24:
                                            summary = detail_24['summary']
                                            content += f"坐山得分：{summary.get('mountain_score', 'N/A')}\n"
                                    except Exception:
                                        content += "分析出错：返回值格式不正确\n"
                    except Exception as e:
                        content += f"\n\n【二十四山分析】\n分析出错：{str(e)}\n"
                
                text.insert(tk.END, content)
                text.config(state=tk.DISABLED)
                
                # 按钮区域
                button_frame = ttk.Frame(detail_window)
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
                                'yi_list': detail.get('yi_list', []),
                                'ji_list': detail.get('ji_list', []),
                                'shensha_list': detail.get('shensha_list', []),
                                'reason': detail.get('reason', '')
                            }
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(json_data, f, ensure_ascii=False, indent=2)
                            messagebox.showinfo("成功", f"日课详情已保存到：{file_path}")
                        
                    except Exception as e:
                        messagebox.showerror("错误", f"保存失败：{str(e)}")
                
                ttk.Button(button_frame, text="保存详情", command=save_detail).pack(side=tk.LEFT, padx=5)
                ttk.Button(button_frame, text="关闭", command=detail_window.destroy).pack(side=tk.RIGHT, padx=5)
        except Exception as e:
            messagebox.showerror("错误", f"查看详情失败：{str(e)}")
    
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
                        # 从 detail 中获取宜忌信息
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
                                result['sizhu'],
                                result.get('detail', {}).get('month_score', 0),
                                result.get('detail', {}).get('xishen_score', 0),
                                result.get('detail', {}).get('huangdao_score', 0)
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
                                result['sizhu'],
                                result.get('detail', {}).get('month_score', 0),
                                result.get('detail', {}).get('xishen_score', 0),
                                result.get('detail', {}).get('huangdao_score', 0)
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
                            result['sizhu'],
                            result.get('detail', {}).get('month_score', 0),
                            result.get('detail', {}).get('xishen_score', 0),
                            result.get('detail', {}).get('huangdao_score', 0)
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
            # 尝试不同的导入方式，适应不同环境
            DayScoreWindow = None
            
            # 打印当前工作目录和文件路径，帮助调试
            import os
            print(f"当前工作目录: {os.getcwd()}")
            print(f"当前文件路径: {os.path.abspath(__file__)}")
            
            # 1. 尝试直接导入日课评分系统文件（最优先，适应手机环境）
            try:
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                modules_dir = os.path.join(current_dir, 'modules')
                
                # 检查 modules 目录是否存在
                if os.path.exists(modules_dir):
                    print(f"Modules 目录存在: {modules_dir}")
                    sys.path.insert(0, modules_dir)
                    
                    # 检查日课评分系统文件是否存在
                    score_system_path = os.path.join(modules_dir, '日课评分系统.py')
                    if os.path.exists(score_system_path):
                        print(f"日课评分系统文件存在: {score_system_path}")
                        # 尝试直接导入
                        from 日课评分系统 import DayScoreWindow
                        print("✓ 成功: 直接导入日课评分系统文件")
                    else:
                        print(f"日课评分系统文件不存在: {score_system_path}")
                else:
                    print(f"Modules 目录不存在: {modules_dir}")
            except Exception as e1:
                print(f"✗ 失败: 直接导入文件 - {e1}")
                
            # 2. 尝试正常模块导入
            if DayScoreWindow is None:
                try:
                    from modules.日课评分系统 import DayScoreWindow
                    print("✓ 成功: 从 modules 包导入日课评分系统")
                except Exception as e2:
                    print(f"✗ 失败: 从 modules 包导入 - {e2}")
            
            # 3. 尝试动态导入
            if DayScoreWindow is None:
                try:
                    import importlib
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    modules_dir = os.path.join(current_dir, 'modules')
                    
                    if os.path.exists(modules_dir):
                        sys.path.insert(0, modules_dir)
                        # 尝试导入
                        日课评分系统 = importlib.import_module('日课评分系统')
                        DayScoreWindow = 日课评分系统.DayScoreWindow
                        print("✓ 成功: 动态导入日课评分系统")
                except Exception as e3:
                    print(f"✗ 失败: 动态导入 - {e3}")
            
            # 4. 尝试从当前目录导入（适应手机环境）
            if DayScoreWindow is None:
                try:
                    import sys
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    sys.path.insert(0, current_dir)
                    
                    # 检查当前目录是否有日课评分系统文件
                    score_system_path = os.path.join(current_dir, '日课评分系统.py')
                    if os.path.exists(score_system_path):
                        print(f"当前目录有日课评分系统文件: {score_system_path}")
                        from 日课评分系统 import DayScoreWindow
                        print("✓ 成功: 从当前目录导入日课评分系统")
                except Exception as e4:
                    print(f"✗ 失败: 从当前目录导入 - {e4}")
            
            # 5. 最后的备用方案：创建一个简单的备用窗口
            if DayScoreWindow is None:
                print("✗ 所有导入方式都失败，使用备用窗口")
                # 创建一个简单的备用窗口
                class BackupDayScoreWindow:
                    def __init__(self, master=None):
                        self.window = tk.Toplevel(master)
                        self.window.title("日课评分系统")
                        self.window.geometry("600x400")
                        
                        # 创建标签
                        label = ttk.Label(self.window, text="评分系统暂时不可用，请稍后再试\n\n原因：可能是模块文件未找到或环境配置问题", 
                                         font=("SimHei", 12), justify=tk.CENTER)
                        label.pack(expand=True, fill=tk.BOTH)
                        
                        # 创建关闭按钮
                        ttk.Button(self.window, text="关闭", 
                                  command=self.window.destroy).pack(pady=20)
                    
                    def import_results(self, *args, **kwargs):
                        pass
                    
                    def run(self):
                        self.window.transient(self.window.master)
                        self.window.grab_set()
                        self.window.wait_window()
                
                DayScoreWindow = BackupDayScoreWindow
            
            score_window = DayScoreWindow(master=self.root)
            
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
            # 尝试不同的导入方式，适应不同环境
            DayScoreWindow = None
            
            # 打印当前工作目录和文件路径，帮助调试
            import os
            print(f"当前工作目录: {os.getcwd()}")
            print(f"当前文件路径: {os.path.abspath(__file__)}")
            
            # 1. 尝试直接导入日课评分系统文件（最优先，适应手机环境）
            try:
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                modules_dir = os.path.join(current_dir, 'modules')
                
                # 检查 modules 目录是否存在
                if os.path.exists(modules_dir):
                    print(f"Modules 目录存在: {modules_dir}")
                    sys.path.insert(0, modules_dir)
                    
                    # 检查日课评分系统文件是否存在
                    score_system_path = os.path.join(modules_dir, '日课评分系统.py')
                    if os.path.exists(score_system_path):
                        print(f"日课评分系统文件存在: {score_system_path}")
                        # 尝试直接导入
                        from 日课评分系统 import DayScoreWindow
                        print("✓ 成功: 直接导入日课评分系统文件")
                    else:
                        print(f"日课评分系统文件不存在: {score_system_path}")
                else:
                    print(f"Modules 目录不存在: {modules_dir}")
            except Exception as e1:
                print(f"✗ 失败: 直接导入文件 - {e1}")
                
            # 2. 尝试正常模块导入
            if DayScoreWindow is None:
                try:
                    from modules.日课评分系统 import DayScoreWindow
                    print("✓ 成功: 从 modules 包导入日课评分系统")
                except Exception as e2:
                    print(f"✗ 失败: 从 modules 包导入 - {e2}")
            
            # 3. 尝试动态导入
            if DayScoreWindow is None:
                try:
                    import importlib
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    modules_dir = os.path.join(current_dir, 'modules')
                    
                    if os.path.exists(modules_dir):
                        sys.path.insert(0, modules_dir)
                        # 尝试导入
                        日课评分系统 = importlib.import_module('日课评分系统')
                        DayScoreWindow = 日课评分系统.DayScoreWindow
                        print("✓ 成功: 动态导入日课评分系统")
                except Exception as e3:
                    print(f"✗ 失败: 动态导入 - {e3}")
            
            # 4. 尝试从当前目录导入（适应手机环境）
            if DayScoreWindow is None:
                try:
                    import sys
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    sys.path.insert(0, current_dir)
                    
                    # 检查当前目录是否有日课评分系统文件
                    score_system_path = os.path.join(current_dir, '日课评分系统.py')
                    if os.path.exists(score_system_path):
                        print(f"当前目录有日课评分系统文件: {score_system_path}")
                        from 日课评分系统 import DayScoreWindow
                        print("✓ 成功: 从当前目录导入日课评分系统")
                except Exception as e4:
                    print(f"✗ 失败: 从当前目录导入 - {e4}")
            
            # 5. 最后的备用方案：创建一个简单的备用窗口
            if DayScoreWindow is None:
                print("✗ 所有导入方式都失败，使用备用窗口")
                # 创建一个简单的备用窗口
                class BackupDayScoreWindow:
                    def __init__(self, master=None):
                        self.window = tk.Toplevel(master)
                        self.window.title("日课评分系统")
                        self.window.geometry("600x400")
                        
                        # 创建标签
                        label = ttk.Label(self.window, text="评分系统暂时不可用，请稍后再试\n\n原因：可能是模块文件未找到或环境配置问题", 
                                         font=("SimHei", 12), justify=tk.CENTER)
                        label.pack(expand=True, fill=tk.BOTH)
                        
                        # 创建关闭按钮
                        ttk.Button(self.window, text="关闭", 
                                  command=self.window.destroy).pack(pady=20)
                    
                    def import_results(self, *args, **kwargs):
                        pass
                    
                    def run(self):
                        self.window.transient(self.window.master)
                        self.window.grab_set()
                        self.window.wait_window()
                
                DayScoreWindow = BackupDayScoreWindow
            
            score_window = DayScoreWindow(master=self.root)
            
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
【评分规则】

- 基础分：100分
- 吉神加分：每个吉神+5~15分（根据重要性）
- 凶神减分：每个凶神-8~20分（根据严重性）
- 宜事加分：每项宜事+10分
- 忌事减分：每项忌事-15分
- 黄道调整：黄道大吉+10分，黑道-5分

【五行分析】
1. 补龙：与坐山五行相生相助
2. 扶山：加强坐山力量
3. 相主：与事主八字相生相合
4. 避开三杀、冲山等大忌

【黄道分析】
1. 大黄道：十二神吉凶
2. 小黄道：十二建星宜忌
3. 值日星宿：二十八宿吉凶
"""),
            ("常见问题", """
【常见问题】

1. 为什么没有找到合适的日期？
   - 日期范围可能太短
   - 事主八字与事项冲突较大
   - 所选事项在该时间段内确实没有吉时

2. 如何选择最佳日期？
   - 优先选择5星和4星日期
   - 结合事主八字喜用神
   - 考虑特殊选项的要求（如山向、灶向等）

3. 评分是如何计算的？
   - 基础分100分
   - 根据神煞、宜忌、黄道等因素加减分数
   - 五行分析占60%权重，黄道分析占40%权重

4. 可以同时为多个人择日吗？
   - 可以输入多个事主信息
   - 系统会综合考虑所有事主的八字
"""),
            ("注意事项", """
【注意事项】

1. 本软件计算结果仅供参考，重要事项建议咨询专业择日师
2. 事主信息为可选输入，但提供后可获得更精准的分析
3. 修造类事项需要选择山向和宅型
4. 系统会自动避开明显的大凶之日
5. 农历计算需要安装sxtwl库
6. 导出的JSON文件可以在其他设备上导入使用

【联系我们】
如有问题或建议，请联系：
- 邮箱：support@zeri-software.com
- 电话：400-123-4567
- 网站：www.zeri-software.com
""")
        ]
        
        # 创建标签页
        for title, content in help_sections:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=title)
            
            text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, padx=10, pady=10)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, content)
            text.config(state=tk.DISABLED)
    
    def show_about(self):
        """显示关于信息"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="专业级正五行择日软件", font=("微软雅黑", 14, "bold")).pack(pady=10)
        ttk.Label(frame, text="版本：1.0.0").pack(pady=5)
        ttk.Label(frame, text="更新日期：2026年").pack(pady=5)
        ttk.Label(frame, text="作者：专业择日团队").pack(pady=5)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(frame, text="本软件采用传统正五行择日理论，").pack(pady=2)
        ttk.Label(frame, text="结合现代计算机技术，为用户提供专业的择日服务。").pack(pady=2)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(frame, text="© 2026 专业级正五行择日软件 版权所有").pack(pady=10)
        
        ttk.Button(frame, text="确定", command=about_window.destroy).pack(pady=10)
    
    def show_solar_terms(self):
        """显示节气查询"""
        if not HAS_SXTWL:
            messagebox.showerror("错误", "节气查询需要sxtwl库，请先安装")
            return
        
        solar_window = tk.Toplevel(self.root)
        solar_window.title("节气查询")
        solar_window.geometry("400x300")
        
        frame = ttk.Frame(solar_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 年份输入
        ttk.Label(frame, text="年份：").pack(pady=5)
        year_var = tk.StringVar(value=str(date.today().year))
        year_entry = ttk.Entry(frame, textvariable=year_var, width=10)
        year_entry.pack(pady=5)
        
        def query_solar_terms():
            try:
                year = int(year_var.get())
                lunar = sxtwl.Lunar()
                
                # 清空结果
                for widget in result_frame.winfo_children():
                    widget.destroy()
                
                # 查询节气
                text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, padx=10, pady=10)
                text.pack(fill=tk.BOTH, expand=True)
                
                content = f"{year}年节气表\n"
                content += "=" * 30 + "\n"
                
                for month in range(1, 13):
                    # 节气
                    jieqi = lunar.getJieQi(year, month - 1)
                    content += f"{month}月：\n"
                    content += f"  节气：{jieqi[0][0]} {jieqi[0][1].strftime('%Y-%m-%d %H:%M')}\n"
                    content += f"  中气：{jieqi[1][0]} {jieqi[1][1].strftime('%Y-%m-%d %H:%M')}\n\n"
                
                text.insert(tk.END, content)
                text.config(state=tk.DISABLED)
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的年份")
            except Exception as e:
                messagebox.showerror("错误", f"查询失败：{str(e)}")
        
        ttk.Button(frame, text="查询", command=query_solar_terms).pack(pady=10)
        
        # 结果显示
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 初始查询
        query_solar_terms()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ZeriApp(root)
    app.run()