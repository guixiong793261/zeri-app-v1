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

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    # 添加 shensha 子目录到路径
    shensha_dir = os.path.join(modules_dir, 'shensha')
    if os.path.exists(shensha_dir) and shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)

# 尝试不同的导入方式，适应不同环境
try:
    # 尝试从 modules 包导入
    from modules.shensha import get_checker
    from modules.rules import get_rule_checker
    from modules.黄道 import calculate_huangdao
    from modules.喜用神计算器 import calculate_xishen_yongshen
except ImportError:
    # 尝试直接导入（适应手机环境）
    import sys
    import os
    # 添加当前目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 添加 shensha 目录到路径
    shensha_dir = os.path.join(current_dir, 'shensha')
    if os.path.exists(shensha_dir) and shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)
    
    # 添加 rules 目录到路径
    rules_dir = os.path.join(current_dir, 'rules')
    if os.path.exists(rules_dir) and rules_dir not in sys.path:
        sys.path.insert(0, rules_dir)
    
    # 直接导入模块
    try:
        from shensha import get_checker
        from rules import get_rule_checker
        from 黄道 import calculate_huangdao
        from 喜用神计算器 import calculate_xishen_yongshen
    except ImportError as e:
        print(f"导入模块失败: {e}")
        # 导入失败时的备用实现
        def get_checker(event_type):
            class MockChecker:
                def check(self, *args, **kwargs):
                    return []
            return MockChecker()
        
        def get_rule_checker(event_type):
            class MockRuleChecker:
                def check(self, *args, **kwargs):
                    return [], []
            return MockRuleChecker()
        
        def calculate_huangdao(sizhu):
            return {
                'da_huang_dao': {'name': '黄道吉日', 'type': '吉', 'score': 10, 'description': '适合办大事'},
                'xiao_huang_dao': {'name': '黄道吉日', 'type': '吉', 'score': 5, 'description': '适合办大事'},
                'huang_dao_score': 15,
                'huang_dao_level': '大吉',
                'description': '黄道吉日，适合办大事'
            }
        
        def calculate_xishen_yongshen(sizhu):
            return "水", "水"

# 导入八字工具整合模块的新功能
try:
    # 尝试从 modules 包导入
    from modules.八字工具整合 import (
        get_zhangsheng, get_nayin, get_canggan,
        check_liuhe, check_liuchong, check_sanhe, check_sanxing,
        check_liuhai, check_po, check_xing, check_hai
    )
    HAS_BAZI_TOOLS = True
except ImportError:
    # 手机环境：直接导入
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

