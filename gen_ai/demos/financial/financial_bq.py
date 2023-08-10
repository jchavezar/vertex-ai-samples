# %%
#region Import Libraries
import ast
import time
import openai
import vertexai
import pandas as pd
from google.cloud import bigquery
from datasets import load_dataset
from vertexai.language_models import TextGenerationModel
from credentials import *
#endregion

#region Variables
project_id="vtxdemos"
region="us-central1"
#endregion

#region Preparing data
# Reading data from csv file
dataset = load_dataset("financial_phrasebank", name='sentences_allagree')
dataset_dict = {"input_text": dataset["train"][:]["sentence"], "output_text": dataset["train"][:]["label"]}
df=pd.DataFrame(dataset_dict)
mymap = {0:"negative", 1:"neutral", 2:"positive"}
df=df.applymap(lambda x: mymap.get(x) if x in mymap else x)

# - Spliting data (prompt engineering + prediction)
label_prompt=[values for values in df.iloc[:5,:].reset_index()["output_text"]]
text_prompt=[values for values in df.iloc[:5,:].reset_index()["input_text"]]
df_to_predict=df.iloc[5:100,:].reset_index(drop=True)

# - Store non-prompt used data in BQ
job_config=bigquery.LoadJobConfig()
job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
bigquery.Client(project="vtxdemos").load_table_from_dataframe(df_to_predict, destination="llm_outputs.llm_financial_input_ev", job_config=job_config)
#endregion

# %%
#region LLM (text-bison) To Detect Spam
def gcp_sentiment_analysis(text_input):
    vertexai.init(project=project_id, location=region)
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison")
    response = model.predict(
        f"""your task is to classify text into negative, neutral and positive, the output should have the following structure:

    Output python dictionary: {{\"<input_text>\": \"<negative/neutral/positive>\"}}

    input: {text_prompt[0]}
    output: {{\"{text_prompt[0]}\": \"{label_prompt[0]}\"}}

    input: {text_prompt[1]}
    output: {{\"{text_prompt[1]}\": \"{label_prompt[1]}\"}}

    input: {text_prompt[2]}
    output: {{\"{text_prompt[2]}\": \"{label_prompt[2]}\"}}

    input: {text_prompt[3]}
    output: {{\"{text_prompt[3]}\": \"{label_prompt[3]}\"}}

    input: {text_prompt[4]}
    output: {{\"{text_prompt[4]}\": \"{label_prompt[4]}\"}}

    input: {text_input}
    output: 

    """,
        **parameters
    )
    #print(text_input)
    return ast.literal_eval(response.text)
#endregion

#region openAI To Detect Spam
openai.api_key=api_key
def open_ai_analysis(text_input, model="gpt-3.5-turbo"):
    prompt=f"""your task is to classify text into negative, neutral and positive, the output should have the following structure:
        
        Output python dictionary: {{\"<input_text>\": \"<negative/neutral/positive>\"}}

        input: {text_prompt[0]}
        output: {{\"{text_prompt[0]}\": \"{label_prompt[0]}\"}}

        input: {text_prompt[1]}
        output: {{\"{text_prompt[1]}\": \"{label_prompt[1]}\"}}

        input: {text_prompt[2]}
        output: {{\"{text_prompt[2]}\": \"{label_prompt[2]}\"}}

        input: {text_prompt[3]}
        output: {{\"{text_prompt[3]}\": \"{label_prompt[3]}\"}}

        input: {text_prompt[4]}
        output: {{\"{text_prompt[4]}\": \"{label_prompt[4]}\"}}

        input: {text_input}
        output: 
    """
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
        )
    return ast.literal_eval(response.choices[0].message["content"])
#endregion

# %%
#region Taking 15 examples for prediction [GCP]
text=[]
label=[]
end_time=0
for index, row in df_to_predict.iterrows():
    start_time = time.time()
    res=(gcp_sentiment_analysis(row["input_text"]))
    text.append(list(res.keys())[0])
    label.append(list(res.values())[0])
    print(index)
    print(res)
    print(time.time()-start_time)
    end_time+=(time.time()-start_time)
print(f"GCP Time: {end_time}")    
gcp_df=pd.DataFrame({"text": text, "label": label})
#endregion

#region Taking 15 examples for prediction [OpenAI]
text=[]
label=[]
end_time=0
for index, row in df_to_predict.iterrows():
    start_time = time.time()
    res=(open_ai_analysis(row["input_text"]))
    text.append(list(res.keys())[0])
    label.append(list(res.values())[0])
    print(res)
    print(time.time()-start_time)
    end_time+=(time.time()-start_time)
print(f"OpenAI Time: {end_time}")  
open_ai_df=pd.DataFrame({"text": text, "label": label})
#endregion

# %%
#region Store predictions in BigQuery (DW)
# - GCP
client = bigquery.Client(project="vtxdemos")
table_id = "llm_outputs.gcp_llm_financial"
job_config = bigquery.LoadJobConfig(
    schema=[
        bigquery.SchemaField("text", "STRING"),
        bigquery.SchemaField("label", "STRING")
    ],
)
job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
job = client.load_table_from_dataframe(gcp_df, table_id, job_config=job_config)

# - Wait for the load job to complete.
job.result()

# - OpenAI
client = bigquery.Client(project="vtxdemos")
table_id = "llm_outputs.open_ai_llm_financial"
job_config = bigquery.LoadJobConfig(
    schema=[
        bigquery.SchemaField("text", "STRING"),
        bigquery.SchemaField("label", "STRING")
    ],
)
job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
job = client.load_table_from_dataframe(open_ai_df, table_id, job_config=job_config)

# - Wait for the load job to complete.
job.result()
#endregion

# %%
