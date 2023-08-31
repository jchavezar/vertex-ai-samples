#%%
#region Libraries
import sys
sys.path.append('utils')
import sockcop_vertexai
import pandas as pd
import streamlit as st

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
st.divider()

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