# -*- coding: utf-8 -*-
"""
================================================================================
日课评分系统模块
================================================================================
专业级日课评分系统，支持多种输入方式和详细评分分析

使用方法:
    1. 作为主程序导入: from modules.日课评分系统 import DayScoreWindow
    2. 直接运行: python -m modules.日课评分系统
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, date
import json
import os
import sys

# 处理导入
# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# 添加 modules 目录到路径
modules_dir = os.path.dirname(os.path.abspath(__file__))
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

# 定义备用函数
def _mock_calculate_sizhu(*args, **kwargs):
    return {'年柱': '甲子', '月柱': '甲子', '日柱': '甲子', '时柱': '甲子'}

def _mock_analyze_sizhu(*args, **kwargs):
    return {}

def _mock_calculate_score(*args, **kwargs):
    return {
        'score': 0, 
        'level': '平', 
        'yi_list': [], 
        'ji_list': [],
        'shensha_list': [],
        'score_details': {
            '基础分': 100,
            '月令得分': 0,
            '月令详细': {
                '旺衰得分': 0,
                '支支关系得分': 0
            },
            '喜用神得分': 0,
            '黄道得分': 0,
            '总分': 0,
            '事主匹配': []
        },
        'wu_xing_result': {
            'details': {
                '地支关系': [],
                '吉神': [],
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
        'reason': '此日为黄道吉日，适合各项事务。'
    }

def _mock_calculate_xishen_yongshen(*args, **kwargs):
    return ('', '')

def _mock_get_shan_xiang_list():
    return []

def _mock_show_compass_dialog(*args, **kwargs):
    pass

def _mock_shan_xiang_to_shan(shan_xiang):
    """备用的山向转坐山函数"""
    if shan_xiang:
        return shan_xiang.split('山')[0] if '山' in shan_xiang else shan_xiang
    return ''

# 初始化所有导入的名称为备用值
calculate_sizhu = _mock_calculate_sizhu
analyze_sizhu = _mock_analyze_sizhu
calculate_score = _mock_calculate_score
calculate_xishen_yongshen = _mock_calculate_xishen_yongshen
get_shan_xiang_list = _mock_get_shan_xiang_list
show_compass_dialog = _mock_show_compass_dialog
shan_xiang_to_shan = _mock_shan_xiang_to_shan

# 添加日志记录器
import logging
logger = logging.getLogger(__name__)

# 尝试多种导入方式
try:
    # 尝试相对导入（作为模块导入时）
    from .四柱计算器 import calculate_sizhu, analyze_sizhu
    from .评分器 import calculate_score
    from .喜用神计算器 import calculate_xishen_yongshen
    from .二十四山 import get_shan_xiang_list, shan_xiang_to_shan
    from .电子罗盘 import show_compass_dialog
    print("✓ 成功: 从相对路径导入模块")
except ImportError:
    try:
        # 尝试绝对导入（直接运行时）
        from modules.四柱计算器 import calculate_sizhu, analyze_sizhu
        from modules.评分器 import calculate_score
        from modules.喜用神计算器 import calculate_xishen_yongshen
        from modules.二十四山 import get_shan_xiang_list, shan_xiang_to_shan
        from modules.电子罗盘 import show_compass_dialog
        print("✓ 成功: 从 modules 导入模块")
    except ImportError:
        try:
            # 最后尝试直接导入
            from 四柱计算器 import calculate_sizhu, analyze_sizhu
            from 评分器 import calculate_score
            from 喜用神计算器 import calculate_xishen_yongshen
            from 二十四山 import get_shan_xiang_list, shan_xiang_to_shan
            from 电子罗盘 import show_compass_dialog
            print("✓ 成功: 直接导入模块")
        except ImportError as e:
            print(f"✗ 警告: 导入模块失败，使用备用函数 - {e}")
            # 使用预先定义的备用值
            pass

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
            # 强制设置Toplevel窗口的背景色和文本颜色
            self.window.configure(bg='white')
        
        # 获取屏幕尺寸并设置窗口大小
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置为屏幕的90%大小，与主程序一致
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.state('zoomed')  # 窗口最大化，与主程序一致
        
        # 确保窗口显示
        self.window.deiconify()
        
        # 数据存储
        self.date_list = []
        self.scoring_results = []
        self.owners_info = []
        self._owner_entries_list = []  # 存储所有事主的输入框，用于键盘导航
        
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
            # 清空并更新事主信息框架
            self.update_owners_frame()
            # 更新特殊选项
            self.update_special_options()
            
            # 强制刷新界面（Toplevel窗口需要更强的刷新）
            self.window.update_idletasks()
            self.window.update()
            
            # 重新打包框架以确保布局更新
            self.owners_frame.pack_forget()
            self.owners_frame.pack(fill=tk.X, pady=6, padx=20)
            self.special_frame.pack_forget()
            self.special_frame.pack(fill=tk.X, pady=3)
            
            # 再次强制刷新，确保Toplevel窗口完全更新
            self.window.update_idletasks()
            self.window.update()
            
            # 如果是Toplevel窗口，确保窗口可见并置顶
            if isinstance(self.window, tk.Toplevel):
                self.window.lift()
                self.window.focus_force()
                self.window.deiconify()
                self.window.update_idletasks()
                self.window.update()
            
            # 填充事主信息
            for i, owner_data in enumerate(owners_data):
                if i < len(self.owners_info):
                    # 填充公历日期
                    self.owners_info[i]['solar_year'].set(str(owner_data.get('year', '')))
                    self.owners_info[i]['solar_month'].set(str(owner_data.get('month', '')))
                    self.owners_info[i]['solar_day'].set(str(owner_data.get('day', '')))
                    self.owners_info[i]['hour'].set(str(owner_data.get('hour', 12)))
                    self.owners_info[i]['minute'].set(str(owner_data.get('minute', 0)))
                    
                    # 自动计算四柱
                    self.calculate_owner_sizhu(
                        self.owners_info[i]['solar_year'],
                        self.owners_info[i]['solar_month'],
                        self.owners_info[i]['solar_day'],
                        self.owners_info[i]['lunar_year'],
                        self.owners_info[i]['lunar_month'],
                        self.owners_info[i]['lunar_day'],
                        self.owners_info[i]['leap'],
                        self.owners_info[i]['hour'],
                        self.owners_info[i]['minute'],
                        self.owners_info[i]['name'],
                        self.owners_info[i]['sizhu_var'],
                        self.owners_info[i]['xishen_var'],
                        self.owners_info[i]['yongshen_var'],
                        self.owners_info[i].get('fuzi_var'),
                        self.owners_info[i].get('date_type_var'),
                        self.owners_info[i].get('gender_var')
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
                    wuxing_score = score_details.get('五行评分', 100)
                    yueling_score = score_details.get('月令得分', 0)
                    xishen_score = score_details.get('喜用神得分', 0)
                    huangdao_score = score_details.get('黄道得分', 0)
                    
                    # 获取地支关系信息（从wu_xing_result中获取详细地支关系）
                    wu_xing_result = result.get('wu_xing_result', detail.get('wu_xing_result', {}))
                    wu_xing_details = wu_xing_result.get('details', {})
                    
                    # 构建地支关系文本（显示具体的三合、六合等）
                    dizhi_relations = wu_xing_details.get('地支关系', [])
                    if dizhi_relations:
                        # 提取地支关系的简短描述
                        dizhi_text_list = []
                        for relation in dizhi_relations:
                            # 提取关键信息，如"三合火局"、"六合"等
                            if '三合' in relation:
                                # 提取"三合X局"
                                import re
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
                                # 其他关系，取前10个字符
                                dizhi_text_list.append(relation[:10])
                        dizhi_text = ', '.join(dizhi_text_list[:2])  # 最多显示2个关系
                    else:
                        dizhi_text = '-'
                    
                    # 获取吉神信息（从wu_xing_details中获取详细吉神）
                    jishen_list = wu_xing_details.get('吉神', [])
                    if jishen_list:
                        # 提取吉神的简短描述
                        jishen_text_list = []
                        for jishen in jishen_list:
                            # 提取关键信息，如"天德贵人"、"禄神"等
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
                                # 其他吉神，取前6个字符
                                jishen_text_list.append(jishen[:6])
                        jishen_text = ', '.join(jishen_text_list[:2])  # 最多显示2个吉神
                    else:
                        # 如果没有详细吉神，使用yi_list
                        yi_list = result.get('yi_list', detail.get('yi_list', []))
                        jishen_text = ', '.join(yi_list[:2]) if yi_list else '-'
                    
                    # 添加到Treeview
                    self.date_treeview.insert('', tk.END, values=(date_str, score, level, sizhu_str, wuxing_score, yueling_score, xishen_score, huangdao_score, dizhi_text, jishen_text))
                    
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
            
            # 只有在有结果时才显示成功消息
            if results:
                messagebox.showinfo("成功", f"成功导入 {len(results)} 个择日结果到评分系统")
        except Exception as e:
            messagebox.showerror("错误", f"导入择日结果时出错: {str(e)}")
    
    def run(self):
        """运行日课评分系统"""
        # 确保窗口显示在最前面
        self.window.lift()
        self.window.focus_force()
        
        # 只有在没有调用过import_results时，才初始化默认的事主信息
        # 通过检查owners_info是否为空来判断是否已经初始化过
        if not self.owners_info:
            self.update_owners_frame()
            self.update_special_options()
        
        # 如果是主窗口（Tk），使用mainloop
        # 如果是子窗口（Toplevel），使用wait_window等待窗口关闭
        if isinstance(self.window, tk.Tk):
            self.window.mainloop()
        else:
            # 对于Toplevel窗口，确保它可见并等待用户交互
            self.window.transient(self.window.master)
            self.window.grab_set()
            self.window.wait_window()
    
    def configure_styles(self):
        """配置界面样式，与主程序一致"""
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
        
        # 次要按钮样式 - 使用与主按钮相同的蓝色系
        style.configure('Secondary.TButton', 
                       background='#007bff',
                       foreground='white',
                       font=('微软雅黑', 11, 'bold'),
                       padding=(10, 5),
                       borderwidth=0,
                       relief='flat')
        style.map('Secondary.TButton', 
                  background=[('active', '#0069d9')])
        
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
    
    def create_widgets(self):
        """创建界面组件"""
        # 配置样式
        self.configure_styles()
        
        # 创建主滚动区域 - 添加水平和垂直滚动条
        main_frame_container = ttk.Frame(self.window)
        main_frame_container.pack(fill=tk.BOTH, expand=True)
        
        main_canvas = tk.Canvas(main_frame_container, bg="#ffffff")
        v_scrollbar = ttk.Scrollbar(main_frame_container, orient="vertical", command=main_canvas.yview)
        h_scrollbar = ttk.Scrollbar(main_frame_container, orient="horizontal", command=main_canvas.xview)
        
        self.main_frame = ttk.Frame(main_canvas, padding="20", style="MainFrame.TFrame")
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw", width=self.window.winfo_screenwidth()-50)
        main_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 使用网格布局
        main_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置网格权重
        main_frame_container.grid_rowconfigure(0, weight=1)
        main_frame_container.grid_columnconfigure(0, weight=1)
        
        # 绑定鼠标滚轮（垂直滚动）
        main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        # 绑定Shift+鼠标滚轮（水平滚动）
        main_canvas.bind_all("<Shift-MouseWheel>", lambda e: main_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 标题区域
        title_frame = ttk.Frame(self.main_frame, style="TitleFrame.TFrame")
        title_frame.pack(fill=tk.X, pady=8, padx=20)
        
        title_label = ttk.Label(title_frame, text="专业级日课评分系统", 
                               font=("微软雅黑", 18, "bold"), style="Title.TLabel")
        title_label.pack(pady=4)
        
        subtitle_label = ttk.Label(title_frame, text="精准评分，详细分析", 
                                  font=("微软雅黑", 9), style="Subtitle.TLabel")
        subtitle_label.pack()
        
        # 提前定义event_var变量
        self.event_var = tk.StringVar(value="嫁娶")
        
        # 事主信息区域（放在最上方）
        self.owners_frame = ttk.LabelFrame(self.main_frame, text="事主信息", padding="20", style="Card.TLabelframe")
        self.owners_frame.pack(fill=tk.X, pady=6, padx=20)
        # 暂时不更新，等到import_results或用户选择事项类型时再更新
        # self.update_owners_frame()
        
        # 创建左右分栏布局
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        # 使用网格布局，设置左右分栏的宽度比例
        content_frame.columnconfigure(0, weight=1, minsize=500)  # 左侧占1份
        content_frame.columnconfigure(1, weight=1, minsize=500)  # 右侧占1份
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧内容（输入区域和按钮）
        left_frame = ttk.Frame(content_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # 右侧内容（留空，用于平衡布局）
        right_frame = ttk.Frame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # 输入区域
        input_frame = ttk.LabelFrame(left_frame, text="日课输入", padding="8", style="Card.TLabelframe")
        input_frame.pack(fill=tk.X, pady=6)
        
        # 事项类型选择
        event_frame = ttk.Frame(input_frame)
        event_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(event_frame, text="事项类型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        events = ["嫁娶", "修造", "动土", "入宅", "开业", "出行", "安床", "作灶", "安葬"]
        event_combo = ttk.Combobox(event_frame, textvariable=self.event_var, 
                                   values=events, state="readonly", width=15, font=("微软雅黑", 10))
        event_combo.pack(side=tk.LEFT, padx=5)
        # 绑定事件，使用更可靠的方式
        event_combo.bind("<<ComboboxSelected>>", self.on_event_type_changed)
        
        # 特殊选项框架（用于修造等需要额外选项的事项）
        self.special_frame = ttk.Frame(input_frame)
        self.special_frame.pack(fill=tk.X, pady=3)
        
        # 初始化特殊选项
        self.update_special_options()
        
        # 输入方式选择
        input_mode_frame = ttk.Frame(input_frame)
        input_mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_mode_frame, text="输入方式:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.input_mode = tk.StringVar(value="date")
        ttk.Radiobutton(input_mode_frame, text="按日期", variable=self.input_mode, 
                       value="date", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(input_mode_frame, text="按四柱", variable=self.input_mode, 
                       value="sizhu", command=self.toggle_input_mode).pack(side=tk.LEFT, padx=5)
        
        # 日期输入框
        self.date_frame = ttk.Frame(input_frame)
        self.date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.date_frame, text="日期 (YYYY-MM-DD):", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.date_entry = ttk.Entry(self.date_frame, width=12, font=("微软雅黑", 10))
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # 时间输入
        ttk.Label(self.date_frame, text="时间 (HH:MM):", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.time_entry = ttk.Entry(self.date_frame, width=6, font=("微软雅黑", 10))
        self.time_entry.pack(side=tk.LEFT, padx=5)
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
        
        # 按钮区域 - 使用两行布局，统一颜色
        button_frame = ttk.Frame(left_frame, style="ButtonFrame.TFrame")
        button_frame.pack(fill=tk.X, pady=8, padx=20)
        
        # 第一行按钮
        button_row1 = ttk.Frame(button_frame, style="ButtonFrame.TFrame")
        button_row1.pack(fill=tk.X, pady=3)
        
        ttk.Button(button_row1, text="添加日课", command=self.add_date, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_row1, text="添加四柱", command=self.add_sizhu, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_row1, text="日课评分", command=self.start_scoring, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_row1, text="对比分析", command=self.compare_analysis, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_row1, text="清空列表", command=self.clear_dates, width=10, style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        
        # 第二行按钮
        button_row2 = ttk.Frame(button_frame, style="ButtonFrame.TFrame")
        button_row2.pack(fill=tk.X, pady=3)
        
        ttk.Button(button_row2, text="保存分析", command=self.save_single_analysis, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_row2, text="导出报告", command=self.export_report, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_row2, text="导入文件", command=self.import_file, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(button_row2, text="帮助", command=self.show_help, width=10, style="Secondary.TButton").pack(side=tk.LEFT, padx=4)
        
        # 日课列表
        list_frame = ttk.LabelFrame(self.main_frame, text="日课列表", padding="20", style="Card.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # 创建Treeview控件替代Listbox，显示更多信息
        columns = ('date', 'score', 'level', 'sizhu', 'wuxing', 'yueling', 'xishen', 'huangdao', 'dizhi', 'jishen')
        self.date_treeview = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 设置列标题
        self.date_treeview.heading('date', text='日期/四柱')
        self.date_treeview.heading('score', text='评分')
        self.date_treeview.heading('level', text='等级')
        self.date_treeview.heading('sizhu', text='四柱')
        self.date_treeview.heading('wuxing', text='五行得分')
        self.date_treeview.heading('yueling', text='月令得分')
        self.date_treeview.heading('xishen', text='喜用神得分')
        self.date_treeview.heading('huangdao', text='黄道得分')
        self.date_treeview.heading('dizhi', text='地支关系')
        self.date_treeview.heading('jishen', text='吉神信息')
        
        # 设置列宽 - 缩小列宽以适应手机屏幕
        self.date_treeview.column('date', width=90)
        self.date_treeview.column('score', width=45, anchor='center')
        self.date_treeview.column('level', width=45, anchor='center')
        self.date_treeview.column('sizhu', width=90)
        self.date_treeview.column('wuxing', width=50, anchor='center')
        self.date_treeview.column('yueling', width=50, anchor='center')
        self.date_treeview.column('xishen', width=55, anchor='center')
        self.date_treeview.column('huangdao', width=50, anchor='center')
        self.date_treeview.column('dizhi', width=80)
        self.date_treeview.column('jishen', width=90)
        
        # 添加滚动条 - 同时添加垂直和水平滚动条
        tree_v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                         command=self.date_treeview.yview)
        tree_h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, 
                                         command=self.date_treeview.xview)
        self.date_treeview.config(yscrollcommand=tree_v_scrollbar.set, 
                                  xscrollcommand=tree_h_scrollbar.set)
        
        # 使用网格布局
        self.date_treeview.grid(row=0, column=0, sticky="nsew")
        tree_v_scrollbar.grid(row=0, column=1, sticky="ns")
        tree_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置网格权重
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定双击事件
        self.date_treeview.bind('<Double-1>', self.on_date_double_click)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.main_frame, text="评分结果", padding="20", style="Card.TLabelframe")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, font=("微软雅黑", 11))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置金色tag用于显示星星
        self.result_text.tag_configure("gold", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        self.result_text.tag_configure("gold_star", foreground="#FFD700", font=("微软雅黑", 11, "bold"))
        # 配置可用/不可用标签
        self.result_text.tag_configure("usable", foreground="#228B22", font=("微软雅黑", 11, "bold"))  # 森林绿
        self.result_text.tag_configure("unusable", foreground="#DC143C", font=("微软雅黑", 11, "bold"))  # 猩红
        self.result_text.tag_configure("bold", font=("微软雅黑", 11, "bold"))
        
        # 保存按钮
        save_frame = ttk.Frame(result_frame)
        save_frame.pack(fill=tk.X, pady=5)
        
        save_btn = ttk.Button(save_frame, text="保存评分结果", width=20, command=self.save_score_result)
        save_btn.pack(side=tk.RIGHT, padx=10)
    
    def on_event_type_changed(self, event=None):
        """事项类型变化时的回调函数"""
        # 更新特殊选项
        self.update_special_options()
        # 更新事主信息框架
        self.update_owners_frame()
        # 强制刷新界面
        self.window.update_idletasks()
        self.window.update()
        # 重新打包框架以确保布局更新
        self.owners_frame.pack_forget()
        self.owners_frame.pack(fill=tk.X, pady=6, padx=20)
    
    def update_special_options(self):
        """更新特殊选项（如阳宅/阴宅选择）"""
        # 清空特殊选项框架
        for widget in self.special_frame.winfo_children():
            widget.destroy()
        
        event_type = self.event_var.get()
        
        # 修造、动土、入宅事项需要选择宅型（阳宅/阴宅）和山向
        if event_type in ["修造", "动土", "入宅"]:
            # 宅型选择
            ttk.Label(self.special_frame, text="宅型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=3)
            self.house_type = tk.StringVar(value="阳宅")
            house_combo = ttk.Combobox(self.special_frame, textvariable=self.house_type,
                                       values=["阳宅", "阴宅"], width=8, state="readonly", font=("微软雅黑", 10))
            house_combo.pack(side=tk.LEFT, padx=3)
            
            # 山向选择（使用二十四山模块的完整山向列表）
            ttk.Label(self.special_frame, text="山向:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=3)
            self.shan_xiang = tk.StringVar()
            # 使用二十四山模块获取完整的24山向列表
            shan_xiangs = get_shan_xiang_list(use_24_shan=True)
            shan_combo = ttk.Combobox(self.special_frame, textvariable=self.shan_xiang, 
                                      values=shan_xiangs, width=12, state="readonly", font=("微软雅黑", 10))
            shan_combo.pack(side=tk.LEFT, padx=3)
            
            # 兼向选择（动态更新）
            ttk.Label(self.special_frame, text="兼向:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=3)
            self.jian_xiang = tk.StringVar(value="正中")
            self.jian_xiang_combo = ttk.Combobox(self.special_frame, textvariable=self.jian_xiang,
                                      values=["正中"], width=10, state="readonly", font=("微软雅黑", 10))
            self.jian_xiang_combo.pack(side=tk.LEFT, padx=3)
            self.jian_xiang.set("正中")  # 默认正中
            # 绑定山向变化时更新兼向选项
            self.shan_xiang.trace_add('write', self._update_jianxiang_options)
            
            # 电子罗盘按钮
            ttk.Button(self.special_frame, text="罗盘", width=6,
                      command=self._show_compass_dialog).pack(side=tk.LEFT, padx=3)
            
            # 强制刷新界面
            self.special_frame.update_idletasks()
            self.special_frame.update()
    
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
    
    def _show_compass_dialog(self):
        """显示电子罗盘对话框"""
        # 获取当前山向
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
                    # 先更新兼向选项
                    self._update_jianxiang_options()
                    # 然后设置兼向值
                    if jianxiang:
                        self.jian_xiang.set(jianxiang)
                    else:
                        self.jian_xiang.set("正中")
        
        # 显示罗盘对话框
        show_compass_dialog(self.window, initial_shan_xiang, on_compass_select)
    
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
            hint_label = tk.Label(self.owners_frame, text="（提示：以下事主信息为可选，可根据需要填写）", 
                                   fg="gray", bg='white', font=("微软雅黑", 11, "italic"))
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
        
        for owner in owners:
            owner_frame = ttk.Frame(self.owners_frame)
            owner_frame.pack(fill=tk.X, pady=8)
            
            # 标题行
            title_row = ttk.Frame(owner_frame)
            title_row.pack(fill=tk.X, pady=2)
            
            tk.Label(title_row, text=f"{owner}:", font=("微软雅黑", 12), bg='white', fg='black').pack(side=tk.LEFT, padx=5)
            
            # 日期类型和性别选择
            type_row = ttk.Frame(owner_frame)
            type_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(type_row, text="日期类型:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            date_type_var = tk.StringVar(value="公历")
            
            # 创建单选按钮，先不设置command
            solar_radio = ttk.Radiobutton(type_row, text="公历", variable=date_type_var, value="公历")
            solar_radio.pack(side=tk.LEFT, padx=5)
            lunar_radio = ttk.Radiobutton(type_row, text="农历", variable=date_type_var, value="农历")
            lunar_radio.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(type_row, text="性别:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            gender_var = tk.StringVar(value="男" if owner in ["新郎", "孝子1", "孝子2", "孝子3", "事主1", "事主2", "事主3", "事主4", "事主"] else "女")
            ttk.Radiobutton(type_row, text="男", variable=gender_var, value="男").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(type_row, text="女", variable=gender_var, value="女").pack(side=tk.LEFT, padx=5)
            
            # 婚嫁事项默认填充日期，其他事项默认为空（可选）
            if event_type == "嫁娶":
                solar_year_var = tk.StringVar(value=str(date.today().year - 20))
                solar_month_var = tk.StringVar(value=str(1))
                solar_day_var = tk.StringVar(value=str(1))
                lunar_year_var = tk.StringVar(value=str(date.today().year - 20))
                lunar_month_var = tk.StringVar(value=str(1))
                lunar_day_var = tk.StringVar(value=str(1))
                hour_var = tk.StringVar(value=str(12))
                minute_var = tk.StringVar(value=str(0))
            else:
                solar_year_var = tk.StringVar()
                solar_month_var = tk.StringVar()
                solar_day_var = tk.StringVar()
                lunar_year_var = tk.StringVar()
                lunar_month_var = tk.StringVar()
                lunar_day_var = tk.StringVar()
                hour_var = tk.StringVar(value="12")
                minute_var = tk.StringVar(value="0")
            
            # 闰月变量
            leap_var = tk.BooleanVar(value=False)
            
            # 公历输入框
            solar_frame = ttk.Frame(owner_frame)
            solar_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(solar_frame, text="年:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            solar_year_entry = ttk.Entry(solar_frame, textvariable=solar_year_var, width=6, font=("微软雅黑", 10))
            solar_year_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(solar_frame, text="月:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            solar_month_entry = ttk.Entry(solar_frame, textvariable=solar_month_var, width=4, font=("微软雅黑", 10))
            solar_month_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(solar_frame, text="日:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            solar_day_entry = ttk.Entry(solar_frame, textvariable=solar_day_var, width=4, font=("微软雅黑", 10))
            solar_day_entry.pack(side=tk.LEFT, padx=3)
            
            # 农历输入框
            lunar_frame = ttk.Frame(owner_frame)
            
            ttk.Label(lunar_frame, text="农历年:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            lunar_year_entry = ttk.Entry(lunar_frame, textvariable=lunar_year_var, width=6, font=("微软雅黑", 10))
            lunar_year_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(lunar_frame, text="月:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            lunar_month_entry = ttk.Entry(lunar_frame, textvariable=lunar_month_var, width=4, font=("微软雅黑", 10))
            lunar_month_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(lunar_frame, text="日:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            lunar_day_entry = ttk.Entry(lunar_frame, textvariable=lunar_day_var, width=4, font=("微软雅黑", 10))
            lunar_day_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(lunar_frame, text="闰月:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            leap_check = ttk.Checkbutton(lunar_frame, variable=leap_var)
            leap_check.pack(side=tk.LEFT, padx=3)
            
            # 时间输入行
            time_row = ttk.Frame(owner_frame)
            time_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(time_row, text="时:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
            hour_entry = ttk.Entry(time_row, textvariable=hour_var, width=4, font=("微软雅黑", 10))
            hour_entry.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(time_row, text="分:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
            minute_entry = ttk.Entry(time_row, textvariable=minute_var, width=4, font=("微软雅黑", 10))
            minute_entry.pack(side=tk.LEFT, padx=3)
            
            # 存储当前事主的输入框，用于跨事主导航
            owner_entries = {
                'solar': [solar_year_entry, solar_month_entry, solar_day_entry],
                'lunar': [lunar_year_entry, lunar_month_entry, lunar_day_entry],
                'time': [hour_entry, minute_entry],
                'all': [solar_year_entry, solar_month_entry, solar_day_entry,
                       lunar_year_entry, lunar_month_entry, lunar_day_entry,
                       hour_entry, minute_entry]
            }
            self._owner_entries_list.append(owner_entries)
            
            # 绑定当前事主的输入框导航
            self._bind_owner_navigation(owner_entries, len(self._owner_entries_list) - 1)
            
            # 四柱显示
            sizhu_row = ttk.Frame(owner_frame)
            sizhu_row.pack(fill=tk.X, pady=2)
            
            tk.Label(sizhu_row, text="四柱:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
            sizhu_var = tk.StringVar(value="未计算")
            sizhu_label = tk.Label(sizhu_row, textvariable=sizhu_var, font=("微软雅黑", 10, "bold"), bg='white', fg='black')
            sizhu_label.pack(side=tk.LEFT, padx=3)
            
            # 喜用神显示
            xishen_var = tk.StringVar(value="")
            yongshen_var = tk.StringVar(value="")
            
            xishen_row = ttk.Frame(owner_frame)
            xishen_row.pack(fill=tk.X, pady=2)
            
            tk.Label(xishen_row, text="喜神:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
            tk.Label(xishen_row, textvariable=xishen_var, fg="blue", bg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)
            tk.Label(xishen_row, text="  用神:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
            tk.Label(xishen_row, textvariable=yongshen_var, fg="green", bg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)
            
            # 夫星子星显示（婚嫁专用）
            fuzi_var = tk.StringVar(value="")
            if event_type == "嫁娶":
                fuzi_row = ttk.Frame(owner_frame)
                fuzi_row.pack(fill=tk.X, pady=2)
                
                tk.Label(fuzi_row, text="夫星/子星:", font=("微软雅黑", 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10)
                tk.Label(fuzi_row, textvariable=fuzi_var, fg="purple", bg='white', font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)
            
            # 为每个事主创建独立的auto_calculate函数
            def create_auto_calculate(syv, smv, sdv, lyv, lmv, ldv, lv, hv, miv, o, sv, xv, ygv, fzv, dtv, gv):
                def auto_calculate(event):
                    # 根据日期类型获取相应的日期变量
                    if dtv.get() == "公历":
                        year_val = syv.get()
                        month_val = smv.get()
                        day_val = sdv.get()
                    else:
                        year_val = lyv.get()
                        month_val = lmv.get()
                        day_val = ldv.get()
                    
                    hour_val = hv.get()
                    minute_val = miv.get()
                    
                    if year_val and month_val and day_val and hour_val and minute_val:
                        try:
                            year = int(year_val)
                            month = int(month_val)
                            day = int(day_val)
                            hour = int(hour_val)
                            minute = int(minute_val)
                            
                            # 验证日期有效性
                            if 0 <= hour < 24 and 0 <= minute < 60:
                                # 延迟计算，避免频繁触发
                                self.window.after(500, lambda:
                                    self.calculate_owner_sizhu(syv, smv, sdv, lyv, lmv, ldv, lv, hv, miv, o, sv, xv, ygv, fzv, dtv, gv))
                        except:
                            pass
                return auto_calculate
            
            # 创建独立的auto_calculate函数
            auto_calculate = create_auto_calculate(solar_year_var, solar_month_var, solar_day_var, 
                                                lunar_year_var, lunar_month_var, lunar_day_var, leap_var, 
                                                hour_var, minute_var, owner, sizhu_var, xishen_var, yongshen_var, fuzi_var, 
                                                date_type_var, gender_var)
            
            # 日期类型选择变化时的回调函数
            def create_toggle_command(dt_var, sf, lf, tr, owner_name):
                def toggle_date_fields():
                    current_type = dt_var.get()
                    print(f"[DEBUG] {owner_name}: 日期类型切换为 '{current_type}'")
                    if current_type == "农历":
                        # 显示农历输入框，隐藏公历输入框
                        print(f"[DEBUG] {owner_name}: 显示农历输入框")
                        sf.pack_forget()
                        lf.pack(fill=tk.X, pady=2, before=tr)
                    else:
                        # 显示公历输入框，隐藏农历输入框
                        print(f"[DEBUG] {owner_name}: 显示公历输入框")
                        lf.pack_forget()
                        sf.pack(fill=tk.X, pady=2, before=tr)
                return toggle_date_fields
            
            # 创建并绑定日期类型变化事件
            toggle_command = create_toggle_command(date_type_var, solar_frame, lunar_frame, time_row, owner)
            
            # 为单选按钮设置command - 使用工厂函数确保正确捕获变量
            def create_radio_command(dt_var, cmd, value):
                def radio_command():
                    dt_var.set(value)
                    self.window.after(10, cmd)
                return radio_command
            
            solar_radio.config(command=create_radio_command(date_type_var, toggle_command, "公历"))
            lunar_radio.config(command=create_radio_command(date_type_var, toggle_command, "农历"))
            
            # 同时绑定变量变化事件
            def create_trace_callback(cmd):
                return lambda *args: self.window.after(10, cmd)
            
            date_type_var.trace_add('write', create_trace_callback(toggle_command))
            
            # 初始状态
            toggle_command()
            
            # 绑定输入框的事件
            solar_year_entry.bind('<KeyRelease>', auto_calculate)
            solar_month_entry.bind('<KeyRelease>', auto_calculate)
            solar_day_entry.bind('<KeyRelease>', auto_calculate)
            lunar_year_entry.bind('<KeyRelease>', auto_calculate)
            lunar_month_entry.bind('<KeyRelease>', auto_calculate)
            lunar_day_entry.bind('<KeyRelease>', auto_calculate)
            hour_entry.bind('<KeyRelease>', auto_calculate)
            minute_entry.bind('<KeyRelease>', auto_calculate)
            
            # 按钮行
            button_row = ttk.Frame(owner_frame)
            button_row.pack(fill=tk.X, pady=2)
            
            # 计算按钮
            calc_btn = ttk.Button(button_row, text="计算四柱", 
                                 command=lambda sy=solar_year_var, sm=solar_month_var, sd=solar_day_var, 
                                 ly=lunar_year_var, lm=lunar_month_var, ld=lunar_day_var, lp=leap_var, 
                                 h=hour_var, mi=minute_var, o=owner, s=sizhu_var, 
                                 x=xishen_var, yg=yongshen_var, fz=fuzi_var, dt=date_type_var, g=gender_var: 
                                 self.calculate_owner_sizhu(sy, sm, sd, ly, lm, ld, lp, h, mi, o, s, x, yg, fz, dt, g))
            calc_btn.pack(side=tk.LEFT, padx=10)
            
            # 八字排盘详情按钮
            bazi_btn = ttk.Button(button_row, text="八字排盘详情", 
                                 command=lambda sy=solar_year_var, sm=solar_month_var, sd=solar_day_var, 
                                 ly=lunar_year_var, lm=lunar_month_var, ld=lunar_day_var, lp=leap_var, 
                                 h=hour_var, mi=minute_var, o=owner, dt=date_type_var, g=gender_var: 
                                 self.show_bazi_detail(sy, sm, sd, ly, lm, ld, lp, h, mi, o, dt, g))
            bazi_btn.pack(side=tk.LEFT, padx=10)
            
            # 保存事主信息
            owner_info = {
                'name': owner,
                'solar_year': solar_year_var,
                'solar_month': solar_month_var,
                'solar_day': solar_day_var,
                'lunar_year': lunar_year_var,
                'lunar_month': lunar_month_var,
                'lunar_day': lunar_day_var,
                'leap': leap_var,
                'hour': hour_var,
                'minute': minute_var,
                'sizhu_var': sizhu_var,
                'xishen_var': xishen_var,
                'yongshen_var': yongshen_var,
                'fuzi_var': fuzi_var,
                'date_type_var': date_type_var,  # 保存日期类型引用
                'gender_var': gender_var  # 保存性别引用
            }
            
            self.owners_info.append(owner_info)
    
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
            # 检查光标是否在最后或输入框为空
            widget = event.widget
            if widget.index(tk.INSERT) >= len(widget.get()):
                if idx < len(entries) - 1:
                    entries[idx + 1].focus_set()
                    entries[idx + 1].select_range(0, tk.END)
                    return "break"
            return None
        
        def on_key_tab(event, idx):
            """Tab键移动到下一个输入框"""
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
            # 绑定Tab键
            entry.bind('<Tab>', lambda e, idx=i: on_key_tab(e, idx))
    
    def _bind_owner_navigation(self, owner_entries, owner_idx):
        """为单个事主的输入框绑定键盘导航，支持跨事主导航
        
        Args:
            owner_entries: 当前事主的输入框字典
            owner_idx: 当前事主的索引
        """
        solar_entries = owner_entries['solar']
        lunar_entries = owner_entries['lunar']
        time_entries = owner_entries['time']
        
        # 获取当前日期类型
        date_type = self.owners_info[owner_idx]['date_type'] if owner_idx < len(self.owners_info) else None
        
        def get_visible_entries():
            """获取当前可见的输入框列表"""
            if date_type and date_type.get() == "农历":
                return lunar_entries + time_entries
            else:
                return solar_entries + time_entries
        
        def on_key_right(event, current_entries, entry_idx):
            """向右移动"""
            visible_entries = get_visible_entries()
            # 在当前可见组内移动
            if entry_idx < len(current_entries) - 1:
                next_idx = entry_idx + 1
            elif current_entries == solar_entries and date_type and date_type.get() == "公历":
                # 从公历日移动到时
                time_entries[0].focus_set()
                time_entries[0].select_range(0, tk.END)
                return "break"
            elif current_entries == lunar_entries and date_type and date_type.get() == "农历":
                # 从农历日移动到时
                time_entries[0].focus_set()
                time_entries[0].select_range(0, tk.END)
                return "break"
            elif current_entries == time_entries:
                # 从分移动到下一个事主
                if owner_idx < len(self._owner_entries_list) - 1:
                    next_owner = self._owner_entries_list[owner_idx + 1]
                    next_visible = next_owner['solar'] if next_owner.get('date_type', '公历') == '公历' else next_owner['lunar']
                    next_visible[0].focus_set()
                    next_visible[0].select_range(0, tk.END)
                return "break"
            else:
                return None
            
            current_entries[next_idx].focus_set()
            current_entries[next_idx].select_range(0, tk.END)
            return "break"
        
        def on_key_left(event, current_entries, entry_idx):
            """向左移动"""
            if entry_idx > 0:
                prev_idx = entry_idx - 1
                current_entries[prev_idx].focus_set()
                current_entries[prev_idx].select_range(0, tk.END)
                return "break"
            elif current_entries == time_entries:
                # 从时移动到日（公历或农历）
                if date_type and date_type.get() == "农历":
                    lunar_entries[-1].focus_set()
                    lunar_entries[-1].select_range(0, tk.END)
                else:
                    solar_entries[-1].focus_set()
                    solar_entries[-1].select_range(0, tk.END)
                return "break"
            elif current_entries in [solar_entries, lunar_entries] and owner_idx > 0:
                # 移动到上一个事主的最后一个输入框
                prev_owner = self._owner_entries_list[owner_idx - 1]
                prev_time = prev_owner['time']
                prev_time[-1].focus_set()
                prev_time[-1].select_range(0, tk.END)
                return "break"
            return None
        
        def on_key_down(event):
            """向下移动到下一个事主的对应输入框"""
            if owner_idx < len(self._owner_entries_list) - 1:
                next_owner = self._owner_entries_list[owner_idx + 1]
                # 找到当前输入框在可见列表中的位置
                visible = get_visible_entries()
                widget = event.widget
                try:
                    current_idx = visible.index(widget)
                    next_visible = next_owner['solar'] if next_owner.get('date_type', '公历') == '公历' else next_owner['lunar']
                    if current_idx < len(next_visible):
                        next_visible[current_idx].focus_set()
                        next_visible[current_idx].select_range(0, tk.END)
                except ValueError:
                    pass
            return "break"
        
        def on_key_up(event):
            """向上移动到上一个事主的对应输入框"""
            if owner_idx > 0:
                prev_owner = self._owner_entries_list[owner_idx - 1]
                visible = get_visible_entries()
                widget = event.widget
                try:
                    current_idx = visible.index(widget)
                    prev_visible = prev_owner['solar'] if prev_owner.get('date_type', '公历') == '公历' else prev_owner['lunar']
                    if current_idx < len(prev_visible):
                        prev_visible[current_idx].focus_set()
                        prev_visible[current_idx].select_range(0, tk.END)
                except ValueError:
                    pass
            return "break"
        
        # 绑定公历输入框
        for i, entry in enumerate(solar_entries):
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, solar_entries, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, solar_entries, idx))
            entry.bind('<Down>', on_key_down)
            entry.bind('<Up>', on_key_up)
        
        # 绑定农历输入框
        for i, entry in enumerate(lunar_entries):
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, lunar_entries, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, lunar_entries, idx))
            entry.bind('<Down>', on_key_down)
            entry.bind('<Up>', on_key_up)
        
        # 绑定时间输入框
        for i, entry in enumerate(time_entries):
            entry.bind('<Right>', lambda e, idx=i: on_key_right(e, time_entries, idx))
            entry.bind('<Left>', lambda e, idx=i: on_key_left(e, time_entries, idx))
            entry.bind('<Down>', on_key_down)
            entry.bind('<Up>', on_key_up)
    
    def calculate_owner_sizhu(self, solar_year_var, solar_month_var, solar_day_var, 
                              lunar_year_var, lunar_month_var, lunar_day_var, leap_var, 
                              hour_var, minute_var, owner, sizhu_var, xishen_var, yongshen_var, 
                              fuzi_var=None, date_type_var=None, gender_var=None):
        """计算事主四柱"""
        try:
            # 防御性检查：获取小时和分钟
            hour_str = hour_var.get() if hasattr(hour_var, 'get') else str(hour_var)
            minute_str = minute_var.get() if hasattr(minute_var, 'get') else str(minute_var)
            
            if not hour_str or not minute_str:
                return
            
            hour = int(hour_str)
            minute = int(minute_str)
            
            # 处理日期类型和闰月
            date_type = date_type_var.get() if date_type_var and hasattr(date_type_var, 'get') else "公历"
            is_leap = leap_var.get() if leap_var and hasattr(leap_var, 'get') else False
            
            if date_type == "农历":
                # 农历日期转换为公历
                lunar_year_str = lunar_year_var.get() if hasattr(lunar_year_var, 'get') else str(lunar_year_var)
                lunar_month_str = lunar_month_var.get() if hasattr(lunar_month_var, 'get') else str(lunar_month_var)
                lunar_day_str = lunar_day_var.get() if hasattr(lunar_day_var, 'get') else str(lunar_day_var)
                
                if not (lunar_year_str and lunar_month_str and lunar_day_str):
                    return
                    
                year = int(lunar_year_str)
                month = int(lunar_month_str)
                day = int(lunar_day_str)
                # 使用sxtwl库进行农历转公历
                import sxtwl
                day_obj = sxtwl.fromLunar(year, month, day, is_leap)
                target_date = date(day_obj.getSolarYear(), day_obj.getSolarMonth(), day_obj.getSolarDay())
            else:
                # 公历日期
                solar_year_str = solar_year_var.get() if hasattr(solar_year_var, 'get') else str(solar_year_var)
                solar_month_str = solar_month_var.get() if hasattr(solar_month_var, 'get') else str(solar_month_var)
                solar_day_str = solar_day_var.get() if hasattr(solar_day_var, 'get') else str(solar_day_var)
                
                if not (solar_year_str and solar_month_str and solar_day_str):
                    return
                    
                year = int(solar_year_str)
                month = int(solar_month_str)
                day = int(solar_day_str)
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
            if fuzi_var and hasattr(fuzi_var, 'set') and self.event_var.get() == "嫁娶" and owner == "新娘":
                fuzi = analysis.get('夫星子星', {})
                fu_xing = fuzi.get('fu', '')
                zi_xing = fuzi.get('zi', '')
                if fu_xing or zi_xing:
                    fuzi_var.set(f"夫星: {fu_xing}, 子星: {zi_xing}")
        except Exception as e:
            messagebox.showerror("计算错误", f"计算四柱失败: {str(e)}")
            logger.error(f"计算四柱失败: {str(e)}", exc_info=True)
    
    def show_bazi_detail(self, solar_year_var, solar_month_var, solar_day_var, 
                         lunar_year_var, lunar_month_var, lunar_day_var, leap_var, 
                         hour_var, minute_var, owner, date_type_var=None, gender_var=None):
        """显示八字排盘详情"""
        try:
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            
            # 处理日期类型和闰月
            date_type = date_type_var.get() if date_type_var else "公历"
            is_leap = leap_var.get() if leap_var else False
            gender = gender_var.get() if gender_var else "男"
            
            if date_type == "农历":
                # 农历日期转换为公历
                year = int(lunar_year_var.get())
                month = int(lunar_month_var.get())
                day = int(lunar_day_var.get())
                # 使用sxtwl库进行农历转公历
                import sxtwl
                day_obj = sxtwl.fromLunar(year, month, day, is_leap)
                solar_year = day_obj.getSolarYear()
                solar_month = day_obj.getSolarMonth()
                solar_day = day_obj.getSolarDay()
            else:
                # 公历日期
                solar_year = int(solar_year_var.get())
                solar_month = int(solar_month_var.get())
                solar_day = int(solar_day_var.get())

            # 使用八字可视化模块显示排盘
            from .八字可视化模块 import show_bazi_from_birth
            show_bazi_from_birth(
                self.window,
                solar_year,
                solar_month,
                solar_day,
                hour,
                minute,
                gender
            )
        except Exception as e:
            messagebox.showerror("错误", f"显示八字排盘详情失败: {str(e)}")
            logger.error(f"显示八字排盘详情失败: {str(e)}", exc_info=True)
    
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
                # 添加到Treeview - 使用完整的10列
                self.date_treeview.insert('', tk.END, values=(date_time_str, '', '', '', '', '', '', '', '', ''))
            else:
                messagebox.showwarning("警告", "该日期时间已在列表中")
        except ValueError:
            messagebox.showerror("错误", "日期或时间格式不正确")
    
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
        self.date_treeview.insert('', tk.END, values=(sizhu_str, '', '', sizhu_str, '', '', '', '', '', ''))
        
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
                
                # 处理时间格式，支持多种输入方式
                if ':' in time_str:
                    # 已有冒号，直接验证
                    datetime.strptime(time_str, '%H:%M')
                else:
                    # 无冒号，根据长度处理
                    time_str = time_str.strip()
                    if len(time_str) == 1:
                        # 只有小时，如"8" → "08:00"
                        time_str = f"0{time_str}:00"
                    elif len(time_str) == 2:
                        # 只有小时，如"12" → "12:00"
                        time_str = f"{time_str}:00"
                    elif len(time_str) == 3:
                        # 小时+分钟，如"830" → "08:30"
                        time_str = f"0{time_str[:1]}:{time_str[1:]}"
                    elif len(time_str) == 4:
                        # 小时+分钟，如"1230" → "12:30"
                        time_str = f"{time_str[:2]}:{time_str[2:]}"
                    else:
                        # 其他情况，抛出异常
                        raise ValueError("时间格式错误")
                
                current_rike = f"{date_str} {time_str}"
            except ValueError:
                messagebox.showerror("错误", "日期或时间格式不正确")
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
        
        # 检查是否已存在于已评分列表中
        if current_rike in self.date_list:
            # 检查是否已经有评分结果
            has_score = False
            for item in self.date_treeview.get_children():
                values = self.date_treeview.item(item, 'values')
                if values[0] == current_rike and values[1] != '':  # 第二列是评分
                    has_score = True
                    break
            
            if has_score:
                messagebox.showwarning("警告", "该日课已评分")
                return
            # 如果已添加但未评分，继续评分流程
        
        event_type = self.event_var.get()
        
        # 获取事主信息
        owners_detail = []
        for info in self.owners_info:
            try:
                # 添加防御性检查
                year_val = info['year'].get() if hasattr(info['year'], 'get') else info.get('year', '')
                month_val = info['month'].get() if hasattr(info['month'], 'get') else info.get('month', '')
                day_val = info['day'].get() if hasattr(info['day'], 'get') else info.get('day', '')
                hour_val = info['hour'].get() if hasattr(info['hour'], 'get') else info.get('hour', '12')
                minute_val = info['minute'].get() if hasattr(info['minute'], 'get') else info.get('minute', '0')
                
                # 检查是否有完整的日期信息
                if not (year_val and month_val and day_val):
                    continue
                
                year = int(year_val)
                month = int(month_val)
                day = int(day_val)
                hour = int(hour_val)
                minute = int(minute_val)
                
                target_date = date(year, month, day)
                sizhu = calculate_sizhu(target_date, hour, minute)
                analysis = analyze_sizhu(sizhu)
                
                # 获取姓名（添加防御性检查）
                name = info['name'].get() if hasattr(info['name'], 'get') else info.get('name', '')
                
                owner_detail = {
                    'name': name,
                    'birth_date': f"{year}年{month}月{day}日 {hour}时{minute}分",
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'xishen': info['xishen_var'].get() if hasattr(info.get('xishen_var'), 'get') else '',
                    'yongshen': info['yongshen_var'].get() if hasattr(info.get('yongshen_var'), 'get') else '',
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
            except Exception as e:
                continue
        
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
                    'hour_zhi': parts[3][1],
                    'is_sizhu_input': True  # 标记这是四柱输入模式
                }
                # 从年柱地支推断年份（仅用于显示，不用于验证）
                zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                year_zhi = parts[0][1]
                if year_zhi in zhi_order:
                    base_year = 2024
                    base_zhi_index = zhi_order.index('辰')
                    target_zhi_index = zhi_order.index(year_zhi)
                    diff = (target_zhi_index - base_zhi_index) % 12
                    sizhu['year'] = base_year + diff
                # 从月柱地支推断月份
                month_zhi = parts[1][1]
                if month_zhi in zhi_order:
                    sizhu['month'] = zhi_order.index(month_zhi) + 1
                # 从日柱地支推断日期（简化处理）
                sizhu['day'] = 1
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
            
            # 获取宅型和山向（如果是修造、动土、入宅事项）
            house_type = None
            shan_xiang = None
            jian_xiang = None
            if event_type in ["修造", "动土", "入宅"]:
                # 获取宅型
                house_type = getattr(self, 'house_type', None)
                if house_type:
                    house_type = house_type.get()
                # 获取山向
                shan_xiang = getattr(self, 'shan_xiang', None)
                if shan_xiang:
                    shan_xiang = shan_xiang.get()
                # 获取兼向
                jian_xiang = getattr(self, 'jian_xiang', None)
                if jian_xiang:
                    jian_xiang = jian_xiang.get()
            
            # 使用calculate_score进行评分
            score_result = calculate_score(sizhu, event_type, owners_detail, house_type, shan_xiang, None, None, None, jian_xiang)
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
                'shensha_list': score_result.get('shensha_list', []),
                'score_details': score_result.get('score_details', {})
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
            wuxing_score = score_details.get('五行评分', 100)
            yueling_score = score_details.get('月令得分', 0)
            xishen_score = score_details.get('喜用神得分', 0)
            huangdao_score = score_details.get('黄道得分', 0)
            
            # 获取地支关系信息（从wu_xing_result中获取详细地支关系）
            wu_xing_result = score_result.get('wu_xing_result', {})
            wu_xing_details = wu_xing_result.get('details', {})
            
            # 构建地支关系文本（显示具体的三合、六合等）
            dizhi_relations = wu_xing_details.get('地支关系', [])
            if dizhi_relations:
                # 提取地支关系的简短描述
                dizhi_text_list = []
                for relation in dizhi_relations:
                    # 提取关键信息，如"三合火局"、"六合"等
                    if '三合' in relation:
                        # 提取"三合X局"
                        import re
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
                        # 其他关系，取前10个字符
                        dizhi_text_list.append(relation[:10])
                dizhi_text = ', '.join(dizhi_text_list[:2])  # 最多显示2个关系
            else:
                dizhi_text = '-'
            
            # 获取吉神信息（从wu_xing_details中获取详细吉神）
            jishen_list = wu_xing_details.get('吉神', [])
            if jishen_list:
                # 提取吉神的简短描述
                jishen_text_list = []
                for jishen in jishen_list:
                    # 提取关键信息，如"天德贵人"、"禄神"等
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
                        # 其他吉神，取前6个字符
                        jishen_text_list.append(jishen[:6])
                jishen_text = ', '.join(jishen_text_list[:2])  # 最多显示2个吉神
            else:
                # 如果没有详细吉神，使用yi_list
                yi_list = score_result.get('yi_list', [])
                jishen_text = ', '.join(yi_list[:2]) if yi_list else '-'
            
            # 更新或添加到Treeview
            values = (current_rike, score, level, sizhu_str, wuxing_score, yueling_score, xishen_score, huangdao_score, dizhi_text, jishen_text)
            
            # 检查是否已存在于Treeview中
            existing_item = None
            for item in self.date_treeview.get_children():
                item_values = self.date_treeview.item(item, 'values')
                if item_values[0] == current_rike:
                    existing_item = item
                    break
            
            if existing_item:
                # 更新已存在的行
                self.date_treeview.item(existing_item, values=values)
            else:
                # 添加新行
                self.date_treeview.insert('', tk.END, values=values)
            
            self.scoring_results.append(result)
            
            # 显示结果
            self.show_single_result(result)
            
            # 确保日课评分系统窗口获得焦点后再显示消息框
            self.window.lift()
            self.window.focus_force()
            messagebox.showinfo("成功", f"日课评分完成！\n评分：{result['score']} 分\n等级：{result['level']}")
        except Exception as e:
            messagebox.showerror("错误", f"评分时出错: {str(e)}")
    
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
        
        # 提取大利月/小利月信息（婚嫁专用）
        daliyue_info = '-'
        event_type = result.get('event_type', '')
        if result.get('shensha_list') and event_type in ['嫁娶', '订婚', '纳采']:
            for shensha in result['shensha_list']:
                if isinstance(shensha, dict):
                    shensha_name = shensha.get('name', '')
                    if shensha_name == '大利月':
                        daliyue_info = '大利月'
                        break
                    elif shensha_name == '小利月':
                        daliyue_info = '小利月'
                        break
        
        # 如果是婚嫁择日，显示大利月/小利月信息
        if event_type in ['嫁娶', '订婚', '纳采'] and daliyue_info != '-':
            self._insert_colored_text(f"  利月：{daliyue_info}\n")
        
        self._insert_colored_text("\n")
        
        # 事主信息
        self._insert_colored_text("""【事主信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
        owners_detail = result.get('owners_detail', [])
        if owners_detail:
            for i, owner in enumerate(owners_detail[:4], 1):  # 只显示前4个事主
                name = owner.get('name', f'事主{i}')
                self._insert_colored_text(f"  【{name}】\n")
                
                if owner.get('birth_date'):
                    self._insert_colored_text(f"    出生日期: {owner['birth_date']}\n")
                
                if owner.get('sizhu'):
                    self._insert_colored_text(f"    四柱: {owner['sizhu']}\n")
                
                if owner.get('xishen'):
                    self._insert_colored_text(f"    喜神: {owner['xishen']}\n")
                
                if owner.get('yongshen'):
                    self._insert_colored_text(f"    用神: {owner['yongshen']}\n")
                
                # 如果是嫁娶，显示新娘的夫子星、阴胎、阳气
                if event_type in ['嫁娶', '订婚', '纳采', '结婚'] and owner.get('gender') == '女':
                    if owner.get('fu_xing'):
                        self._insert_colored_text(f"    夫星: {owner['fu_xing']}\n")
                    if owner.get('zi_xing'):
                        self._insert_colored_text(f"    子星: {owner['zi_xing']}\n")
                    if owner.get('yintai'):
                        self._insert_colored_text(f"    阴胎: {owner['yintai']}\n")
                    if owner.get('yangqi'):
                        self._insert_colored_text(f"    阳气: {owner['yangqi']}\n")
                
                if owner.get('match_result'):
                    self._insert_colored_text(f"    匹配结果: {owner['match_result']}\n")
                
                self._insert_colored_text("\n")
        else:
            self._insert_colored_text("  暂无事主信息\n\n")
        
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
            
            # 显示婚嫁评分详情（夫星受克等）
            marriage_details = result.get('marriage_details', [])
            if marriage_details:
                for detail_name, detail_score in marriage_details:
                    if detail_score != 0:
                        self._insert_colored_text(f"    {'├─' if score_breakdown else ''}{detail_name}：{detail_score:+d} 分\n")
            
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
                # 处理shensha可能是字符串或字典的情况
                if isinstance(shensha, dict):
                    name = shensha.get('name', '')
                    desc = shensha.get('description', '')
                    self._insert_colored_text(f"  • {name}: {desc}\n")
                else:
                    # 如果是字符串，直接显示
                    self._insert_colored_text(f"  • {shensha}\n")
            self._insert_colored_text("\n")
        
        # 二十四山动土方位吉凶（仅限修造相关事件）
        event_type = result.get('event_type', '')
        construction_events = ['修造', '动土', '装修', '入宅', '安床', '作灶']
        
        if result.get('sizhu') and event_type in construction_events:
            from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
            construction_shensha = ConstructionShenShaCheckerExt()
            lucky_directions = construction_shensha.get_lucky_directions(result['sizhu'])
            
            # 修造专属信息（扶山相主补龙、山家吉凶、时辰吉凶、建除十二神等）
            if event_type in construction_events and result.get('shensha_list'):
                self._insert_colored_text("""【修造择日分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
                
                # 获取坐山和主命信息
                zuoshan = None
                zhuming = None
                
                # 从owners_detail中获取事主信息
                owners_detail = result.get('owners_detail', [])
                if owners_detail:
                    owner_info = owners_detail[0]
                    if owner_info.get('sizhu'):
                        zhuming = owner_info['sizhu']
                
                # 显示神煞分类
                shensha_items = result.get('shensha_list', [])
                fushan_items = []
                xiangzhu_items = []
                shanjia_items = []
                direction_items = []
                hour_items = []
                jianchu_items = []
                other_items = []
                
                for s in shensha_items:
                    # 处理s可能是字符串或字典的情况
                    if isinstance(s, dict):
                        name = s.get('name', '')
                        desc = s.get('description', '')
                        score = s.get('score', 0)
                        tag = f"{name}: {desc}（{score:+.0f}分）"
                    else:
                        # 如果是字符串，直接使用
                        name = str(s)
                        desc = ''
                        score = 0
                        tag = name
                    
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
                    self._insert_colored_text("\n  【扶山·相主·补龙】\n")
                    for item in fushan_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if shanjia_items:
                    self._insert_colored_text("\n  【山家吉凶】\n")
                    for item in shanjia_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if direction_items:
                    self._insert_colored_text("\n  【动土方位凶煞】\n")
                    for item in direction_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if hour_items:
                    self._insert_colored_text("\n  【时辰吉凶】\n")
                    for item in hour_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                if jianchu_items:
                    self._insert_colored_text("\n  【建除十二神】\n")
                    for item in jianchu_items:
                        self._insert_colored_text(f"    • {item}\n")
                
                self._insert_colored_text("\n")
            
            # 整理方位数据，按方向分组
            direction_groups = {
                '北方': ['壬', '子', '癸'],
                '东北': ['丑', '艮', '寅'],
                '东方': ['甲', '卯', '乙'],
                '东南': ['辰', '巽', '巳'],
                '南方': ['丙', '午', '丁'],
                '西南': ['未', '坤', '申'],
                '西方': ['庚', '酉', '辛'],
                '西北': ['戌', '乾', '亥']
            }
            
            # 创建方位分数映射
            direction_scores = {item['方位']: item['分值'] for item in lucky_directions}
            
            self._insert_colored_text("""【二十四山动土方位吉凶】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  （0分=安全可用，负分=犯煞不宜）

""")
            
            for direction, shan_list in direction_groups.items():
                self._insert_colored_text(f"    {direction}：")
                for i, shan in enumerate(shan_list):
                    score = direction_scores.get(shan, 0)
                    if score < 0:
                        # 负分显示红色
                        self._insert_colored_text(f"{shan}({score}分)  ", "unusable")
                    else:
                        # 0分显示正常
                        self._insert_colored_text(f"{shan}({score}分)  ")
                self._insert_colored_text("\n\n")
            
            # 显示犯煞方位的具体说明
            bad_directions = [item for item in lucky_directions if item['分值'] < 0]
            safe_directions = [item for item in lucky_directions if item['分值'] == 0]
            
            if safe_directions:
                safe_names = '、'.join([f"{d['方位']}({d['分值']}分)" for d in safe_directions])
                self._insert_colored_text(f"\n  ★ 安全方位（共{len(safe_directions)}个）：{safe_names}\n")
            
            if bad_directions:
                self._insert_colored_text(f"  ✗ 犯煞方位（共{len(bad_directions)}个）：")
                for d in bad_directions:
                    self._insert_colored_text(f"\n    {d['方位']}（{d['分值']}分）：{'、'.join(d['说明'])}")
                self._insert_colored_text("\n")
        
        # 评语
        if result.get('reason'):
            # 判断是否可用
            score = result.get('score', 0)
            level = result.get('level', '')
            
            # 判断是否可用（分数>=80且等级不为凶）
            is_usable = score >= 80 and '凶' not in level
            
            if is_usable:
                usability_text = "✓ 此日课可用"
                usability_tag = "usable"
            else:
                usability_text = "✗ 此日课不宜使用"
                usability_tag = "unusable"
            
            self._insert_colored_text(f"""【综合评语】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {result['reason']}

""")
            # 显示是否可用
            self._insert_colored_text(f"【使用建议】\n", "bold")
            if is_usable:
                self._insert_colored_text(f"  ✓ 此日课综合评分{score}分，等级为{level}，", "usable")
                self._insert_colored_text("可以使用\n", "usable")
            else:
                self._insert_colored_text(f"  ✗ 此日课综合评分{score}分，等级为{level}，", "unusable")
                self._insert_colored_text("不建议使用\n", "unusable")
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
            # 提示用户将使用当前界面事主信息进行自动评分
            if unscored_dates:
                msg = f"发现有 {len(unscored_dates)} 个日课未评分。\n将使用当前界面输入的事主信息进行自动评分。\n\n如需使用其他事主信息，请先在界面中修改事主资料。"
                messagebox.showinfo("自动评分提示", msg)

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
                except Exception as e:
                    continue
            
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
                    
                    # 获取宅型和山向（如果是修造、动土、入宅事项）
                    house_type = None
                    shan_xiang = None
                    if event_type in ["修造", "动土", "入宅"]:
                        # 获取宅型
                        house_type = getattr(self, 'house_type', None)
                        if house_type:
                            house_type = house_type.get()
                        # 获取山向
                        shan_xiang = getattr(self, 'shan_xiang', None)
                        if shan_xiang:
                            shan_xiang = shan_xiang.get()
                        # 获取兼向
                        jian_xiang = getattr(self, 'jian_xiang', None)
                        if jian_xiang:
                            jian_xiang = jian_xiang.get()
                    
                    # 使用calculate_score进行评分
                    score_result = calculate_score(sizhu, event_type, owners_detail, house_type, shan_xiang, None, None, None, jian_xiang)
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
                year = info['solar_year'].get()
                month = info['solar_month'].get()
                day = info['solar_day'].get()
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
        
        imported_count = 0
        
        try:
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
                                    continue
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
                                continue
            else:
                # 导入文本格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 尝试提取日期（格式：YYYY-MM-DD）
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
        10. 保存评分结果：保存当前显示的评分结果
        
        注意事项：
        - 事主信息为可选，可根据实际情况填写
        - 对比分析需要至少两个日课
        - 保存功能支持文本和JSON格式
        """
        messagebox.showinfo("帮助", help_text)
    
    def save_score_result(self):
        """保存当前评分结果"""
        try:
            # 检查是否有评分结果
            if not self.scoring_results:
                messagebox.showwarning("提示", "请先进行日课评分")
                return
            
            # 获取当前显示的结果
            current_text = self.result_text.get(1.0, tk.END).strip()
            if not current_text:
                messagebox.showwarning("提示", "没有评分结果可保存")
                return
            
            # 打开文件保存对话框
            import tkinter.filedialog as filedialog
            
            # 定义文件类型
            file_types = [
                ("文本文件", "*.txt"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
            
            # 获取保存路径
            file_path = filedialog.asksaveasfilename(
                title="保存评分结果",
                filetypes=file_types,
                defaultextension=".txt",
                initialfile=f"日课评分结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if not file_path:
                return  # 用户取消保存
            
            # 根据文件扩展名保存
            if file_path.endswith('.json'):
                # 保存为JSON格式
                # 获取最新的评分结果
                latest_result = self.scoring_results[-1]
                
                json_data = {
                    'score_result': latest_result,
                    'save_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'event_type': self.event_var.get(),
                    'content': current_text
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            else:
                # 保存为文本格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_text)
                    f.write('\n\n')
                    f.write(f"保存时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"事项类型：{self.event_var.get()}\n")
            
            messagebox.showinfo("成功", f"评分结果已保存到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")



# 独立运行入口
if __name__ == '__main__':
    app = DayScoreWindow()
    app.run()
