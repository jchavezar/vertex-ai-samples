
import os
import vertexai
from utils.crewai.k import *
import streamlit as st
from crewai import Agent
from langchain.tools import Tool
from streamlit_website.utils.crewai_tax.RagTools import SearchTools
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
      def __init__(self):
          pass
      def search_analyst(self, model, parameters):
            print(parameters)
            print(parameters["temperature"])
            print(type(parameters["temperature"]))
            temperature = parameters["temperature"]
            max_output_tokens = parameters["max_output_tokens"]
            top_p = parameters["top_p"]
            top_k = parameters["top_k"]
            print(temperature, max_output_tokens, top_p, top_k)
            self.llm = VertexAI(model_name=model, temperature=temperature, max_output_tokens=max_output_tokens, top_p=top_p, top_k=top_k)
            st.markdown(f":green[Model selected: {model}]")
            return Agent(
                role='Internet Scraping Agent',
                goal="""Scrap the internet and get details about the snippets found""",
                backstory="""The most seasoned search surfer with a lot of expertise navigating through internet, that is working for a super important customer.""",
                llms=self.llm,
                verbose=True,
                tools=[
                    search_tool,
                    ],
                    )
      def search_internal(self, filename):
          return Agent(
              role="Financial Internal Data Analyst",
              goal="Get all the information you can from rag internal documents about what is being asked in the financial, revenue and sales space for Amazon, Microsoft and Google",
              backstory="The most seasoned search analyst with lot of expertise in financial local reports.",
              llms=self.llm,
              verbose=True,
              tools=[
                    SearchTools.search_rag(filename=filename),
                    ],
              )