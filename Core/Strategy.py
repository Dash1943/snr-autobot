import numpy as np
from typing import Dict

class MomentumStrategy:
    def __init__(self):
        self.window_size = 24  # 分析窗口（小时）

    def analyze(self, klines: list) -> Dict[str, float]:
        closes = [float(k['close']) for k in klines]
        volumes = [float(k['volume']) for k in klines]
        
        analysis = {
            'trend_strength': self._calc_trend_strength(closes),
            'volatility': self._calc_volatility(closes),
            'volume_change': self._calc_volume_change(volumes)
        }
        return analysis

    def _calc_trend_strength(self, closes: list) -> float:
        returns = np.diff(closes) / closes[:-1]
        return np.mean(returns[-6:])  # 最近6小时平均收益

    def _calc_volatility(self, closes: list) -> float:
        return np.std(np.log(closes[1:]/closes[:-1])) * np.sqrt(365)

    def _calc_volume_change(self, volumes: list) -> float:
        return volumes[-1] / np.mean(volumes[-6:]) - 1

    def generate_signal(self, analysis: dict) -> int:
        if (analysis['trend_strength'] > 0.002 and 
            analysis['volume_change'] > 0.5 and 
            analysis['volatility'] < 0.15):
            return 1  # 买入
        elif analysis['trend_strength'] < -0.003:
            return -1 # 卖出
        return 0       # 观望
