<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://aistudio-preprod.corp.google.com/apps/b6680d9a-8a7e-41c4-8834-3450047ff461

## Run Locally


### Prerequisites
- Node.js
- [uv](https://github.com/astral-sh/uv) (for backend)

### Setup & Run
1. **Frontend**:
   ```bash
   npm install
   npm run dev
   ```

2. **Backend**:
   ```bash
   cd backend
   uv sync
   uv run main.py
   ```

3. **Secrets**:
   Ensure you have a `.env` file in the root directory with your keys:
   ```env
   GEMINI_API_KEY=...
   GOOGLE_API_KEY=...
   ```

