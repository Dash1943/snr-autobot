from decimal import Decimal
from config.settings import Config

class RiskController:
    def __init__(self, api_client):
        self.api = api_client
        self.balance = Decimal('0')
        self.position_book = {}

    async def refresh_balance(self):
        self.balance = Decimal(str(await self.api.get_balance()))

    def calculate_position_size(self, entry_price: float) -> Decimal:
        risk_amount = self.balance * Decimal(str(Config.RISK_PER_TRADE))
        return (risk_amount / Decimal(str(entry_price))).quantize(
            Decimal(f"1e-{Config.QTY_PRECISION}"))

    def validate_position(self, symbol: str, qty: Decimal) -> bool:
        if len(self.position_book) >= Config.MAX_SYMBOLS:
            return False
        existing = sum(p['qty'] for p in self.position_book.values())
        return (existing + qty) * Decimal('1.5') <= self.balance

    def update_position(self, symbol: str, qty: Decimal, side: str):
        self.position_book[symbol] = {
            'qty': qty,
            'side': side,
            'timestamp': time.time()
        }
