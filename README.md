# 🚨 Smart Infra Monitor – Real-Time Anomaly Detection Dashboard

A full-stack observability dashboard that monitors CPU, memory, and I/O usage in real-time and alerts teams on system anomalies using ML. It is a production-ready full-stack observability and anomaly detection system that simulates system metrics, stores them in a time-series database, detects anomalies via ML, and alerts via Slack.


## ✨ Features
- 📈 Live metrics dashboard using React + Chart.js
- 🧐 ML-based anomaly detection with Isolation Forest
- 🔔 Real-time Slack alert integration
- 🚧 Fully dockerized setup (backend, frontend, InfluxDB, simulator)
- ⚙️ End-to-end modular architecture with clean folder structure

---

## 💡 Project Purpose

Modern DevOps and ML teams need observability tools that can:
- Continuously monitor infrastructure metrics
- Detect performance anomalies (like CPU spikes or memory leaks)
- Proactively alert and explain issues using AI

This project mimics that setup using open-source tools to build a **miniature Datadog/New Relic**.

---
## 📊 System Architecture
```text
┌────────────────────┐             ┌─────────────────────┐             ┌────────────────────┐
│  🛰️  Stream Simulator │ ─────POST──▶ │  🚀 FastAPI Backend     │ ─────▶ │  🧠 InfluxDB (TSDB) │
└────────────────────┘             └─────────────────────┘             └────────────────────┘
        │                                   │                                     ▲
        │                                   ▼                                     │
        ▼                         ┌────────────────────┐                         │
  🔍 ML Anomaly Detection         │  💻 React Dashboard │ ◀───────API─────────────┘
        │                         └────────────────────┘
        ▼
  🔔 Slack Alert (via webhook)
```

### 📘 How It Works
Stream Simulator generates fake metrics (CPU, memory, disk) every 3 seconds
Sends a POST request to the FastAPI /ingest endpoint

FastAPI stores the data in InfluxDB, and also:
Detects anomalies using an Isolation Forest model
Triggers Slack alerts when thresholds or ML flags are hit
The React frontend polls the backend's /metrics and /anomalies endpoints

User views real-time graphs and anomaly logs

### Tech Stack
```markdown
| Component | Tech Stack                |
| --------- | ------------------------- |
| Frontend  | React + Chart.js + Vite   |
| Backend   | FastAPI (Python)          |
| Database  | InfluxDB 2.7              |
| ML        | IsolationForest (sklearn) |
| Simulator | Python                    |
| Alerting  | Slack Webhook             |
| Infra     | Docker Compose            |
```

## ✅ Components & Flow

We've implemented a Dockerized FastAPI backend that exposes endpoint to receive real-time system metrics:

### 1. `stream_simulator.py` (Dockerized)

- Generates CPU, memory, and disk values every 3s
- 10% of the time injects anomalous values
- POSTs data to `/ingest` route of FastAPI backend

### 2. FastAPI Backend (Dockerized)

- `/ingest`: Receives metric and stores to InfluxDB
- `/metrics`: Returns last 10 mins of time-series metrics
- `/predict`: Uses IsolationForest to detect anomalies
- `/anomaly`: Logs detected anomaly to InfluxDB
- `/anomalies`: Returns anomaly history (30 hrs)

Also sends alert via Slack webhook if:

- Thresholds are breached (CPU > 85%, etc.)
- ML model detects anomaly

### 3. InfluxDB 2.7

- Stores both normal metrics and detected anomalies
- Accessible at [http://localhost:8086](http://localhost:8086) (Dockerized)

### 4. React Frontend (Dockerized)

- Polls `/metrics` every 5s
- Visualizes data using Chart.js
- Shows anomaly table
- UI polished using Bootstrap

### 5. Slack Alerts

- Real-time alert sent for every anomaly
- Uses webhook URL (in `.env` or `docker-compose.yml`)

---

## 📊 Sample Metric

This endpoint recieves JSON payload like
```json
{
  "timestamp": "2025-06-24T16:42:00Z",
  "cpu": 92.3,
  "memory": 88.1,
  "disk": 95.6
}
```
and writes them to influxDB time-series database

## Run Manually (For Debugging)
⚠️ You must have Python + Node.js + InfluxDB installed locally.

1. Start InfluxDB locally (or via Docker):
```bash
docker run -p 8086:8086 influxdb:2.7
```

2. Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

3. Simulator
```bash
cd simulator
python stream_simulator.py
```

4. Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## Dockerized Infrastructure (Setup)
Why we use docker?
I am running this code with specific python version, OS, InfluxDB installed, etc. But what if this same code doesn't work in a differnt person's system (due to lack of required infrastructure)?
Solution: Dockerize everything.
Docker = A lightweight, virtual computer running inside your real computer.
Therefore, a docker container will have:
1. An Operating system
2. All the required tools
3. All the dependecies
4. Code

Therefore, to maintain the consistency between different platform/environment, it is best to dockerize everything.

1. Clone and navigate:
```bash
git clone https://github.com/shreya7code/Anomaly_Detection-Smart_Infra_Monitor.git
cd Anomaly_Detection-Smart_Infra_Monitor
```

2. Start all the containers:
```bash
docker compose up --build
```

3. Access:
Frontend: [http://localhost:4173]
Backend: [http://localhost:8000]
InfluxDB UI: [http://localhost:8086]


## Folder Structure
```bash
Anomaly_Detection-Smart_Infra_Monitor/
├── backend/             # FastAPI + ML + Slack Alerts
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/            # React + Chart.js UI
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── simulator/           # Fake metrics simulator
│   ├── stream_simulator.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── .env # environment file (Local)
├── docker-compose.yml   # Orchestrates all services
└── README.md
```

## InfluxDB Schema

system_metrics (measurement)
```markdown
| \_time | cpu | memory | disk |
| ------ | --- | ------ | ---- |
```

anomalies (measurement)
```markdown
| \_time | cpu | memory | disk |
| ------ | --- | ------ | ---- |
```

## 🛠️ Environment Setup

Create a .env file in the root directory with the following values:
```env
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=<your-token-here>
INFLUXDB_ORG=my-org
INFLUXDB_BUCKET=metrics
SLACK_WEBHOOK_URL=<your-slack-webhook-url>
```

A running InfluxDB instance for high-frequency metrics storage
🔧 docker-compose.yml snippet:


## 🧠 Anomaly Detection Logic
Model Used:
- IsolationForest from scikit-learn
- Trained on 2 mins of simulated normal metrics

Detection Flow:
- Payload comes in via /predict
- If CPU > 85% (threshold): alert immediately
- Else: run model.predict(X)
- If prediction == -1: mark as anomaly
- Save to DB + Alert Slack

## 🔔 Alerting
Format:
```makefile
ALERT! High metrics detected:
CPU = 92.3% | Mem = 88.1% | Disk = 95.6%
```


## Sample API Testing
```bash
curl http://localhost:8000/metrics
curl http://localhost:8000/anomalies
```


## 📸 Live Dashboard Preview

![Smart Infra Dashboard](./Smart_Infra_Monitor_frontend.png)

> A real-time UI showing live CPU, memory, and disk metrics, with detected anomalies highlighted in red.
