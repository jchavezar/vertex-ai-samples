#%%
import time
import vertexai
import streamlit as st
from streamlit_chat import message
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

def llm_predict(input: str):
    config = {
        "max_output_tokens": 2048,
        "temperature": 0.9,
        "top_p": 1
    }
    model = GenerativeModel("gemini-1.0-pro-001")
    chat = model.start_chat()
    res = chat.send_message(f"{input}", generation_config=config, safety_settings={
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    })

    # noinspection PyBroadException
    try:
        re = res.text
    except:
        re = res

    return re


# Streamlit
def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):

        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
    return conversation_string


def stream_data(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.02)

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

# Containers for chat history and text box
response_container = st.container()
text_container = st.container()

with text_container:
    query = st.text_input("Query: ", key="input")
    if query:
        response = llm_predict(input=f"Query:\n{query}")
        print(response)
        st.session_state.requests.append(query)
        st.session_state.responses.append(response)

    st.write(st.session_state.requests)
    st.write(st.session_state.responses)

    with response_container:
        if st.session_state['responses']:
            for i in range(len(st.session_state['responses'])):
                st.write_stream(stream_data(st.session_state['responses'][i]))
                if i < len(st.session_state['requests']):
                    st.write_stream(stream_data(st.session_state['requests'][i]))





