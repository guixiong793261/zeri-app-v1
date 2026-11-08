# -*- coding: utf-8 -*-
"""
================================================================================
精准择时 · 反推面板（001 §210 Commit 2）
================================================================================
三层视图（用户 2026-10-31 拍板）：
    1. 热力日历：吉日标红、慎用标黄、否决深灰（格内显示 ×，不显示 0 分），
       Top-N 日加蓝框，右上角 ★ 为吉神星级（契合度分档），悬停看归类/分值；
    2. Top-N 吉日列表：排名/日期/农历/评分/吉神契合(★)/扣分主因/最优时辰，
       慎用行黄底，原因列写明负分项与忌项（不解释清楚会被误读成软件发疯）；
    3. 最优时间轴：12 时辰逐条给"时辰级"建议（最优/吉神/犯煞/平/忌用），
       禁止复用日级 yi_list 充数。

约束：
    - 本模块只做展示与调度，不计算任何分值（一律来自 modules.反推引擎.search_top_n）；
    - 后台线程只往 queue 塞消息，所有 Tk 操作都在主线程的 _poll 中完成
      （禁止在子线程直接触碰控件）；
    - 面板不进入主窗口评分链路，关窗即停（置 cancel 标志）。
================================================================================
"""

import calendar
import os
import queue
import tempfile
import threading
import tkinter as tk
from datetime import date, datetime
from tkinter import filedialog, messagebox, ttk

from modules.反推引擎 import search_top_n, MAX_DAYS, DEFAULT_DAYS, DEFAULT_TOP_N
from modules.排序键 import jishen_stars
from modules.事项标准 import UI_EVENTS, MOUNTAIN_CENTERED_EVENTS

COLOR_JI = '#C62828'        # 吉日：红
COLOR_CAUTION = '#F9A825'   # 慎用：黄
COLOR_VETO = '#263238'      # 否决：黑
COLOR_NA = '#F5F5F5'        # 范围外
TXT_ON_DARK = '#FFFFFF'
TXT_ON_YELLOW = '#212121'
STAR_ON_JI = '#FFD54F'      # 红格上的金色星
STAR_ON_CAUTION = '#6D4C00' # 黄格上的深棕星（保证对比度）

CELL_W, CELL_H = 66, 50
PAD = 10


class _GreenProgressbar:
    """Canvas 自绘绿色进度条（Windows ttk 默认主题不支持改 Progressbar 颜色）。

    兼容 ttk.Progressbar 的 config(maximum=, value=) 调用接口。
    """

    def __init__(self, master, length=180, height=18):
        self._cv = tk.Canvas(master, width=length, height=height,
                             bg='#E8E8E8', highlightthickness=1,
                             highlightbackground='#BDBDBD')
        self._len = length
        self._h = height
        self._max = 100.0
        self._val = 0.0
        self._fill = self._cv.create_rectangle(
            0, 0, 0, height, fill='#2E7D32', outline='')

    def config(self, **kw):
        if 'maximum' in kw:
            self._max = float(kw['maximum'])
        if 'value' in kw:
            self._val = float(kw['value'])
        ratio = min(1.0, self._val / self._max) if self._max > 0 else 0.0
        self._cv.coords(self._fill, 0, 0, int(self._len * ratio), self._h)

    def pack(self, **kw):
        self._cv.pack(**kw)


def _reason_text(day, compact=True):
    """扣分主因/类型说明（Top-N 原因列 + 热力格状态栏共用）。

    慎用：神煞负分总和 <= -20 的负分项（如杨公忌日 -20、羊刃 -15）；
    吉日但仍有轻扣/忌项：写"轻扣/忌项"，解释为何"分数高却不是唯一指标"；
    否决：写 veto_reasons（无则写总分）。

    compact=True 时只显示前 2 条负分 + 前 1 条忌项并加省略号，
    避免 Treeview 单元格横向截断（完整文本见点击/悬停状态栏）。
    """
    _kind = day.get('kind') or ''
    if _kind == '否决':
        _rs = day.get('veto_reasons') or []
        if not _rs:
            return '否决：%s 分' % day.get('score')
        _shown = _rs[:(2 if compact else 9)]
        return '否决：' + '、'.join(_shown) + (
            '…' if len(_rs) > len(_shown) else '')
    _parts = []
    _di = (day.get('deduct_items') or [])
    if _di:
        _shown = _di[:(2 if compact else 9)]
        _txt = '、'.join('%s %d' % (_s.get('name', ''), int(_s.get('score') or 0))
                        for _s in _shown)
        _parts.append('%s：%s%s' % ('慎用' if _kind == '慎用' else '轻扣',
                                   _txt, '…' if len(_di) > len(_shown) else ''))
    _ji = (day.get('ji_items') or [])
    if _ji:
        _shown_ji = _ji[:(1 if compact else 9)]
        _parts.append('忌项：' + '、'.join(_shown_ji)
                      + ('…' if len(_ji) > len(_shown_ji) else ''))
    return '；'.join(_parts) or '—'


