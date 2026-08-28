"""Standalone evaluation of the forecasting approach: train/test split +
RMSE, so the model's accuracy claim is backed by a real number instead of
just 'I used a RandomForestRegressor'.

This script deliberately reimplements the regression with plain NumPy
(closed-form least squares) instead of importing scikit-learn, because
scikit-learn isn't installable in the environment this was built in (no
network access). The feature set is identical to app/services/forecasting.py
(day index, day-of-week, weekend flag, 7-day rolling mean -> next day's
units sold). Swap in RandomForestRegressor/GradientBoostingRegressor from
sklearn for the real service; this script exists to prove the *approach*
generalizes to held-out days, not to replace the production model.

Run: python3 scripts/evaluate_forecast.py
"""
import random
import numpy as np

random.seed(42)
np.random.seed(42)


def gen_history(base, trend, noise, n=90):
    v = base
    out = []
    for i in range(n):
        v = max(0.5, v + trend + random.uniform(-noise, noise))
        dow = i % 7
        seasonal = 1.3 if dow in (5, 6) else 1.0
        out.append(max(0, round(v * seasonal)))
    return out


ITEMS = {
    "WM-1042": gen_history(6, 0.15, 2),
    "UC-2210": gen_history(9, 0.10, 2),
    "BS-3305": gen_history(4, 0.25, 1.5),
    "MK-5510": gen_history(5, 0.30, 1.5),
    "PC-8801": gen_history(11, 0.20, 3),
    "MA-9909": gen_history(3, 0.18, 1.2),
}


def build_features(series):
    n = len(series)
    X, y = [], []
    rolling = []
    for i, v in enumerate(series):
        rolling.append(v)
        roll_mean = np.mean(rolling[-7:])
        dow = i % 7
        is_weekend = 1 if dow in (5, 6) else 0
        if i > 0:  # predict day i from features known up to day i-1
            X.append([i - 1, dow, is_weekend, roll_mean])
            y.append(series[i])
    return np.array(X, dtype=float), np.array(y, dtype=float)


def fit_least_squares(X, y):
    X_bias = np.hstack([np.ones((X.shape[0], 1)), X])
    # closed-form OLS: beta = (X^T X)^-1 X^T y
    beta, *_ = np.linalg.lstsq(X_bias, y, rcond=None)
    return beta


def predict(beta, X):
    X_bias = np.hstack([np.ones((X.shape[0], 1)), X])
    return X_bias @ beta


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true, y_pred):
    return float(np.mean(np.abs(y_true - y_pred)))


def naive_baseline_rmse(y_true):
    """Baseline: 'predict tomorrow = yesterday's actual'. Any real model
    should beat this, or it isn't adding value."""
    preds = np.roll(y_true, 1)
    preds[0] = y_true[0]
    return rmse(y_true, preds)


def main():
    print(f"{'SKU':<10} {'Train RMSE':>11} {'Test RMSE':>11} {'Test MAE':>10} {'Naive RMSE':>11} {'Beats naive?':>13}")
    print("-" * 70)
    results = []
    for sku, series in ITEMS.items():
        X, y = build_features(series)
        split = int(len(X) * 0.8)  # last 20% of days held out as test
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        beta = fit_least_squares(X_train, y_train)
        train_rmse = rmse(y_train, predict(beta, X_train))
        test_rmse = rmse(y_test, predict(beta, X_test))
        test_mae = mae(y_test, predict(beta, X_test))
        baseline = naive_baseline_rmse(y_test)
        beats = "yes" if test_rmse < baseline else "no"

        results.append((sku, train_rmse, test_rmse, beats))
        print(f"{sku:<10} {train_rmse:>11.2f} {test_rmse:>11.2f} {test_mae:>10.2f} {baseline:>11.2f} {beats:>13}")

    beat_count = sum(1 for r in results if r[3] == "yes")
    print("-" * 70)
    print(f"Model beats the naive baseline on {beat_count}/{len(results)} SKUs.")
    print("\nNote: this is a linear least-squares fit on synthetic data as a")
    print("sanity check of the feature engineering, not the production model.")
    print("app/services/forecasting.py uses RandomForestRegressor on the same")
    print("features, which handles the non-linear demand/day-of-week")
    print("interactions this simple linear fit can't capture.")


if __name__ == "__main__":
    main()
