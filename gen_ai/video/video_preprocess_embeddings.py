#%%
#region Librariess
import cv2
import os
import re
import sys
import vertexai
import numpy as np
import pandas as pd
from datetime import timedelta
from google.cloud import storage
from google_database import vector_db
from typing import Optional, Sequence, cast
from google.cloud import videointelligence as vi
from vertexai.preview.language_models import TextGenerationModel
sys.path.append("..")
from ai import multimodal as mm
#endregion

#region Variables
project_id="vtxdemos"
region="us-central1"
video_gcs_uri="vtxdemos-fb-videos"
video_transcript_annotations_gcs="vtxdemos-fb-videos-json"
fps_gcs_uri="vtxdemos-fb-snippets"
database_name ="video-frame-emb-2"
instance_name="pg15-pgvector-demo"
database_user="emb-admin"
database_password="Pumasunam1!"
#endregion

#%%
#region Video to FPS (Images)
def video_preprocessing(video):
    
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
#endregion

#region Video Intelligence for Transcription
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
        output_uri=f"gs://{video_transcript_annotations_gcs}/{file_name}.json",
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
#endregion

#region Transcription Summarization and Classification (text-bison)
def llm_sum_class(text):
    vertexai.init(project=project_id, location="us-central1")
    generation_model = TextGenerationModel.from_pretrained("text-bison")

    prompt_1 = """
      You are a sports analyst, provide a brief summary (no more than 15 words) of the following, try to enrich the data with public resources:
      """+text
    summarization = generation_model.predict(
            prompt_1, temperature=0.4, max_output_tokens=1024, top_k=40, top_p=0.8
        ).text
    prompt_2 = f'''Multi-choice problem: What is the category of the following?

    Text: Scores off bench Vela scored one goal to go with one shot 
    The answer is: MLS

    Text: Up a man, Philadelphia managed to find a go-ahead goal in the 124th minute
    The answer is: MLS

    Text: Michael Jordan made a jump shot with 6 seconds left to give the Bulls a 99–98 lead.
    The answer is: NBA

    Text: the Nuggets escaped with a 94-89 win in Game 5 of the 2023 NBA Finals to claim their first championship
    The answer is: NBA

    Text: Dallas Cowboys wide receiver CeeDee Lamb makes a toe-tapping touchdown catch
    The answer is: NFL

    Text:  {summarization}
    The answer is:
    '''
    classification = generation_model.predict(
            prompt_2, temperature=0.4, max_output_tokens=1024, top_k=40, top_p=0.8
        ).text
    print(summarization)
    return summarization, classification
#endregion

#region Storing Videos and FPS
def saving_to_gcs(file, video=True):
    client = storage.Client(project=project_id)
    if video:
        client.bucket(video_gcs_uri).blob(file).upload_from_filename(file)
        print("video saved on GCS job done")
    else:
        client.bucket(fps_gcs_uri).blob(file).upload_from_filename(file)
#endregion

#region Creating DB Structure
_index=[]
_type=[]
_emb=[]
_frame_link=[]
_video_link=[]
_summary=[]

list = [i for i in os.listdir() if re.search("\.mp4$", i)]

for video in list:
    saving_to_gcs(video)
    transcription = video_transcription(f"gs://{video_gcs_uri}/{video}")
    summarization, classification  = llm_sum_class(transcription)
    _dir, _prefix = video_preprocessing(video)
    _ = [os.path.join(_dir, _vid) for _vid in os.listdir(_dir)]
    for frame in _:       
        _index.append(_prefix)
        _type.append(classification)
        _summary.append(summarization)
        _emb.append(mm.get_embedding(image=frame).image_embedding)
        _frame_link.append(f"https://storage.googleapis.com/{fps_gcs_uri}/{frame.split('/')[-1]}")
        _video_link.append(f"https://storage.googleapis.com/{video_gcs_uri}/{video}")
        saving_to_gcs(frame.split('/')[-1], video=False)

df = pd.DataFrame({
    "index": _index,
    "sports_type": _type,
    "summary": _summary,
    "frame_link": _frame_link,
    "video_link": _video_link,
    "embedding": _emb
})
#endregion     

#%%
if "df" in locals():
    df.to_csv("emb2.csv", index=False)
else: df=pd.read_csv("emb2.csv")

#%%
#region Database Create/Insert
### Remember to create a cloud sql database first: gcloud sql databases create $database_name --instance pg15-pgvector-demo
vdb = vector_db(
    project_id=project_id,
    region=region,
    instance_name=instance_name,
    database_user=database_user,
    database_password=database_password
)
cdb = await vdb.create_database(database_name)
await vdb.insert_item(df)
#endregion
# %%
#await vdb.delete(database_name)

