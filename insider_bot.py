import requests
import time
from datetime import datetime, timedelta

# 你的設定
BOT_TOKEN = "8216193424:AAHtDkN3ibr-jyDSCo7ERoqnY3vKdjvzCnA"
CHAT_ID = "5733112110"
FINNHUB_TOKEN = "d2hlsahr01qv0ma89lo0d2hlsahr01qv0ma89log"

# 傳訊息到 Telegram
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

# 抓 Finnhub 的全美股內部人交易
def check_all_insider_trades():
    today = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")  # 最近 3 天
    url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol=&from={start_date}&to={today}&token={FINNHUB_TOKEN}"

    try:
        r = requests.get(url)
        data = r.json()

        if "data" in data:
            for trade in data["data"]:
                if trade.get("transactionCode") == "P":  # P = Purchase
                    price = trade.get("transactionPrice", 0) or 0
                    shares = trade.get("share", 0) or 0
                    total_value = price * shares

                    # 只推播金額 >= $100,000 的交易
                    if total_value >= 100000:
                        msg = (
                            f"🚨 Insider Buy Alert\n"
                            f"股票: {trade.get('symbol')}\n"
                            f"人物: {trade.get('name')}\n"
                            f"職位: {trade.get('position')}\n"
                            f"數量: {shares} 股\n"
                            f"單價: ${price}\n"
                            f"總金額: ${total_value:,.0f}\n"
                            f"日期: {trade.get('transactionDate')}"
                        )
                        send_telegram(msg)
    except Exception as e:
        print("Finnhub Error:", e)

# 主程式
def main():
    while True:
        check_all_insider_trades()
        time.sleep(3600)  # 每小時檢查一次

if __name__ == "__main__":
    send_telegram("🚀 BOT 已經在 Railway 上跑起來！（監控全美股內部人大額買進 ≥ $100K）")
    main()
