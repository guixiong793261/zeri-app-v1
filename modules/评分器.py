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
                # 从sizhu字段提取日柱
                if 'sizhu' in owner:
                    sizhu_parts = owner['sizhu'].split()
                    if len(sizhu_parts) >= 1:
                        bride_bazi['year_zhi'] = sizhu_parts[0][1]  # 年支
                    if len(sizhu_parts) >= 3:
                        bride_bazi['ri_gan'] = sizhu_parts[2][0]  # 日干
                        bride_bazi['ri_zhi'] = sizhu_parts[2][1]  # 日支
                # 从birth_date计算
                if 'birth_date' in owner:
                    try:
                        from .四柱计算器 import calculate_sizhu
                        birth_sizhu = calculate_sizhu(
                            owner['birth_date'],
                            owner.get('birth_hour', 12),
                            owner.get('birth_minute', 0)
                        )
                        bride_bazi['year_zhi'] = birth_sizhu['年柱'][1]
                        bride_bazi['ri_gan'] = birth_sizhu['日柱'][0]
                        bride_bazi['ri_zhi'] = birth_sizhu['日柱'][1]
                    except Exception as e:
                        logger.error(f"提取新娘八字失败: {e}")
            
            # 提取新郎信息
            if role == '新郎' or gender == '男':
                groom_bazi = {}
                if 'sizhu' in owner:
                    sizhu_parts = owner['sizhu'].split()
                    if len(sizhu_parts) >= 3:
                        groom_bazi['ri_gan'] = sizhu_parts[2][0]
                        groom_bazi['ri_zhi'] = sizhu_parts[2][1]
                if 'birth_date' in owner:
                    try:
                        from .四柱计算器 import calculate_sizhu
                        birth_sizhu = calculate_sizhu(
                            owner['birth_date'],
                            owner.get('birth_hour', 12),
                            owner.get('birth_minute', 0)
                        )
                        groom_bazi['ri_gan'] = birth_sizhu['日柱'][0]
                        groom_bazi['ri_zhi'] = birth_sizhu['日柱'][1]
                    except Exception as e:
                        logger.error(f"提取新郎八字失败: {e}")
        
        return bride_bazi, groom_bazi
    
    def score(self, sizhu, event_type, owners=None, house_type=None, shan_xiang=None,
              zaoxiang=None, zaowei=None, chuangwei=None, direction=None, jian_xiang=None):
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
            # 合并山向和兼向
            full_shan_xiang = shan_xiang
            if shan_xiang and jian_xiang and jian_xiang != '正中':
                full_shan_xiang = f"{shan_xiang}{jian_xiang}"
            
            # ========== 婚嫁专用评分 ==========
            if event_type == '嫁娶':
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
                        marriage_result = score_marriage_day(date_obj, bride_bazi, groom_bazi)
                        
                        if marriage_result.get('reject_reason'):
                            # 即使有否决项，也要计算五行分析等详细信息
                            wu_xing_result = self._check_wu_xing(sizhu, event_type, owners,
                                                                  house_type, shan_xiang,
                                                                  zaoxiang, zaowei, chuangwei,
                                                                  direction=direction)
                            
                            # 计算基本评分详情
                            yueling_score = self._calculate_yueling_help(sizhu)
                            xishen_score = 0
                            if owners:
                                xishen_score, _ = self._calculate_xishen_match(sizhu, owners)
                            
                            score_details = {
                                '五行评分': wu_xing_result.get('score', 0),
                                '月令得分': yueling_score,
                                '喜用神得分': xishen_score,
                                '黄道得分': 0,
                                '总分': 0
                            }
                            
                            # 生成综合评语（包含月令分析）
                            reason_parts = [marriage_result['reject_reason']]
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
                                'ji_list': [marriage_result['reject_reason']],
                                'huangdao_info': self.huangdao_info,
                                'marriage_details': marriage_result.get('details', []),
                                'warnings': marriage_result.get('warnings', []),
                                'wu_xing_result': wu_xing_result,
                                'score_details': score_details,
                                'sizhu': sizhu
                            }
                        
                        # 计算正五行喜用神得分（作为补充）
                        xishen_score = 0
                        if owners:
                            xishen_score, _ = self._calculate_xishen_match(sizhu, owners)
                        
                        # 计算月令得分
                        yueling_score = self._calculate_yueling_help(sizhu)
                        
                        # 计算黄道信息（用于显示）
                        # 注意：黄道得分已包含在marriage_result['score']中，不需要重复加
                        self.huangdao_info = calculate_huangdao(sizhu)

                        # 计算太阳太阴得分
                        sun_moon_info = calculate_sun_moon_position(sizhu, shan_xiang)
                        sun_moon_score = sun_moon_info.get('score', 0)

                        # 综合得分 = 婚嫁评分（含黄道得分）+ 喜用神得分 + 月令得分 + 太阳太阴得分
                        # 注意：黄道得分已包含在marriage_result['score']中，不再重复加
                        total_score = marriage_result['score'] + xishen_score + yueling_score + sun_moon_score

                        # 重新确定等级（婚嫁专用）
                        if total_score >= 150:
                            level = '★★★★★ 上吉'
                        elif total_score >= 130:
                            level = '★★★★ 大吉'
                        elif total_score >= 110:
                            level = '★★★ 吉'
                        elif total_score >= 90:
                            level = '★★ 次吉'
                        elif total_score >= 70:
                            level = '★ 平'
                        else:
                            level = '❌ 凶'

                        # 构建详细得分明细
                        score_details = {
                            '基础分': self.base_score,
                            '五行评分': marriage_result['score'],
                            '月令得分': yueling_score,
                            '喜用神得分': xishen_score,
                            '太阳太阴得分': sun_moon_score,
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
                                return {
                                    'he_ge': False,
                                    'score': 0,
                                    'ji_yu': veto_reason,
                                    'details': wu_xing_details,
                                    'score_breakdown': {},
                                    'has_deduction': False
                                }
                        else:
                            self.yi_list, self.ji_list = result
                        
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
                                                                         owner.get('birth_minute', 0))
                                            bride_year_zhi = owner_sizhu.get('year_zhi', '')
                                            if bride_year_zhi:
                                                # 从月地支获取农历月份
                                                month_zhi = sizhu.get('month_zhi', '')
                                                zhi_to_month = {'寅': 1, '卯': 2, '辰': 3, '巳': 4, '午': 5, '未': 6,
                                                                '申': 7, '酉': 8, '戌': 9, '亥': 10, '子': 11, '丑': 12}
                                                lunar_month = zhi_to_month.get(month_zhi, 0)
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
                        
                        # 生成综合评语（包含月令分析）
                        reason_parts = []
                        reason_parts.append(marriage_result['reason'])
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
                            'sizhu': sizhu  # 添加sizhu信息，用于二十四山等后续处理
                        }
                    else:
                        # date_obj为None，无法进行婚嫁评分，继续执行通用评分逻辑
                        logger.warning("无法构建日期对象，跳过婚嫁评分算法")
                except ImportError:
                    logger.warning("婚嫁评分算法模块未找到，使用通用评分")
            
            # ========== 通用评分逻辑 ==========
            # 第一步：正五行审核（核心门槛）
            wu_xing_result = self._check_wu_xing(sizhu, event_type, owners,
                                                    house_type, shan_xiang,
                                                    zaoxiang, zaowei, chuangwei,
                                                    direction=direction)

            # 如果五行不合格（犯三杀、冲山等大忌），直接返回"❌ 凶"
            if not wu_xing_result['he_ge']:
                # 计算完整评分详情（保持严格模式，但显示各项得分）
                yueling_score = self._calculate_yueling_help(sizhu)
                xishen_score, _ = self._calculate_xishen_match(sizhu, owners)
                
                # 计算黄道得分（即使一票否决，也显示详情）
                self.huangdao_info = calculate_huangdao(sizhu)
                huangdao_score = self.huangdao_info.get('huang_dao_score', 0)
                
                # 计算太阳太阴得分
                sun_moon_info = calculate_sun_moon_position(sizhu, shan_xiang)
                sun_moon_score = sun_moon_info.get('score', 0)
                
                # 计算神煞得分
                shensha_score = sum(s.get('score', 0) for s in self.shensha_list if isinstance(s, dict))
                
                # 构建完整的评分详情
                score_details = {
                    '基础分': self.base_score,
                    '五行评分': wu_xing_result.get('score', 0),
                    '月令得分': yueling_score,
                    '喜用神得分': xishen_score,
                    '黄道得分': huangdao_score,
                    '太阳太阴得分': sun_moon_score,
                    '神煞得分': shensha_score,
                    '总分': 0  # 一票否决，总分仍为0
                }
                
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
                    'huangdao_info': self.huangdao_info,
                    'wu_xing_result': wu_xing_result,
                    'score_details': score_details,
                    'sun_moon_info': sun_moon_info,
                    'sizhu': sizhu  # 添加sizhu信息，用于二十四山等后续处理
                }

            # 第二步：月令对日主的帮助评分
            yueling_score = self._calculate_yueling_help(sizhu)

            # 第三步：日课五行与事主喜用神匹配评分（正五行择日法核心）
            xishen_score, owner_matches = self._calculate_xishen_match(sizhu, owners)

            # 第四步：大小黄道审核（加分/减分项）
            self.huangdao_info = calculate_huangdao(sizhu)
            huangdao_score = self.huangdao_info.get('huang_dao_score', 0)

            # 第五步：太阳太阴到山到向分析
            sun_moon_info = calculate_sun_moon_position(sizhu, shan_xiang)
            sun_moon_score = sun_moon_info.get('score', 0)

            # 计算最终得分：五行评分已经包含了神煞得分，不需要再重复加
            # 五行评分 = 基础分 + 神煞得分 + 宜事得分 + 忌事得分 + 十二长生得分 + 地支关系得分 + 纳音匹配得分 + 相主得分
            # 所以最终得分 = 五行评分 + 月令得分 + 喜用神得分 + 黄道得分 + 太阳太阴得分
            self.final_score = wu_xing_result['score'] + yueling_score + xishen_score + huangdao_score + sun_moon_score

            # 总分上限控制：防止加分项过度累积，普通吉课最高150分，大吉最高180分
            max_score = 180
            if self.final_score > max_score:
                self.final_score = max_score

            # 第五步：综合评定
            self.level = self._get_level(self.final_score, wu_xing_result, self.huangdao_info)

            # 构建详细得分明细
            # 注意：神煞得分已包含在五行评分中，不需要单独列出
            score_details = {
                '基础分': self.base_score,
                '五行评分': wu_xing_result['score'],
                '月令得分': yueling_score,
                '喜用神得分': xishen_score,
                '黄道得分': huangdao_score,
                '太阳太阴得分': sun_moon_score,
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
                'reason': self._generate_reason(wu_xing_result, self.huangdao_info, yueling_score, xishen_score, owner_matches, sun_moon_info),
                'shensha_list': self.shensha_list,
                'yi_list': self.yi_list,
                'ji_list': self.ji_list,
                'huangdao_info': self.huangdao_info,
                'wu_xing_result': wu_xing_result,
                'score_details': score_details,
                'sun_moon_info': sun_moon_info,
                'sizhu': sizhu  # 添加sizhu信息，用于二十四山等后续处理
            }

        except Exception as e:
            import traceback
            error_msg = f"评分计算异常: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            # 返回错误结果而不是崩溃
            return {
                'score': 0,
                'level': '❌ 计算错误',
                'reason': f"评分计算异常: {str(e)}",
                'shensha_list': [],
                'yi_list': [],
                'ji_list': [],
                'huangdao_info': {},
                'wu_xing_result': {'he_ge': False, 'ji_yu': f"计算错误: {str(e)}", 'score': 0},
                'score_details': {},
                'sun_moon_info': {},
                'error': error_msg
            }

    def analyze_year(self, year, event_type, owners=None, shan_xiang=None, jian_xiang=None, direction=None):
        """
        分析年份吉凶

        Args:
            year: 年份（如2026）
            event_type: 事项类型
            owners: 事主信息
            shan_xiang: 山向信息
            jian_xiang: 兼向信息
            direction: 动土方位

        Returns:
            dict: 年份分析结果
        """
        from datetime import date
        import calendar
        
        # 构建年份的代表性日期（使用该年的1月1日）
        test_date = date(year, 1, 1)
        
        # 计算该年的干支
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
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
        
        # 对于嫁娶，检查大利年
        if event_type == "嫁娶" and owners:
            for owner in owners:
                if owner.get('role') == '新娘' or owner.get('性别') == '女':
                    # 计算新娘年干
                    if 'birth_date' in owner:
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
        
        # 对于修造类事项，分析年煞和二十四山方位吉凶（仅提供信息，不扣分）
        if event_type in ['修造', '动土', '装修', '入宅']:
            # 年三煞分析
            # 年三煞方位映射
            year_sansha_map = {
                '申': ['巳', '丙', '午'],  # 申子辰年煞南
                '子': ['巳', '丙', '午'],
                '辰': ['巳', '丙', '午'],
                '寅': ['亥', '壬', '子'],  # 寅午戌年煞北
                '午': ['亥', '壬', '子'],
                '戌': ['亥', '壬', '子'],
                '巳': ['寅', '甲', '卯'],  # 巳酉丑年煞东
                '酉': ['寅', '甲', '卯'],
                '丑': ['寅', '甲', '卯'],
                '亥': ['申', '庚', '酉'],  # 亥卯未年煞西
                '卯': ['申', '庚', '酉'],
                '未': ['申', '庚', '酉']
            }

            sansha_fang = year_sansha_map.get(year_zhi, [])
            if sansha_fang:
                # 仅提供信息，不扣分
                analysis['reasons'].append(f"年三煞在{''.join(sansha_fang)}方（忌修造）")
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
                analysis['reasons'].append(f"太岁在{taisui_fang}方（忌动土）")
                analysis['details']['太岁'] = taisui_fang

                # 如果提供了山向，分析山向与太岁的关系
                if full_shan_xiang:
                    # 提取山向中的所有方向信息（包括兼向）
                    shan_xiang_dirs = [full_shan_xiang[0]]
                    # 如果有兼向，提取兼向的方位
                    if '兼' in full_shan_xiang:
                        jian_index = full_shan_xiang.find('兼')
                        if jian_index + 1 < len(full_shan_xiang):
                            shan_xiang_dirs.append(full_shan_xiang[jian_index + 1])
                    
                    # 检查所有方向是否犯太岁
                    for shan_xiang_dir in shan_xiang_dirs:
                        if shan_xiang_dir == taisui_fang:
                            analysis['reasons'].append(f"所选山向{full_shan_xiang}犯太岁，不利动土")
                            analysis['details']['山向犯太岁'] = True
                            analysis['suitable'] = False
                            analysis['score'] = 0
                            analysis['level'] = '大凶'
                            break

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
                analysis['reasons'].append(f"岁破在{suipo_fang}方（忌修造）")
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
        elif analysis['score'] >= 40:
            # 分数在40-60之间仍视为小凶，可用但不推荐
            analysis['level'] = '小凶'
        else:
            analysis['level'] = '大凶'
            analysis['suitable'] = False
        
        return analysis
    
    def analyze_month(self, year, month, event_type, owners=None, shan_xiang=None, direction=None):
        """
        分析月份吉凶

        Args:
            year: 年份（如2026）
            month: 月份（1-12）
            event_type: 事项类型
            owners: 事主信息
            shan_xiang: 山向信息
            direction: 动土方位

        Returns:
            dict: 月份分析结果
        """
        from datetime import date, timedelta
        
        # 首先检查年份是否适合，如果年份不适合，则月份也不适合
        year_analysis = self.analyze_year(year, event_type, owners, shan_xiang, direction)
        if not year_analysis['suitable']:
            # 如果年份不适合，直接返回年份分析结果（作为月份分析结果）
            analysis = year_analysis.copy()
            analysis['month'] = month
            analysis['month_gz'] = ''
            analysis['month_gan'] = ''
            analysis['month_zhi'] = ''
            analysis['reasons'] = [f"年份{year}不适合{event_type}，该年所有月份均不宜"] + year_analysis['reasons']
            return analysis
        
        # 构建月份的代表性日期（使用该月的1日）
        test_date = date(year, month, 1)
        
        # 计算该月的干支
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
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
        
        # 检查月份与事主生肖的关系
        if owners:
            for owner in owners:
                if 'birth_date' in owner:
                    owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                               owner.get('birth_hour', 12), 
                                               owner.get('birth_minute', 0))
                    owner_year_zhi = owner_sizhu.get('year_zhi', '')
                    
                    # 检查冲刑害关系
                    if self.check_liuchong(month_zhi, owner_year_zhi):
                        analysis['suitable'] = False
                        analysis['score'] -= 25
                        analysis['reasons'].append(f"月支与{owner['name']}生肖相冲")
                    elif self.check_po(month_zhi, owner_year_zhi):
                        analysis['score'] -= 15
                        analysis['reasons'].append(f"月支与{owner['name']}生肖相破")
                    elif self.check_xing(month_zhi, owner_year_zhi):
                        analysis['score'] -= 10
                        analysis['reasons'].append(f"月支与{owner['name']}生肖相刑")
                    elif self.check_hai(month_zhi, owner_year_zhi):
                        analysis['score'] -= 8
                        analysis['reasons'].append(f"月支与{owner['name']}生肖相害")
                    elif self.check_liuhe(month_zhi, owner_year_zhi):
                        analysis['score'] += 15
                        analysis['reasons'].append(f"月支与{owner['name']}生肖六合")
                    elif self.check_sanhe([month_zhi, owner_year_zhi]):
                        analysis['score'] += 10
                        analysis['reasons'].append(f"月支与{owner['name']}生肖三合")
        
        # 对于修造类事项，分析月煞和二十四山方位吉凶（仅提供信息，不扣分）
        if event_type in ['修造', '动土', '装修', '入宅']:
            # 阴府检测：月干若为正/傍阴府，则直接判定为不可用
            if shan_xiang:
                # 使用新的阴府配置表
                try:
                    from modules.二十四山择吉天机 import get_yinfu_config
                    
                    yinfu_config = get_yinfu_config(shan_xiang)
                    if yinfu_config:
                        ji_gan_list = yinfu_config.get('忌干', [])
                        yinfu_type = yinfu_config.get('type', '傍阴府')
                        
                        # 检查月干是否犯阴府
                        month_gan = analysis.get('month_gan', '')
                        if month_gan and month_gan in ji_gan_list:
                            # 根据阴府类型采取不同的处理方式
                            if yinfu_type == '正阴府':
                                # 正阴府：单干也大忌，一票否决
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
            
            # 月三煞分析
            # 月三煞方位映射
            month_sansha_map = {
                '申': ['巳', '丙', '午', '丁', '未'],  # 申子辰月煞南
                '子': ['巳', '丙', '午', '丁', '未'],
                '辰': ['巳', '丙', '午', '丁', '未'],
                '寅': ['亥', '壬', '子', '癸', '丑'],  # 寅午戌月煞北
                '午': ['亥', '壬', '子', '癸', '丑'],
                '戌': ['亥', '壬', '子', '癸', '丑'],
                '巳': ['寅', '甲', '卯', '乙', '辰'],  # 巳酉丑月煞东
                '酉': ['寅', '甲', '卯', '乙', '辰'],
                '丑': ['寅', '甲', '卯', '乙', '辰'],
                '亥': ['申', '庚', '酉', '辛', '戌'],  # 亥卯未月煞西
                '卯': ['申', '庚', '酉', '辛', '戌'],
                '未': ['申', '庚', '酉', '辛', '戌']
            }
            
            sansha_fang = month_sansha_map.get(month_zhi, [])
            if sansha_fang:
                # 仅提供信息，不扣分
                analysis['reasons'].append(f"月三煞在{''.join(sansha_fang)}方（忌修造）")
                analysis['details']['月三煞'] = sansha_fang
                
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
                        # 兼向时只取主地支
                        zuoshan_zhis = ['丑'] if has_jianxiang else ['丑', '寅']
                    elif zuoshan in ['甲', '卯', '乙']:
                        zuoshan_zhis = ['卯']
                    elif zuoshan in ['辰', '巽', '巳']:
                        # 兼向时只取主地支
                        zuoshan_zhis = ['辰'] if has_jianxiang else ['辰', '巳']
                    elif zuoshan in ['丙', '午', '丁']:
                        zuoshan_zhis = ['午']
                    elif zuoshan in ['未', '坤', '申']:
                        # 兼向时只取主地支
                        zuoshan_zhis = ['未'] if has_jianxiang else ['未', '申']
                    elif zuoshan in ['庚', '酉', '辛']:
                        zuoshan_zhis = ['酉']
                    elif zuoshan in ['戌', '乾', '亥']:
                        # 兼向时只取主地支（乾卦以戌为主）
                        zuoshan_zhis = ['戌'] if has_jianxiang else ['戌', '亥']
                    
                    # 检查坐山是否在月三煞方（仅检查主坐山，兼向不单独判定三煞）
                    # 使用更精确的方位判定：只有当坐山地支是煞方的核心地支时才判定为犯煞
                    # 核心地支：煞南(午)、煞北(子)、煞东(卯)、煞西(酉)
                    core_sansha = {
                        '巳': '午', '丙': '午', '午': '午', '丁': '午', '未': '午',  # 南
                        '亥': '子', '壬': '子', '子': '子', '癸': '子', '丑': '子',  # 北
                        '寅': '卯', '甲': '卯', '卯': '卯', '乙': '卯', '辰': '卯',  # 东
                        '申': '酉', '庚': '酉', '酉': '酉', '辛': '酉', '戌': '酉',  # 西
                    }
                    
                    zuoshan_fan_sansha = False
                    for zuoshan_zhi in zuoshan_zhis:
                        # 获取煞方的核心方向
                        sansha_core = core_sansha.get(zuoshan_zhi, '')
                        if sansha_core:
                            # 检查煞方中是否包含该核心方向
                            if sansha_core in sansha_fang:
                                zuoshan_fan_sansha = True
                                break
                    
                    if zuoshan_fan_sansha:
                        analysis['reasons'].append(f"所选山向{shan_xiang}坐山犯月三煞，不利修造")
                        analysis['details']['山向犯月煞'] = True
                        # 月三煞不再一票否决，改为扣分
                        analysis['score'] -= 25
                        # 只有主坐山犯煞才设为凶，兼向犯煞不额外扣分
                        if zuoshan_zhi == zuoshan_zhis[0]:  # 主坐山
                            analysis['level'] = '凶'
                        # 不设置suitable为False
            
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
                analysis['reasons'].append(f"月破在{yuepo_fang}方（忌修造）")
                analysis['details']['月破'] = yuepo_fang
                
                # 如果提供了山向，分析山向与月破的关系
                if shan_xiang:
                    shan_xiang_dir = shan_xiang[0]
                    if shan_xiang_dir == yuepo_fang:
                        analysis['reasons'].append(f"所选山向{shan_xiang}犯月破，不利修造")
                        analysis['details']['山向犯月破'] = True
            
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
                analysis['reasons'].append(f"暗建煞在{''.join(anjian_fang)}方（忌修造）")
                analysis['details']['暗建煞'] = anjian_fang
                
                # 如果提供了山向，分析山向与暗建煞的关系
                if shan_xiang:
                    shan_xiang_dir = shan_xiang[0]
                    if shan_xiang_dir in anjian_fang:
                        analysis['reasons'].append(f"所选山向{shan_xiang}犯暗建煞，不利修造")
                        analysis['details']['山向犯暗建煞'] = True
            
            # 五行择月法分析
            if shan_xiang and self.wuxing_selector:
                wuxing_result = self.wuxing_selector.analyze_month_by_wuxing(year, month, shan_xiang)
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
            
            # 增强山向分析：考虑所有山向的相关方位（仅在未犯月三煞时执行）
            if shan_xiang and event_type in ['修造', '动土', '装修', '入宅'] and analysis['suitable']:
                # 定义各山向的相关方位（二十四山）
                mountain_related = {
                    '乾': ['乾', '戌', '亥'],
                    '坤': ['坤', '未', '申'],
                    '艮': ['艮', '寅', '丑'],
                    '巽': ['巽', '辰', '巳'],
                    '甲': ['甲', '寅', '卯'],
                    '乙': ['乙', '卯', '辰'],
                    '丙': ['丙', '巳', '午'],
                    '丁': ['丁', '午', '未'],
                    '庚': ['庚', '申', '酉'],
                    '辛': ['辛', '酉', '戌'],
                    '壬': ['壬', '亥', '子'],
                    '癸': ['癸', '子', '丑'],
                    '子': ['子', '壬', '癸'],
                    '丑': ['丑', '癸', '艮'],
                    '寅': ['寅', '艮', '甲'],
                    '卯': ['卯', '甲', '乙'],
                    '辰': ['辰', '乙', '巽'],
                    '巳': ['巳', '巽', '丙'],
                    '午': ['午', '丙', '丁'],
                    '未': ['未', '丁', '坤'],
                    '申': ['申', '坤', '庚'],
                    '酉': ['酉', '庚', '辛'],
                    '戌': ['戌', '辛', '乾'],
                    '亥': ['亥', '乾', '壬']
                }
                
                # 标记是否已经因为月三煞扣分
                sansha_deducted = analysis['details'].get('山向犯月煞', False)
                
                # 处理特殊情况：山向组合（如坤山艮向）
                if '山' in shan_xiang:
                    parts = shan_xiang.split('山')
                    if len(parts) > 1:
                        # 提取坐山和朝向
                        zuo_shan = parts[0]
                        if '兼' in parts[1]:
                            xiang = parts[1].split('兼')[0]
                        elif '向' in parts[1]:
                            xiang = parts[1].split('向')[0]
                        else:
                            xiang = parts[1].strip()
                        
                        # 检查坐山
                        if zuo_shan in mountain_related:
                            related_dirs = mountain_related[zuo_shan]
                            # 检查月三煞是否影响坐山相关方位（仅在未扣过分时执行）
                            if sansha_fang and not sansha_deducted:
                                for fang in related_dirs:
                                    if fang in sansha_fang:
                                        analysis['reasons'].append(f"月三煞在{fang}方，冲克{zuo_shan}山")
                                        analysis['details'][f'{zuo_shan}山犯月三煞'] = True
                                        analysis['score'] -= 25
                                        analysis['level'] = '凶'
                                        sansha_deducted = True
                                        break
                            # 检查月破是否影响坐山相关方位
                            if yuepo_fang:
                                if yuepo_fang in related_dirs:
                                    analysis['reasons'].append(f"月破在{yuepo_fang}方，冲克{zuo_shan}山")
                                    analysis['details'][f'{zuo_shan}山犯月破'] = True
                                    analysis['score'] -= 20
                                    analysis['level'] = '凶'
                                    # 不设置suitable为False
                        
                        # 检查朝向（仅在未扣过分时执行）
                        if xiang and xiang in mountain_related and not sansha_deducted:
                            related_dirs = mountain_related[xiang]
                            # 检查月三煞是否影响朝向相关方位
                            if sansha_fang:
                                for fang in related_dirs:
                                    if fang in sansha_fang:
                                        analysis['reasons'].append(f"月三煞在{fang}方，冲克{xiang}向")
                                        analysis['details'][f'{xiang}向犯月三煞'] = True
                                        analysis['score'] -= 25
                                        analysis['level'] = '凶'
                                        # 不设置suitable为False
                                        break
                            # 检查月破是否影响朝向相关方位
                            if yuepo_fang:
                                if yuepo_fang in related_dirs:
                                    analysis['reasons'].append(f"月破在{yuepo_fang}方，冲克{xiang}向")
                                    analysis['details'][f'{xiang}向犯月破'] = True
                                    analysis['score'] -= 20
                                    analysis['level'] = '凶'
                                    # 不设置suitable为False

        # 对于嫁娶，检查大利月、小利月
        if event_type == "嫁娶" and owners:
            for owner in owners:
                if owner.get('role') == '新娘' or owner.get('性别') == '女':
                    # 计算新娘年支
                    if 'birth_date' in owner:
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
        elif analysis['score'] >= 40:
            # 分数在40-60之间仍视为小凶，可用但不推荐
            analysis['level'] = '小凶'
        else:
            analysis['level'] = '大凶'
            analysis['suitable'] = False
        
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
                    owner.get('birth_minute', 0)
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
        
        month_zhi = sizhu.get('month_zhi', '')
        
        analysis = {
            'has_shan_xiang': True,
            'shan_xiang': shan_xiang,
            'month_sansha': [],
            'yuepo': '',
            'matches': []
        }
        
        # 月三煞
        month_sansha_map = {
            '申': ['巳', '丙', '午'], '子': ['巳', '丙', '午'], '辰': ['巳', '丙', '午'],
            '寅': ['亥', '壬', '子'], '午': ['亥', '壬', '子'], '戌': ['亥', '壬', '子'],
            '巳': ['寅', '甲', '卯'], '酉': ['寅', '甲', '卯'], '丑': ['寅', '甲', '卯'],
            '亥': ['申', '庚', '酉'], '卯': ['申', '庚', '酉'], '未': ['申', '庚', '酉']
        }
        analysis['month_sansha'] = month_sansha_map.get(month_zhi, [])
        
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
                            owner.get('birth_minute', 0)
                        )
                        owner_year_zhi = owner_sizhu.get('year_zhi', '')
                        day_zhi = sizhu.get('day_zhi', '')
                        if self.check_liuchong(day_zhi, owner_year_zhi):
                            suggestions.append(f'{owner_name}生肖与日支相冲，需注意')
                    except:
                        pass
        
        return suggestions if suggestions else ['此日课整体吉利，可放心使用']
    
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
    
    def _check_li_yue(self, bride_year_zhi, month):
        """
        检查嫁娶大利月、小利月
        依据：女命年支与月份的关系
        """
        # 大利月、小利月表（基于女命年支）
        # 口诀：正七迎鸡兔，二八虎和猴，三九蛇共猪，四十龙和狗，牛羊五十一，鼠马六腊月
        # 兔(卯)、鸡(酉)：正七月；虎(寅)、猴(申)：二八月；蛇(巳)、猪(亥)：三九月
        # 龙(辰)、狗(戌)：四月、十月；牛(丑)、羊(未)：五月、十一月；鼠(子)、马(午)：六月、十二月
        
        li_yue_table = {
            '子': {'大利月': [6, 12], '小利月': [3, 9]},
            '午': {'大利月': [6, 12], '小利月': [3, 9]},
            '丑': {'大利月': [5, 11], '小利月': [1, 7]},
            '未': {'大利月': [5, 11], '小利月': [1, 7]},
            '寅': {'大利月': [2, 8], '小利月': [3, 9]},
            '申': {'大利月': [2, 8], '小利月': [3, 9]},
            '卯': {'大利月': [1, 7], '小利月': [6, 12]},
            '酉': {'大利月': [1, 7], '小利月': [6, 12]},
            '辰': {'大利月': [4, 10], '小利月': [5, 11]},
            '戌': {'大利月': [4, 10], '小利月': [5, 11]},
            '巳': {'大利月': [3, 9], '小利月': [2, 8]},
            '亥': {'大利月': [3, 9], '小利月': [2, 8]}
        }
        
        if bride_year_zhi in li_yue_table:
            if month in li_yue_table[bride_year_zhi]['大利月']:
                return '大利月'
            elif month in li_yue_table[bride_year_zhi]['小利月']:
                return '小利月'
        
        # 妨夫月、妨妻月（简化判断）
        # 一般来说，除了大利月、小利月外，其他月份需要谨慎
        return '普通月'
    
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

            total_score += owner_score
            owner_matches.append({
                'name': owner_name,
                'score': owner_score,
                'details': match_details,
                'xishen': owner_xishen,
                'yongshen': owner_yongshen
            })

        return total_score, owner_matches
    
    def _check_owner_day_zhichong(self, sizhu, owners):
        """
        检查日课日支与事主日支的冲合关系（相主原则）
        
        正五行择日法强调"相主"，必须检查日课日支与事主日支的关系：
        - 日课日支冲事主日支：大凶，-20分
        - 日课日支刑事主日支：凶，-10分
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
                        owner.get('birth_minute', 0)
                    )
                    owner_day_zhi = owner_sizhu.get('day_zhi', '')
                except Exception as e:
                    logger.error(f"计算事主{owner_name}日柱失败: {str(e)}")
                    pass
            
            if not owner_day_zhi:
                continue
            
            try:
                # 六冲检查
                if check_liuchong(day_zhi, owner_day_zhi):
                    score = -20
                    total_score += score
                    details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}相冲，{score}分")
                # 三刑检查
                elif check_xing(day_zhi, owner_day_zhi):
                    score = -10
                    total_score += score
                    details.append(f"{owner_name}日支{owner_day_zhi}与日课日支{day_zhi}相刑，{score}分")
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
            except Exception as e:
                logger.error(f"相主检查失败({owner_name}日支{owner_day_zhi}与日课日支{day_zhi}): {str(e)}")
                pass
        
        return total_score, details
    
    def _check_wu_xing(self, sizhu, event_type, owners, house_type, shan_xiang,
                      zaoxiang, zaowei, chuangwei, direction=None):
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
        construction_events = ['修造', '动土', '装修']
        
        # 对于修造类事项，尝试使用扩展的检查器
        if event_type in construction_events:
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
                                                         owner.get('birth_minute', 0))
                            zhuming = owner_sizhu.get('年柱', '')
                    except:
                        pass
                
                shensha_checker = ConstructionShenShaCheckerExt(zuoshan=zuoshan, zhuming=zhuming, direction=direction)
                self.shensha_list = shensha_checker.check(sizhu, owners, zuoshan=zuoshan, zhuming=zhuming, direction=direction)
            except ImportError:
                # 如果扩展模块导入失败，使用原检查器
                shensha_checker = get_checker(event_type)
                self.shensha_list = shensha_checker.check(sizhu, owners)
        else:
            # 其他事项使用原检查器
            shensha_checker = get_checker(event_type)
            self.shensha_list = shensha_checker.check(sizhu, owners)
        
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
                details = self._generate_wu_xing_details(sizhu, owners)
                details['ji_list'] = self.ji_list
                return {
                    'he_ge': False,
                    'score': 0,
                    'ji_yu': veto_reason,
                    'details': details,
                    'score_breakdown': {},
                    'has_deduction': False
                }
        else:
            self.yi_list, self.ji_list = result
        
        # 记录各项得分详情（提前定义，避免引用错误）
        score_breakdown = {
            '基础分': self.base_score,
            '神煞得分': 0,
            '宜事得分': 0,
            '忌事得分': 0,
            '十二长生得分': 0,
            '地支关系得分': 0,
            '纳音匹配得分': 0
        }
        
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
                return {
                    'he_ge': False,
                    'score': 0,
                    'ji_yu': f"当日忌{event_type}，一票否决",
                    'details': details,
                    'score_breakdown': score_breakdown,
                    'has_deduction': True
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
                year_analysis = self.analyze_year(year, event_type, owners, shan_xiang, direction)
                if not year_analysis['suitable']:
                    return {
                        'he_ge': False,
                        'score': 0,
                        'ji_yu': f"年份不宜: {'; '.join(year_analysis['reasons'])}",
                        'details': year_analysis,
                        'score_breakdown': score_breakdown,
                        'has_deduction': True
                    }
                
                # 分析月份吉凶（传递山向和动土方位用于分析）
                month_analysis = self.analyze_month(year, month, event_type, owners, shan_xiang, direction)
                if not month_analysis['suitable']:
                    return {
                        'he_ge': False,
                        'score': 0,
                        'ji_yu': f"月份不宜: {'; '.join(month_analysis['reasons'])}",
                        'details': month_analysis,
                        'score_breakdown': score_breakdown,
                        'has_deduction': True
                    }
        
        # 计算五行评分
        wu_xing_score = self.base_score
        
        # 尝试导入 calculate_sizhu
        try:
            from .四柱计算器 import calculate_sizhu
        except ImportError:
            from 四柱计算器 import calculate_sizhu
        
        # 对于嫁娶，检查大利月、小利月（基于具体日期的月支）
        if event_type == "嫁娶" and owners:
            for owner in owners:
                if owner.get('role') == '新娘' or owner.get('性别') == '女':
                    # 计算新娘年支
                    if 'birth_date' in owner:
                        owner_sizhu = calculate_sizhu(owner['birth_date'], 
                                                   owner.get('birth_hour', 12), 
                                                   owner.get('birth_minute', 0))
                        bride_year_zhi = owner_sizhu.get('year_zhi', '')
                        
                        # 从月地支获取农历月份
                        month_zhi = sizhu.get('month_zhi', '')
                        lunar_month = self._get_lunar_month_from_zhi(month_zhi)
                        
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
            
            # 4. 相主检查：日课日支与事主日支的冲合关系
            owner_day_relation_score, owner_day_details = self._check_owner_day_zhichong(sizhu, owners)
            wu_xing_score += owner_day_relation_score
            score_breakdown['相主得分'] = owner_day_relation_score
            # 将相主检查详情添加到神煞列表用于显示
            for detail in owner_day_details:
                self.shensha_list.append({
                    'name': '相主',
                    'description': detail,
                    'score': 0  # 分数已在相主得分中计算
                })
        
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
        
        # 三合局（区分半合与三合）
        sanhe_groups = {
            '申子辰': '水局', '寅午戌': '火局', '巳酉丑': '金局', '亥卯未': '木局'
        }
        zhi_list = [z[1] for z in zhis]
        from collections import Counter
        zhi_counter = Counter(zhi_list)
        
        for group, ju in sanhe_groups.items():
            # 获取该组中存在的不同地支
            present_zhis = [z for z in group if z in zhi_counter]
            unique_count = len(present_zhis)
            total_count = sum(zhi_counter[z] for z in present_zhis)
            
            if unique_count == 3:
                # 三个不同地支都存在，构成三合
                details['地支关系'].append(f"三合{ju}: {', '.join([z[0]+z[1] for z in zhis if z[1] in group])}")
            elif unique_count == 2:
                # 两个不同地支存在，构成半合
                missing_zhi = [z for z in group if z not in zhi_counter][0]
                details['地支关系'].append(f"半合{ju}（缺{missing_zhi}）: {', '.join([z[0]+z[1] for z in zhis if z[1] in present_zhis])}")
            elif unique_count == 1 and total_count >= 2:
                # 只有一个地支但出现多次，为伏吟（比和）
                zhi = present_zhis[0]
                matching_zhis = [z[0]+z[1] for z in zhis if z[1] == zhi]
                details['地支关系'].append(f"伏吟({zhi}): {', '.join(matching_zhis)}")
        
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
        
        # 三刑（必须是不同地支才能构成三刑）
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
                details['地支关系'].append(f"三刑({name}): {', '.join([z[0]+z[1] for z in zhis if z[1] in present_zhis])}")
        
        # 自刑（必须相同地支重复出现才构成自刑）
        # 自刑：辰辰、午午、酉酉、亥亥
        zixing_zhi = ['辰', '午', '酉', '亥']
        from collections import Counter
        zhi_counter = Counter(zhi_list)
        for zhi in zixing_zhi:
            if zhi_counter.get(zhi, 0) >= 2:
                matching_zhis = [z[0]+z[1] for z in zhis if z[1] == zhi]
                details['地支关系'].append(f"自刑: {', '.join(matching_zhis)}")
        
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
        month_zhu = sizhu.get('月柱', '')
        month_zhi = month_zhu[1] if len(month_zhu) > 1 else ''
        day_zhu = sizhu.get('日柱', '')
        day_gan = sizhu.get('day_gan', '')
        day_zhi = day_zhu[1] if len(day_zhu) > 1 else ''
        
        # 天德贵人查法（以月支查日干）
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
            '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
            '戌': '丙', '亥': '乙', '子': '巳', '丑': '庚'
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
        # 歌诀：甲丙庚寅子，乙癸卯丑寻，戊申己未位，丁亥庚午存，辛巳壬逢辰
        # 来源：百度百科、《钦定协纪辨方书》
        fuxing_map = {
            '甲': '寅', '乙': '卯', '丙': '子', '丁': '亥',
            '戊': '申', '己': '未', '庚': '午', '辛': '戌',
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
                except Exception as e:
                    logger.error(f"十二长生计算失败({pillar}柱{pillar_value}): {str(e)}")
                    pass
        
        return int(score)
    
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
        # 新增硬性限制：黑道日最高只能评为★★★ 吉
        if wu_xing_score >= 120 and da_huang_dao['type'] == '凶':
            # 黑道日降级限制：综合评分<130时最高只能评为★★★ 吉
            if score >= 130:
                return '★★★★ 大吉'
            elif score >= 120:
                return '★★★ 吉'
            else:
                return '★★ 次吉'
        
        # 新增：其他情况下黑道日也应降级
        if da_huang_dao['type'] == '凶' and score < 130:
            # 黑道日最高只能评为★★★ 吉
            if score >= 100:
                return '★★★ 吉'
            elif score >= 80:
                return '★★ 次吉'
            elif score >= 60:
                return '★ 平'
        
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
    
    def _generate_reason(self, wu_xing_result, huangdao_info, yueling_score, xishen_score=0, owner_matches=None, sun_moon_info=None):
        """
        生成评分理由

        Args:
            wu_xing_result: 五行审核结果
            huangdao_info: 黄道信息
            yueling_score: 月令评分
            xishen_score: 喜用神匹配评分
            owner_matches: 每个事主的详细匹配信息
            sun_moon_info: 太阳太阴到山到向信息

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

    def _generate_yueling_analysis(self, sizhu):
        """
        生成月令分析

        Args:
            sizhu: 四柱信息字典

        Returns:
            str: 月令分析描述
        """
        day_gan = sizhu.get('day_gan', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        if not day_gan or not month_zhi:
            return ''
        
        # 天干五行
        gan_wuxing = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', 
                      '戊': '土', '己': '土', '庚': '金', '辛': '金', 
                      '壬': '水', '癸': '水'}
        
        # 地支五行
        zhi_wuxing = {'子': '水', '丑': '土', '寅': '木', '卯': '木', 
                      '辰': '土', '巳': '火', '午': '火', '未': '土', 
                      '申': '金', '酉': '金', '戌': '土', '亥': '水'}
        
        # 十二长生状态
        changsheng = {
            '木': {'长生': '亥', '沐浴': '子', '冠带': '丑', '临官': '寅', '帝旺': '卯', 
                   '衰': '辰', '病': '巳', '死': '午', '墓': '未', '绝': '申', '胎': '酉', '养': '戌'},
            '火': {'长生': '寅', '沐浴': '卯', '冠带': '辰', '临官': '巳', '帝旺': '午', 
                   '衰': '未', '病': '申', '死': '酉', '墓': '戌', '绝': '亥', '胎': '子', '养': '丑'},
            '土': {'长生': '寅', '沐浴': '卯', '冠带': '辰', '临官': '巳', '帝旺': '午', 
                   '衰': '未', '病': '申', '死': '酉', '墓': '戌', '绝': '亥', '胎': '子', '养': '丑'},
            '金': {'长生': '巳', '沐浴': '午', '冠带': '未', '临官': '申', '帝旺': '酉', 
                   '衰': '戌', '病': '亥', '死': '子', '墓': '丑', '绝': '寅', '胎': '卯', '养': '辰'},
            '水': {'长生': '申', '沐浴': '酉', '冠带': '戌', '临官': '亥', '帝旺': '子', 
                   '衰': '丑', '病': '寅', '死': '卯', '墓': '辰', '绝': '巳', '胎': '午', '养': '未'}
        }
        
        day_wuxing = gan_wuxing.get(day_gan, '')
        month_wuxing = zhi_wuxing.get(month_zhi, '')
        
        if not day_wuxing:
            return ''
        
        # 获取十二长生状态
        changsheng_states = changsheng.get(day_wuxing, {})
        changsheng_state = ''
        for state, zhi in changsheng_states.items():
            if zhi == month_zhi:
                changsheng_state = state
                break
        
        # 五行生克关系
        sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        
        analysis_parts = []
        
        if changsheng_state in ['长生', '冠带', '临官', '帝旺']:
            analysis_parts.append(f"{day_gan}日主得令")
        elif changsheng_state in ['衰', '病', '死']:
            analysis_parts.append(f"{day_gan}日主失令")
        elif changsheng_state in ['墓', '绝']:
            analysis_parts.append(f"{day_gan}日主入墓绝")
        elif changsheng_state in ['沐浴']:
            analysis_parts.append(f"{day_gan}日主沐浴")
        elif changsheng_state in ['胎', '养']:
            analysis_parts.append(f"{day_gan}日主胎养")
        
        # 添加五行关系
        if month_wuxing:
            if sheng.get(month_wuxing) == day_wuxing:
                analysis_parts.append(f"{month_wuxing}生{day_wuxing}")
            elif ke.get(month_wuxing) == day_wuxing:
                analysis_parts.append(f"{month_wuxing}克{day_wuxing}")
            elif month_wuxing == day_wuxing:
                analysis_parts.append(f"同气相求")
            elif sheng.get(day_wuxing) == month_wuxing:
                analysis_parts.append(f"{day_wuxing}生{month_wuxing}")
        
        if analysis_parts:
            return '，'.join(analysis_parts)
        return ''


