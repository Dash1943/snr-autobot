class RiskManager:
    def __init__(self, api_client: BybitAPIClient):
        self.api_client = api_client
        self.coin = Config.BALANCE_COIN  # 新增配置项
        self._equity = 0.0
        self.max_drawdown = 0.0

    async def initialize(self):
        """异步初始化获取初始余额"""
        self._equity = await self.api_client.get_unified_balance(self.coin)
        self.max_drawdown = self._equity

    @property
    def equity(self) -> float:
        """当前账户净值"""
        return self._equity

    async def update_balance(self):
        """更新账户余额"""
        new_balance = await self.api_client.get_unified_balance(self.coin)
        self._equity = new_balance
        self.max_drawdown = min(self.max_drawdown, new_balance)

    # 其余方法保持原样...
