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
import os
import time
import schedule
from telegram_notifier import send_telegram_message

# 啟動通知
send_telegram_message("SNR 自動交易機器人啟動！")

# 每日重啟指令
schedule.every().day.at("00:00").do(lambda: os.system("reboot"))

# Telegram 指令處理
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def status(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="機器人運作正常。")

dispatcher.add_handler(CommandHandler("status", status))

updater.start_polling()

# 主迴圈
while True:
    schedule.run_pending()
    time.sleep(1)
