#%%
import time
import io
import time
import asyncio
import vertexai
from flet import *
from utils.temp import *
import utils.database as vector_database
# from temp import *
# import database as vector_database
import pandas as pd
from typing import Any
from typing import List
from pdf2image import convert_from_path, convert_from_bytes
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold
from vertexai.language_models import TextEmbeddingModel
from langchain.text_splitter import RecursiveCharacterTextSplitter

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_tax_lang",
    "database_password": DB,
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

light_primary = colors.BLUE_300

vertexai.init(project=variables["project_id"])
model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
vector_database_client = vector_database.Client(variables)

def extraction(image):
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0,
        "top_p": 0.55,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Keeping Image bytes in-memory
    images_bytesio = io.BytesIO()
    image.save(images_bytesio, "PNG")
    image1 = Part.from_data(
        mime_type="image/png",
        data=images_bytesio.getvalue(),
    )

    text1 = """You are a tax agent analyst, so your answer needs to be very accurate (100%), 
        from the document extract all the paragraphs, text, images, tables, checkboxes everything to get an 
        structured text as an output. 
        
        - consider checkboxes marked with a clear 'X' as checked (true). All other checkboxes, 
        including empty ones, ambiguous markings, or other symbols, should be treated as unchecked (false)
        - Do not miss any letter or word.
        - Do not make up any key value.
        - Do not forget any value is very important for your tax analysis.
        
        Output in python dictionary:
        """

    text1 = """You are a tax agent analyst, so your answer needs to be very accurate (100%), 
        from the document extract all the paragraphs, text, images, tables, checkboxes everything to get an 
        structured text as an output. 
        
        - consider checkboxes marked with a clear 'X' as checked (true). All other checkboxes, 
        including empty ones, ambiguous markings, or other symbols, should be treated as unchecked (false)
        - Do not miss any letter or word.
        - Do not make up any key value.
        - Do not forget any value is very important for your tax analysis.
        
        Output in structured markdown:
        """
    print("before gemini1.5")
    model = GenerativeModel("gemini-1.5-pro-preview-0409")
    gemini_response = model.generate_content(
        [image1, text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    images_bytesio.close()

    try:
        re = gemini_response.text
    except:
        re = "There was a problem with the extraction, problem: {}".format(gemini_response)
    return re

def split_docs(docs: List, chunk_size=500, chunk_overlap=20):
    lang_docs = []
    list_docs = []
    start = time.time()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for page, doc in enumerate(docs):
        _docs = text_splitter.create_documents([doc])
        # Adding metadata to each chunk (page number)
        for lang_doc in _docs:
            lang_doc.metadata["page_number"]=page
            lang_docs.append(lang_doc)
            list_docs.append(doc)

    return lang_docs, list_docs


def create_embeddings(documents: List, list_docs: List):
    start = time.time()
    pp = 0
    docs_with_emb = []
    for n, content in enumerate(documents):
        rate_limit_minute = 550
        pp += 1
        #elapsed_time = time.time() - start
        sleep_time = (pp*(60/rate_limit_minute)) - (time.time()-start)
        if sleep_time > 0:
            time.sleep(sleep_time)
        docs_with_emb.append({f"page": str(content.metadata["page_number"]), f"content": content.page_content, "page_text": list_docs[n], "embedding": model_emb.get_embeddings([f"page: {content.metadata['page_number']}, {content.page_content}"])[0].values})
    return docs_with_emb


def run(filename, page):
    print(page)
    print(page.controls[0])
    page.controls[0].content.controls[1].content.controls[1].content.controls[1]\
        .content.content.controls.append(Text("Processing your file, please wait...", color="black", bgcolor="grey"))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    doc = []
    start = time.time()
    if type(filename) == str:
        images = convert_from_path(filename)
    else:
        images = convert_from_bytes(filename.getvalue())

    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("From files to image pages finished in: {:.2f} s".format(time.time()-start),
                                              color=colors.WHITE, bgcolor=light_primary))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Gemini 1.5 Extraction please wait...", color=colors.BLACK, bgcolor=colors.GREY))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    cp_time = time.time()
    for p, image in enumerate(images):
        start_extraction = time.time()
        response = extraction(image)
        print(response)
        doc.append(response)
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Extraction finished in: {:.2f} s".format(time.time()-start),
                                              color=colors.WHITE, bgcolor=light_primary))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Using gecko for embeddings please wait...",  color=colors.BLACK, bgcolor=colors.GREY))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    cp_time = time.time()
    lang_docs, list_docs = split_docs(doc)
    docs_with_emb = create_embeddings(lang_docs, list_docs)
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Embeddings finished in: {:.2f} s".format(time.time()-start),
                                              color=colors.WHITE, bgcolor=light_primary))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Enjoy!", bgcolor="green"))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    rag_schema = asyncio.run(vector_database_client.run(docs_with_emb))
    print(rag_schema)
    return rag_schema, doc

# query = model_emb.get_embeddings(["What's the total income?"])[0].values
# result = asyncio.run(vector_database_client.query(query, rag_schema))