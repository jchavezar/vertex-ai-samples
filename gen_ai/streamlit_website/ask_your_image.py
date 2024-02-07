import io
import base64
from distutils.command import upload
import vertexai
from utils.k import *
import streamlit as st
from utils.links_references import *
from vertexai.preview.vision_models import ImageQnAModel, Image
from vertexai.preview.generative_models import GenerativeModel, Part

def app(model, parameters):
    st.title('Gemini Pro Multimodal & Imagen')
    st.markdown("[github repo](https://github.com/jchavezar/vertex-ai-samples/tree/main/gen_ai/pages/Financial_RAG_[Vertex_Search].py)")

    #region Model Settings

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
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({ask_your_image})""")

    uploaded_file = st.file_uploader("Upload your image here...", type=['png', 'jpeg', 'jpg'])
    question = st.text_input(label="Ask something about the image...")

    if uploaded_file is not None:
        st.image(uploaded_file)

    if question and uploaded_file:
        # Image Preprocess
        bytes_io = io.BytesIO(uploaded_file.read())
        base64_string = base64.b64encode(bytes_io.getvalue()).decode("utf-8")

        template = f"""
            You are a business analytics and your goal is to get a very detailed analysis of what you are being asked:
            - Give accurate details as much as possible.

            question:
            {question}

            answer:
        """
        
        if model == "gemini-pro-vision":
            model = GenerativeModel(model)
            image = Part.from_data(data=base64.b64decode(base64_string), mime_type="image/png")
            response = model.generate_content(
                [image, template],
                generation_config=parameters,
                )
            st.info(response.candidates[0].content.parts[0].text)
        
        else: 
            model = ImageQnAModel.from_pretrained("imagetext@001")
            response = model.ask_question(
                image=Image(uploaded_file.getvalue()),
                question=question,
                number_of_results=1,)
            st.info(response)