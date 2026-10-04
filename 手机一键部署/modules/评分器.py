# -*- coding: utf-8 -*-
"""
================================================================================
评分模块
================================================================================
根据神煞和规则计算综合评分并判断等级
采用"五行为主，黄道为用"的架构

使用方法:
    1. 作为模块导入: from modules.评分器 import calculate_score
    2. 直接运行: python -m modules.评分器
================================================================================
"""

import sys
import os
import re
import logging

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('评分模块.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = (getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable))) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = (getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable))) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    # 添加 shensha 子目录到路径
    shensha_dir = os.path.join(modules_dir, 'shensha')
    if os.path.exists(shensha_dir) and shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)

# 尝试相对导入，失败则使用绝对导入
try:
    from .shensha import get_checker
    from .rules import get_rule_checker
    from .黄道 import calculate_huangdao
    from .喜用神计算器 import calculate_xishen_yongshen
    
    # 导入八字工具整合模块的新功能
    try:
        from .八字工具整合 import (
            get_zhangsheng, get_nayin, get_canggan,
            check_liuhe, check_liuchong, check_sanhe, check_sanxing,
            check_liuhai, check_po, check_xing, check_hai
        )
        HAS_BAZI_TOOLS = True
    except ImportError:
        # 八字工具整合模块不存在，设置默认值
        HAS_BAZI_TOOLS = False
        get_zhangsheng = lambda *args, **kwargs: '未知'
        get_nayin = lambda *args, **kwargs: '未知'
        get_canggan = lambda *args, **kwargs: []
        check_liuhe = lambda *args, **kwargs: False
        check_liuchong = lambda *args, **kwargs: False
        check_sanhe = lambda *args, **kwargs: False
        check_sanxing = lambda *args, **kwargs: False
        check_liuhai = lambda *args, **kwargs: False
        check_po = lambda *args, **kwargs: False
        check_xing = lambda *args, **kwargs: False
        check_hai = lambda *args, **kwargs: False
except ImportError:
    # 绝对导入（用于直接运行）
    from shensha import get_checker
    from rules import get_rule_checker
    from 黄道 import calculate_huangdao
    from 喜用神计算器 import calculate_xishen_yongshen
    
    try:
        from 八字工具整合 import (
            get_zhangsheng, get_nayin, get_canggan,
            check_liuhe, check_liuchong, check_sanhe, check_sanxing,
            check_liuhai, check_po, check_xing, check_hai
        )
        HAS_BAZI_TOOLS = True
    except ImportError:
        # 八字工具整合模块不存在，设置默认值
        HAS_BAZI_TOOLS = False
        get_zhangsheng = lambda *args, **kwargs: '未知'
        get_nayin = lambda *args, **kwargs: '未知'
        get_canggan = lambda *args, **kwargs: []
        check_liuhe = lambda *args, **kwargs: False
        check_liuchong = lambda *args, **kwargs: False
        check_sanhe = lambda *args, **kwargs: False
        check_sanxing = lambda *args, **kwargs: False
        check_liuhai = lambda *args, **kwargs: False
        check_po = lambda *args, **kwargs: False
        check_xing = lambda *args, **kwargs: False
        check_hai = lambda *args, **kwargs: False

# 事项标准注册表（2026-09-16 口径统一：事项分组/画像唯一来源）
try:
    from .事项标准 import (
        event_profile as _event_profile,
        canonical_profile as _canonical_profile,
        canonical_event as _canonical_event,
        get_rule_checker as _std_get_rule_checker,
        get_shensha_checker as _std_get_shensha_checker,
        CONSTRUCTION_SHENSHA_EXT_CLASS as _CONSTRUCTION_EXT_SPEC,
    )
except ImportError:
    from 事项标准 import (
        event_profile as _event_profile,
        canonical_profile as _canonical_profile,
        canonical_event as _canonical_event,
        get_rule_checker as _std_get_rule_checker,
        get_shensha_checker as _std_get_shensha_checker,
        CONSTRUCTION_SHENSHA_EXT_CLASS as _CONSTRUCTION_EXT_SPEC,
    )

# ============================================================================
# 亡命（仙命）角色判定：安葬路径的死者卡。GUI 默认卡名"死者"，兼容
# "亡命/仙命/亡人"称谓（用户可改卡名）。
# ============================================================================
WANGMING_ROLES = ('死者', '亡命', '仙命', '亡人')


def _is_wangming_role(role):
    return str(role or '').strip() in WANGMING_ROLES


# ============================================================================
# 仙命 × 坐山纳音五行生克判定（第二阶段，2026-10-04 用户口径拍板）
# ============================================================================
# 生克分级（传统"坐山扶命为上"，人地不对称）：
#   坐山生仙命=大吉 > 仙命生坐山=小吉 > 比和=平（暂 0 分，待调）
#   > 仙命克坐山=小凶 > 坐山克仙命=凶中之凶
# 否决仅给"坐山克仙命"且叠其他忌时；纯"仙命克坐山"仅扣分不否决。
# 坐山范围：仅正向 24 山，兼向复用主山纳音（第一阶段简化）。
_WANGMING_SHANZUO_SCORE = {
    '坐山生仙命': 20,
    '仙命生坐山': 10,
    '比和': 0,
    '仙命克坐山': -15,
    '坐山克仙命': -30,
}
_WANGMING_SHANZUO_LEVEL = {
    '坐山生仙命': '大吉',
    '仙命生坐山': '小吉',
    '比和': '平',
    '仙命克坐山': '小凶',
    '坐山克仙命': '凶中之凶',
}


def evaluate_wangming_vs_shanzuo(wangming_nayin_wuxing, shanzuo_wuxing):
    """仙命纳音五行 vs 坐山五行 生克判定（方向敏感）。

    返回 dict：
        relation: 方向性关系名（5 种之一）
        score: 基础分值（尚未叠其他忌）
        level: 5 级吉凶（大吉/小吉/平/小凶/凶中之凶）
        reason: 可读文案（供报告展示）
    """
    _wx = str(wangming_nayin_wuxing or '').strip()
    _sx = str(shanzuo_wuxing or '').strip()
    if not _wx or not _sx:
        return {'relation': '未知', 'score': 0, 'level': '平',
                'reason': '仙命或坐山五行缺失，不予判定'}
    from .二十四山 import WuxingRelation
    if WuxingRelation.is_bihe(_wx, _sx):
        relation = '比和'
    elif WuxingRelation.is_sheng(_sx, _wx):
        relation = '坐山生仙命'   # 地生人，大吉
    elif WuxingRelation.is_sheng(_wx, _sx):
        relation = '仙命生坐山'   # 人让地，小吉
    elif WuxingRelation.is_ke(_sx, _wx):
        relation = '坐山克仙命'   # 地克人，凶中之凶
    elif WuxingRelation.is_ke(_wx, _sx):
        relation = '仙命克坐山'   # 人克地，小凶
    else:
        return {'relation': '未知', 'score': 0, 'level': '平',
                'reason': f'无法判定 {_wx} 与 {_sx} 的关系'}
    score = _WANGMING_SHANZUO_SCORE.get(relation, 0)
    level = _WANGMING_SHANZUO_LEVEL.get(relation, '平')
    reason = (
        f"仙命纳音五行属{_wx}，坐山五行属{_sx}，二者{relation}（{level}）"
    )
    return {'relation': relation, 'score': score, 'level': level,
            'reason': reason}


# H1 双族去重映射表（2026-10-01 用户拍板：Q1=甲 Q2=修造建除停 Q3=veto附文停 Q4=交集停/分歧挂账）
# 语义：规则文本精确命中 tx 且当日 shensha_list 含 ss 名 → 该条仅展示、不计分。
H1_ANCHOR_MAP = {
    '嫁娶': [            # 9 族
        ('不将日', '不将日'),
        ('月德', '月德日'),
        ('黄沙', '黄沙日'),
        ('月破', '月破日'),
        ('杨公忌日', '杨公忌'),
        ('神号', '神号日'),
        ('天德', '天德日'),
        ('鬼哭', '鬼哭日'),
        ('红砂日', '红纱日'),
    ],
    '修造': [            # 13 族（建除12＋月破1）
        ('建除十二神-建', '建除建日忌修造'),
        ('建除十二神-除', '建除除日宜修造'),
        ('建除十二神-满', '建除满日忌修造'),
        ('建除十二神-平', '建除平日忌修造'),
        ('建除十二神-定', '建除定日宜修造'),
        ('建除十二神-执', '建除执日宜修造'),
        ('建除十二神-破', '建除破日忌修造'),
        ('建除十二神-危', '建除危日宜修造'),
        ('建除十二神-成', '建除成日宜修造'),
        ('建除十二神-收', '建除收日忌修造'),
        ('建除十二神-开', '建除开日宜修造'),
        ('建除十二神-闭', '建除闭日忌修造'),
        ('月破', '月破日忌修造'),
    ],
    '动土': [            # 2 族
        ('岁破', '岁破日忌动土'),
        ('月破', '月破日忌动土'),
    ],
    '拆舍': [            # 2 族
        ('岁破', '岁破日忌拆舍'),
        ('月破', '月破日忌拆舍'),
    ],
    '入宅': [            # 3 族
        ('不将日', '不将日宜修造'),
        ('岁破', '岁破日忌入宅'),
        ('月破', '月破日忌入宅'),
    ],
    '作灶': [            # 5 族
        ('不将日', '不将日宜作灶'),
        ('丙丁日', '丙丁日火旺宜作灶'),
        ('天火日', '天火日忌作灶'),
        ('灶君朝天', '灶君朝天日忌作灶'),
        ('月破', '月破日忌作灶'),
    ],
    '开业': [            # 3 族
        ('不将日', '不将日宜开业'),
        ('月破', '月破日忌开业'),
        ('破日', '建除破日忌开业'),
    ],
    '出行': [            # 1 族（12 个参数变体精确串）
        ('月破', '月破日(子月午日)忌出行'),
        ('月破', '月破日(丑月未日)忌出行'),
        ('月破', '月破日(寅月申日)忌出行'),
        ('月破', '月破日(卯月酉日)忌出行'),
        ('月破', '月破日(辰月戌日)忌出行'),
        ('月破', '月破日(巳月亥日)忌出行'),
        ('月破', '月破日(午月子日)忌出行'),
        ('月破', '月破日(未月丑日)忌出行'),
        ('月破', '月破日(申月寅日)忌出行'),
        ('月破', '月破日(酉月卯日)忌出行'),
        ('月破', '月破日(戌月辰日)忌出行'),
        ('月破', '月破日(亥月巳日)忌出行'),
    ],
    '安葬': [            # 9 族
        ('不将日', '不将日宜安葬'),
        ('鸣吠日', '鸣吠日宜安葬'),
        ('鸣吠对日', '鸣吠对日宜安葬'),
        ('往亡', '往亡日忌安葬'),
        ('重丧', '重丧日忌安葬'),
        ('年重丧', '年重丧忌安葬'),
        ('复日', '复日忌安葬'),
        ('十恶大败', '十恶大败日忌安葬'),
        ('月破', '月破日忌安葬'),
    ],
    '安床': [            # 2 族
        ('不将日', '不将日宜安床'),
        ('月破', '月破日忌安床'),
    ],
    '签约': [            # 2 族
        ('岁破', '岁破日忌签约'),
        ('月破', '月破日忌签约'),
    ],
}

def _h1_is_veto_reason(text):
    """Q3：规则 veto 理由文本（'岁破日：日支X冲太岁Y，大事忌用'）只展示、不计分。"""
    return isinstance(text, str) and text.startswith('岁破日：日支') and text.endswith('，大事忌用')

