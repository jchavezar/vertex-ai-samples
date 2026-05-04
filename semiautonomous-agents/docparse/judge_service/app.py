"""Judge service — direct REST API calls to avoid genai SDK truncation."""
from fastapi import FastAPI
from pydantic import BaseModel
import json
import logging
import requests
import google.auth
import google.auth.transport.requests

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Get credentials from Cloud Run service account (automatic)
credentials, project = google.auth.default()
PROJECT = project or "sharepoint-wif"

JUDGE_PROMPT = """You are an evaluator. Score this Q&A:

QUESTION: {q}
GROUND TRUTH: {gt}
ANSWER: {ans}

Return ONLY JSON:
{{"correctness": 0.0-1.0, "completeness": 0.0-1.0, "verdict": "correct"|"partial"|"wrong"|"refused", "reason": "one sentence"}}"""


class JudgeRequest(BaseModel):
    question: str
    ground_truth: str
    answer: str


def get_token():
    """Get access token from Cloud Run service account."""
    if not credentials.valid:
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
    return credentials.token


@app.post("/judge")
def judge(req: JudgeRequest):
    """Score via direct REST API call."""
    prompt = JUDGE_PROMPT.format(q=req.question, gt=req.ground_truth, ans=req.answer)

    url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT}/locations/global/publishers/google/models/gemini-2.5-flash:generateContent"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 500, "temperature": 0}
    }

    try:
        token = get_token()
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=30)
        r.raise_for_status()

        resp_data = r.json()

        # Extract text from ALL parts
        if "candidates" in resp_data and len(resp_data["candidates"]) > 0:
            parts = resp_data["candidates"][0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)

            # Clean markdown fences
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
                text = text.replace("```json", "").replace("```", "").strip()

            result = json.loads(text)
            return result
        else:
            logging.error(f"No candidates in response: {resp_data}")
            return {"correctness": 0, "completeness": 0, "verdict": "error", "reason": "No candidates"}

    except json.JSONDecodeError as e:
        # Return the FULL text so we can see what Gemini actually generated
        full_text = text if 'text' in locals() else 'N/A'
        return {
            "correctness": 0,
            "completeness": 0,
            "verdict": "error",
            "reason": f"Parse fail pos {e.pos}",
            "gemini_response": full_text  # Return the COMPLETE raw response
        }

    except Exception as e:
        logging.error(f"Judge failed: {type(e).__name__}: {str(e)}")
        return {"correctness": 0, "completeness": 0, "verdict": "error", "reason": f"{type(e).__name__}"}


@app.get("/health")
def health():
    return {"status": "ok", "model": "gemini-2.5-flash", "project": PROJECT}
