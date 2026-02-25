import logging
import os
from typing import List
from google import genai
from google.genai.types import EmbedContentConfig

from .schemas import ExtractedEntity

logger = logging.getLogger(__name__)

async def generate_embeddings_for_entities(entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
    """
    Takes a list of normalized ExtractedEntities, generates embeddings asynchronously for their content,
    and returns the updated list.
    """
    if not entities:
        return []

    client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location=os.environ.get("GOOGLE_CLOUD_LOCATION"))
    
    # We will embed the 'content_description' text
    contents_to_embed = []
    for entity in entities:
        text = entity.content_description
        if entity.structured_data:
            text += f"\nStructured Data Context: {str(entity.structured_data)}"
        contents_to_embed.append(text)
        
    try:
        # Vertex AI embeddings limit is 250 instances per prediction call
        batch_size = 250
        all_embeddings = []
        
        for i in range(0, len(contents_to_embed), batch_size):
            batch = contents_to_embed[i:i + batch_size]
            response = await client.aio.models.embed_content(
                model="text-embedding-004", # Standard Vertex AI text embedding model
                contents=batch,
                config=EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768,
                ),
            )
            if response.embeddings:
                all_embeddings.extend(response.embeddings)
        
        if len(all_embeddings) != len(entities):
            logger.error(f"Mismatch in embedding count returned. Expected {len(entities)}, got {len(all_embeddings)}.")
            return entities
            
        for i, entity in enumerate(entities):
            entity.embedding = all_embeddings[i].values
            
    except Exception as e:
        logger.error(f"Failed to generate async embeddings: {e}")
        
    return entities
