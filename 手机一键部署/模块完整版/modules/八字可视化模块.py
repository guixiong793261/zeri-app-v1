# -*- coding: utf-8 -*-
"""
================================================================================
八字可视化模块
================================================================================
提供八字排盘的可视化展示功能，包括：
- 八字排盘表格
- 五行图表
- 十神分布图
- 大运流年图
- 综合分析报告

【重要说明】
本模块统一使用八字排盘模块作为四柱计算的唯一入口
================================================================================
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, List, Optional
import logging
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

# 导入八字排盘模块（唯一入口）
from modules.八字排盘 import BaZiPanPan


class BaZiInputDialog:
    """
    八字排盘输入对话框
    
    让用户输入出生信息和性别，然后显示八字排盘
    """
    
    def __init__(self, parent: tk.Tk):
        """
        初始化输入对话框
        
        Args:
            parent: 父窗口
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("八字排盘")
        self.dialog.geometry("500x350")
        
        # 居中显示
        self.dialog.update_idletasks()
        width = 500  # 使用固定宽度
        height = 350  # 使用固定高度
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # 创建输入界面
        self._create_input_ui()
    
    def _create_input_ui(self):
        """创建输入界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="请输入出生信息", 
                             font=("微软雅黑", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 性别选择
        gender_frame = ttk.LabelFrame(main_frame, text="性别", padding="10")
        gender_frame.pack(fill=tk.X, pady=10)
        
        self.gender_var = tk.StringVar(value='男')
        ttk.Radiobutton(gender_frame, text="男", variable=self.gender_var, 
                       value='男').pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(gender_frame, text="女", variable=self.gender_var, 
                       value='女').pack(side=tk.LEFT, padx=20)
        
        # 出生日期时间
        date_frame = ttk.LabelFrame(main_frame, text="出生日期时间", padding="10")
        date_frame.pack(fill=tk.X, pady=10)
        
        # 年月日
        date_row1 = ttk.Frame(date_frame)
        date_row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_row1, text="年:").pack(side=tk.LEFT, padx=(0, 10))
        self.year_var = tk.StringVar(value=str(1990))
        year_entry = ttk.Entry(date_row1, textvariable=self.year_var, width=8)
        year_entry.pack(side=tk.LEFT, padx=5)
        year_entry.insert(0, "1990")
        ttk.Label(date_row1, text="(1900-2100)", font=("微软雅黑", 8, "italic")).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_row1, text="月:").pack(side=tk.LEFT, padx=(20, 10))
        self.month_var = tk.StringVar(value="5")
        month_entry = ttk.Entry(date_row1, textvariable=self.month_var, width=5)
        month_entry.pack(side=tk.LEFT, padx=5)
        month_entry.insert(0, "5")
        ttk.Label(date_row1, text="(1-12)", font=("微软雅黑", 8, "italic")).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_row1, text="日:").pack(side=tk.LEFT, padx=(20, 10))
        self.day_var = tk.StringVar(value="15")
        day_entry = ttk.Entry(date_row1, textvariable=self.day_var, width=5)
        day_entry.pack(side=tk.LEFT, padx=5)
        day_entry.insert(0, "15")
        ttk.Label(date_row1, text="(1-31)", font=("微软雅黑", 8, "italic")).pack(side=tk.LEFT, padx=5)
        
        # 时分
        date_row2 = ttk.Frame(date_frame)
        date_row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_row2, text="时:").pack(side=tk.LEFT, padx=(0, 10))
        self.hour_var = tk.StringVar(value="10")
        hour_entry = ttk.Entry(date_row2, textvariable=self.hour_var, width=5)
        hour_entry.pack(side=tk.LEFT, padx=5)
        hour_entry.insert(0, "10")
        ttk.Label(date_row2, text="(0-23)", font=("微软雅黑", 8, "italic")).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_row2, text="分:").pack(side=tk.LEFT, padx=(20, 10))
        self.minute_var = tk.StringVar(value="30")
        minute_entry = ttk.Entry(date_row2, textvariable=self.minute_var, width=5)
        minute_entry.pack(side=tk.LEFT, padx=5)
        minute_entry.insert(0, "30")
        ttk.Label(date_row2, text="(0-59)", font=('微软雅黑', 8, 'italic')).pack(side=tk.LEFT, padx=5)
        
        # 提示信息
        tip_label = ttk.Label(main_frame, text="提示：请输入准确的出生时间，以确保排盘结果的准确性", 
                             font=('微软雅黑', 10, 'italic'), foreground="#666666")
        tip_label.pack(pady=(10, 5))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="开始排盘", 
                  command=self._start_panpan, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", 
                  command=self.dialog.destroy, width=10).pack(side=tk.RIGHT, padx=10)
    
    def _start_panpan(self):
        """开始排盘"""
        try:
            # 获取输入值
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            gender = self.gender_var.get()
            
            # 验证输入
            if not (1900 <= year <= 2100):
                raise ValueError("年份必须在1900-2100之间")
            if not (1 <= month <= 12):
                raise ValueError("月份必须在1-12之间")
            if not (1 <= day <= 31):
                raise ValueError("日期必须在1-31之间")
            if not (0 <= hour <= 23):
                raise ValueError("小时必须在0-23之间")
            if not (0 <= minute <= 59):
                raise ValueError("分钟必须在0-59之间")
            
            # 验证日期是否有效（考虑闰年）
            import calendar
            max_day = calendar.monthrange(year, month)[1]
            if day > max_day:
                raise ValueError(f"该月份只有{max_day}天，请输入正确的日期")
            
            # 使用八字排盘模块创建排盘
            bazi = BaZiPanPan(
                year, month, day, hour, minute, gender
            )
            panpan_data = bazi.calculate()
            
            # 关闭输入对话框
            self.dialog.destroy()
            
            # 强制更新主窗口，确保输入对话框完全关闭
            self.dialog.master.update()
            
            # 显示排盘结果对话框
            BaZiDialog(self.dialog.master, panpan_data)
            
        except ValueError as e:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("输入错误", str(e))
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("错误", f"排盘失败：{str(e)}")


class BaZiDialog:
    """
    八字排盘对话框
    
    独立的八字排盘展示窗口
    """
    
    def __init__(self, parent: tk.Tk, panpan_data: Dict = None):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            panpan_data: 排盘数据
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("八字排盘详情")
        self.dialog.geometry("1200x700")
        
        # 创建主滚动区域
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        main_frame = ttk.Frame(canvas)
        
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=main_frame, anchor="nw", width=1180)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass  # 忽略canvas已销毁时的错误
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 显示排盘数据
        if panpan_data:
            self._display_panpan(main_frame, panpan_data)
        
        # 关闭按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="关闭", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="打印", 
                  command=lambda: self._print_panpan(panpan_data)).pack(side=tk.RIGHT, padx=5)
    
    def _display_panpan(self, parent_frame: tk.Frame, panpan_data: Dict):
        """
        显示排盘数据
        
        Args:
            parent_frame: 父级Frame容器
            panpan_data: 排盘数据字典
        """
        # 基本信息区域（上方）
        basic_frame = ttk.LabelFrame(parent_frame, text="基本信息", padding="10")
        basic_frame.pack(fill=tk.X, padx=10, pady=5)
        
        basic_info = panpan_data.get('基本信息', {})
        info_items = [
            ('性别', basic_info.get('性别', '-')),
            ('出生日期', basic_info.get('出生日期', '-'))
        ]
        
        for i, (key, value) in enumerate(info_items):
            ttk.Label(basic_frame, text=f"{key}:").grid(row=0, column=i*2, sticky=tk.W, padx=5)
            ttk.Label(basic_frame, text=value, font=("微软雅黑", 10, "bold")).grid(row=0, column=i*2+1, sticky=tk.W, padx=5)
        
        # 创建左右分栏的主框架
        main_content_frame = ttk.Frame(parent_frame)
        main_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧区域（四柱排盘 + 五行分析）
        left_frame = ttk.Frame(main_content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 四柱排盘区域
        sizhu_frame = ttk.LabelFrame(left_frame, text="四柱排盘", padding="10")
        sizhu_frame.pack(fill=tk.X, pady=5)
        
        sizhu = panpan_data.get('四柱', {})
        nayin = panpan_data.get('纳音', {})
        shengyang = panpan_data.get('十二长生', {})
        
        # 创建四柱表格
        columns = ['', '年柱', '月柱', '日柱', '时柱']
        sizhu_tree = ttk.Treeview(sizhu_frame, columns=columns, 
                                   show="headings", height=5)
        
        for col in columns:
            sizhu_tree.heading(col, text=col)
            sizhu_tree.column(col, width=120, anchor='center')
        
        # 添加行
        sizhu_tree.insert('', 'end', values=['天干', 
                                               sizhu.get('年柱', '')[0] if sizhu.get('年柱') else '-',
                                               sizhu.get('月柱', '')[0] if sizhu.get('月柱') else '-',
                                               sizhu.get('日柱', '')[0] if sizhu.get('日柱') else '-',
                                               sizhu.get('时柱', '')[0] if sizhu.get('时柱') else '-'])
        
        sizhu_tree.insert('', 'end', values=['地支', 
                                               sizhu.get('年柱', '')[1] if len(sizhu.get('年柱', '')) > 1 else '-',
                                               sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else '-',
                                               sizhu.get('日柱', '')[1] if len(sizhu.get('日柱', '')) > 1 else '-',
                                               sizhu.get('时柱', '')[1] if len(sizhu.get('时柱', '')) > 1 else '-'])
        
        sizhu_tree.insert('', 'end', values=['纳音', 
                                               nayin.get('年柱', '-'),
                                               nayin.get('月柱', '-'),
                                               nayin.get('日柱', '-'),
                                               nayin.get('时柱', '-')])
        
        sizhu_tree.insert('', 'end', values=['十二长生', 
                                               shengyang.get('年支', '-'),
                                               shengyang.get('月支', '-'),
                                               shengyang.get('日支', '-'),
                                               shengyang.get('时支', '-')])
        
        sizhu_tree.insert('', 'end', values=['十神', 
                                               panpan_data.get('十神', {}).get('年干', '-'),
                                               panpan_data.get('十神', {}).get('月干', '-'),
                                               '日主',
                                               panpan_data.get('十神', {}).get('时干', '-')])
        
        sizhu_tree.pack(fill=tk.X)
        
        # 五行分析区域（下方）
        wuxing_frame = ttk.LabelFrame(left_frame, text="五行分析", padding="10")
        wuxing_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        wuxing_score = panpan_data.get('五行分数', {})
        wuxing_labels = {}
        wuxing_items = ['金', '木', '水', '火', '土']
        for i, wx in enumerate(wuxing_items):
            ttk.Label(wuxing_frame, text=f"{wx}:").grid(row=0, column=i*2, sticky=tk.W, padx=5)
            score = wuxing_score.get(wx, 0)
            wuxing_labels[wx] = ttk.Label(wuxing_frame, text=f"{score:.2f}", font=("微软雅黑", 10, "bold"))
            wuxing_labels[wx].grid(row=0, column=i*2+1, sticky=tk.W, padx=5)
        
        # 五行说明
        wuxing_text = scrolledtext.ScrolledText(wuxing_frame, wrap=tk.WORD, height=10)
        wuxing_text.grid(row=1, column=0, columnspan=10, sticky=tk.EW, pady=5)
        
        wuxing_desc = self._format_wuxing(wuxing_score)
        wuxing_text.insert(tk.END, wuxing_desc)
        wuxing_text.config(state=tk.DISABLED)
        
        # 右侧区域（大运分析）
        right_frame = ttk.Frame(main_content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # 大运分析区域
        dayun_frame = ttk.LabelFrame(right_frame, text="大运分析", padding="10")
        dayun_frame.pack(fill=tk.BOTH, expand=True)
        
        # 起运信息
        start_age = panpan_data.get('起运年龄', 0)
        start_year = panpan_data.get('起运年份', 0)
        ttk.Label(dayun_frame, text=f"起运年龄: {start_age}岁  起运年份: {start_year}年", 
                 font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        # 大运表格
        dayun_columns = ['序号', '大运', '起运年龄', '起运年份', '纳音']
        dayun_tree = ttk.Treeview(dayun_frame, columns=dayun_columns, 
                                   show="headings", height=15)
        
        for col in dayun_columns:
            dayun_tree.heading(col, text=col)
            dayun_tree.column(col, width=80, anchor='center')
        
        dayun_list = panpan_data.get('大运', [])
        for dayun in dayun_list:
            dayun_tree.insert('', 'end', values=(
                dayun.get('序号', ''),
                dayun.get('大运', ''),
                f"{dayun.get('起运年龄', 0)}岁",
                dayun.get('起运年份', ''),
                dayun.get('纳音', '-')
            ))
        
        dayun_tree.pack(fill=tk.BOTH, expand=True)
    
    def _format_wuxing(self, wuxing: Dict) -> str:
        """格式化五行信息"""
        if not wuxing:
            return "暂无五行信息"
        
        total = sum(wuxing.values())
        if total == 0:
            return "五行数据异常"
        
        lines = ["五行分布:"]
        for wx in ['金', '木', '水', '火', '土']:
            count = wuxing.get(wx, 0)
            percentage = (count / total) * 100 if total > 0 else 0
            bar = '█' * int(percentage / 5)
            lines.append(f"  {wx}: {count:.2f} ({percentage:.1f}%) {bar}")
        
        return '\n'.join(lines)
    
    def _print_panpan(self, panpan_data: Dict):
        """打印排盘数据"""
        try:
            import tkinter.filedialog as filedialog
            
            file_path = filedialog.asksaveasfilename(
                title="保存八字排盘",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 保存为文本文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("八字排盘详情\n")
                f.write("=" * 60 + "\n\n")
                
                # 基本信息
                basic_info = panpan_data.get('基本信息', {})
                f.write(f"性别: {basic_info.get('性别', '-')}\n")
                f.write(f"出生日期: {basic_info.get('出生日期', '-')}\n\n")
                
                # 四柱排盘
                sizhu = panpan_data.get('四柱', {})
                f.write("四柱排盘:\n")
                f.write(f"  年柱: {sizhu.get('年柱', '-')}\n")
                f.write(f"  月柱: {sizhu.get('月柱', '-')}\n")
                f.write(f"  日柱: {sizhu.get('日柱', '-')}\n")
                f.write(f"  时柱: {sizhu.get('时柱', '-')}\n\n")
                
                # 纳音
                nayin = panpan_data.get('纳音', {})
                f.write("纳音:\n")
                f.write(f"  年柱: {nayin.get('年柱', '-')}\n")
                f.write(f"  月柱: {nayin.get('月柱', '-')}\n")
                f.write(f"  日柱: {nayin.get('日柱', '-')}\n")
                f.write(f"  时柱: {nayin.get('时柱', '-')}\n\n")
                
                # 十二长生
                shengyang = panpan_data.get('十二长生', {})
                f.write("十二长生:\n")
                f.write(f"  年支: {shengyang.get('年支', '-')}\n")
                f.write(f"  月支: {shengyang.get('月支', '-')}\n")
                f.write(f"  日支: {shengyang.get('日支', '-')}\n")
                f.write(f"  时支: {shengyang.get('时支', '-')}\n\n")
                
                # 十神
                shishen = panpan_data.get('十神', {})
                f.write("十神:\n")
                f.write(f"  年干: {shishen.get('年干', '-')}\n")
                f.write(f"  月干: {shishen.get('月干', '-')}\n")
                f.write(f"  时干: {shishen.get('时干', '-')}\n\n")
                
                # 五行分数
                wuxing_score = panpan_data.get('五行分数', {})
                f.write("五行分数:\n")
                for wx in ['金', '木', '水', '火', '土']:
                    f.write(f"  {wx}: {wuxing_score.get(wx, 0):.2f}\n")
                f.write("\n")
                
                # 大运
                dayun_list = panpan_data.get('大运', [])
                f.write("大运:\n")
                f.write(f"  起运年龄: {panpan_data.get('起运年龄', 0)}岁\n")
                f.write(f"  起运年份: {panpan_data.get('起运年份', 0)}年\n\n")
                
                for dayun in dayun_list:
                    f.write(f"  {dayun.get('序号', '')}. {dayun.get('大运', '')} ")
                    f.write(f"({dayun.get('起运年龄', 0)}岁, {dayun.get('起运年份', '')}年) ")
                    f.write(f"纳音: {dayun.get('纳音', '-')}\n")
            
            import tkinter.messagebox as messagebox
            messagebox.showinfo("成功", f"八字排盘已保存到：{file_path}")
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("错误", f"保存失败：{str(e)}")


def show_bazi_input_dialog(parent: tk.Tk):
    """
    显示八字排盘输入对话框
    
    Args:
        parent: 父窗口
    """
    BaZiInputDialog(parent)


def show_bazi_dialog(parent: tk.Tk, panpan_data: Dict):
    """
    显示八字排盘对话框
    
    Args:
        parent: 父窗口
        panpan_data: 排盘数据
    """
    BaZiDialog(parent, panpan_data)


def show_bazi_from_birth(parent: tk.Tk, year: int, month: int, day: int, 
                         hour: int = 12, minute: int = 0, gender: str = '男',
                         use_true_solar: bool = False, longitude: float = 120.0, latitude: float = 30.0):
    """
    从出生信息直接显示八字排盘
    
    Args:
        parent: 父窗口
        year: 出生年
        month: 出生月
        day: 出生日
        hour: 出生时（默认12）
        minute: 出生分（默认0）
        gender: 性别（默认'男'）
        use_true_solar: 是否使用真太阳时（默认False）
        longitude: 经度（默认120.0，北京时间基准）
        latitude: 纬度（默认30.0，参考值）
        
    Returns:
        BaZiDialog: 对话框对象
    """
    # 使用八字排盘模块创建排盘
    bazi = BaZiPanPan(
        year, month, day, hour, minute, gender,
        use_true_solar=use_true_solar,
        longitude=longitude,
        latitude=latitude
    )
    panpan_data = bazi.get_panpan_result()
    
    # 显示对话框
    dialog = BaZiDialog(parent, panpan_data)
    
    return dialog


if __name__ == '__main__':
    # 测试代码
    root = tk.Tk()
    root.title("八字可视化模块测试")
    # 隐藏根窗口，只显示排盘对话框
    root.withdraw()
    
    # 测试显示八字排盘（不使用真太阳时）
    dialog = show_bazi_from_birth(root, 1990, 5, 15, 10, 30, '男')
    
    root.mainloop()
