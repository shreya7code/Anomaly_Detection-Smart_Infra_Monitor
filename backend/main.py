from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from influxdb_client import Point
import joblib
import numpy as np
from pydantic import BaseModel
from fastapi_slack import send_slack_alert


app = FastAPI()

class Metrics(BaseModel):
    '''when POST data to the API, 
    payload should look like this in JSON'''
    cpu: float
    memory: float
    disk: float

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

# loading the model
model = joblib.load("isolation_forest_model.pkl")

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


@app.post("/predict")
async def predict_metrics(metrics: Metrics):

    # Adding threshold logic in addition to model prediction
    # as of now the model is predicting too high vales as normal since the model was trained on less data
    # that contained mostly values 30-50. Therefore values 80-100 might be considered as outliers for this model
    # so these are like obvious spikes that it will catch and subtle anomalies according. to patter and data - model will catch
    if metrics.cpu > 85 or metrics.memory > 85 or metrics.disk > 90:
        # send Alert to slack
        send_slack_alert(f"ALERT! High metrics detected: \n"
                         f"CPU = {metrics.cpu}% | Mem={metrics.memory}% | Disk={metrics.disk}%")
        
        return {
        "prediction": "anomaly",
        "reason": "Threshold exceeded",
        "score": None
    }

    #converting incoming metrics to numpy array for the model
    metrics_arr = np.array([[metrics.cpu, metrics.memory, metrics.disk]])

    #prediccting the metrics using the model - Isolation Forest
    pred = model.predict(metrics_arr)[0]
    score = model.decision_function(metrics_arr)[0]
    print(f"Data: {metrics_arr}, Prediction: {pred}, Score: {score}")

    #Translate the prediction above: 1 = Normal; -1 = Anomaly
    if pred == -1:
        send_slack_alert(f"ML Anomaly detected: \n"
                         f"CPU = {metrics.cpu}% | Mem={metrics.memory}% | Disk={metrics.disk}%\n"
                         f"Anomaly Score={score:.4f}")
        
    prediction_label = "anomaly" if pred == -1 else "normal"

    return {
        "prediction": prediction_label,
        "reason": "ML model",
        "score": float(score)
    }



@app.post("/anomaly")
async def save_anomaly(request: Request):
    '''
    This function saves the detected anomaly in the InfluxDB
    '''
    data = await request.json()
    print("Saving anomaly: ", data)

    #Create anomaly Point
    # each of the values are stored in its respective field in the table - anomalies
    point = Point("anomalies") \
        .field("cpu", float(data['cpu'])) \
        .field("memory", float(data['memory'])) \
        .field("disk", float(data['disk'])) \
        .time(data['timestamp'])
    
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(
        bucket=INFLUXDB_BUCKET,
        org=INFLUXDB_ORG,
        record=point
    )

    return {"status": "success"}


@app.get("/anomalies")
def get_anomalies():
    '''
    It queries for 30 days
    Filter for measurement - anomalies (table)
    Convert vertical rows into table format
    Returns the JSON array
    '''
    flux_query = f'''
                    from(bucket: "{INFLUXDB_BUCKET}")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r["_measurement"] == "anomalies")
                    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                    |> keep(columns: ["_time", "cpu", "memory", "disk"])
                '''
    
    result = query_api.query_data_frame(org=INFLUXDB_ORG, query=flux_query)

    if result.empty:
        return []

    return result.to_dict(orient="records")

