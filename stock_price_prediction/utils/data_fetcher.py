# ============================================================
#   Stock Data Fetcher — Yahoo Finance + CSV support
# ============================================================

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def fetch_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    period options: 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    stock = yf.Ticker(ticker.upper())
    df = stock.history(period=period)

    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}'. Check the symbol.")

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)  # remove timezone
    df.dropna(inplace=True)
    return df


def load_csv_data(filepath: str) -> pd.DataFrame:
    """
    Load stock data from a CSV file.
    Expected columns: Date, Open, High, Low, Close, Volume
    """
    df = pd.read_csv(filepath, parse_dates=["Date"], index_col="Date")
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.sort_index(inplace=True)
    df.dropna(inplace=True)
    return df


def get_stock_info(ticker: str) -> dict:
    """Fetch basic company info from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker.upper())
        info  = stock.info
        return {
            "name":     info.get("longName", ticker.upper()),
            "sector":   info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", "N/A"),
            "market_cap": info.get("marketCap", None),
            "pe_ratio":   info.get("trailingPE", None),
            "52w_high":   info.get("fiftyTwoWeekHigh", None),
            "52w_low":    info.get("fiftyTwoWeekLow", None),
        }
    except Exception:
        return {"name": ticker.upper(), "sector": "N/A", "currency": "USD"}


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add moving averages and RSI to the dataframe."""
    df = df.copy()

    # Moving averages
    df["MA_20"]  = df["Close"].rolling(window=20).mean()
    df["MA_50"]  = df["Close"].rolling(window=50).mean()
    df["MA_200"] = df["Close"].rolling(window=200).mean()

    # Bollinger Bands
    rolling_std     = df["Close"].rolling(window=20).std()
    df["BB_upper"]  = df["MA_20"] + (rolling_std * 2)
    df["BB_lower"]  = df["MA_20"] - (rolling_std * 2)

    # RSI (14-period)
    delta     = df["Close"].diff()
    gain      = delta.clip(lower=0).rolling(14).mean()
    loss      = (-delta.clip(upper=0)).rolling(14).mean()
    rs        = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Daily return %
    df["Daily_Return"] = df["Close"].pct_change() * 100

    return df


def prepare_chart_data(df: pd.DataFrame) -> dict:
    """Convert dataframe to JSON-serialisable chart data."""
    df = df.dropna(subset=["Close"])

    dates = df.index.strftime("%Y-%m-%d").tolist()

    result = {
        "dates":   dates,
        "close":   [round(float(v), 2) for v in df["Close"]],
        "open":    [round(float(v), 2) for v in df["Open"]],
        "high":    [round(float(v), 2) for v in df["High"]],
        "low":     [round(float(v), 2) for v in df["Low"]],
        "volume":  [int(v) for v in df["Volume"]],
    }

    for col in ["MA_20", "MA_50", "MA_200", "BB_upper", "BB_lower", "RSI", "Daily_Return"]:
        if col in df.columns:
            result[col.lower()] = [
                round(float(v), 4) if pd.notna(v) else None
                for v in df[col]
            ]

    return result
