import time
from flask import Flask, jsonify, render_template
import yfinance as yf

app = Flask(__name__)

TICKERS = ["AMZN", "AAPL", "MSFT", "GOOGL", "NVDA"]
CACHE_SECONDS = 900  # 15 min, keeps Yahoo from throttling you
_cache = {"ts": 0, "data": []}

def fetch_stocks():
    results = []
    for t in TICKERS:
        closes = yf.Ticker(t).history(period="2mo")["Close"].tail(30)
        if closes.empty:
            continue
        prices = [round(float(p), 2) for p in closes]
        results.append({
            "ticker": t,
            "price": prices[-1],
            "prices": prices,
            "dates": [d.strftime("%b %d") for d in closes.index],
            "pct_change": round((prices[-1] / prices[0] - 1) * 100, 2),
        })
        time.sleep(0.5)
    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/api/stocks")
def stocks():
    if time.time() - _cache["ts"] > CACHE_SECONDS or not _cache["data"]:
        _cache["data"] = fetch_stocks()
        _cache["ts"] = time.time()
    return jsonify(_cache["data"])

if __name__ == "__main__":
    app.run(debug=True)
