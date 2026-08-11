import os
import time
import uuid
import socket
import logging
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Vertex AI Zone & Resiliency Detector")

# Generate a unique replica ID and record startup timestamp when this container initializes
REPLICA_UUID = str(uuid.uuid4())
STARTUP_TIME = datetime.utcnow().isoformat() + "Z"
CONTAINER_HOSTNAME = socket.gethostname()

try:
    CONTAINER_IP = socket.gethostbyname(CONTAINER_HOSTNAME)
except Exception:
    CONTAINER_IP = "unknown"

def get_gcp_metadata(path: str, timeout: float = 0.5) -> str:
    """Helper to query the GCP Compute Engine metadata server."""
    url = f"http://metadata.google.internal/computeMetadata/v1/{path}"
    headers = {"Metadata-Flavor": "Google"}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception as e:
        logger.debug(f"Metadata query failed for {path}: {e}")
    return "unknown"

def get_kernel_boot_id() -> str:
    """Read Linux kernel boot ID if available."""
    try:
        with open("/proc/sys/kernel/random/boot_id", "r") as f:
            return f.read().strip()
    except Exception:
        return "unknown"

# Cache host metadata collected at startup or first request
ZONE_RAW = get_gcp_metadata("instance/zone")
# Zone typically returns in format: projects/<PROJECT_NUM>/zones/<ZONE> (e.g. projects/123/zones/us-central1-a)
ZONE_NAME = ZONE_RAW.split("/")[-1] if "/" in ZONE_RAW else ZONE_RAW
INSTANCE_NAME = get_gcp_metadata("instance/name")
INSTANCE_ID = get_gcp_metadata("instance/id")
MACHINE_TYPE_RAW = get_gcp_metadata("instance/machine-type")
MACHINE_TYPE = MACHINE_TYPE_RAW.split("/")[-1] if "/" in MACHINE_TYPE_RAW else MACHINE_TYPE_RAW
BOOT_ID = get_kernel_boot_id()

@app.get("/ping")
@app.get("/health")
@app.get("/")
def health_check():
    """Vertex AI health check endpoint (AIP_HEALTH_ROUTE)."""
    return JSONResponse(status_code=200, content={"status": "healthy", "replica_id": REPLICA_UUID})

@app.post("/predict")
async def predict(request: Request):
    """
    Vertex AI prediction endpoint (AIP_PREDICT_ROUTE).
    Accepts JSON body: {"instances": [...]}
    Returns metadata about which replica/node/zone served the prediction.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    instances = body.get("instances", [{}])
    server_timestamp = datetime.utcnow().isoformat() + "Z"

    # Re-verify zone in case it resolves post-startup
    current_zone = ZONE_NAME
    if current_zone == "unknown":
        z = get_gcp_metadata("instance/zone")
        if z != "unknown":
            current_zone = z.split("/")[-1]

    predictions = []
    for inst in instances:
        result = {
            "served_by": {
                "replica_uuid": REPLICA_UUID,
                "container_hostname": CONTAINER_HOSTNAME,
                "container_ip": CONTAINER_IP,
                "zone": current_zone,
                "instance_name": INSTANCE_NAME,
                "instance_id": INSTANCE_ID,
                "machine_type": MACHINE_TYPE,
                "kernel_boot_id": BOOT_ID,
                "replica_startup_time": STARTUP_TIME,
                "served_timestamp": server_timestamp
            },
            "echo_input": inst
        }
        predictions.append(result)

    return JSONResponse(content={"predictions": predictions})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("AIP_HTTP_PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
