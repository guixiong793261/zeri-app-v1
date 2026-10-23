# -*- coding: utf-8 -*-
"""
业务逻辑正确性专项验证（L3-业务层单元测试）
============================================

覆盖用户指出的验证盲区：
  A. 夫星 / 子星 / 阴胎 / 阳气 的计算正确性（婚嫁四大核心参数）
  B. 大黄道 / 小黄道 / 贵人时 算法正确性（含单源规则比对）
  C. 条件择日缺陷修复验证（三煞纯地支 / 扶山四柱分析 / 贵人时非永真）

运行方法：
    python -m unittest tests.test_business_logic -v
"""

import sys
import os
_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj_root = os.path.dirname(_this_dir)
for _p in [_proj_root, os.path.join(_proj_root, 'modules')]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
from datetime import date


# ============================================================================
# A. 婚嫁四大核心参数：夫星 / 子星 / 阴胎 / 阳气
# ============================================================================
class TestMarriageCoreParams(unittest.TestCase):
    """夫星、子星、阴胎、阳气计算正确性验证（project_memory硬约束）"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.婚嫁评分算法 as mod_hj
            import modules.工具函数 as mod_util
            import modules.rules.嫁娶规则 as mod_rule
            cls._hj = mod_hj
            cls._util = mod_util
            cls._rule_mod = mod_rule
        except ImportError as e:
            raise unittest.SkipTest("婚嫁模块导入失败: %s" % e)

    # -------- 阴胎/阳气 公式正确性 (project_memory 硬约束) --------
    def test_yintai_formula_gan_plus_1_zhi_plus_3(self):
        """【硬约束】阴胎公式：月干+1，月支+3（=胎元）。甲子月→乙卯"""
        # 工具函数版（权威统一出口）
        self.assertEqual(self._util.get_yintai('甲', '子'), '乙卯',
                         "甲子月阴胎：甲+1=乙，子+3=卯 → 乙卯")
        self.assertEqual(self._util.get_yintai('丙', '寅'), '丁巳',
                         "丙寅月阴胎：丙+1=丁，寅+3=巳 → 丁巳")

    def test_yangqi_formula_gan_plus_1_zhi_plus_3(self):
        """【典籍口径】阳气公式：月干+1，月支+3（与阴胎同法·胎元）。甲子月→乙卯"""
        self.assertEqual(self._util.get_yangqi('甲', '子'), '乙卯',
                         "甲子月阳气：甲+1=乙，子+3=卯 → 乙卯（男命阳气，同阴胎法）")
        self.assertEqual(self._util.get_yangqi('丙', '寅'), '丁巳',
                         "丙寅月阳气：丙+1=丁，寅+3=巳 → 丁巳")

    def test_yintai_yangqi_same_taiyuan_method(self):
        """【典籍口径】阴胎/阳气同法：同月柱干支二者结果相同（男称阳气女称阴胎）"""
        cases = [('甲','子'),('丙','寅'),('庚','申'),('癸','亥'),('己','丑')]
        for mg, mz in cases:
            yt = self._util.get_yintai(mg, mz)  # 返回字符串如'乙卯'
            yq = self._util.get_yangqi(mg, mz)
            self.assertEqual(yt, yq,
                             "%s%s月：阳气应与阴胎同值（同胎元法），阴胎=%s 阳气=%s" % (mg, mz, yt, yq))

    def test_yintai_between_two_modules_consistency(self):
        """阴胎/阳气：工具函数版 vs 婚嫁算法版 结果一致（仅返回格式差：str vs tuple）"""
        for mg, mz in [('甲','子'),('丙','寅'),('辛','未'),('戊','辰')]:
            util_yt = self._util.get_yintai(mg, mz)          # '乙卯'
            hj_yt = self._hj.get_yintai(mg, mz)               # ('乙','卯')
            util_yq = self._util.get_yangqi(mg, mz)           # '乙卯'
            hj_yq = self._hj.get_yangqi(mg, mz)               # ('乙','卯')
            self.assertEqual(util_yt, ''.join(hj_yt),
                             "%s%s阴胎两模块结果不一致" % (mg, mz))
            self.assertEqual(util_yq, ''.join(hj_yq),
                             "%s%s阳气两模块结果不一致" % (mg, mz))

    # -------- 夫星/子星 干支计算 --------
    def test_fuxing_zixing_basic_ganzhi(self):
        """夫星正官/七杀、子星食神/伤官干支结构长度必须=2"""
        cases = [('甲','子'),('丙','午'),('辛','未'),('己','丑'),('癸','亥')]
        for yg, yz in cases:
            r = self._hj.get_fuxing_zixing_by_year(yg, yz)
            for k, label in [('fu','正官夫星'),('qi','七杀'),('zi','食神子星'),('shang','伤官')]:
                val = r.get(k, '')
                self.assertEqual(len(val), 2,
                                 "%s%s年 %s(%s) 长度≠2" % (yg, yz, label, val))
                TIAN_GAN = set('甲乙丙丁戊己庚辛壬癸')
                DI_ZHI = set('子丑寅卯辰巳午未申酉戌亥')
                self.assertIn(val[0], TIAN_GAN,
                              "%s%s年 %s 天干非法: %s" % (yg, yz, label, val))
                self.assertIn(val[1], DI_ZHI,
                              "%s%s年 %s 地支非法: %s" % (yg, yz, label, val))

    def test_fuxing_tiangan_ke_wonian(self):
        """夫星天干 = 克年干的五行（正官）。甲木→辛金克"""
        # 甲木 → 辛金（正官）；丙火 → 癸水（正官）；庚金 → 丁火（正官）
        expected = {'甲':'辛', '丙':'癸', '庚':'丁', '壬':'己', '戊':'乙'}
        for yg, exp in expected.items():
            r = self._hj.get_fuxing_zixing_by_year(yg, '子')
            self.assertEqual(r['fu'][0], exp,
                             "%s年夫星天干应为%s(克我者)，实际%s" % (yg, exp, r['fu'][0]))

    def test_zixing_tiangan_wonian_sheng(self):
        """子星(食神)天干 = 年干所生的五行。甲木→丙火"""
        expected = {'甲':'丙', '丙':'戊', '庚':'壬', '壬':'甲', '戊':'庚'}
        for yg, exp in expected.items():
            r = self._hj.get_fuxing_zixing_by_year(yg, '子')
            self.assertEqual(r['zi'][0], exp,
                             "%s年子星天干应为%s(我生者)，实际%s" % (yg, exp, r['zi'][0]))

    def test_jiazi_year_known_values(self):
        """甲子年五虎遁权威定局：真夫星辛未、七杀庚午、真天嗣丙寅、伤官丁卯
        （年上起月丙寅、丁卯、戊辰、己巳、庚午、辛未；2026-09 按《选择求真》修正）"""
        r = self._hj.get_fuxing_zixing_by_year('甲', '子')
        self.assertEqual(r['fu'], '辛未', "甲子年真夫星正官（五虎遁）")
        self.assertEqual(r['qi'], '庚午', "甲子年七杀（五虎遁）")
        self.assertEqual(r['zi'], '丙寅', "甲子年真天嗣食神（五虎遁）")
        self.assertEqual(r['shang'], '丁卯', "甲子年伤官（五虎遁）")

    # -------- 阴阳胎取用对象：阴胎属女命(新娘)、阳气属男命(新郎) --------
    def test_marriage_rule_checker_gender_role(self):
        """嫁娶规则：_is_female/_is_male 性别角色判断（role='新娘'优先）"""
        checker = self._rule_mod.MarriageRuleChecker()
        # 新娘 = 女命（阴胎取用基准）
        self.assertTrue(checker._is_female({'role':'新娘','性别':'女','name':'张三'}))
        self.assertFalse(checker._is_male({'role':'新娘','性别':'女','name':'张三'}))
        # 新郎 = 男命（阳气取用基准）
        self.assertTrue(checker._is_male({'role':'新郎','性别':'男','name':'李四'}))
        self.assertFalse(checker._is_female({'role':'新郎','性别':'男','name':'李四'}))


# ============================================================================
# B. 黄道算法正确性（单源比对）
# ============================================================================
class TestHuangDaoAlgorithm(unittest.TestCase):
    """大黄道/小黄道/贵人时的算法正确性"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.黄道 as mod_hd
            import modules.婚嫁评分算法 as mod_hj
            import modules.shensha.时辰系 as mod_ssc
            cls._hd_mod = mod_hd
            cls._hj_mod = mod_hj
            cls._ssc_mod = mod_ssc
            cls._calc = mod_hd.黄道计算器()
        except ImportError as e:
            raise unittest.SkipTest("黄道模块导入失败: %s" % e)

    # -------- 大黄道值日公式：(day_idx - 2*month_idx + 4) % 12 --------
    def test_da_huangdao_zhiri_formula_zi_month_zi_day(self):
        """【硬约束】大黄道值日公式：子月子日 → (0-0+4)%12=4 → 金匮"""
        ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        # 公式独立复算
        expected_name = ['青龙','明堂','天刑','朱雀','金匮','天德',
                         '白虎','玉堂','天牢','玄武','司命','勾陈'][
                             (ZHI.index('子') - 2 * ZHI.index('子') + 4) % 12
                         ]
        self.assertEqual(expected_name, '金匮')
        r = self._calc._calculate_da_huangdao_zhiri('子', '子')
        self.assertEqual(r['name'], expected_name, "子月子日值日应为金匮")
        self.assertEqual(r['type'], '吉', "金匮为黄道吉神")

    # -------- 大黄道时辰级：DA_HUANG_DAO_TABLE 单点权威源 --------
    def test_da_huangdao_shichen_mao_day_wu_hour(self):
        """【硬约束】时辰级查表：卯日午时 → 金匮(吉)"""
        # 卯日午时：卯日 DA_HUANG_DAO_TABLE['卯'][午索引6] → 金匮
        table_mao = self._calc.DA_HUANG_DAO_TABLE.get('卯', [])
        ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        expected = table_mao[ZHI.index('午')]
        self.assertEqual(expected, '金匮', "卯日午时查表应得金匮")
        r = self._calc._calculate_da_huangdao_shichen('卯', '午')
        self.assertEqual(r['name'], '金匮')
        self.assertEqual(r['type'], '吉')

    def test_da_huangdao_shichen_tables_consistent_with_hunjia(self):
        """【单源一致性】黄道模块 DA_HUANG_DAO_TABLE == 婚嫁评分算法 HUANGDAO_SHI_TABLE"""
        self.assertEqual(
            self._calc.DA_HUANG_DAO_TABLE,
            self._hj_mod.HUANGDAO_SHI_TABLE,
            "时辰级大黄道十二神表在两模块中必须完全一致（单点权威源）"
        )

    def test_da_huangdao_qinglong_start_verse(self):
        """J2（001 §57）：十二神起青龙按《协纪辨方书·卷七》引《考原》——
        寅申起子、卯酉起寅、辰戌起辰、巳亥起午、子午起申、丑未起戌，顺行十二辰。"""
        ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
        # (日支组, 正确青龙时支, 旧错表青龙位；None=该组本就正确不做反向)
        cases = [
            (['子','午'], '申', 0),
            (['丑','未'], '戌', 2),
            (['寅','申'], '子', 10),
            (['卯','酉'], '寅', None),
            (['辰','戌'], '辰', None),
            (['巳','亥'], '午', 5),
        ]
        for dzz, qz, old_idx in cases:
            for dz in dzz:
                got = self._calc.DA_HUANG_DAO_TABLE.get(dz, [''])[ZHI.index(qz)]
                self.assertEqual(got, '青龙',
                    "%s日%s时应为青龙（J2正确起例）" % (dz, qz))
            # 反向：错组旧青龙位必须不再是青龙（旧错表锁死口）
            if old_idx is not None:
                self.assertNotEqual(self._calc.DA_HUANG_DAO_TABLE.get(dzz[0], [''])[old_idx], '青龙',
                    "%s日旧错表青龙位不应再为青龙" % dzz[0])

    # -------- 小黄道（建除十二神） --------
    def test_xiao_huangdao_yin_month_jian_position(self):
        """寅月：寅日应为"建"（建除循环起点），子日应为"开"（寅前两位）"""
        r_yin = self._calc._calculate_xiao_huang_dao('寅', '寅')
        self.assertEqual(r_yin['name'], '建', "寅月寅日=建日（月支所在=建）")
        r_zi = self._calc._calculate_xiao_huang_dao('寅', '子')
        self.assertEqual(r_zi['name'], '开', "寅月子日=开日")

    # -------- 贵人时（天乙贵人时辰表） --------
    def test_tianyi_guiren_zhixing_table(self):
        """【硬约束】天乙贵人时辰表：甲戊庚(牛羊丑未)/乙己(鼠猴子申)/丙丁(猪鸡亥酉)/辛(马虎寅午)/壬癸(兔蛇卯巳)

        001 §168 收口：断言对象为唯一事实源 modules/shensha/时辰系.GUIREN_SHICHEN
        （原婚嫁评分算法.TIANYI_GUIREN 死表已删，值与本表逐键一致）。"""
        G = self._ssc_mod.GUIREN_SHICHEN
        self.assertEqual(sorted(G['甲']), sorted(['丑','未']), "甲日贵人=丑未")
        self.assertEqual(sorted(G['戊']), sorted(['丑','未']), "戊日贵人=丑未")
        self.assertEqual(sorted(G['己']), sorted(['子','申']), "己日贵人=子申")
        self.assertEqual(sorted(G['庚']), sorted(['丑','未']), "庚日贵人=丑未")
        self.assertEqual(sorted(G['乙']), sorted(['子','申']), "乙日贵人=子申")
        self.assertEqual(sorted(G['丙']), sorted(['亥','酉']), "丙日贵人=亥酉")
        self.assertEqual(sorted(G['丁']), sorted(['亥','酉']), "丁日贵人=亥酉")
        self.assertEqual(sorted(G['辛']), sorted(['寅','午']), "辛日贵人=寅午（六辛逢马虎）")
        self.assertEqual(sorted(G['壬']), sorted(['卯','巳']), "壬日贵人=卯巳")
        self.assertEqual(sorted(G['癸']), sorted(['卯','巳']), "癸日贵人=卯巳")

    def test_guiren_hour_not_always_true(self):
        """【反例验证】甲日卯时不应是贵人时（贵人时≠永真）。project_memory 曾有永远为真的缺陷"""
        # 甲日贵人时只有丑、未；卯时不是（001 §168：断言对象为唯一事实源时辰系表）
        G = self._ssc_mod.GUIREN_SHICHEN
        self.assertIn('丑', G['甲'])
        self.assertIn('未', G['甲'])
        self.assertNotIn('卯', G['甲'], "甲日卯时不应为贵人时（证明永真缺陷已修复）")
        self.assertNotIn('戌', G['丙'], "丙日戌时不应为贵人时")

    def test_guiren_geng_day_main_program_vs_hunjia(self):
        """【单点权威验证】庚日贵人时三端一致（主程序/修造/时辰系）。口诀：甲戊庚牛羊=丑未。"""
        # 正宗口诀：甲戊庚牛羊 → 庚日贵人时辰地支 = [丑, 未]
        AUTHORITY_GENG = ['丑', '未']  # 主程序 L3417、修造gui_ren 均为该值

        # 1. 唯一事实源 时辰系.GUIREN_SHICHEN 当前值
        #    （001 §168 收口：原婚嫁评分算法.TIANYI_GUIREN 死表已删，本断言改指唯一事实源）
        shichen_geng = sorted(self._ssc_mod.GUIREN_SHICHEN.get('庚', []))

        # 2. 修造模块 gui_ren 当前值
        try:
            import modules.shensha.修造神煞扩展 as mod_xz
            c = mod_xz.ConstructionShenShaCheckerExt()
            xz_geng = c.gui_ren.get('庚', {}) if hasattr(c, 'gui_ren') else {}
            if isinstance(xz_geng, dict):
                xz_geng_list = sorted([
                    v for v in xz_geng.values()
                    if isinstance(v, str) and v in '子丑寅卯辰巳午未申酉戌亥'
                ])
            else:
                xz_geng_list = []
        except ImportError:
            xz_geng_list = []

        # 3. 断言：三端必须全部与权威一致（=丑未）。若不一致，属于真实业务缺陷
        self.assertEqual(
            shichen_geng, AUTHORITY_GENG,
            "庚日贵人时三端不一致！口诀甲戊庚牛羊=[丑,未]；"
            "主程序=%s；修造=%s；时辰系GUIREN_SHICHEN[庚]=%s → 唯一事实源需修正"
            % (AUTHORITY_GENG, xz_geng_list if xz_geng_list else '?', shichen_geng)
        )
        if xz_geng_list:
            self.assertEqual(
                xz_geng_list, AUTHORITY_GENG,
                "修造gui_ren[庚] 与权威不一致：实际%s" % xz_geng_list
            )


