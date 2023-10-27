import streamlit as st
from k import *
from vertexai.preview.vision_models import ImageQnAModel, Image

st.title("Image QnA")
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
question=st.text_input(label="Ask something about the image...")

if uploaded_file is not None:
    st.image(uploaded_file)

if question:
    model = ImageQnAModel.from_pretrained("imagetext@001")
    #image = Image.load_from_file("image.png")
    answers = model.ask_question(
        image=Image(uploaded_file.getvalue()),
        question=question,
        # Optional:
        number_of_results=1,
    )
    st.write(answers)
    
button = f'''<script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
<df-messenger
  agent-id="{dialogflow_id}"
  language-code="en">
  <df-messenger-chat-bubble
   chat-title="infobot"
   bot-writing-text="..."
   placeholder-text="Tell me something!">
  </df-messenger-chat-bubble>
</df-messenger>
<style>
  df-messenger {{
    z-index: 999;
    position: fixed;
    bottom: 16px;
    right: 16px;
  }}
</style>'''

st.components.v1.html(button, height=700, width=350)

st.markdown(
    """
    <style>
        iframe[width="350"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

