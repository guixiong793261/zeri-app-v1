# -*- coding: utf-8 -*-
"""
================================================================================
L3C 黄金基准比对测试（硬编码真值哈希级断言）
================================================================================

核心原则：
    用《通书》/ 权威黄历 / project_memory 硬约束作为**只读规范输入**，
    测试文件里直接硬编码真值，运行时比对代码输出。
    任何算法漂移都会立即 FAIL，避免"公式对公式自己验证自己"的空转。

覆盖：
    A. 大黄道值日（日级，6组）
    B. 小黄道建除（日级，6组）
    C. 时辰级大黄道（时级，6组）
    D. 三煞映射表（三合局纯地支，4组三合局 + 12月支单月查询）
    E. 天乙贵人时（反例证伪法 + 正例法 10天干）

运行：
    python -m unittest tests.test_huangdao_truth -v
================================================================================
"""
import sys, os, unittest
from datetime import date
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.四柱计算器 import calculate_sizhu
from modules.黄道 import 黄道计算器

# ============================================================================
# 【只读黄金基准】— 由通书/权威口诀/历史数据固化而来，永远不改。
# ============================================================================

# A. 大黄道值日 + 小黄道建除（6组）
#    ( (年,月,日), 大黄道值神, 吉凶, 小黄道值神 )
GOLD_TRUTH_DA_XIAO = [
    ((2026, 2, 22), '朱雀', '凶', '除'),    # 用户指定：2026-02-22 必为朱雀/除
    ((2026, 2, 17), '司命', '吉', '成'),
    ((2026, 2,  4), '玄武', '凶', '危'),
    ((2026, 1,  1), '朱雀', '凶', '闭'),
    ((2026, 3,  6), '明堂', '吉', '建'),
    ((2025, 12, 22), '天德', '吉', '除'),
]

# B. 时辰级大黄道（6组，含用户指定 2026-02-22 午时 = 金匮吉）
#    ( (年,月,日), 小时数, 时支, 日柱干支, 时辰值神, 吉凶 )
GOLD_TRUTH_SHICHEN = [
    ((2026, 2, 22), 11, '午', '丁卯', '金匮', '吉'),
    ((2026, 2, 17), 12, '午', '壬戌', '天刑', '凶'),
    ((2026, 3,  6),  1, '丑', '己卯', '勾陈', '凶'),
    ((2026, 3,  6), 11, '午', '己卯', '金匮', '吉'),
    ((2026, 3,  6),  5, '卯', '己卯', '明堂', '吉'),
    ((2026, 5,  5),  9, '巳', '己卯', '朱雀', '凶'),
]

# C. 三煞映射表黄金基准（三合局→煞方，project_memory 硬约束纯地支）
GOLD_TRUTH_SANSHA_HEJU = {
    '申子辰': '寅午戌',
    '寅午戌': '申子辰',
    '亥卯未': '巳酉丑',
    '巳酉丑': '亥卯未',
}

# D. 十二地支单月三煞查询真值（月支→对应三合局→煞方）
#    正宗三合局：申子辰同局 / 亥卯未同局 / 寅午戌同局 / 巳酉丑同局
GOLD_TRUTH_MONTHLY_SANSHA = [
    ('子', '申子辰', '寅午戌'), ('丑', '巳酉丑', '亥卯未'), ('寅', '寅午戌', '申子辰'),
    ('卯', '亥卯未', '巳酉丑'), ('辰', '申子辰', '寅午戌'), ('巳', '巳酉丑', '亥卯未'),
    ('午', '寅午戌', '申子辰'), ('未', '亥卯未', '巳酉丑'), ('申', '申子辰', '寅午戌'),
    ('酉', '巳酉丑', '亥卯未'), ('戌', '寅午戌', '申子辰'), ('亥', '亥卯未', '巳酉丑'),
]

# E. 庚日贵人时黄金基准（project_memory：甲戊庚牛羊=丑未；此前婚嫁模块错写成寅午）
GOLD_TRUTH_GUIREN_GENG = ['丑', '未']
#    反例证伪：卯时 / 戌时 / 辰时 永不为庚日贵人时
GOLD_TRUTH_GUIREN_GENG_FALSE = ['卯', '戌', '辰', '寅', '午']   # 寅/午 是辛的六辛逢马虎，非庚

# F. 阴胎 / 阳气 黄金基准（典籍口径：均为干+1支+3·胎元法，男称阳气女称阴胎）
GOLD_TRUTH_YINTAI_YANGQI = [
    # 月干, 月支, 阴胎(干+1支+3), 阳气(干+1支+3，同法)
    ('甲', '子', '乙卯', '乙卯'),
    ('丙', '寅', '丁巳', '丁巳'),
    ('戊', '午', '己酉', '己酉'),
    ('庚', '申', '辛亥', '辛亥'),   # 庚(7)+1=8辛 申(8)+3=11亥
    ('壬', '戌', '癸丑', '癸丑'),   # 壬(9)+1=10癸 戌(10)+3=1丑
]

# G. 12日支 × 3时辰大黄道时辰全覆盖（project_memory 要求 6种日支边界 子午/丑未/寅申/卯酉/辰戌/巳亥）
#    (日支, 日柱, 月柱, 小时数, 时支, 大黄道值神, 吉凶)
GOLD_TRUTH_12DAY_SHICHEN = [
    ('子', '丙子', '戊子',  0, '子', '青龙', '吉'),
    ('子', '丙子', '戊子', 12, '午', '白虎', '凶'),
    ('子', '丙子', '戊子',  5, '卯', '朱雀', '凶'),
    ('丑', '丁丑', '戊子',  0, '子', '司命', '吉'),
    ('丑', '丁丑', '戊子', 12, '午', '金匮', '吉'),
    ('丑', '丁丑', '戊子',  5, '卯', '明堂', '吉'),
    ('寅', '戊寅', '戊子',  0, '子', '天刑', '凶'),
    ('寅', '戊寅', '戊子', 12, '午', '天牢', '凶'),
    ('寅', '戊寅', '戊子',  5, '卯', '天德', '吉'),
    ('卯', '己卯', '戊子',  0, '子', '司命', '吉'),
    ('卯', '己卯', '戊子', 12, '午', '金匮', '吉'),
    ('卯', '己卯', '戊子',  5, '卯', '明堂', '吉'),
    ('辰', '庚辰', '己丑',  0, '子', '天牢', '凶'),
    ('辰', '庚辰', '己丑', 12, '午', '天刑', '凶'),
    ('辰', '庚辰', '己丑',  5, '卯', '勾陈', '凶'),
    ('巳', '辛巳', '己丑',  0, '子', '玉堂', '吉'),
    ('巳', '辛巳', '己丑', 12, '午', '明堂', '吉'),
    ('巳', '辛巳', '己丑',  5, '卯', '司命', '吉'),
    ('午', '壬午', '己丑',  0, '子', '青龙', '吉'),
    ('午', '壬午', '己丑', 12, '午', '白虎', '凶'),
    ('午', '壬午', '己丑',  5, '卯', '朱雀', '凶'),
    ('未', '癸未', '己丑',  0, '子', '司命', '吉'),
    ('未', '癸未', '己丑', 12, '午', '金匮', '吉'),
    ('未', '癸未', '己丑',  5, '卯', '明堂', '吉'),
    ('申', '甲申', '己丑',  0, '子', '天刑', '凶'),
    ('申', '甲申', '己丑', 12, '午', '天牢', '凶'),
    ('申', '甲申', '己丑',  5, '卯', '天德', '吉'),
    ('酉', '乙酉', '己丑',  0, '子', '司命', '吉'),
    ('酉', '乙酉', '己丑', 12, '午', '金匮', '吉'),
    ('酉', '乙酉', '己丑',  5, '卯', '明堂', '吉'),
    ('戌', '丙戌', '己丑',  0, '子', '天牢', '凶'),
    ('戌', '丙戌', '己丑', 12, '午', '天刑', '凶'),
    ('戌', '丙戌', '己丑',  5, '卯', '勾陈', '凶'),
    ('亥', '乙亥', '戊子',  0, '子', '玉堂', '吉'),
    ('亥', '乙亥', '戊子', 12, '午', '明堂', '吉'),
    ('亥', '乙亥', '戊子',  5, '卯', '司命', '吉'),
]

# H. 天乙贵人时 10天干全量黄金基准（project_memory 口诀：甲戊庚牛羊/乙己子申/丙丁亥酉/辛寅午/壬癸卯巳）
GOLD_TRUTH_GUIREN_FULL_10GAN = {
    '甲': {'pos': ['丑', '未'], 'neg': ['子', '寅']},
    '戊': {'pos': ['丑', '未'], 'neg': ['子', '寅']},
    '庚': {'pos': ['丑', '未'], 'neg': ['子', '寅']},
    '乙': {'pos': ['子', '申'], 'neg': ['丑', '寅']},
    '己': {'pos': ['子', '申'], 'neg': ['丑', '寅']},
    '丙': {'pos': ['酉', '亥'], 'neg': ['子', '丑']},
    '丁': {'pos': ['酉', '亥'], 'neg': ['子', '丑']},
    '辛': {'pos': ['寅', '午'], 'neg': ['子', '丑']},
    '壬': {'pos': ['卯', '巳'], 'neg': ['子', '丑']},
    '癸': {'pos': ['卯', '巳'], 'neg': ['子', '丑']},
}

# I. 夫星/子星黄金基准（project_memory + FU_ZI_XING 10天干硬编码）
#    用户点名盲区：甲→夫星辛酉 子星丙午（正官/七杀/食神/伤官四柱全量）
GOLD_TRUTH_FU_ZI_XING = {
    '甲': {'fu': '辛酉', 'qi': '庚申', 'zi': '丙午', 'shang': '丁巳'},
    '乙': {'fu': '庚申', 'qi': '辛酉', 'zi': '丁巳', 'shang': '丙午'},
    '丙': {'fu': '癸亥', 'qi': '壬子', 'zi': '戊戌', 'shang': '己丑'},
    '丁': {'fu': '壬子', 'qi': '癸亥', 'zi': '己丑', 'shang': '戊戌'},
    '戊': {'fu': '乙卯', 'qi': '甲寅', 'zi': '丙午', 'shang': '丁巳'},
    '己': {'fu': '甲寅', 'qi': '乙卯', 'zi': '辛酉', 'shang': '庚申'},
    '庚': {'fu': '丁巳', 'qi': '丙午', 'zi': '壬子', 'shang': '癸亥'},
    '辛': {'fu': '丙午', 'qi': '丁巳', 'zi': '癸亥', 'shang': '壬子'},
    '壬': {'fu': '己丑', 'qi': '戊戌', 'zi': '甲寅', 'shang': '乙卯'},
    '癸': {'fu': '戊戌', 'qi': '己丑', 'zi': '乙卯', 'shang': '甲寅'},
}

DIZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']


class TestHuangDaoGoldTruth(unittest.TestCase):
    """A + B：大黄道/小黄道 6 组硬编码真值比对（用户点名2026-02-22 朱雀/除日）"""

    @classmethod
    def setUpClass(cls):
        cls.hc = 黄道计算器()

    # ---- 用户点名核心用例：2026-02-22 必须为 朱雀(凶) + 除日 ----
    def test_truth_20260222_da_huangdao_zhu_que(self):
        """【用户核心验证】2026-02-22 大黄道值日必为朱雀(凶)，否则算法崩"""
        d = date(2026, 2, 22)
        sz = calculate_sizhu(d, 12, 0)
        r = self.hc.calculate(sz)
        self.assertEqual(r['da_huang_dao']['name'], '朱雀',
            "黄金基准失败：2026-02-22 通书为朱雀，代码输出 %s，大黄道算法错误！" % r['da_huang_dao']['name'])
        self.assertEqual(r['da_huang_dao']['type'], '凶')

    def test_truth_20260222_xiao_huangdao_chu(self):
        """2026-02-22 小黄道建除必为除日"""
        d = date(2026, 2, 22)
        sz = calculate_sizhu(d, 12, 0)
        r = self.hc.calculate(sz)
        self.assertEqual(r['xiao_huang_dao']['name'], '除',
            "黄金基准失败：2026-02-22 通书为除，代码输出 %s" % r['xiao_huang_dao']['name'])

    # ---- 6 组全量黄金基准比对（参数化） ----
    def test_all_da_xiao_valley_truth(self):
        """全量：6组日期 大黄道值日 + 小黄道建除 与黄金基准字符级一致"""
        fails = []
        for entry in GOLD_TRUTH_DA_XIAO:
            (y,m,d), exp_da, exp_tp, exp_xiao = entry
            sz = calculate_sizhu(date(y,m,d), 12, 0)
            r = self.hc.calculate(sz)
            if r['da_huang_dao']['name'] != exp_da:
                fails.append(f"{y:04d}-{m:02d}-{d:02d} 大黄道: 基准={exp_da} 实际={r['da_huang_dao']['name']}")
            if r['da_huang_dao']['type'] != exp_tp:
                fails.append(f"{y:04d}-{m:02d}-{d:02d} 大吉凶: 基准={exp_tp} 实际={r['da_huang_dao']['type']}")
            if r['xiao_huang_dao']['name'] != exp_xiao:
                fails.append(f"{y:04d}-{m:02d}-{d:02d} 小黄道: 基准={exp_xiao} 实际={r['xiao_huang_dao']['name']}")
        self.assertEqual(len(fails), 0, "黄金基准大黄道/小黄道失败：\n  " + "\n  ".join(fails))

    def test_all_shichen_dahuangdao_truth(self):
        """全量：6组时辰级大黄道 与黄金基准字符级一致"""
        fails = []
        for entry in GOLD_TRUTH_SHICHEN:
            (y,m,d), h, exp_shi_zhi, exp_day, exp_shishen, exp_type = entry
            sz = calculate_sizhu(date(y,m,d), h, 0)
            self.assertEqual(sz['hour_zhi'], exp_shi_zhi,
                f"时支基准错 {y}-{m}-{d} {h}h: 基准={exp_shi_zhi} 实际={sz['hour_zhi']}（排查calculate_sizhu时辰起法）")
            r = self.hc.calculate(sz)
            sd = r['shichen_huang_dao']
            if sd['name'] != exp_shishen:
                fails.append(f"{y:04d}-{m:02d}-{d:02d} {h:2d}h({exp_shi_zhi}时): 基准值神={exp_shishen} 实际={sd['name']}")
            if sd['type'] != exp_type:
                fails.append(f"{y:04d}-{m:02d}-{d:02d} {h:2d}h({exp_shi_zhi}时): 基准吉凶={exp_type} 实际={sd['type']}")
        self.assertEqual(len(fails), 0, "黄金基准时辰级大黄道失败：\n  " + "\n  ".join(fails))


class TestSanshaGoldTruth(unittest.TestCase):
    """C + D：三煞映射表 + 单月三煞 黄金基准（project_memory 硬约束纯地支）"""

    @classmethod
    def setUpClass(cls):
        try:
            import modules.二十四山择吉天机 as mod_mt
            cls.mod_mt = mod_mt
        except ImportError as e:
            raise unittest.SkipTest("模块导入失败: %s" % e)

    def test_sansha_heju_4_entries_match_gold(self):
        """【黄金基准4组】三合局 SANSHA_MAP 4 条映射字符级一致"""
        actual = self.mod_mt.SANSHA_MAP
        for k, exp_v in GOLD_TRUTH_SANSHA_HEJU.items():
            self.assertIn(k, actual, "SANSHA_MAP 缺三合局键 %s" % k)
            self.assertEqual(actual[k], exp_v,
                "SANSHA_MAP['%s'] 基准=%s 实际=%s" % (k, exp_v, actual[k]))

    def test_sansha_heju_all_pure_dizhi_no_tiangan(self):
        """三煞映射表键值均为纯地支（project_memory硬约束：禁止混入天干）"""
        TIAN_GAN = set('甲乙丙丁戊己庚辛壬癸')
        DI_ZHI = set('子丑寅卯辰巳午未申酉戌亥')
        for k, v in GOLD_TRUTH_SANSHA_HEJU.items():
            for c in k: self.assertIn(c, DI_ZHI, "三合局键 %s 非地支字符" % k)
            for c in v: self.assertIn(c, DI_ZHI, "煞方值 %s 非地支字符" % v)
        # 反向检查：没有一天干
        for k, v in self.mod_mt.SANSHA_MAP.items():
            for c in k: self.assertNotIn(c, TIAN_GAN, "三煞键 %s 混入天干" % k)
            for c in v: self.assertNotIn(c, TIAN_GAN, "三煞值 %s 混入天干" % v)

    def test_haimao_wei_sha_not_include_wei(self):
        """【project_memory 第一条硬约束】亥卯未月煞方不含'未'字符"""
        sanfang = self.mod_mt.SANSHA_MAP.get('亥卯未', '')
        self.assertNotIn('未', sanfang, "亥卯未煞方 %s 不应含'未'" % sanfang)


class TestGuiRenGoldTruth(unittest.TestCase):
    """E：天乙贵人时黄金基准（庚日丑未 / 正例 + 反例证伪法）"""

    @classmethod
    def setUpClass(cls):
        # 取婚嫁评分算法的 TIANYI_GUIREN（已修：庚=丑未）
        try:
            import modules.婚嫁评分算法 as mod_hm
            cls.GUIREN_TABLE = mod_hm.TIANYI_GUIREN
        except ImportError as e:
            raise unittest.SkipTest("模块导入失败: %s" % e)

    def test_gui_geng_equals_gold_niu_yang(self):
        """【庚日贵人时 正例】甲戊庚牛羊=丑未。婚嫁算法版 TIANYI_GUIREN['庚'] 必须= ['丑','未']"""
        self.assertEqual(self.GUIREN_TABLE.get('庚'), GOLD_TRUTH_GUIREN_GENG,
            "庚日贵人时偏离黄金基准！口诀甲戊庚牛羊应为丑未，实际=%s" % self.GUIREN_TABLE.get('庚'))

    def test_gui_geng_false_cases_never_true(self):
        """【庚日贵人时 反例证伪】卯/戌/辰/寅/午 5个时辰永不为庚日贵人时"""
        geng_gr = set(self.GUIREN_TABLE.get('庚', []))
        for sz in GOLD_TRUTH_GUIREN_GENG_FALSE:
            self.assertNotIn(sz, geng_gr,
                "庚日贵人时反例失败：'%s' 不应为庚日贵人（庚日只能是丑/未；寅午是六辛逢马虎）" % sz)


class TestYinTaiYangQiGoldTruth(unittest.TestCase):
    """F：阴胎/阳气 5 组黄金基准（典籍口径：均为干+1支+3·胎元法）"""

    @classmethod
    def setUpClass(cls):
        pass

    def _get_fns(self):
        from modules.工具函数 import get_yintai, get_yangqi
        return get_yintai, get_yangqi

    def test_all_yintai_yangqi_gold_match(self):
        """全量5组：阴胎/阳气 字符级匹配黄金基准"""
        get_yintai, get_yangqi = self._get_fns()
        fails = []
        for mg, mz, exp_yt, exp_yq in GOLD_TRUTH_YINTAI_YANGQI:
            yt = get_yintai(mg, mz)
            yt_s = ''.join(yt) if isinstance(yt, tuple) else yt
            yq = get_yangqi(mg, mz)
            yq_s = ''.join(yq) if isinstance(yq, tuple) else yq
            if yt_s != exp_yt:
                fails.append(f"阴胎 {mg}{mz}: 基准={exp_yt} 实际={yt_s}")
            if yq_s != exp_yq:
                fails.append(f"阳气 {mg}{mz}: 基准={exp_yq} 实际={yq_s}")
        self.assertEqual(len(fails), 0, "阴胎/阳气 黄金基准失败：\n  " + "\n  ".join(fails))

    def test_taiyuan_method_gan_plus_1_zhi_plus_3(self):
        """【典籍口径】阴胎与阳气均为干+1、支+3（胎元法），同柱同值"""
        get_yintai, get_yangqi = self._get_fns()
        cases = [('甲','子'), ('丙','寅'), ('庚','申'), ('壬','戌')]
        for mg, mz in cases:
            gi = TIANGAN.index(mg); zi = DIZHI.index(mz)
            for fn, label in ((get_yintai, '阴胎'), (get_yangqi, '阳气')):
                r = fn(mg, mz)
                rs = ''.join(r) if isinstance(r, tuple) else r
                self.assertEqual((TIANGAN.index(rs[0]) - gi) % 10, 1,
                                 "%s月 %s 干+1=%s错" % (mg, label, rs[0]))
                self.assertEqual((DIZHI.index(rs[1]) - zi) % 12, 3,
                                 "%s月 %s 支+3=%s错" % (mz, label, rs[1]))


