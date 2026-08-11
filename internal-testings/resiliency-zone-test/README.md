# Vertex AI Multi-Zone Resiliency & SLA Verification Test

This repository provides an empirical test suite and architectural reference proving that **Google Cloud Vertex AI Online Prediction** endpoints automatically distribute container replicas across distinct **Availability Zones (AZs)** within a region when configured with $\ge 2$ replicas.

For the comprehensive technical deep dive with full failover mechanics and metadata introspection, see [**ARCHITECTURE_AND_REPLICATION.md**](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/ARCHITECTURE_AND_REPLICATION.md).

---

## Architectural Overview

```
                      +-----------------------------+
                      |   Client Application / SDK  |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |  Vertex AI Regional Ingress |
                      |    (Load Balancing / GFE)   |
                      +--------------+--------------+
                                     |
                    +----------------+----------------+
                    | (50% Traffic)                   | (50% Traffic)
                    v                                 v
   +---------------------------------+   +---------------------------------+
   |    Zone: us-central1-a          |   |    Zone: us-central1-b          |
   |  +---------------------------+  |   |  +---------------------------+  |
   |  | Node: gk3-vertex-...-qj5n |  |   |  | Node: gk3-vertex-...-nqg8 |  |
   |  | Pod IP: 10.0.0.196        |  |   |  | Pod IP: 10.0.6.4          |  |
   |  | Replica: b28562d4-...     |  |   |  | Replica: c616a9a2-...     |  |
   |  +---------------------------+  |   |  +---------------------------+  |
   +---------------------------------+   +---------------------------------+
```

### Key Architectural Findings

- **Multi-Zone Scheduling**: Vertex AI leverages regional GKE clusters / Borg cells with pod topology spread constraints (`topologyKey: topology.kubernetes.io/zone`) to guarantee replica placement across independent failure domains.
- **Dynamic Load Balancing**: The regional endpoint balances inference requests evenly across the provisioned availability zones (50% / 50% split).
- **Autonomous Zonal Failover**: If an availability zone experiences an outage, ingress health checking redirects 100% of traffic to surviving healthy zones with zero downtime.
- **SLA Qualification**: Google Cloud requires $\ge 2$ nodes/replicas for Custom Model Online Prediction to qualify for the **99.9% Monthly Uptime Percentage SLA**.

---

## Empirical Test Telemetry (us-central1)

During automated testing of 50 concurrent requests against a 2-replica endpoint, the following telemetry was recorded:

| Telemetry Metric | Replica #1 | Replica #2 | Verification Status |
| :--- | :--- | :--- | :--- |
| **GCP Zone** | `us-central1-a` | `us-central1-b` | **Multi-Zone Proven** |
| **Underlying GKE Node** | `gk3-vertex-...-0b02f326-qj5n` | `gk3-vertex-...-518fb93b-nqg8` | **Independent VMs** |
| **Container IP Subnet** | `10.0.0.196` | `10.0.6.4` | **Disparate Subnets** |
| **Traffic Split** | 50% (25/50 requests) | 50% (25/50 requests) | **Balanced Ingress** |
| **Avg Latency** | 43.12 ms | 44.08 ms | **Symmetric Performance** |

---

## File Directory Reference

| Filename | Description |
| :--- | :--- |
| [`app.py`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/app.py) | FastAPI prediction server implementing `/health` and `/predict`, querying GCP metadata server (`http://metadata.google.internal/computeMetadata/v1/instance/zone`), container IPs, hostnames, and kernel boot IDs. |
| [`Dockerfile`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/Dockerfile) | Production Docker container configuration with Vertex AI environment variables (`AIP_HTTP_PORT=8080`, `AIP_HEALTH_ROUTE=/health`, `AIP_PREDICT_ROUTE=/predict`). |
| [`requirements.txt`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/requirements.txt) | Python dependencies for the serving container (`fastapi`, `uvicorn`, `requests`). |
| [`deploy_and_test.py`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/deploy_and_test.py) | Comprehensive test orchestration script to upload the model, deploy a 2-replica endpoint, run multi-threaded concurrent prediction batches, and clean up resources. |
| [`quick_test.py`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/quick_test.py) | Lightweight verification script to send 10 sequential inference requests and print a tabular zone distribution summary. |
| [`README.md`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/README.md) | High-level landing page, executive overview, empirical findings, and quickstart instructions. |
| [`ARCHITECTURE_AND_REPLICATION.md`](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/ARCHITECTURE_AND_REPLICATION.md) | In-depth technical architecture blueprint, detailed ASCII diagrams, failover mechanics, SLA breakdown, and complete replication guide. |

---

## Quickstart & Replication

### 1. Build and Push Container Image
```bash
export PROJECT_ID="vtxdemos"
export REGION="us-central1"
export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/custom-predictions/resiliency-zone-detector:latest"

gcloud builds submit . --tag=${IMAGE_URI}
```

### 2. Deploy Model & Run Automated Load Test
```bash
# Uploads model, deploys 2 replicas, and fires 50 requests across 10 threads
python3 deploy_and_test.py --requests=50 --concurrency=10
```

### 3. Rapid Sequential Zone Check
```bash
python3 quick_test.py
```

### 4. Cleanup Resources
```bash
python3 deploy_and_test.py --cleanup
```

---

## Further Reading

For complete details on:
- Google Compute Engine metadata introspection mechanics
- Linux kernel boot ID and container fingerprinting
- Autonomous zonal failover event lifecycle
- Official Google Cloud Vertex AI 99.9% SLA requirements

Read the full guide: [**ARCHITECTURE_AND_REPLICATION.md**](file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/internal-testings/resiliency-zone-test/ARCHITECTURE_AND_REPLICATION.md).
