import io
import time
import vertexai
import pandas as pd
from typing import Any
import streamlit as st
from google.cloud import bigquery
from pdf2image import convert_from_path, convert_from_bytes
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold


class Client:
    # noinspection PyTypeChecker
    def __init__(self, model: str, project_id: str, bq_dataset: str, bq_connection_id: str, bq_embedding_model: str):
        self.model = model
        self.project_id = project_id
        self.dataset = bq_dataset
        self.bq_connection_id = bq_connection_id
        self.bq_embedding_model = bq_embedding_model
        self.bq_client = bigquery.Client(project=self.project_id)
        self.extraction_model = GenerativeModel(self.model)
        vertexai.init(project=self.project_id)

    def preprocess(self, filename) -> pd.DataFrame:
        chunk_number = 1
        chunked_text_dict = {}
        page_number = []
        chunk_number_value = []
        chunk_text = []
        character_limit = 500
        overlap = 60
        q = 1
        if type(filename) == str:
            images = convert_from_path(filename)
        else:
            images = convert_from_bytes(filename.getvalue())

        st.info(":blue[Extracting Text from document, please wait...]")
        start = time.time()
        for p, image in enumerate(images):
            start_extraction = time.time()
            response = self.extraction(image)
            st.info(f":green[Extraction from page {p+1} using Gemini 1.5; done in {time.time()-start_extraction:.2f} seconds]")
            for i in range(0, len(response), character_limit - overlap):
                end_index = min(i + character_limit, len(response))
                chunk = response[i:end_index]
                chunked_text_dict[chunk_number] = chunk.encode("ascii", "ignore").decode(
                    "utf-8", "ignore"
                )
                page_number.append(f"page_{p + 1}")
                chunk_number_value.append(f"chunk_{chunk_number}")
                chunk_text.append(chunked_text_dict[chunk_number])
                chunk_number += 1

            q += 1
            elapsed_time = time.time() - start

            if q == 6 and elapsed_time < 60:
                time.sleep(60 - elapsed_time)
                q = 1
                start = time.time()

        df = pd.DataFrame(
            {
                "page_number": page_number,
                "chunk_number": chunk_number_value,
                "chunk_text": chunk_text,
            }
        )

        # Vector Database using BigQuery
        # noinspection PyTypeChecker
        client = bigquery.Client(project=self.project_id)
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = client.load_table_from_dataframe(
            df, f"{self.dataset}.taxes", job_config=job_config
        )
        job.result()

        # Create Embeddings Model
        sql_query = f"""
        CREATE OR REPLACE MODEL `{self.dataset}.embedding_model`
          REMOTE WITH CONNECTION `projects/{self.project_id}/locations/us/connections/{self.bq_connection_id}`
          OPTIONS (ENDPOINT = 'textembedding-gecko@003');
        """
        job = client.query(sql_query)
        job.result()

        # Create Embeddings Table
        sql_query = f"""
        CREATE OR REPLACE TABLE `{self.dataset}.taxes_embeddings` AS
        SELECT * FROM ML.GENERATE_EMBEDDING(
          MODEL `{self.dataset}.{self.bq_embedding_model}`,
          (
            SELECT *, chunk_text AS content
            FROM `{self.dataset}.taxes`
          )
        )
        """
        job = client.query(sql_query)
        job.result()
        return df

    def extraction(self, image):
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 0,
            "top_p": 0.55,
        }

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }

        # Keeping Image bytes in-memory
        images_bytesio = io.BytesIO()
        image.save(images_bytesio, "PNG")
        image1 = Part.from_data(
            mime_type="image/png",
            data=images_bytesio.getvalue(),
        )

        text1 = """You are a tax agent analyst, so your answer needs to be very accurate (100%), 
        from the document extract all the paragraphs, text, images, tables, checkboxes everything to get an 
        structured text as an output. 
        
        - consider checkboxes marked with a clear 'X' as checked (true). All other checkboxes, 
        including empty ones, ambiguous markings, or other symbols, should be treated as unchecked (false)
        - Do not miss any letter or word.
        - Do not make up any key value.
        """

        model = GenerativeModel(self.model)
        gemini_response = model.generate_content(
            [image1, text1],
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        images_bytesio.close()
        try:
            response = gemini_response.text
        except:
            response = "There is an error with the extraction"
            st.info(f":red[{response}]")
        return response

    def query(self, prompt: str) -> dict[str, Any]:
        # Query Search
        # noinspection SqlDialectInspection,PyStringFormat
        sql_query = """
            WITH taxes_table AS (
              SELECT *
              FROM
                ML.GENERATE_EMBEDDING(
                  MODEL `{dataset}.{embedding_model}`,
                  (
                     SELECT page_number, chunk_number, content FROM {dataset}.taxes_embeddings
                  ),
                  STRUCT(TRUE AS flatten_json_output)
                )
            ),
            original_query AS (
              SELECT ml_generate_embedding_result
              FROM
                ML.GENERATE_EMBEDDING(
                  MODEL `{dataset}.{embedding_model}`,
                  (SELECT "{prompt}" AS content),
                  STRUCT(TRUE AS flatten_json_output)
                )
            )
            SELECT
              page_number,
              chunk_number,
              content,
              ML.DISTANCE(
                (SELECT ml_generate_embedding_result FROM original_query),
                ml_generate_embedding_result,
                'COSINE'
              ) AS distance_to_average_review
            FROM
              taxes_table
            ORDER BY distance_to_average_review
            LIMIT 10
            """.format(prompt=prompt, dataset=self.dataset, embedding_model=self.bq_embedding_model)
        time_to_query_start = time.time()
        extracted_df = self.bq_client.query(sql_query).to_dataframe()

        res = {}
        for index, row in extracted_df.iterrows():
            res[row["page_number"]+"_"+row["chunk_number"]] = row["content"]
        with st.expander("VDB Context From BigQuery"):
            st.write(res)
        st.info(f":blue[Query Elapsed Time {time.time()-time_to_query_start:.2f} seconds]")
        return res
