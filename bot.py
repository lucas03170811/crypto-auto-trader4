
import os, time
from datetime import datetime
from binance.client import Client
import pandas as pd
import ta

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key, api_secret)

TRADE_SETTINGS = {
    "spot": {
        "XRPUSDT": {"buy": 0.5, "sell": 0.7, "qty": 20}
    },
    "futures": {
        "BTCUSDT": {"buy": 60000, "sell": 70000, "qty": 0.001},
        "ETHUSDT": {"buy": 3000, "sell": 4000, "qty": 0.01},
        "SOLUSDT": {"buy": 130, "sell": 160, "qty": 1}
    }
}

STOP_LOSS_PCT = 0.05
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

def get_klines(symbol, interval="1m", limit=100):
    data = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    closes = [float(k[4]) for k in data]
    return closes

def get_rsi(symbol):
    closes = get_klines(symbol)
    df = pd.DataFrame({"close": closes})
    rsi = ta.momentum.RSIIndicator(df["close"], window=RSI_PERIOD)
    return rsi.rsi().iloc[-1]

def get_price(symbol):
    return float(client.get_symbol_ticker(symbol=symbol)["price"])

def create_spot_order(symbol, side, qty):
    return client.order_market(symbol=symbol, side=side.upper(), quantity=qty)

def create_futures_order(symbol, side, qty):
    return client.futures_create_order(symbol=symbol, side=side.upper(), type="MARKET", quantity=qty)

def trade_logic(symbol, trade_type, rule):
    try:
        price = get_price(symbol)
        rsi = get_rsi(symbol)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action = "hold"

        if price <= rule["buy"] and rsi < RSI_OVERSOLD:
            action = "buy"
        elif price >= rule["sell"] or price <= rule["buy"] * (1 - STOP_LOSS_PCT) or rsi > RSI_OVERBOUGHT:
            action = "sell"

        print(f"[{now}] {symbol} | 價格: {price:.2f} | RSI: {rsi:.2f} | 動作: {action}")

        if action in ["buy", "sell"]:
            if trade_type == "spot":
                create_spot_order(symbol, action.upper(), rule["qty"])
            else:
                create_futures_order(symbol, action.upper(), rule["qty"])
            print(f"✅ 已下 {trade_type} 市價 {action.upper()} 單: {symbol} 數量: {rule['qty']}")
    except Exception as e:
        print(f"❌ {symbol} 交易錯誤: {e}")

if __name__ == "__main__":
    print("🚀 啟動交易機器人")
print("✅ 讀取 API Key:", api_key)
print("✅ 讀取 API Secret:", "✔️ 有" if api_secret else "❌ 沒有")
    print("📈 自動交易機器人已啟動（RSI + 止損）")
    while True:
        for t_type, symbols in TRADE_SETTINGS.items():
            for sym, rule in symbols.items():
                trade_logic(sym, t_type, rule)
        time.sleep(60)
