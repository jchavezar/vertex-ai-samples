import streamlit as st
from utils import sockcop_vertexai
import streamlit.components.v1 as components
from streamlit_extras.colored_header import colored_header

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "news_1687453492092"
}

client = sockcop_vertexai.Client(variables)

st.set_page_config(
    page_title="Generative AI",
    page_icon="👋",
)

colored_header(
    label="Generative AI 👋",
    description="Google LLM Demos",
    color_name="violet-70",
)

st.write("*Topology below represents the elements used by this website*")
st.write("**Model used: chat-bison@001**")

st.image("images/genai_demos.png")
st.sidebar.success("Select a demo above.")
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

on = st.toggle('Internet News Enable')
st.write("Talk to me...")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "user":
        avatar="🦖"
    else: avatar="🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user", avatar="🦖"):
        st.markdown(prompt)
    
    if len(st.session_state.messages) == 1:
        st.session_state.messages.append({"role": "general_news", "content": ",".join(client.search(prompt, web_type=True)["snippets"])})
    
    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        user_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] == "user"]
        if on:
            news_context = ",".join(client.search(prompt, web_type=True)["snippets"])
            full_response = client.chat_bison(prompt=user_messages[-1]["content"], news_context=news_context, context=st.session_state.messages)
        else :
            news_context=[m for m in st.session_state.messages if m["role"] == "general_news"]
            full_response = client.chat_bison(prompt=user_messages[-1]["content"], news_context=news_context, context=st.session_state.messages)
            

        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
