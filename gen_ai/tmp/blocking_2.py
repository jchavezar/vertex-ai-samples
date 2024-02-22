#%%
#region PDF Document Extraction of Multiple Pages    
import io
import time
import PyPDF2
import concurrent
from google.cloud import documentai
from google.cloud.documentai_v1 import Document
import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import GenerativeModel, Part

variables = {
    "project_id": "vtxdemos",
    "project": "vtxdemos",
    "region": "us-central1",
    "instance_name": "pg15-pgvector-demo",
    "database_user": "emb-admin",
    "database_name": "ask_your_doc_tax_lang",
    "docai_processor_id": "projects/254356041555/locations/us/processors/2fba46b6c23108b7",
    "location": "us",
}

docai_client = documentai.DocumentProcessorServiceClient(
    client_options = {"api_endpoint": f"{variables['location']}-documentai.googleapis.com"}
    )

def read_file(filename: str):
    pdfs = []
    docs = []
    pdf_data = PyPDF2.PdfReader(filename)
    print(f"Number of pages: {len(pdf_data.pages)}")
    for page in pdf_data.pages:
        writer = PyPDF2.PdfWriter()
        writer.add_page(page)
        with io.BytesIO() as bytes_stream:
            pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())        

    rate_limit_minute = 120
    adjust_rate_limit = rate_limit_minute / 2

    
    print(":blue[Reading the file, please wait...]")
    def docai_runner(p, start, raw_document):

        sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
        if sleep_time > 0: 
            time.sleep(sleep_time)
        return docai_client.process_document(
            request = documentai.ProcessRequest(
            name = variables["docai_processor_id"],
            raw_document = documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'),
            process_options = documentai.ProcessOptions(
            from_start = 5)))
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                docai_runner,
                p, start,
                file
            ) for p, file in enumerate(pdfs)
        ]
        for page, future in enumerate(concurrent.futures.as_completed(futures)):
            docs.append(Document.to_dict(future.result().document)["text"])
    print("Job Finished in: {:.2f} sec".format(time.time()-start))
    return docs
#endregion
# %%


docs = read_file("garm_table.pdf")

article = """

Extraordinarily high bacteria levels in Iowa lake

TWIN LAKES, Iowa —
The Iowa Department of Natural Resources is cautioning people about entering the water at North Twin Lake near Fort Dodge after a test showed extraordinarily high bacteria levels.

The Fort Dodge Messenger newspaper reports the DNR says a May 20 sample taken at Treman Park showed 160,000 E. coli bacteria per 100 milliliters of water. State guidelines set a maximum E. coli level of 235 bacteria per 100 milliliters.

Jason McCurdy, of the DNR, says it's the highest level he's seen at a beach.

By Tuesday, the level had fallen to 1,200 at Treman. Levels were below the state maximum level at other spots along the lake.

Calhoun County Conservation director Keith Roos says the problem was probably due to agricultural runoff after heavy rain, but other causes were possible.

"""


# %%


cat_search_prompt_new = f"""
        You are a brand safety tool. Answer the following question using only the article and brand safety categories provided.
        
        ARTICLE:
        {article}.
        END OF ARTICLE
        
        BRAND SAFETY CATEGORIES:
        {str(docs[0])}.
        END OF BRAND SAFETY CATEGORIES
        
        Use the following rules to answer the question:
            1. If no categories are mentioned in the article, the answer is "None".
            2. Store your results as a python dictionary without a variable - store explanations as strings.
            3. Do not included categories not mentioned in the article.
            4. Do not list all the categories in the table.       
            
        QUESTION: Find which brand safety categories from this category list are in the provided article.
        - Remember your task is to list categories that are in the article and EXPLAIN HOW YOU FOUND THESE CATEGORIES. """


model = GenerativeModel("gemini-pro")

responses = model.generate_content(
    cat_search_prompt_new,
    generation_config={
        "max_output_tokens": 8000,
        "temperature": 0.9,
        "top_p": 1
    },
    safety_settings={
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    },
  )
# %%
