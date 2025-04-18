async def get_unified_balance(self, coin: str = "USDT") -> float:
    """获取统一账户余额"""
    params = await self._sign_request({
        "accountType": "UNIFIED",
        "coin": coin
    })
    try:
        response = await self.session.get(
            f"{Config.BASE_URL}/v5/account/wallet-balance",
            params=params
        )
        data = await response.json()
        return float(data['result']['list'][0]['coin'][0]['walletBalance'])
    except (KeyError, IndexError) as e:
        print(f"余额解析失败: {e}")
        return 0.0
