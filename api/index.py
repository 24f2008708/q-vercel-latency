from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
from typing import List

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load JSON file
with open("q-vercel-latency.json") as f:
    data = json.load(f)

class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/")
def analyze(request: RequestBody):

    regions_result = {}

    for region in request.regions:

        region_data = [r for r in data if r["region"] == region]

        if not region_data:
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]

        regions_result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(1 for l in latencies if l > request.threshold_ms)
        }

    return {
        "regions": regions_result
    }
