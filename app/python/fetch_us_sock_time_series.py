import os
import io
import json
import logging
import requests
from datetime import datetime
from google.cloud import pubsub_v1
from avro.io import BinaryEncoder, DatumWriter
import avro.schema as schema
from google.api_core.exceptions import NotFound
from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AlphaVantageAPIError(Exception):
    """Custom exception for Alpha Vantage API errors."""
    pass

def publish_message_binary(project_id, topic_id, schema_path, messages_data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    try:
        # Read Avro schema from file
        with open(schema_path, "rb") as file:
            avro_schema = schema.parse(file.read())

        # Serialize message data using Avro
        futures = []
        for message_data in messages_data:
            try:
                logging.info(f"Attempting to serialize message data: {message_data}")
                writer = DatumWriter(avro_schema)
                bout = io.BytesIO()
                encoder = BinaryEncoder(bout)
                writer.write(message_data, encoder)
                data = bout.getvalue()
                logging.info(f"Preparing a binary-encoded message:\n{data.decode()}")

                future = publisher.publish(topic_path, data)
                futures.append(future)
            except Exception as e:
                logging.error(f"An unexpected error occurred during serialization: {e}")

            for future in futures:
                try:
                    message_id = future.result()
                    logging.info(f"Published message ID: {message_id}")
                except Exception as e:
                    logging.error(f"Error during publishing: {e}")

    except Exception as e:
        logging.error(f"Error publishing message: {e}")

def fetch_stock_data(api_key, symbol, interval):
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "apikey": api_key,
            "interval": interval,
            "outputsize": "compact"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise AlphaVantageAPIError("Invalid JSON response from Alpha Vantage API.")
        if "Error Message" in data:
            raise AlphaVantageAPIError(f"Alpha Vantage API error: {data['Error Message']}")

        logging.info(f"Successfully fetched data for symbol {symbol}.")
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        raise AlphaVantageAPIError(f"Error connecting to Alpha Vantage API: {e}")
    except AlphaVantageAPIError as e:
        logging.error(f"Alpha Vantage API error: {e}")
        raise
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        return None  # Return None to avoid crashing

def format_stock_data(raw_data):
    if not isinstance(raw_data, dict):
        logging.error("Invalid input: raw_data must be a dictionary.")
        return []

    meta_data = raw_data.get("Meta Data", None)
    time_series = raw_data.get("Time Series (5min)", None)
    if not (time_series and meta_data):
        logging.error("No 'Time Series (5min)' data found in the raw data.")
        return []

    formatted_data = []
    for date, data_point in time_series.items():
        try:
            formatted_data_point = {
                "symbol": meta_data.get("2. Symbol", None),
                "date_time": date,
                "date": datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d"),
                "open": str(data_point.get("1. open", 0)),
                "high": str(data_point.get("2. high", 0)),
                "low": str(data_point.get("3. low", 0)),
                "close": str(data_point.get("4. close", 0)),
                "volume": str(data_point.get("5. volume", 0)),
                "last_refreshed_at": meta_data.get("3. Last Refreshed", None),
                "time_zone": meta_data.get("6. Time Zone", None)
            }
            formatted_data.append(formatted_data_point)
        except Exception as e:
            logging.warning(f"Error formatting data point for date {date}: {e}. Skipping this entry.")
            continue  # Skip to the next entry

    logging.info(f"Formatted {len(formatted_data)} daily stock data points.")
    return formatted_data

def main():
    project_id = "ssh-0001-analytics-ist"
    topic_id = "us_stock_intraday_time_series"
    schema_path = "/content/time_series_intraday_schema.avsc"
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY", "TGH4R6V3P6D14NYI")
    if not api_key:
        logging.error("ALPHAVANTAGE_API_KEY environment variable not set.")
        return

    symbol = "AAPL"
    interval = "5min"

    try:
        raw_data = fetch_stock_data(api_key, symbol, interval)

        # Format the data
        formatted_data = format_stock_data(raw_data)

        if formatted_data:
            print(json.dumps(formatted_data, indent=2))  # Pretty print the JSON output
            # Here, you could publish the formatted_data to Pub/Sub
            publish_message_binary(project_id, topic_id, schema_path, formatted_data)
        else:
            logging.warning("No stock data to output.")

    except AlphaVantageAPIError as e:
        logging.error(f"Failed to process stock data: {e}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    main()
