import streamlit as st
from utils import sockcop_vertexai
from utils.links_references import *
import streamlit.components.v1 as components
from streamlit_extras.colored_header import colored_header

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "news_1687453492092"
}

def app(model, parameters):
    client = sockcop_vertexai.Client(variables)

    st.write("*Topology below represents the elements used by this website*")
    st.write("**Model used: chat-bison@001**")

    st.image("images/genai_demos.png")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({movies_qa})""")
    
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
            st.session_state.messages.append({"role": "general_news", "content": ",".join(client.search("latest news", news=True)["snippets"])})

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            user_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] == "user"]

            news_context = ",".join(client.search("Bring me the latest news", news=True)["snippets"])

            template_context=f"""
            You are a very friendly and funny chat, use the following session data as historic information for your conversations: {st.session_state.messages},
            use the following news enclosed by backticks as your only source of truth, do not make up or use old data: ```{news_context}```,
            from time to times ask friendly questions to gather more information and do not repeat questions,
            When someone ask for demos give the following links: for Image QnA video: https://genai.sonrobots.net/Image_QnA_[vision], for Movies QnA using Enterprise Search: https://genai.sonrobots.net/Movies_QnA_,
            """

            full_response = client.chat_multiturn(user_messages[-1]["content"], template_context, model, parameters)

            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
