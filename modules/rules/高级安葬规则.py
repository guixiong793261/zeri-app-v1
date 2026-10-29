# -*- coding: utf-8 -*-
"""
================================================================================
高级安葬规则模块（基于《协纪辨方书》）
================================================================================
实现高级安葬择日的宜忌规则

核心规则：
1. 一票否决：复日（旧称重丧日）、三丧日、四离四绝（「岁破」已删：岁破批
   2026-10-20，001 §140；年重丧 §198 撤否决降为 -30 扣分；冲山/月破为扣分项）
2. 吉神：天德、月德、不将日、黄道吉日、鸣吠日、鸣吠对日
3. 扶山：日课五行生扶坐山
4. 三合六合：日课与坐山相合
5. 相主：日课与孝子年命不冲克
================================================================================
"""

import sys
import os

# 处理导入路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
modules_dir = os.path.dirname(os.path.abspath(__file__))
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

try:
    from .规则基类 import EventRuleChecker
except ImportError:
    from 规则基类 import EventRuleChecker

# 鸣吠日 13 干支、鸣吠对日 11 干支（《协纪》卷五／卷九）——2026-10 A1
# 收口到神煞基类模块级唯一实现（本类旧表为 10 日／6 日错表）。
try:
    from ..shensha.神煞基类 import (is_mingfei_by_pillar, is_mingfeidui_by_pillar,
                                   is_furi_by_month_zhi)
except ImportError:
    from shensha.神煞基类 import (is_mingfei_by_pillar, is_mingfeidui_by_pillar,
                                 is_furi_by_month_zhi)

from datetime import date
import logging

logger = logging.getLogger(__name__)

# 建除十二神—— 批次 2（001 §162）从 建除.py 卷十唯一事实源动态生成
# 高级安葬同安葬（卷十 L317：宜无；忌建/破/平/收）
try:
    from ..建除 import get_event_yiji
except ImportError:
    from 建除 import get_event_yiji
_YJ = get_event_yiji('安葬')

