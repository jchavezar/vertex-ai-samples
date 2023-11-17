#region Libraries and Variables
import os
import re
import base64
import vertexai
import pandas as pd
from PIL import Image
from google.cloud import storage
from flask import Flask, request
from utils import ai, video, variables, credentials
from vertexai.preview.vision_models import MultiModalEmbeddingModel, Image

var={
    "project_id":variables.PROJECT_ID,
    "region":variables.REGION,
    "video_gcs_uri":variables.VIDEO_GCS_URI,
    "pickle_file_name":variables.PICKLE_FILE_NAME,
    "snippets_gcs_uri":variables.SNIPPETS_GCS_URI,
    "video_transcript_annotations_gcs":variables.VIDEO_TRANSCRIPT_ANNOTATIONS_GCS,
    "database_name":variables.DATABASE_NAME,
    "instance_name":variables.INSTANCE_NAME,
    "database_user":variables.DATABASE_USER,
    "database_password":credentials.DATABASE_PASSWORD,
    "linux":variables.LINUX,
}

app = Flask(__name__)
# [END eventarc_pubsub_server]


# [START eventarc_pubsub_handler]
@app.route("/", methods=["POST"])
def index():
    data = request.get_json()
    print(data["bucket"])
    print(data)
    if not data:
        msg = "no eventarc received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(data, dict) or "bucket" not in data:
        msg = "invalid message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400
    
    vertexai.init(project=variables.PROJECT_ID, location=variables.REGION)
    client = storage.Client(project=var["project_id"])

    aip = ai.Client(var)
    vi = video.Client(var)
    #vdb = database.Client(var)
    mm = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
    #endregion

    #region Main: Create Vector Database Structure
    image_index=[] # (image) MultiModal embeddings from images
    image_ai_type=[]
    image_type=[]
    image_summary=[]
    image_emb=[]
    image_frame_link=[]
    image_video_link=[]

    file_name = data["name"].split("/")[-1]
    transcript = aip.video_transcription(f"gs://{data['bucket']}/{data['name']}") #Speech to Text / Captioning / Video Transcription
    summarization, classification  = aip.llm_sum_class(transcript) #text-bison to summarize and classify transcription
    _dir, _prefix = vi.preprocess(data["bucket"], data["name"]) #Video Preprocessing: From video to Frames Per Second / images

    _ = [os.path.join(_dir, _vid) for _vid in os.listdir(_dir)]
    for frame in _:       
        image_index.append(_prefix)
        image_ai_type.append("from_image")
        image_type.append(classification)
        image_summary.append(summarization)
        image_emb.append(mm.get_embeddings(image=Image.load_from_file(frame)).image_embedding)
        if var['linux']:
            image_frame_link.append(f"https://storage.googleapis.com/{var.snippets_gcs_uri}/{frame.split('/')[-1]}")
        else: 
            f= frame.split('\\')[-1]
            image_frame_link.append(f"https://storage.googleapis.com/{var['snippets_gcs_uri']}/{f}")
        image_video_link.append(f"https://storage.googleapis.com/{var['video_gcs_uri']}/{file_name}")
        client.bucket(var.snippets_gcs_uri).blob(data['name']).upload_from_filename(file_name)
        
        print("done")    

    return ("done", 200)





# [END eventarc_pubsub_handler]


# [START eventarc_pubsub_server]
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))