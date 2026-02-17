import logging
from typing import List
from google import genai
from google.genai.types import EmbedContentConfig

from .schemas import ExtractedEntity

logger = logging.getLogger(__name__)

def generate_embeddings_for_entities(entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
    """
    Takes a list of normalized ExtractedEntities, generates embeddings for their content,
    and returns the updated list.
    
    We use gemini-embedding-001 (or another feature-store compatible model, as configured)
    and set the dimensionality to 3072.
    """
    if not entities:
        return []

    import os
    client = genai.Client(vertexai=True, project=os.environ.get("PROJECT_ID"), location=os.environ.get("LOCATION"))
    
    # We will embed the 'content_description' text
    # In a full production system, you might concatenate 'structured_data' to this as well
    # for tables to provide richer embeddings.
    contents_to_embed = []
    for entity in entities:
        text = entity.content_description
        if entity.structured_data:
            text += f"\nStructured Data Context: {str(entity.structured_data)}"
        contents_to_embed.append(text)
        
    try:
        response = client.models.embed_content(
            model="text-embedding-004", # Typically standard for Vertex FS now, allows 768 or 3072
            contents=contents_to_embed,
            config=EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768, # Feature store often uses 768 by default in tutorials, but can be 3072. Using 768 for faster vectorizing.
            ),
        )
        
        if not response.embeddings or len(response.embeddings) != len(entities):
            logger.error("Mismatch in embedding count returned.")
            return entities
            
        for i, entity in enumerate(entities):
            entity.embedding = response.embeddings[i].values
            
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        
    return entities
