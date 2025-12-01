import logging
import traceback
import fnmatch
from google.cloud import storage

def _get_gcs_client():
    """Initializes and returns a GCS storage client."""
    try:
        return storage.Client()
    except Exception as e:
        logging.error(f"Failed to create GCS client: {e}")
        raise

def list_files(bucket_name: str, prefix: str = None) -> list[str]:
    """
    Lists all files in a given GCS bucket and optional prefix.

    Args:
        bucket_name: The name of the GCS bucket.
        prefix: The prefix to filter files by.

    Returns:
        A list of file names.
    """
    # TODO: You may need to run 'gcloud auth application-default login'
    # in your terminal for authentication.
    try:
        client = _get_gcs_client()
        bucket = client.bucket(bucket_name)
        blobs = client.list_blobs(bucket, prefix=prefix)
        return [blob.name for blob in blobs]
    except Exception as e:
        logging.error(traceback.format_exc())
        return [f"An error occurred: {e}"]

def find_file(bucket_name: str, match_glob: str = "*", prefix: str = None) -> list[str]:
    """
    Finds files in a GCS bucket matching a glob pattern.

    Args:
        bucket_name: The name of the GCS bucket.
        match_glob: The glob pattern to match file names against (e.g., '*.pdf').
        prefix: The prefix to filter files by (directory path).

    Returns:
        A list of matching file names.
    """
    try:
        client = _get_gcs_client()
        bucket = client.bucket(bucket_name)
        blobs = client.list_blobs(bucket, prefix=prefix)
        
        # If no glob is provided, default to matching everything
        if not match_glob:
            match_glob = "*"

        matching_files = []
        for blob in blobs:
             if fnmatch.fnmatch(blob.name, match_glob):
                 matching_files.append(blob.name)
                 
        return matching_files
    except Exception as e:
        logging.error(traceback.format_exc())
        return [f"An error occurred: {e}"]

def get_file_metadata(bucket_name: str, file_name: str = "") -> dict:
    """
    Retrieves metadata for a specific file in a GCS bucket.

    Args:
        bucket_name: The name of the GCS bucket.
        file_name: The full name/path of the file in the bucket.

    Returns:
        A dictionary containing file metadata.
    """
    try:
        if not file_name:
             return {"error": "File name is required"}
        client = _get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.reload()  # Fetch the blob's metadata from GCS
        return {
            "name": blob.name,
            "bucket": blob.bucket.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "time_created": blob.time_created.isoformat(),
            "last_updated": blob.updated.isoformat(),
        }
    except Exception as e:
        return {"error": f"An error occurred: {e}"}