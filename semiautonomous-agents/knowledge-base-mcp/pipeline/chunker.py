"""Topic-shift detection and conversation segmentation.

Uses heuristics (not LLM) to split conversations into coherent segments:
- Time gaps > 10 minutes
- Working directory changes
- Tool diversity shifts
- Explicit topic markers in user messages
- Force-split at 30 messages
"""

import re
import logging
from datetime import datetime, timezone

from pipeline.models import TranscriptMessage, Segment

logger = logging.getLogger(__name__)

MAX_SEGMENT_SIZE = 30
MIN_SEGMENT_SIZE = 3
TIME_GAP_MINUTES = 10

TOPIC_SHIFT_PATTERNS = re.compile(
    r"(?i)^(next|now let'?s|switching to|new task|moving on|ok\s+now|"
    r"let'?s move|different question|another thing|can you now|"
    r"forget that|actually,?\s+let'?s|hold on)"
)


def parse_timestamp(ts: str | None) -> datetime | None:
    """Parse ISO 8601 timestamp."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def detect_time_gap(prev: TranscriptMessage, curr: TranscriptMessage) -> bool:
    """Check if there's a >10 minute gap between messages."""
    t1 = parse_timestamp(prev.timestamp)
    t2 = parse_timestamp(curr.timestamp)
    if t1 and t2:
        gap = (t2 - t1).total_seconds() / 60
        return gap > TIME_GAP_MINUTES
    return False


def detect_cwd_change(prev: TranscriptMessage, curr: TranscriptMessage) -> bool:
    """Check if working directory changed."""
    if prev.cwd and curr.cwd and prev.cwd != curr.cwd:
        return True
    return False


def detect_topic_shift(msg: TranscriptMessage) -> bool:
    """Check if user message contains topic-shift language."""
    if msg.type != "user" or not msg.content_text:
        return False
    return bool(TOPIC_SHIFT_PATTERNS.match(msg.content_text.strip()))


def detect_tool_diversity_shift(
    prev_tools: set[str], curr_tools: set[str]
) -> bool:
    """Check if the set of tools shifted significantly."""
    if not prev_tools or not curr_tools:
        return False
    overlap = prev_tools & curr_tools
    total = prev_tools | curr_tools
    if not total:
        return False
    # Jaccard similarity < 0.2 = significant shift
    return len(overlap) / len(total) < 0.2


def build_segment(
    messages: list[TranscriptMessage],
    session_id: str,
) -> Segment:
    """Build a Segment from a list of messages."""
    model_ids = list(set(m.model_id for m in messages if m.model_id))
    tools_used = list(set(t for m in messages for t in m.tool_uses))

    return Segment(
        messages=messages,
        start_idx=messages[0].index,
        end_idx=messages[-1].index,
        session_id=session_id,
        model_ids=model_ids,
        tools_used=tools_used,
        start_time=messages[0].timestamp,
        end_time=messages[-1].timestamp,
        cwd=next((m.cwd for m in messages if m.cwd), None),
        git_branch=next((m.git_branch for m in messages if m.git_branch), None),
    )


def chunk_conversation(
    messages: list[TranscriptMessage],
    session_id: str = "",
) -> list[Segment]:
    """Split a conversation into topic-coherent segments.

    Args:
        messages: List of TranscriptMessage (from parser).
        session_id: Session ID for the conversation.

    Returns:
        List of Segments, each 3-30 messages.
    """
    if not messages:
        return []

    if not session_id:
        session_id = messages[0].session_id or "unknown"

    segments: list[Segment] = []
    current_chunk: list[TranscriptMessage] = [messages[0]]
    recent_tools: set[str] = set(messages[0].tool_uses)

    for i in range(1, len(messages)):
        prev = messages[i - 1]
        curr = messages[i]

        should_split = False

        # Check split conditions
        if len(current_chunk) >= MAX_SEGMENT_SIZE:
            should_split = True
        elif len(current_chunk) >= MIN_SEGMENT_SIZE:
            if detect_time_gap(prev, curr):
                should_split = True
            elif detect_cwd_change(prev, curr):
                should_split = True
            elif detect_topic_shift(curr):
                should_split = True
            elif detect_tool_diversity_shift(recent_tools, set(curr.tool_uses)):
                should_split = True

        if should_split:
            segments.append(build_segment(current_chunk, session_id))
            current_chunk = [curr]
            recent_tools = set(curr.tool_uses)
        else:
            current_chunk.append(curr)
            recent_tools.update(curr.tool_uses)

    # Flush remaining
    if current_chunk:
        if len(current_chunk) < MIN_SEGMENT_SIZE and segments:
            # Merge tiny tail into last segment
            segments[-1].messages.extend(current_chunk)
            segments[-1].end_idx = current_chunk[-1].index
            segments[-1].end_time = current_chunk[-1].timestamp
        else:
            segments.append(build_segment(current_chunk, session_id))

    logger.info(
        f"Chunked {len(messages)} messages into {len(segments)} segments "
        f"(avg {len(messages) / max(len(segments), 1):.1f} msgs/segment)"
    )
    return segments
