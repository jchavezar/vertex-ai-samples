import vertexai
from typing import cast
from google.cloud import videointelligence as vi
from vertexai.language_models import TextGenerationModel

class Client:
    def __init__(self, iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)

    def video_transcription(self, video_uri):
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
            output_uri=f"gs://{self.video_transcript_annotations_gcs}/{file_name}.json",
            features=features,
            video_context=context,
        )

        print(f'Processing video "{video_uri}"...')
        operation = video_client.annotate_video(request)
        response = cast(vi.AnnotateVideoResponse, operation.result())
        transcript_list = [n.transcript.strip() for i in response.annotation_results[0].speech_transcriptions for n in i.alternatives][:-2]
        transcript = ",".join([item for item in transcript_list if item])
        print("Transcription job done")
        return transcript, transcript_list
    
    def llm_sum_class(self, text):
        vertexai.init(project=self.project_id, location="us-central1")
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
        print(summarization)
        return summarization, classification