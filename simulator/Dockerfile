# ------------- Dockerfile for stream_simulator.py-----------------
FROM python:3.10-slim

WORKDIR /app

#install required system packages for building wheels (psutil needs gcc)
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

#install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run simulator when container starts
CMD ["python", "stream_simulator.py"]