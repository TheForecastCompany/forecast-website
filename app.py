import gradio as gr
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import json
import os
from datetime import timedelta
import plotly.graph_objects as go
from scipy import stats

# --------------- CONFIG ---------------
EXPORT_DIR = "models"
CSV_PATH = "Wanda_Sales_2023-May2025.csv"
N_WEEKS_FORECAST = 16   # 4 months forecast horizon
DATE_FORMAT = "%m/%d/%Y"

# --------------- LOAD ARTIFACTS ---------------
sarimax_model = joblib.load(os.path.join(EXPORT_DIR, "sarimax_model.pkl"))
xgb_main = xgb.XGBRegressor()
xgb_main.load_model(os.path.join(EXPORT_DIR, "xgb_main.json"))

quantiles = joblib.load(os.path.join(EXPORT_DIR, "quantiles.pkl"))
xgb_hol_models = {}
for q in quantiles:
    mdl = xgb.XGBRegressor()
    mdl.load_model(os.path.join(EXPORT_DIR, f"xgb_hol_model_{q}.json"))
    xgb_hol_models[q] = mdl

sarimax_columns = joblib.load(os.path.join(EXPORT_DIR, "sarimax_columns.pkl"))
xgb_columns = joblib.load(os.path.join(EXPORT_DIR, "xgb_columns.pkl"))

report_json = os.path.join(EXPORT_DIR, "model_report.json")
if os.path.exists(report_json):
    with open(report_json, "r") as f:
        report = json.load(f)
else:
    report = {}

# --------------- EXOG FEATURE ENGINEERING ---------------
def add_time_exog(idx, include_spike_flags=False):
    df_h = pd.DataFrame(index=idx)
    df_h['week_of_year'] = idx.isocalendar().week.astype(int)
    df_h['month'] = idx.month.astype(int)
    df_h['year'] = idx.year.astype(int)
    df_h['weekend'] = (idx.weekday >= 5).astype(int)
    df_h['valentines_day'] = ((idx.month == 2) & (idx.day == 14)).astype(int)
    df_h['mothers_day'] = ((idx.month == 5) & (idx.weekday == 6) & (idx.day >= 7) & (idx.day <= 13)).astype(int)
    df_h['fathers_day'] = ((idx.month == 6) & (idx.weekday == 6) & (idx.day >= 15) & (idx.day <= 21)).astype(int)
    df_h['independence_day'] = ((idx.month == 7) & (idx.day == 4)).astype(int)
    df_h['thanksgiving'] = ((idx.month == 11) & (idx.weekday == 3) & (idx.day >= 23) & (idx.day <= 29)).astype(int)
    df_h['christmas'] = ((idx.month == 12) & (idx.day == 25)).astype(int)
    springs = {
        "valentines_day": pd.Timestamp("2024-02-14"),
        "mothers_day": pd.Timestamp("2024-05-12"),
        "fathers_day": pd.Timestamp("2024-06-16"),
    }
    for name, dt in springs.items():
        df_h[f"{name}_pre"] = ((idx >= dt - timedelta(days=14)) & (idx < dt)).astype(int)
        df_h[f"{name}_post"] = ((idx > dt) & (idx <= dt + timedelta(days=14))).astype(int)
    for h in ['valentines_day', 'mothers_day', 'fathers_day',
              'independence_day', 'thanksgiving', 'christmas']:
        df_h[f"{h}_x_week"] = df_h[h] * df_h['week_of_year']
        df_h[f"{h}_x_month"] = df_h[h] * df_h['month']
    if include_spike_flags:
        df_h['spike_high'] = 0.0
        df_h['spike_med'] = 0.0
    return df_h.astype(float)

# --------------- LOAD DATA & PREPARE ---------------
raw_df = pd.read_csv(CSV_PATH)
raw_df['Date'] = pd.to_datetime(raw_df['Date'], format=DATE_FORMAT)
raw_df.set_index('Date', inplace=True)
df_weekly = raw_df.resample('W-SUN').sum()
y_hist = df_weekly['Gross Sales']

