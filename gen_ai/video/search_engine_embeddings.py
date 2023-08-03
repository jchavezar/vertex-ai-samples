##### Global Variables and Libraries
#%%
import sys
import asyncio
import pandas as pd
import streamlit as st
from credentials import *
from ai import multimodal as mm
from unidecode import unidecode
from google_database import vector_db

##### Website Fonts and Title
st.set_page_config(page_title="Sports World!", page_icon="🐍", layout="wide")
st.title("NBA Search Engine (PaLM Multimodal Embeddings)")

st.write("Search Engine was built from 3 videos like: [\"5 Minutes Of The Best Warriors Moments This Season\"](https://www.youtube.com/watch?v=r_osdIa5hx8&pp=ygUUbmJhIGhpZ2hsaWdodHMgNSBtaW4%3D)")
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
selected = st.text_input("", "A player jumping to score...")
button_clicked = st.button("OK")
text_search = selected
text_search = unidecode(text_search.lower())


##### Query from Database Using LLM and Match with Embeddings
if text_search:
    qe = mm.get_embedding(text=text_search).text_embedding

    vdb = vector_db()
    matches = asyncio.run(vdb.query(qe, database_name="video-frame-emb-2"))  # type: ignore


    # Show the results for similar products that matched the user query.
    matches = pd.DataFrame(matches)
    matches.head(10)

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
                st.markdown(f"**{row['sports_type'].strip()}**")
                st.markdown(f"**{row['summary'].strip()}**")
                st.markdown(f"*{row['video_link'].strip()}*")
                link=row['frame_link']
                image_link=row["frame_link"]
                clickable_image = f'<a href="{link}" target="_blank"> <img src="{image_link}" style="width:100%;"> </a>'
                st.markdown("authors_html" + clickable_image, unsafe_allow_html=True)

    st.write(matches["similarity"])