class AdvancedBurialRuleChecker(EventRuleChecker):
    """高级安葬规则检查器"""
    
    JIANCHU_YI = _YJ['yi']
    JIANCHU_JI = _YJ['ji']
    
    # 二十四山五行属性
    ER_SHI_SI_SHAN_WUXING = {
        '壬': '水', '子': '水', '癸': '水',
        '丑': '土', '艮': '土', '寅': '木',
        '甲': '木', '卯': '木', '乙': '木',
        '辰': '土', '巽': '木', '巳': '火',
        '丙': '火', '午': '火', '丁': '火',
        '未': '土', '坤': '土', '申': '金',
        '庚': '金', '酉': '金', '辛': '金',
        '戌': '土', '乾': '金', '亥': '水'
    }
    
    # 地支五行
    ZHI_WUXING = {
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }
    
    # 五行生克（用于扶山判断：日课生坐山为吉）
    SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
    
    # 三煞方位（年支对应）
    SAN_SHA = {
        '申': ['巳', '午', '未'],  # 申子辰年煞南方
        '子': ['巳', '午', '未'],
        '辰': ['巳', '午', '未'],
        '寅': ['亥', '子', '丑'],  # 寅午戌年煞北方
        '午': ['亥', '子', '丑'],
        '戌': ['亥', '子', '丑'],
        '巳': ['寅', '卯', '辰'],  # 巳酉丑年煞东方
        '酉': ['寅', '卯', '辰'],
        '丑': ['寅', '卯', '辰'],
        '亥': ['申', '酉', '戌'],  # 亥卯未年煞西方
        '卯': ['申', '酉', '戌'],
        '未': ['申', '酉', '戌']
    }
    
    # 岁破方位（年支对冲）
    SUI_PO = {
        '子': '午', '午': '子',
        '丑': '未', '未': '丑',
        '寅': '申', '申': '寅',
        '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰',
        '巳': '亥', '亥': '巳'
    }
    
    # 三合局
    SANHE_GROUPS = [
        ['申', '子', '辰'],  # 水局
        ['寅', '午', '戌'],  # 火局
        ['巳', '酉', '丑'],  # 金局
        ['亥', '卯', '未']   # 木局
    ]
    
    # 复日（旧称重丧日）起例（001 §197 拍板 D3-Q1/Q2/Q3）：
    # 《协纪》正法「建月同干」单干表，按节气月支：
    #   正甲、二乙、三戊、四丙、五丁、六己、七庚、八辛、九戊、十壬、十一癸、十二己。
    # 原「正七连庚甲…」双干表即协纪 p279217 点名之误（正月庚、七月甲），已废除；
    # 判定统一走 神煞基类 单点出口 is_furi_by_month_zhi，本类不再自持表
    # （原 ZHONG_SANG_MAP 冗余副本已删，避免与基类口径漂移）。
    
    # 年重丧映射（按年支查日干）
    # 001 §197 D3-Q6：三库全卷零词条，已另立专项；裁断前冻结原双干口径。
    NIAN_ZHONG_SANG_MAP = {
        '寅': ['庚', '甲'], '卯': ['乙', '辛'], '辰': ['戊', '己'],
        '巳': ['丙', '壬'], '午': ['丁', '癸'], '未': ['戊', '己'],
        '申': ['庚', '甲'], '酉': ['乙', '辛'], '戌': ['戊', '己'],
        '亥': ['丙', '壬'], '子': ['丁', '癸'], '丑': ['戊', '己'],
    }
    
    # FURI_MAP 已删（001 §197 D3-Q5）：原「正月甲、二月乙、三月丙…顺序干」
    # 三库无载，与月「复日」同一概念，合并后不再单列。
    
    # 往亡日映射
    WANGWANG_MAP = {
        '寅': '寅', '卯': '巳', '辰': '申', '巳': '亥',
        '午': '卯', '未': '午', '申': '酉', '酉': '子',
        '戌': '辰', '亥': '未', '子': '戌', '丑': '丑'
    }
    
    # 十恶大败日表与一票否决引用已删（2026-10-19 全删批·二档，001 §139）：
    # 三库无「十恶大败忌安葬」明文，无典据不得一票否决（拍板逐项批准）。
    
    # 鸣吠日/鸣吠对日：2026-10 A1 起不再在本类维护干支表——典载 13 日／11 日
    # 收口到 神煞基类.is_mingfei_by_pillar / is_mingfeidui_by_pillar（见文件头
    # 导入；旧 MINGFEI 10 日表、MINGFEIDUI 6 日表均为错表，已删）。

    # 地支列表
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    def __init__(self):
        super().__init__()
        self._init_dependencies()
    
    def _init_dependencies(self):
        """初始化依赖模块"""
        self.has_marriage_shensha = False
        self.get_jianchu = None
        self.is_tiande_day = None
        self.is_yuede_day = None
        self.is_bujiang_day = None
        self.is_month_break = None
        self.is_year_break = None
        self.is_sili_sijue = None
        
        try:
            from ..shensha.marriage_shensha import (
                get_jianchu,
                is_tiande_day,
                is_yuede_day,
                is_bujiang_day,
                is_month_break,
                is_year_break,
                is_sili_sijue
            )
            self.get_jianchu = get_jianchu
            self.is_tiande_day = is_tiande_day
            self.is_yuede_day = is_yuede_day
            self.is_bujiang_day = is_bujiang_day
            self.is_month_break = is_month_break
            self.is_year_break = is_year_break
            self.is_sili_sijue = is_sili_sijue
            self.has_marriage_shensha = True
        except ImportError:
            pass
    
    def _sizhu_to_date(self, sizhu):
        """从sizhu构建日期对象"""
        if 'date' in sizhu:
            return sizhu['date']
        
        try:
            year = int(sizhu.get('year', sizhu.get('年柱', '2000')[0:4]))
            month = int(sizhu.get('month', 1))
            day = int(sizhu.get('day', 1))
            return date(year, month, day)
        except:
            return None
    
    def _get_lunar_info(self, date_obj):
        """获取农历信息"""
        try:
            from ..四柱计算器 import get_lunar_date
            return get_lunar_date(date_obj)
        except:
            return {}
    
    def _extract_zuoshan(self, shan_xiang):
        """从山向字符串中提取坐山"""
        if not shan_xiang:
            return None
        
        # 处理"子山午向"格式
        if '山' in shan_xiang:
            return shan_xiang.split('山')[0]
        
        # 处理"乾山巽向"格式或单字
        if len(shan_xiang) >= 1:
            return shan_xiang[0]
        
        return shan_xiang
    
    def _extract_zuoshan_jianxiang(self, shan_xiang):
        """从山向字符串中提取坐山（支持兼向）"""
        if not shan_xiang:
            return None
        
        # 处理"子山兼壬"或"壬山兼子"格式
        if '兼' in shan_xiang:
            parts = shan_xiang.split('兼')
            zuoshan_base = parts[0].replace('山', '')
            jianxiang = parts[1][0] if len(parts[1]) > 0 else ''
            return zuoshan_base, jianxiang
        
        # 处理"子山午向"格式
        if '山' in shan_xiang:
            zuoshan_base = shan_xiang.split('山')[0]
            return zuoshan_base, ''
        
        return shan_xiang[0] if len(shan_xiang) >= 1 else None, ''
    
    def _get_owner_year_zhi(self, owner):
        """获取事主年支"""
        if '生肖' in owner:
            return owner['生肖']
        
        if 'sizhu' in owner:
            sizhu_parts = owner['sizhu'].split()
            if len(sizhu_parts) >= 1:
                return sizhu_parts[0][1]
        
        if 'birth_date' in owner:
            try:
                from ..四柱计算器 import calculate_sizhu
                birth_sizhu = calculate_sizhu(
                    owner['birth_date'],
                    owner.get('birth_hour', 12),
                    owner.get('birth_minute', 0),
                    longitude=owner.get('birth_longitude')
                )
                return birth_sizhu['年柱'][1]
            except:
                pass
        
        return None
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查安葬规则（基于《协纪辨方书》）"""
        yi_list = []
        ji_list = []
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list
        
        day_gan = sizhu.get('day_gan', '')
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        shan_xiang = kwargs.get('shan_xiang')
        
        # 提取坐山
        zuoshan = self._extract_zuoshan(shan_xiang)
        
        # ===== 一票否决项（大凶）=====
        # §186（2026-10-26）：重丧/三丧/复日/年重丧升级为一票否决。
        # 古籍「重丧不葬，三丧绝嗣」——极凶日绝不能仅扣分，必须否决。
        # §197（2026-10-28 D3-Q1/Q5）：注册名正名「复日」，原「重丧日」与
        #   「复日」两条同概念双计合并为一条；起例改协纪正法单干·节气月建。
        # 制化豁免：三库确认有特定制化能解时另行豁免，当前绝对禁用。
        _daxiong_veto = []

        # 1. 复日（旧称重丧日；《协纪》正法单干·节气月建，月支查日干）
        if month_zhi and day_gan and self._is_zhongsang(month_zhi, day_gan):
            ji_list.append('复日忌安葬')
            _daxiong_veto.append('复日')
        
        # 2. 年重丧（按年支查日干）
        # §198（2026-10-29 拍板）：三库全卷零词条且起例为协纪 p279217 明斥之
        # 通书伪表年家翻版，撤销一票否决；分值 -30 由神煞层承载，本处仅保留
        # 忌项文本作「存疑警示」，不再进 _daxiong_veto。
        if year_zhi and day_gan and self._is_nian_zhongsang(year_zhi, day_gan):
            ji_list.append('年重丧忌安葬')
        
        # 3. 三丧日（按季节查日支）
        if month_zhi and day_zhi and self._is_sansang(month_zhi, day_zhi):
            ji_list.append('三丧日忌安葬')
            _daxiong_veto.append('三丧日')
        
        # 4. 复日（重丧类）独立判定已删（001 §197 D3-Q5）：与第 1 项合并去重，
        #    原 FURI_MAP「正月甲、二月乙…顺序干」三库无载。
        
        # 5. 十恶大败日——已删（2026-10-19 全删批·二档）：三库无「十恶大败
        # 忌安葬」明文，无典据不得一票否决（拍板逐项批准）；编号保留防错位。
        
        # 6. 月破日
        if self.has_marriage_shensha:
            try:
                if self.is_month_break(date_obj):
                    ji_list.append('月破日忌安葬')
            except:
                pass
        else:
            # 备用检查：日支与月支相冲
            if month_zhi and day_zhi and self._is_chong(month_zhi, day_zhi):
                ji_list.append('月破日忌安葬')
        
        # 7. 岁破日×安葬已删（岁破批 2026-10-20，001 §140）：日课普适岁破注册零日课
        # 典据（协纪卷内「岁破日」0 命中），拍板删日课通道普适忌注册；谓词
        # _is_sui_po_day 同步删除（无 caller）。发射原为：
        #     if year_zhi and day_zhi and self._is_sui_po_day(year_zhi, day_zhi):
        #         ji_list.append('岁破日忌安葬')
        # 注：第 12 项「岁破检查（方位）」为山向（坐山犯岁破）语境，保留并标注。
        
        # 8. 四离四绝（§198：补齐 HARD_VETO）
        # 2026-09-20 死表清理：原 else 备用检查引用 _is_sili/_is_sijue 月支→日支
        # 固定映射表，原理不成立（四离四绝是节气前一日，随节气日期逐年漂移，
        # 与月支日支无固定对应），且 has_marriage_shensha 恒为 True 时该分支
        # 不可达。已连同两个死表方法一并删除，四离四绝仅保留 marriage_shensha
        # 单一实现路径（sxtwl 精确判定）。
        # §198（2026-10-29 拍板）：原仅 append 忌项文本、未进 _daxiong_veto，
        # 且安葬分值键 ('安葬','四离日'/'四绝日') 因无同名发射而休眠，致
        # 「一票否决」名存实亡。现补齐否决门槛；异常改为 logger.warning 留痕，
        # 不再静默 pass。
        if self.has_marriage_shensha:
            try:
                if self.is_sili_sijue(date_obj):
                    ji_list.append('四离四绝日忌安葬')
                    _daxiong_veto.append('四离四绝日')
            except Exception as e:
                logger.warning(f"四离四绝判定失败（漏否决，请核查）: {e}")
        
        # 9. 往亡日
        if month_zhi and day_zhi and self._is_wangwang(month_zhi, day_zhi):
            ji_list.append('往亡日忌安葬')
        
        # 10. 冲山日（日支冲坐山）
        if zuoshan and day_zhi:
            if self._is_chong(day_zhi, zuoshan):
                ji_list.append(f'{zuoshan}山被日支冲克')
        
        # 11. 三煞检查（年/月/日三煞）
        if zuoshan:
            if year_zhi and self._is_san_sha(year_zhi, zuoshan):
                ji_list.append(f'{zuoshan}山犯年三煞')
            if month_zhi and self._is_san_sha(month_zhi, zuoshan):
                ji_list.append(f'{zuoshan}山犯月三煞')
            if day_zhi and self._is_san_sha(day_zhi, zuoshan):
                ji_list.append(f'{zuoshan}山犯日三煞')
        
        # 12. 岁破检查（方位）
        # 【保留·仅方位语境】坐山犯岁破方位（山向语境，非日课普适岁破注册）
        if year_zhi and zuoshan and self._is_sui_po_direction(year_zhi, zuoshan):
            ji_list.append(f'{zuoshan}山犯岁破')
        
        # §186：大凶日（复日/三丧/四离四绝）一票否决，返回 4-tuple
        # （年重丧 §198 已撤否决，降为 -30 扣分，在此走下方 ji_list 提前返回）
        if _daxiong_veto:
            ji_list.append('安葬')
            _veto_reason = '、'.join(_daxiong_veto) + '忌安葬（一票否决）'
            return yi_list, ji_list, True, _veto_reason

        # 如果有其他忌项（月破/往亡/冲山等，扣分不否决），直接返回
        if ji_list:
            ji_list.append('安葬')
            return yi_list, ji_list
        
        # ===== 吉神检查 =====
        # 1. 建除十二神
        self._check_jianchu(date_obj, yi_list, ji_list)
        
        # 2. 天德月德
        self._check_tiande_yuede(date_obj, yi_list)
        
        # 3. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 鸣吠日
        if day_gan and day_zhi and self._is_mingfei(day_gan + day_zhi):
            yi_list.append('鸣吠日宜安葬')
        
        # 5. 鸣吠对日
        if day_gan and day_zhi and self._is_mingfeidui(day_gan + day_zhi):
            yi_list.append('鸣吠对日宜安葬')
        
        # ===== 扶山检查（日课生扶坐山）=====
        if zuoshan:
            self._check_fushan(sizhu, zuoshan, yi_list, ji_list)
            
            # 三合局检查
            self._check_sanhe(sizhu, zuoshan, yi_list)
        
        # ===== 相主检查（与孝子年命关系）=====
        self._check_owner_match(sizhu, owners, yi_list, ji_list)
        
        # 综合判断
        if yi_list and not ji_list:
            yi_list.append('安葬')
        elif ji_list:
            ji_list.append('安葬')
        
        return yi_list, ji_list
    
    # ===== 重丧类神煞 =====
    
    def _is_zhongsang(self, month_zhi, day_gan):
        """
        是否复日（旧称重丧日；《协纪》正法单干·节气月建，月支查日干）

        001 §197（2026-10-28 拍板 D3-Q1/Q2/Q3）：原「正七连庚甲」双干口诀即
        协纪 p279217 点名之误，已废除；统一委托 神煞基类 单点出口
        is_furi_by_month_zhi（正甲、二乙、三戊、四丙、五丁、六己、七庚、八辛、
        九戊、十壬、十一癸、十二己）。
        """
        return is_furi_by_month_zhi(month_zhi, day_gan)
    
    def _is_nian_zhongsang(self, year_zhi, day_gan):
        """
        是否年重丧（按年支查日干）

        001 §197 D3-Q6 专项取证：三库全卷零词条，起例为协纪 p279217 明斥之
        通书双干伪表年家翻版。§198（2026-10-29 拍板）撤销一票否决，仅作 -30
        存疑警示；本表在通书层补扫（Y1）出结论前冻结原双干口径。
        """
        return day_gan in self.NIAN_ZHONG_SANG_MAP.get(year_zhi, [])
    
    def _is_sansang(self, month_zhi, day_zhi):
        """
        是否三丧日（按季节查日支）
        口诀：春辰夏未秋戌冬丑（四季墓库派）
        《协纪辨方书》: 三丧日为四季月建墓库对应的地支
        §186（2026-10-26）：原误作「春戌夏丑秋辰冬未」（实为四击/杀师日表），
        已统一为墓库派，与安葬神煞模块对齐。
        """
        if month_zhi in ['寅', '卯', '辰']:  # 春季
            return day_zhi == '辰'
        elif month_zhi in ['巳', '午', '未']:  # 夏季
            return day_zhi == '未'
        elif month_zhi in ['申', '酉', '戌']:  # 秋季
            return day_zhi == '戌'
        elif month_zhi in ['亥', '子', '丑']:  # 冬季
            return day_zhi == '丑'
        return False
    
    # _is_furi 已删（001 §197 D3-Q5）：复日与重丧日合并后统一走 _is_zhongsang
    # → is_furi_by_month_zhi；原 FURI_MAP「正月甲、二月乙…顺序干」三库无载。
    
    def _is_wangwang(self, month_zhi, day_zhi):
        """
        是否往亡日
        口诀：正寅二巳三申四亥五卯六午七酉八子九辰十未十一戌十二丑
        """
        return day_zhi == self.WANGWANG_MAP.get(month_zhi)
    
    # _is_shie_dabai 已删（2026-10-19 全删批·二档）：SHIE_DABAI 表与一票否决
    # 引用同删——无典据不得一票否决（拍板逐项批准，001 §139）。

    # _is_sui_po_day 已删（岁破批 2026-10-20，001 §140）：日课普适岁破谓词，
    # 唯一消费者（第 7 项岁破日发射）本批同步删除后无 caller。
    # 原实现：return self._is_chong(year_zhi, day_zhi)

    def _is_mingfei(self, day_pillar):
        """是否鸣吠日（委托 神煞基类 典载 13 日柱，2026-10 A1）"""
        return is_mingfei_by_pillar(day_pillar)

    def _is_mingfeidui(self, day_pillar):
        """是否鸣吠对日（委托 神煞基类 典载 11 日柱，2026-10 A1）"""
        return is_mingfeidui_by_pillar(day_pillar)
    
    def _is_chong(self, zhi1, zhi2):
        """检查两个地支是否相冲"""
        chong_pairs = [('子','午'), ('丑','未'), ('寅','申'), 
                       ('卯','酉'), ('辰','戌'), ('巳','亥')]
        return (zhi1, zhi2) in chong_pairs or (zhi2, zhi1) in chong_pairs
    
    def _check_jianchu(self, date_obj, yi_list, ji_list):
        """检查建除十二神"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            if jianchu in self.JIANCHU_YI:
                yi_list.append(f'建除{jianchu}日宜安葬')
            elif jianchu in self.JIANCHU_JI:
                ji_list.append(f'建除{jianchu}日忌安葬')
        except Exception:
            pass
    
    def _check_tiande_yuede(self, date_obj, yi_list):
        """检查天德、月德日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜安葬')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜安葬')
        except Exception:
            pass
    
    def _check_bujiang(self, date_obj, yi_list):
        """检查不将日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_bujiang_day(date_obj):
                yi_list.append('不将日宜安葬')
        except Exception:
            pass
    
    def _check_fushan(self, sizhu, zuoshan, yi_list, ji_list):
        """扶山检查：日课生扶坐山"""
        zuoshan_wuxing = self.ER_SHI_SI_SHAN_WUXING.get(zuoshan)
        if not zuoshan_wuxing:
            return
        
        # 获取日课地支五行
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        
        # 检查日课地支是否生扶坐山
        for zhi in [year_zhi, month_zhi, day_zhi]:
            if not zhi:
                continue
            
            zhi_wuxing = self.ZHI_WUXING.get(zhi)
            if not zhi_wuxing:
                continue
            
            # 日课生坐山为吉（扶山）
            if self.SHENG.get(zhi_wuxing) == zuoshan_wuxing:
                yi_list.append(f'{zuoshan}山得{zhi}生扶')
                break
            
            # 日课克坐山为凶
            if self.KE.get(zhi_wuxing) == zuoshan_wuxing:
                ji_list.append(f'{zuoshan}山被{zhi}克制')
                break
    
    def _check_sanhe(self, sizhu, zuoshan, yi_list):
        """三合局检查"""
        zhis = []
        for key in ['year_zhi', 'month_zhi', 'day_zhi']:
            zhi = sizhu.get(key)
            if zhi:
                zhis.append(zhi)
        
        # 检查是否与坐山形成三合局
        for group in self.SANHE_GROUPS:
            if zuoshan in group:
                count = sum(1 for z in zhis if z in group)
                if count >= 1:
                    other_zhis = [z for z in group if z != zuoshan]
                    present = [z for z in other_zhis if z in zhis]
                    yi_list.append(f'{zuoshan}山与{"、".join(present)}半合{self._get_sanhe_name(group)}')
    
    def _get_sanhe_name(self, group):
        """获取三合局名称"""
        if '申' in group:
            return '水局'
        elif '寅' in group:
            return '火局'
        elif '巳' in group:
            return '金局'
        elif '亥' in group:
            return '木局'
        return '局'
    
    def _is_san_sha(self, year_zhi, zuoshan):
        """检查坐山是否犯三煞"""
        san_sha_directions = self.SAN_SHA.get(year_zhi, [])
        return zuoshan in san_sha_directions
    
    def _is_sui_po_direction(self, year_zhi, zuoshan):
        """检查坐山是否犯岁破方位"""
        sui_po_direction = self.SUI_PO.get(year_zhi, '')
        return zuoshan == sui_po_direction
    
    def _check_owner_match(self, sizhu, owners, yi_list, ji_list):
        """检查与事主年命关系"""
        if not owners:
            return
        
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi:
            return
        
        for owner in owners:
            name = owner.get('name', '事主')
            owner_zhi = self._get_owner_year_zhi(owner)
            
            if not owner_zhi:
                continue
            
            # 检查相冲
            if self._is_chong(day_zhi, owner_zhi):
                ji_list.append(f'与{name}年命相冲')
                break
            
            # 检查三合六合
            if self._is_sanheliuhe(day_zhi, owner_zhi):
                yi_list.append(f'与{name}年命相合')
    
    def _is_sanheliuhe(self, zhi1, zhi2):
        """检查两个地支是否三合或六合"""
        # 六合
        liuhe_pairs = [('子','丑'), ('寅','亥'), ('卯','戌'), 
                       ('辰','酉'), ('巳','申'), ('午','未')]
        if (zhi1, zhi2) in liuhe_pairs or (zhi2, zhi1) in liuhe_pairs:
            return True
        
        # 三合
        for group in self.SANHE_GROUPS:
            if zhi1 in group and zhi2 in group:
                return True
        
        return False
    
    def get_forbidden_directions(self, sizhu):
        """获取禁止使用的方位列表"""
        forbidden = []
        all_directions = ['壬', '子', '癸', '丑', '艮', '寅', '甲', '卯', '乙', '辰', '巽', '巳',
                         '丙', '午', '丁', '未', '坤', '申', '庚', '酉', '辛', '戌', '乾', '亥']
        
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            year_zhu = sizhu.get('年柱', '')
            if len(year_zhu) >= 2:
                year_zhi = year_zhu[1]
        
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        
        for direction in all_directions:
            # 三煞
            if year_zhi and self._is_san_sha(year_zhi, direction):
                forbidden.append(direction)
                continue
            
            # 岁破方位
            if year_zhi and self._is_sui_po_direction(year_zhi, direction):
                forbidden.append(direction)
                continue
            
            # 冲山（日支冲坐山）
            if day_zhi and self._is_chong(day_zhi, direction):
                forbidden.append(direction)
                continue
        
        return forbidden
    
    def is_direction_forbidden(self, sizhu, direction):
        """检查某个方位是否被禁止"""
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            year_zhu = sizhu.get('年柱', '')
            if len(year_zhu) >= 2:
                year_zhi = year_zhu[1]
        
        day_zhi = sizhu.get('day_zhi', '')
        
        return (year_zhi and self._is_san_sha(year_zhi, direction)) or \
               (year_zhi and self._is_sui_po_direction(year_zhi, direction)) or \
               (day_zhi and self._is_chong(day_zhi, direction))

