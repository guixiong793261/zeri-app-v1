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


class DiggingShenShaChecker(ConstructionShenShaChecker):
    """动土神煞检查器"""
    
    def _check_year_shensha(self, sizhu):
        """检查年神煞"""
        super()._check_year_shensha(sizhu)

    def _check_month_shensha(self, sizhu):
        """检查月神煞"""
        super()._check_month_shensha(sizhu)
        
        # 土王用事（动土大忌）
        if self._is_tuwang_yongshi(sizhu):
            self._add_shensha('土王用事', -35, '土王当权，忌动土')
        
        # 杀师日（动土大忌，伤工匠）
        if self._is_shashi(sizhu):
            self._add_shensha('杀师日', -30, '动土大忌，犯之伤害工匠')

    def _check_day_shensha(self, sizhu):
        """检查日神煞"""
        super()._check_day_shensha(sizhu)
        
        # 天赦（动土大吉）
        if self._is_tianshe(sizhu):
            self._add_shensha('天赦', 25, '天赦吉日，动土百无禁忌')


if __name__ == '__main__':
    print("动土神煞模块")
    print("使用方法: from modules.shensha.动土神煞 import DiggingShenShaChecker")
