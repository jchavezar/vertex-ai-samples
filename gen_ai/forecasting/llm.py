#%%
#region Libraries
import vertexai
from vertexai.language_models import CodeGenerationModel, TextGenerationModel
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
#endregion

#region Variables
project_id="vtxdemos"
region="us-central1"
training_dataset_bq_path="bq://bigquery-public-data:iowa_liquor_sales_forecasting.2020_sales_train"
#endregion

#region Model to Generate Code
def code(**kwargs):
    vertexai.init(project="jchavezar-demo", location="us-central1")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024
    }
    model = CodeGenerationModel.from_pretrained("code-bison@001")
    response = model.predict(
        prefix = """given the following features enclosed by backticks and their values create an rest API call to a vertex endpoint using python:

    ```
    city: Adair
    store_name: Caseys General Store #2521 / Adair
    zip_code: 50003
    county: DALLAS
    ```""",
        **parameters
    )
    print(f"Response from Model: {response.text}")
    return response.text
#endregion

#region LLM Model
def text_bison():
    vertexai.init(project="jchavezar-demo", location="us-central1")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
        """You are a business analytics and want to make forecasting by using variables detected during the following prompt enclosed by backticks, your knowledge base is an endpoint handled by other model so you only need to detect revelant information like store_name, city, zip_code, and county if there\'s something missing ask for them.


    ```
    Given the following values I need a forecasting for the next 3 months, store name: Kum & Go, city: Adair, zip code: 50003 and the county Dallas
    ```

    Output python dictionary as follows: {
    \"store_name\": <store_name>,
    \"city\": <city>,
    \"zip_code\": <zip_code>,
    \"county\": <county>
    }""",
        **parameters
    )
    print(f"Response from Model: {response.text}")
    return response.text
#endregion


#region Chat Model
def chat_model(prompt):
    vertexai.init(project="jchavezar-demo", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    chat = chat_model.start_chat(
        context=f"""You are a business analytics and 
        want to make forecasting by using variables detected during the following prompt 
        enclosed by backticks, your knowledge base is an endpoint handled by other model 
        so you only need to detect revelant information like store_name, city, zip_code, and county if there\'s something missing ask for them.
        Also be gentle and if you do not detect this intention you ask how are they and how can you help them with.


    ```
    {prompt}
    ```

    Output python dictionary:
    {{
    \'store_name\': <store_name>,
    \'city\': <city>,
    \'zip_code\': <zip_code>,
    \'county\': <county>
    }}
    """)
    response=chat.send_message(prompt)
    return response.text
    #response = chat.send_message("""Hi I\'d like to make a forecasting about the next 2 months what do I need?""", **parameters)
    #print(f"Response from Model: {response.text}")
    #response = chat.send_message("""Casey\'s General Store #2521 / Adair""", **parameters)
    #print(f"Response from Model: {response.text}")
    #response = chat.send_message("""Adair""", **parameters)
    #print(f"Response from Model: {response.text}")
    #response = chat.send_message("""50002""", **parameters)
    #print(f"Response from Model: {response.text}")
    #response = chat.send_message("""ADAIR""", **parameters)
    #print(f"Response from Model: {response.text}")#


###

import streamlit as st

st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

response=chat_model(st.session_state.messages[-1]["content"])
# Display assistant response in chat message container
with st.chat_message("assistant"):
    st.markdown(response)
# Add assistant response to chat history

st.session_state.messages.append({"role": "assistant", "content": response})
print(st.session_state.messages[-1]["content"])
print(st.session_state.messages)
