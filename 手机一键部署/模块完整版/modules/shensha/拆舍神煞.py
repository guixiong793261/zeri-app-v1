import sys
import os

shensha_dir = os.path.dirname(os.path.abspath(__file__))
if shensha_dir not in sys.path:
    sys.path.insert(0, shensha_dir)

try:
    from .神煞基类 import ShenShaChecker
    from .修造神煞 import ConstructionShenShaChecker
    from ..工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE
except ImportError:
    from 神煞基类 import ShenShaChecker
    from 修造神煞 import ConstructionShenShaChecker
    from 工具函数 import SANSHA_MAP, TIAN_GAN, DI_ZHI, TIANDE, YUEDE


class DemolitionShenShaChecker(ConstructionShenShaChecker):
    """拆舍神煞检查器"""
    
    def _check_year_shensha(self, sizhu, **kwargs):
        """检查年神煞"""
        super()._check_year_shensha(sizhu, **kwargs)
        
        # 太岁（拆舍大忌）
        if self._is_taisui(sizhu):
            self._add_shensha('太岁', -20, '太岁当头，忌拆舍')
        
        # 岁破（拆舍大忌）
        if self._is_suipo(sizhu):
            self._add_shensha('岁破', -30, '岁破日忌拆舍，犯之主凶')
        
        # 岁煞
        if self._is_suisha(sizhu):
            self._add_shensha('岁煞', -20, '岁煞日忌拆舍')
        
        # 黄幡
        if self._is_huangfan(sizhu):
            self._add_shensha('黄幡', -15, '黄幡日忌拆舍')
        
        # 豹尾
        if self._is_baowei(sizhu):
            self._add_shensha('豹尾', -12, '豹尾日忌拆舍')

        # 大煞发射已删（2026-10-18 月家P1：协纪卷十仅忌军事，拆舍超范围；
        # docs/月家P1_大煞八专四击_对勘.md）

    def _check_month_shensha(self, sizhu, **kwargs):
        """检查月神煞"""
        # 土符（忌破屋坏垣——典据正名，2026-10-18 判据(b)拍板：协纪16事作
        # 「破屋坏垣」，软件事项「拆舍」与之语义等价（⚠️档），正名后分值 -20 不动。
        # 前置发射：super 链（修造）亦注册同名土符，_add_shensha 同名先到
        # 先得去重，置 super 之前方使拆舍专用文案生效；修造/动土路径不变）
        if self._is_tufu(sizhu):
            self._add_shensha('土符', -20, '忌破屋坏垣（拆舍），犯之主灾')
        super()._check_month_shensha(sizhu, **kwargs)
        
        # 土王用事（拆舍大忌）
        if self._is_tuwang_yongshi(sizhu):
            self._add_shensha('土王用事', -40, '土王当权，忌拆舍')
        
        # 月刑
        if self._is_yuexing(sizhu):
            self._add_shensha('月刑', -15, '月刑日忌拆舍')
        
        # 月害——P2 删除候选隔离（2026-10-18，001 §120）：月害×拆舍三库无载
        # （系逐字重提更正诊断漏标，docs/月家P2_月害大时往亡五墓_续取证.md §六），
        # 基类通用链已按事项排除；本行原为死链，基类排除后将复活，故一并注释。
        # if self._is_yuehai(sizhu):
        #     self._add_shensha('月害', -15, '月害日忌拆舍')

    def _check_day_shensha(self, sizhu, **kwargs):
        """检查日神煞"""
        super()._check_day_shensha(sizhu, **kwargs)
        
        # 天赦（拆舍大吉）
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦吉日，拆舍百无禁忌')
        
        # 受死日
        if self._is_shousi_day(sizhu):
            self._add_shensha('受死日', -22, '受死日忌拆舍，犯之主凶')
        
        # 往亡日
        if self._is_wangwang(sizhu):
            self._add_shensha('往亡日', -20, '往亡日忌拆舍')


if __name__ == '__main__':
    print("拆舍神煞模块")
    print("使用方法: from modules.shensha.拆舍神煞 import DemolitionShenShaChecker")
