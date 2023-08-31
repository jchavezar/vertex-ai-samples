#%%
#region Libraries
import re
import ast
import json
import vertexai
import pandas as pd
from vertexai.language_models import TextGenerationModel, ChatModel, InputOutputTextPair
from typing import List
from google.cloud import discoveryengine
from google.protobuf.json_format import MessageToDict
#endregion

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        
        vertexai.init(project=self.project, location=self.region)

    #region EnterpriseSearch
    def search(self, prompt) -> List[discoveryengine.SearchResponse.SearchResult]:
        # Create a client
        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=self.project,
            location=self.location,
            data_store=self.datastore,
            serving_config="default_config",
        )
        print(serving_config)
        request = discoveryengine.SearchRequest(
            serving_config=serving_config, query=prompt, page_size=5)

        response = client.search(request)

        col=list(set([key for res in response.results for key in MessageToDict(res.document._pb)["structData"].keys()]))
        _res=[MessageToDict(_.document._pb)["structData"] for _ in response.results]
        for c in col:
            for num,res in enumerate(_res):
                if c not in res.keys():
                    _res[num][c]="None"

        df=pd.DataFrame(_res)

        return df
    #endregion
    
    #region Text LLM
    def text_bison(self, prompt, parameters="", model="text-bison", entities=True):
        if parameters == "":
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40
                }
        model = TextGenerationModel.from_pretrained(model)
        response = model.predict(prompt,
            **parameters
        )
        if entities:
            response = ast.literal_eval(re.findall(r"\[.*\]",response.text.strip())[0])
        else: response = response.text.replace("$", "\$")
        return response
    #endregion
    
    
    #region Chat LLM
    def chat_bison(self, prompt, context="", parameters="", model="chat-bison@001"):
        if parameters == "":
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40
                }
        print(context)
        chat_model = ChatModel.from_pretrained(model)

        chat = chat_model.start_chat(
            context=f'''You are a very friendly and funny chat, use the following data as context and historic information for your interactions: {context}

        Additional context: 
        - try to ask friendly questions to gather more information
        - here you have some links that you might be ask for: for Image QnA video: http://34.29.151.13:8501/Image_QnA_[vision], for Movies QnA using Enterprise Search: http://34.29.151.13:8501/Movies_QnA_[Enterprise_Search]
        ''',
        )
        response = chat.send_message(prompt, **parameters)
        return response.text
    
