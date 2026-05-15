"""Create RAG Engine corpus and import PDFs."""
import vertexai
from vertexai.preview import rag
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.adk.agents import Agent

PROJECT_ID = "sharepoint-wif"
LOCATION = "us-west1"  # No Spanner capacity restrictions
STAGING_BUCKET = "gs://sharepoint-wif-agent-staging"

RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "AGENT_MODEL": "gemini-2.5-flash",
}


def main():
    print(f"\n=== Creating RAG Engine corpus in {PROJECT_ID} ===")

    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    # Step 1: Create corpus
    print("\n1. Creating RAG corpus...")
    corpus = rag.create_corpus(
        display_name="docparse-accenture-metaverse",
        description="Accenture Metaverse PDF - extracted with docparse, 90.5% eval"
    )
    print(f"   ✓ Corpus created: {corpus.name}")
    corpus_name = corpus.name

    # Step 2: Import PDFs from GCS
    print("\n2. Importing PDFs from GCS...")
    print("   This may take 5-10 minutes...")

    import_response = rag.import_files(
        corpus_name=corpus_name,
        paths=["gs://sharepoint-wif-docparse-in/Accenture-Metaverse-Evolution-Before-Revolution.pdf"],
        chunk_size=512,
        chunk_overlap=100,
        max_embedding_requests_per_min=900
    )
    print(f"   ✓ Import complete: {import_response.imported_rag_files_count} files")

    # Step 3: Create agent with RAG retrieval
    print("\n3. Creating RAG Engine agent...")

    rag_agent = Agent(
        model="gemini-2.5-flash",
        name="rag_docparse_agent",
        description="RAG Engine with semantic search over docparse PDFs",
        instruction="""You answer questions about PDF reports using RAG retrieval.

WORKFLOW:
1. The RAG tool automatically retrieves relevant chunks semantically
2. Answer EXHAUSTIVELY using the retrieved content
3. Quote statistics and numbers VERBATIM
4. Do NOT say you lack access - RAG provides the data

Use ONLY the retrieved chunks to answer.""",
        tools=[rag.VertexRagStore(
            rag_corpora=[corpus_name],
            similarity_top_k=10
        )]
    )

    app = reasoning_engines.AdkApp(agent=rag_agent, enable_tracing=True)

    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-rag-engine",
        description="RAG Engine + semantic search + gemini-2.5-flash [90.5%]",
        requirements=["google-cloud-aiplatform[adk,agent_engines,rag]", "google-genai"],
        env_vars=RUNTIME_ENV_VARS,
    )

    print(f"\n✅ RAG ENGINE DEPLOYED")
    print(f"   Corpus: {corpus_name}")
    print(f"   Agent: {remote.resource_name}")

    return corpus_name, remote.resource_name


if __name__ == "__main__":
    main()
