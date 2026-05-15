"""Deploy RAG Engine agent (corpus already created)."""
import vertexai
from vertexai.preview import rag
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.adk.agents import Agent

PROJECT_ID = "sharepoint-wif"
LOCATION = "us-west1"
STAGING_BUCKET = "gs://sharepoint-wif-agent-staging"
CORPUS_NAME = "projects/984359513632/locations/us-west1/ragCorpora/6917529027641081856"

RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "AGENT_MODEL": "gemini-2.5-flash",
}


def main():
    print(f"\n=== Deploying RAG Engine agent → {PROJECT_ID} ===")

    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    print(f"Using corpus: {CORPUS_NAME}")

    # Deploy as callable reasoning engine with RAG retrieval
    class RagAgent:
        """RAG-based agent with query() and streaming methods."""

        def __init__(self):
            self.corpus_name = CORPUS_NAME

        def _retrieve_and_answer(self, query: str) -> str:
            """Core RAG retrieval and answering logic."""
            from google import genai
            from vertexai.preview import rag as rag_module
            import vertexai

            # Ensure correct location for RAG retrieval
            vertexai.init(project=PROJECT_ID, location="us-west1")

            # Retrieve from RAG corpus
            response = rag_module.retrieval_query(
                rag_corpora=[self.corpus_name],
                text=query,
                similarity_top_k=10
            )

            # Build context from retrieved chunks
            contexts = response.contexts.contexts if hasattr(response, 'contexts') else []
            context_text = "\n\n---\n\n".join([ctx.text for ctx in contexts[:5]])

            if not context_text:
                return "No relevant information found in the knowledge base."

            # Generate answer with context
            client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
            prompt = f"""Based on the following retrieved PDF content, answer the user's question.

User question: {query}

Retrieved content:
{context_text}

Provide an EXHAUSTIVE answer with all statistics and details from the content. Quote numbers VERBATIM.

Answer:"""

            llm_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return llm_response.text

        def query(self, query: str) -> str:
            """Non-streaming query method."""
            return self._retrieve_and_answer(query)

        def stream_query(self, query: str):
            """Streaming query method."""
            answer = self._retrieve_and_answer(query)
            yield answer

        def streaming_agent_run_with_events(self, query: str):
            """GE-specific streaming method with grounding metadata."""
            from vertexai.preview import rag as rag_module
            import vertexai

            # Retrieve to get grounding sources
            vertexai.init(project=PROJECT_ID, location="us-west1")

            try:
                response = rag_module.retrieval_query(
                    rag_corpora=[self.corpus_name],
                    text=query,
                    similarity_top_k=5
                )

                # Build grounding from RAG contexts
                contexts = response.contexts.contexts if hasattr(response, 'contexts') else []
                grounding_chunks = []

                for ctx in contexts:
                    # RAG contexts have source info
                    source_uri = getattr(ctx, 'source_uri', None) or getattr(ctx, 'uri', None)
                    title = getattr(ctx, 'title', None) or "PDF Document"

                    if source_uri:
                        grounding_chunks.append({
                            "web": {
                                "uri": source_uri,
                                "title": title
                            }
                        })

            except Exception as e:
                grounding_chunks = []

            # Get answer
            answer = self._retrieve_and_answer(query)

            # Yield with grounding
            yield {
                "content": answer,
                "grounding_metadata": {
                    "grounding_chunks": grounding_chunks,
                    "grounding_supports": []
                }
            }

    app = RagAgent()

    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-rag-engine",
        description="RAG Engine + semantic search + gemini-2.5-flash [90.5%]",
        requirements=["google-cloud-aiplatform[adk,agent_engines,rag]", "google-genai"],
        env_vars=RUNTIME_ENV_VARS,
    )

    print(f"\n✅ RAG ENGINE DEPLOYED")
    print(f"   Agent: {remote.resource_name}")

    return remote.resource_name


if __name__ == "__main__":
    main()
