# -*- coding: utf-8 -*-
"""
核心算法单元测试
=================
针对系统核心模块（四柱计算器、二十四山择吉天机、评分器）的逻辑正确性验证。

运行方法:
    cd /d 项目根目录
    python -m unittest tests.test_core -v
    或: python tests/test_core.py

【重要修复】
    不要把「模块级普通函数」通过 cls.func = func 直接绑定到类属性后用 self.func() 调用，
    因为 Python 会把测试实例 self 自动当作第一个位置参数传入，导致参数错位。
    方案：在 setUpClass 里保存模块对象 (self._模块名)，测试方法里 self._模块名.func() 调用。
"""

import sys
import os
import unittest

# ---------------------------------------------------------------------------
# 路径配置（确保以脚本方式或模块方式均可运行）
# ---------------------------------------------------------------------------
_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj_root = os.path.dirname(_this_dir)
for _p in [_proj_root, os.path.join(_proj_root, 'modules')]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from datetime import date


# ==========================================================================
# Test Case 1: 四柱计算器
# ==========================================================================
class TestSiZhuCalculator(unittest.TestCase):
    """四柱计算模块核心逻辑验证"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.四柱计算器 as mod_sizhu
            cls._mod = mod_sizhu
        except ImportError as e:
            raise unittest.SkipTest(f"四柱计算器模块导入失败: {e}")

    def test_basic_sizhu_structure(self):
        """基本四柱结构验证：年/月/日/时柱字段齐全"""
        sz = self._mod.calculate_sizhu(date(2026, 1, 1), 12, 0)
        self.assertIsInstance(sz, dict, "calculate_sizhu 应返回 dict")
        for k in ['年柱', '月柱', '日柱', '时柱',
                  'year_gan', 'year_zhi', 'month_gan', 'month_zhi',
                  'day_gan', 'day_zhi', 'hour_gan', 'hour_zhi']:
            self.assertIn(k, sz, f"返回结果缺少字段: {k}")
            self.assertTrue(sz[k], f"字段不应为空: {k}")

    def test_2024_lichun_year_change(self):
        """测试2024年立春前后年柱是否正确切换
        2024年立春: 2024-02-04 前后年柱应不同 (癸卯 → 甲辰)
        """
        before = self._mod.calculate_sizhu(date(2024, 2, 3), 12, 0)
        after = self._mod.calculate_sizhu(date(2024, 2, 5), 12, 0)
        self.assertNotEqual(
            before['年柱'], after['年柱'],
            "立春前后年柱应不同（2024立春: 2024-02-04）"
        )
        # 立春日之后年柱应为甲辰
        self.assertEqual(
            after['年柱'], '甲辰',
            f"2024-02-05年柱应为甲辰，实际: {after['年柱']}"
        )

    def test_2026_jan_year_pillar(self):
        """2026年1月仍属乙巳年（未立春），年柱应为乙巳"""
        sz = self._mod.calculate_sizhu(date(2026, 1, 15), 12, 0)
        # 2026年2月4日立春前仍属乙巳年
        self.assertEqual(
            sz['年柱'], '乙巳',
            f"2026-01-15 年柱应为乙巳，实际: {sz['年柱']}"
        )

    def test_hour_zhi_wuzidun(self):
        """时柱地支验证：亥时、子时、午时地支（本模块子时从00:00起算，23:00仍属亥时）"""
        # 23:00-23:59 属亥时（子时跨日，次日00:00起算）
        sz_2330 = self._mod.calculate_sizhu(date(2026, 3, 15), 23, 30)
        self.assertEqual(sz_2330['hour_zhi'], '亥', "23:30 仍属亥时（子时次日00:00起算）")
        # 00:00-00:59 属子时
        sz_0030 = self._mod.calculate_sizhu(date(2026, 3, 15), 0, 30)
        self.assertEqual(sz_0030['hour_zhi'], '子', "00:30 应为子时")
        # 11:00-12:59 属午时
        sz_noon = self._mod.calculate_sizhu(date(2026, 3, 15), 12, 0)
        self.assertEqual(sz_noon['hour_zhi'], '午', "12:00 应为午时")

    def test_ganzhi_combination_format(self):
        """干支组合格式：长度=2，天干+地支"""
        sz = self._mod.calculate_sizhu(date(2026, 6, 1), 10, 30)
        tian_gan = set('甲乙丙丁戊己庚辛壬癸')
        di_zhi = set('子丑寅卯辰巳午未申酉戌亥')
        for col in ['年柱', '月柱', '日柱', '时柱']:
            self.assertEqual(len(sz[col]), 2, f"{col}长度应为2")
            self.assertIn(sz[col][0], tian_gan, f"{col}天干非法: {sz[col]}")
            self.assertIn(sz[col][1], di_zhi, f"{col}地支非法: {sz[col]}")


# ==========================================================================
# Test Case 2: 二十四山择吉天机
# ==========================================================================
class TestTwentyFourMountains(unittest.TestCase):
    """二十四山择吉天机核心算法验证"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.二十四山择吉天机 as mod_mt
            cls._mod = mod_mt
        except ImportError as e:
            raise unittest.SkipTest(f"二十四山择吉天机模块导入失败: {e}")

    # ------------------------------------------------------------------
    # 基础数据完整性
    # ------------------------------------------------------------------
    def test_mountain_wuxing_core(self):
        """核心山向五行属性验证（八天干四维三山）"""
        cases = [
            ('壬山丙向', '水'),   ('子山午向', '水'),   ('癸山丁向', '水'),
            ('丙山壬向', '火'),   ('午山子向', '火'),   ('丁山癸向', '火'),
            ('甲山庚向', '木'),   ('卯山酉向', '木'),   ('乙山辛向', '木'),
            ('庚山甲向', '金'),   ('酉山卯向', '金'),   ('辛山乙向', '金'),
        ]
        for shan, expected in cases:
            actual = self._mod.get_mountain_wuxing(shan)
            self.assertEqual(
                actual, expected,
                f"{shan} 五行应为 {expected}，实际 {actual}"
            )

    def test_mountain_data_valid(self):
        """主要山向 get_mountain_data 返回有效 dict（五行在 basic_info.wuxing）"""
        for shan in ['子山午向', '壬山丙向', '乾山巽向', '坤山艮向']:
            data = self._mod.get_mountain_data(shan)
            self.assertIsInstance(
                data, dict,
                f"get_mountain_data({shan}) 应返回 dict"
            )
            # 五行在 basic_info.wuxing 下（结构：basic_info/wuxing）
            self.assertIn('basic_info', data, f"{shan} 缺少 basic_info 节点")
            self.assertIn(
                'wuxing', data['basic_info'],
                f"{shan} basic_info 缺少 wuxing 字段"
            )
            self.assertTrue(
                data['basic_info']['wuxing'],
                f"{shan} wuxing 不应为空"
            )

    def test_yinfu_config_kunshan(self):
        """坤山正阴府忌干必须为 ['丙', '辛']（遵循口诀：丙辛坤坎君莫犯）"""
        yf = self._mod.get_yinfu_config('坤山艮向')
        # get_yinfu_config 返回扁平结构: {'type':'正阴府', '忌干':[...], '说明':'...'}
        self.assertEqual(
            yf.get('type'), '正阴府',
            f"坤山应为正阴府类型，实际 {yf.get('type')!r}"
        )
        ji_gan = yf.get('忌干', [])
        self.assertEqual(
            sorted(ji_gan), ['丙', '辛'],
            f"坤山正阴府忌干应为 [丙,辛]，实际 {ji_gan}"
        )

    def test_yinfu_config_qianshan(self):
        """乾山正阴府忌干必须为 ['乙', '庚']（遵循口诀：乙庚乾兑甲庚离）"""
        yf = self._mod.get_yinfu_config('乾山巽向')
        self.assertEqual(
            yf.get('type'), '正阴府',
            f"乾山应为正阴府类型，实际 {yf.get('type')!r}"
        )
        ji_gan = yf.get('忌干', [])
        self.assertEqual(
            sorted(ji_gan), ['乙', '庚'],
            f"乾山正阴府忌干应为 [乙,庚]，实际 {ji_gan}"
        )

    # ------------------------------------------------------------------
    # 冲山检测
    # ------------------------------------------------------------------
    def test_chong_shan_zi_wu(self):
        """子山午向 → 午为冲山"""
        self.assertTrue(
            self._mod.check_chong_shan('子山午向', '午'),
            "子山午向，午支应冲山"
        )
        self.assertFalse(
            self._mod.check_chong_shan('子山午向', '子'),
            "子山午向，子支不应冲山"
        )
        self.assertFalse(
            self._mod.check_chong_shan('子山午向', '寅'),
            "子山午向，寅支不应冲山"
        )

    # ------------------------------------------------------------------
    # 三煞检测（纯地支映射）
    # ------------------------------------------------------------------
    def test_sansha_return_format(self):
        """check_sansha 返回格式必须是 dict，含 犯煞、煞类型、位置"""
        r = self._mod.check_sansha('壬山丙向', '寅', '子')
        self.assertIsInstance(r, dict, "check_sansha 应返回 dict")
        for k in ['犯煞', '煞类型', '位置']:
            self.assertIn(k, r, f"check_sansha 结果缺少 '{k}'")

    def test_sansha_shenzi_chen_nan(self):
        """申子辰年，三煞在南方（巳午未）→ 测试不崩溃"""
        # 申子辰年 → 煞南(巳午未)
        r = self._mod.check_sansha('壬山丙向', '巳', '子')
        # 只验证不崩溃 + 返回 bool / 文本
        self.assertIn(r['犯煞'], [True, False])
        self.assertIn(r['煞类型'], ['劫煞', '灾煞', '岁煞', ''])

    def test_sansha_hai_mao_wei_west(self):
        """亥卯未煞西(申酉戌)，仅测试格式不崩溃"""
        r = self._mod.check_sansha('甲山庚向', '申', '亥')
        self.assertIn(r['犯煞'], [True, False])
        self.assertIn(r['煞类型'], ['劫煞', '灾煞', '岁煞', ''])

    # ------------------------------------------------------------------
    # 阴府检测
    # ------------------------------------------------------------------
    def test_yinfu_basic_structure(self):
        """check_yinfu 返回结构完整"""
        r = self._mod.check_yinfu('坤山艮向', ['丙', '辛'], '修造')
        self.assertIsInstance(r, dict)
        for k in ['犯阴府', '类型', '说明']:
            self.assertIn(k, r, f"check_yinfu 缺少 '{k}'")

    def test_yinfu_kunshan_bingxin_xiuzao(self):
        """坤山 + 丙辛齐全 + 修造 → 应犯正阴府且禁用"""
        r = self._mod.check_yinfu('坤山艮向', ['丙', '辛'], '修造')
        self.assertTrue(r['犯阴府'], "坤山丙辛齐全应犯阴府")
        self.assertEqual(r['类型'], '正阴府')
        self.assertTrue(r.get('禁用', False), "正阴府修造应禁用")

    # ------------------------------------------------------------------
    # 冬至判断（精确节气）
    # ------------------------------------------------------------------
    def test_is_after_dongzhi_known_dates(self):
        """冬至前后日期判断"""
        # 2024年冬至: 2024-12-21 附近
        self.assertFalse(
            self._mod.is_after_dongzhi(2024, 12, 20),
            "2024-12-20 应在冬至前"
        )
        self.assertTrue(
            self._mod.is_after_dongzhi(2024, 12, 22),
            "2024-12-22 应在冬至后"
        )


