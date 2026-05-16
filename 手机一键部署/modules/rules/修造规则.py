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

# -*- coding: utf-8 -*-
"""
================================================================================
修建规则模块（基于《协纪辨方书》）
================================================================================
实现修造、动土等修建类事项的宜忌规则

核心规则：
1. 建除十二神：宜成、开、定；忌破、闭、平
2. 天德、月德日宜
3. 不将日宜
4. 忌月破、岁破、四离四绝
5. 扶山：日课五行生扶坐山为宜，克制坐山为忌
6. 相主：忌与事主生肖相冲
7. 山向三合局：日课地支与坐山三合为宜
================================================================================
"""

from .规则基类 import EventRuleChecker
from datetime import date

class ConstructionRuleChecker(EventRuleChecker):
    """修建规则检查器
    
    集成二十四山择吉天机数据，提供：
    - 流年吉凶检查
    - 流月吉凶检查
    - 避忌信息检查（冲山、山家三煞、阴府、克山运等）
    - 杨公风水大吉时
    """
    
    # 建除十二神分类
    JIANCHU_YI = ['成', '开', '定']
    JIANCHU_JI = ['破', '闭', '平']
    
    # 二十四山五行映射
    SHIERSHAN_WUXING = {
        '壬': '水', '子': '水', '癸': '水',
        '丑': '土', '艮': '土', '寅': '木',
        '甲': '木', '卯': '木', '乙': '木',
        '辰': '土', '巽': '木', '巳': '火',
        '丙': '火', '午': '火', '丁': '火',
        '未': '土', '坤': '土', '申': '金',
        '庚': '金', '酉': '金', '辛': '金',
        '戌': '土', '乾': '金', '亥': '水',
    }
    
    # 地支五行
    ZHI_WUXING = {
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }
    
    # 五行相生（日课生坐山为吉）
    SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    
    # 五行相克（日课克坐山为凶）
    KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
    
    # 三合局
    SANHE_GROUPS = [
        ['申', '子', '辰'],  # 水局
        ['寅', '午', '戌'],  # 火局
        ['巳', '酉', '丑'],  # 金局
        ['亥', '卯', '未']   # 木局
    ]
    
    def __init__(self):
        super().__init__()
        self._init_dependencies()
        self._init_mountain_data()
    
    def _init_mountain_data(self):
        """初始化二十四山择吉天机数据"""
        self.has_mountain_data = False
        self.get_mountain_data = None
        self.check_year_luck = None
        self.check_month_luck = None
        self.check_keshan = None
        self.get_yang_gong_jishi = None
        
        try:
            from ..二十四山择吉天机 import (
                get_mountain_data,
                check_year_luck,
                check_month_luck,
                check_keshan,
                get_yang_gong_jishi
            )
            self.get_mountain_data = get_mountain_data
            self.check_year_luck = check_year_luck
            self.check_month_luck = check_month_luck
            self.check_keshan = check_keshan
            self.get_yang_gong_jishi = get_yang_gong_jishi
            self.has_mountain_data = True
        except ImportError:
            pass
    
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
            self._init_fallback_functions()
    
    def _init_fallback_functions(self):
        """备用函数实现"""
        ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        def fallback_get_jianchu(date_obj):
            try:
                from ..shensha.marriage_shensha import get_day_ganzhi
                month = date_obj.month
                month_zhi = ZHI[(month - 1) % 12]
                _, day_zhi = get_day_ganzhi(date_obj)
                month_idx = ZHI.index(month_zhi) if month_zhi in ZHI else 0
                day_idx = ZHI.index(day_zhi) if day_zhi in ZHI else 0
                offset = (day_idx - month_idx) % 12
                jianchu_list = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']
                return jianchu_list[offset]
            except:
                return ''
        
        self.get_jianchu = fallback_get_jianchu
    
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
    
    def _extract_zuoshan(self, shan_xiang):
        """从山向字符串中提取坐山"""
        if not shan_xiang:
            return None
        
        # 处理"子山午向"格式
        if '山' in shan_xiang:
            return shan_xiang.split('山')[0]
        
        # 处理"乾山巽向"格式
        if len(shan_xiang) >= 1:
            return shan_xiang[0]
        
        return shan_xiang
    
    def _get_owner_year_zhi(self, owner):
        """获取事主年支"""
        if '生肖' in owner:
            zhi_map = {'鼠':'子','牛':'丑','虎':'寅','兔':'卯','龙':'辰','蛇':'巳',
                       '马':'午','羊':'未','猴':'申','鸡':'酉','狗':'戌','猪':'亥'}
            return zhi_map.get(owner['生肖'], '')
        
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
                    owner.get('birth_minute', 0)
                )
                return birth_sizhu['年柱'][1]
            except:
                pass
        
        return None
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查修建规则"""
        yi_list = []
        ji_list = []
        
        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list, False, ""
        
        house_type = kwargs.get('house_type')
        shan_xiang = kwargs.get('shan_xiang')
        
        # 1. 建除十二神规则
        self._check_jianchu(date_obj, yi_list, ji_list)
        
        # 2. 天德、月德日
        self._check_tiande_yuede(date_obj, yi_list)
        
        # 3. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 4. 月破、岁破、四离四绝
        self._check_po_and_sili(date_obj, sizhu, owners, ji_list)
        
        # 5. 山向相关规则（扶山）
        zuoshan = self._extract_zuoshan(shan_xiang)
        if zuoshan:
            self._check_fushan(sizhu, zuoshan, yi_list, ji_list)
            self._check_sanhe(sizhu, zuoshan, yi_list)
        
        # 6. 相主：忌与事主生肖相冲
        self._check_shengxiao_chong(sizhu, owners, ji_list)
        
        # 7. 二十四山择吉天机检查
        if shan_xiang and self.has_mountain_data:
            self._check_mountain_yearly_luck(shan_xiang, sizhu, yi_list, ji_list)
            self._check_mountain_monthly_luck(shan_xiang, date_obj, yi_list, ji_list)
            self._check_mountain_avoid_info(shan_xiang, sizhu, ji_list)
            self._check_mountain_keshan(shan_xiang, sizhu, ji_list)
        
        # 8. 添加通用修造动土宜忌
        self._add_general_yi_ji(yi_list, ji_list)
        
        # 9. 检查一票否决项
        veto, veto_reason = self._check_veto_items(shan_xiang, sizhu, owners, ji_list)
        if veto:
            return yi_list, ji_list, True, veto_reason
        
        return yi_list, ji_list, False, ""
    
    def _check_jianchu(self, date_obj, yi_list, ji_list):
        """检查建除十二神"""
        if not self.get_jianchu:
            return
        
        try:
            jianchu = self.get_jianchu(date_obj)
            if jianchu in self.JIANCHU_YI:
                yi_list.append(f'建除{jianchu}日宜修造')
            elif jianchu in self.JIANCHU_JI:
                ji_list.append(f'建除{jianchu}日忌修造')
        except Exception:
            pass
    
    def _check_tiande_yuede(self, date_obj, yi_list):
        """检查天德、月德日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_tiande_day(date_obj):
                yi_list.append('天德日宜修造')
            if self.is_yuede_day(date_obj):
                yi_list.append('月德日宜修造')
        except Exception:
            pass
    
    def _check_bujiang(self, date_obj, yi_list):
        """检查不将日"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_bujiang_day(date_obj):
                yi_list.append('不将日宜修造')
        except Exception:
            pass
    
    def _check_po_and_sili(self, date_obj, sizhu, owners, ji_list):
        """检查月破、岁破、四离四绝"""
        if not self.has_marriage_shensha:
            return
        
        try:
            # 月破（月支与日支相冲）
            if self.is_month_break(date_obj):
                ji_list.append('月破日忌修造')
            
            # 四离四绝
            if self.is_sili_sijue(date_obj):
                ji_list.append('四离四绝日忌修造')
            
            # 岁破（年支与日支相冲）
            year_zhi = sizhu.get('year_zhi', '')
            if year_zhi and self.is_year_break(date_obj, year_zhi):
                ji_list.append('岁破日忌修造')
            
            # 与事主年支相冲
            if owners:
                for owner in owners:
                    owner_zhi = self._get_owner_year_zhi(owner)
                    if owner_zhi and self.is_year_break(date_obj, owner_zhi):
                        name = owner.get('name', '事主')
                        ji_list.append(f'与{name}年命相冲，忌修造')
        except Exception:
            pass
    
    def _check_fushan(self, sizhu, zuoshan, yi_list, ji_list):
        """扶山：日课生扶坐山为吉，克制坐山为凶
        
        正确规则：日课五行生扶坐山为宜，日课克坐山为凶
        """
        zuoshan_wuxing = self.SHIERSHAN_WUXING.get(zuoshan)
        if not zuoshan_wuxing:
            return
        
        # 获取日课中所有地支
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        
        # 检查日课地支五行是否生扶或克制坐山五行
        for zhi in [day_zhi, month_zhi, year_zhi]:
            if not zhi:
                continue
            
            zhi_wuxing = self.ZHI_WUXING.get(zhi)
            if not zhi_wuxing:
                continue
            
            # 日课生坐山为吉（扶山）
            if self.SHENG.get(zhi_wuxing) == zuoshan_wuxing:
                yi_list.append(f'{zuoshan}山得{zhi}生扶')
                return
            
            # 日课克坐山为凶
            if self.KE.get(zhi_wuxing) == zuoshan_wuxing:
                ji_list.append(f'{zuoshan}山被{zhi}克制')
                return
    
    def _check_sanhe(self, sizhu, zuoshan, yi_list):
        """山向三合局"""
        # 获取日课地支
        zhis = []
        for key in ['year_zhi', 'month_zhi', 'day_zhi']:
            zhi = sizhu.get(key)
            if zhi:
                zhis.append(zhi)
        
        # 检查是否与坐山形成三合局
        for group in self.SANHE_GROUPS:
            if zuoshan in group:
                # 检查日课中是否有另外两个地支中的至少一个
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
    
    def _check_shengxiao_chong(self, sizhu, owners, ji_list):
        """检查与事主生肖相冲"""
        if not owners:
            return
        
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi:
            return
        
        chong_map = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        
        for owner in owners:
            name = owner.get('name', '事主')
            shengxiao = owner.get('生肖', '')
            
            if not shengxiao:
                shengxiao = self._get_owner_year_zhi(owner)
            
            if shengxiao and chong_map.get(shengxiao) == day_zhi:
                ji_list.append(f'与{name}生肖相冲')
    
    def _add_general_yi_ji(self, yi_list, ji_list):
        """添加通用修造动土宜忌"""
        # 如果有宜项且没有忌项，添加通用宜
        if yi_list and not ji_list:
            yi_list.append('修造')
            yi_list.append('动土')
        # 如果有忌项但没有宜项，才添加通用忌
        if ji_list and not yi_list:
            ji_list.append('修造')
            ji_list.append('动土')
    
    def _check_mountain_yearly_luck(self, shan_xiang, sizhu, yi_list, ji_list):
        """检查流年吉凶
        
        根据二十四山择吉天机数据，检查当前年份对山向的吉凶
        """
        if not self.has_mountain_data or not self.check_year_luck:
            return
        
        try:
            year_gan = sizhu.get('year_gan', '')
            year_zhi = sizhu.get('year_zhi', '')
            if not year_gan or not year_zhi:
                return
            
            year_ganzhi = year_gan + year_zhi
            luck = self.check_year_luck(shan_xiang, year_ganzhi)
            
            if luck:
                if '大利' in luck:
                    yi_list.append(f'{shan_xiang}{year_ganzhi}年{luck}')
                elif '不利' in luck:
                    ji_list.append(f'{shan_xiang}{year_ganzhi}年{luck}')
                elif '权用' in luck:
                    yi_list.append(f'{shan_xiang}{year_ganzhi}年{luck}')
                elif '利' in luck and '不利' not in luck:
                    yi_list.append(f'{shan_xiang}{year_ganzhi}年{luck}')
        except Exception:
            pass
    
    def _check_mountain_monthly_luck(self, shan_xiang, date_obj, yi_list, ji_list):
        """检查流月吉凶
        
        根据二十四山择吉天机数据，检查当前月份对山向的吉凶
        """
        if not self.has_mountain_data or not self.check_month_luck:
            return
        
        try:
            month_names = ['正月', '二月', '三月', '四月', '五月', '六月',
                          '七月', '八月', '九月', '十月', '十一月', '十二月']
            month_idx = date_obj.month - 1
            if month_idx < 0 or month_idx >= 12:
                return
            
            month_name = month_names[month_idx]
            month_data = self.check_month_luck(shan_xiang, month_name, bury=False)
            
            if month_data:
                luck = month_data.get('luck', '')
                reason = month_data.get('reason', '')
                jiri = month_data.get('jiri', [])
                
                if luck == '凶':
                    ji_list.append(f'{shan_xiang}{month_name}{reason}')
                elif luck == '吉':
                    yi_list.append(f'{shan_xiang}{month_name}吉')
                    if jiri:
                        day_zhi = ''
                        try:
                            from ..shensha.marriage_shensha import get_day_ganzhi
                            _, day_zhi = get_day_ganzhi(date_obj)
                        except:
                            pass
                        
                        if day_zhi:
                            for jiri_item in jiri:
                                if day_zhi in jiri_item:
                                    yi_list.append(f'{month_name}{jiri_item}日吉')
                                    break
        except Exception:
            pass
    
    def _check_mountain_avoid_info(self, shan_xiang, sizhu, ji_list):
        """检查避忌信息
        
        检查冲山、山家三煞、阴府等避忌
        """
        if not self.has_mountain_data or not self.get_mountain_data:
            return
        
        try:
            data = self.get_mountain_data(shan_xiang)
            if not data or 'avoid_info' not in data:
                return
            
            avoid_info = data['avoid_info']
            year_gan = sizhu.get('year_gan', '')
            year_zhi = sizhu.get('year_zhi', '')
            month_zhi = sizhu.get('month_zhi', '')
            day_zhi = sizhu.get('day_zhi', '')
            hour_zhi = sizhu.get('hour_zhi', '')
            
            # 检查冲山
            chongshan = avoid_info.get('chongshan', '')
            if chongshan:
                chong_zhi = ''
                for zhi in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
                    if f'忌{zhi}年' in chongshan or f'忌{zhi}' in chongshan:
                        chong_zhi = zhi
                        break
                
                if chong_zhi:
                    if year_zhi == chong_zhi:
                        ji_list.append(f'{shan_xiang}冲山：忌{chong_zhi}年')
                    if month_zhi == chong_zhi:
                        ji_list.append(f'{shan_xiang}冲山：忌{chong_zhi}月')
                    if day_zhi == chong_zhi:
                        ji_list.append(f'{shan_xiang}冲山：忌{chong_zhi}日')
                    if hour_zhi == chong_zhi:
                        ji_list.append(f'{shan_xiang}冲山：忌{chong_zhi}时')
            
            # 检查山家三煞
            shanjia_sansha = avoid_info.get('shanjia_sansha', '')
            if shanjia_sansha:
                sansha_zhis = []
                if '寅午戌' in shanjia_sansha:
                    sansha_zhis = ['寅', '午', '戌']
                elif '申子辰' in shanjia_sansha:
                    sansha_zhis = ['申', '子', '辰']
                elif '巳酉丑' in shanjia_sansha:
                    sansha_zhis = ['巳', '酉', '丑']
                elif '亥卯未' in shanjia_sansha:
                    sansha_zhis = ['亥', '卯', '未']
                
                for zhi in sansha_zhis:
                    if year_zhi == zhi:
                        ji_list.append(f'{shan_xiang}山家三煞：忌{zhi}年')
                    if month_zhi == zhi:
                        ji_list.append(f'{shan_xiang}山家三煞：忌{zhi}月')
                    if day_zhi == zhi:
                        ji_list.append(f'{shan_xiang}山家三煞：忌{zhi}日')
            
            # 检查阴府
            yinfu = avoid_info.get('yinfu', '')
            if yinfu:
                yinfu_gans = []
                for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
                    if gan in yinfu:
                        yinfu_gans.append(gan)
                
                for gan in yinfu_gans:
                    if year_gan == gan:
                        ji_list.append(f'{shan_xiang}阴府：忌{gan}年干')
                    if sizhu.get('month_gan') == gan:
                        ji_list.append(f'{shan_xiang}阴府：忌{gan}月干')
                    if sizhu.get('day_gan') == gan:
                        ji_list.append(f'{shan_xiang}阴府：忌{gan}日干')
            
            # 检查山方煞
            shanfang_sha = avoid_info.get('shanfang_sha', {})
            if shanfang_sha:
                ji_ri = shanfang_sha.get('ji_ri', [])
                day_ganzhi = sizhu.get('day_gan', '') + sizhu.get('day_zhi', '')
                for ri in ji_ri:
                    if ri in day_ganzhi or day_ganzhi in ri:
                        ji_list.append(f'{shan_xiang}山方煞：忌{ri}日')
            
            # 检查星曜煞
            xingyao_sha = avoid_info.get('xingyao_sha', '')
            if xingyao_sha and day_ganzhi:
                for item in ['戊辰', '戊戌', '己丑', '己未']:
                    if item in xingyao_sha and item in day_ganzhi:
                        ji_list.append(f'{shan_xiang}星曜煞：忌{item}日')
            
            # 检查剑锋煞
            jianfeng_sha = avoid_info.get('jianfeng_sha', '')
            if jianfeng_sha:
                month_ganzhi = sizhu.get('month_gan', '') + month_zhi
                if jianfeng_sha in month_ganzhi:
                    ji_list.append(f'{shan_xiang}剑锋煞：忌{jianfeng_sha}')
        except Exception:
            pass
    
    def _check_mountain_keshan(self, shan_xiang, sizhu, ji_list):
        """检查克山运
        
        根据年干组合检查克山运
        """
        if not self.has_mountain_data or not self.check_keshan:
            return
        
        try:
            year_gan = sizhu.get('year_gan', '')
            if not year_gan:
                return
            
            gan_combinations = {
                '甲': '甲己', '己': '甲己',
                '乙': '乙庚', '庚': '乙庚',
                '丙': '丙辛', '辛': '丙辛',
                '丁': '丁壬', '壬': '丁壬',
                '戊': '戊癸', '癸': '戊癸'
            }
            
            year_gan_combo = gan_combinations.get(year_gan)
            if not year_gan_combo:
                return
            
            keshan_info = self.check_keshan(shan_xiang, year_gan_combo)
            if not keshan_info:
                return
            
            month = sizhu.get('month', 0)
            day = sizhu.get('day', 0)
            
            dongzhi_month = 12
            is_after_dongzhi = month == dongzhi_month and day >= 22
            
            if is_after_dongzhi:
                key = 'dongzhi_hou'
            else:
                key = 'dongzhi_qian'
            
            if key in keshan_info:
                info = keshan_info[key]
                yun = info.get('yun', '')
                ji = info.get('ji', '')
                if yun and ji:
                    ji_list.append(f'{shan_xiang}克山运：{yun}，{ji}')
        except Exception:
            pass
    
    def _check_veto_items(self, shan_xiang, sizhu, owners, ji_list):
        """检查一票否决项
        
        根据传统择日学，以下事项应直接判为不合格：
        1. 阴府（正阴府+傍阴府）- 修造大忌
        2. 克山运 - 主宅气受损
        3. 坐山犯三煞 - 修造大忌
        4. 年冲事主 - 主事受冲不宜动土
        """
        veto_reasons = []
        
        # 1. 检查阴府（从ji_list中检查是否有阴府相关忌项）
        for ji in ji_list:
            if '阴府' in ji:
                veto_reasons.append(ji)
        
        # 2. 检查克山运（从ji_list中检查）
        for ji in ji_list:
            if '克山运' in ji:
                veto_reasons.append(ji)
        
        # 3. 检查坐山犯三煞
        if shan_xiang and self.has_mountain_data:
            zuoshan = self._extract_zuoshan(shan_xiang)
            if zuoshan:
                # 检查月三煞
                month_zhi = sizhu.get('month_zhi', '')
                # 寅午戌月三煞在北方（亥子丑）
                # 申子辰月三煞在南方（巳午未）
                # 巳酉丑月三煞在东方（寅卯辰）
                # 亥卯未月三煞在西方（申酉戌）
                sansha_map = {
                    '寅': ['亥', '子', '丑'],
                    '午': ['亥', '子', '丑'],
                    '戌': ['亥', '子', '丑'],
                    '申': ['巳', '午', '未'],
                    '子': ['巳', '午', '未'],
                    '辰': ['巳', '午', '未'],
                    '巳': ['寅', '卯', '辰'],
                    '酉': ['寅', '卯', '辰'],
                    '丑': ['寅', '卯', '辰'],
                    '亥': ['申', '酉', '戌'],
                    '卯': ['申', '酉', '戌'],
                    '未': ['申', '酉', '戌']
                }
                sansha_zhis = sansha_map.get(month_zhi, [])
                # 检查坐山是否在三煞方
                zuoshan_zhis = []
                if zuoshan in ['壬', '子', '癸']:
                    zuoshan_zhis = ['子']
                elif zuoshan in ['丑', '艮', '寅']:
                    zuoshan_zhis = ['丑', '寅']
                elif zuoshan in ['甲', '卯', '乙']:
                    zuoshan_zhis = ['卯']
                elif zuoshan in ['辰', '巽', '巳']:
                    zuoshan_zhis = ['辰', '巳']
                elif zuoshan in ['丙', '午', '丁']:
                    zuoshan_zhis = ['午']
                elif zuoshan in ['未', '坤', '申']:
                    zuoshan_zhis = ['未', '申']
                elif zuoshan in ['庚', '酉', '辛']:
                    zuoshan_zhis = ['酉']
                elif zuoshan in ['戌', '乾', '亥']:
                    zuoshan_zhis = ['戌', '亥']
                
                for zuoshan_zhi in zuoshan_zhis:
                    if zuoshan_zhi in sansha_zhis:
                        veto_reasons.append(f'{shan_xiang}坐山犯月三煞（{zuoshan}方为月三煞位）')
                        break
        
        # 4. 检查年冲事主
        if owners:
            year_zhi = sizhu.get('year_zhi', '')
            chong_map = {
                '子': '午', '丑': '未', '寅': '申', '卯': '酉',
                '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
                '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
            }
            year_chong = chong_map.get(year_zhi, '')
            for owner in owners:
                zodiac = owner.get('生肖', '')
                if zodiac and year_chong:
                    zodiac_map = {
                        '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
                        '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
                        '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
                    }
                    owner_zhi = zodiac_map.get(zodiac, '')
                    if owner_zhi == year_chong:
                        veto_reasons.append(f'年支{year_zhi}冲事主{owner.get("name", "")}生肖{zodiac}')
        
        if veto_reasons:
            return True, "、".join(veto_reasons)
        
        return False, ""

# 测试
if __name__ == '__main__':
    checker = ConstructionRuleChecker()
    
    test_sizhu = {
        'day_gan': '丙',
        'day_zhi': '寅',
        'month_zhi': '寅',
        'year_zhi': '子',
        '年柱': '甲子',
        'month': 2,
        'day': 10,
        'year': 2024
    }
    
    test_owners = [{
        'name': '张三',
        '生肖': '猴'
    }]
    
    # 使用新接口测试
    yi_list, ji_list, veto, veto_reason = checker._check_rules(test_sizhu, test_owners, house_type='阳宅', shan_xiang='乾山巽向')
    
    print("宜：", yi_list)
    print("忌：", ji_list)