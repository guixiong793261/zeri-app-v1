# -*- coding: utf-8 -*-
"""
================================================================================
修造神煞扩展模块
================================================================================
实现修造择日的完整功能，包括：
1. 太阳太阴到山到向计算
2. 扶山、相主、补龙核心逻辑
3. 山家专属吉神判断（三合、六合、禄、贵）
4. 补充缺失的凶煞（杨公忌、三娘煞、红纱煞、重丧日等）
5. 建除十二神判断
6. 时辰吉凶判断

使用方法:
    from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
================================================================================
"""

import sys
import os
from datetime import date, datetime

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    modules_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    shensha_dir = os.path.dirname(os.path.abspath(__file__))
    if shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)

try:
    from .修造神煞 import ConstructionShenShaChecker
    from .神煞基类 import (is_yanggongji_by_lunar, is_zhongsang_by_lunar,
                           get_sun_moon_mountains, get_xiangshan_24)
    from .时辰系 import (
        WUSHU_DUN,
        get_gui_ren_shichen as _ss_gui_ren,
        get_lu_shichen as _ss_lu,
        is_wubuyu as _ss_wubuyu,
    )
    from ..工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE
    from ..二十四山 import ZhengTiWuXingSelectorDB
except ImportError:
    from 修造神煞 import ConstructionShenShaChecker
    from 神煞基类 import is_yanggongji_by_lunar, get_sun_moon_mountains, get_xiangshan_24
    from 时辰系 import (
        WUSHU_DUN,
        get_gui_ren_shichen as _ss_gui_ren,
        get_lu_shichen as _ss_lu,
        is_wubuyu as _ss_wubuyu,
    )
    from 工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE
    from 二十四山 import ZhengTiWuXingSelectorDB


