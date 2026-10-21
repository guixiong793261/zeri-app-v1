# -*- coding: utf-8 -*-
"""
================================================================================
作灶神煞模块
================================================================================
实现作灶择日专用神煞的检查逻辑
================================================================================
"""

import sys
import os

# 检查是否是直接运行（不是作为模块导入）
if __name__ == '__main__' and __package__ is None:
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 添加 modules 目录到路径
    modules_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    # 添加 shensha 目录到路径
    shensha_dir = os.path.dirname(os.path.abspath(__file__))
    if shensha_dir not in sys.path:
        sys.path.insert(0, shensha_dir)

try:
    from .神煞基类 import ShenShaChecker
except ImportError:
    from 神煞基类 import ShenShaChecker

class StoveShenShaChecker(ShenShaChecker):
    """作灶神煞检查器"""
    
    def __init__(self):
        super().__init__()
        # 五行映射
        self.zhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        self.direction_wuxing = {
            '东': '木', '南': '火', '西': '金', '北': '水',
            '东南': '木', '西南': '土', '东北': '土', '西北': '金',
            '艮': '土', '坤': '土', '震': '木', '巽': '木',
            '离': '火', '坎': '水', '兑': '金', '乾': '金'
        }
        self.wuxing_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        # 灶神方位检查暂时禁用（需要方位信息）
        # 如需启用，请传入 zaoxiang 或 zaowei 参数
    
    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        super()._check_month_shensha(sizhu, **kwargs)
        
        # ===== 凶煞 =====
        
        # 劫煞
        if self._is_jiesha(sizhu):
            self._add_shensha('劫煞', -25, '劫煞日忌作灶')
        
        # 灾煞
        if self._is_zaijiesha(sizhu):
            self._add_shensha('灾煞', -25, '灾煞日忌作灶')
        
        # 月煞
        if self._is_yuesha(sizhu):
            self._add_shensha('月煞', -20, '月煞日忌作灶')
        
        # 月厌
        if self._is_yueyan(sizhu):
            self._add_shensha('月厌', -15, '月厌日忌作灶')
        
        # 月破
        if self._is_yuepo(sizhu):
            self._add_shensha('月破', -30, '月破日忌作灶')
        
        # 土府日
        if self._is_tufu2(sizhu):
            self._add_shensha('土府日', -20, '土府日忌作灶')
        
        # 大耗
        if self._is_dahao(sizhu):
            self._add_shensha('大耗', -20, '大耗日忌作灶')
        
        # 小耗
        if self._is_xiaohao(sizhu):
            self._add_shensha('小耗', -15, '小耗日忌作灶')
    
    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
        # ===== 凶煞 =====

        # 红嘴朱雀（红嘴朱雀按典修批 B，2026-10-20）：陈书 p890「甲子、癸酉、
        # 壬午、辛卯、庚子、己酉、戊午七日在**震宮**，忌修厨」（朱雀歌「震宮
        # 修厨新婦亡」）。修厨按作灶通道落地；起例按日干支×九宫（基类）。
        if self._is_hongzui_zhuque(sizhu, '震'):
            self._add_shensha('红嘴朱雀', -30, '红嘴朱雀临震宮，忌修厨（作灶）')

        # 十恶大败发射行已注释（2026-10-19 全删批·一档，001 §139）：三库无
        # 「十恶大败」普适日课忌明文（取证 aa47dcd／快照 2ca7b4e；协纪
        # 「然惟随各年及本命避之」属本命避忌，非日课普适扣分）；谓词保留作无禄日载体。
        # if self._is_shie_dabai(sizhu):
        #     self._add_shensha('十恶大败', -30, '十恶大败日忌作灶')
        
        # 四废
        if self._is_sifei(sizhu):
            self._add_shensha('四废', -15, '四废日忌作灶')
        
        # 五墓条目已删（2026-10-18 P2 删除批，001 §122）：五墓×作灶三库无载
        # （协纪无用事条+陈书作灶条 p625-627 无载，docs/月家P2_月害大时往亡五墓_续取证.md §六）；
        # 本行原为死链，基类通用链事项排除后隔离（001 §120）。

        # 大时条目已删（2026-10-18 P2 删除批，001 §122）：大时×作灶三库无载
        # （docs/月家P2_月害大时往亡五墓_续取证.md §六）；本行原为死链，
        # 基类通用链事项排除后隔离（001 §120）。
        
        # 天吏×作灶已删（2026-10-21 口径收口批，001 §153）：协纪卷十天吏忌列
        # 37 项无作灶（取证稿 §1.8 判 ❌）。原发射为：
        #     if self._is_tianli(sizhu):
        #         self._add_shensha('天吏', -15, '天吏日忌作灶')
        
        # ===== 吉神 =====
        
        # 天德
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德吉星，作灶大吉')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德吉星，作灶大吉')
        
        # 天德合
        if self._is_tiande_he(sizhu):
            self._add_shensha('天德合', 15, '天德合，作灶吉')
        
        # 月德合
        if self._is_yuede_he(sizhu):
            self._add_shensha('月德合', 12, '月德合，作灶吉')
        
        # 2026-10 A4：三奇同名重加删除（基类 super 日块单点注册，此块从未生效）。

        # 将星
        if self._is_jiangxing(sizhu):
            self._add_shensha('将星', 12, '将星到座，作灶吉')
        
        # ===== 作灶专用 =====
        
        # 丙丁日（火旺适合作灶）
        if self._is_bingding(sizhu):
            self._add_shensha('丙丁日', 5, '丙丁日火旺适合作灶（需结合其他神煞）')
        
        # 天火日（传统公式：正月子、二月丑、三月寅...）
        if self._is_tianhuo(sizhu):
            self._add_shensha('天火日', -15, '天火日不宜作灶')
        
        # 地火日（传统公式：正月戌、二月亥、三月子...）
        if self._is_dihuo(sizhu):
            self._add_shensha('地火日', -10, '地火日不宜作灶')
        
        # 灶君朝天（登天太微宫五日：戊戌、己亥、庚子、辛丑、壬寅）  # _zjct0914
        if self._is_zaojun_chaotian(sizhu):
            self._add_shensha('灶君朝天', -15,
                              '灶君朝天（登天太微宫）日忌作灶，安灶新修俱不利（古歌：吉神会聚可制化）')

        # 逐月作灶忌日（《居家必用事类全集》）
        if self._is_zao_yueji(sizhu):
            self._add_shensha('作灶月忌', -15, '逐月作灶忌日，忌作灶')
        
        # 火忌（午未日）
        if self._is_huoji(sizhu):
            self._add_shensha('火忌', -10, '火忌日不宜作灶')
        
        # ===== 补充缺失的吉神检查 =====
        
        # 天德日
        if self._is_tiande(sizhu):
            self._add_shensha('天德', 20, '天德吉星，作灶大吉')
        
        # 月德
        if self._is_yuede(sizhu):
            self._add_shensha('月德', 18, '月德吉星，作灶大吉')
        
        # '天赦日'重加已删除（2026-09-18，001跟踪项13.2方案①）：基类
        # _check_day_shensha 已加'天赦'+25（本类日方法 super 先行且全路径必达），
        # 原异名重加致真天赦日 +50 双计；删除后走基类统一，天赦日=+25。

        # 2026-10 A1：'鸣吠日'/'鸣吠对日' 同名重加删除（基类月作用域统一注册，
        # 旧软件名「鸣犬日/对」已正名，谓词收为 13/11 典载日柱）。

        # 天愿
        if self._is_tianyuan(sizhu):
            self._add_shensha('天愿', 12, '天愿吉星，作灶吉')
        
        # 月恩
        if self._is_yueen(sizhu):
            self._add_shensha('月恩', 10, '月恩吉星，作灶吉')
        
        # 四相
        if self._is_sixiang(sizhu):
            self._add_shensha('四相', 10, '四相吉日，作灶吉')
        
        # 时德
        if self._is_shide(sizhu):
            self._add_shensha('时德', 10, '时德吉日，作灶吉')

        # 2026-10 A1：'岁德'/'岁德合' 同名重加删除（基类年作用域统一注册，
        # 谓词已修为年干比日干典载口径）。

        # 母仓日
        if self._is_mucang(sizhu):
            self._add_shensha('母仓日', 10, '母仓日作灶吉')
        
        # 相日
        if self._is_xiangri(sizhu):
            self._add_shensha('相日', 10, '相日作灶吉')
        
        # ===== 补充缺失的凶煞检查 =====
        
        # 丧门
        if self._is_sangmen(sizhu):
            self._add_shensha('丧门', -15, '丧门日忌作灶')
        
        # 吊客
        if self._is_diaoke(sizhu):
            self._add_shensha('吊客', -12, '吊客日忌作灶')
        
        # 月虚
        if self._is_yuexu(sizhu):
            self._add_shensha('月虚', -10, '月虚日主虚耗，忌作灶')

        # 八专发射已删（2026-10-18 月家P1：协纪仅忌军事+嫁娶，作灶超范围；
        # docs/月家P1_大煞八专四击_对勘.md）

    def _check_special_shensha(self, sizhu, owners, **kwargs):
        """检查特殊神煞，主要处理事主（宅主）生肖与日课的冲合"""
        zaoxiang = kwargs.get('zaoxiang')
        zaowei = kwargs.get('zaowei')
        
        if not owners:
            return
        
        def _ssw(raw, wv):
            # 2026-09 作灶主事人模式：辅助者半权重
            if wv >= 1.0:
                return raw
            _v = raw * wv
            return int(_v + 0.5) if _v >= 0 else -int(-_v + 0.5)

        for i, owner in enumerate(owners):
            owner_zodiac = owner.get('生肖', '')
            owner_year_zhi = owner.get('年支', '')
            owner_name = owner.get('姓名') or owner.get('name') or f'宅主{i+1}'
            _wv = owner.get('_zaozhu_weight', None)
            owner_weight = float(_wv) if _wv is not None else 1.0
            
            # 宅主灶向相合
            if self._check_owner_zao_match(sizhu, owner, zaoxiang, zaowei):
                self._add_shensha('宅主灶向相合', _ssw(10, owner_weight), '宅主八字与灶向相合')
            
            # 年支相冲
            year_zhi = sizhu['year_zhi']
            if self._is_chong(year_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'年冲{owner_name}', _ssw(-20, owner_weight), f'年支与{owner_name}生肖相冲')
            
            # 月支相冲
            month_zhi = sizhu['month_zhi']
            if self._is_chong(month_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'月冲{owner_name}', _ssw(-15, owner_weight), f'月支与{owner_name}生肖相冲')
            
            # 日支相冲
            day_zhi = sizhu['day_zhi']
            if self._is_chong(day_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'日冲{owner_name}', _ssw(-25, owner_weight), f'日支与{owner_name}生肖相冲，大忌')
            elif self._check_owner_sanhe_liuhe(sizhu, owner):
                self._add_shensha('日支与宅主合', _ssw(8, owner_weight), '日支与宅主年支相合')
            
            # 时支相冲
            hour_zhi = sizhu.get('hour_zhi', '')
            if hour_zhi and self._is_chong(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时冲{owner_name}', _ssw(-12, owner_weight), f'时支与{owner_name}生肖相冲')
            elif hour_zhi and self._is_he(hour_zhi, owner_year_zhi or owner_zodiac):
                self._add_shensha(f'时合{owner_name}', _ssw(6, owner_weight), f'时支与{owner_name}生肖相合')
    
    def _shengxiao_to_zhi(self, shengxiao):
        """生肖转换为地支"""
        shengxiao_map = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }
        return shengxiao_map.get(shengxiao)
    
    def _is_yuepo(self, sizhu):
        """是否月破日（日支与月支相冲）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return day_zhi == chong_map.get(month_zhi)
    
    def _is_dahao(self, sizhu):
        """是否大耗日（土府日之次日）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 使用基类的土府映射表
        tufu_map = {
            '寅': '辰', '卯': '巳', '辰': '午', '巳': '未',
            '午': '申', '未': '酉', '申': '戌', '酉': '亥',
            '戌': '子', '亥': '丑', '子': '寅', '丑': '卯'
        }
        tufu_zhi = tufu_map.get(month_zhi)
        if not tufu_zhi:
            return False
        tufu_idx = zh_list.index(tufu_zhi)
        dahao_zhi = zh_list[(tufu_idx + 1) % 12]
        return day_zhi == dahao_zhi
    
    def _is_xiaohao(self, sizhu):
        """是否小耗日（大耗日之次日）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        zh_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 使用基类的土府映射表
        tufu_map = {
            '寅': '辰', '卯': '巳', '辰': '午', '巳': '未',
            '午': '申', '未': '酉', '申': '戌', '酉': '亥',
            '戌': '子', '亥': '丑', '子': '寅', '丑': '卯'
        }
        tufu_zhi = tufu_map.get(month_zhi)
        if not tufu_zhi:
            return False
        tufu_idx = zh_list.index(tufu_zhi)
        xiaohao_zhi = zh_list[(tufu_idx + 2) % 12]
        return day_zhi == xiaohao_zhi
    
    def _is_chong(self, zhi1, zhi2):
        """检查两个地支是否相冲"""
        if not zhi1 or not zhi2:
            return False
        
        # 如果zhi2是生肖，转换为地支
        if zhi2 not in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
            zhi2 = self._shengxiao_to_zhi(zhi2)
            if not zhi2:
                return False
        
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return zhi1 == chong_map.get(zhi2)
    
    def _is_he(self, zhi1, zhi2):
        """检查两个地支是否相合（六合或三合）"""
        if not zhi1 or not zhi2:
            return False
        
        # 如果zhi2是生肖，转换为地支
        if zhi2 not in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
            zhi2 = self._shengxiao_to_zhi(zhi2)
            if not zhi2:
                return False
        
        # 六合
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        if liuhe_map.get(zhi1) == zhi2:
            return True
        
        # 三合
        sanhe_sets = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
        for s in sanhe_sets:
            if zhi1 in s and zhi2 in s and zhi1 != zhi2:
                return True
        
        return False
    
    def _check_owner_zao_match(self, sizhu, owner, zaoxiang=None, zaowei=None):
        """检查宅主与灶向是否相合"""
        # 获取宅主年命五行
        owner_year_zhi = owner.get('year_zhi', '')
        owner_wuxing = self.zhi_wuxing.get(owner_year_zhi, '')
        
        # 获取灶向或灶位五行
        direction = zaoxiang or zaowei
        if not direction:
            return False
        
        # 尝试从方向获取五行
        dir_wuxing = self.direction_wuxing.get(direction)
        if not dir_wuxing:
            # 尝试从第一个字获取五行
            dir_wuxing = self.direction_wuxing.get(direction[0])
        
        if not dir_wuxing:
            return False
        
        # 灶向生宅主命为吉
        return self.wuxing_sheng.get(dir_wuxing) == owner_wuxing
    
    def _check_owner_sanhe_liuhe(self, sizhu, owner):
        """检查日支与宅主年支是否三合或六合"""
        day_zhi = sizhu.get('day_zhi', '')
        owner_year_zhi = owner.get('year_zhi', '')
        
        if not day_zhi or not owner_year_zhi:
            return False
        
        # 六合检查
        liuhe = {('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')}
        if (day_zhi, owner_year_zhi) in liuhe or (owner_year_zhi, day_zhi) in liuhe:
            return True
        
        # 三合检查
        sanhe_groups = [{'申', '子', '辰'}, {'寅', '午', '戌'}, {'巳', '酉', '丑'}, {'亥', '卯', '未'}]
        for group in sanhe_groups:
            if day_zhi in group and owner_year_zhi in group:
                return True
        
        return False
    
    def _is_bingding(self, sizhu):
        """是否丙丁日"""
        day_gan = sizhu.get('day_gan', '')
        return day_gan in ['丙', '丁']
    
    def _is_tianhuo(self, sizhu):
        """是否天火日（传统公式：正月子、二月丑、三月寅...，即月支前2位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        if not month_zhi or not day_zhi:
            return False
        
        # 天火日：月支前2位（正月寅→子，二月卯→丑，...）
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        try:
            month_idx = zhi_order.index(month_zhi)
            tianhuo_zhi = zhi_order[(month_idx - 2) % 12]
            return day_zhi == tianhuo_zhi
        except ValueError:
            return False
    
    def _is_dihuo(self, sizhu):
        """是否地火日（传统公式：正月戌、二月亥、三月子...，即月支后2位）"""
        month_zhi = sizhu.get('month_zhi', '')
        day_zhi = sizhu.get('day_zhi', '')
        
        if not month_zhi or not day_zhi:
            return False
        
        # 地火日：月支后2位（正月寅→辰，二月卯→巳，...）
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        try:
            month_idx = zhi_order.index(month_zhi)
            dihuo_zhi = zhi_order[(month_idx + 2) % 12]
            return day_zhi == dihuo_zhi
        except ValueError:
            return False
