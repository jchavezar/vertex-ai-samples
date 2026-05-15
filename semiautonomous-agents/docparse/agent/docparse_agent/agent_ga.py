"""docparse RAG agent — GA-compatible version (gemini-2.5-flash).

Validated 2026-05-01: 92.1% composite using full GA stack (gemini-2.5 extraction
+ gemini-2.5-flash answering, no re-ranker). Clears 90% target by +2.1 pts.

Uses ADK's built-in VertexAiRagRetrieval (no custom tool) with top_k=20.
"""
import os
from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag


CORPUS = os.environ["RAG_CORPUS_NAME"]
MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")
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
        "corpus (GA-extracted with gemini-2.5 models)."
    ),
    rag_resources=[rag.RagResource(rag_corpus=CORPUS)],
    similarity_top_k=TOP_K,
    vector_distance_threshold=0.5,
)


root_agent = Agent(
    model=MODEL,
    name="docparse_rag_agent_ga",
    description=(
        "Answers questions about reports indexed by docparse. Full GA stack: "
        "gemini-2.5 extraction + gemini-2.5-flash answering. 92.1% composite "
        "on 216-question eval."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[retrieval_tool],
)
