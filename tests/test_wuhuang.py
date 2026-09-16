# -*- coding: utf-8 -*-
"""
年家五黄煞计算单元测试
=====================
验证年家紫白飞星五黄推算逻辑（二十四山择吉天机.py / 二十四山.py）。

运行方法（-B 避免写 __pycache__）:
    cd /d 项目根目录
    python -B -m unittest tests.test_wuhuang -v
    或: python -B tests/test_wuhuang.py

【权威基准】（与通书公开口径一致）
    2023 癸卯年：四绿入中，五黄到乾宫（戌乾亥，西北）
    2024 甲辰年：三碧入中，五黄到兑宫（庚酉辛，正西）
    2025 乙巳年：二黑入中，五黄到艮宫（丑艮寅，东北）
    2026 丙午年：一白入中，五黄到离宫（丙午丁，正南）
    2027 丁未年：九紫入中，五黄到坎宫（壬子癸，正北）
    锚点：1864甲子年一白入中；1984甲子年（下元起）七赤入中
"""

import sys
import os
import unittest

# ---------------------------------------------------------------------------
# 路径配置（确保以脚本方式或模块方式均可运行）
# ---------------------------------------------------------------------------
_this_dir = (getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable))) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)))
_proj_root = os.path.dirname(_this_dir)
for _p in [_proj_root, os.path.join(_proj_root, 'modules')]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ==========================================================================
# Test Case 1: 年家紫白飞星入中星与五黄宫位（二十四山择吉天机）
# ==========================================================================
class TestWuhuangPalace(unittest.TestCase):
    """年家紫白飞星入中星与五黄宫位推算验证（重点：2024-2026）"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.二十四山择吉天机 as mod_mt
            cls._mod = mod_mt
        except ImportError as e:
            raise unittest.SkipTest(f"二十四山择吉天机模块导入失败: {e}")

    def test_zhongxing_anchor_1864_1984(self):
        """入中星锚点：1864甲子一白入中、1984甲子（下元起）七赤入中"""
        self.assertEqual(self._mod.get_nian_jia_zibai_zhongxing(1864), 1,
                         "1864甲子年应一白入中")
        self.assertEqual(self._mod.get_nian_jia_zibai_zhongxing(1984), 7,
                         "1984甲子年（下元起）应七赤入中")

    def test_zhongxing_2024_2026(self):
        """入中星验证：2024三碧、2025二黑、2026一白"""
        self.assertEqual(self._mod.get_nian_jia_zibai_zhongxing(2024), 3,
                         "2024甲辰年应三碧入中")
        self.assertEqual(self._mod.get_nian_jia_zibai_zhongxing(2025), 2,
                         "2025乙巳年应二黑入中")
        self.assertEqual(self._mod.get_nian_jia_zibai_zhongxing(2026), 1,
                         "2026丙午年应一白入中")

    def test_wuhuang_palace_2024(self):
        """2024甲辰年五黄到兑宫（庚酉辛，正西）"""
        self.assertEqual(self._mod.get_wuhuang_palace(2024), '兑')
        self.assertEqual(self._mod.get_wuhuang_mountains(2024), ['庚', '酉', '辛'])

    def test_wuhuang_palace_2025(self):
        """2025乙巳年五黄到艮宫（丑艮寅，东北）"""
        self.assertEqual(self._mod.get_wuhuang_palace(2025), '艮')
        self.assertEqual(self._mod.get_wuhuang_mountains(2025), ['丑', '艮', '寅'])

    def test_wuhuang_palace_2026(self):
        """2026丙午年五黄到离宫（丙午丁，正南）"""
        self.assertEqual(self._mod.get_wuhuang_palace(2026), '离')
        self.assertEqual(self._mod.get_wuhuang_mountains(2026), ['丙', '午', '丁'])

    def test_wuhuang_palace_neighbors(self):
        """边界年份：2023乾宫（西北）、2027坎宫（正北）"""
        self.assertEqual(self._mod.get_wuhuang_palace(2023), '乾')
        self.assertEqual(self._mod.get_wuhuang_mountains(2023), ['戌', '乾', '亥'])
        self.assertEqual(self._mod.get_wuhuang_palace(2027), '坎')
        self.assertEqual(self._mod.get_wuhuang_mountains(2027), ['壬', '子', '癸'])

    def test_wuhuang_ruzhong_2022(self):
        """2022壬寅年五黄入中（无落宫），应返回空列表"""
        self.assertEqual(self._mod.get_wuhuang_palace(2022), '中')
        self.assertEqual(self._mod.get_wuhuang_mountains(2022), [])

    def test_nine_year_cycle(self):
        """9年一循环：同宫位每9年重现"""
        for y in (2024, 2025, 2026):
            self.assertEqual(self._mod.get_wuhuang_palace(y),
                             self._mod.get_wuhuang_palace(y + 9),
                             f"{y}年与{y + 9}年五黄宫位应相同（9年循环）")


# ==========================================================================
# Test Case 2: check_wuhuang 山向判定
# ==========================================================================
class TestCheckWuhuang(unittest.TestCase):
    """五黄到山/到兼向判定验证"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.二十四山择吉天机 as mod_mt
            cls._mod = mod_mt
        except ImportError as e:
            raise unittest.SkipTest(f"二十四山择吉天机模块导入失败: {e}")

    def test_2026_wushan_veto(self):
        """2026丙午年五黄到离宫：午山犯五黄，级别=凶煞"""
        r = self._mod.check_wuhuang({'year_gan': '丙', 'year_zhi': '午', 'year': 2026}, '午山')
        self.assertTrue(r['犯五黄'])
        self.assertEqual(r['级别'], '凶煞')
        self.assertIn('离宫', r['说明'])

    def test_2026_bingshan_dingshan_veto(self):
        """2026年丙山、丁山同属离宫三山，均犯五黄"""
        for shan in ('丙山', '丁山'):
            r = self._mod.check_wuhuang({'year_gan': '丙', 'year_zhi': '午', 'year': 2026}, shan)
            self.assertTrue(r['犯五黄'], f"{shan}应犯五黄")
            self.assertEqual(r['级别'], '凶煞')

    def test_2026_zishan_clean(self):
        """2026年子山（坎宫）不犯五黄"""
        r = self._mod.check_wuhuang({'year_gan': '丙', 'year_zhi': '午', 'year': 2026}, '子山')
        self.assertFalse(r['犯五黄'])
        self.assertEqual(r['级别'], '')

    def test_2026_jianxiang_warning(self):
        """2026年未山兼丁：兼向犯五黄，级别=警告"""
        r = self._mod.check_wuhuang({'year_gan': '丙', 'year_zhi': '午', 'year': 2026}, '未兼丁')
        self.assertTrue(r['犯五黄'])
        self.assertEqual(r['级别'], '警告')

    def test_ganzhi_fallback_no_year(self):
        """无公历年份时，从年干支（丙午→2026）回退推算仍能判定"""
        r = self._mod.check_wuhuang({'year_gan': '丙', 'year_zhi': '午'}, '午山')
        self.assertTrue(r['犯五黄'])
        self.assertEqual(r['级别'], '凶煞')

    def test_sizhu_input_mode_ganzhi_priority(self):
        """手动输入四柱干支模式：以年柱干支定年，不受按年支猜测的year干扰
        模拟日课评分系统四柱输入：年柱甲午 → 干支语义为2014年（五黄在乾宫），
        而非评分系统按年支猜测的2026年（五黄在离宫）。午山属离宫，
        按2014年应不犯五黄、按2026年则犯——正确结果是不犯。"""
        di = {'year_gan': '甲', 'year_zhi': '午', 'year': 2026, 'is_sizhu_input': True}
        r = self._mod.check_wuhuang(di, '午山')
        self.assertFalse(r['犯五黄'],
                         "甲午年柱应按2014年（五黄乾宫）判定，午山不犯五黄")
        # 反证：同一年柱干支在2026年口径下午山必犯（离宫），确保上述判定走的是干支定年
        self.assertIn('犯五黄',
                      self._mod.check_wuhuang({'year_gan': '丙', 'year_zhi': '午', 'year': 2026}, '午山'))

    def test_year_only_fallback(self):
        """仅公历年份、无干支 → 用year字段兜底判定"""
        r = self._mod.check_wuhuang({'year': 2026}, '午山')
        self.assertTrue(r['犯五黄'])
        self.assertEqual(r['级别'], '凶煞')

    def test_2025_genshan_veto(self):
        """2025乙巳年五黄到艮宫：艮山犯五黄（交叉年份验证）"""
        r = self._mod.check_wuhuang({'year_gan': '乙', 'year_zhi': '巳', 'year': 2025}, '艮山')
        self.assertTrue(r['犯五黄'])
        self.assertEqual(r['级别'], '凶煞')

    def test_no_year_info_skipped(self):
        """年干支缺失且无公历年 → 跳过检查，不误报"""
        r = self._mod.check_wuhuang({}, '午山')
        self.assertFalse(r['犯五黄'])
        self.assertEqual(r['级别'], '')

    def test_info_fields_for_detail_display(self):
        """返回值信息字段（供日课详情展示）：年份/宫位/三山/入中"""
        r = self._mod.check_wuhuang({'year_gan': '丙', 'year_zhi': '午', 'year': 2026}, '午山')
        self.assertEqual(r['年份'], 2026)
        self.assertEqual(r['宫位'], '离')
        self.assertEqual(r['三山'], '丙午丁')
        self.assertFalse(r['入中'])
        # 五黄入中年：入中=True，三山为空
        r2 = self._mod.check_wuhuang({'year_gan': '壬', 'year_zhi': '寅', 'year': 2022}, '午山')
        self.assertTrue(r2['入中'])
        self.assertEqual(r2['宫位'], '中')
        self.assertEqual(r2['三山'], '')


