"""Custom Vertex AI RAG retrieval tool that always uses function-call style
to ensure grounding_metadata is populated.

The standard VertexAiRagRetrieval uses built-in retrieval for Gemini 2+,
which doesn't populate grounding_metadata. This wrapper forces function-call
style RAG which DOES populate grounding.
"""
from typing import Any

from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools.tool_context import ToolContext
from google.adk.models import LlmRequest
from typing_extensions import override


class GroundingVertexAiRagRetrieval(VertexAiRagRetrieval):
    """Vertex AI RAG retrieval that forces function-call style for grounding."""

    @override
    async def process_llm_request(
        self,
        *,
        tool_context: ToolContext,
        llm_request: LlmRequest,
    ) -> None:
        # Always use the function declaration approach (the else branch in parent)
        # instead of built-in retrieval, because built-in doesn't populate grounding.
        from google.adk.tools.retrieval.base_retrieval_tool import BaseRetrievalTool

        # Call grandparent's process_llm_request to add function declaration
        await BaseRetrievalTool.process_llm_request(
            self, tool_context=tool_context, llm_request=llm_request
        )
