#%%
import vertexai
from utils.ggl import Client
from datetime import datetime, timezone
from utils import variables, credentials
from vertexai.preview.language_models import ChatModel

chat_history = []
counter = 0

variables = {
    "project_id": variables.PROJECT_ID,
    "region": variables.REGION,
    "location": variables.LOCATION,
    "docai_processor_id": variables.PROCESSOR_ID, # DocumentAI Processor ID
    "embeddgins_chunk_size": variables.EMBEDDINGS_CHUNK_SIZE, # size of the paragraph in the documents to be represented as embeddings / characters
    "embeedings_chunk_overlap": variables.EMBEDDINGS_OVERLAPPING_CHUNK_SIZE,
    "embeddings_model": variables.EMBEDDINGS_MODEL, # Gecko embeddings selected
    "database_doc_name" : variables.DATABASE_DOC_NAME,
    "database_chat_history_name": variables.DATABASE_CHAT_NAME,
    "instance_name" : variables.INSTANCE_NAME,
    "database_user" : variables.DATABASE_USER,
    "database_password" : credentials.DATABASE_PASSWORD,
}

client = Client(variables)

documents, reading_time, embeddings_time = client.file_preprocessing("1065_1_pages.pdf")
await client.create_table(database_user = variables.database_doc_name)
await client.insert_documents_vdb(documents, database_user = variables.database_doc_name)
# %%

vertexai.init(project="vtxdemos", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison-32k")
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 8000,
    "temperature": 0,
    "top_p": 0.8,
    "top_k": 40
}

async def chat_bison(query: str, rag_document: dict):
    await client.create_table(database_user = variables.database_chat_history_name)
    global chat_history
    global counter
    counter +=  1
    if len(chat_history) > 4:
        await client.insert_documents_vdb(chat_history[:4], database_user = variables.database_chat_history_name)
        chat_history = chat_history[4:]
        print("inserting_items_into_vdb")
    if counter > 6:
        rag_matches = await client.query(query)
        print(rag_matches)
        chat = chat_model.start_chat(
            context=f"""You are a very funny and a bully chatbot, 
            you can be disrespectful any time you want just to make a joke. 
            Your name is asbot. 
            Use the next document_source_of_truth as the only data to respond your answers, you can still make jokes but try to be accurate in the response agains the document.
            If you dont know the answer you can tell it so.
            If your response is related to the document_source_of_truth, describe the reference like the page number, do not make up information.
            
            document_source_of_truth: {rag_document}
            
            chat history: {rag_matches+chat_history}
            
            Output format: <your_output> \n:

            """,
        )
    else :
        print(rag_document)
        chat = chat_model.start_chat(
            context=f"""You are a very funny and a bully chatbot, 
            you can be disrespectful any time you want just to make a joke. 
            Your name is asbot.
            Your name is asbot. 
            Use the next document_source_of_truth as the only data to respond your answers, you can still make jokes but try to be accurate in the response agains the document.
            If you dont know the answer you can tell it so.
            If your response is related to the document_source_of_truth, describe the reference like the page number, do not make up information.

            document_source_of_truth: {rag_document}

            chat history: {chat_history}

            Output format: <your_output> \n

            """,
        )
    
    response = chat.send_message(query, **parameters).text
    chat_history.append({"date": datetime.now(timezone.utc),"user": query, "asbot": response})
    
    #print(chat_history)
    
    return response