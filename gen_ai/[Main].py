import streamlit as st
from utils import sockcop_vertexai

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "kaggle-movies_1692703558099"
}

client = sockcop_vertexai.Client(variables)

st.set_page_config(
    page_title="Generative AI",
    page_icon="👋",
)

st.write("# Welcome to VertexAI 👋")

st.sidebar.success("Select a demo above.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] == "user"]
        st.write(messages)
        full_response = client.chat_bison(prompt=messages[-1]["content"], context=messages[-10:])
        st.write(full_response)
        