class Scorer:
    """评分器"""
    
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
            # 尝试从 modules 包导入
            try:
                from modules.八字工具整合 import (
                    check_liuhe, check_liuchong, check_sanhe, check_sanxing,
                    check_liuhai, check_po, check_xing, check_hai
                )
            except ImportError:
                # 手机环境：直接导入
                from 八字工具整合 import (
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
    
    def score(self, sizhu, event_type, owners=None, house_type=None, shan_xiang=None, 
              zaoxiang=None, zaowei=None, chuangwei=None):
        """
        计算评分
        
        架构说明：
        第一层（核心筛选）：正五行模块 - 这是系统的"否决权"模块
        第二层（优选排序）：大小黄道模块 - 这是系统的"加分项"
        第三层（深度优化）：月令对日主的帮助 - 正五行择日法的重要维度
        
        Args:
            sizhu: 四柱信息
            event_type: 事项类型
            owners: 事主信息
            house_type: 宅型（阳宅/阴宅）
            shan_xiang: 山向
            zaoxiang: 灶向（作灶专用）
            zaowei: 灶位（作灶专用）
            chuangwei: 床位朝向（安床专用）
            
        Returns:
            dict: 评分结果
        """
        # 第一步：正五行审核（核心门槛）
        wu_xing_result = self._check_wu_xing(sizhu, event_type, owners, 
                                                house_type, shan_xiang, 
                                                zaoxiang, zaowei, chuangwei)
        
        # 如果五行不合格（犯三杀、冲山等大忌），直接返回"❌ 凶"
        if not wu_xing_result['he_ge']:
            return {
                'score': 0,
                'level': '❌ 凶',
                'reason': wu_xing_result['ji_yu'],
                'shensha_list': self.shensha_list,
                'yi_list': self.yi_list,
                'ji_list': self.ji_list,
                'huangdao_info': {},
                'wu_xing_result': wu_xing_result
            }
        
        # 第二步：月令对日主的帮助评分
        yueling_score = self._calculate_yueling_help(sizhu)
        
        # 第三步：日课五行与事主喜用神匹配评分（正五行择日法核心）
        xishen_score, owner_matches = self._calculate_xishen_match(sizhu, owners)
        
        # 第四步：大小黄道审核（加分/减分项）
        self.huangdao_info = calculate_huangdao(sizhu)
        huangdao_score = self.huangdao_info.get('huang_dao_score', 0)
        
        # 计算最终得分：五行评分 + 月令得分 + 喜用神得分 + 黄道得分
        self.final_score = wu_xing_result['score'] + yueling_score + xishen_score + huangdao_score
        
        # 第五步：综合评定
        self.level = self._get_level(self.final_score, wu_xing_result, self.huangdao_info)
        
        # 构建详细得分明细
        score_details = {
            '基础分': self.base_score,
            '五行评分': wu_xing_result['score'],
            '月令得分': yueling_score,
            '喜用神得分': xishen_score,
            '黄道得分': huangdao_score,
            '总分': self.final_score
        }
        
        # 添加每个事主的详细匹配信息
        if owner_matches:
            score_details['事主匹配'] = owner_matches
        
        # 添加月令详细得分
        wangxiang_score = self._calculate_wangxiang(sizhu)
        zhizhi_score = self._calculate_zhizhi_relation(sizhu)
        score_details['月令详细'] = {
            '旺衰得分': wangxiang_score,
            '支支关系得分': zhizhi_score
        }
        
        return {
            'score': self.final_score,
            'level': self.level,
            'reason': self._generate_reason(wu_xing_result, self.huangdao_info, yueling_score, xishen_score, owner_matches),
            'shensha_list': self.shensha_list,
            'yi_list': self.yi_list,
            'ji_list': self.ji_list,
            'huangdao_info': self.huangdao_info,
            'wu_xing_result': wu_xing_result,
            'score_details': score_details
        }
    
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
            for wx in sizhu_wuxing:
                if wx in owner_yongshen_list:
                    owner_score += 8  # 天干为用神：+8分
                    match_details.append(f"天干五行{wx}与用神匹配")
                elif wx in owner_xishen_list:
                    owner_score += 5  # 天干为喜神：+5分
                    match_details.append(f"天干五行{wx}与喜神匹配")

            # 2. 检查日课藏干与用神匹配
            for wx in sizhu_canggan:
                if wx in owner_yongshen_list:
                    owner_score += 3  # 藏干为用神：+3分
                    match_details.append(f"藏干五行{wx}与用神匹配")
                elif wx in owner_xishen_list:
                    owner_score += 2  # 藏干为喜神：+2分
                    match_details.append(f"藏干五行{wx}与喜神匹配")

            total_score += owner_score
            owner_matches.append({
                'name': owner_name,
                'score': owner_score,
                'details': match_details,
                'xishen': owner_xishen,
                'yongshen': owner_yongshen
            })

        return total_score, owner_matches
    
    def _check_wu_xing(self, sizhu, event_type, owners, house_type, shan_xiang,
                      zaoxiang, zaowei, chuangwei):
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
        # 检查神煞
        shensha_checker = get_checker(event_type)
        print(f"[评分器] 事项类型: {event_type}, 检查器类型: {type(shensha_checker).__name__}", flush=True)
        print(f"[评分器] 事主数据: {owners}", flush=True)
        self.shensha_list = shensha_checker.check(sizhu, owners)
        print(f"[评分器] 神煞列表: {[s.get('name', '') for s in self.shensha_list]}", flush=True)
        
        # 检查宜忌规则
        rule_checker = get_rule_checker(event_type)
        self.yi_list, self.ji_list = rule_checker.check(
            sizhu, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei
        )
        
        # 计算五行评分
        wu_xing_score = self.base_score
        
        # 记录各项得分详情
        score_breakdown = {
            '基础分': self.base_score,
            '神煞得分': 0,
            '宜事得分': 0,
            '忌事得分': 0,
            '十二长生得分': 0,
            '地支关系得分': 0,
            '纳音匹配得分': 0
        }
        
        for shensha in self.shensha_list:
            wu_xing_score += shensha['score']
            score_breakdown['神煞得分'] += shensha['score']
        for yi in self.yi_list:
            wu_xing_score += 10
            score_breakdown['宜事得分'] += 10
        for ji in self.ji_list:
            wu_xing_score -= 15
            score_breakdown['忌事得分'] -= 15
        
        # 新增：集成八字工具整合模块的功能
        if HAS_BAZI_TOOLS:
            # 1. 计算日主十二长生状态，影响旺衰评分
            zhangsheng_score = self._calculate_zhangsheng_score(sizhu)
            wu_xing_score += zhangsheng_score
            score_breakdown['十二长生得分'] = zhangsheng_score
            
            # 2. 分析日课四柱内部地支关系（冲合刑害）
            zhizhi_relation_score = self._calculate_zhizhi_relations(sizhu)
            wu_xing_score += zhizhi_relation_score
            score_breakdown['地支关系得分'] = zhizhi_relation_score
            
            # 3. 纳音五行与事主年命的匹配度（可选）
            nayin_match_score = self._calculate_nayin_match(sizhu, owners)
            wu_xing_score += nayin_match_score
            score_breakdown['纳音匹配得分'] = nayin_match_score
        
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
            return '五行严重不合格，犯大忌，坚决不用'
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
    
    def _generate_wu_xing_details(self, sizhu, owners):
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
        
        # 三合局
        sanhe_groups = {
            '申子辰': '水局', '寅午戌': '火局', '巳酉丑': '金局', '亥卯未': '木局'
        }
        zhi_list = [z[1] for z in zhis]
        for group, ju in sanhe_groups.items():
            count = sum(1 for z in zhi_list if z in group)
            if count >= 2:
                details['地支关系'].append(f"三合{ju}: {', '.join([z[0]+z[1] for z in zhis if z[1] in group])}")
        
        # 六合
        liuhe_pairs = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), 
                       ('辰', '酉'), ('巳', '申'), ('午', '未')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuhe_pairs or (z2, z1) in liuhe_pairs:
                    details['地支关系'].append(f"六合: {z1_name}{z1}合{z2_name}{z2}")
        
        # 六冲
        liuchong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), 
                          ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuchong_pairs or (z2, z1) in liuchong_pairs:
                    details['地支关系'].append(f"六冲: {z1_name}{z1}冲{z2_name}{z2}")
        
        # 六害
        liuhai_pairs = [('子', '未'), ('丑', '午'), ('寅', '巳'), 
                        ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                z1_name, z1 = zhis[i]
                z2_name, z2 = zhis[j]
                if (z1, z2) in liuhai_pairs or (z2, z1) in liuhai_pairs:
                    details['地支关系'].append(f"六害: {z1_name}{z1}害{z2_name}{z2}")
        
        # 三刑
        sanxing_groups = [
            (['寅', '巳', '申'], '无恩之刑'),
            (['丑', '戌', '未'], '恃势之刑'),
            (['子', '卯'], '无礼之刑'),
            (['辰', '午', '酉', '亥'], '自刑')
        ]
        for group, name in sanxing_groups:
            count = sum(1 for z in zhi_list if z in group)
            if count >= 2:
                details['地支关系'].append(f"三刑({name}): {', '.join([z[0]+z[1] for z in zhis if z[1] in group])}")
        
        # 3. 十二长生状态
        day_gan = sizhu.get('day_gan', '')
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
        month_zhi = sizhu.get('月柱', '')[1] if len(sizhu.get('月柱', '')) > 1 else ''
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('日柱', '')[1] if len(sizhu.get('日柱', '')) > 1 else ''
        
        # 天德贵人查法（以月支查日干）
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '甲', '未': '癸', '申': '寅', '酉': '丙',
            '戌': '乙', '亥': '己', '子': '戊', '丑': '庚'
        }
        if month_zhi in tiande_map and day_gan == tiande_map[month_zhi]:
            details['吉神'].append(f"天德贵人: 月支{month_zhi}见日干{day_gan}")
        
        # 月德贵人查法（以月支查日干）
        yuede_map = {
            '寅': '丙', '卯': '丙', '辰': '壬', '巳': '庚',
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
        fuxing_map = {
            '甲': '寅', '乙': '丑', '丙': '子', '丁': '酉',
            '戊': '申', '己': '未', '庚': '午', '辛': '巳',
            '壬': '辰', '癸': '卯'
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
                # 检查相生
                for s1, s2, desc in sheng_relations:
                    if (w1 == s1 and w2 == s2) or (w2 == s1 and w1 == s2):
                        details['五行生克'].append(f"{desc}: {p1}{g1}({w1})与{p2}{g2}({w2})")
                # 检查相克
                for k1, k2, desc in ke_relations:
                    if (w1 == k1 and w2 == k2) or (w2 == k1 and w1 == k2):
                        details['五行生克'].append(f"{desc}: {p1}{g1}({w1})克{p2}{g2}({w2})")
        
        return details
    
    def _calculate_zhangsheng_score(self, sizhu):
        """
        计算日主在各柱的十二长生状态评分
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            int: 十二长生评分
        """
        score = 0
        
        # 检查八字工具整合模块是否可用
        if not HAS_BAZI_TOOLS:
            return score
        
        # 获取日干
        day_gan = sizhu.get('day_gan', '')
        if not day_gan:
            return score
        
        # 十二长生状态评分表
        zhangsheng_scores = {
            '长生': 8,
            '沐浴': 4,
            '冠带': 6,
            '临官': 10,
            '帝旺': 12,
            '衰': 2,
            '病': -2,
            '死': -6,
            '墓': -4,
            '绝': -8,
            '胎': 3,
            '养': 5
        }
        
        # 计算各柱的十二长生状态
        for pillar in ['year', 'month', 'day', 'hour']:
            zhi_key = f'{pillar}_zhi'
            if zhi_key in sizhu:
                zhi = sizhu[zhi_key]
                try:
                    state = get_zhangsheng(day_gan, zhi)
                    if state in zhangsheng_scores:
                        # 月令的影响更大
                        if pillar == 'month':
                            score += zhangsheng_scores[state] * 1.5
                        else:
                            score += zhangsheng_scores[state]
                except Exception:
                    pass
        
        return int(score)
    
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
                    # 三合
                    elif check_sanhe(zhi1, zhi2):
                        score += 6
                    # 六冲
                    elif check_liuchong(zhi1, zhi2):
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
                except Exception:
                    pass
        
        return score
    
    def _calculate_nayin_match(self, sizhu, owners):
        """
        计算纳音五行与事主年命的匹配度
        
        Args:
            sizhu: 四柱信息
            owners: 事主信息
            
        Returns:
            int: 纳音匹配评分
        """
        if not owners:
            return 0
        
        score = 0
        
        # 提取日课各柱纳音
        sizhu_nayin = []
        for pillar in ['年柱', '月柱', '日柱', '时柱']:
            if pillar in sizhu:
                try:
                    nayin = get_nayin(sizhu[pillar])
                    if nayin:
                        sizhu_nayin.append(nayin)
                except Exception:
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
        if sizhu_nayin:
            score += len(sizhu_nayin) * 2
        
        return score
    
    def _get_level(self, score, wu_xing_result, huangdao_info):
        """
        根据分数、五行和黄道判断等级（含星级）
        
        星级标准：
        ⭐⭐⭐⭐⭐ (5星) = 上吉 - 首选推荐，五行大吉+黄道大吉
        ⭐⭐⭐⭐ (4星) = 大吉 - 诸事皆宜，五行大吉
        ⭐⭐⭐ (3星) = 吉 - 可用，五行合格+黄道吉
        ⭐⭐ (2星) = 中吉/次吉 - 可用但需谨慎
        ⭐ (1星) = 平 - 仅适合小事
        ❌ (0星) = 凶 - 坚决不用
        
        冲突处理规则：
        规则一：五行大吉 + 黄道大吉 → ⭐⭐⭐⭐⭐ 上吉（首选推荐）
        规则二：五行大吉 + 黄道黑道 → ⭐⭐ 次吉（可用，可加注"虽有黑道，但五行旺相无碍"或建议化解）
        规则三：五行平平 + 黄道大吉 → ⭐ 平（仅适合小事，大事根基不稳）
        规则四：五行凶 + 任何黄道 → ❌ 凶（坚决不用）
        
        Args:
            score: 综合评分
            wu_xing_result: 五行审核结果
            huangdao_info: 黄道信息
            
        Returns:
            str: 等级（含星级）
        """
        wu_xing_score = wu_xing_result['score']
        huangdao_level = huangdao_info['huang_dao_level']
        da_huang_dao = huangdao_info['da_huang_dao']
        
        # 规则四：五行凶 + 任何黄道 → ❌ 凶（坚决不用）
        if wu_xing_score < 60:
            return '❌ 凶'
        
        # 规则一：五行大吉 + 黄道大吉 → ★★★★★ 上吉（首选推荐）
        if wu_xing_score >= 120 and huangdao_level == '大吉':
            return '★★★★★ 上吉'
        
        # 规则二：五行大吉 + 黄道黑道 → 根据综合评分判断
        if wu_xing_score >= 120 and da_huang_dao['type'] == '凶':
            # 即使黄道是黑道，如果综合评分很高，也应该给予更高的等级
            if score >= 130:
                return '★★★★ 大吉'
            elif score >= 120:
                return '★★★ 吉'
            else:
                return '★★ 次吉'
        
        # 规则三：五行平平 + 黄道大吉 → ★ 平
        if wu_xing_score >= 60 and wu_xing_score < 80 and huangdao_level == '大吉':
            return '★ 平'
        
        # 根据综合评分判断
        if score >= 130:
            return '★★★★★ 上吉'
        elif score >= 120:
            return '★★★★ 大吉'
        elif score >= 100:
            return '★★★ 吉'
        elif score >= 80:
            return '★★ 中吉'
        elif score >= 60:
            return '★ 平'
        else:
            return '❌ 凶'
    
    def _generate_reason(self, wu_xing_result, huangdao_info, yueling_score, xishen_score=0, owner_matches=None):
        """
        生成评分理由

        Args:
            wu_xing_result: 五行审核结果
            huangdao_info: 黄道信息
            yueling_score: 月令评分
            xishen_score: 喜用神匹配评分
            owner_matches: 每个事主的详细匹配信息

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

        # 吉神分析
        if details.get('吉神'):
            jishen = details['吉神']
            if jishen:
                reason.append(f"吉神：{'；'.join(jishen)}")

        # 月令评语
        if yueling_score > 5:
            reason.append(f"月令：得令助，日主旺相")
        elif yueling_score > 0:
            reason.append(f"月令：有生扶，日主得力")
        elif yueling_score == 0:
            reason.append(f"月令：平平，无明显助力")
        elif yueling_score > -5:
            reason.append(f"月令：气弱，需后天补救")
        else:
            reason.append(f"月令：失令，日主乏力")

        # 喜用神匹配评语
        if xishen_score > 20:
            reason.append(f"喜用神：日课大喜事主用神，能量共振极佳")
        elif xishen_score > 10:
            reason.append(f"喜用神：日课补益事主用神，有利催吉")
        elif xishen_score > 0:
            reason.append(f"喜用神：日课对事主有一定补益")
        elif xishen_score == 0:
            reason.append(f"喜用神：日课与事主八字无明显冲突")
        
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
        good_shensha = [s for s in self.shensha_list if s['score'] > 0]
        bad_shensha = [s for s in self.shensha_list if s['score'] < 0]
        
        if good_shensha:
            reason.append('吉神：' + '、'.join([s['name'] for s in good_shensha]))
        if bad_shensha:
            reason.append('凶神：' + '、'.join([s['name'] for s in bad_shensha]))
        
        # 宜忌理由
        if self.yi_list:
            reason.append('宜：' + '、'.join(self.yi_list))
        if self.ji_list:
            reason.append('忌：' + '、'.join(self.ji_list))
        
        return '；'.join(reason)


    def analyze_year(self, year, event_type, owners=None):
        """
        分析年份吉凶
        
        Args:
            year: 年份（如2026）
            event_type: 事项类型
            owners: 事主信息
            
        Returns:
            dict: 年份分析结果
        """
        from datetime import date
        import calendar
        
        # 构建年份的代表性日期（使用该年的1月1日）
        test_date = date(year, 1, 1)
        
        # 计算该年的干支
        try:
            # 尝试从 modules 包导入
            try:
                from modules.四柱计算器 import calculate_sizhu
            except ImportError:
                # 手机环境：直接导入
                from 四柱计算器 import calculate_sizhu
        except ImportError:
            # 无法导入，返回默认结果
            return {
                'year': year,
                'year_gz': '',
                'year_gan': '',
                'year_zhi': '',
                'suitable': True,
                'score': 100,
                'level': '吉',
                'reasons': ['无法计算干支，默认吉'],
                'details': {}
            }
        
        sizhu = calculate_sizhu(test_date, 12, 0)
        year_gan = sizhu.get('year_gan', '')
        year_zhi = sizhu.get('year_zhi', '')
        
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
            'details': {}
        }
        
        # 检查太岁与事主的关系
        if owners:
            for owner in owners:
                if 'birth_date' in owner:
                    try:
                        owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                                   owner.get('birth_hour', 12), 
                                                   owner.get('birth_minute', 0))
                        owner_year_zhi = owner_sizhu.get('year_zhi', '')
                        
                        # 检查冲刑害关系
                        if self.check_liuchong(year_zhi, owner_year_zhi):
                            analysis['suitable'] = False
                            analysis['score'] -= 30
                            analysis['reasons'].append(f"与{owner['name']}年命六冲")
                        elif self.check_po(year_zhi, owner_year_zhi):
                            analysis['score'] -= 20
                            analysis['reasons'].append(f"与{owner['name']}年命相破")
                        elif self.check_xing(year_zhi, owner_year_zhi):
                            analysis['score'] -= 15
                            analysis['reasons'].append(f"与{owner['name']}年命相刑")
                        elif self.check_hai(year_zhi, owner_year_zhi):
                            analysis['score'] -= 10
                            analysis['reasons'].append(f"与{owner['name']}年命相害")
                        elif self.check_liuhe(year_zhi, owner_year_zhi):
                            analysis['score'] += 20
                            analysis['reasons'].append(f"与{owner['name']}年命六合")
                        elif self.check_sanhe([year_zhi, owner_year_zhi]):
                            analysis['score'] += 15
                            analysis['reasons'].append(f"与{owner['name']}年命三合")
                    except:
                        pass
        
        # 对于嫁娶，检查大利年
        if event_type == "嫁娶" and owners:
            for owner in owners:
                if owner.get('name') == '新娘' or owner.get('性别') == '女':
                    # 计算新娘年干
                    if 'birth_date' in owner:
                        try:
                            owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                                       owner.get('birth_hour', 12), 
                                                       owner.get('birth_minute', 0))
                            bride_year_gan = owner_sizhu.get('year_gan', '')
                            
                            # 检查大利年
                            if self._is_dali_year(bride_year_gan, year_gan):
                                analysis['score'] += 30
                                analysis['reasons'].append("新娘大利年")
                            elif self._is_xiaoli_year(bride_year_gan, year_gan):
                                analysis['score'] += 15
                                analysis['reasons'].append("新娘小利年")
                        except:
                            pass
        
        # 如果没有特殊原因，添加基本信息
        if not analysis['reasons']:
            if owners:
                analysis['reasons'].append("年份平和，无冲克")
            else:
                analysis['reasons'].append("未提供事主信息，无法判断")
        
        # 确定等级
        if analysis['score'] >= 120:
            analysis['level'] = '大吉'
        elif analysis['score'] >= 100:
            analysis['level'] = '吉'
        elif analysis['score'] >= 80:
            analysis['level'] = '平'
        elif analysis['score'] >= 60:
            analysis['level'] = '小凶'
        else:
            analysis['level'] = '大凶'
            analysis['suitable'] = False
        
        return analysis
    
    def analyze_month(self, year, month, event_type, owners=None):
        """
        分析月份吉凶
        
        Args:
            year: 年份（如2026）
            month: 月份（1-12）
            event_type: 事项类型
            owners: 事主信息
            
        Returns:
            dict: 月份分析结果
        """
        from datetime import date, timedelta
        
        # 构建月份的代表性日期（使用该月的1日）
        test_date = date(year, month, 1)
        
        # 计算该月的干支
        try:
            # 尝试从 modules 包导入
            try:
                from modules.四柱计算器 import calculate_sizhu
            except ImportError:
                # 手机环境：直接导入
                from 四柱计算器 import calculate_sizhu
        except ImportError:
            # 无法导入，返回默认结果
            return {
                'year': year,
                'month': month,
                'month_gz': '',
                'month_gan': '',
                'month_zhi': '',
                'suitable': True,
                'score': 100,
                'level': '吉',
                'reasons': ['无法计算干支，默认吉'],
                'details': {}
            }
        
        sizhu = calculate_sizhu(test_date, 12, 0)
        month_gan = sizhu.get('month_gan', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        
        # 分析结果
        analysis = {
            'year': year,
            'month': month,
            'month_gz': f"{month_gan}{month_zhi}",
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'suitable': True,
            'score': 100,
            'level': '吉',
            'reasons': [],
            'details': {}
        }
        
        # 检查月破（月支与日支相冲）
        # 这里使用该月1日的日支作为参考
        day_zhi = sizhu.get('day_zhi', '')
        if self.check_liuchong(month_zhi, day_zhi):
            analysis['score'] -= 25
            analysis['reasons'].append('月破')
        
        # 检查月刑
        if self.check_xing(month_zhi, year_zhi):
            analysis['score'] -= 20
            analysis['reasons'].append('月刑')
        
        # 检查月害
        if self.check_hai(month_zhi, year_zhi):
            analysis['score'] -= 15
            analysis['reasons'].append('月害')
        
        # 对于嫁娶，检查大利月、小利月
        if event_type == "嫁娶" and owners:
            for owner in owners:
                if owner.get('name') == '新娘' or owner.get('性别') == '女':
                    # 计算新娘年支
                    if 'birth_date' in owner:
                        try:
                            owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                                       owner.get('birth_hour', 12), 
                                                       owner.get('birth_minute', 0))
                            bride_year_zhi = owner_sizhu.get('year_zhi', '')
                            
                            # 检查该月份包含的所有农历月份
                            lunar_months = set()
                            d = date(year, month, 1)
                            while d.month == month:
                                # 计算每天的月支
                                daily_sizhu = calculate_sizhu(d, 12, 0)
                                daily_month_zhi = daily_sizhu.get('month_zhi', '')
                                # 从月地支获取农历月份
                                lunar_month = self._get_lunar_month_from_zhi(daily_month_zhi)
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
                        except:
                            pass
        
        # 如果没有特殊原因，添加基本信息
        if not analysis['reasons']:
            if owners:
                analysis['reasons'].append("月份平和，无冲克")
            else:
                analysis['reasons'].append("未提供事主信息，无法判断")
        
        # 确定等级
        if analysis['score'] >= 120:
            analysis['level'] = '大吉'
        elif analysis['score'] >= 100:
            analysis['level'] = '吉'
        elif analysis['score'] >= 80:
            analysis['level'] = '平'
        elif analysis['score'] >= 60:
            analysis['level'] = '小凶'
        else:
            analysis['level'] = '大凶'
            analysis['suitable'] = False
        
        return analysis
    
    def _is_dali_year(self, bride_year_gan, year_gan):
        """
        检查是否为新娘大利年
        依据：女命年干与流年干的关系
        """
        # 大利年规则（简化版）
        # 实际规则需要更复杂的计算，这里使用简化版本
        # 基于女命年干与流年干的相合关系
        tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        if bride_year_gan and year_gan:
            try:
                bride_index = tian_gan.index(bride_year_gan)
                year_index = tian_gan.index(year_gan)
                # 六合关系
                liuhe_pairs = [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]
                return (bride_index, year_index) in liuhe_pairs
            except ValueError:
                pass
        return False
    
    def _is_xiaoli_year(self, bride_year_gan, year_gan):
        """
        检查是否为新娘小利年
        """
        # 小利年规则（简化版）
        tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        if bride_year_gan and year_gan:
            try:
                bride_index = tian_gan.index(bride_year_gan)
                year_index = tian_gan.index(year_gan)
                # 相生关系
                sheng_pairs = [(0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 8), (7, 9), (8, 0), (9, 1)]
                return (bride_index, year_index) in sheng_pairs
            except ValueError:
                pass
        return False
    
    def _get_lunar_month_from_zhi(self, month_zhi):
        """
        从月地支获取农历月份
        """
        zhi_to_month = {
            '寅': 1, '卯': 2, '辰': 3, '巳': 4, '午': 5, '未': 6,
            '申': 7, '酉': 8, '戌': 9, '亥': 10, '子': 11, '丑': 12
        }
        return zhi_to_month.get(month_zhi, 1)
    
    def _check_li_yue(self, bride_year_zhi, month):
        """
        检查是否为新娘大利月或小利月
        
        规则：
        - 大利月：新娘年支的六合月
        - 小利月：新娘年支的三合月
        """
        # 地支六合关系
        liuhe = {
            '子': '丑', '丑': '子', '寅': '亥', '卯': '戌',
            '辰': '酉', '巳': '申', '午': '未', '未': '午',
            '申': '巳', '酉': '辰', '戌': '卯', '亥': '寅'
        }
        
        # 地支三合局
        sanhe = {
            '子': ['申', '辰'], '丑': ['巳', '酉'], '寅': ['午', '戌'],
            '卯': ['未', '亥'], '辰': ['子', '申'], '巳': ['丑', '酉'],
            '午': ['寅', '戌'], '未': ['卯', '亥'], '申': ['子', '辰'],
            '酉': ['丑', '巳'], '戌': ['寅', '午'], '亥': ['卯', '未']
        }
        
        # 地支对应的月份
        zhi_to_month = {
            '寅': 1, '卯': 2, '辰': 3, '巳': 4, '午': 5, '未': 6,
            '申': 7, '酉': 8, '戌': 9, '亥': 10, '子': 11, '丑': 12
        }
        
        if bride_year_zhi in liuhe:
            # 计算大利月
            dali_zhi = liuhe[bride_year_zhi]
            dali_month = zhi_to_month.get(dali_zhi, 0)
            if month == dali_month:
                return '大利月'
        
        if bride_year_zhi in sanhe:
            # 计算小利月
            xiaoli_zhis = sanhe[bride_year_zhi]
            for zhi in xiaoli_zhis:
                xiaoli_month = zhi_to_month.get(zhi, 0)
                if month == xiaoli_month:
                    return '小利月'
        
        # 妨夫月、妨妻月（简化判断）
        # 一般来说，除了大利月、小利月外，其他月份需要谨慎
        return '普通月'

# 全局评分器实例
scorer = Scorer()

def calculate_score(sizhu, event_type, owners=None, house_type=None, shan_xiang=None,
                    zaoxiang=None, zaowei=None, chuangwei=None):
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
        
    Returns:
        dict: 评分结果
    """
    return scorer.score(sizhu, event_type, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei)
