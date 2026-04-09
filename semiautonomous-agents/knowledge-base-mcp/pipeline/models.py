"""Pydantic models for the knowledge base extraction pipeline."""

from pydantic import BaseModel, Field


class ImageData(BaseModel):
    """A base64-encoded image from a conversation."""
    media_type: str = "image/png"
    data: str = ""  # base64 string


class TranscriptMessage(BaseModel):
    """A parsed message from a Claude Code JSONL transcript."""
    type: str
    role: str | None = None
    content_text: str = ""
    images: list[ImageData] = Field(default_factory=list)
    tool_uses: list[str] = Field(default_factory=list)
    tool_results: list[str] = Field(default_factory=list)
    model_id: str | None = None
    message_id: str | None = None
    timestamp: str | None = None
    session_id: str | None = None
    uuid: str | None = None
    parent_uuid: str | None = None
    usage: dict | None = None
    git_branch: str | None = None
    cwd: str | None = None
    duration_ms: int | None = None
    index: int = 0


class Segment(BaseModel):
    """A topic-coherent segment of conversation messages."""
    messages: list[TranscriptMessage]
    start_idx: int
    end_idx: int
    session_id: str
    model_ids: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    start_time: str | None = None
    end_time: str | None = None
    cwd: str | None = None
    git_branch: str | None = None


class FailedAttempt(BaseModel):
    """A failed attempt at solving a problem."""
    attempt: str
    reason_failed: str
    score: float = Field(ge=0.0, le=1.0, description="How close to the solution (1.0 = almost worked)")


class KnowledgeItem(BaseModel):
    """An extracted problem-solution pattern."""
    session_id: str
    model_id: str | None = None
    timestamp: str | None = None
    problem: str
    error_message: str | None = None
    solution: str
    solution_score: float = Field(ge=0.0, le=1.0)
    failed_attempts: list[FailedAttempt] = Field(default_factory=list)
    anti_patterns: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    search_text: str = ""
    anchor_idx: int = 0
    window: tuple[int, int] = (0, 0)
    embedding: list[float] | None = None
    expanded_messages: list[dict] | None = None


class PlaybookItem(BaseModel):
    """A crystallized idea, decision, or pattern from a conversation."""
    session_id: str
    model_id: str | None = None
    timestamp: str | None = None
    title: str
    content: str
    category: str = "idea"  # architecture | pattern | idea | recipe
    project: str = ""
    tags: list[str] = Field(default_factory=list)
    rejected: list[str] = Field(default_factory=list)
    search_text: str = ""
    anchor_idx: int = 0
    window: tuple[int, int] = (0, 0)
    embedding: list[float] | None = None
    expanded_messages: list[dict] | None = None


class SessionMeta(BaseModel):
    """Metadata about an ingested conversation session."""
    session_id: str
    date: str
    query_count: int = 0
    model_ids: list[str] = Field(default_factory=list)
    source_file: str = ""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
