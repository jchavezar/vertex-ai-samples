import sys
sys.path.append("utils")
import numpy as np
import sockcop_vertexai
import streamlit as st
from google.cloud import bigquery
from k import *

variables={
    "project":"vtxdemos",
    "region": "us-central1",
    "dataset": "public",
    "table": "citibike_stations"
}

settings = ["code-bison@002", "code-bison-32k@002", "text-bison@002", "text-bison-32k@002", "gemini-pro"]
model = st.sidebar.selectbox("Choose a text model", settings)

temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.2) 
if model == "code-bison@002" or model == "text-bison@002":
        token_limit = st.sidebar.select_slider("Token Limit", range(1, 2049), value=1024)
else: token_limit = st.sidebar.select_slider("Token Limit", range(1,8193), value=2048)

if "code" not in model:
    top_k = st.sidebar.select_slider("Top-K", range(1, 41), value=40)
    top_p = st.sidebar.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.8)
    parameters = {"temperature": temperature, "max_output_tokens": token_limit, "top_p": top_p, "top_k": top_k}
    
else: parameters = {"temperature": temperature, "max_output_tokens": token_limit} 

source_df = bigquery.Client(project=variables["project"]).query(f"SELECT * FROM `{variables['dataset']}.{variables['table']}` LIMIT 5").to_dataframe()
client = sockcop_vertexai.Client(variables)

st.title("Analytics Code-b and BQ")
st.image("images/analytics.png")
with st.sidebar:
    st.markdown(
        """
        Follow me on:

        ldap → [@jesusarguelles](https://moma.corp.google.com/person/jesusarguelles)

        GitHub → [jchavezar](https://github.com/jchavezar)
        
        LinkedIn → [Jesus Chavez](https://www.linkedin.com/in/jchavezar)
        
        Medium -> [jchavezar](https://medium.com/@jchavezar)
        """
    )
    
st.write("**Citibike Stations Datastore: **")
st.dataframe(source_df)

prompt = st.text_input("Ask something about citibike dataset 👇", value="Show me the max capacity by grouping per latitude and longitude")
re1 = client.code_bison(prompt, model=model, parameters=parameters)

st.write("**Query From code-bison@002:**")
st.write(re1)

st.write("**Using Query Against BigQuery API:**")
df=bigquery.Client(project=variables["project"]).query(re1).to_dataframe()

st.write("**Response Table:**")
st.dataframe(df)

object_columns = df.select_dtypes(include='object').columns.to_list()
num_columns = df.select_dtypes(include='int64').columns.to_list()
num_lat_long = df.select_dtypes(include='float64').columns.to_list()
if len(object_columns) != 0 and len(num_columns) != 0:
    st.write("**Bar Chart**")
    st.bar_chart(df, x=object_columns[0], y=num_columns[0])

if len(num_lat_long) != 0:
    df["color"]=np.random.rand(df.shape[0], 4).tolist()
    st.write("**Data Map**")
    st.map(df, latitude="latitude", longitude="longitude", size=num_columns[0], color="color")
    
re2, mod = client.llm(prompt, df.to_json(), model=model, parameters=parameters)
st.write(f"**Summarization from Text Large Language Model: {mod}:**")
st.write(re2)
    
button = f'''<script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
<df-messenger
  agent-id="{dialogflow_id}"
  language-code="en">
  <df-messenger-chat-bubble
   chat-title="infobot"
   bot-writing-text="..."
   placeholder-text="Tell me something!">
  </df-messenger-chat-bubble>
</df-messenger>
<style>
  df-messenger {{
    z-index: 999;
    position: fixed;
    bottom: 16px;
    right: 16px;
  }}
</style>'''

st.components.v1.html(button, height=700, width=350)

st.markdown(
    """
    <style>
        iframe[width="350"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
    </style>
    """,
    unsafe_allow_html=True,
)