import io
import base64
from distutils.command import upload
import vertexai
from k import *
import streamlit as st
from PIL import Image
from vertexai.preview.vision_models import ImageQnAModel
from vertexai.preview.generative_models import GenerativeModel, Part

st.title('Gemini Pro Multimodal')
#st.image("images/rag_vertexsearch.png")
st.markdown("[github repo](https://github.com/jchavezar/vertex-ai-samples/tree/main/gen_ai/pages/Financial_RAG_[Vertex_Search].py)")

#region Model Settings

params = {
    "Gemini Pro Vision": "gemini-pro-vision"
}

settings = ["Gemini Pro Vision"]

model = st.sidebar.selectbox("Choose a text model", settings)
model = params[model]

temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.2) 
token_limit = st.sidebar.select_slider("Token Limit", range(1, 2049), value=2048)
top_k = st.sidebar.select_slider("Top-K", range(1, 41), value=40)
top_p = st.sidebar.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.8) 
    
parameters =  {
    "temperature": temperature,
    "max_output_tokens": token_limit,
    "top_p": top_p,
    "top_k": top_k
    }

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
    
    model = GenerativeModel(model)
    image = Part.from_data(data=base64.b64decode(base64_string), mime_type="image/png")
    response = model.generate_content(
        [image, template],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
            },
        )
    st.write(response.candidates[0].content.parts[0].text)
    print("Answer")
  
#     st.write(responses)
    
# button = f'''<script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
# <df-messenger
#   agent-id="{dialogflow_id}"
#   language-code="en">
#   <df-messenger-chat-bubble
#    chat-title="infobot"
#    bot-writing-text="..."
#    placeholder-text="Tell me something!">
#   </df-messenger-chat-bubble>
# </df-messenger>
# <style>
#   df-messenger {{
#     z-index: 999;
#     position: fixed;
#     bottom: 16px;
#     right: 16px;
#   }}
# </style>'''

# st.components.v1.html(button, height=700, width=350)

# st.markdown(
#     """
#     <style>
#         iframe[width="350"] {
#             position: fixed;
#             bottom: 60px;
#             right: 40px;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

