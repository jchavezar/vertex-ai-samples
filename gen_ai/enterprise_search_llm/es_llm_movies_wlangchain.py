#%%
#region Libraries
import re
import ast
import json
import vertexai
import pandas as pd
import streamlit as st
from vertexai.language_models import TextGenerationModel
from typing import Any, Mapping, List, Dict, Optional, Tuple, Sequence, Union
from google.cloud import discoveryengine_v1beta
from google.protobuf.json_format import MessageToDict
#endregion

#region EnterpriseSearch
def search(prompt) -> pd.DataFrame:
    search_client = discoveryengine_v1beta.SearchServiceClient()
    serving_config: str = search_client.serving_config_path(
            project="vtxdemos",
            location="global",
            data_store="kaggle-movies_1692703558099",
            serving_config="default_config",
            )
    _res=discoveryengine_v1beta.SearchServiceClient().search(discoveryengine_v1beta.SearchRequest(serving_config=serving_config, query=prompt))

    #Structured
    original_title=[]
    overview=[]
    revenue=[]
    popularity=[]
    production_companies=[]

    for i in _res.results:
        original_title.append(MessageToDict(i.document._pb)["structData"]["original_title"])
        overview.append(MessageToDict(i.document._pb)["structData"]["overview"])
        revenue.append(MessageToDict(i.document._pb)["structData"]["revenue"])
        popularity.append(MessageToDict(i.document._pb)["structData"]["popularity"])
        production_companies.append(MessageToDict(i.document._pb)["structData"]["production_companies"])
    return pd.DataFrame({"original_title": original_title, "overview": overview, "revenue": revenue, "popularity": popularity, "production_companies": production_companies})
#endregion

#region LLM
def llm(prompt, df):
    vertexai.init(project="vtxdemos", location="us-central1")
    parameters = {
            "max_output_tokens": 256,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison")
    response = model.predict(
            f"""Use the following dataset as context, for comparisons the higher the better: {df.to_json(orient="records")}
            
            {prompt}
            
            """,
        **parameters
    )
    print(f"Response from Model: {response.text}")
    return response.text
#endregion

#region Support LLM
def support_llm(prompt):
    vertexai.init(project="vtxdemos", location="us-central1")
    parameters = {
        "max_output_tokens": 256,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison")
    response = model.predict(
            f"""Your only task is extract entities, don't do anything else,
            Tasl: create a list of entities like movie's name or actor's name from the following text:
            {prompt}
            
            Output should be in the following format: ['entity1', 'entity2']
            
            """,
        **parameters
    )
    print(f"Response from Model: {response.text}")
    return ast.literal_eval(re.findall(r"\[.*\]",response.text.strip())[0])
#endregion

##region Front End (Streamlit)
prompt=st.text_input(label="Search")
if prompt:
    movie=support_llm(prompt)
    _df=[search(i) for i in movie]
    _=pd.concat(_df, ignore_index=True)
    st.dataframe(_)
    response=llm(prompt, _)
    st.write(response)
#endregion

# %%
