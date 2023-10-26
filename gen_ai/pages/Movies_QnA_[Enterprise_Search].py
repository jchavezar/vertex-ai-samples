#%%
#region Libraries
import sys
sys.path.append('utils')
import sockcop_vertexai
import pandas as pd
import streamlit as st
from k import *
#endregion

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "kaggle-movies_1692703558099"
}

client = sockcop_vertexai.Client(variables)

st.title("QnA for Movies")
st.text("")
st.text("")
st.image("images/movies_es.png")
st.markdown("[github repo](https://github.com/jchavezar/vertex-ai-samples/tree/main/gen_ai/pages/Movies_QnA_[Enterprise_Search].py)")
st.divider()
with st.sidebar:
    st.markdown(
        """
        ---
        Follow me on:

        

        ldap → [@jesusarguelles](https://moma.corp.google.com/person/jesusarguelles)


        GitHub → [jchavezar](https://github.com/jchavezar)
        
        LinkedIn → [Jesus Chavez](https://www.linkedin.com/in/jchavezar)
        
        Medium -> [jchavezar](https://medium.com/@jchavezar)
        """
    )
    
prompt = st.text_input("Enter some text 👇", value="Who had more Revenue Godfather or The Matrix?")

if prompt:
    
    #region LLM Text Bison to Get Entities for Vertex Search
    movies = client.text_bison(
        f"""Your only task is extract entities, don't do anything else,
        Task: create a list of entities like movie's name or actor's name from the following text:

        {prompt}

        Output should be in the following python list format: ['entity1', 'entity2']

        """)
    #endregion
    
    st.write(f"**Entities Detected:** \n\n")
    st.write(movies)

    df = pd.concat([client.search(i) for i in movies], ignore_index=True)
    st.dataframe(df)
    #%%

    #region LLM Text Bison to get Insights from Vertex Search Results
    insights = client.text_bison(
        f"""Use the following dataset as context, for comparisons the higher the better: 
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