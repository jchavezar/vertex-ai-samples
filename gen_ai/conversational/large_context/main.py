#%%
import asyncio
import vertexai
import gradio as gr
from utils.credentials import *
from utils import database
from datetime import datetime, timezone
from vertexai.preview.language_models import ChatModel

# Create the database first: gcloud sql databases create rag-pgvector-conversational-1 --instance=pg15-pgvector-demo

chat_history = []
counter = 0

variables = {
    "project_id": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_password": DATABASE_PASSWORD,
    "database_name": "rag-pgvector-conversational-1",
    "location": "us"
}
vertexai.init(project="vtxdemos", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison-32k")
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 8000,
    "temperature": 0,
    "top_p": 0.8,
    "top_k": 40
}
db_client = database.Client(variables)
print(counter)
    
async def chat_bison(query: str, rag_document: dict):
    global chat_history
    global counter
    counter +=  1
    if len(chat_history) > 4:
        await db_client.insert_items_vdb(chat_history[:4])
        chat_history = chat_history[4:]
        print("inserting_items_into_vdb")
    if counter > 6:
        rag_matches = await db_client.query(query)
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


# Gradio


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
        rag_document = asyncio.run(db_client.rag_query(message, database_name="rag-pgvector-conversational-rag-1"))
        #print(rag_document)
        bot_message = asyncio.run(chat_bison(message, rag_document=rag_document))
        print(bot_message)
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

demo.launch()

## Streamlit space
#if "messages" not in st.session_state:
#    st.session_state.messages = []
#    
## Display chat messages from history on app rerun
#for message in st.session_state.messages:
#    if message["role"] == "user":
#        avatar="🦖"
#    else: avatar="🤖"
#    with st.chat_message(message["role"], avatar=avatar):
#        st.markdown(message["content"])
#
## Accept user input
#if prompt := st.chat_input("What is up?"):
#    # Add user message to chat history
#    st.session_state.messages.append({"role": "user", "content": prompt})
#    # Display user message in chat message container
#    with st.chat_message("user", avatar="🦖"):
#        st.markdown(prompt)
#    
#    # Display assistant response in chat message container
#    with st.chat_message("assistant", avatar="🤖"):
#        message_placeholder = st.empty()
#        user_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] == "user"]
#        rag_document = asyncio.run(db_client.rag_query(user_messages[-1]["content"], database_name="rag-pgvector-conversational-rag-1"))
#        full_response =  asyncio.run(chat_bison(user_messages[-1]["content"], rag_document=rag_document))
#            
#
#        message_placeholder.markdown(full_response)
#    st.session_state.messages.append({"role": "assistant", "content": full_response})




import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "~/Downloads/k.py"
