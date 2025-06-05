bq mk \
    --table \
    --schema stock_data_schema.json \
    --time_partitioning_type=DAY \
    --time_partitioning_field=date \
    --clustering_fields=symbol \
    ssh-0001-analytics-ist.us_stock_time_series.time_series_intraday
