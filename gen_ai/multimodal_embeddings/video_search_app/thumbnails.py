#%%
import cv2
import tempfile
from google.cloud import storage

def generate_specific_gcs_thumbnail(
        bucket_name: str,
        video_blob_name: str,
        output_thumbnail_blob_name: str, # Full GCS path for the output thumbnail
        target_time_sec: float
):
    """
    Reads a video from GCS, creates a thumbnail for a specific time,
    and stores it back in GCS.

    Args:
        bucket_name (str): The name of the GCS bucket.
        video_blob_name (str): The path to the video file in the bucket (e.g., "video_search_app/videos/video.mp4").
        output_thumbnail_blob_name (str): The full GCS path for the output thumbnail blob (e.g., "video_search_app/thumbnails/video/thumb_5.00s.png").
        target_time_sec (float): The time in seconds to capture the thumbnail from.
    Returns:
        str: The GCS URI of the uploaded thumbnail, or None if failed.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    video_blob = bucket.blob(video_blob_name)

    # Ensure the thumbnail directory structure exists if implied by output_thumbnail_blob_name
    # (GCS doesn't have real directories, but prefixes work like them)
    # No explicit directory creation needed for GCS blob upload.

    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_video_file:
        try:
            video_blob.download_to_filename(temp_video_file.name)
        except Exception as e:
            print(f"Error downloading video {video_blob_name}: {e}")
            return None

        video_capture = cv2.VideoCapture(temp_video_file.name)

        if not video_capture.isOpened():
            print(f"Error: Could not open video file {video_blob_name}")
            return None

        fps = video_capture.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            print(f"Error: Could not get FPS for video {video_blob_name}. Assuming 30 FPS for frame calculation.")
            # Fallback FPS, or handle error more gracefully
            # For this example, let's try to proceed, but this might lead to incorrect frame selection.
            # A better approach might be to skip thumbnail generation or use a default thumbnail.
            # fps = 30 # Example fallback, use with caution
            video_capture.release()
            return None


        target_frame_number = int(fps * target_time_sec)
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame_number)

        success, frame = video_capture.read()
        if not success:
            print(f"Error: Could not read frame at {target_time_sec:.2f}s (frame {target_frame_number}) for video {video_blob_name}")
            video_capture.release()
            return None

        # Encode frame to an in-memory buffer
        is_success, buffer = cv2.imencode('.png', frame)
        if not is_success:
            print(f"Error: Could not encode frame to PNG for video {video_blob_name}")
            video_capture.release()
            return None

        # Upload the in-memory buffer to GCS
        thumbnail_blob = bucket.blob(output_thumbnail_blob_name)
        try:
            thumbnail_blob.upload_from_string(buffer.tobytes(), content_type='image/png')
            print(f"Uploaded {output_thumbnail_blob_name}")
        except Exception as e:
            print(f"Error uploading thumbnail {output_thumbnail_blob_name}: {e}")
            video_capture.release()
            return None

        video_capture.release()
        return f"https://storage.googleapis.com/{bucket_name}/{output_thumbnail_blob_name}"

# generate_specific_gcs_thumbnail(
#     "vtxdemos-datasets-public",
#     "video_search_app/videos/gabby_thomas_gold.mp4",
#     "video_search_app/thumbnail/gabby_thomas_gold.png",
#     12)