class Scorer:
    """评分器"""

    # 不可制化硬否决关键词（忌项文本命中且无"（有制化：…）"标记即阻断放宽；
    # 2026-09-11 从 score() 内联 _hard 提为类常量，供放宽闸门与否决评语共用，
    # 避免"放宽已通过/文案仍列其为大忌"两套口径）
    _HARD_VETO_KEYWORDS = (
        '年三煞', '月三煞', '年家三煞', '岁煞', '岁破', '日破', '日支未冲太岁',
        '五黄到坐山', '五黄在', '犯五黄', '犯二黑', '二黑到坐山',
        '双干', '乙庚合化金克木，.*大凶', '克山运', '正体大凶',
        '大凶（一票否决）', '大凶.*一票否决', '冲山（', '切忌动土',
        '凶煞级', '禁用级', '不可制化'
    )

    @staticmethod
    def _is_pillar_sansha_item(txt):
        """三煞临四柱忌项（如 年三煞(日柱)/月日三煞叠犯(时柱)）；
        三煞犯山向文本以"山向)"结尾，不匹配。山向类事项四柱临方扣分不否决。"""
        return bool(re.search(r'(?:三煞|叠犯)\s*[（(][^）)]*柱[）)]', str(txt)))

    def __init__(self):
        self.base_score = 100
        self.final_score = 100
        self.level = ''
        self.shensha_list = []
        self.yi_list = []
        self.ji_list = []
        self.huangdao_info = {}
        
        # 导入必要的函数
        try:
            from .八字工具整合 import (
                check_liuhe, check_liuchong, check_sanhe, check_sanxing,
                check_liuhai, check_po, check_xing, check_hai
            )
            self.check_liuhe = check_liuhe
            self.check_liuchong = check_liuchong
            self.check_sanhe = check_sanhe
            self.check_sanxing = check_sanxing
            self.check_liuhai = check_liuhai
            self.check_po = check_po
            self.check_xing = check_xing
            self.check_hai = check_hai
        except ImportError:
            # 八字工具整合模块不存在，设置默认值
            self.check_liuhe = lambda *args, **kwargs: False
            self.check_liuchong = lambda *args, **kwargs: False
            self.check_sanhe = lambda *args, **kwargs: False
            self.check_sanxing = lambda *args, **kwargs: False
            self.check_liuhai = lambda *args, **kwargs: False
            self.check_po = lambda *args, **kwargs: False
            self.check_xing = lambda *args, **kwargs: False
            self.check_hai = lambda *args, **kwargs: False
        
        # 导入五行择日法模块
        try:
            from .五行择日法 import 五行择日法
            self.wuxing_selector = 五行择日法()
        except ImportError:
            self.wuxing_selector = None
        
        # 节气日期缓存（避免重复计算）
        self._solar_term_cache = {}
        
        # 节气名称到sxtwl索引的映射
        # sxtwl索引从立春开始（索引0=立春，索引3=春分，索引9=夏至，索引15=秋分，索引21=冬至）
        self._jieqi_indices = {
            '立春': 0, '雨水': 1, '惊蛰': 2,
            '春分': 3, '清明': 4, '谷雨': 5,
            '立夏': 6, '小满': 7, '芒种': 8,
            '夏至': 9, '小暑': 10, '大暑': 11,
            '立秋': 12, '处暑': 13, '白露': 14,
            '秋分': 15, '寒露': 16, '霜降': 17,
            '立冬': 18, '小雪': 19, '大雪': 20,
            '冬至': 21, '小寒': 22, '大寒': 23
        }
        
        # 月建节气（决定农历月份边界的12个节气）
        # 按顺序：立春(1月/寅月)、惊蛰(2月/卯月)、清明(3月/辰月)、
        #         立夏(4月/巳月)、芒种(5月/午月)、小暑(6月/未月)、
        #         立秋(7月/申月)、白露(8月/酉月)、寒露(9月/戌月)、
        #         立冬(10月/亥月)、大雪(11月/子月)、小寒(12月/丑月)
        self._month_jieqi = [
            '立春', '惊蛰', '清明', '立夏', '芒种', '小暑',
            '立秋', '白露', '寒露', '立冬', '大雪', '小寒'
        ]
    
    def _get_solar_term_date(self, year, term_name):
        """
        获取指定年份指定节气的日期（精确到日）
        
        使用sxtwl天文算法，优先精确计算；失败则回退到近似值。
        
        Args:
            year: 年份（如2026）
            term_name: 节气名称（如'立春'）
            
        Returns:
            datetime.date: 节气日期，失败返回近似日期
        """
        from datetime import date, timedelta
        
        cache_key = f"{year}_{term_name}"
        if cache_key in self._solar_term_cache:
            return self._solar_term_cache[cache_key]
        
        # sxtwl节气近似日期（用于回退）
        # 根据sxtwl实际值修正（索引0=立春）
        _jieqi_approx = {
            '立春': (2, 4), '雨水': (2, 19), '惊蛰': (3, 6),
            '春分': (3, 21), '清明': (4, 5), '谷雨': (4, 20),
            '立夏': (5, 6), '小满': (5, 21), '芒种': (6, 6),
            '夏至': (6, 21), '小暑': (7, 7), '大暑': (7, 23),
            '立秋': (8, 8), '处暑': (8, 23), '白露': (9, 8),
            '秋分': (9, 23), '寒露': (10, 8), '霜降': (10, 23),
            '立冬': (11, 7), '小雪': (11, 22), '大雪': (12, 7),
            '冬至': (12, 22), '小寒': (1, 6), '大寒': (1, 20)
        }
        
        # 优先使用sxtwl精确计算
        try:
            import sxtwl
            jq_list = sxtwl.getJieQiByYear(year)
            idx = self._jieqi_indices.get(term_name)
            if idx is not None and idx < len(jq_list):
                jd = jq_list[idx].jd
                dd = sxtwl.JD2DD(jd)
                result = date(int(dd.Y), int(dd.M), int(dd.D))
                self._solar_term_cache[cache_key] = result
                return result
        except ImportError:
            pass
        except Exception:
            pass
        
        # 回退：使用近似日期
        approx = _jieqi_approx.get(term_name)
        if approx:
            m, d = approx
            # 小寒和大寒属于上一年
            if term_name in ('小寒', '大寒'):
                result = date(year + 1, m, d)
            else:
                result = date(year, m, d)
            self._solar_term_cache[cache_key] = result
            return result
        
        # 最终回退
        return date(year, 2, 4)
    
    def _get_month_boundaries(self, year):
        """
        获取指定年份12个农历月的边界日期（以节气划分）
        
        传统择日以节气划分月份：
        寅月=立春至惊蛰, 卯月=惊蛰至清明, 辰月=清明至立夏, 以此类推
        
        Args:
            year: 年份
            
        Returns:
            list: 12个元素的列表，每个元素为该月的(起始日, 结束日, 节气月序号)
                  月序号: 1=寅月, 2=卯月, ..., 11=子月, 12=丑月
        """
        from datetime import date, timedelta
        
        # 获取当年12个月建节气
        term_dates = []
        for term_name in self._month_jieqi:
            td = self._get_solar_term_date(year, term_name)
            term_dates.append(td)
        
        # 获取下一年立春作为最后一个月的结束
        next_lichun = self._get_solar_term_date(year + 1, '立春')
        
        # 构建12个月份的边界
        # 注意：小寒(1月)属于上一年的最后一个月（丑月），
        # 但在本算法中我们将其作为当年12月的边界
        month_boundaries = []
        
        # 寅月: 立春 → 惊蛰
        # 卯月: 惊蛰 → 清明
        # 辰月: 清明 → 立夏
        # 巳月: 立夏 → 芒种
        # 午月: 芒种 → 小暑
        # 未月: 小暑 → 立秋
        # 申月: 立秋 → 白露
        # 酉月: 白露 → 寒露
        # 戌月: 寒露 → 立冬
        # 亥月: 立冬 → 大雪
        # 子月: 大雪 → 小寒
        # 丑月: 小寒 → 立春(次年)
        
        # term_dates 索引: 0=立春, 1=惊蛰, 2=清明, 3=立夏, 4=芒种, 5=小暑,
        #                  6=立秋, 7=白露, 8=寒露, 9=立冬, 10=大雪, 11=小寒
        
        for i in range(12):
            start = term_dates[i]
            if i < 11:
                end = term_dates[i + 1]
            else:
                end = next_lichun
            month_boundaries.append((start, end))
        
        return month_boundaries
    
    def _get_month_representative_date(self, year, month_order):
        """
        获取指定农历月的代表性日期（月中日期）
        
        Args:
            year: 年份
            month_order: 月序号（1=寅月, 2=卯月, ..., 12=丑月）
            
        Returns:
            datetime.date: 月中日期
        """
        from datetime import timedelta
        
        boundaries = self._get_month_boundaries(year)
        if 1 <= month_order <= 12:
            start, end = boundaries[month_order - 1]
            # 取中间日期作为代表
            mid = start + timedelta(days=(end - start).days // 2)
            return mid
        else:
            return self._get_solar_term_date(year, '立春') + timedelta(days=15)
    
    def _extract_bride_groom(self, owners):
        """
        从事主信息中提取新娘和新郎信息
        
        Args:
            owners: 事主信息列表
            
        Returns:
            tuple: (bride_bazi, groom_bazi)
        """
        bride_bazi = None
        groom_bazi = None
        
        if not owners:
            return bride_bazi, groom_bazi
        
        for owner in owners:
            role = owner.get('role', '').strip()
            gender = owner.get('性别', '').strip()
            
            # 提取新娘信息
            if role == '新娘' or gender == '女':
                bride_bazi = {}
                # 从sizhu字段提取年、月、日柱
                if 'sizhu' in owner:
                    sizhu_parts = owner['sizhu'].split()
                    if len(sizhu_parts) >= 1:
                        bride_bazi['year_gan'] = sizhu_parts[0][0]
                        bride_bazi['year_zhi'] = sizhu_parts[0][1]
                    if len(sizhu_parts) >= 2:
                        bride_bazi['yue_gan'] = sizhu_parts[1][0]
                        bride_bazi['yue_zhi'] = sizhu_parts[1][1]
                    if len(sizhu_parts) >= 3:
                        bride_bazi['ri_gan'] = sizhu_parts[2][0]
                        bride_bazi['ri_zhi'] = sizhu_parts[2][1]
                # 从birth_date计算完整四柱
                if 'birth_date' in owner:
                    try:
                        from .四柱计算器 import calculate_sizhu
                        birth_sizhu = calculate_sizhu(
                            owner['birth_date'],
                            owner.get('birth_hour', 12),
                            owner.get('birth_minute', 0),
                            longitude=owner.get('birth_longitude')
                        )
                        bride_bazi['year_gan'] = birth_sizhu['年柱'][0]
                        bride_bazi['year_zhi'] = birth_sizhu['年柱'][1]
                        bride_bazi['yue_gan'] = birth_sizhu['月柱'][0]
                        bride_bazi['yue_zhi'] = birth_sizhu['月柱'][1]
                        bride_bazi['ri_gan'] = birth_sizhu['日柱'][0]
                        bride_bazi['ri_zhi'] = birth_sizhu['日柱'][1]
                    except Exception as e:
                        logger.error(f"提取新娘八字失败: {e}")
            
            # 提取新郎信息
            if role == '新郎' or gender == '男':
                groom_bazi = {}
                if 'sizhu' in owner:
                    sizhu_parts = owner['sizhu'].split()
                    if len(sizhu_parts) >= 2:
                        groom_bazi['yue_gan'] = sizhu_parts[1][0]
                        groom_bazi['yue_zhi'] = sizhu_parts[1][1]
                    if len(sizhu_parts) >= 3:
                        groom_bazi['ri_gan'] = sizhu_parts[2][0]
                        groom_bazi['ri_zhi'] = sizhu_parts[2][1]
                if 'birth_date' in owner:
                    try:
                        from .四柱计算器 import calculate_sizhu
                        birth_sizhu = calculate_sizhu(
                            owner['birth_date'],
                            owner.get('birth_hour', 12),
                            owner.get('birth_minute', 0),
                            longitude=owner.get('birth_longitude')
                        )
                        groom_bazi['yue_gan'] = birth_sizhu['月柱'][0]
                        groom_bazi['yue_zhi'] = birth_sizhu['月柱'][1]
                        groom_bazi['ri_gan'] = birth_sizhu['日柱'][0]
                        groom_bazi['ri_zhi'] = birth_sizhu['日柱'][1]
                    except Exception as e:
                        logger.error(f"提取新郎八字失败: {e}")
        
        return bride_bazi, groom_bazi
    
    def score(self, sizhu, event_type, owners=None, house_type=None, shan_xiang=None,
              zaoxiang=None, zaowei=None, chuangwei=None, direction=None, jian_xiang=None,
              zaozhu_mode=None, zeli_mode='feixing'):  # _zm0915
        """
        计算评分

        架构说明：
        第一层（核心筛选）：正五行模块 - 这是系统的"否决权"模块
        第二层（优选排序）：大小黄道模块 - 这是系统的"加分项"
        第三层（深度优化）：月令对日主的帮助 - 正五行择日法的重要维度

        婚嫁专用：使用独立的婚嫁评分算法，结合正五行喜用神匹配

        Args:
            sizhu: 四柱信息
            event_type: 事项类型
            owners: 事主信息
            house_type: 宅型（阳宅/阴宅）
            shan_xiang: 山向
            zaoxiang: 灶向（作灶专用）
            zaowei: 灶位（作灶专用）
            chuangwei: 床位朝向（安床专用）
            jian_xiang: 兼向

        Returns:
            dict: 评分结果
        """
        try:
            # 重置评分状态（2026-09-02修复）：calculate_score复用模块级单例scorer，
            # 批量扫日时yi_list/ji_list/shensha_list等实例状态会跨日累积（规则检查"合并
            # 去重"把前一日三煞/阴府/封禁带入次日），导致后续日课被误判否决。每次评分
            # 从干净状态开始，等价于每次使用全新Scorer实例。
            self.base_score = 100
            self.final_score = 100
            self.level = ''
            self.shensha_list = []
            self.yi_list = []
            self.ji_list = []
            self.huangdao_info = {}
            # 三煞口径开关：True=四柱不犯（嫁娶等事主中心），False=仅坐山修方论
            # （修造等山向中心，四柱临方扣分不否决）。默认True走严口径，
            # 通用评分路径在 sansha_info 口径确定后立即覆写。
            self._pillar_veto_mode = True
            # _zm0915：择日模式 pure=纯正五行（协纪辨方书；玄空飞星/年家五黄二黑紫白封禁不参与），
            # feixing=正五行+玄空飞星（2026-09-15前的混合规则）。引擎默认 feixing 保持向后兼容，
            # 主程序按界面选择显式传值（界面默认 pure）。
            self._zeli_mode = zeli_mode if zeli_mode in ('pure', 'feixing') else 'feixing'
            # 事项评分画像统一从事项标准注册表读取（嫁娶路径/三煞口径/飞星/利月/作灶半权重）
            _prof = _event_profile(event_type)

            # 合并山向和兼向
            full_shan_xiang = shan_xiang
            if shan_xiang and jian_xiang and jian_xiang != '正中':
                full_shan_xiang = f"{shan_xiang}{jian_xiang}"
            
            # ========== 婚嫁专用评分 ==========
            if _prof['marriage']:
                # 从owners中提取新娘、新郎八字
                bride_bazi, groom_bazi = self._extract_bride_groom(owners)
                
                # 构建日期对象
                try:
                    from datetime import date
                    # 优先使用sizhu中的year字段（整数年份）
                    year_val = sizhu.get('year')
                    if year_val and isinstance(year_val, (int, str)):
                        year = int(year_val)
                    else:
                        # 如果没有year字段，尝试从年柱地支推断年份
                        year_zhi = sizhu.get('year_zhi', '')
                        if year_zhi:
                            # 地支循环为12年，使用固定的地支顺序来推断
                            from datetime import datetime
                            current_year = datetime.now().year
                            zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
                            # 已知2024年为甲辰年（辰），作为基准
                            base_year = 2024
                            base_zhi_index = zhi_order.index('辰')
                            if year_zhi in zhi_order:
                                target_zhi_index = zhi_order.index(year_zhi)
                                # 计算与基准年份相差的年数
                                diff = (target_zhi_index - base_zhi_index) % 12
                                year = base_year + diff
                        else:
                            year = None
                    
                    month_val = sizhu.get('month')
                    if month_val and isinstance(month_val, (int, str)):
                        month = int(month_val)
                    else:
                        month = 1
                    
                    day_val = sizhu.get('day')
                    if day_val and isinstance(day_val, (int, str)):
                        day = int(day_val)
                    else:
                        day = 1
                    
                    if year and month and day:
                        date_obj = date(year, month, day)
                    else:
                        date_obj = None
                except Exception as e:
                    logger.error(f"构建日期对象失败: {e}")
                    date_obj = None
                
                # 调用婚嫁评分算法
                try:
                    from .婚嫁评分算法 import score_marriage_day
                    
                    # 如果date_obj不为None且不是四柱输入模式，调用婚嫁评分算法
                    if date_obj and not sizhu.get('is_sizhu_input', False):
                        # 2026-09-09：婚嫁评分须用当前时柱的真实时辰排盘，而非默认午时(12)。
                        # 否则夫星受克等天干判定恒基于庚午时干，与系统推荐时柱（如壬申/乙丑）
                        # 脱钩，出现"金天干时柱庚克制木夫星"但实际时干为壬/乙的矛盾。
                        _ZHI2HOUR = {'子':0,'丑':2,'寅':4,'卯':6,'辰':8,'巳':10,
                                     '午':12,'未':14,'申':16,'酉':18,'戌':20,'亥':22}
                        _hour_gz = sizhu.get('时柱', '') or ''
                        _marriage_hour = _ZHI2HOUR.get(_hour_gz[1], 12) if len(_hour_gz) >= 2 else 12
                        marriage_result = score_marriage_day(date_obj, bride_bazi, groom_bazi,
                                                             hour=_marriage_hour)
                        
                        # 预先计算黄道信息（避免后续多个提前返回分支重复计算或遗漏）
                        self.huangdao_info = calculate_huangdao(sizhu)
                        
                        # 婚嫁硬性否决：日课日支冲事主日支（冲夫妻宫，婚嫁大忌）
                        cfz_veto_list = self._check_marriage_day_chong(sizhu, owners)

                        if marriage_result.get('reject_reason') or cfz_veto_list:
                            # 汇总否决原因（用于横幅/归零文案/综合评语明确显示）
                            veto_reasons = []
                            if marriage_result.get('reject_reason'):
                                veto_reasons.append(f"婚嫁大忌：{marriage_result['reject_reason']}（一票否决）")
                            veto_reasons.extend(cfz_veto_list)
                            # 即使有否决项，也要计算五行分析等详细信息
                            wu_xing_result = self._check_wu_xing(sizhu, event_type, owners,
                                                                  house_type, shan_xiang,
                                                                  zaoxiang, zaowei, chuangwei,
                                                                  direction=direction)
                            # 【D2 问题一修复】嫁娶事项的五行评分明细必须是嫁娶类（marriage_details），
                            # 不能同时渲染 _check_wu_xing 返回的修造类 score_breakdown（基础分100+
                            # 神煞/宜事/忌事/十二长生/地支/纳音），否则报告会出现两套基础分并存。
                            # 清空修造类明细，让主程序渲染时只走 marriage_details 分支。
                            if _prof['marriage']:
                                if isinstance(wu_xing_result, dict):
                                    wu_xing_result['score_breakdown'] = {}
                                    # 2026-09-17：五行评分与正常嫁娶路径同口径——
                                    # 即嫁娶专用评分（基础60＋利月/神煞/合局，否决日该分
                                    # 仅供追溯，总分仍强制归零），不用修造式 _check_wu_xing 分。
                                    wu_xing_result['score'] = marriage_result.get('score', 0)

                            # 计算基本评分详情
                            yueling_score = self._calculate_yueling_help(sizhu)
                            xishen_score = 0
                            owner_matches = []
                            if owners:
                                xishen_score, owner_matches = self._calculate_xishen_match(sizhu, owners)
                            # 【D5 问题四修复】嫁娶路径：黄道得分已并入嫁娶评分（marriage_details
                            # 中的大黄道/小黄道明细），score_details 不再单独列「黄道得分」项，
                            # 避免与嫁娶明细中的黄道扣分重复计算。与嫁娶正常路径口径一致。
                            huangdao_score = 0
                            # 太阳太阴得分
                            sun_moon_info = calculate_sun_moon_position(sizhu, shan_xiang)
                            sun_moon_score = sun_moon_info.get('score', 0)
                            # 相主得分
                            try:
                                xiangzhu_score, xiangzhu_details = self._check_owner_day_zhichong(sizhu, owners)
                            except Exception:
                                xiangzhu_score, xiangzhu_details = 0, []
                            
                            score_details = {
                                '五行评分': marriage_result.get('score', 0),
                                '五行原始分': marriage_result.get('raw_score', marriage_result.get('score', 0)),
                                '月令得分': yueling_score,
                                '喜用神得分': xishen_score,
                                # 【D5】嫁娶路径黄道已并入嫁娶评分，不单独列黄道得分键
                                # （主程序渲染时 has_hd_key=False → 显示"已并入五行评分"）
                                '太阳太阴得分': sun_moon_score,
                                '相主得分': xiangzhu_score,
                                '相主详情': xiangzhu_details,
                                '事主匹配': owner_matches,
                                '总分': 0,
                                '否决原因': veto_reasons,
                                '说明': '一票否决：' + '；'.join(veto_reasons) + '，得分=0，但各项扣分项已完整显示用于对比'
                            }
                            # 2026-09-17：否决日补齐月令旺衰/支支明细，与正常嫁娶路径
                            # （下方 score_details['月令详细']）同口径，避免月令得分无分项。
                            score_details['月令详细'] = {
                                '旺衰得分': self._calculate_wangxiang(sizhu),
                                '支支关系得分': self._calculate_zhizhi_relation(sizhu)
                            }

                            # 【D3 问题二修复】统一大利月分值：嫁娶神煞检查器(self.shensha_list)
                            # 中大利月是+20，婚嫁评分算法(marriage_details)中是+30。
                            # 嫁娶评分体系基础分60，大利月+30占半，统一为+30。
                            # 同时去重：self.shensha_list 中若已有大利月条目，更新分值；
                            # _check_wu_xing 内部又追加了一个+30大利月，需去重避免两条。
                            _li_yue_names = {'大利月', '小利月', '妨夫月', '妨妻月',
                                             '逐夫月', '逐妇月'}
                            _seen_li = set()
                            _dedup_shensha = []
                            for _s in self.shensha_list:
                                if isinstance(_s, dict) and _s.get('name') in _li_yue_names:
                                    _nm = _s.get('name')
                                    if _nm in _seen_li:
                                        continue  # 跳过重复利月条目
                                    _seen_li.add(_nm)
                                    if _nm == '大利月':
                                        _s = dict(_s)
                                        _s['score'] = 30
                                    elif _nm == '小利月':
                                        _s = dict(_s)
                                        _s['score'] = 15
                                _dedup_shensha.append(_s)
                            self.shensha_list = _dedup_shensha

                            # 【D4 问题三修复】把 marriage_details 中的嫁娶凶煞项
                            # （如夫星受克、逐夫月、逐妇月、孤辰寡宿等）加入 shensha_list，
                            # 使【神煞信息】与【评分详情】一致。
                            _mrg_details = marriage_result.get('details') or []
                            for _md in _mrg_details:
                                if isinstance(_md, (list, tuple)) and len(_md) >= 2:
                                    _mname = str(_md[0])
                                    _mscore = _md[1]
                                    # 只把扣分项（凶煞）加入神煞信息；基础分/大利月/月德等
                                    # 加分项已有对应条目，避免重复。
                                    try:
                                        _ms = int(_mscore)
                                    except (TypeError, ValueError):
                                        continue
                                    if _ms < 0:
                                        # 避免与已有同名条目重复
                                        _exists = any(
                                            isinstance(_x, dict) and _x.get('name') == _mname
                                            for _x in self.shensha_list
                                        )
                                        if not _exists:
                                            self.shensha_list.append({
                                                'name': _mname,
                                                'description': _mname,
                                                'score': _ms
                                            })
                            
                            # 生成综合评语（2026-09-17：与正常嫁娶路径同结构——
                            # 否决横幅/宜/忌为独立行 ＋ "月令分析："起的完整正五行 tail，
                            # 既保证否决日也有日主/合局/吉神等完整分析，又使主程序(5')
                            # 按权威时柱重算 tail 时能精确替换，不出现大段重复）
                            reason_parts = ['；'.join(veto_reasons)]
                            if self.yi_list:
                                reason_parts.append('宜：' + '、'.join(self.yi_list))
                            if self.ji_list:
                                reason_parts.append('忌：' + '、'.join(self.ji_list))

                            yueling_analysis = self._generate_yueling_analysis(sizhu)
                            _veto_tail = self._build_marriage_reason_tail(
                                wu_xing_result, yueling_analysis,
                                yueling_score, xishen_score, self.shensha_list,
                                marriage_details=marriage_result.get('details'),
                                veto_reason=marriage_result.get('reject_reason'))
                            if _veto_tail:
                                reason_parts.append(_veto_tail)

                            final_reason = '\n'.join(reason_parts)
                            if isinstance(wu_xing_result, dict):
                                wu_xing_result['ji_yu'] = final_reason
                            # 三煞信息（即使婚嫁否决日，也保留用于日课评分系统显示完整犯煞情况）
                            sansha_info = {}
                            try:
                                if shan_xiang:
                                    full_shan_xiang = self._get_full_shan_xiang(shan_xiang, jian_xiang)
                                    sansha_info = self._get_sansha_info(sizhu, full_shan_xiang)
                            except Exception:
                                sansha_info = {}
                            
                            # 忌列表：否决原因置首，保留评分用忌项（冲事主日柱、忌嫁娶等），确保宜忌信息完整透明
                            _reject_ji_list = []
                            if marriage_result.get('reject_reason'):
                                _reject_ji_list.append(marriage_result['reject_reason'])
                            for _j in self.ji_list:
                                if _j and _j not in _reject_ji_list:
                                    _reject_ji_list.append(_j)

                            return {
                                'score': 0,
                                'level': '❌ 凶',
                                'reason': final_reason,
                                'shensha_list': self.shensha_list,
                                'yi_list': self.yi_list,
                                'ji_list': _reject_ji_list,
                                'veto_reasons': veto_reasons,
                                'huangdao_info': self.huangdao_info,
                                'marriage_details': marriage_result.get('details', []),
                                'warnings': marriage_result.get('warnings', []),
                                'wu_xing_result': wu_xing_result,
                                'score_details': score_details,
                                'sun_moon_info': sun_moon_info,
                                'sizhu': sizhu,
                                'sansha_info': sansha_info,
                                'shan_xiang': shan_xiang
                            }
                        
                        # 计算正五行喜用神得分（作为补充）
                        xishen_score = 0
                        if owners:
                            xishen_score, _ = self._calculate_xishen_match(sizhu, owners)
                        
                        # 计算月令得分
                        yueling_score = self._calculate_yueling_help(sizhu)
                        
                        # 黄道信息已在婚嫁评分开始时预计算（见 self.huangdao_info = calculate_huangdao(sizhu)），此处无需重复

                        # 计算太阳太阴得分
                        sun_moon_info = calculate_sun_moon_position(sizhu, shan_xiang)
                        sun_moon_score = sun_moon_info.get('score', 0)

                        # 综合得分 = 婚嫁评分（含黄道得分）+ 喜用神得分 + 月令得分 + 太阳太阴得分
                        # 注意：黄道得分已包含在marriage_result['score']中，不再重复加
                        total_score = marriage_result['score'] + xishen_score + yueling_score + sun_moon_score

                        # 等级判定（2026-02-05 统一）：婚嫁与通用事项共用同一纯函数
                        # _get_level（依据2026-09-02用户确认：等级必须是总分的纯函数，
                        # 同分必须同级，阈值105/100/85/75/60）。
                        # 旧代码在此另立150/130/110/90/70婚嫁专用阈值，导致同一总分在
                        # "评分器初评"与"主程序注入时柱关系分后调_get_level重评"两处
                        # 给出不同等级（如98分既出★★次吉又出★★★吉），即"同分不同级"。
                        # 婚嫁路径的"五行评分"即嫁娶评分(marriage_result['score'])，
                        # 故五行<60直接判凶的质量底线同样适用。
                        level = self._get_level(
                            total_score,
                            {'score': marriage_result['score']},
                            self.huangdao_info
                        )

                        # 2026-09-15 婚嫁硬禁忌降级：若嫁娶评分明细含"忌嫁娶"项
                        # （如小黄道除/危/执日忌嫁娶），说明该日虽评分高但犯嫁娶硬性禁忌，
                        # 等级不得高于"★ 平"，并加注"犯忌嫁娶，慎用"，避免"上吉"与
                        # "忌嫁娶"并存的逻辑矛盾。
                        _mrg_details_for_level = marriage_result.get('details') or []
                        _has_ji_jiaqu_level = False
                        if isinstance(_mrg_details_for_level, list):
                            _has_ji_jiaqu_level = any(
                                '忌嫁娶' in str(_d[0])
                                for _d in _mrg_details_for_level
                                if isinstance(_d, (list, tuple)) and len(_d) >= 1
                            )
                        if _has_ji_jiaqu_level:
                            _level_order = ['❌ 凶', '★ 平', '★★ 中吉', '★★★ 吉', '★★★★ 大吉', '★★★★★ 上吉']
                            _cap = '★ 平'
                            try:
                                _cur_idx = _level_order.index(level)
                                _cap_idx = _level_order.index(_cap)
                                if _cur_idx > _cap_idx:
                                    level = _cap
                            except ValueError:
                                level = _cap
                            if '犯忌嫁娶' not in level:
                                level = level + '（犯忌嫁娶，慎用）'
                        # 记录是否因忌嫁娶被降级，供综合评语口径统一使用
                        _was_capped_for_jijiaqu = _has_ji_jiaqu_level

                        # 构建详细得分明细（2026-09-03 问题4：增加嫁娶分项+神煞明细占位，
                        # 保证"综合分=嫁娶评分+月令+喜用神+太阳太阴+神煞分项"公式可读）
                        # 注：大利月/小利月等神煞shensha_list在本块下方（# 检查大利月/小利月）
                        # 才实际填入，return前统一回填神煞汇总项。
                        score_details = {
                            '基础分': self.base_score,
                            '嫁娶评分': marriage_result['score'],
                            # 嫁娶路径的"五行评分"即嫁娶专用评分（基础60＋利月/天德/黄道/
                            # 三合等吉神、假三煞/夫星等凶煞，黄道已并入，不再单列）。
                            # 补此键使详情页【五行评分】行取到真实分，而非缺省回退100。
                            '五行评分': marriage_result['score'],
                            '五行原始分': marriage_result.get('raw_score', marriage_result['score']),
                            '月令得分': yueling_score,
                            '喜用神得分': xishen_score,
                            '太阳太阴得分': sun_moon_score,
                            '嫁娶明细(分项)': marriage_result.get('details', []),
                            '总分': total_score
                        }
                        
                        # 添加每个事主的详细匹配信息（包含喜用神名称）
                        if owners:
                            _, owner_matches = self._calculate_xishen_match(sizhu, owners)
                            if owner_matches:
                                score_details['事主匹配'] = owner_matches
                        
                        # 添加月令详细得分
                        wangxiang_score = self._calculate_wangxiang(sizhu)
                        zhizhi_score = self._calculate_zhizhi_relation(sizhu)
                        score_details['月令详细'] = {
                            '旺衰得分': wangxiang_score,
                            '支支关系得分': zhizhi_score
                        }
                        
                        # 生成五行分析详情（地支关系、吉神等）
                        wu_xing_details = self._generate_wu_xing_details(sizhu, owners)
                        wu_xing_result = {
                            'he_ge': True,
                            'score': marriage_result['score'],
                            'ji_yu': marriage_result['reason'],
                            'details': wu_xing_details,
                            'score_breakdown': {},
                            'has_deduction': False
                        }
                        
                        # 检查宜忌规则
                        rule_checker = get_rule_checker(event_type)
                        result = rule_checker.check(
                            sizhu, owners,
                            house_type=house_type,
                            shan_xiang=shan_xiang,
                            zaoxiang=zaoxiang,
                            zaowei=zaowei,
                            chuangwei=chuangwei,
                            direction=direction
                        )
                        # 处理返回值（支持新老两种格式）
                        if len(result) == 4:
                            self.yi_list, self.ji_list, veto, veto_reason = result
                            # 检查一票否决
                            if veto:
                                # 【E2 致命错误修复】规则否决时，score_details['总分']
                                # 必须归零，否则主程序优先取 score_details['总分']
                                # 会显示 94 分（而非一票否决的 0 分），与"强制归零"说明矛盾。
                                score_details['总分'] = 0
                                score_details['否决原因'] = [veto_reason] if veto_reason else []
                                score_details['说明'] = (
                                    '一票否决：' + (veto_reason or '') +
                                    '，得分=0，但各项扣分项已完整显示用于对比'
                                )

                                # 【E3 矛盾一/二修复】把 marriage_details 中的嫁娶凶煞项
                                # （假三煞、夫星受克、逐夫月、逐妇月、孤辰寡宿等）加入
                                # self.shensha_list，使【神煞信息】与【评分详情】一致。
                                _mrg_d = marriage_result.get('details') or []
                                for _md in _mrg_d:
                                    if isinstance(_md, (list, tuple)) and len(_md) >= 2:
                                        _mn = str(_md[0])
                                        try:
                                            _ms = int(_md[1])
                                        except (TypeError, ValueError):
                                            continue
                                        if _ms < 0:
                                            _exists = any(
                                                isinstance(_x, dict) and _x.get('name') == _mn
                                                for _x in self.shensha_list
                                            )
                                            if not _exists:
                                                self.shensha_list.append({
                                                    'name': _mn,
                                                    'description': _mn,
                                                    'score': _ms
                                                })

                                # 【E3 利月去重+分值统一】若 self.shensha_list 中有
                                # 利月条目（来自嫁娶神煞检查器），去重并统一大利月+30/小利月+15。
                                _li_names = {'大利月', '小利月', '妨夫月', '妨妻月',
                                             '逐夫月', '逐妇月'}
                                _seen = set()
                                _dedup = []
                                for _s in self.shensha_list:
                                    if isinstance(_s, dict) and _s.get('name') in _li_names:
                                        _nm = _s.get('name')
                                        if _nm in _seen:
                                            continue
                                        _seen.add(_nm)
                                        if _nm == '大利月':
                                            _s = dict(_s); _s['score'] = 30
                                        elif _nm == '小利月':
                                            _s = dict(_s); _s['score'] = 15
                                    _dedup.append(_s)
                                self.shensha_list = _dedup

                                return {
                                    'score': 0,
                                    'level': '❌ 凶',  # 添加缺失的level键
                                    'reason': veto_reason,
                                    # 2026-09-16：补齐 veto_reasons（与上方 reject_reason 分支口径一致）。
                                    # 旧实现缺此键，导致"否决数"按0计、报告横幅与排名降级判定
                                    # 读不到否决原因（凶而无因）。
                                    'veto_reasons': [veto_reason] if veto_reason else [],
                                    'shensha_list': self.shensha_list,
                                    'yi_list': self.yi_list,
                                    'ji_list': [veto_reason],
                                    'huangdao_info': self.huangdao_info,
                                    'wu_xing_result': wu_xing_result,
                                    'score_details': score_details,
                                    # 【E2 修复】补齐 marriage_details，让主程序渲染
                                    # 嫁娶评分分项明细（基础分/大利月/月德/黄道/夫星受克等），
                                    # 否则五行评分只显示"73分"无法追溯来源。
                                    'marriage_details': marriage_result.get('details', []),
                                    'sansha_info': {},
                                    'shan_xiang': shan_xiang
                                }
                        else:
                            self.yi_list, self.ji_list = result
                        
                        # _yj0915：婚嫁口径统一——若嫁娶评分明细含"忌嫁娶"项
                        # （如小黄道除/危/执日忌嫁娶），则从宜列表移除泛项"嫁娶"，
                        # 避免同一报告"宜：嫁娶"与"忌：小黄道除日忌嫁娶"并存矛盾。
                        _mrg_details = marriage_result.get('details') or []
                        if isinstance(_mrg_details, list):
                            _has_ji_jiaqu = any(
                                '忌嫁娶' in str(_d[0]) if isinstance(_d, (list, tuple)) and len(_d) >= 1 else False
                                for _d in _mrg_details
                            )
                            if _has_ji_jiaqu and '嫁娶' in self.yi_list:
                                self.yi_list.remove('嫁娶')

                        # 2026-10-02：小黄道"忌出行"补入嫁娶忌项
                        # 定日黄道信息已显示"宜嫁娶、立约，忌出行"，但【宜忌信息】
                        # 漏列"忌出行"；现补入 ji_list，与黄道描述口径一致。
                        _xo = (self.huangdao_info.get('xiao_huang_dao')
                               if isinstance(self.huangdao_info, dict) else {}) or {}
                        _xo_desc = _xo.get('description', '')
                        _xo_name = _xo.get('name', '')
                        if '忌出行' in _xo_desc and _xo_name:
                            _ji_travel = f'小黄道{_xo_name}日忌出行'
                            if _ji_travel not in self.ji_list:
                                self.ji_list.append(_ji_travel)

                        # 检查大利月/小利月
                        shensha_list = []
                        if owners:
                            for owner in owners:
                                if owner.get('role') == '新娘' or owner.get('性别') == '女':
                                    try:
                                        from .四柱计算器 import calculate_sizhu
                                        if 'birth_date' in owner:
                                            owner_sizhu = calculate_sizhu(owner['birth_date'],
                                                                         owner.get('birth_hour', 12),
                                                                         owner.get('birth_minute', 0),
                                                                         longitude=owner.get('birth_longitude'))
                                            bride_year_zhi = owner_sizhu.get('year_zhi', '')
                                            if bride_year_zhi:
                                                # 2026-09-03 利月一致性修复：以实际农历月份
                                                # （高精度农历）为判定依据，不再用节气月支法。
                                                # 避免腊月/正月交界日"寅月但农历腊月"被误判。
                                                lunar_month = self._resolve_lunar_month(sizhu)
                                                if lunar_month:
                                                    month_type = self._check_li_yue(bride_year_zhi, lunar_month)
                                                    if month_type == '大利月':
                                                        shensha_list.append({
                                                            'name': '大利月',
                                                            'description': f'新娘大利月（农历{lunar_month}月）',
                                                            'score': 30
                                                        })
                                                    elif month_type == '小利月':
                                                        shensha_list.append({
                                                            'name': '小利月',
                                                            'description': f'新娘小利月（农历{lunar_month}月）',
                                                            'score': 15
                                                        })
                                    except Exception as e:
                                        logger.error(f"检查利月失败: {e}")
                        
                        # 羊刃计分（冠带派）：婚嫁路径与通用事项同口径，单见-15/两见以上-25
                        _yr_mrg = self._build_yangren_shensha(sizhu, event_type)
                        if _yr_mrg:
                            shensha_list.append(_yr_mrg)

                        # 2026-10-02 修2：非veto分支同步回填 marriage_details 负分项
                        # （黄沙日/四废/八专/夫星受克等）进 shensha_list，使【神煞信息】
                        # 与【评分详情】口径一致——此前仅 veto 分支回填，非 veto 日
                        # "评分详情有黄沙-12、神煞信息却写无额外神煞加减分"。
                        # 按名称前缀去重（marriage_details 名带"（…）"括注，
                        # 如"羊刃（日干壬见…）"与上方'羊刃'条目视为同项）。
                        _mrg_d_nv = marriage_result.get('details') or []
                        for _md in _mrg_d_nv:
                            if isinstance(_md, (list, tuple)) and len(_md) >= 2:
                                _mn = str(_md[0])
                                try:
                                    _ms = int(_md[1])
                                except (TypeError, ValueError):
                                    continue
                                if _ms < 0:
                                    _mn_prefix = _mn.split('（')[0].split('(')[0].strip()
                                    _exists = any(
                                        isinstance(_x, dict) and
                                        str(_x.get('name', '')).split('（')[0].split('(')[0].strip() == _mn_prefix
                                        for _x in shensha_list
                                    )
                                    if not _exists:
                                        shensha_list.append({
                                            'name': _mn,
                                            'description': _mn,
                                            'score': _ms
                                        })
                        
                        # 生成综合评语（2026-09-03 问题4：格式化+分节，避免假三煞/月令混排）
                        # 结构：嫁娶评分要点 → 宜 → 忌 → 月令分析（独立小标题）
                        reason_parts = []
                        mrg_reason = str(marriage_result.get('reason') or '')
                        if mrg_reason:
                            # 把分号分隔的"条目串"保留为嫁娶小节首段（包含利月/天德/假三煞/
                            # 夫星等）。注意marriage_result里自带的"忌：xxx"会与宜/忌独立
                            # 段落形成小标题重复，这里改为"扣分：xxx"保留条目但去除"忌"标题。
                            mrg_reason = mrg_reason.replace('；忌：', '；扣分：').replace('；忌：', '；扣分：')
                            if mrg_reason.startswith('忌：'):
                                mrg_reason = '扣分：' + mrg_reason[2:]
                            reason_parts.append(f"嫁娶要点：{mrg_reason.rstrip('。；;')}")
                        if self.yi_list:
                            reason_parts.append('宜：' + '、'.join(self.yi_list))
                        # 综合评语的"忌"须与【宜忌信息】段同一口径：self.ji_list +
                        # marriage_details 负分项（如大黄道凶日、小黄道忌嫁娶等），
                        # 避免综合评语漏列核心禁忌。
                        _ji_for_reason = list(self.ji_list)
                        _mrg_details = marriage_result.get('details', [])
                        if isinstance(_mrg_details, list):
                            for _d in _mrg_details:
                                try:
                                    _nm, _sc = _d[0], _d[1]
                                except Exception:
                                    continue
                                if isinstance(_sc, (int, float)) and _sc < 0 and _nm not in _ji_for_reason:
                                    _ji_for_reason.append(_nm)
                        if _ji_for_reason:
                            reason_parts.append('忌：' + '、'.join(_ji_for_reason))
                        
                        # 月令分析 + 其后完整正五行分析串（日主/地支合局/命局吉神/月令/
                        # 喜用神/大黄道/小黄道/吉神/宜）。2026-09-17 应需求补全：原仅
                        # "月令分析"一句即止，致详情综合评语缺少日主、合局、吉神等段。
                        yueling_analysis = self._generate_yueling_analysis(sizhu)
                        _mrg_tail = self._build_marriage_reason_tail(
                            wu_xing_result, yueling_analysis,
                            yueling_score, xishen_score, shensha_list,
                            marriage_details=marriage_result.get('details'),
                            ji_jiaqu_capped=_was_capped_for_jijiaqu,
                            level_str=level)
                        if _mrg_tail:
                            reason_parts.append(_mrg_tail)
                        
                        final_reason = '\n'.join(reason_parts)
                        
                        # return前回填神煞汇总（shensha_list在利月检查块已填充），避免UnboundLocal
                        if 'shensha_list' not in locals() or not isinstance(shensha_list, list):
                            shensha_list = []
                        shensha_total = sum(
                            int(s.get('score', 0)) for s in shensha_list
                            if isinstance(s, dict) and isinstance(s.get('score'), (int, float))
                        )
                        score_details['神煞分项(利月/天德等)'] = shensha_total
                        score_details['神煞明细'] = [
                            (s.get('name'), int(s.get('score', 0)), s.get('description', ''))
                            for s in shensha_list if isinstance(s, dict)
                        ]
                        # 交叉引用：让正体五行分析段ji_yu与reason一致（同数据源）
                        if wu_xing_result and isinstance(wu_xing_result, dict):
                            wu_xing_result['ji_yu'] = final_reason
                        
                        return {
                            'score': total_score,
                            'level': level,
                            'reason': final_reason,
                            'shensha_list': shensha_list,
                            'yi_list': self.yi_list,
                            'ji_list': self.ji_list,
                            'huangdao_info': self.huangdao_info,
                            'marriage_details': marriage_result.get('details', []),
                            'warnings': marriage_result.get('warnings', []),
                            'xishen_score': xishen_score,
                            'marriage_score': marriage_result['score'],
                            'score_details': score_details,
                            'wu_xing_result': wu_xing_result,
                            'sun_moon_info': sun_moon_info,
                            'sizhu': sizhu,
                            'sansha_info': {},
                            'shan_xiang': shan_xiang
                        }
                    else:
                        # date_obj为None，无法进行婚嫁评分，继续执行通用评分逻辑
                        logger.warning("无法构建日期对象，跳过婚嫁评分算法")
                except ImportError:
                    logger.warning("婚嫁评分算法模块未找到，使用通用评分")
            
            # ========== 通用评分逻辑 ==========
            # 预先计算三煞信息（用于日课详情显示）
            self._current_event_type = event_type
            sansha_info = self._get_sansha_info(sizhu, full_shan_xiang)
            # 三煞判定口径（2026-09-07 用户确认）：
            #  山向中心事项（修造/动土/入宅/安葬等，以坐山修方为核心）用"仅坐山修方论"——
            #    坐山/修方犯三煞一票否决；四柱月/日/时支临三煞方可制化，仅扣分不否决。
            #  事主中心事项（嫁娶/订婚/纳采）沿用"四柱不犯"——月/日/时柱临三煞方皆否决。
            _mountain_centered = _prof['mountain_center']
            if _mountain_centered:
                sansha_info['sansha_pillar_veto'] = False
                self._pillar_veto_mode = False
                sansha_info['sansha_koujing'] = (
                    '仅坐山修方论：坐山/修方犯三煞否决；四柱月日时支临三煞方扣分不否决')
            else:
                sansha_info['sansha_pillar_veto'] = True
                self._pillar_veto_mode = True
                sansha_info['sansha_koujing'] = (
                    '四柱不犯：年日月时四柱临三煞方皆忌，犯即否决')
            
            # 三煞评分逻辑（根据避忌原则：年三煞最重，月三煞次之，日三煞又次之）
            total_sansha_penalty = 0
            total_sansha_detail = []  # 2026-09-10：三煞扣分构成明细（如年三煞犯时柱-20），供展示层对账
            
            # 年三煞检查（最重，月、日、时柱不可犯）
            if sansha_info.get('year_sansha_month_fan'):
                penalty = -30
                total_sansha_penalty += penalty
                total_sansha_detail.append('年三煞(月柱)（-30分）')
                self.final_score += penalty
                if '年三煞(月柱)' not in self.ji_list:
                    self.ji_list.append('年三煞(月柱)')
            if sansha_info.get('year_sansha_day_fan'):
                penalty = -30
                total_sansha_penalty += penalty
                total_sansha_detail.append('年三煞(日柱)（-30分）')
                self.final_score += penalty
                if '年三煞(日柱)' not in self.ji_list:
                    self.ji_list.append('年三煞(日柱)')
            if sansha_info.get('year_sansha_hour_fan'):
                penalty = -20
                total_sansha_penalty += penalty
                total_sansha_detail.append('年三煞(时柱)（-20分）')
                self.final_score += penalty
                if '年三煞(时柱)' not in self.ji_list:
                    self.ji_list.append('年三煞(时柱)')
            if sansha_info.get('year_sansha_fan'):
                penalty = -25
                total_sansha_penalty += penalty
                total_sansha_detail.append('年三煞(山向)（-25分）')
                self.final_score += penalty
                if '年三煞(山向)' not in self.ji_list:
                    self.ji_list.append('年三煞(山向)')
            
            # 月三煞检查（次之，日、时柱不可犯）
            if sansha_info.get('month_sansha_day_fan'):
                penalty = -20
                total_sansha_penalty += penalty
                total_sansha_detail.append('月三煞(日柱)（-20分）')
                self.final_score += penalty
                if '月三煞(日柱)' not in self.ji_list:
                    self.ji_list.append('月三煞(日柱)')
            if sansha_info.get('month_sansha_hour_fan'):
                penalty = -15
                total_sansha_penalty += penalty
                total_sansha_detail.append('月三煞(时柱)（-15分）')
                self.final_score += penalty
                if '月三煞(时柱)' not in self.ji_list:
                    self.ji_list.append('月三煞(时柱)')
            if sansha_info.get('month_sansha_fan'):
                penalty = -20
                total_sansha_penalty += penalty
                total_sansha_detail.append('月三煞(山向)（-20分）')
                self.final_score += penalty
                if '月三煞(山向)' not in self.ji_list:
                    self.ji_list.append('月三煞(山向)')
            
            # 日三煞检查（较轻，时柱不可犯）
            if sansha_info.get('day_sansha_hour_fan'):
                penalty = -10
                total_sansha_penalty += penalty
                total_sansha_detail.append('日三煞(时柱)（-10分）')
                self.final_score += penalty
                if '日三煞(时柱)' not in self.ji_list:
                    self.ji_list.append('日三煞(时柱)')
            if sansha_info.get('day_sansha_fan'):
                penalty = -15
                total_sansha_penalty += penalty
                total_sansha_detail.append('日三煞(山向)（-15分）')
                self.final_score += penalty
                if '日三煞(山向)' not in self.ji_list:
                    self.ji_list.append('日三煞(山向)')

            # 月、日三煞同时犯时柱（2026-09-02用户确认）：双重煞叠加，扣分加重
            # 例：月犯时-15 + 日犯时-10 + 叠加-15 = -40
            if sansha_info.get('month_sansha_hour_fan') and sansha_info.get('day_sansha_hour_fan'):
                penalty = -15
                total_sansha_penalty += penalty
                self.final_score += penalty
                total_sansha_detail.append('月日三煞叠犯(时柱)（-15分）')
                if '月日三煞叠犯(时柱)' not in self.ji_list:
                    self.ji_list.append('月日三煞叠犯(时柱)')
            
            sansha_info['sansha_penalty'] = total_sansha_penalty
            sansha_info['sansha_penalty_detail'] = total_sansha_detail
            
            # 山家专业检查结果处理（来自二十四山择吉天机模块）
            if sansha_info.get('mountain_blocked'):
                blocked_reasons = sansha_info.get('mountain_block_reasons', [])
                for reason in blocked_reasons:
                    if reason not in self.ji_list:
                        self.ji_list.append(reason)
                    self.final_score -= 15
                    total_sansha_penalty -= 15
                    total_sansha_detail.append('山家封禁：%s（-15分）' % reason)  # _fc0915
                sansha_info['sansha_penalty'] = total_sansha_penalty  # _fc0915：封禁扣分回写，penalty须==明细合计
                sansha_info['sansha_penalty_detail'] = total_sansha_detail
            if sansha_info.get('mountain_warnings'):
                for warning in sansha_info.get('mountain_warnings', []):
                    warn_text = warning if isinstance(warning, str) else warning.get('说明', str(warning))
                    if warn_text and warn_text not in self.ji_list:
                        # 克山运去重：修造规则路径已报则跳过，避免重复计忌
                        if '克山运' in warn_text and any('克山运' in j for j in self.ji_list):
                            continue
                        self.ji_list.append(warn_text)
                        # 无制化条件凶煞（时灾煞/时曜煞等）独立扣分，与"日三煞(时柱)"同级
                        if '（无制化）' in warn_text:
                            self.final_score -= 10
                            total_sansha_penalty -= 10
                            total_sansha_detail.append('%s（-10分）' % warn_text)
                            sansha_info['sansha_penalty'] = total_sansha_penalty
                            sansha_info['sansha_penalty_detail'] = total_sansha_detail
            
            # 吉神加分（来自山家检查）
            mountain_jishen = sansha_info.get('mountain_jishen', [])
            if mountain_jishen:
                for js in mountain_jishen:
                    if isinstance(js, str) and js not in self.yi_list:
                        self.yi_list.append(js)
                    self.final_score += 5
            
            # 添加日类信息
            day_type = sansha_info.get('mountain_day_type', '')
            if day_type and day_type != '普通日':
                sansha_info['day_type'] = day_type
            
            # 第一步：正五行审核（核心门槛）
            wu_xing_result = self._check_wu_xing(sizhu, event_type, owners,
                                                    house_type, shan_xiang,
                                                    zaoxiang, zaowei, chuangwei,
                                                    direction=direction,
                                                    zaozhu_mode=zaozhu_mode)

            # 如果五行不合格（犯三杀、冲山等大忌），直接返回"❌ 凶"
            # 2026-09-03 用户放宽：若score≥30且所有"硬否决类"凶煞均已被吉神制化（忌项
            # 中带"（有制化：…）"标记），则不降否决、按正常加减分走（有制化不否决）。
            # 不可制化硬煞（Layer1）关键词：年三煞/月三煞/岁煞/岁破/日破/五黄到坐山/
            # 二黑到坐山/双干正阴府禁用/克山运（无制化）/乙庚合化金克木大凶/正体大凶。
            if not wu_xing_result['he_ge']:
                _wx_sc = int(wu_xing_result.get('score') or 0)
                if _wx_sc >= 30:
                    # 2026-09-11 fix: 山向中心事项按"仅坐山修方论"，三煞临年月日时柱
                    # 仅扣分不否决（sansha_pillar_veto=False），"年三煞(日柱)"等四柱
                    # 忌项不得当作未制化硬煞卡住放宽闸门——须与下方综合评定 _spv 口径、
                    # 二十四山窗口"临三煞方扣分不否决"文案三处一致。
                    _spv_mode = sansha_info.get('sansha_pillar_veto', True)
                    _hard_hit = [j for j in self.ji_list
                                 if any(re.search(_k, str(j))
                                        for _k in self._HARD_VETO_KEYWORDS)
                                 and not (_spv_mode is False
                                          and self._is_pillar_sansha_item(j))]
                    _hard_need = [j for j in _hard_hit if '（有制化：' not in str(j)]
                    _mountain_bad = [str(b) for b in sansha_info.get('mountain_block_reasons', [])
                                     if isinstance(b, (str, dict))]
                    _mountain_need = [j for j in _mountain_bad if '（有制化：' not in str(j)]
                    if not _hard_need and not _mountain_need:
                        # 豁免：所有硬凶煞均已被制化或不存在，作为合格继续走正常加权流程
                        wu_xing_result['he_ge'] = True
                        wu_xing_result['_he_ge_note'] = (
                            f"放宽合格：原得分{_wx_sc}未达60分，硬凶煞项全部带制化标记"
                            f"或属四柱临方扣分不否决项，按正常加减分走，不否决"
                            f"（未制化项={len(self.ji_list)-len(_hard_hit)}）"
                        )
                        # 在评语末尾补上制化说明
                        _orig = wu_xing_result.get('ji_yu', '')
                        if _orig.startswith('五行严重不合格'):
                            wu_xing_result['ji_yu'] = (
                                f"五行基本合格（原得分{_wx_sc}，硬煞项均被吉神制化"
                                f"或属四柱临方扣分项，已放宽）"
                            )
                    else:
                        # 仍判否决：用真实硬否决项重写评语，禁止把"扣分不否决/有制化"
                        # 项写成大忌（否则与三煞检查、山家警告文案自相矛盾）。
                        _real_hard = list(_hard_need) + [
                            j for j in _mountain_need if j not in _hard_need]
                        _shown = '、'.join(str(x) for x in _real_hard[:3])
                        if len(_real_hard) > 3:
                            _shown += '等'
                        wu_xing_result['ji_yu'] = (
                            f'五行严重不合格，犯大忌，坚决不用（大忌：{_shown}）')
                # 仍不合格 → 一票否决（保持严格模式）
            if not wu_xing_result['he_ge']:
                # 计算完整评分详情（保持严格模式，但显示各项得分，让用户对比大凶日扣分来源）
                yueling_score = self._calculate_yueling_help(sizhu)
                xishen_score, owner_matches = self._calculate_xishen_match(sizhu, owners)
                
                # 计算黄道得分（即使一票否决，也显示详情）
                self.huangdao_info = calculate_huangdao(sizhu)
                huangdao_score = self.huangdao_info.get('huang_dao_score', 0)
                
                # 计算太阳太阴得分
                sun_moon_info = calculate_sun_moon_position(sizhu, shan_xiang)
                sun_moon_score = sun_moon_info.get('score', 0)
                
                # 计算相主得分
                try:
                    xiangzhu_score, xiangzhu_details = self._check_owner_day_zhichong(sizhu, owners)
                except Exception:
                    xiangzhu_score, xiangzhu_details = 0, []
                
                # 计算神煞得分
                shensha_score = sum(s.get('score', 0) for s in self.shensha_list if isinstance(s, dict))
                
                # 构建完整的评分详情（6 分项与正常日的计算公式保持一致）
                score_details = {
                    '基础分': self.base_score,
                    '五行评分': wu_xing_result.get('score', 0),
                    '月令得分': yueling_score,
                    '喜用神得分': xishen_score,
                    '黄道得分': huangdao_score,
                    '太阳太阴得分': sun_moon_score,
                    '相主得分': xiangzhu_score,
                    '相主详情': xiangzhu_details,
                    '事主匹配': owner_matches,
                    '神煞得分': shensha_score,
                    '总分': 0,  # 一票否决，总分仍为0，但6分项显示完整
                    '说明': '一票否决：正五行门槛未通过（三杀/冲山等大忌），总分强制=0，但各项扣分项完整显示用于对比'
                }
                # 补齐与正常日一致的明细键，确保否决日详情弹窗可完整追溯评分过程
                try:
                    score_details['三煞扣分'] = sansha_info.get('sansha_penalty', 0)
                    score_details['三煞扣分明细'] = sansha_info.get('sansha_penalty_detail', [])
                    score_details['月令详细'] = {
                        '旺衰得分': self._calculate_wangxiang(sizhu),
                        '支支关系得分': self._calculate_zhizhi_relation(sizhu),
                    }
                    _hs, _hl = self._calc_hour_zhi_relations_detail(sizhu)
                    score_details['时柱关系得分'] = _hs
                    score_details['时柱关系明细'] = _hl
                except Exception:
                    pass
                
                # _fc0915：相主硬门槛（自刑/六冲）同步进忌列表，与正常路径口径一致
                for _xz_h in xiangzhu_details:
                    if str(_xz_h).startswith('[硬性门槛]'):
                        _xz_t = str(_xz_h).replace('[硬性门槛]', '')
                        if _xz_t not in self.ji_list:
                            self.ji_list.append(_xz_t)

                # 生成综合评语（包含月令分析）
                reason_parts = [wu_xing_result['ji_yu']]
                if self.yi_list:
                    reason_parts.append('宜：' + '、'.join(self.yi_list))
                if self.ji_list:
                    reason_parts.append('忌：' + '、'.join(self.ji_list))
                
                # 添加月令分析
                yueling_analysis = self._generate_yueling_analysis(sizhu)
                if yueling_analysis:
                    reason_parts.append(f'月令：{yueling_analysis}')
                
                final_reason = '；'.join(reason_parts)
                
                return {
                    'score': 0,
                    'level': '❌ 凶',
                    'reason': final_reason,
                    'shensha_list': self.shensha_list,
                    'yi_list': self.yi_list,
                    'ji_list': self.ji_list,
                    'veto_reasons': [wu_xing_result['ji_yu']] + [
                        str(_d).replace('[硬性门槛]', '').replace('，不可用', '')
                        + '（相主硬门槛，一票否决）'
                        for _d in xiangzhu_details
                        if str(_d).startswith('[硬性门槛]')],  # _fc0915
                    'huangdao_info': self.huangdao_info,
                    'wu_xing_result': wu_xing_result,
                    'score_details': score_details,
                    'sun_moon_info': sun_moon_info,
                    'sizhu': sizhu,
                    'sansha_info': sansha_info,
                    'shan_xiang': shan_xiang
                }

            # 第二步：月令对日主的帮助评分
            yueling_score = self._calculate_yueling_help(sizhu)

            # 第三步：日课五行与事主喜用神匹配评分（正五行择日法核心）
            xishen_score, owner_matches = self._calculate_xishen_match(sizhu, owners)

            # 计算相主得分（日课日支与事主生肖/日支的关系）
            xiangzhu_score, xiangzhu_details = self._check_owner_day_zhichong(sizhu, owners)
            # 仙命信息提前构建（三级判定 + 返回块共用）
            wangming_info = self._build_wangming_info(owners)

            # 仙命×坐山纳音生克（第二阶段 2.1，2026-10-04 拍板）：
            # 仅安葬路径（有亡命卡）且有山向时启用；兼向复用主山五行。
            shanzuo_eval = None
            if wangming_info and shan_xiang:
                _zuoshan = str(shan_xiang)[0] if str(shan_xiang) else ''
                _sz_info = None
                if _zuoshan:
                    try:
                        from .二十四山 import get_mountain_info
                    except ImportError:
                        from 二十四山 import get_mountain_info
                    _sz_info = get_mountain_info(_zuoshan)
                _sz_wx = (_sz_info or {}).get('wuxing', '')
                if _sz_wx:
                    shanzuo_eval = evaluate_wangming_vs_shanzuo(
                        wangming_info.get('五行', ''), _sz_wx)
                    shanzuo_eval['坐山'] = _zuoshan
                    shanzuo_eval['坐山五行'] = _sz_wx
            shanzuo_score = (shanzuo_eval or {}).get('score', 0)

            # 相主硬性门槛：命主年支/日支与日课日支六冲或自刑 → 一票否决
            xiangzhu_veto_items = [str(d) for d in xiangzhu_details if str(d).startswith('[硬性门槛]')]

            # 流年冲太岁提示加入忌列表
            for _d in xiangzhu_details:
                if str(_d).startswith('[流年冲太岁]'):
                    _t = str(_d).replace('[流年冲太岁]', '')
                    if _t not in self.ji_list:
                        self.ji_list.append(_t)

            # 第四步：大小黄道审核（加分/减分项）
            self.huangdao_info = calculate_huangdao(sizhu)
            huangdao_score = self.huangdao_info.get('huang_dao_score', 0)

            # 第五步：太阳太阴到山到向分析
            sun_moon_info = calculate_sun_moon_position(sizhu, shan_xiang)
            sun_moon_score = sun_moon_info.get('score', 0)

            # 计算最终得分：五行评分已经包含了神煞得分，不需要再重复加
            # 五行评分 = 基础分 + 神煞得分 + 宜事得分 + 忌事得分 + 十二长生得分 + 地支关系得分 + 纳音匹配得分
            # 所以最终得分 = 五行评分 + 月令得分 + 喜用神得分 + 相主得分 + 黄道得分 + 太阳太阴得分 + 三煞扣分
            self.final_score = wu_xing_result['score'] + yueling_score + xishen_score + xiangzhu_score + huangdao_score + sun_moon_score + sansha_info.get('sansha_penalty', 0) + shanzuo_score

            # 不设置分数上限，显示实际计算的总分

            # 第五步：综合评定（优先检查三煞大忌与相主硬门槛）
            # 根据择日学原则，犯三煞属于一票否决项
            sansha_fan_da_ji = False
            sansha_fan_reason = ''
            # 三煞口径开关：True=四柱不犯（嫁娶），False=仅坐山修方论（山向类）
            _spv = sansha_info.get('sansha_pillar_veto', True)

            # 年三煞犯日柱（大忌；山向类按仅坐山论，日柱临方扣分不否决）
            if sansha_info.get('year_sansha_day_fan') and _spv:
                sansha_fan_da_ji = True
                sansha_fan_reason = '年三煞(日柱)'
            
            # 年三煞犯山向（大忌）
            if sansha_info.get('year_sansha_fan'):
                sansha_fan_da_ji = True
                if sansha_fan_reason:
                    sansha_fan_reason += '、年三煞(山向)'
                else:
                    sansha_fan_reason = '年三煞(山向)'
            
            # 月三煞犯山向（大忌）
            if sansha_info.get('month_sansha_fan'):
                sansha_fan_da_ji = True
                if sansha_fan_reason:
                    sansha_fan_reason += '、月三煞(山向)'
                else:
                    sansha_fan_reason = '月三煞(山向)'
            
            # 日三煞犯山向（较轻，不列为大忌）
            # 根据三煞避忌原则：日三煞管时柱，山向犯日三煞相对较轻，不一票否决
            
            # 年三煞犯月柱（大忌；山向类按仅坐山论，月柱临方扣分不否决）
            if sansha_info.get('year_sansha_month_fan') and _spv:
                sansha_fan_da_ji = True
                if sansha_fan_reason:
                    sansha_fan_reason += '、年三煞(月柱)'
                else:
                    sansha_fan_reason = '年三煞(月柱)'

            # 年三煞犯时柱（嫁娶等事主中心事项大忌，犯即否决；
            # 修造/动土/入宅/安葬等山向中心事项按"仅坐山修方论"，时支临三煞方
            # 如午年丑时临亥子丑方，坐山不犯即不否决，仅按三煞扣分制化）
            if sansha_info.get('year_sansha_hour_fan') and _spv:
                sansha_fan_da_ji = True
                if sansha_fan_reason:
                    sansha_fan_reason += '、年三煞(时柱)'
                else:
                    sansha_fan_reason = '年三煞(时柱)'

            # 硬性否决原因（供显示层明确提示，避免只显示模糊门槛文案）
            veto_reasons = []
            if sansha_fan_da_ji:
                veto_reasons.append(f"三煞大忌：{sansha_fan_reason}（一票否决）")
            for _v in xiangzhu_veto_items:
                veto_reasons.append(_v.replace('[硬性门槛]', '').replace('，不可用', '') + '（相主硬门槛，一票否决）')
            # 山家封禁一票否决（2026-09-01用户确认）：坐山犯五黄/二黑等绝对禁忌，
            # 与三煞大忌/相主硬门槛/岁破日/分金大凶并列，触发时综合评分强制归零、等级❌凶，
            # 避免"山家封禁·绝对不能用"与"★★★★★上吉"并存的逻辑矛盾
            if sansha_info.get('mountain_blocked'):
                _block_reasons = sansha_info.get('mountain_block_reasons', [])
                _block_text = '；'.join(str(r) for r in _block_reasons) if _block_reasons else '坐山犯五黄，宜静不宜动'
                veto_reasons.append(f"山家封禁：{_block_text}（一票否决）")

            # 仙命真冲三级判定（2026-10-04 用户验收补档，显式 VETO）：
            # 基础 -30（相主通道）
            #   ├─ 叠三煞/岁破/月破（日破）→ 直接否决（有制化也不救）
            #   ├─ 无宽集化解吉神 → 一票否决
            #   └─ 有宽集化解吉神（天德/月德/岁德/太阳到山/天赦/天愿/三合/六合）
            #      → 仅扣分（WARN），并在真冲行标注"有制化：…"
            wangming_veto = ''
            _wm_gz = wangming_info.get('年柱', '') if wangming_info else ''
            _day_zhi = sizhu.get('day_zhi', '')
            _zc_hit = bool(_wm_gz) and self.check_liuchong(_day_zhi, _wm_gz[1])
            _zc_heavy = self._check_veto_overlay(sansha_info) if _zc_hit else []
            _zc_resolvers = []
            if _zc_hit:
                if _zc_heavy:
                    wangming_veto = (
                        f"仙命真冲叠大忌：亡命{wangming_info['name']}年命{_wm_gz[1]}与日支{_day_zhi}相冲，"
                        f"叠{'/'.join(_zc_heavy)}，大忌不用（一票否决）")
                else:
                    _zc_resolvers = self._detect_wm_resolvers(wu_xing_result, sun_moon_info)
                    if _zc_resolvers:
                        # 有制化：仅扣分；在真冲明细行补注（防止用户误判为裸冲）
                        _tag = f"（有制化：{'、'.join(_zc_resolvers)}）"
                        for _i, _line in enumerate(xiangzhu_details):
                            if '真冲' in str(_line) and '有制化' not in str(_line):
                                xiangzhu_details[_i] = str(_line) + _tag
                    else:
                        wangming_veto = (
                            f"仙命真冲无制化：亡命{wangming_info['name']}年命{_wm_gz[1]}与日支{_day_zhi}相冲，"
                            f"四柱无天德/月德/岁德/太阳到山/天赦/天愿/三合/六合等吉神制化，"
                            f"大忌不用（一票否决）")

            # 仙命×坐山纳音三级判定（第二阶段 2.1）：
            #   坐山克仙命（地克人/地不容此命）= 凶中之凶，复用同套叠忌/化解检查
            #     叠重煞 → 直接否决；无化解吉神 → 一票否决；有吉神 → WARN
            #   其余 4 档（坐山生/仙命生/比和/仙命克）仅影响总分，不单独否决
            shanzuo_veto = ''
            _sz_hit = bool(shanzuo_eval) and shanzuo_eval.get('relation') == '坐山克仙命'
            _sz_heavy = self._check_veto_overlay(sansha_info) if _sz_hit else []
            _sz_resolvers = []
            if _sz_hit:
                if _sz_heavy:
                    shanzuo_veto = (
                        f"坐山克仙命叠大忌：坐山{shanzuo_eval['坐山']}五行属"
                        f"{shanzuo_eval['坐山五行']}，克亡命{wangming_info['name']}"
                        f"纳音{wangming_info['纳音']}（{wangming_info['五行']}），"
                        f"地不容此命，叠{'/'.join(_sz_heavy)}，大忌不用（一票否决）")
                else:
                    _sz_resolvers = self._detect_wm_resolvers(wu_xing_result, sun_moon_info)
                    if _sz_resolvers:
                        # 有制化：坐山克仙命仅扣分；标注"有制化：…"
                        shanzuo_eval['_with_huajie'] = True
                        shanzuo_eval['reason'] += f"（有制化：{'、'.join(_sz_resolvers)}）"
                    else:
                        shanzuo_veto = (
                            f"坐山克仙命无制化：坐山{shanzuo_eval['坐山']}五行属"
                            f"{shanzuo_eval['坐山五行']}，克亡命{wangming_info['name']}"
                            f"纳音{wangming_info['纳音']}（{wangming_info['五行']}），"
                            f"地不容此命，四柱无天德/月德/岁德/太阳到山/天赦/天愿/"
                            f"三合/六合等吉神制化，大忌不用（一票否决）")

            # 仙命双凶叠加强制否决（2026-10-04 §59.10 用户拍板）：
            #   日支真冲 + 坐山克仙命同日命中 → 强制 VETO，
            #   即使两边都各有制化也 VETO；文案明示两凶 + 各自制化状态。
            #   单凶时维持各自三级判定不变。
            dual_veto = ''
            if _zc_hit and _sz_hit:
                dual_veto = self._build_wm_dual_veto_text(
                    wangming_info, shanzuo_eval, _day_zhi,
                    _zc_heavy, _zc_resolvers, _sz_heavy, _sz_resolvers)
                veto_reasons.append(dual_veto)
            else:
                if wangming_veto:
                    veto_reasons.append(wangming_veto)
                if shanzuo_veto:
                    veto_reasons.append(shanzuo_veto)

            if (sansha_fan_da_ji or xiangzhu_veto_items
                    or sansha_info.get('mountain_blocked')
                    or wangming_veto or shanzuo_veto or dual_veto):
                self.level = '❌ 凶'
                self.final_score = 0
                # 将三煞犯忌添加到ji_list
                if sansha_info.get('year_sansha_month_fan') and '年三煞(月柱)' not in self.ji_list:
                    self.ji_list.append('年三煞(月柱)')
                if sansha_info.get('year_sansha_day_fan') and '年三煞(日柱)' not in self.ji_list:
                    self.ji_list.append('年三煞(日柱)')
                if sansha_info.get('year_sansha_hour_fan') and '年三煞(时柱)' not in self.ji_list:
                    self.ji_list.append('年三煞(时柱)')
                if sansha_info.get('year_sansha_fan') and '年三煞(山向)' not in self.ji_list:
                    self.ji_list.append('年三煞(山向)')
                if sansha_info.get('month_sansha_day_fan') and '月三煞(日柱)' not in self.ji_list:
                    self.ji_list.append('月三煞(日柱)')
                if sansha_info.get('month_sansha_hour_fan') and '月三煞(时柱)' not in self.ji_list:
                    self.ji_list.append('月三煞(时柱)')
                if sansha_info.get('month_sansha_fan') and '月三煞(山向)' not in self.ji_list:
                    self.ji_list.append('月三煞(山向)')
                if sansha_info.get('day_sansha_hour_fan') and '日三煞(时柱)' not in self.ji_list:
                    self.ji_list.append('日三煞(时柱)')
                if sansha_info.get('day_sansha_fan') and '日三煞(山向)' not in self.ji_list:
                    self.ji_list.append('日三煞(山向)')
                # 相主硬门槛（命主年支/日支与日课日支六冲、自刑）加入忌列表
                for _v in xiangzhu_veto_items:
                    _v_text = _v.replace('[硬性门槛]', '')
                    if _v_text not in self.ji_list:
                        self.ji_list.append(_v_text)
            else:
                self.level = self._get_level(self.final_score, wu_xing_result, self.huangdao_info, shanzuo_eval)

            # 构建详细得分明细
            # 注意：神煞得分已包含在五行评分中，不需要单独列出
            score_details = {
                '基础分': self.base_score,
                '五行评分': wu_xing_result['score'],
                '月令得分': yueling_score,
                '喜用神得分': xishen_score,
                '相主得分': xiangzhu_score,
                '黄道得分': huangdao_score,
                '太阳太阴得分': sun_moon_score,
                '三煞扣分': sansha_info.get('sansha_penalty', 0),
                '三煞扣分明细': sansha_info.get('sansha_penalty_detail', []),
                '总分': self.final_score
            }

            # 添加每个事主的详细匹配信息
            if owner_matches:
                score_details['事主匹配'] = owner_matches

            # 添加相主详情
            if xiangzhu_details:
                score_details['相主详情'] = xiangzhu_details

            # 仙命×坐山纳音生克（第二阶段 2.1）
            if shanzuo_eval:
                score_details['仙命坐山得分'] = shanzuo_score
                score_details['仙命坐山详情'] = shanzuo_eval.get('reason', '')

            # 添加月令详细得分
            wangxiang_score = self._calculate_wangxiang(sizhu)
            zhizhi_score = self._calculate_zhizhi_relation(sizhu)
            score_details['月令详细'] = {
                '旺衰得分': wangxiang_score,
                '支支关系得分': zhizhi_score
            }

            # 时柱地支关系得分/明细（评分器单一数据源，规则同 _calculate_zhizhi_relations；
            # 分数已含于五行评分·地支关系得分，此处仅拆出给展示层读取，主程序不再自算）
            try:
                _hs, _hl = self._calc_hour_zhi_relations_detail(sizhu)
                score_details['时柱关系得分'] = _hs
                score_details['时柱关系明细'] = _hl
            except Exception:
                pass

            # ========== 玄空飞星加减分（2026-09-01 用户确认）==========
            # 仅修造/安葬类事项参与飞星，非否决课
            # 方案B加权：综合分 = 正五行×0.7 + (50+飞星)×0.3
            # 2026-09-16 事项口径统一：飞星事项集合由事项标准注册表提供
            feixing_info = None
            if self._zeli_mode == 'feixing' and _prof['feixing'] and not veto_reasons and full_shan_xiang:  # _zm0915
                feixing_info = self._calculate_feixing_score(sizhu, full_shan_xiang)
                if feixing_info:
                    fx = feixing_info['feixing_score']  # -20~+20
                    _zhengwu = self.final_score  # 加权前的正五行总分
                    _feixing_mapped = 50 + fx  # 映射到30~70区间
                    self.final_score = max(0, min(100, int(_zhengwu * 0.7 + _feixing_mapped * 0.3)))
                    self.level = self._get_level(self.final_score, wu_xing_result, self.huangdao_info, shanzuo_eval)
                    score_details['飞星评分'] = fx
                    score_details['飞星等级'] = feixing_info['feixing_level']
                    score_details['飞星详情'] = feixing_info['feixing_details']
                    score_details['正五行总分'] = _zhengwu  # 加权前的正五行总分
                    score_details['总分'] = self.final_score  # 更新为加权后的综合总分

                    # 飞星大凶一票否决（2026-09-02用户确认）：月五黄/二黑到坐山致
                    # 飞星等级"大凶"或断语含"切忌"（如"五黄到山，切忌动土修造"）时，
                    # 修造择日以山家为核心，直接否决，与分金大凶否决口径一致
                    if (feixing_info.get('feixing_level') == '大凶'
                            or '切忌' in str(feixing_info.get('feixing_comment', ''))):
                        _fx_reason = (
                            f"玄空飞星大忌：{feixing_info.get('feixing_comment', '飞星大凶')}"
                            f"（飞星{fx}分，一票否决）")
                        if _fx_reason not in veto_reasons:
                            veto_reasons.append(_fx_reason)
                        if _fx_reason not in self.ji_list:
                            self.ji_list.append(_fx_reason)
                        self.final_score = 0
                        self.level = '❌ 凶'
                        score_details['总分'] = 0

            return {
                'score': self.final_score,
                'level': self.level,
                'reason': self._generate_reason(wu_xing_result, self.huangdao_info, yueling_score, xishen_score, owner_matches, sun_moon_info, wangming_info, shanzuo_eval),
                'wangming_info': wangming_info,
                'shanzuo_eval': shanzuo_eval,
                'shensha_list': self.shensha_list,
                'yi_list': self.yi_list,
                'ji_list': self.ji_list,
                'veto_reasons': veto_reasons,
                'huangdao_info': self.huangdao_info,
                'wu_xing_result': wu_xing_result,
                'score_details': score_details,
                'sun_moon_info': sun_moon_info,
                'sizhu': sizhu,
                'sansha_info': sansha_info,  # 添加三煞信息
                'shan_xiang': shan_xiang,  # 添加山向信息
                'feixing_info': feixing_info  # 玄空飞星评分信息
            }

        except Exception as e:
            import traceback
            import os
            tb_text = traceback.format_exc()
            # ==========================================================
            #  生成"人读友好的异常定位摘要"（用于横幅/一票否决/综合评语，不翻 logs 也能看）
            #  示例：[AttributeError] 评分器.py(1451)->analyze_month(): 'str' object has no attribute 'year'
            # ==========================================================
            try:
                exc_type = type(e).__name__
                tb_list = traceback.extract_tb(e.__traceback__)
                # 取最末端（抛出点）的那一帧作为定位
                last_frame = tb_list[-1] if tb_list else None
                if last_frame:
                    file_name = os.path.basename(last_frame.filename)
                    locator = f"[{exc_type}] {file_name}({last_frame.lineno})->{last_frame.name}(): {str(e)}"
                else:
                    locator = f"[{exc_type}] {str(e)}"
            except Exception:
                locator = f"[{type(e).__name__}] {str(e)}"

            error_msg = f"评分计算异常: {locator}\n{tb_text}"
            print(error_msg)

            # ======================================================
            #  异常兜底：尽量保留已计算出的中间数据，方便用户定位
            #  （用户截图看到"❌ 计算错误"但仍带五行/月令/喜用神/黄道分 = 需要这里保留之前计算的 score_details）
            # ======================================================
            def _safe(v, fallback):
                try:
                    if v is None:
                        return fallback
                    return v
                except Exception:
                    return fallback

            # 保留已计算的 score_details（否则显示全为默认值 100/0/0/0，用户以为没扣分，与实际计算不一致）
            fallback_score_details = locals().get('score_details') or {}
            if not isinstance(fallback_score_details, dict):
                fallback_score_details = {}
            fallback_score_details = dict(fallback_score_details)  # copy 防污染
            fallback_score_details['异常信息'] = locator
            fallback_score_details['异常堆栈(前8行)'] = tb_text.splitlines()[-8:]

            # 保留已经算出的 wu_xing_result（如果没有，就新建一个带异常说明的，显示在日课详情一票否决区）
            fallback_wx = locals().get('wu_xing_result') or {}
            if not isinstance(fallback_wx, dict):
                fallback_wx = {}
            fallback_wx = dict(fallback_wx)
            fallback_wx['he_ge'] = False
            fallback_wx['ji_yu'] = f"计算错误: {locator}"
            fallback_wx.setdefault('score', fallback_score_details.get('五行评分', 0))
            fallback_wx.setdefault('details', {})
            if isinstance(fallback_wx['details'], dict):
                fallback_wx['details']['异常'] = tb_text.splitlines()[-10:]

            fallback_shensha = _safe(locals().get('shensha_list') or getattr(self, 'shensha_list', None), [])
            fallback_yi = _safe(locals().get('yi_list') or getattr(self, 'yi_list', None), [])
            fallback_ji = _safe(locals().get('ji_list') or getattr(self, 'ji_list', None), [])
            fallback_hd = _safe(locals().get('huangdao_info') or getattr(self, 'huangdao_info', None), {})
            fallback_sm = _safe(locals().get('sun_moon_info'), {})
            fallback_ss = _safe(locals().get('sansha_info'), {})
            # 综合评语末尾也追加完整异常定位 + 前8行堆栈，让用户贴截图就能看出是哪一步炸
            try:
                tb_head8 = "\n    ".join(tb_text.splitlines()[-8:])
            except Exception:
                tb_head8 = ""
            fallback_reason = (
                f"评分计算异常: {locator}\n"
                f"【异常堆栈(末8行)】\n    {tb_head8}"
            )

            # 补全五行/月令/喜用神/黄道 四分项兜底（让日课列表里的"❌ 计算错误"行也能看到各扣分项怎么来）
            try:
                if '月令得分' not in fallback_score_details:
                    yls = locals().get('yueling_score')
                    if isinstance(yls, (int, float)):
                        fallback_score_details['月令得分'] = yls
                    else:
                        try:
                            fallback_score_details['月令得分'] = self._calculate_yueling_help(sizhu)
                        except Exception:
                            pass
                if '喜用神得分' not in fallback_score_details and owners:
                    xss = locals().get('xishen_score')
                    if isinstance(xss, (int, float)):
                        fallback_score_details['喜用神得分'] = xss
                    else:
                        try:
                            xs, _ = self._calculate_xishen_match(sizhu, owners)
                            fallback_score_details['喜用神得分'] = xs
                        except Exception:
                            pass
                if '黄道得分' not in fallback_score_details:
                    hds = locals().get('huangdao_score')
                    if isinstance(hds, (int, float)):
                        fallback_score_details['黄道得分'] = hds
                    elif isinstance(fallback_hd, dict):
                        fallback_score_details['黄道得分'] = fallback_hd.get('huang_dao_score', 0)
                if '五行评分' not in fallback_score_details and isinstance(fallback_wx, dict):
                    fallback_score_details['五行评分'] = fallback_wx.get('score', 100)
            except Exception:
                pass

            # 持久化闪退日志（与日课评分系统入口脚本日志目录一致），便于用户事后反馈异常堆栈
            try:
                LOG_DIR = os.path.join((getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable))) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
                os.makedirs(LOG_DIR, exist_ok=True)
                crash_log = os.path.join(LOG_DIR, '评分器_异常日志.log')
                with open(crash_log, 'a', encoding='utf-8') as f:
                    from datetime import datetime as _dt
                    f.write(f"\n\n===== {_dt.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n")
                    f.write(f"事项: {event_type}\n")
                    f.write(f"四柱: {sizhu}\n")
                    f.write(f"山向: {shan_xiang}\n")
                    f.write(f"事主数量: {len(owners) if owners else 0}\n")
                    f.write(error_msg)
                    f.write("\n")
            except Exception:
                pass

            # 返回错误结果而不是崩溃
            return {
                'score': 0,
                'level': '❌ 计算错误',
                'reason': fallback_reason,
                'shensha_list': fallback_shensha,
                'yi_list': fallback_yi,
                'ji_list': fallback_ji,
                'huangdao_info': fallback_hd if isinstance(fallback_hd, dict) else {},
                'wu_xing_result': fallback_wx,
                'score_details': fallback_score_details,
                'sun_moon_info': fallback_sm if isinstance(fallback_sm, dict) else {},
                'error': error_msg,
                'sansha_info': fallback_ss if isinstance(fallback_ss, dict) else {},
                'shan_xiang': shan_xiang,
                'sizhu': sizhu,
            }

    def _get_year_month_feixing_at_mountain(self, year, year_zhi, month_zhi, mountain):
        """
        计算年/月飞星在坐山宫位的星曜（用于年/月分析预判五黄二黑到山）。
        与 _calculate_feixing_score 年/月盘口径一致。
        Returns: (year_star_at_mountain, month_star_at_mountain) 或 None
        """
        try:
            try:
                from .玄空飞星引擎 import compute_stars, MOUNTAIN_TO_INDEX, DIZHI
            except ImportError:
                from 玄空飞星引擎 import compute_stars, MOUNTAIN_TO_INDEX, DIZHI
            if mountain not in MOUNTAIN_TO_INDEX:
                return None
            idx = MOUNTAIN_TO_INDEX[mountain]
            # 日/时盘此处不用（日、时支传空），仅取年/月盘坐山宫星
            grids = compute_stars(int(year), year_zhi, month_zhi, '', '', None)
            y_star = grids['year']['grid'][idx]
            m_star = grids['month']['grid'][idx] if (month_zhi and month_zhi in DIZHI) else None
            return (y_star, m_star)
        except Exception:
            return None

    def analyze_year(self, year, event_type, owners=None, shan_xiang=None, jian_xiang=None, direction=None, zeli_mode='feixing', year_pillar_override=None):  # _zm0915
        """
        分析年份吉凶

        Args:
            year: 年份（如2026）
            event_type: 事项类型
            owners: 事主信息
            shan_xiang: 山向信息
            jian_xiang: 兼向信息
            direction: 动土方位
            year_pillar_override: 两字年柱（如'乙巳'）。按整数年分析时内部取
                立春后年柱代表全年（2026→丙午）；但分析具体日课（尤其立春前）时，
                流年必须以实际日课年柱为准，由调用方传入覆盖（2026-10-04 仙命
                冲太岁验收整改：否则子命在乙巳年残课会被误判为冲丙午太岁）。

        Returns:
            dict: 年份分析结果
        """
        from datetime import date, timedelta
        
        # 构建年份的代表性日期（使用精确立春日期）
        # 中国传统干支纪年以立春为分界点，使用立春后第一天确保在立春之后
        lichun_date = self._get_solar_term_date(year, '立春')
        if lichun_date:
            test_date = lichun_date + timedelta(days=1)
        else:
            test_date = date(year, 3, 1)  # 回退方案
        
        # 计算该年的干支
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
        sizhu = calculate_sizhu(test_date, 12, 0)
        year_gan = sizhu.get('year_gan', '')
        year_zhi = sizhu.get('year_zhi', '')
        # 具体日课：以实际年柱覆盖代表年柱（见函数 docstring）
        if year_pillar_override and len(str(year_pillar_override)) >= 2:
            year_gan = str(year_pillar_override)[0]
            year_zhi = str(year_pillar_override)[1]
        
        # 分析结果
        analysis = {
            'year': year,
            'year_gz': f"{year_gan}{year_zhi}",
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'suitable': True,
            'score': 100,
            'level': '吉',
            'reasons': [],
            'details': {},
            '_chong_penalty': 0,  # 2026-09-18：年命×流年支六冲扣分（扣分不否决档），
                                 # 不计入末尾 suitable 兜底阈值
        }
        
        # 如果有兼向，合并山向和兼向
        full_shan_xiang = shan_xiang
        if shan_xiang and jian_xiang and jian_xiang != '正中':
            # 兼向已经包含"兼"字，直接拼接
            full_shan_xiang = f"{shan_xiang}{jian_xiang}"
        
        # 检查太岁与事主的关系
        if owners:
            for owner in owners:
                if 'birth_date' in owner:
                    owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                               owner.get('birth_hour', 12), 
                                               owner.get('birth_minute', 0),
                                               longitude=owner.get('birth_longitude'))
                    owner_year_zhi = owner_sizhu.get('year_zhi', '')

                    # 亡命（仙命）流年关系（2026-10-04 用户补授权，分两档）：
                    #   六冲（仙命冲流年太岁）= 岁破级，直接否决；
                    #   破/刑/害/合 = 【第一阶段临时降级】为提示（不扣分不否决），
                    #     第二阶段仙命口径统一时重新核定；叠加重煞的否决由本函数后续
                    #     独立通道（三煞占方等）保证，不因提示漏网。
                    if _is_wangming_role(owner.get('role', '')):
                        if self.check_liuchong(year_zhi, owner_year_zhi):
                            analysis['suitable'] = False
                            analysis['level'] = '大凶'
                            analysis['score'] = 0
                            analysis['reasons'].append(
                                f"亡命（仙命）{owner['name']}年命{owner_year_zhi}冲流年太岁{year_zhi}"
                                f"（岁破级大忌，一票否决）")
                            return analysis
                        _wm_tip = ''
                        if self.check_po(year_zhi, owner_year_zhi): _wm_tip = '相破'
                        elif self.check_xing(year_zhi, owner_year_zhi): _wm_tip = '相刑'
                        elif self.check_hai(year_zhi, owner_year_zhi): _wm_tip = '相害'
                        elif self.check_liuhe(year_zhi, owner_year_zhi): _wm_tip = '六合'
                        elif self.check_sanhe([year_zhi, owner_year_zhi]): _wm_tip = '三合'
                        if _wm_tip:
                            # 害独立降档为"轻微提示"（害<破<刑<冲，P0-2 口径修正）
                            _tip_head = ('轻微提示' if _wm_tip == '相害' else '提示')
                            analysis.setdefault('info_reasons', []).append(
                                f"{_tip_head}（第一阶段临时降级，第二阶段重估）：流年与亡命（仙命）"
                                f"{owner['name']}年命{owner_year_zhi}{_wm_tip}")
                        continue

                    # 2026-09 作灶主事人模式：辅助者（半权重）年命六冲不降否决，冲刑破害/合化半权重
                    _zz_w = owner.get('_zaozhu_weight', None)
                    _zz_aux = _event_profile(event_type)['zaozhu_half'] and _zz_w is not None and float(_zz_w) < 1.0
                    _zz_suf = '（辅助·半权重）' if _zz_aux else ''
                    # 2026-09-18 用户拍板年命六冲三档口径：
                    #   年命×日课日支六冲 = 硬否决；年命×日课年/月/时支六冲 = 扣分不否决；
                    #   辰午酉亥自刑 = 一票否决。此处是【年支（流年/冲太岁）】档，
                    #   不再把整年判 suitable=False 整列剔除，仅扣分提示；日课总分层
                    #   另有 _check_owner_day_zhichong 的"流年冲太岁"-15 计入相主分。
                    if self.check_liuchong(year_zhi, owner_year_zhi):
                        _cp = _zaozhu_weighted(-30, 0.5 if _zz_aux else 1.0)
                        analysis['score'] += _cp
                        analysis['_chong_penalty'] += _cp  # 扣分不否决档，隔离兜底阈值
                        analysis['reasons'].append(
                            f"与{owner['name']}年命六冲（冲太岁年，扣分不否决）" + ('（辅助，半权重）' if _zz_aux else ''))
                    elif self.check_po(year_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(-20, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"与{owner['name']}年命相破{_zz_suf}")
                    elif self.check_xing(year_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(-15, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"与{owner['name']}年命相刑{_zz_suf}")
                    elif self.check_hai(year_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(-10, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"与{owner['name']}年命相害{_zz_suf}")
                    elif self.check_liuhe(year_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(20, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"与{owner['name']}年命六合{_zz_suf}")
                    elif self.check_sanhe([year_zhi, owner_year_zhi]):
                        analysis['score'] += _zaozhu_weighted(15, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"与{owner['name']}年命三合{_zz_suf}")
        
        # 对于修造类事项，分析年煞和二十四山方位吉凶（仅提供信息，不扣分）
        if _event_profile(event_type)['year_month_shan']:
            # 年三煞分析（纯地支，符合三合局规则）
            year_sansha_map = {
                '申': ['巳', '午', '未'], '子': ['巳', '午', '未'], '辰': ['巳', '午', '未'],
                '寅': ['亥', '子', '丑'], '午': ['亥', '子', '丑'], '戌': ['亥', '子', '丑'],
                '巳': ['寅', '卯', '辰'], '酉': ['寅', '卯', '辰'], '丑': ['寅', '卯', '辰'],
                '亥': ['申', '酉', '戌'], '卯': ['申', '酉', '戌'], '未': ['申', '酉', '戌']
            }

            sansha_fang = year_sansha_map.get(year_zhi, [])
            if sansha_fang:
                # 仅提供信息，不扣分
                analysis.setdefault('info_reasons', []).append(f"年三煞在{''.join(sansha_fang)}方（忌修造）")  # 纯信息项：方位未临坐山/动土方不构成否决
                analysis['details']['年三煞'] = sansha_fang

                # 如果提供了山向，分析山向与年煞的关系
                if full_shan_xiang:
                    # 提取山向中的所有方向信息（包括兼向）
                    shan_xiang_dirs = [full_shan_xiang[0]]
                    if '兼' in full_shan_xiang:
                        jian_index = full_shan_xiang.find('兼')
                        if jian_index + 1 < len(full_shan_xiang):
                            shan_xiang_dirs.append(full_shan_xiang[jian_index + 1])
                    
                    # 检查所有方向是否在煞方
                    for shan_xiang_dir in shan_xiang_dirs:
                        if shan_xiang_dir in sansha_fang:
                            analysis['reasons'].append(f"所选山向{full_shan_xiang}犯年三煞，不利修造")
                            analysis['details']['山向犯煞'] = True
                            analysis['suitable'] = False
                            analysis['score'] = 0
                            analysis['level'] = '大凶'
                            break

                # 如果提供了动土方位，检查动土方位是否在煞方
                if direction:
                    # direction可能是完整字符串，需要提取主要方向
                    direction_dir = direction[0] if direction else direction
                    if direction_dir in sansha_fang:
                        analysis['reasons'].append(f"动土方位{direction}犯年三煞，不利修造")
                        analysis['details']['动土犯煞'] = True
                        analysis['suitable'] = False
                        analysis['score'] = 0
                        analysis['level'] = '大凶'

            # 太岁方位
            zhi_fang = {
                '子': '子', '丑': '丑', '寅': '寅', '卯': '卯',
                '辰': '辰', '巳': '巳', '午': '午', '未': '未',
                '申': '申', '酉': '酉', '戌': '戌', '亥': '亥'
            }
            taisui_fang = zhi_fang.get(year_zhi, '')
            if taisui_fang:
                analysis.setdefault('info_reasons', []).append(f"太岁在{taisui_fang}方（忌动土）")  # 纯信息项：太岁可坐不可向，仅向首/动土方临太岁才否决
                analysis['details']['太岁'] = taisui_fang

                # 如果提供了山向，按"太岁可坐不可向"规则分析山向与太岁的关系
                if full_shan_xiang:
                    # 解析坐山、向首（"向"字前一字）、坐方兼针（"兼"字后一字，须为有效二十四山字符）
                    zuoshan = full_shan_xiang[0] if full_shan_xiang else ''
                    xiangshou = ''
                    if '向' in full_shan_xiang and full_shan_xiang.find('向') > 0:
                        xiangshou = full_shan_xiang[full_shan_xiang.find('向') - 1]
                    jian_zhi = ''
                    if '兼' in full_shan_xiang:
                        jian_index = full_shan_xiang.find('兼')
                        if jian_index + 1 < len(full_shan_xiang):
                            jian_char = full_shan_xiang[jian_index + 1]
                            # 兼左/兼右不含具体山名，忽略
                            if jian_char in '子癸丑艮寅甲卯乙辰巽巳丙午丁未坤申庚酉辛戌乾亥壬':
                                jian_zhi = jian_char

                    # 太岁可坐：坐山或坐方兼针临太岁方，可用不扣分
                    if zuoshan == taisui_fang or (jian_zhi and jian_zhi == taisui_fang):
                        analysis['reasons'].append(f"坐山{zuoshan}临太岁{taisui_fang}方，太岁可坐不可向，坐之可用")
                        analysis['details']['坐太岁'] = True

                    # 太岁不可向：向首正对太岁方为大忌
                    if xiangshou == taisui_fang:
                        analysis['reasons'].append(f"所选山向{full_shan_xiang}向首正对太岁{taisui_fang}方，太岁可坐不可向，大忌")
                        analysis['details']['向首犯太岁'] = True
                        analysis['suitable'] = False
                        analysis['score'] = 0
                        analysis['level'] = '大凶'

                # 如果提供了动土方位，检查动土方位是否犯太岁
                if direction:
                    direction_dir = direction[0] if direction else direction
                    if direction_dir == taisui_fang:
                        analysis['reasons'].append(f"动土方位{direction}犯太岁，不利动土")
                        analysis['details']['动土犯太岁'] = True
                        analysis['suitable'] = False
                        analysis['score'] = 0
                        analysis['level'] = '大凶'

            # 岁破方位
            chong_zhi = {
                '子': '午', '午': '子',
                '丑': '未', '未': '丑',
                '寅': '申', '申': '寅',
                '卯': '酉', '酉': '卯',
                '辰': '戌', '戌': '辰',
                '巳': '亥', '亥': '巳'
            }
            suipo_fang = chong_zhi.get(year_zhi, '')
            if suipo_fang:
                # 仅提供信息，不扣分
                analysis.setdefault('info_reasons', []).append(f"岁破在{suipo_fang}方（忌修造）")  # 纯信息项：方位未临坐山/动土方不构成否决
                analysis['details']['岁破'] = suipo_fang

                # 如果提供了山向，分析山向与岁破的关系
                if full_shan_xiang:
                    # 提取山向中的所有方向信息（包括兼向）
                    shan_xiang_dirs = [full_shan_xiang[0]]
                    if '兼' in full_shan_xiang:
                        jian_index = full_shan_xiang.find('兼')
                        if jian_index + 1 < len(full_shan_xiang):
                            shan_xiang_dirs.append(full_shan_xiang[jian_index + 1])
                    
                    # 检查所有方向是否犯岁破
                    for shan_xiang_dir in shan_xiang_dirs:
                        if shan_xiang_dir == suipo_fang:
                            analysis['reasons'].append(f"所选山向{full_shan_xiang}犯岁破，不利修造")
                            analysis['details']['山向犯岁破'] = True
                            analysis['suitable'] = False
                            analysis['score'] = 0
                            analysis['level'] = '大凶'
                            break

                # 如果提供了动土方位，检查动土方位是否犯岁破
                if direction:
                    direction_dir = direction[0] if direction else direction
                    if direction_dir == suipo_fang:
                        analysis['reasons'].append(f"动土方位{direction}犯岁破，不利修造")
                        analysis['details']['动土犯岁破'] = True
                        analysis['suitable'] = False
                        analysis['score'] = 0
                        analysis['level'] = '大凶'
        
        # 玄空飞星年盘：五黄/二黑到坐山（年级因素，整年固定）
        # 与逐日择日"五黄到山一票否决"口径一致，避免月份分析吉而整日被飞星否决
        if zeli_mode == 'feixing' and _event_profile(event_type)['feixing'] and full_shan_xiang:  # _zm0915
            _mtn = None
            for _m in ['壬','子','癸','丑','艮','寅','甲','卯','乙','辰','巽','巳',
                       '丙','午','丁','未','坤','申','庚','酉','辛','戌','乾','亥']:
                if full_shan_xiang.startswith(_m):
                    _mtn = _m; break
            if _mtn:
                _fx = self._get_year_month_feixing_at_mountain(year, year_zhi, None, _mtn)
                if _fx:
                    _y_star = _fx[0]
                    if _y_star == 5:
                        analysis['reasons'].append(f"年家五黄到坐山{_mtn}，整年忌修造动土")
                        analysis['details']['年五黄到山'] = True
                        analysis['suitable'] = False
                        analysis['score'] = 0
                        analysis['level'] = '大凶'
                    elif _y_star == 2:
                        analysis['reasons'].append(f"年家二黑到坐山{_mtn}，多病破财，修造慎之")
                        analysis['details']['年二黑到山'] = True
                        analysis['score'] = max(0, analysis['score'] - 20)
                        if analysis['score'] < 50:
                            analysis['level'] = '大凶'
                            analysis['suitable'] = False

        # 如果没有特殊原因，添加基本信息
        if not analysis['reasons']:
            if owners:
                analysis['reasons'].append("年份平和，无冲克")
            else:
                analysis['reasons'].append("未提供事主信息，无法判断")
        
        # 确定等级
        # 基础分为70分，月破扣25分后为45分（凶），无煞加20分后为90分（吉）
        if analysis['score'] >= 90:
            analysis['level'] = '吉'
        elif analysis['score'] >= 70:
            analysis['level'] = '平'
        elif analysis['score'] >= 50:
            analysis['level'] = '小凶'
        else:
            analysis['level'] = '大凶'
            # 2026-09-18 三档口径：若 <50 纯粹由"年命×流年支六冲（扣分不否决）"
            # 造成（剔除该档后回到 50+），不转 suitable=False；山向犯煞/太岁/岁破/
            # 五黄/二黑等硬项均已在上方显式置 suitable=False，不受影响。
            _score_excl_chong = analysis['score'] - analysis.get('_chong_penalty', 0)
            if _score_excl_chong < 50:
                analysis['suitable'] = False
        analysis.pop('_chong_penalty', None)

        return analysis

    def analyze_month(self, test_date, event_type, owners=None, shan_xiang=None, direction=None, day_sizhu=None, zeli_mode='feixing'):  # _zm0915
        """
        分析月份吉凶

        Args:
            test_date: 日期对象（datetime.date），表示该农历月份的代表性日期
            event_type: 事项类型
            owners: 事主信息
            shan_xiang: 山向信息
            direction: 动土方位

        Returns:
            dict: 月份分析结果
        """
        from datetime import date, timedelta
        
        # 先导入 calculate_sizhu
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
        
        # 计算该月的干支（使用传入的日期）
        sizhu = calculate_sizhu(test_date, 12, 0)
        month_gan = sizhu.get('month_gan', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        year_gz = sizhu.get('年柱', '')
        
        # 从四柱中提取农历年份（干支纪年）
        # 注意：不能使用 test_date.year，因为农历腊月可能对应公历下一年
        # 需要从年柱干支反推年份
        TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 从年柱干支计算农历年份（year_gz 可能是字符串如"丙午"，也可能是其他类型）
        year_gz_str = str(year_gz) if year_gz else ''
        if year_gz_str and len(year_gz_str) >= 2:
            gan_idx = TIANGAN.index(year_gz_str[0]) if year_gz_str[0] in TIANGAN else 0
            zhi_idx = DIZHI.index(year_gz_str[1]) if year_gz_str[1] in DIZHI else 0
            # 干支纪年每 60 年一循环，找到最近的匹配年份
            base_year = test_date.year
            for offset in range(60):
                check_year = base_year - offset
                if (check_year - 4) % 10 == gan_idx and (check_year - 4) % 12 == zhi_idx:
                    year = check_year
                    break
            else:
                year = base_year  #  fallback
        else:
            year = test_date.year  # fallback
        
        # 首先检查年份是否适合，如果年份不适合，则月份也不适合
        year_analysis = self.analyze_year(
            year, event_type, owners, shan_xiang, direction=direction,
            zeli_mode=zeli_mode,
            year_pillar_override=((day_sizhu or {}).get('year_gan', '')
                                  + (day_sizhu or {}).get('year_zhi', '')) or None)  # _zm0915
        # 使用 .get() 方法安全访问，确保所有必要键都存在
        if not year_analysis.get('suitable', True):
            # 如果年份不适合，直接返回年份分析结果（作为月份分析结果）
            analysis = year_analysis.copy()
            analysis['month'] = test_date.month
            analysis['month_gz'] = ''
            analysis['month_gan'] = ''
            analysis['month_zhi'] = ''
            analysis['level'] = year_analysis.get('level', '大凶')  # 确保level键存在
            analysis['reasons'] = [f"年份{year}不适合{event_type}，该年所有月份均不宜"] + year_analysis.get('reasons', [])
            return analysis
        
        # 分析结果
        # 基础分 70 分，这样月破扣 25 分后为 45 分，判为凶
        analysis = {
            'year': year,
            'month': test_date.month,  # 使用日期的月份
            'month_gz': f"{month_gan}{month_zhi}",
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'suitable': True,
            'score': 70,
            'level': '凶',
            'reasons': [],
            'details': {},
            '_chong_penalty': 0,  # 2026-09-18：年命×月支六冲扣分（扣分不否决档），
                                 # 不计入末尾 suitable 兜底阈值
        }

        # 继承年份分析的关键结论（坐太岁可用、年三煞、太岁方、岁破方等方位煞忌信息），
        # 使月度报告完整呈现年、月两层判断
        year_details = year_analysis.get('details') or {}
        for _key in ('年三煞', '太岁', '岁破', '坐太岁'):
            if _key in year_details:
                analysis['details'][_key] = year_details[_key]
        _ya_info = set(year_analysis.get('info_reasons') or [])
        _year_notes = [r for r in year_analysis.get('reasons', [])
                       if r not in _ya_info and any(k in str(r) for k in ('太岁', '三煞', '岁破'))]
        if _year_notes:
            year_gz_label = year_analysis.get('year_gz') or str(year)
            analysis['reasons'] = [f"年份{year_gz_label}：{r}" for r in _year_notes] + analysis['reasons']

        # 检查月破（月支与日支相冲）
        # 这里使用该月1日的日支作为参考
        day_zhi = sizhu.get('day_zhi', '')
        if self.check_liuchong(month_zhi, day_zhi):
            analysis['score'] -= 15
            analysis['reasons'].append('月破')
            # 月破后调整为凶
            if analysis['score'] < 50:
                analysis['level'] = '大凶'
            elif analysis['score'] < 70:
                analysis['level'] = '小凶'
        
        # 检查月刑
        if self.check_xing(month_zhi, year_zhi):
            analysis['score'] -= 8
            analysis['reasons'].append('月刑')
        
        # 检查月害
        if self.check_hai(month_zhi, year_zhi):
            analysis['score'] -= 5
            analysis['reasons'].append('月害')
        
        # 检查月份与事主生肖的关系
        if owners:
            for owner in owners:
                if 'birth_date' in owner:
                    owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                               owner.get('birth_hour', 12), 
                                               owner.get('birth_minute', 0),
                                               longitude=owner.get('birth_longitude'))
                    owner_year_zhi = owner_sizhu.get('year_zhi', '')

                    # 亡命（仙命）月支关系：【第一阶段临时降级】为提示（不扣分、不否决），
                    # 第二阶段仙命口径统一时重新核定。叠加前置条件（2026-10-04 用户验收
                    # 要求）：叠三煞占月/五黄到山/阴府等否决由本函数后续独立通道保证，
                    # 不因本提示漏网；仙命日支真冲的叠加否决在 calculate_score 主流程处理。
                    if _is_wangming_role(owner.get('role', '')):
                        _wm_tip = ''
                        if self.check_liuchong(month_zhi, owner_year_zhi): _wm_tip = '相冲'
                        elif self.check_po(month_zhi, owner_year_zhi): _wm_tip = '相破'
                        elif self.check_xing(month_zhi, owner_year_zhi): _wm_tip = '相刑'
                        elif self.check_liuhai(month_zhi, owner_year_zhi): _wm_tip = '相害'
                        elif self.check_liuhe(month_zhi, owner_year_zhi): _wm_tip = '六合'
                        elif self.check_sanhe([month_zhi, owner_year_zhi]): _wm_tip = '三合'
                        if _wm_tip:
                            # 害独立降档为"轻微提示"（害<破<刑<冲，P0-2 口径修正）
                            _tip_head = ('轻微提示' if _wm_tip == '相害' else '提示')
                            analysis.setdefault('info_reasons', []).append(
                                f"{_tip_head}（第一阶段临时降级，第二阶段重估）：月支与亡命（仙命）"
                                f"{owner['name']}年命{owner_year_zhi}{_wm_tip}")
                        continue

                    # 2026-09 作灶主事人模式：辅助者（半权重）月支六冲不降否决，冲刑破害/合化半权重
                    _zz_w = owner.get('_zaozhu_weight', None)
                    _zz_aux = _event_profile(event_type)['zaozhu_half'] and _zz_w is not None and float(_zz_w) < 1.0
                    _zz_suf = '（辅助·半权重）' if _zz_aux else ''
                    # 2026-09-18 年命六冲三档口径：【月支】档为"扣分不否决"
                    # （有制化余地），不再把整月判 suitable=False；日课总分层在
                    # _check_owner_day_zhichong 内按 -15 计入相主分。
                    if self.check_liuchong(month_zhi, owner_year_zhi):
                        _cp = _zaozhu_weighted(-25, 0.5 if _zz_aux else 1.0)
                        analysis['score'] += _cp
                        analysis['_chong_penalty'] += _cp  # 扣分不否决档，隔离兜底阈值
                        analysis['reasons'].append(
                            f"月支与{owner['name']}生肖相冲（扣分不否决）" + ('（辅助，半权重）' if _zz_aux else ''))
                    elif self.check_po(month_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(-15, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"月支与{owner['name']}生肖相破{_zz_suf}")
                    elif self.check_xing(month_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(-10, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"月支与{owner['name']}生肖相刑{_zz_suf}")
                    elif self.check_hai(month_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(-8, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"月支与{owner['name']}生肖相害{_zz_suf}")
                    elif self.check_liuhe(month_zhi, owner_year_zhi):
                        analysis['score'] += _zaozhu_weighted(15, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"月支与{owner['name']}生肖六合{_zz_suf}")
                    elif self.check_sanhe([month_zhi, owner_year_zhi]):
                        analysis['score'] += _zaozhu_weighted(10, 0.5 if _zz_aux else 1.0)
                        analysis['reasons'].append(f"月支与{owner['name']}生肖三合{_zz_suf}")
        
        # 对于修造类事项，分析月煞和二十四山方位吉凶（仅提供信息，不扣分）
        if _event_profile(event_type)['year_month_shan']:
            # 阴府检测：月干若为正/傍阴府，则直接判定为不可用
            if shan_xiang:
                # 使用新的阴府配置表
                try:
                    from modules.二十四山择吉天机 import get_yinfu_config
                    
                    # 判断冬至前后：春分(3月)到秋分(9月)之间为冬至后（阳长阴消），
                    # 秋分到次年春分之间为夏至后
                    # 简化判断：公历3-8月为冬至后，9-2月为夏至后
                    is_after_dongzhi = 3 <= test_date.month <= 8
                    
                    yinfu_config = get_yinfu_config(shan_xiang, is_after_dongzhi)
                    if yinfu_config:
                        ji_gan_list = yinfu_config.get('忌干', [])
                        yinfu_type = yinfu_config.get('type', '傍阴府')
                        
                        # 检查月干是否犯阴府
                        month_gan = analysis.get('month_gan', '')
                        if month_gan and month_gan in ji_gan_list:
                            # 根据阴府类型采取不同的处理方式
                            if yinfu_type == '正阴府':
                                # 2026-09-10 制化复核（2025-10-28坤山艨向兼未案例）：
                                # 日课含岁德/岁德合/天德/月德等吉神时，正阴府“需制化（不禁用）”，
                                # 与二十四山择吉天机【山家警告】口径一致：扣分不否决。
                                # 制化判定复用 calculate_ji_shanfu，以实际日课四柱（day_sizhu）为准
                                _zhihua = []
                                if day_sizhu:
                                    try:
                                        from modules.二十四山择吉天机 import calculate_ji_shanfu as _cjs
                                        _zhihua = _cjs(day_sizhu, shan_xiang) or []
                                    except Exception:
                                        _zhihua = []
                                if _zhihua:
                                    analysis['reasons'].append(
                                        f"月干{month_gan}为{shan_xiang}{yinfu_type}，大忌（有制化：{'、'.join(_zhihua)}），不禁用")
                                    analysis['details']['月干犯阴府'] = True
                                    analysis['details']['阴府类型'] = yinfu_type
                                    analysis['details']['阴府有制化'] = list(_zhihua)
                                    # 2026-09-10 二次修正：有制化属警告级（二十四山天机口径
                                    # “需制化（不禁用）”），扣-15（介于傍阴府-10与无制化
                                    # 否决之间），避免月分跌破50触发末尾“大凶自动否决”
                                    analysis['score'] -= 15
                                    if analysis['score'] < 60:
                                        analysis['level'] = '小凶'
                                else:
                                    # 无制化：正阴府单干也大忌，一票否决（保留原口径）
                                    analysis['reasons'].append(f"月干{month_gan}为{shan_xiang}{yinfu_type}，大忌")
                                    analysis['details']['月干犯阴府'] = True
                                    analysis['details']['阴府类型'] = yinfu_type
                                    analysis['suitable'] = False
                                    analysis['score'] = 0
                                    analysis['level'] = '大凶'
                            else:
                                # 傍阴府：单干有制权用，只扣分不否决
                                analysis['reasons'].append(f"月干{month_gan}为{shan_xiang}{yinfu_type}")
                                analysis['details']['月干犯阴府'] = True
                                analysis['details']['阴府类型'] = yinfu_type
                                # 傍阴府单干扣10分（比正阴府宽松）
                                analysis['score'] -= 10
                                # 如果分数低于60，设置为小凶
                                if analysis['score'] < 60:
                                    analysis['level'] = '小凶'
                except ImportError:
                    pass
            
            # 如果已经因为正阴府判定为不可用，跳过后续分析
            if not analysis['suitable']:
                return analysis

            # 年三煞占月（三煞月）：月建地支落入年三煞方，整月不宜修造动土
            # 与逐日择日管线"年三煞犯月柱一票否决"口径一致，避免月份分析与择日结果矛盾
            year_sansha_map = {
                '申': ['巳', '午', '未'], '子': ['巳', '午', '未'], '辰': ['巳', '午', '未'],
                '寅': ['亥', '子', '丑'], '午': ['亥', '子', '丑'], '戌': ['亥', '子', '丑'],
                '巳': ['寅', '卯', '辰'], '酉': ['寅', '卯', '辰'], '丑': ['寅', '卯', '辰'],
                '亥': ['申', '酉', '戌'], '卯': ['申', '酉', '戌'], '未': ['申', '酉', '戌']
            }
            _year_sha_fang = year_sansha_map.get(year_zhi, [])
            if month_zhi and month_zhi in _year_sha_fang:
                analysis['reasons'].append(
                    f"月建{month_zhi}正当年三煞（{''.join(_year_sha_fang)}）方，三煞占月，该月忌修造动土")
                analysis['details']['年三煞占月'] = True
                analysis['details']['年三煞方'] = _year_sha_fang
                analysis['suitable'] = False
                analysis['score'] = 0
                analysis['level'] = '大凶'
                return analysis

            # 月三煞分析
            # 月三煞方位映射（按传统择日规则，纯地支）
            # 寅午戌月煞北（亥子丑），亥卯未月煞西（申酉戌），申子辰月煞南（巳午未），巳酉丑月煞东（寅卯辰）
            month_sansha_map = {
                '寅': ['亥', '子', '丑'],  # 寅午戌月煞北
                '午': ['亥', '子', '丑'],
                '戌': ['亥', '子', '丑'],
                '亥': ['申', '酉', '戌'],  # 亥卯未月煞西
                '卯': ['申', '酉', '戌'],
                '未': ['申', '酉', '戌'],
                '申': ['巳', '午', '未'],  # 申子辰月煞南
                '子': ['巳', '午', '未'],
                '辰': ['巳', '午', '未'],
                '巳': ['寅', '卯', '辰'],  # 巳酉丑月煞东
                '酉': ['寅', '卯', '辰'],
                '丑': ['寅', '卯', '辰']
            }
            
            sansha_fang = month_sansha_map.get(month_zhi, [])
            if sansha_fang:
                # 仅提供信息，不扣分
                analysis.setdefault('info_reasons', []).append(f"月三煞在{''.join(sansha_fang)}方（忌修造）")  # 纯信息项：方位未临坐山不构成否决
                analysis['details']['月三煞'] = sansha_fang
                
                # 月柱本身检查：若月柱地支在三煞方位，则该月所有日时柱均不可犯
                # 传统规则：月支在三煞方位时，日时柱若也在煞方为"犯煞"
                # 这里检查月支本身是否在煞方（用于标记警告）
                if month_zhi in sansha_fang:
                    analysis.setdefault('info_reasons', []).append(f"月支{month_zhi}在月三煞方位，该月日时柱需避开煞方")
                    analysis['details']['月支犯煞'] = True
                
                # 如果提供了山向，分析山向与月煞的关系
                if shan_xiang:
                    # 提取坐山（山向的第一个字）
                    zuoshan = shan_xiang[0]
                    
                    # 检查是否有兼向
                    has_jianxiang = '兼' in shan_xiang
                    
                    # 将坐山映射到对应的地支（与修造规则一致）
                    zuoshan_zhis = []
                    if zuoshan in ['壬', '子', '癸']:
                        zuoshan_zhis = ['子']
                    elif zuoshan in ['丑', '艮', '寅']:
                        # 艮宫：丑艮寅三山
                        # 艮山兼丑：坐山在丑方
                        # 艮山兼寅：坐山在寅方
                        if zuoshan == '艮':
                            if has_jianxiang and '兼丑' in shan_xiang:
                                zuoshan_zhis = ['丑']
                            elif has_jianxiang and '兼寅' in shan_xiang:
                                zuoshan_zhis = ['寅']
                            else:
                                zuoshan_zhis = ['丑', '寅']
                        else:
                            zuoshan_zhis = [zuoshan] if has_jianxiang else [zuoshan]
                    elif zuoshan in ['甲', '卯', '乙']:
                        zuoshan_zhis = ['卯']
                    elif zuoshan in ['辰', '巽', '巳']:
                        # 巽宫：辰巽巳三山
                        # 巽山兼辰：坐山在辰方
                        # 巽山兼巳：坐山在巳方
                        if zuoshan == '巽':
                            if has_jianxiang and '兼辰' in shan_xiang:
                                zuoshan_zhis = ['辰']
                            elif has_jianxiang and '兼巳' in shan_xiang:
                                zuoshan_zhis = ['巳']
                            else:
                                zuoshan_zhis = ['辰', '巳']
                        else:
                            zuoshan_zhis = [zuoshan] if has_jianxiang else [zuoshan]
                    elif zuoshan in ['丙', '午', '丁']:
                        zuoshan_zhis = ['午']
                    elif zuoshan in ['未', '坤', '申']:
                        # 坤宫：未坤申三山
                        # 未山：未土
                        # 坤山：坤为西南，兼未时坐山在未方，兼申时坐山在申方
                        # 申山：申金
                        if zuoshan == '坤':
                            # 坤山兼未：坐山在未方（不包含申）
                            # 坤山兼申：坐山在申方
                            if has_jianxiang and '兼未' in shan_xiang:
                                zuoshan_zhis = ['未']
                            elif has_jianxiang and '兼申' in shan_xiang:
                                zuoshan_zhis = ['申']
                            else:
                                # 纯坤山，考虑整个坤宫
                                zuoshan_zhis = ['未', '申']
                        else:
                            zuoshan_zhis = [zuoshan] if has_jianxiang else [zuoshan]
                    elif zuoshan in ['庚', '酉', '辛']:
                        zuoshan_zhis = ['酉']
                    elif zuoshan in ['戌', '乾', '亥']:
                        # 乾宫：戌乾亥三山
                        # 乾山兼戌：坐山在戌方
                        # 乾山兼亥：坐山在亥方
                        if zuoshan == '乾':
                            if has_jianxiang and '兼戌' in shan_xiang:
                                zuoshan_zhis = ['戌']
                            elif has_jianxiang and '兼亥' in shan_xiang:
                                zuoshan_zhis = ['亥']
                            else:
                                zuoshan_zhis = ['戌', '亥']
                        else:
                            zuoshan_zhis = [zuoshan] if has_jianxiang else [zuoshan]
                    
                    # 检查坐山是否在月三煞方
                    # 所有煞方都算犯煞，不仅是核心煞方
                    zuoshan_fan_sansha = False
                    for zuoshan_zhi in zuoshan_zhis:
                        # 检查坐山地支是否在煞方列表中
                        if zuoshan_zhi in sansha_fang:
                            zuoshan_fan_sansha = True
                            break
                        # 也检查坐山映射后的地支
                        zuoshan_to_zhi = {
                            '未': '未',  # 未/坤山 -> 未
                            '申': '申',  # 申山 -> 申
                        }
                        mapped_zhi = zuoshan_to_zhi.get(zuoshan_zhi, zuoshan_zhi)
                        if mapped_zhi != zuoshan_zhi and mapped_zhi in sansha_fang:
                            zuoshan_fan_sansha = True
                            break
                    
                    if zuoshan_fan_sansha:
                        analysis['reasons'].append(f"所选山向{shan_xiang}坐山犯月三煞，不利修造")
                        analysis['details']['山向犯月煞'] = True
                        # 月三煞（犯坐山）扣 20 分，判为"凶"
                        analysis['score'] -= 20
                        # 不设置 suitable 为 False，因为只是月份不利，不是完全不可用
            
            # 月破方位
            chong_zhi = {
                '子': '午', '午': '子',
                '丑': '未', '未': '丑',
                '寅': '申', '申': '寅',
                '卯': '酉', '酉': '卯',
                '辰': '戌', '戌': '辰',
                '巳': '亥', '亥': '巳'
            }
            yuepo_fang = chong_zhi.get(month_zhi, '')
            if yuepo_fang:
                # 仅提供信息，不扣分
                analysis.setdefault('info_reasons', []).append(f"月破在{yuepo_fang}方（忌修造）")  # 纯信息项：方位未临坐山不构成否决
                analysis['details']['月破'] = yuepo_fang
                
                # 如果提供了山向，分析山向与月破的关系
                if shan_xiang:
                    shan_xiang_dir = shan_xiang[0]
                    if shan_xiang_dir == yuepo_fang:
                        analysis['reasons'].append(f"所选山向{shan_xiang}犯月破，不利修造")
                        analysis['details']['山向犯月破'] = True
                    
                    # 检查月支与坐山地支是否相冲（真正的月破）
                    zuoshan = shan_xiang[0]
                    has_jianxiang = '兼' in shan_xiang
                    
                    # 确定坐山地支（与月三煞判定逻辑一致）
                    zuoshan_zhis = []
                    if zuoshan in ['壬', '子', '癸']:
                        zuoshan_zhis = ['子']
                    elif zuoshan in ['丑', '艮', '寅']:
                        if zuoshan == '艮':
                            if has_jianxiang and '兼丑' in shan_xiang:
                                zuoshan_zhis = ['丑']
                            elif has_jianxiang and '兼寅' in shan_xiang:
                                zuoshan_zhis = ['寅']
                            else:
                                zuoshan_zhis = ['丑', '寅']
                        else:
                            zuoshan_zhis = [zuoshan]
                    elif zuoshan in ['甲', '卯', '乙']:
                        zuoshan_zhis = ['卯']
                    elif zuoshan in ['辰', '巽', '巳']:
                        if zuoshan == '巽':
                            if has_jianxiang and '兼辰' in shan_xiang:
                                zuoshan_zhis = ['辰']
                            elif has_jianxiang and '兼巳' in shan_xiang:
                                zuoshan_zhis = ['巳']
                            else:
                                zuoshan_zhis = ['辰', '巳']
                        else:
                            zuoshan_zhis = [zuoshan]
                    elif zuoshan in ['丙', '午', '丁']:
                        zuoshan_zhis = ['午']
                    elif zuoshan in ['未', '坤', '申']:
                        if zuoshan == '坤':
                            if has_jianxiang and '兼未' in shan_xiang:
                                zuoshan_zhis = ['未']
                            elif has_jianxiang and '兼申' in shan_xiang:
                                zuoshan_zhis = ['申']
                            else:
                                zuoshan_zhis = ['未', '申']
                        else:
                            zuoshan_zhis = [zuoshan]
                    elif zuoshan in ['庚', '酉', '辛']:
                        zuoshan_zhis = ['酉']
                    elif zuoshan in ['戌', '乾', '亥']:
                        if zuoshan == '乾':
                            if has_jianxiang and '兼戌' in shan_xiang:
                                zuoshan_zhis = ['戌']
                            elif has_jianxiang and '兼亥' in shan_xiang:
                                zuoshan_zhis = ['亥']
                            else:
                                zuoshan_zhis = ['戌', '亥']
                        else:
                            zuoshan_zhis = [zuoshan]
                    
                    # 检查月支是否与坐山地支相冲（使用六冲字典）
                    chong_zhi_check = {
                        '子': '午', '午': '子',
                        '丑': '未', '未': '丑',
                        '寅': '申', '申': '寅',
                        '卯': '酉', '酉': '卯',
                        '辰': '戌', '戌': '辰',
                        '巳': '亥', '亥': '巳'
                    }
                    
                    zuoshan_fan_yuepo = False
                    for zuoshan_zhi in zuoshan_zhis:
                        # 检查月支的冲支是否是坐山地支
                        if chong_zhi_check.get(month_zhi) == zuoshan_zhi:
                            zuoshan_fan_yuepo = True
                            break
                    
                    if zuoshan_fan_yuepo:
                        analysis['reasons'].append(f"月支{month_zhi}冲坐山{zuoshan}，犯月破，大凶")
                        analysis['details']['山向犯月破（地支冲）'] = True
                        # 月破（犯坐山）扣 25 分，判为凶
                        analysis['score'] -= 25
                        # 不设置 suitable 为 False，因为只是月份不利，不是完全不可用
            
            # 暗建煞分析（修正规则）
            # 标准暗建煞规则：寅午戌月暗建在亥，亥卯未月暗建在申，申子辰月暗建在巳，巳酉丑月暗建在寅
            # 以及它们的三合方
            anjian_map = {
                '寅': ['亥'],  # 寅午戌月暗建在亥
                '午': ['亥'],
                '戌': ['亥'],
                '申': ['巳'],  # 申子辰月暗建在巳
                '子': ['巳'],
                '辰': ['巳'],
                '亥': ['申'],  # 亥卯未月暗建在申
                '卯': ['申'],
                '未': ['申'],
                '巳': ['寅'],  # 巳酉丑月暗建在寅
                '酉': ['寅'],
                '丑': ['寅']
            }
            
            anjian_fang = anjian_map.get(month_zhi, [])
            if anjian_fang:
                # 仅提供信息，不扣分
                analysis.setdefault('info_reasons', []).append(f"暗建煞在{''.join(anjian_fang)}方（忌修造）")  # 纯信息项：方位未临坐山不构成否决
                analysis['details']['暗建煞'] = anjian_fang
                
                # 如果提供了山向，分析山向与暗建煞的关系
                if shan_xiang:
                    shan_xiang_dir = shan_xiang[0]
                    if shan_xiang_dir in anjian_fang:
                        analysis['reasons'].append(f"所选山向{shan_xiang}犯暗建煞，不利修造")
                        analysis['details']['山向犯暗建煞'] = True
            
            # 五行择月法分析
            if shan_xiang and self.wuxing_selector:
                # 将月支转换为节气月序号（寅月=1, 卯月=2, ..., 丑月=12）
                zhi_to_month_order = {
                    '寅': 1, '卯': 2, '辰': 3, '巳': 4, '午': 5, '未': 6,
                    '申': 7, '酉': 8, '戌': 9, '亥': 10, '子': 11, '丑': 12
                }
                month_order = zhi_to_month_order.get(month_zhi, test_date.month)
                wuxing_result = self.wuxing_selector.analyze_month(year, month_order, shan_xiang)
                if wuxing_result['wuxing']:
                    analysis['details']['山向五行'] = wuxing_result['wuxing']
                    analysis['details']['五行择月类型'] = wuxing_result['month_type']
                    if wuxing_result['month_type'] == '优先':
                        analysis['score'] += 15
                        analysis['reasons'].append(f"{wuxing_result['wuxing']}山优先选用月份")
                    elif wuxing_result['month_type'] == '可用':
                        analysis['score'] += 5
                        analysis['reasons'].append(f"{wuxing_result['wuxing']}山可用月份")
                    else:
                        analysis['reasons'].append(f"{wuxing_result['wuxing']}山非优选月份")
            
            # 增加月份基本加分：没有月三煞和月破的月份得"吉"
            # 只有真正没有大煞的月份才给加分
            # 如果有月破或月三煞（犯坐山），不应该加分
            has_po = '山向犯月破' in analysis['details'] or '山向犯月破（地支冲）' in analysis['details']
            has_sansha = analysis['details'].get('山向犯月煞', False)
            has_yinfu = analysis['details'].get('月干犯阴府', False)
            
            if not has_po and not has_sansha and not has_yinfu:
                # 无月破、无月三煞（犯坐山）、无阴府：加分20分，得"吉"
                analysis['score'] += 20
                analysis['reasons'].append('月份平和，无大煞')

        # 对于嫁娶，检查大利月、小利月
        if _event_profile(event_type)['liyue'] and owners:
            for owner in owners:
                if owner.get('role') == '新娘' or owner.get('性别') == '女':
                    # 计算新娘年支
                    if 'birth_date' in owner:
                        owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                                   owner.get('birth_hour', 12), 
                                                   owner.get('birth_minute', 0),
                                                   longitude=owner.get('birth_longitude'))
                        bride_year_zhi = owner_sizhu.get('year_zhi', '')
                        
                        # 检查该月份包含的所有农历月份
                        lunar_months = set()
                        d = date(year, test_date.month, 1)
                        while d.month == test_date.month:
                            # 2026-09-03 利月一致性修复：用高精度农历（实际日历）判定
                            # 每天所属农历月份，不再以节气月支法代推。
                            daily_sizhu = calculate_sizhu(d, 12, 0)
                            daily_sizhu['date'] = d
                            lunar_month = self._resolve_lunar_month(daily_sizhu)
                            lunar_months.add(lunar_month)
                            d += timedelta(days=1)
                        
                        # 检查每个农历月份，只标注利月（大利月或小利月）
                        for lunar_month in lunar_months:
                            month_type = self._check_li_yue(bride_year_zhi, lunar_month)
                            if month_type == '大利月':
                                analysis['score'] += 30
                                analysis['reasons'].append(f'新娘大利月（农历{lunar_month}月）')
                            elif month_type == '小利月':
                                analysis['score'] += 15
                                analysis['reasons'].append(f'新娘小利月（农历{lunar_month}月）')
        
        # 玄空飞星年盘+月盘：五黄/二黑到坐山
        # 年五黄/月五黄到山为年级/月级固定因素，整月每日皆犯，与逐日择日"五黄到山一票否决"口径一致
        if zeli_mode == 'feixing' and _event_profile(event_type)['feixing'] and shan_xiang:  # _zm0915
            _mtn = None
            for _m in ['壬','子','癸','丑','艮','寅','甲','卯','乙','辰','巽','巳',
                       '丙','午','丁','未','坤','申','庚','酉','辛','戌','乾','亥']:
                if shan_xiang.startswith(_m):
                    _mtn = _m; break
            if _mtn:
                _fx = self._get_year_month_feixing_at_mountain(year, year_zhi, month_zhi, _mtn)
                if _fx:
                    _y_star, _m_star = _fx[0], _fx[1]
                    if _y_star == 5 or _m_star == 5:
                        _which = []
                        if _y_star == 5: _which.append("年家")
                        if _m_star == 5: _which.append("月家")
                        analysis['reasons'].append(
                            f"{'、'.join(_which)}五黄到坐山{_mtn}，该月忌修造动土（每日皆犯）")
                        analysis['details']['五黄到山'] = True
                        analysis['suitable'] = False
                        analysis['score'] = 0
                        analysis['level'] = '大凶'
                    elif _y_star == 2 or _m_star == 2:
                        _which = []
                        if _y_star == 2: _which.append("年家")
                        if _m_star == 2: _which.append("月家")
                        analysis['reasons'].append(
                            f"{'、'.join(_which)}二黑到坐山{_mtn}，多病破财，修造慎之")
                        analysis['details']['二黑到山'] = True
                        analysis['score'] = max(0, analysis['score'] - 20)
                        if analysis['score'] < 50:
                            analysis['level'] = '大凶'
                            analysis['suitable'] = False

        # 如果没有特殊原因，添加基本信息
        if not analysis['reasons']:
            if owners:
                analysis['reasons'].append("月份平和，无冲克")
            else:
                analysis['reasons'].append("未提供事主信息，无法判断")
        
        # 确定等级
        # 基础分为70分，月破扣25分后为45分（凶），无煞加20分后为90分（吉）
        if analysis['score'] >= 90:
            analysis['level'] = '吉'
        elif analysis['score'] >= 70:
            analysis['level'] = '平'
        elif analysis['score'] >= 50:
            analysis['level'] = '小凶'
        else:
            analysis['level'] = '大凶'
            # 2026-09-18 三档口径：月支冲年命属"扣分不否决"档，低分纯粹由此造成时
            # （剔除后回到 50+）不转 suitable=False；阴府/月三煞等硬项已显式置位。
            _score_excl_chong = analysis['score'] - analysis.get('_chong_penalty', 0)
            if _score_excl_chong < 50:
                analysis['suitable'] = False
        analysis.pop('_chong_penalty', None)

        return analysis

    def analyze_day_detail(self, year, month, day, event_type, owners=None, shan_xiang=None, jian_xiang=None):
        """
        详细分析日课的吉凶情况
        
        Args:
            year: 年份（如2026）
            month: 月份（1-12）
            day: 日期（1-31）
            event_type: 事项类型
            owners: 事主信息
            shan_xiang: 山向信息
            jian_xiang: 兼向信息
            
        Returns:
            dict: 详细的日课分析结果
        """
        from datetime import date
        
        try:
            test_date = date(year, month, day)
        except ValueError:
            return {
                'success': False,
                'error': '无效日期'
            }
        
        # 计算四柱
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
        sizhu = calculate_sizhu(test_date, 12, 0)
        sizhu['year'] = year
        sizhu['month'] = month
        sizhu['day'] = day
        sizhu['date'] = test_date
        
        year_gan = sizhu.get('year_gan', '')
        year_zhi = sizhu.get('year_zhi', '')
        month_gan = sizhu.get('month_gan', '')
        month_zhi = sizhu.get('month_zhi', '')
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        hour_gan = sizhu.get('hour_gan', '')
        hour_zhi = sizhu.get('hour_zhi', '')
        
        # 合并山向
        full_shan_xiang = shan_xiang
        if shan_xiang and jian_xiang and jian_xiang != '正中':
            full_shan_xiang = f"{shan_xiang}{jian_xiang}"
        
        # 计算评分
        score_result = self.score(
            sizhu, event_type, owners,
            house_type='阳宅',
            shan_xiang=full_shan_xiang
        )
        
        # 构建详细分析结果
        analysis = {
            'success': True,
            'date': test_date.strftime('%Y-%m-%d'),
            'lunar_date': self._get_lunar_date_str(test_date),
            'sizhu': {
                '年柱': f"{year_gan}{year_zhi}",
                '月柱': f"{month_gan}{month_zhi}",
                '日柱': f"{day_gan}{day_zhi}",
                '时柱': f"{hour_gan}{hour_zhi}",
                '年干': year_gan,
                '年支': year_zhi,
                '月干': month_gan,
                '月支': month_zhi,
                '日干': day_gan,
                '日支': day_zhi,
                '时干': hour_gan,
                '时支': hour_zhi
            },
            'score': score_result.get('score', 0),
            'level': score_result.get('level', '未知'),
            'suitable': score_result.get('score', 0) >= 80,
            'reason': score_result.get('reason', ''),
            'analysis': {
                'overall': self._analyze_overall(sizhu, score_result),
                'wu_xing': self._analyze_wu_xing(sizhu),
                'shensha': self._analyze_shensha(sizhu, score_result),
                'owner_match': self._analyze_owner_match(sizhu, owners),
                'shan_xiang': self._analyze_shan_xiang(sizhu, full_shan_xiang, event_type)
            },
            'score_details': score_result.get('score_details', {}),
            'yi_list': score_result.get('yi_list', []),
            'ji_list': score_result.get('ji_list', []),
            'suggestions': self._generate_suggestions(sizhu, score_result, event_type, owners)
        }
        
        return analysis
    
    def _get_lunar_date_str(self, date_obj):
        """获取农历日期字符串"""
        try:
            from .农历转换 import get_lunar_date
            lunar = get_lunar_date(date_obj)
            return f"{lunar.get('year', '')}年{lunar.get('month', '')}{lunar.get('day', '')}"
        except:
            return '-'
    
    def _analyze_overall(self, sizhu, score_result):
        """综合分析"""
        score = score_result.get('score', 0)
        level = score_result.get('level', '')
        
        analysis = []
        
        if score >= 120:
            analysis.append('此日课五行均衡，吉神汇聚，是上等吉日')
        elif score >= 100:
            analysis.append('此日课整体吉利，可用')
        elif score >= 80:
            analysis.append('此日课基本可用，需注意化解')
        elif score >= 60:
            analysis.append('此日课有瑕疵，建议谨慎使用')
        else:
            analysis.append('此日课不吉，不建议使用')
        
        return analysis
    
    def _analyze_wu_xing(self, sizhu):
        """五行分析"""
        day_gan = sizhu.get('day_gan', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        wu_xing_map = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', 
                       '戊': '土', '己': '土', '庚': '金', '辛': '金', 
                       '壬': '水', '癸': '水'}
        
        analysis = {
            '日主': f"{day_gan}({wu_xing_map.get(day_gan, '')})",
            '月令': f"{month_zhi}",
            'analysis': []
        }
        
        # 简单的五行分析
        if day_gan:
            analysis['analysis'].append(f"日主为{day_gan}，属{wu_xing_map.get(day_gan, '')}")
        
        return analysis
    
    def _analyze_shensha(self, sizhu, score_result):
        """神煞分析"""
        shensha_list = score_result.get('shensha_list', [])
        huangdao_info = score_result.get('huangdao_info', {})
        
        analysis = {
            'jishen': [],
            'xiongsha': [],
            'huangdao': huangdao_info.get('huang_dao', '')
        }
        
        for shensha in shensha_list:
            if isinstance(shensha, dict):
                name = shensha.get('name', '')
                score = shensha.get('score', 0)
                if score > 0:
                    analysis['jishen'].append(name)
                elif score < 0:
                    analysis['xiongsha'].append(name)
        
        return analysis
    
    def _analyze_owner_match(self, sizhu, owners):
        """事主匹配分析"""
        if not owners:
            return {'has_owners': False, 'matches': []}
        
        day_zhi = sizhu.get('day_zhi', '')
        matches = []
        
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
        
        for owner in owners:
            owner_name = owner.get('name', '事主')
            if 'birth_date' in owner:
                owner_sizhu = calculate_sizhu(
                    owner['birth_date'],
                    owner.get('birth_hour', 12),
                    owner.get('birth_minute', 0),
                    longitude=owner.get('birth_longitude')
                )
                owner_year_zhi = owner_sizhu.get('year_zhi', '')
                owner_day_zhi = owner_sizhu.get('day_zhi', '')
                
                relation = ''
                if self.check_liuchong(day_zhi, owner_day_zhi):
                    relation = '日支相冲'
                elif self.check_liuhe(day_zhi, owner_day_zhi):
                    relation = '日支相合'
                elif self.check_sanhe([day_zhi, owner_day_zhi]):
                    relation = '日支三合'
                elif self.check_xing(day_zhi, owner_day_zhi):
                    relation = '日支相刑'
                elif self.check_hai(day_zhi, owner_day_zhi):
                    relation = '日支相害'
                
                matches.append({
                    'name': owner_name,
                    'birth_year_zhi': owner_year_zhi,
                    'day_zhi': owner_day_zhi,
                    'relation': relation
                })
        
        return {'has_owners': True, 'matches': matches}
    
    def _analyze_shan_xiang(self, sizhu, shan_xiang, event_type):
        """山向分析"""
        if not shan_xiang:
            return {'has_shan_xiang': False}
        
        year_zhi = sizhu.get('year_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        analysis = {
            'has_shan_xiang': True,
            'shan_xiang': shan_xiang,
            'year_sansha': [],
            'month_sansha': [],
            'day_sansha': [],
            'yuepo': '',
            'matches': []
        }
        
        # 年三煞
        year_sansha_map = {
            '申': ['巳', '丙', '午'], '子': ['巳', '丙', '午'], '辰': ['巳', '丙', '午'],
            '寅': ['亥', '壬', '子'], '午': ['亥', '壬', '子'], '戌': ['亥', '壬', '子'],
            '巳': ['寅', '甲', '卯'], '酉': ['寅', '甲', '卯'], '丑': ['寅', '甲', '卯'],
            '亥': ['申', '庚', '酉'], '卯': ['申', '庚', '酉'], '未': ['申', '庚', '酉']
        }
        analysis['year_sansha'] = year_sansha_map.get(year_zhi, [])
        
        # 月三煞
        month_sansha_map = {
            '申': ['巳', '丙', '午'], '子': ['巳', '丙', '午'], '辰': ['巳', '丙', '午'],
            '寅': ['亥', '壬', '子'], '午': ['亥', '壬', '子'], '戌': ['亥', '壬', '子'],
            '巳': ['寅', '甲', '卯'], '酉': ['寅', '甲', '卯'], '丑': ['寅', '甲', '卯'],
            '亥': ['申', '庚', '酉'], '卯': ['申', '庚', '酉'], '未': ['申', '庚', '酉']
        }
        analysis['month_sansha'] = month_sansha_map.get(month_zhi, [])
        
        # 日三煞（基于日支判断煞方）
        day_sansha_map = {
            '申': ['巳', '丙', '午'], '子': ['巳', '丙', '午'], '辰': ['巳', '丙', '午'],
            '寅': ['亥', '壬', '子'], '午': ['亥', '壬', '子'], '戌': ['亥', '壬', '子'],
            '巳': ['寅', '甲', '卯'], '酉': ['寅', '甲', '卯'], '丑': ['寅', '甲', '卯'],
            '亥': ['申', '庚', '酉'], '卯': ['申', '庚', '酉'], '未': ['申', '庚', '酉']
        }
        analysis['day_sansha'] = day_sansha_map.get(day_zhi, [])
        
        # 月破
        chong_zhi = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                     '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                     '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        analysis['yuepo'] = chong_zhi.get(month_zhi, '')
        
        return analysis
    
    def _generate_suggestions(self, sizhu, score_result, event_type, owners):
        """生成建议"""
        suggestions = []
        score = score_result.get('score', 0)
        ji_list = score_result.get('ji_list', [])
        
        if score < 80:
            suggestions.append('建议选择其他日期')
        
        if '岁破' in str(ji_list):
            suggestions.append('当日为岁破日，大事不宜')
        
        if '月破' in str(ji_list):
            suggestions.append('当日为月破日，不宜办大事')
        
        if '四离' in str(ji_list) or '四绝' in str(ji_list):
            suggestions.append('当日为四离四绝日，不宜嫁娶、出行')
        
        if owners:
            for owner in owners:
                if 'birth_date' in owner:
                    owner_name = owner.get('name', '事主')
                    try:
                        from .四柱计算器 import calculate_sizhu
                        owner_sizhu = calculate_sizhu(
                            owner['birth_date'],
                            owner.get('birth_hour', 12),
                            owner.get('birth_minute', 0),
                            longitude=owner.get('birth_longitude')
                        )
                        owner_year_zhi = owner_sizhu.get('year_zhi', '')
                        day_zhi = sizhu.get('day_zhi', '')
                        if self.check_liuchong(day_zhi, owner_year_zhi):
                            suggestions.append(f'{owner_name}生肖与日支相冲，需注意')
                    except:
                        pass
        
        return suggestions if suggestions else ['此日课整体吉利，可放心使用']
    
    def _get_sansha_info(self, sizhu, shan_xiang=None):
        """
        获取年月日三煞信息
        
        三煞避忌原则：
        - 年三煞最重：月、日、时柱皆不可犯（年柱本身不犯）
        - 月三煞次之：日、时柱不可犯（月柱本身不犯）
        - 日三煞又次之：时柱不可犯（日柱本身不犯）
        - 上管下，下不犯上
        
        Args:
            sizhu: 四柱信息
            shan_xiang: 山向信息
            
        Returns:
            dict: 三煞信息
        """
        year_zhi = sizhu.get('year_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        hour_zhi = sizhu.get('hour_zhi', '')
        
        # 三煞方位映射表（纯地支，符合三合局规则）
        sansha_map = {
            '申': ['巳', '午', '未'], '子': ['巳', '午', '未'], '辰': ['巳', '午', '未'],
            '寅': ['亥', '子', '丑'], '午': ['亥', '子', '丑'], '戌': ['亥', '子', '丑'],
            '巳': ['寅', '卯', '辰'], '酉': ['寅', '卯', '辰'], '丑': ['寅', '卯', '辰'],
            '亥': ['申', '酉', '戌'], '卯': ['申', '酉', '戌'], '未': ['申', '酉', '戌']
        }
        
        year_sansha = sansha_map.get(year_zhi, [])
        month_sansha = sansha_map.get(month_zhi, [])
        day_sansha = sansha_map.get(day_zhi, [])
        
        info = {
            'year_sansha': year_sansha,
            'month_sansha': month_sansha,
            'day_sansha': day_sansha,
            # 山向犯三煞
            'year_sansha_fan': False,
            'month_sansha_fan': False,
            'day_sansha_fan': False,
            # 四柱犯年三煞（年管月日时）
            'year_sansha_month_fan': False,
            'year_sansha_day_fan': False,
            'year_sansha_hour_fan': False,
            # 四柱犯月三煞（月管日时）
            'month_sansha_day_fan': False,
            'month_sansha_hour_fan': False,
            # 四柱犯日三煞（日管时）
            'day_sansha_hour_fan': False,
            # 三煞严重等级
            'year_sansha_severity': 0,
            'month_sansha_severity': 0,
            'day_sansha_severity': 0,
            # 三煞总评分影响
            'sansha_penalty': 0,
            'sansha_penalty_detail': []
        }
        
        # 四柱三煞检查（上管下原则）
        # 年三煞：月、日、时柱不可犯
        if year_sansha:
            if month_zhi in year_sansha:
                info['year_sansha_month_fan'] = True
                info['year_sansha_severity'] += 3
            if day_zhi in year_sansha:
                info['year_sansha_day_fan'] = True
                info['year_sansha_severity'] += 3
            if hour_zhi in year_sansha:
                info['year_sansha_hour_fan'] = True
                info['year_sansha_severity'] += 2
        
        # 月三煞：日、时柱不可犯
        if month_sansha:
            if day_zhi in month_sansha:
                info['month_sansha_day_fan'] = True
                info['month_sansha_severity'] += 2
            if hour_zhi in month_sansha:
                info['month_sansha_hour_fan'] = True
                info['month_sansha_severity'] += 1
        
        # 日三煞：时柱不可犯
        if day_sansha:
            if hour_zhi in day_sansha:
                info['day_sansha_hour_fan'] = True
                info['day_sansha_severity'] += 1
        
        # 检查山向是否犯三煞
        if shan_xiang:
            zuoshan = shan_xiang[0] if shan_xiang else ''
            has_jianxiang = '兼' in shan_xiang
            
            # 二十四山到地支的基础映射
            shan_to_zhi = {
                '壬': '子', '子': '子', '癸': '子',
                '丑': '丑', '艮': '丑', '寅': '寅',
                '甲': '卯', '卯': '卯', '乙': '卯',
                '辰': '辰', '巽': '辰', '巳': '巳',
                '丙': '午', '午': '午', '丁': '午',
                '未': '未', '坤': '未', '申': '申',
                '庚': '酉', '酉': '酉', '辛': '酉',
                '戌': '戌', '乾': '戌', '亥': '亥'
            }
            
            # 二十四山到五行方位的映射（用于三煞检查）
            shan_to_wuxing = {
                '壬': '水', '子': '水', '癸': '水',
                '丑': '土', '艮': '土', '寅': '木',
                '甲': '木', '卯': '木', '乙': '木',
                '辰': '土', '巽': '木', '巳': '火',
                '丙': '火', '午': '火', '丁': '火',
                '未': '土', '坤': '土', '申': '金',
                '庚': '金', '酉': '金', '辛': '金',
                '戌': '土', '乾': '金', '亥': '水'
            }
            
            # 检查坐山是否在煞方
            # 对于天干山（艮、巽、坤、乾），需要根据兼向来确定坐山
            zuoshan_zhis = []
            if zuoshan in ['艮']:
                # 艮宫：丑艮寅三山
                if has_jianxiang and '兼丑' in shan_xiang:
                    zuoshan_zhis = ['丑']
                elif has_jianxiang and '兼寅' in shan_xiang:
                    zuoshan_zhis = ['寅']
                else:
                    zuoshan_zhis = ['丑', '寅']
            elif zuoshan in ['巽']:
                # 巽宫：辰巽巳三山
                if has_jianxiang and '兼辰' in shan_xiang:
                    zuoshan_zhis = ['辰']
                elif has_jianxiang and '兼巳' in shan_xiang:
                    zuoshan_zhis = ['巳']
                else:
                    zuoshan_zhis = ['辰', '巳']
            elif zuoshan in ['坤']:
                # 坤宫：未坤申三山
                if has_jianxiang and '兼未' in shan_xiang:
                    zuoshan_zhis = ['未']
                elif has_jianxiang and '兼申' in shan_xiang:
                    zuoshan_zhis = ['申']
                else:
                    zuoshan_zhis = ['未', '申']
            elif zuoshan in ['乾']:
                # 乾宫：戌乾亥三山
                if has_jianxiang and '兼戌' in shan_xiang:
                    zuoshan_zhis = ['戌']
                elif has_jianxiang and '兼亥' in shan_xiang:
                    zuoshan_zhis = ['亥']
                else:
                    zuoshan_zhis = ['戌', '亥']
            else:
                # 其他山直接使用基础映射
                zuoshan_zhis = [shan_to_zhi.get(zuoshan, '')]
            
            # 检查年月日三煞
            for zhi in zuoshan_zhis:
                if zhi:
                    if zhi in info['year_sansha']:
                        info['year_sansha_fan'] = True
                    if zhi in info['month_sansha']:
                        info['month_sansha_fan'] = True
                    if zhi in info['day_sansha']:
                        info['day_sansha_fan'] = True
            
            # 注意：不需要扩展检查相邻地支
            # 三煞检查以坐山本身为准，对于天干山（坤、艮、巽、乾）：
            # 1. 如果有兼向，以兼向地支为准
            # 2. 如果没有兼向，以天干山所在的五行方位为准
            # 3. 不需要检查相邻地支，因为择日学中三煞检查以坐山为核心
        
        # 使用二十四山择吉天机模块进行专业山家检查
        if shan_xiang:
            try:
                from .二十四山择吉天机 import check_mountain_day
                
                date_info = {
                    'year_gan': sizhu.get('year_gan', ''),
                    'year_zhi': year_zhi,
                    'month_gan': sizhu.get('month_gan', ''),
                    'month_zhi': month_zhi,
                    'day_gan': sizhu.get('day_gan', ''),
                    'day_zhi': day_zhi,
                    'hour_gan': sizhu.get('hour_gan', ''),
                    'hour_zhi': hour_zhi,
                    'year': sizhu.get('year', ''),  # 公历年份（用于年家五黄紫白飞星）
                }
                
                event_type = ''
                if hasattr(self, '_current_event_type'):
                    event_type = self._current_event_type
                
                mountain_result = check_mountain_day(date_info, shan_xiang, event_type or '修造')
                info['mountain_day_check'] = mountain_result
                
                # 从专业检查结果中提取额外信息
                if not mountain_result.get('可用', True):
                    _mb_reasons = list(mountain_result.get('凶煞', []) or [])
                    if getattr(self, '_zeli_mode', 'feixing') == 'pure':
                        # _zm0915：纯正五行（协纪辨方书）剔除三元紫白飞星体系的五黄/二黑封禁；
                        # 日冲山/岁煞/阴府等传统年神照常封禁
                        _mb_reasons = [_r for _r in _mb_reasons
                                       if not any(_k in str(_r) for _k in ('五黄', '二黑', '紫白'))]
                    info['mountain_blocked'] = bool(_mb_reasons)
                    info['mountain_block_reasons'] = _mb_reasons
                else:
                    _mb_warns = list(mountain_result.get('警告', []) or [])
                    if getattr(self, '_zeli_mode', 'feixing') == 'pure':
                        _mb_warns = [_w for _w in _mb_warns
                                     if not any(_k in ((_w.get('说明', '') if isinstance(_w, dict) else str(_w)))
                                                for _k in ('五黄', '二黑', '紫白'))]
                    info['mountain_warnings'] = _mb_warns
                    info['mountain_available'] = True
                
                info['mountain_jishen'] = mountain_result.get('吉神', [])
                info['mountain_day_type'] = mountain_result.get('日类', '普通日')
            except ImportError:
                pass

        # 年家五黄信息（详情展示用；无论是否选山向均给出五黄宫位，
        # 坐山犯/不犯的结论在选中山向时一并给出）
        try:
            if getattr(self, '_zeli_mode', 'feixing') != 'feixing':
                raise ImportError('_zm0915 pure skip wuhuang')  # 纯正五行模式不排年家紫白
            from .二十四山择吉天机 import check_wuhuang as _check_wuhuang
            info['wuhuang_info'] = _check_wuhuang(
                {'year_gan': sizhu.get('year_gan', ''), 'year_zhi': year_zhi,
                 'month_gan': sizhu.get('month_gan', ''), 'month_zhi': month_zhi,
                 'day_gan': sizhu.get('day_gan', ''), 'day_zhi': day_zhi,
                 'hour_gan': sizhu.get('hour_gan', ''), 'hour_zhi': hour_zhi,
                 'year': sizhu.get('year', '')}, shan_xiang or '')
        except ImportError:
            pass

        # 年家二黑信息（详情展示用；二黑为病符星，失运主疾病脾胃）
        try:
            if getattr(self, '_zeli_mode', 'feixing') != 'feixing':
                raise ImportError('_zm0915 pure skip erhei')  # 纯正五行模式不排年家紫白
            from .二十四山择吉天机 import check_erhei as _check_erhei
            info['erhei_info'] = _check_erhei(
                {'year_gan': sizhu.get('year_gan', ''), 'year_zhi': year_zhi,
                 'month_gan': sizhu.get('month_gan', ''), 'month_zhi': month_zhi,
                 'day_gan': sizhu.get('day_gan', ''), 'day_zhi': day_zhi,
                 'hour_gan': sizhu.get('hour_gan', ''), 'hour_zhi': hour_zhi,
                 'year': sizhu.get('year', '')}, shan_xiang or '')
        except ImportError:
            pass

        return info
    
    def _get_lunar_month_from_zhi(self, month_zhi):
        """
        从月地支获取农历月份（1-12）——作为fallback。
        注意：月支法以立春为界（寅=1…丑=12），在腊月/正月的节气交界日与实际农历月份
        可能偏差1个月（如2026-02-05寅月但实际农历腊月）。嫁娶利月判定建议优先使用
        _resolve_lunar_month(sizhu)，它基于sizhu.date走高精度农历转换。
        """
        zhi_to_month = {
            '寅': 1, '卯': 2, '辰': 3, '巳': 4,
            '午': 5, '未': 6, '申': 7, '酉': 8,
            '戌': 9, '亥': 10, '子': 11, '丑': 12
        }
        return zhi_to_month.get(month_zhi, 1)

    def _resolve_lunar_month(self, sizhu):
        """
        2026-09-03 用户利月一致性修复：统一"嫁娶大利月/小利月/妨亲月"判定的农历月份来源。
        优先级：
          1) sizhu内若有明确农历字段（lunar_month / lunar['month']数字）——直接用。
          2) 否则用sizhu.date走高精度农历转换（实际日历农历，腊月=12、正月=1，
             解决2026-02-05"寅月但农历腊月"这类节气月支与农历月错位的矛盾）。
          3) 回退：_get_lunar_month_from_zhi(sizhu.month_zhi)。
        Returns: int 1..12
        """
        # 1) 字段优先
        lm = sizhu.get('lunar_month')
        if isinstance(lm, (int, float)) and 1 <= int(lm) <= 12:
            return int(lm)
        try:
            lunar_obj = sizhu.get('lunar')
            if isinstance(lunar_obj, dict):
                m = lunar_obj.get('month')
                if isinstance(m, (int, float)) and 1 <= int(m) <= 12:
                    return int(m)
                # 中文名称映射（腊月/正月）
                mc = str(lunar_obj.get('month_chinese') or lunar_obj.get('month') or '')
                _map = {'正月':1,'二月':2,'三月':3,'四月':4,'五月':5,'六月':6,
                        '七月':7,'八月':8,'九月':9,'十月':10,'十一月':11,'冬月':11,'腊月':12}
                if mc in _map: return _map[mc]
        except Exception:
            pass
        # 2) 日期高精度农历
        d = sizhu.get('date') or sizhu.get('datetime')
        try:
            if hasattr(d, 'year') and hasattr(d, 'month') and hasattr(d, 'day'):
                try:
                    from .四柱计算器 import get_lunar_date as _gld
                except Exception:
                    from 四柱计算器 import get_lunar_date as _gld
                lun = _gld(d)
                if isinstance(lun, dict):
                    m = lun.get('month')
                    if isinstance(m, (int, float)) and 1 <= int(m) <= 12:
                        return int(m)
                    mc = str(lun.get('month_chinese') or lun.get('month') or '')
                    _map = {'正月':1,'二月':2,'三月':3,'四月':4,'五月':5,'六月':6,
                            '七月':7,'八月':8,'九月':9,'十月':10,'十一月':11,'冬月':11,'腊月':12}
                    if mc in _map: return _map[mc]
        except Exception:
            pass
        # 3) 回退节气月支法
        return self._get_lunar_month_from_zhi(sizhu.get('month_zhi', '') or '')
    
    def _check_li_yue(self, bride_year_zhi, month):
        """
        检查嫁娶大利月、小利月
        依据：女命年支与月份的关系
        """
        # 大利月、小利月表（基于女命年支）
        # 大利月口诀：正七迎鸡兔，二八虎和猴，三九蛇共猪，四十龙和狗，牛羊五十一，鼠马六腊月
        #   兔(卯)、鸡(酉)：正七月；虎(寅)、猴(申)：二八月；蛇(巳)、猪(亥)：三九月
        #   龙(辰)、狗(戌)：四月、十月；牛(丑)、羊(未)：五月、十一月；鼠(子)、马(午)：六月、十二月
        # 小利月口诀：鼠马二八月，牛羊四十当，虎猴正七月，兔鸡六腊月，龙狗三九月，蛇猪五十一
        #   鼠(子)、马(午)：二八月；牛(丑)、羊(未)：四十月；虎(寅)、猴(申)：正七月
        #   兔(卯)、鸡(酉)：六腊月；龙(辰)、狗(戌)：三九月；蛇(巳)、猪(亥)：五冬月
        # （腊月=12、冬月=11）

        li_yue_table = {
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
        
        if bride_year_zhi in li_yue_table:
            if month in li_yue_table[bride_year_zhi]['大利月']:
                return '大利月'
            elif month in li_yue_table[bride_year_zhi]['小利月']:
                return '小利月'
        
        # 妨夫月、妨妻月（简化判断）
        # 一般来说，除了大利月、小利月外，其他月份需要谨慎
        return '普通月'
    
    def _calculate_yueling_help(self, sizhu):
        """
        计算月令对日主的帮助评分
        
        参考正五行择日法，考虑：
        1. 日主在月令中的旺衰（旺相休囚死）
        2. 月令与日支的关系（三合、六合、刑冲等）
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 月令帮助评分
        """
        score = 0
        
        # 1. 日主在月令中的旺衰评分
        wangxiang_score = self._calculate_wangxiang(sizhu)
        score += wangxiang_score
        
        # 2. 月令与日支关系评分
        zhizhi_score = self._calculate_zhizhi_relation(sizhu)
        score += zhizhi_score
        
        return score
    
    def _calculate_wangxiang(self, sizhu):
        """
        计算日主在月令中的旺衰评分
        
        采用八字命理中的"旺相休囚死"表
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 旺衰评分
        """
        # 旺相休囚死表
        wangxiang_table = {
            '甲': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
            '乙': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
            '丙': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
            '丁': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
            '戊': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
            '己': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
            '庚': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
            '辛': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
            '壬': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
            '癸': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']}
        }
        
        # 获取日干和月支
        day_gan = sizhu.get('day_gan', '')
        month_zhi = sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else ''
        
        if not day_gan or not month_zhi:
            return 0
        
        # 查找旺相休囚死
        if day_gan in wangxiang_table:
            table = wangxiang_table[day_gan]
            if month_zhi in table['旺']:
                return 10  # 旺：+10分
            elif month_zhi in table['相']:
                return 5   # 相：+5分
            elif month_zhi in table['休']:
                return 0   # 休：0分
            elif month_zhi in table['囚']:
                return -5  # 囚：-5分
            elif month_zhi in table['死']:
                return -10 # 死：-10分
        
        return 0
    
    def _calculate_zhizhi_relation(self, sizhu):
        """
        计算月令与日支的关系评分
        
        考虑：三合、六合、刑、冲、破、害
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 关系评分
        """
        # 获取月支和日支
        month_zhi = sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else ''
        day_zhi = sizhu.get('日柱', '')[1] if len(sizhu.get('日柱', '')) > 1 else ''
        
        if not month_zhi or not day_zhi:
            return 0
        
        # 六合关系
        liuhe = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        # 三合关系
        sanhe = {
            '申子辰': ['申', '子', '辰'],
            '寅午戌': ['寅', '午', '戌'],
            '巳酉丑': ['巳', '酉', '丑'],
            '亥卯未': ['亥', '卯', '未']
        }
        
        # 六冲关系
        liuchong = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        
        # 六害关系
        liuhai = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        
        # 计算关系
        if liuhe.get(month_zhi) == day_zhi:
            return 8  # 六合：+8分
        
        # 检查三合
        for he in sanhe.values():
            if month_zhi in he and day_zhi in he:
                return 5  # 三合：+5分
        
        if liuchong.get(month_zhi) == day_zhi:
            return -15  # 六冲（月破）：-15分
        
        if liuhai.get(month_zhi) == day_zhi:
            return -5  # 六害：-5分
        
        return 0
    
    def _calculate_xishen_match(self, sizhu, owners):
        """
        计算日课五行与事主喜用神的匹配评分

        正五行择日法核心理念：日课四柱如同为事主"造命"，
        必须补益事主八字中的用神，才能达到催吉的效果。

        评分逻辑：
        1. 日课天干五行与事主用神相同：+8分
        2. 日课天干五行与事主喜神相同：+5分
        3. 日课地支藏干包含用神：+3分
        4. 日课地支藏干包含喜神：+2分
        5. 日课五行克事主用神：-10分（大忌）
        6. 日课五行与事主用神相冲：-8分

        Args:
            sizhu: 日课四柱信息
            owners: 事主信息列表

        Returns:
            tuple: (总评分, 每个事主的详细匹配信息)
        """
        if not owners:
            return 0, []

        total_score = 0
        owner_matches = []

        # 提取日课天干五行
        sizhu_wuxing = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) > 0:
                gan = pillar[0]
                # 天干五行映射
                gan_wuxing = {
                    '甲': '木', '乙': '木',
                    '丙': '火', '丁': '火',
                    '戊': '土', '己': '土',
                    '庚': '金', '辛': '金',
                    '壬': '水', '癸': '水'
                }
                if gan in gan_wuxing:
                    sizhu_wuxing.append(gan_wuxing[gan])

        # 提取日课地支藏干五行
        zhigan_map = {
            '子': ['水'],
            '丑': ['土', '水', '金'],
            '寅': ['木', '火', '土'],
            '卯': ['木'],
            '辰': ['土', '木', '水'],
            '巳': ['火', '土', '金'],
            '午': ['火', '土'],
            '未': ['土', '火', '木'],
            '申': ['金', '水', '土'],
            '酉': ['金'],
            '戌': ['土', '金', '火'],
            '亥': ['水', '木']
        }

        sizhu_canggan = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) > 1:
                zhi = pillar[1]
                if zhi in zhigan_map:
                    sizhu_canggan.extend(zhigan_map[zhi])

        # 遍历所有事主，计算匹配度
        for idx, owner in enumerate(owners):
            owner_name = owner.get('name', f'事主{idx+1}')
            owner_xishen = owner.get('xishen', '')
            owner_yongshen = owner.get('yongshen', '')

            # 解析喜用神（可能包含多个，如"木、水"）
            owner_xishen_list = [x.strip() for x in owner_xishen.split('、') if x.strip()]
            owner_yongshen_list = [x.strip() for x in owner_yongshen.split('、') if x.strip()]

            owner_score = 0
            match_details = []

            # 1. 检查日课天干与用神匹配
            # 记录是否已经匹配过同一种五行，避免重复加分
            matched_wuxing = set()
            for wx in sizhu_wuxing:
                if wx in owner_yongshen_list and wx not in matched_wuxing:
                    owner_score += 5  # 天干为用神：+5分（降低分数）
                    match_details.append(f"天干五行{wx}与用神匹配")
                    matched_wuxing.add(wx)
                elif wx in owner_xishen_list and wx not in matched_wuxing:
                    owner_score += 3  # 天干为喜神：+3分（降低分数）
                    match_details.append(f"天干五行{wx}与喜神匹配")
                    matched_wuxing.add(wx)

            # 2. 检查日课藏干与用神匹配
            matched_canggan = set()
            for wx in sizhu_canggan:
                if wx in owner_yongshen_list and wx not in matched_canggan:
                    owner_score += 2  # 藏干为用神：+2分（降低分数）
                    match_details.append(f"藏干五行{wx}与用神匹配")
                    matched_canggan.add(wx)
                elif wx in owner_xishen_list and wx not in matched_canggan:
                    owner_score += 1  # 藏干为喜神：+1分（降低分数）
                    match_details.append(f"藏干五行{wx}与喜神匹配")
                    matched_canggan.add(wx)
            
            # 限制单个事主喜用神得分上限
            if owner_score > 15:
                owner_score = 15
                match_details.append("喜用神得分已达上限")

            # 2026-09 作灶主事人模式：辅助事主半权重（主事人权重1.0，无打标默认1.0）
            _xw = owner.get('_zaozhu_weight', None)
            _xw = float(_xw) if _xw is not None else 1.0
            if _xw < 1.0:
                owner_score = _zaozhu_weighted(owner_score, _xw)
                match_details.append("辅助事主，按半权重计分")

            total_score += owner_score
            owner_matches.append({
                'name': owner_name,
                'score': owner_score,
                'weight': _xw,
                'details': match_details,
                'xishen': owner_xishen,
                'yongshen': owner_yongshen
            })

        return total_score, owner_matches
    
    def _check_marriage_day_chong(self, sizhu, owners):
        """
        婚嫁硬性否决检查：日课日支冲事主日支（冲夫妻宫，婚嫁大忌）

        嫁娶以日柱为夫妻宫，日课日支冲新郎/新娘日支为大忌，
        与重丧日、三娘煞等同列一票否决（归零），不另设扣分项。
        否决原因通过 veto_reasons 明确显示，避免用户只看到模糊的门槛提示。
        """
        veto_list = []
        if not owners:
            return veto_list
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi and sizhu.get('日柱'):
            day_zhi = str(sizhu['日柱'])[1:2]
        if not day_zhi:
            return veto_list
        liuchong_map = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                        '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                        '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        chong_zhi = liuchong_map.get(day_zhi, '')
        if not chong_zhi:
            return veto_list
        for idx, owner in enumerate(owners):
            if not isinstance(owner, dict):
                continue
            name = owner.get('name') or f"事主{idx + 1}"
            owner_day_zhi = ''
            if owner.get('sizhu'):
                parts = str(owner['sizhu']).split()
                if len(parts) >= 3 and len(parts[2]) >= 2:
                    owner_day_zhi = parts[2][1]
            elif owner.get('birth_date'):
                try:
                    from .四柱计算器 import calculate_sizhu as _calc_sz
                    _osz = _calc_sz(owner.get('birth_date'), owner.get('birth_hour', 12), owner.get('birth_minute', 0), longitude=owner.get('birth_longitude'))
                    owner_day_zhi = _osz.get('day_zhi', '')
                except Exception:
                    owner_day_zhi = ''
            if owner_day_zhi == chong_zhi:
                veto_list.append(f"日课日支{day_zhi}冲{name}日支{owner_day_zhi}（冲夫妻宫，婚嫁大忌）")
        return veto_list

    def _detect_wm_resolvers(self, wu_xing_result=None, sun_moon_info=None):
        """仙命真冲的化解吉神探测（宽集，2026-10-04 用户拍板）。

        宽集：天德/月德/岁德（含 *德合）、天赦、天愿、太阳到山、
        三合、六合——三合/六合不论合化成功与否，见即算有制化。
        来源：
        1. shensha_list 吉神项 name（神煞通道；三合/六合均为吉神项）
        2. wu_xing_result.details['地支关系'] 中的合局（四柱会合）
        3. sun_moon_info.sun_to_mountain（太阳到山）
        返回命中的吉神键名列表；无 → []。
        """
        hits = []

        def _take(blob):
            for k in ('天德', '月德', '岁德', '天赦', '天愿', '三合', '六合'):
                if k in blob and k not in hits:
                    hits.append(k)

        for s in self.shensha_list:
            name = str(s.get('name', '')) if isinstance(s, dict) else ''
            if name:
                _take(name)
        if isinstance(wu_xing_result, dict):
            _d = wu_xing_result.get('details', {})
            for r in (_d.get('地支关系') or []):
                _take(str(r))
        if sun_moon_info and sun_moon_info.get('sun_to_mountain'):
            if '太阳到山' not in hits:
                hits.append('太阳到山')
        return hits

    def _build_wm_dual_veto_text(self, wangming_info, shanzuo_eval, day_zhi,
                                 zc_heavy, zc_resolvers,
                                 sz_heavy, sz_resolvers):
        """仙命双凶叠加否决文案（2026-10-04 §59.10 用户拍板）。

        日支真冲 + 坐山克仙命同日命中时使用：明示两凶及各自制化状态
        （叠大忌 / 有制化：X / 无制化），强制否决，不因个别制化降级。
        纯文本构造，4 种制化状态组合均可独立断言。
        """
        def _state(heavy, resolvers):
            if heavy:
                return f"叠{'/'.join(heavy)}大忌"
            if resolvers:
                return f"有制化：{'、'.join(resolvers)}"
            return "无制化"

        return (
            f"【仙命双凶叠加】日支真冲＋坐山克仙命（亡命{wangming_info['name']}）："
            f"①日支真冲：亡命{wangming_info['name']}年命{wangming_info['年柱'][1]}"
            f"与日支{day_zhi}相冲（{_state(zc_heavy, zc_resolvers)}）；"
            f"②坐山克仙命：坐山{shanzuo_eval['坐山']}五行属"
            f"{shanzuo_eval['坐山五行']}，克亡命纳音{wangming_info['纳音']}"
            f"（{wangming_info['五行']}）（{_state(sz_heavy, sz_resolvers)}）。"
            f"两个-30顶级凶同日并见，吉神同时对症解两凶概率极低，"
            f"强制否决，不因个别制化而降级（一票否决）")

    def _check_veto_overlay(self, sansha_info=None):
        """仙命系三级判定的"叠重煞"检查（公共函数，2026-10-04 拍板抽取）。

        仙命真冲、坐山克仙命共用：命中三煞/岁破/月破/日破任一 → 返回命中键名
        列表（触发直接否决，有制化也不救）；无 → []。
        来源：
        1. ji_list 文本（岁破/月破/日破/三煞）
        2. sansha_info 标志位（年/月三煞犯山向或犯日柱/月柱/时柱；
           日三煞犯山向按既有口径较轻，不算叠忌）
        """
        hits = []
        _ji_blob = ' '.join(str(j) for j in self.ji_list)
        for k in ('三煞', '岁破', '月破', '日破'):
            if k in _ji_blob:
                hits.append(k)
        if isinstance(sansha_info, dict):
            _ss_flags = (
                'year_sansha_fan', 'month_sansha_fan',
                'year_sansha_day_fan', 'year_sansha_month_fan',
                'year_sansha_hour_fan', 'month_sansha_day_fan',
                'month_sansha_hour_fan',
            )
            if any(sansha_info.get(f) for f in _ss_flags) and '三煞' not in hits:
                hits.append('三煞')
        return hits

    def _build_wangming_info(self, owners):
        """构造亡命（仙命）信息：年柱干支 + 纳音名 + 纳音五行。

        安葬路径专用；纳音表复用 modules/二十四山.py 的
        NAYIN_NAMES/NAYIN_WUXING（六十甲子纳音，分金通道同源数据）。
        无死者卡 / 无生辰 → None（旧方案兼容，下游按缺省处理）。
        """
        if not owners:
            return None
        for owner in owners:
            if not _is_wangming_role(owner.get('role', '')):
                continue
            year_gz = ''
            if owner.get('sizhu'):
                _parts = str(owner['sizhu']).split()
                if _parts:
                    year_gz = _parts[0]
            if not year_gz and owner.get('birth_date'):
                try:
                    from .四柱计算器 import calculate_sizhu
                    _osz = calculate_sizhu(
                        owner['birth_date'],
                        owner.get('birth_hour', 12),
                        owner.get('birth_minute', 0),
                        longitude=owner.get('birth_longitude'))
                    year_gz = (_osz.get('year_gan', '')
                               + _osz.get('year_zhi', ''))
                except Exception as e:
                    logger.error(f"亡命年柱计算失败: {str(e)}")
            try:
                from .二十四山 import NAYIN_NAMES, NAYIN_WUXING
            except ImportError:
                from 二十四山 import NAYIN_NAMES, NAYIN_WUXING
            return {
                'name': owner.get('name', ''),
                '年柱': year_gz,
                '纳音': NAYIN_NAMES.get(year_gz, '未知'),
                '五行': NAYIN_WUXING.get(year_gz, '未知'),
            }
        return None

    def _check_owner_day_zhichong(self, sizhu, owners):
        """
        检查日课日支与事主日支的冲合关系（相主原则）
        
        正五行择日法强调"相主"，必须检查日课日支与事主日支的关系：
        - 日课日支冲事主日支：大凶，-20分
        - 日课日支刑事主日支：凶，-10分
        - 日课日支破事主日支：凶，-15分（相破为破坏、捣乱之象）
        - 日课日支害事主日支：小凶，-5分
        - 日课日支合事主日支：吉，+8分
        - 日课日支与事主日支相同（伏吟）：小吉，+3分
        
        Args:
            sizhu: 日课四柱信息
            owners: 事主信息列表
            
        Returns:
            tuple: (总评分, 详细信息列表)
        """
        if not owners or not HAS_BAZI_TOOLS:
            return 0, []
        
        total_score = 0
        details = []
        
        # 获取日课日支
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi:
            return 0, []
        
        for idx, owner in enumerate(owners):
            owner_name = owner.get('name', f'事主{idx+1}')
            # 亡命（仙命）：本函数只产出日支真冲 -30 的扣分与明细（文案"须见
            # 吉神制化"），不直接否决；显式三级判定（有制化WARN/无制化VETO/
            # 叠重煞直否）在 calculate_score 主流程执行。亡命不论日柱、不论月时支
            # 冲；流年（冲太岁）见本函数末段：仙命六冲走 [硬性门槛] 否决。
            _is_wm = _is_wangming_role(owner.get('role', ''))

            # 2026-09 作灶主事人模式：辅助者（半权重）冲刑不降否决、扣分减半
            _zz_w = owner.get('_zaozhu_weight', None)
            _zz_w = float(_zz_w) if _zz_w is not None else 1.0
            _zz_sc0 = total_score
            _zz_det0 = len(details)
            # 获取事主生肖（年支）
            owner_year_zhi = ''
            if 'sizhu' in owner:
                sizhu_parts = owner['sizhu'].split()
                if len(sizhu_parts) >= 1:
                    owner_year_zhi = sizhu_parts[0][1]  # 年柱地支
            elif '生肖' in owner:
                owner_year_zhi = owner['生肖']
            
            # 获取事主日柱（从sizhu字段或birth_date计算）
            owner_day_zhi = ''
            if 'sizhu' in owner:
                # owner['sizhu']格式如 "壬寅 癸丑 丁卯 癸卯"
                sizhu_parts = owner['sizhu'].split()
                if len(sizhu_parts) >= 3:
                    owner_day_zhi = sizhu_parts[2][1]  # 日柱地支
            elif 'birth_date' in owner:
                try:
                    from .四柱计算器 import calculate_sizhu
                    owner_sizhu = calculate_sizhu(
                        owner['birth_date'], 
                        owner.get('birth_hour', 12), 
                        owner.get('birth_minute', 0),
                        longitude=owner.get('birth_longitude')
                    )
                    owner_day_zhi = owner_sizhu.get('day_zhi', '')
                    if not owner_year_zhi:
                        owner_year_zhi = owner_sizhu.get('year_zhi', '')
                except Exception as e:
                    logger.error(f"计算事主{owner_name}四柱失败: {str(e)}")
                    pass
            
            try:
                # 首先检查日课日支与事主生肖（年支）的关系（生肖相主，更重要）
                if owner_year_zhi:
                    # 六冲检查（2026-09-18 用户拍板三档口径·档1：
                    # 年命×日课日支六冲，冲主命宫最重 → 硬否决，-30）
                    if check_liuchong(day_zhi, owner_year_zhi):
                        score = -30  # 生肖相冲更严重
                        total_score += score
                        if _is_wm:
                            details.append(f"{owner_name}年命（仙命）{owner_year_zhi}与日课日支{day_zhi}真冲（仙命大忌，须见吉神制化），{score}分")
                        else:
                            details.append(f"[硬性门槛]{owner_name}生肖{owner_year_zhi}与日课日支{day_zhi}六冲（年命六冲），不可用，{score}分")
                    # 自刑检查（三档口径·档3：年命与日课日支辰午酉亥同支自刑。
                    # 辰午酉亥自刑出自《三命通会》三刑之说 → 一票否决，-25）
                    elif day_zhi == owner_year_zhi and day_zhi in ('辰', '午', '酉', '亥'):
                        score = -25
                        total_score += score
                        if _is_wm:
                            details.append(f"{owner_name}年命（仙命）{owner_year_zhi}与日课日支{day_zhi}自刑（须见吉神制化），{score}分")
                        else:
                            details.append(f"[硬性门槛]{owner_name}年命{owner_year_zhi}与日课日支{day_zhi}自刑，不可用，{score}分")
                    # 三刑检查（包括自刑）
                    elif check_xing(day_zhi, owner_year_zhi):
                        score = -25  # 生肖相刑严重
                        total_score += score
                        details.append(f"{owner_name}生肖{owner_year_zhi}与日课日支{day_zhi}相刑（年支刑），{score}分")
                    # 相破检查
                    elif check_po(day_zhi, owner_year_zhi):
                        score = -20  # 生肖相破严重，破坏之象
                        total_score += score
                        details.append(f"{owner_name}生肖{owner_year_zhi}与日课日支{day_zhi}相破（年支破），{score}分")
                    # 六害检查
                    elif check_liuhai(day_zhi, owner_year_zhi):
                        score = -10
                        total_score += score
                        details.append(f"{owner_name}生肖{owner_year_zhi}与日课日支{day_zhi}相害（年支害），{score}分")
                    # 六合检查
                    elif check_liuhe(day_zhi, owner_year_zhi):
                        score = 15
                        total_score += score
                        details.append(f"{owner_name}生肖{owner_year_zhi}与日课日支{day_zhi}相合（年支合），+{score}分")
                    # 三合检查
                    elif check_sanhe([day_zhi, owner_year_zhi]):
                        score = 10
                        total_score += score
                        details.append(f"{owner_name}生肖{owner_year_zhi}与日课日支{day_zhi}三合（年支合），+{score}分")
                
                # 然后检查日课日支与事主日柱地支的关系。
                # 2026-09-18 三档口径：硬否决仅定义在【事主年命】层；事主日元（日支）
                # 与日课日支的冲/自刑降为普通扣分（日元为辅，有制化余地）。
                # 嫁娶另由 _check_marriage_day_chong 独立判"冲夫妻宫"大忌并归零，
                # 不受此处降级影响。
                if owner_day_zhi and owner_day_zhi != owner_year_zhi and not _is_wm:  # 亡命只论年命，不论日柱
                    # 六冲（扣分不否决；-20）
                    if check_liuchong(day_zhi, owner_day_zhi):
                        score = -20
                        total_score += score
                        details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}六冲，{score}分")
                    # 自刑（辰午酉亥同支；扣分不否决，-15）
                    elif day_zhi == owner_day_zhi and day_zhi in ('辰', '午', '酉', '亥'):
                        score = -15
                        total_score += score
                        details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}自刑，{score}分")
                    # 三刑检查
                    elif check_xing(day_zhi, owner_day_zhi):
                        score = -15
                        total_score += score
                        details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}相刑，{score}分")
                    # 相破检查
                    elif check_po(day_zhi, owner_day_zhi):
                        score = -15  # 相破为破坏之象
                        total_score += score
                        details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}相破，{score}分")
                    # 六害检查
                    elif check_liuhai(day_zhi, owner_day_zhi):
                        score = -5
                        total_score += score
                        details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}相害，{score}分")
                    # 六合检查
                    elif check_liuhe(day_zhi, owner_day_zhi):
                        score = 8
                        total_score += score
                        details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}相合，+{score}分")
                    # 伏吟（相同地支）
                    elif day_zhi == owner_day_zhi:
                        score = 3
                        total_score += score
                        details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}相同（伏吟），+{score}分")

                # 三档口径·档2：年命×日课月支/时支六冲 = 扣分不否决。
                # 月为提纲，对齐本函数末段"流年冲太岁"-15 档；时为末位，
                # 对齐既有相害 -10 档。年支档（流年冲太岁）在本函数末段统一处理。
                _xz_mz = sizhu.get('month_zhi', '')
                _xz_hz = sizhu.get('hour_zhi', '')
                if owner_year_zhi and _xz_mz and not _is_wm and check_liuchong(_xz_mz, owner_year_zhi):
                    score = -15
                    total_score += score
                    details.append(f"{owner_name}年命{owner_year_zhi}与日课月支{_xz_mz}六冲（月柱冲年命，扣分不否决），{score}分")
                if owner_year_zhi and _xz_hz and not _is_wm and check_liuchong(_xz_hz, owner_year_zhi):
                    score = -10
                    total_score += score
                    details.append(f"{owner_name}年命{owner_year_zhi}与日课时支{_xz_hz}六冲（时柱冲年命，扣分不否决），{score}分")
            except Exception as e:
                logger.error(f"相主检查失败({owner_name}日支{owner_day_zhi}与日课日支{day_zhi}): {str(e)}")
                pass

            # 辅助事主（半权重）：本主新增扣分减半；[硬性门槛]降为普通扣分项（不否决）
            if _zz_w < 1.0 and total_score != _zz_sc0:
                total_score = _zz_sc0 + _zaozhu_weighted(total_score - _zz_sc0, _zz_w)
                for _zz_i in range(_zz_det0, len(details)):
                    details[_zz_i] = _zaozhu_aux_detail(details[_zz_i], _zz_w)

        # 流年冲太岁检查：日课年柱地支（流年支）与命主年支六冲 → 扣分并提示（年运层面，不否决）
        year_zhi = ''
        try:
            year_zhi = sizhu.get('year_zhi', '') or ''
        except Exception:
            year_zhi = ''
        if year_zhi:
            for idx, owner in enumerate(owners):
                owner_name = owner.get('name', f'事主{idx+1}')
                owner_year_zhi = ''
                if 'sizhu' in owner:
                    _parts = owner['sizhu'].split()
                    if len(_parts) >= 1:
                        owner_year_zhi = _parts[0][1]
                elif '生肖' in owner:
                    owner_year_zhi = owner['生肖']
                if not owner_year_zhi and owner.get('birth_date') and \
                        _is_wangming_role(owner.get('role', '')):
                    # 仅仙命需要 birth_date 解析（冲太岁硬否决）。
                    # 普通事主保持旧口径：只认 sizhu/生肖 键，不在此扩展，
                    # 避免激活历史死档漂移锁定基线（2021金课 事主4 未冲丑）。
                    _osz = calculate_sizhu(owner['birth_date'],
                                           owner.get('birth_hour', 12),
                                           owner.get('birth_minute', 0),
                                           longitude=owner.get('birth_longitude'))
                    owner_year_zhi = _osz.get('year_zhi', '')
                if owner_year_zhi and check_liuchong(year_zhi, owner_year_zhi):
                    if _is_wangming_role(owner.get('role', '')):
                        # 仙命冲流年太岁（岁破级），2026-10-04 用户补授权：硬否决。
                        # 走 [硬性门槛] → xiangzhu_veto_items，sizhu 直传路径与
                        # analyze_year 通道（非直传路径）双保险，口径一致。
                        details.append(f"[硬性门槛]亡命（仙命）{owner_name}年命{owner_year_zhi}"
                                       f"冲流年太岁{year_zhi}（岁破级大忌），不可用")
                        continue
                    _zn_w = owner.get('_zaozhu_weight', None)
                    _zn_w = float(_zn_w) if _zn_w is not None else 1.0
                    score = _zaozhu_weighted(-15, _zn_w)
                    total_score += score
                    details.append(f"[流年冲太岁]{owner_name}年命{owner_year_zhi}与流年{year_zhi}六冲（冲太岁），此年课慎用，{score}分")

        return total_score, details
    
    def _build_wu_xing_breakdown(self, sizhu, owners, event_type=None):
        """构建五行评分明细构成 + 五行分（供一票否决路径也能展示完整基础分构成）。
        2026-09-08：原否决路径只返回空score_breakdown，导致【评分详情】五行评分只显示
        "基础分：100"而缺神煞/宜事/忌事等分项。明细与score解耦：否决仅把score置0，
        构成仍如实展示。返回 (score_breakdown, wu_xing_score)。
        2026-10-01 H1：event_type 传入后，规则 yi/ji 文本命中 H1_ANCHOR_MAP 且当日
        神煞族已注册同名锚点（或属 veto 理由文案）时，该条仅展示不计分。"""
        bd = {
            '基础分': self.base_score,
            '神煞得分': 0,
            '宜事得分': 0,
            '忌事得分': 0,
            '十二长生得分': 0,
            '地支关系得分': 0,
            '纳音匹配得分': 0,
        }
        sc = self.base_score
        for shensha in self.shensha_list:
            s = shensha.get('score', 0) if isinstance(shensha, dict) else 0
            bd['神煞得分'] += s
            sc += s
        # H1：当日神煞族已注册自身分的锚点规则文本 → 仅展示、不计分
        _h1_skip = set()
        if event_type:
            _ss_names = {_s.get('name') for _s in self.shensha_list if isinstance(_s, dict)}
            for _ss_name, _tx in H1_ANCHOR_MAP.get(_canonical_event(event_type), []):
                if _ss_name in _ss_names:
                    _h1_skip.add(_tx)
        for _yi in self.yi_list:
            _t = _yi.get('name', '') if isinstance(_yi, dict) else (
                _yi if isinstance(_yi, str) else str(_yi))
            if _t in _h1_skip:
                continue
            bd['宜事得分'] += 10
            sc += 10
        for _ji in self.ji_list:
            _t = _ji.get('name', '') if isinstance(_ji, dict) else (
                _ji if isinstance(_ji, str) else str(_ji))
            if _t in _h1_skip or _h1_is_veto_reason(_t):
                continue
            bd['忌事得分'] -= 15
            sc -= 15
        if self.ji_list:
            bd['忌事明细'] = list(self.ji_list)
        if HAS_BAZI_TOOLS:
            zs, _zs_lines = self._calc_zhangsheng_detail(sizhu)
            bd['十二长生得分'] = zs; sc += zs
            bd['十二长生明细'] = _zs_lines
            zz, _zz_lines = self._calc_all_zhi_relations_detail(sizhu)
            bd['地支关系得分'] = zz; sc += zz
            bd['地支关系明细'] = _zz_lines
            ny, _ny_lines = self._calculate_nayin_match(sizhu, owners)
            bd['纳音匹配得分'] = ny; sc += ny
            bd['纳音匹配明细'] = _ny_lines
            ods, odd = self._check_owner_day_zhichong(sizhu, owners)
            # 2026-09-14 修正：相主只放明细键，不并入五行 sc——最终总分公式（wu_xing+月令+喜用+相主+黄道+太阳+三煞）会独立累加，并入即双重计分（相主为0时不可见，相主非0时多算15/10/20等）。
            bd['相主得分'] = ods
            # 相主详情入神煞列表供展示（分数已计入相主得分）
            for detail in odd:
                self.shensha_list.append({'name': '相主', 'description': detail, 'score': 0})
        return bd, sc

    def _check_wu_xing(self, sizhu, event_type, owners, house_type, shan_xiang,
                      zaoxiang, zaowei, chuangwei, direction=None, zaozhu_mode=None):
        """
        正五行审核（核心门槛）
        
        Args:
            sizhu: 四柱信息
            event_type: 事项类型
            owners: 事主信息
            house_type: 宅型
            shan_xiang: 山向
            zaoxiang: 灶向
            zaowei: 灶位
            chuangwei: 床位
            
        Returns:
            dict: 五行审核结果
        """
        # 对于修造类事项，尝试使用扩展的检查器（坐山/主命/向/方位）
        if _event_profile(event_type)['construction_ext']:
            try:
                from .shensha import ConstructionShenShaCheckerExt
                # 从山向中提取坐山
                zuoshan = None
                zhuming = None
                
                if shan_xiang:
                    # 山向格式如"子山午向"，提取坐山
                    if '山' in shan_xiang:
                        zuoshan = shan_xiang.split('山')[0].strip()
                
                # 从主事人中提取主命年柱
                if owners and len(owners) > 0:
                    try:
                        from .四柱计算器 import calculate_sizhu
                        owner = owners[0]
                        if 'birth_date' in owner:
                            owner_sizhu = calculate_sizhu(owner['birth_date'],
                                                         owner.get('birth_hour', 12),
                                                         owner.get('birth_minute', 0),
                                                         longitude=owner.get('birth_longitude'))
                            zhuming = owner_sizhu.get('年柱', '')
                    except:
                        pass
                
                shensha_checker = ConstructionShenShaCheckerExt(zuoshan=zuoshan, zhuming=zhuming, direction=direction)
                # 2026-09-16 口径统一：标注规范事项（修造/装修同标准），供基类从分值单一表取数
                shensha_checker._std_event = _canonical_event(event_type)
                self.shensha_list = shensha_checker.check(sizhu, owners, zuoshan=zuoshan, zhuming=zhuming, direction=direction)
            except ImportError:
                # 如果扩展模块导入失败，使用原检查器
                shensha_checker = get_checker(event_type)
                self.shensha_list = shensha_checker.check(sizhu, owners)
        else:
            # 其他事项使用原检查器
            shensha_checker = get_checker(event_type)
            self.shensha_list = shensha_checker.check(sizhu, owners, zaozhu_mode=zaozhu_mode)
        
        # 羊刃计分（冠带派）：日干查地支，单见-15/两见以上-25；所有事项统一，作为通用凶煞
        _yr = self._build_yangren_shensha(sizhu, event_type)
        if _yr and not any(isinstance(_s, dict) and _s.get('name') == '羊刃' for _s in self.shensha_list):
            self.shensha_list.append(_yr)
        
        # 检查宜忌规则
        rule_checker = get_rule_checker(event_type)
        result = rule_checker.check(
            sizhu, owners,
            house_type=house_type,
            shan_xiang=shan_xiang,
            zaoxiang=zaoxiang,
            zaowei=zaowei,
            chuangwei=chuangwei,
            direction=direction,
            zaozhu_mode=zaozhu_mode
        )
        # 处理返回值（支持新老两种格式）
        # 2026-09-02修复：原直接覆盖 self.ji_list/self.yi_list 会丢失此前已计入的
        # 三煞扣分项（三煞扣分在 _check_wu_xing 之前执行），改为合并去重
        if len(result) == 4:
            _rule_yi, _rule_ji, veto, veto_reason = result
        else:
            _rule_yi, _rule_ji = result
            veto, veto_reason = False, ''
        for _y in (_rule_yi or []):
            if _y not in self.yi_list:
                self.yi_list.append(_y)
        for _j in (_rule_ji or []):
            if _j not in self.ji_list:
                self.ji_list.append(_j)

        # 分金/正体大凶一票否决（选定山向时）：修造择日以山家为核心，
        # 分金五行（纳音）受日课四柱克泄至"大凶"，或正向正体大凶，直接否决。
        # 即使规则检查已否决（如岁破日），也评估分金并将原因并列显示
        if shan_xiang:
            try:
                from .二十四山 import ZhengTiWuXingSelectorDB
                _selector = ZhengTiWuXingSelectorDB()
                # shan_xiang 如"乾山巽向兼亥"，解析坐山与兼向
                _shan_name = shan_xiang.split('山')[0].strip() if '山' in shan_xiang else ''
                _sizhu_gz = (
                    f"{sizhu.get('year_gan', '')}{sizhu.get('year_zhi', '')}",
                    f"{sizhu.get('month_gan', '')}{sizhu.get('month_zhi', '')}",
                    f"{sizhu.get('day_gan', '')}{sizhu.get('day_zhi', '')}",
                    f"{sizhu.get('hour_gan', '')}{sizhu.get('hour_zhi', '')}",
                )
                if _shan_name and all(len(gz) == 2 for gz in _sizhu_gz):
                    _fj_reason = ''
                    if '兼' in shan_xiang:
                        _jianxiang = '兼' + shan_xiang.rsplit('兼', 1)[1][:1]
                        _fj = _selector.evaluate_with_fengjin(
                            _shan_name, _jianxiang, *_sizhu_gz,
                            use_fengjin_wuxing=True
                        )
                        if _fj.get('success') and _fj.get('level') in ('大凶', '凶(犯大煞)'):
                            _fj_reason = (
                                f"分金大凶：{_shan_name}山{_jianxiang}第{_fj.get('fengjin_index', '?')}分金"
                                f"{_fj.get('fengjin_ganzhi', '')}（{_fj.get('nayin_name', '')}），"
                                f"日课四柱克泄分金，得分{_fj.get('score', '')}，一票否决"
                            )
                    else:
                        _zt = _selector.evaluate_by_name(_shan_name, *_sizhu_gz)
                        if _zt.get('success') and _zt.get('level') in ('大凶', '凶(犯大煞)'):
                            _fj_reason = (
                                f"正体大凶：{_shan_name}山正体五行受日课四柱克泄"
                                f"（得分{_zt.get('score', '')}），一票否决"
                            )
                    if _fj_reason:
                        if _fj_reason not in self.ji_list:
                            self.ji_list.append(_fj_reason)
                        if veto:
                            veto_reason = f"{veto_reason}；{_fj_reason}"
                        else:
                            veto = True
                            veto_reason = _fj_reason
            except ImportError:
                pass

        # 检查一票否决（规则否决 + 分金/正体大凶否决）
        if veto:
            details = self._generate_wu_xing_details(sizhu, owners)
            details['ji_list'] = self.ji_list
            _bd, _ = self._build_wu_xing_breakdown(sizhu, owners, event_type)
            return {
                'he_ge': False,
                'score': 0,
                'ji_yu': veto_reason,
                'details': details,
                'score_breakdown': _bd,
                'has_deduction': any(_bd.get(k, 0) < 0 for k in ('忌事得分', '神煞得分'))
            }
        
        # 各项得分明细由 _build_wu_xing_breakdown 统一构建（见下方）
        
        # 新增：忌事一票否决机制
        # 只有当忌项精确匹配"忌{事项类型}"时才一票否决
        # 例如："忌修造"、"忌嫁娶"等
        # "建除平日忌修造"或"忌修造动土"不是精确匹配，不会被否决
        for ji in self.ji_list:
            if isinstance(ji, dict):
                ji_text = ji.get('name', '')
            else:
                ji_text = str(ji)
            # 使用正则表达式精确匹配"忌{事项类型}"模式
            # 例如匹配"忌修造"或"忌修造。"但不匹配"建除平日忌修造"
            if re.search(rf'^忌{re.escape(event_type)}[。\s]?$', ji_text):
                # 生成完整的五行分析信息
                details = self._generate_wu_xing_details(sizhu, owners)
                details['ji_list'] = self.ji_list
                _bd, _ = self._build_wu_xing_breakdown(sizhu, owners, event_type)
                return {
                    'he_ge': False,
                    'score': 0,
                    'ji_yu': f"当日忌{event_type}，一票否决",
                    'details': details,
                    'score_breakdown': _bd,
                    'has_deduction': any(_bd.get(k, 0) < 0 for k in ('忌事得分', '神煞得分'))
                }
        
        # 新增：年、月前置条件校验
        year = sizhu.get('year', 0)
        month = sizhu.get('month', 0)
        
        # 尝试从四柱信息中提取年份
        if year == 0:
            # 从年柱中提取年份（这里需要根据实际情况实现）
            # 暂时跳过年、月分析
            pass
        else:
            # 检查是否为四柱输入模式，如果是则跳过基于日期的年、月分析
            if not sizhu.get('is_sizhu_input', False):
                # 分析年份吉凶（传递山向和动土方位用于分析）
                year_analysis = self.analyze_year(
                    year, event_type, owners, shan_xiang, direction=direction,
                    zeli_mode=self._zeli_mode,
                    year_pillar_override=(sizhu.get('year_gan', '')
                                          + sizhu.get('year_zhi', '')) or None)  # _zm0915
                if not year_analysis['suitable']:
                    # 2026-09-10 否决文案只列真实触发项（同月份不宜口径）
                    _ya_info = set(year_analysis.get('info_reasons') or [])
                    _ya_rs = [r for r in year_analysis['reasons'] if r not in _ya_info]
                    _bd, _ = self._build_wu_xing_breakdown(sizhu, owners, event_type)
                    return {
                        'he_ge': False,
                        'score': 0,
                        'ji_yu': f"年份不宜: {'; '.join(_ya_rs)}",
                        'details': year_analysis,
                        'score_breakdown': _bd,
                        'has_deduction': any(_bd.get(k, 0) < 0 for k in ('忌事得分', '神煞得分'))
                    }
                
                # 分析月份吉凶（传递山向和动土方位用于分析）
                # 使用四柱中的月支来确定农历月份，而不是公历月份
                from datetime import date, timedelta
                
                # 获取立春日期（用于确定月序）
                lichun = self._get_solar_term_date(year, '立春')
                
                month_zhi = sizhu.get('month_zhi', '')
                if month_zhi:
                    # 2026-09-03 利月一致性修复：以sizhu.date高精度农历结果
                    # 作为农历月份来源（analyze_month内部同样使用 _resolve_lunar_month 来
                    # 判定大利/小利月），避免腊月/正月交界日节气月支≠实际农历月导致错位。
                    lunar_month = self._resolve_lunar_month(sizhu)

                    # 使用精确节气边界计算该农历月的代表性日期
                    month_date = self._get_month_representative_date(year, lunar_month)
                else:
                    # 如果没有月支信息，使用公历月份作为近似
                    # 公历月份到节气月序号的近似映射
                    approx_month_order = max(1, min(12, month - 2))  # 公历1月≈丑月(12), 公历3月≈寅月(1)
                    month_date = self._get_month_representative_date(year, approx_month_order)
                
                month_analysis = self.analyze_month(month_date, event_type, owners, shan_xiang, direction,
                                                    day_sizhu=sizhu, zeli_mode=self._zeli_mode)  # _zm0915
                if not month_analysis['suitable']:
                    # 2026-09-10 否决文案只列真实触发项：纯方位信息项（年三煞在X方/太岁在X方/
                    # 岁破在X方/月三煞在X方，未临坐山/动土方不否决）不再混入否决理由
                    _ma_info = set(month_analysis.get('info_reasons') or [])
                    # _fc0915：六合/三合为吉象，不属月份不宜理由，从否决文案剔除
                    _ma_rs = [r for r in month_analysis['reasons']
                              if r not in _ma_info
                              and not any(_k in r for _k in ('六合', '三合'))]
                    _bd, _ = self._build_wu_xing_breakdown(sizhu, owners, event_type)
                    return {
                        'he_ge': False,
                        'score': 0,
                        'ji_yu': f"月份不宜: {'; '.join(_ma_rs)}",
                        'details': month_analysis,
                        'score_breakdown': _bd,
                        'has_deduction': any(_bd.get(k, 0) < 0 for k in ('忌事得分', '神煞得分'))
                    }
        
        # 五行评分与明细由下方 _build_wu_xing_breakdown 统一计算
        
        # 尝试导入 calculate_sizhu
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
        
        # 对于嫁娶，检查大利月、小利月（基于具体日期的月支）
        if _event_profile(event_type)['liyue'] and owners:
            for owner in owners:
                if owner.get('role') == '新娘' or owner.get('性别') == '女':
                    # 计算新娘年支
                    if 'birth_date' in owner:
                        owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                                   owner.get('birth_hour', 12), 
                                                   owner.get('birth_minute', 0),
                                                   longitude=owner.get('birth_longitude'))
                        bride_year_zhi = owner_sizhu.get('year_zhi', '')
                        
                        # 2026-02-05 修正：当前农历月份以具体日期高精度农历转换为准，
                        # 不再用节气月支法（寅=1丑=12）代推，避免2026-02-05这类
                        # "节气寅月但农历腊月"的交界日被误判为大利月。
                        lunar_month = self._resolve_lunar_month(sizhu)
                        
                        # 检查大利月、小利月
                        month_type = self._check_li_yue(bride_year_zhi, lunar_month)
                        if month_type == '大利月':
                            self.shensha_list.append({
                                'name': '大利月',
                                'description': f'新娘大利月（农历{lunar_month}月）',
                                'score': 30
                            })
                        elif month_type == '小利月':
                            self.shensha_list.append({
                                'name': '小利月',
                                'description': f'新娘小利月（农历{lunar_month}月）',
                                'score': 15
                            })
                        elif month_type == '妨夫月':
                            self.shensha_list.append({
                                'name': '妨夫月',
                                'description': '妨夫月',
                                'score': -25
                            })
                        elif month_type == '妨妻月':
                            self.shensha_list.append({
                                'name': '妨妻月',
                                'description': '妨妻月',
                                'score': -25
                            })
        
        # 统一构建五行评分明细与五行分（含神煞/宜事/忌事/十二长生/地支/纳音；相主仅入明细键，不计入五行分）
        score_breakdown, wu_xing_score = self._build_wu_xing_breakdown(sizhu, owners, event_type)
        
        # 判断五行是否合格
        he_ge = wu_xing_score >= 60  # 五行评分低于60分为不合格
        
        # 判断是否有扣分项(忌事、凶神煞等)
        has_deduction = (score_breakdown['忌事得分'] < 0) or (score_breakdown['神煞得分'] < 0)
        
        # 生成五行评语
        ji_yu = self._generate_wu_xing_jiyu(wu_xing_score, he_ge)
        
        # 生成详细的五行分析信息
        details = self._generate_wu_xing_details(sizhu, owners)
        
        return {
            'he_ge': he_ge,
            'score': wu_xing_score,
            'ji_yu': ji_yu,
            'details': details,
            'score_breakdown': score_breakdown,
            'has_deduction': has_deduction
        }
    
    def _generate_wu_xing_jiyu(self, score, he_ge):
        """
        生成五行评语
        
        Args:
            score: 五行评分
            he_ge: 是否合格
            
        Returns:
            str: 五行评语
        """
        if not he_ge:
            base = '五行严重不合格，犯大忌，坚决不用'
            # 2026-09-11：犯忌文案只列真实硬否决项；三煞临四柱（山向类扣分不否决）、
            # 带"（有制化：…）"标记项及普通扣分忌项不得写成"大忌"，避免与
            # 二十四山窗口"扣分不否决"、山家警告"有制化不禁用"自相矛盾。
            _hard_items, _soft_items = [], []
            _spv_mode = getattr(self, '_pillar_veto_mode', True)
            for _j in self.ji_list:
                _t = str(_j)
                if '（有制化：' in _t:
                    _soft_items.append(_t)
                elif (not _spv_mode) and self._is_pillar_sansha_item(_t):
                    _soft_items.append(_t)
                elif any(re.search(_k, _t) for _k in self._HARD_VETO_KEYWORDS):
                    _hard_items.append(_t)
                else:
                    _soft_items.append(_t)
            if _hard_items:
                shown = '、'.join(str(x) for x in _hard_items[:3])
                if len(_hard_items) > 3:
                    shown += '等'
                base += f'（大忌：{shown}）'
                if _soft_items:
                    base += (f'；另有{len(_soft_items)}项为扣分或已有制化项，'
                             f'按扣分处理，不单独否决')
            else:
                base += (f'（五行总分{score}分，未达60分合格门槛；忌项均为临方扣分'
                         f'不否决项或已有吉神制化项，不单独构成大忌）')
            return base
        elif score >= 120:
            return '五行大吉，旺相无碍'
        elif score >= 100:
            return '五行吉日，诸事皆宜'
        elif score >= 80:
            return '五行中吉，可用'
        elif score >= 60:
            return '五行平平，仅适合小事'
        else:
            return '五行凶日，不宜使用'

    def _calculate_feixing_score(self, sizhu, full_shan_xiang):
        """玄空飞星加减分——统一调用 modules/玄空飞星引擎.py（单一数据源）。

        历史上本方法手抄飞星常量与冬至/夏至排盘，与玄空飞星_日课展示.py
        各自维护、靠注释"保持一致"维系，极易漂移。现排盘/坐山分析/数值
        评分全部收敛到引擎纯函数，评分器与玄空九宫窗口共用同一标准。
        返回 {feixing_score(-20~+20), feixing_level, feixing_details,
        feixing_comment, feixing_stars, feixing_star_count}；数据不足返回 None。
        """
        try:
            from .玄空飞星引擎 import score_feixing
        except ImportError:
            from 玄空飞星引擎 import score_feixing
        return score_feixing(sizhu, full_shan_xiang)

    # 羊刃（冠带派）日干→地支映射：甲卯乙辰丙午丁未戊午己未庚酉辛戌壬子癸丑
    _YANGREN_MAP = {
        '甲': '卯', '乙': '辰', '丙': '午', '丁': '未',
        '戊': '午', '己': '未', '庚': '酉', '辛': '戌',
        '壬': '子', '癸': '丑',
    }

    def _build_yangren_shensha(self, sizhu, event_type):
        """构建羊刃神煞计分条目（冠带派，日干查地支）。

        单见：分值取 SHENSHA_SCORES[('*','羊刃')] = -15；
        两见以上：-25。典籍依据：羊刃为刚暴之星，传统命理以"喜一位而忌重见"
        为常说（《三命通会》论羊刃以一位为用、重见则招非致祸；旧注《五行精纪》
        亦以刃多为忌），故重见按重煞论，分值取与劫煞/灾煞单犯同档的 -25。
        2026-09-18 用户拍板（口径B）：保留两见加重并补此典籍注释。
        说明（2026-09-18 核对）：劫煞/灾煞按日支单查，结构上不会两见，
        -25 并非"对齐其两见规则"，而是"羊刃重见 ≈ 一次劫煞级别"的分量对齐。
        无命中返回 None。仅在评分器内调用，不改任何现有神煞分值。
        """
        day_zhu = sizhu.get('日柱', '')
        day_gan = day_zhu[0] if len(day_zhu) >= 1 else sizhu.get('day_gan', '')
        target = self._YANGREN_MAP.get(day_gan)
        if not target:
            return None
        zhis = []
        for pn in ('年柱', '月柱', '日柱', '时柱'):
            p = sizhu.get(pn, '')
            if len(p) >= 2:
                zhis.append((pn, p[1]))
        hits = [(pn, z) for pn, z in zhis if z == target]
        if not hits:
            return None
        try:
            from .事项标准 import shensha_score as _ss
        except ImportError:
            from 事项标准 import shensha_score as _ss
        base = _ss(_canonical_event(event_type), '羊刃', -15)
        score = base if len(hits) == 1 else -25  # 两见以上：重见按重煞论（典籍"刃喜一位忌重见"），取劫煞/灾煞单犯分量 -25
        desc = '、'.join(f"{pn}{z}" for pn, z in hits)
        return {
            'name': '羊刃',
            'score': score,
            'description': f"羊刃（日干{day_gan}见{desc}）",
        }

    def _generate_wu_xing_details(self, sizhu, owners, is_demo_hour=True):
        """
        生成详细的五行分析信息
        
        包括：
        1. 天干地支五行分析
        2. 地支关系（三合、六合、六冲、六害、三刑、相破）
        3. 十二长生状态
        4. 纳音五行
        5. 吉神（天德、月德、天乙、文昌、福星、禄神等）
        6. 日主旺衰分析
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            
        Returns:
            dict: 详细分析信息
        """
        details = {
            '天干五行': {},
            '地支关系': [],
            '十二长生': {},
            '纳音五行': {},
            '吉神': [],
            '凶煞': [],
            '日主旺衰': '',
            '五行生克': []
        }
        
        # 1. 天干地支五行分析
        gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', 
                      '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
        zhi_wuxing = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
                      '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金', 
                      '戌': '土', '亥': '水'}
        
        for pillar_name, pillar_key in [('年柱', 'year'), ('月柱', 'month'), 
                                         ('日柱', 'day'), ('时柱', 'hour')]:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) >= 2:
                gan, zhi = pillar[0], pillar[1]
                details['天干五行'][pillar_name] = {
                    '天干': gan,
                    '天干五行': gan_wuxing.get(gan, '未知'),
                    '地支': zhi,
                    '地支五行': zhi_wuxing.get(zhi, '未知')
                }
        
        # 2. 地支关系分析
        zhis = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) >= 2:
                zhis.append((pillar_name, pillar[1]))
        
        # 三合局（2026-09-01 术语规范）：
        #   三支齐备 = 三合X局（支1, 支2, 支3）
        #   两支按宫位区分——生地半合=长生+帝旺（力强）、墓地半合=帝旺+墓（力弱）、
        #   拱合=长生+墓（如亥未、寅戌、申辰、巳丑，不称半合）
        sanhe_groups = {
            '申子辰': '水局', '寅午戌': '火局', '巳酉丑': '金局', '亥卯未': '木局'
        }
        # 三合局内各支宫位索引：0=长生(生地)、1=帝旺(旺地)、2=墓(墓地)
        sanhe_pos = {}
        for _g, _j in sanhe_groups.items():
            for _i, _z in enumerate(_g):
                sanhe_pos[_z] = (_g, _i)
        zhi_list = [z[1] for z in zhis]
        from collections import Counter
        zhi_counter = Counter(zhi_list)

        for group, ju in sanhe_groups.items():
            # 获取该组中存在的不同地支
            present_zhis = [z for z in group if z in zhi_counter]
            unique_count = len(present_zhis)
            total_count = sum(zhi_counter[z] for z in present_zhis)

            if unique_count == 3:
                # 三支齐备（2026-09-01 用户规范：主体在前+列齐三支）："年柱亥、日柱未、时柱卯 三合木局（亥卯未）"
                _cols = '、'.join([z[0]+z[1] for z in zhis if z[1] in group])
                details['地支关系'].append(f"{_cols} 三合{ju}（{''.join(group)}）")
            elif unique_count == 2:
                # 两个不同地支：按宫位区分生地半合(长生+帝旺)/墓地半合(帝旺+墓)/拱合(长生+墓)
                missing_zhi = [z for z in group if z not in zhi_counter][0]
                _pos = sorted(sanhe_pos[z][1] for z in present_zhis)
                _za = '、'.join([z[0]+z[1] for z in zhis if z[1] == present_zhis[0]])
                _zb = '、'.join([z[0]+z[1] for z in zhis if z[1] == present_zhis[1]])
                _pair = f"{_za} 与 {_zb}"
                if _pos == [0, 1]:
                    # 生地半合（长生+帝旺），力量较强
                    details['地支关系'].append(f"{_pair} 半合{ju}（缺{missing_zhi}）")
                elif _pos == [1, 2]:
                    # 墓地半合（帝旺+墓），力量较弱
                    details['地支关系'].append(f"{_pair} 半合{ju}（缺{missing_zhi}）")
                else:
                    # 生地+墓（长生+墓库）：拱合，不称半合
                    details['地支关系'].append(f"{_pair} 拱合{ju}（拱{missing_zhi}）")

        # 伏吟/自刑（独立检测以免漏报）：同一地支出现多次——
        #   两柱干支完全相同 = 伏吟；仅地支相同：辰午酉亥同支为自刑，
        #   其余八支同支为地支伏吟（非刑）。2026-09-10 纠正旧“凡同支皆自刑”误判（寅寅不刑）。
        for zhi, _cnt in zhi_counter.items():
            if _cnt < 2:
                continue
            _pillars = [(pn, sizhu.get(pn, '')) for pn, zz in zhis if zz == zhi]
            for _a in range(len(_pillars)):
                for _b in range(_a + 1, len(_pillars)):
                    _na, _pa = _pillars[_a]
                    _nb, _pb = _pillars[_b]
                    if _pa and _pb and _pa == _pb:
                        details['地支关系'].append(f"{_na}{_pa} 与 {_nb}{_pb} 伏吟")
                    elif zhi in ('辰', '午', '酉', '亥'):
                        details['地支关系'].append(f"{_na}{zhi} 与 {_nb}{zhi} 自刑（{zhi}{zhi}自刑）")
                    else:
                        details['地支关系'].append(f"{_na}{zhi} 与 {_nb}{zhi} 伏吟（{zhi}{zhi}伏吟）")
        
        # 六合（2026-09-01 用户规范：必须带主体，如"月柱午 与 日柱未 六合（午未合）"）
        liuhe_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'),
                       ('辰', '酉'), ('巳', '申'), ('午', '未')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuhe_pairs or (z2, z1) in liuhe_pairs:
                    _n = f"{z1}{z2}" if (z1, z2) in liuhe_pairs else f"{z2}{z1}"
                    details['地支关系'].append(f"{z1_name}{z1} 与 {z2_name}{z2} 六合（{_n}合）")

        # 六冲（2026-09-01 用户规范：必须带主体，如"年柱子 冲 日柱午（子午冲）"）
        liuchong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'),
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuchong_pairs or (z2, z1) in liuchong_pairs:
                    _n = f"{z1}{z2}" if (z1, z2) in liuchong_pairs else f"{z2}{z1}"
                    details['地支关系'].append(f"{z1_name}{z1} 冲 {z2_name}{z2}（{_n}冲）")

        # 六害（2026-09-01 用户规范：必须带主体，如"年柱酉 与 月柱戌 六害（酉戌害）"）
        liuhai_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'),
                        ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuhai_pairs or (z2, z1) in liuhai_pairs:
                    _n = f"{z1}{z2}" if (z1, z2) in liuhai_pairs else f"{z2}{z1}"
                    details['地支关系'].append(f"{z1_name}{z1} 与 {z2_name}{z2} 六害（{_n}害）")

        # 三刑（必须是不同地支才能构成三刑；2026-09-01 用户规范：主体在前）
        sanxing_groups = [
            (['寅', '巳', '申'], '无恩之刑'),
            (['丑', '戌', '未'], '恃势之刑'),
            (['子', '卯'], '无礼之刑')
        ]
        for group, name in sanxing_groups:
            # 获取该组中存在的不同地支
            present_zhis = set(z for z in zhi_list if z in group)
            unique_count = len(present_zhis)
            # 三刑需要至少两个不同的地支
            if unique_count >= 2:
                _sx_cols = '、'.join([z[0]+z[1] for z in zhis if z[1] in present_zhis])
                _sx_name = ''.join(z for z in group if z in present_zhis)
                details['地支关系'].append(f"{_sx_cols} 三刑-{name}（{_sx_name}）")

        # （自刑/伏吟已在前方独立段统一检测，避免与三合/半合分支互斥而漏报）
        
        # 3. 十二长生状态
        # 日干兼容中文键结构（权威四柱/推荐时柱注入后），否则整段跳过漏报
        _dz_pillar = sizhu.get('日柱', '')
        day_gan = _dz_pillar[0] if len(_dz_pillar) >= 1 else sizhu.get('day_gan', '')
        if day_gan and HAS_BAZI_TOOLS:
            for pillar_name, pillar_key in [('年柱', 'year'), ('月柱', 'month'), 
                                             ('日柱', 'day'), ('时柱', 'hour')]:
                pillar = sizhu.get(pillar_name, '')
                if len(pillar) >= 2:
                    zhi = pillar[1]
                    try:
                        state = get_zhangsheng(day_gan, zhi)
                        details['十二长生'][pillar_name] = state
                    except:
                        pass
        
        # 4. 纳音五行
        if HAS_BAZI_TOOLS:
            for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
                pillar = sizhu.get(pillar_name, '')
                if len(pillar) >= 2:
                    try:
                        nayin = get_nayin(pillar)
                        details['纳音五行'][pillar_name] = nayin
                    except:
                        pass
        
        # 5. 天德、月德贵人
        month_zhu = sizhu.get('月柱', '')
        month_zhi = month_zhu[1] if len(month_zhu) > 1 else ''
        day_zhu = sizhu.get('日柱', '')
        # 日干取值兼容两种键结构（2026-09-02修复：权威四柱/推荐时柱注入后为中文键
        # {'年柱','月柱','日柱','时柱'}，原 sizhu.get('day_gan') 取不到导致天德/月德漏报）
        day_gan = day_zhu[0] if len(day_zhu) >= 1 else sizhu.get('day_gan', '')
        day_zhi = day_zhu[1] if len(day_zhu) > 1 else ''
        
        # 天德贵人查法（以月支查日干/日支，维度感知）
        # 2026-09-19 锚点③漏网副本修复：本表 8 干型月（丁/壬/辛/甲/癸/丙/乙/庚）
        # 比日干；4 地支型四维月（卯→申、午→亥、酉→寅、子→巳，四维卦取宫内
        # 后位地支）须比日支。旧码一律比日干导致这 4 个月天德贵人详情永不显示
        # （与 shensha 层 1889a1e 同一维度 bug，本详情层为展示口径，不参与计分）。
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
        }
        if month_zhi in tiande_map:
            tdv = tiande_map[month_zhi]
            if tdv in ('子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'):
                if day_zhi == tdv:
                    details['吉神'].append(f"天德贵人: 月支{month_zhi}见日支{day_zhi}")
            elif day_gan == tdv:
                details['吉神'].append(f"天德贵人: 月支{month_zhi}见日干{day_gan}")
        
        # 月德贵人查法（以月支查日干）
        # 三合局规则：寅午戌月丙，申子辰月壬，亥卯未月甲，巳酉丑月庚
        yuede_map = {
            '寅': '丙', '卯': '甲', '辰': '壬', '巳': '庚',
            '午': '丙', '未': '甲', '申': '壬', '酉': '庚',
            '戌': '丙', '亥': '甲', '子': '壬', '丑': '庚'
        }
        if month_zhi in yuede_map and day_gan == yuede_map[month_zhi]:
            details['吉神'].append(f"月德贵人: 月支{month_zhi}见日干{day_gan}")
        
        # 6. 天乙贵人查法（以日干查地支）
        tianyi_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'],
            '丁': ['亥', '酉'], '戊': ['丑', '未'], '己': ['子', '申'],
            '庚': ['丑', '未'], '辛': ['寅', '午'], '壬': ['卯', '巳'],
            '癸': ['卯', '巳']
        }
        if day_gan in tianyi_map:
            for zhi_name, zhi in zhis:
                if zhi in tianyi_map[day_gan]:
                    details['吉神'].append(f"天乙贵人: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 7. 文昌贵人查法（以日干查地支）
        wenchang_map = {
            '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
            '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
            '壬': '寅', '癸': '卯'
        }
        if day_gan in wenchang_map:
            for zhi_name, zhi in zhis:
                if zhi == wenchang_map[day_gan]:
                    details['吉神'].append(f"文昌贵人: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 8. 福星贵人查法（以日干查地支）
        # 歌诀：甲丙庚寅子，乙癸卯丑寻，戊申己未位，丁亥庚午存，辛巳壬逢辰
        # 来源：百度百科、《钦定协纪辨方书》
        # 注：2026-09-18 内部一致性修正——旧表'辛':'戌'与自身歌诀"辛巳"矛盾，
        # 统一为歌诀值'辛':'巳'（典籍版本不锁定，仅消除内部矛盾）。
        fuxing_map = {
            '甲': '寅', '乙': '卯', '丙': '子', '丁': '亥',
            '戊': '申', '己': '未', '庚': '午', '辛': '巳',
            '壬': '辰', '癸': '丑'
        }
        if day_gan in fuxing_map:
            for zhi_name, zhi in zhis:
                if zhi == fuxing_map[day_gan]:
                    details['吉神'].append(f"福星贵人: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 9. 禄神查法（以日干查地支）
        lushen_map = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '子'
        }
        if day_gan in lushen_map:
            for zhi_name, zhi in zhis:
                if zhi == lushen_map[day_gan]:
                    details['吉神'].append(f"禄神: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 9.5 羊刃查法（以日干查地支，冠带派）
        # 甲卯、乙辰、丙午、丁未、戊午、己未、庚酉、辛戌、壬子、癸丑
        yangren_map = {
            '甲': '卯', '乙': '辰', '丙': '午', '丁': '未',
            '戊': '午', '己': '未', '庚': '酉', '辛': '戌',
            '壬': '子', '癸': '丑',
        }
        if day_gan in yangren_map:
            for zhi_name, zhi in zhis:
                if zhi == yangren_map[day_gan]:
                    details['凶煞'].append(f"羊刃: 日干{day_gan}见{zhi_name}{zhi}")
        
        # 10. 日主旺衰分析
        if day_gan and month_zhi:
            wangxiang_table = {
                '甲': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], 
                      '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                '乙': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], 
                      '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
                '丙': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], 
                      '囚': ['申', '酉'], '死': ['亥', '子']},
                '丁': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], 
                      '囚': ['申', '酉'], '死': ['亥', '子']},
                '戊': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], 
                      '囚': ['亥', '子'], '死': ['寅', '卯']},
                '己': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], 
                      '囚': ['亥', '子'], '死': ['寅', '卯']},
                '庚': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], 
                      '囚': ['寅', '卯'], '死': ['巳', '午']},
                '辛': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], 
                      '囚': ['寅', '卯'], '死': ['巳', '午']},
                '壬': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], 
                      '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
                '癸': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], 
                      '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']}
            }
            
            if day_gan in wangxiang_table:
                table = wangxiang_table[day_gan]
                if month_zhi in table['旺']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中得令而旺"
                elif month_zhi in table['相']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中得生而相"
                elif month_zhi in table['休']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中休囚"
                elif month_zhi in table['囚']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中受克而囚"
                elif month_zhi in table['死']:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中受克而死"
                else:
                    details['日主旺衰'] = f"日主{day_gan}在月令{month_zhi}中状态一般"
        
        # 7. 五行生克分析
        # 天干相生
        sheng_relations = [
            ('木', '火', '木生火'), ('火', '土', '火生土'),
            ('土', '金', '土生金'), ('金', '水', '金生水'), ('水', '木', '水生木')
        ]
        # 天干相克
        ke_relations = [
            ('木', '土', '木克土'), ('土', '水', '土克水'),
            ('水', '火', '水克火'), ('火', '金', '火克金'), ('金', '木', '金克木')
        ]
        
        gan_list = []
        for pillar_name in ['年柱', '月柱', '日柱', '时柱']:
            pillar = sizhu.get(pillar_name, '')
            if len(pillar) >= 1:
                gan = pillar[0]
                if gan in gan_wuxing:
                    gan_list.append((pillar_name, gan, gan_wuxing[gan]))
        
        for i in range(len(gan_list)):
            for j in range(i + 1, len(gan_list)):
                p1, g1, w1 = gan_list[i]
                p2, g2, w2 = gan_list[j]
                # 检查相生（强制对齐方向：实际谁生谁就在字符串里写在前）
                for s1, s2, desc in sheng_relations:
                    if w1 == s1 and w2 == s2:
                        details['五行生克'].append(f"{desc}: {p1}{g1}({w1})与{p2}{g2}({w2})")
                    elif w2 == s1 and w1 == s2:
                        # 方向反过来：实际是 p2 五行生 p1 五行
                        details['五行生克'].append(f"{desc}: {p2}{g2}({w2})与{p1}{g1}({w1})")
                # 检查相克（强制对齐方向：谁是克方谁在前，避免 VII 报告「木克土：月柱己(土)克日柱乙(木)」方向写反）
                for k1, k2, desc in ke_relations:
                    if w1 == k1 and w2 == k2:
                        details['五行生克'].append(f"{desc}: {p1}{g1}({w1})克{p2}{g2}({w2})")
                    elif w2 == k1 and w1 == k2:
                        # 实际是 p2 五行克 p1 五行（修 VII 方向颠倒）
                        details['五行生克'].append(f"{desc}: {p2}{g2}({w2})克{p1}{g1}({w1})")

        # 涉及时柱的地支关系行加注：时柱为示例时辰（默认午时），评分不含时柱因素
        # （六害/三刑/内部合局检查均以 hour_zhi='' 副本排除示例时柱），
        # 故涉及时柱的关系（半合/六合/六冲/六害/三刑/自刑）仅作展示、不计分。
        # 2026-09-08：主程序注入推荐时柱后传 is_demo_hour=False，时柱为权威
        # 推荐柱、其关系已由时柱关系得分计分，不再加“示例”标注。
        if is_demo_hour:
            details['地支关系'] = [
                (ln + '（示例时柱，不计分）') if '时柱' in ln else ln
                for ln in details['地支关系']
            ]
        return details
    
    def _calc_zhangsheng_detail(self, sizhu):
        """各柱十二长生状态明细（2026-09-10：解决“十二长生得分无明细不可追溯”）。
        与原 _calculate_zhangsheng_score 同一得分表（长生8/沐浴4/冠带6/临官10/
        帝旺12/衰2/病-2/死-6/墓-4/绝-8/胎3/养5），月令柱×1.5。
        Returns: (score:int, lines:list[str])
            行格式：年柱巳·临官：+10分 / 月柱戌·墓：-4分×1.5=-6分
        """
        score = 0
        lines = []
        if not HAS_BAZI_TOOLS:
            return score, lines
        day_gan = sizhu.get('day_gan', '')
        if not day_gan:
            return score, lines
        zhangsheng_scores = {
            '长生': 8, '沐浴': 4, '冠带': 6, '临官': 10,
            '帝旺': 12, '衰': 2, '病': -2, '死': -6,
            '墓': -4, '绝': -8, '胎': 3, '养': 5
        }
        for pillar, cn in (('year', '年柱'), ('month', '月柱'),
                           ('day', '日柱'), ('hour', '时柱')):
            zhi = sizhu.get(f'{pillar}_zhi', '')
            if not zhi:
                continue
            try:
                state = get_zhangsheng(day_gan, zhi)
            except Exception:
                continue
            base = zhangsheng_scores.get(state)
            if base is None:
                continue
            if pillar == 'month':
                val = int(base * 1.5)
                lines.append(f"{cn}{zhi}·{state}：{base:+d}分×1.5={val:+d}分")
            else:
                val = base
                lines.append(f"{cn}{zhi}·{state}：{val:+d}分")
            score += val
        return score, lines

    def _calculate_zhangsheng_score(self, sizhu):
        """日主在各柱十二长生状态评分（明细见 _calc_zhangsheng_detail）"""
        return self._calc_zhangsheng_detail(sizhu)[0]

    def _banhe_pos_label(self, z1, z2):
        """两支半合的宫位命名（生地半合/墓地半合/拱合X局），
        与 _calc_hour_zhi_relations_detail 同一口径；非同一三合局两支返回None。"""
        _sg = (('申', '子', '辰'), ('寅', '午', '戌'),
               ('巳', '酉', '丑'), ('亥', '卯', '未'))
        _g = next((g for g in _sg if z1 in g and z2 in g and z1 != z2), None)
        if not _g:
            return None
        _ju = {'申子辰': '水', '寅午戌': '火',
               '巳酉丑': '金', '亥卯未': '木'}[''.join(_g)]
        _pos = sorted((_g.index(z1), _g.index(z2)))
        if _pos == [0, 1]:
            return '生地半合%s局' % _ju
        if _pos == [1, 2]:
            return '墓地半合%s局' % _ju
        return '拱合%s局' % _ju

    def _calc_all_zhi_relations_detail(self, sizhu):
        """四柱六对全局地支关系明细（2026-09-10：解决“地支关系得分+4与
        时柱关系-2无法对账”）。规则/分值与 _calculate_zhizhi_relations 完全一致：
        六合+8/半合+6/六冲-15/六害-6/相刑-8/相破-4；同支非自刑为伏吟（0分不计分）。
        时柱参与的关系行尾注“（时柱参与）”，便于与时柱关系块对账：
        全局合计 = 年月日三柱关系 + 时柱参与。Returns: (score:int, lines:list[str])
        """
        score = 0
        lines = []
        if not HAS_BAZI_TOOLS:
            return score, lines
        pillars = []
        for key, cn in (('year_zhi', '年支'), ('month_zhi', '月支'),
                        ('day_zhi', '日支'), ('hour_zhi', '时支')):
            z = sizhu.get(key, '')
            if z:
                pillars.append((cn, z))
        for i in range(len(pillars)):
            for j in range(i + 1, len(pillars)):
                n1, z1 = pillars[i]
                n2, z2 = pillars[j]
                _hour_tag = '（时柱参与）' if ('时支' in (n1, n2)) else ''
                try:
                    seg = []
                    if check_liuhe(z1, z2):
                        score += 8
                        seg.append('六合（%s%s合）：+8分' % (z1, z2))
                    else:
                        is_banhe, _bn = self._check_banhe(z1, z2)
                        if is_banhe:
                            score += 6
                            _lb = self._banhe_pos_label(z1, z2) or _bn or '半合'
                            seg.append('%s：+6分' % _lb)
                    if check_liuchong(z1, z2):
                        score -= 15
                        seg.append('六冲（%s%s冲）：-15分' % (z1, z2))
                    elif check_liuhai(z1, z2):
                        score -= 6
                        seg.append('六害（%s%s害）：-6分' % (z1, z2))
                    else:
                        _xing = check_xing(z1, z2)
                        if _xing:
                            score -= 8
                            seg.append('相刑（%s，%s%s刑）：-8分' % (_xing, z1, z2))
                        elif check_po(z1, z2):
                            score -= 4
                            seg.append('相破（%s%s破）：-4分' % (z1, z2))
                    if z1 == z2 and not check_xing(z1, z2):
                        seg.append('伏吟（%s%s伏吟，0分不计分）' % (z1, z2))
                    for _s in seg:
                        lines.append('%s%s 与 %s%s %s%s' % (n1, z1, n2, z2, _s, _hour_tag))
                except Exception:
                    pass
        return score, lines
    
    def _check_banhe(self, zhi1, zhi2):
        """
        检查两个地支是否构成半合（属于同一三合局且不是相同地支）
        
        Args:
            zhi1: 地支1
            zhi2: 地支2
            
        Returns:
            bool: 是否为半合
            str: 半合局名称（如"半合水局"）
        """
        # 相同地支不算半合，是伏吟
        if zhi1 == zhi2:
            return False, None
        
        # 三合局定义
        sanhe_groups = {
            '水局': ['申', '子', '辰'],
            '木局': ['亥', '卯', '未'],
            '火局': ['寅', '午', '戌'],
            '金局': ['巳', '酉', '丑']
        }
        
        for ju_name, zhiz in sanhe_groups.items():
            if zhi1 in zhiz and zhi2 in zhiz:
                return True, f"半合{ju_name}"
        
        return False, None
    
    def _calculate_zhizhi_relations(self, sizhu):
        """
        分析日课四柱内部地支关系（冲合刑害）的评分
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 地支关系评分
        """
        score = 0
        
        # 检查八字工具整合模块是否可用
        if not HAS_BAZI_TOOLS:
            return score
        
        # 获取各柱地支
        zhis = []
        for pillar in ['year', 'month', 'day', 'hour']:
            zhi_key = f'{pillar}_zhi'
            if zhi_key in sizhu:
                zhis.append(sizhu[zhi_key])
        
        # 分析所有地支两两关系
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                zhi1 = zhis[i]
                zhi2 = zhis[j]
                
                try:
                    # 六合
                    if check_liuhe(zhi1, zhi2):
                        score += 8
                    # 半合（三合局中任意两个不同地支）
                    else:
                        is_banhe, banhe_name = self._check_banhe(zhi1, zhi2)
                        if is_banhe:
                            score += 6
                    # 六冲
                    if check_liuchong(zhi1, zhi2):
                        score -= 15
                    # 六害
                    elif check_liuhai(zhi1, zhi2):
                        score -= 6
                    # 相刑
                    elif check_xing(zhi1, zhi2):
                        score -= 8
                    # 相破
                    elif check_po(zhi1, zhi2):
                        score -= 4
                except Exception as e:
                    logger.error(f"地支关系计算失败({zhi1}, {zhi2}): {str(e)}")
                    pass
        
        return score

    def _calc_hour_zhi_relations_detail(self, sizhu):
        """
        时支与年/月/日支的关系明细（单一数据源）。

        规则/分值与 _calculate_zhizhi_relations 完全一致（六合+8、半合+6、六冲-15、
        六害-6、相刑-8、相破-4），仅把"时柱参与的三对关系"单独拆出展示。
        该分数本就含在"五行评分·地支关系得分"内，不再重复累加。

        Returns:
            (score:int, details:list[str])
        """
        score = 0
        lines = []
        if not HAS_BAZI_TOOLS:
            return score, lines
        hz = sizhu.get('hour_zhi', '') if isinstance(sizhu, dict) else ''
        if not hz:
            return score, lines
        pairs = [('年支', sizhu.get('year_zhi', '')),
                 ('月支', sizhu.get('month_zhi', '')),
                 ('日支', sizhu.get('day_zhi', ''))]
        for nm, z in pairs:
            if not z:
                continue
            try:
                # 合（六合优先，否则半合）
                if check_liuhe(hz, z):
                    score += 8
                    lines.append(f"六合：时支{hz}合{nm}{z}：+8分")
                else:
                    is_banhe, banhe_name = self._check_banhe(hz, z)
                    if is_banhe:
                        score += 6
                        _bh = banhe_name or '半合'
                        _sg = (('申', '子', '辰'), ('寅', '午', '戌'), ('巳', '酉', '丑'), ('亥', '卯', '未'))
                        _g = next((g for g in _sg if hz in g and z in g), None)
                        if _g:
                            _ju = {'申子辰': '水', '寅午戌': '火', '巳酉丑': '金', '亥卯未': '木'}[''.join(_g)]
                            _pos = sorted((_g.index(hz), _g.index(z)))
                            if _pos == [0, 1]:
                                _bh = '生地半合%s局' % _ju
                            elif _pos == [1, 2]:
                                _bh = '墓地半合%s局' % _ju
                            else:
                                _bh = '拱合%s局' % _ju
                        lines.append(f"{_bh}（时支{hz}与{nm}{z}）：+6分")
                # 冲/害/刑/破（互斥，与计分同一优先级）
                if check_liuchong(hz, z):
                    score -= 15
                    lines.append(f"六冲：时支{hz}冲{nm}{z}：-15分")
                elif check_liuhai(hz, z):
                    score -= 6
                    lines.append(f"六害：时支{hz}害{nm}{z}：-6分")
                else:
                    _xing = check_xing(hz, z)
                    if _xing:
                        score -= 8
                        lines.append(f"相刑（{_xing}）：时支{hz}刑{nm}{z}：-8分")
                    elif check_po(hz, z):
                        score -= 4
                        lines.append(f"相破：时支{hz}破{nm}{z}：-4分")
            except Exception as e:
                logger.error(f"时柱关系明细计算失败({hz},{z}): {e}")
        return score, lines

    def _calculate_nayin_match(self, sizhu, owners):
        """
        计算纳音五行与事主年命的匹配度
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            
        Returns:
            tuple: (纳音匹配评分, 明细行列表)；无事主为 (0, [])
        """
        if not owners:
            return 0, []  # 2026-09-14：与 tuple 返回口径一致
        
        score = 0
        
        # 提取日课各柱纳音
        sizhu_nayin = []
        for pillar in ['年柱', '月柱', '日柱', '时柱']:
            if pillar in sizhu:
                try:
                    nayin = get_nayin(sizhu[pillar])
                    if nayin:
                        sizhu_nayin.append(nayin)
                except Exception as e:
                    logger.error(f"纳音计算失败({pillar}{sizhu[pillar]}): {str(e)}")
                    pass
        
        # 遍历事主，计算纳音匹配
        for owner in owners:
            # 获取事主年命纳音
            owner_year = owner.get('year', '')
            if owner_year:
                try:
                    # 简化处理：假设owner_year是年份，转换为年柱
                    # 实际应用中可能需要更复杂的年柱计算
                    pass
                except Exception:
                    pass
        
        # 基础纳音匹配评分（简化版）
        # 实际应用中可以根据纳音五行生克关系进行更详细的评分
        # 2026-09-14 口径透明化：本项为「纳音齐备分」——日课每柱可排纳音+2，
        # 与事主喜用/年命纳音无关（事主年命匹配是未启用的简化项），
        # 明细随分项展示，禁止在展示层杜撰「与事主喜用匹配」的解释。
        nayin_lines = []
        if sizhu_nayin:
            score += len(sizhu_nayin) * 2
            nayin_lines.append(
                f"日课{len(sizhu_nayin)}柱纳音（{'、'.join(sizhu_nayin)}）齐备，每柱+2，共+{score}分"
            )

        return score, nayin_lines
    
    def _get_level(self, score, wu_xing_result=None, huangdao_info=None, shanzuo_eval=None):
        """
        根据综合评分判断等级（含星级）

        2026-09-02用户确认：等级必须是总分的纯函数——
        同分的日课无论分项构成（五行/月令/黄道）如何，等级必须一致。
        五行/黄道对优劣的影响已体现在总分构成中（五行加成、黄道得分±），
        不再按"五行大吉+黄道大吉"等组合独立升降级（旧规则会导致
        同分不同级，如108分既评★★★吉又评★★★★★上吉）。

        通用事项等级阈值（按2021年案例期望表校准）：
        ⭐⭐⭐⭐⭐ (5星) = 上吉（≥105分）
        ⭐⭐⭐⭐ (4星) = 大吉（100-104分）
        ⭐⭐⭐ (3星) = 吉（85-99分）
        ⭐⭐ (2星) = 中吉（75-84分）
        ⭐ (1星) = 平（60-74分）
        ❌ (0星) = 凶（<60分）

        唯一例外（质量底线）：五行评分<60（五行凶）仍直接判凶，
        避免五行根基不稳的日课因月令/喜用/黄道加分而标吉。

        注意：婚嫁事项自2026-02-05起同样走本函数（等级=总分纯函数，
        同分必须同级）；婚嫁"五行评分"即嫁娶评分，传入 wu_xing_result
        时其 score 取 marriage_result['score'] 以适用五行<60判凶底线。

        Args:
            score: 综合评分
            wu_xing_result: 五行审核结果（仅用于五行凶兜底判断）
            huangdao_info: 黄道信息（保留参数兼容旧调用，不参与判级）
            shanzuo_eval: 仙命×坐山判定结果（坐山克仙命时等级封顶"❌ 凶"）

        Returns:
            str: 等级（含星级）
        """
        # 质量底线：五行凶 → ❌ 凶（坚决不用）
        try:
            wu_xing_score = wu_xing_result.get('score') if isinstance(wu_xing_result, dict) else None
            if wu_xing_score is not None and wu_xing_score < 60:
                return '❌ 凶'
        except Exception:
            pass

        if score >= 105:
            base_level = '★★★★★ 上吉'
        elif score >= 100:
            base_level = '★★★★ 大吉'
        elif score >= 85:
            base_level = '★★★ 吉'
        elif score >= 75:
            base_level = '★★ 中吉'
        elif score >= 60:
            base_level = '★ 平'
        else:
            base_level = '❌ 凶'

        # 质量底线（2026-10-04 §59.9，保守派）：坐山克仙命等级封顶"❌ 凶"。
        # 坐山克仙命在口径中为"凶中之凶"，比仙命真冲更重——制化只解除否决、
        # 不改变凶性；真冲有制化可到非凶，坐山克不适用。封顶在等级判定层完成，
        # 不改总分（排序/对比仍反映实际分值）。
        if (isinstance(shanzuo_eval, dict)
                and shanzuo_eval.get('relation') == '坐山克仙命'
                and base_level != '❌ 凶'):
            return '❌ 凶'
        return base_level
    
    def _yueling_phrase(self, wangshuai_text, yueling_score):
        """月令评语（2026-10-02 口径修复）：强弱以旺衰判定（与"日主旺衰"段同源）
        为准，帮扶程度以月令得分为准。旧实现仅按分数档位（>0 即"日主得力"），
        会与旺衰段"日主丙在月令戌中休囚"并存成"休囚却又得力"的自相矛盾。
        """
        ws = str(wangshuai_text or '')
        if '得令而旺' in ws:
            if yueling_score > 0:
                return '月令：得令得助，日主旺相'
            return '月令：得令，日主旺相'
        if '得生而相' in ws:
            if yueling_score > 0:
                return '月令：得生得助，日主相旺'
            return '月令：得生，日主相旺'
        if '休囚' in ws:
            if yueling_score > 0:
                return '月令：休囚泄气，得生扶有根不弱'
            if yueling_score == 0:
                return '月令：休囚泄气，生扶平平'
            return '月令：休囚泄气，日主乏力'
        if '受克而囚' in ws or '受克而死' in ws:
            if yueling_score > 0:
                return '月令：失令受克，赖生扶支撑'
            return '月令：失令受克，日主乏力'
        # 旺衰未明/状态一般：退回分数档位
        if yueling_score > 5:
            return '月令：得助偏旺'
        if yueling_score > 0:
            return '月令：有生扶'
        if yueling_score == 0:
            return '月令：平平，无明显助力'
        if yueling_score > -5:
            return '月令：气弱，需后天补救'
        return '月令：失令，日主乏力'

    def _generate_reason(self, wu_xing_result, huangdao_info, yueling_score, xishen_score=0, owner_matches=None, sun_moon_info=None, wangming_info=None, shanzuo_eval=None):
        """
        生成评分理由

        Args:
            wu_xing_result: 五行审核结果
            huangdao_info: 黄道信息
            yueling_score: 月令评分
            xishen_score: 喜用神匹配评分
            owner_matches: 每个事主的详细匹配信息
            sun_moon_info: 太阳太阴到山到向信息
            wangming_info: 亡命（仙命）信息（安葬专用）
            shanzuo_eval: 仙命×坐山纳音生克（第二阶段 2.1）

        Returns:
            str: 评分理由
        """
        reason = []
        details = wu_xing_result.get('details', {})

        # 五行评语
        reason.append(f"五行：{wu_xing_result['ji_yu']}")

        # 日主旺衰分析
        if details.get('日主旺衰'):
            reason.append(f"日主：{details['日主旺衰']}")

        # 地支关系分析
        if details.get('地支关系'):
            relations = details['地支关系']
            good_relations = [r for r in relations if '三合' in r or '六合' in r]
            bad_relations = [r for r in relations if '冲' in r or '害' in r or '刑' in r]
            if good_relations:
                reason.append(f"地支合局：{'；'.join(good_relations)}")
            if bad_relations:
                reason.append(f"地支冲害：{'；'.join(bad_relations)}")

        # 吉神分析（命局贵人神煞：天德/天乙/福星贵人、禄神等，
        #   与下方择日神煞“吉神：”段区分标签，避免同名混淆）
        if details.get('吉神'):
            jishen = details['吉神']
            if jishen:
                reason.append(f"命局吉神：{'；'.join(jishen)}")

        # 月令评语（口径统一走 _yueling_phrase：强弱随旺衰段，帮扶随得分）
        reason.append(self._yueling_phrase(details.get('日主旺衰', ''), yueling_score))

        # 喜用神匹配评语
        # 2026-10-02 优化：分档口径统一（0-5补益有限 / 6-10补益有限，略有助益 /
        # 11-15有一定补益 / 16-20补益较大 / >20能量共振极佳）
        if xishen_score > 20:
            reason.append(f"喜用神：日课大喜事主用神，能量共振极佳")
        elif xishen_score > 15:
            reason.append(f"喜用神：日课对事主补益较大")
        elif xishen_score > 10:
            reason.append(f"喜用神：日课对事主有一定补益")
        elif xishen_score > 5:
            reason.append(f"喜用神：日课对事主补益有限，略有助益")
        elif xishen_score > 0:
            reason.append(f"喜用神：日课对事主补益有限")
        elif xishen_score == 0:
            reason.append(f"喜用神：日课与事主八字无明显冲突")

        # 亡命（仙命）信息段（安葬专用；六冲等忌由相主通道计入，此处只展示仙命）
        if wangming_info and wangming_info.get('年柱'):
            reason.append(
                f"亡命（仙命）：{wangming_info.get('name') or '亡者'}，"
                f"{wangming_info['年柱']}年生，"
                f"{wangming_info['纳音']}命（{wangming_info['五行']}）")
        # 仙命×坐山纳音生克段（第二阶段 2.1）
        if shanzuo_eval and shanzuo_eval.get('relation') != '未知':
            reason.append(
                f"仙命×坐山：{shanzuo_eval['reason']}"
                f"（{shanzuo_eval['score']:+d}分）")

        # 每个事主的详细分析
        if owner_matches:
            for match in owner_matches:
                owner_name = match['name']
                owner_score = match['score']
                details = match['details']
                xishen = match['xishen']
                yongshen = match['yongshen']
                
                # 构建事主分析
                owner_reason = f"{owner_name}："
                if details:
                    owner_reason += f"得分{owner_score}，"
                    owner_reason += "；".join(details)
                else:
                    owner_reason += f"得分{owner_score}，无明显匹配"
                
                reason.append(owner_reason)
        
        # 黄道评语
        da_huang_dao = huangdao_info['da_huang_dao']
        xiao_huang_dao = huangdao_info['xiao_huang_dao']
        
        if da_huang_dao['type'] == '吉':
            reason.append(f"大黄道{da_huang_dao['name']}，{da_huang_dao['description']}")
        elif da_huang_dao['type'] == '凶':
            reason.append(f"黑道{da_huang_dao['name']}，{da_huang_dao['description']}")
        
        if xiao_huang_dao['type'] == '吉':
            reason.append(f"小黄道{xiao_huang_dao['name']}，{xiao_huang_dao['description']}")
        
        # 神煞理由
        _ss_all = [s for s in self.shensha_list if isinstance(s, dict)]
        good_shensha = sorted([s for s in _ss_all if s.get('score', 0) > 0],
                              key=lambda s: s.get('score', 0), reverse=True)
        bad_shensha = sorted([s for s in _ss_all if s.get('score', 0) < 0],
                             key=lambda s: s.get('score', 0), reverse=True)
        
        if good_shensha:
            reason.append('吉神：' + '、'.join([s['name'] for s in good_shensha]))
        if bad_shensha:
            reason.append('凶神：' + '、'.join([s['name'] for s in bad_shensha]))
        
        # 太阳太阴到山到向分析
        if sun_moon_info:
            sun_moon_reason = []
            if sun_moon_info.get('sun_to_mountain'):
                sun_moon_reason.append('太阳到山')
            if sun_moon_info.get('sun_to_direction'):
                sun_moon_reason.append('太阳到向')
            if sun_moon_info.get('moon_to_mountain'):
                sun_moon_reason.append('太阴到山')
            if sun_moon_info.get('moon_to_direction'):
                sun_moon_reason.append('太阴到向')
            if sun_moon_reason:
                reason.append('太阳太阴：' + '、'.join(sun_moon_reason))
            elif sun_moon_info.get('details'):
                reason.append(f"太阳太阴：{sun_moon_info['details']}")
        
        # 宜忌理由
        if self.yi_list:
            reason.append('宜：' + '、'.join(self.yi_list))
        if self.ji_list:
            reason.append('忌：' + '、'.join(self.ji_list))
        
        return '；'.join(reason)

    def _build_marriage_reason_tail(self, wu_xing_result, yueling_analysis,
                                   yueling_score, xishen_score, shensha_list=None,
                                   marriage_details=None, veto_reason=None,
                                   ji_jiaqu_capped=False, level_str=None):
        """
        嫁娶【综合评语】月令分析之后的完整正五行分析串（2026-09-17 应需求补全）。

        原嫁娶评语在"月令分析：…"一句后即止，缺少日主旺衰、地支合局、命局吉神、
        月令、喜用神、黄黑道、吉神、宜等正五行核心分析。此处按与 _generate_reason
        完全一致的判定口径补齐，以"；"连成一段，接在月令分析同一段落内。

        刻意不含：开头"五行："（已由"嫁娶要点"承载）、事主逐条匹配、太阳太阴、
        独立"忌："行（嫁娶评语前段已单列）。

        Args:
            wu_xing_result: 五行审核结果（取 details：日主旺衰/地支关系/吉神）
            yueling_analysis: _generate_yueling_analysis 产出的月令分析句
            yueling_score: 月令得分（决定月令评语措辞）
            xishen_score: 喜用神匹配得分（决定喜用神评语措辞）
            shensha_list: 嫁娶路径本次神煞列表（取吉神名，如大利月）
        """
        seg = []
        details = {}
        if isinstance(wu_xing_result, dict):
            _d = wu_xing_result.get('details', {})
            if isinstance(_d, dict):
                details = _d

        def _clean(ln):
            # 五行分析给时柱关系追加了"（示例时柱，不计分）"后缀；评语里只陈述合局，
            # 不带此括注（与详情【地支关系】展示后缀区分，后者由主程序另做替换）。
            return str(ln).replace('（示例时柱，不计分）', '').strip()

        # 月令分析（本段首句）
        if yueling_analysis:
            seg.append(f'月令分析：{yueling_analysis}')

        # 日主旺衰
        if details.get('日主旺衰'):
            seg.append(f"日主：{details['日主旺衰']}")

        # 地支关系（合局 / 冲害）
        # 2026-10-03 E104修复：评分明细里的合局项（如"六合(子丑)"）须与
        # 地支关系中的描述合并；且即使 details['地支关系'] 缺失/无合局，
        # 只要评分明细有合局加分就必须生成地支合局句（否则 E104 报遗漏）。
        good = []
        bad = []
        if details.get('地支关系'):
            rels = details['地支关系']
            if isinstance(rels, (list, tuple)):
                good = [_clean(r) for r in rels if ('三合' in str(r) or '六合' in str(r) or '半合' in str(r) or '拱合' in str(r)) and _clean(r)]
                bad = [_clean(r) for r in rels if ('冲' in str(r) or '害' in str(r) or '刑' in str(r)) and _clean(r)]
        if marriage_details:
            md_heju = [str(d[0]) for d in marriage_details
                       if isinstance(d, (list, tuple)) and len(d) >= 2
                       and isinstance(d[1], (int, float)) and d[1] > 0
                       and any(k in str(d[0]) for k in ('三合', '半合', '拱合', '六合'))]
            for mh in md_heju:
                _zhis_in_mh = [c for c in mh if c in '子丑寅卯辰巳午未申酉戌亥']
                if _zhis_in_mh and not any(all(z in g for z in _zhis_in_mh[:2]) for g in good):
                    good.append(f"评分合局：{mh}")
        if good:
            seg.append(f"地支合局：{'；'.join(good)}")
        if bad:
            seg.append(f"地支冲害：{'；'.join(bad)}")

        # 命局吉神（天德贵人、禄神等）
        if details.get('吉神'):
            jishen = [str(j).strip() for j in details['吉神'] if str(j).strip()]
            if jishen:
                seg.append(f"命局吉神：{'；'.join(jishen)}")

        # 月令评语（口径同 _generate_reason，统一走 _yueling_phrase）
        seg.append(self._yueling_phrase(details.get('日主旺衰', ''), yueling_score))

        # 喜用神评语（口径同 _generate_reason：0-5补益有限 / 6-10补益有限，略有助益 /
        # 11-15有一定补益 / 16-20补益较大 / >20能量共振极佳）
        if xishen_score > 20:
            seg.append('喜用神：日课大喜事主用神，能量共振极佳')
        elif xishen_score > 15:
            seg.append('喜用神：日课对事主补益较大')
        elif xishen_score > 10:
            seg.append('喜用神：日课对事主有一定补益')
        elif xishen_score > 5:
            seg.append('喜用神：日课对事主补益有限，略有助益')
        elif xishen_score > 0:
            seg.append('喜用神：日课对事主补益有限')
        elif xishen_score == 0:
            seg.append('喜用神：日课与事主八字无明显冲突')

        # 大黄道 / 小黄道（口径同 _generate_reason：凶报黑道，小黄道仅吉时入评语）
        hd = self.huangdao_info if isinstance(self.huangdao_info, dict) else {}
        da = hd.get('da_huang_dao') if isinstance(hd.get('da_huang_dao'), dict) else {}
        if da.get('type') == '吉':
            seg.append(f"大黄道{da.get('name', '')}，{da.get('description', '')}")
        elif da.get('type') == '凶':
            seg.append(f"黑道{da.get('name', '')}，{da.get('description', '')}")
        xo = hd.get('xiao_huang_dao') if isinstance(hd.get('xiao_huang_dao'), dict) else {}
        if xo.get('type') == '吉':
            seg.append(f"小黄道{xo.get('name', '')}，{xo.get('description', '')}")

        # 吉神（本次嫁娶神煞中的加分项，如大利月）
        _ss_src = shensha_list if isinstance(shensha_list, list) else (self.shensha_list or [])
        _ss_all = [s for s in _ss_src if isinstance(s, dict)]
        good_shensha = sorted([s for s in _ss_all if s.get('score', 0) > 0],
                              key=lambda s: s.get('score', 0), reverse=True)
        if good_shensha:
            seg.append('吉神：' + '、'.join([s['name'] for s in good_shensha]))

        # 伏吟加重提示（2026-10-02）：月时/年时伏吟会放大该柱五行力度，
        # 若夫星已受耗，则在评语中提示"X气加重，夫星更受耗"。
        # 夫星受耗判定取 marriage_details 负分项（self.ji_list 在嫁娶路径
        # 只含规则忌项，夫星耗分在 marriage_details，勿混用数据源）。
        _md_neg = [str(_d[0]) for _d in (marriage_details or [])
                   if isinstance(_d, (list, tuple)) and len(_d) >= 2
                   and isinstance(_d[1], (int, float)) and _d[1] < 0]
        _has_fuxing_hao = any('夫星' in _t for _t in _md_neg)
        _zhi_wuxing = {'子': '水', '丑': '土', '寅': '木', '卯': '木',
                       '辰': '土', '巳': '火', '午': '火', '未': '土',
                       '申': '金', '酉': '金', '戌': '土', '亥': '水'}
        _fuyin_lines = [str(r) for r in (details.get('地支关系') or [])
                        if '伏吟' in str(r)]
        if _fuyin_lines:
            for _fl in _fuyin_lines:
                # 提取伏吟地支（如"月柱戊戌 与 时柱戊戌 伏吟"）
                _z = None
                for _c in list(_zhi_wuxing.keys()):
                    if _c in _fl:
                        _z = _c
                        break
                if _z and _has_fuxing_hao:
                    seg.append(f"伏吟：{_fl.replace('（示例时柱，不计分）', '').strip()}，"
                               f"{_zhi_wuxing.get(_z, '')}气加重，夫星更受耗")
                elif _z:
                    seg.append(f"伏吟：{_fl.replace('（示例时柱，不计分）', '').strip()}，"
                               f"{_zhi_wuxing.get(_z, '')}气加重")

        # 宜忌冲突提示（2026-10-02）：夫星受耗时嫁娶仍标"宜嫁娶"且给高星，
        # 评语须加"虽有吉神支撑，然夫星受耗，嫁娶须有制化或另择吉时"，
        # 避免"宜嫁娶"与"忌夫星受耗"并列而无折中说明。
        if _has_fuxing_hao:
            _md_pos = any(isinstance(_d, (list, tuple)) and len(_d) >= 2
                          and isinstance(_d[1], (int, float)) and _d[1] > 0
                          and '基础分' not in str(_d[0])
                          for _d in (marriage_details or []))
            if _md_pos or good_shensha:
                seg.append('虽有天德月德等吉神支撑，然夫星受耗，嫁娶须有制化或另择吉时')

        # 宜（与综合评语末句保持一致，取本次 yi_list）
        if self.yi_list:
            seg.append('宜：' + '、'.join(self.yi_list))

        # 综合结论句（2026-10-02，审查问题6）：评语末尾补嫁娶总结论，
        # 按否决/忌项/吉神自动生成"不宜/可用须择时/可用"，让用户直接看到结论。
        if veto_reason:
            seg.append(f'综合判断：{veto_reason}，本日不宜嫁娶')
        elif self.ji_list or _md_neg:
            # 2026-10-02 修02-05问题3/4：嫁娶路径 ji_list 只含规则忌项，
            # 假三煞/夫星受克等在 marriage_details 负分项，须合并为忌项数据源。
            _all_ji = []
            _seen = set()
            for _j in self.ji_list:
                _st = str(_j).split('【')[0].split('（')[0].strip()
                if _st and _st not in _seen:
                    _all_ji.append(_st)
                    _seen.add(_st)
            for _t in _md_neg:
                _st = str(_t).split('【')[0].split('（')[0].strip()
                if _st and _st not in _seen:
                    _all_ji.append(_st)
                    _seen.add(_st)
            _ji_brief = '、'.join(_all_ji[:2])
            _ji_more = '等' if len(_all_ji) > 2 else ''
            if good_shensha:
                _good_names = '、'.join(s['name'] for s in good_shensha[:3])
            else:
                # 神煞吉项为空时取评分明细正分项（去括注，如 不将日/大黄道天德日）
                _md_good = [str(_d[0]).split('（')[0] for _d in (marriage_details or [])
                            if isinstance(_d, (list, tuple)) and len(_d) >= 2
                            and isinstance(_d[1], (int, float)) and _d[1] > 0
                            and '基础分' not in str(_d[0])][:3]
                _good_names = '、'.join(_md_good) if _md_good else '吉神'
            _tail = ''
            if yueling_score < 0 and xishen_score > 0:
                _tail = '；日主虽失令，喜用神得补，整体吉中带弱'
            # 2026-10-03 凶级分级（校验器E006真阳性修复）：
            # 凶级必须写"不宜"，且区分 纯凶 / 凶（慎用） 两种子类——
            # 纯凶绝对禁用；凶（慎用）有制化空间，须附"如确需使用"说明。
            _lv = str(level_str if level_str is not None
                      else getattr(self, 'level', '') or '')
            _is_xiong = '凶' in _lv
            if _is_xiong and not ji_jiaqu_capped:
                seg.append(f'综合判断：{_ji_brief}{_ji_more}等凶煞并见，'
                           f'不宜嫁娶，另择吉日{_tail}')
            elif _is_xiong and ji_jiaqu_capped:
                seg.append(f'综合判断：{_ji_brief}{_ji_more}须避，然{_good_names}并见，'
                           f'不宜嫁娶；如确需使用，须严格制化并择吉时{_tail}')
            elif ji_jiaqu_capped:
                seg.append(f'综合判断：{_ji_brief}{_ji_more}须避，然{_good_names}并见，'
                           f'嫁娶须慎用，宜择吉时{_tail}')
            else:
                seg.append(f'综合判断：{_ji_brief}{_ji_more}须避，然{_good_names}并见，'
                           f'嫁娶可用，须于十二时辰中择吉时{_tail}')
        else:
            _tail = ''
            if yueling_score < 0 and xishen_score > 0:
                _tail = '；日主虽失令，喜用神得补，整体吉中带弱'
            seg.append(f'综合判断：吉神并见、无忌项，嫁娶可用{_tail}')

        return '；'.join(seg)

    def _generate_yueling_analysis(self, sizhu):
        """
        生成月令分析（与月令旺衰评分同源：旺相休囚死体系）
        —— 修复：原使用"寄生十二宫"判定得令/失令，与月令旺相休囚死评分体系不同源，
           会导致"寄生十二宫判得令 + 旺衰评分判失令"的矛盾（如戊日主寅月）。
           现统一改用旺相休囚死，并追加"通关合局"说明细化旺衰描述。

        Args:
            sizhu: 四柱信息字典

        Returns:
            str: 月令分析描述
        """
        day_gan = sizhu.get('day_gan', '')
        month_zhi = sizhu.get('month_zhi', '')
        if not day_gan or not month_zhi:
            return ''

        # 天干/地支五行
        gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火',
                      '戊': '土', '己': '土', '庚': '金', '辛': '金',
                      '壬': '水', '癸': '水'}
        zhi_wuxing = {'子': '水', '丑': '土', '寅': '木', '卯': '木',
                      '辰': '土', '巳': '火', '午': '火', '未': '土',
                      '申': '金', '酉': '金', '戌': '土', '亥': '水'}
        day_wuxing = gan_wuxing.get(day_gan, '')
        month_wuxing = zhi_wuxing.get(month_zhi, '')
        if not day_wuxing:
            return ''

        # ====== 旺相休囚死表（按日干查月支，与_calculate_wangxiang评分表100%同源） ======
        # 修复：原按季节表判定（丑归冬→土囚），与评分表（戊己土旺于辰戌丑未月）矛盾，
        # 导致"月令分析说失令、月令得分却+15"的描述冲突（如2023-01-11己日丑月案例）。
        if not month_zhi:
            month_zhi = str(sizhu.get('月柱', ''))[1:2]
        WANGXIANG_TABLE = {
            '甲': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
            '乙': {'旺': ['寅', '卯'], '相': ['亥', '子'], '休': ['巳', '午'], '囚': ['辰', '戌', '丑', '未'], '死': ['申', '酉']},
            '丙': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
            '丁': {'旺': ['巳', '午'], '相': ['寅', '卯'], '休': ['辰', '戌', '丑', '未'], '囚': ['申', '酉'], '死': ['亥', '子']},
            '戊': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
            '己': {'旺': ['辰', '戌', '丑', '未'], '相': ['巳', '午'], '休': ['申', '酉'], '囚': ['亥', '子'], '死': ['寅', '卯']},
            '庚': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
            '辛': {'旺': ['申', '酉'], '相': ['辰', '戌', '丑', '未'], '休': ['亥', '子'], '囚': ['寅', '卯'], '死': ['巳', '午']},
            '壬': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']},
            '癸': {'旺': ['亥', '子'], '相': ['申', '酉'], '休': ['寅', '卯'], '囚': ['巳', '午'], '死': ['辰', '戌', '丑', '未']}
        }
        state = ''
        gan_table = WANGXIANG_TABLE.get(day_gan, {})
        for k, zlist in gan_table.items():
            if month_zhi in zlist:
                state = k
                break

        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        ke    = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

        analysis_parts = []
        # ---- 得令/失令判定（与旺相休囚死评分100%同源） ----
        if state == '旺':
            analysis_parts.append(f"{day_gan}日主得令而旺（{day_wuxing}旺于{month_zhi}月）")
        elif state == '相':
            analysis_parts.append(f"{day_gan}日主得生而相（{day_wuxing}处于相地）")
        elif state == '休':
            analysis_parts.append(f"{day_gan}日主休囚（泄气）")
        elif state == '囚':
            analysis_parts.append(f"{day_gan}日主失令（{day_wuxing}克当令之气，反受令困，处囚地）")
        elif state == '死':
            analysis_parts.append(f"{day_gan}日主失令，{day_wuxing}气衰微")
        else:
            analysis_parts.append(f"{day_gan}日主非得令之月")

        # ---- 五行生克关系 ----
        if month_wuxing:
            if sheng.get(month_wuxing) == day_wuxing:
                analysis_parts.append(f"{month_wuxing}生{day_wuxing}")
            elif ke.get(month_wuxing) == day_wuxing:
                analysis_parts.append(f"{month_wuxing}克{day_wuxing}")
            elif month_wuxing == day_wuxing:
                analysis_parts.append("同气相求")
            elif sheng.get(day_wuxing) == month_wuxing:
                analysis_parts.append(f"{day_wuxing}生{month_wuxing}")

        # ---- 细化：通关合局说明（月令克日主→若有木→火→土类链条，则补"幸X通关"） ----
        try:
            year_zhi  = sizhu.get('year_zhi',  '')
            day_zhi   = sizhu.get('day_zhi',   '')
            san_zhi = {z for z in (year_zhi, month_zhi, day_zhi) if z}
            sanzhi_wx = {zhi_wuxing.get(z, '') for z in san_zhi} - {''}
            if ke.get(month_wuxing) == day_wuxing:
                guan_wx = sheng.get(month_wuxing, '')
                if guan_wx and sheng.get(guan_wx) == day_wuxing:
                    nian_gan  = sizhu.get('year_gan',  '')
                    yue_gan   = sizhu.get('month_gan', '')
                    day_gan_v = sizhu.get('day_gan',   '')
                    tiangan_wx = {gan_wuxing.get(g, '') for g in (nian_gan, yue_gan, day_gan_v)} - {''}
                    if guan_wx in (sanzhi_wx | tiangan_wx):
                        analysis_parts.append(
                            f"幸{month_wuxing}{guan_wx}{day_wuxing}通关，降低月令克害"
                        )
                    else:
                        SANHE = {
                            '火': {'寅', '午', '戌'}, '水': {'申', '子', '辰'},
                            '木': {'亥', '卯', '未'}, '金': {'巳', '酉', '丑'},
                        }
                        for he_wx, zset in SANHE.items():
                            if he_wx == guan_wx and len(san_zhi & zset) >= 2:
                                analysis_parts.append(
                                    f"幸{month_wuxing}{guan_wx}{day_wuxing}通关（合局有气），降低月令克害"
                                )
                                break
            # 六合化出通关五行
            LIUHE_MAP = {('卯','戌'):'火', ('寅','亥'):'木', ('子','丑'):'土',
                         ('巳','申'):'水', ('午','未'):'土', ('辰','酉'):'金'}
            he_hua = ''
            for (a, b), hua in LIUHE_MAP.items():
                if a in san_zhi and b in san_zhi:
                    he_hua = hua
                    break
            if he_hua and ke.get(month_wuxing) == day_wuxing and sheng.get(he_hua) == day_wuxing:
                if not any('通关' in x for x in analysis_parts):
                    analysis_parts.append(
                        f"幸六合化{he_hua}通关，{he_hua}生{day_wuxing}化解{month_wuxing}克{day_wuxing}"
                    )
        except Exception:
            pass

        if analysis_parts:
            return '，'.join(analysis_parts)
        return ''


