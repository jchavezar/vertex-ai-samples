# %%
#Vector DB Front End

#region Import Libraries
import base64
import asyncio
import vertexai
import asyncpg
import pandas as pd 
import streamlit as st
from utils.links_references import *
from utils.video import credentials
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from vertexai.preview.generative_models import GenerativeModel, Part
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel
#enregion

#region Set Values
project_id = "vtxdemos"
region = "us-central1"
instance_name = "pg15-pgvector-demo"
database_user = "emb-admin"
database_name = "text-emb-1"
database_password = credentials.DATABASE_PASSWORD

def app(model, parameters):
    vertexai.init(project=project_id, location=region)
    emb_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    #endregion

    st.title('Retrieval Augmented Generation (RAG) | docai+gecko-embeddings+text-bison')
    st.image("images/rag_emb.png")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({fin_rag_diy})""")

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

    with open("files/20230203_alphabet_10K_removed.pdf", "rb") as pdf_file:
        encoded_pdf = pdf_file.read()

    base64_pdf = base64.b64encode(encoded_pdf).decode("utf-8")
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    # %%
    #region query matching testing
    async def query(emb_prompt, database_name=""):
            matches=[]
            if database_name=="":
                 database_name=database_name
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
                                      SELECT page, text, embedding, 1 - (embedding <=> $1) AS similarity
                                      FROM text_embeddings
                                      WHERE 1 - (embedding <=> $1) > $2
                                      ORDER BY similarity DESC
                                      LIMIT $3
                                    )
                                    SELECT * FROM vector_matches
                                    """,
                    emb_prompt,
                    similarity_threshold,
                    num_matches,
                )

                if len(results) == 0:
                    raise Exception("Did not find any results. Adjust the query parameters.")

                for r in results:
                    # Collect the description for all the matched similar toy products.
                    matches.append(
                        {
                            "page": r["page"],
                            "text": r["text"],
                            #"embedding": r["embedding"],
                            "similarity": r["similarity"]
                        }
                    )

                await conn.close()
                return matches

    def google_llm(prompt, context, model, parameters):
        template_prompt = f"""you are a financial analyst from the following context respond the prompt below:

            context: {context}
            prompt: {prompt}

            provide details about your findings and list some potential recommendations over.
            provide how did you get your answers and your references.

            if the prompt asks for analytics or financial summary, bring it in json format: {{'company': \<company\>, 'fiscal year': \<fiscal year\>, .. }}

            """
        if model != "gemini-pro":
            model = TextGenerationModel.from_pretrained(model)
            response = model.predict(
                template_prompt,
                **parameters
            )
        else:
            model = GenerativeModel("gemini-pro")
            response = model.generate_content(
                [template_prompt],
                generation_config=parameters,)

        return response.text.replace("$","")
        return response.text.replace("$","")

    with st.form('my_form'):
        st.markdown("""
                    ***Sample questions...***
                     - What was the earning for Alphabet during 2022?
                     - How much office space reduction took place in 2023?
                     - How much did Google Search & other revenues increase from 2021 to 2022?""")
        text = st.text_area("***Enter text:***", "What was the earning for Alphabet during 2022?")
        submitted = st.form_submit_button('Submit')
        if submitted:
            emb_prompt = emb_model.get_embeddings([text])[0].values
            df =  pd.DataFrame(asyncio.run(query(emb_prompt=emb_prompt, database_name=database_name)))
            st.dataframe(df)
            st.write(f"Model id: {model}")
            st.info(google_llm(prompt=text, context=df.to_json(), model=model, parameters=parameters))