"""LLM-based extraction of problem-solution patterns from conversation segments.

Uses Claude on Vertex AI to analyze each segment and extract structured
knowledge items with confidence scores.
"""

import os
import re
import json
import asyncio
import logging

from google import genai
from google.genai.types import GenerateContentConfig

from pipeline.models import Segment, KnowledgeItem, FailedAttempt, PlaybookItem

logger = logging.getLogger(__name__)

EXTRACTION_MODEL = os.environ.get("EXTRACTION_MODEL", "gemini-2.5-flash")
MAX_CONCURRENT = 10

EXTRACTION_PROMPT = """You are analyzing a conversation segment from a Claude Code coding assistant session.
Your job is to determine if a technical problem was solved in this segment, and if so,
extract a structured knowledge item.

CONVERSATION SEGMENT:
---
{conversation}
---

METADATA:
- Session ID: {session_id}
- Model: {model_id}
- Timestamp range: {start_time} to {end_time}
- Working directory: {cwd}
- Git branch: {git_branch}
- Tools used: {tools_list}

INSTRUCTIONS:
1. Was a specific technical problem identified AND solved in this segment?
   - If NO problem was solved (just exploration, reading, planning, chatting, or the problem remains unresolved), respond with: {{"solved": false}}
   - If YES, continue to extract the fields below.

2. Extract these fields as JSON:
{{
  "solved": true,
  "problem": "One-sentence description of the problem",
  "error_message": "The exact error message if one appeared, or null",
  "failed_attempts": [
    {{
      "attempt": "What was tried and didn't work",
      "reason_failed": "Why it failed",
      "score": 0.0
    }}
  ],
  "solution": "The final working solution - be specific about what code/config/command fixed it",
  "solution_score": 0.0,
  "anti_patterns": ["Things to avoid when encountering this problem"],
  "services": ["List of GCP/cloud services or technologies involved"],
  "search_text": "A natural language sentence combining problem and solution, optimized for semantic search"
}}

SCORING GUIDELINES:
- solution_score 0.9-1.0: Solution verified working, clear cause identified, generalizable
- solution_score 0.7-0.8: Solution appears to work but wasn't fully verified, or is environment-specific
- solution_score 0.5-0.6: Partial fix or workaround, root cause unclear
- solution_score 0.3-0.4: Attempted fix, unclear if it resolved the issue
- solution_score 0.0-0.2: Guess or suggestion, not actually tested

- failed_attempt score: how close to the solution it was (1.0 = almost worked, 0.0 = completely wrong approach)

Respond with ONLY valid JSON, no markdown fences, no explanation."""


_genai_client = None


def get_genai_client():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    return _genai_client


MAX_IMAGES_PER_SEGMENT = 5  # limit total images sent to extraction LLM


def format_segment_for_extraction(segment: Segment) -> tuple[str, list[dict]]:
    """Build cleaned conversation text + images from a segment.

    Returns:
        Tuple of (conversation_text, image_parts) where image_parts
        are dicts with {media_type, data} for multimodal input.
    """
    lines = []
    image_parts = []

    for msg in segment.messages:
        if msg.type == "system":
            continue

        role_label = msg.role or msg.type
        if msg.content_text:
            lines.append(f"[{role_label}]: {msg.content_text}")

        if msg.tool_uses:
            lines.append(f"  (tools: {', '.join(msg.tool_uses)})")

        # Include truncated tool results for context
        for result in msg.tool_results[:3]:
            truncated = result[:500]
            lines.append(f"  [tool_result]: {truncated}")

        # Collect images (screenshots, error screens, etc.)
        for img in msg.images:
            if len(image_parts) < MAX_IMAGES_PER_SEGMENT and img.data:
                lines.append(f"  [screenshot attached — see image {len(image_parts) + 1}]")
                image_parts.append({
                    "media_type": img.media_type,
                    "data": img.data,
                })

    return "\n".join(lines), image_parts


