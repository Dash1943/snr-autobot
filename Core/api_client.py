import hmac
import hashlib
import aiohttp
from config.settings import Config

class BybitAPIClient:
    def __init__(self):
        self.session = None
        self.recv_window = 5000

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"X-BAPI-API-KEY": Config.API_KEY},
            timeout=aiohttp.ClientTimeout(total=Config.ORDER_TIMEOUT)
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def _sign(self, params: dict) -> str:
        params.setdefault("recv_window", self.recv_window)
        params["timestamp"] = str(int(time.time()*1000))
        query = "&".join(f"{k}={v}" for k,v in sorted(params.items()))
        return hmac.new(
            Config.API_SECRET.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()

    async def get_balance(self) -> float:
        params = {"accountType": Config.ACCOUNT_TYPE, "coin": Config.TRADE_COIN}
        params["sign"] = await self._sign(params)
        async with self.session.get(
            f"{Config.BASE_URL}/v5/account/wallet-balance",
            params=params
        ) as resp:
            data = await resp.json()
            return float(data['result']['list'][0]['coin'][0]['walletBalance'])

    async def get_symbol_info(self, symbol: str) -> dict:
        params = {"category": "linear", "symbol": symbol}
        params["sign"] = await self._sign(params)
        async with self.session.get(
            f"{Config.BASE_URL}/v5/market/instruments-info",
            params=params
        ) as resp:
            return (await resp.json())['result']['list'][0]

    async def execute_order(self, order: dict) -> dict:
        order.setdefault("category", "linear")
        order["sign"] = await self._sign(order)
        async with self.session.post(
            f"{Config.BASE_URL}/v5/order/create",
            json=order
        ) as resp:
            return await resp.json()
