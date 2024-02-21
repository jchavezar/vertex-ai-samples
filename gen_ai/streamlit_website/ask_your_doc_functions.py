#%%
import base64
import asyncio
from pathlib import Path
import streamlit as st
from typing import Tuple
from utils.gemini_utils import Functions
from utils import documents_preprocess
from utils import vector_database
from vertexai.language_models import TextEmbeddingModel
from utils.video.credentials import *
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


    all_tools = Tool.from_dict(
        {
            "function_declarations": [
                taxes_info, internal_info
            ]
        }
    )
    
    st.header("Functions Calling")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(taxes_info)
        
    with col2:
        st.write(internal_info)
    
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

    def summarize_api_result(query: str, context: str) -> str:
        """Summarize the API result."""
        prompt = f"""Your task is to explain in a proper way the query below {query} from the context data {context}:
        """  
        model = GenerativeModel("gemini-pro")
        res = model.generate_content(prompt)
        return res.text

    def call_api(name: str, args: Tuple[str], rag_schema:str = None) -> str:
        """Looking for any kind of internal documents related to building policies for everything in general like animals, or trash collection, etc"""
        if name == "get_taxes_info":
            name = args.get("name", None)
            return get_taxes_info(name)
        if name == "get_internal_info":
            context = args.get("context", None)
            return get_internal_info(context, rag_schema)

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
