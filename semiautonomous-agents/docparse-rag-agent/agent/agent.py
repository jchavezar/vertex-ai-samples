"""docparse RAG agent — ADK agent that answers questions about a Vertex AI
RAG Engine corpus and exposes itself to Gemini Enterprise.

Validated 2026-04-25: 92.9% composite on a 216-question docparse eval, vs
87.4% for the same retrieval without per-page chunking + exhaustive prompt,
vs 81% for Discovery Engine streamAssist on the same markdown.

The retrieval target is a RAG Engine corpus that contains the docparse-
extracted markdown, split per-page so chunk text starts with a "Page N"
header. That single trick lets the model ground page-anchored questions
("on page 11", "per page 23") against an embedding rather than relying on
chunk metadata.

Required env vars (read at import time so the deployed Agent Engine
container picks them up at cold start):

    RAG_CORPUS_NAME   full resource name of the RAG corpus, e.g.
                      "projects/<project-number>/locations/us-central1/
                      ragCorpora/<corpus-id>"
    AGENT_MODEL       Gemini model id (default "gemini-3-flash-preview")
    AGENT_TOP_K       similarity_top_k for the retrieval tool (default 20)

The model is bare ("gemini-3-flash-preview") — the genai client routes to
the `global` endpoint via GOOGLE_CLOUD_LOCATION=global, set in deploy.py
because the Gemini 3 preview models only exist in `global` and a regional
path 404s.
"""

import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag


RAG_CORPUS = os.environ["RAG_CORPUS_NAME"]
MODEL = os.environ.get("AGENT_MODEL", "gemini-3-flash-preview")
TOP_K = int(os.environ.get("AGENT_TOP_K", "20"))


SYSTEM_INSTRUCTION = """You answer questions about a corpus of report PDFs
that have been extracted to markdown by the docparse pipeline.

CRITICAL RULES:
1. Always check retrieved chunks first. Each chunk represents ONE page and
   starts with a header like "# <doc title> — Page N" — use that header to
   ground page-anchored questions ("on page 11", "per page 23").
2. Prefer EXHAUSTIVE over terse. If chunks contain additional related detail
   (sample sizes, units, source captions, sub-bullets, named entities),
   include them. Don't summarize away facts.
3. For chart values, quote the printed value VERBATIM from the markdown
   table. Do not reformat ranges. "(1.0)-1.1%" stays "(1.0)-1.1%", not
   "(1.0)% to 1.1%".
4. If chunks contain the answer (even buried in narrative or a table),
   state it directly. Do NOT say "I cannot find" when a search result
   contains the value.
5. If the question asks for a list of N items, list all N — don't say
   "there are N" without enumerating them.
6. Do NOT ask the user to upload anything. Do NOT search the web. Use only
   the retrieved chunks."""


retrieval_tool = VertexAiRagRetrieval(
    name="docparse_corpus_retrieval",
    description=(
        "Retrieves relevant page-level chunks from the docparse markdown "
        "corpus for the connected reports."
    ),
    rag_resources=[rag.RagResource(rag_corpus=RAG_CORPUS)],
    similarity_top_k=TOP_K,
    vector_distance_threshold=0.5,
)


root_agent = Agent(
    model=MODEL,
    name="docparse_rag_agent",
    description=(
        "Answers questions about reports indexed by docparse, citing the "
        "exact source page for every fact."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[retrieval_tool],
)
