
import os
import vertexai
from crewai import Agent
from langchain.tools import Tool
from utils.crewai.k import *
from utils.crewai.search_tools import SearchTools
from langchain_google_vertexai import VertexAI
from langchain_community.utilities import GoogleSearchAPIWrapper

project="vtxdemos"
vertexai.init(project=project)

os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

search = GoogleSearchAPIWrapper()
search_tool = Tool(
    name="Google Search",
    description="Search Google for recent results.",
    func=search.run,
)

class WebsiteAnalysisAgent():
      def __init__(self):
            self.llm = VertexAI(model_name="gemini-pro")
      def search_analyst(self):
            return Agent(
                role='The Best Internet Search Surfer',
                goal="""Scrap the internet and get details about the snippets found""",
                backstory="""The most seasoned search surfer with a lot of expertise navigating through internet, that is working for a super important customer.""",
                llms=self.llm,
                verbose=True,
                tools=[
                    search_tool,
                    ],
                    )
      def search_internal(self):
          return Agent(
              role="Financial Search Analyst with Internal Data",
              goal="Get all the information you can from rag internal documents about what is being asked in the financial, revenue and sales space for Amazon, Microsoft and Google",
              backstory="The most seasoned search analyst with lot of expertise in financial local reports.",
              llms=self.llm,
              verbose=True,
              tools=[
                    SearchTools.search_rag,
                    ],
              )