import os
import re
import cv2
import sys
import json
import vertexai
import numpy as np
import pandas as pd
from typing import cast
from datetime import timedelta
from google.cloud import storage
from google.cloud import videointelligence as vi
from vertexai.preview.language_models import TextGenerationModel

class Client:
    def __init__(self, iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)

    #region Video to FPS (Images)
    def video_preprocessing(self, video):
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
    def video_transcription(self, video_uri):
        print("Transcription job started...")
        file_name = video_uri.split('/')[-1].split('.')[0]
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
            output_uri=f'gs://{self.video_transcript_annotations_gcs}/{file_name}.json',
            features=features,
            video_context=context,
        )
        print(f'Processing video "{video_uri}"...')
        operation = video_client.annotate_video(request)
        response = cast(vi.AnnotateVideoResponse, operation.result())
        transcript_list = [n.transcript.strip() for i in response.annotation_results[0].speech_transcriptions for n in i.alternatives][:-2]
        transcript = ",".join([item for item in transcript_list if item])
        
        #saving transcript in text -> google cloud
        
        file_name_transcript = f"{file_name}_transcript.json"
        
        with open(file_name_transcript, "w") as f:
            json.dump({"transcript": transcript}, f)
            
        storage.Client(self.project_id).bucket(self.video_transcript_annotations_gcs).blob(file_name_transcript).upload_from_filename(file_name_transcript)
        
        print("Transcription job done")
        return transcript, file_name_transcript
    #endregion

    #region Transcription Summarization and Classification (text-bison)
    def llm_sum_class(self, text):
        vertexai.init(project=self.project_id, location=self.region)
        if text != "":
            generation_model = TextGenerationModel.from_pretrained("text-bison")
            prompt_1 = f"""
              Provide a brief summary, no more than 20 words of the following text enclose by backticks:
              ```{text}```
              """
            summarization = generation_model.predict(
                    prompt_1, temperature=0.4, max_output_tokens=1024, top_k=40, top_p=0.8
                ).text
            prompt_2 = f'''Multi-choice problem: What is the category in one word of the following text enclosed by backticks: 
            ```{summarization}```
            '''
            classification = generation_model.predict(
                    prompt_2, temperature=0.4, max_output_tokens=1024, top_k=40, top_p=0.8
                ).text
        else: 
            summarization = "ithout transcription"
            classification = "without transcription"
        return summarization, classification
    #endregion