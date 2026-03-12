# -*- coding: utf-8 -*-
"""
================================================================================
二十四山模块
================================================================================
提供二十四山相关的完整功能，包括：
- 二十四山基本信息（名称、类型、度数范围、五行属性）
- 分金计算（120分金、60分金）
- 五行生克关系判断
- 神煞与山的对应关系
- 择日中的山家吉凶判断
- 数据库支持（从数据库加载规则和基础数据）

使用方法:
    from modules.二十四山 import TwentyFourMountains, WuxingRelation
    
    # 获取二十四山信息
    mountains = TwentyFourMountains()
    shan = mountains.get_mountain_by_name('壬')
    
    # 判断五行生克
    relation = WuxingRelation.get_relation('金', '水')
    
    # 获取分金信息
    fengjin = mountains.get_fengjin('壬', 3)  # 获取壬山第3个分金
    
    # 使用数据库版本的选择器
    from modules.二十四山 import ZhengTiWuXingSelectorDB
    selector = ZhengTiWuXingSelectorDB(db_connection)
================================================================================
"""

import sys
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


class MountainType(Enum):
    """山类型枚举"""
    TIANGAN = '天干'  # 八干：甲乙丙丁庚辛壬癸
    DIZHI = '地支'    # 十二支：子丑寅卯辰巳午未申酉戌亥
    SIWEI = '四维'    # 四维：乾坤艮巽


class YinYang(Enum):
    """阴阳枚举"""
    YANG = '阳'
    YIN = '阴'


# 五行名称映射
WUXING_NAMES = {1: '金', 2: '木', 3: '水', 4: '火', 5: '土'}
WUXING_COLORS = {1: '白', 2: '绿', 3: '黑', 4: '红', 5: '黄'}


class WuxingRelation:
    """
    五行生克关系类
    
    提供五行之间的生克关系判断
    """
    # 名称映射
    NAME_TO_ID = {'金': 0, '木': 1, '水': 2, '火': 3, '土': 4}
    ID_TO_NAME = {0: '金', 1: '木', 2: '水', 3: '火', 4: '土'}
    
    # 生克关系：生成者 -> 被生者
    SHENG_MAP = {0: 2, 1: 3, 2: 1, 3: 4, 4: 0}  # 金生水，木生火，水生木，火生土，土生金
    KE_MAP = {0: 1, 1: 4, 4: 2, 2: 3, 3: 0}    # 金克木，木克土，土克水，水克火，火克金
    
    @classmethod
    def get_relation(cls, wuxing_a, wuxing_b) -> str:
        """
        判断五行a与五行b的关系
        
        Args:
            wuxing_a: 五行名称（如'金'）或ID
            wuxing_b: 五行名称或ID
            
        Returns:
            字符串描述：'相生(a生b)', '相生(b生a)', '相克(a克b)', '相克(b克a)', '比和'
        """
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        
        if a is None or b is None:
            return "未知五行"
        
        if a == b:
            return "比和"
        
        # 检查a生b
        if cls.SHENG_MAP.get(a) == b:
            return f"相生({cls.ID_TO_NAME[a]}生{cls.ID_TO_NAME[b]})"
        # 检查b生a
        if cls.SHENG_MAP.get(b) == a:
            return f"相生({cls.ID_TO_NAME[b]}生{cls.ID_TO_NAME[a]})"
        # 检查a克b
        if cls.KE_MAP.get(a) == b:
            return f"相克({cls.ID_TO_NAME[a]}克{cls.ID_TO_NAME[b]})"
        # 检查b克a
        if cls.KE_MAP.get(b) == a:
            return f"相克({cls.ID_TO_NAME[b]}克{cls.ID_TO_NAME[a]})"
        
        return "无直接生克"
    
    @classmethod
    def is_sheng(cls, wuxing_a, wuxing_b) -> bool:
        """判断a是否生b"""
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        return cls.SHENG_MAP.get(a) == b
    
    @classmethod
    def is_ke(cls, wuxing_a, wuxing_b) -> bool:
        """判断a是否克b"""
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        return cls.KE_MAP.get(a) == b
    
    @classmethod
    def is_bihe(cls, wuxing_a, wuxing_b) -> bool:
        """判断是否比和（相同）"""
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        return a == b
    
    @classmethod
    def get_relation_by_id(cls, a: int, b: int) -> str:
        """
        通过ID返回具体关系代码
        
        Args:
            a: 第一个五行ID（0-4）
            b: 第二个五行ID（0-4）
            
        Returns:
            关系代码：'a_sheng_b', 'b_sheng_a', 'a_ke_b', 'b_ke_a', 'equal', 'none'
        """
        if a == b:
            return 'equal'
        if cls.SHENG_MAP.get(a) == b:
            return 'a_sheng_b'
        if cls.SHENG_MAP.get(b) == a:
            return 'b_sheng_a'
        if cls.KE_MAP.get(a) == b:
            return 'a_ke_b'
        if cls.KE_MAP.get(b) == a:
            return 'b_ke_a'
        return 'none'
    
    @classmethod
    def get_relation_direction(cls, wuxing_a, wuxing_b, mountain_wx) -> str:
        """
        获取五行关系方向（针对坐山）
        
        Args:
            wuxing_a: 日课五行
            wuxing_b: 坐山五行
            mountain_wx: 坐山五行（与wuxing_b相同，用于明确语义）
            
        Returns:
            方向描述：'课生山', '山生课', '课克山', '山克课', '比和', 'none'
        """
        if isinstance(wuxing_a, str):
            a = cls.NAME_TO_ID.get(wuxing_a)
        else:
            a = wuxing_a
        if isinstance(wuxing_b, str):
            b = cls.NAME_TO_ID.get(wuxing_b)
        else:
            b = wuxing_b
        
        if a == b:
            return '比和'
        if cls.SHENG_MAP.get(a) == b:
            return '课生山'
        if cls.SHENG_MAP.get(b) == a:
            return '山生课'
        if cls.KE_MAP.get(a) == b:
            return '课克山'
        if cls.KE_MAP.get(b) == a:
            return '山克课'
        return 'none'


# 二十四山数据
TWENTY_FOUR_MOUNTAINS_DATA = [
    # id, 名称, 类型, 起始度数, 结束度数, 五行, 阴阳
    (1, '壬', MountainType.TIANGAN, 337.5, 352.5, '水', YinYang.YANG),
    (2, '子', MountainType.DIZHI, 352.5, 7.5, '水', YinYang.YANG),
    (3, '癸', MountainType.TIANGAN, 7.5, 22.5, '水', YinYang.YIN),
    (4, '丑', MountainType.DIZHI, 22.5, 37.5, '土', YinYang.YIN),
    (5, '艮', MountainType.SIWEI, 37.5, 52.5, '土', YinYang.YANG),
    (6, '寅', MountainType.DIZHI, 52.5, 67.5, '木', YinYang.YANG),
    (7, '甲', MountainType.TIANGAN, 67.5, 82.5, '木', YinYang.YANG),
    (8, '卯', MountainType.DIZHI, 82.5, 97.5, '木', YinYang.YIN),
    (9, '乙', MountainType.TIANGAN, 97.5, 112.5, '木', YinYang.YIN),
    (10, '辰', MountainType.DIZHI, 112.5, 127.5, '土', YinYang.YANG),
    (11, '巽', MountainType.SIWEI, 127.5, 142.5, '木', YinYang.YIN),
    (12, '巳', MountainType.DIZHI, 142.5, 157.5, '火', YinYang.YIN),
    (13, '丙', MountainType.TIANGAN, 157.5, 172.5, '火', YinYang.YANG),
    (14, '午', MountainType.DIZHI, 172.5, 187.5, '火', YinYang.YANG),
    (15, '丁', MountainType.TIANGAN, 187.5, 202.5, '火', YinYang.YIN),
    (16, '未', MountainType.DIZHI, 202.5, 217.5, '土', YinYang.YIN),
    (17, '坤', MountainType.SIWEI, 217.5, 232.5, '土', YinYang.YIN),
    (18, '申', MountainType.DIZHI, 232.5, 247.5, '金', YinYang.YANG),
    (19, '庚', MountainType.TIANGAN, 247.5, 262.5, '金', YinYang.YANG),
    (20, '酉', MountainType.DIZHI, 262.5, 277.5, '金', YinYang.YIN),
    (21, '辛', MountainType.TIANGAN, 277.5, 292.5, '金', YinYang.YIN),
    (22, '戌', MountainType.DIZHI, 292.5, 307.5, '土', YinYang.YANG),
    (23, '乾', MountainType.SIWEI, 307.5, 322.5, '金', YinYang.YANG),
    (24, '亥', MountainType.DIZHI, 322.5, 337.5, '水', YinYang.YIN),
]


