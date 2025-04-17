import time
import schedule
import threading
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BYBIT_API_KEY, BYBIT_API_SECRET
from exchange_client import ExchangeClient
from snr_strategy import SnrStrategy
from telegram_notifier import send_telegram_message

# 初始化
bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
client = ExchangeClient(BYBIT_API_KEY, BYBIT_API_SECRET)
strategy = SnrStrategy()

# 啟動訊息
send_telegram_message("SNR 自動交易機器人已啟動（最終版）")

# 狀態回傳
def status(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="目前策略正在正常運作中，等待突破條件...")

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="歡迎使用 SNR 翻倍交易機器人！可用指令：/status")

dispatcher.add_handler(CommandHandler("status", status))
dispatcher.add_handler(CommandHandler("start", start))

updater.start_polling()

# 每日自動重啟
schedule.every().day.at("00:00").do(lambda: send_telegram_message("[自動通知] 策略將重啟中..."))
schedule.every().day.at("00:01").do(lambda: exit())

# 策略主邏輯

def run_strategy_loop():
    while True:
        try:
            top_symbols = client.get_strongest_symbols(top_n=8)
            trade_symbols = top_symbols[2:8]  # 僅取第3~8名強勢幣

            for symbol in trade_symbols:
                if strategy.check_multi_timeframe_breakout(symbol):
                    price = client.get_current_price(symbol)
                    qty = client.calculate_position_size(0.05, price, 15)  # 每次 5% 資金, 15 倍槓桿
                    order_id = client.place_long_order(symbol, qty, 15)
                    send_telegram_message(f"突破進場：{symbol} 開多倉 成交價 {price}")
                    client.track_position_with_trailing_stop(symbol, order_id)

        except Exception as e:
            send_telegram_message(f"策略異常：{e}")
        time.sleep(60)

# 平行執行策略 + 排程
threading.Thread(target=run_strategy_loop).start()

while True:
    schedule.run_pending()
    time.sleep(1)
