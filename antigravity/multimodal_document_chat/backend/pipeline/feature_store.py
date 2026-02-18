import os
import logging
from google.cloud import aiplatform

logger = logging.getLogger(__name__)

def sync_feature_store_from_bq(
    dataset_id: str = "esg_demo_data", 
    table_id: str = "document_embeddings_fs",
    feature_store_name: str = "esg_feature_store",
    feature_view_name: str = "document_embeddings_view"
):
    """
    Creates/updates a Vertex AI Feature View based on the BigQuery table and triggers a sync.
    For this to work, the BigQuery table should ideally have a feature_timestamp column 
    and an entity_id column for standard Feature Store setups.
    
    In a simple document retrieval scenario, we treat 'chunk_id' as the entity_id.
    """
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    
    if not project_id or not location:
        logger.warning("GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION not set, skipping Feature Store sync.")
        return

    aiplatform.init(project=project_id, location=location)
    
    bq_source_uri = f"bq://{project_id}.{dataset_id}.{table_id}"
    logger.info(f"Preparing to sync Feature Store '{feature_store_name}' from {bq_source_uri}")

    try:
        # Step 1: Get or Create Online Store (Often provisioned externally, but we can try)
        # Note: Provisioning an online store can take time. In a real app, this is done once manually.
        # We will assume it exists or fail gracefully for demo purposes.
        try:
             online_store = aiplatform.FeatureOnlineStore(feature_store_name)
             logger.info(f"Found existing FeatureOnlineStore: {feature_store_name}")
        except Exception as e:
             logger.error(f"FeatureOnlineStore {feature_store_name} not found. Please create it manually in GCP Console or via Terraform. {e}")
             return

        # Step 2: Get or Create Feature View
        try:
            feature_view = online_store.get_feature_view(feature_view_name)
            logger.info(f"Found existing FeatureView: {feature_view_name}")
        except Exception:
            logger.info(f"Creating FeatureView {feature_view_name}...")
            # We configure it for Vector Search
            from google.cloud.aiplatform.featurestore_v1.types import feature_view as feature_view_pb2
            
            # The BQ table MUST have 'embedding' column for standard Vector Search configuration
            feature_view = online_store.create_feature_view(
                name=feature_view_name,
                source=aiplatform.featurestore.BigQuerySource(
                    uri=bq_source_uri,
                    entity_id_columns=["chunk_id"] # Treat chunk ID as the unique entity
                ),
                sync_config={"cron": "TZ=America/Los_Angeles 00 00 * * *"}, # Daily sync
            )
            logger.info(f"Created FeatureView: {feature_view.name}")
            
        # Step 3: Trigger online sync
        logger.info(f"Triggering sync for FeatureView {feature_view_name}...")
        sync_response = feature_view.sync()
        logger.info(f"Sync initiated: {sync_response}")
        
    except Exception as e:
        logger.error(f"Error during Feature Store operations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Allow manual triggering
    logging.basicConfig(level=logging.INFO)
    sync_feature_store_from_bq()