class TwentyFourMountains:
    """
    二十四山类
    
    提供二十四山的完整功能，包括查询、分金计算等
    """
    
    def __init__(self):
        """初始化二十四山数据"""
        self.mountains = {}
        self._init_mountains()
        self._init_fengjin()
    
    def _init_mountains(self):
        """初始化山数据"""
        for data in TWENTY_FOUR_MOUNTAINS_DATA:
            mid, name, mtype, start_deg, end_deg, wuxing, yinyang = data
            self.mountains[name] = {
                'id': mid,
                'name': name,
                'type': mtype,
                'start_degree': start_deg,
                'end_degree': end_deg,
                'wuxing': wuxing,
                'yinyang': yinyang,
            }
    
    def _init_fengjin(self):
        """初始化120分金数据"""
        # 每个山分为5个分金，每个分金3度
        # 分金名称：如壬山分为癸丑、艮寅、甲卯、乙辰、巽巳
        self.fengjin_data = {}
        
        # 120分金的天干地支顺序
        tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 为每个山创建5个分金
        for data in TWENTY_FOUR_MOUNTAINS_DATA:
            mid, name, mtype, start_deg, end_deg, wuxing, yinyang = data
            self.fengjin_data[name] = []
            
            # 计算该山的5个分金
            for i in range(5):
                fj_start = start_deg + i * 3
                fj_end = fj_start + 3
                
                # 处理跨越0度的情况
                if fj_start >= 360:
                    fj_start -= 360
                if fj_end >= 360:
                    fj_end -= 360
                
                # 分金名称（简化处理，实际应根据具体规则）
                fj_name = f"{name}{i+1}分金"
                
                self.fengjin_data[name].append({
                    'index': i + 1,
                    'name': fj_name,
                    'start_degree': fj_start,
                    'end_degree': fj_end,
                    'width': 3.0,  # 每个分金3度
                })
    
    def get_mountain_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取山信息
        
        Args:
            name: 山名（如'壬'、'子'等）
            
        Returns:
            山信息字典，找不到返回None
        """
        return self.mountains.get(name)
    
    def get_mountain_by_degree(self, degree: float) -> Optional[Dict]:
        """
        根据度数获取山信息
        
        Args:
            degree: 度数（0-360）
            
        Returns:
            山信息字典，找不到返回None
        """
        # 标准化度数到0-360范围
        degree = degree % 360
        
        for name, data in self.mountains.items():
            start = data['start_degree']
            end = data['end_degree']
            
            # 处理跨越0度的情况
            if start > end:  # 如壬山：337.5-352.5，但子山是352.5-7.5
                if degree >= start or degree < end:
                    return data
            else:
                if start <= degree < end:
                    return data
        
        return None
    
    def get_all_mountains(self) -> List[Dict]:
        """
        获取所有山信息
        
        Returns:
            山信息列表
        """
        return list(self.mountains.values())
    
    def get_mountains_by_type(self, mtype: MountainType) -> List[Dict]:
        """
        根据类型获取山
        
        Args:
            mtype: 山类型
            
        Returns:
            山信息列表
        """
        return [m for m in self.mountains.values() if m['type'] == mtype]
    
    def get_mountains_by_wuxing(self, wuxing: str) -> List[Dict]:
        """
        根据五行获取山
        
        Args:
            wuxing: 五行名称（金、木、水、火、土）
            
        Returns:
            山信息列表
        """
        return [m for m in self.mountains.values() if m['wuxing'] == wuxing]
    
    def get_fengjin(self, mountain_name: str, index: int) -> Optional[Dict]:
        """
        获取指定山的分金信息
        
        Args:
            mountain_name: 山名
            index: 分金序号（1-5）
            
        Returns:
            分金信息字典，找不到返回None
        """
        if mountain_name not in self.fengjin_data:
            return None
        
        fengjin_list = self.fengjin_data[mountain_name]
        if index < 1 or index > len(fengjin_list):
            return None
        
        return fengjin_list[index - 1]
    
    def get_all_fengjin(self, mountain_name: str) -> List[Dict]:
        """
        获取指定山的所有分金
        
        Args:
            mountain_name: 山名
            
        Returns:
            分金信息列表
        """
        return self.fengjin_data.get(mountain_name, [])
    
    def get_fengjin_by_degree(self, degree: float) -> Optional[Tuple[str, Dict]]:
        """
        根据度数获取分金信息
        
        Args:
            degree: 度数（0-360）
            
        Returns:
            (山名, 分金信息)元组，找不到返回None
        """
        mountain = self.get_mountain_by_degree(degree)
        if not mountain:
            return None
        
        # 计算在该山内的相对位置
        start_deg = mountain['start_degree']
        relative_deg = (degree - start_deg) % 360
        
        # 确定分金序号（每个分金3度）
        index = int(relative_deg / 3) + 1
        if index > 5:
            index = 5
        
        fengjin = self.get_fengjin(mountain['name'], index)
        if fengjin:
            return (mountain['name'], fengjin)
        
        return None
    
    def check_wuxing_relation(self, mountain_name: str, wuxing: str) -> str:
        """
        检查山五行与指定五行的关系
        
        Args:
            mountain_name: 山名
            wuxing: 五行名称
            
        Returns:
            关系描述字符串
        """
        mountain = self.get_mountain_by_name(mountain_name)
        if not mountain:
            return "未知山"
        
        return WuxingRelation.get_relation(mountain['wuxing'], wuxing)


# 常用神煞与山的对应规则
SHENSHA_MOUNTAIN_RULES = {
    '三煞': {
        'description': '申子辰年煞在南方巳午未，寅午戌年煞在北方亥子丑，巳酉丑年煞在东方寅卯辰，亥卯未年煞在西方申酉戌',
        'rules': [
            {'condition_type': '年', 'condition_value': ['申', '子', '辰'], 'avoid_mountains': ['巳', '午', '未']},
            {'condition_type': '年', 'condition_value': ['寅', '午', '戌'], 'avoid_mountains': ['亥', '子', '丑']},
            {'condition_type': '年', 'condition_value': ['巳', '酉', '丑'], 'avoid_mountains': ['寅', '卯', '辰']},
            {'condition_type': '年', 'condition_value': ['亥', '卯', '未'], 'avoid_mountains': ['申', '酉', '戌']},
        ]
    },
    '岁破': {
        'description': '岁破在年支对冲方位',
        'rules': [
            {'condition_type': '年', 'condition_value': ['子'], 'avoid_mountains': ['午']},
            {'condition_type': '年', 'condition_value': ['丑'], 'avoid_mountains': ['未']},
            {'condition_type': '年', 'condition_value': ['寅'], 'avoid_mountains': ['申']},
            {'condition_type': '年', 'condition_value': ['卯'], 'avoid_mountains': ['酉']},
            {'condition_type': '年', 'condition_value': ['辰'], 'avoid_mountains': ['戌']},
            {'condition_type': '年', 'condition_value': ['巳'], 'avoid_mountains': ['亥']},
            {'condition_type': '年', 'condition_value': ['午'], 'avoid_mountains': ['子']},
            {'condition_type': '年', 'condition_value': ['未'], 'avoid_mountains': ['丑']},
            {'condition_type': '年', 'condition_value': ['申'], 'avoid_mountains': ['寅']},
            {'condition_type': '年', 'condition_value': ['酉'], 'avoid_mountains': ['卯']},
            {'condition_type': '年', 'condition_value': ['戌'], 'avoid_mountains': ['辰']},
            {'condition_type': '年', 'condition_value': ['亥'], 'avoid_mountains': ['巳']},
        ]
    },
}


class MountainShenshaChecker:
    """
    山家神煞检查器
    
    检查特定年份、月份等条件下，哪些山家有神煞影响
    """
    
    def __init__(self):
        self.mountains = TwentyFourMountains()
    
    def check_san_sha(self, year_zhi: str) -> List[str]:
        """
        检查三煞
        
        Args:
            year_zhi: 年支（如'申'、'子'等）
            
        Returns:
            需要避开的山列表
        """
        rules = SHENSHA_MOUNTAIN_RULES['三煞']['rules']
        for rule in rules:
            if year_zhi in rule['condition_value']:
                return rule['avoid_mountains']
        return []
    
    def check_sui_po(self, year_zhi: str) -> List[str]:
        """
        检查岁破
        
        Args:
            year_zhi: 年支
            
        Returns:
            需要避开的山列表
        """
        rules = SHENSHA_MOUNTAIN_RULES['岁破']['rules']
        for rule in rules:
            if year_zhi in rule['condition_value']:
                return rule['avoid_mountains']
        return []
    
    def check_mountain_jixiong(self, mountain_name: str, year_zhi: str, 
                               month_zhi: str = None, day_zhi: str = None) -> Dict:
        """
        综合检查山家吉凶
        
        Args:
            mountain_name: 山名
            year_zhi: 年支
            month_zhi: 月支（可选）
            day_zhi: 日支（可选）
            
        Returns:
            吉凶判断结果
        """
        result = {
            'mountain': mountain_name,
            'is_good': True,
            'shensha': [],
            'warnings': [],
        }
        
        # 检查三煞
        san_sha_mountains = self.check_san_sha(year_zhi)
        if mountain_name in san_sha_mountains:
            result['is_good'] = False
            result['shensha'].append('三煞')
            result['warnings'].append(f'{year_zhi}年三煞在{san_sha_mountains}，忌{mountain_name}山')
        
        # 检查岁破
        sui_po_mountains = self.check_sui_po(year_zhi)
        if mountain_name in sui_po_mountains:
            result['is_good'] = False
            result['shensha'].append('岁破')
            result['warnings'].append(f'{year_zhi}年岁破在{sui_po_mountains}，忌{mountain_name}山')
        
        return result


# 便捷函数
def get_mountain_info(name: str) -> Optional[Dict]:
    """获取山信息"""
    mountains = TwentyFourMountains()
    return mountains.get_mountain_by_name(name)


def check_wuxing_relation(wuxing_a: str, wuxing_b: str) -> str:
    """检查五行关系"""
    return WuxingRelation.get_relation(wuxing_a, wuxing_b)


def get_fengjin(mountain_name: str, index: int) -> Optional[Dict]:
    """获取分金信息"""
    mountains = TwentyFourMountains()
    return mountains.get_fengjin(mountain_name, index)


# ============================================================================
# 数据库表结构定义（SQL）
# ============================================================================

"""
-- 五行字典表
CREATE TABLE wuxing (
    id INT PRIMARY KEY,
    name VARCHAR(10) NOT NULL,  -- 金、木、水、火、土
    color VARCHAR(10)           -- 白、绿、黑、红、黄
);
INSERT INTO wuxing VALUES 
    (1, '金', '白'), 
    (2, '木', '绿'), 
    (3, '水', '黑'), 
    (4, '火', '红'), 
    (5, '土', '黄');

-- 五行生克权重表
CREATE TABLE wuxing_relation_score (
    id INT PRIMARY KEY AUTO_INCREMENT,
    relation_type ENUM('生', '克', '比和') NOT NULL,
    direction ENUM('课生山', '山生课', '课克山', '山克课', '比和') NOT NULL,
    weight INT NOT NULL,           -- 权重（正为吉，负为凶）
    description VARCHAR(255),      -- 描述
    priority INT DEFAULT 1         -- 优先级
);
INSERT INTO wuxing_relation_score (relation_type, direction, weight, description, priority) VALUES
    ('生', '课生山', 10, '日课五行生扶坐山', 1),
    ('生', '山生课', 5, '坐山生日课（泄气）', 2),
    ('克', '课克山', -10, '日课克制坐山', 1),
    ('克', '山克课', -5, '坐山克日课（耗气）', 2),
    ('比和', '比和', 8, '五行相同', 1);

-- 神煞规则表（支持JSON条件）
CREATE TABLE shensha_rule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    shensha_name VARCHAR(50) NOT NULL,      -- 神煞名称
    condition_json JSON NOT NULL,           -- 条件表达式
    weight INT NOT NULL,                    -- 权重（负值表示凶）
    is_decisive BOOLEAN DEFAULT FALSE,      -- 是否为决定性煞
    description TEXT                        -- 详细描述
);
-- 三煞规则示例
INSERT INTO shensha_rule (shensha_name, condition_json, weight, is_decisive, description) VALUES
    ('三煞', '{"rules": [
        {"year_zhi": ["申", "子", "辰"], "mountain_id": [12, 13, 14]},
        {"year_zhi": ["寅", "午", "戌"], "mountain_id": [24, 1, 2]},
        {"year_zhi": ["巳", "酉", "丑"], "mountain_id": [6, 7, 8]},
        {"year_zhi": ["亥", "卯", "未"], "mountain_id": [18, 19, 20]}
    ]}', -100, TRUE, '申子辰年煞在南方巳午未，寅午戌年煞在北方亥子丑，巳酉丑年煞在东方寅卯辰，亥卯未年煞在西方申酉戌');

-- 坐山五行映射表
CREATE TABLE mountain_wuxing (
    mountain_id INT PRIMARY KEY,
    wuxing_id INT NOT NULL,
    FOREIGN KEY (mountain_id) REFERENCES twenty_four_mountains(id),
    FOREIGN KEY (wuxing_id) REFERENCES wuxing(id)
);

-- ============================================================================
-- 龙相关表结构（补龙扶山扩展）
-- ============================================================================

-- 方案1：龙直接用二十四山表示（推荐）
-- 如果来龙方位明确属于二十四山之一，则无需新增表，直接使用现有的 mountain_wuxing 表即可
-- 调用时传入龙的 mountain_id，通过 get_mountain_wuxing() 获取五行

-- 方案2：龙有独立的标识体系
-- 若龙需独立命名（如"紫微龙""天市龙"等），则新建表 long_wuxing
CREATE TABLE long_wuxing (
    long_id INT PRIMARY KEY,
    long_name VARCHAR(20) NOT NULL,     -- 龙名称（如"紫微龙"）
    wuxing_id INT NOT NULL,             -- 五行ID，外键关联 wuxing(id)
    mountain_id INT,                    -- 关联的二十四山ID（可选）
    description TEXT                    -- 描述
);

-- 龙五行示例数据
INSERT INTO long_wuxing (long_id, long_name, wuxing_id, mountain_id, description) VALUES
    (1, '壬龙', 3, 1, '壬山来龙，五行属水'),
    (2, '子龙', 3, 2, '子山来龙，五行属水'),
    (3, '癸龙', 3, 3, '癸山来龙，五行属水'),
    (4, '丑龙', 5, 4, '丑山来龙，五行属土'),
    (5, '寅龙', 2, 5, '寅山来龙，五行属木'),
    (6, '卯龙', 2, 6, '卯山来龙，五行属木'),
    (7, '辰龙', 5, 7, '辰山来龙，五行属土'),
    (8, '巳龙', 4, 8, '巳山来龙，五行属火'),
    (9, '午龙', 4, 9, '午山来龙，五行属火'),
    (10, '未龙', 5, 10, '未山来龙，五行属土'),
    (11, '申龙', 1, 11, '申山来龙，五行属金'),
    (12, '酉龙', 1, 12, '酉山来龙，五行属金'),
    (13, '戌龙', 5, 13, '戌山来龙，五行属土'),
    (14, '亥龙', 3, 14, '亥山来龙，五行属水'),
    (15, '艮龙', 5, 15, '艮山来龙，五行属土'),
    (16, '乾龙', 1, 16, '乾山来龙，五行属金'),
    (17, '坤龙', 5, 17, '坤山来龙，五行属土'),
    (18, '巽龙', 2, 18, '巽山来龙，五行属木');

