# -*- coding: utf-8 -*-
"""
================================================================================
动土神煞模块
================================================================================
实现动土择日专用神煞的检查逻辑
继承修造神煞，添加动土专属检查

使用方法:
    1. 作为模块导入: from modules.shensha.动土神煞 import DiggingShenShaChecker
    2. 直接运行: python -m modules.shensha.动土神煞
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
    from .修造神煞 import ConstructionShenShaChecker
    from ..工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE
except ImportError:
    from 神煞基类 import ShenShaChecker
    from 修造神煞 import ConstructionShenShaChecker
    from 工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE


class DiggingShenShaChecker(ConstructionShenShaChecker):
    """动土神煞检查器
    
    继承修造神煞，添加动土专属规则：
    - 土王用事（动土大忌）
    - 杀师日（动土专属，扣分更高）
    - 天赦日（动土大吉）
    """
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 年干比日干典载口径）。

        # 太岁×动土已删（口径收口批，2026-10-21，001 §153，岁破款收口）：
        # 太岁为方位神（卷三「统正方位……不可向之」、卷八「可坐不可向」），
        # 协纪卷十/十一无日辰忌项（卷十唯一命中为比喻句，卷四按语「历家特误以
        # 年方配日辰耳」）——与已删岁破同源同构（快验稿 §4.4 五维全同）。
        # 原发射为：
        #     if self._is_taisui(sizhu):
        #         self._add_shensha('太岁', -20, '太岁当头，忌动土')

        # 岁破×动土已删（岁破批，2026-10-20，001 §140）：日课普适岁破注册零日课
        # 典据（协纪卷内「岁破日」0 命中），拍板删日课通道普适忌注册。发射原为：
        #     if self._is_suipo(sizhu):
        #         self._add_shensha('岁破', -30, '岁破日，动土大忌')
        
        # 岁煞
        if self._is_suisha(sizhu):
            self._add_shensha('岁煞', -20, '岁煞日，忌动土修造')
        
        # 黄幡
        if self._is_huangfan(sizhu):
            self._add_shensha('黄幡', -15, '黄幡日，忌动土修造')
        
        # 豹尾
        if self._is_baowei(sizhu):
            self._add_shensha('豹尾', -12, '豹尾日，忌动土修造')

        # 2026-10 A3：'飞廉' 年作用域注册删除（典载飞廉为月神，
        # 已由基类月作用域统一注册）。
        
        # 丧门
        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '丧门日，忌动土修造')
        
        # 吊客
        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '吊客日，忌动土修造')
        
        # 病符×动土已删（病符批，2026-10-20，001 §141）：三库病符无日课普适忌
        # 明文（皆方位/年神语境），拍板「删日课通道病符注册」。发射原为：
        #     if self._is_bingfu(sizhu):
        #         self._add_shensha('病符', -12, '病符日，忌动土修造')
        
        # 官符
        if self._is_guanfu(sizhu):
            self._add_shensha('官符', -10, '官符日，忌动土修造')
        
        # 五鬼
        if self._is_wugui(sizhu):
            self._add_shensha('五鬼', -15, '五鬼日，忌动土修造')

        # 大煞发射已删（2026-10-18 月家P1：协纪卷十仅忌军事，动土超范围；
        # docs/月家P1_大煞八专四击_对勘.md）

    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        # 土王用事（动土大忌；轻重层批次1 001 §158：兜底字面量随注册键同步 -40→-20）
        if self._is_tuwang_yongshi(sizhu):
            self._add_shensha('土王用事', -20, '土王当权，忌动土')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德吉星，动土修造大吉')
        
        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合，动土修造吉利')
        
        # 月恩
        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩吉星，动土修造吉')
        
        # 四相
        if self._is_sixiang(sizhu):
            self._add_shensha('四相', 10, '四相吉日，动土修造吉')
        
        # 时德
        if self._is_shide(sizhu):
            self._add_shensha('时德', 10, '时德吉日，动土修造吉')
        
        # 月虚
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚日，忌动土修造')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -15, '月刑日，忌动土修造')
        
        # 月害条目已删（2026-10-18 P2 删除批，001 §122）：月害×动土三库无载
        # （系逐字重提更正诊断漏标，docs/月家P2_月害大时往亡五墓_续取证.md §六）；
        # 本行原为死链，基类通用链事项排除后隔离（001 §120）。

    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        # 不调用 super()：历史原因为杀师日分值差异（现已同为 -30 且 _add_shensha
        # 按名去重不会双计），但本手抄副本与修造日检查已存在差异（缺刀砧煞/斧头煞/
        # 木马煞/天地转煞/山曜/八专/四忌及岁合/益后/续世/福生/天恩等），
        # 贸然改走继承会引入大范围行为变化——如需收口须专项处理，勿在本方法随手改。
        
        # ===== 继承修造神煞的其他日神煞检查（手动调用，除了杀师日）=====
        # 天贼
        if self._is_tianzei(sizhu):
            self._add_shensha('天贼', -20, '忌动土、修造，犯之主耗财')
        
        # 地贼
        if self._is_dizei(sizhu):
            self._add_shensha('地贼', -15, '忌动土、修造，犯之主失盗')
        
        # 四离日
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -35, '春分、秋分、夏至、冬至前一日，忌大事')
        
        # 四绝日
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -35, '立春、立夏、立秋、立冬前一日，忌大事')
        
        # 十恶大败发射行已注释（2026-10-19 全删批·一档，001 §139）：三库无
        # 「十恶大败」普适日课忌明文（取证 aa47dcd／快照 2ca7b4e；协纪
        # 「然惟随各年及本命避之」属本命避忌，非日课普适扣分）；谓词保留作无禄日载体。
        # if self._is_shie_dabai(sizhu):
        #     self._add_shensha('十恶大败', -30, '忌动土修造，犯之主败')

        # 伏断日由基类月作用域统一注册（A6-3 同名分支删除，super 先注册必被去重）

        # 将军箭
        if self._is_jiangjunjian(sizhu):
            self._add_shensha('将军箭', -20, '忌修造，犯之主伤')

        # 杀师日（动土大忌，扣分更高）
        if self._is_shashi(sizhu):
            self._add_shensha('杀师日', -30, '动土大忌，犯之伤害工匠')

        # 杀师时（时柱逢戊午，部分严谨流派大忌，伤工匠）
        if sizhu.get('hour_gan') == '戊' and sizhu.get('hour_zhi') == '午':
            self._add_shensha('杀师时', -30, '时辰逢戊午为杀师时，对现场工匠不利，宜避开')
        
        # 受死日
        if self._is_shousi_day(sizhu):
            self._add_shensha('受死日', -22, '受死日，动土修造大忌')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日，忌动土修造')

        # ===== 吉神 =====
        
        # 天德日（与天德同源吉神，二选一保留较高者，避免重复计分虚高）
        # 2026-09-19 锚点③拍板：动土天德日由 +15 统一为 +20，与其他事项天德口径一致
        if self._is_tiande(sizhu) and '天德' not in [s['name'] for s in self.shensha_list]:
            self._add_shensha('天德日', 20, '天德日，动土修造大吉')
        
        # 月德计分由月神煞方法统一加（'月德' +18），日方法此处分支在完整
        # check() 五步链路中守卫恒假（月神煞先执行），已于 2026-09-21 删除。
        
        # 天德合
        if self._is_tiandehe(sizhu):
            self._add_shensha('天德合', 15, '动土修造吉利')

        # 天乙贵人（001 §250）：本方法不调 super，吉神段为手工副本，
        # 需与基类同步发射，否则动土通道出现「【吉神】有、【吉神(加分项)】无」
        # 的展示与计分割裂。仅补此一项吉神，不改动其余继承差异。
        _ty_pillar = self._is_tianyi_guiren(sizhu)
        if _ty_pillar:
            self._add_shensha(
                '天乙贵人', 15,
                '天乙贵人临%s，主逢凶化吉、贵人扶持' % _ty_pillar)
        
        # 天愿
        if self._is_tianyuan(sizhu):
            self._add_shensha('天愿', 12, '天愿吉星，修造吉')

        # 2026-10 A1：'天马' 同名重加删除（典载天马为月神，基类月作用域注册）。

        # 三奇
        sanqi_result = self._is_sanqi(sizhu)
        if sanqi_result:
            self._add_shensha(f'三奇{sanqi_result}', 15, f'{sanqi_result}三奇照临，修造上吉')
        
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

        # 2026-10 A1：'鸣吠日'/'鸣吠对日' 重加删除（继承修造错表谓词，
        # 基类月作用域已按 13/11 典载日柱统一注册，动土取 15/10 分值键）。

        # 2026-10 A6-4 死代码清理：'不将日' 注册块删除。本类继承修造神煞
        # _is_bujiang（恒 False——不将日为嫁娶专用吉日，修造系刻意禁用，
        # 见 修造神煞.py 同名方法 docstring），本守卫恒假、365 天完整 check()
        # 链路零命中；动土不将宜项文案由 rules 层 marriage_shensha
        # .is_bujiang_day 独立供给（2026 全年 77 天与基类 D 表全等）。

        # 天赦（动土大吉）
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦吉日，动土百无禁忌')

    # ============ 缺失的辅助方法 ============
    
    def _is_taisui(self, sizhu):
        """太岁：日支与年支相同"""
        year_zhi = sizhu.get('year_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        return year_zhi == day_zhi and year_zhi != ''
    
    # _is_suipo 已删（岁破批，2026-10-20，001 §140）：日课普适岁破谓词零典据，
    # 唯一消费者（年块发射行）本批同步删除后无 caller（原实现：日支==年支+6）。

    # 岁煞 _is_suisha 已删除 override，直接继承神煞基类的权威墓库位表
    # （申子辰→未、巳酉丑→辰、寅午戌→丑、亥卯未→戌，2026-09-18 修正）

    def _is_yuexing(self, sizhu):
        """月刑：月支刑日支"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        xing_map = {
            '子': '卯', '卯': '子',
            '寅': '巳', '巳': '申', '申': '寅',
            '丑': '戌', '戌': '未', '未': '丑',
            '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'
        }
        return day_zhi == xing_map.get(month_zhi)
    
    def _is_yuehai(self, sizhu):
        """月害：月支害日支"""
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


if __name__ == '__main__':
    print("动土神煞模块")
    print("使用方法: from modules.shensha.动土神煞 import DiggingShenShaChecker")