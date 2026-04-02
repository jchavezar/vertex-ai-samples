"""
Deep RAG Evaluation Module
Compares Hierarchical RAG vs Simple RAG with detailed metrics and grounding analysis.
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from google import genai
from google.genai.types import EmbedContentConfig
from google.cloud import bigquery

logger = logging.getLogger(__name__)

@dataclass
class GroundedSpan:
    """A span of text in the answer with grounding information."""
    text: str
    start_idx: int
    end_idx: int
    is_grounded: bool
    source_chunk_id: Optional[str] = None
    source_content: Optional[str] = None
    confidence: float = 0.0

@dataclass
class EvaluationScore:
    """Detailed evaluation scores for a single RAG approach."""
    faithfulness: int  # 0-5: Are all claims supported by context?
    groundedness: int  # 0-5: Do citations point to correct sources?
    hallucination_count: int  # Number of hallucinated claims
    completeness: int  # 0-5: Did answer cover all relevant info?
    answer_relevance: int  # 0-5: Does answer address the query?
    context_precision: float  # % of retrieved chunks actually used
    total_score: int  # Sum out of 30
    grounded_percentage: float  # % of answer text that is grounded
    ungrounded_percentage: float  # % that may be hallucinated
    grounded_spans: List[Dict]  # Spans with grounding info
    hallucination_examples: List[str]  # Specific hallucinated claims
    reasoning: str  # Judge's explanation

@dataclass
class RAGComparison:
    """Full comparison result between Hierarchical and Simple RAG."""
    query: str
    hierarchical_answer: str
    simple_answer: str
    hierarchical_context: List[Dict]
    simple_context: List[Dict]
    hierarchical_score: EvaluationScore
    simple_score: EvaluationScore
    winner: str
    winner_reasoning: str
    eval_time_seconds: float


async def hierarchical_search(
    query_text: str,
    top_k: int = 4,
    expand_related: bool = True
) -> Tuple[List[Dict], List[Dict]]:
    """
    Hierarchical RAG: Search children chunks, fetch parent context, expand related entities.
    Returns: (children_chunks, parent_contexts)
    """
    from pipeline import search_embeddings_in_bq

    # 1. Search for matching child chunks
    children = await search_embeddings_in_bq(query_text, top_k=top_k)

    if not children:
        return [], []

    # 2. For each child, fetch the parent chunk (same page, broader context)
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    client = bigquery.Client(project=project_id)

    parent_contexts = []
    seen_parents = set()

    for child in children:
        # Parent is identified by document + page + entity type pattern
        chunk_id = child.get("chunk_id", "")
        doc_name = child.get("document_name", "")
        page_num = child.get("page_number", 0)

        # Find parent chunk (the one without _c suffix, or the main section)
        parent_key = f"{doc_name}_{page_num}"
        if parent_key in seen_parents:
            continue
        seen_parents.add(parent_key)

        # Query for all chunks from same page to get full context
        query = f"""
        SELECT chunk_id, document_name, page_number, entity_type, content
        FROM `{project_id}.esg_demo_data.document_embeddings_fs`
        WHERE document_name = @doc_name AND page_number = @page_num
        ORDER BY chunk_id
        LIMIT 10
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("doc_name", "STRING", doc_name),
                bigquery.ScalarQueryParameter("page_num", "INT64", page_num),
            ]
        )

        try:
            rows = client.query(query, job_config=job_config).result()
            page_chunks = [dict(row) for row in rows]

            # Combine into parent context
            combined_content = "\n".join([c.get("content", "") for c in page_chunks])
            parent_contexts.append({
                "document_name": doc_name,
                "page_number": page_num,
                "content": combined_content,
                "child_chunks": page_chunks,
                "matched_child_id": chunk_id
            })
        except Exception as e:
            logger.error(f"Failed to fetch parent context: {e}")

    # 3. Optionally expand with related entities (e.g., other agents mentioned)
    if expand_related:
        expanded = await _expand_related_entities(children, client, project_id)
        for exp in expanded:
            if exp.get("chunk_id") not in [c.get("chunk_id") for c in children]:
                children.append(exp)

    return children, parent_contexts


