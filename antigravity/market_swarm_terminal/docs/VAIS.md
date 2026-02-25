# Vertex AI Search (VAIS) Integration Research

## Overview
This document details the findings from deep research and testing of the Vertex AI Search (formerly Discovery Engine) API for the `factset` engine. The goal is to integrate this search capability into the `stock-terminal` application to provide a rich, dynamic user experience for financial data discovery.

## API Configuration

**Endpoint:**
```
https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/factset/servingConfigs/default_search:search
```

**Method:** `POST`
**Authentication:** Bearer Token (Google Cloud IAM)
**Content-Type:** `application/json`

### Key Parameters
- `query` (string): The search query.
- `pageSize` (int): Number of results to return (default tested: 10).
- `queryExpansionSpec`: `{"condition": "AUTO"}` - Expands query terms automatically.
- `spellCorrectionSpec`: `{"mode": "AUTO"}` - Corrects typos in queries.
- `userInfo`: `{"timeZone": "America/Los_Angeles"}` - Context for time-sensitive queries.

## Python Integration
The following implementation uses standard Python libraries (`requests`, `google-auth`) to interact with the API. This is ready to be adapted into a FastAPI backend service.

### Prerequisites
- `requests`
- `google-auth`
- `google-auth-requests` (for cleaner token handling)

### Recommended Backend Service Code
```python
import os
import requests
import google.auth
from google.auth.transport.requests import Request
from typing import Dict, List, Any, Optional

# Configuration Constants
PROJECT_ID = "254356041555"
LOCATION = "global"
COLLECTION = "default_collection"
ENGINE = "factset"
SERVING_CONFIG = "default_search"
API_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}/engines/{ENGINE}/servingConfigs/{SERVING_CONFIG}:search"

class VertexSearchClient:
    def __init__(self):
        self.credentials, self.project = google.auth.default()
        self.session = requests.Session()

    def get_token(self) -> str:
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token

    def search(self, query: str, page_size: int = 10, offset: int = 0) -> Dict[str, Any]:
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "pageSize": page_size,
            "offset": offset,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            # "contentSearchSpec": {"summarySpec": {"summaryResultCount": 5}}, # Enable for summaries
            "userInfo": {"timeZone": "UTC"}
        }

        try:
            response = self.session.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"VAIS Search Failed: {e}")
            raise

# Usage Example
if __name__ == "__main__":
    client = VertexSearchClient()
    results = client.search("latest earnings Apple")
    print(results)
```

## Data Schema & Response Structure
The API returns a rich JSON structure. Below is the mapped schema for the `results` array, which is the primary data source for the UI.

### Root Response Fields
- `results`: Array of document objects (see below).
- `totalSize`: Integer, estimated total matches.
- `attributionToken`: String, required for logging/analytics if implemented.
- `nextPageToken`: String, for pagination.
- `semanticState`: String (e.g., `DISABLED`), indicates if semantic ranking was applied.

### Result Object Schema (`results[i].document.derivedStructData`)
This is where the actual content lives.

| Field | Type | Description | UX Use Case |
|-------|------|-------------|-------------|
| `title` | String | Document title | Primary display header card |
| `link` | String | Direct URL to resource | Clickable action |
| `formattedUrl` | String | Pretty-printed URL | Visual URL hint (e.g., breadcrumbs) |
| `htmlSnippet` | HTML String | Contextual snippet with `<b>` tags matching query | Description body with highlighting |
| `snippets` | Array | List of snippet objects (text & html) | Alternative description source |
| `pagemap` | Object | Metadata container (OpenGraph, Twitter Cards) | **Rich Media Integration** |

### Pagemap Schema (Rich Metadata)
The `pagemap` field is critical for a "cool dynamic UX". It contains scraped metadata.

- **`cse_thumbnail`**: Array of objects with `src`, `width`, `height`.
  - *UX Strategy:* Display this image as a thumbnail on the left of the search card.
- **`cse_image`**: High-res image from the page.
  - *UX Strategy:* Use for a detailed view or background blur.
- **`metatags`**: Array of key-value pairs (e.g., `og:description`, `twitter:title`, `creationdate`).
  - *UX Strategy:* Extract `og:site_name` or `author` for "Source" badges. Use `creationdate` to show "Freshness" (e.g., "2 days ago").

## UX Design Recommendations

### 1. The "Smart Card" Layout
Instead of a simple list, render each result as a structured card:
- **Header:** `title` (truncated to 2 lines).
- **Meta Row:** `displayLink` (or domain) • `creationdate` (parsed from metatags).
- **Body:** `htmlSnippet` (rendered safely to show bold matches).
- **Thumbnail:** If `pagemap.cse_thumbnail` exists, show a 80x80px rounded image.
- **Footer:** "Source: FactSet" (derived from domain or metatags).

