#!/bin/bash
# Upload file to Google Drive via MCP server
# Automatically uses direct base64 for small files, GCS staging for large files

set -e

# Configuration
GCS_BUCKET="gs://vtxdemos/mcp-uploads"
MCP_ENDPOINT="http://localhost:8081/mcp"
SIZE_THRESHOLD=50000  # 50KB - files larger than this use GCS staging
DEFAULT_FOLDER_ID="1K2lkvQYuWd3SN8gg9R7obL9GQ2juFj7e"  # artifacts folder

usage() {
    echo "Usage: $0 <file_path> [folder_id] [mime_type]"
    echo ""
    echo "Arguments:"
    echo "  file_path   - Path to file to upload"
    echo "  folder_id   - Google Drive folder ID (default: artifacts folder)"
    echo "  mime_type   - MIME type (auto-detected if not specified)"
    exit 1
}

# Check arguments
if [ -z "$1" ]; then
    usage
fi

FILE_PATH="$1"
FOLDER_ID="${2:-$DEFAULT_FOLDER_ID}"
MIME_TYPE="$3"

# Validate file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

# Get file info
FILE_NAME=$(basename "$FILE_PATH")
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null)

# Auto-detect MIME type if not provided
if [ -z "$MIME_TYPE" ]; then
    case "${FILE_NAME##*.}" in
        png) MIME_TYPE="image/png" ;;
        jpg|jpeg) MIME_TYPE="image/jpeg" ;;
        gif) MIME_TYPE="image/gif" ;;
        pdf) MIME_TYPE="application/pdf" ;;
        txt) MIME_TYPE="text/plain" ;;
        json) MIME_TYPE="application/json" ;;
        csv) MIME_TYPE="text/csv" ;;
        md) MIME_TYPE="text/markdown" ;;
        *) MIME_TYPE="application/octet-stream" ;;
    esac
fi

echo "File: $FILE_NAME ($FILE_SIZE bytes)"
echo "MIME: $MIME_TYPE"
echo "Destination folder: $FOLDER_ID"

# Choose upload method based on size
if [ "$FILE_SIZE" -lt "$SIZE_THRESHOLD" ]; then
    echo "Method: Direct base64 upload"

    # Base64 encode
    CONTENT_B64=$(base64 -w0 "$FILE_PATH" 2>/dev/null || base64 "$FILE_PATH")

    # Call MCP directly via curl
    RESPONSE=$(curl -s -X POST "$MCP_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{
            \"jsonrpc\": \"2.0\",
            \"id\": 1,
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"drive_upload_binary\",
                \"arguments\": {
                    \"name\": \"$FILE_NAME\",
                    \"content_base64\": \"$CONTENT_B64\",
                    \"mime_type\": \"$MIME_TYPE\",
                    \"parent_id\": \"$FOLDER_ID\"
                }
            }
        }")

    echo "$RESPONSE" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('result',{}).get('content',[{}])[0].get('text','Error'))" 2>/dev/null || echo "$RESPONSE"

else
    echo "Method: GCS staging (file > ${SIZE_THRESHOLD} bytes)"

    # Upload to GCS
    GCS_PATH="$GCS_BUCKET/$FILE_NAME"
    echo "Uploading to $GCS_PATH..."
    gsutil -q cp "$FILE_PATH" "$GCS_PATH"

    # Call MCP with GCS URI
    RESPONSE=$(curl -s -X POST "$MCP_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{
            \"jsonrpc\": \"2.0\",
            \"id\": 1,
            \"method\": \"tools/call\",
            \"params\": {
                \"name\": \"drive_upload_binary\",
                \"arguments\": {
                    \"name\": \"$FILE_NAME\",
                    \"gcs_uri\": \"$GCS_PATH\",
                    \"mime_type\": \"$MIME_TYPE\",
                    \"parent_id\": \"$FOLDER_ID\"
                }
            }
        }")

    echo "$RESPONSE" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('result',{}).get('content',[{}])[0].get('text','Error'))" 2>/dev/null || echo "$RESPONSE"

    # Clean up GCS staging file
    echo "Cleaning up staging file..."
    gsutil -q rm "$GCS_PATH"
fi

echo "Done!"
