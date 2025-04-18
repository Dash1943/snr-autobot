import asyncio
import time
from config.settings import Config
from core.api_client import BybitAPIClient
from core.strategy import MomentumStrategy
from core.risk_mgmt import RiskController
from core.order_executor import OrderExecutor

class TradingBot:
    def __init__(self):
        self.api = BybitAPIClient()
        self.strategy = MomentumStrategy()
        self.risk = RiskController(self.api)
        self.executor = OrderExecutor(self.api, self.risk)
        self.last_balance_update = 0

    async def run(self):
        async with self.api:
            await self.initialize()
            while True:
                try:
                    await self.trading_cycle()
                    await asyncio.sleep(10)
                except Exception as e:
                    print(f"主循环异常: {e}")
                    await asyncio.sleep(30)

    async def initialize(self):
        """初始化系统"""
        await self.risk.refresh_balance()
        print(f"初始余额: {self.risk.balance} {Config.TRADE_COIN}")

    async def trading_cycle(self):
        """完整交易周期"""
        # 1. 刷新账户数据
        if time.time() - self.last_balance_update > Config.BALANCE_REFRESH:
            await self.risk.refresh_balance()
            self.last_balance_update = time.time()

        # 2. 获取行情数据
        tickers = await self.get_active_tickers()
        
        # 3. 生成交易信号
        for symbol in tickers:
            klines = await self.api.get_klines(symbol, "1h", Config.STRATEGY_WINDOW)
            analysis = self.strategy.analyze(klines)
            signal = self.strategy.generate_signal(analysis)
            
            if signal != 0:
                await self.process_signal(symbol, signal, analysis)

    async def get_active_tickers(self) -> list:
        """获取活跃交易对"""
        params = {"category": "linear", "limit": 50}
        data = await self.api.fetch_market_data("/v5/market/tickers", params=params)
        return sorted(
            [item['symbol'] for item in data['result']['list']],
            key=lambda x: float(x['turnover24h']),
            reverse=True
        )[:Config.MAX_SYMBOLS]

    async def process_signal(self, symbol: str, signal: int, analysis: dict):
        """处理交易信号"""
        try:
            # 获取当前价格
            ticker = await self.api.fetch_market_data(
                "/v5/market/tickers",
                params={"category": "linear", "symbol": symbol}
            )
            price = float(ticker['result']['list'][0]['lastPrice'])
            
            # 计算仓位
            qty = self.risk.calculate_position_size(price)
            if not self.risk.validate_position(symbol, qty):
                return

            # 执行订单
            order_result = await self.executor.execute_market_order(symbol, signal, qty)
            if order_result['retCode'] == 0:
                await self.executor.set_stop_loss(symbol, price, qty)
                self.risk.update_position(symbol, qty, signal)
                print(f"成功建仓 {symbol} 数量 {qty}")
                
        except Exception as e:
            print(f"交易执行失败: {symbol} - {str(e)}")

if __name__ == "__main__":
    bot = TradingBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("策略手动终止")
