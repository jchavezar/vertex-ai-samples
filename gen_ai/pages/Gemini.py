import os
import re
import sys
import json
import shutil
from k import *
import streamlit as st
import vertexai
import multiprocessing
from PyPDF2 import PdfWriter, PdfReader
from google.cloud import vision, storage
sys.path.append("/home/atreides/vertex-ai-samples/gen_ai/utils")
from cloud_storage import upload_directory_with_transfer_manager, download_all_blobs_with_transfer_manager, reset_defaults
from vertexai.preview.language_models import TextGenerationModel

st.title("Welcome to Document as a Context...")
st.markdown("**Instructions:** Upload any pdf document and ask something about it")

#region infobot
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

st.components.v1.html(button, height=700, width=1200)

st.markdown(
    """
    <style>
        iframe[width="1200"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
#endregion

bucket_name = "vtxdemos-vision"
local_input_path = "/tmp/input"
local_output_path = "/tmp/output"

uploaded_file = st.file_uploader("Upload your image here...", type=['pdf'])

if uploaded_file is None:
    st.stop()
else:
    with open("/tmp/book.pdf", "wb") as f:
        f.write(uploaded_file.read())


#region Using Vision AI for OCR
def vision_ocr(input_file: str):
  input_file_uri=f"gs://vtxdemos-vision/data/{input_file}"
  gcs_destination_uri=f"gs://vtxdemos-vision/output/{input_file.split('.')[0]}/"

  client = vision.ImageAnnotatorClient()
  feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

  gcs_source = vision.GcsSource(uri=input_file_uri)
  input_config = vision.InputConfig(gcs_source=gcs_source, mime_type="application/pdf")
  gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
  output_config = vision.OutputConfig(
    gcs_destination=gcs_destination, batch_size=2
    )

  async_request = vision.AsyncAnnotateFileRequest(
          features=[feature], input_config=input_config, output_config=output_config
      )
  operation = client.async_batch_annotate_files(requests=[async_request])

  print("Waiting for the operation to finish.")
  operation.result(timeout=420)
#endregion

#region Set defaults
if os.path.exists(local_input_path):
  shutil.rmtree(local_input_path, ignore_errors=True)
  
if os.path.exists(local_output_path+"/output"):
  shutil.rmtree(local_output_path+"/output", ignore_errors=True)

os.mkdir(local_input_path)
reset_defaults(bucket_name, )
#endregion

#region Split and limit document for n pages
file_length = st.selectbox(
    'How many pages would you like to take as context? (time sensitive)',
    (0,10, 20, 40, 100),
    index=0,
    placeholder="Select number of pages"
    )

if file_length != 0:
  inputpdf = PdfReader(open("/tmp/book.pdf", "rb"))

  if len(inputpdf.pages) < file_length:
    st.write(f"I'm sorry I only have {len(inputpdf.pages)}")
    file_length=len(inputpdf.pages)

  progress_text=f"Splitting document by page (taking {file_length} pages only)..."
  my_bar = st.progress(0, text=progress_text)
  for i in range(file_length):
      output = PdfWriter()
      output.add_page(inputpdf.pages[i])
      with open(f"{local_input_path}/document-page%s.pdf" % i, "wb") as outputStream:
          output.write(outputStream)
      my_bar.progress(i+1, text=progress_text)
  st.markdown(f"Uploading {file_length} pages to GCS, please wait...")
  upload_directory_with_transfer_manager(bucket_name, local_input_path)
  st.markdown("**Done**")
  #endregion

  #%%
  #region Paralell OCS process
  st.write("Using Vision AI for OCR in parallel, please wait...")
  st.write("While waiting enjoy the toplogy for this demo...")
  st.image("images/32k-text-bison.png")
  pool = multiprocessing.Pool()
  pool = multiprocessing.Pool(processes=4)
  inputs = [f"document-page{i}.pdf"for i in range(file_length)]
  outputs = pool.map(vision_ocr, inputs)

  #%%
  if not os.path.exists(local_output_path):
    os.makedirs(local_output_path)
  download_all_blobs_with_transfer_manager(bucket_name, local_output_path.split("/")[1]+"/")
  #endregion

  #region postprocess: reading out
  def read_outputs(file_path_name):
    with open(file_path_name, "r") as f:
      d = json.load(f)
      if "fullTextAnnotation" in d["responses"][0].keys():
        output = d["responses"][0]["fullTextAnnotation"]["text"]
        return output

  pages = {}
  ocr_documents = []
  for root in os.listdir(local_output_path):
      if re.match(".*document.*", root):
          for n,object in enumerate(os.listdir(os.path.join(local_output_path,root))):
            pages[re.search("page\d*",os.path.join(local_output_path,root,object)).group(0)]=os.path.join(local_output_path,root,object)

  progress_text="Converting files to json"
  my_bar = st.progress(0, text=progress_text)
  for n, (k,v) in enumerate(pages.items()):
    pages[k] = read_outputs(v)
    my_bar.progress(n+1, text=progress_text)
  #endregion

  #region text-bison-32k
  input=st.text_input(label="Do something with your document...", value="Give me a detailed summary of the document")
  st.markdown("*Gemini is reading out your document and following your instructions...*")
  vertexai.init(project="vtxdemos", location="us-central1")
  parameters = {
      "max_output_tokens": 1024,
      "temperature": 0.2,
      "top_p": 0.8,
      "top_k": 40
  }
  model = TextGenerationModel.from_pretrained("text-bison-32k")
  response = model.predict(
      f"""From the following context enclosed by backticks and expressed as dictionary of pages and content, follow the instructions below:
  ```
  {pages}

  Instructions: {input},
  Please respond in the language the document is.
  ```""",
      **parameters
  )
  print(f"Response from Model: {response.text}")

  st.markdown("**Response:**\n")
  st.markdown(response.text)
  #endregion