async def _expand_related_entities(
    chunks: List[Dict],
    client: bigquery.Client,
    project_id: str
) -> List[Dict]:
    """Find related entities mentioned in the chunks (e.g., other agents)."""
    expanded = []

    # Extract entity names mentioned (simple pattern matching)
    all_content = " ".join([c.get("content", "") for c in chunks])

    # Look for agent patterns like "auth_agent", "billing_agent", etc.
    import re
    agent_pattern = r'\b(\w+_agent)\b'
    mentioned_agents = set(re.findall(agent_pattern, all_content.lower()))

    if not mentioned_agents:
        return expanded

    # Query for chunks that are primarily about these agents
    for agent_name in list(mentioned_agents)[:3]:  # Limit expansion
        query = f"""
        SELECT chunk_id, document_name, page_number, entity_type, content, 0.5 as distance
        FROM `{project_id}.esg_demo_data.document_embeddings_fs`
        WHERE LOWER(entity_type) = @agent_name
        LIMIT 2
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("agent_name", "STRING", agent_name),
            ]
        )

        try:
            rows = client.query(query, job_config=job_config).result()
            for row in rows:
                expanded.append(dict(row))
        except Exception as e:
            logger.debug(f"Expansion query failed for {agent_name}: {e}")

    return expanded


async def simple_search(query_text: str, top_k: int = 5) -> List[Dict]:
    """Simple RAG: Just flat vector search, no parent context or expansion."""
    from pipeline import search_embeddings_in_bq
    return await search_embeddings_in_bq(query_text, top_k=top_k)


async def generate_answer(
    query: str,
    context_chunks: List[Dict],
    model: str = "gemini-2.5-flash"
) -> str:
    """Generate an answer using the given context."""
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.agents import LlmAgent
    from google.genai import types
    import uuid

    if not context_chunks:
        return "No relevant context found to answer this question."

    # Build context string
    context_str = "RETRIEVED CONTEXT:\n"
    for idx, chunk in enumerate(context_chunks):
        context_str += f"[{idx+1}] (Doc: {chunk.get('document_name', 'Unknown')}, "
        context_str += f"Page: {chunk.get('page_number', '?')}): "
        context_str += f"{chunk.get('content', '')}\n\n"

    instruction = """You are an expert document analyst. Answer the question using ONLY the provided context.
IMPORTANT: Cite your sources using [1], [2], etc. for EVERY claim you make.
If information is not in the context, say "This information is not available in the provided documents."
Do NOT make up information. Be precise and factual."""

    agent = LlmAgent(name="answer_gen", model=model, instruction=instruction)
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="eval_answer")

    session_id = str(uuid.uuid4())
    await session_service.create_session(user_id="eval", session_id=session_id, app_name="eval_answer")

    content = types.Content(role="user", parts=[
        types.Part.from_text(text=f"Question: {query}\n\n{context_str}")
    ])

    response_text = ""
    async for event in runner.run_async(user_id="eval", session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    return response_text


async def deep_evaluate(
    query: str,
    answer: str,
    context_chunks: List[Dict],
    model: str = "gemini-2.5-flash"
) -> EvaluationScore:
    """
    Deep evaluation using LLM-as-Judge.
    Evaluates multiple dimensions and identifies grounded vs ungrounded spans.
    """
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.agents import LlmAgent
    from google.genai import types
    import uuid

    # Build context for evaluation
    context_str = ""
    for idx, chunk in enumerate(context_chunks):
        context_str += f"[{idx+1}]: {chunk.get('content', '')}\n"

    evaluation_prompt = f"""You are an expert RAG evaluation judge. Analyze the following:

QUERY: {query}

RETRIEVED CONTEXT:
{context_str}

GENERATED ANSWER:
{answer}

Evaluate the answer on these dimensions (score 0-5 each):

1. **Faithfulness** (0-5): Are ALL claims in the answer supported by the context?
   - 5 = Every claim is directly supported
   - 0 = Multiple unsupported claims

2. **Groundedness** (0-5): Do the citations [1], [2] etc. correctly point to the right source?
   - 5 = All citations accurate
   - 0 = Citations are wrong or missing

3. **Completeness** (0-5): Did the answer cover all relevant information from the context?
   - 5 = Comprehensive coverage
   - 0 = Missed critical information

4. **Answer Relevance** (0-5): Does the answer directly address the query?
   - 5 = Perfectly addresses the question
   - 0 = Off-topic or tangential

5. **Context Precision**: What percentage of the retrieved chunks were actually useful for answering?

