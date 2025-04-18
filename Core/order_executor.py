import time
from decimal import Decimal
from config.settings import Config

class OrderExecutor:
    def __init__(self, api_client, risk_controller):
        self.api = api_client
        self.risk = risk_controller
        self.symbol_cache = {}

    async def prepare_symbol_data(self, symbol: str):
        if symbol not in self.symbol_cache or \
           time.time() - self.symbol_cache[symbol]['timestamp'] > Config.SYMBOL_REFRESH:
            
            data = await self.api.get_symbol_info(symbol)
            self.symbol_cache[symbol] = {
                'price_tick': float(data['priceFilter']['tickSize']),
                'min_qty': float(data['lotSizeFilter']['minOrderQty']),
                'timestamp': time.time()
            }

    def _format_price(self, price: float, symbol: str) -> str:
        tick_size = self.symbol_cache[symbol]['price_tick']
        return f"{round(price / tick_size) * tick_size:.{Config.PRICE_PRECISION}f}"

    async def execute_market_order(self, symbol: str, side: str, qty: Decimal):
        await self.prepare_symbol_data(symbol)
        
        if qty < Decimal(str(self.symbol_cache[symbol]['min_qty'])):
            raise ValueError(f"数量低于最小值: {qty} < {self.symbol_cache[symbol]['min_qty']}")

        order = {
            "symbol": symbol,
            "side": "Buy" if side == 1 else "Sell",
            "orderType": "Market",
            "qty": str(qty),
            "timeInForce": "IOC"
        }
        return await self.api.execute_order(order)

    async def set_stop_loss(self, symbol: str, entry_price: float, qty: Decimal):
        stop_price = entry_price * (1 - Config.STOP_LOSS_PCT)
        take_profit = entry_price * (1 + Config.STOP_LOSS_PCT * Config.TAKE_PROFIT_RATIO)
        
        await self.prepare_symbol_data(symbol)
        stop_price = self._format_price(stop_price, symbol)
        take_profit = self._format_price(take_profit, symbol)

        sl_order = {
            "symbol": symbol,
            "side": "Sell",
            "orderType": "Limit",
            "qty": str(qty),
            "price": stop_price,
            "triggerPrice": stop_price,
            "triggerDirection": 1,
            "reduceOnly": True
        }
        tp_order = {
            "symbol": symbol,
            "side": "Sell",
            "orderType": "Limit",
            "qty": str(qty),
            "price": take_profit,
            "reduceOnly": True
        }
        await self.api.execute_order(sl_order)
        await self.api.execute_order(tp_order)
