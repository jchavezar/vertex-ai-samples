##### Global Variables and Libraries
#%%
import pandas as pd
from langchain.embeddings import VertexAIEmbeddings
from google.cloud import aiplatform
from pgvector.asyncpg import register_vector
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import sys
sys.path.append("..")
from ai import multimodal as mm
import streamlit as st
from credentials import *
from unidecode import unidecode


##### Website Fonts and Title
st.set_page_config(page_title="Sports World!", page_icon="🐍", layout="wide")
st.title("Sports Search Engine Embeddings")

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
selected = st.text_input("", "Search...")
button_clicked = st.button("OK")
matches = []
text_search = selected
text_search = unidecode(text_search.lower())


##### Query from Database Using LLM and Match with Embeddings
if text_search:
    qe = mm.get_embedding(text=text_search).text_embedding
    async def main():
        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{database_user}",
                password=f"{database_password}",
                db=f"{database_name}",
            )

            await register_vector(conn)
            similarity_threshold = 0.001
            num_matches = 10

            # Find similar products to the query using cosine similarity search
            # over all vector embeddings. This new feature is provided by `pgvector`.
            results = await conn.fetch(
                """
                                WITH vector_matches AS (
                                  SELECT summary, frame_link, video_link, 1 - (embedding <=> $1) AS similarity
                                  FROM video_embeddings
                                  WHERE 1 - (embedding <=> $1) > $2
                                  ORDER BY similarity DESC
                                  LIMIT $3
                                )
                                SELECT * FROM vector_matches
                                """,
                qe,
                similarity_threshold,
                num_matches,
            )

            if len(results) == 0:
                raise Exception("Did not find any results. Adjust the query parameters.")

            for r in results:
                # Collect the description for all the matched similar toy products.
                matches.append(
                    {
                        "summary": r["summary"],
                        "frame_link": r["frame_link"],
                        "video_link": r["video_link"],
                        "similarity": r["similarity"]
                    }
                )

            await conn.close()

    # Run the SQL commands now.
    asyncio.run(main())  # type: ignore

    # Show the results for similar products that matched the user query.
    matches = pd.DataFrame(matches)
    matches.head(10)
    # %%
    #st.write(matches)


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
                #st.caption(f"{row['class'].strip()} ")
                st.markdown(f"**{row['summary'].strip()}**")
                st.markdown(f"*{row['video_link'].strip()}*")
                link=row['frame_link']
                image_link=row["frame_link"]
                clickable_image = f'<a href="{link}" target="_blank"> <img src="{image_link}" style="width:100%;"> </a>'
                st.markdown("authors_html" + clickable_image, unsafe_allow_html=True)

    st.write(matches["similarity"])
    #st.write(df["transcription"])