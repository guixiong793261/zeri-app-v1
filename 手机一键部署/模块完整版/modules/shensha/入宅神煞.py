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
    from .神煞基类 import ShenShaChecker, is_wangwang_by_zhi
    from ..工具函数 import SANSHA_MAP, DI_ZHI
except ImportError:
    from 神煞基类 import ShenShaChecker, is_wangwang_by_zhi
    from 工具函数 import SANSHA_MAP, DI_ZHI

class RuZhaiShenShaChecker(ShenShaChecker):
    """入宅神煞检查器"""
    
    def __init__(self):
        super().__init__()
        self.owner_zodiac = None
        self.owner_gan = None
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 年三煞检查已移除
        # 注意：年三煞的正确判断应该基于山向（山家三煞），而非仅看日支是否在流年三煞方位
        # 对于入宅，年三煞的判断应该在评分器中根据具体山向进行，不在此处统一扣分
        # if self._is_sansha(sizhu):
        #     self._add_shensha('年三煞', -25, '入宅大忌，犯之主凶灾')
        
        # 岁破（日支与年支相冲）
        if self._is_suipo(sizhu):
            self._add_shensha('岁破', -30, '岁破日诸事不宜，入宅大忌')
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        day_gan = sizhu['day_gan']
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -30, '月破日诸事不宜，入宅大忌')
        
        # 土符（忌动土，入宅搬动家具亦忌）
        if self._is_tufu(sizhu):
            self._add_shensha('土符', -20, '土符日不宜动土、入宅')
        
        # 地囊
        if self._is_dinang(sizhu):
            self._add_shensha('地囊', -25, '地囊日忌动土、入宅')
        
        # 天贼（主盗贼损耗）
        if self._is_tianzei(sizhu):
            self._add_shensha('天贼', -20, '天贼日入宅易遭盗窃损耗')
        
        # 地贼
        if self._is_dizei(sizhu):
            self._add_shensha('地贼', -15, '地贼日入宅不吉')
        
        # 归忌（移徙大忌）
        if self._is_guiji(sizhu):
            self._add_shensha('归忌', -15, '归忌日不宜移徙、入宅')
        
        # 往亡（出行、移徙忌）
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡', -20, '往亡日不宜入宅')
        
        # 红嘴朱雀（入宅大忌）
        if self._is_hongzui_zhuque(sizhu):
            self._add_shensha('红嘴朱雀', -30, '红嘴朱雀日入宅大凶')
        
        # 天狗
        if self._is_tiangou(sizhu):
            self._add_shensha('天狗', -12, '天狗日入宅不吉')

        # 伏断日由基类月作用域统一注册（A6-3 死桩与同名分支删除：
        # 旧 return False 经 self 分派屏蔽基类注册，致入宅/移徙 0 命中）

        # 受死日
        if self._is_shousi(sizhu):
            self._add_shensha('受死日', -22, '受死日不宜入宅')
        
        # 大耗
        if self._is_dahao(sizhu):
            self._add_shensha('大耗', -20, '大耗日入宅主耗财')
        
        # 小耗
        if self._is_xiaohao(sizhu):
            self._add_shensha('小耗', -15, '小耗日入宅主小损')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -15, '月刑日不宜入宅')
        
        # 月害
        if self._is_yuehai(sizhu):
            self._add_shensha('月害', -15, '月害日不宜入宅')
        
        # ===== 补充缺失的凶煞检查 =====
        
        # 劫煞（大忌）
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -25, '劫煞日入宅大忌，主失盗')
        
        # 灾煞（大忌）
        if self._is_zaijiesha(sizhu):
            self._add_shensha('灾煞', -25, '灾煞日入宅大忌，主灾祸')
        
        # 月煞
        if self._is_yuesha(sizhu):
            self._add_shensha('月煞', -20, '月煞日入宅不吉')
        
        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌日入宅不吉')
        
        # 大时
        if self._is_dashi(sizhu):
            self._add_shensha('大时', -12, '大时日入宅不吉')
        
        # 天吏
        if self._is_tianli(sizhu):
            self._add_shensha('天吏', -15, '天吏日入宅不吉')
        
        # 四废
        if self._is_sifei(sizhu):
            self._add_shensha('四废', -15, '四废日入宅大忌')
        
        # 五墓
        if self._is_wumu(sizhu):
            self._add_shensha('五墓', -12, '五墓日入宅不吉')
        
        # ===== 吉神 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德吉星，入宅大吉')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德吉星，入宅大吉')
        
        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合，入宅吉')
        
        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合，入宅吉')
        
        # 天愿
        if self._is_tianyuan(sizhu):
            self._add_shensha('天愿', 12, '天愿吉星，入宅吉')
        
        # 月恩
        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩吉星，入宅吉')
        
        # 四相
        if self._is_sixiang(sizhu):
            self._add_shensha('四相', 10, '四相吉日，入宅吉')
        
        # 时德
        if self._is_shide(sizhu):
            self._add_shensha('时德', 10, '时德吉日，入宅吉')
        
        # 民日
        if self._is_minri(sizhu):
            self._add_shensha('民日', 8, '民日宜入宅')

        # 2026-10 A1：'天马' 同名重加删除（典载天马为月神，基类月作用域注册）。

        # 2026-10 A4：三奇同名重加删除（基类 super 日块以 '三奇{日/月/星}'
        # 单点注册；子类同名块被 _add_shensha 去重屏蔽，从未生效）。

        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星到座，入宅吉')

        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '驿马星动，迁居顺利')
        
        # 建星吉日：成、开、满
        if self._is_jianxing_ji(sizhu):
            self._add_shensha('建星吉日', 10, '成/开/满日宜入宅')
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 极凶日 =====

        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -30, '十恶大败日，入宅大忌')
        
        # ===== 凶煞 =====
        
        # 白虎入中宫
        if self._is_baihu_zhonggong(sizhu):
            self._add_shensha('白虎入中宫', -20, '白虎入中宫，入宅不吉')
        
        # ===== 吉日 =====
        
        # '天赦日'重加已删除（2026-09-18，001跟踪项13.2方案①）：基类
        # _check_day_shensha 已加'天赦'+25（本类日方法 super 先行且全路径必达），
        # 原异名重加致真天赦日 +50 双计；删除后走基类统一，天赦日=+25。

        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '三合吉日，入宅顺遂')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 12, '六合吉日，入宅和谐')
        
        # 母仓日
        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 10, '母仓日入宅吉')
        
        # 相日
        if self._is_xiangri(sizhu):
            self._add_shensha('相日', 10, '相日入宅吉')
        
        # ===== 补充缺失的吉神检查 =====

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 年干比日干典载口径）。

        # 岁合（主和合）
        if self._is_suihe(sizhu):
            self._add_shensha('岁合', 12, '岁合主和合，入宅吉')
        
        # 益后（利于后代）
        if self._is_yihou(sizhu):
            self._add_shensha('益后', 12, '益后日主益后代，入宅吉')
        
        # 续世（利于续嗣）
        if self._is_xushi(sizhu):
            self._add_shensha('续世', 10, '续世日主续嗣，入宅吉')
        
        # 2026-10 批1（001 §70）：'吉庆' 删除——《协纪》卷三十六·辨讹钦定判伪
        # （《选择宗镜》「满德吉庆为伪吉日……毋庸深辨」）。
        
        # 2026-10 A1：'鸣吠日'/'鸣吠对日' 同名重加删除（基类月作用域统一
        # 注册，旧名「鸣犬日/对」已正名，谓词收为 13/11 典载日柱）。

        # 2026-10 A1：'天恩' 同名重加删除——天恩已收口基类日作用域单点注册。
        
        # 旺日
        if self._is_wangri(sizhu):
            self._add_shensha('旺日', 10, '旺日入宅吉')
        
        # ===== 补充缺失的凶煞检查 =====
        
        # 丧门（主丧亡，忌入宅）
        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '丧门日忌入宅')
        
        # 吊客（主吊唁，忌入宅）
        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '吊客日忌入宅')
        
        # 病符（主疾病，忌入宅）
        if self._is_bingfu(sizhu):
            self._add_shensha('病符', -12, '病符日忌入宅')
        
        # 官符（主官讼，忌入宅）
        if self._is_guanfu(sizhu):
            self._add_shensha('官符', -10, '官符日忌入宅')
        
        # 五鬼（主耗散）
        if self._is_wugui(sizhu):
            self._add_shensha('五鬼', -15, '五鬼日主耗散，忌入宅')
        
        # 月虚（主虚耗）
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚日主虚耗，忌入宅')
        
        # 八专（主消耗）
        if self._is_bazhuan(sizhu):
            self._add_shensha('八专', -15, '八专日主消耗，忌入宅')
        
        # 四击（《协纪》卷五「春戌夏丑秋辰冬未」，月神比日支；
        # 2026-10 A6-5 由注册名「四忌」改名归宗为典载正名「四击」）
        if self._is_siji(sizhu):
            self._add_shensha('四击', -12, '四击日忌入宅')
    
    def _check_special_shensha(self, sizhu, owners, **kwargs):
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

    # 归忌 _is_guiji 已删除（2026-10 A5 收口）：本 override 口径（孟月丑/
    # 仲月寅/季月子）与典载一致且正确，收敛回归基类 is_guiji_by_zhi 单点
    # 出口（《协纪·历例》），基类旧"月支前七位"偏移错已同步修复。

    def _is_wangwang(self, sizhu):
        """往亡日（《协纪》口诀"正寅二巳三申四亥五卯六午七酉八子
        九辰十未十一戌十二丑"，月支查日支；委托单点出口
        is_wangwang_by_zhi）。
        """
        return is_wangwang_by_zhi(sizhu.get('month_zhi', ''),
                                  sizhu.get('day_zhi', ''))
    
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
        """天狗日 - 根据《钦定协纪辨方书》，天狗为建除十二神中的"满"日"""
        try:
            from ..shensha.marriage_shensha import get_jianchu
            if 'date' in sizhu:
                jianchu = get_jianchu(sizhu['date'])
                return jianchu == '满'
        except Exception as e:
            # 回退方案：使用月支起建法计算满日
            month_zhi = sizhu['month_zhi']
            day_zhi = sizhu['day_zhi']
            zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
            if month_zhi in zhi_order and day_zhi in zhi_order:
                month_idx = zhi_order.index(month_zhi)
                day_idx = zhi_order.index(day_zhi)
                # 建除十二神顺序：建、除、满、平、定、执、破、危、成、收、开、闭
                # "满"是第2位(index=2)
                offset = (day_idx - month_idx) % 12
                return offset == 2
        return False
    
    # _is_fuduan 死桩已删除（2026-10 A6-3）：旧"return False（伏断即危日，
    # 无权威依据已禁用）"经 self 分派屏蔽基类月作用域注册，致入宅/移徙
    # 伏断 0 命中；现继承基类 _is_fuduan（is_fuduan_by_zhi，六害口径）。

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
        """大耗日
        传统大耗日规则（依据《协纪辨方书》）：
        - 大耗日为土府日之次日
        - 土府日映射：寅月辰日、卯月巳日、辰月午日、巳月未日
                     午月申日、未月酉日、申月戌日、酉月亥日
                     戌月子日、亥月丑日、子月寅日、丑月卯日
        - 大耗日忌动土、修造、嫁娶、入宅等大事
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        zh_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        tufu2_map = {
            '寅': '辰', '卯': '巳', '辰': '午', '巳': '未',
            '午': '申', '未': '酉', '申': '戌', '酉': '亥',
            '戌': '子', '亥': '丑', '子': '寅', '丑': '卯'
        }
        tufu2_zhi = tufu2_map.get(month_zhi)
        if not tufu2_zhi:
            return False
        tufu2_idx = zh_list.index(tufu2_zhi)
        dahao_zhi = zh_list[(tufu2_idx + 1) % 12]
        return day_zhi == dahao_zhi

    def _is_xiaohao(self, sizhu):
        """小耗日
        传统小耗日规则（依据《协纪辨方书》）：
        - 小耗日为大耗日之次日
        - 大耗日为土府日之次日
        - 小耗日忌求财、交易、出行等
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        zh_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        tufu2_map = {
            '寅': '辰', '卯': '巳', '辰': '午', '巳': '未',
            '午': '申', '未': '酉', '申': '戌', '酉': '亥',
            '戌': '子', '亥': '丑', '子': '寅', '丑': '卯'
        }
        tufu2_zhi = tufu2_map.get(month_zhi)
        if not tufu2_zhi:
            return False
        tufu2_idx = zh_list.index(tufu2_zhi)
        xiaohao_zhi = zh_list[(tufu2_idx + 2) % 12]
        return day_zhi == xiaohao_zhi
    
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
        """天德日
        比较维度（2026-09-19 锚点③修复）：天干型比日干；
        地支型（卯月申/午月亥/酉月寅/子月巳，四维月取宫内地支）比日支。
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']

        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
        }

        tiande = tiande_map.get(month_zhi)
        if tiande in DI_ZHI:
            return sizhu.get('day_zhi', '') == tiande
        return day_gan == tiande
    
    # _is_yuede 内嵌表已删除：原表与基类/工具函数 YUEDE 权威表逐字一致（纯表副本），
    # 2026-09-18 拍板方案A改继承基类统一表（与天赦/岁煞收口同手法），行为零变化。
    # 2026-10 A6-4 D 批次：原 _is_yima override（仅年支）已删除，改继承
    # 基类仅月支口径（《协纪》卷六：驿马为月神，正月起申逆行四孟）。
    
    def _is_tiande_he(self, sizhu):
        """天德合日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        # 天德
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
        }
        
        tiande = tiande_map.get(month_zhi, '')
        if not tiande:
            return False

        # 天德合：与天德五行相合
        he_map = {'甲': '己', '乙': '庚', '丙': '辛', '丁': '壬', '戊': '癸',
                 '己': '甲', '庚': '乙', '辛': '丙', '壬': '丁', '癸': '戊',
                 '寅': '亥', '申': '巳', '亥': '寅', '巳': '申'}

        tiande_he = he_map.get(tiande, '')
        # 2026-09-19 锚点③修复：天干型天德比日干（五合）；
        # 地支型天德其合为地支（六合），须比日支（原比日干恒为 False）
        if tiande_he in DI_ZHI:
            return sizhu.get('day_zhi', '') == tiande_he
        return day_gan == tiande_he
    
    def _is_yuede_he(self, sizhu):
        """月德合日"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        # 月德
        yuede_map = {
            '寅': '丙', '午': '丙', '戌': '丙',
            '申': '壬', '子': '壬', '辰': '壬',
            '巳': '庚', '酉': '庚', '丑': '庚',
            '亥': '甲', '卯': '甲', '未': '甲'
        }
        
        yuede = yuede_map.get(month_zhi, '')
        if not yuede:
            return False
        
        # 月德合：与月德五行相合
        he_map = {'甲': '己', '乙': '庚', '丙': '辛', '丁': '壬', '戊': '癸',
                 '己': '甲', '庚': '乙', '辛': '丙', '壬': '丁', '癸': '戊'}
        
        yuede_he = he_map.get(yuede, '')
        return day_gan == yuede_he

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
    
    def _is_shie_dabai(self, sizhu):
        """十恶大败日"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    def _is_baihu_zhonggong(self, sizhu):
        """白虎入中宫
        注：传统"白虎入中宫"有固定推算方法（如九宫飞星），不是简单按月支对应日支。
        当前映射表缺乏依据，已禁用。
        如需使用，请实现正确的九宫飞星算法。
        """
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
        """母仓日
        传统母仓日规则（依据《协纪辨方书》）：
        - 春月（寅卯辰月）：亥、子日
        - 夏月（巳午未月）：寅、卯日
        - 秋月（申酉戌月）：辰、戌、丑、未日
        - 冬月（亥子丑月）：申、酉日
        
        母仓日宜祭祀、祈福、纳财、入宅等吉事。
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        # 传统母仓日映射
        mucang_map = {
            '寅': ['亥', '子'],
            '卯': ['亥', '子'],
            '辰': ['亥', '子'],
            '巳': ['寅', '卯'],
            '午': ['寅', '卯'],
            '未': ['寅', '卯'],
            '申': ['辰', '戌', '丑', '未'],
            '酉': ['辰', '戌', '丑', '未'],
            '戌': ['辰', '戌', '丑', '未'],
            '亥': ['申', '酉'],
            '子': ['申', '酉'],
            '丑': ['申', '酉']
        }

        return day_zhi in mucang_map.get(month_zhi, [])
    
    def _is_xiangri(self, sizhu):
        """相日
        注：传统相日映射与当前实现可能不符。
        传统相日：春（寅卯辰月）午未、夏（巳午未月）申酉、秋（申酉戌月）亥子、冬（亥子丑月）寅卯。
        当前实现可能错误，仅供参考。
        """
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
