# -*- coding: utf-8 -*-
"""
================================================================================
婚嫁神煞扩展模块
================================================================================
本模块扩展婚嫁神煞检查器，提供时辰吉利值计算和大利月等信息。

【职责边界说明】
本模块主要负责：
1. 时辰吉利值计算与排序
2. 大利月/小利月信息
3. 夫子星、阴胎、阳气等信息（需要新娘日柱）

【依赖父类】
完整的嫁娶日课吉凶判断需调用 MarriageShenShaChecker（父类），该父类已实现：
- 三娘煞
- 阴错阳差
- 红纱
- 杨公忌
- 月破、岁破
- 其他嫁娶核心日禁

本模块不重复实现上述日禁，只在父类基础上扩展时辰层面的辅助信息。

【时辰评分项目】
- 大黄道（青龙、明堂、天刑、朱雀等）
- 小黄道（建除十二神）
- 贵人时、禄神时
- 红鸾时、天喜时
- 五不遇时
- 日破时（否决标志）
- 冲新郎/新娘（否决标志）
- 冲阴胎/冲阳气（时支冲新娘阴胎、新郎阳气的胎元地支，否决标志）
================================================================================
"""

try:
    from .嫁娶神煞 import MarriageShenShaChecker
    from .marriage_shensha import get_yintai, get_yangqi
    from ..工具函数 import DI_ZHI, TIAN_GAN
except ImportError:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from modules.shensha.嫁娶神煞 import MarriageShenShaChecker
    from modules.shensha.marriage_shensha import get_yintai, get_yangqi
    from modules.工具函数 import DI_ZHI, TIAN_GAN


