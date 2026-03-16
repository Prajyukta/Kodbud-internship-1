# ============================================================
#   LSTM Stock Price Predictor
# ============================================================

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def build_sequences(data: np.ndarray, seq_len: int):
    """Build (X, y) sequences for LSTM training."""
    X, y = [], []
    for i in range(seq_len, len(data)):
        X.append(data[i - seq_len:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)


def train_lstm(df: pd.DataFrame, forecast_days: int = 30,
               seq_len: int = 60, epochs: int = 25, batch_size: int = 32):
    """
    Train an LSTM model on Close prices.
    Falls back gracefully if TensorFlow is not installed.
    """
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    except ImportError:
        raise ImportError(
            "TensorFlow is required for LSTM. "
            "Install it with: pip install tensorflow"
        )

    prices = df["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(prices)

    # Train/test split
    split   = int(len(scaled) * 0.8)
    train   = scaled[:split]
    test    = scaled[split - seq_len:]   # include lookback

    X_train, y_train = build_sequences(train, seq_len)
    X_test,  y_test  = build_sequences(test,  seq_len)

    # Reshape for LSTM: (samples, timesteps, features)
    X_train = X_train.reshape(-1, seq_len, 1)
    X_test  = X_test.reshape(-1, seq_len, 1)

    # ── Model ─────────────────────────────────────────────────
    model = Sequential([
        Input(shape=(seq_len, 1)),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1),
    ], name="stock_lstm")

    model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
                  loss="mean_squared_error")

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=0),
    ]

    model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=0,
    )

    # ── Evaluate ──────────────────────────────────────────────
    y_pred_scaled = model.predict(X_test, verbose=0)
    y_pred  = scaler.inverse_transform(y_pred_scaled).ravel()
    y_true  = scaler.inverse_transform(y_test.reshape(-1, 1)).ravel()

    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae  = float(mean_absolute_error(y_true, y_pred))
    r2   = float(r2_score(y_true, y_pred))
    mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)

    # ── Future forecast ────────────────────────────────────────
    last_seq = scaled[-seq_len:].reshape(1, seq_len, 1)
    future_preds = []
    for _ in range(forecast_days):
        p = model.predict(last_seq, verbose=0)[0][0]
        future_preds.append(float(scaler.inverse_transform([[p]])[0][0]))
        last_seq = np.roll(last_seq, -1, axis=1)
        last_seq[0, -1, 0] = p

    # ── Dates ──────────────────────────────────────────────────
    test_start   = df.index[split]
    test_dates   = df.index[split:split + len(y_true)].strftime("%Y-%m-%d").tolist()
    train_dates  = df.index[:split].strftime("%Y-%m-%d").tolist()
    train_actual = scaler.inverse_transform(scaled[:split]).ravel().tolist()

    last_date    = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                 periods=forecast_days, freq="B")

    return {
        "model_type": "LSTM Neural Network",
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
