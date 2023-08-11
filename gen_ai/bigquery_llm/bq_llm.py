#%%
import re
import os
import pandas as pd
import streamlit as st
from google.cloud import bigquery, aiplatform
from vertexai.language_models import TextGenerationModel
from vertexai.language_models import CodeGenerationModel

project="vtxdemos"
dataset="custom"
table="delo"

parameters = {
    "temperature": 0.2,
    "max_output_tokens": 1024
}

def llm_code_gen(
        prompt,
        project=project, 
        dataset=dataset, 
        table=table,
        parameters=parameters):
    aiplatform.init(project="vtxdemos", location="us-central1")
    
    model = CodeGenerationModel.from_pretrained("code-bison@001")
    response = model.predict(
        prefix = f"""Context:
    You are a GoogleSQL expert. Given an input question, first create a syntactically correct GoogleSQL query to run, then look at the results of the query and return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most 2000000 results using the LIMIT clause as per GoogleSQL. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question.
    Try to match words with similar column names. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Replace default grouped column names like f0 to something new to identify the new column. Interpert zero or non value as 0
    
    Instructions
    1. Generate the SQL query for BigQuery by using project {project}, dataset {dataset} and table {table} from the following task:
    {prompt}

    Output: 'SQL Query to Run'""",
        **parameters
    )
    st.write(response.text)

    return response.text

prompt=st.text_input(label="Ask me something?")
#prompt="the EAC_Revenue per partner region"

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
    from the following {df}""",
    **parameters
    )
    
    st.write(f"A though from our analyst is: {response.text}")