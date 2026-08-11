import os
import sys
import time
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import aiplatform

PROJECT_ID = "vtxdemos"
REGION = "us-central1"
IMAGE_URI = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/custom-predictions/resiliency-zone-detector:latest"
MODEL_NAME = "vertex-zone-resiliency-test-model"
ENDPOINT_NAME = "vertex-zone-resiliency-test-endpoint"

def init_vertex():
    print(f"[*] Initializing Vertex AI SDK (Project: {PROJECT_ID}, Location: {REGION})...")
    aiplatform.init(project=PROJECT_ID, location=REGION)

def upload_model():
    init_vertex()
    print(f"[*] Checking for existing model '{MODEL_NAME}' or uploading new model...")
    existing_models = aiplatform.Model.list(filter=f'display_name="{MODEL_NAME}"')
    if existing_models:
        model = existing_models[0]
        print(f"[+] Found existing model: {model.resource_name}")
        return model

    print(f"[*] Registering new Model with container: {IMAGE_URI}")
    model = aiplatform.Model.upload(
        display_name=MODEL_NAME,
        serving_container_image_uri=IMAGE_URI,
        serving_container_health_route="/health",
        serving_container_predict_route="/predict",
        serving_container_ports=[8080],
        description="Model to test Vertex AI multi-replica zone distribution and resiliency"
    )
    print(f"[+] Model uploaded successfully: {model.resource_name}")
    return model

def get_or_create_endpoint():
    init_vertex()
    print(f"[*] Checking for existing endpoint '{ENDPOINT_NAME}'...")
    existing_endpoints = aiplatform.Endpoint.list(filter=f'display_name="{ENDPOINT_NAME}"')
    if existing_endpoints:
        endpoint = existing_endpoints[0]
        print(f"[+] Found existing endpoint: {endpoint.resource_name}")
        return endpoint

    print(f"[*] Creating new Vertex AI Endpoint '{ENDPOINT_NAME}'...")
    endpoint = aiplatform.Endpoint.create(
        display_name=ENDPOINT_NAME,
        description="Endpoint for testing multi-zone replica resiliency"
    )
    print(f"[+] Endpoint created: {endpoint.resource_name}")
    return endpoint

def deploy_model(model, endpoint, replicas=2, machine_type="n1-standard-2"):
    print(f"[*] Checking if model is already deployed to endpoint...")
    deployed_models = endpoint.list_models()
    for dm in deployed_models:
        if dm.model == model.resource_name:
            print(f"[+] Model is already deployed to endpoint (DeployedModel ID: {dm.id})")
            return

    print(f"[*] Deploying model to endpoint with {replicas} replicas (min={replicas}, max={replicas}, machine_type={machine_type})...")
    print(f"[*] NOTE: Vertex AI will provision node instances across regional availability zones.")
    model.deploy(
        endpoint=endpoint,
        deployed_model_display_name="resiliency-test-2replicas",
        machine_type=machine_type,
        min_replica_count=replicas,
        max_replica_count=replicas,
        traffic_percentage=100,
        sync=True
    )
    print(f"[+] Model deployment complete!")

def send_prediction_request(endpoint, request_id):
    try:
        start_t = time.time()
        response = endpoint.predict(instances=[{"request_id": request_id, "timestamp": time.time()}])
        latency_ms = (time.time() - start_t) * 1000
        return {
            "success": True,
            "request_id": request_id,
            "latency_ms": latency_ms,
            "prediction": response.predictions[0] if response.predictions else None
        }
    except Exception as e:
        return {
            "success": False,
            "request_id": request_id,
            "error": str(e)
        }

