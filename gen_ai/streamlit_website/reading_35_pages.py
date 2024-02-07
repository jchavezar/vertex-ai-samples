import json
import base64
import vertexai
import streamlit as st
from utils import sockcop_vertexai
from utils.links_references import *
from vertexai.language_models import TextGenerationModel

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
}

client = sockcop_vertexai.Client(variables)

def app(model, parameters):
    
    st.title("Using 35 Pages as Context for Text-Bison")
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
    st.image("images/big_files_text_bison_32k.png")
    st.write("PDF OCR was made before using text-bison, more instructions in the link:")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({reading_35_pages})""")
    @st.cache_data
    def read_document():
        with open("files/othello.json", "r") as f:
            documents = json.load(f)
        return documents

    documents = read_document()

    with open("files/othello.pdf", "rb") as pdf_file:
        encoded_pdf = pdf_file.read()
    #

    base64_pdf = base64.b64encode(encoded_pdf).decode("utf-8")
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

    # %%
    input= st.text_input(label="Do something with your document...", value="Give me summary per page")
    st.markdown("*Bigboy LLM is reading out your 35 pages document and following your instructions...*")
    #
    #st.write(documents)
    vertexai.init(project="vtxdemos", location="us-central1")
    parameters = {
        "max_output_tokens": 8000,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }

    #_documents = [v for k,v in documents.items()]
    
    prompt_template = f"""from the following context enclosed by backticks do the following instructions:
        - Your respond must fulfill the query/input/prompt entirely, do not miss any part in the instructions. 

        context: {str(documents)}

        instructions: {input}
        """
    
    response = client.llm2(prompt_template, model, parameters)
    
    st.info(f"Response: {response}")


    # %%