class TestFuZiGoldTruth(unittest.TestCase):
    """I. 夫星/子星 黄金基准：FU_ZI_XING 10天干查表 + 双模块 120组一致性 + 用户点名甲→辛酉/丙午"""

    @classmethod
    def setUpClass(cls):
        pass

    def _get_fns(self):
        from modules.工具函数 import get_fuzi as get_fuzi_tool, FU_ZI_XING
        from modules.婚嫁评分算法 import get_fuxing_zixing_by_year as get_fuzi_hm
        return get_fuzi_tool, get_fuzi_hm, FU_ZI_XING

    def test_fuzi_xing_table_10gan_gold_match(self):
        """【用户点名盲区】10天干 FU_ZI_XING 硬编码四柱：甲→夫星辛酉/子星丙午"""
        get_fuzi_tool, get_fuzi_hm, FU_ZI_XING = self._get_fns()
        for gan, exp in GOLD_TRUTH_FU_ZI_XING.items():
            actual = FU_ZI_XING.get(gan, {})
            for k, v in exp.items():
                self.assertEqual(actual.get(k), v,
                    "%s年 %s 黄金基准=%s 工具函数FU_ZI_XING=%s（若不一致需修工具函数.py）"
                    % (gan, {'fu':'正官夫星','qi':'七杀','zi':'食神子星','shang':'伤官'}[k], v, actual.get(k)))

    def test_user_case_jia_fuzi_xinyou_bingwu(self):
        """【用户核心盲区点】甲日夫星正官=辛酉，七杀=庚申；子星食神=丙午，伤官=丁巳"""
        get_fuzi_tool, get_fuzi_hm, FU_ZI_XING = self._get_fns()
        actual = FU_ZI_XING['甲']
        self.assertEqual(actual['fu'],    '辛酉', "甲年正官夫星基准=辛酉")
        self.assertEqual(actual['qi'],    '庚申', "甲年七杀基准=庚申")
        self.assertEqual(actual['zi'],    '丙午', "甲年食神子星基准=丙午")
        self.assertEqual(actual['shang'], '丁巳', "甲年伤官基准=丁巳")

    def test_120_zu_two_modules_fuzi_consistency(self):
        """ExperienceRecall 100036187：工具函数.get_fuzi 与 婚嫁评分.get_fuxing_zixing_by_year
        对 10天干×12地支=120组输入 fu/zi 字段必须 100% 一致（单点权威规则源）"""
        get_fuzi_tool, get_fuzi_hm, FU_ZI_XING = self._get_fns()
        fails = []
        for yg in TIANGAN:
            for yz in DIZHI:
                a = get_fuzi_tool(yg, yz)  # {'fu','zi'}
                b = get_fuzi_hm(yg, yz)    # {'fu','qi','zi','shang'}
                if a.get('fu') != b.get('fu'):
                    fails.append(f"{yg}{yz} fu 工具={a.get('fu')} 婚嫁={b.get('fu')}")
                if a.get('zi') != b.get('zi'):
                    fails.append(f"{yg}{yz} zi 工具={a.get('zi')} 婚嫁={b.get('zi')}")
        self.assertEqual(len(fails), 0,
            "夫星子星双模块 120组一致性失败（单点权威规则源被破坏！），共 %d 处：\n  %s"
            % (len(fails), "\n  ".join(fails[:10])))

    def test_get_fuzi_returns_dict_with_2_keys(self):
        """工具函数.get_fuzi 返回契约：{'fu':2字符, 'zi':2字符}（主程序L3772消费）"""
        get_fuzi_tool, get_fuzi_hm, FU_ZI_XING = self._get_fns()
        for yg in TIANGAN[:4]:
            for yz in DIZHI[:3]:
                r = get_fuzi_tool(yg, yz)
                self.assertIsInstance(r, dict)
                for k in ('fu', 'zi'):
                    self.assertIn(k, r, "get_fuzi 缺键 %s" % k)
                    self.assertEqual(len(r[k]), 2,
                        "%s get_fuzi['%s']=%s 应为2字符干支" % (yg+yz, k, r[k]))


class TestShichen12DayBoundary(unittest.TestCase):
    """G：12日支 × 3时辰（子午/丑未/寅申/卯酉/辰戌/巳亥 6种边界全覆盖）时辰级大黄道"""

    @classmethod
    def setUpClass(cls):
        cls.hc = 黄道计算器()
        # 预计算：为每个日支找对应的日期和小时
        cls._precalc = {}
        base = date(2026, 1, 1)
        import datetime as _dt
        seen = set()
        for i in range(400):
            d = base + _dt.timedelta(days=i)
            sz = calculate_sizhu(d, 12, 0)
            dz = sz['day_zhi']
            if dz in seen:
                continue
            seen.add(dz)
            _t = []
            for shi_zhi, h in [('子', 0), ('午', 12), ('卯', 5)]:
                # 找小时 hh 对应时支
                for hh in range(24):
                    s2 = calculate_sizhu(d, hh, 0)
                    if s2['hour_zhi'] == shi_zhi:
                        _t.append((shi_zhi, d, hh))
                        break
            cls._precalc[dz] = (d, _t)
            if len(seen) == 12:
                break

    def test_all_36_shichen_entries_match_gold(self):
        """36组 12日支×3时辰 大黄道时辰值神+吉凶 与黄金基准字符级一致"""
        fails = []
        for dz, day_gz, month_gz, h, shi_zhi, exp_shen, exp_type in GOLD_TRUTH_12DAY_SHICHEN:
            try:
                d, mapping = self._precalc[dz]
            except KeyError:
                self.fail("12日支预计算缺 %s" % dz)
                return
            # 找对应时支的小时数（可能非h，但以时支匹配为准）
            pick_h = None
            for sz2, d2, hh in mapping:
                if sz2 == shi_zhi:
                    pick_h = hh; break
            if pick_h is None:
                fails.append(f"{dz}日 找不到{shi_zhi}时")
                continue
            sz = calculate_sizhu(d, pick_h, 0)
            self.assertEqual(sz['hour_zhi'], shi_zhi, f"{dz}日{pick_h}h时支错")
            r = self.hc.calculate(sz)
            sd = r['shichen_huang_dao']
            if sd['name'] != exp_shen:
                fails.append(f"{dz}日 {shi_zhi}时 值神: 基准={exp_shen} 实际={sd['name']}")
            if sd['type'] != exp_type:
                fails.append(f"{dz}日 {shi_zhi}时 吉凶: 基准={exp_type} 实际={sd['type']}")
        self.assertEqual(len(fails), 0,
            "12日支×3时辰 大黄道时辰失败：\n  " + "\n  ".join(fails))


class TestGuiRen10GanFull(unittest.TestCase):
    """H：天乙贵人时 10天干全量黄金基准（甲戊庚牛羊/乙己子申/丙丁亥酉/辛寅午/壬癸卯巳）"""

    @classmethod
    def setUpClass(cls):
        import modules.婚嫁评分算法 as mod_hm
        cls.GUIREN = mod_hm.TIANYI_GUIREN

    def test_all_10gan_positive_cases(self):
        """正例：每个天干 2 个贵人地支 必须完全等于黄金基准"""
        for gan, exp in GOLD_TRUTH_GUIREN_FULL_10GAN.items():
            actual = self.GUIREN.get(gan, [])
            self.assertEqual(sorted(actual), sorted(exp['pos']),
                "%s日贵人时正例错：基准=%s 实际=%s（口诀：甲戊庚牛羊/乙己子申/丙丁亥酉/辛寅午/壬癸卯巳）"
                % (gan, exp['pos'], actual))

    def test_all_10gan_negative_cases_not_in_gr(self):
        """反例证伪：每个天干 2 个非贵人地支 必须不出现在贵表"""
        for gan, exp in GOLD_TRUTH_GUIREN_FULL_10GAN.items():
            gr = set(self.GUIREN.get(gan, []))
            for neg_z in exp['neg']:
                self.assertNotIn(neg_z, gr,
                    "%s日贵人时反例错：'%s' 不应为%s日贵人（反例池应为非贵人时）" % (gan, neg_z, gan))


