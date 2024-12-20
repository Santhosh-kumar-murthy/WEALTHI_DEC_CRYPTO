from datetime import datetime, timedelta
import pandas as pd
import pytz


class DataProvider:

    @staticmethod
    def fetch_historical_data(client, symbol, limit=50, interval='1m'):
        # start_date = datetime.utcnow() - timedelta(days=20)  # Fetch data for the last 1 hour
        # start_time = int(start_date.timestamp() * 1000)
        klines = client.klines(symbol=symbol, interval=interval, limit=limit)
        data = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume", "close_time",
            "quote_asset_volume", "number_of_trades", "taker_buy_base_volume",
            "taker_buy_quote_volume", "ignore"
        ])
        data["open_time"] = pd.to_datetime(data["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(
            pytz.timezone("Asia/Kolkata"))  # Replace with your timezone
        data["close_time"] = pd.to_datetime(data["close_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(
            pytz.timezone("Asia/Kolkata"))  # Replace with your timezone
        # Convert OHLC and other numeric columns to numeric types
        numeric_columns = ["open", "high", "low", "close", "volume",
                           "quote_asset_volume", "number_of_trades",
                           "taker_buy_base_volume", "taker_buy_quote_volume"]
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
        data = data.drop(columns=["ignore"])
        return data
