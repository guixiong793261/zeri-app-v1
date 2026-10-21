# -*- coding: utf-8 -*-
"""
================================================================================
通用神煞模块
================================================================================
实现通用择日神煞的检查逻辑
包含：太岁、岁破、月破、黄道、黑道等基本神煞

使用方法:
    1. 作为模块导入: from modules.shensha.通用神煞 import CommonShenShaChecker
    2. 直接运行: python -m modules.shensha.通用神煞
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
    from .神煞基类 import ShenShaChecker, is_yanggongji_by_lunar, is_sifei_by_pillar
    from ..工具函数 import TIANDE, YUEDE, DI_ZHI
except ImportError:
    from 神煞基类 import ShenShaChecker, is_yanggongji_by_lunar, is_sifei_by_pillar
    from 工具函数 import TIANDE, YUEDE, DI_ZHI

class CommonShenShaChecker(ShenShaChecker):
    """通用神煞检查器"""

    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        year_gan = sizhu['year_gan']
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']

        # 2026-09-16修复：原此处无条件加 '太岁' -20，导致入学/求医/签约
        # 每一天都被扣20分且神煞栏恒显"犯太岁"。太岁为年神（忌动土方位）。
        # 岁破×通用已删（岁破批，2026-10-20，001 §140）：原此处以
        # day_zhi == self._get_suipo(year_zhi) 发射 '岁破' -30；日课普适岁破注册
        # 零日课典据（协纪卷内「岁破日」0 命中），拍板删日课通道普适忌注册。
        # 发射原为：
        #     if day_zhi == self._get_suipo(year_zhi):
        #         self._add_shensha('岁破', -30, '与太岁相冲，百事不宜')
        # 注：_get_suipo 保留——日破时(:506)/月破(:519) 仍消费，本批不动。

        # 年支三煞（劫煞、灾煞、岁煞）
        if self._is_nian_sansha(sizhu):
            self._add_shensha('年三煞', -18, '年支三煞，诸事不宜')

        # ===== 吉神 =====
        if self._is_suide(sizhu):
            self._add_shensha('岁德', 20, '年干之德，百事皆宜')

        if self._is_suide_he(sizhu):
            self._add_shensha('岁德合', 15, '岁德六合，诸事吉利')

        if self._is_suihe(sizhu):
            self._add_shensha('岁合', 12, '年干六合，诸事顺遂')

        if self._is_sui_lu(sizhu):
            self._add_shensha('岁禄', 15, '年干禄位，财禄双收')

        # 2026-10 A1：'天马' 年作用域注册删除（典载天马为月神，
        # 移入下方月作用域，谓词收口月支比日支）。

        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩加临，恩泽深厚')

        if self._is_fuxing(sizhu):
            self._add_shensha('福星', 10, '福星照临，主福泽')

        # ===== 凶煞 =====
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -25, '劫煞为灾，谨防破财')

        if self._is_zaijiesha(sizhu):
            self._add_shensha('灾煞', -25, '灾煞为患，诸事不顺')

        if self._is_suisha(sizhu):
            self._add_shensha('岁煞', -20, '岁煞临方，慎勿用之')

        if self._is_huangfan(sizhu):
            self._add_shensha('黄幡', -15, '黄幡招凶，主有虚惊')

        if self._is_baowei(sizhu):
            self._add_shensha('豹尾', -12, '豹尾为害，主有损失')

        if self._is_fubing(sizhu):
            self._add_shensha('亡神', -12, '亡神临身，虚耗破财')

        if self._is_dahuo(sizhu):
            self._add_shensha('大祸', -15, '大祸临门，诸事不宜')

        if self._is_suixing(sizhu):
            self._add_shensha('岁刑', -12, '岁刑加身，刑克缠身')

        if self._is_suihai(sizhu):
            self._add_shensha('岁害', -12, '岁害相侵，诸事不顺')

        if self._is_lishi(sizhu):
            self._add_shensha('力士', -10, '力士当权，动作不顺')

        if self._is_canguan(sizhu):
            self._add_shensha('蚕官', -10, '蚕官临位，不利蚕事')

        if self._is_wugui(sizhu):
            self._add_shensha('五鬼', -15, '五鬼缠身，破财耗气')

        # 大煞发射已删（2026-10-18 月家P1：协纪卷十仅忌军事，软件无军事事项；
        # docs/月家P1_大煞八专四击_对勘.md）

        # 金神：年神方位煞，不用于日课评分（见基类 _get_jinshen_positions）

        if self._is_pobai(sizhu):
            self._add_shensha('破败', -10, '破败当头，诸事耗散')

        if self._is_guanfu(sizhu):
            self._add_shensha('官符', -10, '官符缠身，主有官非')

        if self._is_chuguansheng(sizhu):
            self._add_shensha('畜官', -10, '畜官临位，不利畜养')

        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '丧门临头，主有丧事')

        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '吊客临门，主有凶事')

        # 病符×通用已删（病符批，2026-10-20，001 §141）：三库病符无日课普适忌
        # 明文（皆方位/年神语境），拍板「删日课通道病符注册」。发射原为：
        #     if self._is_bingfu(sizhu):
        #         self._add_shensha('病符', -12, '病符加身，提防疾病')

        if self._is_tianhao(sizhu):
            self._add_shensha('天耗', -10, '天耗临身，虚耗破财')

        if self._is_dihao(sizhu):
            self._add_shensha('地耗', -10, '地耗当令，损耗不绝')

        # 2026-09-16修复（第二批）：删除年作用域的 '天医'/'天巫' 两条。
        # 原实现按"年支"起例（_is_tianyi_year 年支+8、_is_tianwu_year 年支后八位），
        # 与日作用域 '天医日'/'天巫日' 同名同分（各 +8）却各执一套起例，同一天会重复计分。
        # 《协纪辨方书》明载二神皆为月神，并无"年支"起例：
        #   天医——「天医者，正月起戌，顺行十二辰」（寅月戌日 = 月支序 + 8）
        #   天巫——「（天巫）常居月建前二辰」（寅月辰日 = 月支序 + 2）
        # 故统一保留日作用域（命名更明确，且不与年作用域重名），此处不再计分。

    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        # 月破
        if day_zhi == self._get_yuepo(month_zhi):
            self._add_shensha('月破', -30, '与月建相冲，诸事不宜')

        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -15, '与月建相刑，诸事不利')

        # 月害——P2 部分匹配拆分（2026-10-18，001 §123）：月害×通用逐子项
        # 判定（docs/月家P2_月害大时往亡五墓_续取证.md §六）：求医✅（卷十忌列
        # +卷十一求医疗病条）、签约✅（立劵交易条）、入学❌（卷十一入学条无月害）
        # ——入学子项删除，按 _std_event 拆分。
        if self._is_yuehai(sizhu) and getattr(self, '_std_event', None) != '入学':
            self._add_shensha('月害', -15, '与月建相害，诸事不顺')

        # ===== 吉神 =====
        if self._is_yuedehe(sizhu):
            self._add_shensha('月德合', 12, '月德合日，诸事吉利')

        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩加临，恩泽深厚')

        if self._is_wufu(sizhu):
            self._add_shensha('五富', 12, '五富临日，财源广进')

        if self._is_jiqi(sizhu):
            self._add_shensha('吉期', 10, '吉期良辰，诸事皆宜')

        if self._is_yangde(sizhu):
            self._add_shensha('阳德', 10, '阳德照临，诸事亨通')

        if self._is_yinde(sizhu):
            self._add_shensha('阴德', 10, '阴德庇佑，暗中得福')

        if self._is_wangri(sizhu):
            self._add_shensha('王日', 10, '王日至尊，诸事可行')

        if self._is_guanri(sizhu):
            self._add_shensha('官日', 8, '官日当令，利见贵人')

        # 2026-10 A3：守日误用八专访词断开（同日 +8 与 -15 并挂）。
        # 守日归批次 D「王官守相民」体系，待翻《协纪》原诀后另行注册。

        if self._is_fusheng(sizhu):
            self._add_shensha('福生', 10, '福生临日，百福骈臻')

        # 2026-10 批1（001 §70）：'吉庆' 删除——《协纪》卷三十六·辨讹钦定判伪
        # （《选择宗镜》「满德吉庆为伪吉日……毋庸深辨」）。

        if self._is_yihou(sizhu):
            self._add_shensha('益后', 12, '益后嗣续，利子嗣')

        if self._is_xushi(sizhu):
            self._add_shensha('续世', 10, '续世绵延，利嗣续')

        if self._is_yaoan(sizhu):
            self._add_shensha('要安', 8, '要安之日，平稳守成')

        # 2026-09-16修复：删除此处月作用域的 '天医'/'天巫' ——
        # 二者分别调用 _is_tianyi_day / _is_tianwu_day，与下方日作用域的
        # '天医日'/'天巫日' 条件完全相同，同一天被重复计分（+8+8）。
        # 保留日作用域的 '天医日'/'天巫日'（命名更明确，且不与年作用域 '天医'/'天巫' 重名）。

        # 2026-10-21 口径收口批（001 §153）：不将日嫁娶专用（协纪卷十「宜嫁娶」
        # +卷十一仅嫁娶+考原+陈书 p134，取证稿 §1.2）。本通道服务移徙/入学/
        # 求医/签约/通用等事项，无嫁娶，发射删除（取证稿 §1.2 判 ❌）。
        # 原发射为：
        #     if self._is_bujiang(sizhu):
        #         self._add_shensha('不将日', 15, '不将吉日，嫁娶大吉')

        if self._is_tianma(sizhu):
            # 天马（月神，2026-10 A1 自年/日作用域移入本类月作用域）
            self._add_shensha('天马', 10, '天马驰驱，出行吉利')

        if self._is_mingfei(sizhu):
            # 2026-10 A1 正名：旧软件名「鸣犬日」→ 典据正名「鸣吠日」
            self._add_shensha('鸣吠日', 12, '鸣吠日吉，诸事皆宜')

        if self._is_mingfeidui(sizhu):
            self._add_shensha('鸣吠对日', 8, '鸣吠对日，次吉之日')

        if self._is_yuekong(sizhu):
            self._add_shensha('月空', 10, '月空之日，诸煞皆空')

        # ===== 凶煞 =====
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚之日，虚耗不实')

        # 八专/四击发射已删（2026-10-18 月家P1：协纪两煞仅忌军事（八专另忌
        # 嫁娶族，由嫁娶通道承载），通用通道服务入学/求医/签约等非军事事项，
        # 注册超范围；docs/月家P1_大煞八专四击_对勘.md）

        # 土符条目已删（2026-10-18 零典据删除：通用通道服务入学/求医/签约等非土工
        # 事项，无典据支持；「土符忌动土」由动土/修造/拆舍专用通道 -20 承载，判据(b) §4）

        # 土府/地囊条目已删（2026-10-18 P1-4 零典据确认后删除：协纪卷十一入学忌无、
        # 求医疗病/立券交易忌列无土符地囊，且协纪「土府」仅作月建别名无独立煞；
        # docs/P1-4_土府地囊_对勘.md，001 §111）

        if self._is_tuwen(sizhu):
            self._add_shensha('土瘟', -20, '土瘟（四季土旺日）临日，大忌动土')

        if self._is_dahao(sizhu):
            self._add_shensha('大耗', -20, '大耗临身，破财耗气')

        if self._is_xiaohao(sizhu):
            self._add_shensha('小耗', -15, '小耗之日，略有损耗')

        if self._is_dashi(sizhu):
            self._add_shensha('大时', -12, '大时咸池，桃花煞')

        if self._is_tianli(sizhu):
            self._add_shensha('天吏', -15, '天吏致死，大忌')

        if self._is_sifei(sizhu):
            self._add_shensha('四废', -15, '四废日，百事不宜')

        if self._is_flyinglian(sizhu):
            self._add_shensha('飞廉', -12, '飞廉作祟，口舌是非')

        if self._is_wumu(sizhu):
            self._add_shensha('五墓', -12, '五墓之日，忌埋葬')

        # 2026-10-21 口径收口批（001 §153）：伏断日日家用忌零载删除（协纪卷十
        # 无条目、卷十一 0 命中、卷三十六辨讹「伏断本选时之法」，取证稿 §1.4）。
        # 原发射为：
        #     if self._is_fuduan(sizhu):
        #         self._add_shensha('伏断日', -15, '伏断之日，切忌用事')

        # 往亡——P2 部分匹配拆分（2026-10-18，001 §123）：往亡×通用逐子项
        # 判定（docs/月家P2_月害大时往亡五墓_续取证.md §六）：求医✅（卷十一
        # 求医疗病条+陈书 p696）、入学❌（入学条无往亡）、签约❌（立劵交易条
        # 无往亡）——入学/签约子项删除，按 _std_event 拆分。
        if self._is_wangwang(sizhu) and getattr(self, '_std_event', None) not in ('入学', '签约'):
            self._add_shensha('往亡', -20, '往亡之日，大忌远行')

        # 2026-10-21 口径收口批（001 §153）：归忌主锚用忌面=般移/移徙＋远回
        # （取证稿 §1.7）；本通道仅移徙在主锚用忌面内（入学/求医/签约/通用
        # 4 事项无载删除），按 _std_event 门控。
        if self._is_guiji(sizhu) and getattr(self, '_std_event', None) == '移徙':
            self._add_shensha('归忌', -15, '归忌之日，忌归家')

        # 红嘴朱雀×通用已删（红嘴朱雀按典修批 A，2026-10-20）：三库无「红嘴朱雀
        # 忌入学/求医/签约」明文，且旧起例（月支对冲+2，等价月支+8）与陈书 p890
        # 「日干支×九宫飞」全异。通用事项按典不注册该煞。发射原为：
        #     if self._is_hongzui_zhuque(sizhu):
        #         self._add_shensha('红嘴朱雀', -12, '红嘴朱雀，口舌是非')

        if self._is_tiangou(sizhu):
            self._add_shensha('天狗', -12, '天狗食日，主有损失')

        if self._is_shenhao(sizhu):
            self._add_shensha('神号', -10, '神号之日，当防惊吓')

        if self._is_guiqi(sizhu):
            self._add_shensha('鬼哭', -10, '鬼哭之日，防鬼魅')

        if self._is_huangsha(sizhu):
            self._add_shensha('黄沙', -12, '黄沙日，忌嫁娶')

        if self._is_baihu(sizhu):
            self._add_shensha('白虎', -10, '白虎当道，凶险')

        if self._is_zhuque(sizhu):
            self._add_shensha('朱雀', -10, '朱雀临门，口舌是非')

    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        month_zhi = sizhu['month_zhi']

        # ===== 凶煞 =====

        # 四离日
        if self._is_sili(sizhu):
            self._add_shensha('四离日', -35, '春分、秋分、夏至、冬至前一日，忌大事')

        # 四绝日
        if self._is_sijue(sizhu):
            self._add_shensha('四绝日', -35, '立春、立夏、立秋、立冬前一日，忌大事')

        # 四废日
        if self._is_sifei(sizhu):
            self._add_shensha('四废日', -15, '春庚申辛酉，夏壬子癸亥，秋甲寅乙卯，冬丙午丁巳')

        # 十恶大败发射行已注释（2026-10-19 全删批·一档，001 §139）：三库无
        # 「十恶大败」普适日课忌明文（取证 aa47dcd／快照 2ca7b4e；协纪
        # 「然惟随各年及本命避之」属本命避忌，非日课普适扣分）；谓词保留作无禄日载体。
        # if self._is_shie_dabai(sizhu):
        #     self._add_shensha('十恶大败', -30, '忌大事，犯之主败')

        # ===== 吉神 =====

        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '百事皆宜，诸凶皆解')

        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '百事皆宜，诸凶皆解')

        # 天德合
        if self._is_tiandehe(sizhu):
            self._add_shensha('天德合', 15, '诸事吉利')

        # 月德合
        if self._is_yuedehe(sizhu):
            self._add_shensha('月德合', 12, '诸事吉利')

        # 大黄道吉日
        da_huangdao = self._get_da_huangdao(day_zhi, month_zhi)
        if da_huangdao:
            self._add_shensha(f'大黄道-{da_huangdao}', 15, '黄道吉日，诸事皆宜')

        # 小黄道吉日（十二建星）
        xiao_huangdao = self._get_xiao_huangdao(day_zhi, month_zhi)
        if xiao_huangdao:
            self._add_shensha(f'小黄道-{xiao_huangdao}', 8, '建星吉日')

        # ===== 日神类吉神 =====
        # 2026-10 A4：注册名由 '三奇-{type}' 统一为 '三奇{type}'（与基类及
        # 九事项同名）；('入学/求医/签约','三奇-日/月') 旧键同步删除，
        # 未列管的星奇仍按调用处默认值 15（SHENSHA_SCORES 单一表决议不变）。
        sanqi_type = self._is_sanqi(sizhu)
        if sanqi_type:
            self._add_shensha(f'三奇{sanqi_type}', 15, '三奇加临，百事皆宜')

        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星镇护，权威显赫')

        if self._is_yima(sizhu):
            self._add_shensha('驿马', 10, '驿马驰驱，出行吉利')

        # 2026-10 A1：日作用域 '天马'(+8) 与月作用域 '天马'(+10) 同名，
        # 月作用域先执行必获胜出，本块本为死分支；'鸣吠日'/'鸣吠对日'
        # （旧名鸣犬）与月作用域同名同谓词，亦为死分支——一并删除。

        if self._is_tianshe(sizhu):
            self._add_shensha('天赦日', 25, '天赦解围，诸凶皆赦')

        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 10, '母仓养畜，利畜牧')

        if self._is_xiangri(sizhu):
            self._add_shensha('相日', 10, '相日旺相，诸事可行')

        if self._is_minri(sizhu):
            self._add_shensha('民日', 8, '民日顺行，宜用民事')

        # E7 旺日：删除'旺日'异名注册（D=0，alias 归一为'王日'，基类已注册）

        if self._is_shangji(sizhu):
            self._add_shensha('上吉日', 12, '上吉之日，百事皆宜')

        if self._is_shengqi(sizhu):
            self._add_shensha('生气', 10, '生气蓬勃，利长养')

        # 2026-09-22：删除日作用域的 '要安' 冗余登记——月作用域已按同一
        # 谓词 _is_yaoan 登记同名条目，_add_shensha 去重使此处永远不生效
        # （死分支）。要安唯一生效点保留在上方月作用域。

        # 2026-10 批7b（001 §80.8）：'益后'/'续世' 日块同名重加删除——本类
        # 月块已按同一谓词各发射 +12/+10（通用 override 月块不调 super，基类
        # 月块对本类不执行，月块为唯一活发射；check 月先日后），日块重加被
        # _add_shensha 先到先得去重，从未生效（死链）。删除零行为差，
        # 运行时实证见 001 §80.8。

        if self._is_wuhe(sizhu):
            self._add_shensha('五合', 10, '五合之日，合和美好')

        if self._is_liuhe(sizhu):
            self._add_shensha('六合', 12, '六合之日，诸事合和')

        if self._is_sanhe(sizhu):
            self._add_shensha('三合', 10, '三合之日，合作顺利')

        if self._is_tianyi_day(sizhu):
            self._add_shensha('天医日', 8, '天医主吉，无疾')

        if self._is_tianwu_day(sizhu):
            self._add_shensha('天巫日', 8, '天巫为吉，祈福灵验')

        # ===== 日神类凶煞 =====
        # 十恶大败发射行已注释（2026-10-19 全删批·一档，001 §139）：三库无
        # 「十恶大败」普适日课忌明文（取证 aa47dcd／快照 2ca7b4e；协纪
        # 「然惟随各年及本命避之」属本命避忌，非日课普适扣分）；谓词保留作无禄日载体。
        # if self._is_shie_dabai(sizhu):
        #     self._add_shensha('十恶大败', -30, '忌大事，犯之主败')

        # 受死日×通用已删（2026-10-20 受死日删除批，001 §145）：本类由入学/
        # 求医/签约/通用共用，通用事项无载（陈书 p54「凡事皆忌者，非」为反向
        # 明载），按 _std_event 门控仅排除通用，其余三事项保留
        #（快照 docs/影响面快照_受死日删除候选.md §一）。
        if (self._is_shousi_day(sizhu)
                and getattr(self, '_std_event', None) != '通用'):
            self._add_shensha('受死日', -22, '受死之日，大忌')

        # 往亡日——P2 部分匹配拆分双链补拦（2026-10-18，001 §123）：本块发射名
        # 「往亡日」经 _SHENSHA_ALIAS_KEY 归一为「往亡」，与上方月块「往亡」构成
        # 双活链（同名先到先得互为占位）——仅拦月块则打戳后日块顶上，行为回弹
        # （实测 2026 全年往亡 30 天×3 事项零消失后定位）。入学/签约子项删除。
        if self._is_wangwang(sizhu) and getattr(self, '_std_event', None) not in ('入学', '签约'):
            self._add_shensha('往亡日', -20, '往亡之日，大忌远行')

        if self._is_guchen_guasu(sizhu):
            self._add_shensha('孤辰寡宿', -15, '孤辰寡宿，孤独无依')

        if self._is_hongsha(sizhu):
            self._add_shensha('红砂日', -15, '红砂日，诸事不宜')

        if self._is_yanggongji(sizhu):
            self._add_shensha('杨公忌日', -20, '杨公忌日，百事不宜')

        if self._is_huangsha(sizhu):
            self._add_shensha('黄沙日', -12, '黄沙日，忌嫁娶')

        if self._is_shenhao(sizhu):
            self._add_shensha('神号日', -10, '神号之日，当防惊吓')

        if self._is_guiqi(sizhu):
            self._add_shensha('鬼哭日', -10, '鬼哭之日，防鬼魅')

        if self._is_tiangang(sizhu):
            self._add_shensha('天罡日', -10, '天罡之日，忌用')

        if self._is_hekui(sizhu):
            self._add_shensha('河魁日', -10, '河魁之日，忌用')

        if self._is_tiandihuo(sizhu):
            self._add_shensha('天火日', -12, '天火日，忌用火')

        if self._is_dihuo(sizhu):
            self._add_shensha('地火日', -10, '地火日，忌动土')

        # 2026-10-21 口径收口批（001 §153）：反支日全事项删除——协纪卷十仅忌
        # 上册进表章/陈词讼（帝王用事，软件无对应通道），取证稿 §1.5。
        # 原发射为：
        #     if self._is_fanzhi(sizhu):
        #         self._add_shensha('反支日', -12, '反支日，忌上书')

        if self._is_shangshuo(sizhu):
            self._add_shensha('上朔日', -10, '上朔日，忌用')

        if self._is_qiwangwang(sizhu):
            self._add_shensha('气往亡', -15, '气往亡之日，大忌')

        if self._is_kuigang(sizhu):
            self._add_shensha('魁罡日', -15, '魁罡日，刚烈之日')

        # 2026-10-21 口径收口批（001 §153）：天恩通道外延仅「与修造吉神并尤宜
        # 兴作」（卷十条件增益句），本通道服务移徙/入学/求医/签约/通用，
        # 无修造，发射删除（取证稿 §1.1，13 项 ❌）。A1 的 15 日柱起例保留。
        # 原发射为：
        #     if self._is_tianen(sizhu):
        #         self._add_shensha('天恩', 10, '天恩日吉')

    def _check_hour_shensha(self, sizhu, **kwargs):
        """检查时神煞"""
        hour_zhi = sizhu['hour_zhi']
        day_zhi = sizhu['day_zhi']

        # 黄道吉时
        huangdao_shi = self._get_huangdao_shi(day_zhi, hour_zhi)
        if huangdao_shi:
            self._add_shensha(f'黄道时-{huangdao_shi}', 8, '时辰吉利')

        # 日破时
        if hour_zhi == self._get_suipo(day_zhi):
            self._add_shensha('日破时', -10, '时辰与日支相冲')

    # ===== 辅助方法 =====

    def _get_suipo(self, zhi):
        """获取冲支（岁破/月破/日破）"""
        zh_list = DI_ZHI
        idx = zh_list.index(zhi)
        return zh_list[(idx + 6) % 12]

    def _get_yuepo(self, month_zhi):
        """获取月破"""
        return self._get_suipo(month_zhi)

    def _is_nian_sansha(self, sizhu):
        """是否年支三煞"""
        try:
            from ..工具函数 import SANSHA_MAP
        except ImportError:
            from 工具函数 import SANSHA_MAP
        year_zhi = sizhu['year_zhi']
        day_zhi = sizhu['day_zhi']
        zh_list = DI_ZHI

        if year_zhi in SANSHA_MAP:
            sansha_indices = SANSHA_MAP[year_zhi]
            day_idx = zh_list.index(day_zhi)
            return day_idx in sansha_indices
        return False

    def _is_yuexing(self, sizhu):
        """是否月刑"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        xing_map = {
            '寅': '巳', '巳': '申', '申': '寅',
            '丑': '戌', '戌': '未', '未': '丑',
            '子': '卯', '卯': '子',
            '辰': '辰', '午': '午', '酉': '酉', '亥': '亥'
        }
        return day_zhi == xing_map.get(month_zhi)

    def _is_yuehai(self, sizhu):
        """是否月害"""
        month_zhi = sizhu['month_zhi']
        day_zhi = sizhu['day_zhi']

        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        return day_zhi == hai_map.get(month_zhi)

    def _is_sifei(self, sizhu):
        """是否四废日（《协纪》四季衰废：春庚申辛酉、夏壬子癸亥、
        秋甲寅乙卯、冬丙午丁巳；委托单点出口 is_sifei_by_pillar）。
        """
        return is_sifei_by_pillar(sizhu['month_zhi'],
                                  sizhu['day_gan'] + sizhu['day_zhi'])

    # 【保留·无禄日历法概念载体】（2026-10-19 全删批·一档）：起例 10 干支日与
    # 协纪/考原无禄日 12/12 全等，概念合典据，谓词保留不删；日课扣分发射行
    # 已全部注释清零（三库无普适日忌明文），规则引擎残留引用随二档批删除。
    def _is_shie_dabai(self, sizhu):
        """是否十恶大败"""
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']
        day_pillar = day_gan + day_zhi

        shie_dabai = ['甲辰', '乙巳', '丙申', '丁亥', '戊戌', '己丑', '庚辰', '辛巳', '壬申', '癸亥']
        return day_pillar in shie_dabai

    def _is_tiande(self, sizhu):
        """是否天德

        比较维度（2026-09-19 锚点③修复）：天干型比日干；
        地支型（卯月申/午月亥/酉月寅/子月巳，四维月取宫内地支）比日支。
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        td = TIANDE.get(idx)
        if td in DI_ZHI:
            return sizhu.get('day_zhi', '') == td
        return day_gan == td

    def _is_yuede(self, sizhu):
        """是否月德"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']
        zh_list = DI_ZHI
        idx = zh_list.index(month_zhi)
        return day_gan == YUEDE.get(idx)

    def _is_tiandehe(self, sizhu):
        """是否天德合（月支→天德合值直查表）

        比较维度（2026-09-19 锚点③修复）：合值为天干时比日干（五合）；
        合值为地支时（卯巳/午寅/酉亥/子申，六合）比日支（原比日干恒为 False）。
        """
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']

        tiandehe_map = {
            '寅': '壬', '卯': '巳', '辰': '丁', '巳': '丙',
            '午': '寅', '未': '己', '申': '戊', '酉': '亥',
            '戌': '辛', '亥': '庚', '子': '申', '丑': '乙'
        }
        he = tiandehe_map.get(month_zhi)
        if he in DI_ZHI:
            return sizhu.get('day_zhi', '') == he
        return day_gan == he

    def _is_yuedehe(self, sizhu):
        """是否月德合"""
        month_zhi = sizhu['month_zhi']
        day_gan = sizhu['day_gan']

        yuedehe_map = {
            '寅': '辛', '午': '辛', '戌': '辛',
            '申': '丁', '子': '丁', '辰': '丁',
            '亥': '己', '卯': '己', '未': '己',
            '巳': '乙', '酉': '乙', '丑': '乙'
        }
        return day_gan == yuedehe_map.get(month_zhi)

    def _get_da_huangdao(self, day_zhi, month_zhi):
        """获取大黄道十二值星"""
        zh_list = DI_ZHI
        huangdao_list = ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德',
                         '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']

        try:
            month_idx = zh_list.index(month_zhi)
            day_idx = zh_list.index(day_zhi)
            huangdao_idx = (day_idx - 2 * month_idx + 4) % 12
            return huangdao_list[huangdao_idx]
        except:
            return None

    def _get_xiao_huangdao(self, day_zhi, month_zhi):
        """获取小黄道十二建星"""
        jianxing_list = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
        zh_list = DI_ZHI

        month_idx = zh_list.index(month_zhi)
        day_idx = zh_list.index(day_zhi)

        offset = (day_idx - month_idx) % 12
        return jianxing_list[offset]

    def _get_huangdao_shi(self, day_zhi, hour_zhi):
        """获取黄道吉时
        【单一权威规则来源】J2（2026-10-01，001 §57）按《协纪辨方书·卷七》
        引《考原》日支起青龙于时支正宗起例：
            寅申起子、卯酉起寅、辰戌起辰，
            巳亥起午、子午起申、丑未起戌，顺行十二辰。
        与 modules/黄道.py DA_HUANG_DAO_TABLE 及 modules/婚嫁评分算法.py
        HUANGDAO_SHI_TABLE 严格逐字节一致；亦与 modules/今日黄历.py
        QINGLONG_SHICHEN_MAP 起例等价。
        【J2 之前错误】：旧表六组中四组起例错（子午/丑未/寅申/巳亥），
        导致非嫁娶择日类型（入宅/修造/安葬/出行/动土/作灶/安床/开业等）的
        吉时判定大面积错位。
        修正：直接复用单点权威 DA_HUANG_DAO_TABLE 查表。
        """
        # 运行时延迟加载：避免循环import（因为黄道计算器内部可能import shensha）
        try:
            from ..黄道 import 黄道计算器
            _cal = 黄道计算器()
            DA_HUANG_DAO_TABLE = _cal.DA_HUANG_DAO_TABLE
        except Exception:
            # 兜底：与权威表完全一致的同值拷贝（保证该方法不依赖import也能正确）
            DA_HUANG_DAO_TABLE = {
                '子': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
                '午': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
                '丑': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
                '未': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
                '寅': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
                '申': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
                '卯': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
                '酉': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
                '辰': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
                '戌': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
                '巳': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德'],
                '亥': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德'],
            }
        if day_zhi not in DA_HUANG_DAO_TABLE:
            return None
        zh_list = self.DI_ZHI if hasattr(self, 'DI_ZHI') else ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        try:
            hour_idx = zh_list.index(hour_zhi)
            shi_xing = DA_HUANG_DAO_TABLE[day_zhi][hour_idx]
        except (ValueError, IndexError):
            return None
        huangdao_xing = ['青龙', '明堂', '金匮', '天德', '玉堂', '司命']
        if shi_xing in huangdao_xing:
            return shi_xing
        return None

    # ===== 新增缺失的神煞检查方法 =====

    def _is_tianwu_day(self, sizhu):
        """天巫日（月建前二辰）

        依据《协纪辨方书·卷四·义例二》与《御定星历考原·卷三》引《总要历》：
        「天巫者，月中善神也。所值之日宜合药请医，祀鬼神求福愿」，
        《历例》曰：「（天巫）常居月建前二辰」——即寅月辰日、卯月巳日、
        辰月午日……（月支序 + 2）。

        同书卷四「建除同位异名」列「满【福德 天巫 天狗】」可互证：正月建寅，
        寅为建、卯为除、辰为满，天巫即满日，正合"月建前二辰"。

        2026-09-16修复（第二批）：原实现为"月支后四位"（月支序 + 4，寅月午日），
        与年作用域 _is_tianwu_year（年支后八位，亦 +4）各执一套起例，二者均无典籍
        依据。天巫本为月神，只有"月建前二辰"一法，故按典籍口径更正为月支序 + 2。
        """
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        if month_zhi in zh_list and day_zhi in zh_list:
            idx = zh_list.index(month_zhi)
            tianwu = zh_list[(idx + 2) % 12]
            return day_zhi == tianwu
        return False

    def _is_dahao(self, sizhu):
        """大耗（月支前六位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        if month_zhi in zh_list:
            idx = zh_list.index(month_zhi)
            dahao = zh_list[(idx + 6) % 12]
            return day_zhi == dahao
        return False

    def _is_xiaohao(self, sizhu):
        """小耗（月支后六位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        if month_zhi in zh_list:
            idx = zh_list.index(month_zhi)
            xiaohao = zh_list[(idx - 6) % 12]
            return day_zhi == xiaohao
        return False

    # _is_fuduan 已删除（2026-10 A6-3）：旧为"月支冲日支"副本（与月破同表），
    # 统一继承基类 _is_fuduan（委托 is_fuduan_by_zhi，月支相害日支六害口径）。

    # 归忌 _is_guiji 已删除（2026-10 A5 收口）：旧"月支前七位"系偏移错，
    # 回归基类 is_guiji_by_zhi（《协纪·历例》孟月丑/仲月寅/季月子）。

    # _is_hongzui_zhuque 已删除（红嘴朱雀按典修批 A，2026-10-20）：旧「月支
    # 对冲+2（等价月支+8）」月起例与陈书 p890「日干支×九宫飞」全异，且通用
    # 事项按典不注册该煞。起例统一收口基类。原实现留档备反证：
    #     chong = {'子': '午', ...}[month_zhi]; idx = DI_ZHI.index(chong)
    #     return day_zhi == DI_ZHI[(idx + 2) % 12]

    def _is_tiangou(self, sizhu):
        """天狗（月支对冲后三位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        duichong = chong_map.get(month_zhi, '')
        if duichong and duichong in zh_list:
            idx = zh_list.index(duichong)
            tiangou = zh_list[(idx - 3) % 12]
            return day_zhi == tiangou
        return False

    def _is_baihu(self, sizhu):
        """白虎（月支前九位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        if month_zhi in zh_list:
            idx = zh_list.index(month_zhi)
            baihu = zh_list[(idx + 9) % 12]
            return day_zhi == baihu
        return False

    def _is_zhuque(self, sizhu):
        """朱雀（月支后九位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        if month_zhi in zh_list:
            idx = zh_list.index(month_zhi)
            zhuque = zh_list[(idx - 9) % 12]
            return day_zhi == zhuque
        return False

    def _is_wuhe(self, sizhu):
        """五合日（日支为寅或卯）

        依据《协纪辨方书·卷五·义例三》引《历例》：「五合者，寅卯日也」，
        其日宜结婚姻、会亲友、立券、交易（与五行择日法 EVENT_RULES 中
        '立券交易' 宜 '五合' 一致）；对冲之申酉日即五离。

        2026-09-16修复：原实现用日干、日支各查六合表后互相回查，
        `gan_liuhe.get(gan_he) == day_gan` 对任何合法干支必然成立，
        导致 60 甲子全部命中，'五合' 每天都虚加 10 分。
        """
        day_zhi = sizhu.get('day_zhi', '')
        return day_zhi in ('寅', '卯')

    def _is_guchen_guasu(self, sizhu):
        """孤辰寡宿（年支查法）
        亥子丑年寅、寅卯辰年巳、巳午未年申、申酉戌年亥
        """
        year_zhi = sizhu.get('year_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        guchen_map = {
            '亥': '寅', '子': '寅', '丑': '寅',
            '寅': '巳', '卯': '巳', '辰': '巳',
            '巳': '申', '午': '申', '未': '申',
            '申': '亥', '酉': '亥', '戌': '亥'
        }
        guasu_map = {
            '亥': '戌', '子': '戌', '丑': '戌',
            '寅': '丑', '卯': '丑', '辰': '丑',
            '巳': '辰', '午': '辰', '未': '辰',
            '申': '未', '酉': '未', '戌': '未'
        }
        return day_zhi == guchen_map.get(year_zhi) or day_zhi == guasu_map.get(year_zhi)

    def _is_yanggongji(self, sizhu):
        """杨公忌日（2026-09-20 收敛：改委托基类模块级 is_yanggongji_by_lunar）

        原月支日支表为错表（与真表 2026 仅 2 天碰巧重合，漏 12 误 26），已删除。
        """
        return is_yanggongji_by_lunar(sizhu)

    def _is_tiangang(self, sizhu):
        """天罡日（月支前五位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        if month_zhi in zh_list:
            idx = zh_list.index(month_zhi)
            tiangang = zh_list[(idx + 5) % 12]
            return day_zhi == tiangang
        return False

    def _is_hekui(self, sizhu):
        """河魁日（月支后五位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = DI_ZHI
        if month_zhi in zh_list:
            idx = zh_list.index(month_zhi)
            hekui = zh_list[(idx - 5) % 12]
            return day_zhi == hekui
        return False

    def _is_tiandihuo(self, sizhu):
        """天火日（春酉、夏午、秋卯、冬子）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        if month_zhi in ['寅', '卯', '辰']:
            return day_zhi == '酉'
        elif month_zhi in ['巳', '午', '未']:
            return day_zhi == '午'
        elif month_zhi in ['申', '酉', '戌']:
            return day_zhi == '卯'
        elif month_zhi in ['亥', '子', '丑']:
            return day_zhi == '子'
        return False

    def _is_dihuo(self, sizhu):
        """地火日（春午、夏卯、秋子、冬酉）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        if month_zhi in ['寅', '卯', '辰']:
            return day_zhi == '午'
        elif month_zhi in ['巳', '午', '未']:
            return day_zhi == '卯'
        elif month_zhi in ['申', '酉', '戌']:
            return day_zhi == '子'
        elif month_zhi in ['亥', '子', '丑']:
            return day_zhi == '酉'
        return False

    def _is_qiwangwang(self, sizhu):
        """气往亡（节气前一日冲支）"""
        try:
            from datetime import date as date_type, timedelta
            target_date = None
            if 'date' in sizhu:
                target_date = sizhu['date']
                if not isinstance(target_date, date_type):
                    target_date = None
            if target_date is None:
                year = sizhu.get('year')
                month = sizhu.get('month')
                day = sizhu.get('day')
                if year and month and day:
                    try:
                        target_date = date_type(int(year), int(month), int(day))
                    except (ValueError, TypeError):
                        return False
            if target_date is None:
                return False
            year = target_date.year
            ershiba_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
            term_dates = self._get_solar_term_dates(year, ershiba_indices)
            for term_date in term_dates:
                prev_day = term_date - timedelta(days=1)
                if target_date == prev_day:
                    day_zhi = sizhu.get('day_zhi', '')
                    month_zhi = sizhu.get('month_zhi', '')
                    chong_map = {
                        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
                        '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
                        '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
                    }
                    return day_zhi == chong_map.get(month_zhi)
            return False
        except Exception:
            return False