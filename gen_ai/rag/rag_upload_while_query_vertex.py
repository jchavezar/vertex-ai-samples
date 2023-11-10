#%%
import time
import asyncio
import pandas as pd
import gradio as gr
from utils import google
from utils.credentials import *

variables = {
    "project_id": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_password": DATABASE_PASSWORD,
    "database_name": "rag-pgvector-langchain-1",
    "docai_processor_id": "projects/254356041555/locations/us/processors/5f0b0deeb0a5d23b",
    "location": "us"
}

client = google.Client(variables)


async def db_functions(documents, query):
    await client.create_table()
    await client.insert_documents_vdb(documents)    
    return await client.query(query)

# %%
# LLM prompt + context

def greet(file,name):
    documents, ocr_time, embeddings_time = client.prepare_file(file.name)
    
    start = time.time()
    matches = asyncio.run(db_functions(documents, name))
    vdb_time = time.time() - start
    response = client.llm_predict(name, context=pd.DataFrame(matches).to_json())

    x = str(response)
    return str(response), f"ocr time: {ocr_time}", f"embeddings time: {embeddings_time}", f"vdb time: {vdb_time}"

demo = gr.Interface(
    greet,
    inputs=["file","text"],
    outputs=["text", "text", "text", "text"],
    title="Tax Return Analytics",
    description="Tax Return Deloitte",
    article="Jesus C",
    css=".gradio-container {background-color: neutral}",
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    demo.launch(show_api=True, debug=True)
# %%
