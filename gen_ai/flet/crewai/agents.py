from crewai import Agent
from broswer_tools import BrowserTools
from rag_tools import InternalSearchTools
from langchain_google_vertexai import VertexAI

model = VertexAI(model_name="gemini-pro")


# noinspection PyMethodMayBeStatic
class AnalysisAgents:
    def search(self):
        return Agent(
            llm=model,
            role="The best search internal and external (internet) scrapper",
            goal="Impress all customers with your analysis, use your tools as only true",
            backstory="""The most expert analysis that uses multiple 
            search tools to get the most relevant data from topics""",
            verbose=True,
            tools=[
                BrowserTools.search_internet,
                InternalSearchTools.search_internal
            ]
        )