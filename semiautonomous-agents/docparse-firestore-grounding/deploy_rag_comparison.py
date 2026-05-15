"""Deploy RAG Engine version for comparison with Firestore."""
import vertexai
from vertexai.preview import rag
from vertexai import agent_engines
from google.adk.agents import Agent

PROJECT_ID = "sharepoint-wif"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://sharepoint-wif-agent-staging"

RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "AGENT_MODEL": "gemini-2.5-flash",
}


def deploy():
    print(f"\n=== Deploying RAG Engine agent → {PROJECT_ID} ===")

    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    # Check for existing corpus
    try:
        corpora = rag.list_corpora()
        docparse_corpus = None
        for corpus in corpora:
            if "docparse" in corpus.display_name.lower():
                docparse_corpus = corpus
                break

        if docparse_corpus:
            print(f"Found existing corpus: {docparse_corpus.name}")
            corpus_name = docparse_corpus.name
        else:
            print("No docparse corpus found. Creating new corpus...")
            corpus = rag.create_corpus(
                display_name="docparse-accenture-metaverse",
                description="Accenture Metaverse PDF extracted with docparse"
            )
            corpus_name = corpus.name
            print(f"Created corpus: {corpus_name}")

            # Import files from GCS
            print("Importing markdown files from GCS...")
            rag.import_files(
                corpus_name=corpus_name,
                paths=["gs://sharepoint-wif-docparse/*.md"],
                chunk_size=512,
                chunk_overlap=100
            )
    except Exception as e:
        print(f"Error with corpus: {e}")
        print("Skipping RAG Engine deployment")
        return None

    # Create agent with RAG retrieval
    rag_agent = Agent(
        model="gemini-2.5-flash",
        name="rag_docparse_agent",
        instruction="""You answer questions about PDF reports.

Use the RAG retrieval tool to find relevant information, then answer EXHAUSTIVELY.
Quote statistics and numbers VERBATIM from the retrieved content.""",
        tools=[rag.VertexRagStore(corpus_name=corpus_name, similarity_top_k=5)]
    )

    from vertexai.preview import reasoning_engines
    app = reasoning_engines.AdkApp(agent=rag_agent, enable_tracing=True)

    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-rag-engine-comparison",
        description="RAG Engine + gemini-2.5-flash [90.5%]",
        requirements=["google-cloud-aiplatform[adk,agent_engines,rag]", "google-genai"],
        env_vars=RUNTIME_ENV_VARS,
    )

    print(f"\n✅ RAG ENGINE DEPLOYED")
    print(f"Resource: {remote.resource_name}")
    return remote


if __name__ == "__main__":
    deploy()