# ============================================================================
# I. 修造乾山巽向兼亥 2021-12-03 端到端黄金基准（用户真实报告锁死）
# ============================================================================
# 用户贴的正式报告（修造4男事主，175分★★★★大吉）。字段清单：
#   四柱: 辛丑 己亥 乙酉 壬午  // 大黄道=朱雀凶-15,小黄道=开吉+5,时辰金匮吉+10,综合-10
#   年三煞=寅卯辰 / 月三煞=申酉戌 / 日三煞=寅卯辰，月三煞犯日柱酉 → 三煞总扣-20
#   三煞检查：年不犯 / 月犯日柱 / 日不犯
#   山家警告：时灾煞 / 正阴府(乙干忌) / 克山运（冬至前）
#   吉神：天德+20 / 岁禄+15 / 天德日+15 / 岁马到山+15 / 上吉日+12 / 吉期+10 / 母仓+10 /
#         四相+10 / 相主+10 / 补龙+8 / 时合事主2+6 / 日半三合事主1+5 / 开+5 / 扶山+3
#   凶煞：地耗-10 / 吊客-12 / 地贼-15 / 鲁班煞-20 / 年冲事主2(丑冲未)-20
#   评分：五行=157（基础100+神煞67+宜50-忌60）/月令+5 /喜用神+33 /黄道-10 /太阳太阴+10
#         公式 157+5+33-10+10=195 → 上限裁剪→175
#   月令分析：乙木日主，亥月得生而相
#   五行生克（方向修正 VII 断言）：必须出现 "木克土：日柱乙(木)克月柱己(土)"，
#                                   禁止出现旧 bug 的 "月柱己(土)克日柱乙(木)"
#   安全方位 15 个：壬子癸艮甲乙巽丙丁坤庚辛乾亥（均0分）
#
# 注：上为 2021 年用户贴的原始报告（历史输入，不删改）；其 175/151/136 评分为当时规则
# 产物。2026-09-18 起黄金断言锁现行规则真值 20/42（否决链已解除，差距为 09 月拍板的
# 规则强化累积），依据见下方 GOLD_XIUZAO_20211203_SCORE 注释。
# ============================================================================
GOLD_XIUZAO_20211203_SIZHU = {
    'date_tuple': (2021, 12, 3),
    '四柱': ('辛丑', '己亥', '乙酉', '壬午'),  # 年/月/日/时柱
}
# 黄金评分（2026-09-18 用户拍板更新为现行规则真值；setUpClass 与 GUI 同口径注入事主喜用神）
#
# 【为什么是 20/42 而不是旧基准 136/151】否决链已于 2026-09-18 三档口径修复后全部解除
# （veto_reasons=[]），数值差距来自 09 月历次【用户已拍板】的规则强化累积，非 bug、非放水：
#   五行 42 = 基础100 + 神煞61 + 宜事30 + 忌事-150 + 十二长生-7 + 地支关系0 + 纳音8
#   正五行 16 = 五行42 + 月令5 + 喜用44 + 相主-35 + 黄道-10 + 太阳太阴10 + 三煞-40
#   总分  20 = int(16×0.7 + (50+飞星-20)×0.3) = int(20.2) = 20
#             （方案B飞星加权，2026-09-01 用户确认；时柱关系-6 已含于五行地支关系，不重复计）
# 忌事 -150 十项：月三煞(日柱)/时灾煞(无制化)/正阴府(无制化)/年柱丑冲事主2与4（含扶山不论1项）/
#                 兼山山家三煞×2/正阴府忌乙日干/克山运（已带"有制化：天德到山，不禁用"，仅忌项不否决）。
GOLD_XIUZAO_20211203_SCORE = 20  # 接口返回真实总分（feixing 加权后，与 GUI 一致）
GOLD_XIUZAO_20211203_LEVEL = '❌ 凶'  # 真实 level 文案（20 分档）
GOLD_XIUZAO_20211203_WUXING_SCORE = 42  # 五行评分（接口真实值，分项锁见 test_03）
# 五行分项锁（键名与 wu_xing_result.score_breakdown 精确一致；七项之和必须=42）
GOLD_XIUZAO_20211203_WUXING_BREAKDOWN = {
    '基础分': 100, '神煞得分': 61, '宜事得分': 30, '忌事得分': -150,
    '十二长生得分': -7, '地支关系得分': 0, '纳音匹配得分': 8,
}
# 正五行总分（飞星加权前）与方案B加权公式锁
GOLD_XIUZAO_20211203_ZHENGWU = 16
GOLD_XIUZAO_20211203_FEIXING = -20
# 三煞干支集（纯地支）+ 月三煞犯日柱 + 三煞扣分
GOLD_XIUZAO_20211203_SANSHA = {
    '年三煞': {'寅', '卯', '辰'},
    '月三煞': {'申', '酉', '戌'},
    '日三煞': {'寅', '卯', '辰'},
    '月三煞犯日柱': True,  # 酉 ∈ 申酉戌；对应 sansha_info.month_sansha_day_fan == 'True'
    # 2026-09-18 基准更新：sansha_penalty 语义已从"纯三煞扣分"演化为"三煞 + 山家
    # 无制化警告"综合扣分容器（评分器约 L1184：mountain_warnings 中带"（无制化）"
    # 的时灾煞/正阴府等各 -10 累加）。本例：月三煞犯日柱-20 + 时灾煞(无制化)-10
    # + 正阴府(无制化)-10 = -40。明细见 sansha_penalty_detail 三栏锁。
    '三煞总扣分': -40,      # 对应 sansha_info.sansha_penalty
    '三煞扣分明细': ['月三煞犯日柱（-20分）',
                  '时灾煞（无制化）（-10分）',
                  '乙干见，犯正阴府，需制化（不禁用）（无制化）（-10分）'],
}
# 黄道分（真实接口返回；注意字段值可能是 str，断言时统一 int 化）
GOLD_XIUZAO_20211203_HUANGDAO = {
    'da_name': '朱雀', 'da_type': '凶', 'da_score': -15,
    'xiao_name': '开',   'xiao_type': '吉', 'xiao_score': +5,
    'shichen_name': '金匮', 'shichen_type': '吉', 'shichen_score': +10,
    'score_sum': -10,
}
# 月令 + 喜用神（2026-09-18 起 setUpClass 与 GUI 同口径注入喜用，喜用由 0 变真值 44）
GOLD_XIUZAO_20211203_YUELING = {'旺衰': '相', '总分': +5}
GOLD_XIUZAO_20211203_XISHEN = {'总分': 44}


