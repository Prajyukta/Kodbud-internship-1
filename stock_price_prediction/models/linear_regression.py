# ============================================================
#   Linear Regression Stock Predictor
# ============================================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def prepare_features(df: pd.DataFrame, lookback: int = 30):
    """
    Create feature matrix using lag features + technical indicators.
    lookback: number of past days to use as features
    """
    data = df[["Close", "Volume", "Open", "High", "Low"]].copy()

    # Add technical features if present
    for col in ["MA_20", "MA_50", "RSI", "Daily_Return", "BB_upper", "BB_lower"]:
        if col in df.columns:
            data[col] = df[col]

    data.dropna(inplace=True)

    # Lag features for Close price
    for lag in range(1, lookback + 1):
        data[f"lag_{lag}"] = data["Close"].shift(lag)

    data.dropna(inplace=True)
    return data


def train_linear_regression(df: pd.DataFrame, forecast_days: int = 30):
    """
    Train Linear Regression model and predict future prices.
    Returns predictions, metrics, and chart-ready data.
    """
    data = prepare_features(df)

    feature_cols = [c for c in data.columns if c != "Close"]
    X = data[feature_cols].values
    y = data["Close"].values

    # Scale features
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

    # Train/test split (80/20, no shuffle — time series)
    split = int(len(X_scaled) * 0.8)
    X_train, X_test = X_scaled[:split], X_scaled[split:]
    y_train, y_test = y_scaled[:split], y_scaled[split:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predictions on test set
    y_pred_scaled = model.predict(X_test)
    y_pred  = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
    y_true  = scaler_y.inverse_transform(y_test.reshape(-1, 1)).ravel()

    # Metrics
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae  = float(mean_absolute_error(y_true, y_pred))
    r2   = float(r2_score(y_true, y_pred))
    mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)

    # Future forecast — recursive multi-step
    future_preds = _forecast_future(model, scaler_X, scaler_y, data, feature_cols, forecast_days)

    # Full actual vs predicted (aligned)
    test_dates   = data.index[split:].strftime("%Y-%m-%d").tolist()
    train_dates  = data.index[:split].strftime("%Y-%m-%d").tolist()
    train_actual = scaler_y.inverse_transform(y_train.reshape(-1, 1)).ravel().tolist()

    # Build future dates
    last_date    = data.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                 periods=forecast_days, freq="B")  # B = business days

    return {
        "model_type":    "Linear Regression",
        "metrics": {
            "rmse": round(rmse, 4),
            "mae":  round(mae, 4),
            "r2":   round(r2, 4),
            "mape": round(mape, 2),
        },
        "train_dates":   train_dates,
        "train_actual":  [round(float(v), 2) for v in train_actual],
        "test_dates":    test_dates,
        "test_actual":   [round(float(v), 2) for v in y_true],
        "test_pred":     [round(float(v), 2) for v in y_pred],
        "future_dates":  future_dates.strftime("%Y-%m-%d").tolist(),
        "future_pred":   [round(float(v), 2) for v in future_preds],
        "last_price":    round(float(df["Close"].iloc[-1]), 2),
        "next_day_pred": round(float(future_preds[0]), 2) if future_preds else None,
    }


def _forecast_future(model, scaler_X, scaler_y, data, feature_cols, n_days):
    """Recursive multi-step forecast."""
    last_row  = data[feature_cols].iloc[-1].values.copy()
    preds     = []
    close_col = data.columns.get_loc("Close") if "Close" in data.columns else 0

    for _ in range(n_days):
        X_in = scaler_X.transform(last_row.reshape(1, -1))
        p    = scaler_y.inverse_transform(model.predict(X_in).reshape(1, -1))[0][0]
        preds.append(p)
        # Shift lag features
        lag_cols = [c for c in feature_cols if c.startswith("lag_")]
        if lag_cols:
            for i in range(len(lag_cols) - 1, 0, -1):
                idx      = feature_cols.index(lag_cols[i])
                prev_idx = feature_cols.index(lag_cols[i - 1])
                last_row[idx] = last_row[prev_idx]
            last_row[feature_cols.index(lag_cols[0])] = p

    return preds
