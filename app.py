from flask import Flask, request
from stable_baselines3 import PPO
from pybit import HTTP
from telegram import Bot
import numpy as np, pandas as pd, os, logging
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
API_KEY    = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
BOT_TOKEN  = os.getenv("TELEGRAM_TOKEN")
CHAT_ID    = os.getenv("TELEGRAM_CHAT_ID")

# 初始化 Bybit 客戶端與 Telegram Bot
client = HTTP("https://api.bybit.com", api_key=API_KEY, api_secret=API_SECRET)
bot    = Bot(token=BOT_TOKEN)
model  = PPO.load("models/ppo_wave_bot_snr")

# Logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

def send_telegram(msg: str):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        logging.error(f"Telegram 發送失敗: {e}")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data   = request.json
        symbol = data['ticker']
        qty_p  = float(data.get('qty_percent', 5))

        # 取得最新 60 根 1h K 線
        res = client.query_kline(symbol=symbol, interval="60", limit=60)
        df  = pd.DataFrame(res['result'])

        # 計算指標
        df['ema20']   = df['close'].ewm(span=20).mean()
        df['ema60']   = df['close'].ewm(span=60).mean()
        df['rsi14']   = df['close'].rolling(14).apply(lambda x: (x.diff()>0).sum()/14*100)
        df['atr14']   = (df['high'] - df['low']).rolling(14).mean()
        df['resist']  = df['high'].rolling(50).max()
        df['support'] = df['low'].rolling(50).min()

        latest = df.iloc[-1]
        obs = np.array([
            latest['close'], latest['ema20'], latest['ema60'],
            latest['rsi14'], latest['atr14'],
            (latest['close']-latest['support'])/latest['support'],
            (latest['resist']-latest['close'])/latest['close'],
        ], dtype=np.float32)

        action, _ = model.predict(obs, deterministic=True)
        side_map  = {1: "Buy", 2: "Sell", 0: None}
        side      = side_map.get(action)

        if side:
            resp = client.place_active_order(
                symbol=symbol,
                side=side,
                order_type="Market",
                qty=qty_p * 0.01,
                time_in_force="GoodTillCancel"
            )
            msg = (
                f"📈 訊號: {symbol} {side}\n"
                f"價格: {latest['close']:.4f}\n"
                f"手數: {qty_p}%\n"
                f"API 回應: {resp.get('ret_msg', 'OK')}"
            )
            send_telegram(msg)
            logging.info(msg)
        return {"status": "ok", "signal": side}

    except Exception as e:
        err = f"❌ 錯誤: {e}"
        logging.exception(err)
        send_telegram(err)
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
