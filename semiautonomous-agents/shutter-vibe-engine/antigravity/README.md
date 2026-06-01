# Antigravity Replication Capsule: Shutter Vibe Engine

This folder is a self-contained, turn-key replication package. **Its sole purpose is to replicate the entire Shutter Vibe Engine application from scratch in a new customer environment using the Antigravity agentic AI coding assistant.**

It contains the exact working frontend source code, backend python servers, containerization templates, deployment configs, and automated verification scripts.

---

## 📂 Capsule Contents

```
antigravity/
├── README.md               # This master onboarding & bootstrap guide
├── WORKFLOW.md             # Declarative, sequential & parallel workflow for Antigravity
├── run_workflow.py         # Threaded python interactive variable prompter & deployer
├── verify_replication.py   # Automated frontend & server router integrity check
├── SKILLS.md               # Model selections, SDK requirements, and security guidelines
├── subagents/              # AI specialist instructions
│   ├── ui_copier.md        # Specs for cloning and adapting index_v2.html, app_v2.js, etc.
│   └── pipeline_builder.md # Specs for provisioning buckets and Cloud Run services
├── deploy/                 # Dockerfiles, requirements, and .gcloudignores
│   ├── Dockerfile.app / .gcloudignore.app
│   ├── Dockerfile.ingest / .gcloudignore.ingest
│   ├── requirements.app.txt
│   └── requirements.ingest.txt
└── src/                    # 100% of the working application source files
    ├── app/                # FastAPI web server and GCS/Firestore ingest handlers
    ├── templates/          # High-fidelity, premium index_v2.html template
    ├── static/             # styles_v2.css, app_v2.js, viz3d.js, sliders, and panels
    ├── pipeline/           # build.py embeddings pipeline logic
    ├── backends/           # Vector Search & BigQuery pluggable dispatch backends
    └── demos/              # _client.py shared connection utility
```

---

## 🚀 The Replication & Deployment Steps

To replicate this application from scratch in your new GCP environment, initiate your pair-programming session with **Antigravity** and execute the following 3 steps:

### Step 1: Workspace Bootstrapping (Self-Copy)
Instruct Antigravity to structure the target workspace:
> *"Extract the working source files from `./antigravity/src/` and structure them in our root directory. Copy `src/app/` to `multimodal-search/app/`, `src/pipeline/` to `multimodal-search/pipeline/`, `src/backends/` to `multimodal-search/backends/`, and `src/demos/` to `demos/` so our workspace perfectly matches the reference framework."*

### Step 2: Interactive Parameter Configuration
Instruct Antigravity to initiate the interactive deployment:
> *"Read and execute the programmatic deployment workflow defined in `./antigravity/WORKFLOW.md`."*

Alternatively, you can run the interactive setup script directly:
```bash
python antigravity/run_workflow.py
```
This script will collect your project configurations (GCP Project ID, region, target GCS bucket, service account), enable APIs, bind IAM policies, build both container images in parallel via Cloud Build, deploy them to Cloud Run, and configure the GCS Eventarc ingestion trigger.

### Step 3: Deployment Verification & Ingestion Test
Once the deployment script reports success:
1. Open the deployed application URL.
2. Drop a sample video or audio clip into your GCS ingestion bucket folder:
   ```bash
   gcloud storage cp some-sample.mp4 gs://<YOUR_BUCKET_NAME>/ingest/
   ```
3. Monitor logs to watch real-time ffmpeg splitting and Vertex AI embedding extraction:
   ```bash
   gcloud run services logs read envato-vibe-ingest --region=<YOUR_REGION> --limit=50
   ```
