# server/huggingface_forecast.py
from gradio_client import Client
import sys
import json

def get_forecast(date_str):
    client = Client("The-Forecast-Company/MechaChocolateSARIMAX")
    result = client.predict(
        date_str=date_str,
        api_name="/forecast_lookup"
    )
    return result

if __name__ == "__main__":
    date_str = sys.argv[1]  # Read date from command line
    forecast = get_forecast(date_str)
    print(json.dumps(forecast))  # Return JSON so Node.js can parse it
