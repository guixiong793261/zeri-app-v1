# -*- coding: utf-8 -*-
"""
评分器集成八字排盘模块示例
展示如何在评分系统中调用八字排盘模块获取更详细的八字信息
"""

from modules.八字排盘 import BaZiPanPan


class EnhancedScorer:
    """
    增强的评分器（集成八字排盘模块）
    
    展示如何在评分系统中使用八字排盘模块获取更详细的八字信息
    """
    
    def __init__(self):
        self.base_score = 100
        self.final_score = 100
        self.level = ''
        self.shensha_list = []
        self.yi_list = []
        self.ji_list = []
        self.huangdao_info = {}
    
    def score_with_bazi_info(self, sizhu, event_type, owners=None, house_type=None, 
                          shan_xiang=None, zaoxiang=None, zaowei=None, chuangwei=None):
        """
        使用八字排盘模块进行评分（集成示例）
        
        Args:
            sizhu: 四柱信息
            event_type: 事项类型
            owners: 事主信息（可选，包含出生日期和性别）
            house_type: 宅型
            shan_xiang: 山向
            zaoxiang: 灶向
            zaowei: 灶位
            chuangwei: 床位
            
        Returns:
            dict: 评分结果
        """
        # 1. 如果提供了事主信息，创建八字排盘对象
        bazi_info = None
        if owners and len(owners) > 0:
            try:
                owner = owners[0]  # 取第一个事主
                if 'birth_year' in owner and 'birth_month' in owner and 'birth_day' in owner:
                    # 创建八字排盘对象
                    bazi = BaZiPanPan(
                        year=owner['birth_year'],
                        month=owner['birth_month'],
                        day=owner['birth_day'],
                        hour=owner.get('birth_hour', 12),
                        minute=owner.get('birth_minute', 0),
                        gender=owner.get('gender', '男')
                    )
                    bazi_info = bazi.get_panpan_result()
                    
                    # 2. 使用八字排盘信息增强评分
                    print("=== 八字排盘信息 ===")
                    print(f"事主八字: {bazi_info['基本信息']['四柱']}")
                    print(f"藏干: {bazi_info['藏干']}")
                    print(f"十神: {bazi_info['十神']}")
                    print(f"五行统计: {bazi_info['五行统计']}")
                    print(f"五行分数: {bazi_info['五行分数']}")
                    print(f"纳音: {bazi_info['纳音']}")
                    print(f"十二长生: {bazi_info['十二长生']}")
                    
                    # 3. 计算事主大运
                    dayun = bazi.get_dayun()
                    print(f"大运: {[d['大运'] for d in dayun[:3]]}...")
                    
                    # 4. 使用八字信息进行评分调整
                    score_adjustment = self._calculate_bazi_score_adjustment(bazi_info, sizhu)
                    print(f"八字评分调整: {score_adjustment}")
                    
            except Exception as e:
                print(f"八字排盘失败: {e}")
        
        # 5. 执行原有的评分逻辑
        # 这里可以调用原有的评分方法
        # ...
        
        return {
            'base_score': self.base_score,
            'bazi_info': bazi_info,
            'shensha_list': self.shensha_list,
            'yi_list': self.yi_list,
            'ji_list': self.ji_list
        }
    
    def _calculate_bazi_score_adjustment(self, bazi_info, day_sizhu):
        """
        根据八字信息计算评分调整
        
        Args:
            bazi_info: 事主八字信息
            day_sizhu: 日课四柱信息
            
        Returns:
            int: 评分调整值
        """
        adjustment = 0
        
        # 1. 日主与日课日主的五行关系
        try:
            owner_day_gan = bazi_info['基本信息']['四柱']['日柱'][0]
            day_day_gan = day_sizhu.get('day_gan', '')
            
            if owner_day_gan and day_day_gan:
                # 检查五行生克关系
                from modules.八字工具整合 import GAN_WUXING, WUXING_SHENG, WUXING_KE
                
                owner_wx = GAN_WUXING.get(owner_day_gan, '')
                day_wx = GAN_WUXING.get(day_day_gan, '')
                
                if owner_wx and day_wx:
                    # 日课生日主：加分
                    if WUXING_SHENG.get(day_wx) == owner_wx:
                        adjustment += 10
                        print("  日课生日主，加10分")
                    # 日课克日主：减分
                    elif WUXING_KE.get(day_wx) == owner_wx:
                        adjustment -= 15
                        print("  日课克日主，减15分")
                    # 日主生日课：加分
                    elif WUXING_SHENG.get(owner_wx) == day_wx:
                        adjustment += 5
                        print("  日主生日课，加5分")
        
        except Exception as e:
            print(f"  五行关系计算失败: {e}")
        
        # 2. 日主与日课地支的关系
        try:
            owner_day_zhi = bazi_info['基本信息']['四柱']['日柱'][1]
            day_day_zhi = day_sizhu.get('day_zhi', '')
            
            if owner_day_zhi and day_day_zhi:
                # 检查地支关系
                from modules.八字工具整合 import check_liuhe, check_liuchong
                
                # 合：加分
                if check_liuhe(owner_day_zhi, day_day_zhi):
                    adjustment += 8
                    print(f"  日主日支({owner_day_zhi})与日课日支({day_day_zhi})相合，加8分")
                
                # 冲：减分
                if check_liuchong(owner_day_zhi, day_day_zhi):
                    adjustment -= 12
                    print(f"  日主日支({owner_day_zhi})与日课日支({day_day_zhi})相冲，减12分")
        
        except Exception as e:
            print(f"  地支关系计算失败: {e}")
        
        # 3. 纳音匹配度
        try:
            owner_nayin = bazi_info['纳音']['日柱']
            day_nayin = day_sizhu.get('nayin', {}).get('日柱', '')
            
            if owner_nayin and day_nayin and owner_nayin != '未知' and day_nayin != '未知':
                # 提取纳音五行
                from modules.八字工具整合 import NAYIN_WUXING
                
                # 简化：根据纳音名称判断五行
                nayin_wx_map = {
                    '金': ['海中金', '剑锋金', '白蜡金', '砂中金', '金箔金', '钗钏金'],
                    '木': ['大林木', '杨柳木', '松柏木', '平地木', '桑柘木', '大溪水', '石榴木'],
                    '水': ['涧下水', '泉中水', '长流水', '天河水', '大溪水', '大海水'],
                    '火': ['炉中火', '山头火', '霹雳火', '山下火', '覆灯火', '天上火'],
                    '土': ['路旁土', '城头土', '屋上土', '壁上土', '沙中土', '大驿土']
                }
                
                owner_wx = None
                day_wx = None
                
                for wx, names in nayin_wx_map.items():
                    if owner_nayin in names:
                        owner_wx = wx
                    if day_nayin in names:
                        day_wx = wx
                
                if owner_wx and day_wx:
                    # 纳音相同：加分
                    if owner_wx == day_wx:
                        adjustment += 6
                        print(f"  日主纳音({owner_nayin})与日课纳音({day_nayin})五行相同，加6分")
                    # 纳音相生：加分
                    elif WUXING_SHENG.get(owner_wx) == day_wx:
                        adjustment += 4
                        print(f"  日主纳音({owner_nayin})生日课纳音({day_nayin})，加4分")
        
        except Exception as e:
            print(f"  纳音匹配计算失败: {e}")
        
        return adjustment
    
    def _calculate_zhangsheng_score(self, bazi_info):
        """
        计算日主十二长生状态的评分
        
        Args:
            bazi_info: 事主八字信息
            
        Returns:
            int: 十二长生评分
        """
        score = 0
        zhangsheng = bazi_info.get('十二长生', {})
        
        # 检查日支的长生状态
        day_zhi_zhangsheng = zhangsheng.get('日支', '')
        
        # 帝旺、临官、冠带、长生：加分
        if day_zhi_zhangsheng in ['帝旺', '临官', '冠带', '长生']:
            score += 8
            print(f"  日主在日支为{day_zhi_zhangsheng}，加8分")
        # 衰、病、死、墓、绝：减分
        elif day_zhi_zhangsheng in ['衰', '病', '死', '墓', '绝']:
            score -= 6
            print(f"  日主在日支为{day_zhi_zhangsheng}，减6分")
        
        return score


