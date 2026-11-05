# -*- coding: utf-8 -*-
"""
玄空飞星 · 日课展示 (桌面版)
九宫格显示：数字（右）、星名（中）、方位（左），分列显示，避免重叠
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
from datetime import datetime, date, timedelta
import calendar

try:
    from modules.高精度农历转换 import get_lunar_converter
    from modules.四柱计算器 import calculate_sizhu
except ImportError:
    messagebox.showerror("导入错误", "无法导入 modules 目录下的高精度模块，请检查路径")
    sys.exit(1)

import sxtwl

# ============================================================
#  飞星核心算法 / 坐山分析 / 评语 —— 统一来自 modules/玄空飞星引擎.py
#  （单一数据源；排盘常量、洛书飞布、冬至夏至日星、坐山吉凶、
#    数值评分均不在此手抄，避免与评分器双标准漂移）
# ============================================================
from modules.玄空飞星引擎 import (
    DIZHI, MONTH_ZHI_TO_INDEX, HOUR_ZHI_TO_INDEX,
    BASE_MONTH_STAR, BASE_HOUR_STAR, STAR_NAMES, LUO_SHU_ORDER,
    MOUNTAINS_CW, MOUNTAIN_DIRECTION, MOUNTAIN_LABELS, MOUNTAIN_TO_INDEX,
    POS_NAMES, GONG_NAMES, GUA_NAMES, GOOD_STARS, BAD_STARS,
    get_grid_by_middle, get_solstice_info, compute_stars, get_xuan_kong_data,
    get_mountain_label, analyze_mountain, generate_xuankong_comment,
    score_feixing,
)

# ============================================================
#  GUI 界面 (tkinter) — 分列显示数字、星名、方位
# ============================================================
STAR_TYPES = [0, '吉','凶','凶','平','凶','吉','凶','吉','吉']
POS_NAMES = ['东南','南','西南','东','中','西','东北','北','西北']
# 九宫索引对应的八卦卦名（与POS_NAMES同序：0巽/1离/2坤/3震/4中/5兑/6艮/7坎/8乾）
GUA_NAMES = ['巽','离','坤','震','中','兑','艮','坎','乾']
COLORS = {
    '吉': '#3c6e3c', '凶': '#6e3c3c', '平': '#3a4558',
    '吉_text': '#8bc34a', '凶_text': '#e57373', '平_text': '#7fc1b0',
    'star_num': '#f5c542'
}

class XuanKongApp:
    def __init__(self, root, preset=None):
        self.root = root
        self.root.title("玄空飞星 · 日课模块 (二十四山兼向)")
        self.root.geometry("1020x940")
        self.root.configure(bg='#0b0e14')
        self.root.resizable(True, True)
        self._preset = preset or {}  # 由择日结果自动带入的日期/时/坐山/兼向

        top = tk.Frame(root, bg='#141a24', pady=10)
        top.pack(fill='x', padx=20, pady=10)

        tk.Label(top, text="选择日期时间：", fg='#e8edf5', bg='#141a24', font=('微软雅黑', 12)).pack(side='left')

        now = datetime.now()
        self.year_var = tk.StringVar(value=str(now.year))
        self.month_var = tk.StringVar(value=str(now.month))
        self.day_var = tk.StringVar(value=str(now.day))
        self.hour_var = tk.StringVar(value=str(now.hour))
        self.minute_var = tk.StringVar(value=str(now.minute))

        self._add_spinbox(top, "年", self.year_var, 1900, 2100, 4)
        self._add_spinbox(top, "月", self.month_var, 1, 12, 2)
        self._add_spinbox(top, "日", self.day_var, 1, 31, 2)
        self._add_spinbox(top, "时", self.hour_var, 0, 23, 2)
        self._add_spinbox(top, "分", self.minute_var, 0, 59, 2)

        tk.Label(top, text=" 山向：", fg='#e8edf5', bg='#141a24', font=('微软雅黑', 12)).pack(side='left', padx=(10,2))
        self.mountain_var = tk.StringVar()
        self.mountain_combo = ttk.Combobox(top, textvariable=self.mountain_var, values=MOUNTAIN_LABELS,
                                           width=14, state='readonly', font=('微软雅黑', 10))
        self.mountain_combo.pack(side='left', padx=2)
        self.mountain_combo.set('子山 · 正北')

        tk.Label(top, text=" 兼向：", fg='#e8edf5', bg='#141a24', font=('微软雅黑', 10)).pack(side='left', padx=(10,2))
        self.jianxiang_var = tk.StringVar(value="正向")
        self.jianxiang_combo = ttk.Combobox(top, textvariable=self.jianxiang_var, values=["正向"],
                                            width=8, state='readonly', font=('微软雅黑', 10))
        self.jianxiang_combo.pack(side='left', padx=2)

        self.mountain_label_var = tk.StringVar(value="")
        self.mountain_label_display = tk.Label(top, textvariable=self.mountain_label_var,
                                               fg='#d4af70', bg='#141a24', font=('微软雅黑', 10, 'bold'))
        self.mountain_label_display.pack(side='left', padx=15)

        tk.Button(top, text="刷新飞星", command=self.update_grids,
                  bg='#d4af70', fg='#0b0e14', font=('微软雅黑', 10, 'bold'), padx=10).pack(side='left', padx=10)
        tk.Button(top, text="🔍 吉日搜索", command=self._open_feixing_search,
                  bg='#3a6ea5', fg='#ffffff', font=('微软雅黑', 10, 'bold'), padx=10).pack(side='left', padx=4)

        self.mountain_combo.bind('<<ComboboxSelected>>', self._on_mountain_change)
        self.jianxiang_combo.bind('<<ComboboxSelected>>', self.update_mountain_label)
        # 初始化兼向选项
        self._update_jianxiang_options()
        # 自动带入择日结果的日期/时/坐山/兼向（末尾 update_grids 即据此自动分析）
        self._apply_preset(self._preset)

        # 范围声明（2026-11-05 用户指令2）：明确本模块边界，避免误当完整玄空风水排盘
        tk.Label(
            root,
            text=('📌 本模块仅提供日课紫白四盘（年月日时）辅助吉凶，'
                  '不包含宅运盘、替卦、元运旺衰等风水排盘内容。'),
            fg='#ffd27a', bg='#3a2f1a', font=('微软雅黑', 10),
            anchor='w', justify='left', wraplength=940, padx=10, pady=6
        ).pack(fill='x', padx=20, pady=(0, 6))

        self.info_label = tk.Label(root, text="", fg='#d4af70', bg='#0b0e14', font=('微软雅黑', 10))
        self.info_label.pack(pady=5)

        self.grid_frame = tk.Frame(root, bg='#0b0e14')
        self.grid_frame.pack(fill='both', expand=False, padx=20, pady=10)
        self.grid_frame.grid_propagate(False)
        self.grid_frame.config(height=420)

        self.cells = []
        for i in range(4):
            f = tk.Frame(self.grid_frame, bg='#141a24', relief='ridge', bd=2)
            row, col = divmod(i, 2)
            f.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            self.cells.append(f)
        self.grid_frame.grid_rowconfigure(0, weight=1)
        self.grid_frame.grid_rowconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

        self.summary_label = tk.Label(root, text="", fg='#6f7d98', bg='#0b0e14', font=('微软雅黑', 9))
        self.summary_label.pack(pady=5)

        self.comment_text = scrolledtext.ScrolledText(root, wrap=tk.WORD,
                                                      fg='#e8edf5', bg='#1a222e',
                                                      font=('微软雅黑', 12), relief='flat')
        self.comment_text.pack(fill='both', expand=True, padx=20, pady=5)

        self.update_mountain_label()
        self.update_grids()

    def _apply_preset(self, preset):
        """从择日结果自动带入：年月日时分、坐山、兼向。
        preset = dict(year, month, day, hour, minute, mountain(单字), jianxiang('正向'/'兼X'))。
        设置变量后，__init__ 末尾的 update_grids 会据此自动分析。"""
        if not preset:
            return
        try:
            if preset.get('year') is not None:
                self.year_var.set(str(preset['year']))
            if preset.get('month') is not None:
                self.month_var.set(str(preset['month']))
            if preset.get('day') is not None:
                self.day_var.set(str(preset['day']))
            if preset.get('hour') is not None:
                self.hour_var.set(str(preset['hour']))
            if preset.get('minute') is not None:
                self.minute_var.set(str(preset['minute']))
            m = preset.get('mountain')
            if m and m in MOUNTAINS_CW:
                self.mountain_var.set(f"{m}山 · {MOUNTAIN_DIRECTION.get(m, '')}")
                # 坐山变了，兼向下拉选项也要跟着重建
                self._update_jianxiang_options()
            jx = preset.get('jianxiang')
            if jx:
                vals = list(self.jianxiang_combo['values'])
                if jx in vals:
                    self.jianxiang_var.set(jx)
                elif jx == '正向' or '正向' in vals:
                    self.jianxiang_var.set('正向')
        except Exception as e:
            print(f"[玄空飞星] 自动带入择日信息失败: {e}")

    def _add_spinbox(self, parent, label, var, from_, to, width):
        tk.Label(parent, text=label, fg='#e8edf5', bg='#141a24', font=('微软雅黑', 10)).pack(side='left', padx=(5,2))
        sb = tk.Spinbox(parent, textvariable=var, from_=from_, to=to, width=width,
                        bg='#1f2838', fg='#e8edf5', font=('微软雅黑', 10), relief='flat')
        sb.pack(side='left', padx=(0,10))

    def _get_selected_mountain(self):
        """从山向下拉框文字（如'子山 · 正北'）解析出单字山名（如'子'）"""
        text = self.mountain_var.get().strip()
        for m in MOUNTAINS_CW:
            if text.startswith(m + '山'):
                return m
        return text if text in MOUNTAINS_CW else None

    def _get_jianxiang_offset(self):
        """兼向文字 → 偏移角度：正向0.0；兼逆时针邻山(idx-1)为-4.0；兼顺时针邻山(idx+1)为+4.0"""
        mountain = self._get_selected_mountain()
        jx = self.jianxiang_var.get().strip()
        if not mountain or jx == '正向' or not jx.startswith('兼'):
            return 0.0
        target = jx[1:]
        if mountain not in MOUNTAINS_CW or target not in MOUNTAINS_CW:
            return 0.0
        idx = MOUNTAINS_CW.index(mountain)
        if MOUNTAINS_CW[(idx - 1) % 24] == target:
            return -4.0
        if MOUNTAINS_CW[(idx + 1) % 24] == target:
            return 4.0
        return 0.0

    def _update_jianxiang_options(self):
        """根据当前山向，更新兼向下拉框选项（正向 + 左右两个相邻山）"""
        mountain = self._get_selected_mountain()
        if mountain and mountain in MOUNTAINS_CW:
            idx = MOUNTAINS_CW.index(mountain)
            prev_m = MOUNTAINS_CW[(idx - 1) % 24]
            next_m = MOUNTAINS_CW[(idx + 1) % 24]
            self.jianxiang_combo['values'] = ["正向", f"兼{prev_m}", f"兼{next_m}"]
        else:
            self.jianxiang_combo['values'] = ["正向"]

    def _on_mountain_change(self, event=None):
        """山向切换时：重置兼向为正向，刷新兼向选项，更新标签"""
        self.jianxiang_var.set("正向")
        self._update_jianxiang_options()
        self.update_mountain_label()

    def update_mountain_label(self, event=None):
        mountain = self._get_selected_mountain()
        offset = self._get_jianxiang_offset()
        if mountain and mountain in MOUNTAINS_CW:
            label = get_mountain_label(mountain, offset)
            self.mountain_label_var.set(f"→ {label}")
        else:
            self.mountain_label_var.set("")

    def _open_feixing_search(self):
        """打开纯飞星吉日批量搜索窗口（自动带入当前日期/坐山/兼向）。"""
        try:
            preset = {
                'year': int(self.year_var.get()),
                'month': int(self.month_var.get()),
                'day': int(self.day_var.get()),
                'mountain': self._get_selected_mountain(),
                'jianxiang': self.jianxiang_var.get().strip(),
            }
        except Exception:
            preset = {}
        FeixingSearchDialog(self.root, preset=preset)

    def update_grids(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            if month < 1 or month > 12 or day < 1 or day > calendar.monthrange(year, month)[1]:
                messagebox.showerror("日期错误", "无效日期")
                return

            data = get_xuan_kong_data(year, month, day, hour, minute)
            sizhu = data['sizhu']
            self.info_label.config(text=f"{data['lunar_date']}  {sizhu['year']}年 {sizhu['month']}月 {sizhu['day']}日 {sizhu['hour']}时")

            titles = ['年飞星', '月飞星', '日飞星', '时飞星']
            keys = ['year','month','day','hour']
            sub_texts = [f"{sizhu['year']}年", f"{sizhu['month']}月", f"{sizhu['day']}日", f"{sizhu['hour']}时"]

            for idx, frame in enumerate(self.cells):
                for widget in frame.winfo_children():
                    widget.destroy()

                key = keys[idx]
                item = data[key]
                star = item['star']
                grid = item['grid']

                tk.Label(frame, text=f"{titles[idx]}  {sub_texts[idx]}", fg='#b0c0d8',
                         bg='#10161e', font=('微软雅黑', 12, 'bold')).pack(pady=(5,0))
                tk.Label(frame, text=f"入中：{STAR_NAMES[star-1]}", fg='#d4af70',
                         bg='#10161e', font=('微软雅黑', 9)).pack()

                inner = tk.Frame(frame, bg='#0b1018', pady=5)
                inner.pack(expand=True, fill='both', padx=10, pady=5)

                for i in range(9):
                    val = grid[i]
                    typ = STAR_TYPES[val]
                    bg_color = COLORS[typ]
                    txt_color = COLORS.get(typ+'_text', '#ffffff')
                    cell = tk.Frame(inner, bg=bg_color, relief='flat', bd=1)
                    cell.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='nsew')
                    if i == 4:
                        cell.config(bd=2, relief='solid', highlightbackground='#d4af70')

                    # 使用三列：列0-方位（左），列1-星名（中），列2-数字（右）
                    cell.grid_columnconfigure(0, weight=1)
                    cell.grid_columnconfigure(1, weight=1)
                    cell.grid_columnconfigure(2, weight=1)
                    cell.grid_rowconfigure(0, weight=1)

                    # 方位（左）—— 加入八卦卦名
                    _gua = GUA_NAMES[i]
                    _pos_text = f"{_gua}·{POS_NAMES[i]}" if _gua != '中' else f"{_gua}宫"
                    tk.Label(cell, text=_pos_text, fg='#6f7d98', bg=bg_color,
                             font=('微软雅黑', 14)).grid(row=0, column=0, sticky='w')
                    # 星名（中）
                    tk.Label(cell, text=STAR_NAMES[val-1], fg=txt_color, bg=bg_color,
                             font=('微软雅黑', 14)).grid(row=0, column=1)
                    # 数字（右）
                    tk.Label(cell, text=str(val), fg=COLORS['star_num'], bg=bg_color,
                             font=('微软雅黑', 14, 'bold')).grid(row=0, column=2, sticky='e')

                    inner.grid_rowconfigure(i//3, weight=1)
                    inner.grid_columnconfigure(i%3, weight=1)

            self.summary_label.config(text=f"星曜：{data['summary']}  |  节气：{data['jie_qi'] or '无'}")

            selected = self._get_selected_mountain()
            offset = self._get_jianxiang_offset()

            comment = generate_xuankong_comment(data, selected if selected else None, offset)

            lines = []
            lines.append(f"【综合】{comment['summary']}")
            if comment['good_points']:
                lines.append("【吉利】" + "；".join(comment['good_points']))
            if comment.get('mountain_warnings'):
                lines.append("【坐山警示】" + "；".join(comment['mountain_warnings']))
            if comment.get('other_warnings'):
                lines.append("【他宫提示】" + "；".join(comment['other_warnings']))
            if comment.get('mountain_combos'):
                lines.append("【坐山凶格】" + "；".join(comment['mountain_combos']))
            if comment.get('other_combos'):
                lines.append("【他宫凶格】" + "；".join(comment['other_combos']))
            if comment.get('fx_score') is not None:
                lines.append(f"【飞星评分】{comment['fx_score']:+d} 分（坐山口径，-20~+20）｜等级：{comment['fx_level']}")
                # 2026-09-13 追加分项明细（吉星汇聚/凶格/兼向替卦各值），使总分可逐项核对
                _fx_det = (comment.get('mountain_analysis') or {}).get('fx_details') or []
                if _fx_det:
                    lines.append("【得分明细】" + "；".join(_fx_det))
            else:
                lines.append("【飞星评分】未选坐山，暂无坐山评分")

            if comment['mountain_analysis']:
                ma = comment['mountain_analysis']
                lines.append(f"\n【山向分析】{ma['mountain_label']}（{ma['position']}方） 偏移：{ma['offset']:.1f}°")
                lines.append(f"  年星：{STAR_NAMES[ma['stars']['年']-1]}，月星：{STAR_NAMES[ma['stars']['月']-1]}，"
                             f"日星：{STAR_NAMES[ma['stars']['日']-1]}，时星：{STAR_NAMES[ma['stars']['时']-1]}")
                lines.append(f"  吉星数：{ma['good_count']}，凶星数：{ma['bad_count']}")
                lines.append(f"  断语：{ma['level']} —— {ma['suggestion']}")
                if ma['is_partial']:
                    lines.append("  ⚠️ 注意：此日课若用于此兼向，需用替卦飞星重新复核。")
            else:
                lines.append("\n【山向】未选择或无效。")

            self.comment_text.config(state='normal')
            self.comment_text.delete(1.0, tk.END)
            self.comment_text.insert(tk.END, "\n".join(lines))
            self.comment_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")

# ============================================================
#  飞星吉日搜索（纯飞星批量条件搜索，2026-09-12）
#  遍历时间范围每日12时辰，按坐山方年/月/日/时四盘飞星过滤排序；
#  排盘/评分只调用玄空飞星引擎 score_feixing，与单点窗口、评分器同源。
# ============================================================
# (子时初, 时支, 时辰时段显示)
_FX_SEARCH_HOURS = [
    (0, '子', '23-1'), (2, '丑', '1-3'), (4, '寅', '3-5'), (6, '卯', '5-7'),
    (8, '辰', '7-9'), (10, '巳', '9-11'), (12, '午', '11-13'), (14, '未', '13-15'),
    (16, '申', '15-17'), (18, '酉', '17-19'), (20, '戌', '19-21'), (22, '亥', '21-23'),
]
_WEEK = '一二三四五六日'


class FeixingSearchDialog:
    """玄空飞星·吉日搜索对话框（纯飞星口径，不含正五行）。

    过滤项：排除五黄/二黑到坐山、排除凶格（二五/三七/六七）、到山吉星≥N、
    最低飞星分；可选"仅保留每日最佳时辰"。结果按飞星分降序，双击行打开
    该日该时的单点飞星排盘，支持导出 CSV。
    """

    def __init__(self, parent, preset=None):
        self.parent = parent
        self._rows = []          # 当前结果（dict 列表，导出/联动用）
        self._row_iid = {}       # tree iid -> row
        preset = preset or {}

        self.win = tk.Toplevel(parent)
        self.win.title("玄空飞星 · 吉日搜索（纯飞星，不涉正五行）")
        self.win.geometry("1080x680")
        self.win.configure(bg='#0b0e14')
        self.win.transient(parent)

        frm = tk.Frame(self.win, bg='#141a24', padx=12, pady=10)
        frm.pack(fill='x', padx=14, pady=(14, 8))

        # —— 第1行：日期范围 + 坐山兼向 ——
        r1 = tk.Frame(frm, bg='#141a24'); r1.pack(fill='x', pady=3)
        tk.Label(r1, text="起：", fg='#e8edf5', bg='#141a24', font=('微软雅黑', 10)).pack(side='left')
        self.start_var = tk.StringVar()
        tk.Entry(r1, textvariable=self.start_var, width=11, bg='#1f2838',
                 fg='#e8edf5', insertbackground='#e8edf5', font=('微软雅黑', 10)).pack(side='left')
        tk.Label(r1, text=" 止：", fg='#e8edf5', bg='#141a24', font=('微软雅黑', 10)).pack(side='left')
        self.end_var = tk.StringVar()
        tk.Entry(r1, textvariable=self.end_var, width=11, bg='#1f2838',
                 fg='#e8edf5', insertbackground='#e8edf5', font=('微软雅黑', 10)).pack(side='left')
        tk.Label(r1, text="（YYYY-MM-DD）   坐山：", fg='#8fa0b8', bg='#141a24',
                 font=('微软雅黑', 10)).pack(side='left')
        self.mountain_var = tk.StringVar()
        self.mountain_combo = ttk.Combobox(r1, textvariable=self.mountain_var,
                                           values=MOUNTAIN_LABELS, width=13, state='readonly',
                                           font=('微软雅黑', 10))
        self.mountain_combo.pack(side='left', padx=2)
        tk.Label(r1, text=" 兼向：", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', 10)).pack(side='left')
        self.jx_var = tk.StringVar(value='正向')
        self.jx_combo = ttk.Combobox(r1, textvariable=self.jx_var, values=['正向'],
                                     width=7, state='readonly', font=('微软雅黑', 10))
        self.jx_combo.pack(side='left', padx=2)

        # —— 第2行：过滤条件 ——
        r2 = tk.Frame(frm, bg='#141a24'); r2.pack(fill='x', pady=3)
        self.var_no5 = tk.IntVar(value=1)
        self.var_no2 = tk.IntVar(value=1)
        self.var_nocombo = tk.IntVar(value=1)
        self.var_best_only = tk.IntVar(value=1)
        for txt, var in [("排除五黄到山", self.var_no5), ("排除二黑到山", self.var_no2),
                         ("排除凶格(二五/三七/六七)", self.var_nocombo),
                         ("仅保留每日最佳时辰", self.var_best_only)]:
            tk.Checkbutton(r2, text=txt, variable=var, bg='#141a24', fg='#e8edf5',
                           selectcolor='#1f2838', activebackground='#141a24',
                           activeforeground='#e8edf5', font=('微软雅黑', 10)).pack(side='left', padx=6)
        tk.Label(r2, text="  到山吉星≥", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', 10)).pack(side='left')
        self.good_min_var = tk.IntVar(value=0)
        tk.Spinbox(r2, from_=0, to=4, width=3, textvariable=self.good_min_var,
                   bg='#1f2838', fg='#e8edf5', font=('微软雅黑', 10)).pack(side='left', padx=2)
        tk.Label(r2, text="颗  最低飞星分", fg='#e8edf5', bg='#141a24',
                 font=('微软雅黑', 10)).pack(side='left')
        self.min_score_var = tk.IntVar(value=-20)
        tk.Spinbox(r2, from_=-20, to=20, increment=1, width=4,
                   textvariable=self.min_score_var, bg='#1f2838', fg='#e8edf5',
                   font=('微软雅黑', 10)).pack(side='left', padx=2)
        tk.Label(r2, text="(-20=不限)", fg='#8fa0b8', bg='#141a24',
                 font=('微软雅黑', 9)).pack(side='left')

        # —— 第3行：按钮 + 进度 ——
        r3 = tk.Frame(frm, bg='#141a24'); r3.pack(fill='x', pady=(6, 0))
        self.btn_search = tk.Button(r3, text="🔍 开始搜索", command=self.do_search,
                                    bg='#d4af70', fg='#0b0e14', font=('微软雅黑', 10, 'bold'),
                                    padx=14)
        self.btn_search.pack(side='left')
        tk.Button(r3, text="导出CSV", command=self.export_csv, bg='#3a6ea5', fg='#ffffff',
                  font=('微软雅黑', 10), padx=12).pack(side='left', padx=8)
        self.status_var = tk.StringVar(value="请设置条件后开始搜索")
        tk.Label(r3, textvariable=self.status_var, fg='#d4af70', bg='#141a24',
                 font=('微软雅黑', 10)).pack(side='left', padx=12)
        self.pbar = ttk.Progressbar(frm, mode='determinate')
        self.pbar.pack(fill='x', pady=(6, 0))

        # —— 结果表 ——
        cols = ('date', 'week', 'hour', 'shizhu', 'stars', 'good', 'score', 'level', 'warn')
        headers = {'date': '公历', 'week': '星期', 'hour': '时辰', 'shizhu': '时柱',
                   'stars': '到山星(年月日时)', 'good': '吉星', 'score': '飞星分',
                   'level': '等级', 'warn': '凶格/断语'}
        widths = {'date': 92, 'week': 48, 'hour': 92, 'shizhu': 58, 'stars': 150,
                  'good': 46, 'score': 58, 'level': 58, 'warn': 420}
        tree_frame = tk.Frame(self.win, bg='#0b0e14')
        tree_frame.pack(fill='both', expand=True, padx=14, pady=10)
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=16)
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], anchor='center',
                             stretch=(c == 'warn'))
        self.tree.tag_configure('大吉', foreground='#8bc34a')
        self.tree.tag_configure('吉', foreground='#b8d98a')
        self.tree.tag_configure('平', foreground='#9fb0c8')
        self.tree.tag_configure('凶', foreground='#e5a073')
        self.tree.tag_configure('大凶', foreground='#e57373')
        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', self.open_detail)

        # —— 带入 preset ——
        m0 = preset.get('mountain')
        if m0 and m0 in MOUNTAINS_CW:
            self.mountain_var.set(f"{m0}山 · {MOUNTAIN_DIRECTION.get(m0, '')}")
        else:
            self.mountain_var.set('乾山 · 西北')
        self._refresh_jx_options()
        jx0 = preset.get('jianxiang')
        if jx0 and jx0 in self.jx_combo['values']:
            self.jx_var.set(jx0)
        try:
            d0 = date(int(preset.get('year') or datetime.now().year),
                      int(preset.get('month') or datetime.now().month),
                      int(preset.get('day') or datetime.now().day))
        except Exception:
            d0 = date.today()
        self.start_var.set(str(d0))
        self.end_var.set(str(d0 + timedelta(days=30)))
        self.mountain_combo.bind('<<ComboboxSelected>>', self._on_mountain_change)

    # ---------- 山向辅助 ----------
    def _selected_mountain(self):
        text = self.mountain_var.get().strip()
        for m in MOUNTAINS_CW:
            if text.startswith(m + '山'):
                return m
        return text if text in MOUNTAINS_CW else None

    def _refresh_jx_options(self):
        m = self._selected_mountain()
        if m in MOUNTAINS_CW:
            idx = MOUNTAINS_CW.index(m)
            prev_m = MOUNTAINS_CW[(idx - 1) % 24]
            next_m = MOUNTAINS_CW[(idx + 1) % 24]
            self.jx_combo['values'] = ['正向', f'兼{prev_m}', f'兼{next_m}']
        else:
            self.jx_combo['values'] = ['正向']

    def _on_mountain_change(self, event=None):
        self.jx_var.set('正向')
        self._refresh_jx_options()

    # ---------- 搜索主流程 ----------
    def do_search(self):
        try:
            d0 = datetime.strptime(self.start_var.get().strip(), '%Y-%m-%d').date()
            d1 = datetime.strptime(self.end_var.get().strip(), '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("日期错误", "请输入正确的日期格式：YYYY-MM-DD", parent=self.win)
            return
        if d0 > d1:
            messagebox.showerror("日期错误", "开始日期不能晚于结束日期", parent=self.win)
            return
        m = self._selected_mountain()
        if not m:
            messagebox.showerror("山向错误", "请选择坐山", parent=self.win)
            return
        jx = self.jx_var.get().strip()
        sx_full = m + '山' + ('' if jx == '正向' else jx)

        no5, no2 = bool(self.var_no5.get()), bool(self.var_no2.get())
        no_combo = bool(self.var_nocombo.get())
        best_only = bool(self.var_best_only.get())
        good_min = int(self.good_min_var.get())
        min_score = int(self.min_score_var.get())

        days_total = (d1 - d0).days + 1
        self.pbar.configure(maximum=days_total, value=0)
        self.btn_search.configure(state='disabled')
        rows = []
        try:
            cur, di = d0, 0
            while cur <= d1:
                day_hits = []
                for h, hz, hr_txt in _FX_SEARCH_HOURS:
                    try:
                        sz = calculate_sizhu(cur, h, 0)
                        sz['year'] = cur.year
                        sz['month'] = cur.month
                        sz['day'] = cur.day
                        sz['date'] = cur
                        r = score_feixing(sz, sx_full)
                        if not r:
                            continue
                        if no5 and r['has_5']:
                            continue
                        if no2 and r['has_2']:
                            continue
                        if no_combo and r['combos']:
                            continue
                        if r['good_count'] < good_min:
                            continue
                        if r['feixing_score'] < min_score:
                            continue
                        warns = '、'.join(r['combos'])
                        if warns:
                            warns += '；'
                        if r['combos'] or r['feixing_level'] in ('凶', '大凶', '平'):
                            warns += r['feixing_comment']
                        day_hits.append({
                            'date': cur, 'hour': h, 'hour_zhi': hz, 'hour_range': hr_txt,
                            'shizhu': sz.get('时柱', ''),
                            'stars': r['stars_list'], 'good': r['good_count'],
                            'bad': r['bad_count'], 'score': r['feixing_score'],
                            'level': r['feixing_level'], 'warns': warns,
                            'details': '；'.join(r['feixing_details']),
                            'mountain': m, 'jianxiang': jx, 'sx_full': sx_full,
                        })
                    except Exception as e:
                        print(f"[飞星搜索] {cur} {hz}时 计算失败: {e}")
                # 每日仅取综合最优（飞星分→吉星数→早时优先），避免一日占满列表
                if day_hits:
                    if best_only:
                        best = max(day_hits, key=lambda x: (x['score'], x['good'], -x['hour']))
                        rows.append(best)
                    else:
                        rows.extend(day_hits)
                cur += timedelta(days=1)
                di += 1
                self.pbar.configure(value=di)
                self.status_var.set(f"搜索中… {di}/{days_total} 天，已命中 {len(rows)} 条")
                if di % 5 == 0:
                    self.win.update_idletasks()
        finally:
            self.btn_search.configure(state='normal')

        rows.sort(key=lambda x: (-x['score'], -x['good'], x['date'].toordinal(), x['hour']))
        self._rows = rows
        self._populate(rows)
        self.status_var.set(f"完成：{days_total} 天，命中 {len(rows)} 条（{sx_full}），按飞星分降序")

    def _populate(self, rows):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._row_iid = {}
        for row in rows:
            stars_txt = ' · '.join(str(s) for s in row['stars'])
            iid = self.tree.insert(
                '', 'end',
                values=(str(row['date']), '周' + _WEEK[row['date'].weekday()],
                        f"{row['hour_zhi']}时({row['hour_range']})", row['shizhu'],
                        stars_txt, row['good'], row['score'], row['level'], row['warns']),
                tags=(row['level'],))
            self._row_iid[iid] = row

    # ---------- 双击：打开该时辰单点排盘 ----------
    def open_detail(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        row = self._row_iid.get(sel[0])
        if not row:
            return
        win2 = tk.Toplevel(self.win)
        XuanKongApp(win2, preset={
            'year': row['date'].year, 'month': row['date'].month, 'day': row['date'].day,
            'hour': row['hour'], 'minute': 0,
            'mountain': row['mountain'], 'jianxiang': row['jianxiang'],
        })

    # ---------- 导出 ----------
    def export_csv(self):
        if not self._rows:
            messagebox.showinfo("提示", "没有可导出的搜索结果", parent=self.win)
            return
        path = filedialog.asksaveasfilename(
            title="导出飞星吉日搜索结果",
            defaultextension='.csv', filetypes=[('CSV 文件', '*.csv')],
            initialfile=f"飞星吉日_{self.start_var.get()}_{self.end_var.get()}.csv",
            parent=self.win)
        if not path:
            return
        import csv
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['公历', '星期', '时辰', '时柱', '坐山', '兼向',
                        '年到山星', '月到山星', '日到山星', '时到山星',
                        '吉星数', '凶星数', '飞星分', '等级', '凶格/断语', '评分明细'])
            for r in self._rows:
                w.writerow([str(r['date']), '周' + _WEEK[r['date'].weekday()],
                            f"{r['hour_zhi']}时({r['hour_range']})", r['shizhu'],
                            r['mountain'], r['jianxiang'],
                            r['stars'][0], r['stars'][1], r['stars'][2], r['stars'][3],
                            r['good'], r['bad'], r['score'], r['level'],
                            r['warns'], r['details']])
        messagebox.showinfo("导出成功", f"已导出 {len(self._rows)} 条：\n{path}", parent=self.win)


if __name__ == '__main__':
    try:
        import sxtwl
        import lunar_python
    except ImportError:
        print("请先安装依赖：pip install sxtwl lunar-python loguru")
        sys.exit(1)

    root = tk.Tk()
    app = XuanKongApp(root)
    root.mainloop()