-- 扩展神煞规则表，增加龙相关规则
-- 在 shensha_rule 表中可增加 long_id 字段，定义与龙相关的神煞规则
ALTER TABLE shensha_rule ADD COLUMN target_type ENUM('山', '龙', '山龙') DEFAULT '山';
ALTER TABLE shensha_rule ADD COLUMN long_id INT;

-- 龙相关神煞规则示例
INSERT INTO shensha_rule (shensha_name, condition_json, weight, is_decisive, target_type, description) VALUES
    ('龙犯三煞', '{"rules": [
        {"year_zhi": ["申", "子", "辰"], "long_mountain_id": [8, 9, 10]},
        {"year_zhi": ["寅", "午", "戌"], "long_mountain_id": [14, 2, 3]},
        {"year_zhi": ["巳", "酉", "丑"], "long_mountain_id": [5, 6, 7]},
        {"year_zhi": ["亥", "卯", "未"], "long_mountain_id": [11, 12, 13]}
    ]}', -100, TRUE, '龙', '来龙犯三煞，大凶');

-- 扩展五行生克权重表，支持龙
ALTER TABLE wuxing_relation_score ADD COLUMN target_type ENUM('山', '龙', '通用') DEFAULT '通用';

-- 龙专用权重（可选，若与山不同）
INSERT INTO wuxing_relation_score (relation_type, direction, weight, description, priority, target_type) VALUES
    ('生', '课生龙', 12, '日课五行生扶来龙（补龙）', 1, '龙'),
    ('生', '龙生课', 4, '来龙生日课（泄气）', 2, '龙'),
    ('克', '课克龙', -12, '日课克制来龙', 1, '龙'),
    ('克', '龙克课', -4, '来龙克日课', 2, '龙'),
    ('比和', '比和', 10, '五行相同', 1, '龙');

-- ============================================================================
-- 龙上八煞规则
-- ============================================================================
-- 龙上八煞：坎龙坤兔震山猴，巽鸡乾马兑蛇头，艮虎离猪为煞曜，宅墓逢之一时休
-- 解释：
-- 坎龙：坎卦（子山）忌辰龙（辰为龙）
-- 坤兔：坤卦（坤山）忌卯兔（卯为兔）
-- 震山猴：震卦（卯山）忌申猴（申为猴）
-- 巽鸡：巽卦（巽山）忌酉鸡（酉为鸡）
-- 乾马：乾卦（乾山）忌午马（午为马）
-- 兑蛇头：兑卦（酉山）忌巳蛇（巳为蛇）
-- 艮虎：艮卦（艮山）忌寅虎（寅为虎）
-- 离猪：离卦（午山）忌亥猪（亥为猪）

INSERT INTO shensha_rule (shensha_name, condition_json, weight, is_decisive, target_type, description) VALUES
    ('龙上八煞-坎龙', '{"long_mountain_id": [2], "avoid_zhi": ["辰"]}', -80, TRUE, '龙', '坎龙忌辰，来龙在子山忌见辰支'),
    ('龙上八煞-坤兔', '{"long_mountain_id": [17], "avoid_zhi": ["卯"]}', -80, TRUE, '龙', '坤兔忌卯，来龙在坤山忌见卯支'),
    ('龙上八煞-震山猴', '{"long_mountain_id": [6], "avoid_zhi": ["申"]}', -80, TRUE, '龙', '震山猴忌申，来龙在卯山忌见申支'),
    ('龙上八煞-巽鸡', '{"long_mountain_id": [18], "avoid_zhi": ["酉"]}', -80, TRUE, '龙', '巽鸡忌酉，来龙在巽山忌见酉支'),
    ('龙上八煞-乾马', '{"long_mountain_id": [16], "avoid_zhi": ["午"]}', -80, TRUE, '龙', '乾马忌午，来龙在乾山忌见午支'),
    ('龙上八煞-兑蛇头', '{"long_mountain_id": [12], "avoid_zhi": ["巳"]}', -80, TRUE, '龙', '兑蛇头忌巳，来龙在酉山忌见巳支'),
    ('龙上八煞-艮虎', '{"long_mountain_id": [15], "avoid_zhi": ["寅"]}', -80, TRUE, '龙', '艮虎忌寅，来龙在艮山忌见寅支'),
    ('龙上八煞-离猪', '{"long_mountain_id": [9], "avoid_zhi": ["亥"]}', -80, TRUE, '龙', '离猪忌亥，来龙在午山忌见亥支');
