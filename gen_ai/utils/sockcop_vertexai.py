#%%
#region Libraries
import re
import ast
import json
import vertexai
import pandas as pd
from vertexai.language_models import TextGenerationModel, ChatModel, CodeGenerationModel
from typing import List
from google.cloud import discoveryengine, bigquery
from google.protobuf.json_format import MessageToDict
#endregion

class Client:
    def __init__(self,iterable=(), **kwargs) -> None:
        self.__dict__.update(iterable, **kwargs)
        
        vertexai.init(project=self.project, location=self.region)

    #region EnterpriseSearch
    def search(self, prompt) -> List[discoveryengine.SearchResponse.SearchResult]:
        # Create a client
        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=self.project,
            location=self.location,
            data_store=self.datastore,
            serving_config="default_config",
        )
        print(serving_config)
        request = discoveryengine.SearchRequest(
            serving_config=serving_config, query=prompt, page_size=5)

        response = client.search(request)

        col=list(set([key for res in response.results for key in MessageToDict(res.document._pb)["structData"].keys()]))
        _res=[MessageToDict(_.document._pb)["structData"] for _ in response.results]
        for c in col:
            for num,res in enumerate(_res):
                if c not in res.keys():
                    _res[num][c]="None"

        df=pd.DataFrame(_res)

        return df
    #endregion
    
    #region Text LLM
    def text_bison(self, prompt, parameters="", model="text-bison", entities=True):
        if parameters == "":
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40
                }
        model = TextGenerationModel.from_pretrained(model)
        response = model.predict(prompt,
            **parameters
        )
        if entities:
            response = ast.literal_eval(re.findall(r"\[.*\]",response.text.strip())[0])
        else: response = response.text.replace("$", "\$")
        return response
    #endregion
    
    #region Chat LLM
    def chat_bison(self, prompt, context="", parameters="", model="chat-bison@001"):
        if parameters == "":
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40
                }
        print(context)
        chat_model = ChatModel.from_pretrained(model)

        chat = chat_model.start_chat(
            context=f'''You are a very friendly and funny chat, use the following data as context and historic information for your interactions: {context}

        Additional context: 
        - try to ask friendly questions to gather more information
        - When someone ask for demos give the following links: for Image QnA video: https://genai.sonrobots.net/Image_QnA_[vision], for Movies QnA using Enterprise Search: https://genai.sonrobots.net/Movies_QnA_[Enterprise_Search], for Analytics: https://genai.sonrobots.net/Analytics_[BigQuery]
        - Do not repeat questions under any circumstances.
        ''',
        )
        response = chat.send_message(prompt, **parameters)
        return response.text
    #endregion
    
    #region Code LLM    
    def code_bison(self, prompt, parameters="", model="code-bison@001", top_k=1000000):
        schema_columns=[i.column_name for i in bigquery.Client(project=self.project).query(f"SELECT column_name FROM `{self.project}`.{self.dataset}.INFORMATION_SCHEMA.COLUMNS WHERE table_name='{self.table}'").result()]

        if parameters == "":
            parameters = {
                "max_output_tokens": 1024,
                "temperature": 0.2,
            }
        model = CodeGenerationModel.from_pretrained(model)
        response = model.predict(
            prefix = f"""You are a GoogleSQL expert. Given an input question, first create a syntactically correct GoogleSQL query to run. This will be the SQLQuery. Then look at the results of the query. This will be SQLResults. Finally return the answer to the input question.
        Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per GoogleSQL. You can order the results to return the most informative data in the database.
        When running SQLQuery across BigQuery you must only include BigQuery SQL code from SQLQuery.
        Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
        Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
        
        Match the <prompt> below to this coulmn name schema: {schema_columns}
        
        Use the following project {self.project}, dataset {self.dataset} and {self.table} to create the query
        
        Question: {prompt}
        
        Output: 'SQL Query to Run':
        """,
                **parameters
            )
        res=re.sub('```', "", response.text.replace("SQLQuery:", "").replace("sql", ""))

        df=bigquery.Client(project=self.project).query(res).to_dataframe()
    
        return res, df
    #endregion