# ==========================================================================
# Test Case 3: check_mountain_day 管线集成
# ==========================================================================
class TestMountainDayIntegration(unittest.TestCase):
    """五黄检查接入 check_mountain_day 综合管线验证"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.二十四山择吉天机 as mod_mt
            cls._mod = mod_mt
        except ImportError as e:
            raise unittest.SkipTest(f"二十四山择吉天机模块导入失败: {e}")

    def test_2026_wushan_burial_blocked(self):
        """2026丙午年午山安葬：五黄到山 → 不可用，凶煞含五黄说明"""
        di = {'year_gan': '丙', 'year_zhi': '午', 'year': 2026}
        r = self._mod.check_mountain_day(di, '午山', '安葬')
        self.assertFalse(r.get('可用', True), "五黄到山应一票否决")
        self.assertTrue(any('五黄' in x for x in r['凶煞']),
                        f"凶煞列表应含五黄说明，实际: {r['凶煞']}")

    def test_2026_zishan_not_wuhuang_blocked(self):
        """2026年子山安葬：不因五黄被否决（凶煞列表不含五黄）"""
        di = {'year_gan': '丙', 'year_zhi': '午', 'year': 2026}
        r = self._mod.check_mountain_day(di, '子山', '安葬')
        self.assertFalse(any('五黄' in x for x in r['凶煞']),
                         f"子山不应犯五黄，实际凶煞: {r['凶煞']}")


# ==========================================================================
# Test Case 4: 二十四山.py MountainShenshaChecker 五黄接口
# ==========================================================================
class TestMountainShenshaCheckerWuhuang(unittest.TestCase):
    """二十四山.py 山家神煞检查器五黄接口验证"""

    @classmethod
    def setUpClass(cls):
        try:
            from modules.二十四山 import MountainShenshaChecker
            cls._checker = MountainShenshaChecker()
        except ImportError as e:
            raise unittest.SkipTest(f"二十四山模块导入失败: {e}")

    def test_palace_and_mountains_2024_2026(self):
        """2024兑/2025艮/2026离 三山列表验证"""
        self.assertEqual(self._checker.get_wuhuang_palace(2024), '兑')
        self.assertEqual(self._checker.check_wu_huang(2024), ['庚', '酉', '辛'])
        self.assertEqual(self._checker.get_wuhuang_palace(2025), '艮')
        self.assertEqual(self._checker.check_wu_huang(2025), ['丑', '艮', '寅'])
        self.assertEqual(self._checker.get_wuhuang_palace(2026), '离')
        self.assertEqual(self._checker.check_wu_huang(2026), ['丙', '午', '丁'])

    def test_ruzhong_2022_empty(self):
        """2022五黄入中，check_wu_huang 返回空列表"""
        self.assertEqual(self._checker.check_wu_huang(2022), [])

    def test_check_mountain_jixiong_with_year(self):
        """check_mountain_jixiong 传入公历年份：午山2026犯五黄，is_good=False"""
        r = self._checker.check_mountain_jixiong('午', '午', year_num=2026)
        self.assertIn('五黄', r['shensha'])
        self.assertFalse(r['is_good'])

    def test_check_mountain_jixiong_without_year(self):
        """check_mountain_jixiong 不传年份：不触发五黄检查（向后兼容）"""
        r = self._checker.check_mountain_jixiong('午', '午')
        self.assertNotIn('五黄', r['shensha'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