async def extract_knowledge(
    segment: Segment,
    semaphore: asyncio.Semaphore | None = None,
) -> KnowledgeItem | None:
    """Extract a knowledge item from a conversation segment.

    Args:
        segment: A topic-coherent conversation segment.
        semaphore: Optional concurrency limiter.

    Returns:
        KnowledgeItem if a problem was solved, None otherwise.
    """
    conversation_text, image_parts = format_segment_for_extraction(segment)
    if not conversation_text.strip():
        return None

    model_id = segment.model_ids[0] if segment.model_ids else "unknown"

    prompt_text = EXTRACTION_PROMPT.format(
        conversation=conversation_text,
        session_id=segment.session_id,
        model_id=model_id,
        start_time=segment.start_time or "unknown",
        end_time=segment.end_time or "unknown",
        cwd=segment.cwd or "unknown",
        git_branch=segment.git_branch or "unknown",
        tools_list=", ".join(segment.tools_used) or "none",
    )

    # Build multimodal content: text prompt + images
    from google.genai.types import Part, Blob
    contents = [Part.from_text(text=prompt_text)]
    for img in image_parts:
        contents.append(Part.from_bytes(
            data=__import__("base64").b64decode(img["data"]),
            mime_type=img["media_type"],
        ))

    client = get_genai_client()

    async def _call():
        response = await client.aio.models.generate_content(
            model=EXTRACTION_MODEL,
            contents=contents,
            config=GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )
        return response.text

    try:
        if semaphore:
            async with semaphore:
                raw_response = await _call()
        else:
            raw_response = await _call()

        # Parse JSON response
        cleaned = raw_response.strip()
        # Remove markdown fences if present
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:-1])
        # Fix trailing commas (common Gemini issue)
        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

        data = json.loads(cleaned)

        if not data.get("solved"):
            return None

        # Build expanded_messages (cleaned conversation for later retrieval)
        expanded = []
        for msg in segment.messages:
            if msg.type == "system":
                continue
            entry = {
                "role": msg.role or msg.type,
                "text": msg.content_text,
            }
            if msg.tool_uses:
                entry["tools_used"] = msg.tool_uses
            expanded.append(entry)

        failed = [
            FailedAttempt(
                attempt=fa.get("attempt", ""),
                reason_failed=fa.get("reason_failed", ""),
                score=max(0.0, min(1.0, fa.get("score", 0.0))),
            )
            for fa in data.get("failed_attempts", [])
        ]

        item = KnowledgeItem(
            session_id=segment.session_id,
            model_id=model_id,
            timestamp=segment.start_time,
            problem=data.get("problem", ""),
            error_message=data.get("error_message"),
            solution=data.get("solution", ""),
            solution_score=max(0.0, min(1.0, data.get("solution_score", 0.5))),
            failed_attempts=failed,
            anti_patterns=data.get("anti_patterns", []),
            services=data.get("services", []),
            tools_used=segment.tools_used,
            search_text=data.get("search_text", ""),
            anchor_idx=segment.end_idx,
            window=(segment.start_idx, segment.end_idx),
            expanded_messages=expanded,
        )

        logger.info(
            f"Extracted: [{item.solution_score:.1f}] {item.problem[:80]}"
        )
        return item

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse LLM response for segment {segment.start_idx}-{segment.end_idx}: {e}")
        return None
    except Exception as e:
        logger.error(f"Extraction error for segment {segment.start_idx}-{segment.end_idx}: {e}")
        return None


async def extract_batch(
    segments: list[Segment],
    max_concurrent: int = MAX_CONCURRENT,
) -> list[KnowledgeItem]:
    """Extract knowledge items from multiple segments concurrently.

    Args:
        segments: List of conversation segments.
        max_concurrent: Max concurrent LLM calls.

    Returns:
        List of extracted KnowledgeItem (only resolved ones).
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = [extract_knowledge(seg, semaphore) for seg in segments]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    items = []
    errors = 0
    skipped = 0
    for r in results:
        if isinstance(r, Exception):
            errors += 1
            logger.error(f"Extraction failed: {r}")
        elif r is None:
            skipped += 1
        else:
            items.append(r)

    logger.info(
        f"Extraction complete: {len(items)} items extracted, "
        f"{skipped} segments skipped (no problem solved), "
        f"{errors} errors"
    )
    return items


# ---------------------------------------------------------------------------
# Playbook extraction — ideas, decisions, architecture, patterns
# ---------------------------------------------------------------------------

PLAYBOOK_PROMPT = """You are analyzing a conversation segment from a Claude Code coding assistant session.
Your job is to determine if any IDEAS, DECISIONS, ARCHITECTURE CHOICES, or REUSABLE PATTERNS
were discussed and crystallized in this segment.

This is NOT about errors or bugs. You're looking for:
- Architecture decisions ("let's use weighted scoring with 3 sources")
- Design patterns ("we'll use a draft→crystallize pipeline")
- Ideas that evolved through discussion and reached a conclusion
- Reusable recipes or how-to knowledge

CONVERSATION SEGMENT:
---
{conversation}
---

METADATA:
- Session ID: {session_id}
- Model: {model_id}
- Timestamp range: {start_time} to {end_time}
- Working directory: {cwd}
- Git branch: {git_branch}
- Tools used: {tools_list}

INSTRUCTIONS:
1. Was a meaningful idea, decision, or pattern discussed and crystallized?
   - If NO (just debugging, reading files, or no decision was reached), respond with: {{"found": false}}
   - If YES, extract the FINAL crystallized outcome only — not the back-and-forth discussion.

