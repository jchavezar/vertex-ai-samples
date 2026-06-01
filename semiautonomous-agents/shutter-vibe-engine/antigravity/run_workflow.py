#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import tempfile
import threading

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("=" * 60)
    print(f" {title:^58} ")
    print("=" * 60)

def run_cmd(args, capture_output=True, env=None, check=True):
    """Runs a shell command and returns output or raises exception."""
    try:
        res = subprocess.run(
            args,
            shell=True,
            text=True,
            capture_output=capture_output,
            env=env,
            check=check
        )
        return res.stdout.strip() if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed: {args}")
        if capture_output:
            print(f"Error output: {e.stderr}")
        raise e

def query_user(prompt, default=None):
    """Interactive input collector with defaults."""
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    else:
        while True:
            val = input(f"{prompt}: ").strip()
            if val:
                return val
            print("[ERROR] Value cannot be empty. Please enter a value.")

def main():
    clear_screen()
    print_header("ANTIGRAVITY DYNAMIC GCP ORCHESTRATOR")
    print(" This script will interactively configure, provision, build, and")
    print(" deploy your Shutter Vibe Engine serverless ingestion pipeline.")
    print("=" * 60)

    # 1. Verification of environment dependencies
    print("\n[1/5] Verifying CLI Dependencies...")
    try:
        gcloud_ver = run_cmd("gcloud --version | head -n 1")
        print(f"  -> Found gcloud: {gcloud_ver}")
    except Exception:
        print("[CRITICAL] Google Cloud CLI (gcloud) is not installed or not in PATH.")
        sys.exit(1)

    # Gather default project from gcloud configuration
    default_project = ""
    try:
        default_project = run_cmd("gcloud config get-value project 2>/dev/null")
    except Exception:
        pass

    # 2. Variable Gathering Phase
    print("\n[2/5] Collecting Workspace Parameters...")
    project = query_user("Enter Google Cloud Project ID", default=default_project)
    region = query_user("Enter Google Cloud Region/Location", default="us-central1")
    bucket_default = f"{project}-vibe-engine-data"
    bucket = query_user("Enter target Google Cloud Storage Bucket Name", default=bucket_default)
    sa_name = query_user("Enter Service Account Name to create/use", default="envato-vibe-runner")
    search_backend = query_user("Select Search Backend (vector-search/bigquery)", default="vector-search")
    
    # Save parameters to a local .env file (excluded by git)
    print("\n  -> Saving configurations to `.env`...")
    with open(".env", "w") as env_file:
        env_file.write(f"GOOGLE_CLOUD_PROJECT={project}\n")
        env_file.write(f"GOOGLE_CLOUD_LOCATION={region}\n")
        env_file.write(f"ENVATO_GCS_BUCKET={bucket}\n")
        env_file.write(f"SEARCH_BACKEND={search_backend}\n")
        env_file.write(f"ENVATO_SA_NAME={sa_name}\n")
    print("  -> Configuration cached.")

    # 3. Cloud Provider Preparations & Enablement
    print("\n[3/5] Setting up GCP Environment...")
    run_cmd(f"gcloud config set project {project}", capture_output=False)
    
    apis = [
        "run.googleapis.com",
        "eventarc.googleapis.com",
        "firestore.googleapis.com",
        "aiplatform.googleapis.com",
        "cloudbuild.googleapis.com"
    ]
    print(f"  -> Enabling API services in parallel: {', '.join(apis)}...")
    enable_threads = []
    for api in apis:
        t = threading.Thread(target=lambda a=api: run_cmd(f"gcloud services enable {a} --quiet"))
        enable_threads.append(t)
        t.start()
    for t in enable_threads:
        t.join()
    print("  -> APIs enabled.")

    # Setup Service Account
    sa_email = f"{sa_name}@{project}.iam.gserviceaccount.com"
    try:
        print(f"  -> Verifying Service Account: {sa_email}")
        run_cmd(f"gcloud iam service-accounts describe {sa_email}")
        print("     Account exists.")
    except Exception:
        print(f"  -> Creating Service Account: {sa_name}")
        run_cmd(f"gcloud iam service-accounts create {sa_name} --display-name='Shutter Vibe Runner' --quiet")
    
    # Assign IAM Roles
    roles = [
        "roles/aiplatform.user",
        "roles/storage.objectAdmin",
        "roles/datastore.user",
        "roles/run.invoker",
        "roles/pubsub.publisher",
        "roles/eventarc.eventReceiver"
    ]
    print("  -> Binding roles to Service Account...")
    for role in roles:
        run_cmd(f"gcloud projects add-iam-policy-binding {project} --member='serviceAccount:{sa_email}' --role='{role}' --quiet >/dev/null")

    # Authorize GCS agent for Eventarc notifications
    project_num = run_cmd(f"gcloud projects describe {project} --format='value(projectNumber)'")
    gcs_agent = f"service-{project_num}@gs-project-accounts.iam.gserviceaccount.com"
    print(f"  -> Authorizing GCS service agent: {gcs_agent}")
    run_cmd(f"gcloud projects add-iam-policy-binding {project} --member='serviceAccount:{gcs_agent}' --role='roles/pubsub.publisher' --quiet >/dev/null")

    # 4. Provision Storage Schema & Buckets
    print("\n[4/5] Provisioning Storage Schema...")
    try:
        print(f"  -> Checking GCS Bucket: gs://{bucket}")
        run_cmd(f"gcloud storage buckets describe gs://{bucket}")
        print("     Bucket exists.")
    except Exception:
        print(f"  -> Creating GCS Bucket: gs://{bucket}")
        run_cmd(f"gcloud storage buckets create gs://{bucket} --location={region} --quiet")
    
    # Create schema directories inside GCS
    subfolders = ["ingest/", "originals/", "thumbnails/", "segments/"]
    print("  -> Initializing folder schema...")
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(b"")
        tmp.flush()
        for folder in subfolders:
            run_cmd(f"gcloud storage cp {tmp.name} gs://{bucket}/{folder}.placeholder --quiet >/dev/null")
    print("  -> Folder schema successfully written.")

    # 5. Build and Deploy Cloud Run Containers
    print("\n[5/5] Launching Parallel Cloud Run Build & Deploy Workflows...")
    
    errors = []
    def deploy_app():
        print("  -> [App Server Build]: Compiling FastAPI Frontend App Container...")
        try:
            # Swap in the gcloudignore configuration
            shutil.copy("antigravity/deploy/.gcloudignore.app", ".gcloudignore")
            
            image_app = f"gcr.io/{project}/envato-vibe-app:latest"
            build_yaml = """
steps:
- name: gcr.io/cloud-builders/docker
  args: ['build', '-f', 'antigravity/deploy/Dockerfile.app', '-t', '{image}', '.']
images:
- '{image}'
options:
  logging: CLOUD_LOGGING_ONLY
""".replace("{image}", image_app)
            
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
                f.write(build_yaml)
                cfg_path = f.name
                
            run_cmd(f"gcloud builds submit . --project {project} --config {cfg_path}")
            os.remove(cfg_path)
            
            print("  -> [App Server Deploy]: Provisioning Cloud Run instance...")
            run_cmd(
                f"gcloud run deploy envato-vibe-app "
                f"--image {image_app} "
                f"--region {region} "
                f"--project {project} "
                f"--service-account {sa_email} "
                f"--memory 2Gi --cpu 2 --timeout 600 "
                f"--allow-unauthenticated "
                f"--set-env-vars 'GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT={project},GOOGLE_CLOUD_LOCATION={region},ENVATO_GCS_BUCKET={bucket},SEARCH_BACKEND={search_backend}'"
            )
            print("  ✓ [App Server]: Deployed successfully!")
        except Exception as e:
            errors.append(f"App deployment error: {e}")

    def deploy_ingest():
        print("  -> [Ingest Worker Build]: Compiling Ingestion Processor Container...")
        try:
            # Swap in the gcloudignore configuration
            shutil.copy("antigravity/deploy/.gcloudignore.ingest", ".gcloudignore")
            
            image_ingest = f"gcr.io/{project}/envato-vibe-ingest:latest"
            build_yaml = """
steps:
- name: gcr.io/cloud-builders/docker
  args: ['build', '-f', 'antigravity/deploy/Dockerfile.ingest', '-t', '{image}', '.']
images:
- '{image}'
options:
  logging: CLOUD_LOGGING_ONLY
""".replace("{image}", image_ingest)
            
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
                f.write(build_yaml)
                cfg_path = f.name
                
            run_cmd(f"gcloud builds submit . --project {project} --config {cfg_path}")
            os.remove(cfg_path)
            
            print("  -> [Ingest Worker Deploy]: Provisioning Cloud Run instance...")
            run_cmd(
                f"gcloud run deploy envato-vibe-ingest "
                f"--image {image_ingest} "
                f"--region {region} "
                f"--project {project} "
                f"--service-account {sa_email} "
                f"--memory 2Gi --cpu 2 --timeout 600 "
                f"--no-allow-unauthenticated "
                f"--set-env-vars 'GOOGLE_CLOUD_PROJECT={project},GOOGLE_CLOUD_LOCATION={region},ENVATO_GCS_BUCKET={bucket},GOOGLE_GENAI_USE_VERTEXAI=True'"
            )
            print("  ✓ [Ingest Worker]: Service deployed.")
            
            # Setup Eventarc GCS Trigger
            trigger_name = "envato-vibe-ingest-trigger"
            print(f"  -> [Ingest Worker Hook]: Configuring Eventarc Trigger {trigger_name}...")
            try:
                run_cmd(f"gcloud eventarc triggers describe {trigger_name} --location {region} --project {project}")
                print("     Trigger already exists, updating destination run service...")
                run_cmd(
                    f"gcloud eventarc triggers update {trigger_name} "
                    f"--location {region} --project {project} "
                    f"--destination-run-service envato-vibe-ingest "
                    f"--destination-run-region {region} "
                    f"--service-account {sa_email}"
                )
            except Exception:
                print("     Trigger does not exist, creating new...")
                run_cmd(
                    f"gcloud eventarc triggers create {trigger_name} "
                    f"--location {region} --project {project} "
                    f"--destination-run-service envato-vibe-ingest "
                    f"--destination-run-region {region} "
                    f"--event-filters 'type=google.cloud.storage.object.v1.finalized' "
                    f"--event-filters 'bucket={bucket}' "
                    f"--service-account {sa_email}"
                )
            print("  ✓ [Ingest Worker Trigger]: Successfully bound to GCS finalized-object events.")
        except Exception as e:
            errors.append(f"Ingest deployment error: {e}")

    # Launch deployments inside parallel threads
    t1 = threading.Thread(target=deploy_app)
    t2 = threading.Thread(target=deploy_ingest)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()

    # Restore original .gcloudignore if one existed
    if os.path.exists(".gcloudignore"):
        os.remove(".gcloudignore")

    print("\n" + "=" * 60)
    if errors:
        print(" [FAILURE] Deployment failed with the following issues:")
        for err in errors:
            print(f"  * {err}")
        sys.exit(1)
    else:
        # Fetch the deployed Web Service URL
        url = run_cmd(f"gcloud run services describe envato-vibe-app --region {region} --project {project} --format 'value(status.url)'")
        print(" [SUCCESS] Orchestration Workflow Completed!")
        print(f"  -> Frontend UI URL: {url}")
        print(f"  -> GCS Pipeline Bucket: gs://{bucket}")
        print("  -> Direct Ingest Path: gs://{bucket}/ingest/")
        print("\n To test tomorrow:")
        print(f"  1. Upload video: `gcloud storage cp your-video.mp4 gs://{bucket}/ingest/`")
        print(f"  2. Watch logs:   `gcloud run services logs read envato-vibe-ingest --region {region}`")
        print("=" * 60)

if __name__ == "__main__":
    main()
