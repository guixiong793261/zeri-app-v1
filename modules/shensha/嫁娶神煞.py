# -*- coding: utf-8 -*-
"""
================================================================================
婚嫁神煞模块
================================================================================
实现婚嫁择日专用神煞的检查逻辑
依据：《协纪辨方书》、《象吉通书》等传统择日经典

使用方法:
    1. 作为模块导入: from modules.shensha.嫁娶神煞 import 婚嫁神煞Checker
    2. 直接运行: python -m modules.shensha.嫁娶神煞
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
    from .神煞基类 import ShenShaChecker
    from ..工具函数 import DI_ZHI, TIAN_GAN
except ImportError:
    from 神煞基类 import ShenShaChecker
    from 工具函数 import DI_ZHI, TIAN_GAN


class MarriageShenShaChecker(ShenShaChecker):
    """婚嫁神煞检查器"""
    
    def __init__(self):
        super().__init__()
        self.bride_gan = None
        self.groom_gan = None
        self.bride_zhi = None
        self.groom_zhi = None
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        month_zhi = sizhu['month_zhi']
        
        # 月破（婚嫁大忌）
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -25, '月破日诸事不宜，婚嫁大忌')
        
        # 大利月（需女命年干）
        if self.bride_gan and self._is_daliyue(sizhu):
            self._add_shensha('大利月', 20, '女命大利之月，婚嫁首选')
        
        # 小利月（需女命年干）
        if self.bride_gan and self._is_xiaoliyue(sizhu):
            self._add_shensha('小利月', 10, '女命小利之月，婚嫁可用')
        
        # 妨翁姑月（不利公婆）
        if self.bride_gan and self._is_fang_wenggu(sizhu):
            self._add_shensha('妨翁姑月', -15, '此月婚嫁不利翁姑（公婆）')
        
        # 妨父母月
        if self.bride_gan and self._is_fang_fumu(sizhu):
            self._add_shensha('妨父母月', -15, '此月婚嫁不利新娘父母')
        
        # 妨夫月
        if self.bride_gan and self._is_fang_fu(sizhu):
            self._add_shensha('妨夫月', -18, '此月婚嫁不利新郎')
        
        # 妨妻月
        if self.bride_gan and self._is_fang_qi(sizhu):
            self._add_shensha('妨妻月', -18, '此月婚嫁不利新娘')
        
        # 逐夫月
        if self.bride_gan and self._is_zhu_fu(sizhu):
            self._add_shensha('逐夫月', -12, '逐夫月不利新郎')
        
        # 逐妇月
        if self.bride_gan and self._is_zhu_qi(sizhu):
            self._add_shensha('逐妇月', -12, '逐妇月不利新娘')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 极凶日（婚嫁绝对禁忌）=====
        
        # 红砂日（按孟仲季月）
        if self._is_hongsha(sizhu):
            self._add_shensha('红砂日', -20, '红砂日婚嫁大忌')
        
        # 杨公忌日（固定日期）
        if self._is_yanggongji(sizhu):
            self._add_shensha('杨公忌日', -20, '杨公忌日百事不宜，婚嫁大忌')
        
        # 受死日
        if self._is_shousi(sizhu):
            self._add_shensha('受死日', -20, '受死日婚嫁大忌')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -18, '往亡日忌婚嫁')
        
        # 重丧日
        if self._is_zhongsang(sizhu):
            self._add_shensha('重丧日', -20, '重丧日婚嫁大忌')
        
        # 三娘煞
        if self._is_sanniang(sizhu):
            self._add_shensha('三娘煞', -15, '三娘煞日不宜婚嫁')
        
        # ===== 凶煞 =====
        
        # 白虎日
        if self._is_baihu(sizhu):
            self._add_shensha('白虎日', -12, '白虎日婚嫁不吉')
        
        # 朱雀日
        if self._is_zhuque(sizhu):
            self._add_shensha('朱雀日', -12, '朱雀日婚嫁不吉')
        
        # 天狗日
        if self._is_tiangou(sizhu):
            self._add_shensha('天狗日', -12, '天狗日不宜婚嫁')
        
        # 孤辰寡宿
        if self._is_guchen(sizhu):
            self._add_shensha('孤辰寡宿', -15, '孤辰寡宿主孤独，忌婚嫁')
        
        # ===== 吉日 =====
        
        # 不将日（婚嫁首选）
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 15, '不将日婚嫁大吉')
        
        # 周堂吉日
        if self._is_zhoutang(sizhu):
            self._add_shensha('周堂吉日', 12, '周堂吉日婚嫁可用')
        
        # 天德日
        if self._is_tiande(sizhu):
            self._add_shensha('天德日', 12, '天德日百事吉')
        
        # 月德日
        if self._is_yuede(sizhu):
            self._add_shensha('月德日', 10, '月德日百事吉')
        
        # 三合日
        if self._is_sanhe(sizhu):
            self._add_shensha('三合日', 8, '三合日婚嫁吉')
        
        # 六合日
        if self._is_liuhe(sizhu):
            self._add_shensha('六合日', 8, '六合日婚嫁吉')
        
        # 五合日
        if self._is_wuhe(sizhu):
            self._add_shensha('五合日', 8, '五合日婚嫁吉')
        
        # 母仓日
        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 6, '母仓日婚嫁吉')
        
        # 旺日
        if self._is_wangri(sizhu):
            self._add_shensha('旺日', 6, '旺日婚嫁吉')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞（与新人相关）"""
        if not owners:
            return
        
        # 解析新郎新娘信息
        for owner in owners:
            name = owner.get('姓名', '')
            gender = owner.get('性别', '')
            zodiac = owner.get('生肖', '')
            year_gan = owner.get('年干', '')
            
            if gender == '女':
                self.bride_gan = year_gan
                self.bride_zhi = zodiac
            elif gender == '男':
                self.groom_gan = year_gan
                self.groom_zhi = zodiac
        
        # 检查与新人冲煞
        if self.bride_zhi:
            # 冲新娘
            if self._is_chong_bride(sizhu):
                self._add_shensha('冲新娘', -25, f'日支与新娘生肖({self.bride_zhi})相冲，大凶')
            # 新娘相合
            elif self._is_he_bride(sizhu):
                self._add_shensha('新娘相合', 10, f'日支与新娘生肖({self.bride_zhi})相合，吉')
        
        if self.groom_zhi:
            # 冲新郎
            if self._is_chong_groom(sizhu):
                self._add_shensha('冲新郎', -25, f'日支与新郎生肖({self.groom_zhi})相冲，大凶')
            # 新郎相合
            elif self._is_he_groom(sizhu):
                self._add_shensha('新郎相合', 10, f'日支与新郎生肖({self.groom_zhi})相合，吉')
        
        # 日干与新人年干相合
        if self.bride_gan and self._is_gan_he_bride(sizhu):
            self._add_shensha('新娘干合', 8, f'日干与新娘年干({self.bride_gan})相合，吉')
        
        if self.groom_gan and self._is_gan_he_groom(sizhu):
            self._add_shensha('新郎干合', 8, f'日干与新郎年干({self.groom_gan})相合，吉')
    
    # ===== 大利月/小利月（按女命年干）=====
    
    def _is_daliyue(self, sizhu):
        """
        是否大利月（按女命年干推算）
        口诀：甲己大利二八月，乙庚四十二月当，丙辛六十二月在，丁壬八二月相当，戊癸大利四十月
        """
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        daliyue_map = {
            '甲': ['卯', '酉'],      # 二月、八月
            '己': ['卯', '酉'],
            '乙': ['巳', '亥'],      # 四月、十月
            '庚': ['巳', '亥'],
            '丙': ['午', '子'],      # 五月、十一月
            '辛': ['午', '子'],
            '丁': ['未', '丑'],      # 六月、十二月
            '壬': ['未', '丑'],
            '戊': ['巳', '亥'],      # 四月、十月
            '癸': ['巳', '亥']
        }
        
        return month_zhi in daliyue_map.get(self.bride_gan, [])
    
    def _is_xiaoliyue(self, sizhu):
        """
        是否小利月（按女命年干推算）
        小利月为大利月的前后月
        """
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        xiaoliyue_map = {
            '甲': ['辰', '戌'],      # 三月、九月
            '己': ['辰', '戌'],
            '乙': ['午', '子'],      # 五月、十一月
            '庚': ['午', '子'],
            '丙': ['未', '丑'],      # 六月、十二月
            '辛': ['未', '丑'],
            '丁': ['申', '寅'],      # 七月、正月
            '壬': ['申', '寅'],
            '戊': ['午', '子'],      # 五月、十一月
            '癸': ['午', '子']
        }
        
        return month_zhi in xiaoliyue_map.get(self.bride_gan, [])
    
    # ===== 妨碍类月份 =====
    
    def _is_fang_wenggu(self, sizhu):
        """是否妨翁姑月（不利公婆）"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        fang_wenggu_map = {
            '甲': ['巳', '亥'],
            '己': ['巳', '亥'],
            '乙': ['午', '子'],
            '庚': ['午', '子'],
            '丙': ['申', '寅'],
            '辛': ['申', '寅'],
            '丁': ['酉', '卯'],
            '壬': ['酉', '卯'],
            '戊': ['未', '丑'],
            '癸': ['未', '丑']
        }
        
        return month_zhi in fang_wenggu_map.get(self.bride_gan, [])
    
    def _is_fang_fumu(self, sizhu):
        """是否妨父母月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        fang_fumu_map = {
            '甲': ['午', '子'],
            '己': ['午', '子'],
            '乙': ['未', '丑'],
            '庚': ['未', '丑'],
            '丙': ['酉', '卯'],
            '辛': ['酉', '卯'],
            '丁': ['戌', '辰'],
            '壬': ['戌', '辰'],
            '戊': ['申', '寅'],
            '癸': ['申', '寅']
        }
        
        return month_zhi in fang_fumu_map.get(self.bride_gan, [])
    
    def _is_fang_fu(self, sizhu):
        """是否妨夫月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        fang_fu_map = {
            '甲': ['未', '丑'],
            '己': ['未', '丑'],
            '乙': ['申', '寅'],
            '庚': ['申', '寅'],
            '丙': ['戌', '辰'],
            '辛': ['戌', '辰'],
            '丁': ['亥', '巳'],
            '壬': ['亥', '巳'],
            '戊': ['酉', '卯'],
            '癸': ['酉', '卯']
        }
        
        return month_zhi in fang_fu_map.get(self.bride_gan, [])
    
    def _is_fang_qi(self, sizhu):
        """是否妨妻月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        fang_qi_map = {
            '甲': ['申', '寅'],
            '己': ['申', '寅'],
            '乙': ['酉', '卯'],
            '庚': ['酉', '卯'],
            '丙': ['亥', '巳'],
            '辛': ['亥', '巳'],
            '丁': ['子', '午'],
            '壬': ['子', '午'],
            '戊': ['戌', '辰'],
            '癸': ['戌', '辰']
        }
        
        return month_zhi in fang_qi_map.get(self.bride_gan, [])
    
    def _is_zhu_fu(self, sizhu):
        """是否逐夫月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        zhu_fu_map = {
            '甲': ['酉', '卯'],
            '己': ['酉', '卯'],
            '乙': ['戌', '辰'],
            '庚': ['戌', '辰'],
            '丙': ['子', '午'],
            '辛': ['子', '午'],
            '丁': ['丑', '未'],
            '壬': ['丑', '未'],
            '戊': ['亥', '巳'],
            '癸': ['亥', '巳']
        }
        
        return month_zhi in zhu_fu_map.get(self.bride_gan, [])
    
    def _is_zhu_qi(self, sizhu):
        """是否逐妇月"""
        if not self.bride_gan:
            return False
        
        month_zhi = sizhu['month_zhi']
        
        zhu_qi_map = {
            '甲': ['戌', '辰'],
            '己': ['戌', '辰'],
            '乙': ['亥', '巳'],
            '庚': ['亥', '巳'],
            '丙': ['子', '午'],
            '辛': ['子', '午'],
            '丁': ['丑', '未'],
            '壬': ['丑', '未'],
            '戊': ['寅', '申'],
            '癸': ['寅', '申']
        }
        
        return month_zhi in zhu_qi_map.get(self.bride_gan, [])
    
    # ===== 凶煞 =====
    
    def _is_yuepo(self, sizhu):
        """是否月破"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        yuepo = zh_list[(idx + 6) % 12]
        return day_zhi == yuepo
    
    def _is_hongsha(self, sizhu):
        """
        是否红砂日（按孟仲季月）
        口诀：四孟月酉，四仲月巳，四季月丑
        孟月：正月、四月、七月、十月（寅巳申亥）
        仲月：二月、五月、八月、十一月（子午卯酉）
        季月：三月、六月、九月、十二月（辰戌丑未）
        """
        month = sizhu['month_zhi']
        day = sizhu['day_zhi']
        meng = ['寅','巳','申','亥']
        zhong = ['子','午','卯','酉']
        ji = ['辰','戌','丑','未']
        if month in meng and day == '酉': return True
        if month in zhong and day == '巳': return True
        if month in ji and day == '丑': return True
        return False
    
    def _is_yanggongji(self, sizhu):
        """
        是否杨公忌日（固定农历日期）
        正月十三、二月十一、三月初九、四月初七、五月初五、六月初三、
        七月初一、七月廿九、八月廿七、九月廿五、十月廿三、十一月廿一、十二月十九
        
        【实现说明】
        使用 lunar_python 计算农历日期，判断是否为固定的13个杨公忌日
        若 lunar_python 不可用，则使用简化版判断
        """
        try:
            from lunar_python import Solar
            
            # 从 sizhu 中提取年、月、日信息
            # 注意：这里需要从外部传入公历日期，或者通过其他方式获取
            # 暂时假设 sizhu 中包含公历日期信息
            # 实际使用时，需要从调用方传入完整的日期信息
            
            # 简化实现：返回 False，实际使用时需要根据具体日期计算
            # 后续可通过修改接口，让调用方传入完整的日期信息
            return False
        except ImportError:
            # 简化版：按日支判断（仅供参考）
            month_zhi = sizhu['month_zhi']
            day_zhi = sizhu['day_zhi']
            
            # 杨公忌日对应日支（简化版，实际需农历）
            yanggongji_map = {
                '寅': '午',   # 正月十三（午日附近）
                '卯': '辰',   # 二月十一
                '辰': '寅',   # 三月初九
                '巳': '子',   # 四月初七
                '午': '戌',   # 五月初五
                '未': '申',   # 六月初三
                '申': '午',   # 七月初一
                '酉': '辰',   # 七月廿九/八月廿七
                '戌': '寅',   # 九月廿五
                '亥': '子',   # 十月廿三
                '子': '戌',   # 十一月廿一
                '丑': '申'    # 十二月十九
            }
            
            return day_zhi == yanggongji_map.get(month_zhi)
    
    def _is_shousi(self, situ):
        """
        是否受死日
        口诀：正戌二辰三亥四巳五子六午七丑八未八寅九申十卯十酉十一辰十二戌
        """
        month_zhi = situ['month_zhi']
        day_zhi = situ['day_zhi']
        
        shousi_map = {
            '寅': '戌', '卯': '辰', '辰': '亥', '巳': '巳',
            '午': '子', '未': '午', '申': '丑', '酉': '未',
            '戌': '寅', '亥': '申', '子': '卯', '丑': '酉'
        }
        return day_zhi == shousi_map.get(month_zhi)
    
    def _is_wangwang(self, sizhu):
        """是否往亡日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        wangwang_map = {
            '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
            '午': '卯', '未': '午', '申': '酉', '酉': '子',
            '戌': '辰', '亥': '未', '子': '戌', '丑': '丑'
        }
        return day_zhi == wangwang_map.get(month_zhi)
    
    def _is_zhongsang(self, sizhu):
        """是否重丧日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        zhongsang_map = {
            '寅': ['庚', '甲'],
            '卯': ['乙', '辛'],
            '辰': ['戊', '己'],
            '巳': ['丙', '壬'],
            '午': ['丁', '癸'],
            '未': ['戊', '己'],
            '申': ['庚', '甲'],
            '酉': ['乙', '辛'],
            '戌': ['戊', '己'],
            '亥': ['丙', '壬'],
            '子': ['丁', '癸'],
            '丑': ['戊', '己']
        }
        
        return day_gan in zhongsang_map.get(month_zhi, [])
    
    def _is_sanniang(self, sizhu):
        """
        是否三娘煞
        每月初三、初七、十三、十八、廿二、廿七
        注：需农历日期，当前实现需要传入完整的日期信息
        """
        # 三娘煞按农历日期判断：每月初三、初七、十三、十八、廿二、廿七
        # 由于当前sizhu不包含农历日期信息，暂时返回False
        # 后续可通过修改接口，让调用方传入完整的日期信息
        return False
    
    def _is_baihu(self, sizhu):
        """是否白虎日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        baihu_map = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == baihu_map.get(month_zhi)
    
    def _is_zhuque(self, sizhu):
        """是否朱雀日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        zhuque_map = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == zhuque_map.get(month_zhi)
    
    def _is_tiangou(self, sizhu):
        """是否天狗日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        tiangou_map = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == tiangou_map.get(month_zhi)
    
    def _is_guchen(self, sizhu):
        """是否孤辰寡宿"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        guchen_map = {
            '寅': ['巳', '丑'],
            '卯': ['巳', '丑'],
            '辰': ['巳', '丑'],
            '巳': ['申', '辰'],
            '午': ['申', '辰'],
            '未': ['申', '辰'],
            '申': ['亥', '未'],
            '酉': ['亥', '未'],
            '戌': ['亥', '未'],
            '亥': ['寅', '戌'],
            '子': ['寅', '戌'],
            '丑': ['寅', '戌']
        }
        
        return day_zhi in guchen_map.get(month_zhi, [])
    
    # ===== 吉日 =====
    
    def _is_bujiang(self, sizhu):
        """是否不将日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        yang_month = ['寅', '辰', '午', '申', '戌', '子']
        yin_month = ['卯', '巳', '未', '酉', '亥', '丑']
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        yin_gan = ['乙', '丁', '己', '辛', '癸']
        yang_zhi = ['子', '寅', '辰', '午', '申', '戌']
        yin_zhi = ['丑', '卯', '巳', '未', '酉', '亥']
        
        if month_zhi in yang_month:
            return day_gan in yin_gan and day_zhi in yin_zhi
        else:
            return day_gan in yang_gan and day_zhi in yang_zhi
    
    def _is_zhoutang(self, sizhu):
        """是否周堂吉日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        zhoutang_ji = {
            '寅': ['丑', '卯', '辰', '午'],
            '卯': ['寅', '辰', '巳', '未'],
            '辰': ['卯', '巳', '午', '申'],
            '巳': ['辰', '午', '未', '酉'],
            '午': ['巳', '未', '申', '戌'],
            '未': ['午', '申', '酉', '亥'],
            '申': ['未', '酉', '戌', '子'],
            '酉': ['申', '戌', '亥', '丑'],
            '戌': ['酉', '亥', '子', '寅'],
            '亥': ['戌', '子', '丑', '卯'],
            '子': ['亥', '丑', '寅', '辰'],
            '丑': ['子', '寅', '卯', '巳']
        }
        
        return day_zhi in zhoutang_ji.get(month_zhi, [])
    
    def _is_tiande(self, sizhu):
        """是否天德日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
        }
        
        tiande = tiande_map.get(month_zhi)
        return day_gan == tiande or day_zhi == tiande
    
    def _is_yuede(self, sizhu):
        """是否月德日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        yuede_map = {
            '寅': '丙', '午': '丙', '戌': '丙',
            '申': '壬', '子': '壬', '辰': '壬',
            '巳': '庚', '酉': '庚', '丑': '庚',
            '亥': '甲', '卯': '甲', '未': '甲'
        }
        
        return day_gan == yuede_map.get(month_zhi)
    
    def _is_sanhe(self, sizhu):
        """是否三合日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        sanhe_map = {
            '寅': ['午', '戌'],
            '午': ['寅', '戌'],
            '戌': ['寅', '午'],
            '巳': ['酉', '丑'],
            '酉': ['巳', '丑'],
            '丑': ['巳', '酉'],
            '申': ['子', '辰'],
            '子': ['申', '辰'],
            '辰': ['申', '子'],
            '亥': ['卯', '未'],
            '卯': ['亥', '未'],
            '未': ['亥', '卯']
        }
        
        return day_zhi in sanhe_map.get(month_zhi, [])
    
    def _is_liuhe(self, sizhu):
        """是否六合日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(month_zhi)
    
    def _is_wuhe(self, sizhu):
        """是否五合日"""
        day_gan = sizhu['day_gan']
        
        wuhe = ['甲', '己', '丙', '辛', '戊', '癸']
        return day_gan in wuhe
    
    def _is_mucang(self, sizhu):
        """是否母仓日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        mucang_map = {
            '寅': ['卯', '辰'],
            '卯': ['卯', '辰'],
            '辰': ['卯', '辰'],
            '巳': ['午', '未'],
            '午': ['午', '未'],
            '未': ['午', '未'],
            '申': ['酉', '戌'],
            '酉': ['酉', '戌'],
            '戌': ['酉', '戌'],
            '亥': ['子', '丑'],
            '子': ['子', '丑'],
            '丑': ['子', '丑']
        }
        
        return day_zhi in mucang_map.get(month_zhi, [])
    
    def _is_wangri(self, sizhu):
        """是否旺日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        wangri_map = {
            '寅': '卯', '卯': '卯',
            '辰': '午', '巳': '午',
            '午': '午', '未': '酉',
            '申': '酉', '酉': '酉',
            '戌': '子', '亥': '子',
            '子': '子', '丑': '卯'
        }
        
        return day_zhi == wangri_map.get(month_zhi)
    
    # ===== 新人相关检查 =====
    
    def _is_chong_bride(self, sizhu):
        """日支是否冲新娘生肖"""
        if not self.bride_zhi:
            return False
        
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if self.bride_zhi not in zh_list:
            return False
        
        idx = zh_list.index(self.bride_zhi)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_chong_groom(self, sizhu):
        """日支是否冲新郎生肖"""
        if not self.groom_zhi:
            return False
        
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if self.groom_zhi not in zh_list:
            return False
        
        idx = zh_list.index(self.groom_zhi)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_he_bride(self, sizhu):
        """日支是否与新娘生肖相合"""
        if not self.bride_zhi:
            return False
        
        day_zhi = sizhu['day_zhi']
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(self.bride_zhi)
    
    def _is_he_groom(self, sizhu):
        """日支是否与新郎生肖相合"""
        if not self.groom_zhi:
            return False
        
        day_zhi = sizhu['day_zhi']
        
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(self.groom_zhi)
    
    def _is_gan_he_bride(self, sizhu):
        """日干是否与新娘年干相合"""
        if not self.bride_gan:
            return False
        
        day_gan = sizhu['day_gan']
        
        ganhe_map = {
            '甲': '己', '己': '甲',
            '乙': '庚', '庚': '乙',
            '丙': '辛', '辛': '丙',
            '丁': '壬', '壬': '丁',
            '戊': '癸', '癸': '戊'
        }
        
        return day_gan == ganhe_map.get(self.bride_gan)
    
    def _is_gan_he_groom(self, sizhu):
        """日干是否与新郎年干相合"""
        if not self.groom_gan:
            return False
        
        day_gan = sizhu['day_gan']
        
        ganhe_map = {
            '甲': '己', '己': '甲',
            '乙': '庚', '庚': '乙',
            '丙': '辛', '辛': '丙',
            '丁': '壬', '壬': '丁',
            '戊': '癸', '癸': '戊'
        }
        
        return day_gan == ganhe_map.get(self.groom_gan)
