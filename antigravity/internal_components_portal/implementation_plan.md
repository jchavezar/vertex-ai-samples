# Implementation Plan: Action Layer & Governance Engine

This plan covers the integration of proactive governance, document manipulation, and multimodal asset generation into the Zero-Leak Security Proxy.

## 1. Goal
Transition the agent from a passive "Read-Only" proxy to an active "AI Governance Engine" that can secure sensitive data, browse enterprise repositories, and assist in document creation.

## 2. Technical Components

### A. Backend (SharePoint Action Layer)
- [x] **mcp_sharepoint.py**: Implement `move_item`, `upload_file`, `list_folder_contents`, and `get_special_folder`.
- [x] **agent.py**: 
    - Expose new tools: `secure_document_governance`, `browse_sharepoint_folder`, `update_sharepoint_document`, `generate_embedded_image`.
    - Update `ProjectCard` schema with `pii_detected` and `governance_recommendation`.
    - Update `INSTRUCTIONS` for the Governance Protocol.

### B. Frontend (Action Center UI)
- [x] **dashboardStore.ts**: Update interface to support governance state.
- [x] **ProjectCardWidget.tsx**: Add "PII Alert" UI and "Secure Now" action button.
- [ ] **App.tsx**: 
    - Add "Document Workspace" tab to the main navigation.
    - Implement the Workspace view allowing direct folder browsing.
- [ ] **WorkspaceView.tsx**: (New Component) Functional explorer for SharePoint items with "Modify with AI" capabilities.

### C. Creative Integration
- [ ] **Multimodal Action**: Link `generate_embedded_image` to a UI trigger for "Add AI Visualization" inside the document editor.

## 3. Testing & Verification (Validation Protocol)
- [ ] **Functional Test (PII)**: Query for a document known to contain PII. Verify `pii_detected` flag triggers and the "Secure Now" button appears.
- [ ] **Governance Test**: Execute "Secure Now" and verify the file is moved to the "Restricted Vault" via backend logs/SharePoint check.
- [ ] **Workspace Test**: Navigate to the new tab, browse root, and verify file listing.
- [ ] **Zero-Leak Test**: Ensure that even while modifying documents, no unmasked data enters the main chat or frontend state.

## 4. Rollback Plan
- [x] Git Checkpoint established at `CHKPNT: Multimodal Vision + Neural Markdown stable state`.
- Fast revert via `git checkout` if backend dependencies (Microsoft Graph scopes) cause 401/403 errors.
