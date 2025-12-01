import logging
import io
from google import genai

client = genai.Client()

def summarize_gcs_document(gcs_uri: str) -> str:
    """
    Reads a document from GCS, extracts its text, and returns a summary.
    Supports PDF and plain text files.

    Args:
        gcs_uri: The GCS URI of the document (e.g., gs://bucket-name/file-name.pdf).

    Returns:
        A summary of the document's content.
    """


    try:
        msg_file = genai.types.Part.from_uri(
            file_uri=gcs_uri,
            mime_type="application/pdf",
        )

        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[
                genai.types.Content(
                    role="user",
                    parts=[
                        msg_file,
                        genai.types.Part.from_text(text="Give me an accurate summary of the document.")
                    ],
                )
            ]
        )

        return response.text

    except Exception as e:
        logging.error(f"An error occurred during summarization: {e}")
        return f"An error occurred: {e}"