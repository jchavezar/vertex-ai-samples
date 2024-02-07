import re
import sys
import numpy as np
from utils.k import *
import streamlit as st
from google.cloud import bigquery
from utils import sockcop_vertexai
from utils.links_references import *

variables={
    "project":"vtxdemos",
    "region": "us-central1",
    "dataset": "public",
    "table": "citibike_stations"
}

def app(model_text, parameters_text, model_code, parameters_code):
    
    max_results = 1000000
    project = variables["project"]
    dataset = variables["dataset"]
    table = variables["table"]
    
    bq_client = bigquery.Client(project=project)
    
    source_df = bq_client.query(f"SELECT * FROM `{dataset}.{table}` LIMIT 5").to_dataframe()
    client = sockcop_vertexai.Client(variables)
    
    st.title("Analytics Code-b and BQ")
    st.image("images/analytics.png")
    st.markdown(f""" :green[repo:] [![Repo]({github_icon})]({analytics_bq})""")
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
        
    st.write("**Citibike Stations Datastore: **")
    st.dataframe(source_df)
    
    schema_columns=[i.column_name for i in bq_client.query(f"SELECT column_name FROM {project}.{dataset}.INFORMATION_SCHEMA.COLUMNS WHERE table_name='{table}'").result()]
    
    prompt = st.text_input("Ask something about citibike dataset 👇", value="Show me the max capacity by grouping per latitude and longitude")
    prompt_template = f"""You are a GoogleSQL expert. Given an input question, first create a syntactically correct GoogleSQL query to run. This will be the SQLQuery. Then look at the results of the query. This will be SQLResults. Finally return the answer to the input question.
        - Unless the user specifies in the question a specific number of examples to obtain, query for at most {max_results} results using the LIMIT clause as per GoogleSQL. You can order the results to return the most informative data in the database.
        - When running SQLQuery across BigQuery you must only include BigQuery SQL code from SQLQuery.
        - Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
        - Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        - Do not generate fake responses, only respond with SQL query code.
        - Do not add unnecesary backticks.
        
        Match the <prompt> below to this column name schema: {schema_columns}
        
        Use the following project {project}, dataset {dataset} and {table} to create the query
        
        Question: {prompt}
        
        
        Output: 'SQL Query (only) to Run':
        """
    
    
    re1 = client.llm2(prompt_template, model=model_code, parameters=parameters_code)
    res = re.sub('```', "", re1.replace("SQLQuery:", "").replace("sql", ""))

    st.write("**Query From code-bison@002:**")
    st.write(re1)
    
    st.write("**Using Query Against BigQuery API:**")
    df = bq_client.query(res).to_dataframe()
    
    st.write("**Response Table:**")
    st.dataframe(df)
    
    object_columns = df.select_dtypes(include='object').columns.to_list()
    num_columns = df.select_dtypes(include='int64').columns.to_list()
    num_lat_long = df.select_dtypes(include='float64').columns.to_list()
    if len(object_columns) != 0 and len(num_columns) != 0:
        st.write("**Bar Chart**")
        st.bar_chart(df, x=object_columns[0], y=num_columns[0])
    
    if len(num_lat_long) != 0:
        df["color"]=np.random.rand(df.shape[0], 4).tolist()
        st.write("**Data Map**")
        st.map(df, latitude="latitude", longitude="longitude", size=num_columns[0], color="color")
    
    template_prompt = f"from the context enclosed by backticks ```{df.iloc[:10,:].to_json()}``` give me a detailed summary"
    
    re2 = client.llm2(template_prompt, model=model_text, parameters=parameters_text)
    
    st.write(f"**Summarization from Text Large Language Model: {model_text}:**")
    st.write(re2)