"""Search and expand tools for the knowledge base MCP server."""

import re
import logging

logger = logging.getLogger(__name__)

# Patterns that indicate time-based intent
_TIME_PATTERNS = re.compile(
    r"\b(recent|latest|last|newest|today|yesterday|this week|this month"
    r"|first|oldest|earliest|what did I|what was the last"
    r"|most recent|previously|before that)\b",
    re.IGNORECASE,
)

_OLDEST_PATTERNS = re.compile(
    r"\b(first|oldest|earliest)\b",
    re.IGNORECASE,
)


def register_search_tools(mcp, firestore_client, embedding_service):

    @mcp.tool()
    async def search_knowledge(query: str, top_k: int = 3, service_filter: str = "") -> str:
        """Search the knowledge base for problem-solution patterns.

        Automatically detects time-based queries (e.g. "last issue",
        "most recent fix") and uses timestamp ordering instead of
        vector search.

        Args:
            query: Natural language description of the problem or topic.
            top_k: Number of results to return (default 3, max 10).
            service_filter: Optional filter by service name (e.g. "Cloud Run").
        """
        top_k = min(top_k, 10)

        # Detect time-based intent → use Firestore timestamp query
        if _TIME_PATTERNS.search(query):
            ascending = bool(_OLDEST_PATTERNS.search(query))
            direction = "ascending" if ascending else "descending"
            logger.info(f"Time-based query detected: '{query}' → timestamp {direction}")
            results = await firestore_client.get_recent(
                limit=top_k,
                service_filter=service_filter or None,
                ascending=ascending,
            )
        else:
            query_embedding = await embedding_service.embed_query(query)
            results = await firestore_client.vector_search(
                query_embedding=query_embedding,
                top_k=top_k,
                service_filter=service_filter or None,
            )

        if not results:
            return "No matching knowledge items found."

        lines = [f"## Knowledge Base Results ({len(results)} matches)\n"]

        for i, r in enumerate(results, 1):
            score = r.get("solution_score", 0.0)
            lines.append(f"### Result {i} (confidence: {score:.2f})")
            lines.append(f"**Problem:** {r.get('problem', 'N/A')}")

            if r.get("error_message"):
                lines.append(f"**Error:** `{r['error_message']}`")

            lines.append(f"**Solution:** {r.get('solution', 'N/A')}")

            # Failed attempts
            failed = r.get("failed_attempts", [])
            if failed:
                lines.append("**Failed attempts (don't waste time on these):**")
                for fa in failed:
                    fa_score = fa.get("score", 0.0)
                    lines.append(f"  - [{fa_score:.1f}] {fa.get('attempt', '')} — {fa.get('reason_failed', '')}")

            # Anti-patterns
            anti = r.get("anti_patterns", [])
            if anti:
                lines.append(f"**Avoid:** {', '.join(anti)}")

            services = r.get("services", [])
            tools = r.get("tools_used", [])
            model = r.get("model_id", "unknown")
            lines.append(
                f"**Services:** {', '.join(services) or 'N/A'} | "
                f"**Tools:** {', '.join(tools) or 'N/A'} | "
                f"**Model:** {model}"
            )

            # Expand hint
            session_id = r.get("session_id", "")
            window = r.get("window", [0, 0])
            if session_id:
                lines.append(
                    f"**Expand:** `expand_context("
                    f"session_id=\"{session_id}\", "
                    f"start_idx={window[0]}, end_idx={window[1]})`"
                )

            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    async def recent_knowledge(limit: int = 5, service_filter: str = "") -> str:
        """Get the most recent knowledge items by timestamp.

        Use this instead of search_knowledge when you need time-based
        queries like "what did I fix last?" or "recent issues".

        Args:
            limit: Number of results (default 5, max 20).
            service_filter: Optional filter by service name.
        """
        limit = min(limit, 20)
        results = await firestore_client.get_recent(
            limit=limit,
            service_filter=service_filter or None,
        )

        if not results:
            return "No knowledge items found."

        lines = [f"## Recent Knowledge Items ({len(results)} results)\n"]

        for i, r in enumerate(results, 1):
            score = r.get("solution_score", 0.0)
            ts = r.get("timestamp", "unknown")[:19]
            lines.append(f"### {i}. [{ts}] (confidence: {score:.2f})")
            lines.append(f"**Problem:** {r.get('problem', 'N/A')}")

            if r.get("error_message"):
                lines.append(f"**Error:** `{r['error_message']}`")

            lines.append(f"**Solution:** {r.get('solution', 'N/A')[:300]}")

            services = r.get("services", [])
            lines.append(f"**Services:** {', '.join(services) or 'N/A'}")
            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    async def search_playbooks(
        query: str,
        top_k: int = 3,
        project_filter: str = "",
        category_filter: str = "",
    ) -> str:
        """Search the playbook knowledge base for ideas, decisions, and patterns.

        Use this to find architecture decisions, design patterns, reusable
        recipes, and ideas from past conversations. Not for error/bug fixes
        — use search_knowledge for those.

        Automatically detects time-based queries and uses timestamp ordering.

        Args:
            query: Natural language description of what you're looking for.
            top_k: Number of results to return (default 3, max 10).
            project_filter: Optional filter by project name (e.g. "vibes_nyc").
            category_filter: Optional filter: architecture, pattern, idea, or recipe.
        """
        top_k = min(top_k, 10)

        if _TIME_PATTERNS.search(query):
            results = await firestore_client.get_recent_playbooks(
                limit=top_k,
                project_filter=project_filter or None,
            )
        else:
            query_embedding = await embedding_service.embed_query(query)
            results = await firestore_client.vector_search_playbooks(
                query_embedding=query_embedding,
                top_k=top_k,
                project_filter=project_filter or None,
                category_filter=category_filter or None,
            )

        if not results:
            return "No matching playbook items found."

        lines = [f"## Playbook Results ({len(results)} matches)\n"]

        for i, r in enumerate(results, 1):
            cat = r.get("category", "idea")
            project = r.get("project", "")
            proj_label = f" | **Project:** {project}" if project else ""
            lines.append(f"### {i}. [{cat.upper()}]{proj_label}")
            lines.append(f"**{r.get('title', 'Untitled')}**")
            lines.append(f"{r.get('content', 'N/A')}")

            tags = r.get("tags", [])
            if tags:
                lines.append(f"**Tags:** {', '.join(tags)}")

            rejected = r.get("rejected", [])
            if rejected:
                lines.append("**Rejected:**")
                for rej in rejected:
                    lines.append(f"  - {rej}")

            session_id = r.get("session_id", "")
            window = r.get("window", [0, 0])
            if session_id:
                lines.append(
                    f"**Expand:** `expand_context("
                    f"session_id=\"{session_id}\", "
                    f"start_idx={window[0]}, end_idx={window[1]})`"
                )

            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    async def get_topic_timeline(
        query: str,
        top_k: int = 10,
        service_filter: str = "",
    ) -> str:
        """Get knowledge items related to a topic in chronological order (oldest first).

        Unlike search_knowledge (ranked by relevance), this returns results
        sorted by timestamp to show how a topic evolved over time ACROSS
        MULTIPLE SESSIONS. Use this to understand the full history of a topic.

        Args:
            query: Topic to search for (e.g., "WIF provider configuration").
            top_k: Number of results to return (default 10, max 20).
            service_filter: Optional filter by service name.
        """
        top_k = min(top_k, 20)

        query_embedding = await embedding_service.embed_query(query)
        results = await firestore_client.get_topic_timeline(
            query_embedding=query_embedding,
            top_k=top_k,
            service_filter=service_filter or None,
        )

        if not results:
            return "No matching knowledge items found."

        lines = [f"## Topic Timeline: {query} ({len(results)} entries, oldest first)\n"]

        for i, r in enumerate(results, 1):
            ts = r.get("timestamp", "unknown")[:19]
            session = r.get("session_id", "?")[:8]
            score = r.get("solution_score", 0.0)

            lines.append(f"### {i}. [{ts}] session:{session}... (confidence: {score:.2f})")
            lines.append(f"**Problem:** {r.get('problem', 'N/A')}")

            if r.get("error_message"):
                lines.append(f"**Error:** `{r['error_message']}`")

            lines.append(f"**Solution:** {r.get('solution', 'N/A')[:300]}")

            services = r.get("services", [])
            lines.append(f"**Services:** {', '.join(services) or 'N/A'}")

            # Expand hint
            session_id = r.get("session_id", "")
            window = r.get("window", [0, 0])
            if session_id:
                lines.append(
                    f"**Expand:** `expand_context("
                    f"session_id=\"{session_id}\", "
                    f"start_idx={window[0]}, end_idx={window[1]})`"
                )

            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    async def expand_context(session_id: str, start_idx: int, end_idx: int) -> str:
        """Expand a knowledge base result to show surrounding conversation.

        Returns cleaned conversation messages (no thinking blocks, no base64,
        no raw tool output — just user text, assistant text, and tool names).

        Args:
            session_id: Session ID from a search result.
            start_idx: Start message index.
            end_idx: End message index.
        """
        messages = await firestore_client.get_expanded_context(
            session_id=session_id,
            start_idx=start_idx,
            end_idx=end_idx,
        )

        if not messages:
            return f"No expanded context found for session {session_id} [{start_idx}:{end_idx}]"

        lines = [f"## Conversation Context (session: {session_id}, messages {start_idx}-{end_idx})\n"]

        for msg in messages:
            role = msg.get("role", "?")
            text = msg.get("text", "")
            tools = msg.get("tools_used", [])

            if text:
                lines.append(f"**[{role}]:** {text}")
            if tools:
                lines.append(f"  _(tools: {', '.join(tools)})_")
            lines.append("")

        return "\n".join(lines)
