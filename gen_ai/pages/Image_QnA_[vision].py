import streamlit as st
from vertexai.preview.vision_models import ImageQnAModel, Image

st.title("Image QnA")

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