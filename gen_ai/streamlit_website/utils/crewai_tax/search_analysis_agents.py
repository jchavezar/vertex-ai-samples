
import os
import vertexai
from utils.crewai.k import *
import streamlit as st
from crewai import Agent
from langchain.tools import Tool
from utils.crewai_tax.tools import sTools
from langchain_google_vertexai import VertexAI
from langchain.chains.llm_math.base import LLMMathChain
#from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.chat_models.vertexai import ChatVertexAI
import vertexai.preview.generative_models as generative_models

safety_settings={
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

class WebsiteAnalysisAgent:
    def __init__(self, iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)

    def cleaning_agent_expert(self):
        agent_llm = VertexAI(model_name=self.comp_model, temperature=self.comp_params["temperature"])
        st.markdown(f":blue[Model selected for Clean Agent:] {self.comp_model}")

        #st.markdown(f":green[Model selected: {model}]")
        return Agent(
            role="Clean & Math Expert",
            goal="""Use your tools to clean and do math operations if needed.
            
            """,
            backstory="You are very good organizing responses from your tools `clean_interpret` and `math_tool`.",
            llm=agent_llm,
            tools=[
                sTools.clean_interpret,
                sTools.math_tool
            ],
            allow_delegation=False,
            verbose=True,
        )

    def summary_expert(self):
        model = "gemini-pro"
        #llm = VertexAI(model=self.other_model,temperature=self.other_params["temperature"])
        st.markdown(f":green[Model selected for Summarization: {self.other_model}]")
        return Agent(
            role="Staff Research Analyst",
            goal="""Best to give data shape and structure it.""",
            backstory="An expert tax return analyst",
            llm=VertexAI(model_name=self.other_model, temperature=self.other_params["temperature"]),
            allow_delegation=False,
            verbose=True,
        )