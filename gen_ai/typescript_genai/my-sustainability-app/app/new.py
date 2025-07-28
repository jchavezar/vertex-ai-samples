# backend.py - Add these imports at the top
from fastapi.middleware.cors import CORSMiddleware

# ... (keep existing imports and code)

app = FastAPI(
    title="Agent Workflow API",
    description="API to invoke the multi-agent search and analysis workflow."
)

# --- Add CORS Middleware ---
origins = [
    "http://localhost:3000",  # Your Next.js frontend origin
    "http://localhost",  # Sometimes needed depending on browser/setup
    # Add any other origins if necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# --- End CORS Middleware ---


# ... (rest of your FastAPI code: models, endpoint, etc.)
