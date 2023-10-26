#%%
#region Import Libraries
import io
import json
import time
import PyPDF2
import concurrent
from google.cloud import documentai
from PyPDF2 import PdfWriter, PdfReader
from google.cloud.documentai_v1 import Document
#endregion

#region Set Variables
project_id = "vtxdemos"
region = "us-central1"
location = "us"
docai_processor_id = "projects/254356041555/locations/us/processors/5f0b0deeb0a5d23b"
pdfs = []
results = []
documents = {}
page_images = []
#endregion

#region set document_ai for ocr
docai_client = documentai.DocumentProcessorServiceClient(
    client_options = {"api_endpoint": f"{location}-documentai.googleapis.com"}
)
#endregion

#%%
#region Document Preprocess
#splitting per pages, ocr streaming and split it further by chunks
def reading_file(filename: str):
    pdf_data = PyPDF2.PdfReader(filename)

    for page in pdf_data.pages:
      writer = PyPDF2.PdfWriter()
      writer.add_page(page)
      with io.BytesIO() as bytes_stream:
        pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())

    rate_limit_minute = 120
    adjust_rate_limit = rate_limit_minute / 2

    def docai_runner(p, start, raw_document):
      sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
      if sleep_time > 0: time.sleep(sleep_time)
      return docai_client.process_document(request = {"raw_document" : documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'), "name" : docai_processor_id})

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                docai_runner,
                p, start,
                file
            ) for p, file in enumerate(pdfs)
        ]
        for future in concurrent.futures.as_completed(futures):
          results.append(Document.to_dict(future.result().document))

    documents = {}
    for page, result in enumerate(results):
        documents[str(page)] = result["text"]
    return documents
documents = reading_file("../../files/othello.pdf")
#endregion
# %%

#region Storing ocr dictionary as file
with open("../../files/othello.json", "w") as f:
    json.dump(documents, f)
#endregion

# %%