# 使用示例
def demo_integration():
    """演示评分器与八字排盘模块的集成"""
    
    print("=== 评分器集成八字排盘模块演示 ===\n")
    
    # 模拟日课四柱
    day_sizhu = {
        '年柱': '甲辰', '月柱': '丙寅', '日柱': '戊戌', '时柱': '戊午',
        'year_gan': '甲', 'year_zhi': '辰',
        'month_gan': '丙', 'month_zhi': '寅',
        'day_gan': '戊', 'day_zhi': '戌',
        'hour_gan': '戊', 'hour_zhi': '午',
        'nayin': {
            '年柱': '覆灯火', '月柱': '炉中火',
            '日柱': '平地木', '时柱': '天上火'
        }
    }
    
    # 模拟事主信息
    owners = [{
        'name': '张三',
        'birth_year': 1990,
        'birth_month': 5,
        'birth_day': 15,
        'birth_hour': 10,
        'birth_minute': 30,
        'gender': '男'
    }]
    
    # 创建增强评分器
    scorer = EnhancedScorer()
    
    # 执行评分
    result = scorer.score_with_bazi_info(
        sizhu=day_sizhu,
        event_type='嫁娶',
        owners=owners
    )
    
    print(f"\n=== 评分结果 ===")
    print(f"基础分: {result['base_score']}")
    print(f"神煞列表: {len(result['shensha_list'])}个")
    print(f"宜事列表: {len(result['yi_list'])}个")
    print(f"忌事列表: {len(result['ji_list'])}个")


if __name__ == '__main__':
    demo_integration()
