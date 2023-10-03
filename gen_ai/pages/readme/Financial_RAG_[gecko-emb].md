# Getting Started
**Prerequisities:**
- Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- Install python requirements:

```sh
cd ../..
pip install -r requirements.txt
```
- Authenticate against your project to create DB:
```sh
gcloud au
- Authenticate against your project to run python scripts:
```sh
gcloud auth application-default login
```
- Create a Google Cloud SQL Vector Database:
```sh
gcloud sql instances create prod-instance --database-version=POSTGRES_15 --cpu=2 --memory=8GiB --zone=us-central1-a --root-password=password123
```

**Steps:**
2 main tasks needs to be accomplished:
- Create **ocr** **indexing/embeddings job** by runing [prepare_vector_db_for_rag_text.py](../preprocess/prepare_vector_db_for_rag_text.py)

```sh
cd preproces
python prepare_vector_db_for_rag_text.py
```
- Run streamlit front end by running: 

file: [Financial_RAG_[Vertex_Search].py](../Financial_RAG_[Vertex_Search].py)
```sh
cd pages
streamlit run Financial_RAG_[Vertex_Search].py
```
or run the [Main.py](../../Main.py) on this folder:
```sh
cd ..
streamlit run Main.py
```