class ConstructionShenShaCheckerExt(ConstructionShenShaChecker):
    """修建神煞检查器扩展版 - 完整的修造择日功能"""
    
    def __init__(self, zuoshan=None, zhuming=None, direction=None):
        """
        初始化
        
        Args:
            zuoshan: 坐山（二十四山之一，如'子山午向'中的'子'）
            zhuming: 主命年柱（如'甲子'）
            direction: 动土方位（如'子'、'午'、'丑'等）
        """
        super().__init__()
        self.zuoshan = zuoshan  # 坐山
        self.zhuming = zhuming  # 主命
        self.direction = direction  # 动土方位
        
        # 二十四山列表
        self.shan_list = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                         '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
        
        # 天干禄位（禄神）
        self.lu_shen = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '子'
        }
        
        # 天干贵人（阳贵、阴贵）
        self.gui_ren = {
            '甲': {'阳': '丑', '阴': '未'},
            '乙': {'阳': '子', '阴': '申'},
            '丙': {'阳': '亥', '阴': '酉'},
            '丁': {'阳': '亥', '阴': '酉'},
            '戊': {'阳': '丑', '阴': '未'},
            '己': {'阳': '子', '阴': '申'},
            '庚': {'阳': '丑', '阴': '未'},
            '辛': {'阳': '寅', '阴': '午'},
            '壬': {'阳': '卯', '阴': '巳'},
            '癸': {'阳': '卯', '阴': '巳'}
        }
        
        # 太阳/太阴到山表已收敛至 神煞基类.TAIYANG_DAOSHAN_24SHAN
        # （2026-09-22 B3 修复：sxtwl 节气口径单点出口 get_sun_moon_mountains；
        # 原实例表 taiyang_daoshan/taiyin_daoshan 表值正确但取数死链恒不命中）

        # 杨公忌日表已收敛至 神煞基类._YANGGONGJI_LUNAR（2026-09-20，
        # 农历月日唯一口径、闰月不计），判定统一走 is_yanggongji_by_lunar

        # 真三娘煞日：农历日+干支日双条件见 _is_sanniangsha

        # 红纱日：2026-10-15 D3 删除 self.hongsha 与 override _is_hongsha，
        # 统一继承基类节气月支版（与黄沙口径一致）。
        
        # 建除十二神
        self.jianchu = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
        
        # 山家五行
        self.shan_wuxing = {
            '壬': '水', '子': '水', '癸': '水',
            '丑': '土', '艮': '土', '寅': '木',
            '甲': '木', '卯': '木', '乙': '木',
            '辰': '土', '巽': '木', '巳': '火',
            '丙': '火', '午': '火', '丁': '火',
            '未': '土', '坤': '土', '申': '金',
            '庚': '金', '酉': '金', '辛': '金',
            '戌': '土', '乾': '金', '亥': '水'
        }
    
    def check(self, sizhu, owners=None, zuoshan=None, zhuming=None, direction=None):
        """
        检查修造神煞（完整版）
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            zuoshan: 坐山（可选，覆盖初始化时的设置）
            zhuming: 主命（可选，覆盖初始化时的设置）
            direction: 动土方位（可选，覆盖初始化时的设置）
        """
        # 更新坐山、主命和动土方位
        if zuoshan:
            self.zuoshan = zuoshan
        if zhuming:
            self.zhuming = zhuming
        if direction:
            self.direction = direction
        
        # 标准化sizhu格式（支持中文键名和英文键名两种格式）
        sizhu = self._normalize_sizhu(sizhu)
        
        # 调用基类检查
        super().check(sizhu, owners)
        
        # 补充缺失的凶煞
        self._check_additional_shensha(sizhu)
        
        # 建除十二神
        self._check_jianchu(sizhu)
        
        # 时辰吉凶
        self._check_hour_shensha_ext(sizhu)
        
        # 山家专属吉神（如果有坐山）
        if self.zuoshan:
            self._check_shanjia_jishen(sizhu)
        
        # 动土方位检查
        self._check_direction_shensha(sizhu)
        
        # 太阳太阴到山到向
        self._check_taiyang_taiyin(sizhu)
        
        # 扶山、相主、补龙
        self._check_fushan_xiangzhu_bulong(sizhu)
        
        return self.shensha_list
    
    # ===== 补充凶煞 =====
    
    def _check_additional_shensha(self, sizhu):
        """检查补充的凶煞"""
        # 杨公忌日已由基类 _check_day_shensha 统一添加（'杨公忌日' -20，
        # 判定走 is_yanggongji_by_lunar）。此处原独立分支 '杨公忌' 与基类
        # 条目不同名不去重，2026-09-20 收敛后会双重扣分，已删除。

        # 真三娘煞
        if self._is_sanniangsha(sizhu):
            self._add_shensha('真三娘煞', -15, '真三娘煞日忌婚嫁、修建')

        # 红纱日已由基类 _check_day_shensha 统一添加（'红砂日' -15，判定走
        # 本类 override 的农历月版 _is_hongsha）。此处原独立分支 '红纱日' 与
        # 基类条目不同名不去重，2026-09-20 红纱死链修复后会双重扣分，已删除
        # （与杨公忌日收敛同款机制）。

        # 重丧日 - 修造需参看，非首要禁忌
        if self._is_zhongsang(sizhu):
            self._add_shensha('重丧日', -10, '重丧日，修造需参看，非首要禁忌')
        
        # 重复日 - 忌凶事，利吉事
        if self._is_chongfu(sizhu):
            self._add_shensha('重复日', -10, '重复日，忌凶事，利吉事')
    
    def _is_yanggongji(self, sizhu):
        """是否杨公忌日（2026-09-20 修复第五种失效模式：字段名隐性死链）

        原实现取 get_lunar_date() 返回值中不存在的 'month_num'/'day_num' 键
        （实际返回中文键 'month'/'day'），.get 默认 0 → 静默 False → 全年 0 命中。
        现改委托 神煞基类.is_yanggongji_by_lunar（sxtwl 直取农历数字月日）。
        """
        return is_yanggongji_by_lunar(sizhu)
    
    def _is_sanniangsha(self, sizhu):
        """是否真三娘煞日：农历日与日干支同时满足（全年仅6天）

        初三逢庚午、初七逢辛未、十三逢戊申、十八逢己酉、廿二逢丙午、廿七逢丁未；
        仅农历日相符的"假三娘煞"不再作为禁忌。
        口径依据软件现行共识（嫁娶规则/嫁娶神煞/婚嫁评分算法/本扩展四处表一字
        不差，非《协纪》正式条目）；闰月不计（通用规则，与杨公忌口径一致）。
        2026-09-20 修复第五种失效模式：原实现取 get_lunar_date() 中不存在的
        'day_num' 键（实际返回中文键 'day'，如'初三'），.get 默认 0 → 静默
        False → 全年 0 命中。
        """
        if 'date' not in sizhu:
            return False
        from ..四柱计算器 import get_lunar_date
        lunar = get_lunar_date(sizhu['date'])
        ms = str(lunar.get('month', ''))
        if '闰' in ms:   # 闰月不计（通用规则，与杨公忌口径一致）
            return False
        day_map = {'初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
                   '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
                   '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
                   '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
                   '廿一': 21, '廿二': 22, '廿三': 23, '廿四': 24, '廿五': 25,
                   '廿六': 26, '廿七': 27, '廿八': 28, '廿九': 29, '三十': 30}
        day = day_map.get(str(lunar.get('day', '')), 0)
        zhen_map = {3: '庚午', 7: '辛未', 13: '戊申', 18: '己酉', 22: '丙午', 27: '丁未'}
        if day in zhen_map:
            ganzhi = sizhu.get('day_gan', '') + sizhu.get('day_zhi', '')
            return ganzhi == zhen_map[day]
        return False
    
    def _is_zhongsang(self, sizhu):
        """是否重丧日（农历月查日干）

        001 §195 Commit2（2026-10-28 拍板）：废弃本类原有的**第三套实现**
        （节令月支查日干，2026 年命中 68 天），统一委托神煞基类单点出口
        is_zhongsang_by_lunar（农历月查日干，2026 年命中 32 天），与嫁娶神煞、
        婚嫁评分算法同源。原实现与单点出口 2026 年分歧 58 天。

        原实现另有一处死 Bug：zhongsang_map 中 '戌' 键重复（'四月丙壬' 与
        '九月戊己' 共用 戌），Python 后值覆盖前值 → 戌月按戊己判，
        「四十丙壬方」的十月支被吃掉。统一到单点出口后，该分支语义由
        单点出口表的「四月丙／十月壬」承接，重复键随表一并废除。
        """
        d = sizhu.get('date')
        if not isinstance(d, date):
            try:
                d = date(int(sizhu.get('year')), int(sizhu.get('month')),
                         int(sizhu.get('day')))
            except (TypeError, ValueError):
                return False
        return is_zhongsang_by_lunar(d)
    
    def _is_chongfu(self, sizhu):
        """是否重复日
        重复日：巳日、亥日
        """
        day_zhi = sizhu['day_zhi']
        return day_zhi in ['巳', '亥']
    
    # ===== 建除十二神 =====
    
    def _check_jianchu(self, sizhu):
        """检查建除十二神（批次 1：星名委托 modules/建除.py）"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        # 批次 1（001 §161）：星名统一由 modules/建除.py 计算；
        # 四档分值属批次 2 口径，本批原样保留。
        try:
            from ..建除 import star as _jianchu_star
        except ImportError:
            from 建除 import star as _jianchu_star

        try:
            jianchu_value = _jianchu_star(month_zhi, day_zhi)
            
            # 修造宜用：除、定、执、成、开
            # 修造忌用：建、破、平、收、闭
            if jianchu_value in ['除', '定', '执', '成', '开']:
                self._add_shensha(f'建除十二神-{jianchu_value}', 5, f'修造吉，{jianchu_value}日宜动土')
            elif jianchu_value in ['建', '破']:
                self._add_shensha(f'建除十二神-{jianchu_value}', -15, f'修造凶，{jianchu_value}日忌动土')
            elif jianchu_value in ['危']:
                self._add_shensha(f'建除十二神-{jianchu_value}', 10, f'修造吉，{jianchu_value}日宜安床')
            else:
                self._add_shensha(f'建除十二神-{jianchu_value}', -5, f'修造平，{jianchu_value}日谨慎')
        except:
            pass
    
    # ===== 动土方位检查 =====
    
    def _check_direction_shensha(self, sizhu):
        """检查动土方位在年、月、日是否犯煞"""
        if not self.direction:
            return
        
        # 年三煞到方
        if self._is_direction_in_year_sansha(sizhu):
            self._add_shensha('年三煞到方', -30, '动土方位犯年三煞，大忌')
        
        # 月三煞到方
        if self._is_direction_in_month_sansha(sizhu):
            self._add_shensha('月三煞到方', -20, '动土方位犯月三煞，忌')
        
        # 太岁到方
        if self._is_direction_taisui(sizhu):
            self._add_shensha('太岁到方', -25, '动土方位犯太岁，大忌')
        
        # 岁破到方
        if self._is_direction_suipo(sizhu):
            self._add_shensha('岁破到方', -25, '动土方位犯岁破，大忌')
        
        # 月破到方
        if self._is_direction_yuepo(sizhu):
            self._add_shensha('月破到方', -20, '动土方位犯月破，忌')
        
        # 暗建煞到方
        if self._is_direction_anjian(sizhu):
            self._add_shensha('暗建煞到方', -15, '动土方位犯暗建煞，忌')
    
    def _is_direction_in_year_sansha(self, sizhu):
        """年三煞到方：根据年支的三合局对冲方
        年三煞仅包含地支（巳午未、亥子丑、寅卯辰、申酉戌），不含天干
        """
        year_zhi = sizhu.get('year_zhi', '')
        sansha_map = {
            '申': ['巳', '午', '未'],  # 申子辰年煞南
            '子': ['巳', '午', '未'],
            '辰': ['巳', '午', '未'],
            '寅': ['亥', '子', '丑'],  # 寅午戌年煞北
            '午': ['亥', '子', '丑'],
            '戌': ['亥', '子', '丑'],
            '巳': ['寅', '卯', '辰'],  # 巳酉丑年煞东
            '酉': ['寅', '卯', '辰'],
            '丑': ['寅', '卯', '辰'],
            '亥': ['申', '酉', '戌'],  # 亥卯未年煞西
            '卯': ['申', '酉', '戌'],
            '未': ['申', '酉', '戌']
        }
        sansha_fang = sansha_map.get(year_zhi, [])
        return self.direction in sansha_fang
    
    def _is_direction_in_month_sansha(self, sizhu):
        """月三煞到方：根据月支的三合局对冲方
        月三煞仅包含地支（亥子丑、巳午未、寅卯辰、申酉戌），不含天干
        传统风水理论：寅午戌月煞北（亥子丑）、巳酉丑月煞东（寅卯辰）
        申子辰月煞南（巳午未）、亥卯未月煞西（申酉戌）
        """
        month_zhi = sizhu.get('month_zhi', '')
        sansha_map = {
            '申': ['巳', '午', '未'],  # 申子辰月煞南
            '子': ['巳', '午', '未'],
            '辰': ['巳', '午', '未'],
            '寅': ['亥', '子', '丑'],  # 寅午戌月煞北
            '午': ['亥', '子', '丑'],
            '戌': ['亥', '子', '丑'],
            '巳': ['寅', '卯', '辰'],  # 巳酉丑月煞东
            '酉': ['寅', '卯', '辰'],
            '丑': ['寅', '卯', '辰'],
            '亥': ['申', '酉', '戌'],  # 亥卯未月煞西
            '卯': ['申', '酉', '戌'],
            '未': ['申', '酉', '戌']
        }
        sansha_fang = sansha_map.get(month_zhi, [])
        return self.direction in sansha_fang
    
    def _is_direction_taisui(self, sizhu):
        """太岁到方：年支对应方位"""
        year_zhi = sizhu.get('year_zhi', '')
        # 地支对应方位
        zhi_fang = {
            '子': '子', '丑': '丑', '寅': '寅', '卯': '卯',
            '辰': '辰', '巳': '巳', '午': '午', '未': '未',
            '申': '申', '酉': '酉', '戌': '戌', '亥': '亥'
        }
        taisui_fang = zhi_fang.get(year_zhi, '')
        return self.direction == taisui_fang
    
    def _is_direction_suipo(self, sizhu):
        """岁破到方：太岁对冲方位"""
        year_zhi = sizhu.get('year_zhi', '')
        # 地支对冲
        chong_zhi = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        suipo_fang = chong_zhi.get(year_zhi, '')
        return self.direction == suipo_fang
    
    def _is_direction_yuepo(self, sizhu):
        """月破到方：月支对冲方位"""
        month_zhi = sizhu.get('month_zhi', '')
        # 地支对冲
        chong_zhi = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        yuepo_fang = chong_zhi.get(month_zhi, '')
        return self.direction == yuepo_fang
    
    def _is_direction_anjian(self, sizhu):
        """暗建煞到方：月支三合局之对冲方（即三煞方）
        传统暗建煞：月建三合局的对冲局三个地支
        例如寅月，三合局为寅午戌，对冲为申子辰，所以暗建煞在申子辰方
        """
        month_zhi = sizhu['month_zhi']
        # 暗建煞方位映射（正确：月建三合局的对冲方）
        anjian_map = {
            '寅': ['申', '子', '辰'],   # 寅月暗煞在申子辰
            '午': ['申', '子', '辰'],   # 午月同
            '戌': ['申', '子', '辰'],
            '申': ['寅', '午', '戌'],   # 申月暗煞在寅午戌
            '子': ['寅', '午', '戌'],   # 子月同
            '辰': ['寅', '午', '戌'],
            '亥': ['巳', '酉', '丑'],   # 亥月暗煞在巳酉丑
            '卯': ['巳', '酉', '丑'],   # 卯月同
            '未': ['巳', '酉', '丑'],
            '巳': ['亥', '卯', '未'],   # 巳月暗煞在亥卯未
            '酉': ['亥', '卯', '未'],   # 酉月同
            '丑': ['亥', '卯', '未']
        }
        anjian_fang = anjian_map.get(month_zhi, [])
        return self.direction in anjian_fang
    
    # ===== 时辰吉凶判断 =====
 
    def _check_hour_shensha_ext(self, sizhu):
        """扩展的时辰神煞检查"""
        hour_zhi = sizhu.get('hour_zhi', '')
        hour_gan = sizhu.get('hour_gan', '')
        day_zhi = sizhu['day_zhi']
        day_gan = sizhu['day_gan']
        
        if not hour_zhi:
            return
        
        # 1. 时辰与坐山关系
        if self.zuoshan:
            mountain_zhi = self._get_shan_zhi(self.zuoshan)
            if mountain_zhi:
                if self._is_chong_zhi(mountain_zhi, hour_zhi):
                    self._add_shensha('时冲坐山', -30, '时辰地支冲坐山，大忌')
                if self._is_liuhe(mountain_zhi, hour_zhi):
                    self._add_shensha('时与坐山六合', 10, '吉时')
                if self._is_sanhe_with_mountain(hour_zhi, mountain_zhi):
                    self._add_shensha('时与坐山三合', 15, '吉时')
        
        # 2. 时辰与主命关系
        if self.zhuming:
            zhuming_zhi = self.zhuming[1] if len(self.zhuming) >= 2 else ''
            if zhuming_zhi:
                if self._is_chong_zhi(zhuming_zhi, hour_zhi):
                    self._add_shensha('时冲主命', -30, '时辰地支冲主命，大忌')
                if self._is_liuhe(zhuming_zhi, hour_zhi):
                    self._add_shensha('时与主命六合', 10, '吉时')
                if self._is_sanhe_with_mountain(hour_zhi, zhuming_zhi):
                    self._add_shensha('时与主命三合', 12, '吉时')
        
        # 3. 时辰自身吉凶
        # 日破时
        if self._is_chong_zhi(day_zhi, hour_zhi):
            self._add_shensha('日破时', -20, '日破时，忌大事')
        
        # 贵人时（按日干）
        gui_ren = self._get_gui_ren_shichen(day_gan)
        if hour_zhi in gui_ren:
            self._add_shensha('日贵人时', 15, '天乙贵人时辰，吉')
        
        # 禄神时（按日干）
        lu = self._get_lu_shichen(day_gan)
        if hour_zhi == lu:
            self._add_shensha('日禄时', 10, '禄神时辰，吉')
        
        # 五不遇时
        if self._is_wubuyu(hour_gan, day_gan):
            self._add_shensha('五不遇时', -15, '五不遇时，凶')
    
    def _is_guiren_hour(self, sizhu):
        """是否贵人时"""
        day_gan = sizhu['day_gan']
        hour_zhi = sizhu.get('hour_zhi', '')
        
        if day_gan in self.gui_ren:
            return hour_zhi in [self.gui_ren[day_gan]['阳'], self.gui_ren[day_gan]['阴']]
        return False
    
    def _is_ripo_hour(self, sizhu):
        """是否日破时（时辰冲日支）"""
        day_zhi = sizhu['day_zhi']
        hour_zhi = sizhu.get('hour_zhi', '')
        
        zh_list = DI_ZHI
        try:
            day_idx = zh_list.index(day_zhi)
            chong_idx = (day_idx + 6) % 12
            return hour_zhi == zh_list[chong_idx]
        except:
            return False
    
    def _is_jielu_kongwang_shi(self, day_gan, hour_zhi):
        """是否截路空亡时（出行选时通道，2026-10-26 A 修复，001 §183）

        谓词与选日通道求（出行神煞._is_jielu_kongwang 的 day_gan 查表口径）一致，
        《历例》甲己日申酉时、乙庚日午未时、丙辛日辰巳时、丁壬日寅卯时、
        戊癸日子丑戌亥时；《考原》五鼠遁得壬申癸酉时为截路空亡。
        day_gan 为日干，hour_zhi 为候选时支（get_lucky_hours 已归一）。
        """
        if not day_gan or not hour_zhi:
            return False
        jielu = {
            '甲': ['申', '酉'], '己': ['申', '酉'],
            '乙': ['午', '未'], '庚': ['午', '未'],
            '丙': ['辰', '巳'], '辛': ['辰', '巳'],
            '丁': ['寅', '卯'], '壬': ['寅', '卯'],
            '戊': ['子', '丑', '戌', '亥'], '癸': ['子', '丑', '戌', '亥']
        }
        return hour_zhi in jielu.get(day_gan, [])
    
    def _is_chongshan_hour(self, sizhu):
        """是否冲山时"""
        if not self.zuoshan:
            return False
        
        hour_zhi = sizhu.get('hour_zhi', '')
        
        # 获取坐山对应的地支
        shan_zhi = self.zuoshan
        if shan_zhi in ['艮', '巽', '坤', '乾']:
            # 四维山对应的地支
            sizhi_map = {'艮': '丑', '巽': '辰', '坤': '未', '乾': '戌'}
            shan_zhi = sizhi_map.get(shan_zhi, '')
        
        if shan_zhi:
            zh_list = DI_ZHI
            try:
                shan_idx = zh_list.index(shan_zhi)
                chong_idx = (shan_idx + 6) % 12
                return hour_zhi == zh_list[chong_idx]
            except:
                pass
        return False
    
    # ===== 山家专属吉神 =====
    
    def _check_shanjia_jishen(self, sizhu):
        """检查山家专属吉神"""
        if not self.zuoshan:
            return
        
        day_zhi = sizhu['day_zhi']
        day_gan = sizhu['day_gan']
        
        # 获取坐山对应的地支
        shan_zhi = self._get_shan_zhi(self.zuoshan)
        
        if not shan_zhi:
            return
        
        # 山家三合
        if self._is_sanhe_with_mountain(day_zhi, shan_zhi):
            self._add_shensha('山家三合', 15, f'{self.zuoshan}山三合，动土大吉')
        
        # 山家六合
        if self._is_liuhe_with_mountain(day_zhi, shan_zhi):
            self._add_shensha('山家六合', 12, f'{self.zuoshan}山六合，动土吉利')
        
        # 山家禄神
        if self._is_lu_shen(day_gan, shan_zhi):
            self._add_shensha('山家禄神', 10, f'{self.zuoshan}山得禄，主富贵')
        
        # 山家贵人
        if self._is_gui_ren_shen(day_gan, day_zhi, shan_zhi):
            self._add_shensha('山家贵人', 10, f'{self.zuoshan}山得贵人，主吉祥')
        
        # 岁禄到山（年干禄神到山）
        if self._is_sui_lu_daoshan(sizhu.get('year_gan', ''), shan_zhi):
            self._add_shensha('岁禄到山', 15, f'{self.zuoshan}山得岁禄，主富贵')
        
        # 岁马到山（年支驿马到山）
        if self._is_sui_ma_daoshan(sizhu.get('year_zhi', ''), shan_zhi):
            self._add_shensha('岁马到山', 15, f'{self.zuoshan}山得岁马，主升迁')
        
        # 冲山
        if self._is_chong_shan(day_zhi, shan_zhi):
            self._add_shensha('冲山', -30, f'日冲{self.zuoshan}山，修建大凶')
        
        # 金神到山（年家方位煞：坐山落在当年金神方位，开山立向修方忌）
        # 【分值依据】典籍义例：《协纪》体系金神为年神（非日神），所理之方
        # 忌开山、立向、修方；原典籍不具现代分值，软件分值按既有凶煞档位对齐：
        # 冲山-30（日冲坐山，最重）> 月三煞犯日柱-20 > 红砂日/地贼-15 >
        # 大煞-12。金神到山为"年神方位犯坐山"，非日柱直接冲克，归入 -15 档，
        # 与红砂日、地贼同级（SHENSHA_SCORES 未设'金神到山'专项，沿用本处直配）。
        # 【影响面】365天×24山穷举（calculate_sizhu 实测）：仅在传入 zuoshan 的
        # 修造事项生效；2025 年（乙巳，金神辰巳，另含年初甲辰段34天）命中
        # 1893/8760=21.6%，2026 年（丙午，金神子丑寅卯午未，另含年初乙巳段34天）
        # 命中 3811/8760=43.5%。无坐山事项（嫁娶/开业/安床等）零影响。
        # 【年界】年干随立春换柱（verify_jinshen 边界断言：2026-02-03/02-04）。
        year_gan = sizhu.get('year_gan', '')
        jinshen_pos = self._get_jinshen_positions(year_gan)
        if jinshen_pos and shan_zhi in jinshen_pos:
            self._add_shensha('金神到山', -15,
                f'{self.zuoshan}山（{shan_zhi}）犯{year_gan}年金神，开山立向修方忌')
    
    def _get_shan_zhi(self, shan):
        """获取山家对应的地支"""
        # 二十四山对应的地支（正确的对应关系）
        # 乾在亥宫，艮在丑宫，巽在辰宫，坤在未宫
        shan_zhi_map = {
            '壬': '亥', '子': '子', '癸': '丑',
            '丑': '丑', '艮': '丑', '寅': '寅',
            '甲': '寅', '卯': '卯', '乙': '辰',
            '辰': '辰', '巽': '辰', '巳': '巳',
            '丙': '巳', '午': '午', '丁': '未',
            '未': '未', '坤': '未', '申': '申',
            '庚': '申', '酉': '酉', '辛': '戌',
            '戌': '戌', '乾': '亥', '亥': '亥'  # 修正：乾山对应亥宫，而非戌宫
        }
        return shan_zhi_map.get(shan, shan)
    
    def _is_sanhe_with_mountain(self, day_zhi, shan_zhi):
        """是否与山家三合"""
        sanhe_groups = [
            {'申', '子', '辰'},
            {'寅', '午', '戌'},
            {'巳', '酉', '丑'},
            {'亥', '卯', '未'}
        ]
        
        for group in sanhe_groups:
            if shan_zhi in group and day_zhi in group:
                return True
        return False
    
    def _is_liuhe_with_mountain(self, day_zhi, shan_zhi):
        """是否与山家六合"""
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        return liuhe_map.get(shan_zhi) == day_zhi
    
    def _is_lu_shen(self, day_gan, shan_zhi):
        """是否山家禄神"""
        # 天干禄位
        lu_wei = self.lu_shen.get(day_gan, '')
        return lu_wei == shan_zhi
    
    def _is_gui_ren_shen(self, day_gan, day_zhi, shan_zhi):
        """是否山家贵人"""
        if day_gan in self.gui_ren:
            return shan_zhi in [self.gui_ren[day_gan]['阳'], self.gui_ren[day_gan]['阴']]
        return False
    
    def _is_sui_lu_daoshan(self, year_gan, shan_zhi):
        """是否岁禄到山（年干禄神到山）"""
        # 年干禄位
        sui_lu = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '子'
        }
        return sui_lu.get(year_gan) == shan_zhi
    
    def _is_sui_ma_daoshan(self, year_zhi, shan_zhi):
        """是否岁马到山（年支驿马到山）"""
        # 年支驿马
        sui_ma = {
            '子': '寅', '丑': '亥', '寅': '申', '卯': '巳',
            '辰': '寅', '巳': '亥', '午': '申', '未': '巳',
            '申': '寅', '酉': '亥', '戌': '申', '亥': '巳'
        }
        return sui_ma.get(year_zhi) == shan_zhi
    
    def _is_chong_shan(self, day_zhi, shan_zhi):
        """是否冲山"""
        zh_list = DI_ZHI
        try:
            shan_idx = zh_list.index(shan_zhi)
            chong_idx = (shan_idx + 6) % 12
            return day_zhi == zh_list[chong_idx]
        except:
            return False
    
    def _is_chong_zhi(self, zhi1, zhi2):
        """检查两个地支是否对冲"""
        zh_list = DI_ZHI
        try:
            idx1 = zh_list.index(zhi1)
            idx2 = zh_list.index(zhi2)
            return abs(idx1 - idx2) == 6
        except:
            return False
    
    def _is_liuhe(self, *args):
        """检查两个地支是否六合，兼容原方法调用"""
        if len(args) == 1 and isinstance(args[0], dict):
            # 兼容原方法调用：_is_liuhe(sizhu)
            sizhu = args[0]
            month_zhi = sizhu['month_zhi']
            day_zhi = sizhu['day_zhi']
            zhi1, zhi2 = month_zhi, day_zhi
        elif len(args) == 2:
            # 新方法调用：_is_liuhe(zhi1, zhi2)
            zhi1, zhi2 = args
        else:
            return False
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        return liuhe_map.get(zhi1) == zhi2
    
    def _get_gui_ren_shichen(self, gan):
        """返回某天干的贵人时辰地支列表（委托单一事实源 modules/shensha/时辰系.py，001 §168 收口）"""
        return _ss_gui_ren(gan)

    def _get_lu_shichen(self, gan):
        """返回某天干的禄神时辰地支（委托单一事实源 modules/shensha/时辰系.py，001 §168 收口）"""
        return _ss_lu(gan)

    def _is_wubuyu(self, hour_gan, day_gan):
        """检查五不遇时（委托单一事实源 modules/shensha/时辰系.py，001 §168 收口）

        历史参数序 (hour_gan, day_gan) 保留，壳内翻转为统一口径 is_wubuyu(day_gan, hour_gan)。
        原实现裸 except: pass 已随委托消除；原"阴阳属性相同"附加检查数学上恒真
        （日干与时干相差6位必同奇偶同阴阳），委托纯相差6位判定完全等价。
        """
        return _ss_wubuyu(day_gan, hour_gan)
    
    # ===== 太阳太阴到山到向 =====
    
    def _check_taiyang_taiyin(self, sizhu):
        """检查太阳太阴到山到向（2026-09-22 B3 修复：sxtwl 节气口径）

        原实现两病同发（跟踪项22）：
        1. 字段名隐性死链：取 get_lunar_date() 不存在的 'month_num'/'day_num'
           键（实际返回中文键 month/day），position 恒 -1 → 全年 0 命中；
        2. 口径方向性错位：农历月半月段把正月当冬至后第一段，与《协纪》太阳
           二十四节气过宫（冬至到子）不符，365 天无一一致。
        现统一委托 神煞基类.get_sun_moon_mountains（sxtwl jqIndex，冬至到子，
        节气日当天换山），本方法只负责坐山/向山比对与登记，分值文案不变。
        """
        if not self.zuoshan:
            return

        dq = sizhu.get('date') if isinstance(sizhu, dict) else None
        if dq is None or not hasattr(dq, 'year'):
            return

        taiyang_shan, taiyin_shan = get_sun_moon_mountains(dq)
        xiangshan = self._get_xiangshan(self.zuoshan)

        # 太阳到山
        if taiyang_shan == self.zuoshan:
            self._add_shensha('太阳到山', 25, '太阳到山，诸凶回避，大吉')
        elif taiyang_shan == xiangshan:
            self._add_shensha('太阳到向', 20, '太阳到向，主光明吉利')

        # 太阴到山
        if taiyin_shan == self.zuoshan:
            self._add_shensha('太阴到山', 20, '太阴到山，主阴德吉利')
        elif taiyin_shan == xiangshan:
            self._add_shensha('太阴到向', 15, '太阴到向，主财禄')

    def _get_xiangshan(self, shan):
        """获取向山（委托神煞基类单点 helper，罗盘序 +12）"""
        return get_xiangshan_24(shan)
    
    # ===== 扶山、相主、补龙 =====
    
    def _check_fushan_xiangzhu_bulong(self, sizhu):
        """检查扶山、相主、补龙"""
        if not self.zuoshan:
            return
        
        # 扶山：日课五行生扶坐山五行
        fushan_score = self._calc_fushan(sizhu)
        if fushan_score > 0:
            self._add_shensha('扶山', fushan_score, f'日课生扶{self.zuoshan}山，主吉利')
        elif fushan_score < 0:
            self._add_shensha('克山', fushan_score, f'日课克泄{self.zuoshan}山，主凶')
        
        # 相主：日课与主命相生相合
        if self.zhuming:
            xiangzhu_score = self._calc_xiangzhu(sizhu)
            if xiangzhu_score > 0:
                self._add_shensha('相主', xiangzhu_score, '日课与主命相生，主吉')
            elif xiangzhu_score < 0:
                self._add_shensha('冲主', xiangzhu_score, '日课冲克主命，主凶')
        
        # 补龙：补坐山来龙之不足
        bulong_score = self._calc_bulong(sizhu)
        if bulong_score > 0:
            self._add_shensha('补龙', bulong_score, '日课补龙脉之不足，主兴旺')
    
    def _calc_fushan(self, sizhu):
        """计算扶山分数"""
        if not self.zuoshan:
            return 0
        
        # 获取坐山五行
        shan_wuxing = self.shan_wuxing.get(self.zuoshan, '')
        if not shan_wuxing:
            return 0
        
        # 天干五行
        gan_wuxing = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
            '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
        }
        
        # 地支五行
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
            '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        # 五行生克关系
        sheng_relation = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        ke_relation = {
            '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
        }
        
        score = 0
        
        # 检查日柱与坐山的关系
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        day_gan_wx = gan_wuxing.get(day_gan, '')
        day_zhi_wx = zhi_wuxing.get(day_zhi, '')
        
        # 日干生扶坐山
        if sheng_relation.get(day_gan_wx) == shan_wuxing:
            score += 8
        # 日干克坐山
        elif ke_relation.get(day_gan_wx) == shan_wuxing:
            score -= 10
        # 日干与坐山相同
        elif day_gan_wx == shan_wuxing:
            score += 5
        
        # 日支生扶坐山
        if sheng_relation.get(day_zhi_wx) == shan_wuxing:
            score += 5
        # 日支克坐山
        elif ke_relation.get(day_zhi_wx) == shan_wuxing:
            score -= 8
        # 日支与坐山相同
        elif day_zhi_wx == shan_wuxing:
            score += 3
        
        return score
    
    def _calc_xiangzhu(self, sizhu):
        """计算相主分数
        相主：日课与主命相生相合
        包括：五行相生相克、三合六合
        """
        if not self.zhuming:
            return 0

        # 解析主命年柱
        if len(self.zhuming) >= 2:
            zhuming_gan = self.zhuming[0]
            zhuming_zhi = self.zhuming[1]
        else:
            return 0

        # 天干五行
        gan_wuxing = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
            '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
        }

        # 地支五行
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
            '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        # 五行生克关系
        sheng_relation = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        ke_relation = {
            '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
        }

        score = 0

        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']

        zhuming_gan_wx = gan_wuxing.get(zhuming_gan, '')
        zhuming_zhi_wx = zhi_wuxing.get(zhuming_zhi, '')
        day_gan_wx = gan_wuxing.get(day_gan, '')
        day_zhi_wx = zhi_wuxing.get(day_zhi, '')

        # 日干生主命年干
        if sheng_relation.get(day_gan_wx) == zhuming_gan_wx:
            score += 8
        # 日干克主命年干
        elif ke_relation.get(day_gan_wx) == zhuming_gan_wx:
            score -= 10
        # 日干与主命年干相同
        elif day_gan_wx == zhuming_gan_wx:
            score += 5

        # 日支生主命年支
        if sheng_relation.get(day_zhi_wx) == zhuming_zhi_wx:
            score += 5
        # 日支克主命年支
        elif ke_relation.get(day_zhi_wx) == zhuming_zhi_wx:
            score -= 8
        # 日支与主命年支相同
        elif day_zhi_wx == zhuming_zhi_wx:
            score += 3

        # 日支与主命年支三合
        sanhe_groups = [
            {'申', '子', '辰'},
            {'寅', '午', '戌'},
            {'巳', '酉', '丑'},
            {'亥', '卯', '未'}
        ]
        for group in sanhe_groups:
            if day_zhi in group and zhuming_zhi in group:
                score += 10  # 三合加分
                break

        # 日支与主命年支六合
        liuhe_pairs = [
            ('子', '丑'), ('寅', '亥'), ('卯', '戌'),
            ('辰', '酉'), ('巳', '申'), ('午', '未')
        ]
        if (day_zhi, zhuming_zhi) in liuhe_pairs or (zhuming_zhi, day_zhi) in liuhe_pairs:
            score += 8  # 六合加分

        # 检查六冲
        zh_list = DI_ZHI
        try:
            zhuming_idx = zh_list.index(zhuming_zhi)
            day_idx = zh_list.index(day_zhi)
            if abs(zhuming_idx - day_idx) == 6:
                score -= 15  # 六冲
        except:
            pass

        return score
    
    def _calc_bulong(self, sizhu):
        """计算补龙分数
        补龙：补坐山来龙之不足
        传统补龙包括：
        1. 旺龙：四柱五行与龙脉五行相同（+3/+2）
        2. 生龙：四柱五行生龙脉五行（+2/+1）
        """
        if not self.zuoshan:
            return 0

        # 获取坐山五行作为龙脉五行
        long_wuxing = self.shan_wuxing.get(self.zuoshan, '')
        if not long_wuxing:
            return 0

        # 天干五行
        gan_wuxing = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
            '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
        }

        # 地支五行
        zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
            '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        # 五行生关系
        sheng_relation = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }

        score = 0

        # 检查四柱是否补充龙脉
        for pillar in ['年柱', '月柱', '日柱', '时柱']:
            pillar_val = sizhu.get(pillar, '')
            if len(pillar_val) >= 2:
                gan = pillar_val[0]
                zhi = pillar_val[1]

                gan_wx = gan_wuxing.get(gan, '')
                zhi_wx = zhi_wuxing.get(zhi, '')

                # 与龙脉五行相同，补龙有力（旺龙）
                if gan_wx == long_wuxing:
                    score += 3
                if zhi_wx == long_wuxing:
                    score += 2

                # 五行生龙脉（生龙）
                if sheng_relation.get(gan_wx) == long_wuxing:
                    score += 2
                if sheng_relation.get(zhi_wx) == long_wuxing:
                    score += 1

        return min(score, 15)
    
    def _parse_sizhu(self, sizhu_input):
        """
        解析sizhu输入，支持字符串格式和字典格式
        
        Args:
            sizhu_input: 字符串格式("甲子 乙丑 丙寅 丁卯")或字典格式
            
        Returns:
            dict: 包含year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi, hour_gan, hour_zhi的字典
        """
        if isinstance(sizhu_input, dict):
            # 已经是字典格式，直接返回
            return sizhu_input
        
        if isinstance(sizhu_input, str):
            # 字符串格式，解析为字典
            parts = sizhu_input.split()
            if len(parts) >= 3:
                year_zhu = parts[0] if len(parts) > 0 else ''
                month_zhu = parts[1] if len(parts) > 1 else ''
                day_zhu = parts[2] if len(parts) > 2 else ''
                hour_zhu = parts[3] if len(parts) > 3 else ''
                
                return {
                    'year_gan': year_zhu[0] if len(year_zhu) >= 1 else '',
                    'year_zhi': year_zhu[1] if len(year_zhu) >= 2 else '',
                    'month_gan': month_zhu[0] if len(month_zhu) >= 1 else '',
                    'month_zhi': month_zhu[1] if len(month_zhu) >= 2 else '',
                    'day_gan': day_zhu[0] if len(day_zhu) >= 1 else '',
                    'day_zhi': day_zhu[1] if len(day_zhu) >= 2 else '',
                    'hour_gan': hour_zhu[0] if len(hour_zhu) >= 1 else '',
                    'hour_zhi': hour_zhu[1] if len(hour_zhu) >= 2 else '',
                }
        
        # 返回空字典作为默认
        return {}
    
    def get_lucky_directions(self, sizhu):
        """
        计算当日吉利的动土方位
        
        遍历二十四山，检查每个方位是否犯煞，
        返回安全（不犯煞）的方位列表，按吉凶排序。
        
        Args:
            sizhu: 四柱信息（字符串或字典格式）
            
        Returns:
            list: [{'方位': '子', '分值': 0, '说明': [...]}, ...]
        """
        # 先解析sizhu为字典格式
        sizhu = self._parse_sizhu(sizhu)
        # 再标准化sizhu格式（支持中文键名和英文键名两种格式）
        sizhu = self._normalize_sizhu(sizhu)
        results = []
        old_direction = self.direction
        
        for shan in self.shan_list:
            self.direction = shan
            direction_score = 0
            reasons = []
            
            if self._is_direction_in_year_sansha(sizhu):
                direction_score -= 30
                reasons.append('犯年三煞')
            if self._is_direction_in_month_sansha(sizhu):
                direction_score -= 20
                reasons.append('犯月三煞')
            if self._is_direction_taisui(sizhu):
                direction_score -= 25
                reasons.append('犯太岁')
            if self._is_direction_suipo(sizhu):
                direction_score -= 25
                reasons.append('犯岁破')
            if self._is_direction_yuepo(sizhu):
                direction_score -= 20
                reasons.append('犯月破')
            if self._is_direction_anjian(sizhu):
                direction_score -= 15
                reasons.append('犯暗建煞')
            
            if not reasons:
                reasons.append('无煞')
            
            results.append({
                '方位': shan,
                '分值': direction_score,
                '说明': reasons
            })
        
        self.direction = old_direction
        results.sort(key=lambda x: x['分值'], reverse=True)
        return results
    
    def get_lucky_hours(self, sizhu):
        """
        计算当日吉利的动土时辰
        
        遍历十二时辰，检查每个时辰的吉凶，
        返回按时辰排序的吉凶列表。
        
        Args:
            sizhu: 四柱信息（字符串或字典格式）
            
        Returns:
            list: [{'时辰': '子时', '地支': '子', '分值': 0, '说明': [...]}, ...]
        """
        # 先解析sizhu为字典格式
        sizhu = self._parse_sizhu(sizhu)
        # 再标准化sizhu格式（支持中文键名和英文键名两种格式）
        sizhu = self._normalize_sizhu(sizhu)
        results = []
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        hour_names = {
            '子': '子时(23-1)', '丑': '丑时(1-3)', '寅': '寅时(3-5)',
            '卯': '卯时(5-7)', '辰': '辰时(7-9)', '巳': '巳时(9-11)',
            '午': '午时(11-13)', '未': '未时(13-15)', '申': '申时(15-17)',
            '酉': '酉时(17-19)', '戌': '戌时(19-21)', '亥': '亥时(21-23)'
        }
        
        # 五鼠遁时干：单一事实源 modules/shensha/时辰系.py（001 §168 收口）
        zi_gan = WUSHU_DUN.get(day_gan, '甲')
        zi_idx = TIAN_GAN.index(zi_gan)
        
        for i, zhi in enumerate(DI_ZHI):
            hour_gan = TIAN_GAN[(zi_idx + i) % 10]
            hour_score = 0
            reasons = []
            # §189 P1（2026-10-27 拍板·方案A）：五不遇时为选时硬黑名单，
            # 只影响推荐引擎的候选/择优，不改变分值与其他事项口径。
            hour_disabled = False
            
            # 日破时（2026-09-16 口径统一：分值走 SHENSHA_SCORES 单一表）
            if self._is_chong_zhi(day_zhi, zhi):
                hour_score += self._hour_delta('日破时', -20)
                reasons.append('日破时')
            
            # 2026-10-26 双通道割裂修复（A，001 §183）：出行选时补截路空亡。
            # 选日通道（出行神煞 hour 块）早已发射，选时通道此前缺失——本批按
            # _std_event=='出行' 补齐，分值经 _hour_delta 走 SHENSHA_SCORES解析
            # （出行,截路空亡）=-15，与选日同价。谓词按《历例》甲己日申酉时…
            # 戊癸日子丑戌亥时；仅出行适用，其它事项选时不受影响。
            if getattr(self, '_std_event', None) == '出行' and self._is_jielu_kongwang_shi(day_gan, zhi):
                hour_score += self._hour_delta('截路空亡', -15)
                reasons.append('截路空亡')
            
            # 时辰刑害扣分（年/月/日支全量检查；刑-15/害-10，不同支扣分叠加；冲已由日破时处理）
            xh_pen, xh_reasons = self._get_xinghai_penalty_all(sizhu, zhi)
            if xh_pen:
                hour_score += xh_pen
                reasons.extend(xh_reasons)

            # 时支与日课年/月/日支构成三合局加分
            sanhe_bonus = self._get_sanhe_daycourse_bonus(sizhu, zhi)
            if sanhe_bonus:
                hour_score += sanhe_bonus['score']
                reasons.append(sanhe_bonus['reason'])
            
            # 贵人时（时辰专属项，未登记统一表时沿用默认15分）
            gui_ren = self._get_gui_ren_shichen(day_gan)
            if zhi in gui_ren:
                hour_score += self._hour_delta('贵人时', 15)
                reasons.append('贵人时')

            # 禄神时
            lu = self._get_lu_shichen(day_gan)
            if zhi == lu:
                hour_score += self._hour_delta('禄神时', 10)
                reasons.append('禄神时')

            # 五不遇时
            if self._is_wubuyu(hour_gan, day_gan):
                hour_score += self._hour_delta('五不遇时', -15)
                reasons.append('五不遇时')
                hour_disabled = True

            # 与坐山关系
            if self.zuoshan:
                mountain_zhi = self._get_shan_zhi(self.zuoshan)
                if mountain_zhi:
                    if self._is_chong_zhi(mountain_zhi, zhi):
                        hour_score += self._hour_delta('冲坐山', -30)
                        reasons.append('冲坐山')
                    if self._is_liuhe(mountain_zhi, zhi):
                        hour_score += self._hour_delta('合坐山', 10)
                        reasons.append('合坐山')
                    if self._is_sanhe_with_mountain(zhi, mountain_zhi):
                        hour_score += self._hour_delta('三合坐山', 15)
                        reasons.append('三合坐山')

            # 与主命关系
            if self.zhuming:
                zhuming_zhi = self.zhuming[1] if len(self.zhuming) >= 2 else ''
                if zhuming_zhi:
                    if self._is_chong_zhi(zhuming_zhi, zhi):
                        hour_score += self._hour_delta('冲主命', -30)
                        reasons.append('冲主命')
                    if self._is_liuhe(zhuming_zhi, zhi):
                        hour_score += self._hour_delta('合主命', 10)
                        reasons.append('合主命')
                    if self._is_sanhe_with_mountain(zhi, zhuming_zhi):
                        hour_score += self._hour_delta('三合主命', 12)
                        reasons.append('三合主命')
            
            if not reasons:
                reasons.append('平')
            
            results.append({
                '时辰': hour_names.get(zhi, f'{zhi}时'),
                '地支': zhi,
                '天干': hour_gan,
                '分值': hour_score,
                '说明': reasons,
                '禁用': hour_disabled
            })
        
        results.sort(key=lambda x: x['分值'], reverse=True)
        return results


# 测试代码
if __name__ == '__main__':
    print("=" * 80)
    print("修造神煞扩展模块测试")
    print("=" * 80)
    
    # 添加项目根目录到路径
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 重新导入
    from modules.shensha.修造神煞扩展 import ConstructionShenShaCheckerExt
    
    checker = ConstructionShenShaCheckerExt(zuoshan='子', zhuming='甲子')
    
    # 测试数据
    test_sizhu = {
        'year_gan': '丙', 'year_zhi': '午',
        'month_gan': '甲', 'month_zhi': '午',
        'day_gan': '壬', 'day_zhi': '子',
        'hour_gan': '庚', 'hour_zhi': '子',
        '年柱': '丙午', '月柱': '甲午', '日柱': '壬子', '时柱': '庚子',
        'year_zhi': '午', 'month_zhi': '午', 'day_zhi': '子', 'hour_zhi': '子',
        'date': date(2026, 6, 15)
    }
    
    result = checker.check(test_sizhu)
    
    print("\n【神煞检查结果】")
    for shensha in result:
        print(f"  {shensha['name']}: {shensha['score']:+.0f}分 - {shensha['description']}")
    
    total_score = sum(s['score'] for s in result)
    print(f"\n总评分: {total_score}分")