if __name__ == '__main__':
    checker = AdvancedBurialRuleChecker()
    
    test_sizhu = {
        '年柱': '戊子',
        '月柱': '庚申',
        '日柱': '辛亥',
        '时柱': '甲午',
        'year_zhi': '子',
        'month_zhi': '申',
        'day_zhi': '亥',
        'day_gan': '辛',
        'hour_zhi': '午',
        'year': 2008,
        'month': 8,
        'day': 31
    }
    
    test_owners = [{'name': '孝子张三', '生肖': '鼠'}]
    
    yi_list, ji_list = checker._check_rules(test_sizhu, test_owners, shan_xiang='壬山丙向')
    
    print("宜：", yi_list)
    print("忌：", ji_list)
    
    forbidden = checker.get_forbidden_directions(test_sizhu)
    print(f"\n禁止使用的方位: {forbidden}")
    
    # 测试复日（旧称重丧日；《协纪》正法单干·节气月建）
    print("\n=== 复日测试（协纪正法单干） ===")
    test_sizhu2 = {
        'month_zhi': '申',
        'day_gan': '庚',
        'day_zhi': '午'
    }
    print(f"申月（七月）庚日是否复日: {checker._is_zhongsang('申', '庚')}")
    print(f"申月甲日是否复日: {checker._is_zhongsang('申', '甲')}")
    print(f"申月辛日是否复日: {checker._is_zhongsang('申', '辛')}")
    
    # 测试三丧日（口诀：春辰夏未秋戌冬丑）
    print("\n=== 三丧日测试（口诀：春辰夏未秋戌冬丑） ===")
    print(f"春季辰日是否三丧: {checker._is_sansang('寅', '辰')}")
    print(f"夏季未日是否三丧: {checker._is_sansang('巳', '未')}")
    print(f"秋季戌日是否三丧: {checker._is_sansang('申', '戌')}")
    print(f"冬季丑日是否三丧: {checker._is_sansang('亥', '丑')}")
    
    # 「岁破日」自测已删（岁破批 2026-10-20，001 §140：_is_sui_po_day 同步删除）