class MarriageShenShaCheckerExt(MarriageShenShaChecker):
    """婚嫁神煞检查器扩展版"""
    
    def __init__(self, bride_gan=None, bride_zhi=None, groom_gan=None, groom_zhi=None,
                 bride_month_gan=None, bride_month_zhi=None,
                 groom_month_gan=None, groom_month_zhi=None):
        """
        初始化
        
        Args:
            bride_gan: 新娘年干
            bride_zhi: 新娘年支（生肖）
            groom_gan: 新郎年干
            groom_zhi: 新郎年支（生肖）
            bride_month_gan: 新娘生月天干（推阴胎，用于时辰冲阴胎禁用）
            bride_month_zhi: 新娘生月地支
            groom_month_gan: 新郎生月天干（推阳气，用于时辰冲阳气禁用）
            groom_month_zhi: 新郎生月地支
        """
        super().__init__()
        self.bride_gan = bride_gan
        self.bride_zhi = bride_zhi
        self.groom_gan = groom_gan
        self.groom_zhi = groom_zhi
        self.bride_month_gan = bride_month_gan
        self.bride_month_zhi = bride_month_zhi
        self.groom_month_gan = groom_month_gan
        self.groom_month_zhi = groom_month_zhi
    
    def get_lucky_hours(self, sizhu):
        """
        计算当日吉利的婚嫁时辰

        遍历十二时辰，检查每个时辰的吉凶，
        返回按时辰排序的吉凶列表。

        【时辰吉凶项目】
        - 大黄道（青龙、明堂、天刑、朱雀等）
        - 小黄道（建除十二神）
        - 贵人时、禄神时
        - 红鸾时、天喜时
        - 五不遇时
        - 日破时、冲命（禁用标志）
        - 冲阴胎、冲阳气（需构造时传入双方生月干支；禁用标志）

        Args:
            sizhu: 四柱信息

        Returns:
            list: [{'时辰': '子时', '地支': '子', '分值': 0, '禁用': False, '说明': [...]}, ...]
        """
        results = []
        day_gan = sizhu['day_gan']
        day_zhi = sizhu['day_zhi']

        hour_names = {
            '子': '子时(23-1)', '丑': '丑时(1-3)', '寅': '寅时(3-5)',
            '卯': '卯时(5-7)', '辰': '辰时(7-9)', '巳': '巳时(9-11)',
            '午': '午时(11-13)', '未': '未时(13-15)', '申': '申时(15-17)',
            '酉': '酉时(17-19)', '戌': '戌时(19-21)', '亥': '亥时(21-23)'
        }

        wushu_dun = {
            '甲': '甲', '乙': '丙', '丙': '戊', '丁': '庚', '戊': '壬',
            '己': '甲', '庚': '丙', '辛': '戊', '壬': '庚', '癸': '壬'
        }
        zi_gan = wushu_dun.get(day_gan, '甲')
        zi_idx = TIAN_GAN.index(zi_gan)

        for i, zhi in enumerate(DI_ZHI):
            hour_gan = TIAN_GAN[(zi_idx + i) % 10]
            hour_score = 0
            reasons = []
            is_disabled = False

            if self._is_chong_zhi(day_zhi, zhi):
                is_disabled = True
                reasons.append('日破时（禁用）')

            # 时辰刑害扣分（年/月/日支全量检查；刑-15/害-10，不同支扣分叠加；冲已由日破时处理）
            xh_pen, xh_reasons = self._get_xinghai_penalty_all(sizhu, zhi)
            if xh_pen:
                hour_score += xh_pen
                reasons.extend(xh_reasons)

            # 时支与日课年/月/日支构成三合局加分
            sanhe_bonus = self._get_sanhe_daycourse_bonus(sizhu, zhi)
            if sanhe_bonus:
                hour_score += sanhe_bonus['score']
                reasons.append(sanhe_bonus['reason'])

            gui_ren = self._get_gui_ren_shichen(day_gan)
            if zhi in gui_ren:
                hour_score += 15
                reasons.append('贵人时')

            lu = self._get_lu_shichen(day_gan)
            if zhi == lu:
                hour_score += 10
                reasons.append('禄神时')

            if self._is_wubuyu(hour_gan, day_gan):
                hour_score -= 15
                # 2026-10-02：五不遇时即使综合评分为正，也须提示"用课须再权衡"，
                # 避免"五不遇时"与"★吉时"并列而无风险提示。
                reasons.append('五不遇时（用课须再权衡）')

            if self.bride_zhi:
                if self._is_chong_zhi(self.bride_zhi, zhi):
                    is_disabled = True
                    reasons.append('冲新娘（禁用）')
                if not is_disabled:
                    if self._is_liuhe_zhi(self.bride_zhi, zhi):
                        hour_score += 10
                        reasons.append('合新娘')
                    if self._is_banhe_zhi(self.bride_zhi, zhi):
                        hour_score += 6
                        reasons.append('半合新娘')

            if self.groom_zhi:
                if self._is_chong_zhi(self.groom_zhi, zhi):
                    is_disabled = True
                    reasons.append('冲新郎（禁用）')
                if not is_disabled:
                    if self._is_liuhe_zhi(self.groom_zhi, zhi):
                        hour_score += 10
                        reasons.append('合新郎')
                    if self._is_banhe_zhi(self.groom_zhi, zhi):
                        hour_score += 6
                        reasons.append('半合新郎')

            # 冲阴胎 / 冲阳气（典籍"日时勿冲犯阴胎阳气"）：
            # 时支冲新娘阴胎地支（子午冲等）或新郎阳气地支（丑未冲等）→ 该时辰禁用。
            # 日支冲在日课评分中扣30分（婚嫁评分算法），时支冲只在此处置禁用，不入日课总分。
            if self.bride_month_gan and self.bride_month_zhi:
                _yt_gan, _yt_zhi = get_yintai(self.bride_month_gan, self.bride_month_zhi)
                if self._is_chong_zhi(_yt_zhi, zhi):
                    is_disabled = True
                    reasons.append(f'冲阴胎（{zhi}{_yt_zhi}冲，禁用）')
            if self.groom_month_gan and self.groom_month_zhi:
                _yq_gan, _yq_zhi = get_yangqi(self.groom_month_gan, self.groom_month_zhi)
                if self._is_chong_zhi(_yq_zhi, zhi):
                    is_disabled = True
                    reasons.append(f'冲阳气（{zhi}{_yq_zhi}冲，禁用）')

            if self._is_hongluan_hour(zhi, sizhu):
                hour_score += 15
                reasons.append('红鸾时')

            if self._is_tianxi_hour(zhi, sizhu):
                hour_score += 12
                reasons.append('天喜时')

            da_huangdao = self._get_da_huangdao(zhi, day_zhi)
            if da_huangdao:
                reasons.append(f'大黄道{da_huangdao}')
                if da_huangdao in ['青龙', '明堂', '金匮', '天德', '玉堂']:
                    hour_score += 20
                elif da_huangdao in ['天刑', '白虎']:
                    hour_score -= 10

            xiao_huangdao = self._get_xiao_huangdao(zhi)
            if xiao_huangdao:
                reasons.append(f'建除{xiao_huangdao}')
                if xiao_huangdao in ['成', '开', '定']:
                    hour_score += 8
                elif xiao_huangdao in ['破', '闭', '建']:
                    hour_score -= 5

            if not reasons:
                reasons.append('平')

            # 禁用时辰分数强制封顶为 -20（避免"禁用"标记与正分并存误导用户）
            if is_disabled:
                hour_score = min(hour_score, -20)

            results.append({
                '时辰': hour_names.get(zhi, f'{zhi}时'),
                '地支': zhi,
                '天干': hour_gan,
                '分值': hour_score,
                '禁用': is_disabled,
                '说明': reasons
            })

        results.sort(key=lambda x: (-x['禁用'], x['分值']), reverse=True)
        return results

    def _get_da_huangdao(self, zhi, day_zhi):
        """获取大黄道时辰神煞
        
        J2（2026-10-01，001 §57）起例按《协纪辨方书·卷七》引《考原》：
        寅申起子、卯酉起寅、辰戌起辰，
        巳亥起午、子午起申、丑未起戌，顺行十二辰。
        
        十二神顺序：青龙、明堂、天刑、朱雀、金匮、天德、白虎、玉堂、天牢、玄武、司命、勾陈
        """
        day_zhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        da_huangdao_list = ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德',
                            '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈']
        
        # 确定起始时辰（青龙所在的时辰）——J2 按《协纪》卷七更正
        start_map = {
            '子': '申', '午': '申',
            '丑': '戌', '未': '戌',
            '寅': '子', '申': '子',
            '卯': '寅', '酉': '寅',
            '辰': '辰', '戌': '辰',
            '巳': '午', '亥': '午'
        }
        
        try:
            start_zhi = start_map.get(day_zhi, '子')
            start_idx = day_zhi_list.index(start_zhi)
            current_zhi_idx = day_zhi_list.index(zhi)
            
            # 计算偏移量
            offset = (current_zhi_idx - start_idx) % 12
            return da_huangdao_list[offset]
        except:
            return None

    def _get_xiao_huangdao(self, zhi):
        """获取小黄道（建除十二神）

        建除十二神：建、除、满、平、定、执、破、危、成、收、开、闭

        按时辰地支推算：
        子时：建
        丑时：除
        寅时：满
        卯时：平
        辰时：定
        巳时：执
        午时：破
        未时：危
        申时：成
        酉时：收
        戌时：开
        亥时：闭
        """
        xiao_huangdao_map = {
            '子': '建', '丑': '除', '寅': '满', '卯': '平',
            '辰': '定', '巳': '执', '午': '破', '未': '危',
            '申': '成', '酉': '收', '戌': '开', '亥': '闭'
        }
        return xiao_huangdao_map.get(zhi)
    
    def _is_chong_zhi(self, zhi1, zhi2):
        """检查两个地支是否对冲"""
        try:
            idx1 = DI_ZHI.index(zhi1)
            idx2 = DI_ZHI.index(zhi2)
            return abs(idx1 - idx2) == 6
        except:
            return False
    
    def _is_liuhe_zhi(self, zhi1, zhi2):
        """检查两个地支是否六合"""
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        return liuhe_map.get(zhi1) == zhi2
    
    def _is_banhe_zhi(self, zhi1, zhi2):
        """检查两个地支是否半合（同属一个三合局且非相同地支）。

        注意：两支仅构成半合局（缺第三支），非完整三合局。
        完整三合局（三支齐备）的判定见神煞基类._get_sanhe_daycourse_bonus。
        """
        sanhe_groups = [
            {'申', '子', '辰'},
            {'寅', '午', '戌'},
            {'巳', '酉', '丑'},
            {'亥', '卯', '未'}
        ]
        for group in sanhe_groups:
            if zhi1 in group and zhi2 in group and zhi1 != zhi2:
                return True
        return False
    
    def _get_gui_ren_shichen(self, gan):
        """返回某天干的贵人时辰地支列表"""
        gui_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'], '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '戊': ['丑', '未'], '己': ['子', '申'], '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }
        return gui_map.get(gan, [])
    
    def _get_lu_shichen(self, gan):
        """返回某天干的禄神时辰地支"""
        lu_map = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
            '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'
        }
        return lu_map.get(gan)
    
    def _is_wubuyu(self, hour_gan, day_gan):
        """检查五不遇时

        五不遇时：时干克日干，且两者阴阳相同。
        位移差固定为6（顺数第7位）：甲日庚时、乙日辛时、丙日壬时、
        丁日癸时、戊日甲时、己日乙时、庚日丙时、辛日丁时、壬日戊时、癸日己时。

        例如：甲日→庚时（甲0，庚6，差6，金克木）；丁日→癸时（丁3，癸9，差6，水克火）。
        """
        try:
            hour_idx = TIAN_GAN.index(hour_gan)
            day_idx = TIAN_GAN.index(day_gan)

            if (hour_idx - day_idx) % 10 == 6:
                yang_gan = ['甲', '丙', '戊', '庚', '壬']
                hour_is_yang = hour_gan in yang_gan
                day_is_yang = day_gan in yang_gan
                if hour_is_yang == day_is_yang:
                    return True
        except:
            pass
        return False
    
    def _is_hongluan_hour(self, hour_zhi, sizhu):
        """检查是否红鸾时（按年支推算）"""
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            return False
        
        hongluan_map = {
            '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
            '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
            '申': '未', '酉': '午', '戌': '巳', '亥': '辰'
        }
        return hongluan_map.get(year_zhi) == hour_zhi
    
    def _is_tianxi_hour(self, hour_zhi, sizhu):
        """检查是否天喜时（红鸾对冲）"""
        year_zhi = sizhu.get('year_zhi', '')
        if not year_zhi:
            return False
        
        hongluan_map = {
            '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
            '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
            '申': '未', '酉': '午', '戌': '巳', '亥': '辰'
        }
        hongluan = hongluan_map.get(year_zhi, '')
        if hongluan:
            try:
                idx = DI_ZHI.index(hongluan)
                tianxi = DI_ZHI[(idx + 6) % 12]
                return hour_zhi == tianxi
            except:
                pass
        return False
    
    def get_daliyue_info(self, sizhu):
        """
        获取大利月/小利月信息
        
        Args:
            sizhu: 四柱信息
            
        Returns:
            dict: {'大利月': [...], '小利月': [...], '当前月份状态': '大利月/小利月/普通月份'}
        """
        if not self.bride_zhi:
            return {'大利月': [], '小利月': [], '当前月份状态': '未知（缺少新娘生肖）'}
        
        # 大利月口诀：正七迎鸡兔，二八虎和猴，三九蛇共猪，四十龙和狗，牛羊五十一，鼠马六腊月
        # 小利月口诀：鼠马二八月，牛羊四十当，虎猴正七月，兔鸡六腊月，龙狗三九月，蛇猪五十一
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
        
        info = li_yue_table.get(self.bride_zhi, {'大利月': [], '小利月': []})
        
        month_names = {1: '正月', 2: '二月', 3: '三月', 4: '四月',
                       5: '五月', 6: '六月', 7: '七月', 8: '八月',
                       9: '九月', 10: '十月', 11: '十一月', 12: '十二月'}
        
        dali_names = [month_names.get(m, str(m)) for m in info['大利月']]
        xiaoli_names = [month_names.get(m, str(m)) for m in info['小利月']]
        
        # 2026-09-03 利月一致性修复：当前农历月份以sizhu.date高精度农历转换结果为准，
        # 不再用节气月支法（寅=1丑=12）代推，避免2026-02-05这类"寅月但农历腊月"被误判。
        def _resolve_lunar_month(sz):
            try:
                # 本模块在 modules.shensha 包内，'..' 即 modules 包
                from ..四柱计算器 import get_lunar_date as _gld
            except Exception:
                try:
                    from modules.四柱计算器 import get_lunar_date as _gld
                except Exception:
                    try:
                        from 四柱计算器 import get_lunar_date as _gld
                    except Exception:
                        _gld = None
            # 1) 内建字段优先
            lm = sz.get('lunar_month')
            if isinstance(lm, (int, float)) and 1 <= int(lm) <= 12:
                return int(lm)
            try:
                lun = sz.get('lunar')
                if isinstance(lun, dict):
                    m = lun.get('month')
                    if isinstance(m, (int, float)) and 1 <= int(m) <= 12:
                        return int(m)
                    mc = str(lun.get('month_chinese') or lun.get('month') or '')
                    mp = {'正月':1,'二月':2,'三月':3,'四月':4,'五月':5,'六月':6,
                          '七月':7,'八月':8,'九月':9,'十月':10,'十一月':11,'冬月':11,'腊月':12}
                    if mc in mp: return mp[mc]
            except Exception:
                pass
            # 2) 高精度农历（推荐）
            d = sz.get('date') or sz.get('datetime')
            if _gld is not None and hasattr(d, 'year'):
                try:
                    lun = _gld(d)
                    if isinstance(lun, dict):
                        m = lun.get('month')
                        if isinstance(m, (int, float)) and 1 <= int(m) <= 12:
                            return int(m)
                        mc = str(lun.get('month_chinese') or lun.get('month') or '')
                        mp = {'正月':1,'二月':2,'三月':3,'四月':4,'五月':5,'六月':6,
                              '七月':7,'八月':8,'九月':9,'十月':10,'十一月':11,'冬月':11,'腊月':12}
                        if mc in mp: return mp[mc]
                except Exception:
                    pass
            # 3) 回退：节气月支法
            zhi_to_month = {
                '寅': 1, '卯': 2, '辰': 3, '巳': 4,
                '午': 5, '未': 6, '申': 7, '酉': 8,
                '戌': 9, '亥': 10, '子': 11, '丑': 12
            }
            return zhi_to_month.get(sz.get('month_zhi', ''), 0)

        current_month = _resolve_lunar_month(sizhu)
        
        if current_month in info['大利月']:
            status = f"大利月（+30分，农历{current_month}月）"
        elif current_month in info['小利月']:
            status = f"小利月（+15分，农历{current_month}月）"
        else:
            status = '普通月份（无利月加分）'
        
        return {
            '大利月': dali_names,
            '小利月': xiaoli_names,
            '当前月份状态': status
        }
    
    def get_fuzi_info(self, bride_year_gan=None, bride_year_zhi=None, bride_day_gan=None, bride_day_zhi=None, bride_month_gan=None, bride_month_zhi=None, groom_month_gan=None, groom_month_zhi=None):
        """
        计算新娘的夫子星、阴胎，以及新郎的阳气等信息

        注意：夫子星需要新娘年柱（年干、年支）；
        阴胎取新娘月柱、阳气取新郎月柱（均为干+1支+3胎元法）。

        Args:
            bride_year_gan: 新娘年干（计算夫子星必须）
            bride_year_zhi: 新娘年支（计算夫子星必须）
            bride_day_gan: 新娘日干（保留参数，兼容旧接口）
            bride_day_zhi: 新娘日支（保留参数，兼容旧接口）
            bride_month_gan: 新娘月干（计算阴胎必须）
            bride_month_zhi: 新娘月支（计算阴胎必须）
            groom_month_gan: 新郎月干（计算阳气必须）
            groom_month_zhi: 新郎月支（计算阳气必须）

        Returns:
            dict: 包含夫子星、阴胎（新娘）、阳气（新郎）等信息的字典
                  如果缺少必要信息，返回提示信息
        """
        result = {}
        
        # 计算夫子星（需要年柱）
        if bride_year_gan and bride_year_zhi:
            try:
                from modules.工具函数 import get_fuzi
                fuzi_info = get_fuzi(bride_year_gan, bride_year_zhi)
                result['夫子星'] = fuzi_info.get('fu', '未知')
                result['子星'] = fuzi_info.get('zi', '未知')
            except ImportError:
                result['夫子星'] = '未知'
                result['子星'] = '未知'
        else:
            result['夫子星'] = '未知（缺少年柱信息）'
            result['子星'] = '未知（缺少年柱信息）'
        
        # 阴胎（新娘月柱）与阳气（新郎月柱），同法：干+1支+3（胎元）
        try:
            from modules.工具函数 import get_yintai, get_yangqi
        except ImportError:
            get_yintai = get_yangqi = None
        if bride_month_gan and bride_month_zhi and get_yintai:
            try:
                result['阴胎'] = get_yintai(bride_month_gan, bride_month_zhi)
            except Exception:
                result['阴胎'] = '未知'
        else:
            result['阴胎'] = '未知（缺少新娘月柱信息）'
        if groom_month_gan and groom_month_zhi and get_yangqi:
            try:
                result['阳气'] = get_yangqi(groom_month_gan, groom_month_zhi)
            except Exception:
                result['阳气'] = '未知'
        else:
            result['阳气'] = '未知（缺少新郎月柱信息）'
        
        return result
