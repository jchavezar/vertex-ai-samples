#%%
import base64
import io
import time
import vertexai
import streamlit as st
from pathlib import Path
from pdf2image import convert_from_path, convert_from_bytes
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

vertexai.init(project="jesusarguelles-sandbox", location="us-central1")
extraction_model = GenerativeModel("gemini-1.5-pro-preview-0409")
<<<<<<< HEAD

if "taxy_response" not in st.session_state:
    st.session_state.taxy_response = ""

=======
conversational_model = GenerativeModel("gemini-1.0-pro-001")
>>>>>>> origin/main

def gemini_1_5_extraction_model(image):
    """
    Gemini 1.5 Pro (MultiModal) to extract text from PDF
    :return: text
    """
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0,
<<<<<<< HEAD
        "top_p": 0.55,
=======
        "top_p": 0.95,
>>>>>>> origin/main
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    }
    images_bytesio = io.BytesIO()
    image.save(images_bytesio, "PNG")
    image1 = Part.from_data(
        mime_type="image/png",
        data=images_bytesio.getvalue(),
    )

    text1 = """You are a tax agent analyst, so your answer needs to be very accurate (100%), 
                - from the document extract all the paragraphs, text, images, tables, checkboxes everything to get an 
                structured text as an output. 
<<<<<<< HEAD
                - Do not miss any letter or word.
                - Do not make up any key value.
                - If you have unchecked boxes do not count them.
                """
