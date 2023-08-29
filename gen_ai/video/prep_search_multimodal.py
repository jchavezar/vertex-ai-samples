#%%
#region Libraries and Variables
import os
import re
import pandas as pd
from PIL import Image
from utils import ai, store, video, database, variables, credentials
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

ai=ai.Client(var)
vi=video.Client(var)
store=store.Client(var)
database=database.Client(var)
mm=MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
#endregion

#region Main: Create Vector Database Structure
image_index=[] # (image) MultiModal embeddings from images
image_ai_type=[]
image_type=[]
image_summary=[]
image_emb=[]
image_frame_link=[]
image_video_link=[]

list = [i for i in os.listdir() if re.search("\.mp4$", i)]

for video in list:
    store.saving_to_gcs(video)
    transcript, transcript_list = ai.video_transcription(f"gs://{var['video_gcs_uri']}/{video}") #Speech to Text / Captioning / Video Transcription
    summarization, classification  = ai.llm_sum_class(transcript) #text-bison to summarize and classify transcription
    _dir, _prefix = vi.preprocess(video) #Video Preprocessing: From video to Frames Per Second / images
    
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
        image_video_link.append(f"https://storage.googleapis.com/{var['video_gcs_uri']}/{video}")
        store.saving_to_gcs(frame,video=False)

df_merged = pd.DataFrame({
    "index": image_index,
    "ai_type": image_ai_type,
    "class": image_type,
    "summary": image_summary,
    "frame_link": image_frame_link,
    "video_link": image_video_link,
    "embedding": image_emb
})
#%%
# This is needed in case the session has been closed.
if "df_merged" in locals():
    df_merged.to_pickle(var['pickle_file_name'])
else: df_merged=pd.read_pickle(var['pickle_file_name'])
#endregion    


#%%
#region Database Create/Insert
### Remember to create a cloud sql database first: gcloud sql databases create $database_name --instance pg15-pgvector-demo

await database.create_database()
await database.insert_item(df_merged)
#%%
await database.delete()
await database.query_test("SELECT * FROM video_embeddings")
#endregion


# %%
