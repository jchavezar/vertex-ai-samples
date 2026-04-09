"""Streaming JSONL parser for Claude Code conversation transcripts."""

import json
import logging
from typing import Iterator

from pipeline.models import TranscriptMessage, ImageData

logger = logging.getLogger(__name__)

SKIP_TYPES = {"file-history-snapshot", "queue-operation", "permission-mode", "last-prompt"}
MAX_TOOL_RESULT_LEN = 2000
MAX_IMAGES_PER_MESSAGE = 3  # limit to avoid token explosion


def extract_text_from_content(content) -> str:
    """Extract plain text from message content (string or array)."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        texts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                texts.append(block.get("text", ""))
        return "\n".join(texts).strip()

    return ""


def extract_tool_names(content) -> list[str]:
    """Extract tool names from assistant message content blocks."""
    if not isinstance(content, list):
        return []

    tools = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            name = block.get("name", "")
            if name:
                tools.append(name)
    return tools


def extract_images(content) -> list[ImageData]:
    """Extract images from message content blocks.

    Captures screenshots from user messages and tool results (e.g., take_screenshot).
    Limited to MAX_IMAGES_PER_MESSAGE to avoid token explosion.
    """
    if not isinstance(content, list):
        return []

    images = []
    for block in content:
        if not isinstance(block, dict):
            continue

        # Direct image blocks
        if block.get("type") == "image":
            source = block.get("source", {})
            data = source.get("data", "")
            if data:
                images.append(ImageData(
                    media_type=source.get("media_type", "image/png"),
                    data=data,
                ))

        # Images inside tool results (e.g., take_screenshot)
        if block.get("type") == "tool_result":
            sub_content = block.get("content", "")
            if isinstance(sub_content, list):
                for sub in sub_content:
                    if isinstance(sub, dict) and sub.get("type") == "image":
                        source = sub.get("source", {})
                        data = source.get("data", "")
                        if data:
                            images.append(ImageData(
                                media_type=source.get("media_type", "image/png"),
                                data=data,
                            ))

        if len(images) >= MAX_IMAGES_PER_MESSAGE:
            break

    return images[:MAX_IMAGES_PER_MESSAGE]


def extract_tool_result_summaries(content) -> list[str]:
    """Extract truncated tool result texts from user messages."""
    if not isinstance(content, list):
        return []

    summaries = []
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_result":
            continue
        result_content = block.get("content", "")
        if isinstance(result_content, str):
            text = result_content[:MAX_TOOL_RESULT_LEN]
        elif isinstance(result_content, list):
            parts = []
            for part in result_content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(part.get("text", ""))
            text = "\n".join(parts)[:MAX_TOOL_RESULT_LEN]
        else:
            continue
        if text.strip():
            summaries.append(text)
    return summaries


def parse_jsonl_streaming(path: str) -> Iterator[TranscriptMessage]:
    """Stream-parse a Claude Code JSONL transcript.

    Yields one TranscriptMessage at a time. Skips non-conversation types
    (file-history-snapshot, queue-operation, etc.). Strips thinking blocks
    and base64 images.

    Args:
        path: Absolute path to the JSONL file.

    Yields:
        TranscriptMessage for each user/assistant/system message.
    """
    index = 0

    with open(path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                logger.warning(f"Skipping malformed JSON at line {line_num}")
                continue

            msg_type = obj.get("type", "")
            if msg_type in SKIP_TYPES:
                continue

            # Only process user, assistant, system messages
            if msg_type not in ("user", "assistant", "system"):
                continue

            message = obj.get("message", {})
            role = message.get("role") or obj.get("role")
            content = message.get("content", "")

            # Extract text, images, and tool info
            content_text = extract_text_from_content(content)
            images = extract_images(content)
            tool_uses = extract_tool_names(content)
            tool_results = extract_tool_result_summaries(content) if msg_type == "user" else []

            # Skip user messages that are pure tool results with no text
            if msg_type == "user" and not content_text and tool_results:
                # Still yield but mark as tool-result-only
                pass

            # Extract metadata
            model_id = message.get("model")
            message_id = message.get("id")
            usage = message.get("usage")
            if usage:
                usage = {
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
                    "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
                }

            # System message metadata
            duration_ms = obj.get("durationMs")

            msg = TranscriptMessage(
                type=msg_type,
                role=role,
                content_text=content_text,
                images=images,
                tool_uses=tool_uses,
                tool_results=tool_results,
                model_id=model_id,
                message_id=message_id,
                timestamp=obj.get("timestamp"),
                session_id=obj.get("sessionId"),
                uuid=obj.get("uuid"),
                parent_uuid=obj.get("parentUuid"),
                usage=usage,
                git_branch=obj.get("gitBranch"),
                cwd=obj.get("cwd"),
                duration_ms=duration_ms,
                index=index,
            )
            index += 1
            yield msg

    logger.info(f"Parsed {index} messages from {path}")
