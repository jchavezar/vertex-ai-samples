## Before everything I highly recommend to create 2 buckets: gs://video_store* and gs://frame_per_second* [it has to be unique]

#%%
# Importing all necessary libraries
import pandas as pd
import re
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector
from credentials import *
import os
import sys
sys.path.append("..")
import numpy as np
import pandas as pd
from ai import multimodal as mm
import cv2
import os
from google.cloud import storage
from google.cloud import videointelligence as vi
from typing import Optional, Sequence, cast
import vertexai
from vertexai.preview.language_models import TextGenerationModel
from google_database import vector_db

file_with_values = "emb3.csv"
database_name = "video-frame-emb-3"

#%%

# Video are segmented as frames per second images
def video_preprocessing(video):
    from datetime import timedelta
    import cv2
    import numpy as np
    import os

    prefix = video.split(".")[-2]
    # i.e if video of duration 30 seconds, saves 10 frame per second = 300 frames saved in total
    SAVING_FRAMES_PER_SECOND = 1

    def format_timedelta(td):
        """Utility function to format timedelta objects in a cool way (e.g 00:00:20.05) 
        omitting microseconds and retaining milliseconds"""
        result = str(td)
        try:
            result, ms = result.split(".")
        except ValueError:
            return (result + ".00").replace(":", "-")
        ms = int(ms)
        ms = round(ms / 1e4)
        return f"{result}.{ms:02}".replace(":", "-")


    def get_saving_frames_durations(cap, saving_fps):
        """A function that returns the list of durations where to save the frames"""
        s = []
        # get the clip duration by dividing number of frames by the number of frames per second
        clip_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        # use np.arange() to make floating-point steps
        for i in np.arange(0, clip_duration, 1 / saving_fps):
            s.append(i)
        return s


    def main(video_file):
        filename, _ = os.path.splitext(video_file)
        filename += "-opencv"
        # make a folder by the name of the video file
        if not os.path.isdir(filename):
            os.mkdir(filename)
        # read the video file    
        cap = cv2.VideoCapture(video_file)
        # get the FPS of the video
        fps = cap.get(cv2.CAP_PROP_FPS)
        # if the SAVING_FRAMES_PER_SECOND is above video FPS, then set it to FPS (as maximum)
        saving_frames_per_second = min(fps, SAVING_FRAMES_PER_SECOND)
        # get the list of duration spots to save
        saving_frames_durations = get_saving_frames_durations(cap, saving_frames_per_second)
        # start the loop
        count = 0
        while True:
            is_read, frame = cap.read()
            if not is_read:
                # break out of the loop if there are no frames to read
                break
            # get the duration by dividing the frame count by the FPS
            frame_duration = count / fps
            try:
                # get the earliest duration to save
                closest_duration = saving_frames_durations[0]
            except IndexError:
                # the list is empty, all duration frames were saved
                break
            if frame_duration >= closest_duration:
                # if closest duration is less than or equals the frame duration, 
                # then save the frame
                frame_duration_formatted = format_timedelta(timedelta(seconds=frame_duration))
                cv2.imwrite(os.path.join(filename, f"{prefix}{frame_duration_formatted}.jpg"), frame) 
                # drop the duration spot from the list, since this duration spot is already saved
                try:
                    saving_frames_durations.pop(0)
                except IndexError:
                    pass
            # increment the frame count
            count += 1
        return os.path.join(filename), prefix
    return main(video)

# Insert Values on Cloud SQL Function
async def insert_items():
    ##### Insert Items into DB Table
    df = pd.read_csv("emb2.csv")
    df2 = df.copy()
    df2["embedding"] = df2["embedding"].apply(lambda x: x.strip("][").split(","))

    async def main():
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{database_user}",
                password=f"{database_password}",
                db="video-frame-emb",
            )

            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)
            # Create the `video_embeddings` table to store vector embeddings.

            # Store all the generated embeddings back into the database.
            for index, row in df2.iterrows():
                print(np.array(row["embedding"]))
                await conn.execute(
                    "INSERT INTO video_embeddings (summary, frame_link, video_link, embedding) VALUES ($1, $2, $3, $4)",
                    row["summary"],
                    row["frame_link"],
                    row["video_link"],
                    np.array(row["embedding"]),
                )

            x = await conn.fetch("SELECT * FROM video_embeddings")
            for i in x:
               print("te")
               print(i)
            await conn.close()
    await main()  # type: ignore

