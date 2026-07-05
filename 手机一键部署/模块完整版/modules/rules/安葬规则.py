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
安葬规则模块
================================================================================
实现安葬择日的宜忌规则
核心规则基于《协纪辨方书》：
1. 建除十二神：宜成、开；忌破、闭、建
2. 天德、月德日宜
3. 不将日宜
4. 忌月破、岁破、四离四绝
5. 重丧日忌（一票否决）
6. 山向五行生扶判断
7. 忌与事主年命相冲
================================================================================
"""

from .规则基类 import EventRuleChecker
from datetime import date

class BurialRuleChecker(EventRuleChecker):
    """安葬规则检查器
    
    集成二十四山择吉天机数据，提供：
    - 流年吉凶检查
    - 安葬流月吉凶检查
    - 避忌信息检查（冲山、山家三煞、阴府、克山运等）
    """

    # 建除十二神分类
    JIANCHU_YI = ['成', '开', '定']
    JIANCHU_JI = ['破', '闭', '建']
    
    # 二十四山五行映射
    SHANXIANG_WUXING = {
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
        
        try:
            from ..二十四山择吉天机 import (
                get_mountain_data,
                check_year_luck,
                check_month_luck,
                check_keshan
            )
            self.get_mountain_data = get_mountain_data
            self.check_year_luck = check_year_luck
            self.check_month_luck = check_month_luck
            self.check_keshan = check_keshan
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
                get_jianchu, is_tiande_day, is_yuede_day,
                is_bujiang_day, is_month_break, is_year_break, is_sili_sijue
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
    
    def _is_chong_sang(self, sizhu):
        """检查重丧日（一票否决）
        
        重丧日规则：
        - 春月（寅卯辰）：甲、乙日
        - 夏月（巳午未）：丙、丁日
        - 秋月（申酉戌）：庚、辛日
        - 冬月（亥子丑）：壬、癸日
        
        以及：
        - 每月初三、二十七日为重丧日
        """
        day_gan = sizhu.get('day_gan', '')
        month_zhi = sizhu.get('month_zhi', '')
        day = sizhu.get('day', 0)
        
        # 每月固定重丧日
        if day in [3, 27]:
            return True
        
        # 按季节判断重丧日
        spring_months = ['寅', '卯', '辰']
        summer_months = ['巳', '午', '未']
        autumn_months = ['申', '酉', '戌']
        winter_months = ['亥', '子', '丑']
        
        if month_zhi in spring_months and day_gan in ['甲', '乙']:
            return True
        if month_zhi in summer_months and day_gan in ['丙', '丁']:
            return True
        if month_zhi in autumn_months and day_gan in ['庚', '辛']:
            return True
        if month_zhi in winter_months and day_gan in ['壬', '癸']:
            return True
        
        return False
    
    def _is_ya_sang(self, sizhu):
        """检查压丧日
        
        压丧日：月支与日支相同（伏吟）
        """
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        return month_zhi == day_zhi
    
    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查安葬规则"""
        yi_list = []
        ji_list = []

        date_obj = self._sizhu_to_date(sizhu)
        if not date_obj:
            return yi_list, ji_list
        
        house_type = kwargs.get('house_type')
        shan_xiang = kwargs.get('shan_xiang')
        
        # 1. 一票否决：重丧日
        if self._is_chong_sang(sizhu):
            ji_list.append('重丧日忌安葬（一票否决）')
            return yi_list, ji_list
        
        # 2. 压丧日
        if self._is_ya_sang(sizhu):
            ji_list.append('压丧日忌安葬')
        
        # 3. 建除十二神规则
        self._check_jianchu(date_obj, yi_list, ji_list)
        
        # 4. 天德、月德日
        self._check_tiande_yuede(date_obj, yi_list)
        
        # 5. 不将日
        self._check_bujiang(date_obj, yi_list)
        
        # 6. 月破、岁破、四离四绝
        self._check_po_and_sili(date_obj, sizhu, owners, ji_list)
        
        # 7. 山向相关规则（扶山）
        zuoshan = self._extract_zuoshan(shan_xiang)
        if zuoshan:
            self._check_fushan(sizhu, zuoshan, yi_list, ji_list)
        
        # 8. 相主：忌与事主生肖相冲
        self._check_shengxiao_chong(sizhu, owners, ji_list)
        
        # 9. 二十四山择吉天机检查
        if shan_xiang and self.has_mountain_data:
            self._check_mountain_yearly_luck(shan_xiang, sizhu, yi_list, ji_list)
            self._check_mountain_monthly_luck(shan_xiang, date_obj, yi_list, ji_list)
            self._check_mountain_avoid_info(shan_xiang, sizhu, ji_list)
            self._check_mountain_keshan(shan_xiang, sizhu, ji_list)
        
        # 10. 综合判断
        if yi_list and not ji_list:
            yi_list.append('安葬')
        elif ji_list:
            ji_list.append('安葬')

        return yi_list, ji_list
    
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
    
    def _check_po_and_sili(self, date_obj, sizhu, owners, ji_list):
        """检查月破、岁破、四离四绝"""
        if not self.has_marriage_shensha:
            return
        
        try:
            if self.is_month_break(date_obj):
                ji_list.append('月破日忌安葬')
            
            if self.is_sili_sijue(date_obj):
                ji_list.append('四离四绝日忌安葬')
            
            # 岁破（年支与日支相冲）
            year_zhi = sizhu.get('year_zhi', '')
            if year_zhi and self.is_year_break(date_obj, year_zhi):
                ji_list.append('岁破日忌安葬')
            
            # 与事主年支相冲
            if owners:
                for owner in owners:
                    owner_zhi = self._get_owner_year_zhi(owner)
                    if owner_zhi and self.is_year_break(date_obj, owner_zhi):
                        name = owner.get('name', '事主')
                        ji_list.append(f'与{name}年命相冲，忌安葬')
        except Exception:
            pass
    
    def _check_fushan(self, sizhu, zuoshan, yi_list, ji_list):
        """扶山：日课生扶坐山为吉，克制坐山为凶"""
        zuoshan_wuxing = self.SHANXIANG_WUXING.get(zuoshan)
        if not zuoshan_wuxing:
            return
        
        day_zhi = sizhu.get('day_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        
        # 检查日课地支是否生扶坐山
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
    
    def _check_shengxiao_chong(self, sizhu, owners, ji_list):
        """
        检查四柱与事主生肖相冲
        传统择日：年=日 > 月 > 时；长子（承重孙）一票否决
        
        参数:
            sizhu: 四柱字典
            owners: 事主列表
            ji_list: 忌项列表，会被修改
        """
        if not owners:
            return
        
        # 获取四柱地支
        year_zhi = sizhu.get('year_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        hour_zhi = sizhu.get('hour_zhi', '')
        
        if not day_zhi:
            return
        
        # 地支六冲表
        chong_map = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        
        # 检查每个事主
        for owner in owners:
            name = owner.get('name', '事主')
            role = owner.get('role', '').lower()
            shengxiao = owner.get('生肖', '')
            
            if not shengxiao:
                shengxiao = self._get_owner_year_zhi(owner)
            
            if not shengxiao:
                continue
            
            # 判断是否为长子/承重孙（一票否决对象）
            is_eldest = role in ('长子', '承重孙', '孝子', '主祭') or name in ('长子', '孝子', '主祭')
            target_chong_zhi = chong_map.get(shengxiao, '')
            
            if not target_chong_zhi:
                continue
            
            # 检查年柱
            if year_zhi == target_chong_zhi:
                if is_eldest:
                    ji_list.append(f'长子{name}年命被年柱{year_zhi}冲，一票否决')
                    return  # 直接返回，一票否决
                else:
                    ji_list.append(f'年柱{year_zhi}冲{name}生肖{shengxiao}')
            
            # 检查月柱
            if month_zhi == target_chong_zhi:
                if is_eldest:
                    ji_list.append(f'长子{name}年命被月柱{month_zhi}冲')
                else:
                    ji_list.append(f'月柱{month_zhi}冲{name}生肖{shengxiao}')
            
            # 检查日柱
            if day_zhi == target_chong_zhi:
                if is_eldest:
                    ji_list.append(f'长子{name}年命被日柱{day_zhi}冲，一票否决')
                    return  # 直接返回，一票否决
                else:
                    ji_list.append(f'日柱{day_zhi}冲{name}生肖{shengxiao}')
            
            # 检查时柱
            if hour_zhi == target_chong_zhi:
                if is_eldest:
                    ji_list.append(f'长子{name}年命被时柱{hour_zhi}冲')
                else:
                    ji_list.append(f'时柱{hour_zhi}冲{name}生肖{shengxiao}')
    
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
        """检查安葬流月吉凶
        
        根据二十四山择吉天机数据，检查当前月份对山向的安葬吉凶
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
            month_data = self.check_month_luck(shan_xiang, month_name, bury=True)
            
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

# 测试
if __name__ == '__main__':
    checker = BurialRuleChecker()
    
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
    yi_list, ji_list = checker._check_rules(test_sizhu, test_owners, house_type='阴宅', shan_xiang='乾山巽向')
    
    print("宜：", yi_list)
    print("忌：", ji_list)