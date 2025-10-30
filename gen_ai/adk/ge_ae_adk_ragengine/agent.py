import sys
from vertexai import rag
from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus="projects/vtxdemos/locations/us-east4/ragCorpora/6917529027641081856"
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="ask_rag_agent",
    instruction="""
    Respond to any question using your `ask_vertex_retrieval` tool ONLY, be concise in the response
    
    But give details right after like document used (citations), position, etc.
    
    Output e.g
    ```Markdown
    **Output**: <your concise response>\


    **Rag Details**: <the details mentioned above>
    ```
    """,
    tools=[
        ask_vertex_retrieval,
    ]
)