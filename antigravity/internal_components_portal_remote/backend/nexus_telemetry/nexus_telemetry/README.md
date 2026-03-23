# 📶 Nexus Telemetry: The "Sensors" for the Suite

Nexus Telemetry is the instrumentation package used by all Antigravity applications to enable real-time observability. It is a strictly **zero-latency**, **non-blocking** SDK that pushes events to the **Observability Nexus** hub.

## 🏗️ Role in the Platform
While `observability_nexus` is the "monitor" (the Brain), **Nexus Telemetry** acts as the "Sensors" (the Cameras). It provides:
1.  **Shared Library**: A Python package imported by all other `antigravity` apps.
2.  **Zero-Latency Dispatch**: Uses an internal queue and a dedicated background thread to ensure logging never slows down your main application.
3.  **FastAPI Middleware**: Automatically capture API requests and responses to monitor agent behavior.
4.  **Custom Event Pushing**: Manual methods like `push_telemetry_async()` for application-specific logs.

---

## 🚀 How to Implement

### **1. Add Dependency**
In your `antigravity` project's `pyproject.toml`:
```toml
[tool.uv.sources]
nexus-telemetry = { path = "../../nexus_telemetry" }
```

### **2. Instrument Your FastAPI App**
```python
from nexus_telemetry import NexusAPITrackerMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(NexusAPITrackerMiddleware)
```

### **3. Push Custom Events**
```python
from nexus_telemetry import push_telemetry_async

push_telemetry_async({
    "tag": "agent_action",
    "event": {"action": "fetching_data", "success": True}
})
```

---

## 🩺 System Integration
Typically, you don't run this folder directly. It is designed to be **imported** as a package by your other apps. It points by default to **Port 8145** (where `observability_nexus` should be listening).

> [!CAUTION]
> If the `observability_nexus` server isn't running, this library will **fail silently** to ensure it never crashes your main application.