2. Extract these fields as JSON:
{{
  "found": true,
  "title": "Short descriptive title for this idea/decision",
  "content": "The crystallized outcome — what was decided and why. Include specifics (numbers, names, config values). Discard intermediate discussion.",
  "category": "architecture|pattern|idea|recipe",
  "project": "Project name if identifiable from the conversation, or empty string",
  "tags": ["relevant", "topic", "tags"],
  "rejected": ["Options or approaches that were explicitly rejected and why"],
  "search_text": "Natural language sentence combining the idea and its context, optimized for semantic search"
}}

CATEGORY GUIDELINES:
- architecture: System design decisions, component choices, data flow designs
- pattern: Reusable code patterns, integration approaches, API usage patterns
- idea: Raw ideas, feature concepts, product direction thoughts
- recipe: Step-by-step how-tos, deployment procedures, configuration guides

IMPORTANT:
- Only extract the FINAL decision, not every intermediate thought
- If an idea was discussed but no conclusion was reached, respond with {{"found": false}}
- Include what was REJECTED so it's not re-explored later
- Be specific: "use Google Places API with 0.4 weight" not "use an API"

Respond with ONLY valid JSON, no markdown fences, no explanation."""


async def extract_playbook(
    segment: Segment,
    semaphore: asyncio.Semaphore | None = None,
) -> PlaybookItem | None:
    """Extract a playbook item from a conversation segment."""
    conversation_text, image_parts = format_segment_for_extraction(segment)
    if not conversation_text.strip():
        return None

    model_id = segment.model_ids[0] if segment.model_ids else "unknown"

    prompt_text = PLAYBOOK_PROMPT.format(
        conversation=conversation_text,
        session_id=segment.session_id,
        model_id=model_id,
        start_time=segment.start_time or "unknown",
        end_time=segment.end_time or "unknown",
        cwd=segment.cwd or "unknown",
        git_branch=segment.git_branch or "unknown",
        tools_list=", ".join(segment.tools_used) or "none",
    )

    from google.genai.types import Part
    contents = [Part.from_text(text=prompt_text)]
    for img in image_parts:
        contents.append(Part.from_bytes(
            data=__import__("base64").b64decode(img["data"]),
            mime_type=img["media_type"],
        ))

    client = get_genai_client()

    async def _call():
        response = await client.aio.models.generate_content(
            model=EXTRACTION_MODEL,
            contents=contents,
            config=GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )
        return response.text

    try:
        if semaphore:
            async with semaphore:
                raw_response = await _call()
        else:
            raw_response = await _call()

        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:-1])
        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

        data = json.loads(cleaned)

        if not data.get("found"):
            return None

        # Build expanded_messages
        expanded = []
        for msg in segment.messages:
            if msg.type == "system":
                continue
            entry = {
                "role": msg.role or msg.type,
                "text": msg.content_text,
            }
            if msg.tool_uses:
                entry["tools_used"] = msg.tool_uses
            expanded.append(entry)

        category = data.get("category", "idea")
        if category not in ("architecture", "pattern", "idea", "recipe"):
            category = "idea"

        item = PlaybookItem(
            session_id=segment.session_id,
            model_id=model_id,
            timestamp=segment.start_time,
            title=data.get("title", ""),
            content=data.get("content", ""),
            category=category,
            project=data.get("project", ""),
            tags=data.get("tags", []),
            rejected=data.get("rejected", []),
            search_text=data.get("search_text", ""),
            anchor_idx=segment.end_idx,
            window=(segment.start_idx, segment.end_idx),
            expanded_messages=expanded,
        )

        logger.info(
            f"Playbook: [{item.category}] {item.title[:80]}"
        )
        return item

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse playbook response for segment {segment.start_idx}-{segment.end_idx}: {e}")
        return None
    except Exception as e:
        logger.error(f"Playbook extraction error for segment {segment.start_idx}-{segment.end_idx}: {e}")
        return None


async def extract_playbooks_batch(
    segments: list[Segment],
    max_concurrent: int = MAX_CONCURRENT,
) -> list[PlaybookItem]:
    """Extract playbook items from multiple segments concurrently."""
    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = [extract_playbook(seg, semaphore) for seg in segments]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    items = []
    errors = 0
    skipped = 0
    for r in results:
        if isinstance(r, Exception):
            errors += 1
            logger.error(f"Playbook extraction failed: {r}")
        elif r is None:
            skipped += 1
        else:
            items.append(r)

    logger.info(
        f"Playbook extraction complete: {len(items)} items, "
        f"{skipped} skipped, {errors} errors"
    )
    return items
