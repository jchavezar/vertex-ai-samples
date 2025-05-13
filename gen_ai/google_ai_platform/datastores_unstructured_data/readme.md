## Data Prep

[from_gcs_to_jsonl_metadata.py](from_gcs_to_jsonl_metadata.py):

**Purpose**: This script creates a JSONL file containing metadata for PDF documents, 
including their respective storage URIs. This file is formatted to facilitate the import of these documents into a 
Vertex AI Search unstructured datastore, allowing them to be indexed and made searchable.

**Main Steps in the Code**:
1. Initialize Clients and Define Configurations.
2. Define Title Generation Function Using Gemini.
3. Process Cloud Storage Blobs and Create Dataset
4. Upload Dataset to Cloud Storage