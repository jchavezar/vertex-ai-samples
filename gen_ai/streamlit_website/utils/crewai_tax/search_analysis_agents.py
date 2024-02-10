
import os
import vertexai
from utils.crewai.k import *
import streamlit as st
from crewai import Agent
from langchain.tools import Tool
from utils.crewai_tax.tools import sTools
from langchain_google_vertexai import VertexAI
from langchain.chains.llm_math.base import LLMMathChain
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.chat_models.vertexai import ChatVertexAI

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

llm_math_chain = LLMMathChain.from_llm(llm=ChatVertexAI(model="gemini-pro"))
math_tool = Tool(
    name="Calculator",
    func=llm_math_chain.run,
    description="useful when you need to answer questions about math"
)

class WebsiteAnalysisAgent():
      def __init__(self, model, parameters):
          temperature = parameters["temperature"]
          max_output_tokens = parameters["max_output_tokens"]
          top_p = parameters["top_p"]
          top_k = parameters["top_k"]
          
          import vertexai.preview.generative_models as generative_models
          
          safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    },          
          self.llm = ChatVertexAI(
              model_name=model, 
              temperature=temperature, 
              max_output_tokens=max_output_tokens, 
              top_p=top_p, 
              top_k=top_k,
              afety_settings=safety_settings)
            
          st.markdown(f":green[Model selected: {model}]")

      def cleaning_agent_expert(self):
          return Agent(
              role="Clean & Math Expert",
              goal="""Being the best at gather, transform, clean and use math tools to get
              accurate responses.
              
              """,
              backstory="The Best cleaning expert & mathematician like Caurl Gauss or Srinivasa Ramanujan.",
              llms=ChatVertexAI(model="text-unicorn@001", temperature=0),
              tools=[
                  sTools.clean_interpret,
                  math_tool
                  ],
              allow_delegation=False,
              verbose=True,
              )
    
      #def math_agent_analyst(self):
      #      self.math_llm = VertexAI(model="text-unicorn@001", temperature=0)
      #      st.markdown(f":red[Model selected: {self.math_llm}]")
      #      return Agent(
      #          role='Mathematician',
      #          goal="""Precision is important so use the CalculatorTools.calculate.
      #          """,
      #          backstory="""You are a very smart mathematician like Caurl Gauss or Srinivasa Ramanujan.""",
      #          llms=self.math_llm,
      #          allow_delegation=False,
      #          verbose=True,
      #          tools=[
      #              CalculatorTools.calculate,
      #              ],
      #              )

      def summary_expert(self):
          return Agent(
              role="Staff Research Analyst",
              goal="""Best to give data shape and structure it.""",
              backstory="An expert tax return analyst",
              llms=VertexAI(model="gemini-pro",temperature=0),
              allow_delegation=False,
              verbose=True,
              )