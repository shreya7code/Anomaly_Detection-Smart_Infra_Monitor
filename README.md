# 🚨 Smart Infra Monitor – Real-Time Anomaly Detection Dashboard

A full-stack observability dashboard that monitors CPU, memory, and I/O usage in real-time and alerts teams on system anomalies using ML and LLMs.

## ✨ Features
- 📈 Live dashboard built with React & D3.js *(coming soon)*
- 🤖 Real-time anomaly detection using Isolation Forest *(in progress)*
- 🔔 Slack/Email alerts for critical incidents *(coming soon)*
- 🧠 GPT-based explanations of anomalies (via OpenAI API) *(optional)*
- ⚙️ Dockerized, deployable on AWS or Render

---

## 💡 Project Purpose

Modern DevOps and ML teams need observability tools that can:
- Continuously monitor infrastructure metrics
- Detect performance anomalies (like CPU spikes or memory leaks)
- Proactively alert and explain issues using AI

This project mimics that setup using open-source tools to build a **miniature Datadog/New Relic**.

---

## ✅ Implemented So Far

### 1. FastAPI Backend with `/ingest` Endpoint

We've implemented a Dockerized FastAPI backend that exposes a `/ingest` endpoint to receive real-time system metrics:

```python
@app.post("/ingest")
async def ingest(request: Request):
    data = await request.json()

    point = (
        Point("system_metrics")
        .field("cpu", float(data["cpu"]))
        .field("memory", float(data["memory"]))
        .field("disk", float(data["disk"]))
        .time(datetime.utcnow(), WritePrecision.NS)
    )

    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

    return {"status": "ok", "received": data}
```

This endpoint recieves JSON payload like
```json
{
  "timestamp": "2025-06-24T16:42:00Z",
  "cpu": 65.2,
  "memory": 53.1,
  "disk": 72.6
}
```
and writes them to influxDB time-series database

2. Dockerized Infrastructure
Using Docker Compose, we orchestrate:

A FastAPI service for data ingestion

A running InfluxDB instance for high-frequency metrics storage
🔧 docker-compose.yml snippet:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - INFLUXDB_URL=http://influxdb:8086
      - INFLUXDB_TOKEN=my-token
      - INFLUXDB_ORG=my-org
      - INFLUXDB_BUCKET=metrics
    depends_on:
      - influxdb

  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=adminpass
      - DOCKER_INFLUXDB_INIT_ORG=my-org
      - DOCKER_INFLUXDB_INIT_BUCKET=metrics
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-token
```

3. One-Off Metric Test Script
You can test the full ingestion pipeline by running:

python
Copy code
```python
# simulate_one_post.py
import requests
from datetime import datetime

payload = {
    "timestamp": datetime.utcnow().isoformat(),
    "cpu": 67.3,
    "memory": 49.8,
    "disk": 71.2
}

res = requests.post("http://localhost:8000/ingest", json=payload)
print("Response:", res.json())
```

🧪 Local Development Setup
```bash
git clone https://github.com/shreya7code/Anomaly_Detection-Smart_Infra_Monitor.git
cd Anomaly_Detection-Smart_Infra_Monitor
docker compose up --build
```

Visit
```arduino
http://localhost:8000
```

To check health:
```bash
curl http://localhost:8000
```

📦 Current Folder Structure
```bash
Anomaly_Detection-Smart_Infra_Monitor/
├── backend/
│   ├── main.py              ← FastAPI app with /ingest endpoint
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml       ← FastAPI + InfluxDB orchestration
└── simulate_one_post.py     ← Test script for ingestion

```