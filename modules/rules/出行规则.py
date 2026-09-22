import sys
import os

if __name__ == '__main__' and __package__ is None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    modules_dir = os.path.dirname(os.path.abspath(__file__))
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

# -*- coding: utf-8 -*-
"""
================================================================================
出行规则模块
================================================================================
实现出行择日的宜忌规则，参考《协纪辨方书》卷三十二"出行"章节

规则层次：
1. 建除十二神宜忌
2. 天德/月德/不将日等吉神
3. 月破/岁破/四离四绝等凶煞
4. 与事主生肖关系（冲日忌出行）
5. 出行方位辅助
6. 专用出行吉日（鸣犬日、要安日等）
================================================================================
"""

from .规则基类 import EventRuleChecker


class TravelRuleChecker(EventRuleChecker):
    """出行规则检查器 - 参考《协纪辨方书》卷三十二"""

    # 建除十二神宜忌（出行）
    # 2026-09-16修复：原表 YI=['除','满','平','定','执','成','开'] / JI=['建','破','危','收','闭']
    # 与软件内权威小黄道表 modules/黄道.py XIAO_HUANG_DAO_YIJI 对"出行"的判定相互矛盾
    # （建日黄道宜出行却在此被列为忌；定/执日黄道忌出行却在此被列为宜），报告会同时出现
    # "小黄道 建日 宜出行"与"建除建日忌出行"。现按黄道表（亦与通书建除十二神宜忌一致）对齐：
    # 宜出行=建/除/平/成/开；忌出行=定/执/破/危/收/闭；满日黄道未列出行（中性，不判）。
    JIANCHU_YI = ['建', '除', '平', '成', '开']
    JIANCHU_JI = ['定', '执', '破', '危', '收', '闭']

    # 出行专用吉日
    CHUXING_YI_DAYS = ['天德', '月德', '不将日', '鸣犬日', '要安日', '六合日', '天赦日']

    # 出行专用凶日
    CHUXING_JI_DAYS = ['月破', '岁破', '大煞', '四离四绝', '往亡', '朱雀', '白虎', '玄武']

    # 地支对应方位
    ZHI_TO_DIRECTION = {
        '子': '北', '丑': '东北', '寅': '东北', '卯': '东',
        '辰': '东南', '巳': '东南', '午': '南', '未': '西南',
        '申': '西南', '酉': '西', '戌': '西北', '亥': '西北'
    }

    # 天干对应方位
    GAN_TO_DIRECTION = {
        '甲': '东', '乙': '东', '丙': '南', '丁': '南',
        '戊': '中', '己': '中', '庚': '西', '辛': '西',
        '壬': '北', '癸': '北'
    }

    # 建除补充判据（原标注为"鸣犬日"，但"鸣犬日"本是独立神煞名、不由建除推）
    # 2026-09-16 用户裁决：保留判定、文案改名，不再冒用"鸣犬X日"以免误导。
    # 注：除/成/开/破/危/闭 与上方 JIANCHU_YI/JI 同向，故同一天会出现两条同名宜忌
    # （一条无后缀、一条带"（鸣犬）"），此为用户确认保留的重复展示；
    # 本表相对建除表唯一增量 = 满日（建除表对满日中性，本表判宜）。
    MINGQUAN_YI = ['除', '满', '成', '开']
    MINGQUAN_JI = ['破', '危', '闭']

    def __init__(self):
        super().__init__()
        self.has_marriage_shensha = self._check_dependencies()

    def _check_dependencies(self):
        try:
            from ..黄历宜忌 import get_huangli_info
            return True
        except ImportError:
            return False

    def _check_rules(self, sizhu, owners=None, **kwargs):
        """检查出行规则 - 参考《协纪辨方书》"""
        yi_list = []
        ji_list = []

        date_obj = kwargs.get('date_obj')
        shan_xiang = kwargs.get('shan_xiang')

        # 1. 建除十二神宜忌
        self._check_jianchu(date_obj, yi_list, ji_list)

        # 2. 天德/月德/不将日等吉神
        self._check_shensha_yi(date_obj, yi_list)

        # 3. 月破/岁破/四离四绝等凶煞
        self._check_shensha_ji(sizhu, date_obj, ji_list)

        # 4. 出行专用吉凶
        self._check_chuxing_special(sizhu, date_obj, yi_list, ji_list)

        # 5. 与事主生肖关系
        if owners:
            self._check_owner_relation(sizhu, owners, ji_list)

        # 6. 出行方位辅助
        self._check_direction(sizhu, yi_list, ji_list)

        # 7. 检查一票否决项
        veto, veto_reason = self._check_veto_items(sizhu, ji_list)
        if veto:
            return yi_list, ji_list, True, veto_reason

        return yi_list, ji_list, False, ""

    def _check_jianchu(self, date_obj, yi_list, ji_list):
        """检查建除十二神"""
        if not date_obj:
            return

        try:
            jianchu = getattr(date_obj, '建除十二神', None) or getattr(date_obj, 'jianchu', None)
            if not jianchu:
                return

            if jianchu in self.JIANCHU_YI:
                yi_list.append(f'建除{jianchu}日宜出行')
            elif jianchu in self.JIANCHU_JI:
                ji_list.append(f'建除{jianchu}日忌出行')
        except Exception:
            pass

    def _check_shensha_yi(self, date_obj, yi_list):
        """检查天德/月德等吉神"""
        if not date_obj:
            return

        try:
            yi_ji_data = getattr(date_obj, '宜', '') or getattr(date_obj, 'yi', '') or []
            if isinstance(yi_ji_data, (list, tuple)):
                yi_text = ' '.join(str(x) for x in yi_ji_data)
            else:
                yi_text = str(yi_ji_data)

            # 2026-10 A1：'鸣犬' 改典据正名 '鸣吠'（黄历宜文字用「鸣吠」，
            # 旧 token 永不命中）；CHUXING_YI_DAYS 中同名死属性归 C 批清理。
            for shensha in ['天德', '月德', '不将日', '鸣吠', '要安', '六合', '天赦']:
                if shensha in yi_text:
                    yi_list.append(f'{shensha}日宜出行')
        except Exception:
            pass

    def _check_shensha_ji(self, sizhu, date_obj, ji_list):
        """检查月破/岁破/四离四绝等凶煞"""
        day_zhi = sizhu.get('day_zhi', '')
        year_zhi = sizhu.get('year_zhi', '')
        month_zhi = sizhu.get('month_zhi', '')

        # 月破日（月支冲日支）
        if month_zhi and day_zhi:
            chong_map = {
                '子': '午', '丑': '未', '寅': '申', '卯': '酉',
                '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
                '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
            }
            if chong_map.get(month_zhi) == day_zhi:
                ji_list.append(f'月破日({month_zhi}月{day_zhi}日)忌出行')

        # 岁破日（年支冲日支）
        if year_zhi and day_zhi:
            chong_map = {
                '子': '午', '丑': '未', '寅': '申', '卯': '酉',
                '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
                '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
            }
            if chong_map.get(year_zhi) == day_zhi:
                ji_list.append(f'岁破日({year_zhi}年{day_zhi}日)忌出行')

        # 四离四绝日
        if date_obj:
            try:
                jieri = getattr(date_obj, '忌', '') or getattr(date_obj, 'ji', '') or []
                if isinstance(jieri, (list, tuple)):
                    ji_text = ' '.join(str(x) for x in jieri)
                else:
                    ji_text = str(jieri)

                for xiongsa in ['四离', '四绝', '往亡', '朱雀', '白虎', '玄武', '大煞']:
                    if xiongsa in ji_text or xiongsa in str(date_obj):
                        ji_list.append(f'{xiongsa}日忌出行')
            except Exception:
                pass

    def _check_chuxing_special(self, sizhu, date_obj, yi_list, ji_list):
        """检查出行专用吉凶"""
        day_zhi = sizhu.get('day_zhi', '')
        day_gan = sizhu.get('day_gan', '')

        # 出行宜日（传统口诀：寅申巳亥为四马，子午卯酉为四正，辰戌丑未为四库）
        # 宜出行：四马日（寅、申、巳、亥）和四正日（子、午、卯、酉）
        chuxing_yi_zhi = ['子', '寅', '卯', '巳', '午', '申', '酉', '亥']
        chuxing_ji_zhi = ['丑', '辰', '未', '戌']

        if day_zhi in chuxing_yi_zhi:
            yi_list.append(f'出行宜日({day_zhi})')
        elif day_zhi in chuxing_ji_zhi:
            ji_list.append(f'出行忌日({day_zhi})')

        # 远行吉日（四马日：寅、申、巳、亥）
        yuanxing_yi = ['寅', '申', '巳', '亥']
        if day_zhi in yuanxing_yi:
            yi_list.append(f'远行吉日({day_zhi})')

        # 归家吉日（四库日：丑、辰、未、戌）
        guijia_yi = ['子', '丑', '辰', '未', '戌', '亥']
        if day_zhi in guijia_yi:
            yi_list.append(f'归家吉日({day_zhi})')

        # 检查建除补充判据（原"鸣犬日"，2026-09-16 保留判定、改名以免冒用神煞名）
        if date_obj:
            try:
                jianchu = getattr(date_obj, '建除十二神', None) or getattr(date_obj, 'jianchu', None)
                if jianchu:
                    if jianchu in self.MINGQUAN_YI:
                        yi_list.append(f'建除{jianchu}日宜出行（鸣犬）')
                    elif jianchu in self.MINGQUAN_JI:
                        ji_list.append(f'建除{jianchu}日忌出行（鸣犬）')
            except Exception:
                pass

        # 日辰纳音检查（简化版）
        # 天干为甲丙戊庚壬时，利出行
        if day_gan in ['甲', '丙', '戊', '庚', '壬']:
            yi_list.append(f'日干{day_gan}(阳干)利出行')

    def _check_owner_relation(self, sizhu, owners, ji_list):
        """检查与事主生肖关系"""
        day_zhi = sizhu.get('day_zhi', '')
        if not day_zhi or not owners:
            return

        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }

        zodiac_to_zhi = {
            '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
            '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
            '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
        }

        day_chong = chong_map.get(day_zhi, '')
        for owner in owners:
            name = owner.get('name', '事主')
            zodiac = owner.get('生肖', '')
            owner_zhi = zodiac_to_zhi.get(zodiac, '')

            if owner_zhi and day_chong == owner_zhi:
                ji_list.append(f'出行日支{day_zhi}冲{name}生肖{zodiac}')

    def _check_direction(self, sizhu, yi_list, ji_list):
        """出行方位辅助"""
        day_zhi = sizhu.get('day_zhi', '')
        day_gan = sizhu.get('day_gan', '')

        # 根据日支给出有利方位
        direction = self.ZHI_TO_DIRECTION.get(day_zhi, '')
        if direction:
            yi_list.append(f'出行吉日支{day_zhi}利{direction}方')

        # 根据日干给出有利方位
        gan_direction = self.GAN_TO_DIRECTION.get(day_gan, '')
        if gan_direction and gan_direction != '中':
            yi_list.append(f'出行吉日干{day_gan}利{gan_direction}方')

    def _check_veto_items(self, sizhu, ji_list):
        """检查一票否决项"""
        veto_keywords = ['月破日', '岁破日', '四离', '四绝', '往亡']
        veto_reasons = []

        for ji in ji_list:
            for keyword in veto_keywords:
                if keyword in ji:
                    veto_reasons.append(ji)
                    break

        if veto_reasons:
            return True, "、".join(veto_reasons)

        return False, ""