# 全局评分器实例
scorer = Scorer()

def calculate_sun_moon_position(sizhu, shan_xiang):
    """
    太阳太阴到山到向（2026-09-22 B3 层3 收敛：统一 sxtwl 节气口径）

    口径历史（跟踪项22）：
    - 原实现按 sizhu['month'] 公历月序查 12 支山表（月1→子…月12→亥），
      八干四维归支，与《协纪》太阳二十四节气过宫（冬至到子）不符，且月序11
      子山实测返回戌——方向性错位；
    - 现判定全部委托 神煞基类.get_sun_moon_mountains（sxtwl jqIndex，
      冬至到子、节气日当天换山、24 山），与修造神煞扩展同一单点出口。
    计分：本函数 2026-09-22 起 score 恒 0。太阳/太阴到山到向的加分唯一走
    修造神煞扩展神煞档（太阳到山+25/到向+20、太阴到山+20/到向+15，
    SHENSHA_SCORES 单一登记），避免同一吉神双轨计分（原 +10/+8 与 +25
    档并存会同日双加）。本函数仅保留到山/到向布尔标志与详情文本供展示层。

    Args:
        sizhu: 四柱信息（需含 date，回退 year/month/day）
        shan_xiang: 山向（如 '寅山申向'）

    Returns:
        dict: 太阳太阴到山到向信息（score 恒 0）
    """
    empty = {
        'sun_position': '无山向信息',
        'moon_position': '无山向信息',
        'score': 0
    }
    if not shan_xiang:
        return empty

    # 日期解析（与四离四绝等 sxtwl 规则同款回退）
    dq = sizhu.get('date') if isinstance(sizhu, dict) else None
    if dq is None or not hasattr(dq, 'year'):
        try:
            from datetime import date as _date
            dq = _date(int(sizhu.get('year')), int(sizhu.get('month')),
                       int(sizhu.get('day')))
        except (TypeError, ValueError):
            return {
                'sun_position': '无日期信息',
                'moon_position': '无日期信息',
                'score': 0
            }

    try:
        from .shensha.神煞基类 import get_sun_moon_mountains, get_xiangshan_24
    except ImportError:
        from shensha.神煞基类 import get_sun_moon_mountains, get_xiangshan_24

    zuoshan = shan_xiang[0]
    xiangshan = get_xiangshan_24(zuoshan)
    sun_position, moon_position = get_sun_moon_mountains(dq)

    sun_to_mountain = sun_position == zuoshan
    sun_to_direction = bool(xiangshan) and sun_position == xiangshan
    moon_to_mountain = moon_position == zuoshan
    moon_to_direction = bool(xiangshan) and moon_position == xiangshan

    return {
        'sun_position': sun_position,
        'moon_position': moon_position,
        'sun_to_mountain': sun_to_mountain,
        'sun_to_direction': sun_to_direction,
        'moon_to_mountain': moon_to_mountain,
        'moon_to_direction': moon_to_direction,
        'score': 0,  # 计分已收敛至修造神煞档（+25/+20/+20/+15），此处不再双轨加分
        'details': f"太阳在{sun_position}方，太阴在{moon_position}方"
    }

