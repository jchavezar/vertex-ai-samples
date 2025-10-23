from a2a.types import AgentSkill
from vertexai.preview.reasoning_engines.templates.a2a import create_agent_card

qna_agent_skill = AgentSkill(
    id="web_qa",
    name="Web Q&A",
    description="Answer questions using current web search results",
    tags=["question-answering", "search", "research"],
    examples=[
        "What is the current weather in Tokyo?",
        "Who won the latest Nobel Prize in Physics?",
        "What are the symptoms of the flu?",
        "How do I make sourdough bread?",
    ],
    input_modes=["text/plain"],
    output_modes=["text/plain"],
)

qna_agent_card = create_agent_card(
    agent_name="Q&A Agent",
    description="A helpful assistant agent that can answer questions.",
    skills=[qna_agent_skill],
)
