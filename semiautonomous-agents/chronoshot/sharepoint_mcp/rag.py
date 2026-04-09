"""Gemini 2.0 Flash Q&A with stuffed document context."""

from google import genai
from google.genai.types import GenerateContentConfig

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """You are a document analysis assistant. Answer questions based ONLY on the provided documents.
Be concise and specific. Include exact numbers, names, dates, and percentages when available.
Quote specific values directly from the documents. If the answer is not in the documents, say "Not found in documents."
Do not add qualifiers or hedging — give direct answers."""


def create_qa_chain(documents: dict[str, str]):
    """Create a Q&A function with pre-loaded document context.

    Args:
        documents: {filename: text_content} from parser.parse_all()

    Returns:
        Callable that takes a question string and returns an answer string.
    """
    context = "\n\n---\n\n".join(
        f"## Document: {name}\n\n{text}" for name, text in documents.items()
    )

    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    config = GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1,
        max_output_tokens=500,
    )

    def answer(question: str) -> str:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"{context}\n\n---\n\nQuestion: {question}\n\nAnswer:",
            config=config,
        )
        return response.text

    return answer
