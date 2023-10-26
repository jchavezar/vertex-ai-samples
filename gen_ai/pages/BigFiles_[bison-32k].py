import json
import base64
import vertexai
import streamlit as st
from vertexai.preview.language_models import TextGenerationModel

st.title("Using 35 Pages as Context for Text-Bison")
st.write("Preprocessing handled before with DocumentAI API to OCR.")
st.markdown("[processing code](https://github.com/jchavezar/vertex-ai-samples/tree/main/gen_ai/pages/preprocess)")
@st.cache_data
def read_document():
    with open("../files/othello.json", "r") as f:
        documents = json.load(f)
    return documents

documents = read_document()

with open("../files/othello.pdf", "rb") as pdf_file:
    encoded_pdf = pdf_file.read()
#

base64_pdf = base64.b64encode(encoded_pdf).decode("utf-8")
pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
st.markdown(pdf_display, unsafe_allow_html=True)

# %%
#input = "Create a summary per page from the context, remember you have to fit 8000 tokens in your response"
input= st.text_input(label="Do something with your document...", value="Create a summary per page from the context")
st.markdown("*Bigboy LLM is reading out your 35 pages document and following your instructions...*")
#
#st.write(documents)
vertexai.init(project="vtxdemos", location="us-central1")
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 8000,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}

#_documents = [v for k,v in documents.items()]
model = TextGenerationModel.from_pretrained("text-bison-32k")
response = model.predict(
    f"""from the following context create a summary per page: {str(documents)}""",
    **parameters
)
print(f"Response from Model: {response.text}")
st.markdown("**Response:**\n")
st.markdown(response.text)


# %%
