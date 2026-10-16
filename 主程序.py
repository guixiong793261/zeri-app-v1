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

【星级等级划分】（2026-09-02起：等级完全由综合评分决定，同分同级）
⭐⭐⭐⭐⭐ (5星) = 上吉（105分以上）
⭐⭐⭐⭐ (4星) = 大吉（100-104分）
⭐⭐⭐ (3星) = 吉（85-99分）
⭐⭐ (2星) = 中吉（75-84分）
⭐ (1星) = 平（60-74分）
❌ (0星) = 凶（<60分，或五行评分<60的五行凶日）

【判级原则】
1. 等级由综合评分唯一决定，同分必同级（五行/黄道影响已体现在总分中）
2. 例外：五行评分<60（五行凶）直接判凶，不因月令/喜用/黄道加分标吉
3. 婚嫁事项总分构成不同，等级阈值另行独立计算（150/130/110/90/70）

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
import re
import sys
import collections

# 输出编码兜底：中文 Windows 下 print 到 GBK 控制台/日志管道时，
# ❌✅⭐ 等字符会抛 UnicodeEncodeError 中断计算，改为自动替换不可编码字符
try:
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if sys.stderr is not None and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(errors="replace")
except Exception:
    pass

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.四柱计算器 import calculate_sizhu, analyze_sizhu, get_lunar_date
from modules.评分器 import calculate_score, Scorer
from modules.工具函数 import DI_ZHI_WUXING, TIAN_GAN_WUXING
from modules.黄道 import 黄道计算器
from modules.喜用神计算器 import calculate_xishen_yongshen
from modules.八字排盘 import BaZiPanPan
from modules.八字可视化模块 import show_bazi_dialog, show_bazi_from_birth, show_bazi_input_dialog
from modules.二十四山 import (
    get_shan_xiang_list, shan_xiang_to_shan, shan_to_shan_xiang,
    SHAN_XIANG_12, SHAN_XIANG_24, ZhengTiWuXingSelectorDB
)
from modules.二十四山择吉天机 import (
    get_mountain_data, check_mountain_day, check_sansha,
    check_yinfu, check_chong_shan, calculate_keshan_yun,
    calculate_xingyao_sha, get_yinfu_config, get_mountain_wuxing
)
from modules.电子罗盘 import CompassFrame, CompassDialog, show_compass_dialog
from modules.城市经度 import CITY_NAMES, get_longitude, filter_cities

# 导入节气计算模块
try:
    import sxtwl
    HAS_SXTWL = True
except ImportError:
    HAS_SXTWL = False

# 事件类型分组（2026-09-16 口径统一：唯一来源 modules/事项标准.py，禁止在此另列事项）
# SHAN_EVENTS 为 UI 山向段落分组（含历史标签上梁/竖柱）；MARRIAGE_EVENTS 含订婚/纳采等别名；
# FEIXING_EVENTS 为玄空飞星参与事项（含别名），与评分器飞星口径一致。
from modules.事项标准 import SHAN_UI_EVENTS as SHAN_EVENTS, MARRIAGE_EVENTS, MARRIAGE_UI_EVENTS, FEIXING_EVENTS, UI_EVENTS


def _fmt_score(v, empty='-'):
    """得分列通用格式化：非0强制带±号，0显示'0'，None/空显示empty
    对齐日课详情页 {:+d} 的显示规则，解决问题一：择日结果表黄道扣分显示不明确。"""
    if v is None or v == '' or v == '-':
        return empty
    try:
        num = int(v)
    except (TypeError, ValueError):
        try:
            num = int(float(v))
        except (TypeError, ValueError):
            return str(v)
    return '0' if num == 0 else f"{num:+d}"

def _parse_owner_longitude(longitude_var, show_warning=True):
    """事主经度输入解析（真太阳时立项，2026-09-29，001 §43.9 拍板③/§48）。

    字符串→float 明确处理：None/空串/缺键 → 120.0（北京时间基准，不启用）；
    合法浮点 → 原值返回；非法字符串或越界 → 弹窗警告并回退 120.0
    （不静默吞错——静默失败家族防御，与 §45 同口径）。
    经度=120 等价于不启用（北京时间基准）。

    show_warning=False：扫日/导出/详情等下游批处理回路不重复弹窗——
    输入入口 calculate_owner_sizhu 已显式警告过一次，回路中非法值
    静默回退 120.0 属明示设计（与入口提示配套），非吞错。
    """
    raw = longitude_var.get() if hasattr(longitude_var, 'get') else longitude_var
    if raw is None or str(raw).strip() == '':
        return 120.0
    try:
        longitude = float(str(raw).strip())
    except (TypeError, ValueError):
        if show_warning:
            messagebox.showwarning(
                "经度格式", f"经度「{raw}」无法解析为数字，已按 120°E（北京时间）处理。\n"
                "请填写出生地东经度数（如 成都 104.1、乌鲁木齐 87.6）。")
        return 120.0
    # 与 modules/真太阳时.py 有效域一致：[60, 150]°E
    if not (60.0 <= longitude <= 150.0):
        if show_warning:
            messagebox.showwarning(
                "经度越界", f"经度 {longitude}°E 超出有效域 [60, 150]，已按 120°E（北京时间）处理。\n"
                "本软件仅支持 UTC+8 时区，海外用户请先换算为北京时间。")
        return 120.0
    return longitude

def _fmt_tree_date_sizhu(date, sizhu):
    """结果表首列：日期一行、四柱一行（Treeview 加大行高后单元格内 \\n 可多行渲染）。
    2026-09-03 用户要求：四柱并入"日期/四柱"列，与列标题对应。"""
    return f"{date or ''}\n{sizhu or '-'}"

def _fmt_tree_relation(text):
    """地支关系列：首个分号处换行（最多两行），配合加宽列与两行行高，
    让长关系文本完整可见（2026-09-03 用户要求全部信息可见）。"""
    s = str(text or '')
    parts = s.split("；")
    if len(parts) >= 2:
        return parts[0] + "\n" + "；".join(parts[1:])
    return s

def _extract_tree_dizhi_jishen(score_result):
    """结果表“地支关系/吉神”两列文本提取（统一入口，2026-09-05）。

    从 score_result['wu_xing_result']['details'] 提取：
    - 地支关系：带主体完整文本，去掉（示例时柱/推荐时柱…）计分后缀，取前2条分号连接
    - 吉神：规范化名称，取前2条逗号连接
    _inject_best_hour_to_result 第(5)步会用权威四柱（含推荐时柱）重算 details，
    注入后再次调用本函数刷新两列，即可让地支关系反映真实推荐时辰
    参与的关系，而非基准午时示例（2026-09-05 用户确认）。
    """
    try:
        _wr = (score_result or {}).get('wu_xing_result') or {}
        details = _wr.get('details') or {}
    except Exception:
        details = {}
    rels = details.get('地支关系') or []
    if rels:
        dizhi_text = '；'.join([re.sub(r'（(?:示例时柱|推荐时柱)[^）]*）', '', _r) for _r in rels][:2])
    else:
        dizhi_text = '-'
    jishen_list = details.get('吉神') or []
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
    return dizhi_text, jishen_text




def _fenjin_preview_penalty(sx_full, nian, yue, ri, shi, yi_list, ssl):
    """2026-09-11: preview of inject block (6) fenjin recheck.
    Returns (level, deduct): 0=clean, 1=medium hit (deduct applied),
    2=severe without mitigation (veto). Same criteria as block (6), so
    hour ranking never prefers an hour that (6) will penalize later."""
    try:
        if not sx_full or '\u5c71' not in sx_full:
            return 0, 0
        import importlib as _il
        _m24 = _il.import_module('modules.\u4e8c\u5341\u56db\u5c71')
        _FJ = _m24.ZhengTiWuXingSelectorDB
        _fjs = _FJ()
        _sn = sx_full.split('\u5c71')[0].strip()
        if '\u517c' in sx_full:
            _jx = '\u517c' + sx_full.rsplit('\u517c', 1)[1][:1]
            _fjr = _fjs.evaluate_with_fengjin(_sn, _jx, nian, yue, ri, shi,
                                              use_fengjin_wuxing=True)
        else:
            _fjr = _fjs.evaluate_by_name(_sn, nian, yue, ri, shi)
        if not (isinstance(_fjr, dict) and _fjr.get('success', True)):
            return 0, 0
        _fs = _fjr.get('score', 0)
        _lvl = _fjr.get('level', '')
        _hit = _lvl in ('\u5927\u51f6', '\u51f6(\u72af\u5927\u715e)') or (
            isinstance(_fs, (int, float)) and _fs <= -30)
        if not _hit:
            return 0, 0
        _severe = isinstance(_fs, (int, float)) and _fs <= -50
        _good_qual = isinstance(ssl, list) and any(
            isinstance(_s, dict) and int(_s.get('score', 0) or 0) >= 10 for _s in ssl)
        _has_zhi = False
        if isinstance(yi_list, list):
            for _j in yi_list:
                _t = str(_j)
                if any(_kw in _t for _kw in
                       ['\uff08\u6709\u5236\u5316\uff1a', '\u5929\u5fb7', '\u6708\u5fb7', '\u5c81\u5fb7',
                        '\u5929\u4e59', '\u592a\u9633', '\u592a\u9634', '\u7389\u5802', '\u9752\u9f99']):
                    _has_zhi = True
                    break
        if not _has_zhi and _good_qual:
            _has_zhi = True
        if _severe and not _has_zhi:
            return 2, 100
        _deduct = 30 if _severe else (20 if _fs <= -40 else (15 if _fs <= -30 else 10))
        return 1, _deduct
    except Exception:
        return 0, 0


def _fmt_feixing(feixing_info):
    """结果表"玄空"列文本（2026-09-02）：飞星等级+带符号评分，如"大吉+15"/"大凶-20"。
    0分显示"大凶0"（与_fmt_score的0显示规则一致）。
    无飞星信息（非修造安葬类/未填坐山/否决课）显示 '-'。"""
    try:
        if not isinstance(feixing_info, dict) or not feixing_info:
            return '-'
        lv = str(feixing_info.get('feixing_level') or '')
        sc = feixing_info.get('feixing_score')
        if sc is None:
            return lv or '-'
        sc_i = int(sc)
        sc_txt = '0' if sc_i == 0 else f"{sc_i:+d}"
        return f"{lv}{sc_txt}"
    except Exception:
        return '-'


def _star_row_tag(level):
    """等级文本（含★数）→ 结果表行标签 '5star'..'1star'/''。
    2026-09-16 口径统一：正常择日与条件择日结果表共用同一判定。"""
    s = str(level or '')
    for _n in (5, 4, 3, 2, 1):
        if '★' * _n in s:
            return f'{_n}star'
    return ''


