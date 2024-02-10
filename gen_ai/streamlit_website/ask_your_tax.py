#%%
import base64
from textwrap import dedent
import time
import asyncio
import streamlit as st
from crewai import Crew, Process
from utils import vector_database 
from streamlit_chat import message
from utils.video.credentials import *
from langchain.chat_models import ChatOpenAI
from langchain_google_vertexai import VertexAI
from langchain.chains import ConversationChain
from vertexai.language_models import TextEmbeddingModel
from utils import documents_preprocess, sockcop_vertexai
from utils.crewai_tax.search_analysis_tasks import SearchAnalysisTask
from utils.crewai_tax.search_analysis_agents import WebsiteAnalysisAgent
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_community.chat_models.vertexai import ChatVertexAI

st.subheader("Chatbot with Langchain, Gemini Pro, CloudSQL, and Streamlit")

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_tax_lang",
    "database_password": DATABASE_PASSWORD, #utils.video.credentials
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

preprocess_client = documents_preprocess.Client(variables)
vector_database_client = vector_database.Client(variables)
model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
llm_client = sockcop_vertexai.Client(variables)
llm = ChatVertexAI(model_name="gemini-pro")

def display_document(file):
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

@st.cache_data
def preprocess(filename: str):
    docs = preprocess_client.run(filename=filename)
    return asyncio.run(vector_database_client.run(docs))

parameters = {
        "max_output_tokens": 8000,
        "temperature": 0.1,
        "top_p": 1,
        "top_k": 20
    }


filename = "supertest for rag wow"

class FinancialCrew:
    def __init__(self):
        self._message = ""
    def run(self, query, context):
        agents = WebsiteAnalysisAgent("gemini-pro", parameters)
        tasks = SearchAnalysisTask()
        #math_analyst_agent = agents.math_agent_analyst()
        cleaning_agent = agents.cleaning_agent_expert()
        summary_expert_agent = agents.summary_expert()
        cleaning_task = tasks.clean_tax(cleaning_agent, query, context)
        #math_analyst_task = tasks.math_task(math_analyst_agent, query)
        summary_expert_task = tasks.summary_task(summary_expert_agent, query)
        crew = Crew(
            agents=[cleaning_agent, summary_expert_agent],
            tasks=[cleaning_task, summary_expert_task],
            manager_llm=ChatVertexAI(temperature=0,model="gemini-pro"),
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff()
        return result

filename = st.file_uploader("Upload your PDF", type="pdf")
if filename:
    with st.expander("pdf view"):
        display_document(filename)
    rag_schema = preprocess(filename)
    if rag_schema:
        text = st.text_input("Ask anything 👇")
        if text:
            matches = find_match(text, rag_schema)
            print("*"*80)
            print("*"*80)
            print(matches)
            print("*"*80)
            print("*"*80)
            #st.write(matches)
            query = dedent(text.replace(",",""))
            crew = FinancialCrew()
            result = crew.run(query, context=matches)
            st.info(result)