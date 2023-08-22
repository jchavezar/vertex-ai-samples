#%%
#region Libraries
import pandas as pd
import streamlit as st
from utils.gen_app import ES
from google.cloud import discoveryengine_v1beta
#endregion

#region Variables
datastore_id="news_1687453492092"
#endregion

#region ES+text-bison
prompt=st.text_input(
    label="Query the News", 
    value="News about Messi")
es = ES(data_store_id="news_1687453492092", prompt=prompt)
snippets,urls=es.search()
st.dataframe(pd.DataFrame({"snippets":snippets,"urls":urls}))
#endregion

#region ES+text-ai
summ=es.summarization()

if summ:
    st.write(f"**New Article/Summary:** {summ}")

# %%