# 测试
if __name__ == '__main__':
    checker = TravelRuleChecker()

    test_sizhu = {
        'day_gan': '丙',
        'day_zhi': '寅',
        'month_zhi': '寅',
        'year_zhi': '子',
        'hour_zhi': '午',
        'day_gan_zhi': '丙寅',
        'month_gan_zhi': '庚寅',
        'year_gan_zhi': '戊子',
        'hour_gan_zhi': '壬午'
    }

    class MockDateObj:
        def __init__(self):
            self.建除十二神 = '除'
            self.宜 = ['出行', '会友', '上任', '天德', '月德']
            self.忌 = ['安葬', '伐木']

    test_date = MockDateObj()

    test_owners = [
        {'name': '张先生', '性别': '男', '生肖': '虎'},
        {'name': '李女士', '性别': '女', '生肖': '猴'}
    ]

    print("=== 出行规则测试 ===")
    yi, ji, veto, veto_reason = checker._check_rules(
        test_sizhu,
        owners=test_owners,
        date_obj=test_date
    )

    print(f"\n宜项 ({len(yi)}):")
    for y in yi:
        print(f"  ✅ {y}")

    print(f"\n忌项 ({len(ji)}):")
    for j in ji:
        print(f"  ❌ {j}")

    print(f"\n否决: {veto}")
    if veto:
        print(f"原因: {veto_reason}")