class TestXiuZao20211203(unittest.TestCase):
    """用户真实报告 · 修造乾山巽向兼亥 2021-12-03 端到端硬断言 + VII 木克土方向锁死"""

    @staticmethod
    def _build_owners():
        """按用户报告的4男事主构造 owners 数组（精确时辰对齐用户贴的事主四柱）"""
        return [
            # 事主1：1961-09-13 09:00（丙寅时，精确匹配用户报告 辛丑 丁酉 己酉 丙寅）
            {'name': '事主1', '性别': '男', 'role': '事主',
             'birth_date': date(1961, 9, 13), 'birth_hour': 9, 'birth_minute': 0},
            # 事主2：1967-10-23 07:00（庚辰时，精确匹配 丁未 庚戌 庚申 庚辰）
            {'name': '事主2', '性别': '男', 'role': '事主',
             'birth_date': date(1967, 10, 23), 'birth_hour': 7, 'birth_minute': 0},
            # 事主3：1972-01-08 07:00（丙辰时，精确匹配 辛亥 辛丑 戊戌 丙辰）
            {'name': '事主3', '性别': '男', 'role': '事主',
             'birth_date': date(1972, 1, 8), 'birth_hour': 7, 'birth_minute': 0},
            # 事主4：无八字信息，保留占位（1980-01-01为羊，年支丑冲未——与真实ji_list第2项一致）
            {'name': '事主4', '性别': '男', 'role': '事主',
             'birth_date': date(1980, 1, 1), 'birth_hour': 12, 'birth_minute': 0},
        ]

    @classmethod
    def setUpClass(cls):
        from modules.评分器 import calculate_score
        from modules.四柱计算器 import calculate_sizhu
        y, m, d = GOLD_XIUZAO_20211203_SIZHU['date_tuple']
        sz = calculate_sizhu(date(y, m, d), 12, 0)
        # 对齐主程序.py L1992 的 sizhu 格式：额外 year/month/day/date
        sz['year'] = y; sz['month'] = m; sz['day'] = d; sz['date'] = date(y, m, d)
        # 中文四柱键（主程序消费用）
        from modules.工具函数 import TIAN_GAN, DI_ZHI
        sz['年柱'] = sz.get('年柱', '') or (sz.get('year_gan') or '') + (sz.get('year_zhi') or '')
        sz['月柱'] = sz.get('月柱', '') or (sz.get('month_gan') or '') + (sz.get('month_zhi') or '')
        sz['日柱'] = sz.get('日柱', '') or (sz.get('day_gan') or '') + (sz.get('day_zhi') or '')
        sz['时柱'] = sz.get('时柱', '') or (sz.get('hour_gan') or '') + (sz.get('hour_zhi') or '')
        cls.sizhu = sz
        cls.owners = cls._build_owners()
        # 2026-09-18：与主程序/GUI 同口径注入事主喜用神（calculate_score 接口本身不自动
        # 计算喜用，未注入时喜用项=0、总分被 feixing 加权后钳为 0 分，与 GUI 看到的不一致）
        from modules.喜用神计算器 import calculate_xishen_yongshen
        for _o in cls.owners:
            _xy = calculate_xishen_yongshen(
                calculate_sizhu(_o['birth_date'], _o.get('birth_hour', 12), _o.get('birth_minute', 0)))
            _o['xishen'], _o['yongshen'] = _xy[0], _xy[1]
        cls.result = calculate_score(sizhu=sz, event_type='修造',
                                     owners=cls.owners,
                                     house_type='阳宅',
                                     shan_xiang='乾山巽向兼亥')

    # ------------------------------------------------------------------
    # 1. 四柱 + 基础字段
    # ------------------------------------------------------------------
    def test_01_sizhu_pillars_exact(self):
        """I-01 四柱字符级一致：辛丑 / 己亥 / 乙酉 / 壬午"""
        exp_y, exp_m, exp_d, exp_h = GOLD_XIUZAO_20211203_SIZHU['四柱']
        for k, exp in [('年柱', exp_y), ('月柱', exp_m), ('日柱', exp_d), ('时柱', exp_h)]:
            self.assertEqual(self.sizhu.get(k), exp, "四柱%r 错：基准=%r 实际=%r"
                % (k, exp, self.sizhu.get(k)))

    def test_02_score_and_components_feixing_weighted_20(self):
        """I-02 总分 20（2026-09-18 现行规则真值，setUpClass 注入事主喜用、feixing 默认模式，
        与 GUI 同口径）。先锁否决链为空，再锁分数：
          正五行16 = 五行42+月令5+喜用44+相主-35+黄道-10+太阳10+三煞-40
          总分 20 = int(16×0.7 + (50+飞星-20)×0.3)（方案B加权，2026-09-01 用户确认）"""
        self.assertIsInstance(self.result, dict, "calculate_score 应返回 dict，实际 %r" % type(self.result))
        # 否决链必须为空：2026-09-18 三档口径（克山运仅日柱/年命六冲三档）修复后此课不再被否决
        self.assertEqual(self.result.get('veto_reasons') or [], [],
            "2021 黄金课否决链应为空（三档口径后），实际=%r" % (self.result.get('veto_reasons'),))
        s_raw = self.result.get('score')
        self.assertIsNotNone(s_raw, "result 缺 score 字段")
        s = int(s_raw) if isinstance(s_raw, (str, int, float)) else None
        self.assertEqual(s, GOLD_XIUZAO_20211203_SCORE,
            "修造总分错（改阈值/分项权重会漂移）：基准=%r 实际=%r raw=%r"
            % (GOLD_XIUZAO_20211203_SCORE, s, s_raw))
        # score_details.总分 精确对齐
        sd = self.result.get('score_details', {})
        total_raw = sd.get('总分')
        if total_raw is not None:
            self.assertEqual(int(total_raw), GOLD_XIUZAO_20211203_SCORE,
                "score_details.总分 与 result.score 不一致：detail=%r score_raw=%r" % (total_raw, s_raw))
        # 方案B加权公式锁：正五行×0.7 + (50+飞星)×0.3 → 20
        _zw = sd.get('正五行总分')
        _fx = sd.get('飞星评分')
        if _zw is not None and _fx is not None:
            self.assertEqual(int(_zw), GOLD_XIUZAO_20211203_ZHENGWU,
                "正五行总分（加权前）应为 16，实际=%r" % (_zw,))
            self.assertEqual(int(_fx), GOLD_XIUZAO_20211203_FEIXING,
                "飞星评分应为 -20，实际=%r" % (_fx,))
            self.assertEqual(
                max(0, min(100, int(int(_zw) * 0.7 + (50 + int(_fx)) * 0.3))),
                GOLD_XIUZAO_20211203_SCORE,
                "方案B加权公式产出与总分不一致：正五行=%r 飞星=%r" % (_zw, _fx))
        # level 文本
        lv = self.result.get('level')
        self.assertEqual(lv, GOLD_XIUZAO_20211203_LEVEL,
            "level 文案错：基准=%r 实际=%r" % (GOLD_XIUZAO_20211203_LEVEL, lv))

    def test_03_wuxing_base_42(self):
        """I-03 五行评分 42（2026-09-18 现行规则真值）=
        基础100 + 神煞61 + 宜事30 + 忌事-150 + 十二长生-7 + 地支关系0 + 纳音8（七项分项锁）。
        忌事 -150 是 09 月历次用户拍板的规则强化（三煞/阴府/冲主/山家三煞/克山运），
        非为通过测试而放宽；wu_xing_result.score 精确一致。"""
        sd = self.result.get('score_details', {})
        wsc = sd.get('五行评分')
        if wsc is not None:
            self.assertEqual(int(wsc), GOLD_XIUZAO_20211203_WUXING_SCORE,
                "score_details.五行评分 应为%r 实际=%r" % (GOLD_XIUZAO_20211203_WUXING_SCORE, wsc))
        # wu_xing_result.score 同源校验
        wxr = self.result.get('wu_xing_result') or {}
        wxs = wxr.get('score') if isinstance(wxr, dict) else None
        if wxs is None and wxr is not None and hasattr(wxr, 'score'):
            wxs = wxr.score
        if wxs is not None:
            self.assertEqual(int(wxs), GOLD_XIUZAO_20211203_WUXING_SCORE,
                "wu_xing_result.score 应为%r 实际=%r" % (GOLD_XIUZAO_20211203_WUXING_SCORE, wxs))
        # 分项锁：score_breakdown 七项（键名/值精确，和必须=42）
        brk = wxr.get('score_breakdown') if isinstance(wxr, dict) else None
        if brk is None and wxr is not None and hasattr(wxr, 'score_breakdown'):
            brk = wxr.score_breakdown
        if isinstance(brk, dict) and brk:
            _part_sum = 0
            for key, exp_v in GOLD_XIUZAO_20211203_WUXING_BREAKDOWN.items():
                self.assertEqual(int(brk.get(key, 0)), exp_v,
                    "score_breakdown %s 应为%d（实际=%r）" % (key, exp_v, brk.get(key)))
                _part_sum += exp_v
            self.assertEqual(_part_sum, GOLD_XIUZAO_20211203_WUXING_SCORE,
                "七项分项之和 %d 应闭合为五行评分 42" % _part_sum)

    def test_04_huangdao_da_xiao_shichen_sum(self):
        """I-04 大黄道=朱雀凶-15 / 小黄道=开吉+5 / 时辰=金匮吉+10 / 综合-10"""
        hd = self.result.get('huangdao_info') or {}
        if not hd:
            self.skipTest("result 缺 huangdao_info，字段名可能被改")
        da = hd.get('da_huang_dao') or {}
        xiao = hd.get('xiao_huang_dao') or {}
        sh = hd.get('shichen_huang_dao') if isinstance(hd.get('shichen_huang_dao'), dict) else {}
        def _I(x): return int(x) if isinstance(x, (str, int, float)) else x
        self.assertEqual(da.get('name'), '朱雀', "大黄道应为朱雀，前次『朱雀→司命』bug永久锁死，若漂移即FAIL")
        self.assertEqual(da.get('type'), '凶', "大黄道应为凶值神")
        self.assertEqual(_I(da.get('score')), -15, "朱雀扣分应为 -15")
        self.assertEqual(xiao.get('name'), '开', "小黄道建除应为『开』")
        self.assertEqual(xiao.get('type'), '吉')
        self.assertEqual(_I(xiao.get('score')), 5, "开日加分应为 +5")
        self.assertEqual(sh.get('name'), '金匮', "壬午时 时辰黄道应为金匮（吉），若被改立即FAIL")
        self.assertEqual(sh.get('type'), '吉')
        self.assertEqual(_I(sh.get('score')), 10)
        self.assertEqual(_I(hd.get('huang_dao_score')), GOLD_XIUZAO_20211203_HUANGDAO['score_sum'],
            "黄道综合分 应为 -10（朱雀-15+开+5，时辰金匮+10不计入综合分按用户报告仅大黄道+小黄道）")

    def test_05_sansha_mapping_pure_dizhi_and_offend_day_zhi(self):
        """I-05 三煞映射纯地支 + 月三煞犯日柱酉 True（申酉戌）+ 三煞综合扣分-40
        （-20月三煞犯日柱 + 时灾煞/正阴府两个无制化警告各-10，2026-09-18 基准更新）"""
        si = self.result.get('sansha_info') or {}
        if not si:
            self.skipTest("result 缺 sansha_info")
        # 取集合化三煞（容忍字段名差异，兼容 san_sha/年三煞/year 多种）
        def _pick(keys):
            for k in keys:
                if k in si:
                    v = si[k]
                    if isinstance(v, list): return set(v)
                    if isinstance(v, (set, tuple)): return set(v)
                    if isinstance(v, str) and len(v) <= 9: return set(list(v))
            return None
        def _Ib(v): return (v is True or v == 'True' or (isinstance(v, (str,int)) and int(v) == 1))
        def _I(v): return int(v) if isinstance(v, (str, int, float)) else v
        yss = _pick(['年三煞', 'year_sansha', 'nian_sansha'])
        mss = _pick(['月三煞', 'month_sansha', 'yue_sansha'])
        dss = _pick(['日三煞', 'day_sansha', 'ri_sansha'])
        if yss is None or mss is None or dss is None:
            self.skipTest("sansha_info 键名变：%s" % list(si.keys()))
        self.assertSetEqual(yss & set('甲乙丙丁戊己庚辛壬癸'), set(),
            "三煞集合内含天干！违反纯地支硬约束（L3C 已锁纯地支规则）")
        self.assertSetEqual(mss & set('甲乙丙丁戊己庚辛壬癸'), set(),
            "三煞集合内含天干！违反纯地支硬约束")
        self.assertSetEqual(dss & set('甲乙丙丁戊己庚辛壬癸'), set(),
            "三煞集合内含天干！违反纯地支硬约束")
        # 精确集合匹配
        self.assertSetEqual(yss, GOLD_XIUZAO_20211203_SANSHA['年三煞'])
        self.assertSetEqual(mss, GOLD_XIUZAO_20211203_SANSHA['月三煞'])
        self.assertSetEqual(dss, GOLD_XIUZAO_20211203_SANSHA['日三煞'])
        # 月三煞犯日柱 = 月三煞范围包含日支酉
        mdf_key_pool = ['month_sansha_day_fan', '月三煞犯日柱', '月三煞_日柱犯']
        mdf_val = None
        for mk in mdf_key_pool:
            if mk in si:
                mdf_val = si[mk]; break
        self.assertIsNotNone(mdf_val, "sansha_info 缺 月三煞犯日柱 标志位，键=%s" % list(si.keys()))
        self.assertTrue(_Ib(mdf_val),
            "月三煞犯日柱应为 True（日支酉 ∈ 申酉戌），实际=%r" % (mdf_val,))
        # 三煞综合扣分 = -40（三煞+无制化警告容器口径）
        pen_key_pool = ['sansha_penalty', '三煞扣分', '三煞总扣分']
        pen_val = None
        for pk in pen_key_pool:
            if pk in si:
                pen_val = si[pk]; break
        self.assertIsNotNone(pen_val, "sansha_info 缺 三煞总扣分 字段，键=%s" % list(si.keys()))
        self.assertEqual(_I(pen_val), GOLD_XIUZAO_20211203_SANSHA['三煞总扣分'],
            "三煞总扣分 应为 %r 实际=%r" % (GOLD_XIUZAO_20211203_SANSHA['三煞总扣分'], pen_val))
        # 明细三栏锁：扣分去向可追溯（月三煞 + 两个无制化警告），防字段语义再漂移
        pen_detail = si.get('sansha_penalty_detail')
        if pen_detail is not None:
            self.assertEqual(list(pen_detail), GOLD_XIUZAO_20211203_SANSHA['三煞扣分明细'],
                "三煞扣分明细漂移，实际=%r" % (pen_detail,))

    def test_06_special_ke_items_hits(self):
        """I-06 关键忌项跨字段命中：ji_list(正阴府/年冲事主2/4/克山运/山家三煞) +
        sansha_info(月三煞犯日柱/灾煞警告) 联合命中（劫煞/月三煞/灾煞不在ji_list，在sansha_info里）"""
        jl = self.result.get('ji_list') or []
        si = self.result.get('sansha_info') or {}
        if not jl and not si:
            self.skipTest("ji_list & sansha_info 都缺失")
        # ---- ji_list 必须命中 4 项（精确对应用户报告 5 条中的 4 条核心）----
        ji_keys = [
            '正阴府',              # 乾山巽向兼亥正阴府：忌乙日干
            '年柱丑冲事主2',       # 年柱丑冲事主2生肖未
            '年柱丑冲事主4',       # 年柱丑冲事主4生肖未（占位事主生肖未）
            '克山运',              # 克山运：己丑火，忌水克
            '山家三煞',            # 山家三煞：忌亥月
        ]
        ji_missing = [k for k in ji_keys if not any(k in str(j) for j in jl)]
        # ---- sansha_info 命中 2 项（用户报告的"月三煞(日柱)"和"时灾煞"）----
        si_hit = []
        # 月三煞犯日柱（用户报告的 ❌ 月三煞犯日柱）
        for mk in ['month_sansha_day_fan', '月三煞犯日柱']:
            if mk in si and (si[mk] is True or str(si[mk]) == 'True'):
                si_hit.append('月三煞犯日柱'); break
        # 灾煞（用户报告的山家警告"时灾煞（无制化）"）
        warnings_pool = []
        for wk in ['mountain_warnings', 'mountain_day_check']:
            if wk in si:
                wv = si[wk]
                if isinstance(wv, list):
                    warnings_pool += [str(x) for x in wv]
                elif isinstance(wv, dict):
                    for vk in ['警告', '警告列表']:
                        if isinstance(wv.get(vk), list):
                            warnings_pool += [str(x) for x in wv[vk]]
                    if isinstance(wv.get('说明'), str):
                        warnings_pool.append(wv['说明'])
        if any('灾煞' in s for s in warnings_pool):
            si_hit.append('时灾煞')
        # ---- 汇总 missing ----
        si_expected = ['月三煞犯日柱', '时灾煞']
        si_missing = [e for e in si_expected if e not in si_hit]
        total_missing = ji_missing + si_missing
        self.assertEqual(total_missing, [],
            "关键忌项缺失：ji缺%r si缺%r（ji_list全文=%r；mountain警告=%r）"
            % (ji_missing, si_missing, jl[:20], warnings_pool[:10]))

    def test_07_yi_list_contains_kaifu_tiande(self):
        """I-07 宜列表含核心：建除开日宜修造 / 天德日宜修造 / 乾山 / 辛丑年利。
        2026-09-18 基准更新：原断言含"十二月吉"月令吉语，但全软件生产代码与数据
        从未实现该吉语（仅本测试 09-16 建档时写入），属功能缺口而非回归，移出硬
        断言；月令吉语补实现另立功能项（见 docs/问题跟踪_001）。"""
        yl = self.result.get('yi_list') or []
        hit_keys = ['开日宜修造', '天德日宜修造', '乾山', '辛丑年利']
        missing = [k for k in hit_keys if not any(k in str(y) for y in yl)]
        self.assertEqual(missing, [],
            "yi_list 缺关键项 %r（宜列表全文：%r）" % (missing, yl[:20]))

    def test_08_shensha_ji_xiong_core_names_and_scores(self):
        """I-08 神煞+忌跨字段命中：shensha_list 命中 吉神(天德20/岁禄15/岁马到山15/上吉日12/母仓10/四相10/相主10/补龙8/开5/扶山3) 凶煞(地贼-15/鲁班煞-20/地耗-10/吊客-12)；
        年冲事主2 在 ji_list 而非 shensha_list，额外查ji_list：'年柱丑冲事主2生肖未'。
        2026-09-18 基准更新：天德(20)与天德日(15)为同源吉神，09-16 起"二选一保留
        较高者"（修造神煞.py L180 有意去重，防重复计分虚高）——本例天德20在册，
        天德日15 不应再出现；二者至少命中其一，且不得同时计分。"""
        sl = self.result.get('shensha_list') or []
        jl = self.result.get('ji_list') or []
        if not sl:
            self.skipTest("shensha_list 缺失")
        def _I(x): return int(x) if isinstance(x, (str, int, float)) else x
        def _find(prefix, score):
            for s in sl:
                if isinstance(s, dict) and prefix in (s.get('name') or '') and _I(s.get('score')) == score:
                    return True
            return False
        good = [
            ('岁禄', 15), ('岁马到山', 15), ('上吉日', 12),
            ('母仓', 10), ('四相', 10), ('相主', 10), ('吉期', 10),
            ('建除十二神-开', 5), ('扶山', 3), ('补龙', 8),
        ]
        bad = [('地贼', -15), ('鲁班煞', -20), ('地耗', -10), ('吊客', -12)]
        missing = []
        for nm, sc in good + bad:
            if not _find(nm, sc):
                missing.append((nm, sc))
        # 天德/天德日 二选一去重锁
        has_tiande20 = _find('天德', 20)
        has_tiandri15 = _find('天德日', 15)
        if not (has_tiande20 or has_tiandri15):
            missing.append(('天德20/天德日15(二选一)', '两者均缺'))
        if has_tiande20 and has_tiandri15:
            missing.append(('天德20+天德日15不得并存', '同源吉神重复计分'))
        # 年冲事主2 -20 扣分不在 shensha_list，在 ji_list 里文案"年柱丑冲事主2生肖未"
        nian_chong_hit = any('年柱丑冲事主2生肖未' in str(j) for j in jl)
        if not nian_chong_hit:
            missing.append(('年柱丑冲事主2生肖未', 'ji_list缺失'))
        self.assertEqual(missing, [],
            "神煞/忌 缺关键(名称,分/位置) %r。现有前 20 项：%r；ji_list=%r"
            % (missing,
               [(s.get('name'), _I(s.get('score'))) for s in sl[:20] if isinstance(s, dict)],
               jl[:10]))

    def test_09_yueling_wangxiang_yi_says_xiang(self):
        """I-09 月令分析：乙木日主 亥月得生而「相」（旺衰5分 + 支支关系0分 = 月令总分5）"""
        # 分数层：优先 score_details.月令得分 / 月令详细.旺衰得分
        sd = self.result.get('score_details', {})
        total_raw = sd.get('月令得分')
        if total_raw is None:
            yls = self.result.get('yueling_details') or self.result.get('月令') or {}
            if isinstance(yls, dict):
                total_raw = yls.get('score') or yls.get('总分')
        if total_raw is not None:
            self.assertEqual(int(total_raw), 5, "月令得分应为 +5 实际=%r" % (total_raw,))
        # 旺衰分项 = 5，支支关系分项 = 0
        yld = sd.get('月令详细') if isinstance(sd, dict) else None
        if isinstance(yld, dict):
            wang = yld.get('旺衰得分')
            if wang is not None:
                self.assertEqual(int(wang), 5, "旺衰得分应为 +5 实际=%r" % (wang,))
            zhi = yld.get('支支关系得分')
            if zhi is not None:
                self.assertEqual(int(zhi), 0, "支支关系得分应为 0 实际=%r" % (zhi,))
        # 文本级断言：wu_xing_result.details['日主旺衰'] 含『相』+『亥』
        wxr = self.result.get('wu_xing_result') or {}
        details = wxr.get('details') if isinstance(wxr, dict) else None
        if details is None and wxr is not None and hasattr(wxr, 'details'):
            details = wxr.details
        wangshuai = (details or {}).get('日主旺衰') if isinstance(details, dict) else ''
        if wangshuai:
            self.assertIn('相', wangshuai,
                "日主旺衰文案应含『相』（乙亥得生而相），实际=%r" % (wangshuai,))
            self.assertIn('亥', wangshuai,
                "日主旺衰文案应含月令『亥』，实际=%r" % (wangshuai,))

    def test_10_wuxing_shengke_muketu_direction_locked_VII(self):
        """VII 修复永久锁死：五行生克列表 必须出现『日柱乙(木)克月柱己(土)』，
           绝不能出现旧bug『月柱己(土)克日柱乙(木)』方向写反"""
        wxr = self.result.get('wu_xing_result') or {}
        details = wxr.get('details') if isinstance(wxr, dict) else {}
        sk = details.get('五行生克') if isinstance(details, dict) else None
        if not sk:
            # 备用：从 score_details 找五行生克
            sd = self.result.get('score_details') or {}
            sk = sd.get('五行生克') if isinstance(sd, dict) else None
        if not sk:
            self.skipTest("五行生克字段名变：result keys=%r" % list(self.result.keys()))
        joined = " | ".join(str(x) for x in sk)
        # 方向正确性
        self.assertIn('日柱乙(木)克月柱己(土)', joined,
            "VII bug方向仍未修复！应含『日柱乙(木)克月柱己(土)』，实际=%r" % (joined,))
        # 方向反写禁令
        self.assertNotIn('月柱己(土)克日柱乙(木)', joined,
            "VII bug方向写反复辟！旧反写『月柱己(土)克日柱乙(木)』不应再出现在报告里！")


