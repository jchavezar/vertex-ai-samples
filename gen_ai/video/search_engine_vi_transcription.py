##### Global Variables and Libraries
#%%
from unidecode import unidecode
import sqlalchemy
import pandas as pd
import streamlit as st
from google.cloud.sql.connector import Connector
from credentials import *

st.set_page_config(page_title="Sports World!", page_icon="🐍", layout="wide")
st.title("Sports Search Engine")


class_list = []
transcription_list = []
summary_list = []
video_link_list = []
snippet_link_list =[]


##### Reading info from Database Table to Match Query
connector = Connector()
def getconn():
    conn = connector.connect(
        f"{project_id}:{region}:{instance_name}",
        "pg8000",
        user=database_user,
        password=database_password,
        db=database_name
    )
    return conn

pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

with pool.connect() as db_conn:
    results = db_conn.execute(sqlalchemy.text("SELECT * FROM video_metadata")).fetchall()
    
    for i in results:
        class_list.append(list(i)[1])
        transcription_list.append(list(i)[0])
        summary_list.append(list(i)[2])
        video_link_list.append(list(i)[3])
        snippet_link_list.append(list(i)[4])
    print("Results: ", results[0])
connector.close()

_ = {
    "class":class_list,
    "transcription":transcription_list,
    "summary":summary_list,
    "video_link":video_link_list,
    "snippet_link":snippet_link_list
}
df = pd.DataFrame(_)
df_lower = df.copy()
df_lower.columns = [ unidecode(s.lower().strip()) for s in df_lower.columns]
for col in df_lower.columns:
    df_lower[col] = df_lower[col].apply(lambda x: unidecode(x.lower().strip()))


##### Seach Engine Front End Using Streamlit
# %%

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search videos by transcription", value="")
text_search = unidecode(text_search.lower())

# Filter the dataframe using masks
m1 = df_lower["transcription"].str.contains(text_search)
m2 = df_lower["summary"].str.contains(text_search)
df_search = df[m1 | m2]

# Show the cards
N_cards_per_row = 3
if text_search:
    for n_row, row in df_search.reset_index().iterrows():
        i = n_row%N_cards_per_row
        if i==0:
            st.write("---")
            cols = st.columns(N_cards_per_row, gap="large")
        # draw the card
        with cols[n_row%N_cards_per_row]:
            st.caption(f"{row['class'].strip()} ")
            st.markdown(f"**{row['summary'].strip()}**")
            st.markdown(f"*{row['video_link'].strip()}*")
            link=row['video_link']
            image_link=row["snippet_link"]
            clickable_image = f'<a href="{link}" target="_blank"> <img src="{image_link}" style="width:100%;"> </a>'
            st.markdown("authors_html" + clickable_image, unsafe_allow_html=True)