def _owners_fingerprint(owners):
    """事主信息指纹（推荐时柱缓存键用，模块级函数便于脱离实例的测试桩复用）。

    owners 为 start_calculation 预取的普通 dict 列表（值仅 str/int/date 等
    可稳定 repr 的类型，不含 Tk 变量）。用排序后的 (键, repr(值)) 元组，
    保证内容一致即指纹一致：不受 dict 键顺序影响，也不依赖 list 对象身份。
    """
    if not isinstance(owners, list):
        return ()
    _fp = []
    for _o in owners:
        if isinstance(_o, dict):
            _fp.append(tuple(sorted((str(_k), repr(_v))
                                    for _k, _v in _o.items())))
        else:
            _fp.append(repr(_o))
    return tuple(_fp)


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

    # 得分格式化（类内同名单点入口，方便self调用）
    _fmt_score = staticmethod(_fmt_score)
    _fmt_tree_date_sizhu = staticmethod(_fmt_tree_date_sizhu)
    _fmt_tree_relation = staticmethod(_fmt_tree_relation)

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
        tools_menu.add_command(label="胎神查询", command=self.open_taishen_query)
        tools_menu.add_command(label="今日黄历", command=self.open_today_huangli)
        tools_menu.add_command(label="择日贴", command=self.open_zeeri_tie)
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
                                   values=UI_EVENTS, width=20, state="readonly",
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
        
        # _zm0915 择日模式：纯正五行（协纪辨方书，默认；玄空飞星/年家五黄二黑紫白封禁不参与择日）
        # / 正五行+玄空飞星（2026-09-15前的“正常择日”混合规则，改名保留）
        zeli_mode_frame = ttk.LabelFrame(self.main_frame, text="择日模式", padding="8")
        zeli_mode_frame.pack(fill=tk.X, pady=6, padx=20)
        self.zeli_mode_var = tk.StringVar(value="pure")
        ttk.Radiobutton(zeli_mode_frame, text="纯正五行（协纪辨方书）",
                        variable=self.zeli_mode_var, value="pure",
                        command=self._on_zeli_mode_change).pack(side=tk.TOP, anchor=tk.W, pady=2)
        ttk.Radiobutton(zeli_mode_frame, text="正五行+玄空飞星",
                        variable=self.zeli_mode_var, value="feixing",
                        command=self._on_zeli_mode_change).pack(side=tk.TOP, anchor=tk.W, pady=2)

        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=8, padx=20)
        
        ttk.Button(button_frame, text="分析年份", command=self.analyze_year, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="分析月份", command=self.analyze_month, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="开始择日", command=self.start_calculation, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="条件择日", command=self.conditional_calculation, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="日课评分", command=self.open_score_system, 
                  width=12).pack(side=tk.LEFT, padx=6)
        self.xuankong_btn = ttk.Button(button_frame, text="玄空飞星", command=self.open_xuankong,
                          width=12)  # _zm0915：纯正五行模式隐藏，飞星模式显示
        if self._get_zeli_mode() == 'feixing':
            self.xuankong_btn.pack(side=tk.LEFT, padx=6)
        self.date_test_btn = ttk.Button(button_frame, text="日期测试", command=self.open_date_test,
                          width=12)
        self.date_test_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="导出结果", command=self.export_results, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="导入文件", command=self.import_file, 
                  width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="查看记录", command=self.view_records, 
                  width=12).pack(side=tk.LEFT, padx=6)
        self.zeeri_tie_btn = ttk.Button(button_frame, text="择日贴", command=self.open_zeeri_tie, 
                  width=12)
        self.zeeri_tie_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="帮助", command=self.show_help, 
                  width=12).pack(side=tk.RIGHT, padx=6)
        # 初始化择日贴暂存区（右键加入的日课先暂存，点「择日贴」按键时再载入显示）
        self._zeri_tie_pending = []
        
        # ===== 进度条区域 =====
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=5, padx=20)

        # ---- 配置进度条样式（绿色） ----
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Green.Horizontal.TProgressbar",
                        background='#00cc00',
                        troughcolor='#e0e0e0',
                        bordercolor='#00cc00',
                        lightcolor='#00cc00',
                        darkcolor='#00cc00')

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400,
            style="Green.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.progress_label = ttk.Label(
            progress_frame,
            text="就绪",
            font=("微软雅黑", 9),
            foreground="#666"
        )
        self.progress_label.pack(side=tk.RIGHT)

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
        ttk.Radiobutton(output_mode_radio_frame, text="不合格输出（仅显示否决/凶日）",
                       variable=self.output_mode_var, value="unqualified").pack(side=tk.TOP, anchor=tk.W, pady=2)

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
        
        # 结果列表（2026-09-03：四柱并入"日期/四柱"列两行显示，删除独立四柱列）
        columns = ("日期/四柱", "评分", "等级", "五行得分", "月令得分", "喜用神得分", "黄道得分", "地支关系", "吉神信息", "利月", "事主信息", "玄空")
        self.result_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

        # 设置列宽（2026-09-08 用户反馈：地支关系太宽挤占吉神信息）：
        # 地支关系固定宽度容纳两行文本，不再独占拉伸余量；吉神信息加宽并接管 stretch，
        # 让"天乙贵人 ㄅ 凶-20"等内容完整可见。
        self.result_tree.column("日期/四柱", width=140, anchor=tk.W, stretch=False)
        self.result_tree.column("评分", width=48, anchor=tk.CENTER, stretch=False)
        self.result_tree.column("等级", width=104, anchor=tk.CENTER, stretch=False)
        self.result_tree.column("五行得分", width=62, anchor=tk.CENTER, stretch=False)
        self.result_tree.column("月令得分", width=62, anchor=tk.CENTER, stretch=False)
        self.result_tree.column("喜用神得分", width=76, anchor=tk.CENTER, stretch=False)
        self.result_tree.column("黄道得分", width=62, anchor=tk.CENTER, stretch=False)
        self.result_tree.column("地支关系", width=300, anchor=tk.W, stretch=False)
        self.result_tree.column("吉神信息", width=200, anchor=tk.W, stretch=True)
        self.result_tree.column("利月", width=56, anchor=tk.CENTER, stretch=False)
        self.result_tree.column("事主信息", width=80, anchor=tk.W, stretch=False)
        self.result_tree.column("玄空", width=66, anchor=tk.CENTER, stretch=False)
        
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

        # 右键日课加入择日贴
        self.result_tree.bind("<Button-3>", self.on_result_right_click)
        
        # 绑定鼠标悬停效果
        self.result_tree.bind("<Motion>", self.on_tree_motion)
        
        # 绑定触摸事件到结果树
        self.result_tree.bind("<Button-1>", self._on_tree_touch_start)
        self.result_tree.bind("<B1-Motion>", self._on_tree_touch_move)
        self.result_tree.bind("<ButtonRelease-1>", self._on_tree_touch_end)

        # 左键单击某个日期 → 提示用玄空飞星分析（延迟触发，双击查看详情时自动取消）
        self._xk_after = None
        self.result_tree.bind("<Button-1>", self._xk_click_schedule, add="+")
        
        # 为不同星级设置行背景色
        self.result_tree.tag_configure('5star', background='#FFF9E6')  # 淡金色背景
        self.result_tree.tag_configure('4star', background='#F0F8FF')  # 淡蓝色背景
        self.result_tree.tag_configure('3star', background='#F0FFF0')  # 淡绿色背景
        self.result_tree.tag_configure('2star', background='#FFF5EE')  # 淡橙色背景
        self.result_tree.tag_configure('1star', background='#F5F5F5')  # 淡灰色背景

        # 列显示初始化：事主信息栏一律不显示，利月栏仅嫁娶类事项显示
        self._update_result_columns()
    
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
                       rowheight=40,
                       fieldbackground='#ffffff',
                       borderwidth=1,
                       relief='solid')
        
        # 树形视图标题样式（左右内边距压缩到5，确保窄列表头文字完整显示）
        style.configure('Treeview.Heading',
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 10, 'bold'),
                       padding=(5, 4))

        # 树形视图悬停样式
        style.map('Treeview.Treeview',
                  background=[('selected', '#cce7ff'), ('!selected', '#ffffff')],
                  foreground=[('selected', '#007bff'), ('!selected', '#333333')])

        # 默认 Treeview 样式（结果表等未显式指定 style 的控件实际使用此样式名）
        # 行高40：容纳"日期/四柱""地支关系"单元格内两行文本，避免第二行被裁切
        style.configure('Treeview',
                        background='#ffffff',
                        foreground='#333333',
                        font=('微软雅黑', 10),
                        rowheight=40,
                        fieldbackground='#ffffff',
                        borderwidth=1,
                        relief='solid')
        style.map('Treeview',
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

        # 事项类型变化时同步刷新结果表列显示（利月/事主信息栏可见性）
        self._update_result_columns()

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
        elif event_type == "拆舍":
            # 绘制拆除图案（使用修造图案）
            self._draw_construction(center_x, center_y)
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
        
        if event_type in ["修造", "动土", "拆舍", "入宅"]:
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
            # §59.13 拍板②兜底3：可下拉选环序兼向，也可手动输入"兼X"（如"兼亥"）
            # 覆盖系统环序映射；非相邻山由引擎标记为"手动覆盖"
            self.jian_xiang_combo = ttk.Combobox(self.special_frame, textvariable=self.jian_xiang,
                                                  values=["正中", "兼左", "兼右"], width=10)
            self.jian_xiang_combo.grid(row=0, column=5, sticky=tk.W, padx=5)
            special_entries.append(self.jian_xiang_combo)
            self.jian_xiang.set("正中")  # 默认正中
            # §59.13 批次一细节4：失焦/回车行内即时提示（不拦输入不改值）
            self._jx_hint_label = ttk.Label(self.special_frame, text="")
            self._jx_hint_label.grid(row=0, column=7, sticky=tk.W, padx=2)
            self.jian_xiang_combo.bind('<FocusOut>', lambda e: self._update_jx_hint())
            self.jian_xiang_combo.bind('<Return>', lambda e: self._update_jx_hint())
            # 绑定山向变化时更新兼向选项
            self.shan_xiang.trace_add('write', self._update_jianxiang_options)
            
            # 电子罗盘按钮
            ttk.Button(self.special_frame, text="罗盘", width=6,
                      command=self._show_compass_dialog).grid(row=0, column=6, sticky=tk.W, padx=5)

        elif event_type == "安葬":
            # 安葬（阴宅）择日必以墓穴坐山为纲：坐山+兼向+罗盘（_azss0914）
            ttk.Label(self.special_frame, text="坐山：").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.shan_xiang = tk.StringVar()
            shan_xiangs = get_shan_xiang_list(use_24_shan=True)
            shan_combo = ttk.Combobox(self.special_frame, textvariable=self.shan_xiang,
                        values=shan_xiangs, width=12, state="readonly")
            shan_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
            special_entries.append(shan_combo)

            # 兼向选择
            ttk.Label(self.special_frame, text="兼向：").grid(row=0, column=2, sticky=tk.W, padx=5)
            self.jian_xiang = tk.StringVar()
            # §59.13 拍板②兜底3：可下拉选环序兼向，也可手动输入"兼X"（如"兼亥"）
            # 覆盖系统环序映射；非相邻山由引擎标记为"手动覆盖"
            self.jian_xiang_combo = ttk.Combobox(self.special_frame, textvariable=self.jian_xiang,
                                                  values=["正中", "兼左", "兼右"], width=10)
            self.jian_xiang_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
            special_entries.append(self.jian_xiang_combo)
            self.jian_xiang.set("正中")
            # §59.13 批次一细节4：失焦/回车行内即时提示（不拦输入不改值）
            self._jx_hint_label = ttk.Label(self.special_frame, text="")
            self._jx_hint_label.grid(row=0, column=7, sticky=tk.W, padx=2)
            self.jian_xiang_combo.bind('<FocusOut>', lambda e: self._update_jx_hint())
            self.jian_xiang_combo.bind('<Return>', lambda e: self._update_jx_hint())
            self.shan_xiang.trace_add('write', self._update_jianxiang_options)

            # 电子罗盘按钮 + 必填提示
            ttk.Button(self.special_frame, text="罗盘", width=6,
                      command=self._show_compass_dialog).grid(row=0, column=4, sticky=tk.W, padx=5)
            ttk.Label(self.special_frame, text="安葬必选坐山").grid(
                row=0, column=5, columnspan=2, sticky=tk.W, padx=2)

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

            # 2026-09 作灶主事人模式：男主人（宅主，默认）/女主人/双主
            ttk.Label(self.special_frame, text="主事人：").grid(row=0, column=4, sticky=tk.W, padx=5)
            self.zaozhu_mode = tk.StringVar(value="男主人")
            for _zi, _ztxt in enumerate(("男主人(宅主)", "女主人", "双主")):
                _zrb = ttk.Radiobutton(self.special_frame, text=_ztxt, variable=self.zaozhu_mode,
                                       value=_ztxt.split('(')[0])
                _zrb.grid(row=0, column=5 + _zi, sticky=tk.W, padx=2)
                special_entries.append(_zrb)
            
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
    
    def _require_shan_for_burial(self, event_type=None):
        """安葬（阴宅）择日必须结合墓穴坐山（2026-09-14 用户明确口径，_azss0914）。
        无坐山则三煞坐山、山家封禁（五黄/二黑）、玄空飞星等阴宅核心判定全部落空，
        故事先拦截；非安葬事项一律放行。True=可继续，False=已弹窗拦截。"""
        if event_type is None:
            event_type = self.event_var.get()
        if event_type != '安葬':
            return True
        _sv = getattr(self, 'shan_xiang', None)
        if _sv is not None and str(_sv.get() or '').strip():
            return True
        messagebox.showwarning(
            "请先选择墓穴坐山",
            "安葬择日与嫁娶不同，必须结合墓穴的坐山（二十四山）才能计算。\n\n"
            "未选坐山时，三煞坐山、山家封禁（五黄/二黑）、玄空飞星等阴宅核心判定\n"
            "均无法进行。请先在上方“坐山”栏选择墓穴坐山（或点“罗盘”选山），再开始计算。")
        return False

    def _tag_zaozhu_owners(self, owners_data):
        """2026-09 作灶主事人模式：按 UI 所选 男主人(默认)/女主人/双主 为打包后的事主写入
        _zaozhu_primary（是否主事人：被日支冲即一票否决；双主两主皆 True）与
        _zaozhu_weight（1.0/0.5：辅助者半权重参与喜用神/生肖相主/神煞匹配）。"""
        mode_v = getattr(self, 'zaozhu_mode', None)
        mode = mode_v.get() if hasattr(mode_v, 'get') else (mode_v or '男主人')
        if mode not in ('男主人', '女主人', '双主'):
            mode = '男主人'
        if mode == '双主':
            for _o in owners_data:
                _o['_zaozhu_primary'] = True
                _o['_zaozhu_weight'] = 1.0
            return
        want = '男' if mode == '男主人' else '女'
        primary_idx = None
        for _i, _o in enumerate(owners_data):
            if _o.get('性别') == want:
                primary_idx = _i
                break
        if primary_idx is None:
            # 兜底：无对应性别事主时，男主人模式取首位、女主人模式取末位
            primary_idx = 0 if want == '男' else (len(owners_data) - 1 if owners_data else 0)
        for _i, _o in enumerate(owners_data):
            _ok = (_i == primary_idx)
            _o['_zaozhu_primary'] = _ok
            _o['_zaozhu_weight'] = 1.0 if _ok else 0.5

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
        
        # 城市选择绑定工厂（必须在 for 循环外定义：循环内闭包晚绑定会让所有
        # 卡片处理器共享循环结束后的最后一组变量）
        def bind_city_selector(city_combo, city_v, longitude_v):
            def apply():
                lng = get_longitude(city_v.get())
                if lng is not None:
                    longitude_v.set(str(lng))
                    return True
                return False

            def on_selected(_event=None):
                apply()

            def on_type(event):
                if event.keysym in ('Return', 'Tab'):
                    apply()
                    return
                text = city_v.get()
                if get_longitude(text) is not None:
                    apply()
                else:
                    city_combo['values'] = filter_cities(text)

            def on_focusout(_event=None):
                apply()

            city_combo.bind('<<ComboboxSelected>>', on_selected)
            city_combo.bind('<KeyRelease>', on_type)
            city_combo.bind('<FocusOut>', on_focusout)

        # 根据事项类型确定事主
        if event_type == "嫁娶":
            owners = ["新娘", "新郎"]
        elif event_type == "安葬":
            owners = ["死者", "孝子1", "孝子2", "孝子3"]
        elif event_type == "作灶":
            # 2026-09：作灶首重宅主（男主人），女主人为辅（主事模式可在上方切换）
            owners = ["宅主", "女主人"]
        elif event_type == "安床":
            # 安床以夫妻双方为主，尤重女主人（求子），女主人置首卡
            owners = ["女主人", "宅主"]
        elif event_type in ["修造", "动土", "拆舍", "入宅", "开业", "出行"]:
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
            elif owner == '女主人':
                # 作灶/安床女主人卡片默认女
                gender_var = tk.StringVar(value='女')
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

            # 出生地经度（真太阳时立项，2026-09-29，001 §43.9 拍板③/§48）：
            # 默认 120=北京时间；普通用户经下方「城市」下拉自动填经度（001 §51）
            longitude_var = tk.StringVar(value="120")
            ttk.Label(date_row, text="经度:").pack(side=tk.LEFT, padx=(10, 0))
            longitude_entry = ttk.Entry(date_row, textvariable=longitude_var, width=6)
            longitude_entry.pack(side=tk.LEFT, padx=2)
            all_entries.append(longitude_entry)
            ttk.Label(date_row, text="(120=北京时间;可直接改)",
                      foreground="gray").pack(side=tk.LEFT)

            # 城市选择（主入口）：选城市 → 经度自动填入；支持打字过滤
            city_row = ttk.Frame(owner_frame)
            city_row.pack(fill=tk.X, pady=1)
            city_var = tk.StringVar(value="")
            ttk.Label(city_row, text="城市:").pack(side=tk.LEFT, padx=(10, 0))
            city_combo = ttk.Combobox(city_row, textvariable=city_var,
                                      values=CITY_NAMES, width=18)
            city_combo.pack(side=tk.LEFT, padx=2)
            bind_city_selector(city_combo, city_var, longitude_var)
            ttk.Label(city_row, text="(选城市自动填经度;可输入字过滤)",
                      foreground="gray").pack(side=tk.LEFT)

            # 四柱显示行
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(sizhu_row, text="四柱:", width=10).pack(side=tk.LEFT, padx=5)
            sizhu_var = tk.StringVar(value="未计算")
            ttk.Label(sizhu_row, textvariable=sizhu_var,
                     font=("微软雅黑", 10, "bold")).pack(side=tk.LEFT, padx=5)
            # 真太阳时口径标注（§48）：独立于 sizhu_var 文本，避免污染下游
            # _parse_owner 对四柱串的 split() 解析（长度==4 检查）
            true_solar_flag_var = tk.StringVar(value="")
            ttk.Label(sizhu_row, textvariable=true_solar_flag_var,
                      foreground="darkgreen").pack(side=tk.LEFT, padx=2)
            
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
                
                # 阴胎行（新娘）/阳气行（新郎）：阴胎属女命、阳气属男命，
                # 2026-09-14 修正归属：阳气归位新郎卡片，各显示在本人名下
                if owner == "新娘":
                    yintai_row = ttk.Frame(owner_frame)
                    yintai_row.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(yintai_row, text="阴胎:", width=10).pack(side=tk.LEFT, padx=5)
                    ttk.Label(yintai_row, textvariable=yintai_var, foreground="green").pack(side=tk.LEFT, padx=5)
                    
                    # 阴胎属新娘：保存为实例变量，供calculate_owner_sizhu联动使用
                    self.yintai_var = yintai_var
                if owner == "新郎":
                    # 阳气属新郎（男命）：显示在新郎本人卡片
                    yangqi_row = ttk.Frame(owner_frame)
                    yangqi_row.pack(fill=tk.X, pady=2)
                    
                    ttk.Label(yangqi_row, text="阳气:", width=10).pack(side=tk.LEFT, padx=5)
                    ttk.Label(yangqi_row, textvariable=yangqi_var, foreground="red").pack(side=tk.LEFT, padx=5)
                    
                    self.yangqi_var = yangqi_var
            
            # 计算按钮
            calc_btn = ttk.Button(owner_frame, text="计算四柱",
                                 command=lambda y=year_var, m=month_var, d=day_var,
                                 h=hour_var, mi=minute_var, g=gender_var, o=owner, s=sizhu_var,
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var, yt=yintai_var, yq=yangqi_var,
                                 ct=calendar_type_var, z=zodiac_var, fx=fu_xing_var, zx=zi_xing_var,
                                 lo=longitude_var, tsf=true_solar_flag_var:
                                 self.calculate_owner_sizhu(y, m, d, h, mi, g, o, s, x, yg, fz, yt, yq, ct, z, fx, zx, lo, tsf))
            calc_btn.pack(side=tk.LEFT, padx=5, pady=2)

             # 八字排盘详情按钮
            detail_btn = ttk.Button(owner_frame, text="八字排盘详情",
                                   command=lambda y=year_var, m=month_var, d=day_var,
                                   h=hour_var, mi=minute_var, g=gender_var, o=owner,
                                   lo=longitude_var:
                                   self.show_owner_bazi_detail(y, m, d, h, mi, g, o, lo))
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
                'longitude': longitude_var,
                'birth_city': city_var,
                'true_solar_flag_var': true_solar_flag_var,
                'gender': gender_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var,
                'yintai_var': yintai_var,
                'yangqi_var': yangqi_var,
                # 2026-09-17 修复 Bug1：补 calendar_type_var 键
                #   否则 calculate_owner_sizhu L2495 / _parse_owner L7493 读取恒 None，
                #   用户勾"农历"输入生辰仍按公历排，四柱/生肖/喜用神全错。
                'calendar_type_var': calendar_type_var
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
                    # 使用更安全的方式获取字段值
                    year_var = owner_info.get('year')
                    month_var = owner_info.get('month')
                    day_var = owner_info.get('day')
                    year_str = year_var.get() if year_var and hasattr(year_var, 'get') else ''
                    month_str = month_var.get() if month_var and hasattr(month_var, 'get') else ''
                    day_str = day_var.get() if day_var and hasattr(day_var, 'get') else ''
                    
                    # 检查是否填写了日期（年、月、日都必须填写）
                    if not (year_str and month_str and day_str):
                        continue
                    
                    hour_var = owner_info.get('hour')
                    minute_var = owner_info.get('minute')
                    gender_var = owner_info.get('gender')
                    hour_str = hour_var.get() if hour_var and hasattr(hour_var, 'get') else '12'
                    minute_str = minute_var.get() if minute_var and hasattr(minute_var, 'get') else '0'
                    gender = gender_var.get() if gender_var and hasattr(gender_var, 'get') else ''
                    
                    year = int(year_str)
                    month = int(month_str)
                    day = int(day_str)
                    hour = int(hour_str)
                    minute = int(minute_str)
                    # 出生地经度（真太阳时 §48）：缺键/空/120 → 不启用
                    birth_longitude = _parse_owner_longitude(owner_info.get('longitude'))

                    name_var = owner_info.get('name')
                    name = name_var.get() if name_var and hasattr(name_var, 'get') else str(name_var) if name_var else ''
                    role = str(owner_info.get('role', ''))

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
                        'birth_longitude': birth_longitude,
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

            # 安葬无墓穴坐山不予年份分析（_azss0914）
            if not self._require_shan_for_burial(event_type):
                return
            
            # 创建评分器
            scorer = Scorer()
            
            # 分析年份
            results = []
            for year in range(start_year, end_year + 1):
                try:
                    analysis = scorer.analyze_year(year, event_type, owners, shan_xiang_value, jian_xiang_value, zeli_mode=self._get_zeli_mode())  # _zm0915
                    results.append(analysis)
                except Exception as e:
                    import traceback
                    print(f"分析年份{year}时出错: {e}")
                    traceback.print_exc()
                    # 创建一个错误结果而不是中断整个流程
                    results.append({
                        'year': year,
                        'year_gz': '',
                        'level': '错误',
                        'score': 0,
                        'suitable': False,
                        'reasons': [f'分析出错: {str(e)}']
                    })
            
            # 显示年份分析结果
            self.show_year_analysis(results)
            
        except Exception as e:
            import traceback
            error_msg = f"分析年份时出错: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            # 显示更详细的错误信息
            detailed_msg = f"{error_msg}\n\n详细错误信息:\n{traceback.format_exc()}"
            messagebox.showerror("错误", detailed_msg)
    
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
            suitable = "是" if result.get('suitable', True) else "否"
            reasons = "; ".join(result.get('reasons', [])) if result.get('reasons') else "无"
            
            tree.insert("", tk.END, values=(
                result.get('year', ''),
                result.get('year_gz', ''),
                result.get('level', '未知'),
                result.get('score', 0),
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
            # 确保 date 在局部作用域中可用
            from datetime import date, timedelta
            # 获取事项类型
            event_type = self.event_var.get()
            
            # 获取事主信息
            owners = []
            for owner_info in self.owners_info:
                try:
                    # 使用更安全的方式获取字段值
                    year_var = owner_info.get('year')
                    month_var = owner_info.get('month')
                    day_var = owner_info.get('day')
                    year_str = year_var.get() if year_var and hasattr(year_var, 'get') else ''
                    month_str = month_var.get() if month_var and hasattr(month_var, 'get') else ''
                    day_str = day_var.get() if day_var and hasattr(day_var, 'get') else ''
                    
                    # 检查是否填写了日期（年、月、日都必须填写）
                    if not (year_str and month_str and day_str):
                        continue
                    
                    hour_var = owner_info.get('hour')
                    minute_var = owner_info.get('minute')
                    gender_var = owner_info.get('gender')
                    hour_str = hour_var.get() if hour_var and hasattr(hour_var, 'get') else '12'
                    minute_str = minute_var.get() if minute_var and hasattr(minute_var, 'get') else '0'
                    gender = gender_var.get() if gender_var and hasattr(gender_var, 'get') else ''
                    
                    year = int(year_str)
                    month = int(month_str)
                    day = int(day_str)
                    hour = int(hour_str)
                    minute = int(minute_str)
                    # 出生地经度（真太阳时 §48）：缺键/空/120 → 不启用
                    birth_longitude = _parse_owner_longitude(owner_info.get('longitude'))

                    name_var = owner_info.get('name')
                    name = name_var.get() if name_var and hasattr(name_var, 'get') else str(name_var) if name_var else ''
                    role = str(owner_info.get('role', ''))

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
                        'birth_longitude': birth_longitude,
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
            
            # 获取兼向信息并合并到山向中
            jian_xiang = getattr(self, 'jian_xiang', None)
            jian_xiang_value = jian_xiang.get() if jian_xiang else None
            if shan_xiang_value and jian_xiang_value:
                # §59.13 批次一提醒3：提交前校验——非法兼向弹窗提示，不阻断
                # （引擎按正向处理并记日志）
                self._warn_invalid_jianxiang_before_submit(jian_xiang_value)
                # §59.13：手动裸值"亥"规范化为"兼亥"，保证拼接串可被引擎解析
                _jx_v = jian_xiang_value.strip()
                if _jx_v and _jx_v != '正中' and not _jx_v.startswith('兼'):
                    _jx_v = '兼' + _jx_v
                shan_xiang_value = shan_xiang_value + _jx_v

            # 安葬无墓穴坐山不予月份分析（_azss0914）
            if not self._require_shan_for_burial(event_type):
                return
            
            # 创建评分器
            scorer = Scorer()
            
            # 分析农历年的月份（从立春开始）
            results = []
            
            # 获取该年立春日期（使用sxtwl库）
            import sxtwl
            jq_list = sxtwl.getJieQiByYear(year)
            lichun_jd = jq_list[0].jd  # 立春是第一个节气（索引0）
            lichun_dd = sxtwl.JD2DD(lichun_jd)
            lichun = date(int(lichun_dd.Y), int(lichun_dd.M), int(lichun_dd.D))
            
            # 如果当前日期在立春之前，使用上一年的立春
            if date.today() < lichun:
                jq_list_prev = sxtwl.getJieQiByYear(year - 1)
                lichun_jd = jq_list_prev[0].jd
                lichun_dd = sxtwl.JD2DD(lichun_jd)
                lichun = date(int(lichun_dd.Y), int(lichun_dd.M), int(lichun_dd.D))
            
            # 分析从立春开始的 12 个月份
            from datetime import timedelta
            for i in range(12):
                # 计算每个农历月份的代表性日期（每月中旬）
                # 每个农历月大约 29.5 天，取每月 15 日左右
                days_offset = i * 30 + 15
                month_date = lichun + timedelta(days=days_offset)
                
                # 直接传入完整的日期对象，而不是 year 和 month
                try:
                    analysis = scorer.analyze_month(month_date, event_type, owners, shan_xiang_value, zeli_mode=self._get_zeli_mode())  # _zm0915
                    # 更新月份显示为农历月份（正月到十二月）
                    analysis['month'] = i + 1
                    results.append(analysis)
                except Exception as e:
                    import traceback
                    print(f"分析月份{i+1}时出错: {e}")
                    traceback.print_exc()
                    # 创建一个错误结果而不是中断整个流程
                    results.append({
                        'month': i + 1,
                        'month_gz': '',
                        'level': '错误',
                        'score': 0,
                        'suitable': False,
                        'reasons': [f'分析出错: {str(e)}']
                    })
            
            # 显示月份分析结果
            self.show_month_analysis(results, year)
            
        except Exception as e:
            import traceback
            error_msg = f"计算出错: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            # 显示更详细的错误信息
            detailed_msg = f"{error_msg}\n\n详细错误信息:\n{traceback.format_exc()}"
            messagebox.showerror("错误", detailed_msg)
    
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
            suitable = "是" if result.get('suitable', True) else "否"
            reasons = "; ".join(result.get('reasons', [])) if result.get('reasons') else "无"
            
            tree.insert("", tk.END, values=(
                result.get('month', ''),
                result.get('month_gz', ''),
                result.get('level', '未知'),
                result.get('score', 0),
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
                lunar_month = int(item['values'][0])  # 农历月份（1-12）
                
                # 计算该农历月份对应的公历日期范围
                # 使用节气来精确划分农历月份
                SOLAR_TERMS = ['立春', '惊蛰', '清明', '立夏', '芒种', '小暑', 
                              '立秋', '白露', '寒露', '立冬', '大雪', '小寒']
                
                try:
                    from modules.节气计算器 import get_solar_term_date
                    
                    # 获取该农历月开始的节气
                    if lunar_month == 1:
                        term_start = get_solar_term_date(year, '立春')
                    else:
                        term_start = get_solar_term_date(year, SOLAR_TERMS[lunar_month - 1])
                    
                    # 获取下一个月的节气作为结束
                    if lunar_month == 12:
                        term_end = get_solar_term_date(year + 1, '立春')
                    else:
                        term_end = get_solar_term_date(year, SOLAR_TERMS[lunar_month])
                    
                    # 设置日期范围（包含开始节气，不包含结束节气）
                    self.start_date.set(term_start.strftime("%Y-%m-%d"))
                    self.end_date.set((term_end - timedelta(days=1)).strftime("%Y-%m-%d"))
                    
                except Exception as e:
                    # 如果节气计算失败，使用原来的近似方法
                    print(f"节气计算失败: {e}")
                    lichun = date(year, 2, 4)
                    month_start = lichun + timedelta(days=(lunar_month - 1) * 30)
                    month_end = lichun + timedelta(days=lunar_month * 30 - 1)
                    self.start_date.set(month_start.strftime("%Y-%m-%d"))
                    self.end_date.set(month_end.strftime("%Y-%m-%d"))
                
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

    def _maybe_save_owners_on_finish(self, finish_msg):
        """择日完成后询问是否保存事主和事项信息（完成弹窗统一调用）

        事项类型由 save_owners_info 内部按 event_var 作为方案 key 前缀保存，
        因此「是」即同时保存事主资料与事项类型。
        方案名称为空时弹窗补问，用户取消则跳过保存。
        """
        if not messagebox.askyesno("完成", f"{finish_msg}\n\n是否保存当前的事主和事项信息？"):
            return

        plan_name = self.plan_name_var.get().strip() if hasattr(self, 'plan_name_var') else ''
        if not plan_name:
            from tkinter import simpledialog
            event_type = self.event_var.get() if hasattr(self, 'event_var') else '择日'
            plan_name = simpledialog.askstring(
                "保存事主方案",
                f"请输入方案名称（{event_type}类）：",
                initialvalue=f"{event_type}{datetime.now().strftime('%Y%m%d')}",
                parent=self.root)
            if not plan_name or not plan_name.strip():
                return  # 用户取消输入，跳过保存
            self.plan_name_var.set(plan_name.strip())

        self.save_owners_info()

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
            # 真太阳时立项 §48：持久化经度（字符串原样保存，与其他字段一致；缺键默认 '120'）
            _lng_raw = owner_info.get('longitude')
            longitude = _lng_raw.get() if hasattr(_lng_raw, 'get') else (_lng_raw or '120')
            # 001 §51：城市名仅显示/回填用（数值口径仍以经度为准），缺键默认 ''
            _city_raw = owner_info.get('birth_city')
            birth_city = _city_raw.get() if hasattr(_city_raw, 'get') else (_city_raw or '')
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
                'longitude': longitude,
                'birth_city': birth_city,
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
        # 2026-09-11: persist 24-mountain direction with the plan
        special_data = {}
        for _fk in ('house_type', 'shan_xiang', 'jian_xiang',
                    'zao_xiang', 'zao_wei', 'chuang_wei', 'zaozhu_mode'):
            _fv = getattr(self, _fk, None)
            if hasattr(_fv, 'get'):
                special_data[_fk] = _fv.get()
        all_plans[plan_key] = {
            'event_type': event_type,
            'plan_name': plan_name,
            'owners': save_data,
            'special': special_data
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
        
        # 2026-09-11: mountain-direction suffix for plan list entries
        def _sx_suffix(pd):
            _sp = pd.get('special') or {}
            if not isinstance(_sp, dict):
                return ''
            _sx = str(_sp.get('shan_xiang') or '').strip()
            _jx = str(_sp.get('jian_xiang') or '').strip()
            if _sx:
                return '｜' + _sx + (_jx if (_jx and _jx != '正中') else '')
            if str(_sp.get('zao_xiang') or '').strip():
                return '｜灶向' + str(_sp.get('zao_xiang')).strip()
            if str(_sp.get('chuang_wei') or '').strip():
                return '｜床向' + str(_sp.get('chuang_wei')).strip()
            return ''

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
                plan_listbox.insert(tk.END, f"  {plan_data['plan_name']}（{owners_count}个事主{_sx_suffix(plan_data)}）")
        
        if other_plans:
            plan_listbox.insert(tk.END, f"--- 其他事项方案 ---")
            for key, plan_data in other_plans:
                owners_count = len(plan_data.get('owners', []))
                plan_listbox.insert(tk.END, f"  [{plan_data.get('event_type', '')}] {plan_data['plan_name']}（{owners_count}个事主{_sx_suffix(plan_data)}）")
        
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
            # 2026-09-11: rebuild direction controls before restoring them
            self.update_special_options()
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
                # 真太阳时立项 §48：恢复经度；旧方案无此键 → 默认 '120'（不启用，向后兼容）
                if 'longitude' in owner_info:
                    owner_info['longitude'].set(owner_data.get('longitude', '120'))
                # 001 §51：恢复城市（旧方案无此键 → ''），不改经度数值
                if 'birth_city' in owner_info:
                    owner_info['birth_city'].set(owner_data.get('birth_city', ''))
                owner_info['gender'].set(owner_data.get('gender', '男'))
                owner_info['sizhu_var'].set(owner_data.get('sizhu', '未计算'))
                owner_info['xishen_var'].set(owner_data.get('xishen', ''))
                owner_info['yongshen_var'].set(owner_data.get('yongshen', ''))
                owner_info['fuzi_var'].set(owner_data.get('fuzi', ''))
        
        # 2026-09-11: restore 24-mountain direction / stove / bed params
        _sp = plan_data.get('special') or {}
        _sxr = ''
        if isinstance(_sp, dict):
            _ht = str(_sp.get('house_type') or '').strip()
            if _ht and hasattr(self, 'house_type'):
                self.house_type.set(_ht)
            _sx = str(_sp.get('shan_xiang') or '').strip()
            if _sx and hasattr(self, 'shan_xiang'):
                # set mountain first: its trace rebuilds jian options
                self.shan_xiang.set(_sx)
            _jx = str(_sp.get('jian_xiang') or '').strip()
            if _jx and hasattr(self, 'jian_xiang_combo'):
                try:
                    _jopts = list(self.jian_xiang_combo.cget('values') or [])
                except Exception:
                    _jopts = []
                if (not _jopts) or (_jx in _jopts):
                    self.jian_xiang.set(_jx)
            for _fk in ('zao_xiang', 'zao_wei', 'chuang_wei', 'zaozhu_mode'):
                _v = str(_sp.get(_fk) or '').strip()
                if _v and hasattr(self, _fk):
                    getattr(self, _fk).set(_v)
            if _sx:
                _sxr = _sx + (_jx if (_jx and _jx != '正中') else '')
            elif str(_sp.get('zao_xiang') or '').strip():
                _sxr = '灶向' + str(_sp.get('zao_xiang')).strip()
            elif str(_sp.get('chuang_wei') or '').strip():
                _sxr = '床向' + str(_sp.get('chuang_wei')).strip()
        _toast_dir = ('（' + _sxr + '）') if _sxr else ''
        messagebox.showinfo("加载成功",
                            f"方案「{plan_data.get('plan_name', '')}」已加载{_toast_dir}")
        # 2026-09-23 晚子时派兼容提示（ea447a4 起 23:00-23:59 时柱按子时、日柱仍取当日）：
        # 加载含 23 时出生事主的历史方案时弹一次/会话；只提示、不改写记录，
        # 由用户决定是否重新点「计算四柱」按新口径重排。
        if not getattr(self, '_night_zishi_hint_shown', False):
            def _is_hour_23(v):
                try:
                    return int(float(str(v).strip())) == 23
                except (TypeError, ValueError, OverflowError):
                    return False
            if any(isinstance(o, dict) and _is_hour_23(o.get('hour', ''))
                   for o in load_data):
                self._night_zishi_hint_shown = True
                messagebox.showinfo(
                    "晚子时派口径说明",
                    "本软件已升级为「晚子时派」：23:00-23:59 出生者时柱按子时计、"
                    "日柱仍按当日。\n"
                    "本方案含出生于 23 时的事主，若其四柱为旧口径（亥时/次日早子时）"
                    "所排，\n请重新点击「计算四柱」更新。历史记录不会被自动修改。")

    def calculate_owner_sizhu(self, year_var, month_var, day_var, hour_var, minute_var,
                              gender_var, owner, sizhu_var, xishen_var, yongshen_var, fuzi_var,
                              yintai_var=None, yangqi_var=None, calendar_type_var=None, zodiac_var=None,
                              fu_xing_var=None, zi_xing_var=None,
                              longitude_var=None, true_solar_flag_var=None):
        """计算事主四柱（longitude_var：出生地经度，真太阳时立项 §48；
        120/空 = 北京时间基准不启用，非 120 按拍板①②经度+EoT 修正）"""
        try:
            # 获取输入值，添加防御性检查
            year_str = year_var.get() if hasattr(year_var, 'get') else str(year_var)
            month_str = month_var.get() if hasattr(month_var, 'get') else str(month_var)
            day_str = day_var.get() if hasattr(day_var, 'get') else str(day_var)
            hour_str = hour_var.get() if hasattr(hour_var, 'get') else str(hour_var)
            minute_str = minute_var.get() if hasattr(minute_var, 'get') else str(minute_var)
            gender = gender_var.get() if hasattr(gender_var, 'get') else str(gender_var)

            # 验证输入值
            if not year_str or not month_str or not day_str:
                messagebox.showwarning("提示", "请填写完整的年月日信息")
                return

            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            hour = int(hour_str) if hour_str else 12
            minute = int(minute_str) if minute_str else 0
            # 出生地经度（字符串→float 明确处理，非法/越界弹窗回退 120）
            longitude = _parse_owner_longitude(longitude_var)
            
            # 判断是公历还是农历
            calendar_type = 'solar'
            if calendar_type_var and hasattr(calendar_type_var, 'get'):
                calendar_type = calendar_type_var.get()
            
            if calendar_type == 'lunar':
                # 农历转公历
                try:
                    from modules.高精度农历转换 import get_lunar_converter
                    converter = get_lunar_converter()
                    solar_date = converter.lunar_to_solar(year, month, day, hour, minute, 0)
                    year = solar_date['year']
                    month = solar_date['month']
                    day = solar_date['day']
                except Exception as e:
                    messagebox.showwarning("提示", f"农历转换失败: {e}")
                    return
            
            # 使用八字排盘模块获取详细信息（经度透传：120=北京时间不修正）
            panpan = BaZiPanPan(year, month, day, hour, minute, gender, longitude=longitude)
            panpan_result = panpan.get_panpan_result()

            # 检查四柱是否有效
            sizhu_info = panpan_result.get('四柱', {})
            if not sizhu_info or not sizhu_info.get('年柱'):
                messagebox.showwarning("提示", "四柱计算失败，请检查输入日期是否正确")
                return

            # 显示四柱（经度≠120 启用真太阳时时在独立标签标注口径，
            # 不改 sizhu_var 文本本体——下游 _parse_owner 按 split()==4 解析）
            sizhu_text = f"{sizhu_info['年柱']} {sizhu_info['月柱']} {sizhu_info['日柱']} {sizhu_info['时柱']}"
            sizhu_var.set(sizhu_text)
            if true_solar_flag_var is not None and hasattr(true_solar_flag_var, 'set'):
                true_solar_flag_var.set("(真太阳时)" if longitude != 120.0 else "")
            
            # 显示生肖
            if zodiac_var and hasattr(zodiac_var, 'set'):
                year_zhi = sizhu_info['年柱'][1] if len(sizhu_info['年柱']) > 1 else ''
                zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                             '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
                zodiac = zodiac_map.get(year_zhi, '')
                zodiac_var.set(zodiac)
            
            # 显示喜用神
            sizhu_info_detailed = {
                'year_gan': sizhu_info['年柱'][0] if sizhu_info['年柱'] else '',
                'year_zhi': sizhu_info['年柱'][1] if len(sizhu_info['年柱']) > 1 else '',
                'month_gan': sizhu_info['月柱'][0] if sizhu_info['月柱'] else '',
                'month_zhi': sizhu_info['月柱'][1] if len(sizhu_info['月柱']) > 1 else '',
                'day_gan': sizhu_info['日柱'][0] if sizhu_info['日柱'] else '',
                'day_zhi': sizhu_info['日柱'][1] if len(sizhu_info['日柱']) > 1 else '',
                'hour_gan': sizhu_info['时柱'][0] if sizhu_info['时柱'] else '',
                'hour_zhi': sizhu_info['时柱'][1] if len(sizhu_info['时柱']) > 1 else ''
            }
            xishen, yongshen = calculate_xishen_yongshen(sizhu_info_detailed)
            xishen_var.set(xishen)
            yongshen_var.set(yongshen)
            
            # 夫星子星（婚嫁专用）
            if self.event_var.get() == "嫁娶" and owner == "新娘":
                # 从八字分析中获取夫星子星信息
                from modules.工具函数 import get_fuzi, get_yintai, get_yangqi
                # 修正：从sizhu_info_detailed中获取天干地支，而不是sizhu_info
                year_gan = sizhu_info_detailed['year_gan']
                year_zhi = sizhu_info_detailed['year_zhi']
                month_gan = sizhu_info_detailed.get('month_gan', '甲')
                month_zhi = sizhu_info_detailed.get('month_zhi', '子')
                if year_gan and year_zhi:
                    # 计算夫星子星（基于年干年支）
                    fuzi_info = get_fuzi(year_gan, year_zhi)
                    fu = fuzi_info.get('fu', '未知')
                    zi = fuzi_info.get('zi', '未知')
                    if fu_xing_var and hasattr(fu_xing_var, 'set'):
                        fu_xing_var.set(fu)
                    if zi_xing_var and hasattr(zi_xing_var, 'set'):
                        zi_xing_var.set(zi)
                    
                    # 计算阴胎（以新娘月柱为基准 = 胎元）
                    yintai = get_yintai(month_gan, month_zhi)
                    
                    # 计算阳气（以新郎月柱为基准 = 胎元法：月干+1、月支+3，与阴胎同法；
                    # 男命（新郎）生月月柱所得称阳气，女命（新娘）称阴胎。典籍《选择求真·卷五》
                    # 【修正前的两套标准问题】：
                    #   ① 计算时序：之前依赖新郎已点击"计算八字"设置 groom_sizhu_var.get()，若新娘先点按钮就返回未知
                    #   ② 显示层与详情判定不一致：显示层用 role=='新郎'，详情层用 gender=='男'
                    # 修正策略：直接读取新郎的年月日输入 → 当场调用 BaZiPanPan 算月柱 → 再调用 get_yangqi
                    #          不再依赖新郎的sizhu_var是否被填充；同时统一采用 role=='新郎' 判定（与 self.owners_info 构造一致）
                    yangqi = '未知'
                    for owner_info in self.owners_info:
                        if owner_info.get('role') == '新郎':
                            # 直接读新郎输入变量（year_var/month_var/day_var/hour_var/minute_var/gender_var）
                            gy = owner_info.get('year')
                            gm = owner_info.get('month')
                            gd = owner_info.get('day')
                            gh = owner_info.get('hour')
                            gmi = owner_info.get('minute')
                            gg = owner_info.get('gender')
                            def _varval(x):
                                return x.get() if x and hasattr(x,'get') else (str(x) if x else '')
                            gys, gms, gds, ghs, gmis, ggs = _varval(gy), _varval(gm), _varval(gd), _varval(gh), _varval(gmi), _varval(gg)
                            if gys and gms and gds:
                                try:
                                    gyear, gmonth, gday = int(gys), int(gms), int(gds)
                                    ghour = int(ghs) if ghs else 12
                                    gminute = int(gmis) if gmis else 0
                                    ggender = ggs if ggs else '男'
                                    # 优先用与新娘相同的农历转换逻辑（calendar_type_var来自外层owner_info）
                                    g_ct_var = owner_info.get('calendar_type_var')
                                    cal_type = 'solar'
                                    if g_ct_var and hasattr(g_ct_var, 'get'):
                                        cal_type = g_ct_var.get()
                                    if cal_type == 'lunar':
                                        try:
                                            from modules.高精度农历转换 import get_lunar_converter
                                            conv = get_lunar_converter()
                                            sd = conv.lunar_to_solar(gyear, gmonth, gday, ghour, gminute, 0)
                                            gyear, gmonth, gday = sd['year'], sd['month'], sd['day']
                                        except Exception:
                                            pass
                                    pan_g = BaZiPanPan(gyear, gmonth, gday, ghour, gminute, ggender,
                                                       longitude=_parse_owner_longitude(owner_info.get('longitude'), show_warning=False))
                                    pan_g_r = pan_g.get_panpan_result()
                                    g_sizhu = pan_g_r.get('四柱', {})
                                    if g_sizhu and g_sizhu.get('月柱'):
                                        gy_g = g_sizhu['月柱'][0]
                                        gy_z = g_sizhu['月柱'][1] if len(g_sizhu['月柱']) > 1 else ''
                                        if gy_g and gy_z:
                                            yangqi = get_yangqi(gy_g, gy_z)
                                except (ValueError, TypeError):
                                    pass
                            break
                    
                    # 显示阴胎（新娘本卡）；阳气联动填入新郎卡片（self.yangqi_var 指向新郎卡片控件）
                    if yintai_var and hasattr(yintai_var, 'set'):
                        yintai_var.set(f"阴胎: {yintai if yintai else '未知'}")
                    _yq_self = getattr(self, 'yangqi_var', None)
                    if _yq_self and hasattr(_yq_self, 'set'):
                        _yq_self.set(f"阳气: {yangqi if yangqi else '未知'}")  # 阳气归位新郎卡片（2026-09-14）
                else:
                    if fu_xing_var and hasattr(fu_xing_var, 'set'):
                        fu_xing_var.set("未知")
                    if zi_xing_var and hasattr(zi_xing_var, 'set'):
                        zi_xing_var.set("未知")
                    if yintai_var and hasattr(yintai_var, 'set'):
                        yintai_var.set("阴胎: 未知")
                    # 阳气属新郎卡片，新娘信息缺失不清空新郎行（可能新郎已算好）
            
            elif self.event_var.get() == "嫁娶" and owner == "新郎":
                # 阳气归位新郎卡片（2026-09-14）：新郎点"计算四柱"时用本盘月柱
                # （胎元法：月干+1、月支+3，男称阳气）直接填本人卡片阳气行
                try:
                    from modules.工具函数 import get_yangqi as _get_yq
                    _mg = sizhu_info_detailed.get('month_gan', '')
                    _mz = sizhu_info_detailed.get('month_zhi', '')
                    _yq_val = _get_yq(_mg, _mz) if (_mg and _mz) else '未知'
                    if yangqi_var and hasattr(yangqi_var, 'set'):
                        yangqi_var.set(f"阳气: {_yq_val}")
                except Exception:
                    pass

            # 保存详细的事主信息到owners_data中
            # 这里可以将panpan_result保存到全局变量中，供后续使用
            # 例如：self.owners_data = panpan_result

            # ── 检查新娘新郎出生信息是否完全相同 ──
            try:
                _inputs = []
                for _oi in self.owners_info:
                    _role = _oi.get('role', '')
                    if hasattr(_role, 'get'):
                        _role = _role.get()
                    if _role in ('新娘', '新郎'):
                        def _vv(x):
                            return x.get() if x and hasattr(x, 'get') else (str(x) if x else '')
                        _key = (_vv(_oi.get('year')), _vv(_oi.get('month')),
                                _vv(_oi.get('day')), _vv(_oi.get('hour')), _vv(_oi.get('minute')))
                        _inputs.append((_role, _key))
                if len(_inputs) >= 2:
                    _roles = [r for r, _ in _inputs]
                    _keys = [k for _, k in _inputs]
                    if '新娘' in _roles and '新郎' in _roles and len(set(_keys)) == 1:
                        messagebox.showwarning("事主信息提醒",
                            "新娘与新郎的出生信息（年月日时）完全相同，\n"
                            "请确认是否输入有误。\n"
                            "（若为双胞胎则属正常，可忽略此提示）")
            except Exception:
                pass
        except ValueError as e:
            messagebox.showwarning("警告", f"请输入有效的日期时间: {e}")
        except Exception as e:
            messagebox.showwarning("警告", f"日期转换失败: {e}")
    
    def show_owner_bazi_detail(self, year_var, month_var, day_var, hour_var, minute_var, gender_var, owner, longitude_var=None):
        """显示事主八字排盘详情"""
        try:
            year = int(year_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            gender = gender_var.get()
            longitude = _parse_owner_longitude(longitude_var)

            # 使用八字排盘模块获取详细信息
            panpan = BaZiPanPan(year, month, day, hour, minute, gender, longitude=longitude)
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
    
    def _jianxiang_invalid_reason(self, value):
        """§59.13 批次一细节4：兼向输入校验（复用引擎单点解析，UI不另建白名单）。
        返回 None=合法；否则返回提示文案。"""
        v = (value or '').strip()
        if not v or v == '正中':
            return None
        try:
            from modules.二十四山 import parse_shan_xiang_jianxiang
        except ImportError:
            from 二十四山 import parse_shan_xiang_jianxiang
        p = parse_shan_xiang_jianxiang('甲山', v)
        if p['兼向原始'] and p['兼向'] is None:
            return (f"兼向\"{p['兼向原始']}\"未识别为二十四山山字，"
                    "将按正向处理（可从下拉选择，或输入合法山字如\"兼卯\"）")
        return None

    def _update_jx_hint(self, *_args):
        """§59.13 批次一细节4：失焦/回车时更新兼向行内提示（不拦输入不改值）。"""
        combo = getattr(self, 'jian_xiang_combo', None)
        label = getattr(self, '_jx_hint_label', None)
        if combo is None or label is None:
            return
        msg = self._jianxiang_invalid_reason(combo.get())
        if msg:
            label.config(text='⚠ ' + msg, foreground='#c62828')
        else:
            label.config(text='', foreground='#000000')

    def _warn_invalid_jianxiang_before_submit(self, jian_xiang_value):
        """§59.13 批次一细节4（提醒3）：提交前校验——生成报告/扫描前兜底提示，
        保证用户提交前一定看到提示；不阻断流程（引擎按正向处理并记日志）。"""
        msg = self._jianxiang_invalid_reason(jian_xiang_value)
        if msg:
            messagebox.showwarning('兼向提示', msg)
        return msg

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
    
    def _get_base_shan_xiang(self):
        """获取基础山向名称（不含兼向）"""
        shan_xiang = getattr(self, 'shan_xiang', None)
        if not shan_xiang:
            return None
        value = shan_xiang.get()
        if not value:
            return None
        if '兼' in value:
            return value.split('兼')[0].strip()
        return value
    
    def _validate_shan_xiang(self, shan_xiang):
        """验证山向是否有效"""
        if not shan_xiang:
            return False
        valid = get_shan_xiang_list(use_24_shan=True)
        base = shan_xiang.split('兼')[0].strip()
        return base in valid
    
    def _extract_shan_zhi(self, mountain_name):
        """从山向提取坐山地支"""
        if not mountain_name:
            return ''
        if '兼' in mountain_name:
            base = mountain_name.split('兼')[0].strip()
        else:
            base = mountain_name
        data = get_mountain_data(base)
        if data and 'basic_info' in data:
            return data['basic_info'].get('地支', '')
        return ''
    
    def _get_zeli_mode(self):
        """_zm0915：'pure' 纯正五行（协纪辨方书，默认）/ 'feixing' 正五行+玄空飞星"""
        _v = getattr(self, 'zeli_mode_var', None)
        _m = _v.get() if hasattr(_v, 'get') else 'pure'
        return _m if _m in ('pure', 'feixing') else 'pure'

    def _on_zeli_mode_change(self, event=None):
        """_zm0915：模式切换即时刷新玄空列与飞星按钮显隐"""
        try:
            self._update_result_columns()
            _btn = getattr(self, 'xuankong_btn', None)
            if _btn is None:
                return
            if self._get_zeli_mode() == 'feixing':
                if not _btn.winfo_ismapped():
                    _nb = getattr(self, 'date_test_btn', None)
                    if _nb is not None:
                        _btn.pack(side=tk.LEFT, padx=6, before=_nb)
                    else:
                        _btn.pack(side=tk.LEFT, padx=6)
            elif _btn.winfo_ismapped():
                _btn.pack_forget()
        except Exception:
            pass

    def on_event_change(self, event=None):
        """事项类型改变时的处理"""
        self.update_special_options()
        self.update_owners_frame()
        self._update_result_columns()

    def _update_result_columns(self):
        """动态控制结果表列显示（2026-09-01 用户要求）：
        1. 事主信息栏：所有择日事项一律不显示；
        2. 利月栏：仅嫁娶类事项（嫁娶/订婚/纳采）显示，其他事项隐藏。
        3. 玄空栏（2026-09-02）：仅修造安葬类事项（FEIXING_EVENTS）显示，置于表格最后。
        列仍在 columns 定义中（保证 insert values 索引对齐），仅通过 displaycolumns 控制可见性。
        """
        if not hasattr(self, 'result_tree'):
            return
        try:
            cols = ["日期/四柱", "评分", "等级", "五行得分", "月令得分",
                    "喜用神得分", "黄道得分", "地支关系", "吉神信息"]
            if self.event_var.get() in MARRIAGE_EVENTS:
                cols.append("利月")
            if self.event_var.get() in FEIXING_EVENTS and self._get_zeli_mode() == 'feixing':  # _zm0915
                cols.append("玄空")
            self.result_tree["displaycolumns"] = cols
        except Exception:
            pass
    
    # ============================================================
    # 【最佳吉时注入】：把 result['sizhu'] / score_result['sizhu']
    #   的时柱，从午时(12:00)计算的默认值，替换为"事项专属最佳吉时"
    # 评分计算仍使用午时sizhu（评分口径不变），这里只改"显示用"四柱。
    # 调用点：两个扫日循环中，在 result = {...} 构建后、append前。
    # ============================================================
    @staticmethod
    def _calc_hour_zhi_relation_score(nian_zhu, yue_zhu, ri_zhu, shi_zhu):
        """
        推荐时柱地支关系计分（2026-09-01 用户确认：推荐时柱参与的地支关系应计分）
        时支分别与年/月/日支计算：六合+8、半合+6、六冲-15、六害-6、相刑-8、相破-4；
        相刑含无恩之刑（寅巳/巳申/申寅）、恃势之刑（丑戌/戌未/未丑）、无礼之刑（子卯），
        两支即成刑；自刑（辰午酉亥同支相见，如酉酉）-8；其余同支伏吟不计分。
        分值口径严格对齐评分器._calc_hour_zhi_relations_detail（单一数据源）。
        Returns:
            (total, details): 总分 与 明细文本列表
        """
        zixing_zhis = ('辰', '午', '酉', '亥')  # 四自刑
        def _z(p):
            return p[1:2] if isinstance(p, str) and len(p) >= 2 else ''
        h_z = _z(shi_zhu)
        if not h_z:
            return 0, []
        liuhe = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯',
                 '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
        sanhe_groups = [('申', '子', '辰'), ('寅', '午', '戌'), ('巳', '酉', '丑'), ('亥', '卯', '未')]
        liuchong = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                    '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        liuhai = {'子': '未', '未': '子', '丑': '午', '午': '丑', '寅': '巳', '巳': '寅',
                  '卯': '辰', '辰': '卯', '申': '亥', '亥': '申', '酉': '戌', '戌': '酉'}
        liupo = {'子': '酉', '酉': '子', '丑': '辰', '辰': '丑', '寅': '亥', '亥': '寅',
                 '卯': '午', '午': '卯', '巳': '申', '申': '巳', '未': '戌', '戌': '未'}
        _xing_pairs = {('子', '卯'), ('寅', '巳'), ('巳', '申'), ('申', '寅'),
                       ('丑', '戌'), ('戌', '未'), ('未', '丑')}
        others = [('年支', _z(nian_zhu)), ('月支', _z(yue_zhu)), ('日支', _z(ri_zhu))]
        total = 0
        details = []
        # 逐对关系（严格对齐评分器._calc_hour_zhi_relations_detail：合与冲/害/刑/破互相独立判定）
        for name, z in others:
            if not z:
                continue
            if z == h_z:
                # 同支：辰午酉亥相见为自刑（-8）；其余同支为伏吟，不计分
                if h_z in zixing_zhis:
                    total -= 8
                    details.append(f"自刑（时支{h_z}与{name}{z}同支，{h_z}{h_z}自刑）：-8分")
                continue
            # 合：六合优先，否则半合（生地半合/墓地半合/拱合）
            if liuhe.get(h_z) == z:
                total += 8
                details.append(f"六合：时支{h_z}合{name}{z}：+8分")
            elif any(h_z in g and z in g for g in sanhe_groups):
                total += 6
                _g = next(g for g in sanhe_groups if h_z in g and z in g)
                _ju = {'申子辰': '水', '寅午戌': '火', '巳酉丑': '金', '亥卯未': '木'}[''.join(_g)]
                _pos = sorted((_g.index(h_z), _g.index(z)))
                if _pos == [0, 1]:
                    details.append(f"生地半合{_ju}局（时支{h_z}+{name}{z}）：+6分")
                elif _pos == [1, 2]:
                    details.append(f"墓地半合{_ju}局（时支{h_z}+{name}{z}）：+6分")
                else:
                    details.append(f"拱合{_ju}局（时支{h_z}与{name}{z}）：+6分")
            # 冲/害/刑/破（互斥）
            if liuchong.get(h_z) == z:
                total -= 15
                details.append(f"六冲：时支{h_z}冲{name}{z}：-15分")
            elif liuhai.get(h_z) == z:
                total -= 6
                details.append(f"六害：时支{h_z}害{name}{z}：-6分")
            elif (h_z, z) in _xing_pairs or (z, h_z) in _xing_pairs:
                total -= 8
                if {h_z, z} == {'子', '卯'}:
                    _xn = '无礼之刑'
                elif {h_z, z} <= {'寅', '巳', '申'}:
                    _xn = '无恩之刑'
                else:
                    _xn = '恃势之刑'
                details.append(f"相刑（{_xn}）：时支{h_z}刑{name}{z}：-8分")
            elif liupo.get(h_z) == z:
                total -= 4
                details.append(f"相破：时支{h_z}破{name}{z}：-4分")
        return total, details

    def _inject_best_hour_to_result(self, result, score_result, event_type, owners_info,
                                    current_date, wushu_sizhu,
                                    house_type='', shan_xiang='', zao_xiang='',
                                    zao_wei='', chuang_wei=''):
        """
        根据事项类型选出当日最佳吉时，并把时柱写回到：
          (1) result['sizhu']  —— 头段 & 结果表第4列字符串
          (2) score_result['sizhu']['时柱'] —— 【四柱八字】段字典
        参数：
          - wushu_sizhu: 午时(12:00) calculate_sizhu 返回的字典（含年/月/日柱）
        无任何返回，失败则保持原样不动。
        """
        try:
            if not isinstance(result, dict) or not isinstance(wushu_sizhu, dict):
                return
            # ---- 解析基础四柱 ----
            def _gz(v):
                if isinstance(v, str) and len(v) >= 2:
                    return v[0], v[1]
                if isinstance(v, (list, tuple)) and len(v) >= 2:
                    return str(v[0]), str(v[1])
                return '', ''
            y_g, y_z = _gz(wushu_sizhu.get('年柱', ''))
            m_g, m_z = _gz(wushu_sizhu.get('月柱', ''))
            d_g, d_z = _gz(wushu_sizhu.get('日柱', ''))
            if not (d_g and d_z and y_g and y_z and m_g and m_z):
                return

            # 代表时辰时柱（扫描12时辰择优后的权威四柱）先于一切改写快照留存。
            # 评分器返回的 score_result['sizhu'] 与传入 calculate_score 的 sizhu（即本函数
            # wushu_sizhu）是【同一字典对象】；下方(2)步若原地改写会连带污染 wushu_sizhu，
            # 导致 (5.5) "代表时辰即评分最优"分支回读代表时柱时，读到已被覆盖的 checker 时柱
            # （如辛亥），形成"显示辛亥、评分明细却是午时"的两套时辰。故先快照、(2)步用副本。
            _rep_hour_gz = ''
            _rv0 = wushu_sizhu.get('时柱', '') if isinstance(wushu_sizhu, dict) else ''
            if isinstance(_rv0, str) and len(_rv0) >= 2:
                _rep_hour_gz = _rv0[0:2]

            # ---- 归一化 sizhu（与 get_lucky_hours 口径一致） ----
            norm_sizhu = {
                'year_gan': y_g, 'year_zhi': y_z,
                'month_gan': m_g, 'month_zhi': m_z,
                'day_gan': d_g, 'day_zhi': d_z,
            }

            # ---- 权威推荐时柱（单一数据源 modules.推荐时柱）----
            # 修造带坐山/主命、婚姻带新郎新娘、其它通用，全部由 resolve_recommended_hour
            # 统一构造 checker 并选时；扫日/详情/玄空开窗共用，禁止各处自行选时。
            from modules.推荐时柱 import resolve_recommended_hour
            _sv0 = getattr(self, 'shan_xiang', None)
            _shan_str0 = _sv0.get() if hasattr(_sv0, 'get') else (_sv0 or '')
            # 2026-09-17 隐患1 方案C：优先复用 _rescan_best_hour 缓存的 _rec
            #   （扫日循环内 _rescan 与 _inject 紧邻成对调用，命中即避免重复构造
            #   checker）。lucky_hours 不依赖输入 sizhu 时柱，故可安全复用。
            # 复用条件：缓存键（日期 / 事项 / 事主指纹 / 坐山）四者全等；
            #   跨天、切换事项、编辑事主或更改坐山一律缓存失效并重新解析，
            #   杜绝隐式依赖"成对紧邻调用"，也保证两次择优共用同一份 lucky_hours。
            _cached_rec = getattr(self, '_cached_rec', None)
            _cached_key = getattr(self, '_cached_rec_key', None)
            _expect_key = (current_date, event_type,
                           _owners_fingerprint(owners_info), _shan_str0)
            if _cached_rec is not None and _cached_key == _expect_key:
                _rec = _cached_rec
            else:
                _rec = resolve_recommended_hour(
                    wushu_sizhu, event_type,
                    owners_info if isinstance(owners_info, list) else [], _shan_str0)
            lucky_hours = _rec['lucky_hours'] if _rec else None

            if not isinstance(lucky_hours, list) or not lucky_hours:
                return

            # ---- 最佳吉时取权威函数结果；重建 good/avail 供 (5.5) 候选重算 ----
            best = _rec['best'] if _rec else None
            avail = [h for h in lucky_hours if isinstance(h, dict) and not h.get('禁用', False)]
            good = [h for h in avail if int(h.get('分值', 0) or 0) > 0]
            if not best:
                return

            h_g = str(_rec.get('best_gan', '') or '').strip()
            h_z = str(_rec.get('best_zhi', '') or '').strip()
            if not (h_g and h_z):
                return
            best_shizhu = h_g + h_z

            # ---- 写回三处显示数据源 ----
            nian_zhu = y_g + y_z
            yue_zhu = m_g + m_z
            ri_zhu = d_g + d_z
            new_sizhu_str = f"{nian_zhu} {yue_zhu} {ri_zhu} {best_shizhu}"
            result['sizhu'] = new_sizhu_str

            # (2) score_result['sizhu'] —— 【四柱八字】段逐柱
            #   铁律：score_result['sizhu'] 与 wushu_sizhu（扫描代表时辰字典）是同一对象，
            #   严禁原地改写，否则污染调用方四柱、(5.5) 回归代表时辰时读到 checker 时柱。
            #   必须复制出新字典再写回（副本同时保留 year/month/date 等键供详情取农历）。
            if isinstance(score_result, dict):
                old_sd = score_result.get('sizhu')
                _sd_new = dict(old_sd) if isinstance(old_sd, dict) else {}
                _sd_new['年柱'] = nian_zhu
                _sd_new['月柱'] = yue_zhu
                _sd_new['日柱'] = ri_zhu
                _sd_new['时柱'] = best_shizhu
                score_result['sizhu'] = _sd_new
                # (3) 给详情弹窗做来源标识：推荐时柱，不是午时示例
                score_result['_auth_sizhu'] = True
                # 把最佳时详情存入，方便后续追溯
                score_result['_best_hour'] = {
                    '时辰': best.get('时辰', ''),
                    '天干': h_g, '地支': h_z,
                    '分值': best.get('分值', 0),
                    '说明': best.get('说明', []),
                }
                # (5.5) 权威重算（2026-09-07 用户确认：推荐时柱以完整评分器为准，单一数据源）
                #   旧实现只把神煞吉时checker的时柱"贴"到午时评分上（仅补一个时柱关系分），
                #   飞星/三煞/综合评语仍是午时、时柱却显示推荐柱（如癸丑），自相矛盾。
                #   现对 checker 推荐候选时辰逐一用完整评分器 calculate_score 重算，连同
                #   当前代表时辰，取"否决最少→分数最高"者整表采用：正五行/飞星/三煞/月令/
                #   综合评语/总分全部来自同一时柱，彻底一致。
                # ============================================================
                try:
                    # full shan-xiang incl. jian for fenjin preview (same as block (6))
                    _sxf_full = shan_xiang or ''
                    _jxv = getattr(self, 'jian_xiang', None)
                    _jxs = _jxv.get() if hasattr(_jxv, 'get') else (_jxv or '')
                    if _sxf_full and _jxs and _jxs != '正中':
                        _sxf_full = f"{_sxf_full}{_jxs}"
                    _HH = {'子': 0, '丑': 2, '寅': 4, '卯': 6, '辰': 8, '巳': 10,
                           '午': 12, '未': 14, '申': 16, '酉': 18, '戌': 20, '亥': 22}
                    _cand_z = []
                    # 2026-09-11: candidates = all non-disabled hours
                    # (checker-positive first, then the rest), no [:6] slice.
                    # Otherwise a 0-checker but full-scorer-100 hour (e.g.
                    # geng-shen/ren-xu) can never replace the rep hour on a tie.
                    for _h in list(good) + [_x for _x in avail if _x not in good]:
                        _z = str(_h.get('地支', '') or '').strip()
                        if _z and _z not in _cand_z:
                            _cand_z.append(_z)
                    _owners = owners_info if isinstance(owners_info, list) else []

                    def _rescore_hour(_z):
                        # 2026-10-02 性能优化（方向D）：优先复用 _rescan_best_hour 已评分的时辰结果，
                        # 避免重复调用 calculate_sizhu + calculate_score。
                        _rescan_scores = wushu_sizhu.get('_rescan_hour_scores', {})
                        if isinstance(_rescan_scores, dict) and _z in _rescan_scores:
                            return _rescan_scores[_z]
                        _hh = _HH.get(_z)
                        if _hh is None:
                            return None, None
                        _hs = calculate_sizhu(current_date, _hh, 0)
                        try:
                            _hs['date'] = current_date
                            _hs['year'] = current_date.year
                            _hs['month'] = current_date.month
                            _hs['day'] = current_date.day
                        except Exception:
                            pass
                        _zmv = getattr(self, 'zaozhu_mode', None)
                        _rr = calculate_score(_hs, event_type, _owners, house_type,
                                              shan_xiang, zao_xiang, zao_wei, chuang_wei,
                                              zaozhu_mode=(_zmv.get() if hasattr(_zmv, 'get') else None),
                                              zeli_mode=self._get_zeli_mode())  # _zm0915
                        return _hs, _rr

                    def _shashi_hour(_rr):
                        # sha-shi hour is a craft-hour-only heavy evil (-30):
                        # not a veto, but never the preferred pick on a tie.
                        try:
                            for _s in (_rr.get('shensha_list') or []):
                                if isinstance(_s, dict) and '\u6740\u5e08' in str(_s.get('name', '')):
                                    return 1
                        except Exception:
                            pass
                        return 0

                    # _ck0915：时辰表分数查找表（地支→分值）
                    _ck_scores = {}
                    for _h in lucky_hours:
                        if isinstance(_h, dict):
                            _ck_scores[str(_h.get('地支', ''))] = int(_h.get('分值', 0) or 0)
                    # 代表时辰地支（午时基准）
                    _rep_zhi = ''
                    _rv = wushu_sizhu.get('时柱', '') if isinstance(wushu_sizhu, dict) else ''
                    if isinstance(_rv, str) and len(_rv) >= 2:
                        _rep_zhi = _rv[1]
                    # _ck0915：仅嫁娶事件将时辰表分数纳入排序优先级；
                    # 非嫁娶（作灶/修造等）仍以完整评分器总分为准。
                    # 2026-09-17 方案C收口：以注册表 MARRIAGE_EVENTS（嫁娶/订婚/纳采）
                    # 为唯一口径，与 _rescan_best_hour 完全一致；'结婚'/'领证' 非注册
                    # 事项不再按嫁娶加权，'纳采' 恢复嫁娶加权。
                    _ck_w = 1 if event_type in MARRIAGE_EVENTS else 0

                    def _skey(_rr, _z=''):
                        # order: fewer vetoes (incl. fenjin severe preview)
                        # > higher checker score (时辰表分数；# _ck0915 嫁娶专用)
                        # > higher post-(6) score (minus medium deduct preview)
                        # > no sha-shi hour > clean fenjin > higher raw wu-xing
                        _gs = _rr.get('sizhu') if isinstance(_rr.get('sizhu'), dict) else {}
                        _fl, _fd = _fenjin_preview_penalty(
                            _sxf_full, str(_gs.get('年柱', '')), str(_gs.get('月柱', '')),
                            str(_gs.get('日柱', '')), str(_gs.get('时柱', '')),
                            _rr.get('yi_list') or [], _rr.get('shensha_list') or [])
                        _zw = int((_rr.get('score_details') or {}).get('五行评分') or 0)
                        _ck = _ck_scores.get(_z, 0) * _ck_w
                        return (len(_rr.get('veto_reasons') or []) + (1 if _fl == 2 else 0),
                                -_ck,
                                -(int(_rr.get('score') or 0) - (_fd if _fl >= 1 else 0)),
                                _shashi_hour(_rr), _fl, -_zw)

                    _best_hs, _best_rr, _best_z = wushu_sizhu, score_result, _rep_zhi
                    for _z in _cand_z:
                        _hs, _rr = _rescore_hour(_z)
                        if _rr is None:
                            continue
                        if _skey(_rr, _z) < _skey(_best_rr, _best_z):
                            _best_hs, _best_rr, _best_z = _hs, _rr, _z

                    if _best_rr is not score_result:
                        _auth_gz = _best_hs.get('时柱', '') if isinstance(_best_hs, dict) else ''
                        score_result.clear()
                        score_result.update(_best_rr)
                        score_result['_auth_sizhu'] = True
                        score_result['_best_hour'] = {
                            '时辰': '',
                            '天干': _auth_gz[:1], '地支': _auth_gz[1:2],
                            '分值': int(_best_rr.get('score') or 0),
                            '说明': ['完整评分器权威重算：正五行/飞星/三煞/综合评语均按本时柱'],
                        }
                        if len(_auth_gz) >= 2:
                            best_shizhu = _auth_gz[0:2]
                        # 交节日防御：选中时辰可能与基准 wushu_sizhu 跨节气（如小暑当天
                        # 12:00 基准属乙未月，而选中的寅时 3-5 点尚未交节仍属甲午月）。
                        # 年/月/日柱必须跟随真实选中四柱 _best_hs，不能沿用函数开头从
                        # wushu_sizhu 缓存的年月柱，否则出现“显示乙未月、评分按甲午”的错配。
                        if isinstance(_best_hs, dict):
                            nian_zhu = str(_best_hs.get('年柱') or nian_zhu)
                            yue_zhu = str(_best_hs.get('月柱') or yue_zhu)
                            ri_zhu = str(_best_hs.get('日柱') or ri_zhu)
                        result['sizhu'] = f"{nian_zhu} {yue_zhu} {ri_zhu} {best_shizhu}"
                        result['score'] = score_result.get('score', 0)
                        result['level'] = score_result.get('level', '')
                    else:
                        # 代表时辰（午时基准或规则3所选）即评分最优：显示时柱回归代表
                        # 四柱，勿保留未被完整评分器采纳的神煞吉时柱，杜绝两套时辰。
                        # 注意：必须用函数开头快照的 _rep_hour_gz，不能回读 wushu_sizhu
                        # ——该字典与 score_result['sizhu'] 同对象，(2)步前曾被原地污染。
                        _rep_gz = _rep_hour_gz
                        if len(_rep_gz) >= 2:
                            best_shizhu = _rep_gz[0:2]
                            result['sizhu'] = f"{nian_zhu} {yue_zhu} {ri_zhu} {best_shizhu}"
                            if isinstance(score_result.get('sizhu'), dict):
                                score_result['sizhu']['时柱'] = best_shizhu
                            score_result['_auth_sizhu'] = True
                        result['score'] = score_result.get('score', 0)
                        result['level'] = score_result.get('level', '')
                except Exception as _e55:
                    print(f"[最佳吉时] 权威重算失败，保留原评分: {_e55}")

                # ============================================================
                # (4') 时柱地支关系展示（评分器单一数据源）
                #   步骤(5.5)权威重算时，评分器 _calc_hour_zhi_relations_detail 已按与
                #   _calculate_zhizhi_relations 完全相同的规则产出"时柱关系得分/明细"，
                #   且该分已计入五行评分·地支关系得分。此处直接读取展示、仅补"不重复累加"
                #   注记，不再用主程序自有规则(半合+5/六害-5)另算，避免展示分≠实际计入分。
                # ============================================================
                try:
                    sd_details = score_result.get('score_details')
                    _NOTE = '（已含于五行评分·地支关系得分中，不重复累加）'
                    if event_type in MARRIAGE_EVENTS:
                        # 婚嫁按"彻底分离"原则：日课评分不含时柱冲合刑害（时柱可换，
                        # 由【十二时辰婚嫁吉凶】独立评估，婚嫁评分算法以 hour_zhi='' 副本
                        # 排除时柱）。故评分详情不得出现"时柱地支关系得分"，否则与五行分析
                        # 后缀"冲合刑害不计入日课总分"自相矛盾（如酉酉自刑无扣分项却标已计分）。
                        if isinstance(sd_details, dict):
                            sd_details.pop('时柱关系得分', None)
                            sd_details.pop('时柱关系明细', None)
                    elif isinstance(sd_details, dict) and sd_details.get('时柱关系明细'):
                        _lines = [str(x) for x in sd_details['时柱关系明细']]
                        if not any('不重复累加' in x for x in _lines):
                            # 动态对账注记：全局地支关系=年月日三柱+时柱参与（如+4=+6+-2）
                            _all_zz = None
                            _bd4 = score_result.get('wu_xing_result')
                            if isinstance(_bd4, dict):
                                _all_zz = (_bd4.get('score_breakdown') or {}).get('地支关系得分')
                            _hr_zz = int(sd_details.get('时柱关系得分') or 0)
                            if isinstance(_all_zz, (int, float)):
                                _rest_zz = int(_all_zz) - _hr_zz
                                _note_now = ('（时柱参与%+d分＋年月日三柱关系%+d分＝地支关系得分%+d分，'
                                             '已含于上方五行评分，不重复累加）'
                                             % (_hr_zz, _rest_zz, int(_all_zz)))
                            else:
                                _note_now = _NOTE
                            sd_details['时柱关系明细'] = _lines + [_note_now]
                    else:
                        # 兜底：评分器未产出（异常/环境），方用主程序方法补算
                        rel_score, rel_details = self._calc_hour_zhi_relation_score(
                            nian_zhu, yue_zhu, ri_zhu, best_shizhu)
                        if isinstance(sd_details, dict):
                            sd_details['时柱关系得分'] = rel_score
                            sd_details['时柱关系明细'] = (list(rel_details) + [_NOTE]) if rel_details else []
                except Exception as _e4:
                    print(f"[最佳吉时] 时柱关系分展示失败: {_e4}")

                # ============================================================
                # (5') 用最终权威时柱重算五行详情 + 综合评语（单一数据源）
                #   确保五行分析/综合评语的地支关系与展示时柱一致，推荐时柱不加示例标注。
                # ============================================================
                try:
                    from modules.评分器 import Scorer as _DScorer
                    _wr3 = score_result.get('wu_xing_result')
                    if isinstance(_wr3, dict):
                        _auth_sz = {
                            '年柱': nian_zhu, '月柱': yue_zhu,
                            '日柱': ri_zhu, '时柱': best_shizhu,
                        }
                        _new_det = _DScorer()._generate_wu_xing_details(
                            _auth_sz,
                            owners_info if isinstance(owners_info, list) else [],
                            is_demo_hour=False)
                        if isinstance(_new_det, dict) and _new_det:
                            _wr3['details'] = _new_det
                    try:
                        _sd = score_result.get('score_details') or {}
                        _rds = _DScorer()
                        _rds.shensha_list = score_result.get('shensha_list') or []
                        _rds.yi_list = score_result.get('yi_list') or []
                        _rds.ji_list = score_result.get('ji_list') or []
                        _rds.huangdao_info = score_result.get('huangdao_info') or {}
                        if event_type in MARRIAGE_EVENTS:
                            # 嫁娶保持评分器专属评语结构（嫁娶要点/宜/忌独立行 ＋ "月令分析："
                            # 起的完整 tail）。不可用通用 _generate_reason 整体覆盖：评分器已把
                            # 完整 final_reason 回填到 wu_xing_result['ji_yu']，通用函数会先把整段
                            # 包进"五行："，再由其日主/合局/吉神/月令/喜用/黄道/宜逻辑重拼一遍，
                            # 造成 tail 大段重复（2026-09-17 补全 tail 后显现）。
                            # 此处仅按权威时柱重算 tail（地支关系/命局吉神随时柱刷新），前段保留。
                            _old_reason = str(score_result.get('reason') or '')
                            _head_parts = []
                            for _line in _old_reason.split('\n'):
                                if _line.startswith('月令分析：'):
                                    break
                                _head_parts.append(_line)
                            _sz_for_yl = score_result.get('sizhu')
                            if not isinstance(_sz_for_yl, dict):
                                _sz_for_yl = {}
                            _yl_new = _rds._generate_yueling_analysis(_sz_for_yl)
                            # 2026-10-02 修复：签名第5位是 shensha_list（原调用正确），
                            #   原调用缺失第6/7/8位：marriage_details（嫁娶分项）、
                            #   veto_reason（否决项）、ji_jiaqu_capped（按最终等级判定）
                            #   ——末者恒为默认 False，导致"平/犯忌慎用"日写出"嫁娶可用"。
                            _md_real = _sd.get('marriage_details')
                            if not isinstance(_md_real, list):
                                _md_real = _sd.get('嫁娶明细(分项)') or []
                            # 2026-11-22 用户审查修复（P1）：合局按含推荐时柱口径重算。
                            # 评分器刻意用 sizhu_no_hour 算合局（时辰不入围日课），但报告
                            # 展示含推荐时柱，导致"拱合局(亥,未，拱卯)"与地支关系段
                            # "三合木局(亥卯未)"并存矛盾。此处按权威时柱重算合局项，
                            # 同步 marriage_details / 五行评分 / 总分 / 等级 / 嫁娶要点行。
                            _capped_real = '犯忌嫁娶' in str(
                                score_result.get('level') or '')
                            _minor_real = '降一格' in str(
                                score_result.get('level') or '')
                            try:
                                from modules.婚嫁评分算法 import get_zhiju_score as _gzs
                                _full_sz = {
                                    'year_zhi': str(nian_zhu)[-1:],
                                    'month_zhi': str(yue_zhu)[-1:],
                                    'day_zhi': str(ri_zhu)[-1:],
                                    'hour_zhi': str(best_shizhu)[-1:],
                                }
                                _zj_new_s, _zj_new_r = _gzs(_full_sz)
                                _HEJU_KEYS = ('三合局', '半合局', '拱合局', '六合(')
                                _old_zj_idx, _old_zj_name, _old_zj_score = None, '', 0
                                for _i, _d in enumerate(_md_real):
                                    if (isinstance(_d, (list, tuple)) and len(_d) >= 2
                                            and isinstance(_d[1], (int, float)) and _d[1] > 0
                                            and any(k in str(_d[0]) for k in _HEJU_KEYS)):
                                        _old_zj_idx, _old_zj_name, _old_zj_score = _i, str(_d[0]), _d[1]
                                        break
                                if _zj_new_r and _zj_new_r != _old_zj_name:
                                    _delta = _zj_new_s - (_old_zj_score if _old_zj_idx is not None else 0)
                                    if _old_zj_idx is not None:
                                        _md_real[_old_zj_idx] = (_zj_new_r, _zj_new_s)
                                    else:
                                        _md_real.append((_zj_new_r, _zj_new_s))
                                    score_result['marriage_details'] = _md_real
                                    if isinstance(_sd, dict):
                                        _sd['嫁娶明细(分项)'] = _md_real
                                        _sd['五行评分'] = (_sd.get('五行评分') or 0) + _delta
                                        if '总分' in _sd:
                                            _sd['总分'] = (_sd.get('总分') or 0) + _delta
                                    score_result['score'] = (score_result.get('score') or 0) + _delta
                                    # 等级重判（与评分器同阈值，两级婚嫁调整走统一方法）
                                    _lv_new = _rds._get_level(
                                        score_result['score'],
                                        {'score': (_sd.get('五行评分') or 0) if isinstance(_sd, dict) else 0},
                                        score_result.get('huangdao_info') or {})
                                    _lv_new, _cap_l1, _cap_l2 = _rds._apply_marriage_level_caps(
                                        _lv_new,
                                        {'details': _md_real,
                                         'warnings': score_result.get('warnings') or []})
                                    score_result['level'] = _lv_new
                                    # 2026-10-15 四数同源修复（2026-04-28审查S1）：合局差额
                                    # 既改 score_details 与 score_result，顶部(result)与五行
                                    # 分析段(wu_xing_result['score'])必须同步刷新，否则同一份
                                    # 报告出现 122/113/115/124 四个数字打架。
                                    result['score'] = score_result['score']
                                    result['level'] = _lv_new
                                    if isinstance(_wr3, dict) and isinstance(_sd, dict):
                                        _wr3['score'] = _sd.get('五行评分') or 0
                                    _capped_real = '犯忌嫁娶' in _lv_new
                                    _minor_real = '降一格' in _lv_new
                                    # "嫁娶要点"行同步替换旧合局名
                                    for _pi, _pline in enumerate(_head_parts):
                                        if _old_zj_name and _old_zj_name in _pline:
                                            _head_parts[_pi] = _pline.replace(_old_zj_name, _zj_new_r)
                            except Exception as _gz_e:
                                print(f"[最佳吉时] 合局重算失败: {_gz_e}")
                            _vrs = score_result.get('veto_reasons') or []
                            _veto_real = ('、'.join(str(_v) for _v in _vrs[:3])
                                          if _vrs else None)
                            _tail_new = _rds._build_marriage_reason_tail(
                                _wr3 if isinstance(_wr3, dict) else {},
                                _yl_new,
                                _sd.get('月令得分', 0) or 0,
                                _sd.get('喜用神得分', 0) or 0,
                                score_result.get('shensha_list') or [],
                                _md_real,
                                _veto_real,
                                _capped_real,
                                level_str=score_result.get('level'),
                                minor_downgrade=_minor_real)
                            _new_parts = [p for p in _head_parts if p]
                            if _tail_new:
                                _new_parts.append(_tail_new)
                            score_result['reason'] = '\n'.join(_new_parts)
                            if isinstance(_wr3, dict):
                                _wr3['ji_yu'] = score_result['reason']
                        else:
                            score_result['reason'] = _rds._generate_reason(
                                _wr3 if isinstance(_wr3, dict) else {},
                                score_result.get('huangdao_info') or {},
                                _sd.get('月令得分', 0) or 0,
                                _sd.get('喜用神得分', 0) or 0,
                                score_result.get('owner_matches'),
                                score_result.get('sun_moon_info') or {},
                            )
                    except Exception as _re:
                        print(f"[最佳吉时] 重算综合评语失败: {_re}")
                except Exception as _e5:
                    print(f"[最佳吉时] 重算五行详情失败: {_e5}")


                # (6) 分金大凶复核（2026-09-02用户确认：分金大凶一票否决）：
                #     评分管线以基准四柱（午时）评估分金，展示层【分金五行分析】以权威
                #     四柱（含推荐时柱）计算，二者不一致会导致"展示大凶-40"与"综合吉"
                #     并存。注入推荐时柱后用权威四柱复核分金，达"大凶/凶(犯大煞)"或
                #     得分≤-30 即一票否决，与评分器分金/正体大凶否决口径一致。
                try:
                    _sx_val = getattr(self, 'shan_xiang', None)
                    _sx_str = _sx_val.get() if hasattr(_sx_val, 'get') else (_sx_val or '')
                    # 2026-09-10 fix: GUI jian_xiang is a separate field; scan loop
                    # combines shan_xiang+jian_xiang before scoring. The (6)/(7)
                    # rechecks must use the same full string, otherwise feixing
                    # recheck sees wrong mountain (wuhuang-dao-shan false veto).
                    _jx_val = getattr(self, 'jian_xiang', None)
                    _jx_str = _jx_val.get() if hasattr(_jx_val, 'get') else (_jx_val or '')
                    if _sx_str and _jx_str and _jx_str != '\u6b63\u4e2d':
                        _sx_str = f"{_sx_str}{_jx_str}"
                    if _sx_str and '山' in _sx_str:
                        from modules.二十四山 import ZhengTiWuXingSelectorDB as _FJSel
                        _fjs = _FJSel()
                        _sn = _sx_str.split('山')[0].strip()
                        _fjr = None
                        _jx_txt = ''
                        if '兼' in _sx_str:
                            _jx_txt = '兼' + _sx_str.rsplit('兼', 1)[1][:1]
                            _fjr = _fjs.evaluate_with_fengjin(
                                _sn, _jx_txt, nian_zhu, yue_zhu, ri_zhu, best_shizhu,
                                use_fengjin_wuxing=True)
                        else:
                            _fjr = _fjs.evaluate_by_name(
                                _sn, nian_zhu, yue_zhu, ri_zhu, best_shizhu)
                        if isinstance(_fjr, dict) and _fjr.get('success', True):
                            _fj_score = _fjr.get('score', 0)
                            _fj_level = _fjr.get('level', '')
                            _fj_hit = (_fj_level in ('大凶', '凶(犯大煞)') or
                                       (isinstance(_fj_score, (int, float)) and _fj_score <= -30))
                            if _fj_hit:
                                # (6) 2026-09-03 用户放宽：分金大凶不再无条件否决
                                #   • 重度：≤-50且无吉神制化 → 一票否决（保留原口径）
                                #   • 中度：≤-30但≥-49，或有吉神制化 → 扣分-15/-20/-30，保留为候选课
                                # 吉神制化判据：yi_list含制化或神煞列表有≥10分吉神
                                _severe = (isinstance(_fj_score, (int, float)) and
                                           _fj_score <= -50)
                                _jid_list = score_result.get('yi_list') or []
                                _ssl = score_result.get('shensha_list') or []
                                _good_qual = (isinstance(_ssl, list) and
                                              any(isinstance(_s, dict) and
                                                  int(_s.get('score', 0)) >= 10
                                                  for _s in _ssl))
                                _has_zhi = False
                                if isinstance(_jid_list, list):
                                    for _j in _jid_list:
                                        _t = str(_j)
                                        if any(_kw in _t for _kw in
                                               ['（有制化：', '天德', '月德', '岁德',
                                                '天乙', '太阳', '太阴', '玉堂', '青龙']):
                                            _has_zhi = True; break
                                if not _has_zhi and _good_qual:
                                    _has_zhi = True
                                if '兼' in _sx_str:
                                    _fj_tag = (f"分金：{_sn}山{_jx_txt}第{_fjr.get('fengjin_index','?')}分金"
                                               f"{_fjr.get('fengjin_ganzhi','')}（{_fjr.get('nayin_name','')}），"
                                               f"日课与分金生克得分{_fj_score}")
                                else:
                                    _fj_tag = (f"正体：{_sn}山正体五行受日课四柱生克"
                                               f"（得分{_fj_score}）")
                                if _severe and not _has_zhi:
                                    # 重度+无制化：一票否决
                                    _fj_reason = f"{_fj_tag}，重度且无吉神制化，一票否决"
                                    score_result['score'] = 0
                                    score_result['level'] = '❌ 凶'
                                    _vr_list = score_result.get('veto_reasons')
                                    score_result['veto_reasons'] = (
                                        list(_vr_list) if isinstance(_vr_list, list) else []
                                    ) + [_fj_reason]
                                    _wl_r = score_result.get('wu_xing_result')
                                    if isinstance(_wl_r, dict):
                                        _jl = _wl_r.get('ji_list')
                                        if isinstance(_jl, list) and _fj_reason not in _jl:
                                            _jl.append(_fj_reason)
                                    if isinstance(result, dict):
                                        result['score'] = 0
                                        result['level'] = '❌ 凶'
                                else:
                                    _deduct = 30 if _severe else (20 if _fj_score <= -40
                                                                  else (15 if _fj_score <= -30 else 10))
                                    _hint = "重度有制化" if _severe else ("中度有制化" if _has_zhi else "中度")
                                    _fj_reason = (f"分金警告（{_hint}）：{_fj_tag}，扣 -{_deduct} 分"
                                                  f"（非否决，保留候选）")
                                    try:
                                        score_result['score'] = max(0, int(score_result.get('score') or 0) - _deduct)
                                    except (TypeError, ValueError):
                                        pass
                                    _wl_r = score_result.get('wu_xing_result')
                                    if isinstance(_wl_r, dict):
                                        _jl = _wl_r.get('ji_list')
                                        if isinstance(_jl, list) and _fj_reason not in _jl:
                                            _jl.append(_fj_reason)
                                    if isinstance(result, dict):
                                        try:
                                            result['score'] = max(0, int(result.get('score') or 0) - _deduct)
                                        except (TypeError, ValueError):
                                            pass

                        # (7) 玄空飞星大凶复核（2026-09-02用户确认）：注入推荐时柱后用
                        #     权威四柱重算飞星，飞星等级"大凶"或断语含"切忌"（五黄/二黑
                        #     到山）即一票否决，与评分器飞星大凶否决口径一致。
                        try:
                            if self._get_zeli_mode() != 'feixing':
                                raise RuntimeError('_zm0915 pure skip feixing recheck')
                            from modules.评分器 import Scorer as _FXScorer
                            _fxr = _FXScorer()._calculate_feixing_score(
                                {'年柱': nian_zhu, '月柱': yue_zhu, '日柱': ri_zhu,
                                 '时柱': best_shizhu, 'year': current_date.year,
                                 # 2026-09-11 fix: 日星六中气换元必须按公历日期切段，
                                 # 缺 date 会走默认五黄入中+阳遁兜底，阴遁日时（如庚午日
                                 # 癸未时八白到坤）被误排成五黄到山而错否决。
                                 'date': current_date,
                                 'month': current_date.month,
                                 'day': current_date.day},
                                _sx_str)
                            if isinstance(_fxr, dict) and (
                                    _fxr.get('feixing_level') == '大凶'
                                    or '切忌' in str(_fxr.get('feixing_comment', ''))):
                                _fx_reason = (
                                    f"玄空飞星大忌：{_fxr.get('feixing_comment', '飞星大凶')}"
                                    f"（飞星{_fxr.get('feixing_score')}分，一票否决）")
                                score_result['score'] = 0
                                score_result['level'] = '❌ 凶'
                                _vr_list2 = score_result.get('veto_reasons')
                                _vr_now2 = list(_vr_list2) if isinstance(_vr_list2, list) else []
                                # 2026-09-12 fix: 评分器对同一四柱已追加过同条飞星否决
                                # （2026-10-03案重复显示两条），去重；仅当无飞星大忌时补登
                                # （评分器在已有其他否决时会跳过飞星计算，此时(7)块补登仍必要）
                                if not any(str(_x).startswith('玄空飞星大忌') for _x in _vr_now2):
                                    _vr_now2.append(_fx_reason)
                                score_result['veto_reasons'] = _vr_now2
                                if isinstance(result, dict):
                                    result['score'] = 0
                                    result['level'] = '❌ 凶'
                        except Exception as _fx_e:
                            if '_zm0915' not in str(_fx_e):  # 纯模式跳过不打印
                                print(f"[最佳吉时] 飞星复核失败: {_fx_e}")
                except Exception as _fj_e:
                    print(f"[最佳吉时] 分金复核失败: {_fj_e}")
        except Exception as _e:
            print(f"[最佳吉时] 注入时柱失败: {_e}")
            # 出错就保持原午时柱不动，避免影响计算/显示
        finally:
            # 2026-10-02 性能优化（方向D）：清理内部缓存键，避免泄露到结果详情
            if isinstance(wushu_sizhu, dict) and '_rescan_hour_scores' in wushu_sizhu:
                del wushu_sizhu['_rescan_hour_scores']
            if isinstance(score_result, dict) and '_rescan_hour_scores' in score_result:
                del score_result['_rescan_hour_scores']

    def _rescan_best_hour(self, current, event_type, owners_data, house_type,
                          shan_xiang, zao_xiang, zao_wei, chuang_wei,
                          zaozhu_mode, init_sizhu, init_result):
        """12时辰实评择优（正常择日/条件择日共用的唯一实现，2026-09-16 合并）。

        以午时结果为初值，遍历其余11个时辰实评，逐对比较取综合最优：
        否决数(含分金重罚) → 扣分金后总分 → 无杀师 → 分金档 → 五行原始分。
        否决文案可能随时柱制化消除，故12时辰必须评满，不按文案关键词跳过。

        Returns:
            (best_sizhu, best_result): 最优时辰四柱及其评分结果
        """
        _best_sz = init_sizhu
        _best_r = init_result
        # full shan-xiang incl. jian for fenjin preview
        _sxf_full = shan_xiang or ''
        _jxv = getattr(self, 'jian_xiang', None)
        _jxs = _jxv.get() if hasattr(_jxv, 'get') else (_jxv or '')
        if _sxf_full and _jxs and _jxs != '正中':
            _sxf_full = f"{_sxf_full}{_jxs}"
        _cur_sc = int(init_result.get('score') or 0)
        _cur_veto = len(init_result.get('veto_reasons') or [])

        # 2026-09-17 隐患1 方案C：调 resolve_recommended_hour 拿 lucky_hours，
        #   计算 _ck_scores 与 _ck_w（嫁娶专用时辰表分数权重），
        #   与 _inject_best_hour_to_result 的 _skey 第2位 _ck 项同口径。
        #   lucky_hours 不依赖输入 sizhu 的时柱（推荐时柱.py L183 注释明确
        #   "时柱无需提供"，由年月日柱 + 事项类型 + checker 决定），
        #   所以 _rescan 用 init_sizhu 算出的 lucky_hours 与 _inject 用
        #   _best_sz 算出的 lucky_hours 实质等价；缓存到 self._cached_rec
        #   供 _inject 复用，避免重复构造 checker。
        try:
            from modules.推荐时柱 import resolve_recommended_hour
            _sv0 = getattr(self, 'shan_xiang', None)
            _shan_str0 = _sv0.get() if hasattr(_sv0, 'get') else (_sv0 or '')
            _rec = resolve_recommended_hour(
                init_sizhu, event_type,
                owners_data if isinstance(owners_data, list) else [],
                _shan_str0)
            _lh = _rec['lucky_hours'] if _rec else None
            # 缓存键四元组：日期/事项/事主指纹/坐山。_inject 复用前必须四者全等，
            # 防止跨天、切换事项、编辑事主或更改坐山后误用前一轮推荐时柱。
            self._cached_rec = _rec
            self._cached_rec_key = (current, event_type,
                                    _owners_fingerprint(owners_data), _shan_str0)
        except Exception:
            _lh = None
            self._cached_rec = None
            self._cached_rec_key = None
        _ck_scores = {}
        if isinstance(_lh, list):
            for _h in _lh:
                if isinstance(_h, dict):
                    _ck_scores[str(_h.get('地支', ''))] = int(_h.get('分值', 0) or 0)
        # _ck0915：仅嫁娶事件将时辰表分数纳入排序优先级；非嫁娶仍以完整评分器总分为准
        # 2026-09-17 隐患1 方案C收口：两处 _ck_w 统一以注册表 MARRIAGE_EVENTS
        #   （嫁娶/订婚/纳采）为唯一口径，禁止再硬编码事项列表。
        _ck_w = 1 if event_type in MARRIAGE_EVENTS else 0

        _hour_candidates = [
            (0, '子'), (2, '丑'), (4, '寅'), (6, '卯'), (8, '辰'), (10, '巳'),
            (12, '午'), (14, '未'), (16, '申'), (18, '酉'), (20, '戌'), (22, '亥')
        ]
        # 2026-10-02 性能优化（方向A）：同一天12个时辰的年月日柱完全相同，
        # 只有时柱变化。先缓存基准sizhu的年月日柱，后续11个时辰只算时柱，
        # 避免每个时辰重复调用 sxtwl 做年柱/月柱/日柱的精确计算。
        _base_ymd = None
        if isinstance(init_sizhu, dict):
            _base_ymd = {
                '年柱': init_sizhu.get('年柱', ''),
                '月柱': init_sizhu.get('月柱', ''),
                '日柱': init_sizhu.get('日柱', ''),
                'year_gan': init_sizhu.get('year_gan', ''),
                'year_zhi': init_sizhu.get('year_zhi', ''),
                'month_gan': init_sizhu.get('month_gan', ''),
                'month_zhi': init_sizhu.get('month_zhi', ''),
                'day_gan': init_sizhu.get('day_gan', ''),
                'day_zhi': init_sizhu.get('day_zhi', ''),
            }
        # 2026-10-02 性能优化（方向D）：缓存12时辰评分结果，供 _inject_best_hour_to_result 复用，
        # 避免注入时重复调用 calculate_sizhu + calculate_score。
        _hour_scores = {}
        for _hh, _hz in _hour_candidates:
            if _hh == 12:
                continue  # 午时已在best初值
            try:
                _hs = calculate_sizhu(current, _hh, 0)
                _hs['year'] = current.year
                _hs['month'] = current.month
                _hs['day'] = current.day
                _hs['date'] = current
                # 方向A：复用年月日柱，仅重算时柱
                # 2026-10-03 交节日修正：年月日柱在同一天内并非恒定——交节时刻
                # 之后时辰的月柱已入下月（如2026-01-05小寒约16:23交节，酉/戌/亥
                # 时真实月柱己丑，曾被压回戊子致评分98→83），立春日04:02后年柱
                # 切换同理。calculate_sizhu 按时辰精度算出的年月日柱是权威值，
                # 仅当与午时基准一致时才覆写统一；不一致（跨节气时辰）时保留
                # 时辰精确值，防止交节后时辰沿用交节前月柱/年柱评分。
                if _base_ymd and (
                        _hs.get('年柱') == _base_ymd['年柱']
                        and _hs.get('月柱') == _base_ymd['月柱']
                        and _hs.get('日柱') == _base_ymd['日柱']):
                    _hs['年柱'] = _base_ymd['年柱']
                    _hs['月柱'] = _base_ymd['月柱']
                    _hs['日柱'] = _base_ymd['日柱']
                    _hs['year_gan'] = _base_ymd['year_gan']
                    _hs['year_zhi'] = _base_ymd['year_zhi']
                    _hs['month_gan'] = _base_ymd['month_gan']
                    _hs['month_zhi'] = _base_ymd['month_zhi']
                    _hs['day_gan'] = _base_ymd['day_gan']
                    _hs['day_zhi'] = _base_ymd['day_zhi']
                _hr = calculate_score(_hs, event_type, owners_data, house_type,
                                      shan_xiang, zao_xiang, zao_wei, chuang_wei,
                                      zaozhu_mode=zaozhu_mode,
                                      zeli_mode=self._get_zeli_mode())  # _zm0915
                # 方向D：缓存本时辰结果，键=时辰地支
                _hour_scores[_hz] = (_hs, _hr)
                _hs_sc = int(_hr.get('score') or 0)
                _hs_veto = len(_hr.get('veto_reasons') or [])
                _cur_ss = int(any(isinstance(_s, dict)
                                  and '\u6740\u5e08' in str(_s.get('name', ''))
                for _s in (_best_r.get('shensha_list') or [])))
                _hs_ss = int(any(isinstance(_s, dict)
                                 and '\u6740\u5e08' in str(_s.get('name', ''))
                for _s in (_hr.get('shensha_list') or [])))
                _cur_wx = int((_best_r.get('score_details') or {}).get('五行评分') or 0)
                _hs_wx = int((_hr.get('score_details') or {}).get('五行评分') or 0)
                # fenjin (6) preview for incumbent and candidate
                _cfg = _best_r.get('sizhu') if isinstance(_best_r.get('sizhu'), dict) else {}
                _hfg = _hr.get('sizhu') if isinstance(_hr.get('sizhu'), dict) else {}
                _cfl, _cfd = _fenjin_preview_penalty(
                    _sxf_full, str(_cfg.get('年柱', '')), str(_cfg.get('月柱', '')),
                    str(_cfg.get('日柱', '')), str(_cfg.get('时柱', '')),
                    _best_r.get('yi_list') or [], _best_r.get('shensha_list') or [])
                _hfl, _hfd = _fenjin_preview_penalty(
                    _sxf_full, str(_hfg.get('年柱', '')), str(_hfg.get('月柱', '')),
                    str(_hfg.get('日柱', '')), str(_hfg.get('时柱', '')),
                    _hr.get('yi_list') or [], _hr.get('shensha_list') or [])
                # 越小越优 + <（与 _inject_best_hour (5.5) 的 _skey 同口径）：
                # fewer vetoes(+severe) > higher checker score (时辰表分数, # _ck0915 嫁娶专用)
                # > higher post-(6) score > no sha-shi > clean fenjin > higher raw wuxing。
                # 2026-07 修正：旧元组用“>”且否决数未取负，导致否决多的候选反而替换
                # 代表（交节日会让交节后被否时辰占住基准月柱）。统一改为“越小越优 + <”。
                # 2026-09-17 隐患1 方案C：在原 5 元组第 2 位插入 _ck 项（与 _inject._skey
                #   完全一致），消除两次择优排序键不一致；_ck_scores 取不到时辰的地支记 0。
                _cur_sz_hz = ''
                _rv = _best_sz.get('时柱', '') if isinstance(_best_sz, dict) else ''
                if isinstance(_rv, str) and len(_rv) >= 2:
                    _cur_sz_hz = _rv[1]
                _bet = ((_hs_veto + (1 if _hfl == 2 else 0),
                         -(_ck_scores.get(_hz, 0) * _ck_w),
                         -(_hs_sc - (_hfd if _hfl >= 1 else 0)),
                         _hs_ss, _hfl, -_hs_wx) <
                        (_cur_veto + (1 if _cfl == 2 else 0),
                         -(_ck_scores.get(_cur_sz_hz, 0) * _ck_w),
                         -(_cur_sc - (_cfd if _cfl >= 1 else 0)),
                         _cur_ss, _cfl, -_cur_wx))
                if _bet:
                    _best_sz = _hs
                    _best_r = _hr
                    _cur_sc = _hs_sc
                    _cur_veto = _hs_veto
            except Exception:
                continue
        # 方向D：把12时辰评分结果挂到返回值上，供 _inject_best_hour_to_result 复用
        # 键 = 时辰地支（'子'/'丑'/.../'亥'），值 = (sizhu_dict, score_result_dict)
        _best_r['_rescan_hour_scores'] = _hour_scores
        # 同时挂在 _best_sz（即 wushu_sizhu）上，因为 _inject 读取的是 wushu_sizhu
        if isinstance(_best_sz, dict):
            _best_sz['_rescan_hour_scores'] = _hour_scores
        return _best_sz, _best_r

    def _render_result_tree(self):
        """把 self.results 统一渲染到结果表（正常择日/条件择日共用）。

        2026-09-16 口径统一：原两条计算链路各自维护一份"排序→列标题→清空→12列插入"
        代码，容易在列构造上漂移；现收口为本方法，评分/等级/五行/月令/喜用/黄道/
        地支关系/吉神（不合格模式为原因）/大利月/事主/飞星 12 列顺序固定。
        """
        # 按评分从高到低排序
        self.results.sort(key=lambda x: x.get('score', 0), reverse=True)

        # 根据输出模式动态调整"吉神信息"列标题
        _cur_mode = self.output_mode_var.get()
        _col_title = '不合格原因' if _cur_mode == 'unqualified' else '吉神信息'
        self.result_tree.heading('吉神信息', text=_col_title)

        # 清空树形视图并重新添加排序后的结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        for result in self.results:
            level = result.get('level', '未知')
            row_tag = _star_row_tag(level)
            # 得分列统一±号格式化；2026-09-03 四柱并入首列两行显示；
            # 不合格输出模式下"吉神信息"列显示不合格原因
            _display_jishen = result.get('unqualified_reasons') or result.get('jishen', '-')
            self.result_tree.insert("", tk.END, values=(
                _fmt_tree_date_sizhu(result.get('date', ''), result.get('sizhu', '-')),
                result.get('score', 0),
                level,
                self._fmt_score(result.get('wuxing_score', 0), '0'),
                self._fmt_score(result.get('yueling_score', 0), '0'),
                self._fmt_score(result.get('xishen_score', 0), '0'),
                self._fmt_score(result.get('huangdao_score', 0), '0'),
                _fmt_tree_relation(result.get('dizhi_relation', '')),
                _display_jishen,
                result.get('daliyue', '-'),
                result.get('owners', '-'),
                result.get('feixing', '-')
            ), tags=(row_tag,))

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
            
            # ===== 初始化进度条 =====
            total_days = (end - start).days + 1
            self.progress_var.set(0.0)
            self.progress_bar['maximum'] = total_days
            self.progress_label.config(text=f"⏳ 开始计算：共 {total_days} 天")
            self.root.update_idletasks()

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
                    
                    # 真太阳时 §48：事主经度透传（扫日回路不弹窗，入口已警告）
                    birth_longitude = _parse_owner_longitude(owner.get('longitude'), show_warning=False)
                    owner_sizhu = calculate_sizhu(birth_date, hour, minute, longitude=birth_longitude)
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
                        'birth_longitude': birth_longitude,
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
            # 安葬无墓穴坐山不予计算（_azss0914）
            if not self._require_shan_for_burial(event_type):
                return
            if event_type == '作灶':
                # 2026-09 作灶主事人模式：给打包后的事主打主次/权重标记
                self._tag_zaozhu_owners(owners_data)
            house_type = getattr(self, 'house_type', None)
            house_type = house_type.get() if house_type else None
            shan_xiang = getattr(self, 'shan_xiang', None)
            shan_xiang = shan_xiang.get() if shan_xiang else None
            
            # 获取兼向信息并合并到山向中
            jian_xiang = getattr(self, 'jian_xiang', None)
            jian_xiang_value = jian_xiang.get() if jian_xiang else None
            if shan_xiang and jian_xiang_value and jian_xiang_value != "正中":
                # §59.13 批次一提醒3：提交前校验——非法兼向弹窗提示，不阻断
                # （引擎按正向处理并记日志）
                self._warn_invalid_jianxiang_before_submit(jian_xiang_value)
                # §59.13：手动裸值"亥"规范化为"兼亥"，保证拼接串可被引擎解析
                _jx_v = jian_xiang_value.strip()
                if not _jx_v.startswith('兼'):
                    _jx_v = '兼' + _jx_v
                shan_xiang = f"{shan_xiang}{_jx_v}"
            
            zao_xiang = getattr(self, 'zao_xiang', None)
            zao_xiang = zao_xiang.get() if zao_xiang else None
            zao_wei = getattr(self, 'zao_wei', None)
            zao_wei = zao_wei.get() if zao_wei else None
            chuang_wei = getattr(self, 'chuang_wei', None)
            chuang_wei = chuang_wei.get() if chuang_wei else None

            # 2026-09 作灶主事人模式（非作灶事项为 None，引擎口径不变）
            zaozhu_mode = getattr(self, 'zaozhu_mode', None)
            zaozhu_mode = zaozhu_mode.get() if hasattr(zaozhu_mode, 'get') else None

            print(f"[调试] 事项类型: {event_type}, 山向: {shan_xiang}, 事主数量: {len(owners_data)}")

            # 2026-09-15（_aznh0915）：收集每日忌项/否决原因频次，用于"0结果"时诊断坐山年煞等全年性冲突
            _blanket_ji = collections.Counter()
            _scanned_days = 0

            # 计算每日吉凶
            current = start
            day_index = 0
            while current <= end:
                day_index += 1

                # ---- 更新进度 ----
                self.progress_var.set(day_index)
                self.progress_label.config(
                    text=f"⏳ 正在计算：第 {day_index}/{total_days} 天（{current.strftime('%Y-%m-%d')}）"
                )
                self.root.update_idletasks()

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
                
                # 计算评分（先按基准午时12:00）
                score_result = calculate_score(
                    sizhu,
                    event_type,
                    owners_data,
                    house_type,
                    shan_xiang,
                    zao_xiang,
                    zao_wei,
                    chuang_wei,
                    zaozhu_mode=zaozhu_mode,
                    zeli_mode=self._get_zeli_mode()  # _zm0915
                )

                # 规则3（2026-09-03 用户放宽）：午时基准被否决≠整日淘汰，
                # 自动遍历12时辰，找综合分最高、否决最少的时柱作为本日代表。
                # 2026-09-16 口径统一：正常/条件择日共用 ZeriApp._rescan_best_hour。
                sizhu, score_result = self._rescan_best_hour(
                    current, event_type, owners_data, house_type,
                    shan_xiang, zao_xiang, zao_wei, chuang_wei,
                    zaozhu_mode, sizhu, score_result)

                # 提取各项得分
                score_details = score_result.get('score_details', {})
                wuxing_score = score_details.get('五行评分', 100)
                yueling_score = score_details.get('月令得分', 0)
                xishen_score = score_details.get('喜用神得分', 0)
                huangdao_score = score_details.get('黄道得分', 0)
                
                # 地支关系/吉神两列文本（统一入口；注入推荐时柱后会再次刷新）
                dizhi_text, jishen_text = _extract_tree_dizhi_jishen(score_result)
                
                # 提取大利月/小利月信息（婚嫁专用）
                daliyue_text = '-'
                if event_type in MARRIAGE_EVENTS:
                    # 【F2 一致性修复】默认普通月份：婚嫁类若无大利月/小利月条目
                    # 即普通月份，显示"普通月份"而非"-"，与【嫁娶择日分析】利月分析一致。
                    daliyue_text = '普通月份'
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
                    'score': score_result.get('score', 0),
                    'level': score_result.get('level', '未知'),
                    'wuxing_score': wuxing_score,
                    'yueling_score': yueling_score,
                    'xishen_score': xishen_score,
                    'huangdao_score': huangdao_score,
                    'dizhi_relation': dizhi_text,
                    'jishen': jishen_text,
                    'daliyue': daliyue_text,
                    'owners': owners_text,
                    'feixing': _fmt_feixing(score_result.get('feixing_info')),
                    'zaozhu_mode': zaozhu_mode,
                    'detail': score_result
                }
                # ── 把显示用时柱从"午时示例"替换为"事项专属最佳吉时" ──
                # 评分仍使用午时sizhu（口径不变）；只改 result['sizhu'] 和 score_result['sizhu']
                self._inject_best_hour_to_result(
                    result, score_result, event_type, owners_data, current, sizhu,
                    house_type=house_type, shan_xiang=shan_xiang, zao_xiang=zao_xiang,
                    zao_wei=zao_wei, chuang_wei=chuang_wei
                )
                # 2026-09-05 用户确认：结果表“地支关系/吉神”两列须反映真实推荐时辰
                # 参与的关系——上面注入推荐时柱后，第(5)步已用权威四柱重算 details，
                # 这里随之刷新，避免仍显示基准午时的地支关系误导用户
                try:
                    _dz_txt, _js_txt = _extract_tree_dizhi_jishen(score_result)
                    result['dizhi_relation'] = _dz_txt
                    result['jishen'] = _js_txt
                except Exception:
                    pass

                # 筛选：只保留吉及以上的日课，过滤掉不吉的日课
                # 提取评分和等级
                score = score_result.get('score', 0)
                level = score_result.get('level', '未知')
                yi_list = score_result.get('yi_list', [])
                ji_list = score_result.get('ji_list', [])
                shensha_list = score_result.get('shensha_list', [])

                # 2026-09-15（_aznh0915）：累计忌项与否决原因（去掉规则层追加的事项名标记"安葬"），
                # 用于扫描结束后诊断"0结果"是否为坐山犯年煞等全年性冲突。
                _scanned_days += 1
                for _ji in ji_list:
                    _jt = str(_ji).strip()
                    if _jt and _jt != event_type:
                        _blanket_ji[_jt] += 1
                for _vr in (score_result.get('veto_reasons') or []):
                    _blanket_ji[str(_vr).strip()] += 1
                
                # 过滤条件1：过滤0分的日课
                wu_xing_hege = score > 0
                # 过滤条件2：过滤所有包含"凶"的等级（大凶、小凶、凶）
                is_not_xiong = '凶' not in level
                # 过滤条件3：忌列表中精确包含"忌{事项类型}"的日课
                # 使用正则表达式精确匹配，避免"建除平日忌修造"被误判
                has_ji_event = False
                for ji in ji_list:
                    ji_text = str(ji)
                    if re.search(rf'^忌{re.escape(event_type)}[。\s]?$', ji_text):
                        has_ji_event = True
                        break

                # 过滤条件4和5：检查神煞中是否有不宜当前事项类型的信息和严重凶煞信息
                # 注意：只有在评分不吉时才使用这些条件作为补充过滤
                # 如果评分已经是吉的，说明神煞的负面影响已经被其他因素抵消
                has_buyi_event = False
                has_serious_xiong_shen = False
                if not (wu_xing_hege and is_not_xiong):
                    for shensha in shensha_list:
                        if isinstance(shensha, dict):
                            shensha_desc = shensha.get('description', '') or shensha.get('name', '')
                        else:
                            shensha_desc = str(shensha)

                        if re.search(rf'不宜{re.escape(event_type)}[。\s]?$', shensha_desc) or re.search(rf'^忌{re.escape(event_type)}[。\s]?$', shensha_desc):
                            has_buyi_event = True

                        serious_xiong_keywords = ['大凶', '绝对不可用']
                        for keyword in serious_xiong_keywords:
                            if keyword in shensha_desc:
                                has_serious_xiong_shen = True
                                break

                        if re.search(rf'^忌{re.escape(event_type)}[。\s]?$', shensha_desc):
                            has_serious_xiong_shen = True

                        if has_buyi_event and has_serious_xiong_shen:
                            break
                
                # 获取输出方式选择（提前判断，不合格模式需绕过吉/凶门槛）
                output_mode = self.output_mode_var.get()

                # ===== 不合格输出模式（终判口径）：仅收录最终结论不合格日课
                    # （一票否决/五行门槛未过/总分0/等级凶/忌本事项）；小扣分仅展示不决定收录（2026-09-11） =====
                if output_mode == "unqualified":
                    wu_xing_result = score_result.get('wu_xing_result', {}) or {}
                    _wx_jiyu = str(wu_xing_result.get('ji_yu', '') or '')
                    # 计算错误/异常属程序问题，不作为"不合格日课"展示，跳过；
                    # 其余 0 分日（月份/年份不宜、三煞大忌、飞星/分金大凶等一票否决）
                    # 恰恰是最该列出的"不合格日课"，不再用 score<=0 一刀切排除——
                    # 否则月份分析判凶（整月 score=0）时，不合格输出反而一个都选不到。
                    if ('计算错误' in _wx_jiyu) or ('计算异常' in _wx_jiyu):
                        current += timedelta(days=1)
                        continue

                    has_wuxing_koufen = bool(wu_xing_result.get('has_deduction', False))

                    score_details = score_result.get('score_details', {}) or {}
                    def _I(v): return int(v) if isinstance(v, (str, int, float)) else 0
                    yueling_score_v = _I(score_details.get('月令得分', 0))
                    huangdao_score_v = _I(score_details.get('黄道得分', 0))
                    xishen_score_v = _I(score_details.get('喜用神得分', 0))
                    xiangzhu_score_v = _I(score_details.get('相主得分', 0))
                    sun_moon_score_v = _I(score_details.get('太阳太阴得分', 0))

                    sansha_info = score_result.get('sansha_info', {}) or {}
                    sansha_penalty_v = _I(sansha_info.get('sansha_penalty', 0))

                    # 任一神煞得分 < 0 即视为有扣分
                    xiong_shen_items = []
                    for s in shensha_list:
                        if isinstance(s, dict):
                            try:
                                sc = int(s.get('score', 0))
                            except (TypeError, ValueError):
                                sc = 0
                            if sc < 0:
                                xiong_shen_items.append(s.get('name', '凶煞'))

                    # 忌列表不为空 → 视为有"忌扣分项"
                    ji_items = [str(j).strip() for j in ji_list if str(j).strip()]

                    # 一票否决原因（含 月份不宜/年份不宜/三煞大忌/山家封禁/飞星大凶/分金大凶 等）
                    veto_reasons = score_result.get('veto_reasons', []) or []

                    # ── 终判口径硬信号（2026-09-11）：命中任一才收录 ──
                    _real_veto = []
                    for _vr in veto_reasons:
                        _vrt = str(_vr).strip()
                        if _vrt and ('计算错误' not in _vrt) and ('计算异常' not in _vrt):
                            _real_veto.append(_vrt)
                    _wx_fail = (not wu_xing_result.get('he_ge', True)) and bool(_wx_jiyu)
                    _hard_fail = (bool(_real_veto) or _wx_fail or score <= 0
                                  or (not is_not_xiong) or has_ji_event)
                    if not _hard_fail:
                        # 终判合格（仅小扣分/三煞临方扣分/有制化软忌项）→ 不进不合格列表
                        current += timedelta(days=1)
                        continue

                    unqualified_reasons = list(_real_veto)
                    # 五行不合格但未列入 veto_reasons 的兜底（he_ge=False 且有 ji_yu）
                    if _wx_fail and not any(_wx_jiyu in r for r in unqualified_reasons) \
                            and ('计算错误' not in _wx_jiyu) and ('计算异常' not in _wx_jiyu):
                        unqualified_reasons.append(_wx_jiyu)
                    if score <= 0 and not any('总分' in r for r in unqualified_reasons):
                        unqualified_reasons.append(f'总分{score}分')
                    # 等级为凶
                    if not is_not_xiong:
                        unqualified_reasons.append(f'等级:{level}')
                    if has_ji_event:
                        unqualified_reasons.append(f'忌本事项（{event_type}）')
                    # ── 以下扣分明细仅作展示，非收录条件：单个凶神负分、三煞临方
                    # （山向类口径扣分不否决）、有制化软忌项等，终判仍吉的日课不会因此被收录 ──
                    _deduct_parts = []
                    if has_wuxing_koufen:
                        _deduct_parts.append('五行有扣分')
                    if yueling_score_v < 0:
                        _deduct_parts.append(f"月令{yueling_score_v}")
                    if huangdao_score_v < 0:
                        _deduct_parts.append(f"黄道{huangdao_score_v}")
                    if xishen_score_v < 0:
                        _deduct_parts.append(f"喜用神{xishen_score_v}")
                    if xiangzhu_score_v < 0:
                        _deduct_parts.append(f"相主{xiangzhu_score_v}")
                    if sun_moon_score_v < 0:
                        _deduct_parts.append(f"太阳太阴{sun_moon_score_v}")
                    if sansha_penalty_v < 0:
                        _deduct_parts.append(f"三煞{sansha_penalty_v}")
                    if xiong_shen_items:
                        _deduct_parts.append('凶煞: ' + '、'.join(xiong_shen_items[:5]))
                    if ji_items:
                        _deduct_parts.append('忌: ' + '、'.join(ji_items[:5]))
                    if _deduct_parts:
                        unqualified_reasons.append('扣分明细：' + '；'.join(_deduct_parts))

                    # 记录不合格原因到 result，供结果列表展示
                    result['unqualified_reasons'] = '；'.join(unqualified_reasons)
                    result['is_unqualified'] = True
                    self.results.append(result)
                    print(f"[调试-不合格] {current}, score={score}, level={level}, reasons={len(unqualified_reasons)}项")
                    current += timedelta(days=1)
                    continue

                # ===== 正常平分模式：原有过滤逻辑 =====
                # 综合过滤条件：评分吉且等级不凶且不忌当前事项
                if wu_xing_hege and is_not_xiong and not has_ji_event:
                    self.results.append(result)
                    print(f"[调试] 通过: {current}, score={score}, level={level}")
                else:
                    # 打印哪个过滤条件失败
                    filters_failed = []
                    if not wu_xing_hege:
                        filters_failed.append(f"score={score}")
                    if not is_not_xiong:
                        filters_failed.append(f"level={level}")
                    if has_ji_event:
                        filters_failed.append("has_ji_event")
                    if has_buyi_event:
                        filters_failed.append("has_buyi_event")
                    if has_serious_xiong_shen:
                        filters_failed.append("has_serious_xiong_shen")
                    print(f"[调试] {current} 被过滤: {', '.join(filters_failed)}")

                current += timedelta(days=1)

            print(f"[调试] 计算完成，共 {len(self.results)} 个结果通过")

            # 2026-09-15（_aznh0915）：安葬 0 结果诊断 —— 若所选坐山在本年犯年三煞/年冲山/岁破等
            # 全年性冲突，几乎每日都被同一忌项否决，明确提示用户，而非默默显示"0结果"。
            _finish_msg = f"✅ 计算完成！共 {len(self.results)} 个结果通过筛选"
            if event_type == '安葬' and not self.results and _scanned_days > 0 and shan_xiang:
                # 覆盖天数占比 >= 80% 的忌项视为全年性冲突
                _threshold = max(1, int(_scanned_days * 0.8))
                # _aznh0916：全年性坐山禁忌关键词——年三煞/岁破/太岁类 + 年家五黄二黑封禁类
                # （如丙午年一白入中，二黑到乾宫则戌乾亥三山全年犯二黑；五黄到离则丙午丁全年犯五黄）
                if self._get_zeli_mode() == 'pure':  # _zm0915 纯正五行不统计紫白封禁
                    _annual_keys = ('犯年三煞', '年三煞(山向)', '年家三煞', '年冲山', '犯岁破',
                                    '冲山', '太岁压', '山家封禁')
                else:
                    _annual_keys = ('犯年三煞', '年三煞(山向)', '年家三煞', '年冲山', '犯岁破',
                                    '冲山', '太岁压', '年家二黑', '年家五黄', '二黑', '五黄',
                                    '病符', '山家封禁', '到山')
                _blanket_hits = [(_t, _c) for _t, _c in _blanket_ji.items()
                                 if _c >= _threshold and any(_k in _t for _k in _annual_keys)]
                if _blanket_hits:
                    _blanket_hits.sort(key=lambda x: -x[1])
                    _top = _blanket_hits[0][0]
                    if len(_top) > 46:
                        _top = _top[:46] + '…'
                    _blanket_hint = (f"请更换不犯年三煞、岁破等年家坐山禁忌的坐山，或改择其他年份。"
                                     if self._get_zeli_mode() == 'pure' else
                                     f"请更换不犯年三煞、年家五黄二黑的坐山，或改择其他年份。")  # _zm0915
                    _finish_msg = (
                        f"⚠ 所选坐山 {shan_xiang} 在 {start.year} 年犯年家坐山禁忌"
                        f"（{_top}），本年内该坐山基本无合格安葬日。"
                        f"{_blanket_hint}"
                        f"（共扫描 {_scanned_days} 天）")
                    print(f"[诊断] 安葬0结果：坐山年家禁忌 -> {_top}")

            # ===== 进度完成 =====
            self.progress_var.set(total_days)
            self.progress_label.config(text=_finish_msg)
            self.root.update_idletasks()

            # 统一渲染结果表（排序/列标题/12列构造；与条件择日链路共用同一方法）
            self._render_result_tree()

            # 保存到记录
            self.save_record()
            
            self._maybe_save_owners_on_finish(f"择日计算完成！\n共计算 {(end - start).days + 1} 天")
            
        except Exception as e:
            self.progress_var.set(0)
            self.progress_label.config(text="❌ 计算出错")
            messagebox.showerror("错误", f"计算出错：{str(e)}")
            import traceback
            traceback.print_exc()
    
    def conditional_calculation(self):
        """按输入条件择日"""
        # 创建条件设置对话框
        condition_window = tk.Toplevel(self.root)
        condition_window.title("条件择日设置")
        condition_window.geometry("700x600")
        condition_window.minsize(600, 400)
        
        # 设置ttk样式，使勾选框显示为✓而不是x
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建带滚动条的框架
        main_canvas = tk.Canvas(condition_window, highlightthickness=0)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(condition_window, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(main_canvas, padding=20)
        main_canvas.create_window((0, 0), window=main_frame, anchor='nw', width=condition_window.winfo_width())
        
        def update_canvas(event):
            main_canvas.configure(scrollregion=main_canvas.bbox('all'))
            main_canvas.itemconfigure(1, width=event.width)
        
        main_canvas.bind('<Configure>', update_canvas)
        
        # 条件变量
        self.condition_vars = {
            'min_score': tk.IntVar(value=60),
            'min_stars': tk.IntVar(value=2),
            'must_have_jishen': tk.StringVar(value=''),
            'must_have_huangdao': tk.BooleanVar(value=False),
            'exclude_xiong': tk.BooleanVar(value=True),
            'exclude_ji': tk.BooleanVar(value=False),
            'max_results': tk.IntVar(value=20),
            'include_xishen': tk.BooleanVar(value=False),
            'require_owner_match': tk.BooleanVar(value=False)
        }
        
        # 评分条件
        score_frame = ttk.LabelFrame(main_frame, text="评分条件")
        score_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(score_frame, text="最低评分：").pack(side=tk.LEFT, padx=5)
        min_score_spin = ttk.Spinbox(score_frame, from_=0, to=200, textvariable=self.condition_vars['min_score'], width=10)
        min_score_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(score_frame, text="分").pack(side=tk.LEFT, padx=5)
        
        # 星级条件
        star_frame = ttk.LabelFrame(main_frame, text="星级条件")
        star_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(star_frame, text="最低星级：").pack(side=tk.LEFT, padx=5)
        min_stars_spin = ttk.Spinbox(star_frame, from_=1, to=5, textvariable=self.condition_vars['min_stars'], width=10)
        min_stars_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(star_frame, text="颗星").pack(side=tk.LEFT, padx=5)
        
        # 吉神条件（按事项类型分组显示）
        jishen_frame = ttk.LabelFrame(main_frame, text="吉神条件")
        jishen_frame.pack(fill=tk.X, pady=10)

        current_event = self.event_var.get()
        
        marriage_gods = ['天德贵人', '月德贵人', '天乙贵人', '禄神', '福星', '不将日', '周堂吉日', 
                         '天德日', '月德日', '三合', '六合', '五合日', '母仓', '王日',
                         '天喜', '红鸾', '生气', '圣心', '解神', '天恩', '阴德', '续世',
                         '大利月', '小利月', '五行相生', '天地同流', '天干三朋', '旺相得令']
        
        common_gods = ['天德贵人', '月德贵人', '天乙贵人', '文昌贵人', '禄神', '福星',
                       '三合局', '六合',
                       '天德日', '月德日', '天赦', '圣心', '解神', '天恩', '阴德', '母仓',
                       '五行相生', '天地同流', '天干三朋', '旺相得令']
        
        burial_gods = ['天德贵人', '月德贵人', '天乙贵人', '禄神', '福星', '生气',
                       '三合', '六合', '太阳到山', '太阴到山', '母仓',
                       '五行相生', '天地同流', '天干三朋', '旺相得令', '天德日', '月德日', '天赦']
        
        build_gods = ['天德贵人', '月德贵人', '天乙贵人', '禄神', '福星',
                      '三合局', '六合', '太阳到山', '太阴到山', '太阳到向', '太阴到向',
                      '天德日', '月德日', '天赦', '圣心', '解神', '天恩', '阴德', '母仓',
                      '五行相生', '天地同流', '天干三朋', '旺相得令', '将星', '帝光']
        
        movein_gods = ['天德贵人', '月德贵人', '天乙贵人', '禄神', '福星',
                        '三合局', '六合', '太阳到山', '太阴到山', '太阳到向', '太阴到向',
                        '天德日', '月德日', '天赦', '圣心', '解神', '天恩', '阴德', '母仓',
                        '五行相生', '天地同流', '天干三朋', '旺相得令', '将星', '帝光',
                        '三奇', '四相']
        
        digging_gods = ['天德贵人', '月德贵人', '天乙贵人', '禄神', '福星',
                        '三合局', '六合', '太阳到山', '太阴到山', '太阳到向', '太阴到向',
                        '天德日', '月德日', '天赦', '圣心', '解神', '天恩', '阴德', '母仓',
                        '五行相生', '天地同流', '天干三朋', '旺相得令', '将星', '三奇']
        
        demolition_gods = ['天德贵人', '月德贵人', '天乙贵人', '禄神', '福星',
                          '三合局', '六合', '太阳到山', '太阴到山',
                          '天德日', '月德日', '天赦', '圣心', '解神', '天恩', '阴德', '母仓',
                          '五行相生', '天地同流', '天干三朋', '旺相得令', '将星', '三奇']

        event_gods_map = {
            '嫁娶': ('嫁娶专用吉神', marriage_gods),
            '修造': ('修造专用吉神', build_gods),
            '动土': ('动土专用吉神', digging_gods),
            '拆舍': ('拆舍专用吉神', demolition_gods),
            '入宅': ('入宅专用吉神', movein_gods),
            '安葬': ('安葬专用吉神', burial_gods),
            '其他': ('通用吉神', common_gods)
        }

        self.jishen_vars = {}

        for event_key, (label, gods) in event_gods_map.items():
            event_frame = ttk.LabelFrame(jishen_frame, text=label)
            event_frame.pack(fill=tk.X, padx=5, pady=3)
            
            for god in gods:
                if god not in self.jishen_vars:
                    self.jishen_vars[god] = tk.BooleanVar(value=False)
            
            gods_list = list(gods)
            for i in range(0, len(gods_list), 5):
                row_frame = ttk.Frame(event_frame)
                row_frame.pack(fill=tk.X, pady=1)
                for god in gods_list[i:i+5]:
                    tk.Checkbutton(row_frame, text=god, variable=self.jishen_vars[god], indicatoron=True).pack(side=tk.LEFT, padx=3)
        
        # 黄道条件
        huangdao_frame = ttk.LabelFrame(main_frame, text="黄道条件")
        huangdao_frame.pack(fill=tk.X, pady=10)
        
        tk.Checkbutton(huangdao_frame, text="必须是黄道吉日", variable=self.condition_vars['must_have_huangdao'], indicatoron=True).pack(side=tk.LEFT, padx=5)
        
        # 排除凶日
        xiong_frame = ttk.LabelFrame(main_frame, text="排除条件")
        xiong_frame.pack(fill=tk.X, pady=10)

        tk.Checkbutton(xiong_frame, text="排除凶日（含'凶'字等级）", variable=self.condition_vars['exclude_xiong'], indicatoron=True).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(xiong_frame, text="排除有忌项的日课", variable=self.condition_vars['exclude_ji'], indicatoron=True).pack(side=tk.LEFT, padx=15)
        
        # 喜用神条件
        xishen_frame = ttk.LabelFrame(main_frame, text="喜用神条件")
        xishen_frame.pack(fill=tk.X, pady=10)
        
        tk.Checkbutton(xishen_frame, text="要求喜用神匹配", variable=self.condition_vars['include_xishen'], indicatoron=True).pack(side=tk.LEFT, padx=5)
        
        # 事主匹配条件
        owner_frame = ttk.LabelFrame(main_frame, text="事主匹配")
        owner_frame.pack(fill=tk.X, pady=10)

        tk.Checkbutton(owner_frame, text="要求事主八字匹配", variable=self.condition_vars['require_owner_match'], indicatoron=True).pack(side=tk.LEFT, padx=5)

        # 五行补龙/扶山要求
        longshan_frame = ttk.LabelFrame(main_frame, text="补龙扶山要求")
        longshan_frame.pack(fill=tk.X, pady=10)

        self.require_longshan = tk.BooleanVar(value=False)
        self.longshan_type = tk.StringVar(value="扶山")

        tk.Checkbutton(longshan_frame, text="要求日课五行与坐山相生或比和", variable=self.require_longshan, indicatoron=True).pack(anchor=tk.W, padx=5)

        type_frame = ttk.Frame(longshan_frame)
        type_frame.pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(type_frame, text="扶山（以坐山为主）", variable=self.longshan_type, value="扶山").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="补龙（以龙脉为主）", variable=self.longshan_type, value="补龙").pack(side=tk.LEFT, padx=5)

        # 避刑冲害事主生肖
        avoid_chong_frame = ttk.LabelFrame(main_frame, text="避刑冲害事主生肖")
        avoid_chong_frame.pack(fill=tk.X, pady=10)

        self.avoid_chong = tk.BooleanVar(value=True)
        self.avoid_xing = tk.BooleanVar(value=False)  # 新增：避刑
        self.avoid_hai = tk.BooleanVar(value=True)   # 新增：避害
        self.avoid_po = tk.BooleanVar(value=False)    # 新增：避破

        tk.Checkbutton(avoid_chong_frame, text="日支不与任何事主生肖相冲", variable=self.avoid_chong, indicatoron=True).pack(anchor=tk.W, padx=5)
        tk.Checkbutton(avoid_chong_frame, text="日支不与任何事主生肖相刑（含自刑）", variable=self.avoid_xing, indicatoron=True).pack(anchor=tk.W, padx=5)
        tk.Checkbutton(avoid_chong_frame, text="日支不与任何事主生肖相害", variable=self.avoid_hai, indicatoron=True).pack(anchor=tk.W, padx=5)
        tk.Checkbutton(avoid_chong_frame, text="日支不与任何事主生肖相破", variable=self.avoid_po, indicatoron=True).pack(anchor=tk.W, padx=5)

        # 三煞方条件
        sansha_frame = ttk.LabelFrame(main_frame, text="三煞方条件")
        sansha_frame.pack(fill=tk.X, pady=10)

        self.avoid_sansha = tk.BooleanVar(value=False)
        tk.Checkbutton(sansha_frame, text="日柱地支不在年月日三煞方", variable=self.avoid_sansha, indicatoron=True).pack(anchor=tk.W, padx=5)

        # 山家检查条件
        mountain_frame = ttk.LabelFrame(main_frame, text="山家检查条件（需选择山向）")
        mountain_frame.pack(fill=tk.X, pady=10)

        self.avoid_mountain_ji = tk.BooleanVar(value=False)
        tk.Checkbutton(mountain_frame, text="使用专业山家检查（冲山/岁煞/阴府/山方煞等）", variable=self.avoid_mountain_ji, indicatoron=True).pack(anchor=tk.W, padx=5)

        self.avoid_sui_po = tk.BooleanVar(value=False)
        tk.Checkbutton(mountain_frame, text="避岁破（日支冲坐山）", variable=self.avoid_sui_po, indicatoron=True).pack(anchor=tk.W, padx=5)

        self.avoid_yue_po = tk.BooleanVar(value=False)
        tk.Checkbutton(mountain_frame, text="避月破（月支冲坐山）", variable=self.avoid_yue_po, indicatoron=True).pack(anchor=tk.W, padx=5)

        # 时辰级过滤
        hour_filter_frame = ttk.LabelFrame(main_frame, text="时辰级过滤")
        hour_filter_frame.pack(fill=tk.X, pady=10)

        self.enable_hour_filter = tk.BooleanVar(value=False)
        tk.Checkbutton(hour_filter_frame, text="要求当日至少包含一个吉利时辰", variable=self.enable_hour_filter, indicatoron=True).pack(anchor=tk.W, padx=5)

        hour_types_frame = ttk.Frame(hour_filter_frame)
        hour_types_frame.pack(anchor=tk.W, padx=20, pady=5)

        self.hour_types = {
            "贵人时": tk.BooleanVar(value=False),
            "禄神时": tk.BooleanVar(value=False),
            "驿马时": tk.BooleanVar(value=False),
            "大黄道吉时": tk.BooleanVar(value=False),
            "小黄道吉时": tk.BooleanVar(value=False),
        }

        row1 = ttk.Frame(hour_types_frame)
        row1.pack(anchor=tk.W)
        for name in ["贵人时", "禄神时", "驿马时"]:
            tk.Checkbutton(row1, text=name, variable=self.hour_types[name], indicatoron=True).pack(side=tk.LEFT, padx=5)

        row2 = ttk.Frame(hour_types_frame)
        row2.pack(anchor=tk.W)
        for name in ["大黄道吉时", "小黄道吉时"]:
            tk.Checkbutton(row2, text=name, variable=self.hour_types[name], indicatoron=True).pack(side=tk.LEFT, padx=5)

        # 排除特定神煞
        exclude_shensha_frame = ttk.LabelFrame(main_frame, text="排除特定神煞")
        exclude_shensha_frame.pack(fill=tk.X, pady=10)

        self.exclude_shensha_vars = {}
        common_xiong = ["三煞", "岁破", "月破", "杨公忌", "四离", "四绝", "往亡", "红砂"]
        for i, shen in enumerate(common_xiong):
            var = tk.BooleanVar(value=False)
            self.exclude_shensha_vars[shen] = var
            cb = tk.Checkbutton(exclude_shensha_frame, text=shen, variable=var, indicatoron=True)
            cb.grid(row=i//4, column=i%4, sticky=tk.W, padx=10, pady=2)

        # 结果数量限制
        result_frame = ttk.LabelFrame(main_frame, text="结果限制")
        result_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(result_frame, text="最多显示：").pack(side=tk.LEFT, padx=5)
        max_results_spin = ttk.Spinbox(result_frame, from_=1, to=100, textvariable=self.condition_vars['max_results'], width=10)
        max_results_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(result_frame, text="个结果").pack(side=tk.LEFT, padx=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def apply_conditions():
            """应用条件并开始择日"""
            # 收集选中的吉神
            selected_jishen = []
            for name, var in self.jishen_vars.items():
                if var.get():
                    selected_jishen.append(name)

            # 收集选中的时辰类型
            selected_hours = [name for name, var in self.hour_types.items() if var.get()]

            # 收集选中的排除神煞
            excluded_shensha = [name for name, var in self.exclude_shensha_vars.items() if var.get()]

            conditions = {
                'min_score': self.condition_vars['min_score'].get(),
                'min_stars': self.condition_vars['min_stars'].get(),
                'must_have_jishen': selected_jishen,
                'must_have_huangdao': self.condition_vars['must_have_huangdao'].get(),
                'exclude_xiong': self.condition_vars['exclude_xiong'].get(),
                'exclude_ji': self.condition_vars['exclude_ji'].get(),
                'max_results': self.condition_vars['max_results'].get(),
                'include_xishen': self.condition_vars['include_xishen'].get(),
                'require_owner_match': self.condition_vars['require_owner_match'].get(),
                'require_longshan': self.require_longshan.get(),
                'longshan_type': self.longshan_type.get(),
                'avoid_chong': self.avoid_chong.get(),
                'avoid_xing': self.avoid_xing.get(),  # 新增
                'avoid_hai': self.avoid_hai.get(),    # 新增
                'avoid_po': self.avoid_po.get(),      # 新增：避破
                'avoid_sansha': self.avoid_sansha.get(),  # 新增：避三煞方
                'avoid_mountain_ji': self.avoid_mountain_ji.get(),  # 新增：专业山家检查
                'avoid_sui_po': self.avoid_sui_po.get(),  # 新增：避岁破
                'avoid_yue_po': self.avoid_yue_po.get(),  # 新增：避月破
                'enable_hour_filter': self.enable_hour_filter.get(),
                'hour_types': selected_hours,
                'exclude_shensha': excluded_shensha
            }
            condition_window.destroy()
            self._run_conditional_calculation(conditions)
        
        ttk.Button(button_frame, text="开始条件择日", command=apply_conditions, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=condition_window.destroy, width=15).pack(side=tk.LEFT, padx=10)
        
        condition_window.focus_force()
    
    def _run_conditional_calculation(self, conditions):
        """执行带条件的择日计算"""
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
            
            # 获取事主信息（同start_calculation）
            owners_data = []
            for owner in self.owners_info:
                try:
                    year_str = owner['year'].get() if hasattr(owner['year'], 'get') else owner.get('year', '')
                    month_str = owner['month'].get() if hasattr(owner['month'], 'get') else owner.get('month', '')
                    day_str = owner['day'].get() if hasattr(owner['day'], 'get') else owner.get('day', '')
                    
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
                    
                    try:
                        birth_date = date(year, month, day)
                    except ValueError:
                        import calendar
                        last_day = calendar.monthrange(year, month)[1]
                        birth_date = date(year, month, last_day)

                    # 真太阳时 §48：事主经度透传（扫日回路不弹窗，入口已警告）
                    birth_longitude = _parse_owner_longitude(owner.get('longitude'), show_warning=False)
                    owner_sizhu = calculate_sizhu(birth_date, hour, minute, longitude=birth_longitude)
                    year_gan = owner_sizhu.get('year_gan', '')
                    year_zhi = owner_sizhu.get('year_zhi', '')
                    day_gan = owner_sizhu.get('day_gan', '')
                    day_zhi = owner_sizhu.get('day_zhi', '')
                    
                    name = owner['name'].get() if hasattr(owner['name'], 'get') else owner.get('name', '')
                    owner_data = {
                        'name': name,
                        'role': owner.get('role', ''),
                        'birth_date': birth_date,
                        'birth_hour': hour,
                        'birth_minute': minute,
                        'birth_longitude': birth_longitude,
                        '性别': gender,
                        '年干': year_gan,
                        '年支': year_zhi,
                        '日干': day_gan,
                        '日支': day_zhi,
                        '生肖': year_zhi
                    }
                    
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
            # 安葬无墓穴坐山不予计算（_azss0914）
            if not self._require_shan_for_burial(event_type):
                return
            if event_type == '作灶':
                # 2026-09 作灶主事人模式：给打包后的事主打主次/权重标记
                self._tag_zaozhu_owners(owners_data)
            house_type = getattr(self, 'house_type', None)
            house_type = house_type.get() if house_type else None
            shan_xiang = getattr(self, 'shan_xiang', None)
            shan_xiang = shan_xiang.get() if shan_xiang else None
            
            jian_xiang = getattr(self, 'jian_xiang', None)
            jian_xiang_value = jian_xiang.get() if jian_xiang else None
            if shan_xiang and jian_xiang_value and jian_xiang_value != "正中":
                # §59.13 批次一提醒3：提交前校验——非法兼向弹窗提示，不阻断
                # （引擎按正向处理并记日志）
                self._warn_invalid_jianxiang_before_submit(jian_xiang_value)
                # §59.13：手动裸值"亥"规范化为"兼亥"，保证拼接串可被引擎解析
                _jx_v = jian_xiang_value.strip()
                if not _jx_v.startswith('兼'):
                    _jx_v = '兼' + _jx_v
                shan_xiang = f"{shan_xiang}{_jx_v}"
            
            zao_xiang = getattr(self, 'zao_xiang', None)
            zao_xiang = zao_xiang.get() if zao_xiang else None
            zao_wei = getattr(self, 'zao_wei', None)
            zao_wei = zao_wei.get() if zao_wei else None
            chuang_wei = getattr(self, 'chuang_wei', None)
            chuang_wei = chuang_wei.get() if chuang_wei else None

            # 2026-09 作灶主事人模式（非作灶事项为 None，引擎口径不变）
            zaozhu_mode = getattr(self, 'zaozhu_mode', None)
            zaozhu_mode = zaozhu_mode.get() if hasattr(zaozhu_mode, 'get') else None
            
            print(f"[条件择日] 事项类型: {event_type}, 山向: {shan_xiang}, 条件: {conditions}")
            
            # 计算每日吉凶（带条件过滤）
            current = start
            while current <= end and len(self.results) < conditions['max_results']:
                sizhu = calculate_sizhu(current, 12, 0)
                sizhu['year'] = current.year
                sizhu['month'] = current.month
                sizhu['day'] = current.day
                sizhu['date'] = current
                
                try:
                    lunar = get_lunar_date(current)
                    lunar_str = f"{lunar['month']}{lunar['day']}"
                except:
                    lunar_str = "-"
                
                score_result = calculate_score(
                    sizhu,
                    event_type,
                    owners_data,
                    house_type,
                    shan_xiang,
                    zao_xiang,
                    zao_wei,
                    chuang_wei,
                    zaozhu_mode=zaozhu_mode,
                    zeli_mode=self._get_zeli_mode()  # _zm0915
                )

                # 规则3（2026-09-03 用户放宽）：午时基准被否决≠整日淘汰，遍历12时辰选最佳
                # 2026-09-16 口径统一：正常/条件择日共用 ZeriApp._rescan_best_hour。
                sizhu, score_result = self._rescan_best_hour(
                    current, event_type, owners_data, house_type,
                    shan_xiang, zao_xiang, zao_wei, chuang_wei,
                    zaozhu_mode, sizhu, score_result)

                score = score_result.get('score', 0)
                level = score_result.get('level', '')
                
                # 条件检查
                pass_conditions = True
                
                # 1. 最低评分条件
                if score < conditions['min_score']:
                    pass_conditions = False
                
                # 2. 最低星级条件
                star_count = level.count('★')
                if star_count < conditions['min_stars']:
                    pass_conditions = False
                
                # 3. 排除凶日条件
                if conditions['exclude_xiong'] and '凶' in level:
                    pass_conditions = False

                # 3.1 排除有忌项的日课
                if conditions['exclude_ji']:
                    ji_list = score_result.get('ji_list', [])
                    yi_ji_info = score_result.get('yi_ji_info', {})
                    # 检查忌项列表中是否包含当前事项类型
                    for ji in ji_list:
                        ji_text = str(ji)
                        # 匹配"忌嫁娶"或"忌 嫁娶"或列表中的"嫁娶"
                        if event_type in ji_text or re.search(rf'忌\s*{re.escape(event_type)}', ji_text):
                            pass_conditions = False
                            break
                    # 也检查综合评语中的忌项
                    if pass_conditions:
                        reason = score_result.get('reason', '')
                        if '忌：' in reason or '忌:' in reason:
                            # 提取忌项部分进行检查
                            if '忌：' in reason:
                                ji_part = reason.split('忌：')[1].split('；')[0] if '；' in reason.split('忌：')[1] else reason.split('忌：')[1]
                            else:
                                ji_part = reason.split('忌:')[1].split('；')[0] if '；' in reason.split('忌:')[1] else reason.split('忌:')[1]
                            if event_type in ji_part:
                                pass_conditions = False
                
                # 4. 吉神条件
                if conditions['must_have_jishen']:
                    selected_items = conditions['must_have_jishen']
                    wu_xing_result = score_result.get('wu_xing_result', {})
                    wu_xing_details = wu_xing_result.get('details', {})
                    jishen_list = wu_xing_details.get('吉神', [])
                    dizhi_relations = wu_xing_details.get('地支关系', [])
                    sun_moon_info = score_result.get('sun_moon_info', {})

                    # 检查是否满足所有选中的吉神/格局条件
                    missing_items = []
                    for item in selected_items:
                        found = False
                        # 检查吉神
                        if item in ['天德贵人', '月德贵人', '天乙贵人', '文昌贵人', '禄神', '福星']:
                            found = any(item in str(j) for j in jishen_list)
                        # 检查三合局
                        elif item == '三合局':
                            found = any('三合' in str(r) for r in dizhi_relations)
                        # 检查六合
                        elif item == '六合':
                            found = any('六合' in str(r) for r in dizhi_relations)
                        # 检查太阳到山
                        elif item == '太阳到山':
                            if sun_moon_info.get('sun_to_mountain'):
                                found = True
                            reason = score_result.get('reason', '')
                            if '太阳到山' in reason:
                                found = True
                        # 检查太阴到山
                        elif item == '太阴到山':
                            if sun_moon_info.get('moon_to_mountain'):
                                found = True
                            reason = score_result.get('reason', '')
                            if '太阴到山' in reason:
                                found = True
                        # 检查太阳到向
                        elif item == '太阳到向':
                            if sun_moon_info.get('sun_to_direction'):
                                found = True
                            reason = score_result.get('reason', '')
                            if '太阳到向' in reason:
                                found = True
                        # 检查太阴到向
                        elif item == '太阴到向':
                            if sun_moon_info.get('moon_to_direction'):
                                found = True
                            reason = score_result.get('reason', '')
                            if '太阴到向' in reason:
                                found = True
                        # 检查嫁娶及其他专用吉神 - 在神煞列表或评语中查找
                        elif item in ['不将日', '周堂吉日', '天德日', '月德日', '六合', 
                                      '五合日', '王日', '天喜', '红鸾', '生气', '圣心', 
                                      '解神', '天恩', '阴德', '续世', '复日', '天德', '月德', '天赦', '母仓', '三合',
                                      '大利月', '小利月', '五行相生', '天地同流', '天干三朋', '旺相得令',
                                      '三奇', '将星', '帝光']:
                            # 在多个地方查找
                            jishen_str = str(jishen_list)
                            dizhi_str = str(dizhi_relations)
                            shensha_str = str(score_result.get('shensha', {}))
                            reason = score_result.get('reason', '')
                            found = (item in jishen_str or item in shensha_str or 
                                    item in reason or item in dizhi_str)
                            # 五行相生需要特殊检查：看五行生克关系中是否有相生
                            if item == '五行相生' and not found:
                                wu_xing_result = score_result.get('wu_xing_result', {})
                                wu_xing_details = wu_xing_result.get('details', {})
                                wuxing_info = wu_xing_details.get('五行生克', [])
                                # 检查是否有相生关系（木生火、火生土、土生金、金生水、水生木）
                                sheng_patterns = ['木生火', '火生土', '土生金', '金生水', '水生木']
                                for relation in wuxing_info:
                                    if any(pattern in str(relation) for pattern in sheng_patterns):
                                        found = True
                                        break
                            # 天地同流：年月柱天干地支相同或相生
                            if item == '天地同流' and not found:
                                wu_xing_result = score_result.get('wu_xing_result', {})
                                wu_xing_details = wu_xing_result.get('details', {})
                                dizhi_relations = wu_xing_details.get('地支关系', [])
                                # 检查是否有天合地合或天地同流格局
                                found = any('六合' in str(r) or '三合' in str(r) for r in dizhi_relations)
                            # 天干三朋：三个相同天干
                            if item == '天干三朋' and not found:
                                wu_xing_result = score_result.get('wu_xing_result', {})
                                wu_xing_details = wu_xing_result.get('details', {})
                                tian_gan_info = wu_xing_details.get('天干五行', [])
                                gan_counts = {}
                                for gan in tian_gan_info:
                                    gan_char = str(gan)[:1] if isinstance(gan, str) else ''
                                    if gan_char in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
                                        gan_counts[gan_char] = gan_counts.get(gan_char, 0) + 1
                                found = any(count >= 3 for count in gan_counts.values())
                            # 旺相得令：日主得令或月支生扶日主
                            if item == '旺相得令' and not found:
                                wu_xing_result = score_result.get('wu_xing_result', {})
                                wu_xing_details = wu_xing_result.get('details', {})
                                zhuwang_info = wu_xing_details.get('日主旺衰', '')
                                # 检查日主是否得令或得地
                                found = ('得令' in zhuwang_info or '得地' in zhuwang_info or '身强' in zhuwang_info)
                            # 四相：四柱中有天干五行与月令五行相同
                            if item == '四相' and not found:
                                sizhu = score_result.get('sizhu', {})
                                year_gan = sizhu.get('year_gan', '')
                                month_gan = sizhu.get('month_gan', '')
                                day_gan = sizhu.get('day_gan', '')
                                hour_gan = sizhu.get('hour_gan', '')
                                gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火',
                                              '戊': '土', '己': '土', '庚': '金', '辛': '金',
                                              '壬': '水', '癸': '水'}
                                month_wuxing = {'寅': '木', '卯': '木', '辰': '土', '巳': '火',
                                                '午': '火', '未': '土', '申': '金', '酉': '金',
                                                '戌': '土', '亥': '水', '子': '水', '丑': '土'}
                                month_zhi = sizhu.get('month_zhi', '')
                                if month_zhi in month_wuxing:
                                    mw = month_wuxing[month_zhi]
                                    found = any(gan_wuxing.get(g, '') == mw for g in [year_gan, month_gan, day_gan, hour_gan])

                        if not found:
                            missing_items.append(item)

                    if missing_items:
                        pass_conditions = False
                
                # 5. 黄道条件
                if conditions['must_have_huangdao']:
                    huangdao_info = score_result.get('huangdao_info', {})
                    da_hd = huangdao_info.get('da_huang_dao', {})
                    if da_hd.get('type') != '吉':
                        pass_conditions = False
                
                # 6. 喜用神条件
                if conditions['include_xishen']:
                    score_details = score_result.get('score_details', {})
                    xishen_score = score_details.get('喜用神得分', 0)
                    if xishen_score <= 0:
                        pass_conditions = False

                # 7. 五行补龙/扶山条件（检查四柱生扶力量）
                if conditions.get('require_longshan', False):
                    shan_xiang = getattr(self, 'shan_xiang', None)
                    shan_val = shan_xiang.get() if shan_xiang else None

                    shan_wuxing = {
                        '壬': '水', '子': '水', '癸': '水',
                        '丑': '土', '艮': '土', '寅': '木',
                        '甲': '木', '卯': '木', '乙': '木',
                        '辰': '土', '巽': '木', '巳': '火',
                        '丙': '火', '午': '火', '丁': '火',
                        '未': '土', '坤': '土', '申': '金',
                        '庚': '金', '酉': '金', '辛': '金',
                        '戌': '土', '乾': '金', '亥': '水',
                    }
                    sheng_map = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
                    ke_map = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

                    if shan_val:
                        mountain = shan_val.split('山')[0] if '山' in shan_val else shan_val
                        shan_wx = shan_wuxing.get(mountain)
                        if shan_wx:
                            # 统计四柱中生扶/克制坐山的干支数量
                            support_count = 0
                            attack_count = 0
                            pillar_keys = [('年柱', '年_gan', '年_zhi'),
                                          ('月柱', '月_gan', '月_zhi'),
                                          ('日柱', '日_gan', '日_zhi'),
                                          ('时柱', '时_gan', '时_zhi')]
                            for col_name, gan_key, zhi_key in pillar_keys:
                                gan = sizhu.get(gan_key, '')
                                zhi = sizhu.get(zhi_key, '')
                                if gan:
                                    gan_wx = TIAN_GAN_WUXING.get(gan, '')
                                    if gan_wx == shan_wx or sheng_map.get(gan_wx) == shan_wx:
                                        support_count += 1
                                    elif ke_map.get(gan_wx) == shan_wx or sheng_map.get(shan_wx) == gan_wx:
                                        attack_count += 1
                                if zhi:
                                    zhi_wx = DI_ZHI_WUXING.get(zhi, '')
                                    if zhi_wx == shan_wx or sheng_map.get(zhi_wx) == shan_wx:
                                        support_count += 1
                                    elif ke_map.get(zhi_wx) == shan_wx or sheng_map.get(shan_wx) == zhi_wx:
                                        attack_count += 1
                            if support_count <= attack_count:
                                pass_conditions = False

                # 8. 避刑冲害破事主生肖
                if owners_data and (conditions.get('avoid_chong') or conditions.get('avoid_xing') or conditions.get('avoid_hai') or conditions.get('avoid_po')):
                    day_zhu_str = sizhu.get('日柱', '')
                    day_zhi = day_zhu_str[1] if len(day_zhu_str) >= 2 else ''
                    
                    # 六冲表
                    chong_map = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                                 '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                                 '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
                    
                    # 三刑表（包括自刑）
                    xing_pairs = [
                        ('寅', '巳'), ('巳', '申'), ('申', '寅'),  # 恩刑
                        ('丑', '戌'), ('戌', '未'), ('未', '丑'),  # 恩刑
                        ('子', '卯'), ('卯', '子'),  # 无礼刑
                        ('辰', '辰'), ('午', '午'), ('酉', '酉'), ('亥', '亥')  # 自刑
                    ]
                    
                    # 六害表
                    hai_map = {'子': '未', '未': '子', '丑': '午', '午': '丑',
                               '寅': '巳', '巳': '寅', '卯': '辰', '辰': '卯',
                               '申': '亥', '亥': '申', '酉': '戌', '戌': '酉'}
                    
                    # 相破表（十二地支相破）
                    po_pairs = [
                        ('子', '酉'), ('酉', '子'), ('丑', '辰'), ('辰', '丑'),
                        ('寅', '亥'), ('亥', '寅'), ('卯', '午'), ('午', '卯'),
                        ('巳', '申'), ('申', '巳'), ('未', '戌'), ('戌', '未')
                        # 2026-09 修正：六破仅子酉/丑辰/寅亥/卯午/巳申/未戌六对，
                        # 戌亥不在其列（无刑冲合害破关系），删去旧补的戌亥相破
                    ]
                    
                    for owner in owners_data:
                        owner_zhi = owner.get('生肖') or owner.get('年支')
                        if not owner_zhi:
                            continue
                        
                        # 检查相冲
                        if conditions.get('avoid_chong', False):
                            if chong_map.get(day_zhi) == owner_zhi:
                                pass_conditions = False
                                break
                        
                        # 检查相刑（包括自刑）
                        if conditions.get('avoid_xing', False):
                            if (day_zhi, owner_zhi) in xing_pairs or (owner_zhi, day_zhi) in xing_pairs:
                                pass_conditions = False
                                break
                        
                        # 检查相害
                        if conditions.get('avoid_hai', False):
                            if hai_map.get(day_zhi) == owner_zhi:
                                pass_conditions = False
                                break
                        
                        # 检查相破
                        if conditions.get('avoid_po', False):
                            if (day_zhi, owner_zhi) in po_pairs or (owner_zhi, day_zhi) in po_pairs:
                                pass_conditions = False
                                break

                # 9. 避三煞方
                if conditions.get('avoid_sansha', False):
                    day_zhu_str = sizhu.get('日柱', '')
                    day_zhi = day_zhu_str[1] if len(day_zhu_str) >= 2 else ''
                    year_zhi = sizhu.get('year_zhi', '')
                    month_zhi = sizhu.get('month_zhi', '')
                    
                    # 三煞方位映射表（纯地支，符合三合局规则）
                    sansha_map = {
                        '申': ['巳', '午', '未'], '子': ['巳', '午', '未'], '辰': ['巳', '午', '未'],
                        '寅': ['亥', '子', '丑'], '午': ['亥', '子', '丑'], '戌': ['亥', '子', '丑'],
                        '巳': ['寅', '卯', '辰'], '酉': ['寅', '卯', '辰'], '丑': ['寅', '卯', '辰'],
                        '亥': ['申', '酉', '戌'], '卯': ['申', '酉', '戌'], '未': ['申', '酉', '戌']
                    }
                    
                    year_sansha = sansha_map.get(year_zhi, [])
                    month_sansha = sansha_map.get(month_zhi, [])
                    day_sansha = sansha_map.get(day_zhi, [])
                    
                    # 检查日柱地支是否在年、月、日三煞方
                    if day_zhi in year_sansha or day_zhi in month_sansha or day_zhi in day_sansha:
                        pass_conditions = False

                # 9. 山家专业检查（使用二十四山择吉天机模块）
                if conditions.get('avoid_mountain_ji', False):
                    shan_xiang = getattr(self, 'shan_xiang', None)
                    shan_val = shan_xiang.get() if shan_xiang else None
                    if shan_val:
                        jian_xiang_val = getattr(self, 'jian_xiang', None)
                        jian_val = jian_xiang_val.get() if jian_xiang_val else None
                        if jian_val and jian_val != "正中":
                            shan_val = f"{shan_val}{jian_val}"
                        
                        date_info = {
                            'year_gan': sizhu.get('year_gan', ''),
                            'year_zhi': sizhu.get('year_zhi', ''),
                            'month_gan': sizhu.get('month_gan', ''),
                            'month_zhi': sizhu.get('month_zhi', ''),
                            'day_gan': sizhu.get('day_gan', ''),
                            'day_zhi': sizhu.get('day_zhi', ''),
                            'hour_gan': sizhu.get('hour_gan', ''),
                            'hour_zhi': sizhu.get('hour_zhi', ''),
                            'year': sizhu.get('year', ''),  # 公历年份（用于年家五黄紫白飞星）
                        }
                        
                        event_type = self.event_var.get()
                        mountain_result = check_mountain_day(date_info, shan_val, event_type)
                        if not mountain_result.get('可用', True):
                            _cm_reasons = [_x for _x in mountain_result.get('凶煞', [])
                                           if not any(_k in str(_x) for _k in ('五黄', '二黑', '紫白'))]
                            if self._get_zeli_mode() == 'feixing' or _cm_reasons:  # _zm0915
                                pass_conditions = False

                # 10. 避岁破（日支冲坐山）
                if conditions.get('avoid_sui_po', False):
                    shan_xiang = getattr(self, 'shan_xiang', None)
                    shan_val = shan_xiang.get() if shan_xiang else None
                    if shan_val:
                        day_zhi = sizhu.get('day_zhi', '')
                        if day_zhi and check_chong_shan(shan_val, day_zhi):
                            pass_conditions = False

                # 11. 避月破（月支冲坐山）
                if conditions.get('avoid_yue_po', False):
                    shan_xiang = getattr(self, 'shan_xiang', None)
                    shan_val = shan_xiang.get() if shan_xiang else None
                    if shan_val:
                        month_zhi = sizhu.get('month_zhi', '')
                        if month_zhi and check_chong_shan(shan_val, month_zhi):
                            pass_conditions = False

                # 12. 时辰级过滤
                if conditions.get('enable_hour_filter', False) and conditions.get('hour_types'):
                    required_hour_types = conditions['hour_types']
                    found_hour = False
                    huangdao_calc = 黄道计算器()
                    day_zhi_for_hour = sizhu.get('日柱', ['', ''])[1] if sizhu.get('日柱') else ''
                    day_gan_for_hour = sizhu.get('日柱', ['', ''])[0] if sizhu.get('日柱') else ''
                    month_zhi_for_hour = sizhu.get('月柱', ['', ''])[1] if sizhu.get('月柱') else ''

                    # 小黄道按日计算（非随时辰变化），预计算一次
                    xiao_hd_info = huangdao_calc._calculate_xiao_huang_dao(month_zhi_for_hour, day_zhi_for_hour) if month_zhi_for_hour and day_zhi_for_hour else None

                    for h in range(0, 24, 2):
                        hour_sizhu = calculate_sizhu(current, h, 0)
                        hour_gan = hour_sizhu.get('时柱', ['', ''])[0] if hour_sizhu.get('时柱') else ''
                        hour_zhi = hour_sizhu.get('时柱', ['', ''])[1] if hour_sizhu.get('时柱') else ''

                        for hour_type in required_hour_types:
                            if hour_type == "贵人时":
                                # 天乙贵人：以日干查贵人时支
                                tianyi_guiRen = {
                                    '甲': ['丑', '未'], '戊': ['丑', '未'],
                                    '乙': ['子', '申'], '己': ['子', '申'],
                                    '丙': ['亥', '酉'], '丁': ['亥', '酉'],
                                    '庚': ['丑', '未'], '辛': ['寅', '午'],
                                    '壬': ['卯', '巳'], '癸': ['卯', '巳']
                                }
                                gui_ren_zhi = tianyi_guiRen.get(day_gan_for_hour, [])
                                if hour_zhi in gui_ren_zhi:
                                    found_hour = True
                                    break
                            elif hour_type == "禄神时":
                                gan_zhi_map = {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
                                               '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'}
                                if gan_zhi_map.get(day_gan_for_hour) == hour_zhi:
                                    found_hour = True
                                    break
                            elif hour_type == "驿马时":
                                yima_map = {'申': '寅', '子': '寅', '辰': '寅',
                                            '亥': '巳', '卯': '巳', '未': '巳',
                                            '寅': '申', '午': '申', '戌': '申',
                                            '巳': '亥', '酉': '亥', '丑': '亥'}
                                if yima_map.get(day_zhi_for_hour) == hour_zhi:
                                    found_hour = True
                                    break
                            elif hour_type == "大黄道吉时":
                                # J1（2026-09-30）只修名实：改调时辰级接口，按
                                # 日支+时支查《协纪》时辰十二神；旧 _calculate_da_huang_dao
                                # 为值日级（忽略时支），"吉时筛选"名实不符。
                                # 局限：时辰表 DA_HUANG_DAO_TABLE 起例值待 J2 按《协纪》
                                # 典据校正——J1 不改表值，只让筛选真正按时支走表。
                                if day_zhi_for_hour and hour_zhi:
                                    da_result = huangdao_calc._calculate_da_huangdao_shichen(
                                        day_zhi_for_hour, hour_zhi)
                                    if da_result.get('type') == '吉':
                                        found_hour = True
                                        break
                            elif hour_type == "小黄道吉时":
                                # 小黄道为日级属性，预计算一次
                                if xiao_hd_info and xiao_hd_info.get('type') == '吉':
                                    found_hour = True
                                    break
                        if found_hour:
                            break
                    if not found_hour:
                        pass_conditions = False

                # 10. 排除特定神煞
                if conditions.get('exclude_shensha'):
                    shensha_list = score_result.get('shensha_list', [])
                    shensha_text = ' '.join([str(s) for s in shensha_list])
                    for shen in conditions['exclude_shensha']:
                        if shen in shensha_text:
                            pass_conditions = False
                            break

                if pass_conditions:
                    # 构建结果（同start_calculation）
                    score_details = score_result.get('score_details', {})
                    wuxing_score = score_details.get('五行评分', 100)
                    yueling_score = score_details.get('月令得分', 0)
                    xishen_score = score_details.get('喜用神得分', 0)
                    huangdao_score = score_details.get('黄道得分', 0)
                    
                    # 地支关系/吉神两列文本（统一入口；注入推荐时柱后会再次刷新）
                    dizhi_text, jishen_text = _extract_tree_dizhi_jishen(score_result)
                    
                    result = {
                        'date': current.strftime("%Y-%m-%d"),
                        'lunar': lunar_str,
                        'score': score,
                        'level': level,
                        'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                        'wuxing_score': wuxing_score,
                        'yueling_score': yueling_score,
                        'xishen_score': xishen_score,
                        'huangdao_score': huangdao_score,
                        'dizhi_relation': dizhi_text,
                        'jishen': jishen_text,
                        'feixing': _fmt_feixing(score_result.get('feixing_info')),
                        'owners_info': getattr(self, 'owners_info', []),
                        'zaozhu_mode': zaozhu_mode,
                        'detail': score_result
                    }
                    # ── 把显示用时柱从"午时示例"替换为"事项专属最佳吉时" ──
                    self._inject_best_hour_to_result(
                        result, score_result, event_type, owners_data, current, sizhu,
                        house_type=house_type, shan_xiang=shan_xiang, zao_xiang=zao_xiang,
                        zao_wei=zao_wei, chuang_wei=chuang_wei
                    )
                    # 2026-09-05 用户确认：结果表“地支关系/吉神”两列须反映真实推荐时辰
                    # 参与的关系——上面注入推荐时柱后，第(5)步已用权威四柱重算 details，
                    # 这里随之刷新，避免仍显示基准午时的地支关系误导用户
                    try:
                        _dz_txt, _js_txt = _extract_tree_dizhi_jishen(score_result)
                        result['dizhi_relation'] = _dz_txt
                        result['jishen'] = _js_txt
                    except Exception:
                        pass

                    self.results.append(result)
                    print(f"[条件择日] 通过: {current}, score={score}, level={level}")
                
                current += timedelta(days=1)
            
            # 统一渲染结果表（排序/列标题/12列构造；与正常择日链路共用同一方法）
            self._render_result_tree()

            self.save_record()
            
            self._maybe_save_owners_on_finish(f"条件择日完成！\n共找到 {len(self.results)} 个符合条件的吉日")
            
        except Exception as e:
            messagebox.showerror("错误", f"计算出错：{str(e)}")
    
    def on_result_double_click(self, event):
        """双击结果查看详情"""
        # 双击时取消左键单击的玄空提示，避免弹窗干扰详情
        if getattr(self, '_xk_after', None):
            try:
                self.root.after_cancel(self._xk_after)
            except Exception:
                pass
            self._xk_after = None
        selected = self.result_tree.selection()
        if not selected:
            return
        
        item = self.result_tree.item(selected[0])
        values = item['values']
        
        # 查找完整结果 - 首列"日期/四柱"为两行文本（2026-09-03起）：第一行日期，第二行四柱
        date_cell = str(values[0] or '') if values else ''
        cell_lines = [ln.strip() for ln in date_cell.splitlines() if ln.strip()]
        date_str = cell_lines[0] if cell_lines else ''
        result = None
        for r in self.results:
            if r.get('date', '') == date_str:
                result = r
                break

        if not result:
            return

        # ── 统一日课详情 & 择日贴的四柱（以结果表首列第二行为"权威四柱"）──
        # 避免：头段/八字段/择日贴 三处显示不同的时柱
        auth_sizhu = ''
        try:
            if len(cell_lines) >= 2:
                pp = cell_lines[1].split()
                if len(pp) == 4 and all(len(p) >= 2 for p in pp):
                    auth_sizhu = ' '.join(pp)
        except Exception:
            auth_sizhu = ''
        # 兜底：旧格式/导入记录首列无第二行时，用结果字典自带四柱
        if not auth_sizhu:
            s = str(result.get('sizhu', '') or '').strip()
            pp = s.split()
            if len(pp) == 4 and all(len(p) >= 2 for p in pp):
                auth_sizhu = ' '.join(pp)
        # 扫日阶段是否已权威注入推荐时柱（_inject_best_hour 成功会在 detail 上设 _auth_sizhu）。
        # 若是，双击详情不再重新选时——旧的"详情预计算选时"会改写 detail['sizhu']，却只让
        # 【五行分析】段实时重算，而【时柱关系分】【综合评语】仍读扫日缓存，两次选时一旦不同
        # （如入宅：扫日按坐山选辛亥、详情兜底表选乙巳）就出现"巳/亥混合"矛盾。扫日注入已是
        # 完整评分器权威结果（含飞星/分金复核），详情直接沿用，保证单一数据源。
        _det = result.get('detail')
        _scan_injected = bool(_det.get('_auth_sizhu')) if isinstance(_det, dict) else False
        # 1) 权威字符串覆盖到头段使用的 result['sizhu']
        if auth_sizhu:
            result['sizhu'] = auth_sizhu
            # 2) 同步覆盖 detail['sizhu']（字典形式：给【四柱八字】段落使用）
            try:
                detail_ref = result.get('detail')
                if isinstance(detail_ref, dict):
                    parts4 = auth_sizhu.split()
                    # 2026-09-17 修复 Bug5（位置1）：原写法整体替换 detail_ref['sizhu']
                    #   丢失 'date'/'year'/'month'/'day' 等键，导致神煞扩展按高精度
                    #   农历取月用 detail['sizhu'].get('date') 落空。改为保留旧键。
                    _old = detail_ref.get('sizhu') or {}
                    _new = dict(_old) if isinstance(_old, dict) else {}
                    _new.update({
                        '年柱': parts4[0],
                        '月柱': parts4[1],
                        '日柱': parts4[2],
                        '时柱': parts4[3],
                    })
                    detail_ref['sizhu'] = _new
                    # 额外保存权威来源，给【四柱八字】段用
                    detail_ref['_auth_sizhu'] = True
            except Exception:
                pass
        
        # 显示详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"日课详情 - {date_str}")
        detail_window.geometry("760x680")
        
        # 创建主框架
        main_frame = ttk.Frame(detail_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文本显示区域（整体字号放大两级）
        _BASE_FONT = ("微软雅黑", 13)
        text = scrolledtext.ScrolledText(main_frame, wrap=tk.CHAR, padx=10, pady=10,
                                         font=_BASE_FONT)
        text.pack(fill=tk.BOTH, expand=True)
        
        # 金色星星/红色叉号 同步放大两级（原11→15）
        text.tag_configure("gold_star", foreground="#FFD700",
                           font=("微软雅黑", 15, "bold"))
        text.tag_configure("red_cross", foreground="#FF0000",
                           font=("微软雅黑", 15, "bold"))
        # ⚠ 警告图标金色前景（仅图标着色，不充填底色）
        text.tag_configure("warn_icon", foreground="#FFD700")
        
        detail = result['detail']
        # 2026-09-06 修正：权威四柱覆盖块重建 detail['sizhu'] 时会丢 'date' 键，
        # 利月分析取不到日期便回退节气月支法（寅=正月），把腊月十八误判成“大利月（+30分，农历1月）”。
        # 此处补 detail['date'] 兜底（'YYYY-MM-DD' 字符串可被下方解析），保证按高精度农历取月。
        try:
            if isinstance(detail, dict) and not detail.get('date'):
                _d_raw = result.get('date') or date_str
                if hasattr(_d_raw, 'year'):
                    detail['date'] = _d_raw
                elif isinstance(_d_raw, str) and len(_d_raw) >= 10:
                    try:
                        from datetime import datetime as _dt
                        detail['date'] = _dt.strptime(_d_raw[:10], '%Y-%m-%d').date()
                    except Exception:
                        detail['date'] = _d_raw
                else:
                    detail['date'] = _d_raw
        except Exception:
            pass
        
        # 提取大利月/小利月信息
        daliyue_info = result.get('daliyue', '-')
        event_type = self.event_var.get()

        # =====================================================================
        # 【推荐时柱预计算】：与详情【十二时辰xx吉凶】同源，避免全部显示午时
        #  扫日阶段 result['sizhu'] 为午时柱（评分基准），此处按事项专属 checker
        #  计算当日最佳吉时 → 重算时柱 → 统一同步到 3 处数据源：
        #    (1) result['sizhu']             → 日课详情头段"四柱：xxxx"
        #    (2) result['detail']['sizhu']   → 【四柱八字】段逐柱解析
        #    (3) 结果表首列第二行（日期/四柱合并列）& 择日贴打包干支
        # =====================================================================
        _ZHI_START = {'子':23,'丑':1,'寅':3,'卯':5,'辰':7,'巳':9,'午':11,'未':13,
                      '申':15,'酉':17,'戌':19,'亥':21}
        try:
            from datetime import date as _date
            from modules.四柱计算器 import calculate_sizhu as _calc_sz

            detail_ref = result.get('detail') if isinstance(result.get('detail'), dict) else {}
            sz_map = detail_ref.get('sizhu') if isinstance(detail_ref.get('sizhu'), dict) else {}
            nian_gz = sz_map.get('年柱', '') or ''
            yue_gz  = sz_map.get('月柱', '') or ''
            ri_gz   = sz_map.get('日柱', '') or ''
            shi_gz  = sz_map.get('时柱', '') or ''

            # 扫日已权威注入推荐时柱时，跳过双击重选（单一数据源，避免巳/亥混合）；
            # 仅扫日未注入（导入旧记录/择日贴/午时基准）时才在此兜底选吉时。
            if all(len(x) == 2 for x in (nian_gz, yue_gz, ri_gz)) and not _scan_injected:
                ds = {
                    'year_gan'  : nian_gz[0], 'year_zhi'  : nian_gz[1],
                    'month_gan' : yue_gz[0],  'month_zhi' : yue_gz[1],
                    'day_gan'   : ri_gz[0],   'day_zhi'   : ri_gz[1],
                    'hour_gan'  : (shi_gz[0] if len(shi_gz) == 2 else ''),
                    'hour_zhi'  : (shi_gz[1] if len(shi_gz) == 2 else ''),
                }
                # 权威推荐时柱（单一数据源 modules.推荐时柱）——未注入兜底也走同一函数，
                # 修造带坐山/主命、婚姻带新郎新娘、其它通用，禁止本块再各自构造 checker。
                from modules.推荐时柱 import resolve_recommended_hour
                def _gv2(oi, k):
                    if not isinstance(oi, dict):
                        return None
                    v = oi.get(k)
                    return v.get() if hasattr(v, 'get') else v
                _owners_std = []
                try:
                    for oi in getattr(self, 'owners_info', []) or []:
                        od = {'gender': _gv2(oi, 'gender') or '', 'role': _gv2(oi, 'role') or ''}
                        try:
                            od['birth_date'] = _date(int(_gv2(oi, 'year')),
                                                     int(_gv2(oi, 'month')),
                                                     int(_gv2(oi, 'day')))
                            od['birth_hour'] = int(_gv2(oi, 'hour') or 12)
                            od['birth_minute'] = int(_gv2(oi, 'minute') or 0)
                            od['birth_longitude'] = _parse_owner_longitude(oi.get('longitude'), show_warning=False)
                        except Exception:
                            pass
                        _owners_std.append(od)
                except Exception:
                    _owners_std = []
                _sx3 = getattr(self, 'shan_xiang', None)
                _sxstr3 = _sx3.get() if hasattr(_sx3, 'get') else (_sx3 or '')
                _rec2 = resolve_recommended_hour(ds, event_type, _owners_std, _sxstr3)
                if _rec2:
                    best_zh = str(_rec2.get('best_zhi', '') or '').strip()
                    start_hh = _ZHI_START.get(best_zh, 12)
                    # 重算推荐四柱（年、月、日柱与日相同，仅时柱变为推荐吉时）
                    try:
                        y, mo, da = str(result.get('date', '') or '').split('-')
                        cur_date = _date(int(y), int(mo), int(da))
                        bs = _calc_sz(cur_date, int(start_hh), 0)
                        if (isinstance(bs, dict)
                                and all(isinstance(bs.get(k), str) for k in ('年柱','月柱','日柱','时柱'))
                                and all(len(bs.get(k,'')) == 2 for k in ('年柱','月柱','日柱','时柱'))):
                            new_str = f"{bs['年柱']} {bs['月柱']} {bs['日柱']} {bs['时柱']}"
                            result['sizhu'] = new_str
                            if isinstance(detail_ref, dict):
                                # 2026-09-17 修复 Bug5（位置2）：同位置1，
                                #   保留旧 detail_ref['sizhu'] 的 'date'/'year'/'month'/'day' 等键。
                                _old2 = detail_ref.get('sizhu') or {}
                                _new2 = dict(_old2) if isinstance(_old2, dict) else {}
                                _new2.update({
                                    '年柱': bs['年柱'], '月柱': bs['月柱'],
                                    '日柱': bs['日柱'], '时柱': bs['时柱'],
                                })
                                detail_ref['sizhu'] = _new2
                                detail_ref['_auth_sizhu'] = True
                            try:
                                vv = list(self.result_tree.item(selected[0], 'values'))
                                if len(vv) > 0:
                                    _lines = str(vv[0] or '').split('\n')
                                    if len(_lines) >= 2:
                                        _lines[1] = new_str
                                    else:
                                        _lines.append(new_str)
                                    vv[0] = '\n'.join(_lines)
                                    self.result_tree.item(selected[0], values=vv)
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            # 任一步失败都不中断原详情显示，保持扫日阶段的午时柱即可
            pass
        # =====================================================================

        # 插入基本信息
        text.insert(tk.END, f"""
日期：{result.get('date', '')}
农历：{result.get('lunar', '')}
四柱：{result.get('sizhu', '')}
评分：{result.get('score', 0)} 分
等级：""")
        
        # 如果有星星，用金色显示
        level = result.get('level', '未知')
        if '★' in level:
            star_count = level.count('★')
            other_text = level.replace('★', '').strip()
            text.insert(tk.END, '★' * star_count, "gold_star")
            if other_text:
                text.insert(tk.END, f" {other_text}")
        else:
            text.insert(tk.END, level)
        
        # 如果是婚嫁择日，显示大利月/小利月信息
        if event_type in MARRIAGE_EVENTS and daliyue_info != '-':
            # 2026-10-16 第4批 L5：普通月份补括注，与【嫁娶择日分析】「非大利月，无加分」口径一致
            _ly_txt = '普通月份（非大利月，无利月加分）' if daliyue_info == '普通月份' else daliyue_info
            text.insert(tk.END, f"\n利月：{_ly_txt}")

        # 2026-09 作灶主事人模式标注（随模式切换文案）
        _zaozhu_mode_rpt = None
        if event_type == '作灶':
            _zaozhu_mode_rpt = result.get('zaozhu_mode')
            if not _zaozhu_mode_rpt:
                _zmv = getattr(self, 'zaozhu_mode', None)
                _zaozhu_mode_rpt = _zmv.get() if hasattr(_zmv, 'get') else '男主人'
            if _zaozhu_mode_rpt not in ('男主人', '女主人', '双主'):
                _zaozhu_mode_rpt = '男主人'
            _zm_lines = {
                '男主人': '作灶主事：男主人（宅主）｜辅：女主人（半权重）',
                '女主人': '作灶主事：女主人｜辅：男主人（半权重）',
                '双主': '作灶主事：男主人、女主人（双主等权，任一被冲即否决）',
            }
            text.insert(tk.END, f"\n{_zm_lines[_zaozhu_mode_rpt]}")
        
        # 插入事主信息
        text.insert(tk.END, "\n\n[事主信息]")
        text.insert(tk.END, "\n ----------------------------------------")
        
        # 导入必要的模块
        from modules.喜用神计算器 import calculate_xishen_yongshen
        
        owners_info = result.get('owners_info', getattr(self, 'owners_info', []))
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
                    text.insert(tk.END, f"\n   事主{i}:{name}")
                    if gender:
                        text.insert(tk.END, f"({gender})")
                    
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
                            panpan = BaZiPanPan(birth_date.year, birth_date.month, birth_date.day, birth_hour, birth_minute, gender,
                                                longitude=_parse_owner_longitude(owner_info.get('longitude'), show_warning=False))
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
                            text.insert(tk.END, f"\n     公历:{birth_date}")
                            
                            # 计算农历日期
                            try:
                                from modules.高精度农历转换 import HighPrecisionLunar
                                lunar_converter = HighPrecisionLunar()
                                lunar_info = lunar_converter._get_lunar_info_sxtwl(birth_date.year, birth_date.month, birth_date.day, 12, 0, 0)
                                lunar_str = f"{lunar_info['lunar_year']}年{lunar_info['lunar_month']}月{lunar_info['lunar_day']}日"
                                if lunar_info['is_leap']:
                                    lunar_str = f"{lunar_info['lunar_year']}年闰{lunar_info['lunar_month']}月{lunar_info['lunar_day']}日"
                                text.insert(tk.END, f"\n     农历:{lunar_str}")
                            except Exception as e:
                                text.insert(tk.END, "\n     农历:未知")
                            
                            text.insert(tk.END, f"\n     四柱:{sizhu_text}")
                            
                            # 显示生肖（直接跟在四柱后面）
                            zodiac_map = {'子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔', '辰': '龙', '巳': '蛇',
                                         '午': '马', '未': '羊', '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪'}
                            year_zhi = year_zhu[1:] if len(year_zhu) > 1 else ''
                            zodiac = zodiac_map.get(year_zhi, '')
                            if zodiac:
                                text.insert(tk.END, "(")
                                text.insert(tk.END, zodiac, "zodiac")
                                text.insert(tk.END, ")")
                                text.tag_config("zodiac", foreground="blue")
                            
                            text.insert(tk.END, f"\n     喜用神:{xishen}")
                            
                            # 如果是嫁娶，女命显示夫星、子星、阴胎（阴胎属女命）
                            if event_type in MARRIAGE_UI_EVENTS and gender == '女':
                                try:
                                    from modules.工具函数 import get_fuzi, get_yintai
                                    
                                    month_gan = month_zhu[:1] if month_zhu else '甲'
                                    month_zhi = month_zhu[1:] if len(month_zhu) > 1 else '子'
                                    year_gan = year_zhu[:1] if year_zhu else ''
                                    year_zhi_part = year_zhu[1:] if len(year_zhu) > 1 else ''
                                    
                                    if year_gan and year_zhi_part:
                                        # 计算夫星子星（基于年干年支）
                                        fuzi_info = get_fuzi(year_gan, year_zhi_part)
                                        fu = fuzi_info.get('fu', '未知')
                                        zi = fuzi_info.get('zi', '未知')
                                        
                                        # 计算阴胎（以新娘月柱为基准 = 胎元）
                                        yintai = get_yintai(month_gan, month_zhi)
                                        
                                        text.insert(tk.END, f"\n    夫星：{fu}")
                                        text.insert(tk.END, f"\n    子星：{zi}")
                                        text.insert(tk.END, f"\n    阴胎：{yintai}")
                                except:
                                    pass
                            # 如果是嫁娶，男命显示阳气（阳气属男命；与阴胎同法：
                            # 月干+1、月支+3即胎元，男称阳气女称阴胎）
                            if event_type in MARRIAGE_UI_EVENTS and gender == '男':
                                try:
                                    from modules.工具函数 import get_yangqi
                                    if month_zhu and len(month_zhu) >= 2:
                                        text.insert(tk.END, f"\n    阳气：{get_yangqi(month_zhu[:1], month_zhu[1:])}")
                                except:
                                    pass
                        except:
                            pass
        else:
            text.insert(tk.END, "\n  暂无事主信息")

        # 2026-09 作灶主事人模式详文
        if event_type == '作灶' and _zaozhu_mode_rpt:
            if _zaozhu_mode_rpt == '双主':
                _zm_para = ('本课作灶择日以男主人（宅主）、女主人同为主事人（双主等权）；'
                            '日柱冲任一主事人即一票否决。')
            else:
                _zm_zhu = '宅主（男主人）' if _zaozhu_mode_rpt == '男主人' else '女主人'
                _zm_fu = '女主人' if _zaozhu_mode_rpt == '男主人' else '宅主（男主人）'
                _zm_nm = '年命'  # 用户原句：以宅主（男主人）年命为主，女主人年命为辅
                _zm_para = (f'本课作灶择日以{_zm_zhu}{_zm_nm}为主，{_zm_fu}{_zm_nm}为辅'
                            f'（辅助者半权重参与喜用神、生肖相主、神煞等匹配项）；'
                            f'日柱冲主事人则一票否决，冲辅助者不否决（仅半权重扣分）。')
            text.insert(tk.END, "\n\n[作灶主事说明]")
            text.insert(tk.END, "\n ----------------------------------------")
            text.insert(tk.END, f"\n   {_zm_para}")
        
        # 添加二十四山方位吉凶信息（修造/安葬等"山家类事项"专用；嫁娶/订婚/纳采不显示，避免山向无关信息）
        sansha_info = detail.get('sansha_info', {})
        shan_xiang = detail.get('shan_xiang', '')
        _show_shan_section = False
        if shan_xiang:
            # 明确选了山向 → 一定显示
            _show_shan_section = True
        elif sansha_info and event_type not in MARRIAGE_EVENTS:
            # 未选山向但属于修造类事件（非婚嫁）→ 也显示纯三煞段/山家警告
            _show_shan_section = True
        if _show_shan_section:
            text.insert(tk.END, "\n\n[二十四山方位吉凶]")
            text.insert(tk.END, "\n ----------------------------------------")
            
            if shan_xiang:
                text.insert(tk.END, f"\n   坐山：{shan_xiang}")
            
            # 三煞信息
            year_sansha = sansha_info.get('year_sansha', [])
            month_sansha = sansha_info.get('month_sansha', [])
            day_sansha = sansha_info.get('day_sansha', [])
            
            if year_sansha:
                text.insert(tk.END, f"\n   年三煞：{'、'.join(year_sansha)}")
            if month_sansha:
                text.insert(tk.END, f"\n   月三煞：{'、'.join(month_sansha)}")
            if day_sansha:
                text.insert(tk.END, f"\n   日三煞：{'、'.join(day_sansha)}")
            
            # 三煞避忌原则说明
            text.insert(tk.END, "\n\n   【三煞避忌原则】")
            text.insert(tk.END, "\n   ──")
            text.insert(tk.END, "\n   年三煞最重：月、日、时柱皆不可犯")
            text.insert(tk.END, "\n   月三煞次之：日、时柱不可犯")
            text.insert(tk.END, "\n   日三煞又次之：时柱不可犯")
            
            # 四柱犯三煞详情
            text.insert(tk.END, "\n\n   【四柱三煞检查】")
            text.insert(tk.END, "\n   ──")
            # 判定口径（2026-09-07 用户确认）：山向类仅坐山修方否决、四柱临方扣分不否决；
            # 嫁娶类四柱不犯。山向犯三煞一律❌否决；四柱月/日/时支临方在山向类降为⚠提示。
            _pv = sansha_info.get('sansha_pillar_veto', True)
            _kj = sansha_info.get('sansha_koujing', '')
            if _kj:
                text.insert(tk.END, f"\n   判定口径：{_kj}")

            def _fan_mark(fan, label, is_shan=False):
                if not fan:
                    return
                if is_shan or _pv:
                    text.insert(tk.END, f"\n   ❌ {label}")
                else:
                    text.insert(tk.END, f"\n   ⚠ {label}（临三煞方，扣分不否决）")

            # 年三煞检查
            year_fan_month = sansha_info.get('year_sansha_month_fan', False)
            year_fan_day = sansha_info.get('year_sansha_day_fan', False)
            year_fan_hour = sansha_info.get('year_sansha_hour_fan', False)
            year_fan_shan = sansha_info.get('year_sansha_fan', False)

            _fan_mark(year_fan_month, '年三煞犯月柱')
            _fan_mark(year_fan_day, '年三煞犯日柱')
            _fan_mark(year_fan_hour, '年三煞犯时柱')
            _fan_mark(year_fan_shan, '年三煞犯山向', is_shan=True)

            if not year_fan_month and not year_fan_day and not year_fan_hour and not year_fan_shan:
                text.insert(tk.END, "\n   ✅ 年三煞不犯")

            # 月三煞检查
            month_fan_day = sansha_info.get('month_sansha_day_fan', False)
            month_fan_hour = sansha_info.get('month_sansha_hour_fan', False)
            month_fan_shan = sansha_info.get('month_sansha_fan', False)

            _fan_mark(month_fan_day, '月三煞犯日柱')
            _fan_mark(month_fan_hour, '月三煞犯时柱')
            _fan_mark(month_fan_shan, '月三煞犯山向', is_shan=True)

            if not month_fan_day and not month_fan_hour and not month_fan_shan:
                text.insert(tk.END, "\n   ✅ 月三煞不犯")

            # 日三煞检查
            day_fan_hour = sansha_info.get('day_sansha_hour_fan', False)
            day_fan_shan = sansha_info.get('day_sansha_fan', False)

            _fan_mark(day_fan_hour, '日三煞犯时柱')
            _fan_mark(day_fan_shan, '日三煞犯山向', is_shan=True)

            if not day_fan_hour and not day_fan_shan:
                text.insert(tk.END, "\n   ✅ 日三煞不犯")

            # 年家五黄检查（详情展示宫位与坐山结论）
            wuhuang_info = sansha_info.get('wuhuang_info') or {}
            if wuhuang_info.get('宫位'):
                text.insert(tk.END, "\n\n   【年家五黄】")
                text.insert(tk.END, "\n   ──")
                if wuhuang_info.get('入中'):
                    text.insert(tk.END, f"\n   {wuhuang_info.get('年份', '')}年五黄入中宫，无固定凶方")
                else:
                    text.insert(tk.END, f"\n   {wuhuang_info.get('年份', '')}年五黄在{wuhuang_info['宫位']}宫（{wuhuang_info.get('三山', '')}）")
                if shan_xiang:
                    _wu_level = wuhuang_info.get('级别', '')
                    if _wu_level == '凶煞':
                        text.insert(tk.END, "\n   ❌ 坐山犯五黄，宜静不宜动，不可动土修造安葬（详见山家封禁）")
                    elif _wu_level == '警告':
                        text.insert(tk.END, "\n   ⚠ 兼向犯五黄，须谨慎制化（详见山家警告）")
                    else:
                        text.insert(tk.END, "\n   ✅ 坐山不犯五黄")

            # 三煞总评分影响
            sansha_penalty = sansha_info.get('sansha_penalty', 0)
            if sansha_penalty != 0:
                text.insert(tk.END, f"\n\n   三煞总扣分：{sansha_penalty}")
            
            # 山家封禁 / 山家警告 / 山家吉神（专业级天机模块）
            blocked = sansha_info.get('mountain_blocked', False)
            blocked_reasons = sansha_info.get('mountain_block_reasons', [])
            mountain_warnings = sansha_info.get('mountain_warnings', [])
            mountain_jishen = sansha_info.get('mountain_jishen', [])
            mountain_day_type = sansha_info.get('mountain_day_type', sansha_info.get('day_type', ''))
            
            if blocked or blocked_reasons:
                text.insert(tk.END, "\n\n   【⛔ 山家封禁 · 绝对不能用】")
                text.insert(tk.END, "\n   ──")
                for r in blocked_reasons:
                    text.insert(tk.END, f"\n   ❌ {r}")
            if mountain_warnings:
                text.insert(tk.END, "\n\n   【⚠️ 山家警告 · 须谨慎】")
                text.insert(tk.END, "\n   ──")
                for w in mountain_warnings:
                    if isinstance(w, dict):
                        msg = w.get('说明') or w.get('msg') or str(w)
                    else:
                        msg = str(w)
                    text.insert(tk.END, f"\n   ⚠ {msg}")
            if mountain_jishen:
                text.insert(tk.END, "\n\n   【✅ 山家吉神 · 加分项】")
                text.insert(tk.END, "\n   ──")
                for js in mountain_jishen:
                    text.insert(tk.END, f"\n   ✓ {js}")
            if mountain_day_type and mountain_day_type not in ('', '普通日'):
                text.insert(tk.END, f"\n\n   【日期类别】：{mountain_day_type}")
        
        content = f"""

【评分详情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        # 显示详细得分
        score_details = detail.get('score_details', {})
        if score_details:
            # 2026-02-05 修正：嫁娶评分路径同步有 '五行评分' 键（即嫁娶评分专用评分）；
            # 若历史数据缺该键则取 '嫁娶评分'，不得回退100错显满分。
            wuxing_score = score_details.get('五行评分', score_details.get('嫁娶评分', 100))
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
                    content += f"    ├─ 十二长生得分（日干在各柱地支的长生旺衰）：{zhangsheng:+d} 分\n"
                    for _zl in score_breakdown.get('十二长生明细', []):
                        content += f"      • {_zl}\n"
                zhizhi = score_breakdown.get('地支关系得分', 0)
                # Q5（2026-10-08 拍板）：地支关系 0 分也展示总分行，
                # 明细存在即列出（如午午午未：六合+24/自刑-24 相抵为 0），
                # 避免审查/用户把“0 分隐藏”误读为时柱关系未计入。
                content += f"    ├─ 地支关系得分（四柱六对合计）：{zhizhi:+d} 分\n"
                for _zl in score_breakdown.get('地支关系明细', []):
                    content += f"      • {_zl}\n"
                nayin = score_breakdown.get('纳音匹配得分', 0)
                if nayin != 0:
                    content += f"    └─ 纳音匹配得分：{nayin:+d} 分\n"
                    for _nl in score_breakdown.get('纳音匹配明细', []):
                        content += f"      • {_nl}\n"
                # 2026-09-10 归零透明化（2025-10-28坤山案例）：一票否决把五行评分强制
                # 归零时，在明细末尾明示归零前合计，避免“明细正常、结果归零”无从追溯
                # U1（2026-10-16 第6批拍板）：明细层归零注统一叙述式句式
                # 「五行明细合计 X 分，<机制>归零为 0 分」，机制名保留区分
                # （一票否决 vs 按规则负分），与嫁娶路径 L596x 同构。
                if wu_xing_result.get('he_ge') is False and wuxing_score == 0:
                    _bd_sum = 0
                    for _bk in ('基础分', '神煞得分', '宜事得分', '忌事得分',
                                '十二长生得分', '地支关系得分', '纳音匹配得分'):
                        _bv = score_breakdown.get(_bk, 0)
                        if isinstance(_bv, (int, float)):
                            _bd_sum += int(_bv)
                    content += f"    └─ 五行明细合计 {_bd_sum} 分，一票否决归零为 0 分\n"
            
            # 显示婚嫁评分详情（夫星受克等）
            marriage_details = detail.get('marriage_details', [])
            if marriage_details:
                for detail_name, detail_score in marriage_details:
                    if detail_score != 0:
                        content += f"    {'├─' if score_breakdown else ''}{detail_name}：{detail_score:+d} 分\n"
                    else:
                        # 2026-10-11 B1：0 分＝信息行（本命三煞新郎未犯/新娘对照/
                        # 新郎生年缺失提示），只展示不标分值，不进忌项与神煞加减分。
                        content += f"    {'├─' if score_breakdown else ''}{detail_name}\n"
                # 2026-09-17 归零透明化：嫁娶明细合计可能为负（如 -2），算法按 max(0,…)
                # 兜底归零显示 0。此处明示归零前合计，避免"明细加总≠显示分"无法追溯。
                _raw_wx = score_details.get('五行原始分')
                if isinstance(_raw_wx, (int, float)) and _raw_wx < 0 and wuxing_score == 0:
                    _veto_tag = '（本日另触发一票否决，总分归零）' if score_details.get('否决原因') else ''
                    content += (f"    └─ 五行明细合计 {int(_raw_wx):+d} 分，"
                                f"按规则负分归零为 0 分{_veto_tag}\n")
                # A4b 纳音说明（2026-10-16 第5批T4）：嫁娶评分体系（婚嫁评分算法
                # 基础60＋利月/神煞/合局）不含纳音匹配分项，纳音行仅存在于正五行
                # 路径（12 事项）。此处补一行说明，防审查把跨路径差异误读为渲染
                # 缺陷（属 #2 两套评分架构差异，算法变更归该议题，本批不动分值）。
                _mrx_prefix = '├─' if score_breakdown else ''
                content += (f"    {_mrx_prefix}纳音匹配：嫁娶评分体系不含此分项，"
                            "属评分架构差异\n")
            
            content += f"  月令得分：{yueling_score:+d} 分\n"
            
            # 月令详细得分
            yueling_detail = score_details.get('月令详细', {})
            if yueling_detail:
                # 2026-10-16 第4批 L1：旺衰/支支得分补依据文案（取分口径来自评分器，纯展示拼接）
                _ws_note = yueling_detail.get('旺衰依据', '')
                _zz_note = yueling_detail.get('支支依据', '')
                content += f"    ├─ 旺衰得分：{yueling_detail.get('旺衰得分', 0):+d} 分{('（' + _ws_note + '）') if _ws_note else ''}\n"
                content += f"    └─ 支支关系得分：{yueling_detail.get('支支关系得分', 0):+d} 分{('（' + _zz_note + '）') if _zz_note else ''}\n"
            
            content += f"  喜用神得分：{xishen_score:+d} 分\n"
            
            # 生肖相主得分（新增）
            xiangzhu_score = score_details.get('相主得分', 0)
            xiangzhu_details = score_details.get('相主详情', [])
            if xiangzhu_score != 0 or xiangzhu_details:
                content += f"  生肖相主得分：{xiangzhu_score:+d} 分\n"
                for detail_item in xiangzhu_details:
                    content += f"    • {detail_item}\n"
            
            # 事主匹配得分（喜用神匹配明细）
            owner_matches = score_details.get('事主匹配', [])
            if owner_matches:
                content += f"  事主匹配（喜用神）：\n"
                for m in owner_matches:
                    if isinstance(m, dict):
                        name = m.get('name') or m.get('owner') or m.get('姓名', '事主')
                        # 2026-10-16 第4批 L2：渲染 details 明细（带分值），空则回退旧 remark 通道
                        _dets = m.get('details') or []
                        rmk = '，'.join(_dets) if _dets else (m.get('remark') or m.get('说明') or m.get('match_detail', ''))
                        sc  = m.get('score', m.get('得分', 0))
                        if sc or rmk:
                            _wt = m.get('weight', 1.0)
                            _wtag = '（辅·半权重）' if isinstance(_wt, (int, float)) and _wt < 1.0 else ''
                            content += f"    • {name}{_wtag}：（{sc:+d}分）{rmk}\n"
                    else:
                        content += f"    • {m}\n"
            
            has_hd_key = '黄道得分' in score_details
            if has_hd_key:
                content += f"  黄道得分：{huangdao_score:+d} 分\n"
            else:
                # 婚嫁路径：黄道得分已并入婚嫁评分（即五行评分行内的大黄道/小黄道明细），不重复计
                content += "  黄道得分：已并入五行评分（大黄道/小黄道明细见五行评分项内）\n"
            sun_moon_score = score_details.get('太阳太阴得分', 0)
            # 2026-10-16 第4批 L3：太阳太阴 +0 补解释——修造神煞档单轨登记，嫁娶无山向不适用，防双轨
            if sun_moon_score == 0 and not shan_xiang:
                _sm_note = '（到山到向仅适用修造类山向事项，本事项不适用；其加分由修造神煞档单轨登记，本项恒 0）'
            elif sun_moon_score == 0:
                _sm_note = '（本日太阳太阴未到山到向）'
            else:
                _sm_note = ''
            content += f"  太阳太阴得分：{sun_moon_score:+d} 分{_sm_note}\n"
            # 时柱地支关系得分（2026-09-01 用户确认：推荐时柱参与的地支关系应计分）
            hour_rel_score = score_details.get('时柱关系得分', 0) or 0
            hour_rel_details = score_details.get('时柱关系明细', [])
            if hour_rel_score or hour_rel_details:
                content += f"  时柱地支关系（按时柱归集展示；时柱关系已计入五行评分·地支关系得分，非独立分项）：{hour_rel_score:+d} 分\n"
                for rl in hour_rel_details:
                    content += f"    • {rl}\n"
            sansha_penalty = score_details.get('三煞扣分', 0) or 0
            # 各分项统一 `or 0`，杜绝 None 进入算术累加
            wuxing_score = wuxing_score or 0
            yueling_score = yueling_score or 0
            xishen_score = xishen_score or 0
            xiangzhu_score = xiangzhu_score or 0
            huangdao_score = huangdao_score or 0
            sun_moon_score = sun_moon_score or 0
            # 2026-09-09：时柱关系分已含于五行评分·地支关系得分，公式行不得再加，
            # 否则公式合计≠总分（如 93-5+22-15=95 与总分110不符）。
            raw_total = wuxing_score + yueling_score + xishen_score + xiangzhu_score + huangdao_score + sun_moon_score
            content += f"  ─────────────────────────────────\n"
            if not has_hd_key:
                # 公式行不含黄道项（已并入五行评分），避免与"+0"重复列出的误读
                if sansha_penalty:
                    content += f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d} {sun_moon_score:+d} {sansha_penalty:+d}(三煞扣分) = {raw_total + sansha_penalty} 分\n"
                else:
                    content += f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d} {sun_moon_score:+d} = {raw_total} 分\n"
            else:
                if sansha_penalty:
                    # 总分含三煞扣分，公式行如实列出，避免误读为"满分上限"
                    content += f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d} {huangdao_score:+d} {sun_moon_score:+d} {sansha_penalty:+d}(三煞扣分) = {raw_total + sansha_penalty} 分\n"
                else:
                    content += f"  计算公式：{wuxing_score} {yueling_score:+d} {xishen_score:+d} {xiangzhu_score:+d} {huangdao_score:+d} {sun_moon_score:+d} = {raw_total} 分\n"
            # _fc0915：一票否决日公式分项合计仅供追溯、总分强制归零，明示口径
            if detail.get('veto_reasons'):
                content += (f"  注：本日触发一票否决（详见【一票否决】），"
                            f"上方公式分项合计 {raw_total + sansha_penalty} 分仅供追溯，"
                            f"总分强制归零。\n")
            # 2026-02-05：删除“满分上限限制：X → Y”提示行——分项键值已全部修正，
            # （五行评分取嫁娶评分、时柱关系得分注入同步总分分键），公式合计必然等于总分分；
            # 若仍有差额说明是代码缺陷，应在数据层修正，而非用“满分上限”措辞掩盖。
            # 玄空加权封顶/封底透明化（2026-09-10）：总分经加权产生时，
            # 在总分处同步明示原始加权值（与下方玄空飞星块加权公式同源同值）
            _cap_note = ''
            try:
                _fi_cap = detail.get('feixing_info') or {}
                if _fi_cap:
                    _zw_cap = score_details.get('正五行总分', total_score)
                    _fx_cap = int(_fi_cap.get('feixing_score', 0) or 0)
                    _wx_cap = float(_zw_cap) * 0.7 + (50 + _fx_cap) * 0.3
                    if _wx_cap > 100 and int(total_score) == 100:
                        _cap_note = (f"  （玄空加权：{_zw_cap}×0.7 + "
                                     f"(50+飞星{_fx_cap:+d}={50+_fx_cap})×0.3 = {_wx_cap:.0f}，"
                                     f"超100，封顶100）\n")
                    elif _wx_cap < 0 and int(total_score) == 0:
                        _cap_note = (f"  （玄空加权：{_zw_cap}×0.7 + "
                                     f"(50+飞星{_fx_cap:+d}={50+_fx_cap})×0.3 = {_wx_cap:.0f}，"
                                     f"低于0，封底0）\n")
            except Exception:
                _cap_note = ''
            _ss_detail = score_details.get('三煞扣分明细') or []
            if _ss_detail:
                content += f"    三煞扣分构成：{'、'.join(str(_x) for _x in _ss_detail)}\n"
            # 三煞“上管下、下不犯上”口径透明化（2026-10-08 拍板维持单向）：
            # 枚举早序柱临晚序柱三煞方的反向组合，按口径不查、不扣分，仅提示，
            # 避免反向相临被误读为“临三煞漏扣分”（hour 三煞方本模块不计算）。
            _ssz = detail.get('sizhu') if isinstance(detail.get('sizhu'), dict) else {}
            _yz = str(_ssz.get('年柱', '') or '')[1:2]
            _mz = str(_ssz.get('月柱', '') or '')[1:2]
            # 直接从 detail 取三煞信息（不依赖外层 sansha_info 绑定，
            # 保证沙箱函数化执行与真实 GUI 内联执行同行为）
            _ssi2 = detail.get('sansha_info') if isinstance(detail.get('sansha_info'), dict) else {}
            _msf = _ssi2.get('month_sansha') or []
            _dsf = _ssi2.get('day_sansha') or []
            _rev = []
            if _yz and _yz in _msf:
                _rev.append(f'年柱{_yz}临月柱三煞方（{"".join(_msf)}）')
            if _yz and _yz in _dsf:
                _rev.append(f'年柱{_yz}临日柱三煞方（{"".join(_dsf)}）')
            if _mz and _mz in _dsf:
                _rev.append(f'月柱{_mz}临日柱三煞方（{"".join(_dsf)}）')
            for _rv in _rev:
                content += f"    • {_rv}：三煞口径“上管下、下不犯上”，反向不查不扣分\n"
            content += f"  总分：{total_score} 分\n"
            content += _cap_note

            # 玄空飞星评分（2026-09-01 用户确认：加减分项，仅修造/安葬类）
            feixing_info = detail.get('feixing_info')
            if feixing_info:
                fx_score = feixing_info.get('feixing_score', 0)
                fx_level = feixing_info.get('feixing_level', '')
                fx_stars = feixing_info.get('feixing_stars', '')
                fx_count = feixing_info.get('feixing_star_count', '')
                fx_comment = feixing_info.get('feixing_comment', '')
                fx_details = feixing_info.get('feixing_details', [])
                _zhengwu_raw = score_details.get('正五行总分', total_score)
                content += f"  玄空飞星评分：{fx_score:+d} 分（{fx_level}）\n"
                if fx_stars:
                    content += f"    坐山星曜：{fx_stars}\n"
                if fx_count:
                    content += f"    {fx_count}\n"
                if fx_comment:
                    content += f"    断语：{fx_comment}\n"
                for fd in fx_details:
                    content += f"    • {fd}\n"
                # 年家煞与玄空飞星并列说明（2026-09-02用户确认）：年家二黑/五黄为年家紫白静盘
                # （全年固定一方，看是否犯坐山）；玄空年/月/日/时星为飞星动盘（逐时飞临坐山）。
                # 年家不犯山而飞星到山时，并列表述（如"年二黑在离宫（不犯山）；时二黑到乾宫（坐山），扣-15分"），
                # 避免两套体系被误读为矛盾
                try:
                    _fx_mg_map = {'壬':'坎','子':'坎','癸':'坎','丑':'艮','艮':'艮','寅':'艮',
                                  '甲':'震','卯':'震','乙':'震','辰':'巽','巽':'巽','巳':'巽',
                                  '丙':'离','午':'离','丁':'离','未':'坤','坤':'坤','申':'坤',
                                  '庚':'兑','酉':'兑','辛':'兑','戌':'乾','乾':'乾','亥':'乾'}
                    _fx_mg = _fx_mg_map.get((shan_xiang or '')[:1], '')
                    _fx_eh = sansha_info.get('erhei_info') or {}
                    _fx_wh = sansha_info.get('wuhuang_info') or {}
                    for _fx_p, _fx_sn in re.findall(r'([年月日时])([一二三四五六七八九][白黑碧绿黄赤紫])', fx_stars or ''):
                        if _fx_sn == '二黑':
                            _fx_ni, _fx_fan = _fx_eh, '犯二黑'
                        elif _fx_sn == '五黄':
                            _fx_ni, _fx_fan = _fx_wh, '犯五黄'
                        else:
                            continue
                        _fx_ng = _fx_ni.get('宫位', '')
                        # 飞星"年星"加"玄空"前缀，避免与年家紫白"年五黄/年二黑"同名混淆
                        _fx_p_txt = '玄空年' if _fx_p == '年' else _fx_p
                        if _fx_ng and not _fx_ni.get('入中') and not _fx_ni.get(_fx_fan) and _fx_mg:
                            content += (f"    说明：年{_fx_sn}在{_fx_ng}宫（不犯山）；"
                                        f"{_fx_p_txt}{_fx_sn}到{_fx_mg}宫（坐山），扣 -15 分。\n")
                except Exception:
                    pass
                # 加权公式如实计算：正五行×0.7 + (50+飞星)×0.3，结果封顶 0–100。
                # 2026-09-09 修：原直接硬写"= 总分"，当加权值>100被封顶时（如 150×0.7+40×0.3=117），
                # 等式左边与右边(100)不符。现展示真实加权值并注明封顶。
                try:
                    _wx = float(_zhengwu_raw) * 0.7 + (50 + int(fx_score)) * 0.3
                    if round(_wx) != int(total_score) and _wx > 100:
                        content += f"    加权公式：正五行{_zhengwu_raw}×0.7 + (50+飞星{fx_score:+d}={50+fx_score})×0.3 = {_wx:.0f}（超100，封顶100）\n"
                    elif round(_wx) != int(total_score) and _wx < 0:
                        content += f"    加权公式：正五行{_zhengwu_raw}×0.7 + (50+飞星{fx_score:+d}={50+fx_score})×0.3 = {_wx:.0f}（低于0，封底0）\n"
                    else:
                        content += f"    加权公式：正五行{_zhengwu_raw}×0.7 + (50+飞星{fx_score:+d}={50+fx_score})×0.3 = {total_score}\n"
                except Exception:
                    content += f"    加权公式：正五行{_zhengwu_raw}×0.7 + (50+飞星{fx_score:+d}={50+fx_score})×0.3 = {total_score}\n"
            else:
                # A2a/b 占位说明（2026-10-16 第5批T2）：feixing_info 仅在评分器
                # 四条件齐备时生成（评分器.py：zeli_mode=='feixing' + 画像含飞星
                # + 非否决课 + 已填坐山），不渲染时在此补原因占位，消除「段缺失」
                # 观感。四分支优先序与生成条件镜像：非山向→无坐山→否决→pure。
                if event_type not in FEIXING_EVENTS:
                    content += "  玄空飞星：本事项非山向类，玄空飞星段不适用\n"
                elif not shan_xiang:
                    content += "  玄空飞星：本事项无坐山，玄空飞星段不适用\n"
                elif detail.get('veto_reasons'):
                    content += "  玄空飞星：本课已否决，玄空飞星段不展开\n"
                else:
                    content += "  玄空飞星：本模式默认不显示玄空飞星段，如需查看请切换至对应模式\n"
        else:
            content += "  暂无详细得分数据\n"
        
        # 一票否决 / 凶煞门槛（正五行不合格直接❌凶）
        detail_veto_reasons = detail.get('veto_reasons') or []
        wu_xing_veto = detail.get('wu_xing_result', {})
        wx_hege_false = (isinstance(wu_xing_veto, dict) and not wu_xing_veto.get('he_ge', True)
                         and '计算错误' not in wu_xing_veto.get('ji_yu', '')
                         and '计算异常' not in wu_xing_veto.get('ji_yu', ''))
        _veto_body = ''
        for _vr in detail_veto_reasons:
            _veto_body += f"  {_vr}\n"
        if wx_hege_false:  # _fc0915：veto_reasons已含ji_yu时不重复渲染
            _jiyu_txt = wu_xing_veto.get('ji_yu', wu_xing_veto.get('reason', '不合格'))
            if not any(str(_jiyu_txt) in str(_v) for _v in detail_veto_reasons):
                _veto_body += f"  正五行门槛未过：{_jiyu_txt}\n"
        if detail_veto_reasons or wx_hege_false:
            content += f"""
【⚠️ 一票否决】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{_veto_body}
"""
        
        # 月令分析（与评分器_calculate_wangxiang旺相休囚死表100%同源，
        #    并追加通关合局细化说明，解决"得令/失令矛盾"）
        content += f"""
【月令分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        sizhu = detail.get('sizhu', {})
        if isinstance(sizhu, dict):
            # 键兼容：detail['sizhu']在权威覆盖/最佳吉时注入后为中文键{'年柱','月柱',...}，
            # 评分原始结构为小写键{'day_gan','month_zhi',...}，两种都要能取到
            def _sz_gan(key_cn, key_en):
                v = sizhu.get(key_en, '') or sizhu.get(key_cn, '')
                return v[:1] if isinstance(v, str) and len(v) >= 1 else ''
            def _sz_zhi(key_cn, key_en):
                v = sizhu.get(key_en, '') or sizhu.get(key_cn, '')
                if not isinstance(v, str) or len(v) < 1:
                    return ''
                # 英文键 month_zhi/day_zhi 存单字符地支（如"酉"），
                # 中文键 月柱/日柱 存"天干+地支"（如"丁酉"）。
                # 取末位字符统一兼容两种形态（单字符直接返回，两字符取地支）。
                return v[-1]
            day_gan = _sz_gan('日柱', 'day_gan')
            month_zhi = _sz_zhi('月柱', 'month_zhi')
            if day_gan and month_zhi:
                gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火',
                              '戊': '土', '己': '土', '庚': '金', '辛': '金',
                              '壬': '水', '癸': '水'}
                zhi_wuxing = {'子': '水', '丑': '土', '寅': '木', '卯': '木',
                              '辰': '土', '巳': '火', '午': '火', '未': '土',
                              '申': '金', '酉': '金', '戌': '土', '亥': '水'}
                day_wuxing = gan_wuxing.get(day_gan, '')
                month_wuxing = zhi_wuxing.get(month_zhi, '')
                if day_wuxing:
                    # ===== 旺相休囚死（按日干查月支）：与评分器_calculate_wangxiang评分表100%同源 =====
                    # 修复：原按季节表判定（丑归冬→土囚），与评分表（戊己土旺于辰戌丑未月）矛盾，
                    # 导致"月令分析说失令、月令得分却+15"的描述冲突（如2023-01-11己日丑月案例）。
                    if not month_zhi:
                        month_zhi = sizhu.get('月柱', '')[1:2]
                    WANGXIANG_TABLE = {
                        '甲': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                        '乙': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                        '丙': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
                        '丁': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
                        '戊': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
                        '己': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
                        '庚': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
                        '辛': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
                        '壬': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
                        '癸': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']}
                    }
                    state = ''
                    gan_table = WANGXIANG_TABLE.get(day_gan, {})
                    for k, zlist in gan_table.items():
                        if month_zhi in zlist:
                            state = k; break
                    sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
                    ke    = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
                    parts = []
                    if state == '旺':
                        parts.append(f"{day_gan}日主属{day_wuxing}气，月支{month_zhi}为{day_wuxing}气得令之月，日主得令而旺")
                    elif state == '相':
                        # 相=月支五行生日主五行（得生），与旺衰得分"相+5"对应，不得写作"得令而旺"
                        parts.append(f"{day_gan}日主属{day_wuxing}气，月支{month_zhi}得生而相")
                    elif state == '休':
                        parts.append(f"{day_gan}日主属{day_wuxing}气，月支{month_zhi}休囚泄气")
                    elif state == '囚':
                        parts.append(f"{day_gan}日主属{day_wuxing}气，月支{month_zhi}非{day_wuxing}气得令之月，日主失令（{day_wuxing}克当令之气，反受令困，处囚地）")
                    elif state == '死':
                        parts.append(f"{day_gan}日主属{day_wuxing}气，月支{month_zhi}非{day_wuxing}气得令之月，日主失令，{day_wuxing}气衰微")
                    else:
                        parts.append(f"{day_gan}日主属{day_wuxing}气，月支{month_zhi}非{day_wuxing}气得令之月，日主失令")
                    # 五行生克句
                    if month_wuxing:
                        if sheng.get(month_wuxing) == day_wuxing:
                            parts.append(f"{month_wuxing}生{day_wuxing}")
                        elif ke.get(month_wuxing) == day_wuxing:
                            parts.append(f"{month_wuxing}克{day_wuxing}")
                        elif month_wuxing == day_wuxing:
                            parts.append("同气相求")
                        elif sheng.get(day_wuxing) == month_wuxing:
                            parts.append(f"{day_wuxing}生{month_wuxing}")
                    # 失令但得生扶的补充说明：呼应月令旺衰得分（休=0不扣分；囚/死有扣分则不写"不扣分"）
                    if state not in ('旺', '相'):
                        supports = []
                        year_zhi_v = _sz_zhi('年柱', 'year_zhi')
                        day_zhi_v = _sz_zhi('日柱', 'day_zhi')
                        month_gan_v = _sz_gan('月柱', 'month_gan')
                        year_gan_v = _sz_gan('年柱', 'year_gan')
                        if zhi_wuxing.get(day_zhi_v) and (sheng.get(zhi_wuxing[day_zhi_v]) == day_wuxing or zhi_wuxing[day_zhi_v] == day_wuxing):
                            supports.append(f"日坐{day_zhi_v}（{zhi_wuxing[day_zhi_v]}气）")
                        if zhi_wuxing.get(year_zhi_v) and (sheng.get(zhi_wuxing[year_zhi_v]) == day_wuxing or zhi_wuxing[year_zhi_v] == day_wuxing):
                            supports.append(f"年支{year_zhi_v}（{zhi_wuxing[year_zhi_v]}气）")
                        if gan_wuxing.get(month_gan_v) and (sheng.get(gan_wuxing[month_gan_v]) == day_wuxing or gan_wuxing[month_gan_v] == day_wuxing):
                            supports.append(f"月干{month_gan_v}（{gan_wuxing[month_gan_v]}气）")
                        if gan_wuxing.get(year_gan_v) and (sheng.get(gan_wuxing[year_gan_v]) == day_wuxing or gan_wuxing[year_gan_v] == day_wuxing):
                            supports.append(f"年干{year_gan_v}（{gan_wuxing[year_gan_v]}气）")
                        if supports:
                            try:
                                wang_score = score_details.get('月令详细', {}).get('旺衰得分', 0)
                            except Exception:
                                wang_score = 0
                            tail = "故月令不扣分" if wang_score >= 0 else "稍解失令之势"
                            parts.append(f"惟{'、'.join(supports)}生扶，仍得根气，{tail}")
                    # 通关合局细化说明：月令克日主 → 若木→火→土链条有气则补
                    try:
                        year_zhi  = _sz_zhi('年柱', 'year_zhi')
                        day_zhi   = _sz_zhi('日柱', 'day_zhi')
                        nian_gan  = _sz_gan('年柱', 'year_gan')
                        yue_gan   = _sz_gan('月柱', 'month_gan')
                        day_gan_v = _sz_gan('日柱', 'day_gan')
                        san_zhi = {z for z in (year_zhi, month_zhi, day_zhi) if z}
                        sanzhi_wx  = {zhi_wuxing.get(z, '') for z in san_zhi} - {''}
                        tiangan_wx = {gan_wuxing.get(g, '') for g in (nian_gan, yue_gan, day_gan_v)} - {''}
                        if ke.get(month_wuxing) == day_wuxing:
                            guan_wx = sheng.get(month_wuxing, '')
                            if guan_wx and sheng.get(guan_wx) == day_wuxing:
                                added = False
                                if guan_wx in (sanzhi_wx | tiangan_wx):
                                    parts.append(f"幸{month_wuxing}{guan_wx}{day_wuxing}通关，降低月令克害")
                                    added = True
                                else:
                                    SANHE = {
                                        '火': {'寅', '午', '戌'}, '水': {'申', '子', '辰'},
                                        '木': {'亥', '卯', '未'}, '金': {'巳', '酉', '丑'},
                                    }
                                    for he_wx, zset in SANHE.items():
                                        if he_wx == guan_wx and len(san_zhi & zset) >= 2:
                                            parts.append(f"幸{month_wuxing}{guan_wx}{day_wuxing}通关（合局有气），降低月令克害")
                                            added = True; break
                                # 六合化出通关五行（卯戌→火等）
                                if not added:
                                    LIUHE_MAP = {('卯','戌'):'火', ('寅','亥'):'木', ('子','丑'):'土',
                                                 ('巳','申'):'水', ('午','未'):'土', ('辰','酉'):'金'}
                                    for (a,b), hua in LIUHE_MAP.items():
                                        if a in san_zhi and b in san_zhi and hua == guan_wx:
                                            parts.append(f"幸六合化{hua}通关，{hua}生{day_wuxing}化解{month_wuxing}克{day_wuxing}")
                                            break
                    except Exception:
                        pass
                    content += "  " + "，".join(parts) + "\n"
                else:
                    content += "  月令分析：暂无数据\n"
            else:
                content += "  月令分析：暂无数据\n"
        else:
            content += "  月令分析：暂无数据\n"
        # 四柱信息
        # → 如果当前时柱 == 中午12点示例 → 显式"示例时辰"提示；
        # → 否则（来自结果表 tree 的权威四柱，通常是系统择定时的推荐柱）→ 不写"示例时辰"误导。
        from modules.四柱计算器 import calculate_sizhu as _calc_sizhu_demo
        _demo_shi = ''
        try:
            _date_obj = result.get('date') or date_str
            if isinstance(_date_obj, str) and len(_date_obj) >= 10:
                yy, mo, dd = int(_date_obj[:4]), int(_date_obj[5:7]), int(_date_obj[8:10])
                _dr = _calc_sizhu_demo((yy, mo, dd), 12, 0)
                if isinstance(_dr, dict):
                    _demo_shi = _dr.get('时柱', '') or ''
        except Exception:
            _demo_shi = ''

        sizhu = detail.get('sizhu', {})
        if sizhu:
            shizhu = sizhu.get('时柱', 'N/A') or ''
            is_demo = (_demo_shi and shizhu == _demo_shi)
            shi_note = ""
            # 2026-09-05 用户确认：_auth_sizhu 成立时，时柱为即系统推荐柱，
            # 即便推荐时辰恰为午时（与午时示例同干支），也不得再标“示例时辰”误导
            if detail.get('_auth_sizhu'):
                shi_note = "　（系统择定推荐时柱，恰为午时）" if is_demo else "　（系统择定推荐时柱）"
            else:
                # Q5（2026-10-08）：非推荐柱按是否午时示例区分，
                # 不再对任意时辰硬写“中午12点”
                shi_note = ("　⚠ 示例时辰（中午12点），非推荐" if is_demo
                            else "　⚠ 此时辰非系统推荐，请参考下方时辰表")
            shi_hint_line = ""
            if detail.get('_auth_sizhu'):
                shi_hint_line = "  💡 提示：时柱为系统择定的推荐用柱，实际用课请参考下方【十二时辰吉凶】做二次确认\n"
            elif is_demo:
                shi_hint_line = "  ⚠ 提示：时柱为中午12点的示例干支，实际用课请参考下方【十二时辰吉凶】选择吉时\n"
            else:
                shi_hint_line = "  ⚠ 提示：此时柱非系统推荐，实际用课请参考下方【十二时辰吉凶】选择吉时\n"
            nian_g = sizhu.get('年柱', '')
            yue_g = sizhu.get('月柱', '')
            ri_g = sizhu.get('日柱', '')
            content += f"""
【四柱八字】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  年柱: {nian_g if nian_g else 'N/A'}    月柱: {yue_g if yue_g else 'N/A'}
  日柱: {ri_g if ri_g else 'N/A'}    时柱: {shizhu}{shi_note}

  【天干五行】
    年干: {nian_g[0] if len(nian_g)>0 else 'N/A'}    月干: {yue_g[0] if len(yue_g)>0 else 'N/A'}    日干: {ri_g[0] if len(ri_g)>0 else 'N/A'}    时干: {shizhu[0] if len(shizhu)>0 else 'N/A'}
  【地支五行】
    年支: {nian_g[1] if len(nian_g)>1 else 'N/A'}    月支: {yue_g[1] if len(yue_g)>1 else 'N/A'}    日支: {ri_g[1] if len(ri_g)>1 else 'N/A'}    时支: {shizhu[1] if len(shizhu)>1 else 'N/A'}

{shi_hint_line.rstrip()}
"""
        
        # 五行分析
        wu_xing_result = detail.get('wu_xing_result', {})
        # ── 推荐时柱重算：若已注入系统推荐时柱，则用权威四柱重算五行分析展示项 ──
        # （天干地支五行/地支关系/吉神/五行生克等原本按午时示例四柱生成，
        #   现用推荐时柱重算，保证与【四柱八字】段一致；评分数值本身不变）
        if detail.get('_auth_sizhu') and isinstance(detail.get('sizhu'), dict):
            try:
                from modules.评分器 import Scorer as _Scorer
                _sc = _Scorer()
                _nd = _sc._generate_wu_xing_details(detail['sizhu'], result.get('owners_info', []) if isinstance(result, dict) else [])
                if isinstance(_nd, dict) and _nd.get('天干五行'):
                    # 含时柱的地支关系行按事项加后缀（2026-09-09 口径勘正）：
                    #   修造/安葬等正五行事项：时柱关系由评分器 _calculate_zhizhi_relations
                    #       计入五行评分·地支关系得分 → 标"已计分"；
                    #   嫁娶类：婚嫁评分算法刻意"日课评分不含时柱冲合刑害"（时柱可换，
                    #       由十二时辰吉凶表独立评估，check_sanxing_penalty 用 hour_zhi='' 副本）
                    #       → 必须标"不计入日课总分"，否则如"酉酉自刑（已计分）"却无扣分项，误导用户。
                    try:
                        _ev = self.event_var.get()
                    except Exception:
                        _ev = ''
                    _is_mrg_ev = _ev in MARRIAGE_EVENTS
                    _hour_suffix = ('（推荐时柱，冲合刑害不计入日课总分，详见十二时辰吉凶）'
                                    if _is_mrg_ev else '（推荐时柱，已计入五行评分·地支关系得分，不重复累加）')
                    # 2026-10-02 口径修复：含时柱的合局（三合/六合/半合）本身已由
                    # 年月日三柱计入总分（婚嫁算法 get_zhiju_score），时柱只是
                    # 参与助局不另计分；原统一后缀"冲合刑害不计入日课总分"挂在
                    # 合局行上，与评分详情"三合局+15"自相矛盾。
                    _heju_suffix = ('（合局已计入日课总分；时柱参与助局不另计分，详见十二时辰吉凶）'
                                    if _is_mrg_ev else _hour_suffix)
                    _new_dz = []
                    for ln in _nd.get('地支关系', []):
                        if '示例时柱' in ln:
                            ln = ln.replace('（示例时柱，不计分）', _hour_suffix)
                        elif '时柱' in ln:
                            if _is_mrg_ev and any(_k in ln for _k in ('三合', '六合', '半合')):
                                ln = ln + _heju_suffix
                            else:
                                ln = ln + _hour_suffix
                        _new_dz.append(ln)
                    _nd['地支关系'] = _new_dz
                    wu_xing_result['details'] = _nd
            except Exception:
                pass
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
                    _dz_rels = wu_xing_details['地支关系']
                    for relation in _dz_rels:
                        content += f"    • {relation}\n"
                    # 裁定4（2026-10-08 拍板）：同段合与刑并存时，固定声明各自计分，
                    # 与 Q2"全量并列"原则一致，避免误读为"合能解刑/刑能破合"。
                    if any(any(_k in str(_r) for _k in ('三合', '六合', '半合'))
                           for _r in _dz_rels) and any('刑' in str(_r) for _r in _dz_rels):
                        content += "    （合刑并存，各自计分，非只取一边）\n"
                else:
                    content += "\n  【地支关系】\n    无明显合冲刑害关系\n"
                
                # 3. 十二长生
                if wu_xing_details.get('十二长生'):
                    content += "\n  【十二长生】（日干在各柱地支的长生旺衰，分值计入五行评分）\n"
                    _zs_score_map = {}
                    for _zl in (score_breakdown.get('十二长生明细') or []):
                        if '：' in _zl:
                            _zs_score_map[_zl[:2]] = _zl.split('：', 1)[1]
                    for pillar, state in wu_xing_details['十二长生'].items():
                        _zv = _zs_score_map.get(pillar, '')
                        content += f"    {pillar}: {state}" + (f"（{_zv}）" if _zv else "") + "\n"
                
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
                    # 2026-09-14：无天德月德时，若神煞信息另有加分吉神，
                    # 不写「无…吉神」以免与【神煞信息】自相矛盾
                    _has_ss_ji = any(
                        (isinstance(_s, dict) and _s.get('score', 0) > 0)
                        for _s in (detail.get('shensha_list') or []))
                    if _has_ss_ji:
                        content += "\n  【吉神】\n    有吉神（详见神煞信息）\n"
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
                content += f"  大黄道: {da_hd.get('name', 'N/A')} ({da_hd.get('type', 'N/A')})"
                if da_hd.get('score'): content += f"  {da_hd['score']:+d}分"
                content += "\n"
                if da_hd.get('description'):
                    content += f"    说明: {da_hd['description']}\n"
            if huangdao_info.get('xiao_huang_dao'):
                xiao_hd = huangdao_info['xiao_huang_dao']
                _xn = xiao_hd.get('name', '')
                _xs = xiao_hd.get('score', 0)
                _xt = xiao_hd.get('type', 'N/A')
                _xd = xiao_hd.get('description', '')
                # _yj0915：嫁娶场景除/危/执虽为吉但忌嫁娶，显示口径与评分详情一致
                # 2026-09-17 修复 Bug4：MARRIAGE_EVENTS 是模块级导入变量（L136），
                #   getattr(self, 'MARRIAGE_EVENTS', None) 恒 None 走 fallback 硬编码
                #   会导致注册表（事项标准.py）更新后此处不同步。直接引用模块级变量。
                _mrg_evts = MARRIAGE_EVENTS
                _cur_ev = ''
                try: _cur_ev = self.event_var.get()
                except Exception: pass
                if _cur_ev in _mrg_evts and _xn in ('除', '危', '执'):
                    _xs = -5
                    _xt = '凶'
                    _xd = f'{_xn}日忌嫁娶'
                content += f"  小黄道: {_xn} ({_xt})"
                if _xs: content += f"  {_xs:+d}分"
                content += "\n"
                if _xd:
                    content += f"    说明: {_xd}\n"
            # 注意："时辰黄道"基于示例午时，不计入黄道综合分，
            # 且分值与说明可能误导用户认为推荐示例时，改由下方【十二时辰吉凶】
            # 逐时辰显示大黄道/建除，此处不再展示。
            content += f"  黄道等级: {huangdao_info.get('huang_dao_level', 'N/A')}\n"
            _hd_total = huangdao_info.get('huang_dao_score', 0)
            # _yj0915：嫁娶场景除/危/执小黄道+5→-5，综合分相应-10
            if _cur_ev in _mrg_evts and _xn in ('除', '危', '执'):
                _hd_total -= 10
            content += f"  黄道综合分: {_hd_total:+d} 分\n"
            if huangdao_info.get('description'):
                content += f"  综合说明: {huangdao_info['description']}\n"
            # 2026-10-02 修8：嫁娶场景黄道等级"大吉"但总等级被降平时，须说明降级原因，
            # 避免用户困惑"黄道大吉为何总等级平"。
            if _cur_ev in _mrg_evts and _xn in ('除', '危', '执'):
                content += (
                    "  注：黄道虽大吉，然小黄道执/除/危日忌嫁娶，"
                    "嫁娶场景整体降格，须慎用并择吉时。\n"
                )
            content += "\n"
        
        # 宜忌信息
        content += f"""【宜忌信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  口径：宜项来自通书黄历/吉神/建除宜等多层；遇冲突时硬门槛优先——
  相主（事主生肖、日柱冲刑）、三煞、山家封禁、建除当日之忌优先于通书宜项，
  通书宜项不覆盖硬性禁忌（硬门槛未犯时方以通书宜项为用）。
"""
        yi_list = detail.get('yi_list', [])
        ji_list = detail.get('ji_list', [])
        # 婚嫁路径：评分扣分项（如大黄道凶日、日主较旺耗夫星）同步到"忌"，
        # 与综合评语保持一致（marriage_details 为 (名称, 分值) 列表，负分为避忌项）
        _md_items = detail.get('marriage_details') or []
        if isinstance(_md_items, list) and _md_items:
            _ji_base = list(ji_list) if isinstance(ji_list, list) else ([ji_list] if ji_list else [])
            for _d in _md_items:
                try:
                    _nm, _sc = _d[0], _d[1]
                except Exception:
                    continue
                if isinstance(_sc, (int, float)) and _sc < 0 and _nm not in _ji_base:
                    _ji_base.append(_nm)
            ji_list = _ji_base
        if yi_list:
            yi_items = yi_list if isinstance(yi_list, list) else yi_list.split(', ')
            content += f"  宜: {', '.join(yi_items)}\n"
        if ji_list:
            ji_items = ji_list if isinstance(ji_list, list) else ji_list.split(', ')
            content += f"  忌: {', '.join(ji_items)}\n"
        content += "\n"
        
        # 神煞信息
        # 2026-10-02 优化：始终渲染【神煞信息】段，无额外神煞时显示占位文案，
        # 保持报告结构完整（与评分详情中的神煞净分是"明细 vs 总分"关系）
        shensha_list = detail.get('shensha_list', [])
        if shensha_list:
            content += """【神煞信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            # 按分值排序显示，并分别显示吉神与凶煞
            sorted_shensha = sorted(shensha_list, key=lambda x: x.get('score', 0) if isinstance(x, dict) else 0, reverse=True)
            ji_items = []
            xiong_items = []
            ping_items = []
            for shensha in sorted_shensha:
                if isinstance(shensha, dict):
                    name = shensha.get('name', '')
                    desc = shensha.get('description', '')
                    score = shensha.get('score', 0)
                    line = f"  {'✓' if score>0 else '✗' if score<0 else '○'} {name}（{score:+.0f}分）: {desc}\n"
                    if score > 0: ji_items.append(line)
                    elif score < 0: xiong_items.append(line)
                    else: ping_items.append(line)
                else:
                    ping_items.append(f"  ○ {shensha}\n")
            if ji_items:
                content += "【吉神(加分项)】\n"
                for it in ji_items: content += it
                content += "\n"
            if xiong_items:
                content += "【凶煞(减分项)】\n"
                for it in xiong_items: content += it
                content += "\n"
            if ping_items:
                content += "【其他神煞】\n"
                for it in ping_items: content += it
                content += "\n"
            content += "\n"
        else:
            content += """【神煞信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  无额外神煞加减分

"""

        # Q4（2026-10-08 拍板）：已制化凶煞不再列忌、不扣忌事分，
        # 独立“山家警告·已制化”区块展示（数据由评分器按警告文本分类注入）
        _mit_warnings = []
        # 直接从 detail 取（与三煞反向枚举同因：块内 sansha_info 为函数参数，
        # 沙箱执行时为{}；detail 路径在真实 GUI 与沙箱均成立）
        _ssi_mit = detail.get('sansha_info') if isinstance(detail.get('sansha_info'), dict) else {}
        if _ssi_mit:
            _mit_warnings = _ssi_mit.get('mountain_warnings_mitigated', []) or []
        elif isinstance(sansha_info, dict):
            _mit_warnings = sansha_info.get('mountain_warnings_mitigated', []) or []
        if _mit_warnings:
            content += """【山家警告 · 已制化】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  以下凶煞本日原有吉神制化，按制化口径不禁用、不作忌项扣分：
"""
            for _mw in _mit_warnings:
                content += f"  • {_mw}\n"
            content += "\n"

        # 评语
        if detail.get('reason'):
            content += f"""【综合评语】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {detail['reason']}

"""
        
        # 修造专属信息（动土方位、时辰吉凶、扶山相主等）
        event_type = self.event_var.get()
        from modules.事项标准 import BUILD_SECTION_UI_EVENTS as construction_events
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
                # 2026-09-16修复：原代码按 owner_info['year_var']/['month_var']/['day_var']
                # /['hour_var']/['minute_var'] 取值，但 owners_info 中真实键名是
                # 'year'/'month'/'day'/'hour'/'minute'（见 _build_owner_inputs 的 owner_info
                # 字典），故 `'year_var' in owner_info` 恒为 False → zhuming 恒为 None，
                # 造成【修造择日分析】缺"主命"行、十二时辰动土吉凶表缺"冲/合主命"项
                # （修造神煞扩展依赖 self.zhuming[1]）。此处改用正确键名，写法与嫁娶块一致。
                owners_info = getattr(self, 'owners_info', [])
                if owners_info:
                    try:
                        owner_info = owners_info[0]
                        if 'year' in owner_info:
                            year_val = owner_info['year'].get() if hasattr(owner_info['year'], 'get') else owner_info.get('year', '')
                            month_val = owner_info['month'].get() if hasattr(owner_info['month'], 'get') else owner_info.get('month', '')
                            day_val = owner_info['day'].get() if hasattr(owner_info['day'], 'get') else owner_info.get('day', '')
                            hour_val = owner_info['hour'].get() if hasattr(owner_info['hour'], 'get') else owner_info.get('hour', '12')
                            minute_val = owner_info['minute'].get() if hasattr(owner_info['minute'], 'get') else owner_info.get('minute', '0')
                            birth_date = date(
                                int(year_val),
                                int(month_val),
                                int(day_val)
                            )
                            _lng = _parse_owner_longitude(owner_info.get('longitude'), show_warning=False)
                            owner_sizhu = calculate_sizhu(birth_date, int(hour_val), int(minute_val), longitude=_lng)
                            zhuming = owner_sizhu.get('年柱', '')
                    except (ValueError, AttributeError):
                        pass
                
                # 构建sizhu字典
                # detail_sizhu 带上真实公历日期，供神煞扩展按高精度农历取月
                # （修复“节气寅月但农历腊月”交界日被月支回退法误判大利月的矛盾）
                _detail_sizhu_src = detail.get('sizhu', {})
                _detail_date = _detail_sizhu_src.get('date') if isinstance(_detail_sizhu_src, dict) else None
                if not hasattr(_detail_date, 'year'):
                    _d_alt = detail.get('date')
                    if hasattr(_d_alt, 'year'):
                        _detail_date = _d_alt
                    elif isinstance(_d_alt, str) and len(_d_alt) >= 10:
                        try:
                            from datetime import datetime as _dt
                            _detail_date = _dt.strptime(_d_alt[:10], '%Y-%m-%d').date()
                        except Exception:
                            _detail_date = None
                detail_sizhu = {
                    'date': _detail_date,
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
                # 2026-09-16 口径统一：标注规范事项，供选时/神煞分值从单一表按事项取数
                # （如日破时：修造类选时 -20 重扣，经 modules/事项标准.py 锁定）
                try:
                    from modules.事项标准 import canonical_event as _canonical_event
                    checker._std_event = _canonical_event(event_type)
                except Exception:
                    pass
                
                # 修造择日分析（2026-09-08：时辰吉凶/建除十二神/十二时辰动土吉凶不依赖坐山，
                # 即使未选坐山也显示；坐山相关项仍判 zuoshan）
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
                
                # 二十四山动土方位（需坐山）
                if zuoshan:
                    lucky_directions = checker.get_lucky_directions(detail_sizhu)
                    safe_dirs = [d for d in lucky_directions if d['分值'] == 0]
                    danger_dirs = [d for d in lucky_directions if d['分值'] < 0]
                    
                    content += "\n  【二十四山动土方位吉凶】\n"
                    content += "  （0分=安全可用，负分=犯煞不宜）\n"
                    content += "  注：四柱不犯三煞不代表所有方位安全，动土方位仍需避犯煞方位\n"
                    
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
                
                # 十二时辰动土吉凶（不依赖坐山，始终显示）
                lucky_hours = checker.get_lucky_hours(detail_sizhu)
                good_hours = [h for h in lucky_hours if h['分值'] > 0]
                bad_hours = [h for h in lucky_hours if h['分值'] < 0]
                
                content += "\n  【十二时辰动土吉凶】\n"
                content += "  （正分=吉时，0分=平，负分=凶时）\n"
                
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
        if event_type in MARRIAGE_EVENTS:
            try:
                from modules.shensha.嫁娶神煞扩展 import MarriageShenShaCheckerExt
                from modules.四柱计算器 import calculate_sizhu
                
                bride_gan = None
                bride_zhi = None
                groom_gan = None
                groom_zhi = None
                bride_m_gan = None
                bride_m_zhi = None
                groom_m_gan = None
                groom_m_zhi = None
                
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
                            bride_m_gan = owner.get('月干', '') or owner.get('month_gan', '')
                            bride_m_zhi = owner.get('月支', '') or owner.get('month_zhi', '')
                            if not bride_gan and owner.get('birth_date'):
                                try:
                                    birth_date = owner['birth_date']
                                    if isinstance(birth_date, str):
                                        from datetime import datetime
                                        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                                    if hasattr(birth_date, 'year'):
                                        owner_sizhu = calculate_sizhu(birth_date,
                                            owner.get('birth_hour', 12),
                                            owner.get('birth_minute', 0),
                                            longitude=owner.get('birth_longitude'))
                                        bride_gan = owner_sizhu.get('年柱', '')[:1]
                                        bride_zhi = owner_sizhu.get('年柱', '')[1:]
                                        bride_m_gan = owner_sizhu.get('月柱', '')[:1]
                                        bride_m_zhi = owner_sizhu.get('月柱', '')[1:]
                                except:
                                    pass
                        elif gender == '男':
                            groom_gan = owner.get('年干', '') or owner.get('year_gan', '')
                            groom_zhi = owner.get('生肖', '') or owner.get('年支', '') or owner.get('year_zhi', '')
                            groom_m_gan = owner.get('月干', '') or owner.get('month_gan', '')
                            groom_m_zhi = owner.get('月支', '') or owner.get('month_zhi', '')
                            if not groom_gan and owner.get('birth_date'):
                                try:
                                    birth_date = owner['birth_date']
                                    if isinstance(birth_date, str):
                                        from datetime import datetime
                                        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                                    if hasattr(birth_date, 'year'):
                                        owner_sizhu = calculate_sizhu(birth_date,
                                            owner.get('birth_hour', 12),
                                            owner.get('birth_minute', 0),
                                            longitude=owner.get('birth_longitude'))
                                        groom_gan = owner_sizhu.get('年柱', '')[:1]
                                        groom_zhi = owner_sizhu.get('年柱', '')[1:]
                                        groom_m_gan = owner_sizhu.get('月柱', '')[:1]
                                        groom_m_zhi = owner_sizhu.get('月柱', '')[1:]
                                except:
                                    pass
                
                # detail_sizhu 带上真实公历日期，供神煞扩展按高精度农历取月
                # （修复“节气寅月但农历腊月”交界日被月支回退法误判大利月的矛盾）
                _detail_sizhu_src = detail.get('sizhu', {})
                _detail_date = _detail_sizhu_src.get('date') if isinstance(_detail_sizhu_src, dict) else None
                if not hasattr(_detail_date, 'year'):
                    _d_alt = detail.get('date')
                    if hasattr(_d_alt, 'year'):
                        _detail_date = _d_alt
                    elif isinstance(_d_alt, str) and len(_d_alt) >= 10:
                        try:
                            from datetime import datetime as _dt
                            _detail_date = _dt.strptime(_d_alt[:10], '%Y-%m-%d').date()
                        except Exception:
                            _detail_date = None
                detail_sizhu = {
                    'date': _detail_date,
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
                    groom_gan=groom_gan, groom_zhi=groom_zhi,
                    bride_month_gan=bride_m_gan, bride_month_zhi=bride_m_zhi,
                    groom_month_gan=groom_m_gan, groom_month_zhi=groom_m_zhi
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
                _cur_status = daliyue_info.get('当前月份状态', '')
                if '大利月' not in _cur_status and '小利月' not in _cur_status:
                    content += f"    说明：当前为非大利月，无加分\n"
                
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
                        # 2026-10-02 修02-05问题5：利月分值已计入五行评分，
                        # 神煞信息区重复展示易误导重复加分，加"已计入"标注。
                        tag = f"{name}（{score:+.0f}分，已计入五行评分）: {desc}"
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
                            # 展示层去重：时支冲日支(=新娘/新郎支)时，"日破时"与
                            # "冲新娘/冲新郎"是同一冲的两个称谓，合并为"日破时/冲X（禁用）"。
                            _raw = list(h.get('说明', []))
                            _has_ribo = any('日破时' in r for r in _raw)
                            _chong_targets = [r for r in _raw if '冲新娘' in r or '冲新郎' in r]
                            if _has_ribo and _chong_targets:
                                _keep = [r for r in _raw if r not in _chong_targets]
                                _suffix = '/'.join(r.split('（')[0] for r in _chong_targets)
                                _merged = []
                                for r in _keep:
                                    if '日破时' in r:
                                        _merged.append(f'日破时/{_suffix}（禁用）')
                                    else:
                                        _merged.append(r)
                                _raw = _merged
                            reasons_str = '、'.join(_raw)
                            if h.get('禁用', False):
                                mark = '✗'
                                content += f"    {mark} {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            elif h['分值'] > 0:
                                mark = '★'
                                content += f"    {mark} {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            elif h['分值'] < 0:
                                mark = '✗'
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
        
        # 通用十二时辰吉凶（安床/安葬/作灶/入宅/开业/出行/移徙/入学/求医/签约等）
        # 修造类(修造/动土/拆舍/装修)与嫁娶类上方已有专属时辰表；
        # 2026-09 补：此前其余事项详情无此时辰表，但四柱段提示语却让用户"参考下方"。
        # 数据源与扫日推荐时柱一致：modules.推荐时柱.build_checker（同一 get_lucky_hours）。
        # 2026-09-17 修复：marriage_events 本地列表已由注册表 MARRIAGE_EVENTS 取代
        # （口径与上方6288嫁娶专属段判断一致：嫁娶/订婚/纳采），漏改会导致 NameError、
        # content 整段无法插入，详情窗口只显示到事主信息。
        if event_type not in construction_events and event_type not in MARRIAGE_EVENTS:
            try:
                from modules.推荐时柱 import build_checker as _build_hour_checker

                _dsrc = detail.get('sizhu', {}) if isinstance(detail, dict) else {}

                def _split_gz(_s):
                    return (_s[:1], _s[1:]) if isinstance(_s, str) and len(_s) >= 2 else ('', '')

                _ddate = _dsrc.get('date') if isinstance(_dsrc, dict) else None
                if not hasattr(_ddate, 'year'):
                    _dalt = detail.get('date') if isinstance(detail, dict) else None
                    if hasattr(_dalt, 'year'):
                        _ddate = _dalt
                    elif isinstance(_dalt, str) and len(_dalt) >= 10:
                        try:
                            from datetime import datetime as _dtx
                            _ddate = _dtx.strptime(_dalt[:10], '%Y-%m-%d').date()
                        except Exception:
                            _ddate = None
                _yg, _yz = _split_gz(_dsrc.get('年柱', ''))
                _mg, _mz = _split_gz(_dsrc.get('月柱', ''))
                _dg, _dz = _split_gz(_dsrc.get('日柱', ''))
                _norm = {
                    'date': _ddate,
                    'year_gan': _yg, 'year_zhi': _yz,
                    'month_gan': _mg, 'month_zhi': _mz,
                    'day_gan': _dg, 'day_zhi': _dz,
                }
                _hour_checker, _ = _build_hour_checker(event_type, None, '')
                lucky_hours = _hour_checker.get_lucky_hours(_norm)
                good_hours = [h for h in lucky_hours
                              if h['分值'] > 0 and not h.get('禁用', False)]
                bad_hours = [h for h in lucky_hours
                             if h['分值'] < 0 or h.get('禁用', False)]

                content += "\n  【十二时辰吉凶】\n"
                content += "  （正分=吉时，0分=平，负分=凶时，禁用=不可用）\n"
                hour_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                for zhi in hour_order:
                    for h in lucky_hours:
                        if h['地支'] == zhi:
                            reasons_str = '、'.join(h.get('说明', []))
                            if h.get('禁用', False):
                                content += f"    ✗ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            elif h['分值'] > 0:
                                content += f"    ★ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            elif h['分值'] < 0:
                                content += f"    ✗ {h['天干']}{h['地支']}时 {h['时辰']}  {h['分值']:+d}分  [{reasons_str}]\n"
                            else:
                                content += f"      {h['天干']}{h['地支']}时 {h['时辰']}  平\n"
                            break
                if good_hours:
                    good_names = '、'.join([f"{h['天干']}{h['地支']}" for h in good_hours])
                    content += f"\n  ★ 吉利时辰（共{len(good_hours)}个）：{good_names}\n"
                if bad_hours:
                    bad_names = '、'.join([f"{h['天干']}{h['地支']}" for h in bad_hours])
                    content += f"  ✗ 凶时/禁用（共{len(bad_hours)}个）：{bad_names}\n"
                # 推荐时柱全局择优 / 时辰表单时评分，两套口径说明（_zjct0914）
                content += ("  注：四柱中的推荐时柱由系统按日课全局综合择优（四柱五行、地支合冲、\n"
                            "事主生肖相合、神煞等整体计分）；本时辰吉凶表仅评单时干支与日柱关系，\n"
                            "两套标准不同，故推荐时柱在表中可能为“平”，请以推荐时柱为主、本表供择时参考。\n")
                content += "\n"
            except Exception as e:
                content += f"\n【十二时辰吉凶】\n  分析出错：{str(e)}\n"

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
        
        # ===== 日课校验器（独立第三方只读通道，2026-10-02 接入）=====
        # 报告渲染完成后自动执行全部已注册规则：ERROR 显著打标，
        # 校验器自身异常明示——不静默吞错，也不阻断详情窗口。
        try:
            from modules.日课校验器 import lint_lesson
            _lint = lint_lesson(
                detail,
                lucky_hours=locals().get('lucky_hours'),
                rendered_content=content,
                bride_year_zhi=locals().get('bride_zhi'))
            content += _lint.format_text()
            # ===== 阶段三：LLM 语义兜底审查 =====
            # 默认关闭；须同时满足：配置 enable_llm_review + 有 API Key。
            # WARN/INFO 级，不阻断报告。失败自动静默降级。
            try:
                import os as _os
                _enable_llm = (
                    _os.environ.get('ENABLE_LLM_REVIEW', '').lower() in ('1', 'true', 'yes')
                    and (_os.environ.get('OPENAI_API_KEY')
                         or _os.environ.get('DASHSCOPE_API_KEY'))
                )
                if _enable_llm:
                    from modules.日课校验器 import llm_review as _llm_review
                    _llm_issues = _llm_review(detail, content, cache={})
                    if _llm_issues:
                        _llm_lines = ['\n\n【语义审查（LLM 辅助）】',
                                      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━']
                        for _li in _llm_issues:
                            _llm_lines.append(f"  {_li.rule_id} [{_li.severity}] {_li.message}")
                            if _li.suggestion:
                                _llm_lines.append(f"      建议：{_li.suggestion}")
                        content += '\n'.join(_llm_lines)
            except Exception:
                pass  # LLM 审查失败不影响主报告
            if _lint.has_error:
                content = (
                    '⛔ 本报告未通过日课校验（ERROR 项见文末），不应直接交付\n'
                    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
                    + content)
                detail_window.title(detail_window.title() + ' [校验未通过]')
        except Exception as _lint_err:
            content += (
                '\n\n【日课校验】\n'
                '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                f'  校验器自身执行异常：{type(_lint_err).__name__}: {_lint_err}\n'
                '  （校验通道故障，不影响报告内容，但须排查校验器）')

        text.insert(tk.END, content)
        # 全文标记：★金色 / ✗红色（content中出现的符号一并着色）
        try:
            pos = '1.0'
            while True:
                pos = text.search('★', pos, tk.END)
                if not pos:
                    break
                text.tag_add("gold_star", pos, f"{pos}+1c")
                pos = f"{pos}+1c"
            pos = '1.0'
            while True:
                pos = text.search('✗', pos, tk.END)
                if not pos:
                    break
                text.tag_add("red_cross", pos, f"{pos}+1c")
                pos = f"{pos}+1c"
        except Exception:
            pass
        # ⚠ 警告图标金色前景（仅图标着色，不充填文字底色）
        try:
            pos = '1.0'
            while True:
                pos = text.search('⚠', pos, tk.END)
                if not pos:
                    break
                if text.get(f"{pos}+1c", f"{pos}+2c") == '️':
                    text.delete(f"{pos}+1c", f"{pos}+2c")  # 去emoji变体符，确保前景色对图标生效
                text.tag_add("warn_icon", pos, f"{pos}+1c")
                pos = f"{pos}+1c"
        except Exception:
            pass
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
                        'date': result.get('date', ''),
                        'lunar': result.get('lunar', ''),
                        'sizhu': result.get('sizhu', ''),
                        'score': result.get('score', 0),
                        'level': result.get('level', '未知'),
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
        """导出结果（支持文本、HTML、PDF格式）"""
        if not self.results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        # 先询问用户想要的导出格式
        from tkinter import simpledialog
        
        export_type = simpledialog.askstring(
            "导出格式",
            "请输入导出格式：\n"
            "  1 - 文本报告 (.txt)\n"
            "  2 - HTML报告 (.html) - 美观专业\n"
            "  3 - JSON数据 (.json) - 二次开发\n"
            "\n"
            "请选择 (1/2/3)：",
            parent=self.root
        )
        
        if not export_type:
            return
        
        try:
            export_type = int(export_type.strip())
        except ValueError:
            messagebox.showwarning("警告", "无效的格式选择")
            return
        
        # 根据选择设置文件类型
        if export_type == 1:
            filetypes = [("文本文件", "*.txt")]
            defaultextension = ".txt"
        elif export_type == 2:
            filetypes = [("HTML文件", "*.html")]
            defaultextension = ".html"
        elif export_type == 3:
            filetypes = [("JSON文件", "*.json")]
            defaultextension = ".json"
        else:
            messagebox.showwarning("警告", "无效的格式选择")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=defaultextension,
            filetypes=filetypes,
            title="导出择日结果"
        )
        
        if not file_path:
            return
        
        try:
            if export_type == 3:
                # JSON格式
                export_data = {
                    'event_type': self.event_var.get(),
                    'start_date': self.start_date.get(),
                    'end_date': self.end_date.get(),
                    'results': self.results
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"JSON数据已导出到：\n{file_path}")
                
            elif export_type in [1, 2]:
                # 导入报告生成器
                try:
                    from modules.报告生成器 import generate_report
                except ImportError:
                    from 报告生成器 import generate_report
                
                # 准备数据
                # 2026-09-17 修复 Bug2：实例属性是 self.shan_xiang（无 _var 后缀，
                #   见 L1184/L1210）；原写法 hasattr(self,'shan_xiang_var') 永远 False
                #   导致 HTML/文本报告坐山信息恒为空。
                _sv = getattr(self, 'shan_xiang', None)
                shan_xiang = _sv.get() if hasattr(_sv, 'get') else (_sv or None)
                
                # 转换results为报告生成器需要的格式
                report_results = []
                for r in self.results:
                    result_dict = {
                        'date': r.get('date', ''),
                        'score': r.get('score', 0),
                        'level': r.get('level', '-'),
                        'sizhu': r.get('sizhu', {}),
                        'yi_list': r.get('yi_list', []),
                        'ji_list': r.get('ji_list', []),
                        'shensha_list': r.get('shensha_list', []),
                        'sansha_info': r.get('sansha_info', {})
                    }
                    
                    # 如果有detail字段，从中提取更多信息
                    detail = r.get('detail', {})
                    if detail:
                        if not result_dict['yi_list']:
                            result_dict['yi_list'] = detail.get('yi_list', [])
                        if not result_dict['ji_list']:
                            result_dict['ji_list'] = detail.get('ji_list', [])
                        if not result_dict['shensha_list']:
                            result_dict['shensha_list'] = detail.get('shensha_list', [])
                        if not result_dict['sansha_info']:
                            result_dict['sansha_info'] = detail.get('sansha_info', {})
                    
                    report_results.append(result_dict)
                
                # 生成报告
                generator = generate_report(
                    report_results,
                    self.event_var.get(),
                    self.start_date.get(),
                    self.end_date.get(),
                    shan_xiang,
                    self.owners_info
                )
                
                if export_type == 1:
                    generator.save_text(file_path)
                    messagebox.showinfo("成功", f"文本报告已导出到：\n{file_path}")
                else:
                    generator.save_html(file_path)
                    messagebox.showinfo(
                        "成功",
                        f"HTML报告已导出到：\n{file_path}\n\n"
                        "提示：可在浏览器中打开查看，或使用Ctrl+P打印为PDF"
                    )
        except Exception as e:
            import traceback
            traceback.print_exc()
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
                                _fmt_tree_date_sizhu(result.get('date', ''), result.get('sizhu', result.get('四柱', '-'))),
                                result.get('score', '-'),
                                result.get('level', '-'),
                                self._fmt_score(result.get('wuxing_score', '-'), '-'),
                                self._fmt_score(result.get('yueling_score', '-'), '-'),
                                self._fmt_score(result.get('xishen_score', '-'), '-'),
                                self._fmt_score(result.get('huangdao_score', '-'), '-'),
                                _fmt_tree_relation(result.get('dizhi_relation', '-')),
                                result.get('jishen', result.get('yi', '-')),
                                result.get('daliyue', '-'),
                                result.get('owners', '-'),
                                result.get('feixing', '-')
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
                                _fmt_tree_date_sizhu(result.get('date', ''), result.get('sizhu', result.get('四柱', '-'))),
                                result.get('score', '-'),
                                result.get('level', '-'),
                                self._fmt_score(result.get('wuxing_score', '-'), '-'),
                                self._fmt_score(result.get('yueling_score', '-'), '-'),
                                self._fmt_score(result.get('xishen_score', '-'), '-'),
                                self._fmt_score(result.get('huangdao_score', '-'), '-'),
                                _fmt_tree_relation(result.get('dizhi_relation', '-')),
                                result.get('jishen', result.get('yi', '-')),
                                result.get('daliyue', '-'),
                                result.get('owners', '-'),
                                result.get('feixing', '-')
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
                            _fmt_tree_date_sizhu(result.get('date', ''), result.get('sizhu', result.get('四柱', '-'))),
                            result.get('score', '-'),
                            result.get('level', '-'),
                            self._fmt_score(result.get('wuxing_score', '-'), '-'),
                            self._fmt_score(result.get('yueling_score', '-'), '-'),
                            self._fmt_score(result.get('xishen_score', '-'), '-'),
                            self._fmt_score(result.get('huangdao_score', '-'), '-'),
                            _fmt_tree_relation(result.get('dizhi_relation', '-')),
                            result.get('jishen', result.get('yi', '-')),
                            result.get('daliyue', '-'),
                            result.get('owners', '-'),
                            result.get('feixing', '-')
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
        """打开日课评分系统（完整版：标题+事主信息+特殊选项+输入+按钮+列表+结果，所有区块齐全）"""
        try:
            from modules.日课评分系统 import DayScoreWindow
            # 传递主程序窗口作为master参数，创建Toplevel窗口
            score_window = DayScoreWindow(master=self.root, mode='full')
            
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
                        'minute': int(minute_str),
                        'longitude': _parse_owner_longitude(owner.get('longitude'), show_warning=False)
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
        """将所有择日结果导入到评分系统（embedded 精简版：仅显示日课输入+按钮+日课列表+评分结果）"""
        if not self.results:
            messagebox.showwarning("提示", "没有可导入的择日结果")
            return

        try:
            from modules.日课评分系统 import DayScoreWindow
            # 精简版：按用户需求隐藏 标题/事主信息/特殊选项 等不相关区块
            # 2026-09-17 修复 Bug3：embedded 模式仍依赖 master 创建 Toplevel，
            #   缺 master 会抛异常。与 open_score_system L7116 同步补 master=self.root。
            score_window = DayScoreWindow(master=self.root, mode='embedded')
            
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
                        'minute': int(minute_str),
                        'longitude': _parse_owner_longitude(owner.get('longitude'), show_warning=False)
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
    
    def open_taishen_query(self):
        """打开胎神查询窗口"""
        try:
            from modules.胎神查询 import TaishenQueryDialog
            TaishenQueryDialog(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"打开胎神查询失败：{str(e)}")

    def open_zeeri_tie(self):
        """打开择日贴窗口（并载入右键暂存的日课）"""
        try:
            from modules.择日贴 import show_zeri_tie
            pad = show_zeri_tie(self.root)
            pending = list(getattr(self, '_zeri_tie_pending', []))
            for entry in pending:
                pad.add_entry(entry)
            if pending:
                self._zeri_tie_pending = []
                self._update_zeeri_tie_btn()
        except Exception as e:
            messagebox.showerror("错误", f"打开择日贴失败：{str(e)}")

    def _update_zeeri_tie_btn(self):
        """更新面板「择日贴」按键文字（显示暂存课数）"""
        if not hasattr(self, 'zeeri_tie_btn'):
            return
        n = len(getattr(self, '_zeri_tie_pending', []))
        self.zeeri_tie_btn.configure(text=f"择日贴({n})" if n else "择日贴")

    def _xk_click_schedule(self, event):
        """左键单击结果行 → 延迟 280ms 弹玄空分析提示（双击时由 on_result_double_click 取消）。"""
        try:
            row_id = self.result_tree.identify_row(event.y)
            if not row_id:
                return
            # 确保该行被选中
            self.result_tree.selection_set(row_id)
            self.result_tree.focus(row_id)
            if getattr(self, '_xk_after', None):
                try:
                    self.root.after_cancel(self._xk_after)
                except Exception:
                    pass
            self._xk_after = self.root.after(280, lambda: self.on_result_xuankong_prompt(row_id))
        except Exception:
            pass

    def open_xuankong(self):
        if self._get_zeli_mode() != 'feixing':
            return  # _zm0915 纯正五行模式不打开玄空飞星窗口
        """主界面【玄空飞星】按钮：直接打开玄空飞星排盘(自动带入当前开始日期/坐山兼向，无需先扫描)。"""
        try:
            import importlib
            xk_mod = importlib.import_module('玄空飞星_日课展示')
            y = mo = dd = None
            try:
                import datetime as _dt
                d0 = _dt.datetime.strptime(str(self.start_date.get()), "%Y-%m-%d").date()
                y, mo, dd = d0.year, d0.month, d0.day
            except Exception:
                pass
            mountain = None
            sx = getattr(self, 'shan_xiang', None)
            sx_v = sx.get() if hasattr(sx, 'get') else (sx or '')
            if sx_v and '山' in sx_v:
                mountain = sx_v.split('山')[0].strip()
            jianxiang = '正向'
            jx = getattr(self, 'jian_xiang', None)
            jx_v = (jx.get() if hasattr(jx, 'get') else '') or ''
            mcw = getattr(xk_mod, 'MOUNTAINS_CW', None)
            if mountain and jx_v and jx_v != '正中' and mcw and mountain in mcw:
                idx = mcw.index(mountain)
                left_m = mcw[(idx - 1) % 24]
                right_m = mcw[(idx + 1) % 24]
                if jx_v.startswith('兼') and len(jx_v) >= 2:
                    jx_shan = jx_v[1:]
                    if jx_shan in (left_m, right_m):
                        jianxiang = f"兼{jx_shan}"
                    elif jx_v == '兼左':
                        jianxiang = f"兼{left_m}"
                    elif jx_v == '兼右':
                        jianxiang = f"兼{right_m}"
                elif jx_v == '兼左':
                    jianxiang = f"兼{left_m}"
                elif jx_v == '兼右':
                    jianxiang = f"兼{right_m}"
            preset = {'year': y, 'month': mo, 'day': dd,
                      'hour': 12, 'minute': 0,
                      'mountain': mountain, 'jianxiang': jianxiang}
            win = tk.Toplevel(self.root)
            xk_mod.XuanKongApp(win, preset=preset)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("玄空飞星", f"打开玄空飞星失败：{e}")

    def on_result_xuankong_prompt(self, row_id=None):
        if self._get_zeli_mode() != 'feixing':
            return  # _zm0915 纯正五行模式不进行玄空飞星分析
        """左键单击日期 → 询问是否用玄空飞星分析；确认后自动带入日期/时柱/坐山兼向开窗分析。"""
        self._xk_after = None
        try:
            if row_id is None:
                sel = self.result_tree.selection()
                if not sel:
                    return
                row_id = sel[0]
            values = self.result_tree.item(row_id, 'values')
            if not values:
                return
            date_cell = str(values[0] or '')
            cell_lines = [ln.strip() for ln in date_cell.splitlines() if ln.strip()]
            date_str = cell_lines[0] if cell_lines else ''

            # 找完整结果，取权威四柱（与双击详情同一口径）
            result = None
            for r in self.results:
                if r.get('date', '') == date_str:
                    result = r
                    break
            auth_sizhu = ''
            if len(cell_lines) >= 2:
                pp = cell_lines[1].split()
                if len(pp) == 4 and all(len(p) >= 2 for p in pp):
                    auth_sizhu = ' '.join(pp)
            if not auth_sizhu and result:
                auth_sizhu = str(result.get('sizhu', '') or '').strip()

            # 日期
            y = mo = dd = None
            try:
                import datetime as _dt
                d0 = _dt.date.fromisoformat(date_str)
                y, mo, dd = d0.year, d0.month, d0.day
            except Exception:
                pass

            # 时柱时支 → 时辰（时支起时，如申→16）
            ZHI2H = {'子': 0, '丑': 2, '寅': 4, '卯': 6, '辰': 8, '巳': 10,
                     '午': 12, '未': 14, '申': 16, '酉': 18, '戌': 20, '亥': 22}
            hour = 12
            parts = auth_sizhu.split()
            if len(parts) == 4 and len(parts[3]) >= 2:
                hour = ZHI2H.get(parts[3][1], 12)

            # 坐山（单字）与兼向（玄空"正向/兼X"）
            mountain = None
            sx = getattr(self, 'shan_xiang', None)
            sx_v = sx.get() if hasattr(sx, 'get') else (sx or '')
            if sx_v and '山' in sx_v:
                mountain = sx_v.split('山')[0].strip()
            jianxiang = '正向'
            jx = getattr(self, 'jian_xiang', None)
            jx_v = (jx.get() if hasattr(jx, 'get') else '') or ''
            xk_mod = None
            try:
                import importlib
                xk_mod = importlib.import_module('玄空飞星_日课展示')
            except Exception as e:
                print(f"[玄空] 模块加载失败: {e}")
            # 主界面兼向下拉的实际值是"兼+相邻山"（如寅山→兼艮/兼甲），与玄空模块兼向选项
            # 同一24山序、文字一致；"正中"→正向。兼左/兼右为旧占位值，按邻山兜底。
            mcw = getattr(xk_mod, 'MOUNTAINS_CW', None)
            if mountain and jx_v and jx_v != '正中' and mcw and mountain in mcw:
                idx = mcw.index(mountain)
                left_m = mcw[(idx - 1) % 24]    # 罗盘逆时针邻山
                right_m = mcw[(idx + 1) % 24]   # 罗盘顺时针邻山
                if jx_v.startswith('兼') and len(jx_v) >= 2:
                    jx_shan = jx_v[1:]
                    if jx_shan in (left_m, right_m):
                        jianxiang = f"兼{jx_shan}"
                    elif jx_v == '兼左':
                        jianxiang = f"兼{left_m}"
                    elif jx_v == '兼右':
                        jianxiang = f"兼{right_m}"
                elif jx_v == '兼左':
                    jianxiang = f"兼{left_m}"
                elif jx_v == '兼右':
                    jianxiang = f"兼{right_m}"

            # 提示
            info = f"日期：{date_str}\n四柱：{auth_sizhu}\n"
            if mountain:
                jx_txt = '正向' if jianxiang == '正向' else jianxiang
                info += f"坐山：{mountain}（{jx_txt}）\n"
            else:
                info += "（当前事项未设坐山，飞星窗口将默认子山，可在窗口内另行选择）\n"
            if not messagebox.askyesno("玄空飞星分析",
                                       f"是否对该日课进行【玄空飞星】分析？\n\n{info}\n确认后将自动带入以上信息并排盘。"):
                return

            if xk_mod is None:
                import importlib
                xk_mod = importlib.import_module('玄空飞星_日课展示')

            preset = {
                'year': y, 'month': mo, 'day': dd,
                'hour': hour, 'minute': 0,
                'mountain': mountain, 'jianxiang': jianxiang,
            }
            win = tk.Toplevel(self.root)
            xk_mod.XuanKongApp(win, preset=preset)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("玄空飞星", f"打开玄空飞星分析失败：{e}")

    def on_result_right_click(self, event):
        """择日结果右键菜单：加入择日贴"""
        row_id = self.result_tree.identify_row(event.y)
        if not row_id:
            return
        self.result_tree.selection_set(row_id)
        self.result_tree.focus(row_id)
        values = self.result_tree.item(row_id, 'values')
        if not values:
            return
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="加入择日贴", command=lambda: self.add_result_to_zeri_tie(values))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def add_result_to_zeri_tie(self, values):
        """把选中的日课暂存到择日贴（不弹窗，点面板「择日贴」按键时统一载入）"""
        try:
            def _v(i):
                return str(values[i]) if len(values) > i else ''

            def _vv(x):
                return x.get() if x and hasattr(x, 'get') else (str(x) if x else '')

            # 首列"日期/四柱"为两行文本（2026-09-03起）：第一行日期、第二行四柱
            _cell_lines = [ln.strip() for ln in _v(0).splitlines() if ln.strip()]
            entry = {
                'date': _cell_lines[0] if _cell_lines else _v(0),
                'score': _v(1),
                'level': _v(2),
                'sizhu': _cell_lines[1] if len(_cell_lines) > 1 else '',
                'jishen': _v(8),
                'owners': _v(10),
                'event_type': self.event_var.get() if hasattr(self, 'event_var') else '',
            }

            def _parse_owner(info):
                """通用：解析 UI owner_info → 扁平 dict（name/role/year_gz/year_sx/sizhu/阴阳胎/夫星子星）。
                婚嫁专用字段只在女/新娘身上才生成 fu/zi/yintai；男/新郎身上生成 yangqi；其他事件为通用 life dict。"""
                if not info:
                    return None
                name = _vv(info.get('name'))
                gender = _vv(info.get('gender'))
                role = info.get('role') or ('乾造' if gender == '男' else ('坤造' if gender == '女' else '事主'))

                # 四柱（优先 sizhu_var 已算好的，否则输入值兜底现场算）
                sizhu = ''
                sz_var = info.get('sizhu_var')
                if sz_var and hasattr(sz_var, 'get'):
                    s = sz_var.get()
                    if s and s != '未计算':
                        sizhu = s
                if not sizhu or sizhu == '未计算':
                    ys, ms, ds, hs, mis = [_vv(info.get(k, '')) for k in ('year', 'month', 'day', 'hour', 'minute')]
                    if ys and ms and ds:
                        try:
                            from modules.四柱计算器 import calculate_sizhu
                            yy, mo, dd = int(ys), int(ms), int(ds)
                            hh = int(hs) if hs else 12
                            mm = int(mis) if mis else 0
                            ct_var = info.get('calendar_type_var')
                            if ct_var and hasattr(ct_var, 'get') and ct_var.get() == 'lunar':
                                # 农历→公历（2026-09-29 修复，001 §45）：
                                # 原写法 import 不存在的模块级 lunar_to_solar 且期待
                                # tuple（实际为 converter 类方法、返回 dict），ImportError
                                # 被 except:pass 吞掉 → 农历输入静默按公历排盘。
                                # 改走与 calculate_owner_sizhu L2438 同一路径，失败显式
                                # 上抛（由本函数外层 messagebox.showerror 提示）。
                                from modules.高精度农历转换 import get_lunar_converter
                                _sd = get_lunar_converter().lunar_to_solar(yy, mo, dd, hh, mm, 0)
                                yy, mo, dd = _sd['year'], _sd['month'], _sd['day']
                            r = calculate_sizhu((yy, mo, dd), hh, mm,
                                                longitude=_parse_owner_longitude(info.get('longitude'), show_warning=False))
                            sz_list = [r.get(k, '') for k in ('年柱', '月柱', '日柱', '时柱')]
                            if all(sz_list):
                                sizhu = ' '.join(sz_list)
                        except Exception as _e:
                            # 不再 except:pass 静默吞错：坏日期/转换失败须显式报错，
                            # 避免错误四柱静默进入择日贴（外层 showerror 统一提示）
                            raise ValueError(f"事主 {name or ''} 四柱现场计算失败: {_e}") from _e

                year_gz = ''
                year_sx = ''
                if sizhu and len(sizhu) >= 2:
                    p = sizhu.split()
                    if p:
                        year_gz = p[0][:2]
                    try:
                        from modules.今日黄历 import SHENGXIAO_MAP
                        if len(year_gz) >= 2:
                            year_sx = SHENGXIAO_MAP.get(year_gz[1], '')
                    except Exception:
                        pass

                out = {'name': name, 'role': role, 'sizhu': sizhu,
                       'year_gz': year_gz, 'year_sx': year_sx,
                       'year': _vv(info.get('year')),
                       'month': _vv(info.get('month')),
                       'day': _vv(info.get('day')),
                       'hour': _vv(info.get('hour')),
                       'minute': _vv(info.get('minute')),
                       'gender': gender}

                # 婚嫁专用附加字段（只针对新郎新娘，其他类事件自然为空）
                try:
                    from modules.工具函数 import get_fuzi, get_yintai, get_yangqi
                except Exception:
                    get_fuzi = get_yintai = get_yangqi = None
                parts = sizhu.split() if sizhu else []
                if len(parts) == 4 and all(len(p) >= 2 for p in parts):
                    y_g, y_z = parts[0][0], parts[0][1]
                    m_g, m_z = parts[1][0], parts[1][1]
                    if gender == '女' or role == '新娘' or role == '坤造':
                        if get_fuzi and y_g and y_z:
                            try:
                                fz = get_fuzi(y_g, y_z)
                                out['fu'] = fz.get('fu', '')
                                out['zi'] = fz.get('zi', '')
                            except Exception:
                                pass
                        if get_yintai and m_g and m_z:
                            try:
                                out['yintai'] = get_yintai(m_g, m_z)
                            except Exception:
                                pass
                    if gender == '男' or role == '新郎' or role == '乾造':
                        if get_yangqi and m_g and m_z:
                            try:
                                out['yangqi'] = get_yangqi(m_g, m_z)
                            except Exception:
                                pass
                # UI 变量设置的 fuzi/yintai/yangqi （用户手动点过"计算四柱"）优先
                fuzi = info.get('fuzi_var')
                if fuzi and hasattr(fuzi, 'get'):
                    t = fuzi.get()
                    if t and t not in ('未计算', ''):
                        if '：' in t:
                            try:
                                _, v = t.split('：', 1)
                                if '子星' in v:
                                    a, b = v.split('，子星：')
                                    out.setdefault('fu', a.strip())
                                    out.setdefault('zi', b.strip())
                            except Exception:
                                pass
                for k, ik in (('yintai_var', 'yintai'), ('yangqi_var', 'yangqi')):
                    v_var = info.get(k)
                    if v_var and hasattr(v_var, 'get'):
                        t = v_var.get()
                        if t and t not in ('未计算', '', '未知'):
                            out[ik] = t
                return out

            # -------- 通用：所有事件都打包 owners_list（仙命/孝子/父/母/宅主/福主 都是靠 role 分的）--------
            owners_list = []
            for info in getattr(self, 'owners_info', []):
                d = _parse_owner(info)
                if d is not None:
                    owners_list.append(d)
            if owners_list:
                entry['owners_list'] = owners_list

            # -------- 通用：修造/动土/入宅/安葬 → 打包山向 + 分金 --------
            event_type = entry.get('event_type', '') or ''
            if event_type in {'修造', '拆舍', '作灶', '安床', '动土', '入宅', '安葬'}:
                try:
                    shan_var = getattr(self, 'shan_xiang', None)
                    shan = shan_var.get() if shan_var and hasattr(shan_var, 'get') else ''
                    # 兼向（若有"正中"就不加，否则拼山向+兼向）
                    jv = getattr(self, 'jian_xiang_var', None)
                    jian = ''
                    if jv and hasattr(jv, 'get'):
                        jian = jv.get() or ''
                    if jian and jian not in ('正中', '-', '—'):
                        shan = (shan or '') + jian
                    entry['shan_xiang'] = shan
                    # 分金：直接现场调用二十四山 selector → 取 fengjin_ganzhi（庚寅 干支）
                    fj_ganzhi = ''
                    try:
                        from modules.二十四山 import ZhengTiWuXingSelectorDB
                        sz_parts = str(entry.get('sizhu', '') or '').split()
                        if len(sz_parts) == 4 and shan:
                            mn = shan[:1]  # 山名：乾山巽向→乾，子山午向→子
                            if '山' in shan and shan.index('山') > 0:
                                mn = shan[:shan.index('山')]
                            sel = ZhengTiWuXingSelectorDB()
                            fj_r = sel.evaluate_with_fengjin(
                                mn, jian or '正中', sz_parts[0], sz_parts[1], sz_parts[2], sz_parts[3]
                            )
                            if isinstance(fj_r, dict):
                                fj_ganzhi = str(fj_r.get('fengjin_ganzhi') or '')
                    except Exception:
                        fj_ganzhi = ''
                    if fj_ganzhi:
                        entry['fenjin'] = fj_ganzhi
                    else:
                        # 兜底：若 UI 有 fenjin_var 可读
                        fjv = getattr(self, 'fenjin_var', None)
                        if fjv and hasattr(fjv, 'get'):
                            fj = fjv.get() or ''
                            if fj:
                                entry['fenjin'] = fj
                except Exception:
                    pass

            # -------- 婚嫁事项：附加乾造/坤造八字、夫星子星、阴阳胎等（择日贴用"嫁娶吉帖"模板）--------
            if event_type in {'嫁娶', '订婚', '纳采'}:
                groom = bride = None
                for info in getattr(self, 'owners_info', []):
                    role = info.get('role') or ''
                    gender = _vv(info.get('gender'))
                    if role == '新郎' or (not groom and gender == '男'):
                        groom = info
                    if role == '新娘' or (not bride and gender == '女'):
                        bride = info
                entry['groom'] = _parse_owner(groom)
                entry['bride'] = _parse_owner(bride)
                if entry.get('bride'):
                    entry.setdefault('fu_xing', entry['bride'].get('fu', ''))
                    entry.setdefault('zi_xing', entry['bride'].get('zi', ''))
        except Exception as err:
            messagebox.showerror("错误", f"加入择日贴失败：{str(err)}")
            return

        # 嫁娶吉帖补数据（2026-09-06用户建议）：按日期取完整结果 reason（含不将日/天德/月德等关键吉神）
        try:
            _d0 = entry.get('date', '')
            for _r in getattr(self, 'results', []) or []:
                if _r.get('date', '') == _d0:
                    entry.setdefault('reason', str(_r.get('reason', '') or ''))
                    break
        except Exception:
            pass

        # 同日期同用事去重（与择日贴窗口规则一致，后加覆盖先加）
        key = (entry['date'], entry['event_type'] or '')
        self._zeri_tie_pending = [x for x in getattr(self, '_zeri_tie_pending', [])
                                  if (x['date'], x.get('event_type') or '') != key]
        self._zeri_tie_pending.append(entry)
        self._update_zeeri_tie_btn()
        et = entry.get('event_type') or ''
        hint_map = {
            '嫁娶': '（嫁娶吉帖·红纸）',
            '订婚': '（纳彩请期吉课·红纸）',
            '纳采': '（纳彩请期吉课·红纸）',
            '修造': '（兴工修造吉课·红纸）',
            '拆舍': '（兴工修造吉课·红纸）',
            '作灶': '（兴工修造吉课·红纸）',
            '安床': '（兴工修造吉课·红纸）',
            '动土': '（兴工动土吉课·红纸）',
            '入宅': '（乔迁入宅吉课·红纸）',
            '安葬': '（福地进金安葬·白纸）',
        }
        hint = hint_map.get(et, '')
        messagebox.showinfo("已加入择日贴",
                            f"{entry['date']} 日课已暂存到择日贴{hint}（共 {len(self._zeri_tie_pending)} 课）。\n"
                            f"点击主面板「择日贴」按键即可查看。")

    def open_today_huangli(self):
        """打开今日黄历查询（完整版）"""
        try:
            from modules.今日黄历 import TodayHuangLiDialog
            TodayHuangLiDialog(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"打开今日黄历失败：{str(e)}")

    def open_bazi_panpan(self):
        """打开八字排盘"""
        try:
            show_bazi_input_dialog(self.root)
        except Exception as e:
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

【星级标准】（等级由综合评分唯一决定，同分同级）
⭐⭐⭐⭐⭐ (5星) = 上吉（105分以上）
⭐⭐⭐⭐ (4星) = 大吉（100-104分）
⭐⭐⭐ (3星) = 吉（85-99分）
⭐⭐ (2星) = 中吉（75-84分）
⭐ (1星) = 平（60-74分）
❌ (0星) = 凶（<60分，或五行评分<60）
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
   - 夫子星按新娘年柱推算
   - 阴胎：取新娘（女命）生月月柱，月干进1位、月支进3位（胎元法）
   - 阳气：取新郎（男命）生月月柱，与阴胎同法（月干+1、月支+3）；男称阳气、女称阴胎
   - 嫁娶日课日支忌冲阴胎、阳气（"犯阴胎""犯阳气"各扣30分）；时支冲者该时辰在【十二时辰婚嫁吉凶】中标记禁用；依据《协纪辨方书》《选择求真·卷五》
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

# 2026-09-14 补丁指纹 nayin-jishen-zaoxiang：纳音齐备明细/吉神口径/灶向依据
