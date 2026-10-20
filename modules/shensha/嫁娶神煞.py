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
    from .神煞基类 import ShenShaChecker, is_yanggongji_by_lunar, is_wangwang_by_zhi
    try:
        from ..工具函数 import DI_ZHI, TIAN_GAN
    except ImportError:
        # 尝试从modules目录导入
        import sys
        import os
        modules_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
        from 工具函数 import DI_ZHI, TIAN_GAN
except ImportError:
    # 直接运行时的导入
    import sys
    import os
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
    from 神煞基类 import ShenShaChecker, is_wangwang_by_zhi
    from 工具函数 import DI_ZHI, TIAN_GAN


class MarriageShenShaChecker(ShenShaChecker):
    """婚嫁神煞检查器"""
    
    def __init__(self):
        super().__init__()
        self.bride_gan = None
        self.groom_gan = None
        self.bride_zhi = None
        self.groom_zhi = None
    
    def check(self, sizhu, owners=None, **kwargs):
        """
        检查神煞（重写以先提取新娘/新郎信息）
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            **kwargs: 与基类签名保持一致（嫁娶不使用 zaozhu_mode 等造灶参数）
            
        Returns:
            list: 神煞列表
        """
        self.shensha_list = []
        
        # 先提取新娘/新郎信息
        if owners:
            for owner in owners:
                name = owner.get('姓名', '') or owner.get('name', '')
                gender = owner.get('性别', '') or owner.get('gender', '')
                zodiac = owner.get('生肖', '') or owner.get('zodiac', '')
                year_gan = owner.get('年干', '') or owner.get('year_gan', '')
                year_zhi = owner.get('年支', '') or owner.get('year_zhi', '')
                
                if gender == '女':
                    self.bride_gan = year_gan
                    self.bride_zhi = zodiac or year_zhi
                elif gender == '男':
                    self.groom_gan = year_gan
                    self.groom_zhi = zodiac or year_zhi
        
        # 然后检查神煞
        self._check_year_shensha(sizhu)
        self._check_month_shensha(sizhu)
        self._check_day_shensha(sizhu)
        self._check_hour_shensha(sizhu)
        self._check_special_shensha(sizhu, owners)
        return self.shensha_list
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        month_zhi = sizhu['month_zhi']
        
        # 月破（婚嫁大忌）
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -40, '月破日诸事不宜，婚嫁大忌')
        
        # 大利月（需女命年支）
        # 【D3 分值统一】大利月分值从+20统一为+30，与婚嫁评分算法(score_marriage_day)
        # 及评分器嫁娶路径中的大利月分值一致，避免【评分详情】(+30)与【神煞信息】(+20)矛盾。
        if self.bride_zhi and self._is_daliyue(sizhu):
            self._add_shensha('大利月', 30, '女命大利之月，婚嫁首选')
        
        # 小利月（需女命年支）
        if self.bride_zhi and self._is_xiaoliyue(sizhu):
            self._add_shensha('小利月', 15, '女命小利之月，婚嫁可用')
        
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
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞（嫁娶特有神煞先于基类发射，确保加重分值生效）"""
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
            self._add_shensha('受死日', -22, '受死日婚嫁大忌')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日忌婚嫁')
        
        # 重丧日 - 嫁娶大忌
        if self._is_zhongsang(sizhu):
            self._add_shensha('重丧日', -25, '重丧日婚嫁大忌')
        
        # 三娘煞（仅在有实际日期时检查）：按传统口径只有"真三娘煞"
        # （农历日与日干支同时满足，全年仅6天）才需回避；
        # 仅农历日相符的"假三娘煞"不再列为婚嫁禁忌
        if not sizhu.get('is_sizhu_input', False):
            if self._is_zhen_sanniang(sizhu):
                self._add_shensha('真三娘煞', -20, '真三娘煞日婚嫁大忌')
        
        # 黄沙日
        if self._is_huangsha(sizhu):
            self._add_shensha('黄沙日', -12, '黄沙日忌婚嫁')
        
        # 神号鬼哭日
        if self._is_shenhao(sizhu):
            self._add_shensha('神号日', -15, '神号日婚嫁不吉')
        if self._is_guiru(sizhu):
            self._add_shensha('鬼哭日', -15, '鬼哭日婚嫁不吉')
        
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

        # 天罡日/河魁日（妨翁姑日）
        # 天罡妨翁、河魁妨姑为嫁娶大忌；2026-10 α 与 D（婚嫁评分算法 -40）
        # 及 SHENSHA_SCORES('嫁娶') 对齐，原 -25 为漂移值
        if self._is_tiangang(sizhu):
            self._add_shensha('天罡日', -40, '天罡日妨翁，不利新郎父亲')
        if self._is_hekui(sizhu):
            self._add_shensha('河魁日', -40, '河魁日妨姑，不利新郎母亲')

        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合，婚嫁吉')
        
        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合，婚嫁吉')
        
        # 2026-10 A4：三奇同名重加删除（基类 super 日块单点注册，此块从未生效）。

        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星到座，婚嫁吉')
        
        # 2026-10 A6-4：异名 '三合日'/'六合日' 重加删除——基类 super 日块已按
        # 典载正名 '三合'(+10)/'六合'(+12) 单点注册，本类 _is_sanhe/_is_liuhe
        # 与基类内联 sanhe_sets/liuhe_map 谓词逐字等价（同局/同合且月≠日），属
        # 同一谓词的异名双注册，异名无独立语义。
        # 分值影响：嫁娶总分由 婚嫁评分算法.score_marriage_day 独立计算（三合局/
        # 六合在 L216/L222 另有 15/10 计分），**不**按本 shensha_list 求和；故旧
        # 异名在本事项内仅造成**展示列表重复**（2026 审计 14 日 Δscore 全为 0，
        # 且均为否决日），无分值漂移。删除仍必要：消除同名重复条目，并防止任何
        # 按 shensha_list 求和的消费者双计。('嫁娶','三合日')/('嫁娶','六合日')
        # 两条异名分值键同步从 SHENSHA_SCORES 删除。

        # 五合日
        if self._is_wuhe(sizhu):
            self._add_shensha('五合日', 8, '五合日婚嫁吉')
        
        # 母仓日
        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 10, '母仓日婚嫁吉')
        
        # E7 旺日：删除'旺日'异名注册（D=0，alias 归一为'王日'，基类已注册）
        
        # ===== 补充缺失的吉神检查 =====

        # 2026-10 批7b（001 §80.8）：'益后'/'续世' 日块同名重加删除——基类
        # 月作用域已统一注册 +12/+10（批7a 委托典载表，经本类月块 super 先
        # 行发射），本块同名重加被 _add_shensha 先到先得去重，从未生效（死
        # 链）。删除零行为差，运行时实证见 001 §80.8。

        # 阴德（阴德之神，利婚嫁）
        if self._is_yinde(sizhu):
            self._add_shensha('阴德', 10, '阴德吉日，婚嫁吉')
        
        # 阳德（阳德之神，利婚嫁）
        if self._is_yangde(sizhu):
            self._add_shensha('阳德', 10, '阳德吉日，婚嫁吉')
        
        # 2026-10 批4（001 §74）：'吉期' 重加删除——基类月作用域已统一
        # 注册 '吉期' +10（E3 修正后委托典载《历例》"常居月建前一辰"表），
        # 本块 super 先行后同名重加（+12）被 _add_shensha 先到先得去重，
        # 从未生效；《协纪》卷十按语明载"谓吉期宜结婚姻，於义无取，故删"，
        # 嫁娶总分由 score_marriage_day 独立计算，本删除零分差。
        
        # 要安（安宁之日，利婚嫁）
        if self._is_yaoan(sizhu):
            self._add_shensha('要安', 8, '要安日婚嫁吉')
        
        # '天赦日'重加已删除（2026-09-18，001跟踪项13.2方案①）：基类
        # _check_day_shensha 已加'天赦'+25（本类日方法 super 先行且全路径必达），
        # 原异名重加致真天赦日 +50 双计；删除后走基类统一，天赦日=+25。

        # 2026-10 A1：'鸣吠日'/'鸣吠对日' 同名重加删除（旧名「鸣犬」，
        # 基类月作用域按典载 13/11 日柱统一注册）；'岁德'/'岁德合' 同名
        # 重加删除（基类年作用域统一注册，年干比日干典载口径）。

        # 岁合（主和合）
        if self._is_suihe(sizhu):
            self._add_shensha('岁合', 12, '岁合主和合，婚嫁吉')
        
        # 2026-10 批1（001 §70）：'吉庆' 删除——《协纪》卷三十六·辨讹钦定判伪
        # （《选择宗镜》「满德吉庆为伪吉日……毋庸深辨」）。
        
        # ===== 补充缺失的凶煞检查 =====
        
        # 五离（典籍口径：申酉日，忌嫁娶）——2026-09-16 由"天干相离"改为与五合配对的"申酉日"
        if self._is_wuli(sizhu):
            self._add_shensha('五离', -20, '五离日主离别，婚嫁大忌')
        
        # 丧门（主丧亡，忌婚嫁）
        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '丧门日忌婚嫁')
        
        # 吊客（主吊唁，忌婚嫁）
        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '吊客日忌婚嫁')
        
        # 病符×嫁娶已删（病符批，2026-10-20，001 §141）：三库病符无日课普适忌
        # 明文（皆方位/年神语境），拍板「删日课通道病符注册」。发射原为：
        #     if self._is_bingfu(sizhu):
        #         self._add_shensha('病符', -12, '病符日忌婚嫁')
        
        # 官符（主官讼，忌婚嫁）
        if self._is_guanfu(sizhu):
            self._add_shensha('官符', -10, '官符日忌婚嫁')
        
        # 月虚（主虚耗，忌婚嫁）
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚日主虚耗，忌婚嫁')
        
        # 八专（主消耗，忌婚嫁）
        if self._is_bazhuan(sizhu):
            self._add_shensha('八专', -15, '八专日主消耗，忌婚嫁')

        # 四击发射已删（2026-10-18 月家P1：协纪卷十一嫁娶忌列无四击（四击仅忌
        # 军事），嫁娶注册超范围；八专嫁娶有典据保留；docs/月家P1_大煞八专四击_对勘.md）

        # 真四忌（《历例》「春甲子、夏丙子、秋庚子、冬壬子」，干支并论；
        # 2026-10 A6-5 新建，典载忌结婚姻嫁娶——与四击为两个独立神煞）
        if self._is_siji_ji(sizhu):
            self._add_shensha('四忌', -12, '四忌日忌婚嫁（春甲子夏丙子秋庚子冬壬子）')
        
        # 魁罡日（主聪明但婚姻不顺）
        if self._is_kuigang(sizhu):
            self._add_shensha('魁罡日', -15, '魁罡日聪明但婚姻不顺')
        
        # 基类通用日神煞（同名去重保留首次，嫁娶加重分值已先注册）
        super()._check_day_shensha(sizhu, **kwargs)
    
    def _check_special_shensha(self, sizhu, owners, **kwargs):
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
    
    # ===== 大利月/小利月（按女命年支）=====
    # 大利月口诀：正七迎鸡兔，二八虎和猴，三九蛇共猪，四十龙和狗，牛羊五十一，鼠马六腊月
    # 小利月口诀：鼠马二八月，牛羊四十当，虎猴正七月，兔鸡六腊月，龙狗三九月，蛇猪五十一
    # 单一数据源（2026-09-16）：_is_daliyue/_is_xiaoliyue 共用 LI_YUE_TABLE，禁止各自内联副本
    LI_YUE_TABLE = {
        '子': {'大利月': [6, 12], '小利月': [2, 8]},
        '午': {'大利月': [6, 12], '小利月': [2, 8]},
        '丑': {'大利月': [5, 11], '小利月': [4, 10]},
        '未': {'大利月': [5, 11], '小利月': [4, 10]},
        '寅': {'大利月': [2, 8], '小利月': [1, 7]},
        '申': {'大利月': [2, 8], '小利月': [1, 7]},
        '卯': {'大利月': [1, 7], '小利月': [6, 12]},
        '酉': {'大利月': [1, 7], '小利月': [6, 12]},
        '辰': {'大利月': [4, 10], '小利月': [3, 9]},
        '戌': {'大利月': [4, 10], '小利月': [3, 9]},
        '巳': {'大利月': [3, 9], '小利月': [5, 11]},
        '亥': {'大利月': [3, 9], '小利月': [5, 11]}
    }
    
    def _is_daliyue(self, sizhu):
        """
        是否大利月（按女命年支推算）
        依据：女命年支与月份的关系
        """
        if not self.bride_zhi:
            return False
        
        # 【F3 一致性修复】用真实农历月判定（sizhu 明确农历字段→高精度农历换算→
        # 最后才回退节气月支法），与评分器 _resolve_lunar_month 及主程序【嫁娶择日分析】
        # 的利月口径统一，避免"农历六月(节气午月)被 未 的大利月[5,11]中的5 误命中断言"，
        # 导致普通月份仍被标成大利月（神煞/利月神煞与利月分析"普通月份"自相矛盾）。
        month = self._get_true_lunar_month(sizhu)
        if month is None:
            return False
        
        if self.bride_zhi in self.LI_YUE_TABLE:
            return month in self.LI_YUE_TABLE[self.bride_zhi]['大利月']
        return False
    
    def _is_xiaoliyue(self, sizhu):
        """
        是否小利月（按女命年支推算）
        依据：女命年支与月份的关系
        """
        if not self.bride_zhi:
            return False
        
        # 从真实农历月份判定（与 _is_daliyue 同一口径，见其注释）
        month = self._get_true_lunar_month(sizhu)
        if month is None:
            return False
        
        if self.bride_zhi in self.LI_YUE_TABLE:
            return month in self.LI_YUE_TABLE[self.bride_zhi]['小利月']
        return False
    
    def _get_true_lunar_month(self, sizhu):
        """
        获取真实农历月份（1-12），与评分器 _resolve_lunar_month 及主程序
        【嫁娶择日分析】口径统一：
          1) sizhu 内明确农历字段（lunar_month / lunar['month']）优先。
          2) 否则用 sizhu.date 走高精度农历换算（腊月=12、正月=1），
             解决"节气月支午=5 但实际农历六月"这类错位导致的利月误判。
          3) 回退节气月支法 _get_lunar_month_from_zhi。
        """
        if not isinstance(sizhu, dict):
            return self._get_lunar_month_from_zhi('')
        lm = sizhu.get('lunar_month')
        if isinstance(lm, (int, float)) and 1 <= int(lm) <= 12:
            return int(lm)
        try:
            lunar_obj = sizhu.get('lunar')
            if isinstance(lunar_obj, dict):
                m = lunar_obj.get('month')
                if isinstance(m, (int, float)) and 1 <= int(m) <= 12:
                    return int(m)
                mc = str(lunar_obj.get('month_chinese') or lunar_obj.get('month') or '')
                _map = {'正月':1,'二月':2,'三月':3,'四月':4,'五月':5,'六月':6,
                        '七月':7,'八月':8,'九月':9,'十月':10,'十一月':11,'冬月':11,'腊月':12}
                if mc in _map:
                    return _map[mc]
        except Exception:
            pass
        d = sizhu.get('date') or sizhu.get('datetime')
        if d is not None and hasattr(d, 'year'):
            try:
                try:
                    from .四柱计算器 import get_lunar_date as _gld
                except Exception:
                    try:
                        from 四柱计算器 import get_lunar_date as _gld
                    except Exception:
                        from modules.四柱计算器 import get_lunar_date as _gld
                lun = _gld(d)
                if isinstance(lun, dict):
                    m = lun.get('month')
                    if isinstance(m, (int, float)) and 1 <= int(m) <= 12:
                        return int(m)
                    mc = str(lun.get('month_chinese') or lun.get('month') or '')
                    _map = {'正月':1,'二月':2,'三月':3,'四月':4,'五月':5,'六月':6,
                            '七月':7,'八月':8,'九月':9,'十月':10,'十一月':11,'冬月':11,'腊月':12}
                    if mc in _map:
                        return _map[mc]
            except Exception:
                pass
        return self._get_lunar_month_from_zhi(str(sizhu.get('month_zhi', '') or ''))
    
    def _get_lunar_month_from_zhi(self, month_zhi):
        """
        从月地支获取农历月份（1-12）
        
        Args:
            month_zhi: 月地支
            
        Returns:
            int: 农历月份（1-12）
        """
        zhi_to_month = {
            '寅': 1, '卯': 2, '辰': 3, '巳': 4,
            '午': 5, '未': 6, '申': 7, '酉': 8,
            '戌': 9, '亥': 10, '子': 11, '丑': 12
        }
        return zhi_to_month.get(month_zhi, 1)
    
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

    def _is_tiangang(self, sizhu):
        """是否天罡日（妨翁日）

        依《协纪辨方书·神煞对照表》：天罡日者，日支临月建也。
        正月寅日、二月卯日、三月辰日…十二月丑日。
        （旧实现误作六害日，已更正：日支与月支相同即为天罡妨翁日。）
        """
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']

        # 天罡日规则（妨翁）：日支临月建
        return bool(month_zhi) and day_zhi == month_zhi

    def _is_hekui(self, sizhu):
        """是否河魁日（妨姑日）

        依《协纪辨方书·神煞对照表》：河魁日者，日支临月破也。
        正月申日、二月酉日、三月戌日、四月亥日、五月子日、六月丑日、
        七月寅日、八月卯日、九月辰日、十月巳日、十一月午日、十二月未日。
        （旧实现误作六合日——六合本为嫁娶大吉，绝无"妨姑"之理，已更正为月破六冲。）
        """
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']

        # 河魁日规则（妨姑）：日支临月破（月支之六冲）
        hekui_map = {
            '寅': '申',  # 正月（寅月）月破在申
            '卯': '酉',  # 二月（卯月）月破在酉
            '辰': '戌',  # 三月（辰月）月破在戌
            '巳': '亥',  # 四月（巳月）月破在亥
            '午': '子',  # 五月（午月）月破在子
            '未': '丑',  # 六月（未月）月破在丑
            '申': '寅',  # 七月（申月）月破在寅
            '酉': '卯',  # 八月（酉月）月破在卯
            '戌': '辰',  # 九月（戌月）月破在辰
            '亥': '巳',  # 十月（亥月）月破在巳
            '子': '午',  # 十一月（子月）月破在午
            '丑': '未'   # 十二月（丑月）月破在未
        }

        return hekui_map.get(month_zhi) == day_zhi

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
    
    def _is_yanggongji(self, sizhu):
        """
        是否杨公忌日（2026-09-20 收敛：改委托 is_yanggongji_by_lunar）

        原为反转桩：lunar_python 已安装 → try 分支恒 return False，
        except 中的"简化版"日支表（与真表 2026 零重合）永不执行。
        现统一走农历月日唯一口径（闰月不计）。
        """
        return is_yanggongji_by_lunar(sizhu)
    
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
        """是否往亡日（《协纪》口诀"正寅二巳三申四亥五卯六午七酉八子
        九辰十未十一戌十二丑"，月支查日支；委托单点出口
        is_wangwang_by_zhi）。
        """
        return is_wangwang_by_zhi(sizhu.get('month_zhi', ''),
                                  sizhu.get('day_zhi', ''))
    
    def _get_date_from_sizhu(self, sizhu):
        """从sizhu中获取date对象"""
        from datetime import date as date_type
        
        if 'date' in sizhu:
            d = sizhu['date']
            if isinstance(d, date_type):
                return d
        
        year = sizhu.get('year')
        month = sizhu.get('month')
        day = sizhu.get('day')
        if year and month and day:
            try:
                return date_type(int(year), int(month), int(day))
            except (ValueError, TypeError):
                pass
        return None
    
    def _is_zhongsang(self, sizhu):
        """是否重丧日（按农历月份，使用完整干支）

        按《协纪辨方书》规则：
        - 正月：庚戌日
        - 二月：辛酉日
        - 三月：庚申日
        - 四月：己未日
        - 五月：戊午日
        - 六月：丁巳日
        - 七月：丙辰日
        - 八月：乙卯日
        - 九月：甲寅日
        - 十月：癸丑日
        - 十一月：壬子日
        - 十二月：辛亥日
        """
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        day_gz = day_gan + day_zhi

        try:
            date_obj = self._get_date_from_sizhu(sizhu)
            if date_obj:
                from modules.四柱计算器 import get_lunar_date
                lunar_info = get_lunar_date(date_obj)
                if lunar_info and 'month' in lunar_info:
                    lunar_month_name = lunar_info['month']
                    zhongsang_map = {
                        '正月': '庚戌', '二月': '辛酉', '三月': '庚申', '四月': '己未',
                        '五月': '戊午', '六月': '丁巳', '七月': '丙辰', '八月': '乙卯',
                        '九月': '甲寅', '十月': '癸丑', '十一月': '壬子', '十二月': '辛亥',
                        '腊月': '辛亥'
                    }
                    return day_gz == zhongsang_map.get(lunar_month_name, '')
        except:
            pass

        return False
    
    def _parse_chinese_day(self, day_str):
        """
        解析中文日期为数字
        """
        day_map = {
            '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
            '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
            '廿一': 21, '廿二': 22, '廿三': 23, '廿四': 24, '廿五': 25,
            '廿六': 26, '廿七': 27, '廿八': 28, '廿九': 29, '三十': 30
        }
        return day_map.get(day_str, 0)
    
    def _parse_chinese_month(self, month_str):
        """解析中文月份为数字"""
        month_map = {
            '正月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
            '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '冬月': 11, '十二月': 12,
            '腊月': 12
        }
        return month_map.get(month_str, 0)
    
    def _is_zhen_sanniang(self, sizhu):
        """是否真三娘煞（特定干支）

        口径依据软件现行共识（非《协纪》正式条目）；闰月不计（通用规则，
        与杨公忌/红纱口径一致）。fallback sizhu['lunar_day'] 路径无农历
        月信息、无法判闰月，保持原行为不动。
        """
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        ganzhi = day_gan + day_zhi

        zhen_sanniang_map = {
            3: ['庚午'],
            7: ['辛未'],
            13: ['戊申'],
            18: ['己酉'],
            22: ['丙午'],
            27: ['丁未']
        }

        lunar_day = 0
        try:
            date_obj = self._get_date_from_sizhu(sizhu)
            if date_obj:
                from modules.四柱计算器 import get_lunar_date
                lunar_info = get_lunar_date(date_obj)
                if lunar_info:
                    # 闰月不计（get_lunar_date 的 month 已含'闰'前缀）
                    if '闰' in str(lunar_info.get('month', '')):
                        return False
                    if 'day' in lunar_info:
                        lunar_day = self._parse_chinese_day(lunar_info['day'])
            elif 'lunar_day' in sizhu:
                lunar_day = sizhu['lunar_day']
        except:
            pass

        return lunar_day in zhen_sanniang_map and ganzhi in zhen_sanniang_map[lunar_day]
    
    def _is_huangsha(self, sizhu):
        """黄沙日（节气月支版：四孟寅申巳亥月逢午日、四仲子午卯酉月逢寅日、
        四季辰戌丑未月子日。2026-09-21 按《协纪》义例体系统一为节气月口径，
        废弃原农历月版。）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        huangsha_map = {
            '寅': '午', '申': '午', '巳': '午', '亥': '午',
            '子': '寅', '午': '寅', '卯': '寅', '酉': '寅',
            '辰': '子', '戌': '子', '丑': '子', '未': '子'
        }
        return huangsha_map.get(month_zhi) == day_zhi
    
    # D2 神号：删除嫁娶 override（农历月查日支版，三库无载＋except:pass 静默降级）。
    # 现继承基类 _is_shenhao（年支查月支版，协纪有载条目）。
    # 嫁娶注册 '神号日' -15 保留（嫁娶重忌口径）。

    def _is_guiru(self, sizhu):
        """是否鬼哭日"""
        lunar_month = 0
        if 'date' in sizhu:
            try:
                from modules.四柱计算器 import get_lunar_date
                lunar_info = get_lunar_date(sizhu['date'])
                if lunar_info and 'month' in lunar_info:
                    lunar_month = self._parse_chinese_month(lunar_info['month'])
            except:
                pass
        elif 'lunar_month' in sizhu:
            lunar_month = sizhu['lunar_month']
        
        day_zhi = sizhu.get('day_zhi', '')
        
        guiru_map = {
            1: ['午'], 2: ['戌'], 3: ['辰'], 4: ['寅'],
            5: ['午'], 6: ['子'], 7: ['酉'], 8: ['申'],
            9: ['巳'], 10: ['亥'], 11: ['丑'], 12: ['卯']
        }
        
        return lunar_month in guiru_map and day_zhi in guiru_map[lunar_month]
    
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
        """是否天狗日 - 根据《钦定协纪辨方书》，天狗为建除十二神中的"满"日"""
        try:
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
    
    # 2026-10 A6-4 批B：旧 _is_bujiang（干支阴阳法 A 实现）已删除，统一继承
    # 基类 _is_bujiang（委托 is_bujiang_by_ganzhi，查唯一权威表 _BUJIANG_TABLE），
    # 与评分/规则层 marriage_shensha.is_bujiang_day 同表同口径。

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
        """是否天德日
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
    # 原日方法内"月德日"/"天德日"守卫重加死分支（基类 super 先加同名条目，守卫恒
    # False）已于 2026-09-21 13.1 死代码专项删除，730 天×14 检查器零差异。
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
    
    # 2026-10 批6' 批2（001 §76）：_is_mucang 子类重写删除——Initial commit
    # 遗留"月支+1/+2 顺行表"（寅卯辰月→卯辰、巳午未月→午未、申酉戌月→酉戌、
    # 亥子丑月→子丑），三库检索穷尽无载（协纪 279xxx 系 24 行、考原 359xxx
    # 系 5 行命中全为卷五正文/卷十义例用例/卷十立成，无任何顺行变体）；且经
    # 动态派发污染基类日块发射——基类 _check_day_shensha 的 self._is_mucang
    # 解析至本 override，致嫁娶母仓＝纯顺行表，典载表命中日（如寅月亥日）
    # 反不含母仓（阶段1 运行时实证）。现继承基类 _is_mucang（典载《历例》
    # "春亥子，夏寅卯，秋辰戌丑未，冬申酉"），下方发射块保留，
    # '母仓日'别名归一不变。收敛路径同 A6-4 驿马、批3 季旺表先例。
    
    # 2026-10 批3 批A（001 §72）：_is_wangri 子类重写删除——Initial commit
    # （9e2b864）遗留的民间帝旺表（寅卯月→卯、辰巳午月→午、未申酉月→酉、
    # 戌亥子月→子，与原入宅 _is_xiangri 同表），覆盖基类委托谓词，致嫁娶
    # 「旺日」脱离《历例》王日典载口径（春寅夏巳秋申冬亥，钦定按语
    # "君用阳而臣用隂"）。帝旺≠王日（卷十："子午卯酉日为三合帝旺所宜并
    # 同王日"——宜同而名异）。现继承基类 _is_wangri（委托 is_wangri_by_zhi）。

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
