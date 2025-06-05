import os
import io
import json
import logging
import requests
from datetime import datetime
from google.cloud import pubsub_v1
import avro.schema as schema
from avro.io import BinaryEncoder, DatumWriter
from google.pubsub_v1.types import Encoding
from google.api_core.exceptions import NotFound

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
                logging.info(f"Attempting to serialize message data for symbol: {message_data['symbol']}")
                writer = DatumWriter(avro_schema)
                bout = io.BytesIO()
                encoder = BinaryEncoder(bout)
                writer.write(message_data, encoder)
                data = bout.getvalue()
                logging.info(f"Preparing a binary-encoded message for symbol: {message_data['symbol']}")

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


def fetch_stock_data(url, api_function, api_key, symbol, interval):
    try:
        params = {
            "function": api_function,
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
            continue 

    logging.info(f"Formatted {len(formatted_data)} daily stock data points.")
    return formatted_data


def parse_json_config(config_path):
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at path: {config_path}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in configuration file: {e}")
        return None


def main():
    conf_path = os.path.abspath("conf/time_series_intraday_conf.json")
    config = parse_json_config(conf_path)

    project_id = config.get("PROJECT_ID", "ssh-0001-analytics-ist")
    topic_id = config.get("TOPIC_ID", "us_stock_intraday_time_series")
    symbol_list = config.get("SYMBOL_LIST", ["AAPL", "MSFT", "GOOGL"])
    interval = config.get("INTERVAL", "5min")
    api_end_point = config.get("API_END_POINT", "https://www.alphavantage.co/query") 
    function=config.get("FUNCTION", "TIME_SERIES_INTRADAY")


    schema_path = os.path.abspath("schema/time_series_intraday_schema.avsc")
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY", "TGH4R6V3P6D14NYI")
    if not api_key:
        logging.error("ALPHAVANTAGE_API_KEY environment variable not set.")
        return
    for symbol in symbol_list:
        try:
            raw_data = fetch_stock_data(api_end_point, function, api_key, symbol, interval)
            formatted_data = format_stock_data(raw_data)

            if formatted_data:
                publish_message_binary(project_id, topic_id, schema_path, formatted_data)
            else:
                logging.warning("No stock data to output.")
        except AlphaVantageAPIError as e:
            logging.error(f"Failed to process stock data: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred in main: {e}")
    

if __name__ == "__main__":
    main()