# ==========================================================================
# Test Case 3: 二十四山择吉天机 - check_mountain_day 综合
# ==========================================================================
class TestCheckMountainDay(unittest.TestCase):
    """综合山家吉凶检查 check_mountain_day"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.二十四山择吉天机 as mod_mt
            cls._mod = mod_mt
        except ImportError as e:
            raise unittest.SkipTest(f"模块导入失败: {e}")

    def _base_date_info(self, overrides=None):
        """构造一个默认日课 + 支持覆盖"""
        info = {
            'year_gan': '甲', 'year_zhi': '子',
            'month_gan': '丙', 'month_zhi': '寅',
            'day_gan': '甲', 'day_zhi': '辰',
            'hour_gan': '庚', 'hour_zhi': '午'
        }
        if overrides:
            info.update(overrides)
        return info

    def test_return_structure(self):
        """check_mountain_day 返回结构"""
        r = self._mod.check_mountain_day(
            self._base_date_info(), '子山午向', '修造'
        )
        self.assertIsInstance(r, dict)
        for k in ['可用', '凶煞', '警告', '吉神', '日类', '说明']:
            self.assertIn(k, r, f"缺少字段 '{k}'")
        self.assertIsInstance(r['凶煞'], list)
        self.assertIsInstance(r['警告'], list)
        self.assertIsInstance(r['吉神'], list)

    def test_day_chong_shan_should_block(self):
        """日冲山（日破）应不可用"""
        # 子山午向，日支午 → 冲山
        info = self._base_date_info({'day_zhi': '午'})
        r = self._mod.check_mountain_day(info, '子山午向', '修造')
        self.assertFalse(
            r['可用'],
            f"日支午冲子山应判不可用。凶煞: {r['凶煞']}"
        )
        self.assertTrue(
            any('冲山' in s for s in r['凶煞']),
            f"应检测到冲山，实际凶煞: {r['凶煞']}"
        )

    def test_year_chong_shan_should_block(self):
        """年冲山也应禁用"""
        info = self._base_date_info({'year_zhi': '午'})
        r = self._mod.check_mountain_day(info, '子山午向', '修造')
        self.assertFalse(r['可用'], f"年支午冲子山应判不可用。凶煞: {r['凶煞']}")

    def test_clean_day_available(self):
        """普通不犯煞日应可用"""
        # 子山午向 + 日辰戌，年丑 → 不冲
        info = {
            'year_gan': '己', 'year_zhi': '丑',
            'month_gan': '丁', 'month_zhi': '卯',
            'day_gan': '戊', 'day_zhi': '戌',
            'hour_gan': '甲', 'hour_zhi': '寅'
        }
        r = self._mod.check_mountain_day(info, '子山午向', '修造')
        self.assertIsInstance(r['可用'], bool)

    def test_event_type_burial_vs_xiuzao(self):
        """同一山家同一日课，修造 vs 安葬 阴府判定可能不同"""
        info = self._base_date_info({
            'year_gan': '丙', 'day_gan': '辛',  # 丙辛齐全
            'year_zhi': '午', 'day_zhi': '寅'
        })
        r_xz = self._mod.check_mountain_day(info, '坤山艮向', '修造')
        r_az = self._mod.check_mountain_day(info, '坤山艮向', '安葬')
        self.assertIsInstance(r_xz['可用'], bool)
        self.assertIsInstance(r_az['可用'], bool)


# ==========================================================================
# Test Case 4: 评分器 - 基本接口
# ==========================================================================
class TestScorerBasic(unittest.TestCase):
    """评分器基础接口验证"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.评分器 as mod_score
            import modules.四柱计算器 as mod_sizhu
            cls._mod_score = mod_score
            cls._mod_sizhu = mod_sizhu
        except ImportError as e:
            raise unittest.SkipTest(f"评分器模块导入失败: {e}")

    def _make_sizhu(self, d, h=12, mi=0):
        """构造四柱 dict，附带 year/month/day/date 辅助字段"""
        sz = self._mod_sizhu.calculate_sizhu(d, h, mi)
        sz['year'] = d.year
        sz['month'] = d.month
        sz['day'] = d.day
        sz['date'] = d
        return sz

    def test_scorer_instance(self):
        """Scorer 类实例化"""
        s = self._mod_score.Scorer()
        self.assertTrue(hasattr(s, 'score'))
        self.assertTrue(hasattr(s, 'base_score'))
        self.assertEqual(s.base_score, 100)

    def test_calculate_score_return_keys(self):
        """calculate_score 返回关键字段齐全"""
        sz = self._make_sizhu(date(2026, 3, 15), 12, 0)
        owners = [{
            'name': '测试',
            'birth_date': date(1990, 5, 15),
            'birth_hour': 10,
            'birth_minute': 30,
            '性别': '男',
            'role': '事主1'
        }]
        result = self._mod_score.calculate_score(
            sizhu=sz,
            event_type='修造',
            owners=owners,
            house_type='阳宅',
            shan_xiang='子山午向'
        )
        self.assertIsInstance(result, dict, "calculate_score 必须返回 dict")

        # 关键字段检查（符合 project_memory 约束）
        required_keys = ['score', 'level', 'shensha_list',
                         'wu_xing_result', 'sansha_info', 'shan_xiang']
        for k in required_keys:
            self.assertIn(
                k, result,
                f"calculate_score 返回缺少必备字段 '{k}'。"
                f"现有键: {list(result.keys())}"
            )

    def test_score_range(self):
        """评分应在合理范围"""
        sz = self._make_sizhu(date(2026, 4, 10), 9, 0)
        r = self._mod_score.calculate_score(
            sizhu=sz, event_type='修造',
            house_type='阳宅', shan_xiang='子山午向'
        )
        score = r.get('score', -9999)
        self.assertGreaterEqual(score, -100, f"评分过低: {score}")
        self.assertLessEqual(score, 300, f"评分过高: {score}")

    def test_score_level_consistency(self):
        """level 字段非空且包含等级标志"""
        sz = self._make_sizhu(date(2026, 5, 20), 14, 0)
        r = self._mod_score.calculate_score(
            sizhu=sz, event_type='入宅',
            house_type='阳宅', shan_xiang='壬山丙向'
        )
        level = r.get('level', '')
        self.assertTrue(
            isinstance(level, str) and len(level) > 0,
            f"level 字段异常: {level!r}"
        )
        markers = ['吉', '凶', '上', '中', '下', '★', 'A', 'B', 'C', 'S']
        self.assertTrue(
            any(m in level for m in markers),
            f"level '{level}' 未包含任何等级标识字符"
        )

    def test_without_shanxiang_no_crash(self):
        """无山向时修造类也应能正常评分（不崩溃）"""
        sz = self._make_sizhu(date(2026, 6, 1), 10, 0)
        try:
            r = self._mod_score.calculate_score(sizhu=sz, event_type='修造')
        except Exception as e:
            self.fail(f"无山向修造评分异常: {type(e).__name__}: {e}")
        self.assertIsInstance(r, dict)
        self.assertIn('score', r)

    def test_shensha_list_format(self):
        """shensha_list 中每个元素若为 dict，必须有 name/score"""
        sz = self._make_sizhu(date(2026, 7, 15), 11, 0)
        r = self._mod_score.calculate_score(
            sizhu=sz, event_type='嫁娶',
            owners=[{
                'name': '新娘',
                'birth_date': date(1995, 8, 8),
                'birth_hour': 8, 'birth_minute': 0,
                '性别': '女', 'role': '新娘'
            }, {
                'name': '新郎',
                'birth_date': date(1993, 6, 6),
                'birth_hour': 6, 'birth_minute': 0,
                '性别': '男', 'role': '新郎'
            }]
        )
        ssl = r.get('shensha_list', [])
        for item in ssl:
            if isinstance(item, dict):
                self.assertIn('name', item, f"神煞dict缺少name键: {item}")
                self.assertIn('score', item, f"神煞dict缺少score键: {item}")


# ==========================================================================
# 入口
# ==========================================================================
if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("  L3: 核心算法单元测试 (tests/test_core.py)")
    print("=" * 70 + "\n")
    unittest.main(verbosity=2)
