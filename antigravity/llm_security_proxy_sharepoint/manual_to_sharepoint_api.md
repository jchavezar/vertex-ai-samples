# SharePoint API Complete Guide for MCP Server Development

A comprehensive reference for building Model Context Protocol (MCP) servers that integrate with Microsoft SharePoint. This guide covers SharePoint REST API, Microsoft Graph API, authentication methods, and complete implementation patterns.

## Table of Contents

- [Overview](#overview)
- [SharePoint API Options](#sharepoint-api-options)
- [Authentication Methods](#authentication-methods)
- [Azure AD App Registration Setup](#azure-ad-app-registration-setup)
- [SharePoint REST API Reference](#sharepoint-rest-api-reference)
- [Microsoft Graph API Reference](#microsoft-graph-api-reference)
- [OData Query Operations](#odata-query-operations)
- [File Operations](#file-operations)
- [List Operations](#list-operations)
- [Search with KQL](#search-with-kql)
- [Webhooks and Change Tracking](#webhooks-and-change-tracking)
- [Batch Requests](#batch-requests)
- [Rate Limiting and Throttling](#rate-limiting-and-throttling)
- [Error Handling](#error-handling)
- [MCP Server Implementation](#mcp-server-implementation)
- [Complete Code Examples](#complete-code-examples)
- [Best Practices](#best-practices)
- [Resources](#resources)

---

## Overview

SharePoint provides two primary API interfaces for programmatic access:

| API | Endpoint Base | Best For |
|-----|---------------|----------|
| **SharePoint REST API** | `https://{tenant}.sharepoint.com/_api/` | SharePoint-specific operations, on-premises support, detailed SharePoint features |
| **Microsoft Graph API** | `https://graph.microsoft.com/v1.0/` | Cross-Microsoft 365 integration, modern applications, unified access |

### Key Differences

| Feature | SharePoint REST API | Microsoft Graph API |
|---------|---------------------|---------------------|
| Scope | SharePoint only | All Microsoft 365 services |
| Environment | Online + On-Premises | Online only |
| Authentication | Certificate required for app-only | Client credentials supported |
| Development Status | Stable, limited new features | Actively developed |
| Performance | Direct access, potentially faster | Unified endpoint, slight overhead |

**Recommendation**: For new projects targeting SharePoint Online, start with Microsoft Graph API for future-proofing. Use SharePoint REST API for specialized features or on-premises deployments.

---

## Authentication Methods

### 1. Certificate-Based Authentication (App-Only) - **Recommended**

SharePoint REST API requires certificate authentication for app-only access. Client secrets alone will return "Unsupported app only token" errors.

```python
from msal import ConfidentialClientApplication
import requests

# Configuration
TENANT_ID = "your-tenant-id"
CLIENT_ID = "your-client-id"
CERT_PATH = "/path/to/certificate.pem"
CERT_THUMBPRINT = "your-certificate-thumbprint"
SHAREPOINT_URL = "https://yourtenant.sharepoint.com"

# Create MSAL app with certificate
app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential={
        "thumbprint": CERT_THUMBPRINT,
        "private_key": open(CERT_PATH).read()
    }
)

# Acquire token for SharePoint
result = app.acquire_token_for_client(
    scopes=[f"{SHAREPOINT_URL}/.default"]
)

if "access_token" in result:
    access_token = result["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json;odata=verbose"
    }
```

### 2. Client Credentials with Microsoft Graph

```python
from msal import ConfidentialClientApplication

app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET  # Works for Graph API
)

result = app.acquire_token_for_client(
    scopes=["https://graph.microsoft.com/.default"]
)
```

### 3. Delegated User Authentication

```python
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

credentials = UserCredential("user@domain.com", "password")
ctx = ClientContext("https://tenant.sharepoint.com/sites/mysite").with_credentials(credentials)

web = ctx.web
ctx.load(web)
ctx.execute_query()
print(f"Site Title: {web.properties['Title']}")
```

### 4. Using Office365-REST-Python-Client Library

```python
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

# With client credentials (for libraries that support it)
client_credentials = ClientCredential(CLIENT_ID, CLIENT_SECRET)
ctx = ClientContext(SHAREPOINT_URL).with_credentials(client_credentials)

# With certificate
ctx = ClientContext.connect_with_certificate(
    SHAREPOINT_URL,
    client_id=CLIENT_ID,
    thumbprint=CERT_THUMBPRINT,
    cert_path=CERT_PATH
)
```

---

## Azure AD App Registration Setup

### Step 1: Create App Registration

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Click **New registration**
3. Enter application name
4. Set **Supported account types** to "Accounts in this organizational directory only"
5. Click **Register**
6. Note down: **Application (client) ID** and **Directory (tenant) ID**

### Step 2: Create Self-Signed Certificate

**Using OpenSSL:**
```bash
# Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
    -subj "/CN=SharePointMCPServer"

# Convert to PFX (for Windows/Azure)
openssl pkcs12 -export -out certificate.pfx -inkey key.pem -in cert.pem

# Get thumbprint
openssl x509 -in cert.pem -fingerprint -noout | sed 's/://g' | cut -d= -f2
```

**Using PowerShell:**
```powershell
$cert = New-SelfSignedCertificate -Subject "CN=SharePointMCPServer" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeySpec Signature `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(2)

# Export certificate
Export-Certificate -Cert $cert -FilePath ".\SharePointMCPServer.cer"
$cert.Thumbprint
```

### Step 3: Upload Certificate to Azure AD

1. In your app registration, go to **Certificates & secrets**
2. Click **Certificates** tab → **Upload certificate**
3. Upload the `.cer` file

### Step 4: Configure API Permissions

| Permission Type | API | Permission | Description |
|-----------------|-----|------------|-------------|
| Application | Microsoft Graph | `Sites.Read.All` | Read all sites |
| Application | Microsoft Graph | `Sites.ReadWrite.All` | Read/write all sites |
| Application | Microsoft Graph | `Sites.Selected` | Granular site access |
| Application | SharePoint | `Sites.FullControl.All` | Full control (admin) |
| Application | SharePoint | `Sites.Selected` | Granular site access |

**For granular access using Sites.Selected:**
```powershell
# Grant permission to specific site using PnP PowerShell
Connect-PnPOnline -Url "https://tenant-admin.sharepoint.com" -Interactive
Grant-PnPAzureADAppSitePermission -AppId $CLIENT_ID `
    -DisplayName "MCP Server" `
    -Site "https://tenant.sharepoint.com/sites/targetsite" `
    -Permissions Write
```

### Step 5: Grant Admin Consent

1. Go to **API permissions** in your app
2. Click **Grant admin consent for {tenant}**

---

## SharePoint REST API Reference

### Base URL Structure
```
https://{tenant}.sharepoint.com/{site}/_api/{resource}
```

### Essential HTTP Headers

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json;odata=verbose",
    "Content-Type": "application/json;odata=verbose",
    "X-RequestDigest": form_digest_value,  # Required for POST/PUT/DELETE
    "IF-MATCH": "*",  # For updates (or use specific ETag)
    "X-HTTP-Method": "MERGE"  # For updates
}
```

### Getting Form Digest (Required for Write Operations)

```python
def get_form_digest(site_url: str, access_token: str) -> str:
    """Get form digest value for POST/PUT/DELETE operations."""
    response = requests.post(
        f"{site_url}/_api/contextinfo",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json;odata=verbose"
        }
    )
    return response.json()["d"]["GetContextWebInformation"]["FormDigestValue"]
```

### Site Operations

```python
# Get site information
GET /_api/web
GET /_api/web?$select=Title,Url,Created

# Get site properties
GET /_api/site

# Get all subsites
GET /_api/web/webs

# Get root web info
GET /_api/site/rootWeb/webinfos
```

### List Operations

```python
# Get all lists
GET /_api/web/lists

# Get list by title
GET /_api/web/lists/GetByTitle('Documents')

# Get list by GUID
GET /_api/web/lists(guid'list-guid-here')

# Get all items from a list
GET /_api/web/lists/GetByTitle('Documents')/items

# Get specific item
GET /_api/web/lists/GetByTitle('Documents')/items({item_id})

# Create list item
POST /_api/web/lists/GetByTitle('Documents')/items
Body: {
    "__metadata": { "type": "SP.Data.DocumentsItem" },
    "Title": "New Item"
}

# Update list item
POST /_api/web/lists/GetByTitle('Documents')/items({item_id})
Headers: X-HTTP-Method: MERGE, IF-MATCH: *
Body: {
    "__metadata": { "type": "SP.Data.DocumentsItem" },
    "Title": "Updated Title"
}

# Delete list item
POST /_api/web/lists/GetByTitle('Documents')/items({item_id})
Headers: X-HTTP-Method: DELETE, IF-MATCH: *
```

### Getting ListItemEntityTypeFullName

Required for create/update operations:

```python
def get_list_item_entity_type(site_url: str, list_title: str, headers: dict) -> str:
    """Get the entity type name required for list item operations."""
    response = requests.get(
        f"{site_url}/_api/web/lists/GetByTitle('{list_title}')?$select=ListItemEntityTypeFullName",
        headers=headers
    )
    return response.json()["d"]["ListItemEntityTypeFullName"]
```

---

## Microsoft Graph API Reference

### Base URL
```
https://graph.microsoft.com/v1.0/
```

### Site Operations

```python
# Get site by path
GET /sites/{hostname}:/{site-path}
# Example: /sites/contoso.sharepoint.com:/sites/marketing

# Get site by ID
GET /sites/{site-id}

# Search for sites
GET /sites?search={query}

# Get root site
GET /sites/root

# List subsites
GET /sites/{site-id}/sites
```

### Drive (Document Library) Operations

```python
# Get default document library
GET /sites/{site-id}/drive

# Get all drives
GET /sites/{site-id}/drives

# Get drive items (root folder)
GET /sites/{site-id}/drive/root/children

# Get items in a folder
GET /sites/{site-id}/drive/items/{folder-id}/children
GET /sites/{site-id}/drive/root:/{folder-path}:/children

# Get item by path
GET /sites/{site-id}/drive/root:/{item-path}

# Get item by ID
GET /sites/{site-id}/drive/items/{item-id}

# Download file content
GET /sites/{site-id}/drive/items/{item-id}/content

# Upload small file (< 4MB)
PUT /sites/{site-id}/drive/root:/{filename}:/content
Content-Type: application/octet-stream
Body: [file content]

# Create folder
POST /sites/{site-id}/drive/root/children
Body: {
    "name": "New Folder",
    "folder": {},
    "@microsoft.graph.conflictBehavior": "rename"
}

# Delete item
DELETE /sites/{site-id}/drive/items/{item-id}
```

### List Operations (Graph)

```python
# Get all lists
GET /sites/{site-id}/lists

# Get list by ID
GET /sites/{site-id}/lists/{list-id}

# Get list items
GET /sites/{site-id}/lists/{list-id}/items?expand=fields

# Create list item
POST /sites/{site-id}/lists/{list-id}/items
Body: {
    "fields": {
        "Title": "New Item"
    }
}
```

---

## OData Query Operations

SharePoint REST API supports OData query parameters for filtering, sorting, and selecting data.

### $select - Choose specific fields

```python
# Select specific fields
GET /_api/web/lists?$select=Title,Id,ItemCount

# Select nested properties
GET /_api/web/lists/GetByTitle('Docs')/items?$select=Title,Author/Title&$expand=Author
```

### $filter - Filter results

```python
# Basic filter
GET /_api/web/lists/GetByTitle('Docs')/items?$filter=Title eq 'Report'

# Multiple conditions
GET /_api/web/lists/GetByTitle('Docs')/items?$filter=Status eq 'Active' and Priority gt 2

# Date filtering
GET /_api/web/lists/GetByTitle('Docs')/items?$filter=Created gt datetime'2024-01-01T00:00:00Z'

# Contains (substringof)
GET /_api/web/lists/GetByTitle('Docs')/items?$filter=substringof('keyword',Title)

# Starts with
GET /_api/web/lists/GetByTitle('Docs')/items?$filter=startswith(Title,'Report')
```

**Supported Filter Operators:**
| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equal | `$filter=Status eq 'Active'` |
| `ne` | Not equal | `$filter=Status ne 'Closed'` |
| `gt` | Greater than | `$filter=Priority gt 3` |
| `ge` | Greater or equal | `$filter=Priority ge 3` |
| `lt` | Less than | `$filter=Priority lt 5` |
| `le` | Less or equal | `$filter=Priority le 5` |
| `and` | Logical and | `$filter=A eq 1 and B eq 2` |
| `or` | Logical or | `$filter=A eq 1 or A eq 2` |
| `not` | Logical not | `$filter=not(Status eq 'Closed')` |

### $orderby - Sort results

```python
# Ascending (default)
GET /_api/web/lists/GetByTitle('Docs')/items?$orderby=Title

# Descending
GET /_api/web/lists/GetByTitle('Docs')/items?$orderby=Created desc

# Multiple fields
GET /_api/web/lists/GetByTitle('Docs')/items?$orderby=Priority desc,Created asc
```

### $top and $skip - Pagination

```python
# Get first 10 items
GET /_api/web/lists/GetByTitle('Docs')/items?$top=10

# Skip first 10, get next 10 (Note: $skip doesn't work for list items)
# Use $skiptoken instead for list items
GET /_api/web/lists/GetByTitle('Docs')/items?$top=10&$skiptoken=Paged=TRUE&p_ID=10
```

### $expand - Include related entities

```python
# Expand lookup fields
GET /_api/web/lists/GetByTitle('Docs')/items?$select=Title,Author/Title,Author/Email&$expand=Author

# Expand file info
GET /_api/web/lists/GetByTitle('Docs')/items?$select=Title,File&$expand=File

# Multiple expansions
GET /_api/web/lists/GetByTitle('Docs')/items?$expand=Author,Editor,File
```

---

## File Operations

### Small File Upload (< 2MB)

```python
def upload_small_file(site_url: str, library_name: str, file_name: str,
                      file_content: bytes, headers: dict) -> dict:
    """Upload file smaller than 2MB."""
    upload_url = (
        f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{library_name}')"
        f"/Files/add(url='{file_name}',overwrite=true)"
    )

    headers_copy = headers.copy()
    headers_copy["Content-Type"] = "application/octet-stream"

    response = requests.post(upload_url, headers=headers_copy, data=file_content)
    return response.json()
```

### Large File Upload (Chunked - > 2MB)

SharePoint supports files up to 250GB using chunked upload. Files larger than 250MB **must** use chunking.

```python
import uuid
import os

def upload_large_file(site_url: str, library_path: str, file_path: str,
                      headers: dict, chunk_size: int = 10 * 1024 * 1024) -> dict:
    """
    Upload large file using chunked upload.

    Chunk size: 10MB recommended (max varies, typically up to 250MB per chunk)
    """
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    upload_id = str(uuid.uuid4())

    # Step 1: Create empty file placeholder
    create_url = (
        f"{site_url}/_api/web/GetFolderByServerRelativeUrl('{library_path}')"
        f"/Files/add(url='{file_name}',overwrite=true)"
    )
    headers_create = headers.copy()
    headers_create["Content-Length"] = "0"
    requests.post(create_url, headers=headers_create)

    # Step 2: Get server-relative URL
    server_relative_url = f"{library_path}/{file_name}"

    with open(file_path, 'rb') as f:
        chunk_num = 0
        offset = 0

        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            is_first = chunk_num == 0
            is_last = offset + len(chunk) >= file_size

            if is_first:
                # Start upload
                url = (
                    f"{site_url}/_api/web/GetFileByServerRelativeUrl('{server_relative_url}')"
                    f"/StartUpload(uploadId=guid'{upload_id}')"
                )
            elif is_last:
                # Finish upload
                url = (
                    f"{site_url}/_api/web/GetFileByServerRelativeUrl('{server_relative_url}')"
                    f"/FinishUpload(uploadId=guid'{upload_id}',fileOffset={offset})"
                )
            else:
                # Continue upload
                url = (
                    f"{site_url}/_api/web/GetFileByServerRelativeUrl('{server_relative_url}')"
                    f"/ContinueUpload(uploadId=guid'{upload_id}',fileOffset={offset})"
                )

            response = requests.post(url, headers=headers, data=chunk)
            response.raise_for_status()

            offset += len(chunk)
            chunk_num += 1

    return {"success": True, "file_url": f"{site_url}{server_relative_url}"}
```

### File Download

```python
def download_file(site_url: str, file_server_relative_url: str,
                  headers: dict) -> bytes:
    """Download file content."""
    url = f"{site_url}/_api/web/GetFileByServerRelativeUrl('{file_server_relative_url}')/$value"
    response = requests.get(url, headers=headers)
    return response.content

# Stream download for large files
def download_file_stream(site_url: str, file_server_relative_url: str,
                         headers: dict, output_path: str):
    """Download large file using streaming."""
    url = f"{site_url}/_api/web/GetFileByServerRelativeUrl('{file_server_relative_url}')/$value"

    with requests.get(url, headers=headers, stream=True) as response:
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
```

### Folder Operations

```python
# Get folder by URL
GET /_api/web/GetFolderByServerRelativeUrl('/sites/mysite/Shared Documents/Folder')

# Get folder contents
GET /_api/web/GetFolderByServerRelativeUrl('/sites/mysite/Shared Documents')/Files
GET /_api/web/GetFolderByServerRelativeUrl('/sites/mysite/Shared Documents')/Folders

# Create folder
POST /_api/web/folders
Body: {
    "__metadata": { "type": "SP.Folder" },
    "ServerRelativeUrl": "/sites/mysite/Shared Documents/NewFolder"
}

# Delete folder
POST /_api/web/GetFolderByServerRelativeUrl('/sites/mysite/Shared Documents/Folder')
Headers: X-HTTP-Method: DELETE
```

### Check-In / Check-Out

```python
# Check out file
POST /_api/web/GetFileByServerRelativeUrl('/sites/mysite/Shared Documents/file.docx')/CheckOut()

# Check in file (0=Minor, 1=Major, 2=Overwrite)
POST /_api/web/GetFileByServerRelativeUrl('/sites/mysite/Shared Documents/file.docx')/CheckIn(comment='Updated content',checkintype=1)

# Discard checkout
POST /_api/web/GetFileByServerRelativeUrl('/sites/mysite/Shared Documents/file.docx')/UndoCheckOut()
```

---

## Search with KQL

SharePoint Search uses Keyword Query Language (KQL) for building search queries.

### Basic Search Endpoint

```python
# GET method
GET /_api/search/query?querytext='search terms'

# POST method (for complex queries)
POST /_api/search/postquery
Body: {
    "request": {
        "Querytext": "search terms",
        "SelectProperties": {
            "results": ["Title", "Path", "Author", "LastModifiedTime"]
        },
        "RowLimit": 50,
        "StartRow": 0
    }
}
```

### KQL Syntax Reference

**Property Searches:**
```
Title:report                    # Title contains "report"
Author:"John Smith"             # Exact author match
FileExtension:pdf               # PDF files only
Path:"/sites/marketing/*"       # Files in specific path
LastModifiedTime>2024-01-01     # Modified after date
ContentType:"Document"          # Specific content type
IsDocument:1                    # Only documents
```

**Operators:**
```
marketing AND sales             # Both terms required
marketing OR sales              # Either term
marketing NOT internal          # Exclude term
"quarterly report"              # Exact phrase
market*                         # Wildcard (suffix only)
```

**Combined Queries:**
```python
# Complex KQL query
query = (
    'ContentClass:STS_ListItem_DocumentLibrary '
    'FileExtension:pdf '
    'Author:"John Smith" '
    'LastModifiedTime>2024-01-01 '
    'Path:"/sites/marketing/*"'
)

GET /_api/search/query?querytext='{query}'&selectproperties='Title,Path,Author'&rowlimit=100
```

### Search with Refiners

```python
POST /_api/search/postquery
Body: {
    "request": {
        "Querytext": "budget report",
        "Refiners": "FileType,Author,LastModifiedTime",
        "SelectProperties": {
            "results": ["Title", "Path", "FileType", "Author"]
        }
    }
}
```

---

## Webhooks and Change Tracking

### Creating a Webhook Subscription

```python
def create_webhook(site_url: str, list_id: str, notification_url: str,
                   expiration_datetime: str, headers: dict) -> dict:
    """
    Create webhook subscription for a list.

    expiration_datetime: ISO 8601 format, max 180 days from now
    """
    url = f"{site_url}/_api/web/lists('{list_id}')/subscriptions"

    body = {
        "resource": f"{site_url}/_api/web/lists('{list_id}')",
        "notificationUrl": notification_url,
        "expirationDateTime": expiration_datetime,
        "clientState": "optional-client-state-string"
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()
```

### Webhook Notification Handler

```python
from fastapi import FastAPI, Request
import asyncio

app = FastAPI()

@app.post("/webhook/sharepoint")
async def handle_webhook(request: Request):
    """
    Handle SharePoint webhook notifications.

    IMPORTANT: Must respond within 5 seconds!
    """
    # Validation request (initial subscription)
    validation_token = request.query_params.get("validationtoken")
    if validation_token:
        return Response(content=validation_token, media_type="text/plain")

    # Process notification asynchronously
    body = await request.json()
    asyncio.create_task(process_notifications(body))

    return {"status": "ok"}

async def process_notifications(notifications: dict):
    """Process webhook notifications asynchronously."""
    for notification in notifications.get("value", []):
        site_url = notification["siteUrl"]
        list_id = notification["resource"]

        # Get changes using change token
        changes = await get_list_changes(site_url, list_id)
        # Process changes...
```

### Getting Changes (Delta Query)

```python
def get_list_changes(site_url: str, list_id: str, change_token: str,
                     headers: dict) -> dict:
    """Get changes since last change token."""
    url = f"{site_url}/_api/web/lists(guid'{list_id}')/GetChanges"

    body = {
        "query": {
            "__metadata": {"type": "SP.ChangeQuery"},
            "Add": True,
            "Update": True,
            "DeleteObject": True,
            "Item": True,
            "ChangeTokenStart": {
                "__metadata": {"type": "SP.ChangeToken"},
                "StringValue": change_token
            }
        }
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()
```

---

## Batch Requests

Combine multiple operations into a single HTTP request to improve performance.

```python
import uuid

def create_batch_request(site_url: str, operations: list, headers: dict) -> dict:
    """
    Execute multiple operations in a single batch request.

    Note: File uploads are NOT supported in batch requests.
    """
    batch_id = str(uuid.uuid4())
    batch_url = f"{site_url}/_api/$batch"

    # Build multipart body
    boundary = f"batch_{batch_id}"
    body_parts = []

    for i, op in enumerate(operations):
        changeset_id = str(uuid.uuid4())
        part = f"""--{boundary}
Content-Type: multipart/mixed; boundary="changeset_{changeset_id}"

--changeset_{changeset_id}
Content-Type: application/http
Content-Transfer-Encoding: binary

{op['method']} {op['url']} HTTP/1.1
Content-Type: application/json;odata=verbose
Accept: application/json;odata=verbose

{json.dumps(op.get('body', {}))}
--changeset_{changeset_id}--"""
        body_parts.append(part)

    body = "\n".join(body_parts) + f"\n--{boundary}--"

    batch_headers = headers.copy()
    batch_headers["Content-Type"] = f'multipart/mixed; boundary="{boundary}"'

    response = requests.post(batch_url, headers=batch_headers, data=body)
    return response.text
```

---

## Rate Limiting and Throttling

### Understanding Throttling

SharePoint Online enforces throttling to ensure service stability:

| Response Code | Meaning | Action |
|---------------|---------|--------|
| **429** | Too Many Requests | Respect `Retry-After` header |
| **503** | Service Unavailable | Wait and retry |

### Handling Throttling

```python
import time
from typing import Callable
import requests

def request_with_retry(
    method: Callable,
    url: str,
    max_retries: int = 5,
    **kwargs
) -> requests.Response:
    """
    Execute request with automatic retry on throttling.
    """
    for attempt in range(max_retries):
        response = method(url, **kwargs)

        if response.status_code == 429 or response.status_code == 503:
            retry_after = int(response.headers.get("Retry-After", 120))
            print(f"Throttled. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response

    raise Exception(f"Max retries ({max_retries}) exceeded")
```

### Using RateLimit Headers (Proactive)

```python
def check_rate_limits(response: requests.Response) -> dict:
    """Extract rate limit headers to prevent throttling."""
    return {
        "limit": response.headers.get("RateLimit-Limit"),
        "remaining": response.headers.get("RateLimit-Remaining"),
        "reset": response.headers.get("RateLimit-Reset")
    }

# Proactively slow down when approaching limits
def smart_request(url: str, headers: dict) -> requests.Response:
    response = requests.get(url, headers=headers)

    limits = check_rate_limits(response)
    if limits["remaining"] and int(limits["remaining"]) < 10:
        # Approaching limit, slow down
        time.sleep(1)

    return response
```

### Best Practices for Avoiding Throttling

1. **Use batch requests** to reduce call count
2. **Implement exponential backoff** for retries
3. **Cache tokens and responses** where appropriate
4. **Monitor RateLimit headers** proactively
5. **Use delta queries** instead of full syncs
6. **Spread requests** over time (avoid bursts)

---

## Error Handling

### Common HTTP Status Codes

| Code | Error | Common Causes | Solution |
|------|-------|---------------|----------|
| **400** | Bad Request | Malformed request, wrong headers | Check request body and headers |
| **401** | Unauthorized | Invalid/expired token | Refresh token, check permissions |
| **403** | Forbidden | Insufficient permissions | Request proper permissions |
| **404** | Not Found | Resource doesn't exist | Verify URL and resource existence |
| **409** | Conflict | Version conflict, locked file | Use proper ETag, check lock status |
| **429** | Too Many Requests | Throttling | Implement retry with backoff |
| **500** | Internal Server Error | Server-side issue | Retry later |
| **503** | Service Unavailable | Temporary overload | Wait and retry |

### Error Response Parser

```python
def parse_sharepoint_error(response: requests.Response) -> dict:
    """Parse SharePoint error response."""
    try:
        error_data = response.json()

        # OData verbose format
        if "error" in error_data:
            return {
                "code": error_data["error"].get("code", "Unknown"),
                "message": error_data["error"]["message"].get("value", str(error_data))
            }

        # OData nometadata format
        if "odata.error" in error_data:
            return {
                "code": error_data["odata.error"].get("code", "Unknown"),
                "message": error_data["odata.error"]["message"].get("value", str(error_data))
            }

        return {"code": response.status_code, "message": str(error_data)}

    except Exception:
        return {"code": response.status_code, "message": response.text}
```

### Common Error Patterns and Solutions

```python
# Error: "The security validation for this page is invalid"
# Solution: Get fresh form digest
form_digest = get_form_digest(site_url, access_token)
headers["X-RequestDigest"] = form_digest

# Error: "Unsupported app only token"
# Solution: Use certificate authentication instead of client secret

# Error: "Item does not exist"
# Solution: Check permissions, verify item exists
try:
    response = requests.get(item_url, headers=headers)
except Exception as e:
    if "does not exist" in str(e):
        # Handle missing item gracefully
        pass

# Error: "The file is checked out"
# Solution: Check in or discard checkout first
POST /_api/web/GetFileByServerRelativeUrl('{path}')/UndoCheckOut()
```

---

## MCP Server Implementation

### Project Structure

```
sharepoint-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py           # MCP server entry point
│   ├── sharepoint/
│   │   ├── __init__.py
│   │   ├── client.py       # SharePoint API client
│   │   ├── auth.py         # Authentication handlers
│   │   └── models.py       # Data models
│   └── tools/
│       ├── __init__.py
│       ├── files.py        # File operation tools
│       ├── lists.py        # List operation tools
│       └── search.py       # Search tools
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Installation

```bash
pip install mcp fastmcp msal requests office365-rest-python-client
```

### Basic MCP Server

```python
# src/server.py
from mcp.server.fastmcp import FastMCP
from sharepoint.client import SharePointClient

# Initialize MCP server
mcp = FastMCP(
    "SharePoint MCP Server",
    description="MCP server for SharePoint document management"
)

# Initialize SharePoint client
sp_client = SharePointClient(
    site_url=os.environ["SHAREPOINT_URL"],
    tenant_id=os.environ["TENANT_ID"],
    client_id=os.environ["CLIENT_ID"],
    cert_path=os.environ["CERT_PATH"],
    cert_thumbprint=os.environ["CERT_THUMBPRINT"]
)

# ============ TOOLS ============

@mcp.tool()
def list_files(folder_path: str = "/Shared Documents") -> list[dict]:
    """
    List all files in a SharePoint folder.

    Args:
        folder_path: Server-relative path to the folder

    Returns:
        List of file metadata objects
    """
    return sp_client.get_folder_files(folder_path)


@mcp.tool()
def search_documents(
    query: str,
    file_type: str = None,
    max_results: int = 50
) -> list[dict]:
    """
    Search for documents in SharePoint using KQL.

    Args:
        query: Search keywords or KQL query
        file_type: Optional file extension filter (e.g., "pdf", "docx")
        max_results: Maximum number of results (default: 50)

    Returns:
        List of matching documents with metadata
    """
    kql = query
    if file_type:
        kql += f" FileExtension:{file_type}"

    return sp_client.search(kql, row_limit=max_results)


@mcp.tool()
def download_file(file_path: str) -> dict:
    """
    Download a file from SharePoint.

    Args:
        file_path: Server-relative path to the file

    Returns:
        File content and metadata
    """
    content, metadata = sp_client.download_file(file_path)
    return {
        "content": content.decode("utf-8", errors="replace"),
        "metadata": metadata
    }


@mcp.tool()
def upload_file(
    folder_path: str,
    file_name: str,
    content: str,
    overwrite: bool = True
) -> dict:
    """
    Upload a file to SharePoint.

    Args:
        folder_path: Target folder path
        file_name: Name for the file
        content: File content as string
        overwrite: Whether to overwrite existing file

    Returns:
        Uploaded file metadata
    """
    return sp_client.upload_file(
        folder_path,
        file_name,
        content.encode("utf-8"),
        overwrite
    )


@mcp.tool()
def get_list_items(
    list_title: str,
    filter_query: str = None,
    top: int = 100
) -> list[dict]:
    """
    Get items from a SharePoint list.

    Args:
        list_title: Title of the list
        filter_query: OData filter expression
        top: Maximum items to return

    Returns:
        List of items with fields
    """
    return sp_client.get_list_items(list_title, filter_query, top)


@mcp.tool()
def create_list_item(list_title: str, fields: dict) -> dict:
    """
    Create a new item in a SharePoint list.

    Args:
        list_title: Title of the list
        fields: Dictionary of field names and values

    Returns:
        Created item metadata
    """
    return sp_client.create_list_item(list_title, fields)


# ============ RESOURCES ============

@mcp.resource("sharepoint://sites")
def get_sites() -> str:
    """Get all accessible SharePoint sites."""
    sites = sp_client.get_sites()
    return json.dumps(sites, indent=2)


@mcp.resource("sharepoint://site/{site_path}/lists")
def get_site_lists(site_path: str) -> str:
    """Get all lists in a site."""
    lists = sp_client.get_lists(site_path)
    return json.dumps(lists, indent=2)


@mcp.resource("sharepoint://file/{file_path}")
def get_file_content(file_path: str) -> str:
    """Get file content by path."""
    content, _ = sp_client.download_file(file_path)
    return content.decode("utf-8", errors="replace")


# ============ RUN SERVER ============

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### SharePoint Client Implementation

```python
# src/sharepoint/client.py
from msal import ConfidentialClientApplication
import requests
from typing import Optional, Tuple
import json

class SharePointClient:
    """SharePoint API client with certificate authentication."""

    def __init__(
        self,
        site_url: str,
        tenant_id: str,
        client_id: str,
        cert_path: str,
        cert_thumbprint: str
    ):
        self.site_url = site_url.rstrip("/")
        self.tenant_id = tenant_id
        self.client_id = client_id

        # Initialize MSAL with certificate
        with open(cert_path, "r") as f:
            private_key = f.read()

        self.app = ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential={
                "thumbprint": cert_thumbprint,
                "private_key": private_key
            }
        )

        self._access_token = None
        self._form_digest = None

    @property
    def access_token(self) -> str:
        """Get or refresh access token."""
        if not self._access_token:
            result = self.app.acquire_token_for_client(
                scopes=[f"{self.site_url}/.default"]
            )
            if "access_token" not in result:
                raise Exception(f"Failed to get token: {result.get('error_description')}")
            self._access_token = result["access_token"]
        return self._access_token

    @property
    def headers(self) -> dict:
        """Standard request headers."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose"
        }

    def get_form_digest(self) -> str:
        """Get form digest for write operations."""
        response = requests.post(
            f"{self.site_url}/_api/contextinfo",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["d"]["GetContextWebInformation"]["FormDigestValue"]

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        require_digest: bool = False
    ) -> dict:
        """Execute API request with error handling."""
        url = f"{self.site_url}/_api/{endpoint}"
        headers = self.headers.copy()

        if require_digest:
            headers["X-RequestDigest"] = self.get_form_digest()

        response = requests.request(
            method,
            url,
            headers=headers,
            json=data
        )

        # Handle throttling
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 120))
            raise Exception(f"Throttled. Retry after {retry_after} seconds.")

        response.raise_for_status()

        if response.content:
            return response.json()
        return {}

    # ============ FILE OPERATIONS ============

    def get_folder_files(self, folder_path: str) -> list[dict]:
        """Get all files in a folder."""
        endpoint = f"web/GetFolderByServerRelativeUrl('{folder_path}')/Files"
        result = self._request("GET", endpoint)

        return [
            {
                "name": f["Name"],
                "path": f["ServerRelativeUrl"],
                "size": f["Length"],
                "modified": f["TimeLastModified"],
                "url": f["__metadata"]["uri"]
            }
            for f in result.get("d", {}).get("results", [])
        ]

    def download_file(self, file_path: str) -> Tuple[bytes, dict]:
        """Download file and return content with metadata."""
        # Get metadata
        meta_endpoint = f"web/GetFileByServerRelativeUrl('{file_path}')"
        metadata = self._request("GET", meta_endpoint)

        # Get content
        url = f"{self.site_url}/_api/web/GetFileByServerRelativeUrl('{file_path}')/$value"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.content, metadata.get("d", {})

    def upload_file(
        self,
        folder_path: str,
        file_name: str,
        content: bytes,
        overwrite: bool = True
    ) -> dict:
        """Upload file to folder."""
        endpoint = (
            f"web/GetFolderByServerRelativeUrl('{folder_path}')"
            f"/Files/add(url='{file_name}',overwrite={'true' if overwrite else 'false'})"
        )

        headers = self.headers.copy()
        headers["Content-Type"] = "application/octet-stream"
        headers["X-RequestDigest"] = self.get_form_digest()

        url = f"{self.site_url}/_api/{endpoint}"
        response = requests.post(url, headers=headers, data=content)
        response.raise_for_status()

        return response.json().get("d", {})

    # ============ LIST OPERATIONS ============

    def get_lists(self, site_path: str = "") -> list[dict]:
        """Get all lists in site."""
        endpoint = "web/lists?$select=Title,Id,ItemCount,BaseTemplate"
        result = self._request("GET", endpoint)

        return [
            {
                "title": lst["Title"],
                "id": lst["Id"],
                "item_count": lst["ItemCount"],
                "template": lst["BaseTemplate"]
            }
            for lst in result.get("d", {}).get("results", [])
        ]

    def get_list_items(
        self,
        list_title: str,
        filter_query: str = None,
        top: int = 100
    ) -> list[dict]:
        """Get items from a list."""
        endpoint = f"web/lists/GetByTitle('{list_title}')/items?$top={top}"
        if filter_query:
            endpoint += f"&$filter={filter_query}"

        result = self._request("GET", endpoint)
        return result.get("d", {}).get("results", [])

    def create_list_item(self, list_title: str, fields: dict) -> dict:
        """Create new list item."""
        # Get entity type
        type_endpoint = f"web/lists/GetByTitle('{list_title}')?$select=ListItemEntityTypeFullName"
        type_result = self._request("GET", type_endpoint)
        entity_type = type_result["d"]["ListItemEntityTypeFullName"]

        # Create item
        endpoint = f"web/lists/GetByTitle('{list_title}')/items"
        data = {
            "__metadata": {"type": entity_type},
            **fields
        }

        result = self._request("POST", endpoint, data=data, require_digest=True)
        return result.get("d", {})

    # ============ SEARCH ============

    def search(self, query: str, row_limit: int = 50) -> list[dict]:
        """Search SharePoint using KQL."""
        encoded_query = requests.utils.quote(query)
        endpoint = (
            f"search/query?querytext='{encoded_query}'"
            f"&selectproperties='Title,Path,Author,LastModifiedTime,FileExtension'"
            f"&rowlimit={row_limit}"
        )

        result = self._request("GET", endpoint)

        rows = (
            result.get("d", {})
            .get("query", {})
            .get("PrimaryQueryResult", {})
            .get("RelevantResults", {})
            .get("Table", {})
            .get("Rows", {})
            .get("results", [])
        )

        items = []
        for row in rows:
            cells = {
                cell["Key"]: cell["Value"]
                for cell in row.get("Cells", {}).get("results", [])
            }
            items.append(cells)

        return items
```

### Running the MCP Server

```bash
# Set environment variables
export SHAREPOINT_URL="https://yourtenant.sharepoint.com/sites/yoursite"
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
export CERT_PATH="/path/to/certificate.pem"
export CERT_THUMBPRINT="your-cert-thumbprint"

# Run with stdio transport (for Claude Desktop, etc.)
python -m src.server

# Or run with HTTP transport
python -c "from src.server import mcp; mcp.run(transport='streamable-http', port=8000)"
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sharepoint": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/sharepoint-mcp-server",
      "env": {
        "SHAREPOINT_URL": "https://tenant.sharepoint.com/sites/site",
        "TENANT_ID": "your-tenant-id",
        "CLIENT_ID": "your-client-id",
        "CERT_PATH": "/path/to/cert.pem",
        "CERT_THUMBPRINT": "thumbprint"
      }
    }
  }
}
```

---

## Complete Code Examples

### Example 1: Document Search and Download Pipeline

```python
from sharepoint.client import SharePointClient

client = SharePointClient(
    site_url="https://contoso.sharepoint.com/sites/legal",
    tenant_id="...",
    client_id="...",
    cert_path="./cert.pem",
    cert_thumbprint="..."
)

# Search for contracts
results = client.search(
    query='ContentClass:STS_ListItem_DocumentLibrary FileExtension:pdf contract',
    row_limit=10
)

# Download each matching document
for doc in results:
    file_path = doc.get("Path", "").replace("https://contoso.sharepoint.com", "")
    if file_path:
        content, metadata = client.download_file(file_path)

        # Save locally
        local_name = metadata.get("Name", "unknown.pdf")
        with open(f"./downloads/{local_name}", "wb") as f:
            f.write(content)
        print(f"Downloaded: {local_name}")
```

### Example 2: Automated Document Processing with MCP

```python
@mcp.tool()
def process_documents_in_folder(
    folder_path: str,
    file_type: str = "pdf"
) -> dict:
    """
    Process all documents of a specific type in a folder.

    Args:
        folder_path: Path to the folder
        file_type: File extension to process

    Returns:
        Processing summary
    """
    files = sp_client.get_folder_files(folder_path)
    processed = []

    for file in files:
        if file["name"].lower().endswith(f".{file_type}"):
            content, metadata = sp_client.download_file(file["path"])

            # Process content (example: extract text, analyze, etc.)
            processed.append({
                "name": file["name"],
                "size": file["size"],
                "status": "processed"
            })

    return {
        "total_files": len(files),
        "processed_count": len(processed),
        "processed_files": processed
    }
```

### Example 3: List Synchronization

```python
@mcp.tool()
def sync_list_items(
    source_list: str,
    target_list: str,
    key_field: str = "Title"
) -> dict:
    """
    Synchronize items between two SharePoint lists.

    Args:
        source_list: Source list title
        target_list: Target list title
        key_field: Field to use as unique key

    Returns:
        Sync statistics
    """
    source_items = sp_client.get_list_items(source_list)
    target_items = sp_client.get_list_items(target_list)

    # Build lookup of existing items
    target_keys = {
        item.get(key_field): item
        for item in target_items
    }

    created = 0
    updated = 0

    for source_item in source_items:
        key = source_item.get(key_field)
        fields = {k: v for k, v in source_item.items()
                  if not k.startswith("_") and k != "Id"}

        if key not in target_keys:
            # Create new item
            sp_client.create_list_item(target_list, fields)
            created += 1
        else:
            # Update existing (implement update method)
            # sp_client.update_list_item(target_list, target_keys[key]["Id"], fields)
            updated += 1

    return {
        "source_count": len(source_items),
        "created": created,
        "updated": updated
    }
```

### Example 4: CAML Query for Complex Filtering

```python
def execute_caml_query(
    site_url: str,
    list_title: str,
    caml_query: str,
    headers: dict
) -> list[dict]:
    """Execute CAML query via REST API."""
    url = f"{site_url}/_api/web/lists/GetByTitle('{list_title}')/GetItems"

    # CAML must be wrapped in proper structure
    body = {
        "query": {
            "__metadata": {"type": "SP.CamlQuery"},
            "ViewXml": f"<View><Query>{caml_query}</Query></View>"
        }
    }

    headers_copy = headers.copy()
    headers_copy["X-RequestDigest"] = get_form_digest(site_url, headers["Authorization"].split()[-1])

    response = requests.post(url, headers=headers_copy, json=body)
    response.raise_for_status()

    return response.json().get("d", {}).get("results", [])

# Example: Complex date and user filtering
caml = """
<Where>
    <And>
        <Geq>
            <FieldRef Name='Created'/>
            <Value Type='DateTime'>2024-01-01T00:00:00Z</Value>
        </Geq>
        <Eq>
            <FieldRef Name='Status'/>
            <Value Type='Choice'>Active</Value>
        </Eq>
    </And>
</Where>
<OrderBy>
    <FieldRef Name='Created' Ascending='FALSE'/>
</OrderBy>
"""

results = execute_caml_query(site_url, "Documents", caml, headers)
```

---

## Best Practices

### Authentication
- **Always use certificate authentication** for app-only access to SharePoint REST API
- Store certificates securely (Azure Key Vault recommended)
- Implement token caching and refresh logic
- Use `Sites.Selected` permission for granular access control

### Performance
- **Use batch requests** for multiple operations
- Implement **pagination** for large result sets
- Use **delta queries** instead of full syncs
- Cache form digest values (valid for 30 minutes)
- Use `$select` to retrieve only needed fields

### Reliability
- Implement **exponential backoff** for throttling
- Monitor `RateLimit-*` headers proactively
- Handle all HTTP error codes appropriately
- Log API calls for debugging

### Security
- Never store credentials in code
- Use environment variables or secret managers
- Validate and sanitize all user inputs
- Implement proper error handling without exposing details

### MCP Server Design
- Keep tools focused and single-purpose
- Provide clear, detailed docstrings
- Return structured, consistent responses
- Handle errors gracefully with informative messages

---

## Resources

### Official Documentation
- [SharePoint REST API Reference](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service)
- [Microsoft Graph SharePoint API](https://learn.microsoft.com/en-us/graph/api/resources/sharepoint)
- [SharePoint Authentication](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/sharepoint-admin-apis-authentication-and-authorization)
- [KQL Syntax Reference](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/keyword-query-language-kql-syntax-reference)
- [SharePoint Webhooks](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview-sharepoint-webhooks)
- [Avoiding Throttling](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online)

### Libraries
- [Office365-REST-Python-Client](https://github.com/vgrem/office365-rest-python-client) - Comprehensive Python library
- [MSAL Python](https://github.com/AzureAD/microsoft-authentication-library-for-python) - Microsoft Authentication Library
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official MCP SDK
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast MCP server framework

### MCP Server Examples
- [sekops-ch/sharepoint-mcp-server](https://github.com/sekops-ch/sharepoint-mcp-server) - TypeScript SharePoint MCP
- [Sofias-ai/mcp-sharepoint](https://github.com/Sofias-ai/mcp-sharepoint) - Python SharePoint MCP
- [DEmodoriGatsuO/sharepoint-mcp](https://github.com/DEmodoriGatsuO/sharepoint-mcp) - SharePoint MCP with Graph API

### Tutorials
- [SharePoint REST API Guide (Merge.dev)](https://www.merge.dev/blog/sharepoint-api)
- [SharePoint REST API Tutorial (SPGuides)](https://www.spguides.com/sharepoint-rest-api/)
- [Building MCP Servers with FastMCP](https://gofastmcp.com/tutorials/create-mcp-server)
- [Azure AD App Registration for SharePoint](https://learn.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread)

---

## License

This documentation is provided for educational purposes. Refer to Microsoft's official documentation for the most up-to-date API specifications.

## Contributing

Contributions welcome! Please submit issues and pull requests for improvements.
