"""docparse RAG agent — ADK agent with semantic re-ranker support.

Validated 2026-05-01: 92.5% composite on 216-question eval using full GA stack
(gemini-2.5 extraction + gemini-2.5-flash answering + semantic-ranker).

The custom retrieval tool wraps the genai SDK's RAG retrieval API because
ADK's built-in VertexAiRagRetrieval doesn't expose rag_retrieval_config
(needed for the re-ranker).

Required env vars:
    RAG_CORPUS_NAME        full resource name of the RAG corpus
    AGENT_MODEL            (default "gemini-2.5-flash")
    AGENT_TOP_K            (default 20)
    AGENT_USE_RERANKER     "true" or "false" (default "true")
"""
import os
from google.adk.agents import Agent
from .reranker_retrieval import reranker_retrieval_tool


MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")


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


root_agent = Agent(
    model=MODEL,
    name="docparse_rag_agent_ga",
    description=(
        "Answers questions about reports indexed by docparse. Full GA stack: "
        "gemini-2.5 extraction + gemini-2.5-flash answering + semantic re-ranker. "
        "92.5% composite on 216-question eval."
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[reranker_retrieval_tool],
)
