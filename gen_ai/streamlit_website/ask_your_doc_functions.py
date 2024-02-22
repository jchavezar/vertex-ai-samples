#%%
import re
import base64
import asyncio
import numpy as np
import streamlit as st
from pathlib import Path
from typing import Tuple
from utils import vector_database
from google.cloud import bigquery
from utils.links_references import *
from utils.video.credentials import *
from utils import documents_preprocess
from utils.gemini_utils import Functions
from vertexai.language_models import TextEmbeddingModel
import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import GenerativeModel, Tool

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

citibikes_dataset = "public"
table = "citibike_stations"
max_results_for_bq = 1000000

def app():
    #region Tools Init
    f = Functions()
    model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    preprocess_client = documents_preprocess.Client(variables)
    vector_database_client = vector_database.Client(variables)
    #endregion
    
    def streamlit_init():
        st.markdown("""
            The following demo has functions calling which is a way to connect the llm to either api calls, 
            python functions or any other task.
            
            [more information](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/function-calling)
            
            """)
    
        description = """Get internal information about building policies like trash collection, packages pickup, ammenities use and dogs animal polices"""
        
        with st.expander("Diagram:"):
            st.image("images/ask_your_doc_extensions.png")
        st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({ask_your_doc_functions})""")

        if 'area_key' not in st.session_state:
            st.session_state.area_key = 1
            
        description_placeholder = st.empty()
        with description_placeholder.container():
            des = st.text_area(label="User or Provide a Description to detect the function to be called:",
                            height=100,
                            value=description, key=st.session_state.area_key)
        
        # your chat code
        if st.button("Reset", type="primary"):
            # when chat complete
            st.session_state.area_key += 1
            description_placeholder.empty()
            with description_placeholder.container():
                des = st.text_area(label="User",
                                height=100,
                                value=description,
                                key=st.session_state.area_key)
        return des
        
        
    des = streamlit_init()

    #region Functions Calling definition                                               
    taxes_info ={
    "name": "get_taxes_info",
    "description": "Get taxes information for users",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The full name, first and last name."
            },
        },
        "required": [
            "name"
        ]
    }
    }

    internal_info ={
    "name": "get_internal_info",
    "description": des,
    "parameters": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "description": "Any contextual search query about the document indexed"
            },
        },
        "required": [
            "context"
        ]
    }
    }

    citibike_info ={
    "name": "get_citibike_info",
    "description": "Get everything regarding citibikes like dock stations available, number of bikes availabe and disabled, capacity, per longitude and latitude, if you get a question about latitud and longiture refere to this function.",
    "parameters": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "description": "extract exactly the query/context as it is, do not manipulate the input"
            },
        },
        "required": [
            "context"
        ]
    }
    }

    all_tools = Tool.from_dict(
        {
            "function_declarations": [
                taxes_info, internal_info, citibike_info
            ]
        }
    )
    
    st.header("Functions Calling")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(taxes_info)
        
    with col2:
        st.write(internal_info)

    with col3:
        st.write(citibike_info)    
    #endregion

    #region Python Functions for Function Callings
    def get_taxes_info(name:str) -> str:
        """This is a function to gather taxes information for users"""
        model = GenerativeModel("gemini-pro")
        prompt = f"""
        Your task is to create a table with synthetic information about tax breakdown 
        like gain, income, etc... for the person below:
        - Table is pipe separated.
        
        Person:
        {name}
        """
        response = model.generate_content([prompt])
        return response.text

    # Using Cloud SQL Database to Query
    def get_internal_info(input, rag_schema):
        query = model_emb.get_embeddings([input])[0].values
        result = asyncio.run(vector_database_client.query(query, rag_schema))
        return result

    def get_citibike_info(context:str) -> str:
        """This is a function to get citibike information"""
        project = variables["project"]
        #dataset = variables["dataset"]
        #table = "citibike_stations"
        model = "gemini-pro"
        bq_client = bigquery.Client(project=project)
        gemini_model = GenerativeModel(model)
        schema_columns=[i.column_name for i in bq_client.query(f"SELECT column_name FROM {project}.{citibikes_dataset}.INFORMATION_SCHEMA.COLUMNS WHERE table_name='{table}'").result()]
        prompt = f"""
        You are a GoogleSQL expert. Given an input question, first create a syntactically correct GoogleSQL query to run. This will be the SQLQuery. Then look at the results of the query. This will be SQLResults. Finally return the answer to the input question.
        - Unless the user specifies in the question a specific number of examples to obtain, query for at most {max_results_for_bq} results using the LIMIT clause as per GoogleSQL. You can order the results to return the most informative data in the database.
        - When running SQLQuery across BigQuery you must only include BigQuery SQL code from SQLQuery.
        - Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
        - Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        - Do not generate fake responses, only respond with SQL query code.
        - Do not add unnecesary backticks.
        - Try to add as much column_name as you can related to the Query.

        Match the <prompt> below to this column name schema: {schema_columns}

        Use the following project only {project}, dataset {citibikes_dataset} and {table} to create the query

        Example:
        Question: Tell me the top 10 brands in consumption the city?
        Output: SELECT brands, sum(consumption) FROM <project>.<dataset>.<table> GROUP by brands ORDER by sum(consumption) DESC LIMIT 10
        
        Question: {context}
        Output in SQL:
        """
        
        safety_settings={
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        }
        response = gemini_model.generate_content([prompt], safety_settings=safety_settings)
        response = response.text
        response = re.sub('```', "", response.replace("SQLQuery:", "").replace("sql", ""))

        st.info(f":blue[Model Used for SQL Generator:] :green[{model}]")

        with st.expander("sql query:"):
            st.write(response)
        
        df = bq_client.query(response).to_dataframe()
        st.dataframe(df)

        object_columns = df.select_dtypes(include='object').columns.to_list()
        num_columns = df.select_dtypes(include='int64').columns.to_list()
        num_lat_long = df.select_dtypes(include='float64').columns.to_list()
        if len(object_columns) != 0 and len(num_columns) != 0:
            st.write("**Bar Chart**")
            st.bar_chart(df, x=object_columns[0], y=num_columns[0])

        if len(num_lat_long) != 0:
            df["color"]=np.random.rand(df.shape[0], 4).tolist()
            st.write("**Data Map**")
            st.map(df, latitude="latitude", longitude="longitude", size=num_columns[0], color="color")

        template_prompt = f"from the context enclosed by backticks ```{df.iloc[:10,:].to_json()}``` give me a detailed summary"
        
        txt = gemini_model.generate_content([template_prompt])

        return txt

    def summarize_api_result(query: str, context: str = None) -> str:
        """Summarize the API result."""
        prompt = f"""Answer the following question from the context below:
        - Always explain in detail your response.

        Question:
        {query} 
        
        Context: 
        {context}:
        """  
        model = GenerativeModel("gemini-pro")
        res = model.generate_content(prompt)
        return res.text.replace("$", "")

    def call_api(name: str, args: Tuple[str], rag_schema:str = None) -> str:
        """Looking for any kind of internal documents related to building policies for everything in general like animals, or trash collection, etc"""
        if name == "get_taxes_info":
            name = args.get("name", None)
            return get_taxes_info(name)
        if name == "get_internal_info":
            context = args.get("context", None)
            return get_internal_info(context, rag_schema)
        if name == "get_citibike_info":
            context = args.get("context", None)
            return get_citibike_info(context)

        else:
            return None
    #endregion

    #region Streamlit Functions
    def display_document(file):
        if file == "files/policies.pdf":
            pdf_path = Path(file)
            base64_pdf = base64.b64encode(pdf_path.read_bytes()).decode("utf-8")
            pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        else:
            base64_pdf = base64.b64encode(file.read()).decode("utf-8")
            pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
    @st.cache_data
    def preprocess(filename: str):
        docs = preprocess_client.run(filename=filename)
        return asyncio.run(vector_database_client.run(docs))

    #endregion

    if "yourfile" not in st.session_state:
        st.session_state.yourfile = False
    
    if "filepath" not in st.session_state:
        st.session_state.filepath = False
    
    col1, col2 = st.columns([1,1])  # Adjust column ratios as needed
    
    yourfile = None

    with col1:
        if st.button("Use Demo File", use_container_width=True):
            st.session_state.filepath = "../"
    
    with col2:
        if st.button("Use your Own File", use_container_width=True):
            st.session_state.yourfile = True
            
    # import time        
    # def stream_data(res):
    #     for word in res.split():
    #         yield word + " "
    #         time.sleep(0.02)
    
    def main(filename):
        with st.expander("pdf view"):
            display_document(filename)
        rag_schema = preprocess(filename)
        if rag_schema:
            with st.expander("question examples:"):
                st.markdown("""
                - Hi, I am Jesus Chavez, can you give me my taxes breakdown please?
                - Is there any restriction about terraces or balconies?
                - Show me the max capacity by grouping per latitude and longitude
                """)
            input_text = st.text_input("Ask anything 👇", placeholder="can you describe all the rules for dogs in the building?")
            if input_text:
                model = GenerativeModel("gemini-pro")
                fc_chat = model.start_chat()
                res = fc_chat.send_message(input_text, tools=[all_tools])
                text = f.get_text(res)
                if not text:
                    name = f.get_function_name(res)
                    args = f.get_function_args(res)
                    print(f"\nFUNCTION CALL: {name}({args})")
                    api_result = call_api(name, args, rag_schema=rag_schema)
                    
                    if api_result:
                        st.write(api_result)
                        res = summarize_api_result(query=input_text, context=api_result)
                        st.info(res)
                    else:
                        st.info(summarize_api_result(query=input_text))
     
    if st.session_state.yourfile:
        filename = st.file_uploader("Upload your PDF", type="pdf")
        if filename:
            main(filename)
    elif st.session_state.filepath:
        filename = "files/policies.pdf"
        main(filename)
    else:
        pass
# %%
app()