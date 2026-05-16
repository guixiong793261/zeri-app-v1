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
    from ..工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE
    from ..二十四山 import ZhengTiWuXingSelectorDB
except ImportError:
    from 修造神煞 import ConstructionShenShaChecker
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
        
        # 太阳到山表（简化版，实际应根据天文计算）
        # 太阳每月过一个宫，约30度，对应二十四山
        self.taiyang_daoshan = {
            1: '子',   # 冬至前后，太阳在子
            2: '癸',
            3: '丑',
            4: '艮',
            5: '寅',
            6: '甲',
            7: '卯',   # 春分前后
            8: '乙',
            9: '辰',
            10: '巽',
            11: '巳',
            12: '丙',
            13: '午',  # 夏至前后
            14: '丁',
            15: '未',
            16: '坤',
            17: '申',
            18: '庚',
            19: '酉',  # 秋分前后
            20: '辛',
            21: '戌',
            22: '乾',
            23: '亥',
            24: '壬'
        }
        
        # 太阴到山表（与太阳相对，约差180度）
        self.taiyin_daoshan = {
            1: '午',   # 太阴与太阳相对
            2: '丁',
            3: '未',
            4: '坤',
            5: '申',
            6: '庚',
            7: '酉',
            8: '辛',
            9: '戌',
            10: '乾',
            11: '亥',
            12: '壬',
            13: '子',
            14: '癸',
            15: '丑',
            16: '艮',
            17: '寅',
            18: '甲',
            19: '卯',
            20: '乙',
            21: '辰',
            22: '巽',
            23: '巳',
            24: '丙'
        }
        
        # 杨公忌日（农历）
        self.yanggongji = {
            1: [13],    # 正月十三
            2: [11],    # 二月十一
            3: [9],     # 三月初九
            4: [7],     # 四月初七
            5: [5],     # 五月初五
            6: [3],     # 六月初三
            7: [1, 29], # 七月初一、二十九
            8: [27],    # 八月二十七
            9: [25],    # 九月二十五
            10: [23],   # 十月二十三
            11: [21],   # 十一月二十一
            12: [19]    # 十二月十九
        }
        
        # 三娘煞日
        self.sanniangsha = [3, 7, 13, 18, 22, 27]
        
        # 红纱日
        self.hongsha = {
            1: ['巳'], 4: ['巳'], 7: ['巳'], 10: ['巳'],
            2: ['酉'], 5: ['酉'], 8: ['酉'], 11: ['酉'],
            3: ['丑'], 6: ['丑'], 9: ['丑'], 12: ['丑']
        }
        
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
        # 杨公忌
        if self._is_yanggongji(sizhu):
            self._add_shensha('杨公忌', -20, '百事忌，修建大凶')
        
        # 三娘煞
        if self._is_sanniangsha(sizhu):
            self._add_shensha('三娘煞', -15, '忌婚嫁、修建')
        
        # 红纱日
        if self._is_hongsha(sizhu):
            self._add_shensha('红纱日', -15, '百事忌，犯之主血光')
        
        # 重丧日 - 修造需参看，非首要禁忌
        if self._is_zhongsang(sizhu):
            self._add_shensha('重丧日', -10, '重丧日，修造需参看，非首要禁忌')
        
        # 重复日 - 忌凶事，利吉事
        if self._is_chongfu(sizhu):
            self._add_shensha('重复日', -10, '重复日，忌凶事，利吉事')
    
    def _is_yanggongji(self, sizhu):
        """是否杨公忌日"""
        try:
            from ..四柱计算器 import get_lunar_date
        except ImportError:
            from 四柱计算器 import get_lunar_date
        
        try:
            if 'date' in sizhu:
                lunar = get_lunar_date(sizhu['date'])
                month = lunar.get('month_num', 0)
                day = lunar.get('day_num', 0)
                if month in self.yanggongji:
                    return day in self.yanggongji[month]
        except:
            pass
        return False
    
    def _is_sanniangsha(self, sizhu):
        """是否三娘煞日"""
        try:
            from ..四柱计算器 import get_lunar_date
        except ImportError:
            from 四柱计算器 import get_lunar_date
        
        try:
            if 'date' in sizhu:
                lunar = get_lunar_date(sizhu['date'])
                day = lunar.get('day_num', 0)
                return day in self.sanniangsha
        except:
            pass
        return False
    
    def _is_hongsha(self, sizhu):
        """是否红纱日"""
        try:
            from ..四柱计算器 import get_lunar_date
        except ImportError:
            from 四柱计算器 import get_lunar_date
        
        try:
            if 'date' in sizhu:
                lunar = get_lunar_date(sizhu['date'])
                month = lunar.get('month_num', 0)
                day_zhi = sizhu['day_zhi']
                if month in self.hongsha:
                    return day_zhi in self.hongsha[month]
        except:
            pass
        return False
    
    def _is_zhongsang(self, sizhu):
        """是否重丧日
        重丧日口诀：正七连庚甲，二八乙辛当
                  五冬丁癸是，四十丙壬方
                  三六九腊月，戊己是重丧
        正月(寅)、七月(申)忌庚甲日
        二月(卯)、八月(酉)忌乙辛日
        三月(辰)、六月(未)、九月(戌)、腊月(丑)忌戊己日
        四月(巳)、十月(戌)忌丙壬日
        五月(午)、十一月(亥)忌丁癸日
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']

        zhongsang_map = {
            '寅': ['庚', '甲'], '申': ['庚', '甲'],  # 正月、七月忌庚甲
            '卯': ['乙', '辛'], '酉': ['乙', '辛'],  # 二月、八月忌乙辛
            '巳': ['丙', '壬'], '戌': ['丙', '壬'],  # 四月、十月忌丙壬
            '午': ['丁', '癸'], '亥': ['丁', '癸'],  # 五月、十一月忌丁癸（修正：原为戊己）
            '辰': ['戊', '己'], '未': ['戊', '己'],  # 三月、六月忌戊己
            '丑': ['戊', '己'], '戌': ['戊', '己']   # 九月、腊月忌戊己
        }
        return day_gan in zhongsang_map.get(month_zhi, [])
    
    def _is_chongfu(self, sizhu):
        """是否重复日
        重复日：巳日、亥日
        """
        day_zhi = sizhu['day_zhi']
        return day_zhi in ['巳', '亥']
    
    # ===== 建除十二神 =====
    
    def _check_jianchu(self, sizhu):
        """检查建除十二神"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 计算建除值
        # 正月建寅，二月建卯，依此类推
        jianzhi_map = {
            '寅': '寅', '卯': '卯', '辰': '辰', '巳': '巳',
            '午': '午', '未': '未', '申': '申', '酉': '酉',
            '戌': '戌', '亥': '亥', '子': '子', '丑': '丑'
        }
        
        jianzhi = jianzhi_map.get(month_zhi, '寅')
        zh_list = DI_ZHI
        
        try:
            jian_idx = zh_list.index(jianzhi)
            day_idx = zh_list.index(day_zhi)
            offset = (day_idx - jian_idx) % 12
            jianchu_value = self.jianchu[offset]
            
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
        """年三煞到方：根据年支的三合局对冲方"""
        year_zhi = sizhu['year_zhi']
        # 年三煞方位映射（简化版）
        sansha_map = {
            '申': ['巳', '丙', '午'],  # 申子辰年煞南
            '子': ['巳', '丙', '午'],
            '辰': ['巳', '丙', '午'],
            '寅': ['亥', '壬', '子'],  # 寅午戌年煞北
            '午': ['亥', '壬', '子'],
            '戌': ['亥', '壬', '子'],
            '巳': ['寅', '甲', '卯'],  # 巳酉丑年煞东
            '酉': ['寅', '甲', '卯'],
            '丑': ['寅', '甲', '卯'],
            '亥': ['申', '庚', '酉'],  # 亥卯未年煞西
            '卯': ['申', '庚', '酉'],
            '未': ['申', '庚', '酉']
        }
        sansha_fang = sansha_map.get(year_zhi, [])
        return self.direction in sansha_fang
    
    def _is_direction_in_month_sansha(self, sizhu):
        """月三煞到方：根据月支的三合局对冲方"""
        month_zhi = sizhu['month_zhi']
        # 月三煞方位映射
        # 传统风水理论：寅午戌月煞北（亥子丑壬癸）、巳酉丑月煞东（寅甲卯乙）
        # 申子辰月煞南（巳丙午丁）、亥卯未月煞西（申庚酉辛）
        sansha_map = {
            '申': ['巳', '丙', '午', '丁'],  # 申子辰月煞南
            '子': ['巳', '丙', '午', '丁'],
            '辰': ['巳', '丙', '午', '丁'],
            '寅': ['亥', '壬', '子', '丑', '癸'],  # 寅午戌月煞北
            '午': ['亥', '壬', '子', '丑', '癸'],
            '戌': ['亥', '壬', '子', '丑', '癸'],
            '巳': ['寅', '甲', '卯', '乙'],  # 巳酉丑月煞东
            '酉': ['寅', '甲', '卯', '乙'],
            '丑': ['寅', '甲', '卯', '乙'],
            '亥': ['申', '庚', '酉', '辛'],  # 亥卯未月煞西
            '卯': ['申', '庚', '酉', '辛'],
            '未': ['申', '庚', '酉', '辛']
        }
        sansha_fang = sansha_map.get(month_zhi, [])
        return self.direction in sansha_fang
    
    def _is_direction_taisui(self, sizhu):
        """太岁到方：年支对应方位"""
        year_zhi = sizhu['year_zhi']
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
        year_zhi = sizhu['year_zhi']
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
        month_zhi = sizhu['month_zhi']
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
        """返回某天干的贵人时辰地支列表"""
        gui_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '戊': ['丑', '未'], '己': ['子', '申'], '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }
        return gui_map.get(gan, [])
    
    def _get_lu_shichen(self, gan):
        """返回某天干的禄神时辰地支"""
        lu_map = {'甲':'寅','乙':'卯','丙':'巳','丁':'午','戊':'巳','己':'午','庚':'申','辛':'酉','壬':'亥','癸':'子'}
        return lu_map.get(gan)
    
    def _is_wubuyu(self, hour_gan, day_gan):
        """检查五不遇时
        五不遇时：时干克日干，且阳日阳时、阴日阴时
        正确算法：时干与日干相差6位（甲日庚时、乙日辛时等）
        """
        gan_list = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        yin_gan = ['乙', '丁', '己', '辛', '癸']

        try:
            hour_idx = gan_list.index(hour_gan)
            day_idx = gan_list.index(day_gan)

            # 时干克日干：时干为日干后6位（庚克甲、辛克乙、...）
            if (day_idx + 6) % 10 == hour_idx:
                # 检查阴阳属性：阳日阳时、阴日阴时
                hour_is_yang = hour_gan in yang_gan
                day_is_yang = day_gan in yang_gan
                return hour_is_yang == day_is_yang
        except:
            pass
        return False
    
    # ===== 太阳太阴到山到向 =====
    
    def _check_taiyang_taiyin(self, sizhu):
        """检查太阳太阴到山到向"""
        if not self.zuoshan:
            return
        
        try:
            from ..四柱计算器 import get_lunar_date
        except ImportError:
            from 四柱计算器 import get_lunar_date
        
        try:
            if 'date' in sizhu:
                lunar = get_lunar_date(sizhu['date'])
                month = lunar.get('month_num', 0)
                
                # 计算太阳位置（简化版，每15天过一个山）
                day = lunar.get('day_num', 1)
                position = (month - 1) * 2 + (1 if day > 15 else 0) + 1
                
                taiyang_shan = self.taiyang_daoshan.get(position, '')
                taiyin_shan = self.taiyin_daoshan.get(position, '')
                
                # 太阳到山
                if taiyang_shan == self.zuoshan:
                    self._add_shensha('太阳到山', 25, '太阳到山，诸凶回避，大吉')
                elif taiyang_shan == self._get_xiangshan(self.zuoshan):
                    self._add_shensha('太阳到向', 20, '太阳到向，主光明吉利')
                
                # 太阴到山
                if taiyin_shan == self.zuoshan:
                    self._add_shensha('太阴到山', 20, '太阴到山，主阴德吉利')
                elif taiyin_shan == self._get_xiangshan(self.zuoshan):
                    self._add_shensha('太阴到向', 15, '太阴到向，主财禄')
        except:
            pass
    
    def _get_xiangshan(self, shan):
        """获取向山（与坐山相对）"""
        try:
            idx = self.shan_list.index(shan)
            xiang_idx = (idx + 12) % 24
            return self.shan_list[xiang_idx]
        except:
            return ''
    
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
    
    def get_lucky_directions(self, sizhu):
        """
        计算当日吉利的动土方位
        
        遍历二十四山，检查每个方位是否犯煞，
        返回安全（不犯煞）的方位列表，按吉凶排序。
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            list: [{'方位': '子', '分值': 0, '说明': [...]}, ...]
        """
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
            sizhu: 四柱信息
            
        Returns:
            list: [{'时辰': '子时', '地支': '子', '分值': 0, '说明': [...]}, ...]
        """
        results = []
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        hour_names = {
            '子': '子时(23-1)', '丑': '丑时(1-3)', '寅': '寅时(3-5)',
            '卯': '卯时(5-7)', '辰': '辰时(7-9)', '巳': '巳时(9-11)',
            '午': '午时(11-13)', '未': '未时(13-15)', '申': '申时(15-17)',
            '酉': '酉时(17-19)', '戌': '戌时(19-21)', '亥': '亥时(21-23)'
        }
        
        # 五鼠遁时干：根据日干推算子时天干
        wushu_dun = {
            '甲': '甲', '乙': '丙', '丙': '戊', '丁': '庚', '戊': '壬',
            '己': '甲', '庚': '丙', '辛': '戊', '壬': '庚', '癸': '壬'
        }
        zi_gan = wushu_dun.get(day_gan, '甲')
        zi_idx = TIAN_GAN.index(zi_gan)
        
        for i, zhi in enumerate(DI_ZHI):
            hour_gan = TIAN_GAN[(zi_idx + i) % 10]
            hour_score = 0
            reasons = []
            
            # 日破时
            if self._is_chong_zhi(day_zhi, zhi):
                hour_score -= 20
                reasons.append('日破时')
            
            # 贵人时
            gui_ren = self._get_gui_ren_shichen(day_gan)
            if zhi in gui_ren:
                hour_score += 15
                reasons.append('贵人时')
            
            # 禄神时
            lu = self._get_lu_shichen(day_gan)
            if zhi == lu:
                hour_score += 10
                reasons.append('禄神时')
            
            # 五不遇时
            if self._is_wubuyu(hour_gan, day_gan):
                hour_score -= 15
                reasons.append('五不遇时')
            
            # 与坐山关系
            if self.zuoshan:
                mountain_zhi = self._get_shan_zhi(self.zuoshan)
                if mountain_zhi:
                    if self._is_chong_zhi(mountain_zhi, zhi):
                        hour_score -= 30
                        reasons.append('冲坐山')
                    if self._is_liuhe(mountain_zhi, zhi):
                        hour_score += 10
                        reasons.append('合坐山')
                    if self._is_sanhe_with_mountain(zhi, mountain_zhi):
                        hour_score += 15
                        reasons.append('三合坐山')
            
            # 与主命关系
            if self.zhuming:
                zhuming_zhi = self.zhuming[1] if len(self.zhuming) >= 2 else ''
                if zhuming_zhi:
                    if self._is_chong_zhi(zhuming_zhi, zhi):
                        hour_score -= 30
                        reasons.append('冲主命')
                    if self._is_liuhe(zhuming_zhi, zhi):
                        hour_score += 10
                        reasons.append('合主命')
                    if self._is_sanhe_with_mountain(zhi, zhuming_zhi):
                        hour_score += 12
                        reasons.append('三合主命')
            
            if not reasons:
                reasons.append('平')
            
            results.append({
                '时辰': hour_names.get(zhi, f'{zhi}时'),
                '地支': zhi,
                '天干': hour_gan,
                '分值': hour_score,
                '说明': reasons
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
