import requests
import random
import time
from datetime import datetime


URL = "http://localhost:8000/ingest"

def generate_metrics():
    """
    This function simulates system metrics.
    - 90% of the time it sends normal values
    - 10% of the time it injects an 'anomaly'
    """

    # 10% chance to create anomaly
    is_anomaly = random.random() < 0.1

        # if anomaly, then replace values with high spikes
    if is_anomaly:
        print("Injecting Anomaly!!!")   # log that code is faking an anomaly
        cpu = random.uniform(85, 99)
        memory = random.uniform(80,95)
        disk = random.uniform(90,100)
    else:
        # generates normal values in a safe range
        cpu = random.uniform(20, 40)
        memory = random.uniform(30,50)
        disk = random.uniform(40,60)

    # returns the metric dictionar with a timestamp
    return{
        "timestamp": datetime.utcnow().isoformat(),       #iso formatted current time
        "cpu": round(cpu, 2),                           # rounding it off for a cleaner display
        "memory": round(memory, 2),
        "disk": round(disk, 2) 
    }



if __name__ == "__main__":
    while True:
        # Creating a new metric datapoint
        data = generate_metrics()

        print("fake metrics ------\n ", data)
        try:
            res = requests.post(URL, json=data)      #send it to FastAPI
            print(f"Sent data: {data}, | Server Response: {res.status_code}")
        except Exception as e:
            #in case of exceptions (if server is down or request fails)w
            print(f"Exception - Failed to send: {e}")

        # wait 3s before sending the next data points
        time.sleep(3)