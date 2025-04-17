class ExchangeClient:
    def get_strongest_symbols(self, top_n=5):
        return ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"][:top_n]

    def get_current_price(self, symbol):
        return 100.0  # 模擬價格

    def calculate_position_size(self, capital, price, leverage):
        return (capital * leverage) / price

    def place_long_order(self, symbol, size, leverage):
        print(f"模擬下單：{symbol} 倉位：{size} 槓桿：{leverage}")
        return "ORDER123"

    def track_position_with_trailing_stop(self, symbol, order_id):
        print(f"{symbol} 進行移動停利監控中...")
