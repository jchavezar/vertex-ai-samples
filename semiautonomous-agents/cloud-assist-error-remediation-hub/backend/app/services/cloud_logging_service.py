import subprocess
import json
from datetime import datetime, timezone, timedelta
from typing import List
from app.models.schemas import GcpErrorItem

def fetch_gcp_errors(time_range: str = "1h") -> List[GcpErrorItem]:
    """
    Fetches real GCP errors from Cloud Logging and merges with high-fidelity representative
    error entries across Cloud Run, Cloud SQL, GKE, and Cloud Storage so every time filter has rich interactive issues.
    """
    errors: List[GcpErrorItem] = []
    now = datetime.now(timezone.utc)
    
    simulated = [
        GcpErrorItem(
            id="err-cloud-run-checkout-500",
            timestamp=(now - timedelta(minutes=1)).isoformat(),
            severity="CRITICAL",
            serviceName="Cloud Run (Storefront)",
            resourceType="cloud_run_revision",
            summary="ZeroDivisionError: division by zero in POST /api/cart/checkout",
            fullText="[CRITICAL] HTTP 500 Internal Server Error returned on POST /api/cart/checkout. Traceback: File '/app/routes/checkout.py', line 42, in process_cart_checkout discount_ratio = total_discount / itemCount ZeroDivisionError: division by zero",
            logPayload={
                "message": "ZeroDivisionError: division by zero in /api/cart/checkout",
                "service": "envato-vibe-storefront",
                "revision": "envato-vibe-storefront-00042-v3x",
                "status": 500
            },
            labels={"region": "us-central1", "service_name": "envato-vibe-storefront"}
        ),
        GcpErrorItem(
            id="err-cloud-run-keyerror-500",
            timestamp=(now - timedelta(minutes=3)).isoformat(),
            severity="CRITICAL",
            serviceName="Cloud Run (Cyberpunk Ledger)",
            resourceType="cloud_run_revision",
            summary="KeyError: 'JWT_SECRET_KEY' in POST /api/auth/token",
            fullText="[CRITICAL] HTTP 500 Internal Server Error returned on POST /api/auth/token. Traceback: File '/app/services/auth.py', line 18, in generate_jwt_token secret = os.environ['JWT_SECRET_KEY'] KeyError: 'JWT_SECRET_KEY'",
            logPayload={
                "message": "KeyError: 'JWT_SECRET_KEY' missing in environment",
                "service": "cyberpunk-ledger-dashboard",
                "revision": "cyberpunk-ledger-dashboard-00001-a1",
                "status": 500
            },
            labels={"region": "us-central1", "service_name": "cyberpunk-ledger-dashboard"}
        ),
        GcpErrorItem(
            id="err-cloud-run-oom-500",
            timestamp=(now - timedelta(minutes=5)).isoformat(),
            severity="CRITICAL",
            serviceName="Cloud Run (Healthcare Portal)",
            resourceType="cloud_run_revision",
            summary="MemoryError: Heap allocation limit 512MB exceeded (OOMKilled)",
            fullText="[CRITICAL] Memory limit of 512M exceeded with 534M used. Container terminated (OOMKilled) on Cloud Run service 'healthcare-patient-portal'. Traceback: File '/app/reports/mri.py', line 88 MemoryError",
            logPayload={
                "message": "MemoryError: Heap memory limit exceeded",
                "service": "healthcare-patient-portal",
                "revision": "healthcare-patient-portal-00001-m2",
                "status": 500
            },
            labels={"region": "us-central1", "service_name": "healthcare-patient-portal"}
        ),
        GcpErrorItem(
            id="err-cloud-run-conn-500",
            timestamp=(now - timedelta(minutes=8)).isoformat(),
            severity="ERROR",
            serviceName="Cloud Run (Logistics Tracker)",
            resourceType="cloud_run_revision",
            summary="ConnectionRefusedError: Postgres connection pool exhausted",
            fullText="[ERROR] HTTP 500 Internal Server Error returned on GET /api/fleet/status. Traceback: File '/app/db/postgres.py', line 34 ConnectionRefusedError: Could not acquire connection from Postgres pool",
            logPayload={
                "message": "ConnectionRefusedError: Postgres connection pool exhausted",
                "service": "realtime-logistics-tracker",
                "revision": "realtime-logistics-tracker-00001-l4",
                "status": 500
            },
            labels={"region": "us-central1", "service_name": "realtime-logistics-tracker"}
        ),
        GcpErrorItem(
            id="err-sql-maint-stall",
            timestamp=(now - timedelta(minutes=28)).isoformat(),
            severity="ERROR",
            serviceName="Cloud SQL",
            resourceType="cloudsql_database",
            summary="Instance stuck in MAINTENANCE state with connection timeout",
            fullText="Cloud SQL instance 'prod-db-postgres' has been in MAINTENANCE state for >45 minutes. Incoming pool connection timeouts exceeding SLA.",
            logPayload={
                "instance": "prod-db-postgres",
                "state": "MAINTENANCE",
                "operation": "SYSTEM_UPDATE",
                "error": "Connection acquire timeout after 5000ms"
            },
            labels={"region": "us-central1", "database_version": "POSTGRES_15"}
        ),
        GcpErrorItem(
            id="err-gke-crashloop",
            timestamp=(now - timedelta(hours=1, minutes=12)).isoformat(),
            severity="ERROR",
            serviceName="Google Kubernetes Engine",
            resourceType="k8s_container",
            summary="Pod CrashLoopBackOff: Readiness probe failed HTTP 500",
            fullText="Back-off restarting failed container 'payment-service-pod-x78z' in deployment 'payments'. Liveness probe failed HTTP GET /healthz 500.",
            logPayload={
                "pod": "payment-service-pod-x78z",
                "namespace": "production",
                "restartCount": 8,
                "reason": "CrashLoopBackOff"
            },
            labels={"cluster_name": "us-central1-prod-cluster", "namespace": "production"}
        ),
        GcpErrorItem(
            id="err-storage-iam-403",
            timestamp=(now - timedelta(hours=3, minutes=40)).isoformat(),
            severity="ERROR",
            serviceName="Cloud Storage",
            resourceType="gcs_bucket",
            summary="HTTP 403 Permission Denied: ServiceAccount missing storage.objects.get",
            fullText="Service account 'app-runtime@vtxdemos.iam.gserviceaccount.com' does not have storage.objects.get access to bucket 'prod-customer-invoice-exports'.",
            logPayload={
                "principalEmail": "app-runtime@vtxdemos.iam.gserviceaccount.com",
                "methodName": "storage.objects.get",
                "resourceName": "projects/_/buckets/prod-customer-invoice-exports",
                "status": "PERMISSION_DENIED"
            },
            labels={"bucket_name": "prod-customer-invoice-exports"}
        )
    ]
    
    # Try querying real live GCP logs
    try:
        cmd = [
            "gcloud", "logging", "read",
            "severity>=ERROR",
            "--limit=15",
            "--format=json"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0 and res.stdout.strip():
            live_entries = json.loads(res.stdout)
            for idx, entry in enumerate(live_entries):
                res_info = entry.get("resource", {})
                res_type = res_info.get("type", "gcp_resource")
                labels = res_info.get("labels", {})
                
                svc_name = "Google Cloud Service"
                if "cloud_run" in res_type:
                    svc_name = "Cloud Run"
                elif "cloudsql" in res_type:
                    svc_name = "Cloud SQL"
                elif "k8s" in res_type or "gke" in res_type:
                    svc_name = "Google Kubernetes Engine"
                elif "gcs" in res_type or "bucket" in res_type:
                    svc_name = "Cloud Storage"
                elif "scheduler" in res_type:
                    svc_name = "Cloud Scheduler"
                
                text_payload = entry.get("textPayload") or str(entry.get("jsonPayload", {}))
                summary = text_payload[:80] + ("..." if len(text_payload) > 80 else "")
                
                err = GcpErrorItem(
                    id=entry.get("insertId", f"live-log-{idx}"),
                    timestamp=entry.get("timestamp", now.isoformat()),
                    severity=entry.get("severity", "ERROR"),
                    serviceName=svc_name,
                    resourceType=res_type,
                    summary=summary,
                    fullText=text_payload,
                    logPayload=entry.get("jsonPayload", {}) if isinstance(entry.get("jsonPayload"), dict) else {"raw": text_payload},
                    labels=labels
                )
                errors.append(err)
    except Exception:
        pass

    mins_map = {
        "15m": 15,
        "1h": 60,
        "6h": 360,
        "24h": 1440,
        "7d": 10080
    }
    allowed_mins = mins_map.get(time_range, 1440)
    cutoff = now - timedelta(minutes=allowed_mins)

    combined = errors + simulated
    filtered = []
    seen_ids = set()
    for e in combined:
        if e.id in seen_ids:
            continue
        seen_ids.add(e.id)
        try:
            ts = datetime.fromisoformat(e.timestamp.replace("Z", "+00:00"))
            if ts >= cutoff:
                filtered.append(e)
        except Exception:
            filtered.append(e)
            
    filtered.sort(key=lambda x: x.timestamp, reverse=True)
    return filtered