# --------------- PRECOMPUTE FORECAST AT STARTUP ---------------
def compute_forecast():
    last_date = df_weekly.index[-1]
    future_idx = pd.date_range(last_date + timedelta(days=1), periods=N_WEEKS_FORECAST, freq='W-SUN')
    full_idx = df_weekly.index.append(future_idx)

    exog_sarimax_full = add_time_exog(full_idx)
    exog_xgb_full = add_time_exog(full_idx, include_spike_flags=True)
    exog_sarimax_full = exog_sarimax_full[sarimax_columns]
    exog_xgb_full = exog_xgb_full[xgb_columns]

    # Prepare SARIMAX exog specifically for forecast
    exog_forecast = exog_sarimax_full.loc[future_idx]

    # SARIMAX forecast with exog
    base_forecast = sarimax_model.get_forecast(steps=N_WEEKS_FORECAST, exog=exog_forecast)
    base_forecast_mean = base_forecast.predicted_mean

    holiday_cols = ['valentines_day', 'mothers_day', 'fathers_day',
                    'independence_day', 'thanksgiving', 'christmas']
    is_hol_future = exog_xgb_full.loc[future_idx][holiday_cols].any(axis=1).values

    # XGBoost residual predictions
    def blended_preds(exog_block, is_holiday):
        preds = {}
        for q in quantiles:
            preds[q] = np.where(is_holiday,
                                xgb_hol_models[q].predict(exog_block),
                                xgb_main.predict(exog_block))
        return preds

    blend = blended_preds(exog_xgb_full.loc[future_idx], is_hol_future)
    full_preds = {}
    for q in quantiles:
        full_preds[q] = base_forecast_mean.values + blend[q]

    # Create DataFrame: Only median and buffer
    df_fcast = pd.DataFrame({
        "median": full_preds[0.5],
    }, index=future_idx)

    # Add Safe Buffer Column (1.25x)
    df_fcast["safe_buffer_1_25x"] = df_fcast["median"] * 1.25

    # Round to nearest dollar
    df_fcast = df_fcast.round(0).astype(int)

    # Build Plotly Figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y_hist.index, y=y_hist.values,
                             mode='lines', name='Historical Sales'))
    fig.add_trace(go.Scatter(
        x=df_fcast.index,
        y=df_fcast['median'],
        mode='lines',
        name='Forecast Median'
    ))
    # Add Safe Buffer Line
    fig.add_trace(go.Scatter(
        x=df_fcast.index,
        y=df_fcast['safe_buffer_1_25x'],
        mode='lines',
        name='Safe Buffer (1.25x)',
        line=dict(dash='dot', color='orange')
    ))

    fig.update_layout(
        title="Restaurant Sales Forecast (next 4 months)",
        xaxis_title="Week",
        yaxis_title="Sales ($)",
        hovermode="x unified"
    )

    metrics_str = "### Historical Model Performance\n"
    for stage, vals in report.items():
        metrics_str += f"**{stage}**<br>"
        for metric, val in vals.items():
            metrics_str += f"- {metric}: {val:.2f}<br>"
        metrics_str += "<br>"

    return fig, metrics_str, df_fcast

precomputed_fig, precomputed_metrics, df_forecast = compute_forecast()

# Helper: snap a date to nearest past Sunday (week start)
def get_nearest_sunday(date_obj):
    weekday = date_obj.weekday()
    sunday = date_obj - timedelta(days=(weekday + 1) % 7)
    return pd.Timestamp(sunday.date())

def lookup_hist_sales(date_str):
    if not date_str:
        return "Please enter a date (YYYY-MM-DD)."
    try:
        date = pd.to_datetime(date_str)
        date_sun = get_nearest_sunday(date)
        if date_sun in y_hist.index:
            sales = y_hist.loc[date_sun]
            return f"Historical Sales on week starting {date_sun.date()}: ${sales:,.0f}"
        else:
            return f"No historical data for week starting {date_sun.date()}"
    except Exception:
        return "Invalid date format. Use YYYY-MM-DD."

def lookup_forecast(date_str):
    if not date_str:
        return "Please enter a date (YYYY-MM-DD)."
    try:
        date = pd.to_datetime(date_str)
        date_sun = get_nearest_sunday(date)
        if date_sun in df_forecast.index:
            median = df_forecast.loc[date_sun, "median"]
            buffer_val = df_forecast.loc[date_sun, "safe_buffer_1_25x"]
            return (f"Forecast median for week starting {date_sun.date()}: ${median:,.0f}\n"
                    f"Safe buffer (1.25x): ${buffer_val:,.0f}")
        else:
            return f"No forecast data for week starting {date_sun.date()}"
    except Exception:
        return "Invalid date format. Use YYYY-MM-DD."

