# Antigravity Replication Capsule: Shutter Vibe Engine

This folder is a self-contained, turn-key replication package. **Its sole purpose is to replicate the entire Shutter Vibe Engine application from scratch in a new customer environment using the Antigravity agentic AI coding assistant.**

It contains the exact working frontend source code, backend python servers, containerization templates, deployment configs, and automated verification scripts.

---

## 📂 Capsule Contents

```
antigravity/
├── README.md               # This master onboarding & bootstrap guide
├── WORKFLOW.md             # Declarative, sequential & parallel workflow for Antigravity
├── CLEANUP_WORKFLOW.md     # Declarative workflow for tearing down environment
├── PLAYGROUND_WORKFLOW.md   # Interactive educational Vector Search playground setup guide
├── cleanup.sh              # Automated GCP resource teardown script
├── verify_replication.py   # Automated frontend & server router integrity check
├── SKILLS.md               # Model selections, SDK requirements, and security guidelines
├── .agent/                 # Portable Antigravity rules, workflows, and skills folder
│   ├── rules/              # Global agent guidelines (general-instructions.md)
│   ├── skills/             # Custom agent capabilities (replicating-vibe-search/SKILL.md)
│   └── workflows/          # Interactive workflows (replicate-vibe-search.md, cleanup-vibe-search.md, setup-playground.md)
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
    │   ├── templates/      # High-fidelity, premium index_v2.html template
    │   └── static/         # styles_v2.css, app_v2.js, viz3d.js, sliders, and panels
    ├── pipeline/           # build.py embeddings pipeline logic
    ├── backends/           # Vector Search & BigQuery pluggable dispatch backends
    └── demos/              # _client.py shared connection utility
```

---

## 💡 One-Click AI Handoff (From an Empty Workspace)

If starting in a completely empty workspace directory, you can simply feed **Antigravity** this direct URL and let it automatically clone the replication capsule and bootstrap the project:

### Copy-Paste Prompt for Your New Session:
```text
Please fetch our complete Shutter Vibe Engine replication capsule directly from this GitHub directory:
https://github.com/jchavezar/vertex-ai-samples/tree/main/semiautonomous-agents/shutter-vibe-engine/antigravity

Download or clone these capsule files into our workspace under an `./antigravity` folder. 

Once you have retrieved the folder, read the master onboarding guide in `./antigravity/README.md`. Copy `./antigravity/.agent` to the root `.agent` folder of your workspace. Then, type `/` in your chat and trigger the `/replicate-vibe-search` workflow.
```

---

## 🚀 The Replication & Deployment Steps

To replicate this application from scratch in your new GCP environment, initiate your pair-programming session with **Antigravity** and execute the following 3 steps:

### Step 1: Activate Antigravity Customizations
Instruct Antigravity to copy the workspace settings, rules, skills, and workflows from the capsule:
> *"Copy the `./antigravity/.agent` folder and its contents directly into our workspace root `.agent` folder to register the global rules, specialized skills, and workflows."*

Once the copy is done, your Antigravity Customizations panel will light up with the `/replicate-vibe-search` workflow!

### Step 2: Trigger Native Interactive Workflow
Initiate the interactive replication sequence inside the Antigravity session:
* Type `/` in the chat, select `/replicate-vibe-search`, and press Enter.

Antigravity will guide you step-by-step through the native commands to:
1. Bootstrap the workspace folder structure (`multimodal-search/app/` etc.).
2. Generate your `.env` workspace parameters.
3. Configure GCP APIs, IAM Service Accounts, and Cloud Storage Bucket structures.
4. Build both frontend and ingestion containers via Cloud Build and deploy them to Cloud Run.
5. Create GCS Eventarc triggers and print the final active Web Service URL!

### Step 3: Deployment Verification & Ingestion Test
Once the workflow reports success:
1. Open the deployed application URL returned by the workflow.
2. Drop a sample video or audio clip into your GCS ingestion bucket folder:
   ```bash
   gcloud storage cp some-sample.mp4 gs://<YOUR_BUCKET_NAME>/ingest/
   ```
3. Monitor logs to watch real-time ffmpeg splitting and Vertex AI embedding extraction:
   ```bash
   gcloud run services logs read envato-vibe-ingest --region=<YOUR_REGION> --limit=50
   ```
