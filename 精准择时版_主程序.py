# -*- coding: utf-8 -*-
"""
================================================================================
择日大师 · 精准择时版（独立版）v1.0
================================================================================
定位：从主程序剥离的「精准择时（反推 Top-N）」独立交付物。

铁律：底层算法必须与主仓共享，严禁新建一套计分逻辑。
- 反推引擎 / 评分器 / 四柱计算器 / 今日黄历 / 玄空飞星等一律 import 现有模块；
- 事主 owners_data 与 context 组装口径严格对齐主程序
  （_collect_owners_data / open_reverse_panel），含真太阳时经度透传；
- 独立版只做「参数收集 + 调用 modules.反推UI.open_reverse_window」的瘦壳。

数据隔离：配置写入 APP_DIR/精准择时版_配置.json，与主程序记录互不干扰。
（frozen 时 APP_DIR = exe 所在目录；源码运行时 = 项目根目录——与主程序 L110 同口径）
================================================================================
"""

import json
import os
import sys
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

# ----- 路径与 APP_DIR（口径同主程序 L95-110） -----
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
    PROJECT_ROOT = APP_DIR
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = PROJECT_ROOT
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CONFIG_PATH = os.path.join(APP_DIR, '精准择时版_配置.json')

# ----- 底层模块：严格复用主仓，不新建计分逻辑 -----
from modules.事项标准 import UI_EVENTS, MOUNTAIN_CENTERED_EVENTS
from modules.二十四山 import get_shan_xiang_list, shan_xiang_to_shan
from modules.城市经度 import CITY_NAMES, get_longitude
from modules.四柱计算器 import calculate_sizhu
from modules.反推UI import open_reverse_window
from modules.高精度农历转换 import get_lunar_converter

VERSION = 'v1.0'
# 宅型适用事项（与主程序 L1401 同口径）
HOUSE_TYPE_EVENTS = {"修造", "动土", "拆舍", "入宅"}
# 山向适用事项（山家核心事项 + 修造/动土/拆舍/入宅/安葬，同主程序 special_frame 口径）
SHAN_XIANG_EVENTS = set(MOUNTAIN_CENTERED_EVENTS) | {"修造", "动土", "拆舍", "入宅"}
# 双事主事项（嫁娶族需新郎新娘双方年命）
DUAL_OWNER_EVENTS = {"嫁娶", "订婚", "纳采"}


def _city_to_longitude(city_text):
    """城市名/经度串 → 经度 float。空值回退 120.0（北京时间基准，同主程序 §48 口径）。"""
    raw = (city_text or '').strip()
    if not raw:
        return 120.0
    lon = get_longitude(raw)
    if lon is not None:
        return float(lon)
    try:
        v = float(raw)
        return v if 60.0 <= v <= 150.0 else 120.0
    except (TypeError, ValueError):
        return 120.0


