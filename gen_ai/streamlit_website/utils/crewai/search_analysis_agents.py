
import os
import vertexai
from utils.crewai.k import *
import streamlit as st
from crewai import Agent
from langchain.tools import Tool
from utils.crewai.search_tools import SearchTools
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
internet = Tool(
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
                role='Search Scrapping Expert',
                goal="""Extract all the information possible from multiple resources and have an accurate response.""",
                backstory="""The most expert agent working on clean, structure and handle different data.""",
                llm=self.llm,
                verbose=True,
                tools=[
                    internet,
                    SearchTools.internal_rag
                    ],
                    )