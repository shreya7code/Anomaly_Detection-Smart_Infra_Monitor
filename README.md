# 🚨 Smart Infra Monitor – Real-Time Anomaly Detection Dashboard

A full-stack observability dashboard that monitors CPU, memory, and I/O usage in real-time and alerts teams on system anomalies using ML and LLMs.

## ✨ Features
- 📈 Live dashboard built with React & D3.js
- 🤖 Real-time anomaly detection using Isolation Forest
- 🔔 Slack/Email alerts for critical incidents
- 🧠 GPT-based explanations of anomalies (via OpenAI API)
- ⚙️ Dockerized, deployable on AWS or Render

## 💻 Tech Stack
- **Frontend**: React + Chart.js + Tailwind
- **Backend**: FastAPI + Kafka (or mocked stream)
- **ML**: Scikit-learn (Isolation Forest)
- **LLM**: OpenAI GPT-4 (anomaly explanations)
- **DB**: InfluxDB / TimescaleDB
- **Infra**: Docker, Docker Compose, CI/CD, AWS EC2

## 🚀 Run Locally
```bash
git clone https://github.com/yourusername/smart-infra-monitor
cd smart-infra-monitor
docker-compose up --build
