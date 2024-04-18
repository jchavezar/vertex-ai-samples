#%%
import io
import os
import time
import vertexai
import pandas as pd
from pdf2image import convert_from_path, convert_from_bytes
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold
from vertexai.language_models import TextEmbeddingModel
from langchain.text_splitter import RecursiveCharacterTextSplitter

project_id = "vtxdemos"

vertexai.init(project=project_id)
model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

def extraction(image):
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0,
        "top_p": 0.55,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Keeping Image bytes in-memory
    images_bytesio = io.BytesIO()
    image.save(images_bytesio, "PNG")
    image1 = Part.from_data(
        mime_type="image/png",
        data=images_bytesio.getvalue(),
    )

    text1 = """You are a tax agent analyst, so your answer needs to be very accurate (100%), 
        from the document extract all the paragraphs, text, images, tables, checkboxes everything to get an 
        structured text as an output. 
        
        - consider checkboxes marked with a clear 'X' as checked (true). All other checkboxes, 
        including empty ones, ambiguous markings, or other symbols, should be treated as unchecked (false)
        - Do not miss any letter or word.
        - Do not make up any key value.
        
        Output in python dictionary:
        """

    text1 = """You are a tax agent analyst, so your answer needs to be very accurate (100%), 
        from the document extract all the paragraphs, text, images, tables, checkboxes everything to get an 
        structured text as an output. 
        
        - consider checkboxes marked with a clear 'X' as checked (true). All other checkboxes, 
        including empty ones, ambiguous markings, or other symbols, should be treated as unchecked (false)
        - Do not miss any letter or word.
        - Do not make up any key value.
        
        Output in structured markdown:
        """
    model = GenerativeModel("gemini-1.5-pro-preview-0409")
    gemini_response = model.generate_content(
        [image1, text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    images_bytesio.close()

    try:
        re = gemini_response.text
    except:
        re = "There was a problem with the extraction, problem: {}".format(gemini_response)
    return re

path = "../documents"
filename = "../documents/1065.pdf"

documents = []
for i in os.listdir(path):
    if i.endswith(".pdf"):
        filename = os.path.join(path, i)

        if type(filename) == str:
            images = convert_from_path(filename)
        else:
            images = convert_from_bytes(filename.getvalue())

        pages = []
        character_limit = 500
        overlap = 20
        chunk_number = 1
        for p, image in enumerate(images):
            start_extraction = time.time()
            text = extraction(image)
            end_extraction = time.time()-start_extraction
            for i in range(0, len(text), character_limit - overlap):
                end_index = min(i + character_limit, len(text))
                chunk = text[i:end_index]
                chunk_r = chunk.encode("ascii", "ignore").decode("utf-8", "ignore")
                # Encode and decode for consistent encoding
                d = {
                    "filename": filename.split("/")[-1],
                    "page_number": p+1,
                    "page_text": text,
                    "chunk_number": chunk_number,
                    "chunk_text": chunk_r,
                    "extraction_time_in_seconds": end_extraction,
                    "embeddings": model_emb.get_embeddings([chunk_r])[0].values
                }
                documents.append(d)
                # Increment chunk number
                chunk_number += 1
pr
df = pd.DataFrame(documents)
df.to_pickle("tax_vdb_latest.pkl")
