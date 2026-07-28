# StreamAssist Federated Sync Portal 🚀

This is a premium, fully-synchronized custom integration for **Vertex AI Search (Discovery Engine)** and **SharePoint Federated Search Connectors**. 

It implements the latest sync specs including domain allowlisting (Step 2), engine authorization synchronization (Step 5), and clean revoke/expired routines (Step 6).

---

## 🎨 Premium Capabilities
* **Full Engine State Synchronization:** Instead of storing tokens only in the database, the backend calls `getEngineUserData` and `updateEngineUserData` (Steps 5 & 6) to keep OOTB Search apps and custom portals perfectly in sync.
* **COOP Silent Callback Polling:** Implements the silent polling fallback hook on the frontend (`App.tsx`) to bypass Cross-Origin Opener Policy (COOP) blocks when the parent window and popup origins differ.
* **Active Pipeline Visualizer:** Features a real-time side-panel that visualizes WIF tokens, Consent Popups, and REST transactions as they occur.

---

## 🚀 Setup & Execution

### 1. Backend Setup

1. Copy and rename the environment template:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Populate the parameters in `backend/.env` with your GCP Project, WIF, and MSAL Credentials.
3. Run the backend using `uvicorn`:
   ```bash
   cd backend
   python -m pip install -e .
   python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload
   ```

### 2. Frontend Setup

1. Create a `frontend/.env` file:
   ```env
   VITE_CLIENT_ID=your-microsoft-portal-app-client-id
   VITE_TENANT_ID=your-microsoft-directory-tenant-id
   ```
2. Launch the Vite hot-reloading dev server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open your browser to `http://localhost:5174`.
