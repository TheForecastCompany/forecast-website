from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from datetime import timedelta

# ---------------- Load Model & Data ----------------
MODEL_PATH = "mecha_chocolate_sarimax_statsmodels.pkl"
DATA_PATH = "Mecha Chocolate Sales oct2023-jun2025.csv"

df = pd.read_csv(DATA_PATH, parse_dates=["Day"]).set_index("Day")
df = df.resample("W-SUN").sum()
y = df["Total sales"]
model = joblib.load(MODEL_PATH)

# ---------------- Feature Engineering ----------------
def add_holiday_features(idx):
    df_h = pd.DataFrame(index=idx)
    df_h["valentine_season"] = ((idx.month == 2) & (idx.day == 14)).astype(int)
    easter_dates = pd.to_datetime(["2024-03-31", "2025-04-20"])
    df_h["easter_season"] = idx.isin(easter_dates).astype(int)
    df_h["mothersday_season"] = ((idx.month == 5) & (idx.weekday == 6) & (idx.day >= 8) & (idx.day <= 14)).astype(int)
    df_h["christmas_season"] = ((idx.month == 12) & (idx.day >= 24) & (idx.day <= 31)).astype(int)
    df_h["fathersday_season"] = ((idx.month == 6) & (idx.weekday == 6) & (idx.day >= 15) & (idx.day <= 21)).astype(int)
    return df_h

df = df.join(add_holiday_features(df.index))

# ---------------- Flask App ----------------
app = Flask(__name__)

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        forecast_steps = 12
        last_date = df.index[-1]
        future_idx = pd.date_range(start=last_date + timedelta(weeks=1), periods=forecast_steps, freq="W-SUN")
        X_future = add_holiday_features(future_idx)

        fc_res = model.get_forecast(steps=forecast_steps, exog=X_future)
        forecast_values = fc_res.predicted_mean
        safe_estimate = forecast_values * 1.1

        # Calculate historical metrics
        hist_steps = 52
        hist_idx = df.index[-hist_steps:]
        X_hist = df.loc[hist_idx][[
            'valentine_season','easter_season','mothersday_season','christmas_season','fathersday_season'
        ]]
        y_true = y.loc[hist_idx]
        hist_res = model.get_prediction(start=hist_idx[0], end=hist_idx[-1], exog=X_hist)
        hist_mean = hist_res.predicted_mean
        rmse = np.sqrt(mean_squared_error(y_true, hist_mean))
        mae  = mean_absolute_error(y_true, hist_mean)
        mape = np.mean(np.abs((y_true - hist_mean) / y_true)) * 100
        r2   = r2_score(y_true, hist_mean)

        return jsonify({
            "forecast_dates": [str(d.date()) for d in forecast_values.index],
            "forecast_values": [round(float(v), 2) for v in forecast_values],
            "safe_estimate": [round(float(v), 2) for v in safe_estimate],
            "metrics": {
                "rmse": round(rmse, 2),
                "mae": round(mae, 2),
                "mape": round(mape, 2),
                "r2": round(r2, 3)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
