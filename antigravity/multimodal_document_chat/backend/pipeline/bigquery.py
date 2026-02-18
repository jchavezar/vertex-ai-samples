import logging
import os
from typing import List, Dict, Any
from google.cloud import bigquery

logger = logging.getLogger(__name__)

def insert_embeddings_to_bq(rows: List[Dict[str, Any]], dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs"):
    """
    Inserts a list of dictionaries (rows) into the specified BigQuery table.
    Expects rows to match the schema of the target table.
    """
    if not rows:
        return
        
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        logger.warning("GOOGLE_CLOUD_PROJECT not set, skipping BQ insertion.")
        return
        
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    try:
        # Check if dataset exists, create if not
        dataset_ref = client.dataset(dataset_id)
        try:
            client.get_dataset(dataset_ref)
        except Exception:
            logger.info(f"Dataset {dataset_id} not found, attempting to create it...")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US" # Standard multi-region
            client.create_dataset(dataset)
            
        # Check if table exists
        try:
             client.get_table(table_ref)
        except Exception as e:
             logger.warning(f"Failed to get table {table_ref}, will attempt to create it. {e}")
             schema = [
                 bigquery.SchemaField("chunk_id", "STRING", mode="REQUIRED"),
                 bigquery.SchemaField("document_name", "STRING", mode="REQUIRED"),
                 bigquery.SchemaField("page_number", "INTEGER", mode="REQUIRED"),
                 bigquery.SchemaField("entity_type", "STRING", mode="REQUIRED"),
                 bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
                 # For Feature Store, embeddings are often standard FLOAT arrays
                 bigquery.SchemaField("embedding", "FLOAT", mode="REPEATED")
             ]
             table = bigquery.Table(table_ref, schema=schema)
             client.create_table(table)
             logger.info(f"Created table {table_ref}")
             
             import time
             time.sleep(2) # Give BQ a moment to register the new table
        
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            logger.error(f"Failed to insert rows into BigQuery: {errors}")
        else:
            logger.info(f"Successfully inserted {len(rows)} rows into {table_ref}.")
            
    except Exception as e:
        logger.error(f"Error during BigQuery operation: {e}")

def get_indexed_documents_bq(dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs") -> List[Dict[str, Any]]:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id: return []
    client = bigquery.Client(project=project_id)
    table_ref = f"`{project_id}.{dataset_id}.{table_id}`"
    query = f"SELECT document_name, COUNT(*) as chunk_count FROM {table_ref} GROUP BY document_name ORDER BY document_name"
    try:
        query_job = client.query(query)
        rows = query_job.result()
        return [{"document_name": row.document_name, "chunk_count": row.chunk_count} for row in rows]
    except Exception as e:
        logger.error(f"Error fetching documents from BQ: {e}")
        return []

def delete_document_from_bq(document_name: str, dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs") -> bool:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id: return False
    client = bigquery.Client(project=project_id)
    table_ref = f"`{project_id}.{dataset_id}.{table_id}`"
    query = f"DELETE FROM {table_ref} WHERE document_name = @document_name"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("document_name", "STRING", document_name),
        ]
    )
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return True
    except Exception as e:
        logger.error(f"Error deleting document from BQ: {e}")
        return False

async def search_embeddings_in_bq(query_text: str, dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs", top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embeds the query text and uses BigQuery VECTOR_SEARCH to find the most relevant chunks.
    """
    from google import genai
    from google.genai.types import EmbedContentConfig
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if not project_id:
        return []

    client_genai = genai.Client(vertexai=True, project=project_id, location=location)
        
    # 1. Embed the query
    try:
        response = await client_genai.aio.models.embed_content(
            model="text-embedding-004",
            contents=query_text,
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=768,
            )
        )
        if not response.embeddings:
            return []
        query_vector = response.embeddings[0].values
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return []



    client = bigquery.Client(project=project_id)
    table_ref = f"`{project_id}.{dataset_id}.{table_id}`"
    
    # 2. Run VECTOR_SEARCH
    # BQ VECTOR_SEARCH requires the input to be a table, so we use a CTE
    query = f"""
    WITH query_table AS (
      SELECT {query_vector} AS embedding 
    )
    SELECT base.document_name, base.chunk_id, base.page_number, base.entity_type, base.content, distance
    FROM VECTOR_SEARCH(
      TABLE {table_ref},
      'embedding',
      (SELECT * FROM query_table),
      top_k => @top_k,
      distance_type => 'COSINE'
    )
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("top_k", "INT64", top_k),
        ]
    )
    
    results = []
    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        for row in rows:
            results.append({
                "document_name": row.document_name,
                "chunk_id": row.chunk_id,
                "page_number": row.page_number,
                "entity_type": row.entity_type,
                "content": row.content,
                "distance": row.distance
            })
    except Exception as e:
        logger.error(f"VECTOR_SEARCH failed: {e}")
        
    return results

def get_document_chunks_from_bq(document_name: str, dataset_id: str = "esg_demo_data", table_id: str = "document_embeddings_fs") -> List[Dict[str, Any]]:
    """Retrieves all chunks for a specific document to load the dashboard."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return []
    
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    query = f"""
    SELECT document_name, chunk_id, page_number, entity_type, content
    FROM `{table_ref}`
    WHERE document_name = @doc_name
    ORDER BY page_number, chunk_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("doc_name", "STRING", document_name),
        ]
    )
    
    results = []
    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        for row in rows:
            results.append({
                "document_name": row.document_name,
                "chunk_id": row.chunk_id,
                "page_number": int(row.page_number) if row.page_number else 0,
                "entity_type": row.entity_type,
                "content": row.content,
                "distance": 0.0 # Add default distance for frontend compatibility
            })
    except Exception as e:
        logger.error(f"Failed to fetch document chunks: {e}")
        
    return results
