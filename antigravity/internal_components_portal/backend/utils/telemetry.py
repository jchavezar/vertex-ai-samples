import os
import requests
import logging
import threading

logger = logging.getLogger(__name__)

# Configured to hit the Observability Nexus
NEXUS_ENDPOINT = "http://localhost:8145/ingest"

def push_telemetry_async(payload: dict):
    """
    Non-blocking push of telemetry payload to the Observability Nexus
    """
    if os.environ.get("DISABLE_TELEMETRY") == "true":
        return
        
    def _send():
        try:
            requests.post(NEXUS_ENDPOINT, json=payload, timeout=1)
        except Exception:
            # We fail silently so as not to crash the agent execution if nexus is down
            pass 
            
    threading.Thread(target=_send, daemon=True).start()
