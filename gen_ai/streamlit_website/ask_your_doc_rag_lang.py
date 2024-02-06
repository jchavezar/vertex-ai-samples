#%%
import time
import asyncio
import streamlit as st
from utils import vector_database 
from streamlit_chat import message
from utils.video.credentials import *
from langchain.chat_models import ChatOpenAI
from langchain_google_vertexai import VertexAI
from langchain.chains import ConversationChain
from vertexai.language_models import TextEmbeddingModel
from utils import documents_preprocess, sockcop_vertexai
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

st.subheader("Chatbot with Langchain, Gemini Pro, CloudSQL, and Streamlit")

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_rag_lang",
    "database_password": DATABASE_PASSWORD, #utils.video.credentials
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

preprocess_client = documents_preprocess.Client(variables)
vector_database_client = vector_database.Client(variables)
model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
llm_client = sockcop_vertexai.Client(variables)
langchain_llm = llm = VertexAI(model_name="gemini-pro")

@st.cache_data
def preprocess():
    docs = preprocess_client.run(filename="security_definitions.pdf")
    return asyncio.run(vector_database_client.run(docs))

def find_match(input, schema):
    query = model_emb.get_embeddings([input])[0].values
    result = asyncio.run(vector_database_client.query(query, schema))
    return result

def query_refiner(conversation, query):
    prompt_to_redefine = f"""
    Given the following user query and conversation log, 
    formulate a question that would be the most relevant to provide the user with an answer 
    from a knowledge base.

    CONVERSATION LOG: 
    {conversation}

    Query: {query}

    Refined Query:

    """
    parameters = {
        "temperature": 0.7, 
        "max_output_tokens": 1028, "top_p": 0.6, "top_k": 40}  

    response = llm_client.llm2(prompt=prompt_to_redefine, model="gemini-pro", parameters=parameters)
    return response

def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):
        
        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
    return conversation_string

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]
    
if 'requests' not in st.session_state:
    st.session_state['requests'] = []

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)

system_msg_template = SystemMessagePromptTemplate.from_template(template="""Answer the question as truthfully as possible using the provided context, 
and if the answer is not contained within the text below, say 'I don't know'""")


human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=langchain_llm, verbose=True)

# container for chat history
response_container = st.container()
# container for text box
textcontainer = st.container()

with textcontainer:
    schema = preprocess()
    query = st.text_input("Query: ", key="input")
    if query:
        with st.spinner("typing..."):
            conversation_string = get_conversation_string()
            # st.code(conversation_string)
            refined_query = query_refiner(conversation_string, query)
            st.subheader("Refined Query:")
            st.write(refined_query)
            context = find_match(refined_query, schema)
            print("asdfdfadsfads")
            print(context)
            print("asdfadsfds")
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
        st.session_state.requests.append(query)
        st.session_state.responses.append(response) 
with response_container:
    if st.session_state['responses']:

        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i],key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')