### Using Video Intelligence API to get the transcription of the video (Speech-to-Text)
def video_transcription(video_uri):
    print("Transcription job started...")
    file_name = video_uri.split('/')[-1].split('.'[0])
    video_client = vi.VideoIntelligenceServiceClient()
    features = [
        vi.Feature.SPEECH_TRANSCRIPTION,
    ]
    config = vi.SpeechTranscriptionConfig(
        language_code="en-US",
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True
    )
    context = vi.VideoContext(
        speech_transcription_config=config,
    )
    request = vi.AnnotateVideoRequest(
        input_uri=video_uri,
        output_uri=f"gs://vtxdemos-fb-videos-json/{file_name}.json",
        features=features,
        video_context=context,
    )

    print(f'Processing video "{video_uri}"...')
    operation = video_client.annotate_video(request)
    response = cast(vi.AnnotateVideoResponse, operation.result())
    transcript = [n.transcript.strip() for i in response.annotation_results[0].speech_transcriptions for n in i.alternatives][:-2]
    transcript = ",".join(transcript)
    print("Transcription job done")
    return transcript

### Using LLMs to create a summarization of video transcript
def llm_sum_class(text):
    vertexai.init(project=project_id, location="us-central1")
    generation_model = TextGenerationModel.from_pretrained("text-bison")

    prompt_1 = """
      Provide a brief summary (no more than 15 words) of the following, try to enrich the data with public resources:
      """+text
    summarization = generation_model.predict(
            prompt_1, temperature=0.4, max_output_tokens=1024, top_k=40, top_p=0.8
        ).text
    prompt_2 = f'''Multi-choice problem: What is the category of the following?

    Text:  {summarization}
    The answer is:
    '''
    classification = generation_model.predict(
            prompt_2, temperature=0.4, max_output_tokens=1024, top_k=40, top_p=0.8
        ).text
    print(summarization)
    return summarization, classification

### Storing video in Google Cloud Storage
def saving_to_gcs(file):
    client = storage.Client(project=project_id)
    client.bucket("vtxdemos-fb-videos").blob(file).upload_from_filename(file)
    print("video saved on GCS job done")


_index=[]
_type=[]
_emb=[]
_frame_link=[]
_video_link=[]
_summary=[]

video_list = [i for i in os.listdir() if re.search("\.mp4$", i)]

for video in video_list:
    saving_to_gcs(video)
    transcription = video_transcription(f"gs://vtxdemos-fb-videos/{video}")
    summarization, classification  = llm_sum_class(transcription)
    _dir, _prefix = video_preprocessing(video)
    _ = [os.path.join(_dir, _vid) for _vid in os.listdir(_dir)]
#df = pd.read_csv("backup_2.csv")
    for i in _:
        _index.append(_prefix)
        _type.append(classification)
        _summary.append(summarization)
        _emb.append(mm.get_embedding(image=i).image_embedding)
        _frame_link.append(f"https://storage.googleapis.com/vtxdemos-fb-frames/{i.split('/')[-1]}")
        _video_link.append(f"https://storage.googleapis.com/vtxdemos-fb-videos/{video}")

#%%
_ = {
    "index": _index,
    "sports_type": _type,
    "summary": _summary,
    "frame_link": _frame_link,
    "video_link": _video_link,
    "embedding": _emb
}
df = pd.DataFrame(_)

## Copy all the frames to GCS (it's faster with gsutil cp best-warriors-opencv/*.* gs://vtxdemos-fb-frames)

#%%
if "df" in locals():
    df.to_csv("emb3.csv", index=False)
else: df=pd.read_csv("emb3.csv")

#%%
database_name = "video-frame-emb-3"
### Remember to create a cloud sql database first: gcloud sql databases create $database_name --instance pg15-pgvector-demo

vdb = vector_db()
cdb = await vdb.create_database(database_name)
await vdb.insert_item(df)

# %%
