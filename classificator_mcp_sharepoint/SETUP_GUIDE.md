# How to Get SharePoint Credentials for the `.env` File

You need 5 values. Here is how to get each one.

## Part 1: App Registration (Tenant, Client, Secret)

1.  **Go to Azure Portal**: [https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps)
2.  Click **"New registration"**.
    *   **Name**: `SharePoint-Metadata-Extractor` (or similar).
    *   **Supported account types**: "Accounts in this organizational directory only (Single tenant)".
    *   Click **Register**.

3.  **Get IDs from the "Overview" page**:
    *   **`TENANT_ID`**: Copy "Directory (tenant) ID".
    *   **`CLIENT_ID`**: Copy "Application (client) ID".

4.  **Get Client Secret**:
    *   In the left menu, click **"Certificates & secrets"**.
    *   Click **"New client secret"**.
    *   Description: `v1 key`; Expires: `180 days` (or as preferred).
    *   Click **Add**.
    *   **`CLIENT_SECRET`**: **IMPORTANT:** Copy the "Value" (not Secret ID) immediately. You won't see it again.

## Part 2: Grant Permissions (Critical!)

1.  In the left menu of your App, click **"API permissions"**.
2.  Click **"Add a permission"** -> **"Microsoft Graph"** -> **"Application permissions"**.
    *   *Note: Make sure you choose "Application", not "Delegated".*
3.  Search for and check these boxes:
    *   `Sites.Read.All`
    *   `Files.Read.All`
4.  Click **Add permissions**.
5.  **CRITICAL STEP**: Usage requires Admin Consent.
    *   Click the checkmark button **"Grant admin consent for [Your Org]"** at the top of the list.
    *   Confirm "Status" shows a green checkmark for both permissions.

## Part 3: Find Site ID and Drive ID

You can find these using your browser and the Microsoft Graph API.

### 1. Find `SITE_ID`
The format is: `hostname,sId,wId`.

**Method A: Browser URL Trick**
If your SharePoint URL is: `https://mycompany.sharepoint.com/sites/Marketing`

1.  Log in to [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) with your business account.
2.  Run this GET request:
    ```text
    https://graph.microsoft.com/v1.0/sites/mycompany.sharepoint.com:/sites/Marketing
    ```
    *(Replace `mycompany` and `Marketing` with your actual values)*
3.  **`SITE_ID`**: Copy the `id` field from the response.
    *   *Example:* `mycompany.sharepoint.com,abc-123-guid,xyz-789-guid`

### 2. Find `DRIVE_ID`
Once you have the `SITE_ID`:

1.  In Graph Explorer, run this GET request:
    ```text
    https://graph.microsoft.com/v1.0/sites/{YOUR_SITE_ID}/drives
    ```
2.  Look for the drive where your documents are (usually named "Documents" or "Shared Documents").
3.  **`DRIVE_ID`**: Copy the `id` string for that drive.

---

## Summary for `.env`
- `TENANT_ID`: From Azure App Overview
- `CLIENT_ID`: From Azure App Overview
- `CLIENT_SECRET`: From Certificates & secrets
- `SITE_ID`: From Graph API query
- `DRIVE_ID`: From Graph API query
