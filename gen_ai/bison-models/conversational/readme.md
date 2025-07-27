## Conversational Bot

There are important components to consider when build a conversational chatbot, when we start looking into taking the model into production we have to pay attention to how the front end is integrate with the intelligent/middle ware or the back of the AI/ML.

## Definitions

- **AuthN/Z**: Authentication and Authorization.
- **Interaction**: 1 single conversation between the human and a bot, 
    e.g. {"human": "hi, how are you?", "bot": "I'm doing great thanks for asking!."}

These are the most important components:
1. Keep the session accross users (**AuthN/Z**).
2. Keep relevant information from interactions per user-session (**chat_history**).
3. **Intent detection and chains**, we have to detect the intention of the human so we can route the query properly.

## Folder Structure

1. [large_context](large_context), components used: [documentai](https://cloud.google.com/document-ai), [cloudsql-ppgvector](https://cloud.google.com/blog/products/databases/using-pgvector-llms-and-langchain-with-google-cloud-databases), [gecko-embedings](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings), [text-bison](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text), [gradio](https://www.gradio.app/).
2. [multi_intent](multi_intent), components used: [text-bison](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text), [gradio](https://www.gradio.app/).