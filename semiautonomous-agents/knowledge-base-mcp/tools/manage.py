"""Management tools for the knowledge base — delete, cleanup."""

import logging

logger = logging.getLogger(__name__)


def register_manage_tools(mcp, firestore_client):

    @mcp.tool()
    async def delete_knowledge(
        title_query: str,
        collection: str = "",
    ) -> str:
        """Delete knowledge base entries matching a title.

        Searches by case-insensitive substring match against the title
        (playbooks) or problem description (knowledge items).

        Args:
            title_query: Text to match against titles/problems.
            collection: Optional: "knowledge", "playbooks", or "" for both.
        """
        coll = collection if collection in ("knowledge", "playbooks") else None
        deleted = await firestore_client.delete_by_title(title_query, coll)

        if not deleted:
            return f"No items found matching \"{title_query}\"."

        lines = [f"## Deleted {len(deleted)} item(s)\n"]
        for d in deleted:
            lines.append(
                f"- **[{d['collection']}]** {d['title']} (doc: `{d['doc_id']}`)"
            )

        return "\n".join(lines)
