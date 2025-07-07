from influxdb_client import InfluxDBClient
import pandas as pd

# connecting to InfluxDB
client = InfluxDBClient(
    url="http://localhost:8086",
    token="my-token",
    org="my-org"
)

query_api = client.query_api()

# Write your Flux query
flux_query = '''
from(bucket: "metrics")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "system_metrics")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

# Run query → returns DataFrame
result = query_api.query_data_frame(org="my-org", query=flux_query)

# Clean up the dataframe
df = result.rename(columns={"_time": "timestamp"})
df["timestamp"] = pd.to_datetime(df["timestamp"])

print(df.head())


df.to_csv("training_data_InfluxDB_metrics.csv", index=False)
print("✅ Data saved to training_data_InfluxDB_metrics.csv")
