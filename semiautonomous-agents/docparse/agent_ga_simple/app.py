"""Standalone Cloud Run endpoint — gemini-2.5-flash + RAG + re-ranker.

No ADK, just FastAPI wrapping the genai SDK code that got 92.5%.
Can be registered in Gemini Enterprise as a custom agent endpoint.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

CORPUS = os.environ["RAG_CORPUS_NAME"]
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
MODEL = os.environ.get("AGENT_MODEL", "gemini-2.5-flash")
TOP_K = int(os.environ.get("AGENT_TOP_K", "20"))

SYSTEM_INSTRUCTION = """You answer questions about a corpus of report PDFs
extracted to markdown by docparse.

CRITICAL RULES:
1. Check retrieved chunks first. Each chunk starts with "# <doc> — Page N".
2. Prefer EXHAUSTIVE — include all relevant detail from chunks.
3. Quote chart values VERBATIM. Do not reformat ranges.
4. If chunks contain the answer, state it directly. Do NOT say "I cannot find".
5. Do NOT search the web. Use only retrieved chunks."""

client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)

# Pre-build the re-ranker config (reused for every query)
rag_retrieval_config = types.RagRetrievalConfig(
    top_k=TOP_K,
    ranking=types.RagRetrievalConfigRanking(
        rank_service=types.RagRetrievalConfigRankingRankService(
            model_name="semantic-ranker-default@latest"
        )
    ),
)

tools = [types.Tool(retrieval=types.Retrieval(
    vertex_rag_store=types.VertexRagStore(
        rag_resources=[types.VertexRagStoreRagResource(rag_corpus=CORPUS)],
        rag_retrieval_config=rag_retrieval_config,
    )
))]

cfg = types.GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    max_output_tokens=8192,
    system_instruction=SYSTEM_INSTRUCTION,
    safety_settings=[
        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
    ],
    tools=tools,
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    grounding_chunks: list[dict] = []


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Answer a question using RAG + re-ranker."""
    try:
        resp = await client.aio.models.generate_content(
            model=MODEL,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=req.query)])],
            config=cfg,
        )
        answer = (resp.text or "").strip()

        # Extract grounding chunks if present
        chunks = []
        if resp.candidates and len(resp.candidates) > 0:
            gm = resp.candidates[0].grounding_metadata
            if gm and gm.grounding_chunks:
                for gc in gm.grounding_chunks:
                    chunks.append({
                        "uri": getattr(gc, "uri", ""),
                        "title": getattr(gc, "title", ""),
                    })

        return QueryResponse(answer=answer, grounding_chunks=chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)[:300]}")


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL, "corpus": CORPUS, "reranker": "semantic-ranker-default@latest"}
