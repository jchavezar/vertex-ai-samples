
import os
import vertexai
from utils.crewai.k import *
import streamlit as st
from crewai import Agent
from langchain.tools import Tool
from utils.crewai_tax import RagTools
from utils.crewai_tax.calculator_tool import CalculatorTools
from langchain_google_vertexai import VertexAI
from langchain_community.utilities import GoogleSearchAPIWrapper

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
}

vertexai.init(project=variables["project"])

os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

search = GoogleSearchAPIWrapper()
search_tool = Tool(
    name="Google Search",
    description="Search Google for recent results.",
    func=search.run,
)

class WebsiteAnalysisAgent():
      def __init__(self, model, parameters):
          temperature = parameters["temperature"]
          max_output_tokens = parameters["max_output_tokens"]
          top_p = parameters["top_p"]
          top_k = parameters["top_k"]
          self.llm = VertexAI(model_name=model, temperature=temperature, max_output_tokens=max_output_tokens, top_p=top_p, top_k=top_k)
            
          st.markdown(f":green[Model selected: {model}]")
          
      def math_agent_analyst(self):
            self.math_llm = VertexAI(model="text-unicorn@001")
            return Agent(
                role='Math Agent with phd in Math',
                goal="""Impress other agents with your deep knowledge in mathematics and physics""",
                backstory="""You are a very perfect a sophisticated agent capable of doing complex max operations.""",
                llms=self.math_llm,
                verbose=True,
                tools=[
                    CalculatorTools.calculate,
                    ],
                    )
            
      def internal_agent_expert(self):
          return Agent(
              role="Tax Internal Agent Expert",
              goal="""Provide a detailed list of items related to your query.
                      Give a summary with all the information gathered related to your query.
                      DO NOT provide any extra information not related to your response or the query.
              """,
              backstory="The most intelligent tax analyst with many expertise in tax forms.",
              llms=self.llm,
              verbose=True,
              tools=[
                  RagTools.rag_tool,
                  ]
              )

      def summary_expert(self):
          return Agent(
              role="Tax Agent Expert",
              goal="""You are the most sufficient expert in tax returns but you get help from the other agents to gather important information.
              """,
              backstory="The most intelligent tax analyst with many expertise in tax forms.",
              llms=self.llm,
              verbose=True,
              )