class 精准择时版App:
    """独立版瘦壳：参数区（事项/山向/事主/城市经度）+ 工具栏 + 启动反推面板。"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"择日大师 · 精准择时版 {VERSION}")
        self.root.geometry("980x620")
        self.root.minsize(920, 560)
        self.reverse_window = None
        self.owner_rows = []
        self._zeri_tie_pending = []       # 择日贴暂存（窗口未开时先存，开窗后灌入）
        self.calendar_type_var = tk.StringVar(value='solar')  # 'solar'=公历, 'lunar'=农历（闰月填负数，如闰五月=-5）

        self._build_toolbar()
        self._build_param_area()
        self._build_owner_area()
        self._build_action_area()
        self._build_statusbar()
        self._load_config()
        self._on_event_change()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- UI 构建 ----------
    def _build_toolbar(self):
        bar = ttk.LabelFrame(self.root, text="扩展工具", padding=6)
        bar.pack(fill=tk.X, padx=10, pady=(8, 4))
        ttk.Button(bar, text="🧭 电子罗盘", command=self._open_compass).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="📅 今日黄历", command=self._open_today_huangli).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="📊 八字排盘", command=self._open_bazi).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="🔮 玄空飞星排盘", command=self._open_xuankong).pack(side=tk.LEFT, padx=6)
        # 001 §238.14 P1-c：择日贴（反推右键「加入择日贴」的落地窗口）
        self.zeeri_tie_btn = ttk.Button(bar, text="📜 择日贴",
                                        command=self.open_zeri_tie)
        self.zeeri_tie_btn.pack(side=tk.LEFT, padx=6)

    def _build_param_area(self):
        frm = ttk.LabelFrame(self.root, text="择时参数", padding=8)
        frm.pack(fill=tk.X, padx=10, pady=4)

        ttk.Label(frm, text="事项：").grid(row=0, column=0, sticky=tk.W, padx=4)
        self.event_var = tk.StringVar(value="修造")
        ev = ttk.Combobox(frm, textvariable=self.event_var, values=UI_EVENTS,
                          width=10, state="readonly")
        ev.grid(row=0, column=1, sticky=tk.W, padx=4)
        ev.bind("<<ComboboxSelected>>", lambda e: self._on_event_change())

        ttk.Label(frm, text="宅型：").grid(row=0, column=2, sticky=tk.W, padx=4)
        self.house_type_var = tk.StringVar(value="阳宅")
        self.house_combo = ttk.Combobox(frm, textvariable=self.house_type_var,
                                        values=["阳宅", "阴宅"], width=8, state="readonly")
        self.house_combo.grid(row=0, column=3, sticky=tk.W, padx=4)

        ttk.Label(frm, text="山向：").grid(row=0, column=4, sticky=tk.W, padx=4)
        self.shan_xiang_var = tk.StringVar()
        self.shan_combo = ttk.Combobox(frm, textvariable=self.shan_xiang_var,
                                       values=get_shan_xiang_list(use_24_shan=True),
                                       width=12, state="readonly")
        self.shan_combo.grid(row=0, column=5, sticky=tk.W, padx=4)

        ttk.Label(frm, text="兼向：").grid(row=0, column=6, sticky=tk.W, padx=4)
        self.jian_xiang_var = tk.StringVar(value="正中")
        # 同主程序 §59.13：可下拉选环序兼向，也可手动输入"兼X"
        self.jian_combo = ttk.Combobox(frm, textvariable=self.jian_xiang_var,
                                       values=["正中", "兼左", "兼右"], width=8)
        self.jian_combo.grid(row=0, column=7, sticky=tk.W, padx=4)

        ttk.Button(frm, text="罗盘", width=6,
                   command=self._open_compass).grid(row=0, column=8, sticky=tk.W, padx=6)

        hint = ("山向仅对修造/动土/拆舍/入宅/安葬/作灶/安床等山家事项生效；"
                "城市决定真太阳时（留空按北京时间 120°E）。")
        ttk.Label(frm, text=hint, foreground="#666").grid(
            row=1, column=0, columnspan=9, sticky=tk.W, padx=4, pady=(6, 0))

    def _build_owner_area(self):
        self.owner_frame = ttk.LabelFrame(self.root, text="事主信息（嫁娶请同时填新郎新娘）", padding=8)
        self.owner_frame.pack(fill=tk.X, padx=10, pady=4)
        head = ["角色", "姓名", "性别", "出生年", "月", "日", "时", "分", "出生城市/经度"]
        for c, t in enumerate(head):
            ttk.Label(self.owner_frame, text=t).grid(row=0, column=c, padx=3, sticky=tk.W)
        # 001 §238.17 公历/农历切换（闰月填负数，如闰五月=-5）
        cal_row = ttk.Frame(self.owner_frame)
        cal_row.grid(row=1, column=0, columnspan=9, sticky=tk.W, padx=3, pady=(2, 2))
        ttk.Label(cal_row, text="历法：").pack(side=tk.LEFT)
        ttk.Radiobutton(cal_row, text="公历(阳历)", variable=self.calendar_type_var,
                        value='solar', command=self._on_calendar_change).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(cal_row, text="农历(阴历)", variable=self.calendar_type_var,
                        value='lunar', command=self._on_calendar_change).pack(side=tk.LEFT, padx=2)
        ttk.Label(cal_row, text="（农历闰月填负数，如闰五月=-5）",
                  foreground="gray").pack(side=tk.LEFT, padx=8)
        self._add_owner_row(1, "事主")
        self._add_owner_row(2, "家人")

    def _on_calendar_change(self):
        """公历/农历切换后，所有事主四柱回显立即刷新。"""
        for i in range(len(self.owner_rows)):
            self._update_owner_sizhu(i)

    def _add_owner_row(self, idx, default_role):
        """新增一位事主：输入行 + 四柱/生肖/喜用神回显行（001 §238.14 P1-b）。

        idx 从 1 起：输入行占 grid 行 2*idx（表头 0 + 日历切换 1 各占一行后），
        回显行占 2*idx+1。回显与主程序 calculate_owner_sizhu 同源（calculate_sizhu
        透传经度 + calculate_xishen_yongshen），纯展示，不参与评分。
        """
        r = idx * 2          # 表头 row 0，日历切换 row 1，事主1输入 row 2，回显 row 3
        i = len(self.owner_rows)          # owner_rows 下标（0 起）
        role = ttk.Combobox(self.owner_frame, values=["事主", "新郎", "新娘", "家人"],
                            width=6)
        role.set(default_role)
        role.grid(row=r, column=0, padx=3)
        name = ttk.Entry(self.owner_frame, width=10)
        name.grid(row=r, column=1, padx=3)
        gender = ttk.Combobox(self.owner_frame, values=["男", "女"], width=4, state="readonly")
        gender.set("男")
        gender.grid(row=r, column=2, padx=3)
        year = ttk.Entry(self.owner_frame, width=7)
        year.grid(row=r, column=3, padx=3)
        month = ttk.Entry(self.owner_frame, width=4)
        month.grid(row=r, column=4, padx=3)
        day = ttk.Entry(self.owner_frame, width=4)
        day.grid(row=r, column=5, padx=3)
        hour = ttk.Entry(self.owner_frame, width=4)
        hour.insert(0, "12")
        hour.grid(row=r, column=6, padx=3)
        minute = ttk.Entry(self.owner_frame, width=4)
        minute.insert(0, "0")
        minute.grid(row=r, column=7, padx=3)
        city = ttk.Combobox(self.owner_frame, values=sorted(CITY_NAMES), width=14)
        city.grid(row=r, column=8, padx=3)

        # ---- 回显行：四柱 / 生肖 / 喜神 / 用神 / 嫁娶专用 / 八字详情 ----
        info = ttk.Frame(self.owner_frame)
        info.grid(row=r + 1, column=0, columnspan=9, sticky=tk.W,
                  padx=3, pady=(0, 4))
        sizhu_var = tk.StringVar(value="未计算")
        zodiac_var = tk.StringVar(value="")
        xishen_var = tk.StringVar(value="")
        yongshen_var = tk.StringVar(value="")
        mar1_var = tk.StringVar(value="")   # 夫星（女）/ 阳气（男）
        mar2_var = tk.StringVar(value="")   # 子星（女）
        mar3_var = tk.StringVar(value="")   # 阴胎（女）
        tsf_var = tk.StringVar(value="")    # 真太阳时口径标注
        ttk.Label(info, text="四柱：").pack(side=tk.LEFT)
        ttk.Label(info, textvariable=sizhu_var,
                  font=("Microsoft YaHei UI", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(info, textvariable=tsf_var,
                  foreground="darkgreen").pack(side=tk.LEFT, padx=(2, 0))
        ttk.Label(info, text="生肖：").pack(side=tk.LEFT, padx=(14, 0))
        ttk.Label(info, textvariable=zodiac_var, foreground="blue",
                  font=("Microsoft YaHei UI", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(info, text="喜神：").pack(side=tk.LEFT, padx=(14, 0))
        ttk.Label(info, textvariable=xishen_var, foreground="blue").pack(side=tk.LEFT)
        ttk.Label(info, text="用神：").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(info, textvariable=yongshen_var, foreground="green").pack(side=tk.LEFT)
        ttk.Label(info, textvariable=mar1_var, foreground="purple").pack(
            side=tk.LEFT, padx=(14, 0))
        ttk.Label(info, textvariable=mar2_var, foreground="purple").pack(
            side=tk.LEFT, padx=(8, 0))
        ttk.Label(info, textvariable=mar3_var, foreground="green").pack(
            side=tk.LEFT, padx=(8, 0))
        ttk.Button(info, text="八字详情", width=9,
                   command=lambda j=i: self._open_owner_bazi(j)).pack(
                       side=tk.LEFT, padx=(14, 0))

        self.owner_rows.append({
            'role': role, 'name': name, 'gender': gender,
            'year': year, 'month': month, 'day': day,
            'hour': hour, 'minute': minute, 'city': city,
            'sizhu': sizhu_var, 'zodiac': zodiac_var,
            'xishen': xishen_var, 'yongshen': yongshen_var,
            'mar1': mar1_var, 'mar2': mar2_var, 'mar3': mar3_var,
            'truesolar': tsf_var,
        })
        # 出生信息变动即重算回显（失焦 / 回车 / 下拉选择）
        for _w in (year, month, day, hour, minute):
            _w.bind('<FocusOut>', lambda e, j=i: self._update_owner_sizhu(j))
            _w.bind('<Return>', lambda e, j=i: self._update_owner_sizhu(j))
        gender.bind('<<ComboboxSelected>>', lambda e, j=i: self._update_owner_sizhu(j))
        city.bind('<<ComboboxSelected>>', lambda e, j=i: self._update_owner_sizhu(j))

    # ---------- 事主四柱 / 喜用神回显（001 §238.14 P1-b，纯展示） ----------
    def _owner_birth(self, i):
        """读取第 i 位事主出生信息 → (birth_date, hour, minute, longitude)。

        非法/缺失抛 ValueError（文案可直接展示）；经度口径同 _city_to_longitude，
        与 _collect_owners_data / 主程序 calculate_owner_sizhu 一致。
        001 §238.17：支持农历输入（闰月填负数如闰五月=-5），底层走高精度农历转换。
        """
        row = self.owner_rows[i]
        y = row['year'].get().strip()
        m = row['month'].get().strip()
        d = row['day'].get().strip()
        if not (y and m and d):
            raise ValueError('年月日未填写完整')
        year, month, day = int(y), int(m), int(d)
        hour = int(row['hour'].get().strip() or '12')
        minute = int(row['minute'].get().strip() or '0')
        # 001 §238.17：农历转公历（闰月填负数，如闰五月=-5，与主程序 L2780-2791 同口径）
        if self.calendar_type_var.get() == 'lunar':
            try:
                converter = get_lunar_converter()
                solar_date = converter.lunar_to_solar(year, month, day, hour, minute, 0)
                year, month, day = solar_date['year'], solar_date['month'], solar_date['day']
            except Exception as e:
                raise ValueError(f'农历转公历失败：{e}')
        return date(year, month, day), hour, minute, _city_to_longitude(row['city'].get())

    def _update_owner_sizhu(self, i):
        """事主四柱/生肖/喜用神实时回显（与主程序 calculate_owner_sizhu 同源）。

        嫁娶专用字段按主程序 L2843-2870 口径：女命（新娘）夫星/子星/阴胎，
        男命（新郎）阳气。任一环节失败仅降级文案并 print，不弹窗打断输入。
        """
        row = self.owner_rows[i]
        try:
            birth_date, hour, minute, lng = self._owner_birth(i)
        except (ValueError, TypeError):
            row['sizhu'].set('未计算')
            for _k in ('zodiac', 'xishen', 'yongshen', 'mar1', 'mar2', 'mar3',
                       'truesolar'):
                row[_k].set('')
            return
        try:
            sz = calculate_sizhu(birth_date, hour, minute, longitude=lng)
        except Exception as e:
            print('事主四柱计算失败（%s）：%s' % (row['name'].get() or i, e))
            row['sizhu'].set('计算失败')
            for _k in ('zodiac', 'xishen', 'yongshen', 'mar1', 'mar2', 'mar3',
                       'truesolar'):
                row[_k].set('')
            return

        _pillars = [str(sz.get(_k) or '') for _k in ('年柱', '月柱', '日柱', '时柱')]
        row['sizhu'].set(' '.join(_pillars))
        row['truesolar'].set('(真太阳时)' if lng != 120.0 else '')
        _zhi = _pillars[0][1:2]
        _zhis = '子丑寅卯辰巳午未申酉戌亥'
        row['zodiac'].set('鼠牛虎兔龙蛇马羊猴鸡狗猪'[_zhis.index(_zhi)]
                          if _zhi in _zhis else '')

        # 喜用神（字段口径同主程序 L2829-2841）
        try:
            from modules.喜用神计算器 import calculate_xishen_yongshen
            _det = {_k: sz.get(_k, '') for _k in
                    ('year_gan', 'year_zhi', 'month_gan', 'month_zhi',
                     'day_gan', 'day_zhi', 'hour_gan', 'hour_zhi')}
            _x, _y = calculate_xishen_yongshen(_det)
            row['xishen'].set(_x or '')
            row['yongshen'].set(_y or '')
        except Exception as e:
            print('事主喜用神计算失败：%s' % e)
            row['xishen'].set('')
            row['yongshen'].set('')

        # 嫁娶专用：夫星/子星/阴胎（女命）、阳气（男命）
        for _k in ('mar1', 'mar2', 'mar3'):
            row[_k].set('')
        try:
            if self.event_var.get() == '嫁娶':
                from modules.工具函数 import get_fuzi, get_yintai, get_yangqi
                if row['gender'].get() == '女':
                    _fz = get_fuzi(sz.get('year_gan', ''), sz.get('year_zhi', ''))
                    row['mar1'].set('夫星：%s' % (_fz.get('fu') or '未知'))
                    row['mar2'].set('子星：%s' % (_fz.get('zi') or '未知'))
                    _mg, _mz = sz.get('month_gan', ''), sz.get('month_zhi', '')
                    if _mg and _mz:
                        row['mar3'].set('阴胎：%s' % (get_yintai(_mg, _mz) or '未知'))
                elif row['gender'].get() == '男':
                    _mg, _mz = sz.get('month_gan', ''), sz.get('month_zhi', '')
                    if _mg and _mz:
                        row['mar1'].set('阳气：%s' % (get_yangqi(_mg, _mz) or '未知'))
        except Exception as e:
            print('事主夫星子星/阴阳胎计算失败：%s' % e)

    def _open_owner_bazi(self, i):
        """事主八字排盘详情（与主程序 show_owner_bazi_detail 同源，含真太阳时）。"""
        try:
            birth_date, hour, minute, lng = self._owner_birth(i)
        except (ValueError, TypeError) as e:
            messagebox.showwarning('提示', '请先填写完整有效的出生年月日：%s' % e)
            return
        try:
            from modules.八字排盘 import BaZiPanPan
            from modules.八字可视化模块 import show_bazi_dialog
            panpan = BaZiPanPan(birth_date.year, birth_date.month, birth_date.day,
                                hour, minute, self.owner_rows[i]['gender'].get(),
                                longitude=lng)
            show_bazi_dialog(self.root, panpan.get_panpan_result())
        except Exception as e:
            messagebox.showerror('八字详情', '打开八字排盘详情失败：%s' % e)

    def _build_action_area(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill=tk.X, padx=10, pady=4)
        ttk.Button(frm, text="开始精准择时（反推 Top-N 榜单）",
                   command=self.open_reverse_panel).pack(side=tk.LEFT, padx=4)
        ttk.Button(frm, text="保存当前参数", command=self._save_config).pack(side=tk.LEFT, padx=4)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="就绪：填写参数后点击「开始精准择时」。")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN,
                  anchor=tk.W, padding=4).pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- 事项联动 ----------
    def _on_event_change(self):
        ev = self.event_var.get()
        # 宅型仅对修造/动土/拆舍/入宅生效（主程序 L1401 口径）
        self.house_combo.configure(state="readonly" if ev in HOUSE_TYPE_EVENTS else "disabled")
        # 山向/兼向仅山家事项生效
        st = "readonly" if ev in SHAN_XIANG_EVENTS else "disabled"
        self.shan_combo.configure(state=st)
        self.jian_combo.configure(state="normal" if ev in SHAN_XIANG_EVENTS else "disabled")
        # 嫁娶族：两位事主角色默认新郎/新娘
        if ev in DUAL_OWNER_EVENTS:
            self.owner_rows[0]['role'].set("新郎")
            self.owner_rows[1]['role'].set("新娘")
        # 事项影响嫁娶专用回显（夫星/子星/阴胎/阳气），随事项刷新
        for _i in range(len(self.owner_rows)):
            self._update_owner_sizhu(_i)
        self.status_var.set(f"当前事项：{ev}")

    # ---------- owners_data / context 组装（严格对齐主程序口径） ----------
    def _collect_owners_data(self):
        """与主程序 _collect_owners_data 同口径：空生日跳过、无效生日回退当月末日、
        真太阳时经度透传 calculate_sizhu(longitude=...)。"""
        owners_data = []
        import calendar
        for row in self.owner_rows:
            try:
                year_str = row['year'].get().strip()
                month_str = row['month'].get().strip()
                day_str = row['day'].get().strip()
                if not (year_str and month_str and day_str):
                    continue
                year = int(year_str)
                month = int(month_str)
                day = int(day_str)
                hour = int(row['hour'].get().strip() or '12')
                minute = int(row['minute'].get().strip() or '0')
                gender = row['gender'].get()
                # 001 §238.17：农历转公历（闰月填负数，如闰五月=-5）
                if self.calendar_type_var.get() == 'lunar':
                    try:
                        converter = get_lunar_converter()
                        solar_date = converter.lunar_to_solar(year, month, day, hour, minute, 0)
                        year, month, day = solar_date['year'], solar_date['month'], solar_date['day']
                    except Exception as e:
                        print(f"事主 {row['name'].get().strip()} 农历转公历失败：{e}")
                        continue
                try:
                    birth_date = date(year, month, day)
                except ValueError:
                    last_day = calendar.monthrange(year, month)[1]
                    birth_date = date(year, month, last_day)
                    messagebox.showwarning(
                        "日期修正",
                        f"您输入的日期 {year}-{month}-{day} 无效，已自动修正为 {year}-{month}-{last_day}")
                birth_longitude = _city_to_longitude(row['city'].get())
                owner_sizhu = calculate_sizhu(birth_date, hour, minute, longitude=birth_longitude)
                owner_data = {
                    'name': row['name'].get().strip(),
                    'role': row['role'].get().strip(),
                    'birth_date': birth_date,
                    'birth_hour': hour,
                    'birth_minute': minute,
                    'birth_longitude': birth_longitude,
                    '性别': gender,
                    '年干': owner_sizhu.get('year_gan', ''),
                    '年支': owner_sizhu.get('year_zhi', ''),
                    '日干': owner_sizhu.get('day_gan', ''),
                    '日支': owner_sizhu.get('day_zhi', ''),
                    '生肖': owner_sizhu.get('year_zhi', ''),
                }
                owners_data.append(owner_data)
            except (ValueError, TypeError):
                continue
        return owners_data

    def _build_context(self):
        """与主程序 open_reverse_panel 同口径：兼向拼接 + zeli_mode='pure'。"""
        _shan = self.shan_xiang_var.get() or ''
        _jx = self.jian_xiang_var.get() or ''
        if _shan and _jx and _jx != '正中':
            if not str(_jx).startswith('兼'):
                _jx = '兼' + str(_jx)
            _shan = f"{_shan}{_jx}"
        ev = self.event_var.get()
        return {
            'house_type': self.house_type_var.get() if ev in HOUSE_TYPE_EVENTS else '',
            'shan_xiang': (_shan or None) if ev in SHAN_XIANG_EVENTS else None,
            'zao_xiang': None,
            'zao_wei': None,
            'chuang_wei': None,
            'zaozhu_mode': None,
            'zeli_mode': 'pure',
        }

    def _focus_params(self):
        """反推窗口「修改事主与山向」回调：把焦点交回参数面板首事主姓名框。"""
        try:
            self.root.deiconify()
            self.root.lift()
            self.owner_rows[0]['name'].focus_set()
        except Exception as e:
            self.status_var.set(f"焦点回退失败：{e}")

    # ---------- 打开反推面板 ----------
    def open_reverse_panel(self):
        try:
            owners = self._collect_owners_data()
            ctx = self._build_context()
            self.reverse_window = open_reverse_window(
                self.root, self.event_var.get(), owners, ctx,
                modify_callback=self._focus_params,
                add_tie_callback=self.add_record_to_zeri_tie,
            )
            self.status_var.set("精准择时面板已打开。修改参数后可再次点击重新反推。")
            self._save_config()
        except Exception as e:
            messagebox.showerror("错误", f"打开精准择时面板失败：{e}")

    # ---------- 择日贴（001 §238.14 P1-c） ----------
    def _update_zeri_tie_btn(self):
        """工具栏择日贴按钮显示暂存课数。"""
        n = len(self._zeri_tie_pending)
        try:
            self.zeeri_tie_btn.configure(text=f"📜 择日贴({n})" if n else "📜 择日贴")
        except Exception as e:
            print('刷新择日贴按钮失败：%s' % e)

    def open_zeri_tie(self):
        """打开（或置顶）择日贴窗口，并灌入暂存日课。"""
        try:
            from modules.择日贴 import show_zeri_tie
            pad = show_zeri_tie(self.root)
            pending = list(self._zeri_tie_pending)
            for entry in pending:
                pad.add_entry(entry)
            self._zeri_tie_pending = []
            self._update_zeri_tie_btn()
        except Exception as e:
            messagebox.showerror('择日贴', f'打开择日贴失败：{e}')

    def _build_tie_owners(self):
        """事主 → 择日贴 owners_list（字段口径同主程序 _parse_owner）。"""
        from modules.工具函数 import get_fuzi, get_yintai, get_yangqi
        _zhis = '子丑寅卯辰巳午未申酉戌亥'
        _sx = '鼠牛虎兔龙蛇马羊猴鸡狗猪'
        out = []
        for i in range(len(self.owner_rows)):
            row = self.owner_rows[i]
            try:
                bd, hh, mm, lng = self._owner_birth(i)
            except (ValueError, TypeError) as e:
                print('事主 %d 出生信息不全，跳过入贴：%s' % (i + 1, e))
                continue
            try:
                sz = calculate_sizhu(bd, hh, mm, longitude=lng)
            except Exception as e:
                print('事主 %d 四柱计算失败，跳过入贴：%s' % (i + 1, e))
                continue
            pillars = [str(sz.get(k) or '') for k in ('年柱', '月柱', '日柱', '时柱')]
            if any(len(p) < 2 for p in pillars):
                print('事主 %d 四柱不完整，跳过入贴' % (i + 1))
                continue
            role = row['role'].get()
            gender = row['gender'].get()
            year_gz = pillars[0][:2]
            o = {
                'name': row['name'].get().strip() or role,
                'role': role,
                'sizhu': ' '.join(pillars),
                'year_gz': year_gz,
                'year_sx': _sx[_zhis.index(year_gz[1])] if year_gz[1] in _zhis else '',
                'year': bd.year, 'month': bd.month, 'day': bd.day,
                'hour': hh, 'minute': mm, 'gender': gender,
            }
            # 婚嫁专用：女命夫星/子星/阴胎，男命阳气（同主程序 L9262-9289）
            if gender == '女' or role in ('新娘', '坤造'):
                fz = get_fuzi(pillars[0][0], pillars[0][1])
                o['fu'] = fz.get('fu', '')
                o['zi'] = fz.get('zi', '')
                o['yintai'] = get_yintai(pillars[1][0], pillars[1][1])
            if gender == '男' or role in ('新郎', '乾造'):
                o['yangqi'] = get_yangqi(pillars[1][0], pillars[1][1])
            out.append(o)
        return out

    def _build_tie_entry(self, record, event_type=None):
        """反推日记录 → 择日贴 entry（字段同主程序 add_result_to_zeri_tie）。"""
        ev = event_type or self.event_var.get()
        date_s = str(record.get('date') or '').strip()
        if not date_s:
            raise ValueError('反推记录缺少日期')
        owners_list = self._build_tie_owners()
        entry = {
            'date': date_s,
            'sizhu': str(record.get('sizhu') or ''),
            'score': record.get('score', ''),
            'level': record.get('level', ''),
            'event_type': ev,
            'owners': '、'.join(o['name'] for o in owners_list if o.get('name')),
            'owners_list': owners_list,
            'jishen': str(record.get('jishen') or ''),
            'reason': str(record.get('reason') or ''),
            'veto_reasons': record.get('veto_reasons') or [],
            'reverse_caution': record.get('kind') == '慎用',
            'action_plan': record.get('action_plan'),
            'day_kind': record.get('kind') or '',
            # 001 §238：五行偏枯预警透传（择日贴警示区，纯提示不改分）
            'wuxing_pian_ku': record.get('pian_ku') or '',
        }
        if ev in {'修造', '拆舍', '作灶', '安床', '动土', '入宅', '安葬'}:
            shan = (self.shan_xiang_var.get() or '').strip()
            jian = (self.jian_xiang_var.get() or '').strip()
            if jian and jian not in ('正中', '-', '—'):
                shan += jian
            entry['shan_xiang'] = shan
            # 分金：同主程序 L9345-9360，现场调用二十四山 selector
            try:
                from modules.二十四山 import ZhengTiWuXingSelectorDB
                parts = entry['sizhu'].split()
                if len(parts) == 4 and shan:
                    mn = shan[:shan.index('山')] if '山' in shan else shan[:1]
                    fj = ZhengTiWuXingSelectorDB().evaluate_with_fengjin(
                        mn, jian or '正中', parts[0], parts[1], parts[2], parts[3])
                    if isinstance(fj, dict):
                        entry['fenjin'] = str(fj.get('fengjin_ganzhi') or '')
            except Exception as e:
                print('分金计算失败（不影响入贴）：%s' % e)
        return entry

    def add_record_to_zeri_tie(self, record, event_type=None):
        """反推面板右键「加入择日贴」/「生成红纸帖」回调（签名同主程序 §210）。"""
        try:
            entry = self._build_tie_entry(record, event_type)
        except Exception as e:
            messagebox.showerror('择日贴', f'构造日课失败：{e}')
            return
        win = getattr(self.root, '_zeri_tie_window', None)
        if win is not None:
            try:
                if win.window.winfo_exists():
                    win.add_entry(entry)
                    self.status_var.set(
                        '已加入择日贴：%s %s' % (entry['date'], entry['event_type']))
                    return
            except Exception as e:
                print('加入已开择日贴失败，转暂存重开：%s' % e)
        self._zeri_tie_pending.append(entry)
        self._update_zeri_tie_btn()
        self.open_zeri_tie()

    # ---------- 扩展工具 ----------
    def _open_compass(self):
        """电子罗盘：选择山向后回写参数区，并按度数自动识别兼向（口径同主程序 L3000-3023）。"""
        try:
            from modules.电子罗盘 import show_compass_dialog, CompassConverter

            def on_compass_select(shan_xiang, degree):
                if shan_xiang:
                    self.shan_xiang_var.set(shan_xiang)
                    converter = CompassConverter()
                    mountain = shan_xiang_to_shan(shan_xiang)
                    jianxiang = converter.get_jianxiang(mountain, degree)
                    self.jian_xiang_var.set(jianxiang if jianxiang else "正中")

            show_compass_dialog(self.root, self.shan_xiang_var.get() or None, on_compass_select)
        except Exception as e:
            messagebox.showerror("电子罗盘", f"打开电子罗盘失败：{e}")

    def _open_today_huangli(self):
        try:
            from modules.今日黄历 import show_today_huangli
            show_today_huangli(self.root)
        except Exception as e:
            messagebox.showerror("今日黄历", f"打开今日黄历失败：{e}")

    def _open_bazi(self):
        try:
            from modules.八字可视化模块 import show_bazi_input_dialog
            show_bazi_input_dialog(self.root)
        except Exception as e:
            messagebox.showerror("八字排盘", f"打开八字排盘失败：{e}")

    def _open_xuankong(self):
        """玄空飞星排盘：自动带入当前山向/兼向（口径同主程序 open_xuankong）。"""
        try:
            import datetime as _dt
            import importlib
            xk_mod = importlib.import_module('玄空飞星_日课展示')
            today = _dt.date.today()
            mountain = None
            sx_v = self.shan_xiang_var.get() or ''
            if sx_v and '山' in sx_v:
                mountain = sx_v.split('山')[0].strip()
            jianxiang = '正向'
            jx_v = self.jian_xiang_var.get() or ''
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
            preset = {'year': today.year, 'month': today.month, 'day': today.day,
                      'hour': 12, 'minute': 0,
                      'mountain': mountain, 'jianxiang': jianxiang}
            win = tk.Toplevel(self.root)
            xk_mod.XuanKongApp(win, preset=preset)
        except Exception as e:
            messagebox.showerror("玄空飞星", f"打开玄空飞星失败：{e}")

    # ---------- 配置持久化（独立文件，与主程序隔离） ----------
    def _save_config(self):
        try:
            data = {
                'event': self.event_var.get(),
                'house_type': self.house_type_var.get(),
                'shan_xiang': self.shan_xiang_var.get(),
                'jian_xiang': self.jian_xiang_var.get(),
                'calendar_type': self.calendar_type_var.get(),  # 001 §238.17
                'owners': [{
                    'role': r['role'].get(), 'name': r['name'].get(),
                    'gender': r['gender'].get(),
                    'year': r['year'].get(), 'month': r['month'].get(),
                    'day': r['day'].get(), 'hour': r['hour'].get(),
                    'minute': r['minute'].get(), 'city': r['city'].get(),
                } for r in self.owner_rows],
            }
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"参数已保存：{CONFIG_PATH}")
        except Exception as e:
            messagebox.showwarning("配置保存", f"保存配置失败：{e}")

    def _load_config(self):
        try:
            if not os.path.exists(CONFIG_PATH):
                return
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('event') in UI_EVENTS:
                self.event_var.set(data['event'])
            if data.get('house_type'):
                self.house_type_var.set(data['house_type'])
            if data.get('shan_xiang'):
                self.shan_xiang_var.set(data['shan_xiang'])
            if data.get('jian_xiang'):
                self.jian_xiang_var.set(data['jian_xiang'])
            if data.get('calendar_type') in ('solar', 'lunar'):   # 001 §238.17
                self.calendar_type_var.set(data['calendar_type'])
            for row, saved in zip(self.owner_rows, data.get('owners', [])):
                for key, widget in row.items():
                    val = saved.get(key)
                    if val is None:
                        continue
                    if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                        widget.delete(0, tk.END)
                        widget.insert(0, str(val))
            # 001 §238.19：配置回填后立即刷新四柱/喜用神回显，
            # 不必等用户点击输入框触发 FocusOut
            for _i in range(len(self.owner_rows)):
                self._update_owner_sizhu(_i)
        except Exception as e:
            self.status_var.set(f"读取配置失败（已忽略）：{e}")

    def _on_close(self):
        self._save_config()
        self.root.destroy()


def main():
    root = tk.Tk()
    精准择时版App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
