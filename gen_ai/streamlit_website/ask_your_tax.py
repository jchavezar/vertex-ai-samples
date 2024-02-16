#%%
import base64
import asyncio
import streamlit as st
from textwrap import dedent
from crewai import Crew, Process
from utils import vector_database
from utils.video.credentials import *
from utils import documents_preprocess
from langchain_google_vertexai import VertexAI
from vertexai.language_models import TextEmbeddingModel
from utils.crewai_tax.search_analysis_tasks import SearchAnalysisTask
from utils.crewai_tax.search_analysis_agents import WebsiteAnalysisAgent

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

def app(orch_model, comp_model, other_model, orch_params, comp_params, other_params):
    st.title("CrewAI, I will take care of your taxes")
    with st.expander(label="Diagram"):
        st.image("images/ask_your_tax.png")
    #region preprocessing
    preprocess_client = documents_preprocess.Client(variables)
    vector_database_client = vector_database.Client(variables)
    #endregion
    
    #region Models: Embeddings for Vector Search and Orchestrator Model
    model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    st.markdown(f":red[Orchestrator Model Used:] {orch_model}")
    llm = VertexAI(model_name=orch_model, temperature=orch_params["temperature"], max_output_tokens=orch_params["max_output_tokens"])

    def display_document(file):
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    @st.cache_data
    def preprocess(filename: str):
        docs = preprocess_client.run(filename=filename)
        return asyncio.run(vector_database_client.run(docs))

    def find_match(input, schema):
        query = model_emb.get_embeddings([input])[0].values
        result = asyncio.run(vector_database_client.query(query, schema))
        return result

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
            variables["comp_model"] = comp_model
            variables["other_model"] = other_model
            variables["comp_params"] = comp_params
            variables["other_params"] = other_params
            agents = WebsiteAnalysisAgent(variables)
            tasks = SearchAnalysisTask()
            cleaning_agent = agents.cleaning_agent_expert()
            summary_expert_agent = agents.summary_expert()
            cleaning_task = tasks.clean_tax(cleaning_agent, query, context)
            summary_expert_task = tasks.summary_task(summary_expert_agent, query)
            crew = Crew(
                agents=[cleaning_agent, summary_expert_agent],
                tasks=[cleaning_task, summary_expert_task],
                manager_llm=llm,
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
                #st.write(matches)
                query = dedent(text.replace(",",""))
                crew = FinancialCrew()
                result = crew.run(query, context=matches)
                st.info(result.replace("$", ""))