def generate_diagnostics():
    residuals = y_hist - sarimax_model.fittedvalues

    # Residuals over time
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=y_hist.index, y=residuals, mode='lines', name='Residuals'))
    fig_time.update_layout(title="Residuals Over Time", xaxis_title="Date", yaxis_title="Residual")

    # Histogram
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=residuals, nbinsx=30, name="Residuals"))
    fig_hist.update_layout(title="Histogram of Residuals")

    # Q-Q Plot (Points Only)
    qq_data = stats.probplot(residuals, dist="norm")
    theoretical = qq_data[0][0]
    ordered_resid = qq_data[0][1]
    fig_qq = go.Figure()
    fig_qq.add_trace(go.Scatter(x=theoretical, y=ordered_resid, mode='markers', name='Residuals'))
    fig_qq.update_layout(title="Q-Q Plot", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles")

    return fig_time, fig_hist, fig_qq


# --------------- GRADIO UI ---------------
with gr.Blocks() as demo:
    gr.Markdown("# 🍽️ Restaurant Sales Forecast Dashboard")
    gr.Markdown("Explore historical sales data, future forecasts, and performance diagnostics.")

    with gr.Tabs():
        # Tab 1: Forecast Overview
        with gr.Tab("📈 Forecast Overview"):
            horizon_slider = gr.Slider(4, 52, value=N_WEEKS_FORECAST, step=4, label="Forecast Horizon (Weeks)")
            reforecast_btn = gr.Button("🔁 Generate Forecast")
            forecast_plot = gr.Plot(label="Sales Forecast")
            forecast_table = gr.Dataframe(label="Forecast Data Table", interactive=False)
            summary_metrics = gr.Markdown(label="Model Performance Summary")

            def recompute_forecast(horizon):
                global N_WEEKS_FORECAST
                N_WEEKS_FORECAST = horizon
                fig, metrics, df_fcast = compute_forecast()
                return fig, df_fcast.reset_index().rename(columns={"index": "Week"}), metrics

            reforecast_btn.click(recompute_forecast, inputs=[horizon_slider],
                                 outputs=[forecast_plot, forecast_table, summary_metrics])
        

        # Tab 2: Lookup
        with gr.Tab("🔍 Lookup Tools"):
            with gr.Row():
                with gr.Column():
                    hist_date = gr.Textbox(label="Date to Lookup (Historical) YYYY-MM-DD")
                    hist_out = gr.Textbox(label="Historical Sales", interactive=False)
                    hist_date.change(lookup_hist_sales, inputs=[hist_date], outputs=[hist_out])
                with gr.Column():
                    fcast_date = gr.Textbox(label="Date to Lookup (Forecast) YYYY-MM-DD")
                    fcast_out = gr.Textbox(label="Forecast Sales", interactive=False)
                    fcast_date.change(lookup_forecast, inputs=[fcast_date], outputs=[fcast_out])

        with gr.Tab("🛠️ Diagnostics & Residuals"):
            diag_btn = gr.Button("Generate Residual Diagnostics")
            diag_plot_time = gr.Plot(label="Residuals Over Time")
            diag_plot_hist = gr.Plot(label="Histogram of Residuals")
            diag_plot_qq = gr.Plot(label="Q-Q Plot")

            def load_diagnostics():
                return generate_diagnostics()

            diag_btn.click(load_diagnostics, outputs=[diag_plot_time, diag_plot_hist, diag_plot_qq])


        # Tab 4: Export
        with gr.Tab("📤 Export Data"):
            download_forecast_btn = gr.Button("Download Forecast CSV")
            download_hist_btn = gr.Button("Download Historical CSV")
            forecast_file_out = gr.File(label="Download Forecast")
            hist_file_out = gr.File(label="Download Historical")

            def export_forecast():
                path = "forecast_export.csv"
                df_forecast.to_csv(path)
                return path

            def export_hist():
                path = "historical_export.csv"
                df_weekly.to_csv(path)
                return path

            download_forecast_btn.click(export_forecast, outputs=[forecast_file_out])
            download_hist_btn.click(export_hist, outputs=[hist_file_out])

if __name__ == "__main__":
    demo.launch()
