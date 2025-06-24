from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Smart Infra Monitor Backend Active"}

@app.post("/ingest")
async def ingest(request: Request):
    data = await request.json()
    print("Received data:", data)
    # TODO: InfluxDB write logic will go here
    return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
