#%%
import re
import sys
import vertexai
import pandas as pd
from vertexai.language_models import TextGenerationModel
from google.cloud import storage
from pypdf import PdfReader
from credentials import *
from google_database import vector_db
sys.path.append("..")
from ai import multimodal as mm

project_id="vtxdemos"
bucket="vtxdemos-fb-documents"
region="us-central1"
Linux=True

st_bucket=storage.Client().bucket(bucket)
blobs = [i.name for i in st_bucket.list_blobs() if re.search("\.pdf$", i.name)]
for i in blobs:
    if Linux:
        st_bucket.blob(i).download_to_filename(f"documents/{i}")
    else:
        st_bucket.blob(i).download_to_filename(f"documents\\{i}")

def document_reader(document):
    if Linux:
        reader = PdfReader(f"documents/{document}")
    else:
        reader = PdfReader(f"documents\\{document}")
    number_of_pages = len(reader.pages)
    page = reader.pages[0]
    text = page.extract_text()
    return text

def summarization(text):
    vertexai.init(project=project_id, location=region)
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
        }
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
        f"""Context: You're a very professional and creative chef using the following context 
        enclosed by backticks give me a description in no more than 25 words, never tell how professional you are just try to sell your recipe:
        
        ```{text}```""",
        **parameters)
    return response.text

index=[]
sports_type=[]
summary=[]
frame_link=[]
video_link=[]
emb=[]
frame_link=[]
video_link=[]
for i in blobs:
    text=document_reader(i)
    index.append(i.split(".")[0])
    sports_type.append("cook_document")
    summary.append(summarization(text))
    emb.append(mm.get_embedding(text=i).text_embedding)
    frame_link.append(f"https://storage.googleapis.com/{bucket}/{i.split('.')[0]}.jpg")
    video_link.append(f"https://storage.googleapis.com/{bucket}/{i}")


#%%
df = pd.DataFrame({
    "index": index,
    "sports_type": sports_type,
    "summary": summary,
    "frame_link": frame_link,
    "video_link": video_link,
    "embedding": emb
})

vdb = vector_db(
    project_id=project_id,
    region=region,
    instance_name=instance_name,
    database_user=database_user,
    database_password=database_password
)
cdb = await vdb.create_database(database_name)
await vdb.insert_item(df, database_name=database_name)
# %%
