import requests

def get_image_data_from_uri(image_uri: str) -> tuple[bytes, str]:
    """
    Gets the image bytes and mime type from an image URI.

    Args:
        image_uri: The URI of the image file.

    Returns:
        A tuple containing the image bytes and the mime type.
    """
    response = requests.get(image_uri, timeout=10)
    response.raise_for_status()
    return response.content, response.headers.get('content-type', 'application/octet-stream')
