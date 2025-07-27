
import os
from turtle import back
import vertexai
from crewai import Agent
from search_tools import SearchTools
from langchain_google_vertexai import VertexAI

project="vtxdemos"
vertexai.init(project=project)

class WebsiteAnalysisAgent():
      def __init__(self):
            self.llm = VertexAI(model_name="gemini-pro")
      def search_analyst(self):
            return Agent(
                role='The Best Google Search Analyst',
                goal="""Impress all customers with your universal knowledge and trends analysis""",
                backstory="""The most seasoned search analyst with lot of expertise in history, culture
                and economics, that is working for a super important customer.""",
                llms=self.llm,
                verbose=True,
                tools=[
                    SearchTools.search_internet,
                    ],
                    )
      def search_internal(self):
          return Agent(
              role="The Best Internal Financial Search Analyst",
              goal="Impress all the customers with your knowledge about financial, revenue and sales for Amazon, Microsoft and Google",
              backstory="The most seasoned search analyst with lot of expertise in financial local reports.",
              llms=self.llm,
              verbose=True,
              tools=[
                    SearchTools.search_rag,
                    ],
              )