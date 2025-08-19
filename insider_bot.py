import requests
import time
import json
import os
from datetime import datetime, timedelta

BOT_TOKEN = "8216193424:AAHtDkN3ibr-jyDSCo7ERoqnY3vKdjvzCnA"
CHAT_ID = "5733112110"
FINNHUB_TOKEN = "d2hlsahr01qv0ma89lo0d2hlsahr01qv0ma89log"

SENT_FILE = "sent.json"

if not os.path.exists(SENT_FILE):
    with open(SENT_FILE, "w") as f:
        json.dump([], f)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=payload)

def load_sent():
    with open(SENT_FILE, "r") as f:
        return set(json.load(f))

def save_sent(sent_ids):
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent_ids), f)

def get_symbols(limit=2000):
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_TOKEN}"
    r = requests.get(url).json()
    symbols = [x["symbol"] for x in r if x.get("type")=="Common Stock"][:limit]
    return symbols

def check_insider(symbol, sent_ids):
    url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={symbol}&token={FINNHUB_TOKEN}"
    r = requests.get(url).json()
    for d in r.get("data", []):
        if d.get("transactionCode")=="P":
            filing_date = datetime.strptime(d['filingDate'], "%Y-%m-%d")
            if filing_date < datetime.now() - timedelta(days=3):
                continue
            uid = f"{d['symbol']}_{d['filingDate']}_{d['name']}_{d['share']}"
            if uid not in sent_ids:
                msg = (f"📢 內部人買進通知\n"
                       f"公司: {d['symbol']}\n"
                       f"姓名: {d['name']}\n"
                       f"職位: {d['position']}\n"
                       f"數量: {d['share']} 股\n"
                       f"價格: ${d['price']}\n"
                       f"日期: {d['filingDate']}")
                send_telegram(msg)
                sent_ids.add(uid)

def main():
    sent_ids = load_sent()
    symbols = get_symbols(limit=2000)
    batch_size = 60
    while True:
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            for symbol in batch:
                try:
                    check_insider(symbol, sent_ids)
                except:
                    pass
                time.sleep(1)
            save_sent(sent_ids)
            time.sleep(60)

if __name__ == "__main__":
    main()