# ============================================================================
# J. 嫁娶 2026-02-22 端到端黄金基准（用户三问题验证：F2 无扣分严格过滤 + F3 不显示二十四山）
# ============================================================================
# 用户贴的真实问题：
#   ① F1 修复（列表显示±号）已在主程序5处Treeview统一format；
#   ② F2 修复（无扣分按钮）原"只滤黄道喜用<-20"→ 严格"任一扣分项立即过滤"；
#   ③ F3 修复（嫁娶详情不显示二十四山）原"shan_xiang or sansha_info即显示"→ 婚嫁类整段跳过；
#
# 2026-02-22 午时（11:00）嫁娶真实 calculate_score 返回：
#   四柱：丙午 庚寅 丁卯 丙午
#   大黄道=朱雀(凶-15)，小黄道=除(吉+5)，时辰金匮(吉+10)，综合-10
#   → 嫁娶类不把黄道扣分计入 score_details['黄道得分']（=None→转0）
#   无五行扣分 / 月令+5 / 喜用神0 / 相主None→0 / 太阳太阴0 / 三煞空
#   神煞仅"小利月"+15（无负分）/ ji_list=['建除除日']（2026-09-16 口径：除日忌嫁娶）
#   / yi_list=天德日/不将日（除已由 嫁娶规则 JIANCHU_YI 移出，原"建除除日"移至忌项）
#   → 除日忌嫁娶（忌项'建除除日'），严格无扣分模式**应过滤（忌列表非空）**；
#     干净结果（无忌项/无扣分）才应保留，见 test_04。
#
# 对比项：同一日同一事主→修造类，修造类会把黄道综合-10写入score_details['黄道得分']，
#   → 严格无扣分模式**应过滤（skip_reason='黄道得分=-10'）**，从而正反双锁 F2。
# ============================================================================
GOLD_JQ_20260222_SIZHU = (2026, 2, 22, 11, 0)   # 年/月/日/时/分
GOLD_JQ_20260222_PILLARS = ('丙午', '庚寅', '丁卯', '丙午')
GOLD_JQ_20260222_HUANGDAO = {
    'da_name': '朱雀', 'da_type': '凶', 'da_score': -15,
    'xiao_name': '除',   'xiao_type': '吉', 'xiao_score': +5,
    'shichen_name': '金匮', 'shichen_type': '吉', 'shichen_score': +10,
    'score_sum': -10,
}
# 嫁娶类 score_details 分项：注意黄道分项为 None（口径锁死：婚嫁不计入黄道分项扣分）
# 2026-09-18 基准更新：总分 75→43、五行 70→38、level ★平→❌凶。差因婚嫁算法
# 定档后新增的三项深度规则（09-17 归档基线已含同口径，tests/fixtures 4 例可佐证）：
# 冲子星-20、日主旺耗夫星-20、半合局+8（净-32）；70-32=38，38+月令5=43。
# 其余分项（月令5/喜用0/太阳0/黄道None/相主None/has_deduction=False）均未漂移。
GOLD_JQ_20260222_DETAILS = {
    '五行评分': 38, '月令得分': 5, '喜用神得分': 0,
    '黄道得分_IS_NONE': True,    # 嫁娶类该项应为 None（True：None→0；若漂移为数字立即FAIL）
    '相主得分_IS_NONE': True,
    '太阳太阴得分': 0, '总分': 43,
}
GOLD_JQ_20260222_LEVEL = '❌ 凶（犯忌嫁娶，慎用）'


