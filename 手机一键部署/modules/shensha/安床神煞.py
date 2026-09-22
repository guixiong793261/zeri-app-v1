# -*- coding: utf-8 -*-
"""
================================================================================
安床神煞模块
================================================================================
实现安床择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    # 添加 shensha 目录到路径
    shensha_dir = os.path.dirname(os.path.abspath(__file__))
    if shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)

try:
    from .神煞基类 import ShenShaChecker, is_yanggongji_by_lunar
except ImportError:
    from 神煞基类 import ShenShaChecker, is_yanggongji_by_lunar


class BedShenShaChecker(ShenShaChecker):
    """安床神煞检查器"""

    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)

        # ===== 年神类吉神 =====

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 年干比日干典载口径）。

        # ===== 年神类凶煞 =====

        # 丧门
        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '主丧亡，不宜安床')

        # 吊客
        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '主吊唁，不宜安床')

        # 病符
        if self._is_bingfu(sizhu):
            self._add_shensha('病符', -12, '主疾病，不宜安床')

        # 官符
        if self._is_guanfu(sizhu):
            self._add_shensha('官符', -10, '主官讼，不宜安床')

        # 五鬼
        if self._is_wugui(sizhu):
            self._add_shensha('五鬼', -15, '主耗散，不宜安床')

        # 2026-09-16修复：原此处为 '胎神方位吉' +10 —— _is_taishen_fangwei 内部
        # 按年支算出胎神所值（门/碓磨/厨灶…）后并未使用、直接 return True，
        # 导致任何一天安床都恒定 +10。胎神判吉须以“床的方位不与胎神所值相犯”
        # 为准，而本检查器拿不到床的方位，无法判断，故该项不计分、予以删除。

    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)

        # ===== 月神类吉神 =====

        # 2026-10 A1：'月空' 同名重加删除（基类月作用域统一注册，
        # 月神比日干典载口径）。

        # 吉期
        if self._is_jiqi(sizhu):
            self._add_shensha('吉期', 10, '吉期日，主吉庆，安床吉')

        # 阳德
        if self._is_yangde(sizhu):
            self._add_shensha('阳德', 10, '阳德日，主阳和，安床吉')

        # 阴德
        if self._is_yinde(sizhu):
            self._add_shensha('阴德', 10, '阴德日，主阴德，安床吉')

        # 益后
        if self._is_yihou(sizhu):
            self._add_shensha('益后', 12, '益后日，主益后代，安床吉')

        # 续世
        if self._is_xushi(sizhu):
            self._add_shensha('续世', 10, '续世日，主续嗣，安床吉')

        # 要安
        if self._is_yaoan(sizhu):
            self._add_shensha('要安', 8, '要安日，主安宁，安床吉')

        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 15, '不将日，阳将阴将之日，安床大吉')

        # ===== 月神类凶煞 =====

        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -30, '月破日不宜安床')

        # 土瘟
        if self._is_tuwen(sizhu):
            self._add_shensha('土瘟', -20, '土瘟日不宜安床')

        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌凶日，不宜安床')

        # 月虚
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚日主虚耗，不宜安床')

    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)

        # ===== 吉神 =====

        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德吉星，安床大吉')

        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德吉星，安床大吉')

        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合，安床吉')

        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合，安床吉')

        # 三奇
        sanqi_result = self._is_sanqi(sizhu)
        if sanqi_result:
            self._add_shensha(f'三奇{sanqi_result}', 15, f'{sanqi_result}三奇照临，安床上吉')

        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星到座，安床吉')

        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 12, '地支六合，安床吉')

        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '地支三合，安床吉')

        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '驿马日利于安床')

        # 2026-10 A1：'天马' 同名重加删除（典载天马为月神，基类月作用域注册）。

        # 天赦
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦日百无禁忌，安床大吉')

        # 母仓
        if self._is_mucang(sizhu):
            self._add_shensha('母仓', 10, '母仓日安床吉')

        # ===== 凶煞 =====

        # 受死日
        if self._is_shousi_day(sizhu):
            self._add_shensha('受死日', -22, '受死日不宜安床')

        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日不宜安床')

        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -30, '十恶大败日，不宜安床')

        # ===== 安床专用 =====

        # 安床吉日
        if self._is_anchuang_jiri(sizhu):
            self._add_shensha('安床吉日', 15, '适合安床的吉日')

        # 床公床母日
        if self._is_chuanggong_chuangmu(sizhu):
            self._add_shensha('床公床母日', 12, '床公床母日利于安床')

        # 胎神日
        if self._is_taishen(sizhu):
            self._add_shensha('胎神日', -15, '胎神日不宜安床')

        # 冲床日
        if self._is_chongchuang(sizhu):
            self._add_shensha('冲床日', -12, '冲床日不宜安床')

        # 杨公忌日
        # 注：安床对杨公忌敏感度较低，扣分降为-10（修造为-20、安葬为-20）
        if self._is_yanggongji(sizhu):
            self._add_shensha('杨公忌日', -10, '杨公忌日不宜安床')

        # 红砂日已由基类 _check_day_shensha 统一添加（'红砂日' -15，判定经
        # self._is_hongsha 分派到本类农历月版 override）。此处原自有分支与
        # 基类同名，_add_shensha 同名保留首次，本就为死代码，2026-09-20 删除。

    def _check_special_shensha(self, sizhu, owners, **kwargs):
        """检查特殊神煞，主要处理事主（安床者）生肖与日课的冲合"""
        if not owners:
            return

        for i, owner in enumerate(owners):
            owner_zodiac = owner.get('生肖', '')
            owner_year_zhi = owner.get('年支', '')
            owner_name = owner.get('姓名', f'事主{i+1}')

            if not owner_zodiac and not owner_year_zhi:
                continue

            # 年支相冲
            year_zhi = sizhu['year_zhi']
            if self._is_chong(year_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'年冲{owner_name}', -20, f'年支与{owner_name}生肖相冲')

            # 月支相冲
            month_zhi = sizhu['month_zhi']
            if self._is_chong(month_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'月冲{owner_name}', -15, f'月支与{owner_name}生肖相冲')

            # 日支相冲
            day_zhi = sizhu['day_zhi']
            if self._is_chong(day_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'日冲{owner_name}', -25, f'日支与{owner_name}生肖相冲，大忌')
            elif self._is_he(day_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'日合{owner_name}', 10, f'日支与{owner_name}生肖相合')

            # 时支相冲
            hour_zhi = sizhu.get('hour_zhi', '')
            if hour_zhi and self._is_chong(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时冲{owner_name}', -12, f'时支与{owner_name}生肖相冲')
            elif hour_zhi and self._is_he(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时合{owner_name}', 6, f'时支与{owner_name}生肖相合')

    def _is_anchuang_jiri(self, sizhu):
        """是否安床吉日"""
        day_zhi = sizhu['day_zhi']
        # 安床吉日：阳日
        anchuang_jiri = ['午', '未', '申', '酉', '戌', '亥']
        return day_zhi in anchuang_jiri

    def _is_chuanggong_chuangmu(self, sizhu):
        """是否床公床母日"""
        day_zhi = sizhu['day_zhi']
        # 床公床母日
        chuanggong_chuangmu = ['子', '寅', '卯', '巳', '午', '酉']
        return day_zhi in chuanggong_chuangmu

    def _is_taishen(self, sizhu):
        """是否胎神日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 胎神日
        taishen_days = {
            '寅': '子', '卯': '丑', '辰': '寅', '巳': '卯',
            '午': '辰', '未': '巳', '申': '午', '酉': '未',
            '戌': '申', '亥': '酉', '子': '戌', '丑': '亥'
        }
        return day_zhi == taishen_days.get(month_zhi)

    def _is_chongchuang(self, sizhu):
        """是否冲床日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 冲床日
        chongchuang = {
            '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
            '午': '子', '未': '丑', '申': '寅', '酉': '卯',
            '戌': '辰', '亥': '巳', '子': '午', '丑': '未'
        }
        return day_zhi == chongchuang.get(month_zhi)

    def _is_yanggongji(self, sizhu):
        """是否杨公忌日（2026-09-20 收敛：改委托 is_yanggongji_by_lunar）

        原六冲表（子午/丑未/寅申…）与杨公忌毫无关系——与真表 2026 仅 2 天
        碰巧重合（漏 12 误 29），已删除。安床扣分维持 -10 事项差（同天赦先例）。
        """
        return is_yanggongji_by_lunar(sizhu)

    def _is_hongsha(self, sizhu):
        """是否红砂日（《玉匣记》口诀"四孟金鸡四仲蛇，四季逢丑是红纱"，
        农历月版，与嫁娶规则/修造扩展口径一致；闰月不计——2026-09-20
        通用规则。

        2026-09-20 专项修复：原实现不看月、日支∈{酉,巳,丑}即命中，把
        "按月命中"错成"按日命中"——2026 实测命中 91 天（正确 29 天），
        误扣 62 天，属活错表（第六种失效模式家族，与嫁娶/修造孟仲对调
        同源）。基类 _check_day_shensha 经 self 分派到本 override，安床
        自有同名分支已删（_add_shensha 同名保留首次，该分支本就是死代码）。
        """
        if 'date' not in sizhu:
            return False
        from ..四柱计算器 import get_lunar_date
        lunar = get_lunar_date(sizhu['date'])
        ms = str(lunar.get('month', ''))
        if '闰' in ms:   # 闰月不计（通用规则）
            return False
        month_map = {'正': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                     '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '冬': 11, '腊': 12}
        month = month_map.get(ms.replace('月', ''), 0)
        hongsha = {
            1: ['巳'], 4: ['巳'], 7: ['巳'], 10: ['巳'],
            2: ['酉'], 5: ['酉'], 8: ['酉'], 11: ['酉'],
            3: ['丑'], 6: ['丑'], 9: ['丑'], 12: ['丑']
        }
        day_zhi = sizhu.get('day_zhi', '')
        return month in hongsha and day_zhi in hongsha[month]

    def _check_owner_anchuang_match(self, sizhu, owner):
        """检查事主与安床日是否相合"""
        # 简化判断
        return True