class ReverseWindow:
    """精准择时反推面板（Toplevel，三层视图）。"""

    def __init__(self, master, event_type, owners=None, context=None,
                 modify_callback=None, add_tie_callback=None):
        self.master = master
        self.owners = owners if isinstance(owners, list) else []
        self.context = context if isinstance(context, dict) else {}
        self.modify_callback = modify_callback
        self.add_tie_callback = add_tie_callback
        self._alive = True
        self._cancel = False
        self._thread = None
        self._q = queue.Queue()
        self._res = None
        self._day_map = {}
        self._top_dates = set()

        self.win = tk.Toplevel(master)
        self.win.title('精准择时 · 反推 Top-N（001 §210）')
        self.win.geometry('1240x820')
        self.win.minsize(1000, 640)
        self.win.protocol('WM_DELETE_WINDOW', self._on_close)
        self.win.bind('<Escape>', lambda _e: self._on_close())

        self._build_top_bar(event_type)
        self._build_context_bar()
        self._build_tabs()
        self._poll()

    # ---------------------------------------------------------------- UI 构建
    def _build_top_bar(self, event_type):
        bar = ttk.Frame(self.win, padding=(10, 8, 10, 4))
        bar.pack(fill=tk.X)

        ttk.Label(bar, text='事项:').pack(side=tk.LEFT)
        self.event_var = tk.StringVar(
            value=event_type if event_type in UI_EVENTS else UI_EVENTS[0])
        ttk.Combobox(bar, textvariable=self.event_var, values=list(UI_EVENTS),
                     state='readonly', width=8).pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(bar, text='起始日:').pack(side=tk.LEFT)
        self.start_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        ttk.Entry(bar, textvariable=self.start_var, width=12).pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(bar, text='范围:').pack(side=tk.LEFT)
        self.days_var = tk.StringVar(value=str(DEFAULT_DAYS))
        ttk.Spinbox(bar, from_=1, to=MAX_DAYS, textvariable=self.days_var,
                    width=5).pack(side=tk.LEFT, padx=(2, 2))
        ttk.Label(bar, text='天').pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(bar, text='Top N:').pack(side=tk.LEFT)
        self.topn_var = tk.StringVar(value=str(DEFAULT_TOP_N))
        ttk.Spinbox(bar, from_=1, to=30, textvariable=self.topn_var,
                    width=5).pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(bar, text='状态:').pack(side=tk.LEFT)
        self.kind_var = tk.StringVar(value='全部')
        ttk.Combobox(bar, textvariable=self.kind_var,
                     values=['全部', '吉日', '慎用'],
                     state='readonly', width=5).pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(bar, text='吉神:').pack(side=tk.LEFT)
        self.fit_var = tk.StringVar(value='不限')
        ttk.Combobox(bar, textvariable=self.fit_var,
                     values=['不限', '1星+', '2星+', '3星+', '4星+', '5星'],
                     state='readonly', width=6).pack(side=tk.LEFT, padx=(2, 10))

        self.run_btn = ttk.Button(bar, text='开始反推', command=self._start)
        self.run_btn.pack(side=tk.LEFT, padx=(6, 4))
        self.stop_btn = ttk.Button(bar, text='停止', command=self._stop,
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        self.progress = _GreenProgressbar(bar, length=180)
        self.progress.pack(side=tk.LEFT, padx=(12, 6))
        self.status_var = tk.StringVar(value='就绪：选范围后点"开始反推"（最大 365 天）')
        ttk.Label(bar, textvariable=self.status_var).pack(side=tk.LEFT, padx=4)

    def _build_context_bar(self):
        """当前排盘上下文回显栏（001 §210 Commit 3）。

        显示事主姓名、坐山朝向、当前年份；事主为空时红色警示。
        右侧提供"修改事主与山向"按钮，关闭本窗口并把焦点交回主程序对应输入框。
        """
        bar = ttk.Frame(self.win, padding=(10, 2, 10, 6))
        bar.pack(fill=tk.X)

        # 分隔线
        ttk.Separator(bar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 4))

        inner = ttk.Frame(bar)
        inner.pack(fill=tk.X)

        ttk.Label(inner, text='当前排盘上下文：',
                  font=('Microsoft YaHei UI', 9, 'bold')).pack(side=tk.LEFT)

        # 事主回显
        _names = [str(_o.get('name') or '').strip() for _o in self.owners]
        _names = [_n for _n in _names if _n]
        if _names:
            ttk.Label(inner, text='事主：', foreground='#1565C0').pack(side=tk.LEFT, padx=(8, 0))
            ttk.Label(inner, text='[%s]' % '、'.join(_names),
                      foreground='#1565C0',
                      font=('Microsoft YaHei UI', 9, 'bold')).pack(side=tk.LEFT)
        else:
            ttk.Label(inner, text='⚠ 当前未输入事主（仅按空事主计算）',
                      foreground='#C62828',
                      font=('Microsoft YaHei UI', 9, 'bold')).pack(side=tk.LEFT, padx=(8, 0))

        # 坐向回显
        _shan = str(self.context.get('shan_xiang') or '').strip()
        ttk.Label(inner, text='  ｜  坐向：', foreground='#1565C0').pack(side=tk.LEFT)
        if _shan:
            ttk.Label(inner, text='[%s]' % _shan,
                      foreground='#1565C0',
                      font=('Microsoft YaHei UI', 9, 'bold')).pack(side=tk.LEFT)
        else:
            ttk.Label(inner, text='[未填]',
                      foreground='#E65100',
                      font=('Microsoft YaHei UI', 9, 'bold')).pack(side=tk.LEFT)

        # 当前年份
        ttk.Label(inner, text='  ｜  当前年份：', foreground='#1565C0').pack(side=tk.LEFT)
        ttk.Label(inner, text=str(date.today().year),
                  foreground='#1565C0',
                  font=('Microsoft YaHei UI', 9, 'bold')).pack(side=tk.LEFT)

        # 修改按钮（方案 A：轻量，回主程序改）
        ttk.Button(inner, text='修改事主与山向',
                   command=self._on_modify_context).pack(side=tk.RIGHT, padx=(8, 0))

    def _on_modify_context(self):
        """点击"修改事主与山向"：关闭反推窗口，把焦点交回主程序输入框。"""
        self._cancel = True
        self._alive = False
        try:
            self.win.destroy()
        except tk.TclError:
            pass
        if callable(self.modify_callback):
            try:
                self.modify_callback()
            except Exception:
                pass

    def _build_tabs(self):
        self.nb = ttk.Notebook(self.win)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # ---- 层1：热力日历
        tab1 = ttk.Frame(self.nb)
        self.nb.add(tab1, text='① 热力日历')
        legend = ttk.Frame(tab1)
        legend.pack(fill=tk.X, pady=4)
        for _txt, _color in (('吉日', COLOR_JI), ('慎用', COLOR_CAUTION),
                             ('否决', COLOR_VETO), ('范围外', COLOR_NA)):
            _sw = tk.Label(legend, text='  ', bg=_color, relief='solid', bd=1,
                           width=2)
            _sw.pack(side=tk.LEFT, padx=(6, 2))
            ttk.Label(legend, text=_txt).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(legend, text='（蓝框=入榜 Top-N，★=吉神星级，悬停看归类与分值，点击可跳时间轴）'
                  ).pack(side=tk.LEFT, padx=8)

        body = ttk.Frame(tab1)
        body.pack(fill=tk.BOTH, expand=True)
        self.heat_canvas = tk.Canvas(body, background='#FFFFFF',
                                     highlightthickness=0)
        _vsb = ttk.Scrollbar(body, orient=tk.VERTICAL,
                             command=self.heat_canvas.yview)
        self.heat_canvas.configure(yscrollcommand=_vsb.set)
        _vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.heat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ---- 层2：Top-N 列表
        tab2 = ttk.Frame(self.nb)
        self.nb.add(tab2, text='② Top-N 吉日')
        self.summary_var = tk.StringVar(value='尚未反推')
        ttk.Label(tab2, textvariable=self.summary_var).pack(fill=tk.X, padx=4, pady=4)
        _cols = ('排名', '日期', '星期', '农历', '评分', '等级',
                 '吉神契合', '满分核验', '扣分主因', '最优时辰', '状态')
        self.top_tree = ttk.Treeview(tab2, columns=_cols, show='headings',
                                     selectmode='browse', height=12)
        for _c, _w in (('排名', 48), ('日期', 100), ('星期', 56), ('农历', 96),
                       ('评分', 64), ('等级', 96), ('吉神契合', 90),
                       ('满分核验', 92), ('扣分主因', 400),
                       ('最优时辰', 122), ('状态', 56)):
            self.top_tree.heading(_c, text=_c)
            self.top_tree.column(_c, width=_w, anchor=tk.CENTER)
        self.top_tree.column('扣分主因', anchor=tk.W)
        # 001 §231：满分核验列顺序图例（悬停该列看逐项说明）
        ttk.Label(tab2,
                  text='满分核验：得令 · 合局 · 相主 · 德神 · 硬忌'
                       '（✓/✗ 依次对应，悬停看缺失项）',
                  foreground='#616161').pack(fill=tk.X, padx=6)
        # 榜单保存/打印（与单日详情同一套「保存 + 打印」能力）
        # 001 §220（2026-11-06）：必须在树之前先 pack(BOTTOM)，
        # 否则窗口偏矮时按钮条被树挤到可视区外，用户看不到（原症状）。
        _top_btn_bar = ttk.Frame(tab2)
        _top_btn_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=(4, 4))
        self.save_btn = ttk.Button(_top_btn_bar, text='💾 保存择日结果',
                                   command=self._save_top_list, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT)
        self.print_btn = ttk.Button(_top_btn_bar, text='🖨 打印榜单',
                                    command=self._print_top_list, state=tk.DISABLED)
        self.print_btn.pack(side=tk.LEFT, padx=(6, 0))

        _tsb = ttk.Scrollbar(tab2, orient=tk.VERTICAL,
                             command=self.top_tree.yview)
        self.top_tree.configure(yscrollcommand=_tsb.set)
        _tsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.top_tree.pack(fill=tk.BOTH, expand=True, padx=4)
        self.top_tree.tag_configure('cautious', background='#FFF8E1',
                                    foreground='#6D4C00')
        self.top_tree.tag_configure('auspicious', foreground='#8E0000')
        # 001 §231：五项全✓的极品日课整行金底高亮
        self.top_tree.tag_configure('perfect', background='#FFF3CD',
                                    foreground='#7A4F00')
        self.top_tree.bind('<<TreeviewSelect>>', lambda _e: self._on_tree_select())
        self.top_tree.bind('<Double-Button-1>', self._on_top_double_click)
        self.top_tree.bind('<Button-3>', self._on_top_right_click)
        # 001 §231：满分核验列悬停 Tooltip
        self._perfect_col = '#%d' % (list(_cols).index('满分核验') + 1)
        self._tip_win = None
        self.top_tree.bind('<Motion>', self._on_top_motion)
        self.top_tree.bind('<Leave>', lambda _e: self._hide_tip())
        self.top_tree.bind('<Button-1>', lambda _e: self._hide_tip(), add='+')

        # ---- 层3：时间轴
        tab3 = ttk.Frame(self.nb)
        self.nb.add(tab3, text='③ 最优时间轴')
        self.tl_head = tk.StringVar(value='在“② Top-N 吉日”或热力日历中选择一天')
        ttk.Label(tab3, textvariable=self.tl_head,
                  font=('Microsoft YaHei UI', 10, 'bold')).pack(fill=tk.X, padx=6, pady=6)

        # 001 §214 P2-B：动作轴三行（嫁娶等配置了 ACTION_SEQUENCES 的事项）
        self.act_frame = ttk.LabelFrame(tab3, text='动作时序（一键写入红帖）', padding=6)
        self.act_frame.pack(fill=tk.X, padx=6, pady=(0, 4))
        self.act_status_var = tk.StringVar(value='（选择一天后显示动作时序方案）')
        ttk.Label(self.act_frame, textvariable=self.act_status_var,
                  foreground='#616161').pack(anchor=tk.W)
        self.act_rows = []   # [(label, info_label), ...] 三段展示控件
        for _i in range(3):
            _row = ttk.Frame(self.act_frame)
            _row.pack(fill=tk.X, pady=1)
            _seq = ttk.Label(_row, text='①②③'[_i], width=3,
                             font=('Microsoft YaHei UI', 11, 'bold'), foreground='#8E0000')
            _seq.pack(side=tk.LEFT)
            _info = ttk.Label(_row, text='—', anchor=tk.W,
                              font=('Microsoft YaHei UI', 10))
            _info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.act_rows.append((_seq, _info))
        self.act_alt_var = tk.StringVar(value='')
        ttk.Label(self.act_frame, textvariable=self.act_alt_var,
                  foreground='#E65100', wraplength=1100, justify=tk.LEFT
                  ).pack(anchor=tk.W, pady=(2, 0))
        _act_btn_bar = ttk.Frame(self.act_frame)
        _act_btn_bar.pack(fill=tk.X, pady=(4, 0))
        self.send_tie_btn = ttk.Button(
            _act_btn_bar, text='生成红纸帖（写入动作时序）',
            command=self._send_action_plan_to_tie, state=tk.DISABLED)
        self.send_tie_btn.pack(side=tk.LEFT)

        _tcols = ('时辰', '时段', '时柱', '评分', '等级', '吉时行动建议', '备注')
        self.tl_tree = ttk.Treeview(tab3, columns=_tcols, show='headings',
                                    selectmode='browse', height=13)
        for _c, _w in (('时辰', 70), ('时段', 78), ('时柱', 60), ('评分', 64),
                       ('等级', 130), ('吉时行动建议', 420), ('备注', 220)):
            self.tl_tree.heading(_c, text=_c)
            self.tl_tree.column(_c, width=_w, anchor=tk.W if _c in
                                ('等级', '吉时行动建议', '备注') else tk.CENTER)
        _tl_sb = ttk.Scrollbar(tab3, orient=tk.VERTICAL,
                               command=self.tl_tree.yview)
        self.tl_tree.configure(yscrollcommand=_tl_sb.set)
        _tl_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tl_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 6))
        self.tl_tree.tag_configure('best', background='#FFE082')
        self.tl_tree.tag_configure('ok', foreground='#1B5E20')
        self.tl_tree.tag_configure('bad', foreground='#616161')
        self.tl_tree.tag_configure('disabled', foreground='#9E9E9E')

    # ---------------------------------------------------------------- 调度
    def _start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        try:
            _start = datetime.strptime(self.start_var.get().strip(),
                                       '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('日期格式错误', '起始日须为 YYYY-MM-DD',
                                 parent=self.win)
            return
        try:
            _days = int(str(self.days_var.get()).split('天')[0].strip())
            _topn = int(str(self.topn_var.get()).strip())
        except ValueError:
            messagebox.showerror('参数错误', '范围/Top N 须为整数', parent=self.win)
            return
        if not 1 <= _days <= MAX_DAYS:
            messagebox.showerror('范围超限', f'范围须在 1~{MAX_DAYS} 天之间',
                                 parent=self.win)
            return

        # 收录筛选：状态（全部/吉日/慎用）+ 吉神契合星级下限（0=不限）
        _kind_v = str(self.kind_var.get()).strip()
        _only_kind = None if _kind_v in ('', '全部') else _kind_v
        _fit_v = str(self.fit_var.get()).strip()
        try:
            _min_stars = 0 if _fit_v in ('', '不限') else int(_fit_v[0])
        except ValueError:
            _min_stars = 0

        # 山向中心事项（入宅/修造/安葬等）无坐山时提示确认（001 §210 Commit 3）
        _ev = self.event_var.get()
        _shan = str(self.context.get('shan_xiang') or '').strip()
        if _ev in MOUNTAIN_CENTERED_EVENTS and not _shan:
            if not messagebox.askyesno(
                    '坐山未填',
                    '⚠ 当前未提供坐山朝向，反推结果将缺乏方位吉凶判定\n'
                    '（三煞坐山、山家封禁、玄空飞星等均无法计算）。\n\n'
                    '是否仍要继续？',
                    parent=self.win):
                return

        self._cancel = False
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        self.print_btn.config(state=tk.DISABLED)
        self.progress.config(maximum=_days, value=0)
        self.status_var.set(f'正在反推：{self.event_var.get()} 共 {_days} 天 ...')
        self._thread = threading.Thread(
            target=self._work,
            args=(self.event_var.get(), _days, _topn, _start,
                  _only_kind, _min_stars),
            daemon=True)
        self._thread.start()

    def _work(self, event_type, days, top_n, start, only_kind, min_stars):
        """子线程：只算不碰 Tk，结果经 queue 回主线程。"""
        try:
            _res = search_top_n(
                days=days, event_type=event_type, owners=self.owners,
                start=start, top_n=top_n, context=self.context,
                only_kind=only_kind, min_jishen_stars=min_stars,
                progress=lambda done, tot, d: self._q.put(('progress', done, tot, d)),
                cancel=lambda: self._cancel)
            self._q.put(('done', _res))
        except Exception as _e:      # 参数/计算异常 → 主线程弹窗，不吞
            self._q.put(('error', '%s: %s' % (type(_e).__name__, _e)))

    def _stop(self):
        self._cancel = True
        self.status_var.set('正在停止 ...（当前日算完即返回）')

    def _on_close(self):
        self._cancel = True
        self._alive = False
        try:
            self.win.destroy()
        except tk.TclError:
            pass

    def _poll(self):
        """主线程轮询队列（唯一允许触碰控件的入口）。"""
        if not self._alive:
            return
        try:
            while True:
                _msg = self._q.get_nowait()
                _kind = _msg[0]
                if _kind == 'progress':
                    _, _done, _tot, _d = _msg
                    self.progress.config(maximum=_tot, value=_done)
                    self.status_var.set('反推中：%d/%d（%s）' % (
                        _done, _tot, _d.strftime('%Y-%m-%d')))
                elif _kind == 'done':
                    self._on_done(_msg[1])
                elif _kind == 'error':
                    self.run_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                    self.status_var.set('反推失败：' + _msg[1])
                    messagebox.showerror('反推失败', _msg[1], parent=self.win)
        except queue.Empty:
            pass
        if self._alive:
            self.win.after(80, self._poll)

    # ---------------------------------------------------------------- 渲染
    @staticmethod
    def _filter_text(_m):
        """把筛选条件拼成一句可读文本（无筛选返回空串）。"""
        _parts = []
        if _m.get('only_kind'):
            _parts.append('仅%s' % _m['only_kind'])
        if _m.get('min_jishen_stars'):
            _parts.append('吉神≥%d星' % _m['min_jishen_stars'])
        return '、'.join(_parts)

    def _on_done(self, res):
        self._res = res
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        _m = res['meta']
        _flt = self._filter_text(_m)
        # 001 §214 C2（2026-11-03 拍板）：零候选不得只在状态栏显示数字，
        # 必须显眼提示「本范围内无可用吉日」，杜绝用户对着空榜无从判断。
        if not res.get('days'):
            _zero_msg = ('⚠ 当前时间范围内，没有符合条件且能避开冲煞的可用吉日。'
                         + ('（当前筛选：%s）' % _flt if _flt else '')
                         + '请尝试扩大日期范围、放宽筛选，或调整山向/事主信息。')
            self.status_var.set(_zero_msg)
            self.summary_var.set(
                '事项 %s ｜ %s ~ %s ｜ 候选 0 条（否决 %d 天%s）｜ 建议扩大范围或放宽筛选'
                % (_m['event_type'], _m['start'], _m['end'], _m['vetoed'],
                   ('，筛除 %d 天' % _m.get('filtered_out', 0))
                   if _m.get('filtered_out') else ''))
            self._render_heatmap(res)
            self._render_top(res)
            messagebox.showwarning('无可用吉日', _zero_msg, parent=self.win)
            return
        self.status_var.set(
            '完成：%d/%d 天，候选 %d，筛除 %d，否决 %d，耗时 %.2fs%s' % (
                _m['scanned'], _m['days'], _m['candidates'],
                _m.get('filtered_out', 0), _m['vetoed'],
                _m['elapsed'], '（已停止，为部分结果）' if _m['cancelled'] else ''))
        self.summary_var.set(
            '事项 %s ｜ %s ~ %s ｜ 入榜 %d 条（吉日 %d / 慎用 %d）%s｜ '
            '排序=吉日优先→否决数→吉神契合→总分｜ 双击看详情，右键可加入择日贴' % (
                _m['event_type'], _m['start'], _m['end'], len(res['days']),
                sum(1 for _d in res['days'] if _d['kind'] == '吉日'),
                sum(1 for _d in res['days'] if _d['kind'] == '慎用'),
                ('｜ 筛选：' + _flt) if _flt else ''))
        self._render_heatmap(res)
        self._render_top(res)
        self.save_btn.config(state=tk.NORMAL)
        self.print_btn.config(state=tk.NORMAL)

    # ---------------------------------------------------------------- 榜单导出
    def _build_top_lines(self):
        """拼 Top-N 榜单文本（保存/打印共用，只读已算结果，不重算分值）。"""
        _res = self._res or {}
        _m = _res.get('meta') or {}
        _days = _res.get('days') or []
        _ev = _m.get('event_type', '')
        _flt = self._filter_text(_m) or '不限'
        _n_ji = sum(1 for _d in _days if _d['kind'] == '吉日')
        _n_shen = sum(1 for _d in _days if _d['kind'] == '慎用')
        _lines = [
            '精准择时 · %s' % _ev,
            '=' * 56,
            '扫描范围：%s ~ %s（共 %s 天，已扫 %s 天）' % (
                _m.get('start'), _m.get('end'), _m.get('days'), _m.get('scanned')),
            '收录筛选：%s' % _flt,
            '入榜：%d 条（吉日 %d / 慎用 %d）｜ 候选 %d ｜ 筛除 %s ｜ 否决 %d' % (
                len(_days), _n_ji, _n_shen, _m.get('candidates', 0),
                _m.get('filtered_out', 0), _m.get('vetoed', 0)),
            '排序口径：吉日优先 → 否决数 → 吉神契合 → 总分',
            '生成时间：%s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '',
        ]
        for _i, _d in enumerate(_days, 1):
            _fit = int(_d.get('jishen_fit') or 0)
            _stars = jishen_stars(_fit)
            _bh = _d.get('best_hour') or {}
            _lines.append('%2d. %s　%s　农历%s' % (
                _i, _d['date'], _d['weekday'], _d['lunar']))
            _lines.append('    评分 %s 分（%s）｜ 状态 %s ｜ 吉神契合 %s（%d 分）' % (
                _d['score'], _d['level'], _d['kind'],
                ('★' * _stars) if _stars else '—', _fit))
            _lines.append('    最优时辰 %s（%s）时柱 %s ｜ %s 分 %s' % (
                _bh.get('时辰', '—'), _bh.get('时段', '—'), _bh.get('时柱', '—'),
                _bh.get('score', '—'), _bh.get('level', '')))
            _lines.append('    吉　　神：%s' % (str(_d.get('jishen') or '') or '—'))
            # 001 §231：满分画像核验（五项全✓为极品日课）
            _chk = _d.get('check') or {}
            if _chk.get('items'):
                _lines.append('    满分核验：%s（%d/%d）%s' % (
                    _chk.get('marks', '—'), _chk.get('ok_count', 0),
                    len(_chk.get('items') or []),
                    '　★极品日课' if _chk.get('all_ok') else ''))
                for _tip in (_chk.get('tips') or []):
                    _lines.append('              ✗ %s' % _tip)
            _lines.append('    扣分主因：%s' % _reason_text(_d, compact=True))
            _lines.append('')
        if not _days:
            _lines.append('（本次没有符合筛选条件的可用吉日）')
        return _lines

    def _save_top_list(self):
        """保存 Top-N 榜单为 TXT。"""
        _res = self._res or {}
        if not _res.get('days'):
            return
        _ev = (_res.get('meta') or {}).get('event_type', '')
        _default = '精准择时榜单_%s_%s.txt' % (
            _ev, datetime.now().strftime('%Y%m%d'))
        self._save_text(self._build_top_lines(), _default, '保存精准择时榜单')

    def _print_top_list(self):
        """打印 Top-N 榜单。"""
        _res = self._res or {}
        if not _res.get('days'):
            return
        _ev = (_res.get('meta') or {}).get('event_type', '')
        self._print_text(self._build_top_lines(),
                         '精准择时榜单 · %s' % _ev)

    def _save_text(self, lines, default_name, dialog_title):
        """通用：把文本行写入用户选定路径，并确认落盘。"""
        _path = filedialog.asksaveasfilename(
            title=dialog_title,
            defaultextension='.txt',
            initialfile=default_name,
            filetypes=[('文本文件', '*.txt'), ('所有文件', '*.*')],
            parent=self.win)
        if not _path:
            return
        try:
            with open(_path, 'w', encoding='utf-8') as _f:
                _f.write('\n'.join(lines))
        except Exception as _e:
            messagebox.showerror('保存失败', str(_e), parent=self.win)
            return
        # 落盘确认（经验 813310：必须确认文件存在且大小>0 再提示成功）
        if os.path.exists(_path) and os.path.getsize(_path) > 0:
            messagebox.showinfo(
                '保存成功',
                '已保存至：\n%s\n\n共 %d 行' % (_path, len(lines)),
                parent=self.win)
        else:
            messagebox.showerror('保存失败', '文件未成功写入，请检查路径权限',
                                 parent=self.win)

    def _print_text(self, lines, title):
        """通用：生成临时 HTML（等宽对齐）并调用系统默认浏览器打印。"""
        _html = (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            '<title>%s</title>'
            '<style>body{font-family:"Microsoft YaHei UI",sans-serif;'
            'margin:24px;}h2{color:#8E0000;}pre{font-family:"Consolas",'
            '"Microsoft YaHei UI",monospace;font-size:12px;line-height:1.6;'
            'white-space:pre-wrap;}</style>'
            '<script>window.onload=function(){window.print();}'
            '</script></head><body>'
            '<h2>%s</h2><pre>%s</pre></body></html>'
        ) % (title, title, '\n'.join(lines).replace('&', '&amp;')
             .replace('<', '&lt;').replace('>', '&gt;'))
        try:
            _fd, _tmp = tempfile.mkstemp(suffix='.html', prefix='zeri_print_')
            with os.fdopen(_fd, 'w', encoding='utf-8') as _f:
                _f.write(_html)
        except Exception as _e:
            messagebox.showerror('打印失败', str(_e), parent=self.win)
            return
        try:
            os.startfile(_tmp)
        except Exception as _e:
            messagebox.showerror('打印失败',
                                 '无法调用打印：%s\n临时文件：%s' % (_e, _tmp),
                                 parent=self.win)

    def _render_top(self, res):
        for _i in self.top_tree.get_children():
            self.top_tree.delete(_i)
        self._top_dates = {_d['date'] for _d in res['days']}
        self._top_map = {_d['date']: _d for _d in res['days']}
        self._hide_tip()
        # 001 §210 Commit 4（用户 2026-11-01 拍板）：列表按"最优在前"排列——
        # 吉日层内总分降序（同分比吉神契合），慎用层整体排后。
        # 仅调整展示顺序，不改 rank_day / Top-N 选取口径（引擎与测试基线零漂移）。
        _rows = sorted(res['days'], key=lambda _d: (
            0 if _d['kind'] == '吉日' else 1,
            -int(_d.get('score') or 0),
            -int(_d.get('jishen_fit') or 0),
            _d['date']))
        for _idx, _d in enumerate(_rows, 1):
            _tag = 'cautious' if _d['kind'] == '慎用' else 'auspicious'
            _fit = int(_d.get('jishen_fit') or 0)
            _stars = jishen_stars(_fit)
            # 001 §231：满分核验（得令/合局/相主/德神/硬忌），五项全✓整行金底。
            _chk = _d.get('check') or {}
            _marks = str(_chk.get('marks') or '—')
            if _chk.get('all_ok'):
                _tag = 'perfect'
            self.top_tree.insert('', tk.END, iid=_d['date'], values=(
                _idx, _d['date'], _d['weekday'], _d['lunar'], _d['score'],
                _d['level'], ('%s %d' % ('★' * _stars, _fit)) if _stars else '—',
                _marks,
                _reason_text(_d),
                '%s（%s）%s' % (_d['best_hour']['时辰'],
                              _d['best_hour']['时段'],
                              (' ' + _d['sun_moon_tag']) if _d.get('sun_moon_tag') else ''), _d['kind']),
                tags=(_tag,))

    # ---------- 001 §231：满分核验列悬停提示 ----------
    def _on_top_motion(self, event):
        """悬停「满分核验」列：弹出五项逐条说明（缺失项即诊断报告）。"""
        if getattr(self, '_tip_win', None) is not None and \
                self.top_tree.identify_column(event.x) != self._perfect_col:
            self._hide_tip()
        if self.top_tree.identify_column(event.x) != self._perfect_col:
            return
        _iid = self.top_tree.identify_row(event.y)
        _d = (getattr(self, '_top_map', None) or {}).get(_iid)
        if not _d:
            self._hide_tip()
            return
        _chk = _d.get('check') or {}
        _items = _chk.get('items') or []
        if not _items:
            self._hide_tip()
            return
        _head = '满分核验  %d/%d%s' % (
            _chk.get('ok_count', 0), len(_items),
            '  ·  极品日课' if _chk.get('all_ok') else '')
        _body = ['%s %s：%s' % ('✓' if _i.get('ok') else '✗',
                                _i.get('key', ''), _i.get('detail', ''))
                 for _i in _items]
        self._show_tip('\n'.join([_head] + _body), event.x_root, event.y_root)

    def _show_tip(self, text, x_root, y_root):
        if getattr(self, '_tip_win', None) is None:
            self._tip_win = tk.Toplevel(self.top_tree)
            self._tip_win.overrideredirect(True)
            self._tip_win.attributes('-topmost', True)
            tk.Label(self._tip_win, text='', justify=tk.LEFT,
                     background='#FFFDE7', foreground='#333333',
                     relief=tk.SOLID, borderwidth=1,
                     font=('微软雅黑', 9), padx=8, pady=6).pack()
        self._tip_win.winfo_children()[0].configure(text=text)
        self._tip_win.geometry('+%d+%d' % (x_root + 14, y_root + 14))
        self._tip_win.deiconify()

    def _hide_tip(self):
        if getattr(self, '_tip_win', None) is not None:
            self._tip_win.withdraw()

    def _render_heatmap(self, res):
        cv = self.heat_canvas
        cv.delete('all')
        self._day_map = {_d['date']: _d for _d in res['all_days']}
        _start = date.fromisoformat(res['meta']['start'])
        _end = date.fromisoformat(res['meta']['end'])

        _months = []
        _y, _mth = _start.year, _start.month
        while (_y, _mth) <= (_end.year, _end.month):
            _months.append((_y, _mth))
            _mth += 1
            if _mth > 12:
                _mth, _y = 1, _y + 1

        _yoff = PAD
        for (_y, _mth) in _months:
            _yoff = self._draw_month(cv, _y, _mth, _yoff)
            _yoff += 12
        cv.configure(scrollregion=(0, 0, PAD + CELL_W * 7 + PAD, _yoff))

    def _draw_month(self, cv, year, month, y0):
        cv.create_text(PAD, y0, anchor='nw', text='%d 年 %d 月' % (year, month),
                       font=('Microsoft YaHei UI', 11, 'bold'))
        _y = y0 + 26
        for _i, _w in enumerate(('一', '二', '三', '四', '五', '六', '日')):
            cv.create_text(PAD + _i * CELL_W + CELL_W / 2, _y,
                           text=_w, font=('Microsoft YaHei UI', 9),
                           fill='#546E7A')
        _y += 18
        for _r, _week in enumerate(calendar.Calendar(0).monthdatescalendar(year, month)):
            for _c, _d in enumerate(_week):
                if _d.month != month:
                    continue
                _x = PAD + _c * CELL_W
                _cy = _y + _r * CELL_H
                _ds = _d.strftime('%Y-%m-%d')
                _info = self._day_map.get(_ds)
                _kind = _info['kind'] if _info else '范围外'
                _fill, _fg = ((COLOR_JI, TXT_ON_DARK) if _kind == '吉日' else
                              (COLOR_CAUTION, TXT_ON_YELLOW) if _kind == '慎用' else
                              (COLOR_VETO, '#ECEFF1') if _kind == '否决' else
                              (COLOR_NA, '#B0BEC5'))
                _top = _ds in self._top_dates
                _tag = 'cell_' + _ds
                cv.create_rectangle(
                    _x + 1, _cy + 1, _x + CELL_W - 2, _cy + CELL_H - 2,
                    fill=_fill, outline='#1565C0' if _top else '#CFD8DC',
                    width=3 if _top else 1, tags=(_tag,))
                cv.create_text(_x + 6, _cy + 12, text=str(_d.day), anchor='w',
                               fill=_fg, font=('Microsoft YaHei UI', 9, 'bold'))
                if _info:
                    # 吉神星级角标（右上角）：39 分 → ★★★；否决格不标（避免误导）
                    _stars = jishen_stars(_info.get('jishen_fit') or 0)
                    if _stars and _kind != '否决':
                        _sc = STAR_ON_JI if _kind == '吉日' else STAR_ON_CAUTION
                        cv.create_text(_x + CELL_W - 4, _cy + 12,
                                       text='★' * _stars, anchor='e',
                                       fill=_sc, font=('Microsoft YaHei UI', 7))
                    # 否决格绝不显示 0 分（001 §210：用户会误读为零分上榜）
                    _body = '×' if _kind == '否决' else '%s' % _info['score']
                    cv.create_text(_x + CELL_W / 2, _cy + 34, text=_body,
                                   fill=_fg, font=('Microsoft YaHei UI', 8))
                cv.tag_bind(_tag, '<Button-1>',
                            lambda _e, _s=_ds: self._on_day_click(_s))
                cv.tag_bind(_tag, '<Enter>',
                            lambda _e, _s=_ds: self._on_day_hover(_s))
        return _y + 6 * CELL_H + 4

    # ---------------------------------------------------------------- 交互
    def _on_tree_select(self):
        _sel = self.top_tree.selection()
        if _sel:
            self._show_timeline(_sel[0])

    def _find_top(self, ds):
        """按日期取 Top-N 记录（不在榜返回 None）。"""
        for _d in (self._res or {}).get('days', []):
            if _d.get('date') == ds:
                return _d
        return None

    def _on_top_double_click(self, event):
        """双击榜内行 → 日课详情窗口（001 §210 Commit 4）。"""
        _row = self.top_tree.identify_row(event.y)
        if _row:
            self.top_tree.selection_set(_row)
            self._show_day_detail(_row)

    def _on_top_right_click(self, event):
        """右键榜内行 → 详情 / 加入择日贴 / 时间轴（001 §210 Commit 4）。"""
        _row = self.top_tree.identify_row(event.y)
        if not _row:
            return
        self.top_tree.selection_set(_row)
        self.top_tree.focus(_row)
        _menu = tk.Menu(self.win, tearoff=0)
        _menu.add_command(label='查看日课详情',
                          command=lambda: self._show_day_detail(_row))
        _menu.add_command(label='加入择日贴',
                          command=lambda: self._add_to_tie(_row))
        _menu.add_separator()
        _menu.add_command(label='查看十二时辰时间轴',
                          command=lambda: self._show_timeline(_row))
        self._ctx_menu = _menu      # 持有引用，防止弹出前被回收
        try:
            _menu.tk_popup(event.x_root, event.y_root)
        finally:
            _menu.grab_release()

    def _add_to_tie(self, ds):
        """右键"加入择日贴"：交主程序回调打包 entry（本模块不算分、不建第二份口径）。"""
        _d = self._find_top(ds)
        if _d is None:
            return
        if not callable(self.add_tie_callback):
            messagebox.showinfo(
                '暂不可用', '当前窗口未接入择日贴（请从主程序面板重新打开反推）',
                parent=self.win)
            return
        try:
            self.add_tie_callback(_d, self.event_var.get())
        except Exception as _e:
            messagebox.showerror('加入择日贴失败', str(_e), parent=self.win)

    def _show_day_detail(self, ds):
        """自包含日课详情窗：反推记录无主程序 result['detail']，故不依赖 self.results。"""
        _d = self._find_top(ds)
        if _d is None:
            messagebox.showinfo(
                '日课详情', '%s 不在 Top-N 榜内（热力日历仅显示归类与评分）' % ds,
                parent=self.win)
            return
        _meta = (self._res or {}).get('meta', {})
        _ev = _meta.get('event_type') or '—'
        _bh = _d['best_hour']
        _fit = int(_d.get('jishen_fit') or 0)
        _stars = jishen_stars(_fit)

        _win = tk.Toplevel(self.win)
        _win.title('日课详情 · %s · %s' % (_d['date'], _ev))
        # 手机适配：窗口不得超过屏幕，否则底部（右侧）按钮条会被裁到屏幕外，
        # 表现为"详情窗没有保存/打印"。按可用屏幕尺寸收敛后定位到左上角。
        _sw = _win.winfo_screenwidth()
        _sh = _win.winfo_screenheight()
        _w = min(920, max(320, _sw - 40))
        _h = min(720, max(320, _sh - 60))
        _win.geometry('%dx%d+%d+%d' % (_w, _h, 10, 10))
        _win.minsize(min(760, _w), min(560, _h))
        _win.transient(self.win)

        # 底部按钮条：先于内容区 pack 到底边，窗口被压缩时按钮也不会消失
        _bar = ttk.Frame(_win, padding=(4, 6, 8, 10))
        _bar.pack(side=tk.BOTTOM, fill=tk.X)

        _head = ttk.Frame(_win, padding=(12, 10, 12, 2))
        _head.pack(fill=tk.X)
        _font_l = ('Microsoft YaHei UI', 9, 'bold')
        _wrap = max(220, _w - 180)      # 随窗口宽度收敛，避免表头把窗口撑出屏幕
        for _i, (_k, _v) in enumerate((
                ('日　　期', '%s　%s　农历%s' % (_d['date'], _d['weekday'],
                                               _d['lunar'])),
                ('四　　柱', _d['sizhu']),
                ('用　　事', _ev),
                ('评　　分', '%s 分　%s　[%s]' % (_d['score'], _d['level'],
                                               _d['kind'])),
                ('最优时辰', '%s（%s）　时柱 %s' % (_bh['时辰'], _bh['时段'],
                                                _bh['时柱'])),
                ('吉神契合', '%s　%d 分' % ('★' * _stars if _stars else '—', _fit)),
                ('吉　　神', (str(_d.get('jishen') or '') or '—')
                 + (('　｜　' + _d['sun_moon_tag']) if _d.get('sun_moon_tag') else '')),
                ('扣分主因', _reason_text(_d, compact=False)),
                ('评分理由', str(_d.get('reason') or '') or '—'))):
            ttk.Label(_head, text=_k, font=_font_l).grid(
                row=_i, column=0, sticky='ne', pady=1)
            ttk.Label(_head, text=str(_v), wraplength=_wrap,
                      justify=tk.LEFT).grid(row=_i, column=1, sticky='w',
                                            padx=(6, 0), pady=1)

        _nb = ttk.Notebook(_win)
        _nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 6))

        # 页1：扣分明细 / 忌项 / 否决原因
        _p1 = ttk.Frame(_nb, padding=6)
        _nb.add(_p1, text='扣分明细 / 忌项')
        _t1 = ttk.Treeview(_p1, columns=('类型', '项目', '分值'),
                           show='headings', height=8)
        for _c, _w in (('类型', 110), ('项目', 470), ('分值', 70)):
            _t1.heading(_c, text=_c)
            _t1.column(_c, width=_w,
                       anchor=tk.W if _c == '项目' else tk.CENTER,
                       stretch=(_c == '项目'))
        _t1.pack(fill=tk.BOTH, expand=True)
        _di = _d.get('deduct_items') or []
        _ji = _d.get('ji_items') or []
        _vr = _d.get('veto_reasons') or []
        for _s in _di:
            _t1.insert('', tk.END, values=('扣分神煞', _s.get('name', ''),
                                           int(_s.get('score') or 0)))
        for _j in _ji:
            _t1.insert('', tk.END, values=('忌　　项', _j, '—'))
        for _r in _vr:
            _t1.insert('', tk.END, values=('否决原因', _r, '—'))
        if not (_di or _ji or _vr):
            _t1.insert('', tk.END, values=('—', '无扣分、无忌项、无否决', '—'))

        # 页2：十二时辰
        _p2 = ttk.Frame(_nb, padding=6)
        _nb.add(_p2, text='十二时辰')
        _t2 = ttk.Treeview(_p2, columns=('时辰', '时段', '时柱', '评分', '等级',
                                        '吉神', '凶煞', '行动建议'),
                           show='headings', height=12)
        for _c, _w in (('时辰', 54), ('时段', 60), ('时柱', 52), ('评分', 52),
                       ('等级', 90), ('吉神', 220), ('凶煞', 132),
                       ('行动建议', 196)):
            _t2.heading(_c, text=_c)
            _t2.column(_c, width=_w,
                       anchor=tk.W if _c in ('等级', '吉神', '凶煞', '行动建议')
                       else tk.CENTER,
                       stretch=_c in ('吉神', '凶煞', '行动建议'))
        _t2.pack(fill=tk.BOTH, expand=True)
        _t2.tag_configure('best', background='#FFE082')
        for _h in (_d.get('hours') or []):
            _tags = ('best',) if _h['地支'] == _bh['地支'] else ()
            _t2.insert('', tk.END, values=(
                _h['时辰'], _h['时段'], _h['时柱'], _h['score'], _h['level'],
                '、'.join(_h.get('吉神') or []) or '—',
                '、'.join(_h.get('凶') or []) or '—',
                self._hour_advice(_h, _bh['地支'], _ev, _d['score'])),
                tags=_tags)

        ttk.Button(_bar, text='关闭', command=_win.destroy).pack(
            side=tk.RIGHT, padx=(4, 4))
        ttk.Button(_bar, text='打印',
                   command=lambda: self._print_day_detail(
                       _d, _ev, _bh, _stars, _fit)).pack(
            side=tk.RIGHT, padx=4)
        ttk.Button(_bar, text='保存',
                   command=lambda: self._save_day_detail(
                       _d, _ev, _bh, _stars, _fit)).pack(
            side=tk.RIGHT, padx=4)

    def _build_detail_lines(self, d, ev, bh, stars, fit):
        """构造日课详情的纯文本行列表（保存/打印共用数据源）。"""
        lines = []
        lines.append('日课详情 · %s · %s' % (d['date'], ev))
        lines.append('=' * 50)
        lines.append('日　　期：%s　%s　农历%s' % (d['date'], d['weekday'], d['lunar']))
        lines.append('四　　柱：%s' % d['sizhu'])
        lines.append('用　　事：%s' % ev)
        lines.append('评　　分：%s 分　%s　[%s]' % (d['score'], d['level'], d['kind']))
        lines.append('最优时辰：%s（%s）　时柱 %s' % (bh['时辰'], bh['时段'], bh['时柱']))
        lines.append('吉神契合：%s　%d 分' % ('★' * stars if stars else '—', fit))
        lines.append('吉　　神：%s' % (str(d.get('jishen') or '') or '—'))
        lines.append('扣分主因：%s' % _reason_text(d, compact=False))
        lines.append('评分理由：%s' % (str(d.get('reason') or '') or '—'))
        lines.append('')
        lines.append('【扣分明细 / 忌项】')
        lines.append('-' * 50)
        _di = d.get('deduct_items') or []
        _ji = d.get('ji_items') or []
        _vr = d.get('veto_reasons') or []
        if not (_di or _ji or _vr):
            lines.append('无扣分、无忌项、无否决')
        for _s in _di:
            lines.append('扣分神煞　%s　%d 分' % (_s.get('name', ''),
                                                int(_s.get('score') or 0)))
        for _j in _ji:
            lines.append('忌　　项　%s' % _j)
        for _r in _vr:
            lines.append('否决原因　%s' % _r)
        lines.append('')
        lines.append('【十二时辰】')
        lines.append('-' * 50)
        lines.append('时辰　时段　　时柱　评分　等级　　吉神　　　　凶煞　　　行动建议')
        for _h in (d.get('hours') or []):
            _mark = '★' if _h['地支'] == bh['地支'] else ' '
            lines.append('%s%s　%s　%s　%s　%s　%s　%s　%s' % (
                _mark, _h['时辰'], _h['时段'], _h['时柱'], _h['score'],
                _h['level'],
                '、'.join(_h.get('吉神') or []) or '—',
                '、'.join(_h.get('凶') or []) or '—',
                self._hour_advice(_h, bh['地支'], ev, d['score'])))
        return lines

    def _save_day_detail(self, d, ev, bh, stars, fit):
        """保存日课详情为 TXT（filedialog 选路径，落盘后提示）。"""
        _default = '日课详情_%s_%s.txt' % (d['date'], ev)
        self._save_text(self._build_detail_lines(d, ev, bh, stars, fit),
                        _default, '保存日课详情')

    def _print_day_detail(self, d, ev, bh, stars, fit):
        """打印日课详情：生成临时 HTML，调用系统默认打印。"""
        self._print_text(self._build_detail_lines(d, ev, bh, stars, fit),
                         '日课详情 · %s · %s' % (d['date'], ev))

    def _on_day_click(self, ds):
        if ds in self._top_dates:
            self.top_tree.selection_set(ds)
            self.top_tree.see(ds)
            self.nb.select(2)
            self._show_timeline(ds)
            return
        _info = self._day_map.get(ds)
        if not _info:
            return
        self.status_var.set('%s：%s ｜ %s（评分 %s，%s）' % (
            ds, _reason_text(_info, compact=False), _info['kind'],
            _info['score'], _info['level']))

    def _on_day_hover(self, ds):
        """热力格悬浮提示：把"为什么黄/为什么红"直接写进状态栏。"""
        _info = self._day_map.get(ds)
        if not _info:
            self.status_var.set('%s：不在扫描范围内' % ds)
            return
        self.status_var.set('%s ｜ %s ｜ %s 分 ｜ %s ｜ 吉神契合 %s ｜ %s' % (
            ds, _info['kind'], _info['score'], _info['level'],
            _info.get('jishen_fit') or 0, _reason_text(_info, compact=False)))

    def _hour_advice(self, h, best_zhi, event_type, day_score):
        """时辰级行动建议（001 §210 微调：禁止复用日级 yi_list 充数）。"""
        if h['地支'] == best_zhi:
            return '宜在此刻%s（当日最高分 %s 分）' % (event_type or '用事',
                                                   day_score)
        if h['disabled'] or h['veto'] or int(h['score']) <= 0:
            _why = h['凶'] or (['否决 %d 项' % h['veto']] if h['veto'] else [])
            return '忌用：' + ('、'.join(_why) if _why else '五不遇时')
        if h['凶']:
            return '犯：' + '、'.join(h['凶']) + '（可用但避忌）'
        if h['吉神']:
            return '吉神：' + '、'.join(h['吉神'])
        return '平：无吉神亦无凶煞'

    def _show_timeline(self, ds):
        _entry = self._find_top(ds)
        if _entry is None:
            self.tl_head.set('%s：不在 Top-N 榜内（热力日历中仅显示归类与评分）' % ds)
            for _i in self.tl_tree.get_children():
                self.tl_tree.delete(_i)
            return
        _bh = _entry['best_hour']
        _ev = (self._res or {}).get('meta', {}).get('event_type', '')
        self.tl_head.set('%s %s 农历%s ｜ %s ｜ 最优 %s（%s）｜ %s分 %s ｜ 吉神契合 %s' % (
            _entry['date'], _entry['weekday'], _entry['lunar'], _entry['sizhu'],
            _bh['时辰'], _bh['时段'], _entry['score'], _entry['level'],
            _entry['jishen_fit']))
        for _i in self.tl_tree.get_children():
            self.tl_tree.delete(_i)
        for _h in _entry['hours']:
            _tags = []
            if _h['地支'] == _bh['地支']:
                _tags.append('best')
            if _h['disabled'] or _h['veto'] or int(_h['score']) <= 0:
                _tags.append('bad')
            else:
                _tags.append('ok')
            if _h['disabled']:
                _tags.append('disabled')
            _advice = self._hour_advice(_h, _bh['地支'], _ev, _entry['score'])
            _note = []
            if _h['disabled']:
                _note.append('禁用（五不遇时）')
            if _h['veto']:
                _note.append('有否决 %d 项' % _h['veto'])
            if _h['shashi']:
                _note.append('杀师时')
            # 凶煞已进建议列（"犯：..."），仅最优行在此重复一次便于对照
            if _h['凶'] and _h['地支'] == _bh['地支']:
                _note.append('凶煞：' + '、'.join(_h['凶']))
            self.tl_tree.insert('', tk.END, values=(
                _h['时辰'], _h['时段'], _h['时柱'], _h['score'], _h['level'],
                _advice, '；'.join(_note) or '—'), tags=tuple(_tags))
        _best_row = [_i for _i, _h in zip(self.tl_tree.get_children(),
                                          _entry['hours'])
                     if _h['地支'] == _bh['地支']]
        if _best_row:
            self.tl_tree.see(_best_row[0])

        # 001 §214 P2-B：渲染动作轴三行
        self._render_action_axis(_entry)

    def _render_action_axis(self, entry):
        """根据 day_record['action_plan'] 渲染动作轴三行 + 错峰文案 + 按钮状态。"""
        _plan = entry.get('action_plan')
        if not _plan:
            self.act_status_var.set('（本事项未配置动作时序，或当日无可分配时辰）')
            for _seq, _info in self.act_rows:
                _info.config(text='—', foreground='')
            self.act_alt_var.set('')
            self.send_tie_btn.config(state=tk.DISABLED)
            return
        _status = _plan.get('status')
        _status_txt = {'full': '三段齐备', 'partial': '缺段（建议错峰）',
                       'insufficient': '仅 1 段（建议另择）',
                       'none': '本日无可用动作时辰'}.get(_status, _status)
        # 001 §214 C2（2026-11-03 拍板）：partial 且缺段含发轿/起轿 →
        # 事件级黄标「缺上轿吉时」，不把提示藏在通用文案里（排序权重不变）。
        _missing = [str(x) for x in (_plan.get('missing') or [])]
        if _status == 'partial' and any(('发轿' in x or '起轿' in x) for x in _missing):
            _status_txt = '⚠ 缺上轿吉时（%s）' % _status_txt
        self.act_status_var.set('状态：%s' % _status_txt)
        _segments = _plan.get('plan') or []
        for _i, (_seq_lbl, _info_lbl) in enumerate(self.act_rows):
            if _i < len(_segments):
                _s = _segments[_i]
                _txt = '%s　%s　%s　%s　%s分　%s' % (
                    _s['label'], _s['zhi'] + '时', _s['range'],
                    _s['ganzhi'], _s['score'], _s['level'])
                _fg = '#1B5E20' if _status == 'full' else '#E65100'
                _info_lbl.config(text=_txt, foreground=_fg)
            else:
                _info_lbl.config(text='（缺）', foreground='#C62828')
        # 错峰建议
        _alts = _plan.get('alt') or []
        self.act_alt_var.set(
            '错峰建议：' + '；'.join(a.get('suggest', '') for a in _alts)
            if _alts else '')
        # 交叉校验警告
        _checks = _plan.get('checks') or []
        _warns = [c.get('detail', '') for c in _checks if not c.get('ok')]
        if _warns:
            _cur = self.act_alt_var.get()
            self.act_alt_var.set(
                (_cur + '　' if _cur else '') + '⚠ ' + '；'.join(_warns))
        # 按钮：仅 full/partial 可生成红帖（insufficient/none 不生成）
        self.send_tie_btn.config(
            state=tk.NORMAL if _status in ('full', 'partial') else tk.DISABLED)
        # 缓存当前选中日，供按钮回调使用
        self._current_action_entry = entry

    def _send_action_plan_to_tie(self):
        """tab3「生成红纸帖」：把带 action_plan 的日记录交主程序回调。

        主程序侧透传 action_plan → 择日贴 prepare_entry 的接线在 P2-C/D；
        本批按钮已可用，action_plan 随 day_record 透传，未消费时红帖行为不变。
        """
        _entry = getattr(self, '_current_action_entry', None)
        if _entry is None:
            return
        if not callable(self.add_tie_callback):
            messagebox.showinfo(
                '暂不可用', '当前窗口未接入择日贴（请从主程序面板重新打开反推）',
                parent=self.win)
            return
        try:
            self.add_tie_callback(_entry, self.event_var.get())
        except Exception as _e:
            messagebox.showerror('生成红帖失败', str(_e), parent=self.win)


def open_reverse_window(master, event_type, owners=None, context=None,
                        modify_callback=None, add_tie_callback=None):
    """主程序入口：打开反推面板（不阻塞主窗口，不进入评分链路）。

    modify_callback：用户点"修改事主与山向"时回调，由主程序负责把焦点
    跳转回事主卡片与坐山输入框（方案 A：轻量回主程序改）。
    add_tie_callback：右键"加入择日贴"回调，签名 (day_record, event_type)，
    由主程序构建择日贴 entry（反推模块不复制 owner/山向打包口径）。
    """
    return ReverseWindow(master, event_type, owners, context, modify_callback,
                         add_tie_callback)
