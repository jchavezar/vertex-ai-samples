#%%
import base64
import time
import asyncio
import pandas as pd
import streamlit as st 
from utils import sockcop_rag
from utils import sockcop_vertexai
from utils.links_references import *
from utils.video.credentials import *

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_password": DATABASE_PASSWORD,
    "database_name": "rag-pgvector-langchain-1",
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

def app(model, parameters):
    with st.sidebar:
        st.markdown(
            """
            Follow me on:

            ldap → [@jesusarguelles](https://moma.corp.google.com/person/jesusarguelles)

            GitHub → [jchavezar](https://github.com/jchavezar)

            LinkedIn → [Jesus Chavez](https://www.linkedin.com/in/jchavezar)

            Medium -> [jchavezar](https://medium.com/@jchavezar)
            """
        )

    client = sockcop_rag.Client(variables)
    llm_client = sockcop_vertexai.Client(variables)
    
    async def db_functions(documents, query):
        await client.create_table()
        await client.insert_documents_vdb(documents)    
        return await client.query(query)

    # LLM prompt + context
    @st.cache_data
    def prepare(file):
        documents, ocr_time, embeddings_time = client.prepare_file(file)
        #st.write(f"Embeddings time: {round(embeddings_time, 2)} sec")
        start = time.time()
        asyncio.run(client.create_table())
        asyncio.run(client.insert_documents_vdb(documents))
        st.write(f"OCR Time: **{round(ocr_time, 2)} sec**, Embeddings time: **{round(embeddings_time, 2)} sec**, Vector DB Inserting Time: **{round(time.time()-start, 2)} sec**")
        #st.write(f"Vector DB Inserting Time: {round(time.time()-start, 2)} sec")
        return documents
    
    def display_document(file):
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    
    def query(query):    
        start = time.time()
        matches = asyncio.run(client.query(query))
        st.markdown(f"Vector DB Query Time: **{round(time.time() - start, 2)} sec**")
        df = pd.DataFrame(matches)
        
        prompt_template = f"""

            You are Tax Returns Preparer, friendly and helpful AI assistant that answers questions related to tax return documents.You are given texts from the forms and you give short and precise answers with the line number from the IRS form mentioned in current context.
            Some table information from forms is given as text,each line is a row in table and columns are separated by pipe symbol(|).
            Sometimes there are multiple values associated to a single line item and are separated by pipe symbol(|).In this case,give all the values instead of the first value.
            If amount values are 0,then return the amounts as 0 rather than no information provided.
            If you are asked Yes/No questions,then look out for selected and unselected text with Yes or No to answer these better.
            If Yes:selected then the answer is yes or if No:selected then the answer is no
            Use the following pieces of context to help answer the user's question. You must include sources used to answer this question. If its not relevant to the question, provide friendly responses.
            Answer the questions that are only related to tax forms or the data provided.If asked other questions,then respond as cannot answer.
            
            Context:
            {df.to_json()}
            
            Question:
            {query}

            Answer and Explanation:
            """
        
        response = llm_client.llm2(prompt_template, model, parameters)
        
        return str(response), df
    #%%
    st.title("Anytime RAG Bot")
    st.image("images/realtime_rag.png")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({ask_your_doc})""")
    #st.title("Chat with Your PDF") 
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    if pdf:
        display_document(pdf)
        documents = prepare(pdf)
        text = st.text_input("Prompt")
        if text:
            reponse, df = query(text)
            st.markdown("***Google:***")
            st.info(f"Response: {reponse}")
            st.write(documents)
            st.write(df)    