# 全局评分器实例
scorer = Scorer()

def calculate_sun_moon_position(sizhu, shan_xiang):
    """
    计算太阳太阴到山到向
    
    Args:
        sizhu: 四柱信息
        shan_xiang: 山向
        
    Returns:
        dict: 太阳太阴到山到向信息
    """
    if not shan_xiang:
        return {
            'sun_position': '无山向信息',
            'moon_position': '无山向信息',
            'score': 0
        }
    
    # 提取山向方向
    shan_dir = shan_xiang[0]
    
    # 简单的太阳太阴到山到向计算（基于月份）
    # 实际应用中需要更复杂的天文计算
    month = sizhu['month']
    
    # 太阳到山到向映射（简化版）
    sun_mapping = {
        1: '子', 2: '丑', 3: '寅', 4: '卯',
        5: '辰', 6: '巳', 7: '午', 8: '未',
        9: '申', 10: '酉', 11: '戌', 12: '亥'
    }
    
    # 太阴到山到向映射（简化版）
    moon_mapping = {
        1: '亥', 2: '子', 3: '丑', 4: '寅',
        5: '卯', 6: '辰', 7: '巳', 8: '午',
        9: '未', 10: '申', 11: '酉', 12: '戌'
    }
    
    sun_position = sun_mapping.get(month, '未知')
    moon_position = moon_mapping.get(month, '未知')
    
    # 计算得分
    score = 0
    if sun_position == shan_dir:
        score += 10  # 太阳到山
    if moon_position == shan_dir:
        score += 10  # 太阴到山
    
    # 计算向（与山对冲）
    chong_zhi = {
        '子': '午', '午': '子',
        '丑': '未', '未': '丑',
        '寅': '申', '申': '寅',
        '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰',
        '巳': '亥', '亥': '巳'
    }
    xiang_dir = chong_zhi.get(shan_dir, '')
    if xiang_dir:
        if sun_position == xiang_dir:
            score += 8  # 太阳到向
        if moon_position == xiang_dir:
            score += 8  # 太阴到向
    
    return {
        'sun_position': sun_position,
        'moon_position': moon_position,
        'sun_to_mountain': sun_position == shan_dir,
        'sun_to_direction': sun_position == xiang_dir if xiang_dir else False,
        'moon_to_mountain': moon_position == shan_dir,
        'moon_to_direction': moon_position == xiang_dir if xiang_dir else False,
        'score': score,
        'details': f"太阳在{sun_position}方，太阴在{moon_position}方"
    }

def calculate_score(sizhu, event_type, owners=None, house_type=None, shan_xiang=None,
                    zaoxiang=None, zaowei=None, chuangwei=None, jian_xiang=None):
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
    return scorer.score(sizhu, event_type, owners, house_type, shan_xiang, zaoxiang, zaowei, chuangwei, None, jian_xiang)
