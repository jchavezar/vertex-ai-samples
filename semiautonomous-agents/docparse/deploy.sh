#!/usr/bin/env bash
#
# docparse — one-button deploy.
#
# Provisions the entire pipeline end-to-end:
#   1. Buckets, service accounts, IAM            (extractor/deploy.sh)
#   2. Build + deploy the extractor Cloud Run    (extractor/deploy.sh)
#   3. Eventarc trigger on PDF upload            (extractor/deploy.sh)
#   4. Wait for any PDFs in the input bucket to be processed
#   5. Split markdown per-page, upload to GCS staging
#   6. Create a Vertex AI RAG Engine corpus, import the per-page files
#   7. Deploy the ADK agent to Agent Engine                  (agent/deploy.py)
#   8. (optional) Register agent in Gemini Enterprise         (agent/register_agent.py)
#
# Idempotent — re-run after edits. Each step exits early if its target
# already exists, except the agent step which always re-deploys (cheap).
#
# Required: gcloud, uv, an authenticated gcloud session, and a .env file
# (copy .env.example and fill in PROJECT at minimum).
#
# Usage:
#     cp .env.example .env
#     $EDITOR .env
#     ./deploy.sh                  # everything end-to-end
#     ./deploy.sh extractor        # just steps 1-3
#     ./deploy.sh agent            # just steps 5-7 (assumes extractor done + outputs exist)
#     ./deploy.sh register         # just step 8
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# ---------- Load .env ----------
if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Run: cp .env.example .env && \$EDITOR .env"
  exit 1
fi
set -a; source .env; set +a
: "${PROJECT:?PROJECT is required in .env}"

STEP="${1:-all}"

deploy_extractor() {
  echo
  echo "##############################################"
  echo "# 1-3 · Extractor (Cloud Run + Eventarc)"
  echo "##############################################"
  PROJECT="$PROJECT" REGION="$REGION" \
    INPUT_BUCKET="$INPUT_BUCKET" OUTPUT_BUCKET="$OUTPUT_BUCKET" \
    SERVICE="$SERVICE" SA_NAME="$SA_NAME" \
    TRIGGER_NAME="$TRIGGER_NAME" REPO="$REPO" \
    bash extractor/deploy.sh
}

wait_for_markdown() {
  echo
  echo "##############################################"
  echo "# 4 · Waiting for processed markdown"
  echo "##############################################"
  echo "Looking for .txt files in gs://${OUTPUT_BUCKET}/ ..."
  for i in {1..30}; do
    if gcloud storage ls "gs://${OUTPUT_BUCKET}/*.txt" --project="$PROJECT" >/dev/null 2>&1; then
      n=$(gcloud storage ls "gs://${OUTPUT_BUCKET}/*.txt" --project="$PROJECT" | wc -l)
      echo "  -> $n markdown file(s) found"
      return 0
    fi
    sleep 10
    echo "  ...waiting (iter $i/30)"
  done
  echo "ERROR: no .txt files in gs://${OUTPUT_BUCKET}/ after 5min."
  echo "Upload PDFs first:  gcloud storage cp foo.pdf gs://${INPUT_BUCKET}/"
  exit 1
}

build_per_page() {
  echo
  echo "##############################################"
  echo "# 5 · Per-page split + upload"
  echo "##############################################"
  local tmp_in
  tmp_in=$(mktemp -d)
  gcloud storage cp "gs://${OUTPUT_BUCKET}/*.txt" "${tmp_in}/" --project="$PROJECT"

  local tmp_out="eval/per_page_local"
  rm -rf "$tmp_out"
  python3 eval/build_per_page.py "$tmp_in" "$tmp_out"

  echo "Uploading per-page chunks to gs://${OUTPUT_BUCKET}/per_page/"
  gcloud storage rm -r "gs://${OUTPUT_BUCKET}/per_page/" --project="$PROJECT" 2>/dev/null || true
  gcloud storage cp "${tmp_out}"/*.txt "gs://${OUTPUT_BUCKET}/per_page/" --project="$PROJECT"
  rm -rf "$tmp_in"
}

create_corpus() {
  echo
  echo "##############################################"
  echo "# 6 · Vertex AI RAG Engine corpus"
  echo "##############################################"
  if [[ -n "${RAG_CORPUS_NAME:-}" ]]; then
    echo "RAG_CORPUS_NAME already set -> re-importing per-page files"
  else
    echo "Creating new RAG Engine corpus..."
  fi

  RAG_CORPUS_NAME=$(uv run --with "google-cloud-aiplatform[rag]" python3 - <<PYEOF
import sys, vertexai
from vertexai import rag

vertexai.init(project="$PROJECT", location="$REGION")

existing = "${RAG_CORPUS_NAME:-}"
if existing:
    name = existing
else:
    embed = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"))
    corpus = rag.create_corpus(
        display_name="docparse_per_page",
        backend_config=rag.RagVectorDbConfig(rag_embedding_model_config=embed),
    )
    name = corpus.name
    print(f"created: {name}", file=sys.stderr)

resp = rag.import_files(
    corpus_name=name,
    paths=["gs://${OUTPUT_BUCKET}/per_page/"],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=1000, chunk_overlap=100),
    ),
    max_embedding_requests_per_min=900,
)
print(f"imported={resp.imported_rag_files_count} failed={getattr(resp,'failed_rag_files_count','n/a')}",
      file=sys.stderr)
print(name)
PYEOF
)
  echo "Corpus: $RAG_CORPUS_NAME"

  if grep -q "^RAG_CORPUS_NAME=" .env; then
    sed -i.bak "s|^RAG_CORPUS_NAME=.*|RAG_CORPUS_NAME=${RAG_CORPUS_NAME}|" .env && rm .env.bak
  else
    echo "RAG_CORPUS_NAME=${RAG_CORPUS_NAME}" >> .env
  fi
}

deploy_agent() {
  echo
  echo "##############################################"
  echo "# 7 · ADK agent -> Vertex AI Agent Engine"
  echo "##############################################"
  : "${RAG_CORPUS_NAME:?RAG_CORPUS_NAME unset - run step 6 first}"
  ( cd agent && uv run python deploy.py )
}

register_in_ge() {
  if [[ -z "${GE_PROJECT_ID:-}" || -z "${AS_APP:-}" ]]; then
    echo
    echo "Skipping GE registration - GE_PROJECT_ID and/or AS_APP not set in .env"
    return 0
  fi
  echo
  echo "##############################################"
  echo "# 8 · Register in Gemini Enterprise (ALL_USERS)"
  echo "##############################################"
  ( cd agent && uv run python register_agent.py )
}

case "$STEP" in
  all)
    deploy_extractor
    wait_for_markdown
    build_per_page
    create_corpus
    deploy_agent
    register_in_ge
    ;;
  extractor) deploy_extractor ;;
  agent)     wait_for_markdown; build_per_page; create_corpus; deploy_agent ;;
  register)  register_in_ge ;;
  *) echo "usage: $0 [all|extractor|agent|register]"; exit 1 ;;
esac

echo
echo "==============================================="
echo "  docparse deploy complete"
echo "==============================================="
echo "  Upload PDFs:    gcloud storage cp foo.pdf gs://${INPUT_BUCKET}/"
echo "  Markdown out:   gs://${OUTPUT_BUCKET}/foo.txt"
echo "  Corpus:         ${RAG_CORPUS_NAME:-(not yet)}"
echo "  Agent Engine:   ${REASONING_ENGINE_RES:-(not yet)}"
echo "  GE app:         ${AS_APP:-(skipped)}"
echo "==============================================="
