import os
import asyncio
import threading
import pandas as pd
from flask import Flask, request
from google.cloud import storage
from google.cloud import aiplatform
from utils import ai, database, variables, credentials
from vertexai.preview.vision_models import MultiModalEmbeddingModel, Image

app = Flask(__name__)

var={
    "project_id":variables.PROJECT_ID,
    "region":variables.REGION,
    "video_gcs_uri":variables.VIDEO_GCS_URI,
    "video_transcript_annotations_gcs":variables.VIDEO_TRANSCRIPT_ANNOTATIONS_GCS,
    "snippets_gcs_uri":variables.SNIPPETS_GCS_URI,
    "database_name":variables.DATABASE_NAME,
    "instance_name":variables.INSTANCE_NAME,
    "database_user":variables.DATABASE_USER,
    "database_password":credentials.DATABASE_PASSWORD,
    "linux":variables.LINUX,
}

def preprocess(data):    
    aip = ai.Client(var)
        
    bucket_name = data["bucket"]
    video_name = data["name"]
    
    image_index=[] # (image) MultiModal embeddings from images
    image_ai_type=[]
    image_type=[]
    image_transcript_link=[]
    image_summary=[]
    image_emb=[]
    image_frame_link=[]
    image_video_link=[]
    
    storage.Client(project=var["project_id"]).bucket(bucket_name).blob(video_name).download_to_filename(video_name)
    aiplatform.init(project=var["project_id"], location=var["region"])
    mm = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
    
    print(os.listdir())

    transcript, file_name_transcript = aip.video_transcription(f'gs://{bucket_name}/{video_name}')
    summarization, classification  = aip.llm_sum_class(transcript)
    _dir, _prefix = aip.video_preprocessing(video_name)
    
    _ = [os.path.join(_dir, _vid) for _vid in os.listdir(_dir)]
    
    for frame in _:       
        image_index.append(_prefix)
        image_ai_type.append("from_image")
        image_type.append(classification)
        image_transcript_link.append(f'https://storage.googleapis.com/{var["video_transcript_annotations_gcs"]}/{file_name_transcript}')
        image_summary.append(summarization)
        image_emb.append(mm.get_embeddings(image=Image.load_from_file(frame)).image_embedding)
        image_frame_link.append(f'https://storage.googleapis.com/{var["snippets_gcs_uri"]}/{frame.split("/")[-1]}')
        image_video_link.append(f'https://storage.googleapis.com/{var["video_gcs_uri"]}/{video_name}')
        storage.Client(project=var["project_id"]).bucket(var["snippets_gcs_uri"]).blob(frame.split("/")[-1]).upload_from_filename(frame)
        
    df_merged = pd.DataFrame({
        "index": image_index,
        "ai_type": image_ai_type,
        "class": image_type,
        "image_transcript_link": image_transcript_link,
        "summary": image_summary,
        "frame_link": image_frame_link,
        "video_link": image_video_link,
        "embedding": image_emb
        })
    
    df_merged.to_csv("gs://vtxdemos-tmp/links")
    
    db = database.Client(var)
    asyncio.run(db.create_database())
    asyncio.run(db.insert_item(df_merged))
    
    print("Job Done Succesfully!")
    
    return (f'Detected change in Cloud Storage bucket: {data["bucket"]}', 200)


@app.post("/")
def index():
    
    req = request.get_json() # request from bucket video upload trigger
    print(req)
    data = req["data"]
    preprocess(data)
    print("Job Done!")
    #
    return {"message": "Accepted"}, 202

if __name__ == "__main__":
    # Dev only: run "python main.py" and open http://localhost:8080
    app.run(host="localhost", port=8080, debug=True)
