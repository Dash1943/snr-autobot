import os

class Config:
    # API 配置
    API_KEY = os.getenv("BYBIT_API_KEY")
    API_SECRET = os.getenv("BYBIT_API_SECRET")
    BASE_URL = "https://api.bybit.com"
    
    # 账户配置
    ACCOUNT_TYPE = "UNIFIED"
    TRADE_COIN = "USDT"
    
    # 策略参数
    RISK_PER_TRADE = 0.02  # 单笔交易风险比例
    MAX_LEVERAGE = 15
    STOP_LOSS_PCT = 0.03
    TAKE_PROFIT_RATIO = 2.0  # 止盈/止损比例
    
    # 订单参数
    ORDER_TIMEOUT = 30
    PRICE_PRECISION = 4
    QTY_PRECISION = 3
    
    # 系统参数
    BALANCE_REFRESH = 300  # 余额刷新间隔(秒)
    SYMBOL_REFRESH = 3600  # 交易对信息刷新间隔
    MAX_SYMBOLS = 15       # 最大监控交易对数