6. **Grounding Analysis**: For EACH sentence or claim in the answer, determine:
   - Is it GROUNDED (directly from context)?
   - Is it UNGROUNDED (not in context, potentially hallucinated)?
   - Provide the exact text span and source if grounded

Return your evaluation as valid JSON:
{{
    "faithfulness": <0-5>,
    "groundedness": <0-5>,
    "completeness": <0-5>,
    "answer_relevance": <0-5>,
    "context_precision": <0.0-1.0>,
    "hallucination_count": <number>,
    "hallucination_examples": ["example1", "example2"],
    "grounded_spans": [
        {{"text": "exact text from answer", "is_grounded": true, "source_id": "1", "confidence": 0.95}},
        {{"text": "another span", "is_grounded": false, "source_id": null, "confidence": 0.0}}
    ],
    "grounded_percentage": <0.0-100.0>,
    "ungrounded_percentage": <0.0-100.0>,
    "reasoning": "Brief explanation of your evaluation"
}}

Be thorough and precise. Identify EVERY claim and its grounding status."""

    agent = LlmAgent(
        name="deep_evaluator",
        model=model,
        instruction="You are an expert RAG evaluation judge. Always respond with valid JSON."
    )
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="deep_eval")

    session_id = str(uuid.uuid4())
    await session_service.create_session(user_id="eval", session_id=session_id, app_name="deep_eval")

    content = types.Content(role="user", parts=[
        types.Part.from_text(text=evaluation_prompt)
    ])

    response_text = ""
    async for event in runner.run_async(user_id="eval", session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    # Parse the JSON response
    try:
        # Extract JSON from response (handle markdown code blocks)
        json_str = response_text
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        eval_data = json.loads(json_str.strip())

        total = (
            eval_data.get("faithfulness", 0) +
            eval_data.get("groundedness", 0) +
            eval_data.get("completeness", 0) +
            eval_data.get("answer_relevance", 0) +
            int(eval_data.get("context_precision", 0) * 10)  # Scale to 0-10
        )

        return EvaluationScore(
            faithfulness=eval_data.get("faithfulness", 0),
            groundedness=eval_data.get("groundedness", 0),
            hallucination_count=eval_data.get("hallucination_count", 0),
            completeness=eval_data.get("completeness", 0),
            answer_relevance=eval_data.get("answer_relevance", 0),
            context_precision=eval_data.get("context_precision", 0.0),
            total_score=total,
            grounded_percentage=eval_data.get("grounded_percentage", 0.0),
            ungrounded_percentage=eval_data.get("ungrounded_percentage", 0.0),
            grounded_spans=eval_data.get("grounded_spans", []),
            hallucination_examples=eval_data.get("hallucination_examples", []),
            reasoning=eval_data.get("reasoning", "")
        )
    except Exception as e:
        logger.error(f"Failed to parse evaluation response: {e}")
        logger.error(f"Response was: {response_text}")
        # Return default scores
        return EvaluationScore(
            faithfulness=0, groundedness=0, hallucination_count=0,
            completeness=0, answer_relevance=0, context_precision=0.0,
            total_score=0, grounded_percentage=0.0, ungrounded_percentage=100.0,
            grounded_spans=[], hallucination_examples=[],
            reasoning=f"Evaluation parsing failed: {str(e)}"
        )


async def compare_rag_approaches(
    query: str,
    model: str = "gemini-2.5-flash"
) -> RAGComparison:
    """
    Full comparison between Hierarchical RAG and Simple RAG.
    """
    import time
    start_time = time.time()

    # 1. Run both search approaches in parallel
    hierarchical_task = hierarchical_search(query, top_k=4, expand_related=True)
    simple_task = simple_search(query, top_k=5)

    (h_children, h_parents), s_chunks = await asyncio.gather(hierarchical_task, simple_task)

    # 2. Build context for hierarchical (use parent context)
    h_context = []
    for parent in h_parents:
        h_context.append({
            "chunk_id": parent.get("matched_child_id", ""),
            "document_name": parent.get("document_name", ""),
            "page_number": parent.get("page_number", 0),
            "entity_type": "PARENT_CONTEXT",
            "content": parent.get("content", ""),
            "child_match": next((c.get("content", "")[:150] for c in h_children
                                if c.get("chunk_id") == parent.get("matched_child_id")), "")
        })

    # Add expanded entities
    for child in h_children:
        if child.get("chunk_id") not in [p.get("matched_child_id") for p in h_parents]:
            h_context.append(child)

    # 3. Generate answers in parallel
    h_answer_task = generate_answer(query, h_context, model)
    s_answer_task = generate_answer(query, s_chunks, model)

    h_answer, s_answer = await asyncio.gather(h_answer_task, s_answer_task)

    # 4. Deep evaluate both answers in parallel
    h_eval_task = deep_evaluate(query, h_answer, h_context, model)
    s_eval_task = deep_evaluate(query, s_answer, s_chunks, model)

    h_score, s_score = await asyncio.gather(h_eval_task, s_eval_task)

    # 5. Determine winner
    if h_score.total_score > s_score.total_score:
        winner = "hierarchical"
        winner_reasoning = f"Hierarchical RAG scored {h_score.total_score} vs Simple RAG's {s_score.total_score}. "
        winner_reasoning += f"Hierarchical had {h_score.grounded_percentage:.1f}% grounded content vs {s_score.grounded_percentage:.1f}%."
    elif s_score.total_score > h_score.total_score:
        winner = "simple"
        winner_reasoning = f"Simple RAG scored {s_score.total_score} vs Hierarchical RAG's {h_score.total_score}."
    else:
        winner = "tie"
        winner_reasoning = f"Both approaches scored {h_score.total_score}."

    eval_time = time.time() - start_time

    return RAGComparison(
        query=query,
        hierarchical_answer=h_answer,
        simple_answer=s_answer,
        hierarchical_context=[asdict_safe(c) for c in h_context] if h_context else [],
        simple_context=s_chunks,
        hierarchical_score=h_score,
        simple_score=s_score,
        winner=winner,
        winner_reasoning=winner_reasoning,
        eval_time_seconds=eval_time
    )


def asdict_safe(obj):
    """Convert to dict safely."""
    if isinstance(obj, dict):
        return obj
    try:
        return asdict(obj)
    except:
        return dict(obj) if hasattr(obj, '__iter__') else str(obj)


def format_comparison_for_frontend(comparison: RAGComparison) -> Dict:
    """Format the comparison result for the frontend."""
    return {
        "query": comparison.query,
        "hierarchical": {
            "answer": comparison.hierarchical_answer,
            "context": comparison.hierarchical_context,
            "context_chars": sum(len(c.get("content", "")) for c in comparison.hierarchical_context),
            "scores": {
                "faithfulness": comparison.hierarchical_score.faithfulness,
                "groundedness": comparison.hierarchical_score.groundedness,
                "completeness": comparison.hierarchical_score.completeness,
                "answer_relevance": comparison.hierarchical_score.answer_relevance,
                "context_precision": comparison.hierarchical_score.context_precision,
                "total": comparison.hierarchical_score.total_score,
            },
            "grounding": {
                "grounded_percentage": comparison.hierarchical_score.grounded_percentage,
                "ungrounded_percentage": comparison.hierarchical_score.ungrounded_percentage,
                "grounded_spans": comparison.hierarchical_score.grounded_spans,
                "hallucination_count": comparison.hierarchical_score.hallucination_count,
                "hallucination_examples": comparison.hierarchical_score.hallucination_examples,
            },
            "reasoning": comparison.hierarchical_score.reasoning,
        },
        "simple": {
            "answer": comparison.simple_answer,
            "context": comparison.simple_context,
            "context_chars": sum(len(c.get("content", "")) for c in comparison.simple_context),
            "scores": {
                "faithfulness": comparison.simple_score.faithfulness,
                "groundedness": comparison.simple_score.groundedness,
                "completeness": comparison.simple_score.completeness,
                "answer_relevance": comparison.simple_score.answer_relevance,
                "context_precision": comparison.simple_score.context_precision,
                "total": comparison.simple_score.total_score,
            },
            "grounding": {
                "grounded_percentage": comparison.simple_score.grounded_percentage,
                "ungrounded_percentage": comparison.simple_score.ungrounded_percentage,
                "grounded_spans": comparison.simple_score.grounded_spans,
                "hallucination_count": comparison.simple_score.hallucination_count,
                "hallucination_examples": comparison.simple_score.hallucination_examples,
            },
            "reasoning": comparison.simple_score.reasoning,
        },
        "winner": comparison.winner,
        "winner_reasoning": comparison.winner_reasoning,
        "eval_time_seconds": comparison.eval_time_seconds,
    }
