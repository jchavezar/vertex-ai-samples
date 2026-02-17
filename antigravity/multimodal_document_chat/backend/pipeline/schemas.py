from pydantic import BaseModel, Field
from typing import List, Any, Optional

class ExtractedEntity(BaseModel):
    page_number: int = Field(description="The page number in the original document.")
    entity_type: str = Field(description="'TEXT', 'TABLE', or 'CHART'")
    content_description: str = Field(description="The actual text content, or a detailed description of the table/chart if it is visual.")
    structured_data: Optional[dict] = Field(description="Optional parsed JSON dictionary for tabular data (headers, rows).", default=None)
    embedding: Optional[List[float]] = Field(description="3072-dimensional embedding vector assigned post-extraction.", default=None)
    
class DocumentPageResult(BaseModel):
    page_number: int = Field(description="Page number analyzed")
    entities: List[ExtractedEntity] = Field(description="List of entities (text chunks, tables, charts) identified on this page.")
    
class BQFeatureStoreRow(BaseModel):
    """Schema for final structured insertion into BigQuery for Vertex AI Feature Store."""
    chunk_id: str = Field(description="Unique ID for this chunk (e.g., page_num_entity_idx)")
    document_name: str = Field(description="Source document name")
    page_number: int = Field(description="The page number where this chunk was found")
    entity_type: str = Field(description="Type of entity: TEXT, TABLE, CHART")
    content: str = Field(description="The text content or description used to generate the embedding")
    embedding: List[float] = Field(description="3072-dimensional embedding vector")
