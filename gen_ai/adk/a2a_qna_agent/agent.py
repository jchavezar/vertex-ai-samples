from google.adk.agents import LlmAgent
from google.adk.tools import google_search_tool

qna_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="qa_assistant",
    description="I answer questions using web search.",
    instruction="""You are a helpful Q&A assistant.
        When asked a question:
        1. Use Google Search to find current, accurate information
        2. Synthesize the search results into a clear answer
        3. Cite your sources when possible
        4. If you can't find a good answer, say so honestly

        Always aim for accuracy over speculation.""",
    tools=[google_search_tool.google_search],
)
