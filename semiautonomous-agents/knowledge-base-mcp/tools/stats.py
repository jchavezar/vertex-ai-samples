"""Statistics tool for the knowledge base."""

import logging

logger = logging.getLogger(__name__)


def register_stats_tools(mcp, firestore_client):

    @mcp.tool()
    async def get_stats() -> str:
        """Get knowledge base statistics.

        Returns total items, sessions, average confidence score,
        top services, and model distribution.
        """
        stats = await firestore_client.get_stats()

        lines = [
            "## Knowledge Base Statistics",
            f"- **Total knowledge items:** {stats['total_knowledge_items']}",
            f"- **Total playbook items:** {stats['total_playbook_items']}",
            f"- **Total sessions ingested:** {stats['total_sessions']}",
            f"- **Average solution confidence:** {stats['average_solution_score']:.3f}",
            "",
        ]

        if stats.get("playbook_categories"):
            lines.append("### Playbook Categories:")
            for cat, count in stats["playbook_categories"]:
                lines.append(f"  - {cat}: {count} items")
            lines.append("")

        if stats["top_services"]:
            lines.append("### Top Services:")
            for svc, count in stats["top_services"]:
                lines.append(f"  - {svc}: {count} items")
            lines.append("")

        if stats["top_models"]:
            lines.append("### Models Used:")
            for model, count in stats["top_models"]:
                lines.append(f"  - {model}: {count} items")

        return "\n".join(lines)