=======
                - Do not miss any letter or word, and do not make up any value."""
>>>>>>> origin/main

    st.markdown(":blue[Reading the file, please wait...]")
    gemini_response = extraction_model.generate_content(
        [image1, text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    images_bytesio.close()
    try:
        response = gemini_response.text
    except:
        response = f"There is an error with the gemini_response: {gemini_response}"
    return response

<<<<<<< HEAD

# noinspection PyBroadException
def gemini_1_0_conversational_model(query: str, chat_history: list, context: dict = ""):
    """
    Using Gemini Pro 1.0 for Conversational AI
    :param chat_history: chat conversation history
    :param context: pdf extraction from gemini_1_5_extraction_model
    :param prompt: query from user
    :return: string
    """
    system_prompt = f"""
    You are a friendly/funny bot called Sockcop, act natural like a human.
    - Use <Context> as source of truth only if you have it.
    - If the <Context> is used, expose/explain your references/findings.
    - If you can't find the answer in your question you say so.
    
    Chat History:
    {chat_history}
    
    Context:
    {context}
    """
    conversational_model = GenerativeModel("gemini-1.0-pro-002", system_instruction=[system_prompt])
    if "c_model" not in st.session_state:
        st.session_state.c_model = conversational_model.start_chat()
=======
# noinspection PyBroadException
def gemini_1_0_conversational_model(prompt: str):
    """
    Using Gemini Pro 1.0 for Conversational AI
    :param prompt:
    :return:
    """
>>>>>>> origin/main
    conversational_gen_conf = {
        "max_output_tokens": 2048,
        "temperature": 0.55,
        "top_k": 40,
        "top_p": 1,
    }
<<<<<<< HEAD
    st.write(len(chat_history))
=======

>>>>>>> origin/main
    conversational_safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    }
<<<<<<< HEAD
    r = st.session_state.c_model.send_message(
        [query],
=======

    conversational_gemini_response = conversational_model.generate_content(
        [prompt],
>>>>>>> origin/main
        generation_config=conversational_gen_conf,
        safety_settings=conversational_safety_settings,
    )
    try:
<<<<<<< HEAD
        st.session_state.taxy_response = r.text
    except:
        st.session_state.taxy_response = f"There is an error with the conversational_response: {r}"
    return st.session_state.taxy_response
=======
        return conversational_gemini_response.text.replace("*", "")
    except:
        return f"There is an error with the conversational_gemini_response: {conversational_gemini_response}"
>>>>>>> origin/main


def response_iterator(text: str):
    """
    Iterator for Streamlit (streaming response)
    :param text:
    """
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

<<<<<<< HEAD

=======
>>>>>>> origin/main
def streamlit():
    """
    Function for streamlit app
    :return:
    """
    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []
    if "yourfile" not in st.session_state:
        st.session_state.yourfile = False
    if "filepath" not in st.session_state:
        st.session_state.filepath = False

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

<<<<<<< HEAD
=======
    # @st.cache_data
    # def preprocess(file_uri: str):
    #     preprocess_client = documents_preprocess.Client(variables)
    #     vector_database_client = vector_database.Client(variables)
    #     docs = preprocess_client.run(file_uri=file_uri)
    #     return asyncio.run(vector_database_client.run(docs))

>>>>>>> origin/main
    @st.cache_data
    def preprocess(file_uri):
        """
        Using Gemini Pro 1.5 (MultiModal) to extract text from PDF
        :param file_uri:
        :return:
        """
        if file_uri == str:
            images = convert_from_path(file_uri)
        else:
            images = convert_from_bytes(file_uri.getvalue())
<<<<<<< HEAD
=======
        images_bytesio = io.BytesIO()
        #st.write(images)
>>>>>>> origin/main

        document = {}

        st.markdown(f"Number of pages: {len(images)}")
        start = time.time()
        q = 1
        for p, image in enumerate(images):
            response = gemini_1_5_extraction_model(image)
            document[f"page_{p+1}"] = response
            q += 1
            elapsed_time = time.time() - start
<<<<<<< HEAD
            st.markdown("Elapsed time: {:.2f} sec, number of pages: {}".format(elapsed_time, p+1))
=======
            st.markdown("Elapsed time: {:.2f} sec, number of pages: {}".format(elapsed_time,p+1))
>>>>>>> origin/main

            if q == 6 and elapsed_time < 60:
                time.sleep(60-elapsed_time)
                q = 1
                start = time.time()
        # images_bytesio.close()
        st.markdown("Job Finished in: {:.2f} sec".format(time.time()-start))
        return document

    with st.container():
        col1, col2 = st.columns([1, 1])  # Adjust column ratios as needed
<<<<<<< HEAD
=======
        yourfile = None
>>>>>>> origin/main

        with col1:
            if st.button("Use Demo File", use_container_width=True):
                st.session_state.filepath = "../"
        with col2:
            if st.button("Use your Own File", use_container_width=True):
                st.session_state.yourfile = True

        if st.session_state.yourfile:
            filename = st.file_uploader("Upload your PDF", type="pdf")
        elif st.session_state.filepath:
            filename = "files/1065_1p.pdf"
        else:
            filename = None

        if filename:
            with st.expander("pdf view"):
                display_document(filename)
            context = preprocess(filename)
            if context:
                with st.expander("question examples:"):
                    st.markdown("""
                    - What is the total income?
                    - What is te partnership?
                    """)
                with st.expander("Context From Gemini 1.5 (MultiModal) Model"):
                    st.write(context)
        else:
            context = None

        st.info("Select an option above to get started")

        with st.container():
            for message in st.session_state.chatbot_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("What is up?"):
                st.session_state.chatbot_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    if context:
<<<<<<< HEAD
                        _response = gemini_1_0_conversational_model(
                            query=prompt,
                            chat_history=st.session_state.chatbot_messages[-3:],
                            context=context)
                        st.session_state.chatbot_messages.append({"role": "sockcop", "content": _response})
                    else:
                        _response = gemini_1_0_conversational_model(
                            query=prompt,
                            chat_history=st.session_state.chatbot_messages[-3:]
                        )
                        st.session_state.chatbot_messages.append({"role": "sockcop", "content": _response})
=======
                        _response = gemini_1_0_conversational_model(f"Use the following context to answer the question:\n"
                                           f"- Be verbose and give details about your findings\n"
                                           f"- Explain your findings if possible\n"
                                           f"Context: \n{context}\n"
                                           f"User Query:\n{prompt}")
                    else:
                        _response = gemini_1_0_conversational_model(prompt)
>>>>>>> origin/main

                with st.chat_message("assistant"):

                    bot_res = st.write_stream(response_iterator(_response))

                st.session_state.chatbot_messages.append({"role": "assistant", "content": bot_res})


streamlit()