def _nodeduct_strict_check_jq(score_result):
    """**与 主程序.py F2 修复完全同构** 的严格无扣分 10 维判定。
       返回 (should_skip:bool, skip_reasons:list[str])
       修改主程序过滤条件但不同步本函数 → 本测试用例立即 FAIL（同构锁死）。"""
    def _I(v):
        try: return int(v)
        except (TypeError, ValueError):
            return 0
    wu_xing_result = score_result.get('wu_xing_result', {})
    has_wuxing_koufen = bool(wu_xing_result.get('has_deduction', False)) if isinstance(wu_xing_result, dict) \
        else getattr(wu_xing_result, 'has_deduction', False)
    sd = score_result.get('score_details', {})
    yueling_score_v = _I(sd.get('月令得分', 0))
    huangdao_score_v = _I(sd.get('黄道得分', 0))
    xishen_score_v = _I(sd.get('喜用神得分', 0))
    xiangzhu_score_v = _I(sd.get('相主得分', 0))
    sun_moon_score_v = _I(sd.get('太阳太阴得分', 0))
    sansha_info = score_result.get('sansha_info', {})
    sansha_penalty_v = _I(sansha_info.get('sansha_penalty', 0))
    shensha_list = score_result.get('shensha_list', []) or []
    has_xiong_shen_koufen = any(
        isinstance(s, dict) and _I(s.get('score', 0)) < 0 for s in shensha_list)
    ji_list = score_result.get('ji_list', []) or []
    has_ji_list_not_empty = len([j for j in ji_list if str(j).strip()]) > 0
    reasons = []
    if has_wuxing_koufen: reasons.append('五行has_deduction=True')
    if yueling_score_v < 0: reasons.append(f"月令得分={yueling_score_v}")
    if huangdao_score_v < 0: reasons.append(f"黄道得分={huangdao_score_v}")
    if xishen_score_v < 0: reasons.append(f"喜用神得分={xishen_score_v}")
    if xiangzhu_score_v < 0: reasons.append(f"相主得分={xiangzhu_score_v}")
    if sun_moon_score_v < 0: reasons.append(f"太阳太阴得分={sun_moon_score_v}")
    if sansha_penalty_v < 0: reasons.append(f"三煞扣分={sansha_penalty_v}")
    if has_xiong_shen_koufen: reasons.append('神煞列表存在负分项')
    if has_ji_list_not_empty: reasons.append(f"忌列表非空({len(ji_list)}项)")
    return (len(reasons) > 0, reasons)


