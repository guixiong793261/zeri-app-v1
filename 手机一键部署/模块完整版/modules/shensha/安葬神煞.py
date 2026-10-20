# -*- coding: utf-8 -*-
"""
================================================================================
安葬神煞模块
================================================================================
实现安葬择日专用神煞的检查逻辑
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
    from ..工具函数 import DI_ZHI
except ImportError:
    from 神煞基类 import ShenShaChecker, is_wangwang_by_zhi
    from 工具函数 import DI_ZHI

class BurialShenShaChecker(ShenShaChecker):
    # P1-5（2026-10-18）：安葬不忌土瘟（陈书 p748「止忌破土不忌安葬」+协纪卷十一
    # 安葬忌列无土族煞）——关闭基类通用链土瘟发射；docs/P1-5_安葬土瘟_对勘.md，001 §117
    _TUWEN_DISABLED = True
    """安葬神煞检查器"""
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        
        year_zhi = sizhu.get('year_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        # 年重丧（按年支和日干查）
        if year_zhi and day_gan and self._is_nian_zhongsang(sizhu):
            self._add_shensha('年重丧', -30, '年重丧大凶，绝对不可用')

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 年干比日干典载口径）。

        # 黄幡
        if self._is_huangfan(sizhu):
            self._add_shensha('黄幡', -15, '黄幡主缠绕，凶')
        
        # 豹尾
        if self._is_baowei(sizhu):
            self._add_shensha('豹尾', -12, '豹尾主损伤，凶')
        
        # 丧门
        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '丧门主丧事，凶')
        
        # 吊客
        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '吊客主丧事，凶')
        
        # 病符×安葬已删（病符批，2026-10-20，001 §141）：三库病符无日课普适忌
        # 明文（皆方位/年神语境），拍板「删日课通道病符注册」。发射原为：
        #     if self._is_bingfu(sizhu):
        #         self._add_shensha('病符', -12, '病符主疾病，凶')
        
        # 官符
        if self._is_guanfu(sizhu):
            self._add_shensha('官符', -10, '官符主口舌是非，凶')
        
        # 五鬼
        if self._is_wugui(sizhu):
            self._add_shensha('五鬼', -15, '五鬼主灾祸，凶')

        # 大煞发射已删（2026-10-18 月家P1：协纪卷十仅忌军事，安葬超范围；
        # docs/月家P1_大煞八专四击_对勘.md）

        # 力士
        if self._is_lishi(sizhu):
            self._add_shensha('力士', -10, '力士主阻碍，凶')
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        month_zhi = sizhu.get('month_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        # 重丧（按月查日干）
        if month_zhi and day_gan and self._is_zhongsang(sizhu):
            self._add_shensha('重丧', -30, '重丧日大凶，绝对不宜安葬')
        
        # 三丧（按季节查日支）
        if day_zhi and self._is_sansang(sizhu):
            self._add_shensha('三丧', -25, '三丧日不宜安葬')
        
        # 复日（重丧类）
        if day_zhi and self._is_furi(sizhu):
            self._add_shensha('复日', -25, '复日重丧，不宜安葬')
        
        # 往亡日
        if month_zhi and day_zhi and self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日忌安葬、出行')
        
        # 2026-10 A7：'天吏日' 异名分支删除（原私有 _is_tianli override 用
        # "正卯二寅三丑…"非典载表）。基类月作用域已按典载《协纪》卷六
        # "正月起酉，逆行四仲"（三合死气位）注册 '天吏' -15。
        # 2026-10 批2（001 §71）：'致死日' 全删——致死即天吏同位异名
        # （《协纪》卷六月神表「天吏【致死】」、卷十按语「天吏者三合之死气
        # 也故又为致死」「天吏又名致死」；《考原》致死条曹震圭「与天吏同」），
        # 原 _is_zhisi "正未二申…十二午"（正月起未顺行）表三库均无载，
        # 谓词与注册一并移除；('安葬','天吏日') 悬空条目同批收口。

        # 月破（已在基类中检查，但安葬需特别强调）
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -30, '月破日诸事不宜，安葬大忌')

        # 2026-10 A1：'月空' 同名重加删除（基类月作用域统一注册，
        # 月神比日干典载口径）。

        # 2026-10 批4（001 §74）：'吉期' 重加删除——基类月作用域已统一
        # 注册 '吉期' +10（E3 修正后委托典载《历例》"常居月建前一辰"表），
        # 本块 super 先行后同名重加被 _add_shensha 先到先得去重，从未生效。
        
        # 2026-10 批7b（001 §80.8）：'益后'/'续世' 重加删除——基类
        # _check_month_shensha 已统一注册 +12/+10（批7a 委托典载表），本块
        # 同方法 super 先行后同名重加被 _add_shensha 先到先得去重，从未生
        # 效（死链）。删除零行为差，运行时实证见 001 §80.8。

        # 要安
        if self._is_yaoan(sizhu):
            self._add_shensha('要安', 8, '要安吉日，利于安葬')
        
        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 15, '不将日安葬大吉')
        
        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌凶日，不宜安葬')
        
        # 月虚
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚凶日，不宜安葬')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -15, '月刑凶日，不宜安葬')
        
        # 月害
        if self._is_yuehai(sizhu):
            self._add_shensha('月害', -15, '月害凶日，不宜安葬')
        
        # 大时条目已删（2026-10-18 P2 删除批，001 §122）：大时×安葬三库无载
        # （docs/月家P2_月害大时往亡五墓_续取证.md §六）；本行原为死链（基类
        # 通用链占位），基类通用链事项排除后隔离（001 §120）。
        # 月害（上行）与五墓（下文）系有载确认项，保留不动（基类未排除安葬）。
        
        # 四废
        if self._is_sifei(sizhu):
            self._add_shensha('四废', -15, '四废凶日，不宜安葬')

        # 真四忌（《历例》「春甲子、夏丙子、秋庚子、冬壬子」，干支并论；
        # 2026-10 A6-5 新建补注册：典载四忌忌安葬；本软件仅嫁娶/安葬注册，
        # 与四击（春戌夏丑秋辰冬未）为两个独立神煞）
        if self._is_siji_ji(sizhu):
            self._add_shensha('四忌', -12, '四忌日忌安葬（春甲子夏丙子秋庚子冬壬子）')
        
        # 五墓
        if self._is_wumu(sizhu):
            self._add_shensha('五墓', -12, '五墓凶日，不宜安葬')
        
        # 受死日发射已删（2026-10-20 受死日删除批，001 §145）：陈书 p54
        # 「丧塟即不忌」、p748「即受死日亦不忌安塟」、p152「宜安塟」三条明载
        # 不忌安葬（快照 docs/影响面快照_受死日删除候选.md §一），基类日块
        # 同步加 _std_event 门控。原发射为：
        #     if self._is_shousi_day(sizhu):
        #         self._add_shensha('受死日', -22, '受死日大凶，绝对不可安葬')
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']
        
        # ===== 极凶日（安葬绝对禁忌）=====

        # 十恶大败发射行已注释（2026-10-19 全删批·一档，001 §139）：三库无
        # 「十恶大败」普适日课忌明文（取证 aa47dcd／快照 2ca7b4e；协纪
        # 「然惟随各年及本命避之」属本命避忌，非日课普适扣分）；谓词保留作无禄日载体。
        # if self._is_shie_dabai(sizhu):
        #     self._add_shensha('十恶大败', -30, '十恶大败日，诸事不宜，安葬大忌')

        # 伏断日由基类月作用域统一注册（A6-3 同名分支删除，super 先注册必被去重）

        # ===== 凶煞 =====

        # 土瘟条目已删（2026-10-18 P1-5 零典据删除：陈书 p748「土禁土府土瘟土符
        # 止忌破土不忌安葬」明言不忌；协纪全书土瘟仅建除满日小吉语境2处、考原1处
        # 均无「忌安葬」，卷十一安葬忌列不含任何土族煞；docs/P1-5_安葬土瘟_对勘.md，
        # 001 §112）

        # 八座日
        if self._is_bazuori(sizhu):
            self._add_shensha('八座日', -12, '八座日不宜安葬')
        
        # ===== 吉日 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德吉星，安葬大吉')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德吉星，安葬大吉')
        
        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合，安葬吉')
        
        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合，安葬吉')
        
        # 2026-10 A4：三奇同名重加删除（基类 super 日块单点注册，此块从未生效）。

        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星到座，安葬吉')

        # 2026-10 A1：'鸣吠日'/'鸣吠对日' 重加删除——基类月作用域已按典载
        # 13/11 日柱统一注册（安葬取 SHENSHA_SCORES 既有 15/10 键）；本类
        # 旧 _is_mingfei 为连续 24 日错表（2026 端到端 149 命中），方法删除。

        # 不将日
        if self._is_bujiang(sizhu):
            self._add_shensha('不将日', 15, '不将日安葬可用')
        
        # 六合
        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 12, '六合吉日，利于安葬')
        
        # 三合
        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '三合吉日，利于安葬')
        
        # 驿马
        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '驿马吉日，利于安葬')

        # 2026-10 A1：'天马' 同名重加删除（典载天马为月神，基类月作用域
        # 注册）；旧名「鸣犬日/对」重加删除（与基类月作用域典载鸣吠正名
        # 同源同日，曾异名双扣）。

        # 天赦
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦大德，安葬大吉')

        # 母仓
        if self._is_mucang(sizhu):
            self._add_shensha('母仓', 10, '母仓吉日，利于安葬')

    def _check_special_shensha(self, sizhu, owners, **kwargs):
        """检查特殊神煞（与亡者相关）"""
        if not owners:
            return
        
        for owner in owners:
            # 获取亡者生肖
            owner_zodiac = owner.get('生肖', '')
            if not owner_zodiac:
                continue
            
            # 的呼日（与亡者生肖相冲）
            if self._is_dihu(sizhu, owner_zodiac):
                self._add_shensha('的呼日', -15, f'的呼日与亡者生肖({owner_zodiac})相冲，呼人')
            
            # 人呼日（与孝子生肖相冲）
            if self._is_renhu(sizhu, owner_zodiac):
                self._add_shensha('人呼日', -12, f'人呼日与亡者生肖({owner_zodiac})相关')
            
            # 亡者生肖与日支相冲
            if self._is_owner_chong(sizhu, owner_zodiac):
                self._add_shensha('亡者相冲', -20, f'日支与亡者生肖({owner_zodiac})相冲，大凶')
            
            # 亡者生肖与日支相合
            if self._is_owner_he(sizhu, owner_zodiac):
                self._add_shensha('亡者相合', 10, f'日支与亡者生肖({owner_zodiac})相合，吉')
    
    # ===== 重丧类神煞 =====
    
    def _is_zhongsang(self, sizhu):
        """
        是否重丧日（按月查日干）
        口诀：正七连庚甲，二八乙辛当，五十一丁癸，四十丙壬方，三六九十二，戊己是重丧
        即：正月、七月逢庚日、甲日；二月、八月逢乙日、辛日；以此类推
        """
        month_zhi = sizhu.get('month_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        
        # 月份对应的天干映射
        zhongsang_map = {
            '寅': ['庚', '甲'],  # 正月
            '卯': ['乙', '辛'],  # 二月
            '辰': ['戊', '己'],  # 三月
            '巳': ['丙', '壬'],  # 四月
            '午': ['丁', '癸'],  # 五月
            '未': ['戊', '己'],  # 六月
            '申': ['庚', '甲'],  # 七月
            '酉': ['乙', '辛'],  # 八月
            '戌': ['戊', '己'],  # 九月
            '亥': ['丙', '壬'],  # 十月
            '子': ['丁', '癸'],  # 十一月
            '丑': ['戊', '己']   # 十二月
        }
        
        return day_gan in zhongsang_map.get(month_zhi, [])
    
    def _is_nian_zhongsang(self, sizhu):
        """
        是否年重丧（按年支查日干）
        口诀与月重丧类似，但以年支为准
        """
        year_zhi = sizhu.get('year_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        
        # 年支对应的天干映射（与月重丧相同规律）
        nian_zhongsang_map = {
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
        
        return day_gan in nian_zhongsang_map.get(year_zhi, [])
    
    def _is_sansang(self, sizhu):
        """
        是否三丧日（按季节查日支）
        口诀：春辰夏未秋戌冬丑
        即：春季（寅卯辰月）逢辰日，夏季（巳午未月）逢未日，秋季（申酉戌月）逢戌日，冬季（亥子丑月）逢丑日
        """
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']
        
        # 按季节判断
        if month_zhi in ['寅', '卯', '辰']:  # 春季
            return day_zhi == '辰'
        elif month_zhi in ['巳', '午', '未']:  # 夏季
            return day_zhi == '未'
        elif month_zhi in ['申', '酉', '戌']:  # 秋季
            return day_zhi == '戌'
        elif month_zhi in ['亥', '子', '丑']:  # 冬季
            return day_zhi == '丑'
        return False
    
    def _is_furi(self, sizhu):
        """
        是否复日（重丧类）
        复日：正月甲日、二月乙日、三月丙日……依此类推
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        
        furi_map = {
            '寅': '甲', '卯': '乙', '辰': '丙',
            '巳': '丁', '午': '戊', '未': '己',
            '申': '庚', '酉': '辛', '戌': '壬',
            '亥': '癸', '子': '甲', '丑': '乙'
        }
        return day_gan == furi_map.get(month_zhi)
    
    # ===== 其他凶煞 =====
    
    def _is_wangwang(self, sizhu):
        """是否往亡日（《协纪》口诀"正寅二巳三申四亥五卯六午七酉八子
        九辰十未十一戌十二丑"，月支查日支；委托单点出口
        is_wangwang_by_zhi）。
        """
        return is_wangwang_by_zhi(sizhu.get('month_zhi', ''),
                                  sizhu.get('day_zhi', ''))
    
    # 2026-10 批2（001 §71）：_is_zhisi 谓词删除——致死即天吏同位异名
    # （《协纪》卷六月神表「天吏【致死】」+卷十按语「故又为致死」；
    # 《考原》致死条「正月起酉逆行四仲」曹震圭「与天吏同」），
    # 原 "正未二申…十二午"（正月起未顺行十二辰）表三库均无载。
    
    def _is_yuexing(self, sizhu):
        """是否月刑（月支与日支相刑）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        xing_map = {
            '寅': '巳', '巳': '申', '申': '寅',
            '丑': '戌', '戌': '未', '未': '丑',
            '子': '卯', '卯': '子',
            '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'
        }
        return day_zhi == xing_map.get(month_zhi)
    
    def _is_yuehai(self, sizhu):
        """是否月害（月支与日支相害）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        return day_zhi == hai_map.get(month_zhi)
    
    def _is_bazuori(self, sizhu):
        """是否八座日"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        bazuori_map = {
            '寅': '辰', '卯': '巳', '辰': '午', '巳': '未',
            '午': '申', '未': '酉', '申': '戌', '酉': '亥',
            '戌': '子', '亥': '丑', '子': '寅', '丑': '卯'
        }
        return day_zhi == bazuori_map.get(month_zhi)
    
    # ===== 极凶日 =====

    # 【保留·无禄日历法概念载体】（2026-10-19 全删批·一档）：起例 10 干支日与
    # 协纪/考原无禄日 12/12 全等，概念合典据，谓词保留不删；日课扣分发射行
    # 已全部注释清零（三库无普适日忌明文），规则引擎残留引用随二档批删除。
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败日"""
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        day_pillar = day_gan + day_zhi
        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai
    
    # _is_fuduan 已删除（2026-10 A6-3）：旧为"日干查日支"异表
    # （甲戌/乙酉/丙申/丁未/戊午/己巳/庚辰/辛卯/壬寅/癸丑，2025-2027 共 182
    # 命中，与典载六害口径无关）；统一继承基类 _is_fuduan（月支相害日支）。

    # ===== 吉日 =====

    # 2026-10 A1：旧 _is_mingfei（丙寅至己丑连续 24 日错表，2026 端到端
    # 149 命中）与 _is_mingfeidui（6 日错表）已删除——鸣吠日 13 干支、
    # 鸣吠对日 11 干支收口到 神煞基类.is_mingfei_by_pillar /
    # is_mingfeidui_by_pillar（《协纪》卷五／卷九），注册统一走基类月作用域。

    # 2026-10 A6-4 批B：旧 _is_bujiang（干支阴阳法，与嫁娶神煞旧实现逐字同一副本
    # A'）已删除，统一继承基类 _is_bujiang（委托 is_bujiang_by_ganzhi，查唯一权威表
    # _BUJIANG_TABLE），与评分/规则层 marriage_shensha.is_bujiang_day 同表同口径。

    # ===== 亡者相关检查 =====
    
    def _is_dihu(self, sizhu, owner_zodiac):
        """
        是否的呼日（与亡者生肖相冲）
        的呼日：日支与亡者生肖相冲
        """
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        
        if owner_zodiac not in zh_list:
            return False
        
        idx = zh_list.index(owner_zodiac)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_renhu(self, sizhu, owner_zodiac):
        """
        是否人呼日（与孝子生肖相冲，简化处理为与亡者生肖相关）
        实际应根据孝子生肖判断，这里简化处理
        """
        # 简化：与亡者生肖相害的日子
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        
        if owner_zodiac not in zh_list:
            return False
        
        # 六害关系
        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        
        return day_zhi == hai_map.get(owner_zodiac)
    
    def _is_owner_chong(self, sizhu, owner_zodiac):
        """日支与亡者生肖是否相冲"""
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        
        if owner_zodiac not in zh_list:
            return False
        
        idx = zh_list.index(owner_zodiac)
        chong = zh_list[(idx + 6) % 12]
        return day_zhi == chong
    
    def _is_owner_he(self, sizhu, owner_zodiac):
        """日支与亡者生肖是否相合"""
        day_zhi = sizhu.get('day_zhi', '')
        
        # 六合关系
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        return day_zhi == liuhe_map.get(owner_zodiac)
