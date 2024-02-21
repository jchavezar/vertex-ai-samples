
#%%
import io
import time
import PyPDF2
import concurrent
from google.cloud import documentai
from google.cloud.documentai_v1 import Document

variables = {
    "project_id": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    #"database_password": DATABASE_PASSWORD,
    "database_name": "rag-pgvector-langchain-1",
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us"
}


pdfs = []
results = []
documents = {}
start_job_time = time.time()
        
docai_client = documentai.DocumentProcessorServiceClient(
    client_options = {"api_endpoint": f"{variables['location']}-documentai.googleapis.com"}
)

pdf_data = PyPDF2.PdfReader("form.pdf")

for page in pdf_data.pages:
    writer = PyPDF2.PdfWriter()
    writer.add_page(page)
    with io.BytesIO() as bytes_stream:
        pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())
rate_limit_minute = 120
adjust_rate_limit = rate_limit_minute / 2

#region Doing OCR of multiple pages
print("Entering in OCR zone")
def docai_runner(p, start, raw_document):
  #print(f"Doc: {p}")
  sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
  if sleep_time > 0: 
      time.sleep(sleep_time)
  return docai_client.process_document(
      request = documentai.ProcessRequest(
      name = variables["docai_processor_id"],
      raw_document = documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'),
      ))
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
def split_text_by_chunks(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
documents = {}
for page, result in enumerate(results):
    documents[str(page)] = split_text_by_chunks(result["text"], 750)
ocr_time = time.time()-start_job_time
print(f"Time checkpoint [ocr]: {ocr_time}")
#endregion
# %%


def extractor(component):
    
    components = []
    
    for part in component:
        components.append(
            "".join(
                [
                    results[0]["text"][int(segment["start_index"]):int(segment["end_index"])] for segment in part["layout"]["text_anchor"]["text_segments"]
                ]
            )
        )
    
    return components
# %%

resp = [{p:extractor(txt["pages"][0]["lines"])} for p, txt in enumerate(results)]
respo2 = [extractor(i["pages"][0]["lines"]) for i in results]
#page = results[0]["pages"][0]
#lines = extractor(page["lines"])
# %%
