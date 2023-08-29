import pandas as pd
from google.cloud import storage


class Client:
    def __init__(self, iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
    
    def saving_to_gcs(self, file, video=True):
        client = storage.Client(project=self.project_id)
        if video:
            client.bucket(self.video_gcs_uri).blob(file).upload_from_filename(file)
            print("video saved on GCS job done")
        else:
            if self.linux:
                client.bucket(self.snippets_gcs_uri).blob(file.split('/')[-1]).upload_from_filename(file)
            else:
                client.bucket(self.snippets_gcs_uri).blob(file.split('\\')[-1]).upload_from_filename(file)
                

