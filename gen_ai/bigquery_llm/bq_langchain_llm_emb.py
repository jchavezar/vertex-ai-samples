#%%
import vertexai
from utils.ai import LLM

vertexai.init(project="vtxdemos", location="us-central1")

## LLM Class definition
llm = LLM(
    bq_source="cloud-llm-preview4.sockcop_dataset.billing_latest", 
    text_model="text-bison@001",)


## Loading llm models and creating embeddings
text_llm, embeddings = llm.LoadModels()
df, nl_d, df_index = llm.LoadDatasetCreatingEmb()

## -------------------------------------------------------------------------- ##

## Prompting
#%%
def ask_question(question, max_results=5, threshold=0.5, df_index=df_index):
  # Based on the question, sarch for relevant articles
  similar_docs = df_index.vectorstore.similarity_search_with_score(question, llm=text_llm, k=max_results)
  filtered_docs = list(filter(lambda doc: doc[1] <= threshold, similar_docs))
  print(filtered_docs)
  context = "\n".join([doc.page_content for doc, score in filtered_docs])
  prompt = f"""
  context={context}
  Use the following pieces of context to answer the question at the end.

  Question: {question}
  Answer:
  """
  return text_llm(prompt)
# %%
ask_question("what is the consumption for AlloyDB on region northamerica-northeast2 in the month of April?")


# %%
similar_docs = df_index.vectorstore.similarity_search_with_score("what is the consumption for AlloyDB on region northamerica-northeast2 in the month of April?", llm=text_llm, k=5)
filtered_docs = list(filter(lambda doc: doc[1] <= 0.5, similar_docs))
print(filtered_docs)
# %%
