# Analyst Copilot Workflow Test Script

This script outlines the steps to verify the premium Analyst Copilot features, including the Strategist UI and the Full-Overlay maximization.

## Prerequisites
- Backend running on `8001`
- Frontend running on `5173`
- Environment variables configured for FactSet/Gemini

## Test Cases

### 1. Full-Overlay Terminal Maximization
- **Action**: Open the dashboard and click the 'Maximize' button (angled arrows) on the terminal header.
- **Expected Result**: 
    - The terminal expands to cover the entire right area.
    - The left boundary is flush with the sidebar (~260px).
    - The dashboard background is completely obscured.
- **Verification**: Check for ~8px padding on top, bottom, and right edges.

### 2. Strategist Mode: Macro Pulse
- **Action**: Ask "What is the market pulse for NVDA?" or "Consult the analyst copilot on semiconductor trends."
- **Expected Result**:
    - The response should include a 'Macro Perspective' overview.
    - A clickable **Pulse Icon** (Zap/Table) should appear near headers like "Market Overview & Ratings".
- **Interaction**: Click the icon to open the **Analysis Overlay**.

### 3. Integrated Analysis Overlay (Interactive Tables)
- **Action**: Ask "Give me a peer pack for AMD, NVDA, and AVGO."
- **Expected Result**:
    - Structured data is returned.
    - Click the smart icon in the message.
    - A premium side-panel overlays the chat (or splits the view) showing the `PeerPackGrid`.
- **Verification**: Check for interactive hover states and clear "Consensus" vs "Price Target" data.

### 4. Execution Topology visibility
- **Action**: While in a complex chat, click the 'Graph' tab or 'View Graph' button.
- **Expected Result**:
    - The Topology Overlay appears on top of the chat results.
    - It uses a deep blur background (`backdrop-blur-3xl`).
    - Z-index is high enough to not be cut off by chat messages.

## Troubleshooting
- If cards don't render: Check `analyst_copilot.py` logs to ensure JSON is being returned in the `[STRUCTURED_DATA:...]` format.
- If maximizing fails: Check `App.tsx` and `ChatContainer.tsx` for layout conflicts.
