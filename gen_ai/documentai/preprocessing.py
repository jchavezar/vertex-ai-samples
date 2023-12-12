#%%
#region libraries
import io
import os
import PyPDF2
from tabulate import tabulate
import google.cloud.documentai_v1 as docai
from typing import Iterator, MutableSequence, Optional, Sequence, Tuple
#endregion

#region variables
FILE_PATH = "./advocate_aurora_health.pdf"
PROJECT_ID = "254356041555"
API_LOCATION = "us"
PROCESSOR = "projects/254356041555/locations/us/processors/5f0b0deeb0a5d23b"
DOCAI_DISPLAY_NAME = "fparser"
#endregion

#processor_id="https://us-documentai.googleapis.com/v1/projects/254356041555/locations/us/processors/5f0b0deeb0a5d23b:process"

#region list documentai processor based on display_name
docai_client = docai.DocumentProcessorServiceClient(
    client_options = {"api_endpoint": f"us-documentai.googleapis.com"})

processors = docai_client.list_processors(parent="projects/254356041555/locations/us")

for processor in processors:
    if processor.display_name == DOCAI_DISPLAY_NAME:
        _processor = processor
#endregion

#region preprocess
def process_file(
    processor: docai.Processor,
    document_content: str,
    mime_type: str,
) -> docai.Document:
    #with open(file_path, "rb") as document_file:
    #    document_content = document_file.read()
    document = docai.RawDocument(content=document_content, mime_type=mime_type)
    request = docai.ProcessRequest(raw_document=document, name=processor.name)

    response = docai_client.process_document(request)

    return response.document

#region reading and splitting file
pdf_data = PyPDF2.PdfReader(FILE_PATH)

pdfs = []

for page in pdf_data.pages:
    writer = PyPDF2.PdfWriter()
    writer.add_page(page)
    with io.BytesIO() as bytes_stream:
        pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())
#endregion

documents = []
for page in pdfs:
    document = process_file(
        processor = _processor,
        document_content = page,
        mime_type = "application/pdf"
    )
    documents.append(document)
#endregion
# %%

#region processing tables
tables = []

for document in documents:
    table = document.pages[0].tables
    _ = len(table)
    if _ > 0:
        print(table)
    

    for table in document.pages[0].tables:
        table_txt = ''

        # add header row
        for h, h_row in enumerate(table.header_rows):
            if h > 0: table_txt += '\n'
            for c, cell in enumerate(h_row.cells):
                if c == 0: table_txt += '|'
                table_txt += "".join(
                    [
                        document.text[segment.start_index:segment.end_index] for segment in cell.layout.text_anchor.text_segments
                    ]
                ).strip().replace('\n','\t')
                table_txt += '|'

        # add delimiter (markdown table)
        for i in range(c+1):
            if i == 0: table_txt += '\n|'
            table_txt += '---|'

        # add body rows
        for b, b_row in enumerate(table.body_rows):
            table_txt += '\n|'
            for c, cell in enumerate(b_row.cells):
                table_txt += "".join(
                    [
                        document.text[segment.start_index:segment.end_index] for segment in cell.layout.text_anchor.text_segments
                    ]
                ).strip().replace('\n','\t')
                table_txt += '|'

        tables.append(table_txt)
#endregion
# %%

import vertexai
from vertexai.language_models import TextGenerationModel

vertexai.init(project="vtxdemos", location="us-central1")
parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison-32k@002")
responses = model.predict_streaming(
    f"""from the follwing context enclosed by backticks give me a summary of the doc:

```{tables}```""",
    **parameters
)
results = []
for response in responses:
  print(response)
  results.append(str(response))
# %%
