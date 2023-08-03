#%%
##### Video Processing, Transcription Extraction
import cv2
import pandas
import numpy as np
from google.cloud import storage
from google.cloud import videointelligence as vi
from typing import Optional, Sequence, cast

client = storage.Client(project="vtxdemos")
bucket_name="vtxdemos-fb-videos"

def create_snippets(videos_list):

    for i in videos_list:
        x=i.split("/")[-1]
        client.bucket(bucket_name).blob(x).download_to_filename(f"./tmp/{x}")

        video = cv2.VideoCapture(f"./tmp/{x}")

        # Get the frame width and height
        frame_width = int(video.get(3))
        frame_height = int(video.get(4))

        # Create a blank image to store the snippet
        snippet = np.zeros((frame_height, frame_width, 3), dtype="uint8")

        # Get the current frame
        ret, frame = video.read()

        # If the frame was read successfully,
        # then write it to the snippet image
        snippet_name = f"{x.split('.')[0]}.jpg"
        if ret:
            cv2.imwrite(f"./tmp/{snippet_name}", frame)

        # Release the video capture object
        video.release()

        client.bucket("vtxdemos-fb-snippets").blob(snippet_name).upload_from_filename(f"./tmp/{snippet_name}")
    

def video_intelligence(video_uri, language_code, output_uri):
    video_client = vi.VideoIntelligenceServiceClient()
    features = [
        vi.Feature.SPEECH_TRANSCRIPTION,
    ]
    config = vi.SpeechTranscriptionConfig(
        language_code=language_code,
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True
    )
    context = vi.VideoContext(
        speech_transcription_config=config,
    )
    request = vi.AnnotateVideoRequest(
        input_uri=video_uri,
        output_uri=output_uri,
        features=features,
        video_context=context,
    )

    print(f'Processing video "{video_uri}"...')
    operation = video_client.annotate_video(request)
    response = cast(vi.AnnotateVideoResponse, operation.result())
    transcript = [n.transcript.strip() for i in response.annotation_results[0].speech_transcriptions for n in i.alternatives][:-2]
    transcript = ",".join(transcript)
    return transcript

##### Summarization and Classification using LLMs (text-bison)

def llm_sum_class(project, input_llm):
    import vertexai
    from vertexai.preview.language_models import TextGenerationModel

    vertexai.init(project=project, location="us-central1")
    generation_model = TextGenerationModel.from_pretrained("text-bison")

    prompt_1 = """
      You are a sports analyst, provide a brief summary (no more than 15 words) of the following, try to enrich the data with public resources:
      """+input_llm
    summarization = generation_model.predict(
            prompt_1, temperature=0.4, max_output_tokens=1024, top_k=40, top_p=0.8
        ).text
    prompt_2 = f'''Multi-choice problem: What is the category of the following?
    - NBA
    - MLS
    - NFL

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

def main():

    bucket = client.bucket(bucket_name)
    videos_list = [f"gs://{bucket_name}/{i.name}" for i in bucket.list_blobs()]

    project= "vtxdemos"
    #video_list=["gs://vtxdemos-fb-videos/heats_nuggets.mp4"]
    video_uri="gs://vtxdemos-fb-videos/heats_nuggets.mp4"
    file_name = video_uri.split('/')[-1].split('.'[0])
    language_code = "en-US"
    output_uri = f"gs://vtxdemos-fb-videos-json/{file_name}.json"

    create_snippets(videos_list)
    video_transcriptions = []
    video_link_list = []
    snippet_link_list = []
    for i in videos_list:
        video_transcriptions.append(video_intelligence(i, language_code, output_uri))
        video_link_list.append(f"https://storage.mtls.cloud.google.com/{i.split('/')[-2]}/{i.split('/')[-1]}")
        snippet_link_list.append(f"https://storage.mtls.cloud.google.com/vtxdemos-fb-snippets/{i.split('/')[-1].split('.')[0]}.jpg")
    
    summarization_list = []
    classification_list = []
    for i in video_transcriptions:
        summarization, classification = llm_sum_class(project, i)
        summarization_list.append(summarization)
        classification_list.append(classification)

    print(len(summarization_list))
    print(len(classification_list))
    print(len(video_link_list))
    print(len(snippet_link_list))
    #print(video_link_list)
    #print(snippet_link_list)

    _dict = {
        "class": classification_list,
        "transcription": video_transcriptions,
        "summary": summarization_list,
        "video_link": video_link_list,
        "snippet_link": snippet_link_list,
    }
    print(_dict)

    df = pandas.DataFrame(_dict)
    return df
df = main()
df.to_csv("backup.csv")


##### Loading items into SQL
#%%
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import pandas as pd
import numpy as np
from pgvector.asyncpg import register_vector
from credentials import *

df = pd.read_csv("backup_2.csv", index_col=False)
#%%
async def insert_item(df):
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )
        # Store all the generated embeddings back into the database.
        for index, row in df.iterrows():
            print(row["transcription"])
            await conn.execute(
                "INSERT INTO video_metadata (transcription, class, summary, video_link, snippet_link) VALUES ($1, $2, $3, $4, $5)",
                row["transcription"],
                row["class"],
                row["summary"],
                row["video_link"],
                row["snippet_link"],
            )
        x = await conn.fetch("SELECT * FROM video_metadata")
        for i in x:
           print(x)
        await conn.close()
await insert_item(df)


# %%
