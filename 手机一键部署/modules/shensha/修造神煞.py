# -*- coding: utf-8 -*-
"""
================================================================================
修造神煞模块
================================================================================
实现修造择日专用神煞的检查逻辑
包含：土府、地囊、土王用事等

使用方法:
    1. 作为模块导入: from modules.shensha.修造神煞 import 修造神煞Checker
    2. 直接运行: python -m modules.shensha.修造神煞
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
    from .神煞基类 import ShenShaChecker, is_tuwang_yongshi_by_date
    from ..工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE
except ImportError:
    from 神煞基类 import ShenShaChecker, is_tuwang_yongshi_by_date
    from 工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE


class ConstructionShenShaChecker(ShenShaChecker):
    """修建神煞检查器"""
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 岁破（已在基类中检查）
        
        # 太岁堆黄
        if self._is_taisui_duihuang(sizhu):
            self._add_shensha('太岁堆黄', -15, '忌动土修造')
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 三煞
        if self._is_sansha(sizhu):
            self._add_shensha('三煞', -20, '修建大忌，犯之主灾祸')
        
        # 鲁班煞（按季节判断）
        if self._is_lubansha(sizhu):
            self._add_shensha('鲁班煞', -20, '修建不宜，犯之主损工匠')
        
        # 土符
        if self._is_tufu(sizhu):
            self._add_shensha('土符', -20, '忌动土、修造，犯之主灾')
        
        # 土府
        if self._is_tufu2(sizhu):
            self._add_shensha('土府', -20, '忌动土，犯之主败')
        
        # 土瘟
        if self._is_tuwen(sizhu):
            self._add_shensha('土瘟', -20, '忌动土、修造，犯之主病')
        
        # 地囊
        if self._is_dinang(sizhu):
            self._add_shensha('地囊', -25, '忌动土、开渠，犯之主败')
        
        # 月破（已在基类中检查）
        
        # 大耗
        if self._is_dahao(sizhu):
            self._add_shensha('大耗', -20, '忌动土，犯之主耗财')
        
        # 小耗
        if self._is_xiaohao(sizhu):
            self._add_shensha('小耗', -15, '忌动土，犯之主小损')
        
        # ===== 补充年神检查（劫煞/灾煞为年支查表，不属月神；因基类
        # _check_year_shensha 已查过并去重，此处重加仅保证事项专属文案） =====

        # 劫煞（年神）
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -25, '劫煞日忌修造、动土')

        # 灾煞（年神）
        if self._is_zaijiesha(sizhu):
            self._add_shensha('灾煞', -25, '灾煞日忌修造、动土')
        
        # 月煞
        if self._is_yuesha(sizhu):
            self._add_shensha('月煞', -20, '月煞日忌修造')
        
        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌日忌修造')
        
        # 大时
        if self._is_dashi(sizhu):
            self._add_shensha('大时', -12, '大时日忌修造')
        
        # 天吏
        if self._is_tianli(sizhu):
            self._add_shensha('天吏', -15, '天吏日忌修造')
        
        # 四废
        if self._is_sifei(sizhu):
            self._add_shensha('四废', -15, '四废日忌修造、动土')

        # 2026-10 A3-2b：'五墓' 死分支删除（原 -20 死分支，基类 super 先行已注册
        # 五墓且事项标准修造无键，有效值恒为基类兜底 -12；对齐事项标准 -12）。
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 凶煞 =====
        
        # 天贼
        if self._is_tianzei(sizhu):
            self._add_shensha('天贼', -20, '忌修造、动土，犯之主耗财')
        
        # 地贼
        if self._is_dizei(sizhu):
            self._add_shensha('地贼', -15, '忌修造、动土，犯之主失盗')
        
        # 十恶大败
        if self._is_shie_dabai(sizhu):
            self._add_shensha('十恶大败', -30, '忌动土修造，犯之主败')

        # 伏断日由基类月作用域统一注册（A6-3 死桩与同名分支删除：
        # 旧 return False 经 self 分派屏蔽基类注册，致修造系 0 命中）

        # 将军箭
        if self._is_jiangjunjian(sizhu):
            self._add_shensha('将军箭', -20, '忌修造，犯之主伤')

        # 杀师日（修造大忌，伤工匠）
        if self._is_shashi(sizhu):
            self._add_shensha('杀师日', -30, '修造大忌，犯之伤害工匠')

        # 杀师时（时柱逢戊午，部分严谨修造流派大忌，伤工匠）
        if sizhu.get('hour_gan') == '戊' and sizhu.get('hour_zhi') == '午':
            self._add_shensha('杀师时', -30, '时辰逢戊午为杀师时，对现场工匠不利，宜避开')

        # ===== 吉神 =====

        # 天德合
        if self._is_tiandehe(sizhu):
            self._add_shensha('天德合', 15, '动土修造吉利')
        
        # 月德合
        if self._is_yuedehe(sizhu):
            self._add_shensha('月德合', 12, '动土修造吉利')
        
        # 天愿
        if self._is_tianyuan(sizhu):
            self._add_shensha('天愿', 12, '天愿吉星，修造吉')
        
        # 月恩
        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩吉星，修造吉')
        
        # 四相
        if self._is_sixiang(sizhu):
            self._add_shensha('四相', 10, '四相吉日，修造吉')
        
        # 时德
        if self._is_shide(sizhu):
            self._add_shensha('时德', 10, '时德吉日，修造吉')

        # 2026-10 A1：'天马' 同名重加删除（典载天马为月神，基类月作用域统一注册）。

        # 2026-10 A4：三奇同名重加删除（基类 super 日块单点注册，此块从未生效）。

        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星到座，修造吉')
        
        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '动土催吉，主迁动')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '动土吉利，主和合')
        
        # 六合
        if self._is_month_day_liuhe(sizhu):
            self._add_shensha('六合', 12, '动土吉利，主和谐')

        # 2026-10 A1：'鸣吠日'/'鸣吠对日' 重加删除——基类月作用域已按典载
        # 13/11 日柱统一注册（修造取 SHENSHA_SCORES 既有 15/10 键）；本类
        # 旧 _is_mingfei/_is_mingfeidui 为 6 日错表，方法一并删除收口到基类。

        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 15, '修造吉日')

        # ===== 补充缺失的吉神检查 =====

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 年干比日干典载口径；此处旧 default 12 与事项标准 15 不符，本就不生效）。

        # 岁合（主和合）
        if self._is_suihe(sizhu):
            self._add_shensha('岁合', 12, '岁合主和合，修造吉')
        
        # '天赦日'重加已删除（2026-09-18，001跟踪项13.2方案①）：基类
        # _check_day_shensha 已加'天赦'+25（本类日方法 super 先行且全路径必达），
        # 原异名重加致真天赦日 +50 双计；删除后走基类统一，天赦日=+25。
        # 拆舍经继承链自动同步修复；注意动土/通用的天赦加分为独立活分支，不适用本清理。

        # 2026-10 批7b（001 §80.8）：'益后'(+10)/'续世'(+8) 日块异分重加
        # 删除——基类月作用域已统一注册 '益后'+12/'续世'+10（批7a 委托典载
        # 表，经本类月块 super 先行发射），本块同名重加被 _add_shensha 先到
        # 先得去重，从未生效（死链）；且分值以 SHENSHA_SCORES 表为准，本块
        # 自定异分（+10/+8）双重不生效。删除零行为差，运行时实证见 001 §80.8。

        # 2026-10 批1（001 §70）：'吉庆' 删除——《协纪》卷三十六·辨讹钦定判伪
        # （《选择宗镜》「满德吉庆为伪吉日……毋庸深辨」）。
        
        # 2026-10 A1：'天恩' 同名重加删除——天恩已收口基类日作用域单点注册。

        # 2026-10 A1：第二处 '天马' 同名重加删除（与上一处同为死分支，
        # 典载天马已由基类月作用域统一注册）。

        # ===== 补充缺失的凶煞检查 =====
        
        # 丧门（主丧亡，忌修造）
        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '丧门日忌修造')
        
        # 吊客（主吊唁，忌修造）
        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '吊客日忌修造')
        
        # 病符（主疾病，忌修造）
        if self._is_bingfu(sizhu):
            self._add_shensha('病符', -12, '病符日忌修造')
        
        # 官符（主官讼，忌修造）
        if self._is_guanfu(sizhu):
            self._add_shensha('官符', -10, '官符日忌修造')
        
        # 五鬼（主耗散）
        if self._is_wugui(sizhu):
            self._add_shensha('五鬼', -15, '五鬼日主耗散，忌修造')
        
        # 月虚（主虚耗）
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚日主虚耗，忌修造')
        
        # 八专（主消耗）
        if self._is_bazhuan(sizhu):
            self._add_shensha('八专', -15, '八专日主消耗，忌修造')
        
        # 四击（《协纪》卷五「春戌夏丑秋辰冬未」，月神比日支；
        # 2026-10 A6-5 由注册名「四忌」改名归宗为典载正名「四击」）
        if self._is_siji(sizhu):
            self._add_shensha('四击', -12, '四击日忌修造')
        
        # 土瘟（四季土旺日）
        if self._is_tuwen(sizhu):
            self._add_shensha('土瘟', -20, '土瘟日忌动土修造')
        
        # 土王用事
        if self._is_tuwang(sizhu):
            self._add_shensha('土王用事', -18, '土王用事忌动土')
        
        # 刀砧煞
        if self._is_daozhen(sizhu):
            self._add_shensha('刀砧煞', -20, '刀砧煞忌修造，主伤工匠')
        
        # 斧头煞
        if self._is_futou(sizhu):
            self._add_shensha('斧头煞', -18, '斧头煞忌修造')
        
        # 木马煞
        if self._is_muma(sizhu):
            self._add_shensha('木马煞', -15, '木马煞忌修造')
        
        # 天地转煞
        if self._is_tiandizhuan(sizhu):
            self._add_shensha('天地转煞', -20, '天地转煞忌修造')
        
        # 山曜
        if self._is_shanyao(sizhu):
            self._add_shensha('山曜', -15, '山曜忌修造')

        # 2026-10 A3：'飞廉' 日作用域注册删除（典载飞廉为月神，
        # 已由基类月作用域统一注册）。
    
    def _check_hour_shensha(self, sizhu, **kwargs):
        """检查时神煞"""
        super()._check_hour_shensha(sizhu, **kwargs)

    def _check_special_shensha(self, sizhu, owners, **kwargs):
        """检查特殊神煞，主要处理事主（宅主/工匠）生肖与日课的冲合"""
        if not owners:
            return
        
        for i, owner in enumerate(owners):
            owner_zodiac = owner.get('生肖', '')
            owner_year_zhi = owner.get('年支', '')
            owner_name = owner.get('姓名', f'事主{i+1}')
            is_zhuzhu = owner.get('is_zhuzhu', False)  # 是否宅主/家长
            
            if not owner_zodiac and not owner_year_zhi:
                continue
            
            # 宅主/家长冲克权重更重
            base_penalty = 1.0
            if is_zhuzhu:
                base_penalty = 1.5  # 宅主冲克扣分乘1.5倍
            
            # 年支相冲
            year_zhi = sizhu['year_zhi']
            if self._is_chong(year_zhi, owner_year_zhi or owner_zodiac):
                penalty = int(-25 * base_penalty)
                self._add_shensha(f'年冲{owner_name}', penalty, f'年支与{owner_name}生肖相冲')
            
            # 月支相冲
            month_zhi = sizhu['month_zhi']
            if self._is_chong(month_zhi, owner_year_zhi or owner_zodiac):
                penalty = int(-15 * base_penalty)
                self._add_shensha(f'月冲{owner_name}', penalty, f'月支与{owner_name}生肖相冲')
            
            # 日支相冲
            day_zhi = sizhu['day_zhi']
            if self._is_chong(day_zhi, owner_year_zhi or owner_zodiac):
                penalty = int(-35 * base_penalty)
                self._add_shensha(f'日冲{owner_name}', penalty, f'日支与{owner_name}生肖相冲，大忌')
            elif self._is_liuhe(day_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'日合{owner_name}', 10, f'日支与{owner_name}生肖六合')
            elif self._is_sanhe_pair(day_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'日半三合{owner_name}', 5, f'日支与{owner_name}生肖半三合')
            
            # 时支相冲
            hour_zhi = sizhu.get('hour_zhi', '')
            if hour_zhi and self._is_chong(hour_zhi, owner_year_zhi or owner_zodiac):
                penalty = int(-12 * base_penalty)
                self._add_shensha(f'时冲{owner_name}', penalty, f'时支与{owner_name}生肖相冲')
            elif hour_zhi and self._is_liuhe(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时合{owner_name}', 6, f'时支与{owner_name}生肖六合')
            elif hour_zhi and self._is_sanhe_pair(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时半三合{owner_name}', 3, f'时支与{owner_name}生肖半三合')
    
    def _shengxiao_to_zhi(self, shengxiao):
        """生肖转换为地支"""
        shengxiao_map = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        return shengxiao_map.get(shengxiao)
    
    def _is_chong(self, zhi1, zhi2):
        """检查两个地支是否相冲"""
        if not zhi1 or not zhi2:
            return False
        
        # 如果zhi2是生肖，转换为地支
        if zhi2 not in DI_ZHI:
            zhi2 = self._shengxiao_to_zhi(zhi2)
            if not zhi2:
                return False
        
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return zhi1 == chong_map.get(zhi2)
    
    def _is_liuhe(self, zhi1, zhi2):
        """检查两个地支是否六合"""
        if not zhi1 or not zhi2:
            return False
        
        # 如果zhi2是生肖，转换为地支
        if zhi2 not in DI_ZHI:
            zhi2 = self._shengxiao_to_zhi(zhi2)
            if not zhi2:
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
        return liuhe_map.get(zhi1) == zhi2
    
    def _is_sanhe_pair(self, zhi1, zhi2):
        """检查两个地支是否半三合（用于事主冲合分析）"""
        if not zhi1 or not zhi2:
            return False
        
        # 如果zhi2是生肖，转换为地支
        if zhi2 not in DI_ZHI:
            zhi2 = self._shengxiao_to_zhi(zhi2)
            if not zhi2:
                return False
        
        # 三合（半三合）
        sanhe_sets = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
        for s in sanhe_sets:
            if zhi1 in s and zhi2 in s and zhi1 != zhi2:
                return True
        
        return False
    
    def _is_he(self, zhi1, zhi2):
        """检查两个地支是否相合（六合或三合）"""
        return self._is_liuhe(zhi1, zhi2) or self._is_sanhe_pair(zhi1, zhi2)

    # ===== 凶煞判断方法 =====
    
    def _is_sansha(self, sizhu):
        """是否三煞"""
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
        if year_zhi in SANSHA_MAP:
            sansha_indices = SANSHA_MAP[year_zhi]
            day_idx = zh_list.index(day_zhi)
            return day_idx in sansha_indices
        return False
    
    def _is_lubansha(self, sizhu):
        """是否鲁班煞（按季节判断）
        注：传统鲁班煞有多种说法，常见版本是按天干：
        春三月忌庚辛日，夏三月忌壬癸日，秋三月忌甲乙日，冬三月忌丙丁日。
        此处用地支版本，与常见版本不同，供参考使用。
        春季：亥、子日
        夏季：寅、卯日
        秋季：巳、午日
        冬季：申、酉日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 春季：寅卯辰月
        if month_zhi in ['寅', '卯', '辰']:
            return day_zhi in ['亥', '子']
        # 夏季：巳午未月
        elif month_zhi in ['巳', '午', '未']:
            return day_zhi in ['寅', '卯']
        # 秋季：申酉戌月
        elif month_zhi in ['申', '酉', '戌']:
            return day_zhi in ['巳', '午']
        # 冬季：亥子丑月
        elif month_zhi in ['亥', '子', '丑']:
            return day_zhi in ['申', '酉']
        return False
    
    def _is_tuwang_yongshi(self, sizhu):
        """是否土王用事（2026-10 批8a 修正：原实现把节气月支映射到公历月号
        ＋ monthrange 取公历月天数，节气月跨公历月导致判定失真）。

        典载口径（《神枢经》/《历例》"土於四立之前各旺一十八日"）：委托
        模块级单点出口 is_tuwang_yongshi_by_date，按公历日期查距下一个四立
        的天数∈[1, 18]。
        """
        return is_tuwang_yongshi_by_date(
            sizhu.get('year'), sizhu.get('month'), sizhu.get('day'))
    
    def _is_dahao(self, sizhu):
        """是否大耗
        传统大耗日规则（依据《协纪辨方书》）：
        - 大耗日为土府日之次日
        - 土府日映射：寅月辰日、卯月巳日、辰月午日、巳月未日
                     午月申日、未月酉日、申月戌日、酉月亥日
                     戌月子日、亥月丑日、子月寅日、丑月卯日
        - 大耗日忌动土、修造、嫁娶、入宅等大事
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
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
        """是否小耗
        传统小耗日规则（依据《协纪辨方书》）：
        - 小耗日为大耗日之次日
        - 大耗日为土府日之次日
        - 小耗日忌求财、交易、出行等
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI
        
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
    
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败
        十恶大败日：甲辰、乙巳、丙申、丁亥、戊戌、己丑、庚辰、辛巳、壬申、癸亥
        """
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi
        
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai

    # _is_fuduan 死桩已删除（2026-10 A6-3）：旧"return False（伏断即危日，
    # 无权威依据已禁用）"经 self 分派屏蔽基类月作用域注册，致修造/动土/拆舍
    # 伏断 0 命中；现继承基类 _is_fuduan（is_fuduan_by_zhi，六害口径）。

    def _is_jiangjunjian(self, sizhu):
        """是否将军箭
        注：将军箭有多个版本，此处为简化版本，仅供参考。
        传统版本可能更复杂，需结合时柱判断。
        将军箭：按月支推算
        寅月：卯日，卯月：辰日，辰月：巳日，巳月：午日
        午月：未日，未月：申日，申月：酉日，酉月：戌日
        戌月：亥日，亥月：子日，子月：丑日，丑月：寅日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        jiangjunjian_map = {
            '寅': '卯', '卯': '辰', '辰': '巳', '巳': '午',
            '午': '未', '未': '申', '申': '酉', '酉': '戌',
            '戌': '亥', '亥': '子', '子': '丑', '丑': '寅'
        }
        return day_zhi == jiangjunjian_map.get(month_zhi)

    def _is_shashi(self, sizhu):
        """是否杀师日（修造大忌，伤工匠）

        杀师日传统算法：
        1. 根据年支和月支的关系确定：
           - 子午卯酉年：辰戌丑未月为杀师月
           - 辰戌丑未年：寅申巳亥月为杀师月
           - 寅申巳亥年：丙丁壬癸月为杀师月
        2. 杀师之日：春戌夏丑秋辰冬未（四季月的丑、辰、戌、未日）

        这里采用简化版本：四季月（辰戌丑未）的特定日支为杀师日
        另一种常用算法：基于年支确定杀师之时
        """
        year_zhi = sizhu['year_zhi']
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        # 算法1：四季月（辰戌丑未月）的特定日支为杀师日
        # 口诀：春戌夏丑秋辰冬未
        # 春季（寅卯辰月）的戌日、夏季（巳午未月）的丑日
        # 秋季（申酉戌月）的辰日、冬季（亥子丑月）的未日
        season_to_month = {
            '寅': '戌', '卯': '戌', '辰': '戌',  # 春（寅卯辰月）：戌日
            '巳': '丑', '午': '丑', '未': '丑',  # 夏（巳午未月）：丑日
            '申': '辰', '酉': '辰', '戌': '辰',  # 秋（申酉戌月）：辰日
            '亥': '未', '子': '未', '丑': '未'   # 冬（亥子丑月）：未日
        }

        expected_day_zhi = season_to_month.get(month_zhi)
        if expected_day_zhi and day_zhi == expected_day_zhi:
            return True

        # 算法2：基于年支的杀师日
        # 子午年：卯酉月；卯酉年：子午月；辰戌年：丑未月；丑未年：辰戌月
        # 寅申年：巳亥月；巳亥年：寅申月
        year_to_month = {
            '子': ['卯', '酉'], '午': ['卯', '酉'],
            '卯': ['子', '午'], '酉': ['子', '午'],
            '辰': ['丑', '未'], '戌': ['丑', '未'],
            '丑': ['辰', '戌'], '未': ['辰', '戌'],
            '寅': ['巳', '亥'], '申': ['巳', '亥'],
            '巳': ['寅', '申'], '亥': ['寅', '申']
        }

        if year_zhi in year_to_month and month_zhi in year_to_month[year_zhi]:
            # 这些月份的特定日支为杀师日
            # 子午卯酉年：忌辰戌丑未日；辰戌丑未年：忌寅申巳亥日
            shashi_day_for_year = {
                '子': ['辰', '戌', '丑', '未'], '午': ['辰', '戌', '丑', '未'],
                '卯': ['辰', '戌', '丑', '未'], '酉': ['辰', '戌', '丑', '未'],
                '辰': ['寅', '申', '巳', '亥'], '戌': ['寅', '申', '巳', '亥'],
                '丑': ['寅', '申', '巳', '亥'], '未': ['寅', '申', '巳', '亥'],
                '寅': ['子', '午', '卯', '酉'], '申': ['子', '午', '卯', '酉'],
                '巳': ['子', '午', '卯', '酉'], '亥': ['子', '午', '卯', '酉']
            }
            if year_zhi in shashi_day_for_year and day_zhi in shashi_day_for_year[year_zhi]:
                return True

        return False

    def _is_taisui_duihuang(self, sizhu):
        """是否太岁堆黄
        太岁堆黄：按年支推算
        子年：丑日，丑年：寅日，寅年：卯日，卯年：辰日
        辰年：巳日，巳年：午日，午年：未日，未年：申日
        申年：酉日，酉年：戌日，戌年：亥日，亥年：子日
        """
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        
        zh_list = DI_ZHI
        idx = zh_list.index(year_zhi)
        duihuang = zh_list[(idx + 1) % 12]
        return day_zhi == duihuang
    
    # ===== 吉神判断方法 =====
    
    def _is_tiande(self, sizhu):
        """是否天德
        天德：按月支推算
        寅月：丁，卯月：申，辰月：壬，巳月：辛
        午月：亥，未月：甲，申月：癸，酉月：寅
        戌月：丙，亥月：乙，子月：巳，丑月：庚

        比较维度（2026-09-19 锚点③修复）：天干型比日干；
        地支型（卯月申/午月亥/酉月寅/子月巳，四维月取宫内地支）比日支。
        """
        from ..工具函数 import TIANDE
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        td = TIANDE.get(idx)
        if td in DI_ZHI:
            return sizhu.get('day_zhi', '') == td
        return day_gan == td
    
    def _is_yuede(self, sizhu):
        """是否月德
        月德：按月支推算
        寅午戌月：丙，申子辰月：壬，亥卯未月：甲，巳酉丑月：庚
        """
        from ..工具函数 import YUEDE
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        return day_gan == YUEDE.get(idx)
    
    def _is_tiandehe(self, sizhu):
        """是否天德合
        天德合：与天德相合的天干或地支
        五合规则：甲己合、乙庚合、丙辛合、丁壬合、戊癸合
        六合规则：寅亥合、申巳合

        比较维度（2026-09-19 锚点③修复）：天德为天干时比日干（五合）；
        天德为地支时（卯月申/午月亥/酉月寅/子月巳）比日支（六合），
        原实现地支型月恒返回 False。
        """
        from ..工具函数 import TIANDE
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        tiande = TIANDE.get(idx)

        if not tiande:
            return False

        # 五合天干
        wuhe = {'甲': '己', '己': '甲', '乙': '庚', '庚': '乙',
                '丙': '辛', '辛': '丙', '丁': '壬', '壬': '丁', '戊': '癸', '癸': '戊'}

        # 天德为天干时，日干为其五合即为天德合
        if tiande in wuhe:
            return day_gan == wuhe.get(tiande)

        # 天德为地支时，日支为其六合即为天德合
        liuhe = {'寅': '亥', '亥': '寅', '申': '巳', '巳': '申'}
        he = liuhe.get(tiande)
        if he:
            return sizhu.get('day_zhi', '') == he
        return False
    
    def _is_yuedehe(self, sizhu):
        """是否月德合
        月德合：与月德相合的天干
        丙合辛，壬合丁，甲合己，庚合乙
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        yuedehe_map = {
            '寅': '辛', '午': '辛', '戌': '辛',  # 丙合辛
            '申': '丁', '子': '丁', '辰': '丁',  # 壬合丁
            '亥': '己', '卯': '己', '未': '己',  # 甲合己
            '巳': '乙', '酉': '乙', '丑': '乙'   # 庚合乙
        }
        return day_gan == yuedehe_map.get(month_zhi)
    
    # 2026-10 A6-4 D 批次：原 _is_yima override（仅年支）已删除，改继承
    # 基类仅月支口径（《协纪》卷六：驿马为月神，正月起申逆行四孟）。
    # 年支驿马为年家方位神「岁马到山」，见修造神煞扩展._is_sui_ma_daoshan。
    
    def _is_sanhe(self, sizhu):
        """是否三合
        三合：申子辰合水，寅午戌合火，巳酉丑合金，亥卯未合木
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        sanhe_groups = [
            {'申', '子', '辰'},
            {'寅', '午', '戌'},
            {'巳', '酉', '丑'},
            {'亥', '卯', '未'}
        ]
        
        for group in sanhe_groups:
            if month_zhi in group and day_zhi in group and month_zhi != day_zhi:
                return True
        return False
    
    def _is_month_day_liuhe(self, sizhu):
        """是否六合（月支与日支）
        六合：子丑合，寅亥合，卯戌合，辰酉合，巳申合，午未合
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

    # 2026-10 A1：旧 _is_mingfei（庚午庚子庚申辛酉辛卯辛巳 6 日错表）与
    # _is_mingfeidui（丙子丙午丙寅丁卯丁酉丁亥 6 日错表）已删除——鸣吠日
    # 13 干支、鸣吠对日 11 干支收口到 神煞基类.is_mingfei_by_pillar /
    # is_mingfeidui_by_pillar（《协纪》卷五／卷九），注册统一走基类月作用域。

    def _is_bujiang(self, sizhu):
        """是否不将日
        
        注意：修造模块中不将日判断已禁用（返回 False）。
        原因：不将日为嫁娶专用吉日（阳将阴将之日），与修造、动土无直接关系。
        修造的主要吉神为天德、月德、三奇、将星等，不将日在修造中不作为重要参考。
        
        如需使用不将日判断，请在嫁娶模块中使用 marriage_shensha.is_bujiang_day()。
        """
        return False
    
    def _is_qinglong(self, sizhu):
        """青龙日：十二建星中的青龙"""
        day_zhi = sizhu['day_zhi']
        jianxing_order = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
        qinglong_map = {
            '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
            '辰': '午', '巳': '未', '午': '申', '未': '酉',
            '申': '戌', '酉': '亥', '戌': '子', '亥': '丑'
        }
        return day_zhi == qinglong_map.get(sizhu.get('month_zhi', ''))
    
    def _is_mingtang(self, sizhu):
        """明堂日：十二建星中的明堂"""
        day_zhi = sizhu['day_zhi']
        mingtang_map = {
            '子': '巳', '丑': '午', '寅': '未', '卯': '申',
            '辰': '酉', '巳': '戌', '午': '亥', '未': '子',
            '申': '丑', '酉': '寅', '戌': '卯', '亥': '辰'
        }
        return day_zhi == mingtang_map.get(sizhu.get('month_zhi', ''))
    
    def _is_jinkui(self, sizhu):
        """金匮日：十二建星中的金匮"""
        day_zhi = sizhu['day_zhi']
        jinkui_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == jinkui_map.get(sizhu.get('month_zhi', ''))
