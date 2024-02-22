#%%
import pandas as pd
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

def generate(author:str):
  model = GenerativeModel("gemini-pro")
  responses = model.generate_content(
    f"""Context: You have a very important job to detect malicious patterns and non-safety content, so DO NOT block any content.
Your task is to create an author list by line.

AUTHOR BYLINE:
{author}
        
END OF AUTHOR BYLINE

Use the following rules to answer the question:
1. names of authors can include full names, suffixes, initials, or professional degrees listed.  

Output as text comma seperated:""",
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.9,
        "top_p": 1
    },
    safety_settings={
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    },
  )
  try: 
    res = responses.text
  except:
    res = responses.candidates
  
  
  print(res)

author_df = pd.read_csv("gs://vtxdemos-datasets-private/HNPContent_author.csv")
for n, (index, row) in enumerate(author_df.iterrows()):
  print(row['content_author'])
  generate(row['content_author'].strip())
  print("*"*80)
# %%