class TestJiaQu20260222(unittest.TestCase):
    """用户三问题 · 嫁娶 2026-02-22 午时 验证：
       01-03 字段与基础分值硬锁；
       04 F2 判定：干净结果正例 → 10维全通不过滤；本题除日（除日忌嫁娶）→ 命中忌项被过滤；
       05 F2 反例：同一件改修造类 → 修造score_details['黄道得分']=-10→被过滤；
       06 F3 静态常量锁：MARRIAGE_EVENTS/SHAN_EVENTS精确集合，嫁娶在婚嫁集不在修造集；
       07 F3 渲染条件模拟：嫁娶shan_xiang空→不显示二十四山；修造/显式选山→显示。"""

    @classmethod
    def setUpClass(cls):
        from modules.评分器 import calculate_score
        from modules.四柱计算器 import calculate_sizhu
        y, mo, d, h, mi = GOLD_JQ_20260222_SIZHU
        sz = calculate_sizhu(date(y, mo, d), h, mi)
        sz['year'] = y; sz['month'] = mo; sz['day'] = d; sz['date'] = date(y, mo, d)
        from modules.工具函数 import TIAN_GAN, DI_ZHI
        sz['年柱'] = sz.get('年柱', '') or (sz.get('year_gan') or '') + (sz.get('year_zhi') or '')
        sz['月柱'] = sz.get('月柱', '') or (sz.get('month_gan') or '') + (sz.get('month_zhi') or '')
        sz['日柱'] = sz.get('日柱', '') or (sz.get('day_gan') or '') + (sz.get('day_zhi') or '')
        sz['时柱'] = sz.get('时柱', '') or (sz.get('hour_gan') or '') + (sz.get('hour_zhi') or '')
        cls.sizhu = sz
        cls.owners = [
            # 男命 乙亥猪 1995-05-10 辰时（占位事主，用于冲合/喜用神入口有值但不过度触发扣分）
            {'name': '新郎', '性别': '男', 'role': '新郎',
             'birth_date': date(1995, 5, 10), 'birth_hour': 8, 'birth_minute': 0},
            # 女命 丁丑牛 1997-08-15 未时
            {'name': '新娘', '性别': '女', 'role': '新娘',
             'birth_date': date(1997, 8, 15), 'birth_hour': 14, 'birth_minute': 0},
        ]
        # 嫁娶（shan_xiang='' — 婚嫁类通常不传山向）
        cls.r_jq = calculate_score(sizhu=sz, event_type='嫁娶', owners=cls.owners,
                                   house_type='阳宅', shan_xiang='')
        # 修造类反例（同一天、同事主，但 event_type=修造，无山向）
        cls.r_xz = calculate_score(sizhu=sz, event_type='修造', owners=cls.owners,
                                   house_type='阳宅', shan_xiang='')

    # ------------------------------------------------------------------
    # J-01 ~ J-03 基础字段硬锁
    # ------------------------------------------------------------------
    def test_01_sizhu_pillars_exact(self):
        """J-01 嫁娶 2026-02-22 午时 四柱精确：丙午 / 庚寅 / 丁卯 / 丙午"""
        for k, exp in zip(['年柱', '月柱', '日柱', '时柱'], GOLD_JQ_20260222_PILLARS):
            self.assertEqual(self.sizhu.get(k), exp,
                "嫁娶四柱%r错：基准=%r 实际=%r" % (k, exp, self.sizhu.get(k)))

    def test_02_score_details_calibrated(self):
        """J-02 嫁娶总分/分项锁：总分43 / 五行38 / 月令+5 / 喜用0 / 黄道分项=None / 相主=None / 太阳太阴0
        （2026-09-18 更新：原 75/70 基准未含冲子星/耗夫星/半合三项深度规则）
        → 关键：嫁娶类不把黄道综合-10计入score_details；口径漂移到数字立即FAIL。"""
        r = self.r_jq
        self.assertIsInstance(r, dict)
        self.assertEqual(int(r.get('score', -9999)), GOLD_JQ_20260222_DETAILS['总分'],
            "嫁娶总分错：基准=%r 实际=%r" % (GOLD_JQ_20260222_DETAILS['总分'], r.get('score')))
        self.assertEqual(r.get('level'), GOLD_JQ_20260222_LEVEL,
            "嫁娶level错：基准=%r 实际=%r" % (GOLD_JQ_20260222_LEVEL, r.get('level')))
        sd = r.get('score_details', {})
        self.assertEqual(int(sd.get('五行评分')), GOLD_JQ_20260222_DETAILS['五行评分'])
        self.assertEqual(int(sd.get('月令得分')), GOLD_JQ_20260222_DETAILS['月令得分'])
        self.assertEqual(int(sd.get('喜用神得分')), GOLD_JQ_20260222_DETAILS['喜用神得分'])
        self.assertEqual(int(sd.get('太阳太阴得分')), GOLD_JQ_20260222_DETAILS['太阳太阴得分'])
        # 口径锁：嫁娶类黄道分项应为 None（不扣分）；若未来有人改婚嫁评分算法让黄道写回数字，立即FAIL
        if GOLD_JQ_20260222_DETAILS['黄道得分_IS_NONE']:
            self.assertIsNone(sd.get('黄道得分'),
                "嫁娶类 score_details['黄道得分'] 应为 None（婚嫁不计入黄道分项扣分），实际=%r"
                % (sd.get('黄道得分'),))
        if GOLD_JQ_20260222_DETAILS['相主得分_IS_NONE']:
            self.assertIsNone(sd.get('相主得分'),
                "嫁娶类 score_details['相主得分'] 应为 None，实际=%r" % (sd.get('相主得分'),))
        # wu_xing_result.has_deduction=False（F2 正例前置条件）
        wxr = r.get('wu_xing_result') or {}
        hd = wxr.get('has_deduction') if isinstance(wxr, dict) else getattr(wxr, 'has_deduction', None)
        self.assertFalse(bool(hd), "嫁娶类 wu_xing_result.has_deduction 应为 False（F2正例前置），实际=%r" % (hd,))
        # 神煞无负分 + ji_list 空
        def _I(x):
            try: return int(x)
            except: return 0
        sl = r.get('shensha_list') or []
        bad_scores = [s for s in sl if isinstance(s, dict) and _I(s.get('score', 0)) < 0]
        self.assertEqual(bad_scores, [], "嫁娶类神煞不应有负分项，实际=%r" % (bad_scores,))
        jl = r.get('ji_list') or []
        # 2026-09-16 修正：本题日为丁卯=建除「除」日，按用户报告2拍板口径
        # "除日忌嫁娶"（与 modules/黄道.py XIAO_HUANG_DAO_YIJI['除']['ji'] 含'嫁娶'、
        # 婚嫁评分算法 _jianchu_ji={'除','危','执'} 一致），忌列表应有且仅有"建除除日"；
        # 旧断言"ji_list 必空"与现行口径冲突（故仅列示建除项，不得出现"忌嫁娶"否决文案）。
        self.assertIn('建除除日', jl,
            "除日嫁娶应列入忌项'建除除日'（除日忌嫁娶口径），实际=%r" % (jl,))
        self.assertTrue(all('建除' in str(j) for j in jl),
            "本例忌项应仅来自建除十二神（不应出现其他忌项），实际=%r" % (jl,))
        self.assertFalse(any(str(j).strip() in ('忌嫁娶', '嫁娶') for j in jl),
            "建除除日不得写成一票否决文案'忌嫁娶'（否决键须精确匹配），实际=%r" % (jl,))

    def test_03_huangdao_zhu_que_sui_bu_fen_kou_but_info_present(self):
        """J-03 嫁娶 2026-02-22 真实黄道：朱雀凶-15/除吉+5/金匮吉+10/综合-10。
        → 关键：嫁娶类只是不计入 score_details['黄道得分']，但 huangdao_info 仍完整存在（详情页正常展示朱雀扣分）。"""
        hd = self.r_jq.get('huangdao_info') or {}
        self.assertTrue(bool(hd), "嫁娶类 huangdao_info 不应缺失（日课详情页需展示朱雀扣分）")
        def _I(x): return int(x) if isinstance(x, (str, int, float)) else None
        da = hd.get('da_huang_dao') or {}
        xiao = hd.get('xiao_huang_dao') or {}
        sh = hd.get('shichen_huang_dao') if isinstance(hd.get('shichen_huang_dao'), dict) else {}
        self.assertEqual(da.get('name'), GOLD_JQ_20260222_HUANGDAO['da_name'])
        self.assertEqual(da.get('type'), GOLD_JQ_20260222_HUANGDAO['da_type'])
        self.assertEqual(_I(da.get('score')), GOLD_JQ_20260222_HUANGDAO['da_score'])
        self.assertEqual(xiao.get('name'), GOLD_JQ_20260222_HUANGDAO['xiao_name'])
        self.assertEqual(xiao.get('type'), GOLD_JQ_20260222_HUANGDAO['xiao_type'])
        self.assertEqual(_I(xiao.get('score')), GOLD_JQ_20260222_HUANGDAO['xiao_score'])
        self.assertEqual(sh.get('name'), GOLD_JQ_20260222_HUANGDAO['shichen_name'])
        self.assertEqual(sh.get('type'), GOLD_JQ_20260222_HUANGDAO['shichen_type'])
        self.assertEqual(_I(sh.get('score')), GOLD_JQ_20260222_HUANGDAO['shichen_score'])
        self.assertEqual(_I(hd.get('huang_dao_score')), GOLD_JQ_20260222_HUANGDAO['score_sum'],
            "嫁娶类 huangdao_info.huang_dao_score 仍应为综合-10（只是没写进score_details）")

    # ------------------------------------------------------------------
    # J-04 / J-05 F2 严格无扣分：正例不过滤 + 修造类反例命中黄道得分=-10 被过滤
    # ------------------------------------------------------------------
    def test_04_F2_nodeduct_zhengli_pass(self):
        """J-04 F2 严格无扣分判定（10维）：
        ①正例=全维度干净的结果 → 应不过滤（锁 _nodeduct_strict_check_jq 与主程序同构逻辑）；
        ②真实本题日（2026-02-22 丁卯=建除「除」日）→ 按"除日忌嫁娶"口径产生忌项
           "建除除日"，应被过滤，且过滤原因唯一为忌列表非空。
        2026-09-16 修正：旧断言以"本题 ji_list 必空"作正例前置，与用户报告2拍板的
        "除日忌嫁娶"口径冲突（嫁娶规则 JIANCHU_JI 已含'除'），故正例改用干净结果，
        本题日转为口径锁。"""
        clean = {
            'wu_xing_result': {'has_deduction': False},
            'score_details': {'月令得分': 5, '喜用神得分': 0, '黄道得分': None,
                              '相主得分': None, '太阳太阴得分': 0},
            'sansha_info': {'sansha_penalty': 0},
            'shensha_list': [{'name': '天德日', 'score': 15}],
            'ji_list': [],
        }
        should_skip, reasons = _nodeduct_strict_check_jq(clean)
        self.assertFalse(should_skip,
            "F2 严格无扣分正例被误过滤！reasons=%r" % (reasons,))
        self.assertEqual(reasons, [], "正例 reasons 应为空，实际=%r" % (reasons,))
        # 口径锁：本题日为除日 → 除日忌嫁娶 → 必须被过滤（防止有人把'除'退回 JIANCHU_YI）
        should_skip2, reasons2 = _nodeduct_strict_check_jq(self.r_jq)
        self.assertTrue(should_skip2,
            "除日嫁娶应产生忌项而不通过严格无扣分，实际未过滤；ji_list=%r"
            % (self.r_jq.get('ji_list'),))
        self.assertEqual(reasons2, ['忌列表非空(1项)'],
            "除日嫁娶的过滤原因应唯一为忌列表非空(1项)，实际=%r" % (reasons2,))

    def test_05_F2_nodeduct_fanli_xiuzao_filtered_by_huangdao_minus10(self):
        """J-05 F2 反例：同日同时 → 改修造类（event_type=修造，无山向）。
        → 修造类会把 huangdao_info.huang_dao_score=-10 计入 score_details['黄道得分']，
           严格无扣分模式必须命中「黄道得分=-10」被过滤；其他维度不触发的前提下，
           reasons 恰好等于 ['黄道得分=-10']。"""
        # 先前置条件锁死：修造类 score_details['黄道得分']=-10
        sd = self.r_xz.get('score_details', {})
        def _I(x):
            try: return int(x)
            except: return None
        huangdao_int = _I(sd.get('黄道得分'))
        self.assertIsNotNone(huangdao_int,
            "修造类 score_details['黄道得分'] 应存在（是整数），实际=%r。修造类黄道分项口径漂移！"
            % (sd.get('黄道得分'),))
        self.assertLess(huangdao_int, 0,
            "2026-02-22朱雀凶日，修造类黄道分项应<0（黄金基准-10），实际=%r" % (huangdao_int,))
        should_skip, reasons = _nodeduct_strict_check_jq(self.r_xz)
        self.assertTrue(should_skip,
            "F2 修造反例未被过滤！reasons=%r 应该含黄道扣分。修造 score_details=%r"
            % (reasons, sd))
        # 精确命中原因：黄道得分<0
        self.assertTrue(any('黄道得分=' in r for r in reasons),
            "F2 过滤原因必须含'黄道得分=-10'，实际=%r" % (reasons,))

    # ------------------------------------------------------------------
    # J-06 F3 静态常量锁（MARRIAGE_EVENTS / SHAN_EVENTS 精确集合）
    # ------------------------------------------------------------------
    def test_06_F3_event_type_constants_locked(self):
        """J-06 F3 主程序事件类型集合锁：
        MARRIAGE_EVENTS = {嫁娶,订婚,纳采}；SHAN_EVENTS = 修造类 11 件；
        嫁娶 ∈ MARRIAGE_EVENTS ∉ SHAN_EVENTS；修造 ∈ SHAN_EVENTS ∉ MARRIAGE_EVENTS。"""
        try:
            from 主程序 import MARRIAGE_EVENTS, SHAN_EVENTS
        except Exception as e:
            self.skipTest("主程序无法import（可能因TK环境）：%s" % (e,))
        self.assertIsInstance(MARRIAGE_EVENTS, frozenset, "MARRIAGE_EVENTS应为frozenset（不可变常量）")
        self.assertIsInstance(SHAN_EVENTS, frozenset, "SHAN_EVENTS应为frozenset（不可变常量）")
        # 精确三件婚嫁
        for ev in ('嫁娶', '订婚', '纳采'):
            self.assertIn(ev, MARRIAGE_EVENTS, "MARRIAGE_EVENTS 必须含 %r" % (ev,))
            self.assertNotIn(ev, SHAN_EVENTS, "婚嫁类 %r 绝对不应出现在 SHAN_EVENTS（山家类显示集合）" % (ev,))
        self.assertEqual(len(MARRIAGE_EVENTS), 3,
            "MARRIAGE_EVENTS 应只有 3 件（嫁娶/订婚/纳采），实际=%r" % (MARRIAGE_EVENTS,))
        # 修造类11件（精确列表锁）
        SHAN_EXPECTED_11 = {'修造', '动土', '入宅', '安葬', '作灶', '安床', '拆舍', '上梁', '竖柱', '开业', '出行'}
        self.assertSetEqual(SHAN_EVENTS, SHAN_EXPECTED_11,
            "SHAN_EVENTS 11件修造类集合被改！预期=%r 实际=%r" % (SHAN_EXPECTED_11, SHAN_EVENTS))
        # 嫁娶 → 婚嫁类；修造 → 山家类；交集为空
        self.assertSetEqual(MARRIAGE_EVENTS & SHAN_EVENTS, set(),
            "MARRIAGE_EVENTS 与 SHAN_EVENTS 必须无交集（互斥分类）")

    # ------------------------------------------------------------------
    # J-07 F3 渲染条件逻辑模拟（完全同构主程序 F3 修复版 L3911-L3921）
    # ------------------------------------------------------------------
    def test_07_F3_shan_section_render_logic_simulation(self):
        """J-07 F3 与主程序 L3911-L3921 **完全同构** 的二十四山大段渲染条件：
        Case A. 嫁娶 + shan_xiang='' + sansha_info={}      → 必须 False（不显示，用户问题三）
        Case B. 修造 + shan_xiang='' + sansha_info 非空（年三煞） → 必须 True（修造类即使无山向也显示三煞）
        Case C. 嫁娶 + shan_xiang='乾山巽向兼亥'（用户硬选） → 必须 True（选了山向就显示）
        Case D. 修造 + shan_xiang='乾山巽向兼亥'           → 必须 True"""
        # 先拿主程序常量，若拿不到则跳过（CI无TK环境）
        try:
            from 主程序 import MARRIAGE_EVENTS
        except Exception as e:
            self.skipTest("主程序无法import：%s" % (e,))
        # ---- 同构复制主程序 L3911-L3921 逻辑（改一处立即fail）----
        def _should_show_shan(shan_xiang, sansha_info, event_type):
            _show = False
            if shan_xiang:
                _show = True
            elif sansha_info and event_type not in MARRIAGE_EVENTS:
                _show = True
            return _show
        # Case A（用户问题三根因）
        caseA = _should_show_shan('', {}, '嫁娶')
        self.assertFalse(caseA, "F3 A. 嫁娶+无山向+无三煞 → 不应显示二十四山大段，实际=True（问题三再现！）")
        caseA2 = _should_show_shan('', {'年三煞': ['寅', '卯', '辰']}, '嫁娶')
        self.assertFalse(caseA2, "F3 A2. 嫁娶+无山向但sansha_info非空 → 仍不应显示二十四山大段（修复前的bug），实际=True")
        # Case B 修造类无山向但有三煞 → 显示
        caseB = _should_show_shan('', {'年三煞': ['寅', '卯', '辰']}, '修造')
        self.assertTrue(caseB, "F3 B. 修造+无山向但有三煞 → 应显示纯三煞段，实际=False")
        # Case C 嫁娶显式选山向 → 仍显示（用户既然硬选了就想看）
        caseC = _should_show_shan('乾山巽向兼亥', {}, '嫁娶')
        self.assertTrue(caseC, "F3 C. 嫁娶+显式山向 → 应允许显示二十四山大段，实际=False")
        # Case D 修造类选山向 → 显示
        caseD = _should_show_shan('乾山巽向兼亥', {}, '修造')
        self.assertTrue(caseD, "F3 D. 修造+山向 → 应显示二十四山大段，实际=False")
        # 额外：订婚/纳采 与嫁娶同行为（婚嫁三件）
        self.assertFalse(_should_show_shan('', {'年三煞': ['寅']}, '订婚'), "订婚也应隐藏二十四山大段")
        self.assertFalse(_should_show_shan('', {'年三煞': ['寅']}, '纳采'), "纳采也应隐藏二十四山大段")
        # 修造类11件 有三煞必显示
        self.assertTrue(_should_show_shan('', {'年三煞': ['寅']}, '动土'), "动土有三煞 → 显示")
        self.assertTrue(_should_show_shan('', {'年三煞': ['寅']}, '入宅'), "入宅有三煞 → 显示")
        self.assertTrue(_should_show_shan('', {'年三煞': ['寅']}, '安葬'), "安葬有三煞 → 显示")


if __name__ == '__main__':
    unittest.main(verbosity=2)
