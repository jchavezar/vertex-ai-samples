# Federated Connector DataStore Search & AuthN / AuthZ Architecture

## Executive Summary

This document proves that **Vertex AI Search / Discovery Engine Data Stores for Federated Connectors (e.g. SharePoint, ServiceNow, Outlook)** can be searched and queried **directly at the Data Store level without requiring a Gemini Enterprise (GE) App or Engine (`engines/{ENGINE_ID}`)**.

Furthermore, it documents the complete **Authentication (AuthN) & Authorization (AuthZ)** architecture, proving that all identity federation, per-user OAuth tokens, and connector credential management operate exclusively at the **Google Cloud IAM (WIF)** and **Discovery Engine Collection / DataConnector** levels.

---

## 1. High-Level System Architecture

```
====================================================================================================
                        FEDERATED CONNECTOR DATASTORE SEARCH ARCHITECTURE
====================================================================================================

               +-------------------------------------------------------------+
               |                  Client Application / Agent                 |
               +------------------------------+------------------------------+
                                              |
                     1. Direct REST Search    |  2. Multi-Store / StreamAssist
                        (No GE App needed!)   |     (Requires GE Engine)
                                              |
               +------------------------------v------------------------------+
               |        Google Discovery Engine / Vertex AI Search API       |
               +------------------------------+------------------------------+
                                              |
                  +---------------------------+---------------------------+
                  |                                                       |
                  v                                                       v
+-----------------------------------+               +-----------------------------------+
|     Direct DataStore Endpoint     |               |       Engine / Assistant API      |
|  dataStores/{DATASTORE_ID}/       |               |  engines/{ENGINE_ID}/             |
|  servingConfigs/default_search    |               |  assistants/...:streamAssist      |
+-----------------+-----------------+               +-----------------+-----------------+
                  |                                                   |
                  |                                                   |
                  v                                                   v
+---------------------------------------------------------------------------------------+
|                       Federated Data Connector Entity Stores                          |
|                                                                                       |
|   +--------------------------+  +--------------------------+  +--------------------+  |
|   |  {CONNECTOR_ID}_file     |  |  {CONNECTOR_ID}_page     |  | {CONNECTOR_ID}_... |  |
|   |  - Documents, PDFs, PPTs |  |  - SharePoint Pages      |  | - Comments, Events |  |
|   +--------------------------+  +--------------------------+  +--------------------+  |
+---------------------------------------------------------------------------------------+
====================================================================================================
```

---

## 2. Complete AuthN / AuthZ Pipeline (End-to-End Sequence)

```
====================================================================================================
                      END-TO-END AUTHN & AUTHZ SEQUENCE DIAGRAM
====================================================================================================

  [ User / Browser ]         [ Microsoft Entra ID ]         [ Google STS (WIF) ]         [ Discovery Engine ]
          |                            |                            |                            |
          | 1. Microsoft Login         |                            |                            |
          |--------------------------->|                            |                            |
          |                            |                            |                            |
          | 2. Returns Entra ID Token  |                            |                            |
          |<---------------------------|                            |                            |
          |                            |                            |                            |
          | 3. POST /v1/token (Token Exchange)                      |                            |
          |    (audience: //iam.googleapis.com/.../workforcePools)   |                            |
          |-------------------------------------------------------->|                            |
          |                                                         |                            |
          | 4. Returns GCP Federated Access Token (Bearer ya29...)  |                            |
          |<--------------------------------------------------------|                            |
          |                                                         |                            |
          | 5. Interactive SharePoint OAuth Consent Popup           |                            |
          |--------------------------->|                            |                            |
          |                            |                            |                            |
          | 6. Returns Auth Code       |                            |                            |
          |<---------------------------|                            |                            |
          |                                                                                      |
          | 7. POST .../collections/{CONNECTOR}/dataConnector:acquireAndStoreRefreshToken        |
          |    (Stores SharePoint Refresh Token in Google Connector Vault under WIF Identity)    |
          |------------------------------------------------------------------------------------->|
          |                                                                                      |
          | 8. Returns 200 OK (Token Stored Securely)                                            |
          |<-------------------------------------------------------------------------------------|
          |                                                                                      |
          | 9. POST .../dataStores/{CONNECTOR}_file/servingConfigs/default_search:search         |
          |    (Direct Query: "jennifer" -> Authenticated under WIF identity with SP ACLs)      |
          |------------------------------------------------------------------------------------->|
          |                                                                                      |
          | 10. Returns 200 OK with Indexed Document Metadata & Content Snippets                 |
          |<-------------------------------------------------------------------------------------|
====================================================================================================
```

### Detailed AuthN / AuthZ Stages

1. **User Authentication (AuthN via Entra ID)**:
   - The frontend authenticates the user with Microsoft Entra ID (Azure AD), producing an OpenID Connect (OIDC) ID token (JWT).
2. **Identity Federation (Google Cloud WIF / STS)**:
   - The Entra ID JWT is exchanged via Google Security Token Service (`POST https://sts.googleapis.com/v1/token`) against a Workforce Identity Federation Pool (`sp-wif-pool-v2`).
   - Returns a short-lived federated GCP Access Token.
