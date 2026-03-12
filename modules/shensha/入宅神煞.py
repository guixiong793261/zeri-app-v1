# -*- coding: utf-8 -*-
"""
================================================================================
入宅神煞模块
================================================================================
实现入宅择日专用神煞的检查逻辑
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
    from ..工具函数 import SANSHA_MAP, DI_ZHI
except ImportError:
    from 神煞基类 import ShenShaChecker
    from 工具函数 import SANSHA_MAP, DI_ZHI

class RuZhaiShenShaChecker(ShenShaChecker):
    """入宅神煞检查器"""
    
    def __init__(self):
        super().__init__()
        self.owner_zodiac = None
        self.owner_gan = None
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)
        
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 年三煞（劫煞、灾煞、岁煞）
        if self._is_sansha(sizhu):
            self._add_shensha('年三煞', -25, '入宅大忌，犯之主凶灾')
        
        # 岁破（日支与年支相冲）
        if self._is_suipo(sizhu):
            self._add_shensha('岁破', -25, '岁破日诸事不宜，入宅大忌')
    
    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        day_gan = sizhu['day_gan']
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -25, '月破日诸事不宜，入宅大忌')
        
        # 土符（忌动土，入宅搬动家具亦忌）
        if self._is_tufu(sizhu):
            self._add_shensha('土符', -15, '土符日不宜动土、入宅')
        
        # 地囊
        if self._is_dinang(sizhu):
            self._add_shensha('地囊', -20, '地囊日忌动土、入宅')
        
        # 天贼（主盗贼损耗）
        if self._is_tianzei(sizhu):
            self._add_shensha('天贼', -15, '天贼日入宅易遭盗窃损耗')
        
        # 地贼
        if self._is_dizei(sizhu):
            self._add_shensha('地贼', -12, '地贼日入宅不吉')
        
        # 归忌（移徙大忌）
        if self._is_guiji(sizhu):
            self._add_shensha('归忌', -18, '归忌日不宜移徙、入宅')
        
        # 往亡（出行、移徙忌）
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡', -18, '往亡日不宜入宅')
        
        # 红嘴朱雀（入宅大忌）
        if self._is_hongzui_zhuque(sizhu):
            self._add_shensha('红嘴朱雀', -30, '红嘴朱雀日入宅大凶')
        
        # 天狗
        if self._is_tiangou(sizhu):
            self._add_shensha('天狗', -12, '天狗日入宅不吉')
        
        # 伏断日
        if self._is_fuduan(sizhu):
            self._add_shensha('伏断日', -12, '伏断日忌入宅')
        
        # 受死日
        if self._is_shousi(sizhu):
            self._add_shensha('受死日', -18, '受死日不宜入宅')
        
        # 大耗
        if self._is_dahao(sizhu):
            self._add_shensha('大耗', -15, '大耗日入宅主耗财')
        
        # 小耗
        if self._is_xiaohao(sizhu):
            self._add_shensha('小耗', -10, '小耗日入宅主小损')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -12, '月刑日不宜入宅')
        
        # 月害
        if self._is_yuehai(sizhu):
            self._add_shensha('月害', -12, '月害日不宜入宅')
        
        # ===== 吉神 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 15, '天德吉星，入宅大吉')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 12, '月德吉星，入宅大吉')
        
        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '驿马星动，迁居顺利')
        
        # 建星吉日：成、开、满
        if self._is_jianxing_ji(sizhu):
            self._add_shensha('建星吉日', 8, '成/开/满日宜入宅')
    
    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 极凶日 =====
        
        # 四离日（节气前一日）
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -30, '四离日大事不宜，入宅大忌')
        
        # 四绝日（季节交替日）
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -30, '四绝日大事不宜，入宅大忌')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -25, '十恶大败日，入宅大忌')
        
        # ===== 凶煞 =====
        
        # 白虎入中宫
        if self._is_baihu_zhonggong(sizhu):
            self._add_shensha('白虎入中宫', -15, '白虎入中宫，入宅不吉')
        
        # ===== 吉日 =====
        
        # 天赦日
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦日', 20, '天赦日百事吉，入宅尤佳')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '三合吉日，入宅顺遂')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 10, '六合吉日，入宅和谐')
        
        # 母仓日
        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 8, '母仓日入宅吉')
        
        # 相日
        if self._is_xiangri(sizhu):
            self._add_shensha('相日', 6, '相日入宅吉')
    
    def _check_special_shensha(self, sizhu, owners):
        """检查特殊神煞，主要处理宅主（家长）生肖与日课的冲合"""
        if not owners:
            return
        
        # 取宅主（一般取第一人）
        owner = owners[0]
        self.owner_zodiac = owner.get('生肖', '')
        self.owner_gan = owner.get('年干', '')
        
        if self.owner_zodiac:
            # 与宅主相冲
            if self._is_chong_owner(sizhu):
                self._add_shensha('冲宅主', -25, f'日支与宅主生肖({self.owner_zodiac})相冲，大忌')
            # 与宅主相合
            elif self._is_he_owner(sizhu):
                self._add_shensha('合宅主', 15, f'日支与宅主生肖({self.owner_zodiac})相合，大吉')
            
            # 与宅主相害
            if self._is_hai_owner(sizhu):
                self._add_shensha('害宅主', -12, f'日支与宅主生肖({self.owner_zodiac})相害')
            
            # 与宅主相刑
            if self._is_xing_owner(sizhu):
                self._add_shensha('刑宅主', -12, f'日支与宅主生肖({self.owner_zodiac})相刑')
        
        # 日干与宅主年干相合
        if self.owner_gan and self._is_gan_he_owner(sizhu):
            self._add_shensha('宅主干合', 8, f'日干与宅主年干({self.owner_gan})相合，吉')
    
    # ========== 年神煞判断 ==========
    
    def _is_sansha(self, sizhu):
        """是否年三煞（劫煞、灾煞、岁煞）"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        if year_zhi in SANSHA_MAP:
            sansha_indices = SANSHA_MAP[year_zhi]
            zh_list = DI_ZHI
            day_idx = zh_list.index(day_zhi)
            return day_idx in sansha_indices
        return False
    
    def _is_suipo(self, sizhu):
        """是否岁破（日支与年支相冲）"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        idx = zh_list.index(year_zhi)
        suipo = zh_list[(idx + 6) % 12]
        return day_zhi == suipo
    
    # ========== 月神煞判断 ==========
    
    def _is_yuepo(self, sizhu):
        """月破：日支与月支相冲"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        yuepo = zh_list[(idx + 6) % 12]
        return day_zhi == yuepo
    
    def _is_tufu(self, sizhu):
        """土符日：按月查日支"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        tufu_map = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        return day_zhi == tufu_map.get(month_zhi)
    
    def _is_dinang(self, sizhu):
        """地囊日：按季查日支"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        # 春季（寅卯辰）地囊在亥日；夏季（巳午未）在寅日；秋季（申酉戌）在巳日；冬季（亥子丑）在申日
        dinang_map = {
            '寅': '亥', '卯': '亥', '辰': '亥',
            '巳': '寅', '午': '寅', '未': '寅',
            '申': '巳', '酉': '巳', '戌': '巳',
            '亥': '申', '子': '申', '丑': '申'
        }
        return day_zhi == dinang_map.get(month_zhi)
    
    def _is_tianzei(self, sizhu):
        """天贼日：按月查日支"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        tianzei_map = {
            '寅': '辰', '卯': '巳', '辰': '午',
            '巳': '未', '午': '申', '未': '酉',
            '申': '戌', '酉': '亥', '戌': '子',
            '亥': '丑', '子': '寅', '丑': '卯'
        }
        return day_zhi == tianzei_map.get(month_zhi)
    
    def _is_dizei(self, sizhu):
        """地贼日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        dizei_map = {
            '寅': '子', '卯': '丑', '辰': '寅',
            '巳': '卯', '午': '辰', '未': '巳',
            '申': '午', '酉': '未', '戌': '申',
            '亥': '酉', '子': '戌', '丑': '亥'
        }
        return day_zhi == dizei_map.get(month_zhi)
    
    def _is_guiji(self, sizhu):
        """
        归忌日：孟月忌丑日，仲月忌寅日，季月忌子日
        孟月：寅、申、巳、亥
        仲月：子、午、卯、酉
        季月：辰、戌、丑、未
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        meng = ['寅', '申', '巳', '亥']
        zhong = ['子', '午', '卯', '酉']
        ji = ['辰', '戌', '丑', '未']
        if month_zhi in meng and day_zhi == '丑':
            return True
        if month_zhi in zhong and day_zhi == '寅':
            return True
        if month_zhi in ji and day_zhi == '子':
            return True
        return False
    
    def _is_wangwang(self, sizhu):
        """往亡日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        wangwang_map = {
            '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
            '午': '卯', '未': '午', '申': '酉', '酉': '子',
            '戌': '辰', '亥': '未', '子': '戌', '丑': '丑'
        }
        return day_zhi == wangwang_map.get(month_zhi)
    
    def _is_hongzui_zhuque(self, sizhu):
        """红嘴朱雀日（入宅大忌）"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        hongzui_map = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == hongzui_map.get(month_zhi)
    
    def _is_tiangou(self, sizhu):
        """天狗日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        tiangou_map = {
            '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
            '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
            '戌': '午', '亥': '未', '子': '申', '丑': '酉'
        }
        return day_zhi == tiangou_map.get(month_zhi)
    
    def _is_fuduan(self, sizhu):
        """伏断日：按日干查日支"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        fuduan_map = {
            '甲': '戌', '乙': '酉', '丙': '申', '丁': '未', '戊': '午',
            '己': '巳', '庚': '辰', '辛': '卯', '壬': '寅', '癸': '丑'
        }
        return day_zhi == fuduan_map.get(day_gan)
    
    def _is_shousi(self, sizhu):
        """受死日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        shousi_map = {
            '寅': '戌', '卯': '辰', '辰': '亥', '巳': '巳',
            '午': '子', '未': '午', '申': '丑', '酉': '未',
            '戌': '寅', '亥': '申', '子': '卯', '丑': '酉'
        }
        return day_zhi == shousi_map.get(month_zhi)
    
    def _is_dahao(self, sizhu):
        """大耗日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        dahao_map = {
            '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
            '午': '子', '未': '丑', '申': '寅', '酉': '卯',
            '戌': '辰', '亥': '巳', '子': '午', '丑': '未'
        }
        return day_zhi == dahao_map.get(month_zhi)
    
    def _is_xiaohao(self, sizhu):
        """小耗日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        xiaohao_map = {
            '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅',
            '戌': '卯', '亥': '辰', '子': '巳', '丑': '午'
        }
        return day_zhi == xiaohao_map.get(month_zhi)
    
    def _is_yuexing(self, sizhu):
        """月刑日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        yuexing_map = {
            '寅': '巳', '卯': '子', '辰': '辰', '巳': '申',
            '午': '午', '未': '丑', '申': '寅', '酉': '酉',
            '戌': '未', '亥': '亥', '子': '卯', '丑': '戌'
        }
        return day_zhi == yuexing_map.get(month_zhi)
    
    def _is_yuehai(self, sizhu):
        """月害日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        yuehai_map = {
            '子': '未', '丑': '午', '寅': '巳', '卯': '辰',
            '辰': '卯', '巳': '寅', '午': '丑', '未': '子',
            '申': '亥', '酉': '戌', '戌': '酉', '亥': '申'
        }
        return day_zhi == yuehai_map.get(month_zhi)
    
    def _is_tiande(self, sizhu):
        """天德日"""
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
        """月德日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        yuede_map = {
            '寅': '丙', '午': '丙', '戌': '丙',
            '申': '壬', '子': '壬', '辰': '壬',
            '巳': '庚', '酉': '庚', '丑': '庚',
            '亥': '甲', '卯': '甲', '未': '甲'
        }
        
        return day_gan == yuede_map.get(month_zhi)
    
    def _is_yima(self, sizhu):
        """驿马日"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        yima_map = {
            '寅': '申', '午': '申', '戌': '申',
            '申': '寅', '子': '寅', '辰': '寅',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        
        return day_zhi == yima_map.get(year_zhi)
    
    def _is_jianxing_ji(self, sizhu):
        """建星吉日（成、开、满）"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        zh_list = DI_ZHI
        month_idx = zh_list.index(month_zhi)
        day_idx = zh_list.index(day_zhi)
        
        jian_idx = (day_idx - month_idx) % 12
        
        jianxing_ji = [2, 3, 5]  # 满=2, 成=3, 开=5
        
        return jian_idx in jianxing_ji
    
    # ========== 日神煞判断 ==========
    
    def _is_sili(self, sizhu):
        """四离日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        sili_map = {
            '卯': '辰', '午': '未', '酉': '戌', '子': '丑'
        }
        return day_zhi == sili_map.get(month_zhi)
    
    def _is_sijue(self, sizhu):
        """四绝日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        sijue_map = {
            '丑': '寅', '辰': '巳', '未': '申', '戌': '亥'
        }
        return day_zhi == sijue_map.get(month_zhi)
    
    def _is_shie_dabai(self, sizhu):
        """十恶大败日"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    def _is_baihu_zhonggong(self, sizhu):
        """白虎入中宫"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        baihu_map = {
            '寅': '午', '卯': '未', '辰': '申', '巳': '酉',
            '午': '戌', '未': '亥', '申': '子', '酉': '丑',
            '戌': '寅', '亥': '卯', '子': '辰', '丑': '巳'
        }
        return day_zhi == baihu_map.get(month_zhi)
    
    def _is_tianshe(self, sizhu):
        """
        天赦日：春戊寅，夏甲午，秋戊申，冬甲子
        春季（寅卯辰月）：戊寅日
        夏季（巳午未月）：甲午日
        秋季（申酉戌月）：戊申日
        冬季（亥子丑月）：甲子日
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        if month_zhi in ['寅', '卯', '辰'] and day_gan == '戊' and day_zhi == '寅':
            return True
        if month_zhi in ['巳', '午', '未'] and day_gan == '甲' and day_zhi == '午':
            return True
        if month_zhi in ['申', '酉', '戌'] and day_gan == '戊' and day_zhi == '申':
            return True
        if month_zhi in ['亥', '子', '丑'] and day_gan == '甲' and day_zhi == '子':
            return True
        return False
    
    def _is_sanhe(self, sizhu):
        """
        三合日：日支与月支三合
        申子辰合水局、寅午戌合火局、巳酉丑合金局、亥卯未合木局
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        sanhe_groups = [('申', '子', '辰'), ('寅', '午', '戌'), ('巳', '酉', '丑'), ('亥', '卯', '未')]
        for group in sanhe_groups:
            if month_zhi in group and day_zhi in group and month_zhi != day_zhi:
                return True
        return False
    
    def _is_liuhe(self, sizhu):
        """
        六合日：日支与月支六合
        子丑合土、寅亥合木、卯戌合火、辰酉合金、巳申合水、午未合火/土
        """
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
    
    def _is_mucang(self, sizhu):
        """母仓日"""
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
    
    def _is_xiangri(self, sizhu):
        """相日"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        xiangri_map = {
            '寅': '卯', '卯': '卯',
            '辰': '午', '巳': '午',
            '午': '午', '未': '酉',
            '申': '酉', '酉': '酉',
            '戌': '子', '亥': '子',
            '子': '子', '丑': '卯'
        }
        
        return day_zhi == xiangri_map.get(month_zhi)
    
    # ========== 宅主相关判断 ==========
    
    def _shengxiao_to_zhi(self, shengxiao):
        """
        生肖转换为地支
        生肖对应地支：子鼠、丑牛、寅虎、卯兔、辰龙、巳蛇、午马、未羊、申猴、酉鸡、戌狗、亥猪
        """
        shengxiao_map = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        return shengxiao_map.get(shengxiao)
    
    def _is_chong_owner(self, sizhu):
        """日支是否冲宅主生肖"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu['day_zhi']
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong_map.get(owner_zhi)
    
    def _is_he_owner(self, sizhu):
        """日支是否与宅主生肖相合（六合或三合）"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu['day_zhi']
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        # 六合
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        if liuhe_map.get(owner_zhi) == day_zhi:
            return True
        
        # 三合
        sanhe_sets = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
        for s in sanhe_sets:
            if owner_zhi in s and day_zhi in s and owner_zhi != day_zhi:
                return True
        
        return False
    
    def _is_hai_owner(self, sizhu):
        """日支是否与宅主生肖相害"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu['day_zhi']
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        liuhai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        
        return day_zhi == liuhai_map.get(owner_zhi)
    
    def _is_xing_owner(self, sizhu):
        """日支是否与宅主生肖相刑"""
        if not self.owner_zodiac:
            return False
        
        day_zhi = sizhu['day_zhi']
        owner_zhi = self._shengxiao_to_zhi(self.owner_zodiac)
        
        if not owner_zhi:
            if self.owner_zodiac in DI_ZHI:
                owner_zhi = self.owner_zodiac
            else:
                return False
        
        # 相刑关系
        xing_map = {
            '子': '卯', '卯': '子',
            '寅': '巳', '巳': '申', '申': '寅',
            '丑': '戌', '戌': '未', '未': '丑',
            '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'
        }
        
        return day_zhi == xing_map.get(owner_zhi)
    
    def _is_gan_he_owner(self, sizhu):
        """日干是否与宅主年干相合"""
        if not self.owner_gan:
            return False
        
        day_gan = sizhu['day_gan']
        
        ganhe_map = {
            '甲': '己', '己': '甲',
            '乙': '庚', '庚': '乙',
            '丙': '辛', '辛': '丙',
            '丁': '壬', '壬': '丁',
            '戊': '癸', '癸': '戊'
        }
        
        return day_gan == ganhe_map.get(self.owner_gan)