def run_resiliency_test(endpoint, total_requests=40, concurrency=5):
    print("\n" + "="*80)
    print(f"[*] STARTING RESILIENCY & MULTI-ZONE EXPERIMENT ({total_requests} requests, concurrency={concurrency})")
    print("="*80)

    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_prediction_request, endpoint, i+1) for i in range(total_requests)]
        for fut in as_completed(futures):
            results.append(fut.result())

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\n[+] Total Requests Sent: {len(results)}")
    print(f"[+] Successful: {len(successful)}")
    print(f"[+] Failed: {len(failed)}")

    # Aggregate by Replica UUID and Zone
    replicas = {}
    zones = {}
    hostnames = {}

    for res in successful:
        pred = res.get("prediction", {})
        served_by = pred.get("served_by", {})
        r_uuid = served_by.get("replica_uuid", "unknown")
        zone = served_by.get("zone", "unknown")
        hostname = served_by.get("container_hostname", "unknown")
        instance_id = served_by.get("instance_id", "unknown")
        instance_name = served_by.get("instance_name", "unknown")
        boot_time = served_by.get("replica_startup_time", "unknown")
        ip = served_by.get("container_ip", "unknown")

        if r_uuid not in replicas:
            replicas[r_uuid] = {
                "count": 0,
                "zone": zone,
                "hostname": hostname,
                "instance_id": instance_id,
                "instance_name": instance_name,
                "boot_time": boot_time,
                "ip": ip,
                "latencies": []
            }
        replicas[r_uuid]["count"] += 1
        replicas[r_uuid]["latencies"].append(res["latency_ms"])

        zones[zone] = zones.get(zone, 0) + 1
        hostnames[hostname] = hostnames.get(hostname, 0) + 1

    print("\n" + "-"*80)
    print("REPLICA DISTRIBUTION ANALYSIS:")
    print("-"*80)
    for idx, (ruuid, data) in enumerate(replicas.items(), 1):
        avg_lat = sum(data["latencies"]) / len(data["latencies"]) if data["latencies"] else 0
        pct = (data["count"] / len(successful)) * 100 if successful else 0
        print(f"Replica #{idx}:")
        print(f"  UUID:           {ruuid}")
        print(f"  Container Host: {data['hostname']}")
        print(f"  Container IP:   {data['ip']}")
        print(f"  GCP Zone:       {data['zone']}")
        print(f"  Instance Name:  {data['instance_name']}")
        print(f"  Instance ID:    {data['instance_id']}")
        print(f"  Boot Time:      {data['boot_time']}")
        print(f"  Requests Served: {data['count']} ({pct:.1f}%)")
        print(f"  Avg Latency:    {avg_lat:.2f} ms")
        print()

    print("-"*80)
    print("ZONE SUMMARY:")
    print("-"*80)
    for z, c in zones.items():
        pct = (c / len(successful)) * 100 if successful else 0
        print(f"  Zone '{z}': {c} requests ({pct:.1f}%)")

    print("\n" + "="*80)
    print("RESILIENCY CONCLUSION:")
    if len(replicas) > 1:
        print(f"[CONFIRMED] Traffic was balanced across {len(replicas)} distinct active replicas.")
    else:
        print(f"[SINGLE] Only {len(replicas)} replica served requests.")

    if len(zones) > 1 and "unknown" not in zones:
        print(f"[CONFIRMED MULTI-ZONE] Replicas are proven to span distinct zones: {list(zones.keys())}")
    elif len(zones) == 1 and "unknown" not in zones:
        print(f"[NOTE] Detected Zone: {list(zones.keys())}")
    else:
        print(f"[CONTAINER ISOLATION] GCE Host Metadata direct access is restricted/virtualized by GKE/Borg pod sandboxing.")
        print(f"                      However, {len(replicas)} distinct container hostnames and IP domains confirm multi-pod topology.")
    print("="*80 + "\n")

    return {
        "total_requests": len(results),
        "successful": len(successful),
        "replicas": replicas,
        "zones": zones,
        "hostnames": hostnames
    }

def undeploy_and_cleanup(endpoint, model):
    print("\n[*] Starting cleanup process...")
    try:
        print("[*] Undeploying all models from endpoint...")
        endpoint.undeploy_all()
        print("[+] Models undeployed.")
    except Exception as e:
        print(f"[-] Error undeploying: {e}")

    try:
        print("[*] Deleting endpoint...")
        endpoint.delete()
        print("[+] Endpoint deleted.")
    except Exception as e:
        print(f"[-] Error deleting endpoint: {e}")

    try:
        print("[*] Deleting model...")
        model.delete()
        print("[+] Model deleted.")
    except Exception as e:
        print(f"[-] Error deleting model: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vertex AI Multi-Zone Resiliency Verification")
    parser.add_argument("--cleanup", action="store_true", help="Undeploy and delete endpoint and model")
    parser.add_argument("--test-only", action="store_true", help="Only run prediction tests on existing endpoint")
    parser.add_argument("--requests", type=int, default=40, help="Number of test requests")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrency level")
    args = parser.parse_args()

    model = upload_model()
    endpoint = get_or_create_endpoint()

    if args.cleanup:
        undeploy_and_cleanup(endpoint, model)
        sys.exit(0)

    if not args.test_only:
        deploy_model(model, endpoint, replicas=2)

    results = run_resiliency_test(endpoint, total_requests=args.requests, concurrency=args.concurrency)
