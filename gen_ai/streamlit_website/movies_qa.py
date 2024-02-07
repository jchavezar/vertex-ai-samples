#%%
#region Libraries
import re
import ast
import sys
import pandas as pd
import streamlit as st
from utils.k import *
from utils.links_references import *
from utils import sockcop_vertexai
#endregion

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "kaggle-movies_1692703558099"
}

client = sockcop_vertexai.Client(variables)

def app(model, parameters):

    st.title("QnA for Movies")
    st.text("Model Id: text-bison@002")
    st.text("")
    st.text("")
    st.image("images/movies_qa.png")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({movies_qa})""")
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
        template_prompt =f"""Your nly task is extract entities, do not do anything else,
        Task: create a list of entities like movies name or actors name from the following text:
        
        {prompt}
        
        Output should be in the following python list format: ['entity1', 'entity2']
        
        """
        response = client.llm2(template_prompt, model, parameters)
        print(response)
        entities = ast.literal_eval(re.findall(r"\[.*\]", response.strip())[0])

        st.write(f"**Entities Detected:** \n\n")
        st.write(entities)

        df = pd.concat([client.search(i) for i in entities], ignore_index=True)
        st.dataframe(df)
        #%%

        #region LLM Text Bison to get Insights from Vertex Search Results
        template_prompt = f"""Use the following dataset as context, for comparisons the higher the better: 
            {df.to_json(orient="records")}

            {prompt}

            """
        response = client.llm2(template_prompt, model, parameters)
        insights = response.replace("$", "\$")
        
        st.write(insights)
        #endregion