from telegram_notifier import send_telegram_message
from snr_strategy import SnrStrategy
from exchange_client import ExchangeClient
import time

send_telegram_message("SNR 自動交易機器人已啟動（翻倍特化版）")

client = ExchangeClient()
strategy = SnrStrategy()

capital = 100
leverage = 3
interval = 60

while True:
    try:
        top_symbols = client.get_strongest_symbols(top_n=5)
        for symbol in top_symbols:
            if strategy.check_multi_timeframe_breakout(symbol):
                entry_price = client.get_current_price(symbol)
                position_size = client.calculate_position_size(capital, entry_price, leverage)
                order_id = client.place_long_order(symbol, position_size, leverage)
                send_telegram_message(f"突破進場：{symbol} 開多倉 成交價 {entry_price}")
                client.track_position_with_trailing_stop(symbol, order_id)
    except Exception as e:
        send_telegram_message(f"機器人錯誤：{e}")
    time.sleep(interval)
