#%%
import vertexai
import pandas as pd
import streamlit as st
from google.cloud import discoveryengine
from google.protobuf.json_format import MessageToDict
from vertexai.language_models import TextGenerationModel

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "financial-docs_1695748800641"
}

st.title('Financial Brain')
st.image("images/rag.png")

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
    parameters = {
        "max_output_tokens": 256,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained(model)
    response = model.predict(
        f"""you are a financial analyst from the following context respond the prompt below:

    context: {context}
    prompt: {prompt}

    provide details about your findings and list some potential recommendations over.""",
        **parameters
    )
    return response.text.replace("$","")

model = st.radio(
        "Choose a shipping method",
        ("text-bison@001", "text-bison")
    )

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What was the earning for Alphabet during 2023?')
  submitted = st.form_submit_button('Submit')
  if submitted:
      context = vertex_search(text)
      st.info(google_llm(text, context, model))


# %%

