from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from influxdb_client import Point


app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#Connecting to InfluxDB
# This reads from the env or docker env
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")


# main connection to InfluxDB - to send queries and fetch data
client = InfluxDBClient(
    url = INFLUXDB_URL,
    token = INFLUXDB_TOKEN,
    ORG = INFLUXDB_ORG
)
query_api = client.query_api()

@app.get("/")
async def root():
    return {"message": "Smart Infra Monitor Backend Active"}



#This endpoint recieves metrics sent from the simulator and saves it in the InfluxDB
@app.post("/ingest")
async def ingest(request: Request):
    data = await request.json()
    print("Received data:", data)
    
    # Create a new InfluxDB dataPoint in measurements = "systen_metrics" and adding fields for cpi, mem, and disk
    point = Point("system_metrics") \
        .field("cpu", float(data["cpu"])) \
        .field("memory", float(data["memory"])) \
        .field("disk", float(data["disk"])) \
        .time(data["timestamp"])

    # Writing it into InfluxDB
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(
        bucket=INFLUXDB_BUCKET,
        org=INFLUXDB_ORG,
        record=point
    )

    print("✅ Successfully written to InfluxDB!")

    return {"status": "success", "timestamp": datetime.utcnow().isoformat()}



@app.get("/metrics")
def get_metrics():
    # return {"status": "working"}
    """
    reads from 'metrics' bucket
    fetches the last 10 min
    filters only "system_metrics" measurement
    pivot - converts vertical data to table format - cpu, memory and disk in columns
    sort - data is time-ordered
    """

    flux_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -10m)
        |> filter(fn: (r) => r["_measurement"] == "system_metrics")
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> keep(columns: ["_time", "cpu", "memory", "disk"])
    '''
    # flux_query = f'''
    # from(bucket: "{INFLUXDB_BUCKET}")
    # |> range(start: -5m)
    # |> filter(fn: (r) => r._measurement == "system_metrics")
    # '''



    result = query_api.query_data_frame(org=INFLUXDB_ORG, query=flux_query)
    print('result ---------- ', result)
    if result.empty:
        return {"message": "No data found"}
    
    return {
        "timestamps": result["_time"].astype(str).tolist(),
        "cpu": result["cpu"].tolist(),
        "memory": result["memory"].tolist(),
        "disk": result["disk"].tolist()
    }


