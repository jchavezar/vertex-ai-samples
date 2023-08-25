#%%
#region Libraries
import re
import os
import pandas as pd
import streamlit as st
from google.cloud import bigquery, aiplatform
from vertexai.language_models import TextGenerationModel
from vertexai.language_models import CodeGenerationModel
#endregion

#region Variables
project="vtxdemos"
dataset="custom"
table="delo"

parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.2,
}
schema_columns=[i.column_name for i in bigquery.Client().query("select column_name from `vtxdemos`.custom.INFORMATION_SCHEMA.COLUMNS where table_name='delo'").result()]
#endregion

#region Vertex AI LLM
def llm_code_gen(
        prompt,
        project=project, 
        dataset=dataset, 
        table=table,
        parameters=parameters,
        top_k="100000"
        ):
    aiplatform.init(project="vtxdemos", location="us-central1")
    
    model = CodeGenerationModel.from_pretrained("code-bison@001")
    response = model.predict(
        prefix = f"""You are a GoogleSQL expert. Given an input question, first create a syntactically correct GoogleSQL query to run. This will be the SQLQuery. Then look at the results of the query. This will be SQLResults. Finally return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per GoogleSQL. You can order the results to return the most informative data in the database.
    When running SQLQuery across BigQuery you must only include BigQuery SQL code from SQLQuery.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    
    Match the <prompt> below to this coulmn name schema: {schema_columns}
    
    Use the following project {project}, dataset {dataset} and {table} to create the query
    
    Question: {prompt}
    
    Output: 'SQL Query to Run':
    """,
            **parameters
        )
    
    res=response.text.replace("SQLQuery:", "")    
    st.write(res)

    return res
#endregion

#region Query
prompt=st.text_input(label="Ask me something?")

if prompt:
    re=re.sub('```', "" , llm_code_gen(prompt).replace("sql",""))
    df=bigquery.Client(project=project).query(re).to_dataframe()

    st.write(df)
    object_columns = df.select_dtypes(include='object').columns
    num_columns = df.select_dtypes(include='float64').columns

    st.bar_chart(df, x=object_columns[0], y=num_columns[0])


    model = TextGenerationModel.from_pretrained("text-bison@001")
    response=model.predict(f"""
    You are a business analytic and your job is to get insights, recommendations and a summary 
    from the following {df}
    """,
    **parameters
    )
    
    st.write(f"A though from our analyst is: {response.text}")
#endregion
# %%