### 2. Intelligent Filtering (Facets)
While the current query didn't request facets, VAIS supports them.
*Recommendation:* Future backend updates should request `facetSpecs` for fields like `fileFormat` (PDF vs HTML) or `date`.
- *UI:* "File Type" dropdown (PDF icon for `application/pdf`).

### 3. Generative Summary (Future)
The current response had an empty `summary`.
*Strategy:* Enable `summarySpec` in the request to get a Generative AI answer at the top of the search results (similar to Google's AI Overviews). This can be displayed in a "Key Insight" box above the result list.

### 4. Zero-Result State
If `totalSize` is 0, use the `spellCorrectionSpec` info (if available) to suggest: "Did you mean...?"

## Sample Response Snippet (Analyzed)
```json
{
  "title": "FactSet Earnings Insight",
  "link": "https://www.factset.com/earningsinsight",
  "snippet": "Key Metrics. • Earnings Scorecard: For Q4 2025...",
  "pagemap": {
    "cse_thumbnail": [{ "src": "https://.../image.jpg" }],
    "metatags": [{ "creationdate": "2026-01-16" }]
  }
}
```
*Analysis:* The `creationdate` confirms the data is fresh (Jan 2026). The `fileFormat` was PDF. The UI should show a PDF icon and "4 days ago".

## TypeScript / Frontend Integration
Using `VAIS` directly from the frontend (Client-Side) avoids the need for a separate proxy service, reducing latency and complexity, *provided* you have a secure mechanism to obtain an access token.

### Interfaces
These TypeScript interfaces map directly to the JSON schema discovered during the experiments.

```typescript
export interface VAISRequest {
  query: string;
  pageSize?: number;
  offset?: number;
  queryExpansionSpec?: { condition: "AUTO" | "DISABLED" };
  spellCorrectionSpec?: { mode: "AUTO" | "SUGGESTION_ONLY" };
  userInfo?: { timeZone: string };
}

export interface VAISResponse {
  results: VAISResult[];
  totalSize: number;
  attributionToken: string;
  nextPageToken?: string;
  semanticState?: string;
}

export interface VAISResult {
  id: string;
  document: {
    name: string;
    id: string;
    derivedStructData: VAISDocumentData;
  };
}

export interface VAISDocumentData {
  title: string;
  link: string;
  formattedUrl: string;
  htmlFormattedUrl?: string;
  displayLink?: string;
  snippets?: Array<{ snippet: string; htmlSnippet: string }>;
  htmlSnippet?: string; // Sometimes at root level
  pagemap?: {
    cse_thumbnail?: Array<{ src: string; width?: string; height?: string }>;
    cse_image?: Array<{ src: string }>;
    metatags?: Array<Record<string, string>>;
  };
  mime?: string; // e.g., "application/pdf"
  fileFormat?: string;
}
```

### Client Implementation
Use the native `fetch` API. 
*Note on Auth:* This client expects a valid OAuth 2.0 Access Token. In a production environment, this should be retrieved from a secure token exchange service or via a proxy to avoid exposing service account keys in the browser. For local dev/prototyping with the existing `LiveAPIContext`, ensure you have a valid token strategy.

```typescript
const PROJECT_ID = "254356041555";
const LOCATION = "global";
const COLLECTION = "default_collection";
const ENGINE = "factset";
const SERVING_CONFIG = "default_search";

const API_URL = `https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections/${COLLECTION}/engines/${ENGINE}/servingConfigs/${SERVING_CONFIG}:search`;

export class VertexSearchClient {
  private tokenProvider: () => Promise<string> | string;

  constructor(tokenProvider: () => Promise<string> | string) {
    this.tokenProvider = tokenProvider;
  }

  async search(query: string, options: Partial<VAISRequest> = {}): Promise<VAISResponse> {
    const token = await this.tokenProvider();
    
    const payload: VAISRequest = {
      query,
      pageSize: options.pageSize || 10,
      queryExpansionSpec: { condition: "AUTO" },
      spellCorrectionSpec: { mode: "AUTO" },
      userInfo: { timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone },
      ...options
    };

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`VAIS API Error ${response.status}: ${errorText}`);
    }

    return await response.json();
  }
}
```

## Conclusion
The Vertex AI Search `factset` engine is fully functional and returns high-quality, metadata-rich results. The Python implementation is straightforward. The key to the "dynamic UX" lies in parsing the `pagemap` for images and dates, and rendering the `htmlSnippet` effectively.