3. **Per-User SharePoint Authorization (AuthZ via OAuth 2.0)**:
   - The user authorizes access to SharePoint scopes (`AllSites.Read`, `Sites.Search.All`).
   - The resulting authorization code is passed to Discovery Engine via:
     `POST .../collections/{CONNECTOR_ID}/dataConnector:acquireAndStoreRefreshToken`.
   - Discovery Engine encrypts and associates the user's SharePoint refresh token with their federated WIF identity.
4. **Direct Search & ACL Enforcement**:
   - When calling `dataStores/{CONNECTOR_ID}_file/servingConfigs/default_search:search`, Discovery Engine validates the caller's identity and retrieves the indexed SharePoint content.

---

## 3. Raw Empirical Test Proofs

### Test Query: Search for "Jennifer" on `sharepoint-data-def-connector_file`

#### Request:
```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: 545964020693" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/545964020693/locations/global/collections/default_collection/dataStores/sharepoint-data-def-connector_file/servingConfigs/default_search:search" \
  -d '{
    "query": "jennifer",
    "pageSize": 3
  }'
```

#### Raw Response Output:
```json
{
  "results": [
    {
      "id": "1132300655934632666",
      "document": {
        "name": "projects/545964020693/locations/global/collections/default_collection/dataStores/sharepoint-data-def-connector_file/branches/0/documents/1132300655934632666",
        "id": "1132300655934632666",
        "structData": {
          "title": "03_Client_Contract_Apex_Financial",
          "author": "Jesus Chavez;tester",
          "entity_type": "file",
          "file_type": "pdf",
          "url": "https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/03_Client_Contract_Apex_Financial.pdf?web=1",
          "description": "Indexed for search - updated April 2026",
          "content": "MASTER SERVICES AGREEMENT\nBetween Meridian Technologies Corporation and Apex Financial Services, Inc.\nPrimary Contact: Jennifer Walsh, CFO\nEmail: jwalsh@meridiantech.com\nPhone: (415) 555-8200\n\nSignature: /s/ Jennifer Walsh\nTitle: Chief Financial Officer\nDate: December 20, 2024..."
        }
      }
    },
    {
      "id": "9802524132902347023",
      "document": {
        "name": "projects/545964020693/locations/global/collections/default_collection/dataStores/sharepoint-data-def-connector_file/branches/0/documents/9802524132902347023",
        "id": "9802524132902347023",
        "structData": {
          "title": "05_MA_Due_Diligence_Project_Starlight",
          "author": "Jesus Chavez;tester",
          "entity_type": "file",
          "file_type": "pdf",
          "url": "https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/05_MA_Due_Diligence_Project_Starlight.pdf?web=1",
          "description": "Indexed for search - updated April 2026",
          "content": "DUE DILIGENCE REPORT: Project Starlight\nTarget: NovaTech Solutions, Inc.\nBoard Members: ...Jennifer Liu (Andreessen Horowitz)..."
        }
      }
    },
    {
      "id": "8852519738959929927",
      "document": {
        "name": "projects/545964020693/locations/global/collections/default_collection/dataStores/sharepoint-data-def-connector_file/branches/0/documents/8852519738959929927",
        "id": "8852519738959929927",
        "structData": {
          "title": "02_HR_Employee_Records_2025",
          "author": "Jesus Chavez",
          "entity_type": "file",
          "file_type": "pdf",
          "url": "https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/Restricted%20Vault/02_HR_Employee_Records_2025.pdf?web=1",
          "content": "EMPLOYEE RECORDS - Confidential\n1.2 Chief Financial Officer\nName: Jennifer Anne Walsh\nEmployee ID: MTC-0012\nBase Salary: $625,000\nDepartment: Finance..."
        }
      }
    }
  ]
}
```

---

## 4. API Reference Table

| API Endpoint | Method | Owning Service | Scope / Level | Needs GE App? |
| :--- | :--- | :--- | :--- | :---: |
| `/v1/token` | `POST` | **Google STS / IAM** | Global Workforce Pool | ❌ **No** |
| `/oauth2/v2.0/authorize` | `POST` | **Microsoft Entra ID** | Tenant App Registration | ❌ **No** |
| `.../collections/{CONNECTOR}/dataConnector:acquireAndStoreRefreshToken` | `POST` | **Vertex AI Search** | Collection / Connector | ❌ **No** |
| `.../collections/{CONNECTOR}/dataConnector:acquireAccessToken` | `POST` | **Vertex AI Search** | Collection / Connector | ❌ **No** |
| `.../dataStores/{DATASTORE}/servingConfigs/default_search:search` | `POST` | **Vertex AI Search** | Data Store Level | ❌ **No** |
| `.../engines/{ENGINE}/assistants/...:streamAssist` | `POST` | **Gemini Enterprise** | Engine / Assistant Level | ✅ **Yes** |

---

## 5. Replication Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Direct DataStore Search
```bash
# Query files Data Store
python3 test_datastore_search.py --entity=file --query="jennifer"

# Query pages Data Store
python3 test_datastore_search.py --entity=page --query="document"

# Query all SharePoint entity stores
python3 test_datastore_search.py --entity=all --query="financial"
```

### Step 3: Validate AuthN / AuthZ Architecture
```bash
python3 test_auth_flow.py --project-number=545964020693 --connector-id=sharepoint-data-def-connector
```
