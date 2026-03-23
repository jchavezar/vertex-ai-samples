import os
import queue
import threading
import logging
import httpx
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NexusClient:
    """
    A strictly non-blocking Observability Nexus client.
    Uses a standard queue and a dedicated single daemon thread to ingest telemetry
    guaranteeing zero latency impact on the critical app path.
    """
    _instance = None
    _queue = queue.Queue(maxsize=5000)
    _worker_thread = None
    
    def __init__(self, endpoint=None):
        self.endpoint = endpoint or os.environ.get("NEXUS_ENDPOINT", "http://localhost:8145/ingest")
        self.disabled = os.environ.get("DISABLE_TELEMETRY") == "true"
        self._start_worker()
        
    def _start_worker(self):
        if self.disabled:
            return
            
        if NexusClient._worker_thread is None or not NexusClient._worker_thread.is_alive():
            NexusClient._worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="NexusTelemetryWorker")
            NexusClient._worker_thread.start()
            
    def _worker_loop(self):
        # We use a persistent session to optimize connections if Nexus is local
        with httpx.Client(timeout=1.5) as client:
            while True:
                try:
                    payload = self._queue.get()
                    if payload is None:
                        break # Poison pill
                    
                    try:
                        client.post(self.endpoint, json=payload)
                    except Exception:
                        pass # Fail silently
                        
                except Exception:
                    pass

    def push_event(self, tag: str, event_data: dict):
        if self.disabled:
             return
        
        payload = {"tag": tag, "event": event_data}
        try:
            # Non-blocking enqueue. If it's full (e.g., nexus is down for a long time), drop events.
            self._queue.put_nowait(payload)
        except queue.Full:
            pass 

_default_client = NexusClient()

def push_telemetry_async(payload: dict):
    """
    Backward-compatible push telemetry function.
    """
    if _default_client.disabled:
        return
    
    try:
        _default_client._queue.put_nowait(payload)
    except queue.Full:
        pass
