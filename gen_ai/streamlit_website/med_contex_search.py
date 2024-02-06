##### Global Variables and Libraries
#%%
from utils.k import *
import asyncio
import pandas as pd
import streamlit as st
from unidecode import unidecode
from utils.video import credentials, variables, database
from vertexai.preview.vision_models import MultiModalEmbeddingModel

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

def app():
    db=database.Client(var)
    mm = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")

    #region Website Fonts and Title
    st.title("Video Search Engine (PaLM Multimodal Embeddings) 🐍")
    st.markdown("Query examples:")
    st.markdown("""
                - [eng] Show me Empire State building videos
                - [spa] Recorrido por la ciudad de Mexico
                - [eng] Ferrari car drifting
                - [eng] Dak Prescott running!
                - [eng] Nikola Jokic playing
                - [spa] Fanaticos celebrando con los pumas
                """)
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

    st.write("Search Engine is Contextual ask things like: Soccer player scoring")
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.markdown("[github repo](https://github.com/jchavezar/vertex-ai-samples/tree/main/gen_ai/video)", unsafe_allow_html=True)

    def remote_css(url):
        st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    

    def icon(icon_name):
        st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

    local_css("utils/video/style.css")
    remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

    icon("search")
    selected = st.text_input("", "Messi playing for Miami FC...")
    button_clicked = st.button("OK")
    text_search = selected
    text_search = unidecode(text_search.lower())
    #endregion

    #region Query from Database Using LLM and Match with Embeddings
    if text_search:
        qe = mm.get_embeddings(contextual_text=text_search).text_embedding
        matches = asyncio.run(db.query(qe))

        # Show the results for similar products that matched the user query.
        matches = pd.DataFrame(matches)

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

        st.write(matches)
        st.write(matches["similarity"])
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