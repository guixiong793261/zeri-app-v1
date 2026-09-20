# -*- coding: utf-8 -*-
"""
胎神查询模块（准确版）
月胎神按通书「逐月胎神占」以农历月查表（闰月随本月），
日胎神以六十甲子查表，太岁方位按年支四正四维（与汉程黄历对齐）
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from .四柱计算器 import get_lunar_date, calculate_sizhu

# 尝试导入 sxtwl 进行精确节气判断
try:
    import sxtwl
    HAS_SXTWL = True
except ImportError:
    HAS_SXTWL = False


# ---------- 月胎神占位（通书「逐月胎神占」按农历月，闰月随本月） ----------
MONTH_TAISHEN = {
    1: "占房床",
    2: "占户窗",
    3: "占门堂",
    4: "占厨灶",
    5: "占房床",
    6: "占床仓",
    7: "占碓磨",
    8: "占厕户",
    9: "占门房",
    10: "占房床",
    11: "占灶炉",
    12: "占房床"
}

# 太岁方位（按年支四正四维；如丙午年=正南，与汉程黄历一致）
TAISUI_FANG = {
    '子': '正北', '丑': '东北', '寅': '东北', '卯': '正东',
    '辰': '东南', '巳': '东南', '午': '正南', '未': '西南',
    '申': '西南', '酉': '正西', '戌': '西北', '亥': '西北'
}


# ---------- 日胎神占位（六十甲子完整表，与汉程黄历一致） ----------
DAY_TAISHEN = {
    "甲子": "占门碓外东南", "乙丑": "碓磨厕外东南", "丙寅": "厨灶炉外正南", "丁卯": "仓库门外正南",
    "戊辰": "房床栖外正南", "己巳": "占门床外正南", "庚午": "占碓磨外正南", "辛未": "厨灶厕外西南",
    "壬申": "仓库炉外西南", "癸酉": "房床门外西南", "甲戌": "占门栖外西南", "乙亥": "碓磨床外西南",
    "丙子": "厨灶碓外西南", "丁丑": "仓库厕外正西", "戊寅": "房床炉外正西", "己卯": "占大门外正西",
    "庚辰": "碓磨栖外正西", "辛巳": "厨灶床外正西", "壬午": "仓库碓外西北", "癸未": "房床厕外西北",
    "甲申": "占门炉外西北", "乙酉": "碓磨门外西北", "丙戌": "厨灶栖外西北", "丁亥": "仓库床外西北",
    "戊子": "房床碓外正北", "己丑": "占门厕外正北", "庚寅": "碓磨炉外正北", "辛卯": "厨灶门外正北",
    "壬辰": "仓库栖外正北", "癸巳": "占房床房内北", "甲午": "占门碓房内北", "乙未": "碓磨厕房内北",
    "丙申": "厨灶炉房内北", "丁酉": "仓库门房内北", "戊戌": "房床栖房内中", "己亥": "占门床房内中",
    "庚子": "占碓磨房内南", "辛丑": "厨灶厕房内南", "壬寅": "仓库炉房内南", "癸卯": "房床门房内西",
    "甲辰": "占门栖房内东", "乙巳": "碓磨床房内东", "丙午": "厨灶碓房内东", "丁未": "仓库厕房内东",
    "戊申": "房床炉房内中", "己酉": "占大门外东北", "庚戌": "碓磨栖外东北", "辛亥": "厨灶床外东北",
    "壬子": "仓库碓外东北", "癸丑": "房床厕外东北", "甲寅": "占门炉外东北", "乙卯": "碓磨门外正东",
    "丙辰": "厨灶栖外正东", "丁巳": "仓库床外正东", "戊午": "房床碓外正东", "己未": "占门厕外正东",
    "庚申": "碓磨炉外东南", "辛酉": "厨灶门外东南", "壬戌": "仓库栖外东南", "癸亥": "占房床外东南"
}

def get_lunar_month_with_jieqi(year, month, day):
    """
    根据节气判断当前所属农历月（返回1-12）
    若在立春前，返回12（丑月）；若在立春后，按节气顺序推算
    """
    if not HAS_SXTWL:
        # 若 sxtwl 不可用，用近似法：2月4日左右为立春
        if month < 2 or (month == 2 and day < 4):
            return 12  # 上一年腊月（丑月）
        # 其他月份按农历月近似（粗略）
        lunar = get_lunar_date(date(year, month, day))
        return lunar['month']

    try:
        jq_list = sxtwl.getJieQiByYear(year)
        # 节气名称：立春、惊蛰、清明、立夏、芒种、小暑、
        # 立秋、白露、寒露、立冬、大雪、小寒
        # 对应月支：寅、卯、辰、巳、午、未、申、酉、戌、亥、子、丑
        # sxtwl 索引：0立春,2惊蛰,4清明,6立夏,8芒种,10小暑,
        #            12立秋,14白露,16寒露,18立冬,20大雪,22小寒

        jie_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
        jie_to_month = {0: 1, 2: 2, 4: 3, 6: 4, 8: 5, 10: 6,
                        12: 7, 14: 8, 16: 9, 18: 10, 20: 11, 22: 12}

        # 获取当前时间的时间戳（天）
        from datetime import datetime as dt
        current = dt(year, month, day)

        # 检查是否在立春之前
        lichun_jd = jq_list[0].jd
        lichun_dd = sxtwl.JD2DD(lichun_jd)
        lichun = dt(int(lichun_dd.Y), int(lichun_dd.M), int(lichun_dd.D),
                    int(lichun_dd.h), int(lichun_dd.m), int(lichun_dd.s))

        if current < lichun:
            return 12  # 腊月（丑月）

        # 逐个检查节气
        for idx in jie_indices:
            jd = jq_list[idx].jd
            dd = sxtwl.JD2DD(jd)
            jie_dt = dt(int(dd.Y), int(dd.M), int(dd.D),
                        int(dd.h), int(dd.m), int(dd.s))
            if current < jie_dt:
                # 当前在此节气之前，属于上一个节气的月份
                prev_idx = jie_indices[jie_indices.index(idx) - 1] if jie_indices.index(idx) > 0 else jie_indices[-1]
                return jie_to_month.get(prev_idx, 1)
        # 在所有节气之后（小寒之后），属于子月或丑月
        return 12

    except Exception as e:
        # 出错时回退到农历月
        lunar = get_lunar_date(date(year, month, day))
        return lunar['month']


class TaishenQueryDialog:
    """胎神查询对话框（准确版）"""

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("胎神查询（准确版）")
        self.window.geometry("520x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        # 日期输入
        frame_input = ttk.Frame(self.window, padding="10")
        frame_input.pack(fill=tk.X)

        ttk.Label(frame_input, text="请输入公历日期：").pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        entry_date = ttk.Entry(frame_input, textvariable=self.date_var, width=15)
        entry_date.pack(side=tk.LEFT, padx=8)

        btn_query = ttk.Button(frame_input, text="查询", command=self.query)
        btn_query.pack(side=tk.LEFT, padx=5)
        btn_today = ttk.Button(frame_input, text="今天", command=self.set_today)
        btn_today.pack(side=tk.LEFT, padx=5)

        # 结果显示
        frame_result = ttk.Frame(self.window, padding="10")
        frame_result.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(frame_result, wrap=tk.WORD, font=("微软雅黑", 11), height=14)
        scrollbar = ttk.Scrollbar(frame_result, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定回车键
        entry_date.bind("<Return>", lambda e: self.query())

        # 初始查询今天
        self.query()

    def set_today(self):
        """设置日期为今天"""
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.query()

    def query(self):
        """执行查询"""
        date_str = self.date_var.get().strip()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")
            return

        # 获取农历
        try:
            lunar = get_lunar_date(dt)
            lunar_month = lunar['month']
            lunar_day = lunar['day']
            lunar_year = lunar['year']
            # get_lunar_date 的 month 已含闰前缀与"月"字（'六月'/'闰六月'），无 is_leap 键；
            # 闰标记由源串自含，不再走恒 False 的 .get('is_leap') 死分支。
            lunar_str = f"{lunar_year}年{lunar_month}{lunar_day}日"
        except Exception as e:
            messagebox.showerror("错误", f"农历转换失败：{e}")
            return

        # 计算日柱
        try:
            sizhu = calculate_sizhu(dt, 12, 0)
            day_pillar = sizhu.get('日柱', '')
            if not day_pillar:
                day_gan = sizhu.get('day_gan', '')
                day_zhi = sizhu.get('day_zhi', '')
                if day_gan and day_zhi:
                    day_pillar = day_gan + day_zhi
                else:
                    day_pillar = ''
        except Exception:
            day_pillar = ''

        # 月胎神：通书「逐月胎神占」按农历月查表（闰月随本月，禁用节气月）
        _CN_MONTH = {'正': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
                     '七': 7, '八': 8, '九': 9, '十': 10, '冬': 11, '腊': 12}
        m_key = str(lunar_month).replace('月', '').replace('闰', '')
        true_month = _CN_MONTH.get(m_key) or (lunar_month if isinstance(lunar_month, int) else None)
        month_taishen = MONTH_TAISHEN.get(true_month, "未知")

        # 日胎神（六十甲子完整表）
        day_taishen = DAY_TAISHEN.get(day_pillar, "（无对应占位）") if day_pillar else "（日柱未知）"

        # 太岁方位（按年支四正四维）
        nian_zhu = ''
        try:
            nian_zhu = sizhu.get('年柱', '') or ''
        except Exception:
            nian_zhu = ''
        year_zhi = nian_zhu[1] if len(nian_zhu) > 1 else ''
        taisui_fang = TAISUI_FANG.get(year_zhi, "未知")

        # 构造显示文本
        result = "=" * 40 + "\n"
        result += f"  【公历】{dt.strftime('%Y年%m月%d日')}\n"
        result += f"  【农历】{lunar_str}\n"
        result += f"  【日柱】{day_pillar if day_pillar else '未计算'}\n"
        result += "=" * 40 + "\n\n"
        result += f"★ 本月胎神（通书逐月胎神占，农历{lunar_month}）：{month_taishen}\n"
        result += f"★ 今日胎神（{day_pillar}日·六十甲子）：{day_taishen}\n"
        result += f"★ 太岁方位（{nian_zhu if nian_zhu else '当年'}年）：{taisui_fang}\n\n"
        result += "─" * 40 + "\n"
        result += "【说明】\n"
        result += "• 月胎神按通书逐月胎神占以农历月查表（闰月随本月）\n"
        result += "• 日胎神按六十甲子日查表，与汉程黄历口径一致\n"
        result += "• 太岁方位按流年年支四正四维标示\n"
        result += "• 胎神占位为传统择日参考，请结合全局判断"

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)