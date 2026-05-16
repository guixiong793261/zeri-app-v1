# -*- coding: utf-8 -*-
"""
================================================================================
黄道模块（修正版）
================================================================================
计算大黄道（十二值星）和小黄道（十二建星）
数据依据《协纪辨方书》及传统通书

【大黄道十二值星】
吉星：青龙、明堂、金匮、天德、玉堂、司命
凶星：天刑、朱雀、白虎、天牢、玄武、勾陈

【小黄道十二建星】
顺序：建、除、满、平、定、执、破、危、成、收、开、闭
推算方法：以月支定建星起始点（建日即为月支），然后按顺序循环

【主要修正点说明】
小黄道表 XIAO_HUANG_DAO_TABLE 已按正确顺序重建：
- 每一行对应一个月份（月支），列顺序为日支从子到亥（索引0→子，11→亥）
- 例如寅月，子日应为"开"（因为寅月建日在寅，子日逆推两位得到开）
- 确保 day_idx 直接索引即可得到正确的建星
================================================================================
"""

from datetime import datetime

class 黄道计算器:
    """黄道计算器"""
    
    # 大黄道十二值星
    DA_HUANG_DAO = {
        '青龙': {'type': '吉', 'score': 15, 'description': '黄道吉日，诸事皆宜'},
        '明堂': {'type': '吉', 'score': 15, 'description': '黄道吉日，诸事皆宜'},
        '金匮': {'type': '吉', 'score': 10, 'description': '黄道吉日，宜积蓄财物'},
        '天德': {'type': '吉', 'score': 15, 'description': '黄道吉日，百事皆吉'},
        '玉堂': {'type': '吉', 'score': 15, 'description': '黄道吉日，诸事皆宜'},
        '司命': {'type': '吉', 'score': 10, 'description': '黄道吉日，宜祈福'},
        '天刑': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '朱雀': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '白虎': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '天牢': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '玄武': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
        '勾陈': {'type': '凶', 'score': -15, 'description': '黑道凶日，诸事不宜'},
    }
    
    # 小黄道十二建星
    XIAO_HUANG_DAO = {
        '建': {'type': '平', 'score': 0, 'description': '建日，宜出行、上任，忌动土、安葬'},
        '除': {'type': '吉', 'score': 5, 'description': '除日，宜扫除、清洁，忌安葬'},
        '满': {'type': '吉', 'score': 5, 'description': '满日，宜祭祀、祈福，忌动土'},
        '平': {'type': '平', 'score': 0, 'description': '平日，诸事皆宜'},
        '定': {'type': '吉', 'score': 5, 'description': '定日，宜嫁娶、立约，忌出行'},
        '执': {'type': '平', 'score': 0, 'description': '执日，宜修造、动土，忌嫁娶'},
        '破': {'type': '凶', 'score': -10, 'description': '破日，诸事不宜'},
        '危': {'type': '凶', 'score': -10, 'description': '危日，诸事不宜'},
        '成': {'type': '吉', 'score': 5, 'description': '成日，诸事皆宜'},
        '收': {'type': '平', 'score': 0, 'description': '收日，宜收敛、积蓄，忌嫁娶'},
        '开': {'type': '吉', 'score': 5, 'description': '开日，诸事皆宜'},
        '闭': {'type': '平', 'score': 0, 'description': '闭日，宜闭门、静养，忌出行'},
    }
    
    # 大黄道计算表（根据日支和时辰）
    DA_HUANG_DAO_TABLE = {
        '子': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
        '丑': ['天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂'],
        '寅': ['朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑'],
        '卯': ['金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀'],
        '辰': ['天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮'],
        '巳': ['白虎', '玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德'],
        '午': ['玉堂', '天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎'],
        '未': ['天牢', '玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂'],
        '申': ['玄武', '司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢'],
        '酉': ['司命', '勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武'],
        '戌': ['勾陈', '青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命'],
        '亥': ['青龙', '明堂', '天刑', '朱雀', '金匮', '天德', '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'],
    }
    
    # 小黄道计算表（根据月支和日支）
    # 修正后的正确数据表：以月支为键，值为从子日至亥日的建星列表
    # 推导方法：以月支定建星起始点（建日即为月支），然后按"建除满平定执破危成收开闭"顺序循环
    # 例如寅月：寅日为建，卯日为除，辰日为满，…，丑日为闭
    # 对应到日支子日（索引0）应为开（寅前两位），故子日=开
    # 验证：寅月寅日=建，寅月子日=开（正确）
    XIAO_HUANG_DAO_TABLE = {
        '寅': ['开', '闭', '建', '除', '满', '平', '定', '执', '破', '危', '成', '收'],  # 子→亥
        '卯': ['收', '开', '闭', '建', '除', '满', '平', '定', '执', '破', '危', '成'],
        '辰': ['成', '收', '开', '闭', '建', '除', '满', '平', '定', '执', '破', '危'],
        '巳': ['危', '成', '收', '开', '闭', '建', '除', '满', '平', '定', '执', '破'],
        '午': ['破', '危', '成', '收', '开', '闭', '建', '除', '满', '平', '定', '执'],
        '未': ['执', '破', '危', '成', '收', '开', '闭', '建', '除', '满', '平', '定'],
        '申': ['定', '执', '破', '危', '成', '收', '开', '闭', '建', '除', '满', '平'],
        '酉': ['平', '定', '执', '破', '危', '成', '收', '开', '闭', '建', '除', '满'],
        '戌': ['满', '平', '定', '执', '破', '危', '成', '收', '开', '闭', '建', '除'],
        '亥': ['除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭', '建'],
        '子': ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭'],
        '丑': ['闭', '建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开'],
    }
    
    # 大黄道宜忌表（十二值星对应事项的宜忌）
    DA_HUANG_DAO_YIJI = {
        '青龙': {
            'yi': ['嫁娶', '订婚', '出行', '上任', '开业', '修造', '动土', '安葬', '祭祀', '祈福'],
            'ji': ['诉讼', '争斗'],
            'description': '青龙为黄道之首，诸事皆宜，百事大吉'
        },
        '明堂': {
            'yi': ['嫁娶', '订婚', '开业', '修造', '动土', '安葬', '祭祀', '祈福', '入学', '上任'],
            'ji': ['词讼'],
            'description': '明堂主文明，宜文书、教育、公务之事'
        },
        '金匮': {
            'yi': ['嫁娶', '订婚', '开业', '交易', '签约', '纳财', '修造', '动土', '安葬'],
            'ji': ['开仓', '出货'],
            'description': '金匮主财库，宜积蓄财物、交易签约'
        },
        '天德': {
            'yi': ['嫁娶', '订婚', '出行', '上任', '开业', '修造', '动土', '安葬', '祭祀', '祈福', '求医'],
            'ji': ['刑杀', '争斗'],
            'description': '天德为上天之德，百事皆吉，诸凶皆解'
        },
        '玉堂': {
            'yi': ['嫁娶', '订婚', '开业', '修造', '动土', '安葬', '祭祀', '祈福', '会友', '宴饮'],
            'ji': ['诉讼'],
            'description': '玉堂主贵显，宜喜庆、会友、宴饮之事'
        },
        '司命': {
            'yi': ['嫁娶', '订婚', '祭祀', '祈福', '求医', '疗病', '安葬'],
            'ji': ['上任', '出行', '开业'],
            'description': '司命主生命，宜祈福、祭祀、疗病之事'
        },
        '天刑': {
            'yi': ['祭祀', '祈福', '安葬'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '诉讼'],
            'description': '天刑主刑杀，诸事不宜，唯宜祭祀安葬'
        },
        '朱雀': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '诉讼'],
            'description': '朱雀主口舌是非，诸事不宜，易生争端'
        },
        '白虎': {
            'yi': ['祭祀', '祈福', '安葬'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '诉讼'],
            'description': '白虎主凶杀，诸事不宜，唯宜祭祀安葬'
        },
        '天牢': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '诉讼'],
            'description': '天牢主囚禁，诸事不宜，易有阻碍'
        },
        '玄武': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '交易'],
            'description': '玄武主盗贼阴私，诸事不宜，易有损失'
        },
        '勾陈': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '诉讼'],
            'description': '勾陈主牵连阻滞，诸事不宜，易有拖延'
        }
    }
    
    # 小黄道宜忌表（十二建星对应事项的宜忌）
    XIAO_HUANG_DAO_YIJI = {
        '建': {
            'yi': ['出行', '上任', '谒贵', '上书'],
            'ji': ['嫁娶', '安葬', '动土', '修造', '开仓'],
            'description': '建日宜出行上任，忌嫁娶安葬'
        },
        '除': {
            'yi': ['祭祀', '祈福', '扫除', '清洁', '疗病', '出行'],
            'ji': ['嫁娶', '安葬', '上任', '开业'],
            'description': '除日宜清洁扫除，忌嫁娶安葬'
        },
        '满': {
            'yi': ['祭祀', '祈福', '结亲', '会友'],
            'ji': ['动土', '安葬', '上任', '开业'],
            'description': '满日宜祭祀祈福，忌动土安葬'
        },
        '平': {
            'yi': ['祭祀', '祈福', '出行', '会友', '修造'],
            'ji': ['嫁娶', '安葬', '上任', '开业'],
            'description': '平日诸事平平，无大吉凶'
        },
        '定': {
            'yi': ['嫁娶', '订婚', '立约', '交易', '入学', '上任'],
            'ji': ['出行', '诉讼', '安葬'],
            'description': '定日宜立约交易，忌出行诉讼'
        },
        '执': {
            'yi': ['修造', '动土', '捕捉', '狩猎'],
            'ji': ['嫁娶', '安葬', '上任', '开业', '出行'],
            'description': '执日宜修造动土，忌嫁娶安葬'
        },
        '破': {
            'yi': ['祭祀', '祈福', '治病', '拆除'],
            'ji': ['嫁娶', '订婚', '上任', '开业', '修造', '动土', '安葬', '出行'],
            'description': '破日诸事不宜，唯宜治病拆除'
        },
        '危': {
            'yi': ['祭祀', '祈福'],
            'ji': ['嫁娶', '订婚', '上任', '开业', '修造', '动土', '安葬', '出行'],
            'description': '危日诸事不宜，易有危险'
        },
        '成': {
            'yi': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '祭祀', '祈福', '入学'],
            'ji': ['诉讼'],
            'description': '成日诸事皆宜，百事大吉'
        },
        '收': {
            'yi': ['祭祀', '祈福', '纳财', '收敛', '积蓄'],
            'ji': ['嫁娶', '安葬', '上任', '开业', '出行'],
            'description': '收日宜收敛积蓄，忌嫁娶安葬'
        },
        '开': {
            'yi': ['嫁娶', '订婚', '开业', '上任', '出行', '修造', '动土', '安葬', '祭祀', '祈福', '入学'],
            'ji': ['安葬'],
            'description': '开日诸事皆宜，百事大吉'
        },
        '闭': {
            'yi': ['祭祀', '祈福', '闭门', '静养', '收敛'],
            'ji': ['嫁娶', '安葬', '上任', '开业', '出行', '修造', '动土'],
            'description': '闭日宜闭门静养，忌大事'
        }
    }
    
    # 地支索引
    ZHI_INDEX = {'子': 0, '丑': 1, '寅': 2, '卯': 3, '辰': 4, '巳': 5, 
                '午': 6, '未': 7, '申': 8, '酉': 9, '戌': 10, '亥': 11}
    
    def __init__(self):
        pass
    
    def calculate(self, sizhu):
        """
        计算黄道信息
        
        Args:
            sizhu: 四柱信息，包含年柱、月柱、日柱、时柱
            
        Returns:
            dict: 黄道信息，包含大黄道、小黄道、综合评分等
        """
        day_zhi = sizhu['日柱'][1]  # 日支
        month_zhi = sizhu['月柱'][1]  # 月支
        hour_zhi = sizhu['时柱'][1]  # 时支
        
        # 计算大黄道
        da_huang_dao = self._calculate_da_huang_dao(day_zhi, hour_zhi)
        
        # 计算小黄道
        xiao_huang_dao = self._calculate_xiao_huang_dao(month_zhi, day_zhi)
        
        # 计算黄道综合评分
        huang_dao_score = da_huang_dao['score'] + xiao_huang_dao['score']
        
        # 判断黄道等级
        huang_dao_level = self._get_huang_dao_level(da_huang_dao, xiao_huang_dao)
        
        return {
            'da_huang_dao': da_huang_dao,
            'xiao_huang_dao': xiao_huang_dao,
            'huang_dao_score': huang_dao_score,
            'huang_dao_level': huang_dao_level,
            'description': self._generate_description(da_huang_dao, xiao_huang_dao)
        }
    
    def _calculate_da_huang_dao(self, day_zhi, hour_zhi):
        """计算大黄道"""
        day_idx = self.ZHI_INDEX.get(day_zhi, 0)
        hour_idx = self.ZHI_INDEX.get(hour_zhi, 0)

        da_list = self.DA_HUANG_DAO_TABLE.get(day_zhi, [])
        if not da_list:
            return {'name': '未知', 'type': '平', 'score': 0, 'description': ''}

        name = da_list[hour_idx % 12]
        info = self.DA_HUANG_DAO.get(name, {'type': '平', 'score': 0, 'description': ''})

        return {
            'name': name,
            'type': info['type'],
            'score': info['score'],
            'description': info['description']
        }

    def _calculate_xiao_huang_dao(self, month_zhi, day_zhi):
        """计算小黄道"""
        xiao_list = self.XIAO_HUANG_DAO_TABLE.get(month_zhi, [])
        if not xiao_list:
            return {'name': '未知', 'type': '平', 'score': 0, 'description': ''}

        day_idx = self.ZHI_INDEX.get(day_zhi, 0)

        name = xiao_list[day_idx % 12]
        info = self.XIAO_HUANG_DAO.get(name, {'type': '平', 'score': 0, 'description': ''})

        return {
            'name': name,
            'type': info['type'],
            'score': info['score'],
            'description': info['description']
        }

    def _get_huang_dao_level(self, da_huang_dao, xiao_huang_dao):
        """
        判断黄道等级
        规则：
        - 大黄道凶 → 凶（不论小黄道）
        - 大黄道吉且小黄道吉 → 大吉
        - 大黄道吉且小黄道平 → 吉
        - 大黄道吉且小黄道凶 → 次吉
        - 大黄道平且小黄道吉 → 吉
        - 大黄道平且小黄道平 → 平
        - 大黄道平且小黄道凶 → 次凶
        """
        if da_huang_dao['type'] == '凶':
            return '凶'

        if da_huang_dao['type'] == '吉':
            if xiao_huang_dao['type'] == '吉':
                return '大吉'
            elif xiao_huang_dao['type'] == '平':
                return '吉'
            else:
                return '次吉'

        if xiao_huang_dao['type'] == '吉':
            return '吉'
        elif xiao_huang_dao['type'] == '平':
            return '平'
        else:
            return '次凶'

    def _generate_description(self, da, xiao):
        """生成描述文本"""
        desc = []
        if da['type'] == '吉':
            desc.append(f"大黄道{da['name']}，{da['description']}")
        elif da['type'] == '凶':
            desc.append(f"黑道{da['name']}，{da['description']}")
        else:
            desc.append(f"大黄道{da['name']}")

        if xiao['type'] == '吉':
            desc.append(f"小黄道{xiao['name']}，{xiao['description']}")
        elif xiao['type'] == '凶':
            desc.append(f"小黄道{xiao['name']}，{xiao['description']}")
        else:
            desc.append(f"小黄道{xiao['name']}")

        return '；'.join(desc)
    
    def get_yiji(self, sizhu, event_type=None):
        """
        获取黄道宜忌信息
        
        Args:
            sizhu: 四柱信息
            event_type: 事项类型（如'嫁娶'、'修造'等），为None则返回所有宜忌
            
        Returns:
            dict: 宜忌信息
        """
        day_zhi = sizhu['日柱'][1]  # 日支
        month_zhi = sizhu['月柱'][1]  # 月支
        hour_zhi = sizhu['时柱'][1]  # 时支
        
        # 计算大黄道和小黄道
        da_huang_dao = self._calculate_da_huang_dao(day_zhi, hour_zhi)
        xiao_huang_dao = self._calculate_xiao_huang_dao(month_zhi, day_zhi)
        
        # 获取宜忌
        da_yiji = self.DA_HUANG_DAO_YIJI.get(da_huang_dao['name'], {})
        xiao_yiji = self.XIAO_HUANG_DAO_YIJI.get(xiao_huang_dao['name'], {})
        
        result = {
            'da_huang_dao': {
                'name': da_huang_dao['name'],
                'type': da_huang_dao['type'],
                'yi': da_yiji.get('yi', []),
                'ji': da_yiji.get('ji', []),
                'description': da_yiji.get('description', '')
            },
            'xiao_huang_dao': {
                'name': xiao_huang_dao['name'],
                'type': xiao_huang_dao['type'],
                'yi': xiao_yiji.get('yi', []),
                'ji': xiao_yiji.get('ji', []),
                'description': xiao_yiji.get('description', '')
            }
        }
        
        # 如果指定了事项类型，检查该事项是否适宜
        if event_type:
            result['event_check'] = self._check_event_yiji(event_type, da_yiji, xiao_yiji)
        
        return result
    
    def _check_event_yiji(self, event_type, da_yiji, xiao_yiji):
        """
        检查特定事项的宜忌
        
        Args:
            event_type: 事项类型
            da_yiji: 大黄道宜忌
            xiao_yiji: 小黄道宜忌
            
        Returns:
            dict: 检查结果
        """
        da_yi = da_yiji.get('yi', [])
        da_ji = da_yiji.get('ji', [])
        xiao_yi = xiao_yiji.get('yi', [])
        xiao_ji = xiao_yiji.get('ji', [])
        
        # 检查大黄道
        da_suitable = event_type in da_yi
        da_unsuitable = event_type in da_ji
        
        # 检查小黄道
        xiao_suitable = event_type in xiao_yi
        xiao_unsuitable = event_type in xiao_ji
        
        # 综合判断
        if da_unsuitable or xiao_unsuitable:
            status = '忌'
            score = -20
        elif da_suitable and xiao_suitable:
            status = '大吉'
            score = 15
        elif da_suitable or xiao_suitable:
            status = '宜'
            score = 8
        else:
            status = '平'
            score = 0
        
        return {
            'event': event_type,
            'status': status,
            'score': score,
            'da_huang_dao_suitable': da_suitable,
            'da_huang_dao_unsuitable': da_unsuitable,
            'xiao_huang_dao_suitable': xiao_suitable,
            'xiao_huang_dao_unsuitable': xiao_unsuitable
        }
    
    def get_day_yiji(self, month_zhi, day_zhi):
        """
        获取某日的宜忌（便捷方法）
        
        Args:
            month_zhi: 月支
            day_zhi: 日支
            
        Returns:
            dict: 宜忌信息
        """
        # 计算小黄道
        xiao_huang_dao = self._calculate_xiao_huang_dao(month_zhi, day_zhi)
        xiao_yiji = self.XIAO_HUANG_DAO_YIJI.get(xiao_huang_dao['name'], {})
        
        return {
            'jianxing': xiao_huang_dao['name'],
            'type': xiao_huang_dao['type'],
            'yi': xiao_yiji.get('yi', []),
            'ji': xiao_yiji.get('ji', []),
            'description': xiao_yiji.get('description', '')
        }


# 全局黄道计算器实例
huangdao_calculator = 黄道计算器()

def calculate_huangdao(sizhu):
    """
    计算黄道信息（便捷函数）

    Args:
        sizhu: 四柱信息，格式与黄道计算器.calculate 要求一致

    Returns:
        dict: 黄道信息
    """
    return huangdao_calculator.calculate(sizhu)

def get_huangdao_yiji(sizhu, event_type=None):
    """
    获取黄道宜忌信息（便捷函数）

    Args:
        sizhu: 四柱信息
        event_type: 事项类型（如'嫁娶'、'修造'等），为None则返回所有宜忌

    Returns:
        dict: 宜忌信息
    """
    return huangdao_calculator.get_yiji(sizhu, event_type)

def get_day_yiji(month_zhi, day_zhi):
    """
    获取某日的宜忌（便捷函数）

    Args:
        month_zhi: 月支
        day_zhi: 日支

    Returns:
        dict: 宜忌信息
    """
    return huangdao_calculator.get_day_yiji(month_zhi, day_zhi)
