import time
import base64
import vertexai
import streamlit as st
from typing import Any
from pathlib import Path
from preprocess import gemini15_rag
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold

project_id = "vtxdemos"
bq_dataset = "demos_us"
bq_connection_id = "emb_connection"
bq_embedding_model = "llm_embedding_model"
model = "gemini-1.5-pro-preview-0409"
client = gemini15_rag.Client(model, project_id, bq_dataset, bq_connection_id, bq_embedding_model)

vertexai.init(project=project_id)


def app():
    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []
    if "yourfile" not in st.session_state:
        st.session_state.yourfile = None
    if "filepath" not in st.session_state:
        st.session_state.filepath = None

    with st.expander("Diagram:"):
        st.image("images/ask_your_task_gemini.png")

    @st.cache_data
    def preprocess(filepath):
        return client.preprocess(filepath)

    def display_document(file: str):
        """
        display document in streamlit
        :param file:
        """
        if file == "files/1065_1p.pdf":
            pdf_path = Path(file)
            base64_pdf = base64.b64encode(pdf_path.read_bytes()).decode("utf-8")
            pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" ' \
                          F'width="700" height="1000" type="application/pdf"></iframe>'
        else:
            base64_pdf = base64.b64encode(file.read()).decode("utf-8")
            pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" ' \
                          F'width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    def conversational_bot(chat_history: list, prompt: str, context: dict[str, Any]):
        """
        Using Gemini Pro 1.0 for Conversational AI
        :param chat_history: chat conversation history
        :param context: pdf extraction from gemini_1_5_extraction_model
        :param prompt: query from user
        :return: string
        """
        system_prompt = f"""
            You are a friendly/funny bot called Sockcop, act natural like a human and respond the following <Query>.
            - Use <Context> as your only source of truth.
            - Explain briefly where you get the answer from in the context.
            - If you can't find the answer in your question you say so.
            
            Chat History:
            {chat_history}
            
            """
        conversational_model = GenerativeModel("gemini-1.0-pro-002", system_instruction=[system_prompt])
        if "c_model" not in st.session_state:
            st.session_state.c_model = conversational_model.start_chat()
        conversational_gen_conf = {
            "max_output_tokens": 2048,
            "temperature": 0.55,
            "top_k": 40,
            "top_p": 1,
        }
        conversational_safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
        query = f"""
        Context:
        {context}
        
        User Query:
        {prompt}
        """
        r = st.session_state.c_model.send_message(
            [query],
            generation_config=conversational_gen_conf,
            safety_settings=conversational_safety_settings,
        )
        try:
            st.session_state.taxy_response = r.text
        except:
            st.session_state.taxy_response = f"There is an error with the conversational_response: {r}"
        return st.session_state.taxy_response.replace("*", "").replace("#", "--").replace("/", ",").replace("$", "")

    def response_iterator(text: str):
        """
        Iterator for Streamlit (streaming response)
        :param text:
        """
        for word in text.split():
            yield word + " "
            time.sleep(0.05)

    with st.container():
        col1, col2 = st.columns([1, 1])  # Adjust column ratios as needed

        with col1:
            if st.button("Use Demo File", use_container_width=True, key="gemini15demo_btton1"):
                st.session_state.filepath = "../"
        with col2:
            if st.button("Use your Own File", use_container_width=True, key="gemini15demo_btton2"):
                st.session_state.yourfile = True

        if st.session_state.yourfile is not None:
            filename = st.file_uploader("Upload your PDF", type="pdf")
        elif st.session_state.filepath is not None:
            filename = "files/1065_1p.pdf"
        else:
            filename = None

        if filename:
            with st.expander("pdf view"):
                display_document(filename)
            context_df = preprocess(filename)
            if context_df is not None:
                with st.expander("question examples:"):
                    st.markdown("""
                        - What is the total income?
                        - What is te partnership?
                        """)
                with st.expander("Context From Gemini 1.5 (MultiModal) Model"):
                    st.write(context_df)
        else:
            context_df = None
            st.info("Select an option above to get started")

        for message in st.session_state.chatbot_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.container():
            if prompt := st.chat_input("What is up?"):
                st.session_state.chatbot_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    if context_df is not None:
                        vdb_context = client.query(prompt)
                        _response = conversational_bot(
                            prompt=prompt,
                            chat_history=st.session_state.chatbot_messages[-3:],
                            context=vdb_context)
                        st.session_state.chatbot_messages.append({"role": "sockcop", "content": _response})
                    else:
                        _response = conversational_bot(
                            prompt=prompt,
                            chat_history=st.session_state.chatbot_messages[-3:]
                        )
                        st.session_state.chatbot_messages.append({"role": "sockcop", "content": _response})

                with st.chat_message("assistant"):
                    print(_response)
                    bot_res = st.write_stream(response_iterator(_response))

                st.session_state.chatbot_messages.append({"role": "assistant", "content": bot_res})
app()