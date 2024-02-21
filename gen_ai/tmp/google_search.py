#%%
import os
import vertexai
import sys
sys.path.append("../streamlit_website")
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
    "datastore": "financial-internal-docs_1706730313453"
}

os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

search = GoogleSearchAPIWrapper()
search_tool = Tool(
    name="Google Search",
    description="Search Google for recent results.",
    func=search.run,
)
# %%
search_tool.run("what was the last price for bitcoin today, what is the exact time and date of your reference?")
# %%
search_tool.run("what was the highest price of BTC last year?")
