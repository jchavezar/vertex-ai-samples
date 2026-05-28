## Work IQ SharePoint MCP — tool surface, auth, limits

Captured 2026-05-27 from the [Microsoft Learn reference](https://learn.microsoft.com/en-us/microsoft-agent-365/mcp-server-reference/sharepoint). Status: **PREVIEW**. Tool names and parameters may change.

### Server identity

| | |
|---|---|
| Server ID | `mcp_SharePointRemoteServer` |
| Display name | Work IQ SharePoint MCP Server (Preview) |
| Version | 1.0.2 (per M365 admin panel, 2026-05-27) |
| Real URL | `https://agent365.svc.cloud.microsoft/agents/servers/mcp_SharePointRemoteServer` |
| Docs URL (stale) | `https://agent365.svc.cloud.microsoft/agents/tenants/{tenantId}/servers/mcp_SharePointRemoteServer` |

> The MS Learn docs show the URL with a `/tenants/{tenantId}/` segment. That is stale — the admin panel for the sockcop tenant exposes the no-tenant-path URL above. Tenant is resolved from the caller's Entra bearer token.

### Tools, grouped

#### Site discovery (3)
| Tool | Required params | Notes |
|---|---|---|
| `findSite` | — | Optional `searchQuery`; defaults to top 20 accessible sites. |
| `getSiteByPath` | `hostname`, `serverRelativePath` | Exact URL resolution. |
| `listSubsites` | `siteId` | Child sites under a parent. |

#### Document libraries / folders (4)
| Tool | Required params | Notes |
|---|---|---|
| `listDocumentLibrariesInSite` | — | `siteId` optional (defaults to `root`). |
| `getDefaultDocumentLibraryInSite` | — | `siteId` optional. |
| `getFolderChildren` | `documentLibraryId` | Returns top 20 items. |
| `findFileOrFolder` | `searchQuery` | Cross-tenant DriveItem search. |

#### File metadata (2)
| Tool | Required params | Notes |
|---|---|---|
| `getFileOrFolderMetadata` | `fileOrFolderId`, `documentLibraryId` | |
| `getFileOrFolderMetadataByUrl` | `fileOrFolderUrl` | User must already have explicit permission. |

#### File read (2)  — capped at **≤5 MB**
| Tool | Required params | Notes |
|---|---|---|
| `readSmallTextFile` | `fileId`, `documentLibraryId` | Raw text. |
| `readSmallBinaryFile` | `fileId`, `documentLibraryId` | Base64-encoded. |

#### File write (3) — capped at **≤5 MB**
| Tool | Required params |
|---|---|
| `createSmallTextFile` | `filename`, `contentText`, `documentLibraryId` |
| `createSmallBinaryFile` | `filename`, `base64Content`, `documentLibraryId` |
| `createFolder` | `folderName`, `documentLibraryId` |

#### File / folder mutation (3)
| Tool | Required params | Notes |
|---|---|---|
| `renameFileOrFolder` | `documentLibraryId`, `fileOrFolderId`, `newFileOrFolderName` | `etag` optional. |
| `deleteFileOrFolder` | `documentLibraryId`, `fileOrFolderId` | `etag` optional. |
| `uploadFileFromUrl` | `sourceUrl`, `destinationDocumentLibraryId` | Source must be SP or OneDrive URL. |

#### Async move / copy (3)
| Tool | Required params | Notes |
|---|---|---|
| `moveFileOrFolder` | `sourcedoclibid`, `sourcefileid`, `destdoclibid`, `destfolderid` | Async. |
| `copyFileOrFolder` | `sourcedoclibid`, `sourcefileid`, `destdoclibid`, `destfolderid` | Async. |
| `checkOperationStatus` | `operationToken` | Poll. |

#### Sharing + sensitivity (3)
| Tool | Required params | Notes |
|---|---|---|
| `shareFileOrFolder` | `documentLibraryId`, `fileOrFolderId`, `recipientEmails`, `roles` | `roles` = ['read', 'write']. |
| `sendInviteForList` | `listId`, `recipientEmails`, `role` | List-level sharing. |
| `setSensitivityLabelOnFile` | `documentLibraryId`, `fileId`, `sensitivityLabelId` | Empty string removes the label. |

#### Lists (7)
`listLists`, `createList`, `deleteList`, `listListItems`, `getListItem`, `createListItem`, `updateListItem`, `deleteListItem`.

#### Columns (4)
`listColumns`, `createColumn`, `updateColumn`, `deleteColumn` — supports many types (text, number, choice, dateTime, boolean, user, lookup, calculated, term, geolocation, …).

---

### Auth model

- **Microsoft-managed.** The hosted MCP runs inside Microsoft Agent 365 and authenticates the caller via the tenant's Entra identity. GE forwards the user's bearer token; Agent 365 validates it against the tenant binding.
- ACL fidelity is at SharePoint's standard delegated-permissions level — same as a user clicking around in SharePoint Online.
- No per-tenant OAuth app to provision on the SP side (vs. Option 1, which needs an Entra app with Sites.Read.All etc.).

---

### Hard limits worth quoting in the comparison table

| Limit | Value |
|---|---|
| Per-file read / write size | **5 MB** |
| Folder listing | Top 20 children |
| `findFileOrFolder` / `findSite` | Top 20 results |
| Copy / move | Asynchronous (must poll `checkOperationStatus`) |
| `uploadFileFromUrl` source | Must be SharePoint or OneDrive URL |

---

### Mapping back to the 7 canonical tools used for eval scoring

The eval scores both options on the same 7-tool surface. The hosted MCP is a superset; the table below maps each canonical tool to the hosted equivalent the eval runner should call.

| Canonical tool (eval) | Hosted Work IQ equivalent |
|---|---|
| `search(query)` | `findFileOrFolder(searchQuery=query)` |
| `fetch(id)` | `getFileOrFolderMetadata` → `readSmallTextFile` / `readSmallBinaryFile` (if ≤5 MB) |
| `list_sites()` | `findSite()` |
| `list_libraries(site_id)` | `listDocumentLibrariesInSite(siteId)` |
| `list_files(library_id, folder?)` | `getFolderChildren(documentLibraryId, parentFolderId)` |
| `read_file(file_id)` | `readSmallTextFile` / `readSmallBinaryFile` (size-capped) |
| `search_content(query)` | `findFileOrFolder(searchQuery=query)` *(no separate full-text endpoint — relies on SharePoint Search)* |

The eval should record cases where the hosted tool's 5 MB cap or top-20 ceiling causes a different verdict than option 1.
