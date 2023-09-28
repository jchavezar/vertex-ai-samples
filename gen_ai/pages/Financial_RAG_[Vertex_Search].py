#%%
import sys
import vertexai
import pandas as pd
import streamlit as st
from google.cloud import discoveryengine
from google.protobuf.json_format import MessageToDict
from vertexai.preview.language_models import TextGenerationModel

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "financial-docs_1695748800641"
}

st.title('Retrieval Augmented Generation (RAG) | Vertex Search')
st.image("images/rag_vertexsearch.png")

settings = ["text-bison", "text-bison@001", "text-bison-32k"]

def reset_value():
    st.session_state.numk = 0

#region Model Settings
model = st.sidebar.selectbox("Choose a text model", settings)

temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.2) 
if model == "text-bison" or model == "text-bison@001":
        token_limit = st.sidebar.select_slider("Token Limit", range(1, 1025), value=256)
else:token_limit = st.sidebar.select_slider("Token Limit", range(1,8193), value=1024)
top_k = st.sidebar.select_slider("Top-K", range(1, 41), value=40)
top_p = st.sidebar.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.8) 
    
parameters =  {
    "temperature": temperature,
    "max_output_tokens": token_limit,
    "top_p": top_p,
    "top_k": top_k
    }

st.sidebar.button("Reset", on_click=reset_value)
#endregion

client = discoveryengine.SearchServiceClient()
serving_config = client.serving_config_path(
    project=variables["project"],
    location=variables["location"],
    data_store=variables["datastore"],
    serving_config="default_config",
    )

def vertex_search(prompt):
    request = discoveryengine.SearchRequest(
        serving_config=serving_config, query=prompt, page_size=10)

    response = client.search(request)

    # %%
    documents = [MessageToDict(i.document._pb) for i in response.results]
    links = ["https://storage.mtls.cloud.google.com"+"/".join(i["derivedStructData"]["link"].split("/")[1:]) for i in documents]
    context = [ans["content"] for i in documents for ans in i["derivedStructData"]["extractive_answers"]]
    pages = [ans["pageNumber"] for i in documents for ans in i["derivedStructData"]["extractive_answers"]]

    context = {
        "context": context,
        "links" : links,
        "page_number": pages
        }

    st.markdown("**Context extracted from Vertex Search:**")
    st.dataframe(pd.DataFrame(context))
    
    return context

def google_llm(prompt, context, model):
    vertexai.init(project="vtxdemos", location="us-central1")
    model = TextGenerationModel.from_pretrained(model)
    response = model.predict(
        f"""you are a financial analyst from the following context respond the prompt below:

    context: {context}
    prompt: {prompt}

    provide details about your findings and list some potential recommendations over.
    
    if the prompt asks for analytics or financial summary, bring it in json format: {{'company': \<company\>, 'fiscal year': \<fiscal year\>, .. }}
    
    """,
        **parameters
    )
    return response.text.replace("$","")

#model = st.radio(
#        "Choose a shipping method",
#        ("text-bison@001", "text-bison")
#    )

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What was the earning for Alphabet during 2023?')
  submitted = st.form_submit_button('Submit')
  if submitted:
      context = vertex_search(text)
      st.info(google_llm(text, context, model))


# %%