def _zaozhu_weighted(raw, weight):
    """作灶主事人模式（2026-09）：按权重缩放分值，辅助者半权重。
    四舍五入到远离0方向（-25*0.5=-13、-15*0.5=-8、+15*0.5=+8）。"""
    try:
        w = float(weight)
    except (TypeError, ValueError):
        return int(raw)
    v = raw * w
    return int(v + 0.5) if v >= 0 else -int(-v + 0.5)


def _zaozhu_aux_detail(text, weight):
    """辅助事主相主明细：去[硬性门槛]前缀（辅助者被冲不否决）、分值减半并注明。"""
    import re
    hard = text.startswith('[硬性门槛]')
    t = text[len('[硬性门槛]'):] if hard else text
    m = re.search(r'，([+-]?\d+)分$', t)
    if not m:
        return t
    new = _zaozhu_weighted(int(m.group(1)), weight)
    sign = ('+' if new > 0 else '') + str(new)
    body = t[:m.start()]
    if hard and body.endswith('，不可用'):
        body = body[:-len('，不可用')]
        return f'{body}（辅助，半权重不否决），{sign}分'
    return f'{body}，{sign}分'


def calculate_score(sizhu, event_type, owners=None, house_type=None, shan_xiang=None,
                    zaoxiang=None, zaowei=None, chuangwei=None, jian_xiang=None,
                    zaozhu_mode=None, zeli_mode='feixing'):  # _zm0915
    """
    计算评分（便捷函数）
    
    采用"五行为主，黄道为用"的架构：
    第一层（核心筛选）：正五行模块
    第二层（优选排序）：大小黄道模块
    第三层（深度优化）：月令对日主的帮助
    
    Args:
        sizhu: 四柱信息
        event_type: 事项类型
        owners: 事主信息
        house_type: 宅型（阳宅/阴宅）
        shan_xiang: 山向
        zaoxiang: 灶向（作灶专用）
        zaowei: 灶位（作灶专用）
        chuangwei: 床位朝向（安床专用）
        jian_xiang: 兼向
        
    Returns:
        dict: 评分结果
    """
    return scorer.score(sizhu, event_type, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, None, jian_xiang, zaozhu_mode=zaozhu_mode, zeli_mode=zeli_mode)  # _zm0915

# 2026-09-14 补丁指纹 nayin-jishen-zaoxiang：纳音齐备明细/吉神口径/灶向依据
