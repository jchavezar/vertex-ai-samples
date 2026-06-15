# Visual Interface & UX Specification: Yazdani Architectural Grid

This document defines the layout specifications and visual standards for the **SharePoint Restructure Portal**, matching the minimalistic engineering-drafting aesthetic of *Yazdani Studio of CannonDesign*.

---

## 1. Interface Grid Structural Layout

Below is the ASCII structural map representing the dashboard, queue catalog, slided-up metadata detail drawer, right side AI conversational drawer, and bottom live log console terminal. This corresponds to the zero-border, minimal grid specification.

```text
+---------------------------------------------------------------------------------------+
|                                  YAZDANI STUDIO HEADER                                |
|  [PROJECT: SharePoint Restructure Portal]                 [IDENTITY: Config / User]  |
+-------------------------------------------------------------+-------------------------+
|                                                             |                         |
|   LEFT PANE: WORKSPACE (Document / Ontology Queue)          | RIGHT PANE: CHAT DRAWER |
|                                                             |                         |
|   +-----------------------------------------------------+   | [Aether AI Console]     |
|   | TAB: Document Queue  | TAB: Dynamic Ontology Map   |   |                         |
|   +-----------------------------------------------------+   | > User: "How are..."    |
|   | [Doc Card 1] CONF: 92% | [Approved]                 |   |                         |
|   | [Doc Card 2] CONF: 45% | [PII Warning] -> PENDING QA|   | > Aether AI:            |
|   | [Doc Card 3] CONF: 88% | [Approved]                 |   | "According to client..."|
|   |                                                     |   |                         |
|   |                                                     |   | [LATENCY: 0.55s]        |
|   |                                                     |   | [MODEL: GEMINI 3.5]     |
|   |                                                     |   |                         |
|   +-----------------------------------------------------+   |                         |
|   | MULTIMODAL DETAIL drawer (SLIDED UP)                |   |                         |
|   | [Doc Card 2] - Correct tags / Override / Approve    |   |                         |
|   +-----------------------------------------------------+   |                         |
+-------------------------------------------------------------+-------------------------+
|  BOTTOM TERMINAL CONSOLE: PACED CRAWLER LOGS                                          |
|  [10:20:39] Fetching directory folders mapping recursively...                         |
|  [10:21:07] Skipping already-indexed file: Annual Report 2025.pdf (FR04)              |
|  [10:21:17] Ontology extracted: type=PwC Operational File, subtype=PwC Thought...     |
+---------------------------------------------------------------------------------------+
```

---

## 2. Layout Specifications

### Canvas Grid Dimensions
*   **Root Window bounds:** Height locked at `100vh`, width at `100vw`. No global browser scrollbars.
*   **Header:** Fixed `80px` height at the top. Provides project identifiers and the **Identity Context** configuration dropdown.
*   **Main Workspace:** Flex container with `flex-direction: row` that takes up the remaining viewport space.
    *   **Left Column (Document/Ontology Queue):** Width is responsive (`flex: 1`). Houses the switchable tab views.
    *   **Right Column (Aether AI Chat Drawer):** Fixed at `480px` width. Prevents resizing to maintain console proportions.
*   **Bottom Terminal Console:** Fixed `192px` height, stretched full width. Shows green crawler logs.

### Geometric Restraints
*   **Borders:** All horizontal, vertical, and block dividers are strictly `0.5px` width with color value `#d8d6d0`.
*   **Corner Radii:** Zero rounding. All CSS properties must use `border-radius: 0px !important`.

### Color Values
*   **Core Background:** `#faf9f6` (Alabaster Warm White)
*   **Side Panels & Input Fields:** `#f4f3ef` (Warm Sand/Gray)
*   **Body & Header Text:** `#1a1a19` (Deep Charcoal Black)
*   **Metadata Labels:** `#7c7a75` (Muted Technical Gray)
*   **Terminal Background:** `#111111` (Deep Carbon Charcoal)
*   **Terminal Logs:** `#34d399` (System Green / Tailwind `green-400`)

---

## 3. Interaction Mechanics

1.  **Tab Navigation:** 
    *   Clicking **Document Queue** vs **Dynamic Ontology Map** changes the contents of the left pane dynamically without reloading.
    *   Selected tabs show an underline offset indicator: `border-b-2 border-b-[#1a1a19]`.
2.  **Multimodal detail views:** 
    *   Clicking a document card triggers the detail card sliding up at the bottom of the left pane (taking up `320px` height).
    *   Metadata fields in this card can be modified directly and committed by clicking **Approve Tags**.
3.  **Aether AI Conversational Console:**
    *   Entering text and submitting triggers a typing/searching state (`Searching index... █`).
    *   Responses are printed line-by-line using a left vertical accent border (`border-l border-[#1a1a19]`).
    *   Completed responses append a permanent technical footer tracking response latency and region details (e.g. `[LATENCY: 0.55s] [MODEL: GEMINI 3.5 FLASH // REGION: global]`).
