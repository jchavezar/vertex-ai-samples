##### Global Variables and Libraries
#%%
import sys
import asyncio
import pandas as pd
import streamlit as st
from unidecode import unidecode
from utils import credentials, variables, database
from vertexai.preview.vision_models import MultiModalEmbeddingModel, Image

var={
    "project_id":variables.PROJECT_ID,
    "region":variables.REGION,
    "video_gcs_uri":variables.VIDEO_GCS_URI,
    "pickle_file_name":variables.PICKLE_FILE_NAME,
    "snippets_gcs_uri":variables.SNIPPETS_GCS_URI,
    "video_transcript_annotations_gcs":variables.VIDEO_TRANSCRIPT_ANNOTATIONS_GCS,
    "database_name":variables.DATABASE_NAME,
    "instance_name":variables.INSTANCE_NAME,
    "database_user":variables.DATABASE_USER,
    "database_password":credentials.DATABASE_PASSWORD,
    "linux":variables.LINUX,
}

database=database.Client(var)
mm=MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")

##### Website Fonts and Title
st.set_page_config(page_title="Search World!", page_icon="🐍", layout="wide")
st.title("Search Engine (PaLM Multimodal Embeddings)")

st.write("Search Engine is Contextual ask things like: Soccer player scoring")
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

icon("search")
selected = st.text_input("", "Machester City goal...")
button_clicked = st.button("OK")
text_search = selected
text_search = unidecode(text_search.lower())


##### Query from Database Using LLM and Match with Embeddings
if text_search:
    qe = mm.get_embeddings(contextual_text=text_search).text_embedding
    matches = asyncio.run(database.query(qe))

    # Show the results for similar products that matched the user query.
    matches = pd.DataFrame(matches)
    st.write(matches)

##### Front End Search Engine (cards) using Streamlit
    N_cards_per_row = 3
    if text_search:
        for n_row, row in matches.reset_index().iterrows():
            i = n_row%N_cards_per_row
            if i==0:
                st.write("---")
                cols = st.columns(N_cards_per_row, gap="large")
            # draw the card
            with cols[n_row%N_cards_per_row]:
                st.markdown(f"class - **{row['class'].strip()}**")
                st.markdown(f"ai embeddings type - **{row['ai_type'].strip()}**")
                st.markdown(f"**{row['summary'].strip()}**")
                st.markdown(f"*{row['video_link'].strip()}*")
                link=row['frame_link']
                image_link=row["frame_link"]
                clickable_image = f'<a href="{link}" target="_blank"> <img src="{image_link}" style="width:100%;"> </a>'
                st.markdown("authors_html" + clickable_image, unsafe_allow_html=True)

    st.write(matches["similarity"])