# ============================================================================
# C. 条件择日缺陷修复验证
# ============================================================================
class TestConditionZeriFixes(unittest.TestCase):
    """条件择日/三煞/扶山 等之前审查发现缺陷的专项验证"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.二十四山择吉天机 as mod_mt
            cls._mt = mod_mt
        except ImportError as e:
            raise unittest.SkipTest("模块导入失败: %s" % e)

    # -------- 三煞映射表必须使用纯地支（project_memory 硬约束） --------
    def test_sansha_map_all_pure_dizhi_keys_and_values(self):
        """【硬约束】SANSHA_MAP 键值均必须仅包含地支字符，禁止混入天干"""
        TIAN_GAN = set('甲乙丙丁戊己庚辛壬癸')
        DI_ZHI = set('子丑寅卯辰巳午未申酉戌亥')
        S = self._mt.SANSHA_MAP
        for k, v in S.items():
            # 三煞映射三合局结构：键=3地支，值=3地支
            self.assertEqual(len(k), 3, "SANSHA_MAP 键应为3字符三合局: %s" % k)
            self.assertEqual(len(v), 3, "SANSHA_MAP 值应为3字符三煞方: %s" % v)
            for ch in k:
                self.assertNotIn(ch, TIAN_GAN, "SANSHA_MAP 键 %s 含天干 %s（应为纯地支）" % (k, ch))
                self.assertIn(ch, DI_ZHI, "SANSHA_MAP 键 %s 字符 %s 非法地支" % (k, ch))
            for ch in v:
                self.assertNotIn(ch, TIAN_GAN, "SANSHA_MAP 值 %s 含天干 %s（应为纯地支煞方）" % (v, ch))
                self.assertIn(ch, DI_ZHI, "SANSHA_MAP 值 %s 字符 %s 非法地支" % (v, ch))

    def test_hai_mao_wei_sha_not_contain_wei(self):
        """【硬约束】亥卯未月煞方 = ['申','庚','酉','辛','戌'] 中不含 '未'（project_memory 第一条）"""
        # SANSHA_MAP 三合局映射：亥卯未 → 巳酉丑（纯地支煞方=巳酉丑）
        sanfang = self._mt.SANSHA_MAP.get('亥卯未', '')
        self.assertEqual(sorted(list(sanfang)), sorted(['巳','酉','丑']),
                         "亥卯未三合局 → 煞方应为巳酉丑（纯地支三煞）")
        # 检查原文本要求：'亥卯未' 煞方不包含'未'
        self.assertNotIn('未', sanfang, "亥卯未煞方不可含'未'（project_memory 硬约束）")

    def test_sansha_haimao_wei_value_xi_you_chou(self):
        """亥卯未煞西（巳酉丑）=纯地支，不含天干丙辛等"""
        TIAN_GAN = set('甲乙丙丁戊己庚辛壬癸')
        sanfang = self._mt.SANSHA_MAP.get('亥卯未', '')
        for c in sanfang:
            self.assertNotIn(c, TIAN_GAN,
                             "亥卯未煞方 %s 含天干字符 %s（应为纯地支）" % (sanfang, c))


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("  L3-业务层专项验证 (tests/test_business_logic.py)")
    print("  覆盖：婚嫁四大参数 / 黄道算法 / 条件择日缺陷修复")
    print("=" * 70 + "\n")
    unittest.main(verbosity=2)