"""

# ============================================================================
# 正体五行择日核心算法
# ============================================================================

# 五行生克规则表（硬编码，实际可从数据库读取）
WUXING_SHENGKE_RULES = [
    {'rule_name': '日课生坐山', 'relation': '生', 'direction': '课生山', 'weight': 10, 'priority': 1},
    {'rule_name': '坐山生日课', 'relation': '生', 'direction': '山生课', 'weight': 5, 'priority': 2},
    {'rule_name': '日课克坐山', 'relation': '克', 'direction': '课克山', 'weight': -10, 'priority': 1},
    {'rule_name': '坐山克日课', 'relation': '克', 'direction': '山克课', 'weight': -5, 'priority': 2},
    {'rule_name': '比和', 'relation': '比和', 'direction': '比和', 'weight': 8, 'priority': 1},
]

# 天干五行（正体五行）
TIANGAN_WUXING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 地支五行（正体五行）
DIZHI_WUXING = {
    '寅': '木', '卯': '木',
    '巳': '火', '午': '火',
    '申': '金', '酉': '金',
    '亥': '水', '子': '水',
    '辰': '土', '戌': '土', '丑': '土', '未': '土',
}

# ============================================================================
# 六十甲子纳音五行（用于分金五行）
# ============================================================================

NAYIN_WUXING = {
    # 甲子、乙丑 - 海中金
    '甲子': '金', '乙丑': '金',
    # 丙寅、丁卯 - 炉中火
    '丙寅': '火', '丁卯': '火',
    # 戊辰、己巳 - 大林木
    '戊辰': '木', '己巳': '木',
    # 庚午、辛未 - 路旁土
    '庚午': '土', '辛未': '土',
    # 壬申、癸酉 - 剑锋金
    '壬申': '金', '癸酉': '金',
    # 甲戌、乙亥 - 山头火
    '甲戌': '火', '乙亥': '火',
    # 丙子、丁丑 - 涧下水
    '丙子': '水', '丁丑': '水',
    # 戊寅、己卯 - 城头土
    '戊寅': '土', '己卯': '土',
    # 庚辰、辛巳 - 白蜡金
    '庚辰': '金', '辛巳': '金',
    # 壬午、癸未 - 杨柳木
    '壬午': '木', '癸未': '木',
    # 甲申、乙酉 - 泉中水
    '甲申': '水', '乙酉': '水',
    # 丙戌、丁亥 - 屋上土
    '丙戌': '土', '丁亥': '土',
    # 戊子、己丑 - 霹雳火
    '戊子': '火', '己丑': '火',
    # 庚寅、辛卯 - 松柏木
    '庚寅': '木', '辛卯': '木',
    # 壬辰、癸巳 - 长流水
    '壬辰': '水', '癸巳': '水',
    # 甲午、乙未 - 沙中金
    '甲午': '金', '乙未': '金',
    # 丙申、丁酉 - 山下火
    '丙申': '火', '丁酉': '火',
    # 戊戌、己亥 - 平地木
    '戊戌': '木', '己亥': '木',
    # 庚子、辛丑 - 壁上土
    '庚子': '土', '辛丑': '土',
    # 壬寅、癸卯 - 金箔金
    '壬寅': '金', '癸卯': '金',
    # 甲辰、乙巳 - 覆灯火
    '甲辰': '火', '乙巳': '火',
    # 丙午、丁未 - 天河水
    '丙午': '水', '丁未': '水',
    # 戊申、己酉 - 大驿土
    '戊申': '土', '己酉': '土',
    # 庚戌、辛亥 - 钗钏金
    '庚戌': '金', '辛亥': '金',
    # 壬子、癸丑 - 桑柘木
    '壬子': '木', '癸丑': '木',
    # 甲寅、乙卯 - 大溪水
    '甲寅': '水', '乙卯': '水',
    # 丙辰、丁巳 - 沙中土
    '丙辰': '土', '丁巳': '土',
    # 戊午、己未 - 天上火
    '戊午': '火', '己未': '火',
    # 庚申、辛酉 - 石榴木
    '庚申': '木', '辛酉': '木',
    # 壬戌、癸亥 - 大海水
    '壬戌': '水', '癸亥': '水',
}

# 纳音五行详细名称
NAYIN_NAMES = {
    '甲子': '海中金', '乙丑': '海中金',
    '丙寅': '炉中火', '丁卯': '炉中火',
    '戊辰': '大林木', '己巳': '大林木',
    '庚午': '路旁土', '辛未': '路旁土',
    '壬申': '剑锋金', '癸酉': '剑锋金',
    '甲戌': '山头火', '乙亥': '山头火',
    '丙子': '涧下水', '丁丑': '涧下水',
    '戊寅': '城头土', '己卯': '城头土',
    '庚辰': '白蜡金', '辛巳': '白蜡金',
    '壬午': '杨柳木', '癸未': '杨柳木',
    '甲申': '泉中水', '乙酉': '泉中水',
    '丙戌': '屋上土', '丁亥': '屋上土',
    '戊子': '霹雳火', '己丑': '霹雳火',
    '庚寅': '松柏木', '辛卯': '松柏木',
    '壬辰': '长流水', '癸巳': '长流水',
    '甲午': '沙中金', '乙未': '沙中金',
    '丙申': '山下火', '丁酉': '山下火',
    '戊戌': '平地木', '己亥': '平地木',
    '庚子': '壁上土', '辛丑': '壁上土',
    '壬寅': '金箔金', '癸卯': '金箔金',
    '甲辰': '覆灯火', '乙巳': '覆灯火',
    '丙午': '天河水', '丁未': '天河水',
    '戊申': '大驿土', '己酉': '大驿土',
    '庚戌': '钗钏金', '辛亥': '钗钏金',
    '壬子': '桑柘木', '癸丑': '桑柘木',
    '甲寅': '大溪水', '乙卯': '大溪水',
    '丙辰': '沙中土', '丁巳': '沙中土',
    '戊午': '天上火', '己未': '天上火',
    '庚申': '石榴木', '辛酉': '石榴木',
    '壬戌': '大海水', '癸亥': '大海水',
}

# ============================================================================
# 一百二十分金数据（每山5个分金，共120分金）
# ============================================================================

# 二十四山对应的分金干支（按顺序：第1-5分金）
# 规则：阳山用阳干支，阴山用阴干支
FENGJIN_GANZHI = {
    # 八干四维的分金（使用六十甲子顺序）
    '壬': ['丙子', '丁丑', '戊寅', '己卯', '庚辰'],  # 壬山属阳水
    '子': ['甲子', '丙子', '戊子', '庚子', '壬子'],  # 子山属阳水
    '癸': ['丙子', '丁丑', '戊寅', '己卯', '庚辰'],  # 癸山属阴水
    '丑': ['丁丑', '己丑', '辛丑', '癸丑', '乙丑'],  # 丑山属阴土
    '艮': ['丙寅', '丁卯', '戊辰', '己巳', '庚午'],  # 艮山属阳土
    '寅': ['甲寅', '丙寅', '戊寅', '庚寅', '壬寅'],  # 寅山属阳木
    '甲': ['丙寅', '丁卯', '戊辰', '己巳', '庚午'],  # 甲山属阳木
    '卯': ['乙卯', '丁卯', '己卯', '辛卯', '癸卯'],  # 卯山属阴木
    '乙': ['丙寅', '丁卯', '戊辰', '己巳', '庚午'],  # 乙山属阴木
    '辰': ['甲辰', '丙辰', '戊辰', '庚辰', '壬辰'],  # 辰山属阳土
    '巽': ['丙辰', '丁巳', '戊午', '己未', '庚申'],  # 巽山属阴木
    '巳': ['乙巳', '丁巳', '己巳', '辛巳', '癸巳'],  # 巳山属阴火
    '丙': ['丙午', '丁未', '戊申', '己酉', '庚戌'],  # 丙山属阳火
    '午': ['甲午', '丙午', '戊午', '庚午', '壬午'],  # 午山属阳火
    '丁': ['丙午', '丁未', '戊申', '己酉', '庚戌'],  # 丁山属阴火
    '未': ['乙未', '丁未', '己未', '辛未', '癸未'],  # 未山属阴土
    '坤': ['丙申', '丁酉', '戊戌', '己亥', '庚子'],  # 坤山属阴土
    '申': ['甲申', '丙申', '戊申', '庚申', '壬申'],  # 申山属阳金
    '庚': ['丙申', '丁酉', '戊戌', '己亥', '庚子'],  # 庚山属阳金
    '酉': ['乙酉', '丁酉', '己酉', '辛酉', '癸酉'],  # 酉山属阴金
    '辛': ['丙申', '丁酉', '戊戌', '己亥', '庚子'],  # 辛山属阴金
    '戌': ['甲戌', '丙戌', '戊戌', '庚戌', '壬戌'],  # 戌山属阳土
    '乾': ['丙戌', '丁亥', '戊子', '己丑', '庚寅'],  # 乾山属阳金
    '亥': ['乙亥', '丁亥', '己亥', '辛亥', '癸亥'],  # 亥山属阴水
}


def get_fengjin_wuxing(mountain_name: str, fengjin_index: int) -> Tuple[str, str]:
    """
    获取分金的纳音五行
    
    Args:
        mountain_name: 山名，如"子"
        fengjin_index: 分金索引（0-4），0=第1分金，4=第5分金
        
    Returns:
        (五行, 纳音名称)，如('金', '海中金')
    """
    if mountain_name not in FENGJIN_GANZHI:
        return '土', '未知'
    
    ganzhi_list = FENGJIN_GANZHI[mountain_name]
    if fengjin_index < 0 or fengjin_index >= len(ganzhi_list):
        return '土', '未知'
    
    ganzhi = ganzhi_list[fengjin_index]
    wuxing = NAYIN_WUXING.get(ganzhi, '土')
    nayin_name = NAYIN_NAMES.get(ganzhi, '未知')
    
    return wuxing, nayin_name


def get_fengjin_by_jianxiang(mountain_name: str, jianxiang: str) -> int:
    """
    根据兼向获取分金索引
    
    Args:
        mountain_name: 山名
        jianxiang: 兼向，如"兼壬"、"正中"、"兼癸"
        
    Returns:
        分金索引（0-4）
    """
    if not jianxiang or jianxiang == "正中":
        return 2  # 第3分金（正中）
    elif "兼" in jianxiang:
        # 兼左=第1分金(0)，兼右=第5分金(4)
        # 需要根据具体兼向判断是左还是右
        from modules.电子罗盘 import CompassConverter
        converter = CompassConverter()
        mountains = converter.get_all_mountains()
        
        if mountain_name in mountains:
            idx = mountains.index(mountain_name)
            left_shan = mountains[(idx - 1) % len(mountains)]
            right_shan = mountains[(idx + 1) % len(mountains)]
            
            jian_shan = jianxiang.replace("兼", "")
            if jian_shan == left_shan:
                return 0  # 兼左=第1分金
            elif jian_shan == right_shan:
                return 4  # 兼右=第5分金
    
    return 2  # 默认正中


# ============================================================================
# 山向映射工具（与主程序统一）
# ============================================================================

# 主程序使用的12山向（地支山向）
SHAN_XIANG_12 = [
    "子山午向", "丑山未向", "寅山申向", "卯山酉向",
    "辰山戌向", "巳山亥向", "午山子向", "未山丑向",
    "申山寅向", "酉山卯向", "戌山辰向", "亥山巳向"
]

# 山向到坐山名称的映射
SHAN_XIANG_TO_SHAN = {
    "子山午向": "子",
    "丑山未向": "丑",
    "寅山申向": "寅",
    "卯山酉向": "卯",
    "辰山戌向": "辰",
    "巳山亥向": "巳",
    "午山子向": "午",
    "未山丑向": "未",
    "申山寅向": "申",
    "酉山卯向": "酉",
    "戌山辰向": "戌",
    "亥山巳向": "亥",
}

# 坐山名称到山向的映射（默认向）
SHAN_TO_SHAN_XIANG = {
    "子": "子山午向",
    "丑": "丑山未向",
    "寅": "寅山申向",
    "卯": "卯山酉向",
    "辰": "辰山戌向",
    "巳": "巳山亥向",
    "午": "午山子向",
    "未": "未山丑向",
    "申": "申山寅向",
    "酉": "酉山卯向",
    "戌": "戌山辰向",
    "亥": "亥山巳向",
}

# 完整的二十四山列表（与主程序兼容）
SHAN_XIANG_24 = [
    # 十二地支山向（主程序已有）
    "子山午向", "丑山未向", "寅山申向", "卯山酉向",
    "辰山戌向", "巳山亥向", "午山子向", "未山丑向",
    "申山寅向", "酉山卯向", "戌山辰向", "亥山巳向",
    # 八干四维山向（扩展）
    "壬山丙向", "癸山丁向",
    "甲山庚向", "乙山辛向",
    "丙山壬向", "丁山癸向",
    "庚山甲向", "辛山乙向",
    "乾山巽向", "坤山艮向",
    "艮山坤向", "巽山乾向",
]

# 完整的山向到坐山映射
SHAN_XIANG_24_TO_SHAN = {
    # 十二地支山向
    "子山午向": "子", "丑山未向": "丑", "寅山申向": "寅", "卯山酉向": "卯",
    "辰山戌向": "辰", "巳山亥向": "巳", "午山子向": "午", "未山丑向": "未",
    "申山寅向": "申", "酉山卯向": "酉", "戌山辰向": "戌", "亥山巳向": "亥",
    # 八干四维山向
    "壬山丙向": "壬", "癸山丁向": "癸",
    "甲山庚向": "甲", "乙山辛向": "乙",
    "丙山壬向": "丙", "丁山癸向": "丁",
    "庚山甲向": "庚", "辛山乙向": "辛",
    "乾山巽向": "乾", "坤山艮向": "坤",
    "艮山坤向": "艮", "巽山乾向": "巽",
}


def shan_xiang_to_shan(shan_xiang: str) -> str:
    """
    将山向转换为坐山名称
    
    Args:
        shan_xiang: 山向，如"子山午向"
        
    Returns:
        坐山名称，如"子"
    """
    return SHAN_XIANG_24_TO_SHAN.get(shan_xiang, shan_xiang)


def shan_to_shan_xiang(shan: str, xiang: str = None) -> str:
    """
    将坐山名称转换为山向
    
    Args:
        shan: 坐山名称，如"子"
        xiang: 向山名称（可选），如"午"
        
    Returns:
        山向，如"子山午向"
    """
    if xiang:
        return f"{shan}山{xiang}向"
    return SHAN_TO_SHAN_XIANG.get(shan, f"{shan}山")


def get_shan_xiang_list(use_24_shan: bool = True) -> List[str]:
    """
    获取山向列表
    
    Args:
        use_24_shan: 是否使用完整的二十四山（True）或仅十二地支山（False）
        
    Returns:
        山向列表
    """
    if use_24_shan:
        return SHAN_XIANG_24.copy()
    return SHAN_XIANG_12.copy()


class ZhengTiWuXingSelector:
    """
    正体五行择日选择器
    
    实现正体五行择日的核心算法，包括：
    - 坐山与日课四柱的五行生克关系计算
    - 神煞检查（三煞、岁破等）
    - 综合评分和吉凶判断
    - 支持从配置或数据库动态读取规则
    """
    
    def __init__(self, rules_config: List[Dict] = None, use_default_rules: bool = True):
        """
        初始化选择器
        
        Args:
            rules_config: 自定义规则配置列表，格式同WUXING_SHENGKE_RULES
            use_default_rules: 是否使用默认规则（当rules_config为None时）
        """
        self.mountains = TwentyFourMountains()
        self.shensha_checker = MountainShenshaChecker()
        
        # 加载规则
        if rules_config:
            self.rules = rules_config
        elif use_default_rules:
            self.rules = WUXING_SHENGKE_RULES
        else:
            self.rules = []
        
        # 构建规则查找字典（direction -> weight）
        self._build_rule_dict()
        
        # 评分阈值
        self.score_thresholds = {
            '大吉': 50,
            '吉': 30,
            '平': 0,
            '凶': -30,
        }
    
    def _build_rule_dict(self):
        """构建规则查找字典"""
        self.rule_dict = {}
        for rule in self.rules:
            direction = rule.get('direction')
            if direction:
                self.rule_dict[direction] = rule.get('weight', 0)
    
    def load_rules_from_dict(self, rules: List[Dict]):
        """
        从字典加载规则
        
        Args:
            rules: 规则列表，每个规则包含direction和weight
        """
        self.rules = rules
        self._build_rule_dict()
    
    def get_rule_weight(self, direction: str) -> int:
        """
        获取指定方向的规则权重
        
        Args:
            direction: 方向（'课生山', '山生课', '课克山', '山克课', '比和'）
            
        Returns:
            权重值，找不到返回0
        """
        return self.rule_dict.get(direction, 0)
    
    def calculate_relation_score_with_rules(self, mountain_wx: str, ganzhi_wx: str) -> Tuple[int, str]:
        """
        使用配置的规则计算得分
        
        Args:
            mountain_wx: 坐山五行
            ganzhi_wx: 干支五行
            
        Returns:
            (得分, 关系方向)
        """
        if not mountain_wx or not ganzhi_wx:
            return 0, 'none'
        
        # 获取关系方向
        direction = WuxingRelation.get_relation_direction(ganzhi_wx, mountain_wx, mountain_wx)
        
        # 从规则中获取权重
        weight = self.get_rule_weight(direction)
        
        return weight, direction
    
    def get_ganzhi_wuxing(self, gan: str, zhi: str) -> Tuple[str, str]:
        """
        获取天干和地支的五行
        
        Args:
            gan: 天干
            zhi: 地支
            
        Returns:
            (天干五行, 地支五行)
        """
        gan_wx = TIANGAN_WUXING.get(gan)
        zhi_wx = DIZHI_WUXING.get(zhi)
        return gan_wx, zhi_wx
    
    def calculate_relation_score(self, mountain_wx: str, ganzhi_wx: str) -> int:
        """
        计算单个五行与坐山五行的关系得分
        
        Args:
            mountain_wx: 坐山五行
            ganzhi_wx: 干支五行
            
        Returns:
            得分
        """
        if not mountain_wx or not ganzhi_wx:
            return 0
        
        # 比和
        if mountain_wx == ganzhi_wx:
            return 8
        
        # 检查生克关系
        # 干支生坐山（课生山）
        if WuxingRelation.is_sheng(ganzhi_wx, mountain_wx):
            return 10
        
        # 坐山生干支（山生课）
        if WuxingRelation.is_sheng(mountain_wx, ganzhi_wx):
            return 5
        
        # 干支克坐山（课克山）- 大凶
        if WuxingRelation.is_ke(ganzhi_wx, mountain_wx):
            return -10
        
        # 坐山克干支（山克课）
        if WuxingRelation.is_ke(mountain_wx, ganzhi_wx):
            return -5
        
        return 0
    
    def evaluate_sizhu(self, mountain_name: str, 
                       year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> Dict:
        """
        综合评价四柱与坐山的关系
        
        Args:
            mountain_name: 坐山名称（如'壬'）
            year_gz: 年柱（如'甲子'）
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            
        Returns:
            评价结果字典
        """
        # 获取坐山信息
        mountain = self.mountains.get_mountain_by_name(mountain_name)
        if not mountain:
            return {
                'success': False,
                'error': f'未知坐山：{mountain_name}',
            }
        
        mountain_wx = mountain['wuxing']
        
        # 解析四柱
        sizhu = [
            {'name': '年柱', 'gan': year_gz[0], 'zhi': year_gz[1]},
            {'name': '月柱', 'gan': month_gz[0], 'zhi': month_gz[1]},
            {'name': '日柱', 'gan': day_gz[0], 'zhi': day_gz[1]},
            {'name': '时柱', 'gan': hour_gz[0], 'zhi': hour_gz[1]},
        ]
        
        # 计算各柱得分
        total_score = 0
        details = []
        
        for pillar in sizhu:
            gan_wx, zhi_wx = self.get_ganzhi_wuxing(pillar['gan'], pillar['zhi'])
            
            # 天干得分
            gan_score = self.calculate_relation_score(mountain_wx, gan_wx)
            total_score += gan_score
            
            # 地支得分
            zhi_score = self.calculate_relation_score(mountain_wx, zhi_wx)
            total_score += zhi_score
            
            details.append({
                'pillar': pillar['name'],
                'ganzhi': f"{pillar['gan']}{pillar['zhi']}",
                'gan_wuxing': gan_wx,
                'zhi_wuxing': zhi_wx,
                'gan_score': gan_score,
                'zhi_score': zhi_score,
                'pillar_score': gan_score + zhi_score,
            })
        
        # 判断吉凶等级
        if total_score >= self.score_thresholds['大吉']:
            jixiong = '大吉'
        elif total_score >= self.score_thresholds['吉']:
            jixiong = '吉'
        elif total_score >= self.score_thresholds['平']:
            jixiong = '平'
        elif total_score >= self.score_thresholds['凶']:
            jixiong = '凶'
        else:
            jixiong = '大凶'
        
        return {
            'success': True,
            'mountain': mountain_name,
            'mountain_wuxing': mountain_wx,
            'total_score': total_score,
            'jixiong': jixiong,
            'details': details,
        }
    
    def evaluate_with_shensha(self, mountain_name: str,
                              year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> Dict:
        """
        综合评价（包含神煞检查）
        
        Args:
            mountain_name: 坐山名称
            year_gz: 年柱
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            
        Returns:
            评价结果字典
        """
        # 先计算五行生克得分
        result = self.evaluate_sizhu(mountain_name, year_gz, month_gz, day_gz, hour_gz)
        
        if not result['success']:
            return result
        
        # 获取年支
        year_zhi = year_gz[1]
        
        # 检查神煞
        shensha_warnings = []
        shensha_list = []
        
        # 检查三煞
        san_sha_mountains = self.shensha_checker.check_san_sha(year_zhi)
        if mountain_name in san_sha_mountains:
            shensha_list.append('三煞')
            shensha_warnings.append(f'{year_zhi}年三煞在南方{san_sha_mountains}，{mountain_name}山犯三煞')
            result['total_score'] -= 100  # 大凶，一票否决
        
        # 检查岁破
        sui_po_mountains = self.shensha_checker.check_sui_po(year_zhi)
        if mountain_name in sui_po_mountains:
            shensha_list.append('岁破')
            shensha_warnings.append(f'{year_zhi}年岁破在{sui_po_mountains}，{mountain_name}山犯岁破')
            result['total_score'] -= 50
        
        # 更新吉凶等级
        total_score = result['total_score']
        if total_score >= self.score_thresholds['大吉']:
            jixiong = '大吉'
        elif total_score >= self.score_thresholds['吉']:
            jixiong = '吉'
        elif total_score >= self.score_thresholds['平']:
            jixiong = '平'
        elif total_score >= self.score_thresholds['凶']:
            jixiong = '凶'
        else:
            jixiong = '大凶'
        
        result['jixiong'] = jixiong
        result['shensha'] = shensha_list
        result['shensha_warnings'] = shensha_warnings
        
        return result
    
    def evaluate_sizhu_with_rules(self, mountain_name: str,
                                   year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> Dict:
        """
        使用动态规则评价四柱与坐山的关系
        
        Args:
            mountain_name: 坐山名称
            year_gz: 年柱
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            
        Returns:
            评价结果字典（包含规则信息）
        """
        # 获取坐山信息
        mountain = self.mountains.get_mountain_by_name(mountain_name)
        if not mountain:
            return {
                'success': False,
                'error': f'未知坐山：{mountain_name}',
            }
        
        mountain_wx = mountain['wuxing']
        
        # 解析四柱
        sizhu = [
            {'name': '年柱', 'gan': year_gz[0], 'zhi': year_gz[1]},
            {'name': '月柱', 'gan': month_gz[0], 'zhi': month_gz[1]},
            {'name': '日柱', 'gan': day_gz[0], 'zhi': day_gz[1]},
            {'name': '时柱', 'gan': hour_gz[0], 'zhi': hour_gz[1]},
        ]
        
        # 计算各柱得分
        total_score = 0
        details = []
        
        for pillar in sizhu:
            gan_wx, zhi_wx = self.get_ganzhi_wuxing(pillar['gan'], pillar['zhi'])
            
            # 使用规则计算天干得分
            gan_score, gan_direction = self.calculate_relation_score_with_rules(mountain_wx, gan_wx)
            total_score += gan_score
            
            # 使用规则计算地支得分
            zhi_score, zhi_direction = self.calculate_relation_score_with_rules(mountain_wx, zhi_wx)
            total_score += zhi_score
            
            details.append({
                'pillar': pillar['name'],
                'ganzhi': f"{pillar['gan']}{pillar['zhi']}",
                'gan_wuxing': gan_wx,
                'zhi_wuxing': zhi_wx,
                'gan_score': gan_score,
                'gan_direction': gan_direction,
                'zhi_score': zhi_score,
                'zhi_direction': zhi_direction,
                'pillar_score': gan_score + zhi_score,
            })
        
        # 判断吉凶等级
        if total_score >= self.score_thresholds['大吉']:
            jixiong = '大吉'
        elif total_score >= self.score_thresholds['吉']:
            jixiong = '吉'
        elif total_score >= self.score_thresholds['平']:
            jixiong = '平'
        elif total_score >= self.score_thresholds['凶']:
            jixiong = '凶'
        else:
            jixiong = '大凶'
        
        return {
            'success': True,
            'mountain': mountain_name,
            'mountain_wuxing': mountain_wx,
            'total_score': total_score,
            'jixiong': jixiong,
            'details': details,
            'rules_used': self.rules,  # 记录使用的规则
        }


# ============================================================================
# 数据库支持版本的选择器
# ============================================================================

class ZhengTiWuXingSelectorDB:
    """
    正体五行择日选择器（数据库版本）
    
    支持从数据库加载五行映射和规则，实现动态配置
    """
    
    def __init__(self, db_connection=None):
        """
        初始化，加载五行映射和规则
        
        Args:
            db_connection: 数据库连接对象（可选，为None时使用默认数据）
        """
        self.db = db_connection
        self.wuxing_id = {}        # 名称到ID的映射
        self.id_to_wuxing = {}      # ID到名称的映射
        self.tiangan_wuxing = {}    # 天干五行ID
        self.dizhi_wuxing = {}      # 地支五行ID
        self.relation_weights = {}  # 生克关系权重
        self.shensha_rules = []      # 神煞规则列表
        
        self._load_basic_data()
        self._load_rules()
    
    def _load_basic_data(self):
        """从数据库加载基础五行数据"""
        if self.db:
            # 实际应从数据库查询
            # cursor = self.db.cursor()
            # cursor.execute("SELECT * FROM wuxing;")
            # for row in cursor.fetchall():
            #     self.wuxing_id[row['name']] = row['id']
            #     self.id_to_wuxing[row['id']] = row['name']
            pass
        
        # 默认数据（当数据库不可用时）
        self.wuxing_id = {'金': 1, '木': 2, '水': 3, '火': 4, '土': 5}
        self.id_to_wuxing = {1: '金', 2: '木', 3: '水', 4: '火', 5: '土'}
        
        # 天干五行（根据正体五行）
        self.tiangan_wuxing = {
            '甲': 2, '乙': 2, '丙': 4, '丁': 4, '戊': 5, '己': 5,
            '庚': 1, '辛': 1, '壬': 3, '癸': 3
        }
        # 地支五行
        self.dizhi_wuxing = {
            '寅': 2, '卯': 2, '巳': 4, '午': 4, '申': 1, '酉': 1,
            '亥': 3, '子': 3, '辰': 5, '戌': 5, '丑': 5, '未': 5
        }
    
    def _load_rules(self):
        """从数据库加载生克权重和神煞规则"""
        if self.db:
            # 加载生克权重
            # cursor.execute("SELECT * FROM wuxing_relation_score;")
            # rows = cursor.fetchall()
            pass
        
        # 默认规则（当数据库不可用时）
        rows = [
            {'relation_type': '生', 'direction': '课生山', 'weight': 10},
            {'relation_type': '生', 'direction': '山生课', 'weight': 5},
            {'relation_type': '克', 'direction': '课克山', 'weight': -10},
            {'relation_type': '克', 'direction': '山克课', 'weight': -5},
            {'relation_type': '比和', 'direction': '比和', 'weight': 8},
        ]
        for row in rows:
            key = (row['relation_type'], row['direction'])
            self.relation_weights[key] = row['weight']
        
        # 加载神煞规则
        if self.db:
            # cursor.execute("SELECT * FROM shensha_rule;")
            # rule_rows = cursor.fetchall()
            pass
        
        # 默认神煞规则
        rule_rows = [
            {
                'id': 1,
                'shensha_name': '三煞',
                'condition_json': '{"rules": [{"year_zhi": ["申", "子", "辰"], "mountain_id": [8, 9, 10]}, {"year_zhi": ["寅", "午", "戌"], "mountain_id": [14, 2, 3]}, {"year_zhi": ["巳", "酉", "丑"], "mountain_id": [5, 6, 7]}, {"year_zhi": ["亥", "卯", "未"], "mountain_id": [11, 12, 13]}]}',
                'weight': -100,
                'is_decisive': True,
                'target_type': '山'
            },
            # 龙上八煞规则
            {
                'id': 2,
                'shensha_name': '龙上八煞-坎龙',
                'condition_json': '{"long_mountain_id": [2], "avoid_zhi": ["辰"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '坎龙忌辰，来龙在子山忌见辰支'
            },
            {
                'id': 3,
                'shensha_name': '龙上八煞-坤兔',
                'condition_json': '{"long_mountain_id": [17], "avoid_zhi": ["卯"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '坤兔忌卯，来龙在坤山忌见卯支'
            },
            {
                'id': 4,
                'shensha_name': '龙上八煞-震山猴',
                'condition_json': '{"long_mountain_id": [6], "avoid_zhi": ["申"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '震山猴忌申，来龙在卯山忌见申支'
            },
            {
                'id': 5,
                'shensha_name': '龙上八煞-巽鸡',
                'condition_json': '{"long_mountain_id": [18], "avoid_zhi": ["酉"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '巽鸡忌酉，来龙在巽山忌见酉支'
            },
            {
                'id': 6,
                'shensha_name': '龙上八煞-乾马',
                'condition_json': '{"long_mountain_id": [16], "avoid_zhi": ["午"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '乾马忌午，来龙在乾山忌见午支'
            },
            {
                'id': 7,
                'shensha_name': '龙上八煞-兑蛇头',
                'condition_json': '{"long_mountain_id": [12], "avoid_zhi": ["巳"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '兑蛇头忌巳，来龙在酉山忌见巳支'
            },
            {
                'id': 8,
                'shensha_name': '龙上八煞-艮虎',
                'condition_json': '{"long_mountain_id": [15], "avoid_zhi": ["寅"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '艮虎忌寅，来龙在艮山忌见寅支'
            },
            {
                'id': 9,
                'shensha_name': '龙上八煞-离猪',
                'condition_json': '{"long_mountain_id": [9], "avoid_zhi": ["亥"]}',
                'weight': -80,
                'is_decisive': True,
                'target_type': '龙',
                'description': '离猪忌亥，来龙在午山忌见亥支'
            },
        ]
        for row in rule_rows:
            row['condition'] = json.loads(row['condition_json'])
            self.shensha_rules.append(row)
    
    def get_mountain_wuxing(self, mountain_id: int) -> Optional[int]:
        """
        根据山ID获取五行ID
        
        Args:
            mountain_id: 山ID
            
        Returns:
            五行ID，找不到返回None
        """
        if self.db:
            # cursor.execute("SELECT wuxing_id FROM mountain_wuxing WHERE mountain_id = ?;", (mountain_id,))
            # result = cursor.fetchone()
            # return result['wuxing_id'] if result else None
            pass
        
        # 默认映射（简化版，实际应从数据库查询）
        mountain_wuxing_map = {
            1: 3,  # 壬水
            2: 3,  # 子水
            3: 3,  # 癸水
            4: 5,  # 丑土
            5: 2,  # 寅木
            6: 2,  # 卯木
            7: 5,  # 辰土
            8: 4,  # 巳火
            9: 4,  # 午火
            10: 5, # 未土
            11: 1, # 申金
            12: 1, # 酉金
            13: 5, # 戌土
            14: 3, # 亥水
            15: 5, # 艮土
            16: 1, # 乾金
            17: 5, # 坤土
            18: 2, # 巽木
            19: 5, # 戊己土
            20: 5, # 己
            21: 2, # 甲
            22: 2, # 乙
            23: 4, # 丙
            24: 4, # 丁
        }
        return mountain_wuxing_map.get(mountain_id)
    
    def calculate_relation(self, wx_a: int, wx_b: int) -> Tuple[str, str]:
        """
        判断两个五行的生克关系
        
        Args:
            wx_a: 第一个五行ID
            wx_b: 第二个五行ID
            
        Returns:
            (relation_type, direction)
            relation_type: '生','克','比和'
            direction: 'a生b', 'b生a', 'a克b', 'b克a', '比和'
        """
        if wx_a == wx_b:
            return '比和', '比和'
        
        # 生克关系矩阵（0金,1木,2水,3火,4土）
        # 注意：这里使用0-based索引，但传入的ID是1-based
        sheng = {0: 2, 1: 3, 2: 1, 3: 4, 4: 0}  # 生
        ke = {0: 1, 1: 4, 4: 2, 2: 3, 3: 0}     # 克
        
        # 转换为0-based索引
        a = wx_a - 1
        b = wx_b - 1
        
        if sheng.get(a) == b:
            return '生', 'a生b'
        if sheng.get(b) == a:
            return '生', 'b生a'
        if ke.get(a) == b:
            return '克', 'a克b'
        if ke.get(b) == a:
            return '克', 'b克a'
        return '其他', '无关系'
    
    def score_for_pair(self, mountain_wx: int, ganzhi_wx: int, target_type: str = '山') -> int:
        """
        计算单个干支（天干或地支）与坐山/龙的得分
        
        Args:
            mountain_wx: 坐山/龙五行ID
            ganzhi_wx: 干支五行ID
            target_type: 目标类型（'山' 或 '龙'）
            
        Returns:
            得分
        """
        rel_type, direction = self.calculate_relation(ganzhi_wx, mountain_wx)
        
        # 将方向映射为规则表中的direction字段
        if rel_type == '比和':
            dir_key = '比和'
        elif direction == 'a生b':   # a=ganzhi, b=mountain => 课生山/课生龙
            dir_key = '课生龙' if target_type == '龙' else '课生山'
        elif direction == 'b生a':   # 山/龙生课
            dir_key = '龙生课' if target_type == '龙' else '山生课'
        elif direction == 'a克b':   # 课克山/课克龙
            dir_key = '课克龙' if target_type == '龙' else '课克山'
        elif direction == 'b克a':   # 山/龙克课
            dir_key = '龙克课' if target_type == '龙' else '山克课'
        else:
            return 0
        
        # 先尝试查找特定类型的权重，找不到则使用通用权重
        weight = self.relation_weights.get((rel_type, dir_key))
        if weight is None:
            # 回退到通用权重
            if dir_key in ['课生龙', '课生山']:
                weight = self.relation_weights.get(('生', '课生山'), 0)
            elif dir_key in ['龙生课', '山生课']:
                weight = self.relation_weights.get(('生', '山生课'), 0)
            elif dir_key in ['课克龙', '课克山']:
                weight = self.relation_weights.get(('克', '课克山'), 0)
            elif dir_key in ['龙克课', '山克课']:
                weight = self.relation_weights.get(('克', '山克课'), 0)
            else:
                weight = self.relation_weights.get((rel_type, dir_key), 0)
        
        return weight if weight is not None else 0
    
    def check_shensha_for_long(self, year_zhi: str, long_mountain_id: int, 
                                 ganzhi_list: List[Tuple] = None) -> Tuple[int, bool, List[str]]:
        """
        检查来龙的神煞规则，支持龙上八煞
        
        Args:
            year_zhi: 年支
            long_mountain_id: 来龙山ID
            ganzhi_list: 日课四柱干支列表 [(gan_wx, zhi_wx), ...]，用于检查龙上八煞
            
        Returns:
            (总扣分, 是否否决, 触发的神煞列表)
        """
        total_penalty = 0
        decisive = False
        triggered_shensha = []
        
        for rule in self.shensha_rules:
            condition = rule['condition']
            target_type = rule.get('target_type', '山')
            
            # 只检查龙相关的规则
            if target_type not in ['龙', '山龙']:
                continue
            
            # 处理三煞规则格式
            if 'rules' in condition:
                for rule_item in condition['rules']:
                    # 检查 long_mountain_id 字段
                    if year_zhi in rule_item.get('year_zhi', []) and \
                       long_mountain_id in rule_item.get('long_mountain_id', []):
                        total_penalty += rule['weight']
                        if rule.get('is_decisive'):
                            decisive = True
                        triggered_shensha.append(rule['shensha_name'])
            
            # 处理龙上八煞格式：检查 long_mountain_id 和 avoid_zhi
            if 'long_mountain_id' in condition and 'avoid_zhi' in condition:
                if long_mountain_id in condition['long_mountain_id']:
                    # 检查日课四柱中是否有忌支
                    if ganzhi_list:
                        for gan_wx, zhi_wx in ganzhi_list:
                            # 将地支ID转换为地支名称进行检查
                            zhi_name = None
                            for zhi, wx_id in self.dizhi_wuxing.items():
                                if wx_id == zhi_wx:
                                    zhi_name = zhi
                                    break
                            if zhi_name and zhi_name in condition['avoid_zhi']:
                                total_penalty += rule['weight']
                                if rule.get('is_decisive'):
                                    decisive = True
                                if rule['shensha_name'] not in triggered_shensha:
                                    triggered_shensha.append(rule['shensha_name'])
                                break
        
        return total_penalty, decisive, triggered_shensha
    
    def check_shensha(self, year_zhi: str, mountain_id: int) -> Tuple[int, bool]:
        """
        检查所有神煞规则，返回总扣分和是否否决
        
        Args:
            year_zhi: 年支
            mountain_id: 山ID
            
        Returns:
            (总扣分, 是否否决)
        """
        total_penalty = 0
        decisive = False
        
        for rule in self.shensha_rules:
            condition = rule['condition']
            
            # 处理三煞规则格式
            if 'rules' in condition:
                for rule_item in condition['rules']:
                    if year_zhi in rule_item.get('year_zhi', []) and \
                       mountain_id in rule_item.get('mountain_id', []):
                        total_penalty += rule['weight']
                        if rule.get('is_decisive'):
                            decisive = True
            # 简单格式：{ "year_zhi": [...], "mountain_id": [...] }
            elif 'year_zhi' in condition and 'mountain_id' in condition:
                if year_zhi in condition['year_zhi'] and mountain_id in condition['mountain_id']:
                    total_penalty += rule['weight']
                    if rule.get('is_decisive'):
                        decisive = True
        
        return total_penalty, decisive
    
    def evaluate(self, mountain_id: int,
                 year_gan: str, year_zhi: str,
                 month_gan: str, month_zhi: str,
                 day_gan: str, day_zhi: str,
                 hour_gan: str, hour_zhi: str,
                 long_mountain_id: int = None,
                 long_weight: float = 1.0) -> Tuple[str, int, Any]:
        """
        综合评价一个日课，支持补龙扶山
        
        Args:
            mountain_id: 坐山ID
            year_gan, year_zhi: 年柱天干地支
            month_gan, month_zhi: 月柱天干地支
            day_gan, day_zhi: 日柱天干地支
            hour_gan, hour_zhi: 时柱天干地支
            long_mountain_id: 来龙ID（可选，若为None则不计算补龙）
            long_weight: 来龙得分权重系数（默认1.0，可设为1.5等提高补龙重要性）
            
        Returns:
            (等级, 总分, 详细信息)
        """
        # 1. 坐山五行
        mountain_wx = self.get_mountain_wuxing(mountain_id)
        if not mountain_wx:
            return "错误", 0, "坐山五行未定义"
        
        # 2. 来龙五行（如果有）
        long_wx = None
        if long_mountain_id is not None:
            long_wx = self.get_mountain_wuxing(long_mountain_id)
            if not long_wx:
                return "错误", 0, "来龙五行未定义"
        
        # 3. 日课各柱的五行
        ganzhi_list = [
            (self.tiangan_wuxing.get(year_gan), self.dizhi_wuxing.get(year_zhi)),
            (self.tiangan_wuxing.get(month_gan), self.dizhi_wuxing.get(month_zhi)),
            (self.tiangan_wuxing.get(day_gan), self.dizhi_wuxing.get(day_zhi)),
            (self.tiangan_wuxing.get(hour_gan), self.dizhi_wuxing.get(hour_zhi)),
        ]
        
        # 4. 计算五行生克得分（分别对坐山和来龙）
        score_mountain = 0
        score_long = 0
        details = []
        pillar_names = ['年', '月', '日', '时']
        
        for i, (gan_wx, zhi_wx) in enumerate(ganzhi_list):
            col_name = pillar_names[i]
            
            # 坐山得分
            if gan_wx:
                s = self.score_for_pair(mountain_wx, gan_wx, '山')
                score_mountain += s
                details.append(f"{col_name}干(山):{self.id_to_wuxing[gan_wx]} 得分{s}")
            if zhi_wx:
                s = self.score_for_pair(mountain_wx, zhi_wx, '山')
                score_mountain += s
                details.append(f"{col_name}支(山):{self.id_to_wuxing[zhi_wx]} 得分{s}")
            
            # 来龙得分
            if long_wx:
                if gan_wx:
                    s = self.score_for_pair(long_wx, gan_wx, '龙')
                    score_long += s
                    details.append(f"{col_name}干(龙):{self.id_to_wuxing[gan_wx]} 得分{s}")
                if zhi_wx:
                    s = self.score_for_pair(long_wx, zhi_wx, '龙')
                    score_long += s
                    details.append(f"{col_name}支(龙):{self.id_to_wuxing[zhi_wx]} 得分{s}")
        
        # 5. 神煞检查（同时检查坐山和来龙相关神煞）
        penalty_mountain, decisive_mountain = self.check_shensha(year_zhi, mountain_id)
        penalty_long = 0
        decisive_long = False
        triggered_shensha_long = []
        if long_mountain_id is not None:
            penalty_long, decisive_long, triggered_shensha_long = self.check_shensha_for_long(
                year_zhi, long_mountain_id, ganzhi_list
            )
        
        total_penalty = penalty_mountain + penalty_long
        decisive = decisive_mountain or decisive_long
        
        if decisive:
            return "凶(犯大煞)", score_mountain + score_long + total_penalty, details + [f"犯神煞，总扣{total_penalty}分"]
        
        # 应用来龙权重系数
        score_long_weighted = int(score_long * long_weight)
        total_score = score_mountain + score_long_weighted + total_penalty
        
        # 6. 评级
        if total_score >= 50:
            level = "大吉"
        elif total_score >= 30:
            level = "吉"
        elif total_score >= 10:
            level = "小吉"
        elif total_score >= -10:
            level = "平"
        elif total_score >= -30:
            level = "凶"
        else:
            level = "大凶"
        
        # 添加得分明细
        summary = {
            'mountain_score': score_mountain,
            'long_score': score_long if long_wx else None,
            'long_score_weighted': score_long_weighted if long_wx else None,
            'long_weight': long_weight if long_wx else None,
            'mountain_penalty': penalty_mountain,
            'long_penalty': penalty_long if long_wx else None,
            'triggered_shensha_long': triggered_shensha_long if long_wx else None,
        }
        
        return level, total_score, {'details': details, 'summary': summary}
    
    def evaluate_by_name(self, mountain_name: str,
                         year_gz: str, month_gz: str, day_gz: str, hour_gz: str,
                         long_name: str = None,
                         long_weight: float = 1.0) -> Dict:
        """
        通过山名评价日课（便捷方法），支持补龙
        
        Args:
            mountain_name: 山名（如'壬'）
            year_gz: 年柱（如'甲子'）
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            long_name: 龙名（如'巽'，可选）
            long_weight: 来龙得分权重系数（默认1.0）
            
        Returns:
            评价结果字典
        """
        # 山名到ID的映射
        name_to_id = {
            '壬': 1, '子': 2, '癸': 3, '丑': 4, '寅': 5, '卯': 6,
            '辰': 7, '巳': 8, '午': 9, '未': 10, '申': 11, '酉': 12,
            '戌': 13, '亥': 14, '艮': 15, '乾': 16, '坤': 17, '巽': 18,
            '戊': 19, '己': 20, '甲': 21, '乙': 22, '丙': 23, '丁': 24,
        }
        
        mountain_id = name_to_id.get(mountain_name)
        if not mountain_id:
            return {'success': False, 'error': f'未知山名：{mountain_name}'}
        
        long_mountain_id = None
        if long_name:
            long_mountain_id = name_to_id.get(long_name)
            if not long_mountain_id:
                return {'success': False, 'error': f'未知龙名：{long_name}'}
        
        level, score, result = self.evaluate(
            mountain_id,
            year_gz[0], year_gz[1],
            month_gz[0], month_gz[1],
            day_gz[0], day_gz[1],
            hour_gz[0], hour_gz[1],
            long_mountain_id,
            long_weight
        )
        
        return {
            'success': True,
            'mountain': mountain_name,
            'long': long_name,
            'level': level,
            'score': score,
            'details': result['details'] if isinstance(result, dict) else result,
            'summary': result.get('summary', {}) if isinstance(result, dict) else {}
        }
    
    def evaluate_with_fengjin(self, mountain_name: str, jianxiang: str,
                               year_gz: str, month_gz: str, day_gz: str, hour_gz: str,
                               long_name: str = None, long_weight: float = 1.0,
                               use_fengjin_wuxing: bool = True) -> Dict:
        """
        使用分金五行评价日课
        
        Args:
            mountain_name: 山名（如'子'）
            jianxiang: 兼向（如'兼壬'、'正中'、'兼癸'）
            year_gz: 年柱
            month_gz: 月柱
            day_gz: 日柱
            hour_gz: 时柱
            long_name: 龙名（可选）
            long_weight: 来龙权重系数
            use_fengjin_wuxing: 是否使用分金五行（纳音），False则使用正体五行
            
        Returns:
            评价结果字典
        """
        # 山名到ID的映射
        name_to_id = {
            '壬': 1, '子': 2, '癸': 3, '丑': 4, '寅': 5, '卯': 6,
            '辰': 7, '巳': 8, '午': 9, '未': 10, '申': 11, '酉': 12,
            '戌': 13, '亥': 14, '艮': 15, '乾': 16, '坤': 17, '巽': 18,
            '戊': 19, '己': 20, '甲': 21, '乙': 22, '丙': 23, '丁': 24,
        }
        
        mountain_id = name_to_id.get(mountain_name)
        if not mountain_id:
            return {'success': False, 'error': f'未知山名：{mountain_name}'}
        
        # 获取分金索引
        fengjin_index = get_fengjin_by_jianxiang(mountain_name, jianxiang)
        
        # 获取分金五行（纳音）
        fengjin_wx_name, nayin_name = get_fengjin_wuxing(mountain_name, fengjin_index)
        
        # 获取分金干支
        fengjin_ganzhi = FENGJIN_GANZHI.get(mountain_name, [''])[fengjin_index]
        
        # 获取正体五行
        mountain_wx = self.get_mountain_wuxing(mountain_id)
        
        # 将五行名称转换为ID
        fengjin_wx_id = self.wuxing_id.get(fengjin_wx_name, 5)  # 默认土
        
        # 决定使用哪个五行进行计算
        if use_fengjin_wuxing:
            target_wx = fengjin_wx_id
            target_wx_name = fengjin_wx_name
            wx_type = '分金五行（纳音）'
        else:
            target_wx = mountain_wx
            target_wx_name = self.id_to_wuxing.get(mountain_wx, '土')
            wx_type = '正体五行'
        
        # 日课各柱的五行
        ganzhi_list = [
            (self.tiangan_wuxing.get(year_gz[0]), self.dizhi_wuxing.get(year_gz[1])),
            (self.tiangan_wuxing.get(month_gz[0]), self.dizhi_wuxing.get(month_gz[1])),
            (self.tiangan_wuxing.get(day_gz[0]), self.dizhi_wuxing.get(day_gz[1])),
            (self.tiangan_wuxing.get(hour_gz[0]), self.dizhi_wuxing.get(hour_gz[1])),
        ]
        
        # 计算得分
        total_score = 0
        details = []
        pillar_names = ['年', '月', '日', '时']
        
        for i, (gan_wx, zhi_wx) in enumerate(ganzhi_list):
            col_name = pillar_names[i]
            
            if gan_wx:
                s = self.score_for_pair(target_wx, gan_wx, '分金')
                total_score += s
                details.append(f"{col_name}干:{self.id_to_wuxing.get(gan_wx, '?')} 对{target_wx_name} 得分{s}")
            if zhi_wx:
                s = self.score_for_pair(target_wx, zhi_wx, '分金')
                total_score += s
                details.append(f"{col_name}支:{self.id_to_wuxing.get(zhi_wx, '?')} 对{target_wx_name} 得分{s}")
        
        # 神煞检查
        penalty, decisive = self.check_shensha(year_gz[1], mountain_id)
        
        if decisive:
            return {
                'success': True,
                'mountain': mountain_name,
                'jianxiang': jianxiang,
                'fengjin_ganzhi': fengjin_ganzhi,
                'fengjin_wuxing': fengjin_wx_name,
                'nayin_name': nayin_name,
                'wx_type': wx_type,
                'level': "凶(犯大煞)",
                'score': total_score + penalty,
                'details': details,
                'warning': f"犯神煞，扣{penalty}分"
            }
        
        total_score += penalty
        
        # 评级
        if total_score >= 50:
            level = "大吉"
        elif total_score >= 30:
            level = "吉"
        elif total_score >= 10:
            level = "小吉"
        elif total_score >= -10:
            level = "平"
        elif total_score >= -30:
            level = "凶"
        else:
            level = "大凶"
        
        return {
            'success': True,
            'mountain': mountain_name,
            'jianxiang': jianxiang,
            'fengjin_index': fengjin_index + 1,  # 第几分金
            'fengjin_ganzhi': fengjin_ganzhi,
            'fengjin_wuxing': fengjin_wx_name,
            'nayin_name': nayin_name,
            'zhengti_wuxing': self.id_to_wuxing.get(mountain_wx, '未知'),
            'wx_type': wx_type,
            'level': level,
            'score': total_score,
            'details': details,
            'summary': {
                'mountain_wuxing': self.id_to_wuxing.get(mountain_wx, '未知'),
                'fengjin_wuxing': fengjin_wx_name,
                'nayin_name': nayin_name,
                'fengjin_ganzhi': fengjin_ganzhi,
            }
        }


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("二十四山模块测试")
    print("=" * 60)
    
    # 测试五行生克
    print("\n【五行生克测试】")
    print(WuxingRelation.get_relation('金', '水'))   # 金生水
    print(WuxingRelation.get_relation('木', '火'))   # 木生火
    print(WuxingRelation.get_relation('金', '木'))   # 金克木
    print(WuxingRelation.get_relation('水', '火'))   # 水克火
    print(WuxingRelation.get_relation('土', '土'))   # 比和
    
    # 测试二十四山
    print("\n【二十四山测试】")
    mountains = TwentyFourMountains()
    
    # 获取壬山信息
    ren = mountains.get_mountain_by_name('壬')
    print(f"\n壬山信息：")
    print(f"  类型：{ren['type'].value}")
    print(f"  度数范围：{ren['start_degree']}° - {ren['end_degree']}°")
    print(f"  五行：{ren['wuxing']}")
    print(f"  阴阳：{ren['yinyang'].value}")
    
    # 获取分金
    print(f"\n壬山分金：")
    for i in range(1, 6):
        fj = mountains.get_fengjin('壬', i)
        print(f"  第{i}分金：{fj['name']} ({fj['start_degree']}° - {fj['end_degree']}°)")
    
    # 根据度数查询
    print(f"\n度数查询测试：")
    shan = mountains.get_mountain_by_degree(350)
    print(f"  350° 对应：{shan['name']}山")
    
    # 神煞检查
    print(f"\n【神煞检查测试】")
    checker = MountainShenshaChecker()
    
    # 申子辰年三煞检查
    print("\n申子辰年三煞在南方巳午未：")
    for year in ['申', '子', '辰']:
        avoid = checker.check_san_sha(year)
        print(f"  {year}年忌：{avoid}")
    
    # 山家吉凶检查
    print(f"\n壬山在子年的吉凶：")
    result = checker.check_mountain_jixiong('壬', '子')
    print(f"  是否吉利：{result['is_good']}")
    print(f"  遇到神煞：{result['shensha']}")
    print(f"  警告信息：{result['warnings']}")
    
    # 测试正体五行择日算法
    print("\n【正体五行择日算法测试】")
    selector = ZhengTiWuXingSelector()
    
    # 测试案例：壬山，日课为甲子年 丙寅月 戊辰日 庚午时
    print("\n测试案例：壬山，日课为甲子年 丙寅月 戊辰日 庚午时")
    result = selector.evaluate_sizhu('壬', '甲子', '丙寅', '戊辰', '庚午')
    if result['success']:
        print(f"  坐山：{result['mountain']}（{result['mountain_wuxing']}）")
        print(f"  总得分：{result['total_score']}")
        print(f"  吉凶：{result['jixiong']}")
        print(f"  详细分析：")
        for detail in result['details']:
            print(f"    {detail['pillar']} {detail['ganzhi']}（干{detail['gan_wuxing']} 支{detail['zhi_wuxing']}）得分：{detail['pillar_score']}")
    
    # 测试包含神煞的综合评价
    print("\n综合评价（含神煞）：壬山，子年日课")
    result2 = selector.evaluate_with_shensha('壬', '甲子', '丙寅', '戊辰', '庚午')
    if result2['success']:
        print(f"  坐山：{result2['mountain']}（{result2['mountain_wuxing']}）")
        print(f"  总得分：{result2['total_score']}")
        print(f"  吉凶：{result2['jixiong']}")
        if result2.get('shensha'):
            print(f"  遇到神煞：{result2['shensha']}")
            for warning in result2['shensha_warnings']:
                print(f"    ⚠️ {warning}")
    
    # 测试犯三煞的情况：午山，子年
    print("\n测试犯三煞：午山，子年日课")
    result3 = selector.evaluate_with_shensha('午', '甲子', '丙寅', '戊辰', '庚午')
    if result3['success']:
        print(f"  坐山：{result3['mountain']}（{result3['mountain_wuxing']}）")
        print(f"  总得分：{result3['total_score']}")
        print(f"  吉凶：{result3['jixiong']}")
        if result3.get('shensha'):
            print(f"  遇到神煞：{result3['shensha']}")
            for warning in result3['shensha_warnings']:
                print(f"    ⚠️ {warning}")
    
    # 测试新的扩展功能
    print("\n【扩展功能测试】")
    
    # 测试 get_relation_by_id
    print("\n测试 get_relation_by_id:")
    print(f"  金(0)与水(2): {WuxingRelation.get_relation_by_id(0, 2)}")  # a_sheng_b
    print(f"  水(2)与金(0): {WuxingRelation.get_relation_by_id(2, 0)}")  # b_sheng_a
    print(f"  金(0)与木(1): {WuxingRelation.get_relation_by_id(0, 1)}")  # a_ke_b
    print(f"  木(1)与金(0): {WuxingRelation.get_relation_by_id(1, 0)}")  # b_ke_a
    print(f"  金(0)与金(0): {WuxingRelation.get_relation_by_id(0, 0)}")  # equal
    
    # 测试 get_relation_direction
    print("\n测试 get_relation_direction（针对坐山）:")
    print(f"  日课木 vs 坐山水: {WuxingRelation.get_relation_direction('木', '水', '水')}")  # 课生山
    print(f"  日课金 vs 坐山木: {WuxingRelation.get_relation_direction('金', '木', '木')}")  # 课克山
    print(f"  日课水 vs 坐山水: {WuxingRelation.get_relation_direction('水', '水', '水')}")  # 比和
    
    # 测试自定义规则
    print("\n测试自定义规则配置:")
    custom_rules = [
        {'rule_name': '日课生坐山', 'relation': '生', 'direction': '课生山', 'weight': 15, 'priority': 1},
        {'rule_name': '坐山生日课', 'relation': '生', 'direction': '山生课', 'weight': 8, 'priority': 2},
        {'rule_name': '日课克坐山', 'relation': '克', 'direction': '课克山', 'weight': -15, 'priority': 1},
        {'rule_name': '坐山克日课', 'relation': '克', 'direction': '山克课', 'weight': -8, 'priority': 2},
        {'rule_name': '比和', 'relation': '比和', 'direction': '比和', 'weight': 10, 'priority': 1},
    ]
    custom_selector = ZhengTiWuXingSelector(rules_config=custom_rules)
    print(f"  使用自定义规则（权重加大）")
    result4 = custom_selector.evaluate_sizhu_with_rules('壬', '甲子', '丙寅', '戊辰', '庚午')
    if result4['success']:
        print(f"  坐山：{result4['mountain']}（{result4['mountain_wuxing']}）")
        print(f"  总得分：{result4['total_score']}（使用自定义规则）")
        print(f"  吉凶：{result4['jixiong']}")
        print(f"  详细分析（含方向）：")
        for detail in result4['details']:
            print(f"    {detail['pillar']} {detail['ganzhi']}")
            print(f"      天干：{detail['gan_wuxing']} -> {detail['gan_direction']} ({detail['gan_score']}分)")
            print(f"      地支：{detail['zhi_wuxing']} -> {detail['zhi_direction']} ({detail['zhi_score']}分)")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    # 测试数据库版本
    print("\n" + "=" * 60)
    print("数据库版本选择器测试")
    print("=" * 60)
    
    db_selector = ZhengTiWuXingSelectorDB()
    
    # 测试案例1：壬山，日课为甲子年 丙寅月 戊辰日 庚午时
    print("\n测试案例1：壬山，日课为甲子年 丙寅月 戊辰日 庚午时")
    result_db = db_selector.evaluate_by_name('壬', '甲子', '丙寅', '戊辰', '庚午')
    if result_db['success']:
        print(f"  坐山：{result_db['mountain']}")
        print(f"  等级：{result_db['level']}")
        print(f"  得分：{result_db['score']}")
        print(f"  详细分析：")
        for detail in result_db['details']:
            print(f"    {detail}")
    
    # 测试案例2：子山，日课为甲辰年 戊戌月 丙午日 庚申时
    print("\n测试案例2：子山，日课为甲辰年 戊戌月 丙午日 庚申时")
    result_db2 = db_selector.evaluate_by_name('子', '甲辰', '戊戌', '丙午', '庚申')
    if result_db2['success']:
        print(f"  坐山：{result_db2['mountain']}")
        print(f"  等级：{result_db2['level']}")
        print(f"  得分：{result_db2['score']}")
        print(f"  详细分析：")
        for detail in result_db2['details']:
            print(f"    {detail}")
    
    # 测试案例3：午山，子年日课（犯三煞）
    print("\n测试案例3：午山，子年日课（犯三煞）")
    result_db3 = db_selector.evaluate_by_name('午', '甲子', '丙寅', '戊辰', '庚午')
    if result_db3['success']:
        print(f"  坐山：{result_db3['mountain']}")
        print(f"  等级：{result_db3['level']}")
        print(f"  得分：{result_db3['score']}")
        print(f"  详细分析：")
        for detail in result_db3['details']:
            print(f"    {detail}")
    
    # 直接使用 evaluate 方法测试
    print("\n测试案例4：直接使用 evaluate 方法")
    level, score, result = db_selector.evaluate(
        mountain_id=2,          # 子山
        year_gan='甲', year_zhi='辰',
        month_gan='戊', month_zhi='戌',
        day_gan='丙', day_zhi='午',
        hour_gan='庚', hour_zhi='申'
    )
    print(f"  等级：{level}")
    print(f"  得分：{score}")
    print(f"  详细分析：")
    if isinstance(result, dict):
        for detail in result['details']:
            print(f"    {detail}")
    else:
        for detail in result:
            print(f"    {detail}")
    
    print("\n" + "=" * 60)
    print("数据库版本测试完成！")
    print("=" * 60)
    
    # 测试补龙功能
    print("\n" + "=" * 60)
    print("补龙扶山功能测试")
    print("=" * 60)
    
    # 测试案例5：子山，巽龙，日课为甲子年 丙寅月 戊午日 庚申时
    print("\n测试案例5：子山（水），巽龙（木），日课为甲子年 丙寅月 戊午日 庚申时")
    result_db5 = db_selector.evaluate_by_name('子', '甲子', '丙寅', '戊午', '庚申', long_name='巽')
    if result_db5['success']:
        print(f"  坐山：{result_db5['mountain']}")
        print(f"  来龙：{result_db5['long']}")
        print(f"  等级：{result_db5['level']}")
        print(f"  总得分：{result_db5['score']}")
        if result_db5.get('summary'):
            print(f"  坐山得分：{result_db5['summary'].get('mountain_score', 0)}")
            print(f"  来龙得分：{result_db5['summary'].get('long_score', 0)}")
        print(f"  详细分析：")
        for detail in result_db5['details']:
            print(f"    {detail}")
    
    # 测试案例6：壬山，乾龙（金），日课为甲子年 丙寅月 戊辰日 庚午时
    print("\n测试案例6：壬山（水），乾龙（金），日课为甲子年 丙寅月 戊辰日 庚午时")
    result_db6 = db_selector.evaluate_by_name('壬', '甲子', '丙寅', '戊辰', '庚午', long_name='乾')
    if result_db6['success']:
        print(f"  坐山：{result_db6['mountain']}")
        print(f"  来龙：{result_db6['long']}")
        print(f"  等级：{result_db6['level']}")
        print(f"  总得分：{result_db6['score']}")
        if result_db6.get('summary'):
            print(f"  坐山得分：{result_db6['summary'].get('mountain_score', 0)}")
            print(f"  来龙得分：{result_db6['summary'].get('long_score', 0)}")
        print(f"  详细分析：")
        for detail in result_db6['details']:
            print(f"    {detail}")
    
    # 测试案例7：不使用来龙（对比）
    print("\n测试案例7：壬山（水），无来龙，日课为甲子年 丙寅月 戊辰日 庚午时（对比）")
    result_db7 = db_selector.evaluate_by_name('壬', '甲子', '丙寅', '戊辰', '庚午')
    if result_db7['success']:
        print(f"  坐山：{result_db7['mountain']}")
        print(f"  等级：{result_db7['level']}")
        print(f"  总得分：{result_db7['score']}")
        print(f"  详细分析：")
        for detail in result_db7['details']:
            print(f"    {detail}")
    
    # 测试案例8：直接使用 evaluate 方法测试补龙
    print("\n测试案例8：直接使用 evaluate 方法测试补龙")
    level, score, result = db_selector.evaluate(
        mountain_id=2,          # 子山（水）
        year_gan='甲', year_zhi='子',
        month_gan='丙', month_zhi='寅',
        day_gan='戊', day_zhi='午',
        hour_gan='庚', hour_zhi='申',
        long_mountain_id=18     # 巽龙（木）
    )
    print(f"  坐山：子（水）")
    print(f"  来龙：巽（木）")
    print(f"  等级：{level}")
    print(f"  总得分：{score}")
    if isinstance(result, dict):
        print(f"  坐山得分：{result['summary'].get('mountain_score', 0)}")
        print(f"  来龙得分：{result['summary'].get('long_score', 0)}")
        print(f"  详细分析：")
        for detail in result['details']:
            print(f"    {detail}")
    
    print("\n" + "=" * 60)
    print("补龙扶山功能测试完成！")
    print("=" * 60)
    
    # 测试龙上八煞和权重系数
    print("\n" + "=" * 60)
    print("龙上八煞和权重系数测试")
    print("=" * 60)
    
    # 测试案例9：子山（坎龙），日课含辰支（犯龙上八煞）
    print("\n测试案例9：子山（坎龙），日课为甲辰年 丙寅月 戊辰日 庚申时（犯龙上八煞-坎龙忌辰）")
    result_db9 = db_selector.evaluate_by_name('子', '甲辰', '丙寅', '戊辰', '庚申', long_name='子')
    if result_db9['success']:
        print(f"  坐山：{result_db9['mountain']}")
        print(f"  来龙：{result_db9['long']}")
        print(f"  等级：{result_db9['level']}")
        print(f"  总得分：{result_db9['score']}")
        if result_db9.get('summary'):
            print(f"  坐山得分：{result_db9['summary'].get('mountain_score', 0)}")
            print(f"  来龙得分：{result_db9['summary'].get('long_score', 0)}")
            triggered = result_db9['summary'].get('triggered_shensha_long', [])
            if triggered:
                print(f"  触发神煞：{triggered}")
        print(f"  详细分析：")
        for detail in result_db9['details']:
            print(f"    {detail}")
    
    # 测试案例10：坤山（坤兔），日课含卯支（犯龙上八煞）
    print("\n测试案例10：坤山，坤龙，日课为丁卯年 己卯月 辛卯日 癸卯时（犯龙上八煞-坤兔忌卯）")
    result_db10 = db_selector.evaluate_by_name('坤', '丁卯', '己卯', '辛卯', '癸卯', long_name='坤')
    if result_db10['success']:
        print(f"  坐山：{result_db10['mountain']}")
        print(f"  来龙：{result_db10['long']}")
        print(f"  等级：{result_db10['level']}")
        print(f"  总得分：{result_db10['score']}")
        if result_db10.get('summary'):
            triggered = result_db10['summary'].get('triggered_shensha_long', [])
            if triggered:
                print(f"  触发神煞：{triggered}")
        print(f"  详细分析：")
        for detail in result_db10['details']:
            print(f"    {detail}")
    
    # 测试案例11：权重系数对比测试
    print("\n测试案例11：权重系数对比 - 子山，巽龙，不同权重")
    print("\n  权重系数 1.0（默认）：")
    result_db11a = db_selector.evaluate_by_name('子', '甲子', '丙寅', '戊午', '庚申', long_name='巽', long_weight=1.0)
    if result_db11a['success']:
        print(f"    总得分：{result_db11a['score']}")
        print(f"    坐山得分：{result_db11a['summary'].get('mountain_score', 0)}")
        print(f"    来龙原始得分：{result_db11a['summary'].get('long_score', 0)}")
        print(f"    来龙加权得分：{result_db11a['summary'].get('long_score_weighted', 0)}")
    
    print("\n  权重系数 1.5（补龙更重要）：")
    result_db11b = db_selector.evaluate_by_name('子', '甲子', '丙寅', '戊午', '庚申', long_name='巽', long_weight=1.5)
    if result_db11b['success']:
        print(f"    总得分：{result_db11b['score']}")
        print(f"    坐山得分：{result_db11b['summary'].get('mountain_score', 0)}")
        print(f"    来龙原始得分：{result_db11b['summary'].get('long_score', 0)}")
        print(f"    来龙加权得分：{result_db11b['summary'].get('long_score_weighted', 0)}")
    
    print("\n  权重系数 2.0（补龙最重要）：")
    result_db11c = db_selector.evaluate_by_name('子', '甲子', '丙寅', '戊午', '庚申', long_name='巽', long_weight=2.0)
    if result_db11c['success']:
        print(f"    总得分：{result_db11c['score']}")
        print(f"    坐山得分：{result_db11c['summary'].get('mountain_score', 0)}")
        print(f"    来龙原始得分：{result_db11c['summary'].get('long_score', 0)}")
        print(f"    来龙加权得分：{result_db11c['summary'].get('long_score_weighted', 0)}")
    
    print("\n" + "=" * 60)
    print("龙上八煞和权重系数测试完成！")
    print("=" * 60)
