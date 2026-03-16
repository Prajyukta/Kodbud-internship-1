"""
Stock Price Prediction — Flask App
===================================
Run:  python app.py
Open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import traceback

from utils.data_fetcher import (
    fetch_stock_data,
    get_stock_info,
    add_technical_indicators,
    prepare_chart_data,
    load_csv_data,
)
from models.linear_regression import train_linear_regression
from models.lstm_model import train_lstm

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024   # 10 MB upload

POPULAR_TICKERS = [
    {"symbol": "AAPL",  "name": "Apple"},
    {"symbol": "GOOGL", "name": "Alphabet"},
    {"symbol": "MSFT",  "name": "Microsoft"},
    {"symbol": "TSLA",  "name": "Tesla"},
    {"symbol": "AMZN",  "name": "Amazon"},
    {"symbol": "NVDA",  "name": "NVIDIA"},
    {"symbol": "META",  "name": "Meta"},
    {"symbol": "NFLX",  "name": "Netflix"},
]


# ── Pages ─────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", tickers=POPULAR_TICKERS)


# ── API: Fetch & chart stock data ─────────────────────────────
@app.route("/api/stock", methods=["POST"])
def api_stock():
    data   = request.get_json(silent=True) or {}
    ticker = data.get("ticker", "").strip().upper()
    period = data.get("period", "2y")

    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400

    try:
        df   = fetch_stock_data(ticker, period)
        df   = add_technical_indicators(df)
        info = get_stock_info(ticker)
        chart_data = prepare_chart_data(df)

        # Summary stats
        current  = float(df["Close"].iloc[-1])
        prev     = float(df["Close"].iloc[-2])
        change   = current - prev
        change_p = (change / prev) * 100

        return jsonify({
            "ticker":    ticker,
            "info":      info,
            "chart":     chart_data,
            "summary": {
                "current":   round(current, 2),
                "change":    round(change, 2),
                "change_pct": round(change_p, 2),
                "high_52w":  round(float(df["Close"].max()), 2),
                "low_52w":   round(float(df["Close"].min()), 2),
                "avg_vol":   int(df["Volume"].mean()),
                "data_points": len(df),
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── API: Run prediction ───────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
def api_predict():
    data         = request.get_json(silent=True) or {}
    ticker       = data.get("ticker", "").strip().upper()
    period       = data.get("period", "2y")
    model_type   = data.get("model", "lr")      # "lr" or "lstm"
    forecast_days = int(data.get("forecast_days", 30))

    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400

    try:
        df = fetch_stock_data(ticker, period)
        df = add_technical_indicators(df)

        if model_type == "lstm":
            result = train_lstm(df, forecast_days=forecast_days)
        else:
            result = train_linear_regression(df, forecast_days=forecast_days)

        return jsonify({"ticker": ticker, "result": result})

    except ImportError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ── API: Upload CSV ───────────────────────────────────────────
@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported"}), 400

    try:
        import io
        content = file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(content), parse_dates=["Date"], index_col="Date")
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.sort_index(inplace=True)
        df.dropna(inplace=True)
        df = add_technical_indicators(df)
        chart_data = prepare_chart_data(df)

        current  = float(df["Close"].iloc[-1])
        prev     = float(df["Close"].iloc[-2])
        change   = current - prev
        change_p = (change / prev) * 100

        return jsonify({
            "ticker": file.filename.replace(".csv", "").upper(),
            "info":   {"name": file.filename, "currency": "USD"},
            "chart":  chart_data,
            "summary": {
                "current":    round(current, 2),
                "change":     round(change, 2),
                "change_pct": round(change_p, 2),
                "high_52w":   round(float(df["Close"].max()), 2),
                "low_52w":    round(float(df["Close"].min()), 2),
                "avg_vol":    int(df["Volume"].mean()),
                "data_points": len(df),
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
