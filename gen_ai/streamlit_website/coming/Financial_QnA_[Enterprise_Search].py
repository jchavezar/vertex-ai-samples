#%%
#region Libraries
import sys
sys.path.append('utils')
import sockcop_vertexai
import pandas as pd
import streamlit as st
from utils.k import *
#endregion

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "finance_1695494677668"
}

client = sockcop_vertexai.Client(variables)

st.title("QnA for Finance")
st.text("")
st.text("")
#st.image("images/movies_es.png")
st.divider()

prompt = st.text_input("Enter your question here 👇")

if prompt:
    

    df = client.search(prompt, web_type=True)
    st.dataframe(df)

    #region LLM Text Bison to get Insights from Vertex Search Results
    insights = client.text_bison(
        f"""Use the following dataset as knowledge base/context: 
        {df.to_json(orient="records")}

        {prompt}

        """, entities=False)
    st.write(insights)
    #endregion

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
        }
    </style>
    """,
    unsafe_allow_html=True,
)