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
from google.cloud import discoveryengine
from google.protobuf.json_format import MessageToDict
#endregion

project_id = "vtxdemos"
location = "global"                    # Values: "global"
search_engine_id = "deloi_1692892735553"
serving_config_id = "default_config"          # Values: "default_config"
search_query = "partner"

#region EnterpriseSearch
def search(prompt) -> List[discoveryengine.SearchResponse.SearchResult]:
    # Create a client
    client = discoveryengine.SearchServiceClient()
    serving_config = client.serving_config_path(
        project=project_id,
        location=location,
        data_store=search_engine_id,
        serving_config=serving_config_id,
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
            {prompt}
            
            Output should be in the following python list format: ['entity1', 'entity2']
            
            """,
        **parameters
    )
    print(f"Response from Model: {response.text}")
    return ast.literal_eval(re.findall(r"\[.*\]",response.text.strip())[0])
#endregion

##region Front End (Streamlit)
prompt=st.text_input(label="Search")
if prompt:
    #movie=support_llm(prompt)
    st.write(search(prompt))
    #_df=[search(i) for i in movie]
    #_=pd.concat(_df, ignore_index=True)
    #st.dataframe(_)
    #response=llm(prompt, _)
    #st.write(response)
#endregion

# %%
