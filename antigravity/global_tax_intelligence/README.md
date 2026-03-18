# Global Tax Intelligence

Global Tax Intelligence is an advanced AI-driven tax research methodology and copilot designed to help tax professionals monitor, analyze, and gain actionable insights from global tax data, legislative changes, and corporate compliance documents.

## Features

![Dashboard](docs/dashboard.png)
![Chief Tax Copilot](docs/chat.webp)
![Document Search](docs/search.webp)

- **Chief Tax Copilot:** An interactive, floating conversational interface powered by `gemini-3.0-flash-lite-preview` that provides fast, precise answers to tax and regulatory questions.
- **Document Chat:** Ask questions directly against specific PDF documents and view the document side-by-side with the AI's responses.
- **Vertex AI Search (VAIS) Integration:** Powerful search over tax corpora with direct links to source documents.
- **Global Tax Dashboard:** High-level metrics, actionable insights, and industry impact analysis generated dynamically.
- **Premium UX:** A modern interface mimicking the future of tax tools, with glassmorphism, responsive components, and real-time streaming text generation.

## Zero-Leak Architecture

The application strictly enforces the **Zero-Leak Policy**:
- No secrets, API keys, or `.env` files are tracked in version control.
- Python dependencies are strictly managed using `uv`.

## Running Locally

To run the application locally:

1. Make sure to create a `.env` file at the root of the project with the required Vertex AI and Google Cloud credentials.
2. Start the backend:
   ```bash
   cd backend
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Start the frontend:
   ```bash
   npm install
   npm run dev
   ```

## Deployment

The application includes a `deploy.sh` script that automates the deployment to Google Cloud Run. It configures the service behind a Global External HTTPS Load Balancer, provisions a self-signed SSL certificate for immediate testing, and secures access using Identity-Aware Proxy (IAP) limited to an allowed administrator email.

```bash
chmod +x deploy.sh
./deploy.sh
```
